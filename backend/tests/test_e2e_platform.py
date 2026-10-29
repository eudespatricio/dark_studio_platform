"""
Suíte Completa de Testes Integrados End-to-End (E2E) — Dark Studio Platform.

Valida:
1. Descoberta e Inteligência Competitiva (`NicheScanner.select_top_3_niches()` e `OutlierHunter.hunt_outliers()` com `outlier_score >= 3.0x` + Heatmap).
2. Motores de IA (`LLMEngine`, `TTSEngine`, `TranscriberEngine`) e FinOps tracking.
3. Motores Audiovisuais (`SubtitleMaker`, `VideoRemixer`, `VideoRenderer`, `ThumbnailMaker`).
4. Todas as rotas REST da API FastAPI (`backend/main.py`) + WebSocket `/ws/pipeline`.
"""

from __future__ import annotations

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.core.llm_engine import LLMEngine
from backend.core.quality_scorer import QualityScorer
from backend.core.subtitle_maker import SubtitleMaker
from backend.core.transcriber import TranscriberEngine
from backend.core.tts_engine import TTSEngine
from backend.discovery.niche_scanner import NicheScanner
from backend.discovery.outlier_hunter import OutlierHunter
from backend.main import app
from backend.media.remixer import VideoRemixer
from backend.media.thumbnail_maker import ThumbnailMaker
from backend.media.video_renderer import VideoRenderer


# ==============================================================================
# 1. Testes do NicheScanner (Top 3 Nichos & Fórmula NOS) e OutlierHunter
# ==============================================================================
class TestDiscoveryEngines:
    """Testa NicheScanner e OutlierHunter."""

    def test_niche_scanner_select_top_3_niches(self) -> None:
        scanner = NicheScanner(target_language="pt-BR")
        top_3 = scanner.select_top_3_niches()

        assert len(top_3) == 3
        assert top_3[0].rank == 1
        assert top_3[1].rank == 2
        assert top_3[2].rank == 3
        # Verifica ordenação decrescente de NOS Score
        assert top_3[0].nos_score >= top_3[1].nos_score >= top_3[2].nos_score
        for item in top_3:
            assert 75.0 <= item.nos_score <= 100.0
            assert item.metrics.estimated_rpm_usd > 0
            assert len(item.source_languages) >= 2
            assert item.channel_blueprint.target_language == "pt-BR"

    def test_outlier_hunter_strict_filter_and_heatmap_shorts(self) -> None:
        hunter = OutlierHunter(min_outlier_score=3.0, min_vph=150.0)
        outliers = hunter.hunt_outliers()

        assert len(outliers) >= 3
        for candidate in outliers:
            assert candidate.outlier_score >= 3.0
            assert candidate.vph >= 150.0
            assert len(candidate.heatmap_peaks) >= 1
            assert len(candidate.recommended_shorts_cuts) >= 1
            first_cut = candidate.recommended_shorts_cuts[0]
            assert 20.0 <= first_cut.duration_sec <= 60.0
            assert first_cut.peak_intensity >= 0.65


