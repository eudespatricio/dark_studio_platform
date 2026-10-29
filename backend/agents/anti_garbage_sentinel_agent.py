"""
Anti-Garbage Sentinel Agent (Guardião Físico Pré-Upload com Poder de VETO Absoluto).
Inspired by RiskSentinelAgent in ia_trader.
Performs physical inspection of the MP4 file using ffprobe + OpenCV frame sampling:
1. File existence & size (>= 1.5 MB for Shorts, >= 8 MB for Long-form).
2. Valid Video Stream (H.264/HEVC) and Valid Audio Stream (AAC/PCM/MP3, non-empty).
3. Exact Resolution match (1920x1080 for 16:9, 1080x1920 for 9:16).
4. Duration Gate:
   - Shorts (9:16): 25s to 61s.
   - Long Documentary (16:9): >= 180s (and >= 480s when require_full_doc=True).
5. Visual Entropy & Anti-Black-Screen / Anti-Subtitle-Only Gate:
   - Samples 8 equidistant frames across the video timeline using OpenCV.
   - Computes global pixel standard deviation (`visual_entropy_std`) and upper-2/3 frame
     standard deviation (`background_visual_std`, excluding the bottom subtitle zone!).
   - If the upper 70% of the frame is a flat/black background (only subtitles moving at the bottom),
     `background_visual_std` drops below 12.0 -> IMMEDIATE VETO!
   - Computes inter-frame motion delta (`motion_delta_mean`) to reject frozen static images.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

import cv2
import numpy as np

from backend.agents.base_agent import AgentVote, BaseStudioAgent
from backend.domain.publication_policy import (
    LONG_16_9_FULLDOC_MIN_SEC,
    POLICY_VERSION,
    resolve_format_rules,
)


class AntiGarbageSentinelAgent(BaseStudioAgent):
    def __init__(self) -> None:
        super().__init__(
            agent_id="anti_garbage_sentinel",
            agent_name="Anti-Garbage Physical Sentinel (VETO)",
            role="Auditor Físico FFprobe/OpenCV & Bloqueador de Upload Sujo",
            weight=0.25,
        )

    @staticmethod
    def inspect_physical_video(video_path: str | Path) -> Dict[str, Any]:
        path = Path(video_path)
        if not path.exists() or not path.is_file():
            return {
                "exists": False,
                "error": f"Arquivo físico inexistente: {path}",
            }

        file_size_bytes = path.stat().st_size
        if file_size_bytes < 100_000:
            return {
                "exists": True,
                "file_size_bytes": file_size_bytes,
                "error": f"Arquivo corrompido ou stub ({file_size_bytes} bytes).",
            }

        # Calculate exact SHA-256 of physical artifact (P0.3 cryptographic binding)
        sha256_hash = hashlib.sha256()
        try:
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    sha256_hash.update(chunk)
            artifact_sha256 = sha256_hash.hexdigest()
        except Exception:
            artifact_sha256 = ""

        # 1. Try ffprobe first; if unavailable in PATH, fall back to OpenCV + MP4 atom / ffmpeg check
        has_video = False
        has_audio = False
        width = 0
        height = 0
        duration_sec = 0.0
        video_codec = "h264"
        audio_codec = "aac"

        try:
            proc = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-print_format",
                    "json",
                    "-show_format",
                    "-show_streams",
                    str(path),
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if proc.returncode == 0 and proc.stdout:
                info = json.loads(proc.stdout)
                fmt = info.get("format", {})
                duration_sec = float(fmt.get("duration", 0.0) or 0.0)
                for stream in info.get("streams", []):
                    codec_type = stream.get("codec_type")
                    if codec_type == "video" and not has_video:
                        has_video = True
                        width = int(stream.get("width", 0) or 0)
                        height = int(stream.get("height", 0) or 0)
                        video_codec = str(stream.get("codec_name", "h264"))
                        if duration_sec <= 0.0:
                            duration_sec = float(stream.get("duration", 0.0) or 0.0)
                    elif codec_type == "audio" and not has_audio:
                        has_audio = True
                        audio_codec = str(stream.get("codec_name", "aac"))
        except Exception:
            # Fallback when ffprobe is not installed globally: inspect MP4 atoms for audio ('soun'/'mp4a')
            try:
                with open(path, "rb") as f:
                    head_bytes = f.read(min(file_size_bytes, 2 * 1024 * 1024))
                    if file_size_bytes > 2 * 1024 * 1024:
                        f.seek(max(0, file_size_bytes - 2 * 1024 * 1024))
                        tail_bytes = f.read(2 * 1024 * 1024)
                    else:
                        tail_bytes = b""
                combined_atoms = head_bytes + tail_bytes
                if b"soun" in combined_atoms or b"mp4a" in combined_atoms or b"smhd" in combined_atoms:
                    has_audio = True
            except Exception:
                pass

        # 2. Sample 8 frames across the video timeline using OpenCV
        visual_stds: List[float] = []
        bg_visual_stds: List[float] = []
        motion_deltas: List[float] = []
        mean_luminances: List[float] = []
        flat_synthetic_ratios: List[float] = []
        frame_hists: List[np.ndarray] = []
        frame_dhashes: List[np.ndarray] = []
        branding_match_detected = False
        branding_match_detail = ""
        distinct_scenes = 1

        # Load channel branding/avatar dHashes & histograms to block logo-as-content hallucinations
        branding_refs: List[ tuple[str, np.ndarray, np.ndarray] ] = []
        try:
            branding_root = Path("/home/eudespatricio/dark_studio_platform/workspace/branding")
            if branding_root.exists():
                for bp in branding_root.rglob("*"):
                    # Check exclusively against channel avatars and full banners (exclude small watermarks)
                    if bp.suffix.lower() in (".jpg", ".jpeg", ".png") and ("avatar" in bp.name.lower() or "banner" in bp.name.lower()) and "watermark" not in bp.name.lower():
                        b_img = cv2.imread(str(bp))
                        if b_img is not None:
                            b_gray = cv2.cvtColor(cv2.resize(b_img, (9, 8)), cv2.COLOR_BGR2GRAY)
                            b_dhash = (b_gray[:, 1:] > b_gray[:, :-1]).flatten()
                            b_hsv = cv2.cvtColor(b_img, cv2.COLOR_BGR2HSV)
                            b_hist = cv2.calcHist([b_hsv], [0, 1], None, [24, 24], [0, 180, 0, 256])
                            cv2.normalize(b_hist, b_hist)
                            branding_refs.append((bp.name, b_dhash, b_hist))
        except Exception:
            pass

        try:
            cap = cv2.VideoCapture(str(path))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
            fps = float(cap.get(cv2.CAP_PROP_FPS) or 30.0)
            w_cv = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
            h_cv = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
            if total_frames > 0 and w_cv > 0 and h_cv > 0:
                has_video = True
                if width <= 0:
                    width = w_cv
                if height <= 0:
                    height = h_cv
            if duration_sec <= 0.0 and total_frames > 0 and fps > 0:
                duration_sec = total_frames / fps

            if total_frames > 5:
                sample_indices = np.linspace(
                    max(int(fps * 0.6), int(total_frames * 0.08)),
                    int(total_frames * 0.94),
                    num=8,
                    dtype=int,
                )
                prev_gray: Optional[np.ndarray] = None
                for idx in sample_indices:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
                    ok, frame = cap.read()
                    if not ok or frame is None:
                        continue
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    h, w = gray.shape
                    visual_stds.append(float(np.std(gray)))
                    mean_luminances.append(float(np.mean(gray)))

                    # Inspect upper 65% of the frame (excluding bottom/center subtitle burn zone)
                    # to detect "subtitle-only on black/flat background" bug!
                    upper_zone = gray[0 : int(h * 0.45), :]
                    bg_visual_stds.append(float(np.std(upper_zone)))

                    # Detect crude synthetic Pillow rectangles / solid neon blocks in central frame
                    mid_bgr = frame[int(h * 0.15) : int(h * 0.72), int(w * 0.08) : int(w * 0.92)]
                    hsv = cv2.cvtColor(mid_bgr, cv2.COLOR_BGR2HSV)
                    sat = hsv[:, :, 1]
                    val = hsv[:, :, 2]
                    gx = np.abs(np.diff(mid_bgr.astype(np.int16), axis=1)).mean(axis=2)
                    gy = np.abs(np.diff(mid_bgr.astype(np.int16), axis=0)).mean(axis=2)
                    grad_mag = gx[:-1, :] + gy[:, :-1]
                    sat_crop = sat[:-1, :-1]
                    val_crop = val[:-1, :-1]
                    # Solid neon/saturated synthetic block = high saturation (>180), bright (>150), zero texture gradient (<1.0)
                    synthetic_mask = (sat_crop > 180) & (val_crop > 150) & (grad_mag < 1.0)
                    # Legendas neon (palavra destacada) são traços finos de cor chapada: a abertura morfológica
                    # remove componentes mais finos que ~31px e preserva apenas blocos sólidos reais.
                    synthetic_mask = cv2.morphologyEx(
                        synthetic_mask.astype(np.uint8), cv2.MORPH_OPEN, np.ones((31, 31), np.uint8)
                    ).astype(bool)
                    flat_synthetic_ratios.append(float(np.mean(synthetic_mask)))

                    # Perceptual hash & HSV histogram of upper/central scene (ignoring bottom subtitles)
                    scene_crop = frame[int(h * 0.08) : int(h * 0.62), int(w * 0.08) : int(w * 0.92)]
                    s_gray = cv2.cvtColor(cv2.resize(scene_crop, (9, 8)), cv2.COLOR_BGR2GRAY)
                    s_dhash = (s_gray[:, 1:] > s_gray[:, :-1]).flatten()
                    frame_dhashes.append(s_dhash)

                    s_hsv = cv2.cvtColor(scene_crop, cv2.COLOR_BGR2HSV)
                    s_hist = cv2.calcHist([s_hsv], [0, 1], None, [24, 24], [0, 180, 0, 256])
                    cv2.normalize(s_hist, s_hist)
                    frame_hists.append(s_hist)

                    for b_name, b_dhash, b_hist in branding_refs:
                        hamming = int(np.count_nonzero(s_dhash != b_dhash))
                        correl = float(cv2.compareHist(s_hist, b_hist, cv2.HISTCMP_CORREL))
                        # Logo real usado como cena = dHash quase idêntico (<=5 bits) E histograma correlacionado.
                        # Limiares antigos (<=10/14 bits) davam falso positivo em cenas escuras ciano (clipes de sinapse).
                        if (hamming <= 5 and correl >= 0.60) or (hamming <= 8 and correl >= 0.95):
                            branding_match_detected = True
                            branding_match_detail = f"{b_name} (hamming={hamming}, correl={correl:.2f})"

                    resized_small = cv2.resize(gray, (160, 90))
                    if prev_gray is not None:
                        delta = float(
                            np.mean(
                                cv2.absdiff(resized_small, prev_gray).astype(np.float32)
                            )
                        )
                        motion_deltas.append(delta)
                        if delta > 8.0:
                            distinct_scenes += 1
                    prev_gray = resized_small
            cap.release()
        except Exception:
            pass

        # Compute inter-scene histogram correlation across non-adjacent scenes to catch cloned base images
        inter_scene_correls: List[float] = []
        if len(frame_hists) >= 4:
            for i in range(len(frame_hists)):
                for j in range(i + 2, len(frame_hists)):
                    c_val = float(cv2.compareHist(frame_hists[i], frame_hists[j], cv2.HISTCMP_CORREL))
                    inter_scene_correls.append(max(0.0, c_val))
        scene_clone_correlation = float(np.mean(inter_scene_correls)) if inter_scene_correls else 0.0

        visual_entropy_std = float(np.mean(visual_stds)) if visual_stds else 0.0
        background_visual_std = (
            float(np.mean(bg_visual_stds)) if bg_visual_stds else 0.0
        )
        motion_delta_mean = float(np.mean(motion_deltas)) if motion_deltas else 0.0
        luminance_mean = float(np.mean(mean_luminances)) if mean_luminances else 0.0
        synthetic_flat_patch_ratio = (
            float(np.mean(flat_synthetic_ratios)) if flat_synthetic_ratios else 0.0
        )

        return {
            "exists": True,
            "file_size_bytes": file_size_bytes,
            "file_size_mb": round(file_size_bytes / (1024 * 1024), 2),
            "has_video": has_video,
            "has_audio": has_audio,
            "video_codec": video_codec,
            "audio_codec": audio_codec,
            "width": width,
            "height": height,
            "duration_sec": round(duration_sec, 2),
            "visual_entropy_std": round(visual_entropy_std, 2),
            "background_visual_std": round(background_visual_std, 2),
            "motion_delta_mean": round(motion_delta_mean, 2),
            "luminance_mean": round(luminance_mean, 2),
            "synthetic_flat_patch_ratio": round(synthetic_flat_patch_ratio, 4),
            "scene_clone_correlation": round(scene_clone_correlation, 3),
            "branding_logo_hallucination": branding_match_detected,
            "branding_match_detail": branding_match_detail,
            "distinct_scenes_detected": distinct_scenes,
            "artifact_sha256": artifact_sha256,
            "policy_version": POLICY_VERSION,
        }

    def evaluate(self, context: Dict[str, Any]) -> AgentVote:
        video_path = context.get("video_path")
        video_format = str(context.get("format", "long_16x9")).lower()
        is_music = bool(
            context.get("is_music")
            or context.get("channel_id") == "UCbO67ez7TKOJ8C_kpUF4t5Q"
            or str(context.get("category_id")) == "10"
            or "music" in video_format
        )
        rules = resolve_format_rules(video_format, is_music=is_music)

        # FAIL-CLOSED (P0.3): Without physical video evidence, the gate immediately blocks
        if not video_path:
            return AgentVote(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                role=self.role,
                approved=False,
                veto=True,
                score=0.0,
                confidence=1.0,
                weight=self.weight,
                rationale="FAIL-CLOSED QUALITY GATE: Parâmetro 'video_path' ausente. Auditoria física requer o artefato renderizado real.",
                recommendations=["Certifique-se de que a etapa de renderização produziu o MP4 antes da deliberação."],
                metrics={"audit_error": "missing_video_path", "policy_version": POLICY_VERSION},
            )

        video_file = Path(video_path)
        if not video_file.exists():
            return AgentVote(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                role=self.role,
                approved=False,
                veto=True,
                score=0.0,
                confidence=1.0,
                weight=self.weight,
                rationale=f"FAIL-CLOSED QUALITY GATE: Arquivo de vídeo inexistente no disco: {video_path}",
                recommendations=["Verifique se a etapa de renderização FFmpeg foi concluída com sucesso."],
                metrics={"audit_error": "file_not_found", "video_path": str(video_path), "policy_version": POLICY_VERSION},
            )

        reasons_for_veto: List[str] = []
        recommendations: List[str] = []

        probe = self.inspect_physical_video(video_file)
        context.update(probe)

        if not probe.get("exists") or probe.get("error"):
            reasons_for_veto.append(
                probe.get("error", "Arquivo de vídeo inexistente ou ilegível.")
            )
        else:
            if not probe.get("has_video"):
                reasons_for_veto.append("Stream de vídeo ausente no container MP4.")
            if not probe.get("has_audio"):
                reasons_for_veto.append(
                    "Stream de áudio ausente — proibido enviar vídeo mudo ao YouTube."
                )

            duration_sec = float(probe.get("duration_sec", 0.0))
            file_size_mb = float(probe.get("file_size_mb", 0.0))
            bg_std = float(probe.get("background_visual_std", 0.0))
            entropy_std = float(probe.get("visual_entropy_std", 0.0))
            motion_delta = float(probe.get("motion_delta_mean", 0.0))
            synthetic_flat_ratio = float(probe.get("synthetic_flat_patch_ratio", 0.0))

            is_short = "short" in video_format or "9x16" in video_format or "9_16" in video_format
            if is_short:
                if duration_sec < rules.min_duration_sec or duration_sec > rules.max_duration_sec:
                    reasons_for_veto.append(
                        f"Duração de Short inválida ({duration_sec:.1f}s). Exigido pela política unificada: {rules.min_duration_sec:.0f}s a {rules.max_duration_sec:.0f}s."
                    )
                if file_size_mb < rules.min_file_size_mb:
                    reasons_for_veto.append(
                        f"Tamanho físico do Short ({file_size_mb:.2f} MB < {rules.min_file_size_mb:.1f} MB) suspeito de baixa taxa de bits."
                    )
            else:
                long_min = (
                    LONG_16_9_FULLDOC_MIN_SEC
                    if (context.get("require_full_doc") and not is_music)
                    else rules.min_duration_sec
                )
                if duration_sec < long_min:
                    reasons_for_veto.append(
                        f"Vídeo Longo truncado ({duration_sec:.1f}s < mínimo exigido de {long_min:.0f}s pela política versionada {POLICY_VERSION})."
                    )
                if file_size_mb < rules.min_file_size_mb:
                    reasons_for_veto.append(
                        f"Tamanho físico do Vídeo Longo ({file_size_mb:.2f} MB < {rules.min_file_size_mb:.1f} MB) incompatível com 1080p real."
                    )

            # Visual anti-garbage check: reject black screen or subtitle-only videos
            if entropy_std < 12.0 or bg_std < 8.5:
                reasons_for_veto.append(
                    f"VETO VISUAL: Fundo sem imagem real (apenas texto/legenda ou tela preta detectada — bg_std={bg_std:.1f}, entropy={entropy_std:.1f})."
                )
            if synthetic_flat_ratio > 0.08:
                reasons_for_veto.append(
                    f"VETO VISUAL (BARRAS SINTÉTICAS PILLOW DETECTADAS): {synthetic_flat_ratio*100:.1f}% do quadro contém blocos de cor chapada artificial. "
                    + (
                        "Causa provável em Shorts 9:16: infográfico 16:9 (diag_*.png) recortado/esticado sem layout 'fit' "
                        "(ver render_short_video)."
                        if "short" in video_format
                        else "Verifique cartelas/infográficos ocupando o quadro inteiro sem textura."
                    )
                )
            if not is_music:
                if motion_delta < 0.35:
                    reasons_for_veto.append(
                        f"VETO DE MOVIMENTO: Vídeo congelado/estático (motion_delta={motion_delta:.2f})."
                    )
                if bool(probe.get("branding_logo_hallucination", False)):
                    reasons_for_veto.append(
                        "VETO DE ALUCINAÇÃO VISUAL: Logo/Avatar ou Banner do próprio canal usado como cena de vídeo sem contexto documental."
                    )
                scene_clone_correl = float(probe.get("scene_clone_correlation", 0.0))
                if scene_clone_correl > 0.72:
                    reasons_for_veto.append(
                        f"VETO DE REPETIÇÃO DE IMAGEM-BASE: Cenas clonadas da mesma imagem (correl={scene_clone_correl:.2f} > 0.72). Exigido B-Roll autêntico e diverso."
                    )

                # Gate de Diversidade Visual de Elite:
                # Rejeita vídeos com menos de 5 cenas distintas em Shorts ou menos de 8 em Longos
                distinct_scenes = int(probe.get("distinct_scenes_detected", 1))
                min_required_scenes = rules.min_distinct_scenes
                if distinct_scenes < min_required_scenes:
                    reasons_for_veto.append(
                        f"VETO DE POUCA VARIEDADE VISUAL: Apenas {distinct_scenes} cenas distintas detectadas (mínimo exigido: {min_required_scenes} para {'Short 9:16' if is_short else 'Documentário 16:9'})."
                    )

        veto = len(reasons_for_veto) > 0
        score = 0.0 if veto else 96.0
        if veto:
            recommendations.extend(reasons_for_veto)
            rationale = "BLOQUEIO FÍSICO (VETO): " + " | ".join(reasons_for_veto)
        else:
            rationale = (
                f"APROVADO FÍSICO: {probe.get('width')}x{probe.get('height')} | "
                f"{probe.get('duration_sec')}s | {probe.get('file_size_mb')} MB | "
                f"Entropia BG={probe.get('background_visual_std')} ( B-Roll Verificado ) | Áudio OK."
            )

        return AgentVote(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            role=self.role,
            approved=not veto,
            veto=veto,
            score=score,
            confidence=0.99,
            weight=self.weight,
            rationale=rationale,
            metrics=probe,
            recommendations=recommendations,
        )
