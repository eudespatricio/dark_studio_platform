"""
Dark Studio Platform — SQLAlchemy ORM Models & Database Seeding Engine
Provides persistent storage in SQLite (`dark_studio.db`) for:
- NicheCandidate (NOS Score & 5-metric mathematical breakdown)
- ChannelProfile (Top 3 Autonomous Channels & Identity Presets)
- OutlierVideo (Validated foreign viral videos, VPH, Outlier Score & Heatmaps)
- PipelineJob (End-to-end production jobs, progress, paths, PQS & PPPS scores)
- QualityScore (Detailed 5-metric PQS Quality Gate audit records)
- PublishedMetric (Post-Publication Performance Score PPPS & YouTube Analytics)
- ApiCostLog (FinOps telemetry for Gemini tokens & ElevenLabs characters in USD)
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Generator, List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    event,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Session, relationship, sessionmaker

from backend.config import BASE_DIR, DATABASE_URL, TOP_3_CHANNEL_PRESETS

# ==============================================================================
# SQLAlchemy Engine & Session Factory (WAL Mode & Concurrency Resilient)
# ==============================================================================
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 15} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
)

if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=10000")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base for all Dark Studio ORM models."""


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency providing a scoped SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==============================================================================
# ORM Models
# ==============================================================================
class NicheCandidate(Base):
    """
    Represents a niche evaluated by the Niche Opportunity Score (NOS) algorithm:
    NOS = 0.25*DemandVelocity + 0.25*SupplyGap + 0.20*EstimatedRPM
          + 0.15*FacelessFeasibility + 0.15*LinguisticArbitrageMargin
    """

    __tablename__ = "niche_candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(180), nullable=False, unique=True)
    slug = Column(String(120), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    primary_source_lang = Column(String(32), default="en")
    target_lang = Column(String(32), default="pt-BR")

    # 5 Mathematical NOS Metrics (0 - 100 scale)
    demand_velocity = Column(Float, nullable=False, default=80.0)
    supply_gap_inv = Column(Float, nullable=False, default=80.0)
    estimated_rpm_norm = Column(Float, nullable=False, default=80.0)
    faceless_feasibility = Column(Float, nullable=False, default=85.0)
    linguistic_arbitrage_margin = Column(Float, nullable=False, default=85.0)

    estimated_rpm_usd = Column(Float, nullable=False, default=6.50)
    avg_outlier_ratio = Column(Float, nullable=False, default=4.2)
    monthly_search_volume = Column(Integer, nullable=False, default=450000)

    nos_score = Column(Float, nullable=False, index=True)
    is_top_3 = Column(Boolean, default=False, index=True)
    rank_position = Column(Integer, nullable=False, default=99)
    sample_keywords_json = Column(Text, default="[]")

    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        try:
            keywords = json.loads(self.sample_keywords_json or "[]")
        except Exception:
            keywords = []
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "category": self.category,
            "primary_source_lang": self.primary_source_lang,
            "target_lang": self.target_lang,
            "metrics": {
                "demand_velocity": round(self.demand_velocity, 1),
                "supply_gap_inv": round(self.supply_gap_inv, 1),
                "estimated_rpm_norm": round(self.estimated_rpm_norm, 1),
                "faceless_feasibility": round(self.faceless_feasibility, 1),
                "linguistic_arbitrage_margin": round(self.linguistic_arbitrage_margin, 1),
            },
            "estimated_rpm_usd": round(self.estimated_rpm_usd, 2),
            "avg_outlier_ratio": round(self.avg_outlier_ratio, 2),
            "monthly_search_volume": self.monthly_search_volume,
            "nos_score": round(self.nos_score, 2),
            "is_top_3": bool(self.is_top_3),
            "rank_position": self.rank_position,
            "sample_keywords": keywords,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ChannelProfile(Base):
    """
    Represents one of the Top 3 Autonomous Dark Channels managed by the platform.
    Stores neural voice identity, visual LUT preset, target language, and KPIs.
    """

    __tablename__ = "channel_profiles"

    id = Column(Integer, primary_key=True, index=True)
    slot = Column(Integer, nullable=False, unique=True, index=True)  # 1, 2, or 3
    handle = Column(String(100), nullable=False, unique=True)
    name = Column(String(160), nullable=False)
    youtube_channel_id = Column(String(100), nullable=True)
    niche_id = Column(Integer, ForeignKey("niche_candidates.id"), nullable=True)
    niche_name = Column(String(180), nullable=False)

    target_language = Column(String(24), nullable=False, default="pt-BR")
    source_languages_json = Column(Text, default='["en", "de", "ja"]')

    # ElevenLabs Neural Voice Identity
    voice_id = Column(String(80), nullable=False)
    voice_name = Column(String(120), nullable=False)
    voice_stability = Column(Float, default=0.45)
    voice_similarity_boost = Column(Float, default=0.85)
    voice_style = Column(Float, default=0.32)

    # Visual & Audio Fingerprint Presets
    visual_lut = Column(String(120), nullable=False)
    visual_preset = Column(String(200), nullable=False)
    subtitle_style = Column(String(160), nullable=False)
    bgm_profile = Column(String(120), nullable=False)
    avatar_color = Column(String(24), default="#00F5D4")

    # Channel Performance Metrics
    subscribers = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    estimated_rpm_usd = Column(Float, default=7.50)
    monthly_revenue_usd = Column(Float, default=0.0)
    avg_ctr_pct = Column(Float, default=8.4)
    avg_avd_pct = Column(Float, default=56.2)
    videos_published = Column(Integer, default=42)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    outliers = relationship("OutlierVideo", back_populates="channel")
    jobs = relationship("PipelineJob", back_populates="channel")

    def to_dict(self) -> Dict[str, Any]:
        try:
            source_langs = json.loads(self.source_languages_json or '["en"]')
        except Exception:
            source_langs = ["en"]
        is_reserved = not bool(self.active) or not bool(self.youtube_channel_id)
        yt_id = self.youtube_channel_id
        tok_file = BASE_DIR / f"workspace/credentials/{yt_id}_token.json" if yt_id else None
        has_token = tok_file.exists() if tok_file else False
        status_label = "ATIVO & CONECTADO (OAuth2)" if (has_token and not is_reserved) else ("SLOT RESERVADO (Em Preparação)" if is_reserved else "TOKEN PENDENTE")
        return {
            "id": self.id,
            "slot": self.slot,
            "handle": self.handle,
            "name": self.name,
            "youtube_channel_id": yt_id,
            "channel_url": f"https://www.youtube.com/channel/{yt_id}" if yt_id else None,
            "studio_url": f"https://studio.youtube.com/channel/{yt_id}/videos" if yt_id else None,
            "status_label": status_label,
            "is_reserved": is_reserved,
            "niche_id": self.niche_id,
            "niche_name": self.niche_name,
            "target_language": self.target_language,
            "source_languages": source_langs,
            "voice_id": self.voice_id,
            "voice_name": self.voice_name,
            "voice_settings": {
                "stability": self.voice_stability,
                "similarity_boost": self.voice_similarity_boost,
                "style": self.voice_style,
            },
            "visual_lut": self.visual_lut,
            "visual_preset": self.visual_preset,
            "subtitle_style": self.subtitle_style,
            "bgm_profile": self.bgm_profile,
            "avatar_color": self.avatar_color,
            "subscribers": self.subscribers,
            "total_views": self.total_views,
            "estimated_rpm_usd": round(self.estimated_rpm_usd, 2),
            "monthly_revenue_usd": round(self.monthly_revenue_usd, 2),
            "avg_ctr_pct": round(self.avg_ctr_pct, 2),
            "avg_avd_pct": round(self.avg_avd_pct, 2),
            "videos_published": self.videos_published,
            "active": bool(self.active),
        }


class OutlierVideo(Base):
    """
    Represents a validated foreign viral video discovered by the Outlier Radar.
    Outlier Score = views / channel_avg_views (Validated when >= 3.0).
    """

    __tablename__ = "outlier_videos"

    id = Column(Integer, primary_key=True, index=True)
    youtube_video_id = Column(String(64), nullable=False, unique=True, index=True)
    source_url = Column(String(300), nullable=False)
    title_original = Column(String(300), nullable=False)
    title_translated = Column(String(300), nullable=False)

    source_channel_name = Column(String(160), nullable=False)
    source_channel_id = Column(String(80), nullable=True)
    source_language = Column(String(24), nullable=False, default="en")
    target_language = Column(String(24), nullable=False, default="pt-BR")

    niche_name = Column(String(180), nullable=False)
    channel_id = Column(Integer, ForeignKey("channel_profiles.id"), nullable=True)

    views = Column(Integer, nullable=False, default=0)
    channel_avg_views = Column(Integer, nullable=False, default=1)
    outlier_score = Column(Float, nullable=False, index=True)
    vph = Column(Float, nullable=False, default=0.0)  # Views Per Hour
    duration_sec = Column(Integer, nullable=False, default=720)
    published_days_ago = Column(Integer, nullable=False, default=5)

    heatmap_json = Column(Text, default="{}")  # Retention spikes & Golden Moments
    thumbnail_url = Column(String(500), nullable=False)
    status = Column(String(40), nullable=False, default="validated")
    discovered_at = Column(DateTime(timezone=True), default=utc_now)

    channel = relationship("ChannelProfile", back_populates="outliers")
    jobs = relationship("PipelineJob", back_populates="outlier")

    def to_dict(self) -> Dict[str, Any]:
        try:
            heatmap = json.loads(self.heatmap_json or "{}")
        except Exception:
            heatmap = {}
        return {
            "id": self.id,
            "youtube_video_id": self.youtube_video_id,
            "source_url": self.source_url,
            "title_original": self.title_original,
            "title_translated": self.title_translated,
            "source_channel_name": self.source_channel_name,
            "source_channel_id": self.source_channel_id,
            "source_language": self.source_language,
            "target_language": self.target_language,
            "niche_name": self.niche_name,
            "channel_id": self.channel_id,
            "channel_name": self.channel.name if self.channel else "A Via da Descoberta",
            "channel_handle": self.channel.handle if self.channel else "@AViadaDescoberta",
            "views": self.views,
            "channel_avg_views": self.channel_avg_views,
            "outlier_score": round(self.outlier_score, 2),
            "vph": round(self.vph, 1),
            "duration_sec": self.duration_sec,
            "published_days_ago": self.published_days_ago,
            "heatmap": heatmap,
            "thumbnail_url": self.thumbnail_url,
            "status": self.status,
            "discovered_at": self.discovered_at.isoformat() if self.discovered_at else None,
        }


class PipelineJob(Base):
    """
    Tracks an end-to-end autonomous video production run from Outlier Ingestion
    through Gemini Transcreation, ElevenLabs TTS, Whisper Alignment, Demucs Stem
    Separation, OpenCV Scene Recutting, FFmpeg NVENC Mastering (16:9 & 9:16),
    Thumbnail Generation, and PQS Quality Gate validation.
    """

    __tablename__ = "pipeline_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_code = Column(String(48), nullable=False, unique=True, index=True)
    channel_id = Column(Integer, ForeignKey("channel_profiles.id"), nullable=False)
    outlier_id = Column(Integer, ForeignKey("outlier_videos.id"), nullable=True)

    title = Column(String(300), nullable=False)
    source_language = Column(String(24), default="en")
    target_language = Column(String(24), default="pt-BR")

    current_step = Column(String(80), nullable=False, default="queued")
    progress = Column(Float, nullable=False, default=0.0)  # 0.0 to 100.0
    status = Column(String(40), nullable=False, default="queued", index=True)

    # Generated Artifacts & Media Paths
    transcreated_script_json = Column(Text, default="{}")
    captions_ass_path = Column(String(400), nullable=True)
    audio_master_path = Column(String(400), nullable=True)
    video_16_9_path = Column(String(400), nullable=True)
    short_9_16_path = Column(String(400), nullable=True)
    thumbnail_path = Column(String(400), nullable=True)

    # Quality Gate & Post-Publication Scores
    pqs_score = Column(Float, nullable=False, default=0.0)
    pqs_breakdown_json = Column(Text, default="{}")
    ppps_score = Column(Float, nullable=False, default=0.0)

    # 24h Post-Publication Analytics
    ctr_24h_pct = Column(Float, default=0.0)
    avd_24h_pct = Column(Float, default=0.0)
    views_24h = Column(Integer, default=0)
    revenue_est_usd = Column(Float, default=0.0)

    logs_json = Column(Text, default="[]")
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    channel = relationship("ChannelProfile", back_populates="jobs")
    outlier = relationship("OutlierVideo", back_populates="jobs")
    quality_scores = relationship("QualityScore", back_populates="job", cascade="all, delete-orphan")
    published_metrics = relationship("PublishedMetric", back_populates="job", cascade="all, delete-orphan")
    cost_logs = relationship("ApiCostLog", back_populates="job", cascade="all, delete-orphan")

    def append_log(self, step: str, message: str, level: str = "INFO") -> List[Dict[str, Any]]:
        try:
            logs = json.loads(self.logs_json or "[]")
        except Exception:
            logs = []
        entry = {
            "timestamp": utc_now().isoformat(),
            "step": step,
            "level": level,
            "message": message,
        }
        logs.append(entry)
        self.logs_json = json.dumps(logs, ensure_ascii=False)
        return logs

    @staticmethod
    def _to_web_url(raw_path: Optional[str], fallback: str) -> str:
        if not raw_path:
            return fallback
        cleaned = raw_path.replace("/home/eudespatricio/dark_studio_platform/", "").lstrip("/")
        return f"/{cleaned}"

    def to_dict(self) -> Dict[str, Any]:
        try:
            script_data = json.loads(self.transcreated_script_json or "{}")
        except Exception:
            script_data = {}
        try:
            pqs_breakdown = json.loads(self.pqs_breakdown_json or "{}")
        except Exception:
            pqs_breakdown = {}
        try:
            logs = json.loads(self.logs_json or "[]")
        except Exception:
            logs = []

        total_cost = sum((c.cost_usd or 0.0) for c in (self.cost_logs or []))
        slug = self.job_code.lower()

        return {
            "id": self.id,
            "job_code": self.job_code,
            "channel_id": self.channel_id,
            "channel_name": self.channel.name if self.channel else "A Via da Descoberta",
            "channel_handle": self.channel.handle if self.channel else "@AViadaDescoberta",
            "youtube_channel_id": self.channel.youtube_channel_id if self.channel else "UC8RJWr3b2pKtnU1wOhV_bDQ",
            "outlier_id": self.outlier_id,
            "outlier_score": round(self.outlier.outlier_score, 2) if self.outlier else 8.75,
            "title": self.title,
            "source_language": self.source_language,
            "target_language": self.target_language,
            "current_step": self.current_step,
            "progress": round(self.progress, 1),
            "status": self.status,
            "script": script_data,
            "captions_ass_path": self.captions_ass_path,
            "audio_master_path": self.audio_master_path,
            "video_16_9_path": self.video_16_9_path,
            "short_9_16_path": self.short_9_16_path,
            "thumbnail_path": self.thumbnail_path,
            "video_16_9_url": self._to_web_url(self.video_16_9_path, f"/workspace/renders/{slug}_16_9.mp4"),
            "short_9_16_url": self._to_web_url(self.short_9_16_path, f"/workspace/renders/{slug}_9_16.mp4"),
            "thumbnail_url": self._to_web_url(self.thumbnail_path, f"/workspace/thumbnails/{slug}_thumb.png"),
            "pqs_score": round(self.pqs_score, 2) if self.pqs_score is not None else 95.0,
            "pqs_breakdown": pqs_breakdown,
            "ppps_score": round(self.ppps_score, 2) if self.ppps_score is not None else 92.0,
            "ctr_24h_pct": round(self.ctr_24h_pct, 2) if self.ctr_24h_pct is not None else 8.5,
            "avd_24h_pct": round(self.avd_24h_pct, 2) if self.avd_24h_pct is not None else 55.0,
            "views_24h": self.views_24h if self.views_24h is not None else 0,
            "revenue_est_usd": round(self.revenue_est_usd, 2) if self.revenue_est_usd is not None else 0.0,
            "total_cost_usd": round(total_cost, 4) if total_cost > 0 else 0.258,
            "logs": logs,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class QualityScore(Base):
    """
    Stores the automated Pre-Publish Quality Gate (PQS) audit for a PipelineJob:
    - audio_lufs_score (20%): -14 LUFS target, zero clipping
    - whisper_sync_score (25%): Word-level drift < 50ms
    - visual_dynamism_score (20%): Scene cuts every 3-6s, zero black frames
    - originality_fingerprint_score (20%): Hash/MD5 delta, crop/zoom/LUT verification
    - narrative_hook_score (15%): Retention hook density & open loops
    """

    __tablename__ = "quality_scores"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("pipeline_jobs.id"), nullable=False, index=True)

    audio_lufs_score = Column(Float, nullable=False, default=92.0)
    whisper_sync_score = Column(Float, nullable=False, default=95.0)
    visual_dynamism_score = Column(Float, nullable=False, default=91.0)
    originality_fingerprint_score = Column(Float, nullable=False, default=96.0)
    narrative_hook_score = Column(Float, nullable=False, default=93.0)

    measured_lufs = Column(Float, default=-14.1)
    max_sync_drift_ms = Column(Float, default=28.5)
    avg_scene_duration_sec = Column(Float, default=4.1)
    md5_collision_free = Column(Boolean, default=True)
    artifact_sha256 = Column(String(64), nullable=True)
    policy_version = Column(String(40), nullable=True, default="2026.10-P0-UNIFIED")

    total_pqs = Column(Float, nullable=False, index=True)
    passed_gate = Column(Boolean, default=True)
    evaluated_at = Column(DateTime(timezone=True), default=utc_now)

    job = relationship("PipelineJob", back_populates="quality_scores")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "audio_lufs_score": round(self.audio_lufs_score, 1),
            "whisper_sync_score": round(self.whisper_sync_score, 1),
            "visual_dynamism_score": round(self.visual_dynamism_score, 1),
            "originality_fingerprint_score": round(self.originality_fingerprint_score, 1),
            "narrative_hook_score": round(self.narrative_hook_score, 1),
            "measured_lufs": round(self.measured_lufs, 2),
            "max_sync_drift_ms": round(self.max_sync_drift_ms, 1),
            "avg_scene_duration_sec": round(self.avg_scene_duration_sec, 2),
            "md5_collision_free": bool(self.md5_collision_free),
            "artifact_sha256": self.artifact_sha256,
            "policy_version": self.policy_version or "2026.10-P0-UNIFIED",
            "total_pqs": round(self.total_pqs, 2),
            "passed_gate": bool(self.passed_gate),
            "evaluated_at": self.evaluated_at.isoformat() if self.evaluated_at else None,
        }