# ==============================================================================
# 2. Testes dos Motores de IA e Engenharia Audiovisual
# ==============================================================================
class TestAIAndAudiovisualEngines:
    """Testa LLMEngine, TTSEngine, TranscriberEngine, SubtitleMaker, VideoRemixer, VideoRenderer e ThumbnailMaker."""

    def test_llm_engine_transcreation_and_finops(self) -> None:
        llm = LLMEngine()
        result = llm.transcreate_validated_script(
            source_transcript="In 2025, an underground megaproject worth 170 billion dollars silently halted operations.",
            source_metadata={
                "title": "Why This Megaproject Stopped",
                "original_language": "en-US",
                "outlier_score": 7.7,
                "video_id": "test_outlier_01",
            },
            target_language="pt-BR",
            retention_heatmap=[{"start_sec": 120, "end_sec": 165, "intensity": 0.96}],
        )

        assert "long_script_16_9" in result
        assert "short_script_9_16" in result
        assert "seo_package" in result
        assert "finops_usage" in result
        finops = llm.get_finops_summary()
        assert finops["total_calls"] >= 1
        assert finops["total_tokens"] > 0

    def test_tts_engine_synthesis_and_sha256_cache(self, tmp_path: Path) -> None:
        tts = TTSEngine(cache_dir=str(tmp_path / "tts_cache"))
        narration = "Nos primeiros quinze segundos, um detalhe invisível mudou toda a geopolítica moderna."

        res1 = tts.synthesize_speech(text=narration, channel_id="ch_1_investigativo")
        assert Path(res1["audio_path"]).exists()
        assert res1["duration_sec"] >= 2.0

        # Segunda chamada idêntica deve acionar cache SHA-256 com custo 0
        res2 = tts.synthesize_speech(text=narration, channel_id="ch_1_investigativo")
        assert res2["cache_hit"] is True
        assert res2["estimated_cost_usd"] == 0.0

    def test_transcriber_engine_word_timestamps_and_chunks(self) -> None:
        transcriber = TranscriberEngine(lazy_load=True)
        res = transcriber.transcribe_foreign_video(
            audio_or_video_path="non_existent_sample.wav",
            source_language="en",
            fallback_transcript="This secret megaproject cost billions of dollars and collapsed overnight.",
            estimated_duration_sec=12.0,
        )

        assert len(res["word_timestamps"]) >= 8
        assert len(res["caption_chunks"]) >= 2
        assert res["word_timestamps"][0]["start"] >= 0.0
        assert res["word_timestamps"][-1]["end"] <= 12.5

    def test_subtitle_maker_dual_ass_16_9_and_9_16(self, tmp_path: Path) -> None:
        maker = SubtitleMaker(output_dir=tmp_path)
        dual = maker.generate_dual_profiles(
            words_or_text="O segredo bilionário que mudou o sistema financeiro global para sempre.",
            base_name="e2e_test_sub",
            total_duration=8.0,
        )

        assert "16:9" in dual and "9:16" in dual
        path_16_9 = Path(dual["16:9"]["subtitle_path"])
        path_9_16 = Path(dual["9:16"]["subtitle_path"])
        assert path_16_9.exists()
        assert path_9_16.exists()
        assert "PlayResX: 1920" in path_16_9.read_text(encoding="utf-8")
        assert "PlayResX: 1080" in path_9_16.read_text(encoding="utf-8")

    def test_video_remixer_speed_ramping_and_anti_content_id(self) -> None:
        remixer = VideoRemixer()
        scenes = [
            {"scene_id": 1, "start_sec": 0.0, "end_sec": 4.5, "has_talking_head": False},
            {"scene_id": 2, "start_sec": 4.5, "end_sec": 9.0, "has_talking_head": True},
            {"scene_id": 3, "start_sec": 9.0, "end_sec": 13.5, "has_talking_head": False},
            {"scene_id": 4, "start_sec": 13.5, "end_sec": 18.0, "has_talking_head": False},
        ]
        plan = remixer.create_remix_plan(
            scenes=scenes,
            target_narration_duration_sec=16.5,
            enable_semantic_shuffle=True,
        )

        assert len(plan.clips) == 4
        assert plan.min_speed_factor >= 0.85
        assert plan.max_speed_factor <= 1.15
        assert plan.broll_replacements_count >= 1
        ff_filter = plan.anti_content_id.build_ffmpeg_filter(is_talking_head=False)
        assert "crop=" in ff_filter and "eq=contrast=" in ff_filter

    def test_video_renderer_and_thumbnail_maker(self, tmp_path: Path) -> None:
        # 1. ThumbnailMaker 1280x720
        thumb_maker = ThumbnailMaker(thumbnails_dir=tmp_path / "thumbs")
        thumb = thumb_maker.create_thumbnail(
            headline_text="COLAPSO OCULTO",
            badge_text="DOCUMENTÁRIO",
            job_id="e2e_job",
        )
        assert Path(thumb.output_png_path).exists()
        assert Path(thumb.output_jpg_path).exists()
        assert thumb.width == 1280 and thumb.height == 720

        # 2. VideoRenderer (16:9 e 9:16 com normalização -14 LUFS)
        tts = TTSEngine(cache_dir=str(tmp_path / "tts"))
        narration_res = tts.synthesize_speech(
            text="Teste de renderização audiovisual automatizada do Dark Studio Platform.",
            output_filename=str(tmp_path / "narration.wav"),
        )
        renderer = VideoRenderer(renders_dir=tmp_path / "renders")
        artifact_16_9 = renderer.render_video(
            source_video_path=tmp_path / "missing_src.mp4",
            narration_audio_path=narration_res["audio_path"],
            output_filename="e2e_16x9.mp4",
            aspect_ratio="16:9",
            duration_sec=3.0,
        )
        assert Path(artifact_16_9.output_mp4_path).exists()
        assert artifact_16_9.target_lufs == -14.0
        assert "loudnorm=I=-14.0" in artifact_16_9.audio_filtergraph


