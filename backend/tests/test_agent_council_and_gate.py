"""
Integration & Unit Test Suite for the 7-Agent Money-Making Council,
Anti-Garbage Physical Sentinel (OpenCV/FFprobe), 3-Phase Monetization Ramp Plan,
and N-Channel Category Fleet Manager.
"""

from pathlib import Path

from backend.agents import (
    CATEGORY_CLUSTERS,
    AntiGarbageSentinelAgent,
    ConsensusCouncil,
    PortfolioFleetManagerAgent,
    ScheduleCadenceAuditorAgent,
)
from backend.publisher.youtube_uploader import UploadMetadata, YouTubeMultiChannelUploader

BASE_DIR = Path("/home/eudespatricio/dark_studio_platform")


def test_anti_garbage_sentinel_approves_real_11min_documentary():
    doc_path = BASE_DIR / "workspace/renders/quant_long_11min_doc_16x9.mp4"
    assert doc_path.exists(), "Real 11m50s documentary file must exist on disk"

    sentinel = AntiGarbageSentinelAgent()
    vote = sentinel.evaluate(
        {
            "video_path": str(doc_path),
            "format": "long_16x9",
            "require_full_doc": True,
        }
    )
    assert vote.veto is False
    assert vote.approved is True
    assert vote.metrics["duration_sec"] >= 700.0
    assert vote.metrics["background_visual_std"] >= 15.0
    assert vote.metrics["has_audio"] is True


def test_anti_garbage_sentinel_vetoes_corrupt_or_missing_video(tmp_path):
    stub_mp4 = tmp_path / "corrupt_stub.mp4"
    stub_mp4.write_bytes(b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom")

    sentinel = AntiGarbageSentinelAgent()
    vote = sentinel.evaluate({"video_path": str(stub_mp4), "format": "long_16x9"})
    assert vote.veto is True
    assert vote.approved is False
    assert vote.score == 0.0


def test_youtube_uploader_blocks_garbage_and_isolates_oauth_tokens(tmp_path):
    stub_mp4 = tmp_path / "garbage_black.mp4"
    stub_mp4.write_bytes(b"\x00\x00\x00\x18ftypmp42")

    uploader = YouTubeMultiChannelUploader()
    # Channel 2 must never resolve to Channel 1's token
    ch1_tok = uploader._has_valid_oauth_token("1")
    ch2_tok = uploader._has_valid_oauth_token("2")
    ch99_tok = uploader._has_valid_oauth_token("channel_99_nonexistent")
    assert ch99_tok is None
    if ch1_tok and ch2_tok:
        assert ch1_tok.name != ch2_tok.name

    meta = UploadMetadata(
        channel_id="channel_test_sentinel",
        niche_id="quant_finance",
        title="Teste Bloqueio Anti-Garbage",
        description="Descrição de teste",
        tags=["quant", "teste"],
        video_format="LONG_16_9",
    )
    receipt = uploader.upload_video(str(stub_mp4), meta)
    assert receipt.youtube_video_id == "BLOCKED_MOCKUP"
    assert receipt.privacy_status == "blocked"


def test_3_phase_monetization_ramp_and_normalization():
    auditor = ScheduleCadenceAuditorAgent()

    # Phase 1: New channel (<1,000 subs / <4,000h) -> Ignition Ramp
    p1 = auditor.detect_channel_ramp_phase(subscribers=14, watch_hours=18.5, is_monetized=False)
    assert p1["active_phase_id"] == "PHASE_1_IGNITION_RAMP"
    assert "4 Shorts/dia" in p1["prescription"]["shorts_per_day"]

    # Phase 2: Qualified YPP (1,200 subs, 4,100h, monetized) -> Transition
    p2 = auditor.detect_channel_ramp_phase(subscribers=1200, watch_hours=4100.0, is_monetized=True)
    assert p2["active_phase_id"] == "PHASE_2_YPP_TRANSITION"

    # Phase 3: Consolidated Monetized (>3,000 subs, monetized) -> Post-Monetization Normalization
    p3 = auditor.detect_channel_ramp_phase(subscribers=8500, watch_hours=19000.0, is_monetized=True)
    assert p3["active_phase_id"] == "PHASE_3_MONETIZED_NORMALIZATION"
    assert "Super-Documentários/semana" in p3["prescription"]["long_videos_per_week"]


def test_7_agent_consensus_council_deliberation_and_fleet_clusters():
    council = ConsensusCouncil()
    assert len(council.agents) == 7

    doc_path = BASE_DIR / "workspace/renders/quant_long_11min_doc_16x9.mp4"
    verdict = council.deliberate(
        {
            "channel_id": 2,
            "channel_name": "Finanças Quânticas",
            "title": "O Algoritmo de US$ 100 Bilhões de Jim Simons: Wall Street e Hedge Funds",
            "script_text": "Como algoritmos quantitativos, derivativos, liquidez institucional e arbitragem de Wall Street criaram bilhões.",
            "video_path": str(doc_path),
            "format": "long_16x9",
            "require_full_doc": True,
            "scheduled_hour_brt": "17:30",
            "outlier_score": 11.4,
            "scene_count": 25,
            "has_subtitles": True,
            "base_rpm_usd": 18.40,
        }
    )
    assert verdict.vetoed is False
    assert verdict.approved_for_publish is True
    assert verdict.consensus_score >= 85.0
    assert verdict.midroll_eligible is True
    assert len(verdict.votes) == 7

    fleet = PortfolioFleetManagerAgent()
    assert len(CATEGORY_CLUSTERS) >= 5
    c_ai = fleet.resolve_cluster_for_channel("Singularity AI & Cyber Geopolitics", channel_id=5)
    assert c_ai["cluster_id"] == "CLUSTER_AI_CYBER_GEOPOLITICS"