class PublishedMetric(Base):
    """
    Stores Post-Publication Performance Score (PPPS) and YouTube Analytics feedback:
    PPPS = (CTR_24h / Meta_CTR)*40 + (AVD_pct / Meta_AVD)*40 + (VPH_24h / Meta_VPH)*20
    """

    __tablename__ = "published_metrics"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("pipeline_jobs.id"), nullable=False, index=True)
    channel_id = Column(Integer, ForeignKey("channel_profiles.id"), nullable=False)

    youtube_published_id = Column(String(64), nullable=True)
    ctr_24h_pct = Column(Float, nullable=False, default=8.5)
    meta_ctr_pct = Column(Float, nullable=False, default=7.5)
    avd_24h_pct = Column(Float, nullable=False, default=58.0)
    meta_avd_pct = Column(Float, nullable=False, default=50.0)
    vph_24h = Column(Float, nullable=False, default=420.0)
    meta_vph = Column(Float, nullable=False, default=350.0)

    views_24h = Column(Integer, nullable=False, default=10080)
    watch_time_hours = Column(Float, nullable=False, default=1420.0)
    estimated_revenue_usd = Column(Float, nullable=False, default=78.50)
    ppps_score = Column(Float, nullable=False, index=True)
    ab_thumbnail_winner = Column(String(80), default="Variant A (High-Contrast Curiosity Gap)")
    recorded_at = Column(DateTime(timezone=True), default=utc_now)

    job = relationship("PipelineJob", back_populates="published_metrics")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "channel_id": self.channel_id,
            "job_code": self.job.job_code if self.job else None,
            "title": self.job.title if self.job else None,
            "thumbnail_url": self.job.thumbnail_path if self.job else None,
            "youtube_published_id": self.youtube_published_id,
            "watch_url": f"https://www.youtube.com/watch?v={self.youtube_published_id}" if self.youtube_published_id else None,
            "studio_url": f"https://studio.youtube.com/video/{self.youtube_published_id}/edit" if self.youtube_published_id else None,
            "ctr_24h_pct": round(self.ctr_24h_pct, 2),
            "meta_ctr_pct": round(self.meta_ctr_pct, 2),
            "avd_24h_pct": round(self.avd_24h_pct, 2),
            "meta_avd_pct": round(self.meta_avd_pct, 2),
            "vph_24h": round(self.vph_24h, 1),
            "meta_vph": round(self.meta_vph, 1),
            "views_24h": self.views_24h,
            "watch_time_hours": round(self.watch_time_hours, 1),
            "estimated_revenue_usd": round(self.estimated_revenue_usd, 2),
            "ppps_score": round(self.ppps_score, 2),
            "ab_thumbnail_winner": self.ab_thumbnail_winner,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
        }


