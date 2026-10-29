"""
Testes automatizados exaustivos para o motor QualityScorer (PQS & PPPS).
"""

from __future__ import annotations

import pytest

from backend.core.quality_scorer import QualityScorer


@pytest.fixture
def scorer() -> QualityScorer:
    return QualityScorer(quality_gate_threshold=75.0)


class TestPipelineQualityScorePQS:
    """Testes do Pipeline Quality Score (PQS 0-100) Pré-Publicação."""

    def test_pqs_perfect_s_grade_passes_gate(self, scorer: QualityScorer) -> None:
        job_data = {
            "outlier_score": 5.5,
            "vph": 620.0,
            "hook_strength": 95.0,
            "open_loops_count": 3,
            "avg_scene_duration_sec": 4.2,
            "avg_sync_error_ms": 35.0,
            "demucs_stems_separated": True,
            "integrated_lufs": -14.0,
            "talking_head_replaced_pct": 95.0,
            "lut_applied": True,
            "dynamic_crop_pct": 8.0,
            "speed_ramping_applied": True,
            "scene_permutation_applied": True,
        }

        res = scorer.calculate_pqs(job_data)

        assert res["total_score"] >= 95.0
        assert res["pqs_score"] == res["total_score"]
        assert res["grade"] == "S"
        assert res["passed_quality_gate"] is True
        assert res["outlier_strength_score"] == 25.0
        assert res["hook_and_pacing_score"] >= 24.0
        assert res["audio_sync_and_lufs_score"] == 25.0
        assert res["originality_anti_content_id_score"] == 25.0
        assert all(res["checklist"].values())
        assert len(res["recommendations"]) == 0

    def test_pqs_reprovado_low_metrics_blocked_by_gate(
        self, scorer: QualityScorer
    ) -> None:
        job_data = {
            "outlier_score": 1.2,
            "vph": 20.0,
            "hook_strength": 30.0,
            "open_loops_count": 0,
            "avg_scene_duration_sec": 12.5,
            "avg_sync_error_ms": 280.0,
            "demucs_stems_separated": False,
            "integrated_lufs": -20.0,
            "talking_head_replaced_pct": 20.0,
            "lut_applied": False,
            "dynamic_crop_pct": 1.0,
            "speed_ramping_applied": False,
            "scene_permutation_applied": False,
        }

        res = scorer.calculate_pqs(job_data)

        assert res["total_score"] < 40.0
        assert res["grade"] == "REPROVADO"
        assert res["passed_quality_gate"] is False
        assert any("BLOQUEIO QUALITY GATE" in r for r in res["recommendations"])
        assert res["checklist"]["outlier_gte_3x"] is False
        assert res["checklist"]["audio_sync_under_150ms"] is False
        assert res["checklist"]["demucs_stems_separated"] is False
        assert res["checklist"]["lufs_normalized_minus_14"] is False
        assert res["checklist"]["dynamic_crop_gte_6pct"] is False

    def test_pqs_nested_payload_and_scenes_list_calculation(
        self, scorer: QualityScorer
    ) -> None:
        job_data = {
            "source_video": {"outlier_multiplier": 3.5, "views_per_hour": 350.0},
            "script_data": {
                "hook_score": 8.5,  # escala 0-10 convertida automaticamente para 85
                "open_loops": ["loop_1", "loop_2"],
                "scenes": [
                    {"duration_sec": 4.0},
                    {"duration_sec": 5.0},
                    {"duration_sec": 4.5},
                ],
            },
            "audio_data": {
                "sync_drift_ms": 90.0,
                "demucs_applied": True,
                "lufs": -13.8,
            },
            "originality_data": {
                "talking_head_replaced_pct": 0.90,  # fração convertida para 90%
                "color_grading_applied": True,
                "dynamic_crop_pct": 0.07,  # fração convertida para 7%
                "speed_ramp": True,
                "scene_permutation_applied": True,
            },
        }

        res = scorer.calculate_pqs(job_data)

        assert res["passed_quality_gate"] is True
        assert res["total_score"] >= 85.0
        assert res["grade"] in ("A", "S")
        assert res["checklist"]["optimal_cut_pacing_3_to_6s"] is True
        assert res["checklist"]["audio_sync_under_150ms"] is True
        assert res["checklist"]["anti_content_id_safe"] is True

    def test_pqs_borderline_b_grade_passes_75_threshold(
        self, scorer: QualityScorer
    ) -> None:
        job_data = {
            "outlier_score": 3.1,
            "vph": 220.0,
            "hook_strength": 80.0,
            "open_loops_count": 2,
            "avg_scene_duration_sec": 5.0,
            "avg_sync_error_ms": 110.0,
            "demucs_stems_separated": True,
            "integrated_lufs": -14.6,
            "talking_head_replaced_pct": 82.0,
            "lut_applied": True,
            "dynamic_crop_pct": 6.5,
            "speed_ramping_applied": False,
            "scene_permutation_applied": False,
        }

        res = scorer.calculate_pqs(job_data)

        assert 75.0 <= res["total_score"] < 90.0
        assert res["passed_quality_gate"] is True
        assert res["grade"] in ("B", "A")

    def test_pqs_invalid_input_raises_type_error(self, scorer: QualityScorer) -> None:
        with pytest.raises(TypeError):
            scorer.calculate_pqs("invalid_payload")  # type: ignore[arg-type]


