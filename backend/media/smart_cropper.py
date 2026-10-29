"""
Módulo de Reenquadramento Vertical Inteligente (Smart Cropper 16:9 -> 9:16).
Converte vídeos horizontais (1920x1080) para o formato vertical (1080x1920)
rastreando o ponto de interesse (rosto ou centro de ação óptica) com:
- Filtro de Zona Morta (Deadband) para ignorar micro-tremores
- Suavização Exponencial (EMA / Low-Pass Damping) e limite de velocidade máxima de pan
- Geração de expressão dinâmica FFmpeg (`crop` + `scale=1080:1920:flags=lanczos`).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from .scene_analyzer import SceneSegment


@dataclass
class CropKeyframe:
    """Keyframe suavizado da janela de recorte 9:16 sobre o canvas 16:9."""

    timestamp_sec: float
    raw_poi_x: int
    smoothed_center_x: int
    crop_x: int
    crop_y: int
    crop_w: int
    crop_h: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SmartCropPlan:
    """Plano completo de reenquadramento 16:9 -> 9:16 com telemetria e filtro FFmpeg."""

    source_resolution: Tuple[int, int]
    target_resolution: Tuple[int, int]
    crop_window_size: Tuple[int, int]
    smoothing_alpha: float
    deadband_px: int
    max_pan_speed_px_per_sec: float
    keyframes: List[CropKeyframe] = field(default_factory=list)
    ffmpeg_crop_filter: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SmartCropper:
    """
    Motor de reenquadramento inteligente 16:9 (1920x1080) -> 9:16 (1080x1920).
    Calcula uma trajetória de câmera virtual suave estabilizada para evitar
    efeito de câmera tremida (jitter).
    """

    def __init__(
        self,
        src_width: int = 1920,
        src_height: int = 1080,
        target_width: int = 1080,
        target_height: int = 1920,
        smoothing_alpha: float = 0.18,
        deadband_px: int = 28,
        max_pan_speed_px_per_sec: float = 180.0,
    ) -> None:
        self.src_width = src_width
        self.src_height = src_height
        self.target_width = target_width
        self.target_height = target_height
        self.smoothing_alpha = max(0.02, min(1.0, smoothing_alpha))
        self.deadband_px = max(0, deadband_px)
        self.max_pan_speed_px_per_sec = max(20.0, max_pan_speed_px_per_sec)

        # Em 1920x1080, a janela 9:16 de altura total (1080) possui largura 608px (múltiplo par)
        raw_crop_w = int(round(self.src_height * (self.target_width / float(self.target_height))))
        self.crop_w = raw_crop_w if (raw_crop_w % 2 == 0) else (raw_crop_w + 1)
        self.crop_h = self.src_height
        self.max_crop_x = max(0, self.src_width - self.crop_w)

    def clamp_crop_x(self, center_x: float) -> int:
        """Converte a coordenada X central para o canto superior esquerdo `crop_x` dentro dos limites."""
        desired_x = int(round(center_x - (self.crop_w / 2.0)))
        clamped = max(0, min(self.max_crop_x, desired_x))
        # Garante alinhamento par para compatibilidade YUV420p no FFmpeg
        return clamped - (clamped % 2)

    def build_crop_plan_from_scenes(
        self,
        scenes: Sequence[Union[SceneSegment, Dict[str, Any]]],
    ) -> SmartCropPlan:
        """
        Recebe a lista de cenas analisadas pelo `SceneAnalyzer` e gera uma trajetória
        estabilizada de câmera 9:16 com filtro de zona morta (deadband), amortecimento
        exponencial (EMA) e limitação de velocidade de pan.
        """
        raw_points: List[Tuple[float, int]] = []
        for idx, item in enumerate(scenes):
            if isinstance(item, SceneSegment):
                start_t = item.start_sec
                end_t = item.end_sec
                poi_x = int(item.point_of_interest_xy[0])
            else:
                start_t = float(item.get("start_sec", idx * 4.0))
                end_t = float(item.get("end_sec", start_t + 4.0))
                poi = item.get("point_of_interest_xy", (self.src_width // 2, self.src_height // 2))
                poi_x = int(poi[0]) if isinstance(poi, (list, tuple)) and len(poi) >= 1 else (self.src_width // 2)

            mid_t = round((start_t + end_t) / 2.0, 2)
            raw_points.append((start_t, poi_x))
            raw_points.append((mid_t, poi_x))

        if not raw_points:
            raw_points = [(0.0, self.src_width // 2), (10.0, self.src_width // 2)]

        keyframes: List[CropKeyframe] = []
        smoothed_cx = float(raw_points[0][1])
        prev_t = float(raw_points[0][0])

        for timestamp_sec, target_cx in raw_points:
            dt = max(0.04, timestamp_sec - prev_t)
            delta = float(target_cx) - smoothed_cx

            # 1. Deadband: ignora oscilações menores que `deadband_px` para manter câmera firme
            if abs(delta) <= self.deadband_px:
                effective_target = smoothed_cx
            else:
                effective_target = float(target_cx)

            # 2. Suavização exponencial (EMA)
            candidate_cx = smoothed_cx + self.smoothing_alpha * (effective_target - smoothed_cx)

            # 3. Limite de velocidade máxima de pan (px/s)
            max_step = self.max_pan_speed_px_per_sec * dt
            step = candidate_cx - smoothed_cx
            if abs(step) > max_step:
                candidate_cx = smoothed_cx + (max_step if step > 0 else -max_step)

            smoothed_cx = candidate_cx
            prev_t = timestamp_sec

            crop_x = self.clamp_crop_x(smoothed_cx)
            keyframes.append(
                CropKeyframe(
                    timestamp_sec=round(timestamp_sec, 2),
                    raw_poi_x=int(target_cx),
                    smoothed_center_x=int(round(smoothed_cx)),
                    crop_x=crop_x,
                    crop_y=0,
                    crop_w=self.crop_w,
                    crop_h=self.crop_h,
                )
            )

        ffmpeg_expr = self._build_ffmpeg_filter_expression(keyframes)
        return SmartCropPlan(
            source_resolution=(self.src_width, self.src_height),
            target_resolution=(self.target_width, self.target_height),
            crop_window_size=(self.crop_w, self.crop_h),
            smoothing_alpha=self.smoothing_alpha,
            deadband_px=self.deadband_px,
            max_pan_speed_px_per_sec=self.max_pan_speed_px_per_sec,
            keyframes=keyframes,
            ffmpeg_crop_filter=ffmpeg_expr,
        )

    def _build_ffmpeg_filter_expression(self, keyframes: Sequence[CropKeyframe]) -> str:
        """
        Constrói a cadeia de filtros FFmpeg combinando o `crop` dinâmico interpolado no tempo `t`
        e o redimensionamento Lanczos para `1080x1920`.
        """
        if not keyframes:
            default_x = self.clamp_crop_x(self.src_width / 2.0)
            return (
                f"crop=w={self.crop_w}:h={self.crop_h}:x={default_x}:y=0,"
                f"scale={self.target_width}:{self.target_height}:flags=lanczos,setsar=1"
            )

        # Simplifica keyframes consecutivos com mesmo crop_x
        compact: List[CropKeyframe] = [keyframes[0]]
        for kf in keyframes[1:]:
            if kf.crop_x != compact[-1].crop_x or (kf.timestamp_sec - compact[-1].timestamp_sec) >= 6.0:
                compact.append(kf)

        if len(compact) == 1:
            x_expr = str(compact[0].crop_x)
        else:
            # Limita a até 10 segmentos interpolados para manter a expressão FFmpeg enxuta
            sampled = compact[:10]
            expr = str(sampled[-1].crop_x)
            for i in range(len(sampled) - 2, -1, -1):
                k0 = sampled[i]
                k1 = sampled[i + 1]
                dt = max(0.1, round(k1.timestamp_sec - k0.timestamp_sec, 2))
                if k0.crop_x == k1.crop_x:
                    seg_expr = str(k0.crop_x)
                else:
                    dx = k1.crop_x - k0.crop_x
                    seg_expr = f"({k0.crop_x}+{dx}*((t-{k0.timestamp_sec:.2f})/{dt:.2f}))"
                expr = f"if(lt(t,{k1.timestamp_sec:.2f}),{seg_expr},{expr})"
            x_expr = expr

        return (
            f"crop=w={self.crop_w}:h={self.crop_h}:x='{x_expr}':y=0,"
            f"scale={self.target_width}:{self.target_height}:flags=lanczos,setsar=1"
        )


_SMART_CROPPER_INSTANCE: Optional[SmartCropper] = None


def get_smart_cropper() -> SmartCropper:
    """Singleton factory para `SmartCropper`."""
    global _SMART_CROPPER_INSTANCE
    if _SMART_CROPPER_INSTANCE is None:
        _SMART_CROPPER_INSTANCE = SmartCropper()
    return _SMART_CROPPER_INSTANCE