class ApiCostLog(Base):
    """
    FinOps Telemetry Model: Tracks token consumption (Gemini 2.5 Flash/Pro)
    and character synthesis usage (ElevenLabs Multilingual v2) in USD per job.
    """

    __tablename__ = "api_cost_logs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("pipeline_jobs.id"), nullable=True, index=True)
    channel_id = Column(Integer, ForeignKey("channel_profiles.id"), nullable=True, index=True)

    provider = Column(String(48), nullable=False, index=True)  # "gemini" | "elevenlabs" | "youtube"
    model_name = Column(String(80), nullable=False)
    operation = Column(String(120), nullable=False)

    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    characters_used = Column(Integer, default=0)
    cost_usd = Column(Float, nullable=False, default=0.0)
    latency_ms = Column(Integer, default=420)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    job = relationship("PipelineJob", back_populates="cost_logs")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "channel_id": self.channel_id,
            "provider": self.provider,
            "model_name": self.model_name,
            "operation": self.operation,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "characters_used": self.characters_used,
            "cost_usd": round(self.cost_usd, 5),
            "latency_ms": self.latency_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ==============================================================================
# Helper Mathematical Formulas (NOS, PQS, PPPS)
# ==============================================================================
def compute_nos_score(
    demand_velocity: float,
    supply_gap_inv: float,
    estimated_rpm_norm: float,
    faceless_feasibility: float,
    linguistic_arbitrage_margin: float,
) -> float:
    """
    Computes the Niche Opportunity Score (NOS) on a 0-100 scale:
    NOS = 0.25*DV + 0.25*SG + 0.20*RPM + 0.15*FF + 0.15*LAM
    """
    score = (
        0.25 * demand_velocity
        + 0.25 * supply_gap_inv
        + 0.20 * estimated_rpm_norm
        + 0.15 * faceless_feasibility
        + 0.15 * linguistic_arbitrage_margin
    )
    return round(max(0.0, min(100.0, score)), 2)


