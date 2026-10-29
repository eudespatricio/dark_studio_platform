"""
Módulo de Remixagem Temporal, Embaralhamento Semântico e Evasão de Content ID (`remixer.py`).
Responsável por:
- Casamento de tempo (Time-Matching) entre os blocos da nova locução em Português
  e as cenas originais, aplicando Speed-Ramping controlado entre `0.85x` e `1.15x`
- Embaralhamento semântico de sub-cenas B-Roll para quebrar o hash temporal do Content ID
- Definição de parâmetros de transformação Anti-Content ID (espelhamento horizontal seletivo,
  overscan zoom de 5%, micro-rotação cromática, LUT/Color Grading e remoção de marca d'água).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Union

from .scene_analyzer import BoundingBox, SceneSegment


@dataclass
class AntiContentIDConfig:
    """Parâmetros de transformação visual e temporal para evasão de Content ID."""

    enable_hflip_on_broll: bool = True
    overscan_zoom_factor: float = 1.05  # 5% de zoom para alterar matriz de macroblocos
    contrast: float = 1.08
    brightness: float = 0.012
    saturation: float = 1.12
    gamma: float = 0.97
    hue_shift_deg: float = 2.5
    vignette_angle_rad: float = 0.38
    film_grain_strength: int = 4
    apply_delogo: bool = True
    delogo_box: Optional[BoundingBox] = None

    def build_ffmpeg_filter(self, is_talking_head: bool = False) -> str:
        """Gera a string de filtros FFmpeg de transformação Anti-Content ID."""
        filters: List[str] = []

        if self.apply_delogo and self.delogo_box is not None:
            b = self.delogo_box
            filters.append(f"delogo=x={b.x}:y={b.y}:w={b.width}:h={b.height}:show=0")

        if self.enable_hflip_on_broll and not is_talking_head:
            filters.append("hflip")

        if self.overscan_zoom_factor > 1.001:
            z = round(self.overscan_zoom_factor, 3)
            filters.append(f"crop=iw/{z}:ih/{z}:(iw-iw/{z})/2:(ih-ih/{z})/2,scale=iw*{z}:ih*{z}")

        filters.append(
            f"eq=contrast={self.contrast:.2f}:brightness={self.brightness:.3f}:"
            f"saturation={self.saturation:.2f}:gamma={self.gamma:.2f}"
        )
        filters.append(f"hue=h={self.hue_shift_deg:.1f}:s=1.03")
        filters.append(f"vignette=angle={self.vignette_angle_rad:.2f}")
        return ",".join(filters)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RemixedTimelineClip:
    """Representa um clipe na timeline final sincronizada com a locução PT-BR."""

    timeline_index: int
    original_scene_id: int
    source_start_sec: float
    source_end_sec: float
    source_duration_sec: float
    target_start_sec: float
    target_end_sec: float
    target_duration_sec: float
    speed_factor: float  # Restrito ao intervalo [0.85, 1.15]
    setpts_expr: str
    use_broll_replacement: bool
    broll_prompt: Optional[str]
    apply_hflip: bool
    ken_burns_preset: str  # "zoom_in_slow" | "zoom_out_slow" | "pan_right" | "pan_left"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RemixTimelinePlan:
    """Plano consolidado da timeline remixada pronta para renderização FFmpeg."""

    total_source_duration_sec: float
    total_target_duration_sec: float
    min_speed_factor: float
    max_speed_factor: float
    average_speed_factor: float
    shuffled_scenes_count: int
    broll_replacements_count: int
    anti_content_id: AntiContentIDConfig
    clips: List[RemixedTimelineClip] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class VideoRemixer:
    """
    Motor de sincronia temporal (Speed-Ramping `0.85x` a `1.15x`), embaralhamento
    semântico de sub-cenas e parametrização Anti-Content ID.
    """

    MIN_SPEED = 0.85
    MAX_SPEED = 1.15

    def __init__(
        self,
        min_speed: float = 0.85,
        max_speed: float = 1.15,
    ) -> None:
        self.min_speed = max(0.5, min_speed)
        self.max_speed = min(2.0, max_speed)

    def clamp_speed(self, raw_speed: float) -> float:
        """Restringe o fator de velocidade estritamente entre `0.85x` e `1.15x`."""
        return round(max(self.min_speed, min(self.max_speed, raw_speed)), 4)

    def semantic_shuffle_scenes(
        self,
        scenes: Sequence[SceneSegment],
        preserve_hook_count: int = 1,
    ) -> Tuple[List[SceneSegment], int]:
        """
        Embaralha sub-cenas B-Roll adjacentes em pares dentro de blocos narrativos
        preservando o gancho inicial (`preserve_hook_count`) e o clímax final para
        desconfigurar a assinatura temporal do Content ID sem perder coesão visual.
        """
        ordered = list(scenes)
        n = len(ordered)
        if n <= preserve_hook_count + 2:
            return ordered, 0

        swapped_count = 0
        idx = preserve_hook_count
        while idx + 1 < n - 1:
            s_a = ordered[idx]
            s_b = ordered[idx + 1]
            # Troca pares adjacentes de B-Roll para quebrar sequência de frames original
            if not s_a.has_talking_head and not s_b.has_talking_head:
                ordered[idx], ordered[idx + 1] = ordered[idx + 1], ordered[idx]
                swapped_count += 2
                idx += 2
            else:
                idx += 1

        return ordered, swapped_count

    def create_remix_plan(
        self,
        scenes: Sequence[Union[SceneSegment, Dict[str, Any]]],
        target_narration_duration_sec: float,
        narration_segments: Optional[Sequence[Dict[str, Any]]] = None,
        watermark_box: Optional[BoundingBox] = None,
        enable_semantic_shuffle: bool = True,
    ) -> RemixTimelinePlan:
        """
        Constrói o plano de edição casando a duração das cenas com a nova locução em Português.
        Calcula o `speed_factor` individual por cena respeitando a janela `[0.85x, 1.15x]`.
        """
        normalized_scenes: List[SceneSegment] = []
        for idx, s in enumerate(scenes, start=1):
            if isinstance(s, SceneSegment):
                normalized_scenes.append(s)
            else:
                st = float(s.get("start_sec", (idx - 1) * 4.0))
                et = float(s.get("end_sec", st + 4.0))
                normalized_scenes.append(
                    SceneSegment(
                        scene_id=int(s.get("scene_id", idx)),
                        start_sec=st,
                        end_sec=et,
                        duration_sec=max(0.5, et - st),
                        scene_type=str(s.get("scene_type", "broll_cinematic")),
                        has_talking_head=bool(s.get("has_talking_head", False)),
                        face_presence_ratio=float(s.get("face_presence_ratio", 0.0)),
                        requires_broll_replacement=bool(
                            s.get("requires_broll_replacement", s.get("has_talking_head", False))
                        ),
                        replacement_prompt=s.get("replacement_prompt"),
                    )
                )

        if not normalized_scenes:
            normalized_scenes = [
                SceneSegment(
                    scene_id=1,
                    start_sec=0.0,
                    end_sec=max(5.0, target_narration_duration_sec),
                    duration_sec=max(5.0, target_narration_duration_sec),
                    scene_type="broll_cinematic",
                    has_talking_head=False,
                    face_presence_ratio=0.0,
                )
            ]

        shuffled_count = 0
        if enable_semantic_shuffle:
            normalized_scenes, shuffled_count = self.semantic_shuffle_scenes(normalized_scenes)

        total_src_dur = sum(s.duration_sec for s in normalized_scenes) or 1.0
        target_total = max(2.0, float(target_narration_duration_sec or total_src_dur))

        ken_burns_cycle = ["zoom_in_slow", "pan_right", "zoom_out_slow", "pan_left"]
        clips: List[RemixedTimelineClip] = []
        cursor_target = 0.0

        for idx, scene in enumerate(normalized_scenes, start=1):
            # Duração alvo proporcional para esta cena (ou guiada por segmento de narração se fornecido)
            if narration_segments and idx - 1 < len(narration_segments):
                seg = narration_segments[idx - 1]
                desired_dur = max(
                    0.8,
                    float(seg.get("end", 0.0)) - float(seg.get("start", 0.0)),
                )
            else:
                weight = scene.duration_sec / total_src_dur
                desired_dur = max(0.8, target_total * weight)

            # Speed factor: speed = src_dur / target_dur
            raw_speed = scene.duration_sec / max(0.2, desired_dur)
            clamped_speed = self.clamp_speed(raw_speed)

            # Ajusta a janela fonte consumida para que (effective_src_dur / clamped_speed) == desired_dur
            effective_src_dur = round(desired_dur * clamped_speed, 3)
            if effective_src_dur <= scene.duration_sec:
                src_start = scene.start_sec
                src_end = round(scene.start_sec + effective_src_dur, 3)
            else:
                src_start = scene.start_sec
                src_end = scene.end_sec
                effective_src_dur = scene.duration_sec
                desired_dur = round(effective_src_dur / clamped_speed, 3)

            pts_multiplier = round(1.0 / clamped_speed, 4)
            setpts_expr = f"setpts={pts_multiplier:.4f}*(PTS-STARTPTS)"

            target_start = round(cursor_target, 3)
            target_end = round(cursor_target + desired_dur, 3)
            cursor_target = target_end

            kb_preset = ken_burns_cycle[(idx - 1) % len(ken_burns_cycle)]
            apply_hflip = (not scene.has_talking_head) and (idx % 2 == 1)

            clips.append(
                RemixedTimelineClip(
                    timeline_index=idx,
                    original_scene_id=scene.scene_id,
                    source_start_sec=src_start,
                    source_end_sec=src_end,
                    source_duration_sec=round(src_end - src_start, 3),
                    target_start_sec=target_start,
                    target_end_sec=target_end,
                    target_duration_sec=round(target_end - target_start, 3),
                    speed_factor=clamped_speed,
                    setpts_expr=setpts_expr,
                    use_broll_replacement=scene.requires_broll_replacement,
                    broll_prompt=scene.replacement_prompt,
                    apply_hflip=apply_hflip,
                    ken_burns_preset=kb_preset,
                )
            )

        speeds = [c.speed_factor for c in clips] or [1.0]
        broll_replacements = sum(1 for c in clips if c.use_broll_replacement)
        anti_cid = AntiContentIDConfig(
            enable_hflip_on_broll=True,
            overscan_zoom_factor=1.05,
            apply_delogo=watermark_box is not None,
            delogo_box=watermark_box,
        )

        return RemixTimelinePlan(
            total_source_duration_sec=round(total_src_dur, 2),
            total_target_duration_sec=round(cursor_target, 2),
            min_speed_factor=round(min(speeds), 4),
            max_speed_factor=round(max(speeds), 4),
            average_speed_factor=round(sum(speeds) / len(speeds), 4),
            shuffled_scenes_count=shuffled_count,
            broll_replacements_count=broll_replacements,
            anti_content_id=anti_cid,
            clips=clips,
        )


_REMIXER_INSTANCE: Optional[VideoRemixer] = None


def get_remixer() -> VideoRemixer:
    """Singleton factory para `VideoRemixer`."""
    global _REMIXER_INSTANCE
    if _REMIXER_INSTANCE is None:
        _REMIXER_INSTANCE = VideoRemixer()
    return _REMIXER_INSTANCE
