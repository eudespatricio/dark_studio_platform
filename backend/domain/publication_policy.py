"""
Dark Studio Platform — Unified Publication & Quality Policy (P0.2)
Single source of truth for duration, resolution, audio mastering,
PQS quality scoring thresholds, safety gates, and multi-channel cadence rules.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Tuple


POLICY_VERSION: str = "2026.10-P0-UNIFIED"


class UploadState(str, Enum):
    """Explicit state machine for video publishing lifecycle (eliminates ambiguous simulated IDs)."""
    PENDING = "PENDING"
    AUDITING = "AUDITING"
    UPLOADING = "UPLOADING"
    UPLOADED = "UPLOADED"
    SCHEDULED = "SCHEDULED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    DRY_RUN_COMPLETED = "DRY_RUN_COMPLETED"


@dataclass(frozen=True)
class VideoFormatRules:
    format_name: str
    min_duration_sec: float
    max_duration_sec: float
    target_width: int
    target_height: int
    min_distinct_scenes: int
    min_file_size_mb: float
    max_consecutive_static_sec: float = 3.5


@dataclass(frozen=True)
class AudioMasteringRules:
    target_lufs: float = -14.0
    lufs_tolerance_db: float = 1.5
    max_true_peak_dbtp: float = -1.0
    max_sync_drift_ms: float = 50.0
    ducking_attenuation_db: float = -14.0
    ducking_attack_ms: float = 25.0
    ducking_release_ms: float = 380.0


@dataclass(frozen=True)
class QualityGateRules:
    min_pqs_score: float = 78.0
    min_council_consensus_score: float = 78.0
    audio_lufs_weight: float = 0.20
    whisper_sync_weight: float = 0.25
    visual_dynamism_weight: float = 0.20
    originality_weight: float = 0.20
    narrative_hook_weight: float = 0.15


@dataclass(frozen=True)
class PublicationSafetyRules:
    # Fail-closed default: auto-publishing must be explicitly enabled
    auto_publish_enabled: bool = field(
        default_factory=lambda: os.getenv("AUTO_PUBLISH_ENABLED", "false").lower() in ("true", "1")
    )
    min_cooldown_minutes: float = 90.0
    duplicate_lookback_days: int = 7
    require_real_oauth_verification: bool = True
    contains_synthetic_media_default: bool = True


# Standard format definitions
LONG_16_9_FULLDOC_MIN_SEC = 480.0  # usado quando require_full_doc=True (fase 3 / monetizado)

LONG_16_9_RULES = VideoFormatRules(
    format_name="LONG_16_9",
    # Fase 1 (rampa, canais < 1.000 inscritos): mínimo 150s, alinhado a best_practices_registry.json
    # (min_long_duration_sec_phase1). 480s (midroll/autoridade) só quando require_full_doc=True ou pós-monetização.
    min_duration_sec=150.0,
    max_duration_sec=1800.0,  # 30 min max for standard documentary
    target_width=1920,
    target_height=1080,
    min_distinct_scenes=8,
    min_file_size_mb=10.0,
    max_consecutive_static_sec=3.5,
)

SHORT_9_16_RULES = VideoFormatRules(
    format_name="SHORT_9_16",
    min_duration_sec=28.0,
    max_duration_sec=60.0,
    target_width=1080,
    target_height=1920,
    min_distinct_scenes=5,
    min_file_size_mb=1.0,
    max_consecutive_static_sec=3.0,
)

# Música (canal 4 / Music_Band): single ~3min, sessões longas e Shorts de música (hook de 15s+)
MUSIC_LONG_RULES = VideoFormatRules(
    format_name="MUSIC_LONG_16_9",
    min_duration_sec=120.0,
    max_duration_sec=14400.0,
    target_width=1920,
    target_height=1080,
    min_distinct_scenes=1,
    min_file_size_mb=5.0,
)

MUSIC_SHORT_RULES = VideoFormatRules(
    format_name="MUSIC_SHORT_9_16",
    min_duration_sec=15.0,
    max_duration_sec=60.0,
    target_width=1080,
    target_height=1920,
    min_distinct_scenes=1,
    min_file_size_mb=1.0,
)

AUDIO_RULES = AudioMasteringRules()
GATE_RULES = QualityGateRules()
SAFETY_RULES = PublicationSafetyRules()


def resolve_format_rules(video_format: str, is_music: bool = False) -> VideoFormatRules:
    """Returns canonical rules for a video format string (regras próprias para música)."""
    fmt = str(video_format or "").upper()
    is_short = "SHORT" in fmt or "9_16" in fmt or "9X16" in fmt
    if is_music:
        return MUSIC_SHORT_RULES if is_short else MUSIC_LONG_RULES
    return SHORT_9_16_RULES if is_short else LONG_16_9_RULES


def compute_unified_pqs(
    audio_lufs_score: float,
    whisper_sync_score: float,
    visual_dynamism_score: float,
    originality_fingerprint_score: float,
    narrative_hook_score: float,
) -> float:
    """
    Computes unified PQS (0.0 to 100.0) using canonical weights.
    Weights: 20% audio + 25% sync + 20% visual + 20% originality + 15% narrative.
    """
    total = (
        audio_lufs_score * GATE_RULES.audio_lufs_weight
        + whisper_sync_score * GATE_RULES.whisper_sync_weight
        + visual_dynamism_score * GATE_RULES.visual_dynamism_weight
        + originality_fingerprint_score * GATE_RULES.originality_weight
        + narrative_hook_score * GATE_RULES.narrative_hook_weight
    )
    return round(max(0.0, min(100.0, total)), 2)