# ==============================================================================
# 3. Testes End-to-End da API FastAPI (`backend/main.py`) + WebSocket
# ==============================================================================
class TestFastAPICommandCenterE2E:
    """Testa todas as rotas REST e WebSocket do Command Center via TestClient."""

    def test_all_rest_endpoints_and_websocket(self) -> None:
        with TestClient(app) as client:
            # 1. GET / (Entrega do frontend/index.html com os 6 painéis)
            r_root = client.get("/")
            assert r_root.status_code == 200
            html = r_root.text
            assert "Dark Studio" in html
            # Confirma presença das seções/painéis na interface
            assert "niches" in html.lower()
            assert "pipeline" in html.lower()
            assert "studio" in html.lower()
            assert "finops" in html.lower()
            assert "settings" in html.lower() or "api" in html.lower()

            # 2. GET /api/dashboard
            r_dash = client.get("/api/dashboard")
            assert r_dash.status_code == 200
            dash_data = r_dash.json()
            assert dash_data["status"] == "ok"
            assert len(dash_data["top3_channels"]) == 3
            assert len(dash_data["top3_niches"]) == 3
            assert dash_data["summary"]["avg_pqs_score"] >= 75.0

            # 3. GET /api/niches/top3 e POST /api/niches/scan
            r_top3 = client.get("/api/niches/top3")
            assert r_top3.status_code == 200
            assert len(r_top3.json()["top3_niches"]) == 3

            r_scan = client.post(
                "/api/niches/scan",
                json={"target_languages": ["pt-BR"], "min_nos_score": 75.0},
            )
            assert r_scan.status_code == 200
            scan_data = r_scan.json()
            assert scan_data["status"] == "ok"
            assert len(scan_data["top3_niches"]) == 3

            # 4. GET /api/outliers
            r_out = client.get("/api/outliers")
            assert r_out.status_code == 200
            out_data = r_out.json()
            assert out_data["count"] >= 3
            for o in out_data["outliers"]:
                assert o["outlier_score"] >= 3.0

            # 5. GET /api/pipeline/jobs e POST /api/pipeline/start
            r_jobs = client.get("/api/pipeline/jobs")
            assert r_jobs.status_code == 200
            assert r_jobs.json()["count"] >= 1

            r_start = client.post(
                "/api/pipeline/start",
                json={"channel_id": 1, "outlier_id": 1, "step_delay_sec": 0.05},
            )
            assert r_start.status_code == 200
            start_data = r_start.json()
            assert start_data["status"] == "started"
            assert "job_code" in start_data["job"]

            # 6. GET /api/studio/1
            r_studio = client.get("/api/studio/1")
            assert r_studio.status_code == 200
            studio_data = r_studio.json()
            assert studio_data["status"] == "ok"
            assert "long_form_16_9" in studio_data["studio_preview"]
            assert "short_9_16" in studio_data["studio_preview"]
            assert "pqs_audit" in studio_data["studio_preview"]

            # 7. GET /api/analytics e GET /api/finops
            r_analytics = client.get("/api/analytics")
            assert r_analytics.status_code == 200
            analytics_data = r_analytics.json()
            assert len(analytics_data["growth_series"]) == 3
            assert len(analytics_data["ppps_records"]) >= 1

            r_finops = client.get("/api/finops")
            assert r_finops.status_code == 200
            finops_data = r_finops.json()
            assert "unit_economics" in finops_data
            assert finops_data["unit_economics"]["total_package_cost_usd"] > 0

            # 8. GET /api/settings/apis, POST /api/settings/apis e POST /api/settings/apis/test
            r_apis_get = client.get("/api/settings/apis")
            assert r_apis_get.status_code == 200
            apis_state = r_apis_get.json()
            assert "gemini" in apis_state["providers"]
            assert "elevenlabs" in apis_state["providers"]
            assert "youtube" in apis_state["providers"]
            assert "pexels" in apis_state["providers"]
            assert len(apis_state["channel_voices"]) == 3

            r_apis_post = client.post(
                "/api/settings/apis",
                json={
                    "gemini_model_fast": "gemini-2.5-flash",
                    "finops_daily_budget_usd": 15.0,
                    "circuit_breaker_enabled": True,
                },
            )
            assert r_apis_post.status_code == 200
            assert r_apis_post.json()["finops_circuit_breaker"]["daily_budget_usd"] == 15.0

            r_apis_test = client.post(
                "/api/settings/apis/test",
                json={"provider": "all"},
            )
            assert r_apis_test.status_code == 200
            test_diag = r_apis_test.json()
            assert test_diag["status"] == "ok"
            assert test_diag["diagnostics"]["gemini"]["status"] == "healthy"
            assert test_diag["diagnostics"]["local_engines"]["status"] == "healthy"

            # 9. Conexão WebSocket /ws/pipeline
            with client.websocket_connect("/ws/pipeline") as ws:
                # Recebe mensagem de boas-vindas ou envia ping
                ws.send_json({"action": "ping"})
                received_pong = False
                for _ in range(3):
                    msg = ws.receive_json()
                    if msg.get("event") == "pong":
                        received_pong = True
                        break
                assert received_pong is True