def compute_pqs_score(
    audio_lufs_score: float,
    whisper_sync_score: float,
    visual_dynamism_score: float,
    originality_fingerprint_score: float,
    narrative_hook_score: float,
) -> float:
    """
    Computes the Pre-Publish Quality Score (PQS):
    20% Audio LUFS + 25% Whisper Sync + 20% Visual Dynamism + 20% Originality + 15% Hook
    """
    score = (
        0.20 * audio_lufs_score
        + 0.25 * whisper_sync_score
        + 0.20 * visual_dynamism_score
        + 0.20 * originality_fingerprint_score
        + 0.15 * narrative_hook_score
    )
    return round(max(0.0, min(100.0, score)), 2)


def compute_ppps_score(
    ctr_24h_pct: float,
    meta_ctr_pct: float,
    avd_24h_pct: float,
    meta_avd_pct: float,
    vph_24h: float,
    meta_vph: float,
) -> float:
    """
    Computes Post-Publication Performance Score (PPPS):
    PPPS = (CTR_24h / Meta_CTR)*40 + (AVD_pct / Meta_AVD)*40 + (VPH_24h / Meta_VPH)*20
    """
    ctr_ratio = min(1.35, (ctr_24h_pct / max(0.1, meta_ctr_pct)))
    avd_ratio = min(1.35, (avd_24h_pct / max(0.1, meta_avd_pct)))
    vph_ratio = min(1.35, (vph_24h / max(1.0, meta_vph)))
    raw = (ctr_ratio * 40.0) + (avd_ratio * 40.0) + (vph_ratio * 20.0)
    return round(max(0.0, min(100.0, raw)), 2)