class TestPostPublishPerformanceScorePPPS:
    """Testes do Post-Publish Performance Score (PPPS 0-100) Pós-Publicação."""

    def test_ppps_viral_outperformance_generates_positive_feedback(
        self, scorer: QualityScorer
    ) -> None:
        published_metrics = {
            "ctr_pct": 11.2,
            "avd_pct": 68.0,
            "vph_48h": 540.0,
            "shorts_to_long_conversion_pct": 5.5,
        }
        channel_baseline = {
            "ctr_pct": 6.0,
            "avd_pct": 48.0,
            "vph_48h": 180.0,
            "shorts_to_long_conversion_pct": 2.2,
        }

        res = scorer.calculate_ppps(published_metrics, channel_baseline)

        assert res["total_score"] == 100.0
        assert res["ppps_score"] == 100.0
        assert res["grade"] == "S"
        assert res["ctr_score"] == 35.0
        assert res["avd_retention_score"] == 40.0
        assert res["vph_48h_score"] == 15.0
        assert res["shorts_conversion_score"] == 10.0
        assert res["vs_baseline_deltas"]["ctr_delta_pct"] > 0
        assert res["vs_baseline_deltas"]["vph_ratio_vs_baseline"] == 3.0
        assert "GEMINI_THUMB_TITLE" in res["gemini_feedback_prompt"]
        assert "GEMINI_SCRIPT_PACING" in res["gemini_feedback_prompt"]

    def test_ppps_underperforming_video_generates_corrective_insights(
        self, scorer: QualityScorer
    ) -> None:
        published_metrics = {
            "ctr_pct": 2.8,
            "avd_pct": 25.0,
            "vph_48h": 45.0,
            "shorts_to_long_conversion_pct": 0.5,
        }
        channel_baseline = {
            "ctr_pct": 6.0,
            "avd_pct": 46.0,
            "vph_48h": 160.0,
            "shorts_to_long_conversion_pct": 2.0,
        }

        res = scorer.calculate_ppps(published_metrics, channel_baseline)

        assert res["total_score"] < 50.0
        assert res["grade"] == "REPROVADO"
        assert any("abaixo do esperado" in i for i in res["insights"])
        assert any("Encurtar introdução" in i for i in res["insights"])
        assert any("Tração inicial lenta" in i for i in res["insights"])
        assert any("Conversão de Shorts" in i for i in res["insights"])

    def test_ppps_without_baseline_uses_defaults(self, scorer: QualityScorer) -> None:
        published_metrics = {
            "ctr": 7.5,
            "retention_pct": 52.0,
            "vph": 260.0,
            "bridge_conversion_pct": 3.2,
        }

        res = scorer.calculate_ppps(published_metrics)

        assert 70.0 <= res["total_score"] <= 95.0
        assert len(res["insights"]) >= 2
        assert isinstance(res["gemini_feedback_prompt"], str)

    def test_ppps_invalid_input_raises_type_error(self, scorer: QualityScorer) -> None:
        with pytest.raises(TypeError):
            scorer.calculate_ppps(None)  # type: ignore[arg-type]
