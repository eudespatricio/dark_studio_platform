"""
Quality Gate, Anti-Content-ID Auditor & Post-Publish Performance Scorer (PQS & PPPS).

Responsável por:
1. Calcular o Pipeline Quality Score (PQS 0-100) pré-publicação em 4 pilares de 25 pontos:
   - outlier_strength_score (0-25)
   - hook_and_pacing_score (0-25)
   - audio_sync_and_lufs_score (0-25)
   - originality_anti_content_id_score (0-25)
2. Bloquear automaticamente vídeos que não atinjam o Quality Gate (PQS >= 75.0).
3. Calcular o Post-Publish Performance Score (PPPS 0-100) pós-publicação:
   - CTR da Thumbnail (35%)
   - Retenção Média % / AVD (40%)
   - Velocidade VPH nas primeiras 48h (15%)
   - Conversão de Shorts para Vídeo Longo (10%)
4. Gerar insights acionáveis para retroalimentação contínua do Gemini 1.5 Pro.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class PQSResult:
    """Resultado estruturado do Pipeline Quality Score (Pré-Publicação)."""

    total_score: float
    pqs_score: float
    grade: str
    passed_quality_gate: bool
    outlier_strength_score: float
    hook_and_pacing_score: float
    audio_sync_and_lufs_score: float
    originality_anti_content_id_score: float
    pillars: dict[str, float] = field(default_factory=dict)
    checklist: dict[str, bool] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    evaluated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PPPSResult:
    """Resultado estruturado do Post-Publish Performance Score (Pós-Publicação)."""

    total_score: float
    ppps_score: float
    grade: str
    ctr_score: float
    avd_retention_score: float
    vph_48h_score: float
    shorts_conversion_score: float
    component_scores: dict[str, float] = field(default_factory=dict)
    vs_baseline_deltas: dict[str, float] = field(default_factory=dict)
    insights: list[str] = field(default_factory=list)
    gemini_feedback_prompt: str = ""
    evaluated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class QualityScorer:
    """
    Motor de Auditoria de Qualidade (PQS Pré-Publicação e PPPS Pós-Publicação)
    e conformidade Anti-Content-ID / Diretrizes de Conteúdo Original do YouTube.
    """

    QUALITY_GATE_MIN_SCORE: float = 75.0
    MIN_OUTLIER_MULTIPLIER: float = 3.0
    MAX_SYNC_ERROR_MS: float = 150.0
    TARGET_LUFS: float = -14.0
    LUFS_TOLERANCE: float = 1.2
    MIN_DYNAMIC_CROP_PCT: float = 6.0

    def __init__(self, quality_gate_threshold: float = 75.0) -> None:
        self.quality_gate_threshold = float(quality_gate_threshold)

    # -------------------------------------------------------------------------
    # 1. PIPELINE QUALITY SCORE (PQS 0-100) - PRÉ-PUBLICAÇÃO
    # -------------------------------------------------------------------------
    def calculate_pqs(self, job_data: dict[str, Any]) -> dict[str, Any]:
        """
        Calcula o Pipeline Quality Score (0 a 100) subdividido em 4 pilares de 25 pontos:
        1. outlier_strength_score (0-25)
        2. hook_and_pacing_score (0-25)
        3. audio_sync_and_lufs_score (0-25)
        4. originality_anti_content_id_score (0-25)
        """
        if not isinstance(job_data, dict):
            raise TypeError("job_data deve ser um dicionário válido.")

        recommendations: list[str] = []
        checklist: dict[str, bool] = {}

        # Pilar 1: Outlier Strength Score (0 - 25)
        outlier_score_pts = self._score_outlier_strength(
            job_data, checklist, recommendations
        )

        # Pilar 2: Hook & Pacing Score (0 - 25)
        hook_pacing_pts = self._score_hook_and_pacing(
            job_data, checklist, recommendations
        )

        # Pilar 3: Audio Sync & LUFS Score (0 - 25)
        audio_sync_pts = self._score_audio_sync_and_lufs(
            job_data, checklist, recommendations
        )

        # Pilar 4: Originality & Anti-Content-ID Score (0 - 25)
        originality_pts = self._score_originality_anti_content_id(
            job_data, checklist, recommendations
        )

        total_score = round(
            min(
                100.0,
                max(
                    0.0,
                    outlier_score_pts
                    + hook_pacing_pts
                    + audio_sync_pts
                    + originality_pts,
                ),
            ),
            2,
        )

        grade = self._map_pqs_grade(total_score)
        passed_gate = bool(total_score >= self.quality_gate_threshold)

        if not passed_gate and not any("BLOQUEIO QUALITY GATE" in r for r in recommendations):
            recommendations.insert(
                0,
                f"BLOQUEIO QUALITY GATE: Score total ({total_score:.1f}/100) abaixo do mínimo exigido ({self.quality_gate_threshold:.1f}).",
            )

        pillars = {
            "outlier_strength_score": round(outlier_score_pts, 2),
            "hook_and_pacing_score": round(hook_pacing_pts, 2),
            "audio_sync_and_lufs_score": round(audio_sync_pts, 2),
            "originality_anti_content_id_score": round(originality_pts, 2),
        }

        result = PQSResult(
            total_score=total_score,
            pqs_score=total_score,
            grade=grade,
            passed_quality_gate=passed_gate,
            outlier_strength_score=pillars["outlier_strength_score"],
            hook_and_pacing_score=pillars["hook_and_pacing_score"],
            audio_sync_and_lufs_score=pillars["audio_sync_and_lufs_score"],
            originality_anti_content_id_score=pillars[
                "originality_anti_content_id_score"
            ],
            pillars=pillars,
            checklist=checklist,
            recommendations=recommendations,
        )
        return result.to_dict()

    def _score_outlier_strength(
        self,
        job_data: dict[str, Any],
        checklist: dict[str, bool],
        recommendations: list[str],
    ) -> float:
        """
        Avalia a força do vídeo-fonte (0 a 25 pontos):
        - Outlier Multiplier >= 3.0x (até 15 pontos)
        - VPH (Views Per Hour) do vídeo-fonte (até 10 pontos)
        """
        source = job_data.get("source_video") or job_data.get("outlier_data") or {}
        outlier_ratio = float(
            job_data.get(
                "outlier_score",
                job_data.get(
                    "outlier_multiplier",
                    source.get("outlier_score", source.get("outlier_multiplier", 0.0)),
                ),
            )
            or 0.0
        )
        vph = float(
            job_data.get(
                "vph",
                job_data.get(
                    "source_vph",
                    source.get("vph", source.get("views_per_hour", 0.0)),
                ),
            )
            or 0.0
        )

        # Pontuação de Outlier Ratio (0 a 15 pts)
        # < 1.5x -> 0 a 4 pts | 1.5x a 2.99x -> 4 a 9 pts | >= 3.0x -> 11 a 15 pts (5.0x+ = 15 pts)
        if outlier_ratio >= 5.0:
            ratio_pts = 15.0
        elif outlier_ratio >= self.MIN_OUTLIER_MULTIPLIER:
            ratio_pts = 11.0 + ((outlier_ratio - 3.0) / 2.0) * 4.0
        elif outlier_ratio >= 1.5:
            ratio_pts = 4.0 + ((outlier_ratio - 1.5) / 1.5) * 6.0
        elif outlier_ratio > 0:
            ratio_pts = (outlier_ratio / 1.5) * 4.0
        else:
            ratio_pts = 0.0

        checklist["outlier_gte_3x"] = outlier_ratio >= self.MIN_OUTLIER_MULTIPLIER
        if not checklist["outlier_gte_3x"]:
            recommendations.append(
                f"Vídeo-fonte com Outlier Score baixo ({outlier_ratio:.2f}x < 3.0x). Priorize vídeos com no mínimo 3x a média do canal."
            )

        # Pontuação de VPH (0 a 10 pts)
        # VPH >= 500 -> 10 pts | 200..500 -> 7..10 pts | 50..200 -> 3..7 pts | < 50 -> 0..3 pts
        if vph >= 500.0:
            vph_pts = 10.0
        elif vph >= 200.0:
            vph_pts = 7.0 + ((vph - 200.0) / 300.0) * 3.0
        elif vph >= 50.0:
            vph_pts = 3.0 + ((vph - 50.0) / 150.0) * 4.0
        elif vph > 0.0:
            vph_pts = (vph / 50.0) * 3.0
        else:
            vph_pts = 0.0

        checklist["source_vph_strong"] = vph >= 100.0
        if not checklist["source_vph_strong"]:
            recommendations.append(
                f"VPH do vídeo-fonte reduzido ({vph:.1f} VPH). Busque fontes com tração ativa (>= 100 VPH)."
            )

        return min(25.0, max(0.0, ratio_pts + vph_pts))

    def _score_hook_and_pacing(
        self,
        job_data: dict[str, Any],
        checklist: dict[str, bool],
        recommendations: list[str],
    ) -> float:
        """
        Avalia a força do Hook nos primeiros 15s, presença de Open Loops
        e ritmo de cortes (troca de cena ideal a cada 3-6s) (0 a 25 pontos).
        """
        script_data = job_data.get("script_data") or job_data.get("pacing_data") or {}

        # 1. Força do Hook nos primeiros 15s (0 a 10 pts)
        # Aceita escala 0-100 ou 0-10 ou booleano hook_First_15s_strong
        raw_hook = job_data.get(
            "hook_strength",
            job_data.get(
                "hook_score",
                script_data.get("hook_strength", script_data.get("hook_score", None)),
            ),
        )
        if raw_hook is None:
            hook_15s_ok = bool(
                job_data.get(
                    "hook_first_15s_strong",
                    script_data.get("hook_first_15s_strong", False),
                )
            )
            hook_norm = 85.0 if hook_15s_ok else 40.0
        else:
            val = float(raw_hook)
            hook_norm = val * 10.0 if val <= 10.0 else val

        hook_pts = min(10.0, max(0.0, (hook_norm / 100.0) * 10.0))
        checklist["strong_hook_15s"] = hook_norm >= 75.0
        if not checklist["strong_hook_15s"]:
            recommendations.append(
                "Fortalecer o Hook nos primeiros 15 segundos com promessa direta, quebra de expectativa ou pergunta de alto impacto."
            )

        # 2. Presença de Open Loops (0 a 7 pts)
        open_loops = job_data.get(
            "open_loops_count",
            job_data.get(
                "open_loops",
                script_data.get(
                    "open_loops_count", script_data.get("open_loops", 0)
                ),
            ),
        )
        if isinstance(open_loops, (list, tuple, set)):
            open_loops_count = len(open_loops)
        elif isinstance(open_loops, bool):
            open_loops_count = 2 if open_loops else 0
        else:
            open_loops_count = int(open_loops or 0)

        if open_loops_count >= 3:
            loops_pts = 7.0
        elif open_loops_count == 2:
            loops_pts = 6.0
        elif open_loops_count == 1:
            loops_pts = 3.5
        else:
            loops_pts = 0.0

        checklist["has_open_loops"] = open_loops_count >= 2
        if not checklist["has_open_loops"]:
            recommendations.append(
                f"Inserir pelo menos 2 Open Loops no roteiro (encontrado: {open_loops_count}) para segurar a retenção no meio do vídeo."
            )

        # 3. Ritmo de Cortes / Troca de Cena a cada 3-6s (0 a 8 pts)
        avg_cut_sec = job_data.get(
            "avg_scene_duration_sec",
            job_data.get(
                "cut_pacing_sec",
                script_data.get("avg_scene_duration_sec", None),
            ),
        )
        if avg_cut_sec is None:
            scenes = job_data.get("scenes") or script_data.get("scenes") or []
            if isinstance(scenes, list) and len(scenes) > 0:
                durations = [
                    float(s.get("duration", s.get("duration_sec", 0.0)))
                    for s in scenes
                    if isinstance(s, dict)
                ]
                durations = [d for d in durations if d > 0]
                avg_cut_sec = sum(durations) / len(durations) if durations else 0.0
            else:
                avg_cut_sec = 0.0
        else:
            avg_cut_sec = float(avg_cut_sec)

        if 3.0 <= avg_cut_sec <= 6.0:
            pacing_pts = 8.0
            checklist["optimal_cut_pacing_3_to_6s"] = True
        elif 2.0 <= avg_cut_sec < 3.0 or 6.0 < avg_cut_sec <= 8.0:
            pacing_pts = 5.0
            checklist["optimal_cut_pacing_3_to_6s"] = False
            recommendations.append(
                f"Ajustar ritmo de cortes para a janela ideal de 3s a 6s por cena (atual: {avg_cut_sec:.1f}s)."
            )
        elif avg_cut_sec > 0.0:
            pacing_pts = 2.0
            checklist["optimal_cut_pacing_3_to_6s"] = False
            recommendations.append(
                f"Ritmo de edição fora do padrão ({avg_cut_sec:.1f}s/cena).Subdivida cenas longas com B-roll ou zoom a cada 3-6s."
            )
        else:
            pacing_pts = 0.0
            checklist["optimal_cut_pacing_3_to_6s"] = False
            recommendations.append(
                "Métrica de duração média de cenas ausente ou inválida."
            )

        return min(25.0, max(0.0, hook_pts + loops_pts + pacing_pts))

    def _score_audio_sync_and_lufs(
        self,
        job_data: dict[str, Any],
        checklist: dict[str, bool],
        recommendations: list[str],
    ) -> float:
        """
        Avalia (0 a 25 pontos):
        - Erro médio de sincronia áudio/cena < 150ms (0 a 10 pts)
        - Separação de stems via Demucs (0 a 7 pts)
        - Normalização em -14 LUFS (0 a 8 pts)
        """
        audio_data = job_data.get("audio_data") or job_data.get("audio_metrics") or {}

        # 1. Erro médio de sincronia áudio/cena (< 150ms) -> 0 a 10 pts
        sync_error_ms = job_data.get(
            "avg_sync_error_ms",
            job_data.get(
                "sync_drift_ms",
                audio_data.get(
                    "avg_sync_error_ms", audio_data.get("sync_drift_ms", None)
                ),
            ),
        )
        if sync_error_ms is None:
            sync_pts = 0.0
            checklist["audio_sync_under_150ms"] = False
            recommendations.append(
                "Erro de sincronia áudio/cena não informado. Valide o alinhamento de timecodes (< 150ms)."
            )
        else:
            err = abs(float(sync_error_ms))
            if err <= 50.0:
                sync_pts = 10.0
            elif err < self.MAX_SYNC_ERROR_MS:
                # 50ms a 150ms -> 10.0 down to 7.5 pts
                sync_pts = 7.5 + ((self.MAX_SYNC_ERROR_MS - err) / 100.0) * 2.5
            elif err <= 300.0:
                sync_pts = max(1.0, 5.0 * (1.0 - (err - 150.0) / 150.0))
            else:
                sync_pts = 0.0

            checklist["audio_sync_under_150ms"] = err < self.MAX_SYNC_ERROR_MS
            if not checklist["audio_sync_under_150ms"]:
                recommendations.append(
                    f"Desvio médio de sincronia áudio/cena ({err:.0f}ms) excede o limite de 150ms. Realinhe a locução TTS por cena com time-stretch."
                )

        # 2. Separação de stems via Demucs -> 0 a 7 pts
        demucs_ok = bool(
            job_data.get(
                "demucs_stems_separated",
                job_data.get(
                    "demucs_applied",
                    audio_data.get(
                        "demucs_stems_separated",
                        audio_data.get("demucs_applied", False),
                    ),
                ),
            )
        )
        demucs_pts = 7.0 if demucs_ok else 0.0
        checklist["demucs_stems_separated"] = demucs_ok
        if not demucs_ok:
            recommendations.append(
                "Executar separação de stems via Demucs para remover a voz original preservando SFX/ambience originais."
            )

        # 3. Normalização em -14 LUFS -> 0 a 8 pts
        lufs_val = job_data.get(
            "integrated_lufs",
            job_data.get(
                "lufs",
                audio_data.get("integrated_lufs", audio_data.get("lufs", None)),
            ),
        )
        if lufs_val is None:
            lufs_pts = 0.0
            checklist["lufs_normalized_minus_14"] = False
            recommendations.append(
                "Medição LUFS ausente. Aplique filtro FFmpeg loudnorm=I=-14:TP=-1.5:LRA=11."
            )
        else:
            lufs = float(lufs_val)
            deviation = abs(lufs - self.TARGET_LUFS)
            if deviation <= 0.5:
                lufs_pts = 8.0
            elif deviation <= self.LUFS_TOLERANCE:
                lufs_pts = 6.5
            elif deviation <= 2.5:
                lufs_pts = 3.5
            else:
                lufs_pts = 0.5

            checklist["lufs_normalized_minus_14"] = deviation <= self.LUFS_TOLERANCE
            if not checklist["lufs_normalized_minus_14"]:
                recommendations.append(
                    f"Loudness fora do alvo do YouTube ({lufs:.1f} LUFS vs alvo -14.0 LUFS). Normalize com loudnorm."
                )

        return min(25.0, max(0.0, sync_pts + demucs_pts + lufs_pts))

    def _score_originality_anti_content_id(
        self,
        job_data: dict[str, Any],
        checklist: dict[str, bool],
        recommendations: list[str],
    ) -> float:
        """
        Audita requisitos anti-strike / anti-duplicação (0 a 25 pontos):
        1. % de cenas talking-head substituídas por Imagen 3 / B-roll (0 a 8 pts)
        2. Aplicação de LUT / Color Grading (0 a 5 pts)
        3. Crop dinâmico >= 6% (0 a 5 pts)
        4. Speed-ramping / variação de velocidade (0 a 4 pts)
        5. Permutação / reordenação de cenas (0 a 3 pts)
        """
        orig_data = (
            job_data.get("originality_data")
            or job_data.get("anti_content_id")
            or {}
        )

        # 1. Substituição de Talking-Head por Imagen 3 / B-roll (0 a 8 pts)
        th_replaced_pct = float(
            job_data.get(
                "talking_head_replaced_pct",
                orig_data.get(
                    "talking_head_replaced_pct",
                    job_data.get("broll_replacement_pct", 0.0),
                ),
            )
            or 0.0
        )
        # Se foi passado em fração (ex: 0.95), converte para percentual
        if 0.0 < th_replaced_pct <= 1.0:
            th_replaced_pct *= 100.0

        if th_replaced_pct >= 90.0:
            th_pts = 8.0
        elif th_replaced_pct >= 70.0:
            th_pts = 5.5 + ((th_replaced_pct - 70.0) / 20.0) * 2.5
        elif th_replaced_pct >= 40.0:
            th_pts = 2.5 + ((th_replaced_pct - 40.0) / 30.0) * 3.0
        else:
            th_pts = (th_replaced_pct / 40.0) * 2.0 if th_replaced_pct > 0 else 0.0

        checklist["talking_head_replaced"] = th_replaced_pct >= 80.0
        if not checklist["talking_head_replaced"]:
            recommendations.append(
                f"Substituição de cenas talking-head insuficiente ({th_replaced_pct:.1f}% < 80%). Substitua rostos originais por assets Imagen 3 ou B-roll."
            )

        # 2. Aplicação de LUT / Color Grading (0 a 5 pts)
        lut_applied = bool(
            job_data.get(
                "lut_applied",
                job_data.get(
                    "color_grading_applied",
                    orig_data.get(
                        "lut_applied", orig_data.get("color_grading_applied", False)
                    ),
                ),
            )
        )
        lut_pts = 5.0 if lut_applied else 0.0
        checklist["lut_color_grading_applied"] = lut_applied
        if not lut_applied:
            recommendations.append(
                "Aplicar LUT / Color Grading cinematográfico para alterar a assinatura cromática do frame."
            )

        # 3. Crop dinâmico >= 6% (0 a 5 pts)
        crop_pct = float(
            job_data.get(
                "dynamic_crop_pct",
                orig_data.get(
                    "dynamic_crop_pct", job_data.get("crop_factor_pct", 0.0)
                ),
            )
            or 0.0
        )
        if 0.0 < crop_pct < 1.0:
            crop_pct *= 100.0

        if crop_pct >= self.MIN_DYNAMIC_CROP_PCT:
            crop_pts = 5.0
        elif crop_pct >= 3.0:
            crop_pts = 2.5
        else:
            crop_pts = 0.0

        checklist["dynamic_crop_gte_6pct"] = crop_pct >= self.MIN_DYNAMIC_CROP_PCT
        if not checklist["dynamic_crop_gte_6pct"]:
            recommendations.append(
                f"Crop dinâmico ({crop_pct:.1f}%) abaixo do mínimo de 6%. Aplique zoom/pan Ken Burns >= 6% para quebrar hash visual."
            )

        # 4. Speed-ramping (0 a 4 pts)
        speed_ramp = bool(
            job_data.get(
                "speed_ramping_applied",
                orig_data.get(
                    "speed_ramping_applied",
                    job_data.get("speed_ramp", orig_data.get("speed_ramp", False)),
                ),
            )
        )
        speed_pts = 4.0 if speed_ramp else 0.0
        checklist["speed_ramping_applied"] = speed_ramp
        if not speed_ramp:
            recommendations.append(
                "Ativar speed-ramping sutil (ex: 1.04x-1.08x com variação não-linear) nos clipes originais."
            )

        # 5. Permutação de cenas (0 a 3 pts)
        scene_permuted = bool(
            job_data.get(
                "scene_permutation_applied",
                orig_data.get(
                    "scene_permutation_applied",
                    job_data.get("scenes_permuted", False),
                ),
            )
        )
        perm_pts = 3.0 if scene_permuted else 0.0
        checklist["scene_permutation_applied"] = scene_permuted
        if not scene_permuted:
            recommendations.append(
                "Aplicar permutação temporal de sub-cenas/B-roll para evitar correspondência sequencial no Content ID."
            )

        total_orig = min(25.0, max(0.0, th_pts + lut_pts + crop_pts + speed_pts + perm_pts))
        checklist["anti_content_id_safe"] = total_orig >= 18.0
        return total_orig

    # -------------------------------------------------------------------------
    # 2. POST-PUBLISH PERFORMANCE SCORE (PPPS 0-100) - PÓS-PUBLICAÇÃO
    # -------------------------------------------------------------------------
    def calculate_ppps(
        self,
        published_metrics: dict[str, Any],
        channel_baseline: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Calcula o Post-Publish Performance Score (0 a 100) Pós-Publicação:
        - CTR da Thumbnail: peso 35% (0 a 35 pontos)
        - Retenção Média % / AVD: peso 40% (0 a 40 pontos)
        - Velocidade VPH nas primeiras 48h: peso 15% (0 a 15 pontos)
        - Conversão de Shorts para Vídeo Longo: peso 10% (0 a 10 pontos)

        Gera insights automáticos para retroalimentar o Gemini nos próximos vídeos.
        """
        if not isinstance(published_metrics, dict):
            raise TypeError("published_metrics deve ser um dicionário válido.")

        baseline = channel_baseline or {}
        insights: list[str] = []

        # Extração das métricas publicadas
        ctr = float(
            published_metrics.get(
                "ctr_pct",
                published_metrics.get(
                    "ctr", published_metrics.get("thumbnail_ctr_pct", 0.0)
                ),
            )
            or 0.0
        )
        avd_pct = float(
            published_metrics.get(
                "avd_pct",
                published_metrics.get(
                    "retention_pct",
                    published_metrics.get("average_view_percentage", 0.0),
                ),
            )
            or 0.0
        )
        vph_48h = float(
            published_metrics.get(
                "vph_48h",
                published_metrics.get(
                    "vph", published_metrics.get("views_per_hour_48h", 0.0)
                ),
            )
            or 0.0
        )
        shorts_conv_pct = float(
            published_metrics.get(
                "shorts_to_long_conversion_pct",
                published_metrics.get(
                    "shorts_conversion_pct",
                    published_metrics.get("bridge_conversion_pct", 0.0),
                ),
            )
            or 0.0
        )

        # Baselines do canal (com defaults realistas para canais dark de alta performance)
        base_ctr = max(
            0.5,
            float(
                baseline.get(
                    "ctr_pct", baseline.get("ctr", baseline.get("avg_ctr_pct", 5.5))
                )
                or 5.5
            ),
        )
        base_avd = max(
            5.0,
            float(
                baseline.get(
                    "avd_pct",
                    baseline.get("retention_pct", baseline.get("avg_avd_pct", 45.0)),
                )
                or 45.0
            ),
        )
        base_vph = max(
            10.0,
            float(
                baseline.get(
                    "vph_48h", baseline.get("vph", baseline.get("avg_vph", 150.0))
                )
                or 150.0
            ),
        )
        base_conv = max(
            0.2,
            float(
                baseline.get(
                    "shorts_to_long_conversion_pct",
                    baseline.get("shorts_conversion_pct", 2.0),
                )
                or 2.0
            ),
        )

        # 1. CTR Score (Peso 35% -> 0 a 35 pontos)
        # Excelente quando CTR >= 10% ou >= 1.5x baseline
        ctr_ratio = ctr / base_ctr
        ctr_abs_norm = min(1.0, ctr / 10.0)
        ctr_rel_norm = min(1.0, ctr_ratio / 1.5)
        ctr_score = round(35.0 * (0.55 * ctr_abs_norm + 0.45 * ctr_rel_norm), 2)

        # 2. Retenção Média / AVD Score (Peso 40% -> 0 a 40 pontos)
        # Excelente quando AVD >= 65% ou >= 1.35x baseline
        avd_ratio = avd_pct / base_avd
        avd_abs_norm = min(1.0, avd_pct / 65.0)
        avd_rel_norm = min(1.0, avd_ratio / 1.35)
        avd_score = round(40.0 * (0.55 * avd_abs_norm + 0.45 * avd_rel_norm), 2)

        # 3. Velocidade VPH 48h Score (Peso 15% -> 0 a 15 pontos)
        vph_ratio = vph_48h / base_vph
        vph_abs_norm = min(1.0, vph_48h / 500.0)
        vph_rel_norm = min(1.0, vph_ratio / 2.0)
        vph_score = round(15.0 * (0.45 * vph_abs_norm + 0.55 * vph_rel_norm), 2)

        # 4. Conversão Shorts -> Vídeo Longo (Peso 10% -> 0 a 10 pontos)
        conv_ratio = shorts_conv_pct / base_conv
        conv_abs_norm = min(1.0, shorts_conv_pct / 5.0)
        conv_rel_norm = min(1.0, conv_ratio / 1.6)
        conv_score = round(10.0 * (0.5 * conv_abs_norm + 0.5 * conv_rel_norm), 2)

        total_ppps = round(
            min(100.0, max(0.0, ctr_score + avd_score + vph_score + conv_score)), 2
        )
        grade = self._map_pqs_grade(total_ppps)

        deltas = {
            "ctr_delta_pct": round(ctr - base_ctr, 2),
            "avd_delta_pct": round(avd_pct - base_avd, 2),
            "vph_ratio_vs_baseline": round(vph_ratio, 2),
            "shorts_conversion_delta_pct": round(shorts_conv_pct - base_conv, 2),
        }

        # Geração de insights acionáveis para retroalimentar o Gemini
        if ctr < base_ctr or ctr < 5.0:
            insights.append(
                f"GEMINI_THUMB_TITLE: CTR ({ctr:.1f}%) abaixo do esperado (baseline {base_ctr:.1f}%). Aumentar contraste visual na Thumbnail, reduzir texto para <= 3 palavras e testar gatilho de curiosidade negativa no título."
            )
        elif ctr >= base_ctr * 1.25:
            insights.append(
                f"GEMINI_THUMB_TITLE: CTR vencedor ({ctr:.1f}% vs {base_ctr:.1f}%). Replicar estrutura semântica do título e padrão de composição da Thumbnail no próximo vídeo do canal."
            )

        if avd_pct < base_avd or avd_pct < 40.0:
            insights.append(
                f"GEMINI_SCRIPT_PACING: Retenção média ({avd_pct:.1f}%) abaixo do baseline ({base_avd:.1f}%). Encurtar introdução para < 12s, antecipar o primeiro Open Loop e aumentar densidade de cortes nos primeiros 60s."
            )
        elif avd_pct >= 55.0:
            insights.append(
                f"GEMINI_SCRIPT_PACING: Alta retenção ({avd_pct:.1f}%). Preservar cadência narrativa e estrutura de Open Loops deste roteiro como template do canal."
            )

        if vph_ratio < 0.85:
            insights.append(
                f"GEMINI_TOPIC_SELECTION: Tração inicial lenta ({vph_48h:.0f} VPH vs {base_vph:.0f} VPH). Refinar filtro de sub-nicho para tópicos com maior volume de busca imediata."
            )
        elif vph_ratio >= 1.5:
            insights.append(
                f"GEMINI_TOPIC_SELECTION: Forte velocidade algorítmica ({vph_48h:.0f} VPH, {vph_ratio:.1f}x acima do canal). Produzir parte 2 ou spin-off imediato sobre o mesmo ângulo."
            )

        if shorts_conv_pct < base_conv or shorts_conv_pct < 1.5:
            insights.append(
                f"GEMINI_SHORTS_BRIDGE: Conversão de Shorts ({shorts_conv_pct:.2f}%) baixa. Cortar o Short exatamente no clímax do Open Loop com CTA direto para o vídeo relacionado."
            )
        else:
            insights.append(
                f"GEMINI_SHORTS_BRIDGE: Funil Shorts->Longo eficiente ({shorts_conv_pct:.2f}%). Manter gancho de clímax interrompido nos próximos 3 Shorts."
            )

        feedback_prompt = (
            "AJUSTE DE RETROALIMENTAÇÃO GEMINI (PPPS="
            f"{total_ppps}/100, Nota={grade}): "
            + " | ".join(insights)
        )

        component_scores = {
            "ctr_score": ctr_score,
            "avd_retention_score": avd_score,
            "vph_48h_score": vph_score,
            "shorts_conversion_score": conv_score,
        }

        result = PPPSResult(
            total_score=total_ppps,
            ppps_score=total_ppps,
            grade=grade,
            ctr_score=ctr_score,
            avd_retention_score=avd_score,
            vph_48h_score=vph_score,
            shorts_conversion_score=conv_score,
            component_scores=component_scores,
            vs_baseline_deltas=deltas,
            insights=insights,
            gemini_feedback_prompt=feedback_prompt,
        )
        return result.to_dict()

    @staticmethod
    def _map_pqs_grade(score: float) -> str:
        """Mapeia o score numérico (0-100) para nota conceitual."""
        if score >= 90.0:
            return "S"
        if score >= 82.0:
            return "A"
        if score >= 75.0:
            return "B"
        if score >= 60.0:
            return "C"
        return "REPROVADO"