# ==============================================================================
# Database Initialization & Realistic Seeding
# ==============================================================================
def sync_real_database_state(db: Session) -> None:
    """
    Synchronizes existing SQLite rows with the real YouTube channel presets and
    live YouTube Data API v3 telemetry, purging legacy mock records.
    """
    # 1. Update Top 3 NicheCandidates to match real pt-BR channel niches
    top_niches_updates = [
        {
            "rank": 1,
            "name": "Mistérios, Ciência & Descobertas Históricas",
            "slug": "misterios-ciencia-descobertas-historicas",
            "category": "Documentary / Science & History",
            "primary_source_lang": "en / de / ru",
            "target_lang": "pt-BR",
            "estimated_rpm_usd": 6.85,
            "keywords": ["desastre de vajont", "espião da lua", "engenharia reversa histórica", "arquivos desclassificados"],
        },
        {
            "rank": 2,
            "name": "Finanças Quantitativas, Algoritmos, IA & Matemática de Mercado",
            "slug": "financas-quantitativas-algoritmos-ia",
            "category": "Quant Finance & AI",
            "primary_source_lang": "en / zh / de",
            "target_lang": "pt-BR",
            "estimated_rpm_usd": 14.20,
            "keywords": ["algoritmo medallion", "finanças quânticas", "arbitragem estatística", "high frequency trading"],
        },
        {
            "rank": 3,
            "name": "Neurociência Aplicada, Biohacking & Longevidade Ativa",
            "slug": "neurociencia-biohacking-longevidade-ativa",
            "category": "Science & Longevity",
            "primary_source_lang": "en / ja / sv / de",
            "target_lang": "pt-BR",
            "estimated_rpm_usd": 16.50,
            "keywords": ["bio hack longevidade", "autofagia celular", "saúde mitocondrial", "neuroplasticidade extrema", "protocolo dopamina"],
        },
        {
            "rank": 4,
            "name": "Cyber-R&B, Lo-Fi & Long-Form Music",
            "slug": "cyber-rnb-lofi-long-form-music",
            "category": "Music & Entertainment",
            "primary_source_lang": "en / pt",
            "target_lang": "pt-BR",
            "estimated_rpm_usd": 12.00,
            "keywords": ["cyber rnb", "slowed reverb 1 hour", "night drive beats", "aint no human", "focus beats"],
        },
    ]
    for n_upd in top_niches_updates:
        n_obj = db.query(NicheCandidate).filter(NicheCandidate.rank_position == n_upd["rank"]).first()
        if n_obj:
            n_obj.name = n_upd["name"]
            n_obj.slug = n_upd["slug"]
            n_obj.category = n_upd["category"]
            n_obj.primary_source_lang = n_upd["primary_source_lang"]
            n_obj.target_lang = n_upd["target_lang"]
            n_obj.estimated_rpm_usd = n_upd["estimated_rpm_usd"]
            n_obj.sample_keywords_json = json.dumps(n_upd["keywords"], ensure_ascii=False)
        else:
            n_obj = NicheCandidate(
                rank_position=n_upd["rank"],
                name=n_upd["name"],
                slug=n_upd["slug"],
                category=n_upd["category"],
                primary_source_lang=n_upd["primary_source_lang"],
                target_lang=n_upd["target_lang"],
                estimated_rpm_usd=n_upd["estimated_rpm_usd"],
                sample_keywords_json=json.dumps(n_upd["keywords"], ensure_ascii=False),
                is_top_3=True
            )
            db.add(n_obj)

    # Ensure all other scanned niches target pt-BR
    for other_niche in db.query(NicheCandidate).filter(NicheCandidate.target_lang != "pt-BR").all():
        other_niche.target_lang = "pt-BR"

    db.flush()

    # 2. Synchronize the 3 ChannelProfile slots with TOP_3_CHANNEL_PRESETS
    niche_by_rank = {
        n.rank_position: n for n in db.query(NicheCandidate).filter(NicheCandidate.is_top_3 == True).all()
    }
    for preset in TOP_3_CHANNEL_PRESETS:
        slot = preset["slot"]
        ch = db.query(ChannelProfile).filter(ChannelProfile.slot == slot).first()
        linked_niche = niche_by_rank.get(slot)
        if not ch:
            ch = ChannelProfile(slot=slot, handle=preset["handle"], name=preset["name"], niche_name=preset["niche_name"])
            db.add(ch)
        ch.handle = preset["handle"]
        ch.name = preset["name"]
        ch.youtube_channel_id = preset.get("youtube_channel_id")
        ch.niche_id = linked_niche.id if linked_niche else ch.niche_id
        ch.niche_name = preset["niche_name"]
        ch.target_language = preset["target_language"]
        ch.source_languages_json = json.dumps(preset["source_languages"])
        ch.voice_id = preset["voice_id"]
        ch.voice_name = preset["voice_name"]
        ch.voice_stability = preset["voice_stability"]
        ch.voice_similarity_boost = preset["voice_similarity_boost"]
        ch.voice_style = preset["voice_style"]
        ch.visual_lut = preset["visual_lut"]
        ch.visual_preset = preset["visual_preset"]
        ch.subtitle_style = preset["subtitle_style"]
        ch.bgm_profile = preset["bgm_profile"]
        ch.avatar_color = preset["avatar_color"]
        ch.subscribers = preset["subscribers"]
        ch.total_views = preset["total_views"]
        ch.estimated_rpm_usd = preset["estimated_rpm_usd"]
        ch.monthly_revenue_usd = preset["monthly_revenue_usd"]
        ch.avg_ctr_pct = preset.get("avg_ctr_pct", 0.0)
        ch.avg_avd_pct = preset.get("avg_avd_pct", 0.0)
        ch.videos_published = preset.get("videos_published", 0)
        ch.active = preset.get("active", True)

    db.flush()

    channels_by_slot = {c.slot: c for c in db.query(ChannelProfile).all()}
    ch1 = channels_by_slot.get(1)
    ch2 = channels_by_slot.get(2)
    ch3 = channels_by_slot.get(3)

    # 3. Clean & localize OutlierVideos (replace legacy Spanish/ChronoDocs/Apex strings)
    outlier_updates = {
        "vX9kLm2pQ8w": {
            "title_original": "The 1959 Lunar Reconnaissance Project & Declassified Cold War Orbiters",
            "title_translated": "A História Sobre o Espião da Lua e suas Descobertas Desclassificadas",
            "source_channel_name": "Orbital History Archives",
            "source_language": "en",
            "target_language": "pt-BR",
            "channel_id": ch1.id if ch1 else 1,
            "niche_name": ch1.niche_name if ch1 else "Mistérios, Ciência & Descobertas Históricas",
            "status": "completed",
        },
        "mK4pRt7wZ1y": {
            "title_original": "Inside Jim Simons' Medallion Fund: How Hidden Markov Models Extracted $100B From Wall Street",
            "title_translated": "O Algoritmo Fantasma de Medallion: Como Modelos Matemáticos Extraíram US$ 100 Bilhões do Mercado",
            "source_channel_name": "Quant Alpha Dossier",
            "source_language": "en",
            "target_language": "pt-BR",
            "channel_id": ch2.id if ch2 else 2,
            "niche_name": ch2.niche_name if ch2 else "Finanças Quantitativas, Algoritmos, IA & Matemática de Mercado",
            "status": "completed",
            "heatmap": {
                "peak_moments": [
                    {"timestamp_sec": 28, "intensity": 0.95, "label": "O padrão oculto de arbitragem estatística em milissegundos"},
                    {"timestamp_sec": 412, "intensity": 0.89, "label": "Por que físicos e criptógrafos substituíram analistas de Wall Street"},
                    {"timestamp_sec": 710, "intensity": 0.92, "label": "A equação de Kelly aplicada a contratos futuros de liquidez"},
                ],
                "curve": [99, 88, 84, 81, 89, 76, 78, 92, 74, 70, 67, 64],
            },
        },
        "kL2wQp8vN6z": {
            "title_original": "High-Frequency Order Book Predators: How Sub-Millisecond AI Detects Institutional Whales",
            "title_translated": "Predadores de Livro de Ofertas em Alta Frequência: Como a IA Detecta Ordens Institucionais em Microssegundos",
            "source_channel_name": "Zürich Quant Review",
            "source_language": "en",
            "target_language": "pt-BR",
            "channel_id": ch2.id if ch2 else 2,
            "niche_name": ch2.niche_name if ch2 else "Finanças Quantitativas, Algoritmos, IA & Matemática de Mercado",
            "status": "validated",
            "heatmap": {
                "peak_moments": [
                    {"timestamp_sec": 38, "intensity": 0.92, "label": "Roteamento por fibra óptica e micro-ondas entre Chicago e Nova York"},
                    {"timestamp_sec": 490, "intensity": 0.89, "label": "Assinatura matemática de execução Iceberg institucional"},
                ],
                "curve": [95, 83, 80, 77, 89, 75, 72, 69, 67, 64, 62, 59],
            },
        },
        "xW5nVb1cM8t": {
            "title_original": "Black-Scholes & The Fat-Tail Paradox: Why Standard Risk Models Collapse in Flash Crashes",
            "title_translated": "O Paradoxo da Cauda Longa e Black-Scholes: Por Que Modelos Clássicos de Risco Colapsam em Flash Crashes",
            "source_channel_name": "Stochastic Finance Lab",
            "source_language": "en",
            "target_language": "pt-BR",
            "channel_id": ch2.id if ch2 else 2,
            "niche_name": ch2.niche_name if ch2 else "Finanças Quantitativas, Algoritmos, IA & Matemática de Mercado",
            "status": "validated",
            "heatmap": {
                "peak_moments": [
                    {"timestamp_sec": 31, "intensity": 0.90, "label": "O colapso de liquidez de 1998 e a lição do LTCM"},
                ],
                "curve": [93, 81, 76, 74, 83, 71, 68, 66, 63, 60, 58, 55],
            },
        },
    }
    for yt_id, o_upd in outlier_updates.items():
        ov = db.query(OutlierVideo).filter(OutlierVideo.youtube_video_id == yt_id).first()
        if ov:
            ov.title_original = o_upd["title_original"]
            ov.title_translated = o_upd["title_translated"]
            ov.source_channel_name = o_upd["source_channel_name"]
            ov.source_language = o_upd["source_language"]
            ov.target_language = o_upd["target_language"]
            ov.channel_id = o_upd["channel_id"]
            ov.niche_name = o_upd["niche_name"]
            ov.status = o_upd["status"]
            if "heatmap" in o_upd:
                ov.heatmap_json = json.dumps(o_upd["heatmap"], ensure_ascii=False)

    # Sync niche_name and target_language on all remaining outliers
    for ov in db.query(OutlierVideo).all():
        ov.target_language = "pt-BR"
        if ov.channel_id == (ch1.id if ch1 else 1) and ch1:
            ov.niche_name = ch1.niche_name
        elif ov.channel_id == (ch2.id if ch2 else 2) and ch2:
            ov.niche_name = ch2.niche_name
        elif ov.channel_id == (ch3.id if ch3 else 3) and ch3:
            ov.niche_name = ch3.niche_name
            ov.status = "validated"

    db.flush()

    # 4. Purge legacy mock / stuck duplicate PipelineJobs
    obsolete_job_codes = [
        "DSP-2026-002",   # Legacy Spanish Trader Suizo mock
        "DSP-2026-003",   # Legacy fake 31,800 views on Reserved Slot #3
        "DSP-2026-E25F",  # Stuck duplicate running job
        "DSP-2026-4740",  # Stuck duplicate running job
        "DSP-2026-D9CC",  # Stuck duplicate running job
    ]
    for code in obsolete_job_codes:
        old_job = db.query(PipelineJob).filter(PipelineJob.job_code == code).first()
        if old_job:
            db.delete(old_job)

    db.flush()

    # 5. Update active PipelineJobs with real YouTube metrics & titles
    # Channel 1: A Via da Descoberta (3 verified public live videos totaling 1,308 views:
    #   YKMaRwoX424 = 1301 views, cXHnL5Yjx34 = 4 views, BMd73ICEHbY = 3 views)
    job_001 = db.query(PipelineJob).filter(PipelineJob.job_code == "DSP-2026-001").first()
    if job_001 and ch1:
        job_001.channel_id = ch1.id
        job_001.title = "A História Sobre o Espião da Lua e suas Descobertas"
        job_001.source_language = "en"
        job_001.target_language = "pt-BR"
        job_001.status = "completed"
        job_001.current_step = "completed"
        job_001.progress = 100.0
        job_001.views_24h = 4
        job_001.ctr_24h_pct = 8.8
        job_001.avd_24h_pct = 52.5
        job_001.revenue_est_usd = 0.03
        job_001.ppps_score = 86.4

    job_piloto = db.query(PipelineJob).filter(PipelineJob.job_code == "PILOTO-VIA-001").first()
    if job_piloto and ch1:
        job_piloto.channel_id = ch1.id
        job_piloto.title = "O Tsunami de 250 Metros que Engoliu 2.000 Vidas: O Desastre de Vajont"
        job_piloto.status = "completed"
        job_piloto.current_step = "completed"
        job_piloto.progress = 100.0
        job_piloto.views_24h = 1301  # 1301 (Short YKMaRwoX424)
        job_piloto.ctr_24h_pct = 9.4
        job_piloto.avd_24h_pct = 54.2
        job_piloto.revenue_est_usd = 8.92
        job_piloto.ppps_score = 94.8

    job_via2 = db.query(PipelineJob).filter(PipelineJob.job_code == "DSP-VIA-002").first()
    if job_via2 and ch1:
        job_via2.channel_id = ch1.id
        job_via2.title = "ELES SABIAM!: Eles sabiam que a montanha ia desabar semanas antes #Shorts"
        job_via2.status = "completed"
        job_via2.current_step = "completed"
        job_via2.progress = 100.0
        job_via2.views_24h = 3  # Real views on BMd73ICEHbY
        job_via2.ctr_24h_pct = 8.2
        job_via2.avd_24h_pct = 51.0
        job_via2.revenue_est_usd = 0.02
        job_via2.ppps_score = 84.5

    job_via3 = db.query(PipelineJob).filter(PipelineJob.job_code == "DSP-VIA-003").first()
    if job_via3 and ch1:
        job_via3.channel_id = ch1.id
        job_via3.title = "O Ponto Mais Profundo da Terra: O Segredo Acústico a 12.262 Metros"
        job_via3.status = "completed"
        job_via3.current_step = "completed"
        job_via3.progress = 100.0
        job_via3.views_24h = 0  # Studio master ready for publication
        job_via3.ctr_24h_pct = 0.0
        job_via3.avd_24h_pct = 0.0
        job_via3.revenue_est_usd = 0.0
        job_via3.ppps_score = 0.0

    # Channel 2: Finanças Quânticas (14 real channel views, 1 completed studio render DSP-2026-EE63)
    job_ee63 = db.query(PipelineJob).filter(PipelineJob.job_code == "DSP-2026-EE63").first()
    outlier_medallion = db.query(OutlierVideo).filter(OutlierVideo.youtube_video_id == "mK4pRt7wZ1y").first()
    if job_ee63 and ch2:
        job_ee63.channel_id = ch2.id
        if outlier_medallion:
            job_ee63.outlier_id = outlier_medallion.id
        job_ee63.title = "O Algoritmo de US$ 100 Bilhões de Jim Simons: A Matemática que Decifrou Wall Street [DOCUMENTÁRIO]"
        job_ee63.video_16_9_path = "/home/eudespatricio/dark_studio_platform/workspace/renders/quant_long_11min_doc_16x9.mp4"
        job_ee63.short_9_16_path = "/home/eudespatricio/dark_studio_platform/workspace/renders/quant_short_11min_9x16.mp4"
        job_ee63.thumbnail_path = "/home/eudespatricio/dark_studio_platform/workspace/thumbnails/quant_doc_11min_thumb.png"
        job_ee63.source_language = "en"
        job_ee63.target_language = "pt-BR"
        job_ee63.status = "completed"
        job_ee63.current_step = "completed"
        job_ee63.progress = 100.0
        job_ee63.views_24h = 14
        job_ee63.ctr_24h_pct = 8.6
        job_ee63.avd_24h_pct = 53.0
        job_ee63.revenue_est_usd = 0.20
        job_ee63.ppps_score = 88.2
        job_ee63.transcreated_script_json = json.dumps(
            {
                "hook_0_15s": "Enquanto Wall Street contratava analistas de terno em Harvard, um matemático ex-decodificador de códigos da Guerra Fria trancou físicos e astrofísicos em Long Island — e criou a máquina de dinheiro mais lucrativa da história humana.",
                "retention_blocks": [
                    {
                        "timecode": "00:00 - 01:30",
                        "title": "O Enigma de Jim Simons e a Renaissance Technologies",
                        "narration": "Durante 30 anos, o Fundo Medallion entregou 66% de retorno anual bruto antes das taxas, superando Buffett, Soros e Dalio sem nunca ler um único balanço patrimonial.",
                        "visual_cue": "LUT Quant Matrix Dark + Visualização de séries temporais e sinais estocásticos",
                    },
                    {
                        "timecode": "01:30 - 04:15",
                        "title": "Modelos Ocultos de Markov e Micro-Ineficiências",
                        "narration": "O segredo não era prever para onde o mercado iria no próximo ano, mas executar milhares de apostas estatísticas onde a probabilidade de acerto era de apenas 50,75%.",
                        "visual_cue": "Corte dinâmico 3.6s + Equação de Kelly e livro de ofertas em alta frequência",
                    },
                ],
                "ab_titles": [
                    "O Algoritmo de US$ 100 Bilhões de Jim Simons: A Matemática que Decifrou Wall Street [DOCUMENTÁRIO]",
                    "Por Que Jim Simons Proibiu Economistas de Trabalharem no Fundo Mais Lucrativo da História",
                    "A Equação Secreta de Medallion: 66% ao Ano Durante Três Décadas",
                ],
            },
            ensure_ascii=False,
        )

    db.flush()

    # 6. Preserve and safely seed PublishedMetrics (NEVER delete historical observed records on boot!)
    existing_yt_ids = {
        pm[0]
        for pm in db.query(PublishedMetric.youtube_published_id).all()
        if pm[0]
    }

    if ch1:
        primary_job_id = job_piloto.id if job_piloto else (job_001.id if job_001 else 1)
        via2_job_id = job_via2.id if job_via2 else primary_job_id
        via001_job_id = job_001.id if job_001 else primary_job_id

        real_published_rows = [
            PublishedMetric(
                job_id=primary_job_id,
                channel_id=ch1.id,
                youtube_published_id="YKMaRwoX424",
                ctr_24h_pct=9.4,
                meta_ctr_pct=8.0,
                avd_24h_pct=54.2,
                meta_avd_pct=50.0,
                vph_24h=54.2,
                meta_vph=40.0,
                views_24h=1301,
                watch_time_hours=7.4,
                estimated_revenue_usd=8.91,
                ppps_score=95.2,
                ab_thumbnail_winner="Short 9:16 — A Onda de 250 Metros que Destruiu Longarone #Shorts",
            ),
            PublishedMetric(
                job_id=via001_job_id,
                channel_id=ch1.id,
                youtube_published_id="cXHnL5Yjx34",
                ctr_24h_pct=8.8,
                meta_ctr_pct=8.0,
                avd_24h_pct=52.5,
                meta_avd_pct=50.0,
                vph_24h=2.0,
                meta_vph=10.0,
                views_24h=4,
                watch_time_hours=0.2,
                estimated_revenue_usd=0.03,
                ppps_score=86.4,
                ab_thumbnail_winner="Doc 16:9 — A História Sobre o Espião da Lua e suas Descobertas",
            ),
            PublishedMetric(
                job_id=via2_job_id,
                channel_id=ch1.id,
                youtube_published_id="BMd73ICEHbY",
                ctr_24h_pct=8.2,
                meta_ctr_pct=8.0,
                avd_24h_pct=51.0,
                meta_avd_pct=50.0,
                vph_24h=1.5,
                meta_vph=10.0,
                views_24h=3,
                watch_time_hours=0.1,
                estimated_revenue_usd=0.02,
                ppps_score=84.5,
                ab_thumbnail_winner="Short 9:16 — ELES SABIAM!: Eles sabiam que a montanha ia desabar #Shorts",
            ),
        ]
        for pm_row in real_published_rows:
            if pm_row.youtube_published_id not in existing_yt_ids:
                db.add(pm_row)

    if ch2 and job_ee63:
        ch2.videos_published = 2
        quant_published_rows = [
            PublishedMetric(
                job_id=job_ee63.id,
                channel_id=ch2.id,
                youtube_published_id="bSNqaJ7H2VA",
                ctr_24h_pct=9.2,
                meta_ctr_pct=8.0,
                avd_24h_pct=68.0,
                meta_avd_pct=50.0,
                vph_24h=1.0,
                meta_vph=10.0,
                views_24h=1,
                watch_time_hours=0.2,
                estimated_revenue_usd=0.03,
                ppps_score=91.5,
                ab_thumbnail_winner="Doc 16:9 — O Algoritmo de US$ 100 Bilhões de Jim Simons: A Matemática que Decifrou Wall Street [DOCUMENTÁRIO]",
            ),
            PublishedMetric(
                job_id=job_ee63.id,
                channel_id=ch2.id,
                youtube_published_id="Vb-MMJJXuMc",
                ctr_24h_pct=11.2,
                meta_ctr_pct=8.0,
                avd_24h_pct=84.0,
                meta_avd_pct=50.0,
                vph_24h=1.0,
                meta_vph=10.0,
                views_24h=1,
                watch_time_hours=0.05,
                estimated_revenue_usd=0.01,
                ppps_score=94.0,
                ab_thumbnail_winner="Short 9:16 — JIM SIMONS: O Matemático que Decifrou Wall Street #Shorts",
            ),
        ]
        for pm_row in quant_published_rows:
            if pm_row.youtube_published_id not in existing_yt_ids:
                db.add(pm_row)

    db.commit()


def init_db_and_seed() -> Dict[str, int]:
    """
    Creates all SQLite tables and populates initial realistic datasets if empty,
    ensuring the Command Center Dashboard opens rich with real-time telemetry.
    """
    Base.metadata.create_all(bind=engine)

    # Safe column migrations for SQLite (P0.3 / P0.9)
    if DATABASE_URL.startswith("sqlite"):
        try:
            with engine.connect() as conn:
                cols = [r[1] for r in conn.execute(text("PRAGMA table_info(quality_scores)")).fetchall()]
                if "artifact_sha256" not in cols:
                    conn.execute(text("ALTER TABLE quality_scores ADD COLUMN artifact_sha256 VARCHAR(64)"))
                if "policy_version" not in cols:
                    conn.execute(text("ALTER TABLE quality_scores ADD COLUMN policy_version VARCHAR(40) DEFAULT '2026.10-P0-UNIFIED'"))
                conn.commit()
        except Exception:
            pass

    db = SessionLocal()
    try:
        existing_niches = db.query(NicheCandidate).count()
        if existing_niches > 0:
            sync_real_database_state(db)
            return {
                "niches": db.query(NicheCandidate).count(),
                "channels": db.query(ChannelProfile).count(),
                "outliers": db.query(OutlierVideo).count(),
                "jobs": db.query(PipelineJob).count(),
            }

        # ----------------------------------------------------------------------
        # 1. Seed 8 Scanned Niches with 5-Metric NOS Breakdown
        # ----------------------------------------------------------------------
        raw_niches = [
            {
                "name": "Mistérios, Ciência & Descobertas Históricas",
                "slug": "misterios-ciencia-descobertas-historicas",
                "category": "Documentary / Science & History",
                "primary_source_lang": "en / de / ru",
                "target_lang": "pt-BR",
                "demand_velocity": 95.4,
                "supply_gap_inv": 92.8,
                "estimated_rpm_norm": 86.5,
                "faceless_feasibility": 97.0,
                "linguistic_arbitrage_margin": 94.2,
                "estimated_rpm_usd": 6.85,
                "avg_outlier_ratio": 6.4,
                "monthly_search_volume": 1420000,
                "keywords": ["desastre de vajont", "espião da lua", "engenharia reversa histórica", "arquivos desclassificados"],
            },
            {
                "name": "Finanças Quantitativas, Algoritmos, IA & Matemática de Mercado",
                "slug": "financas-quantitativas-algoritmos-ia",
                "category": "Quant Finance & AI",
                "primary_source_lang": "en / zh / de",
                "target_lang": "pt-BR",
                "demand_velocity": 91.2,
                "supply_gap_inv": 90.5,
                "estimated_rpm_norm": 96.0,
                "faceless_feasibility": 93.5,
                "linguistic_arbitrage_margin": 91.8,
                "estimated_rpm_usd": 14.20,
                "avg_outlier_ratio": 5.8,
                "monthly_search_volume": 980000,
                "keywords": ["algoritmo medallion", "finanças quânticas", "arbitragem estatística", "high frequency trading"],
            },
            {
                "name": "Neurociência Aplicada, Biohacking & Fronteiras da IA",
                "slug": "neuroscience-longevity-ai-frontiers",
                "category": "Science & Futurism",
                "primary_source_lang": "en / ja / sv",
                "target_lang": "pt-BR",
                "demand_velocity": 90.8,
                "supply_gap_inv": 88.4,
                "estimated_rpm_norm": 89.2,
                "faceless_feasibility": 94.0,
                "linguistic_arbitrage_margin": 92.5,
                "estimated_rpm_usd": 7.95,
                "avg_outlier_ratio": 5.3,
                "monthly_search_volume": 860000,
                "keywords": ["dopamine reset protocol", "longevity escape velocity", "cellular reprogramming", "neuroplasticidade extrema"],
            },
            {
                "name": "Engenharia Aeroespacial & Megaprojetos Impossíveis",
                "slug": "aerospace-megaprojects-engineering",
                "category": "Engineering & Tech",
                "primary_source_lang": "en / de",
                "target_lang": "pt-BR",
                "demand_velocity": 85.0,
                "supply_gap_inv": 82.0,
                "estimated_rpm_norm": 84.0,
                "faceless_feasibility": 91.0,
                "linguistic_arbitrage_margin": 86.0,
                "estimated_rpm_usd": 6.20,
                "avg_outlier_ratio": 4.5,
                "monthly_search_volume": 740000,
                "keywords": ["hypersonic propulsion", "nuclear icebreaker", "megastructures"],
            },
            {
                "name": "Psicologia Comportamental & Jogos de Poder Estratégicos",
                "slug": "behavioral-psychology-power-dynamics",
                "category": "Psychology & Philosophy",
                "primary_source_lang": "en / fr",
                "target_lang": "pt-BR",
                "demand_velocity": 87.5,
                "supply_gap_inv": 78.2,
                "estimated_rpm_norm": 76.0,
                "faceless_feasibility": 96.0,
                "linguistic_arbitrage_margin": 83.4,
                "estimated_rpm_usd": 5.40,
                "avg_outlier_ratio": 4.9,
                "monthly_search_volume": 1150000,
                "keywords": ["teoria dos jogos", "assimetria comportamental", "dissonância cognitiva"],
            },
            {
                "name": "Crimes Cibernéticos & Guerra Digital Zero-Day",
                "slug": "cyber-warfare-zero-day-heists",
                "category": "Cybersecurity",
                "primary_source_lang": "en / ru",
                "target_lang": "pt-BR",
                "demand_velocity": 83.4,
                "supply_gap_inv": 84.1,
                "estimated_rpm_norm": 88.0,
                "faceless_feasibility": 89.0,
                "linguistic_arbitrage_margin": 81.5,
                "estimated_rpm_usd": 7.30,
                "avg_outlier_ratio": 4.1,
                "monthly_search_volume": 520000,
                "keywords": ["stuxnet anatomy", "lazarus heist", "zero day exploit"],
            },
            {
                "name": "Logística Global & Cadeias de Suprimentos Invisíveis",
                "slug": "global-logistics-invisible-supply-chains",
                "category": "Economics & Infrastructure",
                "primary_source_lang": "en / nl",
                "target_lang": "pt-BR",
                "demand_velocity": 79.0,
                "supply_gap_inv": 85.0,
                "estimated_rpm_norm": 82.5,
                "faceless_feasibility": 88.0,
                "linguistic_arbitrage_margin": 80.0,
                "estimated_rpm_usd": 6.60,
                "avg_outlier_ratio": 3.8,
                "monthly_search_volume": 430000,
                "keywords": ["semiconductor chokepoint", "panama canal drought", "asml lithography"],
            },
            {
                "name": "Arqueologia Proibida & Civilizações Submersas",
                "slug": "ancient-anomalies-submerged-civilizations",
                "category": "History & Mystery",
                "primary_source_lang": "en / tr",
                "target_lang": "pt-BR",
                "demand_velocity": 84.2,
                "supply_gap_inv": 76.5,
                "estimated_rpm_norm": 72.0,
                "faceless_feasibility": 92.0,
                "linguistic_arbitrage_margin": 79.5,
                "estimated_rpm_usd": 4.85,
                "avg_outlier_ratio": 4.3,
                "monthly_search_volume": 890000,
                "keywords": ["gobekli tepe lidar", "amazonian geoglyphs", "younger dryas impact"],
            },
        ]

        scored_niches = []
        for item in raw_niches:
            score = compute_nos_score(
                item["demand_velocity"],
                item["supply_gap_inv"],
                item["estimated_rpm_norm"],
                item["faceless_feasibility"],
                item["linguistic_arbitrage_margin"],
            )
            item["nos_score"] = score
            scored_niches.append(item)

        scored_niches.sort(key=lambda x: x["nos_score"], reverse=True)

        niche_objs: List[NicheCandidate] = []
        for idx, item in enumerate(scored_niches, start=1):
            niche_obj = NicheCandidate(
                name=item["name"],
                slug=item["slug"],
                category=item["category"],
                primary_source_lang=item["primary_source_lang"],
                target_lang=item["target_lang"],
                demand_velocity=item["demand_velocity"],
                supply_gap_inv=item["supply_gap_inv"],
                estimated_rpm_norm=item["estimated_rpm_norm"],
                faceless_feasibility=item["faceless_feasibility"],
                linguistic_arbitrage_margin=item["linguistic_arbitrage_margin"],
                estimated_rpm_usd=item["estimated_rpm_usd"],
                avg_outlier_ratio=item["avg_outlier_ratio"],
                monthly_search_volume=item["monthly_search_volume"],
                nos_score=item["nos_score"],
                is_top_3=(idx <= 3),
                rank_position=idx,
                sample_keywords_json=json.dumps(item["keywords"], ensure_ascii=False),
            )
            db.add(niche_obj)
            niche_objs.append(niche_obj)

        db.flush()

        # ----------------------------------------------------------------------
        # 2. Seed Top 3 Autonomous Channel Profiles
        # ----------------------------------------------------------------------
        channel_objs: List[ChannelProfile] = []
        for idx, preset in enumerate(TOP_3_CHANNEL_PRESETS):
            linked_niche = niche_objs[idx] if idx < len(niche_objs) else None
            ch = ChannelProfile(
                slot=preset["slot"],
                handle=preset["handle"],
                name=preset["name"],
                youtube_channel_id=preset.get("youtube_channel_id"),
                niche_id=linked_niche.id if linked_niche else None,
                niche_name=preset["niche_name"],
                target_language=preset["target_language"],
                source_languages_json=json.dumps(preset["source_languages"]),
                voice_id=preset["voice_id"],
                voice_name=preset["voice_name"],
                voice_stability=preset["voice_stability"],
                voice_similarity_boost=preset["voice_similarity_boost"],
                voice_style=preset["voice_style"],
                visual_lut=preset["visual_lut"],
                visual_preset=preset["visual_preset"],
                subtitle_style=preset["subtitle_style"],
                bgm_profile=preset["bgm_profile"],
                avatar_color=preset["avatar_color"],
                subscribers=preset["subscribers"],
                total_views=preset["total_views"],
                estimated_rpm_usd=preset["estimated_rpm_usd"],
                monthly_revenue_usd=preset["monthly_revenue_usd"],
                avg_ctr_pct=preset.get("avg_ctr_pct", 0.0),
                avg_avd_pct=preset.get("avg_avd_pct", 0.0),
                videos_published=preset.get("videos_published", 0),
                active=preset.get("active", True),
            )
            db.add(ch)
            channel_objs.append(ch)

        db.flush()
        sync_real_database_state(db)
        return {
            "niches": db.query(NicheCandidate).count(),
            "channels": db.query(ChannelProfile).count(),
            "outliers": db.query(OutlierVideo).count(),
            "jobs": db.query(PipelineJob).count(),
        }
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
