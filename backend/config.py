"""
Dark Studio Platform — Centralized Configuration, API Control Hub & Presets
Provides paths, API credentials, runtime .env persistence, FinOps Circuit Breaker
budgets, local engine diagnostics, quality gates, and Top 3 Autonomous Channel presets.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

# ==============================================================================
# Base Paths & Directories
# ==============================================================================
BASE_DIR: Path = Path("/home/eudespatricio/dark_studio_platform").resolve()
ENV_FILE_PATH: Path = BASE_DIR / ".env"
load_dotenv(ENV_FILE_PATH)

BACKEND_DIR: Path = BASE_DIR / "backend"
FRONTEND_DIR: Path = BASE_DIR / "frontend"
ASSETS_DIR: Path = BASE_DIR / "assets"
WORKSPACE_DIR: Path = BASE_DIR / "workspace"

# Workspace Subdirectories
DOWNLOADS_DIR: Path = WORKSPACE_DIR / "downloads"
SCENES_DIR: Path = WORKSPACE_DIR / "scenes"
AUDIO_DIR: Path = WORKSPACE_DIR / "audio"
RENDERS_DIR: Path = WORKSPACE_DIR / "renders"
THUMBNAILS_DIR: Path = WORKSPACE_DIR / "thumbnails"
CREDENTIALS_DIR: Path = WORKSPACE_DIR / "credentials"

# Asset Subdirectories
FONTS_DIR: Path = ASSETS_DIR / "fonts"
LUTS_DIR: Path = ASSETS_DIR / "luts"
MUSIC_DIR: Path = ASSETS_DIR / "music"
SFX_DIR: Path = ASSETS_DIR / "sfx"

# Ensure all required directories exist on import
for _directory in (
    WORKSPACE_DIR,
    DOWNLOADS_DIR,
    SCENES_DIR,
    AUDIO_DIR,
    RENDERS_DIR,
    THUMBNAILS_DIR,
    CREDENTIALS_DIR,
    FONTS_DIR,
    LUTS_DIR,
    MUSIC_DIR,
    SFX_DIR,
):
    _directory.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# Database Configuration
# ==============================================================================
DB_PATH: Path = BASE_DIR / "dark_studio.db"
DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

# ==============================================================================
# External API Keys & Model Identifiers
# ==============================================================================
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL_FAST: str = os.getenv("GEMINI_MODEL_FAST", "gemini-3.8-flash")
GEMINI_MODEL_PRO: str = os.getenv("GEMINI_MODEL_PRO", "gemini-3.8-flash")

ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_MODEL_ID: str = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")

YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
PEXELS_API_KEY: str = os.getenv("PEXELS_API_KEY", "")
PIXABAY_API_KEY: str = os.getenv("PIXABAY_API_KEY") or os.getenv("pixabaykey", "")

# ==============================================================================
# Quality Thresholds, Quotas & FinOps Circuit Breaker
# ==============================================================================
MIN_OUTLIER_SCORE: float = float(os.getenv("MIN_OUTLIER_SCORE", "3.0"))
AUTO_PUBLISH_ENABLED: bool = os.getenv("AUTO_PUBLISH_ENABLED", "false").lower() in ("true", "1")
MIN_PQS_SCORE: float = float(os.getenv("MIN_PQS_SCORE", "78.0"))
MIN_NOS_SCORE: float = float(os.getenv("MIN_NOS_SCORE", "75.0"))
WHISPER_MODEL_SIZE: str = os.getenv("WHISPER_MODEL_SIZE", "base")
USE_NVENC: bool = os.getenv("USE_NVENC", "false").lower() in ("true", "1", "yes")

FINOPS_DAILY_BUDGET_USD: float = float(os.getenv("FINOPS_DAILY_BUDGET_USD", "15.0"))
FINOPS_MONTHLY_BUDGET_USD: float = float(os.getenv("FINOPS_MONTHLY_BUDGET_USD", "120.0"))
CIRCUIT_BREAKER_ENABLED: bool = os.getenv("CIRCUIT_BREAKER_ENABLED", "true").lower() in (
    "true",
    "1",
    "yes",
)

GEMINI_DAILY_TOKEN_QUOTA: int = int(os.getenv("GEMINI_DAILY_TOKEN_QUOTA", "2000000"))
ELEVENLABS_MONTHLY_CHAR_QUOTA: int = int(os.getenv("ELEVENLABS_MONTHLY_CHAR_QUOTA", "500000"))
YOUTUBE_DAILY_QUOTA_UNITS: int = int(os.getenv("YOUTUBE_DAILY_QUOTA_UNITS", "10000"))

# ==============================================================================
# FinOps Unit Cost Constants (USD)
# ==============================================================================
FINOPS_PRICING: Dict[str, float] = {
    "gemini_flash_input_per_1k": 0.00015,
    "gemini_flash_output_per_1k": 0.00060,
    "gemini_pro_input_per_1k": 0.00125,
    "gemini_pro_output_per_1k": 0.00500,
    "elevenlabs_per_1k_chars": 0.18000,
}

# ==============================================================================
# Top 3 Autonomous Channels — Master Presets
# ==============================================================================
TOP_3_CHANNEL_PRESETS: List[Dict[str, Any]] = [
    {
        "slot": 1,
        "handle": "@AViadaDescoberta",
        "name": "A Via da Descoberta",
        "youtube_channel_id": "UC8RJWr3b2pKtnU1wOhV_bDQ",
        "niche_name": "Mistérios, Ciência & Descobertas Históricas",
        "target_language": "pt-BR",
        "source_languages": ["en", "de", "ru", "ja"],
        "voice_id": "pNInz6obpgDQGcFmaJgB",
        "voice_name": "Marcus Vance (Deep Thriller Baritone)",
        "voice_stability": 0.42,
        "voice_similarity_boost": 0.85,
        "voice_style": 0.35,
        "visual_lut": "teal_orange_thriller.cube",
        "visual_preset": "Cold Obsidian Thriller (1.07x Dynamic Zoom + Vignette + Halation)",
        "subtitle_style": "Hormozi Gold/White Impact — 62px Montserrat ExtraBold",
        "bgm_profile": "dark_ambient_drone_-18dB",
        "estimated_rpm_usd": 6.85,
        "subscribers": 1,
        "total_views": 1310,
        "monthly_revenue_usd": 8.97,
        "videos_published": 4,
        "active": True,
        "avatar_color": "#00F5D4",
    },
    {
        "slot": 2,
        "handle": "@FinancasQuanticasOficial",
        "name": "Finanças Quânticas",
        "youtube_channel_id": "UCE6Ch6nhxI81Z6ILQIw23_Q",
        "niche_name": "Finanças Quantitativas, Algoritmos, IA & Matemática de Mercado",
        "target_language": "pt-BR",
        "source_languages": ["en", "zh", "ko", "de"],
        "voice_id": "ErXwobaYiN019PkySvjV",
        "voice_name": "George (Analytical & Authoritative Quantitative Analyst)",
        "voice_stability": 0.48,
        "voice_similarity_boost": 0.82,
        "voice_style": 0.28,
        "visual_lut": "quantum_emerald_analytics.cube",
        "visual_preset": "Quantum Matrix & Financial Analytics (Deep Obsidian + Emerald Data Glow)",
        "subtitle_style": "Quantum Tech Neon — 60px Montserrat Bold (Cyan/Green Highlight)",
        "bgm_profile": "quant_synthwave_minimal_drone_-19dB",
        "estimated_rpm_usd": 14.50,
        "subscribers": 0,
        "total_views": 14,
        "monthly_revenue_usd": 0.20,
        "videos_published": 0,
        "active": True,
        "avatar_color": "#10B981",
    },
    {
        "slot": 3,
        "handle": "@BioHackLongevidade",
        "name": "Bio Hack Longevidade",
        "youtube_channel_id": "UCIjEnT4adPYVyi0UlrCITBA",
        "niche_name": "Neurociência Aplicada, Biohacking & Longevidade Ativa",
        "target_language": "pt-BR",
        "source_languages": ["en", "ja", "sv", "de"],
        "voice_id": "VR6AewLTigWG4xSOukaG",
        "voice_name": "Dr. Viktor Kael (Clinical Futurist)",
        "voice_stability": 0.50,
        "voice_similarity_boost": 0.88,
        "voice_style": 0.30,
        "visual_lut": "cyber_biolab_clean.cube",
        "visual_preset": "Neural Precision (Crisp Unsharp Mask + Cyan Split-Tone + Smooth Pan)",
        "subtitle_style": "Hormozi Cyan Neon — 60px Montserrat Bold",
        "bgm_profile": "minimal_modular_arp_-20dB",
        "estimated_rpm_usd": 16.50,
        "subscribers": 0,
        "total_views": 0,
        "monthly_revenue_usd": 0.00,
        "videos_published": 0,
        "active": True,
        "avatar_color": "#00F5D4",
    },
    {
        "slot": 4,
        "handle": "@aintnohumanoficial",
        "name": "Ain't No Human",
        "youtube_channel_id": "UCbO67ez7TKOJ8C_kpUF4t5Q",
        "niche_name": "Cyber-R&B, Lo-Fi & Long-Form Music",
        "target_language": "pt-BR",
        "source_languages": ["en", "pt"],
        "voice_id": "music_autonomous_vocalists",
        "voice_name": "Algorhythm & Synthia 4.0 (Autonomous Duo)",
        "voice_stability": 1.0,
        "voice_similarity_boost": 1.0,
        "voice_style": 0.0,
        "visual_lut": "cyber_magenta_cyan.cube",
        "visual_preset": "Cinematic Cyber-R&B Night Drive (1080p 16:9 + Neon Reactive EQ)",
        "subtitle_style": "Cyberpunk HUD Telemetry",
        "bgm_profile": "cyber_rnb_slowed_reverb_92bpm",
        "estimated_rpm_usd": 12.00,
        "subscribers": 0,
        "total_views": 0,
        "monthly_revenue_usd": 0.00,
        "videos_published": 0,
        "active": True,
        "avatar_color": "#EC4899",
        "channel_type": "music",
    },
]


def mask_api_key(raw_key: str) -> str:
    """Returns a safely masked representation of an API key for UI display."""
    clean = (raw_key or "").strip()
    if not clean or clean.startswith("your_"):
        return "Não configurada (Modo Simulação / Fallback Ativo)"
    if len(clean) <= 8:
        return "****" + clean[-2:]
    return f"{clean[:4]}••••••••••••{clean[-4:]}"


def inspect_local_engines() -> Dict[str, Dict[str, Any]]:
    """Checks availability and operational modes of local audiovisual/AI engines."""
    import importlib.util

    ffmpeg_bin = shutil.which("ffmpeg")
    ytdlp_bin = shutil.which("yt-dlp")
    has_whisper = importlib.util.find_spec("faster_whisper") is not None
    has_demucs = (importlib.util.find_spec("demucs") is not None) or bool(shutil.which("demucs"))
    has_ytdlp = bool(ytdlp_bin) or (importlib.util.find_spec("yt_dlp") is not None)

    return {
        "ffmpeg": {
            "name": "FFmpeg Mastering Engine (16:9 & 9:16)",
            "installed": bool(ffmpeg_bin),
            "binary_path": ffmpeg_bin or "/usr/bin/ffmpeg (wrapper active)",
            "hw_accel": "NVIDIA NVENC h264_nvenc" if settings.use_nvenc else "libx264 High-Profile 60fps",
            "audio_norm": "EBU R128 loudnorm (-14.0 LUFS / -1.0 dBTP)",
            "status": "online" if bool(ffmpeg_bin) else "offline",
        },
        "faster_whisper": {
            "name": "Faster-Whisper Word-Level Aligner",
            "installed": has_whisper,
            "model_size": settings.whisper_model_size,
            "compute_type": "int8_float16",
            "max_drift_target_ms": 25.0,
            "status": "online" if has_whisper else "offline (fallback mode)",
        },
        "demucs": {
            "name": "Demucs v4 Hybrid Transformer (htdemucs)",
            "installed": has_demucs,
            "stems": "vocals / drums / bass / other (BGM & SFX preservation)",
            "sidechain_ducking_db": -18.0,
            "status": "online" if has_demucs else "offline (DSP sidechain fallback)",
        },
        "yt_dlp": {
            "name": "yt-dlp Extraction & Heatmap Parser",
            "installed": has_ytdlp,
            "binary_path": ytdlp_bin or "python -m yt_dlp",
            "features": ["Most Replayed Heatmap JSON", "BestVideo+BestAudio Matroska/MP4", "Auto-Subtitles"],
            "status": "online" if has_ytdlp else "offline",
        },
    }


@dataclass
class Settings:
    """Typed configuration container with runtime & .env persistence support."""

    base_dir: Path = BASE_DIR
    backend_dir: Path = BACKEND_DIR
    frontend_dir: Path = FRONTEND_DIR
    assets_dir: Path = ASSETS_DIR
    workspace_dir: Path = WORKSPACE_DIR
    downloads_dir: Path = DOWNLOADS_DIR
    scenes_dir: Path = SCENES_DIR
    audio_dir: Path = AUDIO_DIR
    renders_dir: Path = RENDERS_DIR
    thumbnails_dir: Path = THUMBNAILS_DIR
    fonts_dir: Path = FONTS_DIR
    luts_dir: Path = LUTS_DIR
    music_dir: Path = MUSIC_DIR
    sfx_dir: Path = SFX_DIR

    db_path: Path = DB_PATH
    database_url: str = DATABASE_URL

    gemini_api_key: str = GEMINI_API_KEY
    gemini_model_fast: str = GEMINI_MODEL_FAST
    gemini_model_pro: str = GEMINI_MODEL_PRO

    elevenlabs_api_key: str = ELEVENLABS_API_KEY
    elevenlabs_model_id: str = ELEVENLABS_MODEL_ID

    youtube_api_key: str = YOUTUBE_API_KEY
    pexels_api_key: str = PEXELS_API_KEY
    pixabay_api_key: str = PIXABAY_API_KEY

    min_outlier_score: float = MIN_OUTLIER_SCORE
    min_pqs_score: float = MIN_PQS_SCORE
    min_nos_score: float = MIN_NOS_SCORE
    whisper_model_size: str = WHISPER_MODEL_SIZE
    use_nvenc: bool = USE_NVENC

    finops_daily_budget_usd: float = FINOPS_DAILY_BUDGET_USD
    finops_monthly_budget_usd: float = FINOPS_MONTHLY_BUDGET_USD
    circuit_breaker_enabled: bool = CIRCUIT_BREAKER_ENABLED

    gemini_daily_token_quota: int = GEMINI_DAILY_TOKEN_QUOTA
    elevenlabs_monthly_char_quota: int = ELEVENLABS_MONTHLY_CHAR_QUOTA
    youtube_daily_quota_units: int = YOUTUBE_DAILY_QUOTA_UNITS

    finops_pricing: Dict[str, float] = field(default_factory=lambda: dict(FINOPS_PRICING))
    top_3_channel_presets: List[Dict[str, Any]] = field(
        default_factory=lambda: list(TOP_3_CHANNEL_PRESETS)
    )

    @property
    def has_gemini_key(self) -> bool:
        return bool(
            self.gemini_api_key
            and not self.gemini_api_key.startswith("your_")
            and len(self.gemini_api_key) > 8
        )

    @property
    def has_elevenlabs_key(self) -> bool:
        return bool(
            self.elevenlabs_api_key
            and not self.elevenlabs_api_key.startswith("your_")
            and len(self.elevenlabs_api_key) > 8
        )

    @property
    def has_youtube_key(self) -> bool:
        return bool(
            self.youtube_api_key
            and not self.youtube_api_key.startswith("your_")
            and len(self.youtube_api_key) > 8
        )

    @property
    def has_pexels_key(self) -> bool:
        return bool(
            self.pexels_api_key
            and not self.pexels_api_key.startswith("your_")
            and len(self.pexels_api_key) > 8
        )

    def persist_env_updates(self, env_updates: Dict[str, str]) -> None:
        """Updates runtime attributes, os.environ, and persists values to `.env`."""
        global GEMINI_API_KEY, GEMINI_MODEL_FAST, GEMINI_MODEL_PRO
        global ELEVENLABS_API_KEY, ELEVENLABS_MODEL_ID
        global YOUTUBE_API_KEY, PEXELS_API_KEY

        for k, v in env_updates.items():
            if v is None:
                continue
            str_val = str(v).strip()
            os.environ[k] = str_val

            if k == "GEMINI_API_KEY" and "•" not in str_val:
                self.gemini_api_key = str_val
                GEMINI_API_KEY = str_val
            elif k == "GEMINI_MODEL_FAST":
                self.gemini_model_fast = str_val
                GEMINI_MODEL_FAST = str_val
            elif k == "GEMINI_MODEL_PRO":
                self.gemini_model_pro = str_val
                GEMINI_MODEL_PRO = str_val
            elif k == "ELEVENLABS_API_KEY" and "•" not in str_val:
                self.elevenlabs_api_key = str_val
                ELEVENLABS_API_KEY = str_val
            elif k == "ELEVENLABS_MODEL_ID":
                self.elevenlabs_model_id = str_val
                ELEVENLABS_MODEL_ID = str_val
            elif k == "YOUTUBE_API_KEY" and "•" not in str_val:
                self.youtube_api_key = str_val
                YOUTUBE_API_KEY = str_val
            elif k == "PEXELS_API_KEY" and "•" not in str_val:
                self.pexels_api_key = str_val
                PEXELS_API_KEY = str_val
            elif k == "WHISPER_MODEL_SIZE":
                self.whisper_model_size = str_val
            elif k == "USE_NVENC":
                self.use_nvenc = str_val.lower() in ("true", "1", "yes")
            elif k == "FINOPS_DAILY_BUDGET_USD":
                self.finops_daily_budget_usd = float(str_val)
            elif k == "FINOPS_MONTHLY_BUDGET_USD":
                self.finops_monthly_budget_usd = float(str_val)
            elif k == "CIRCUIT_BREAKER_ENABLED":
                self.circuit_breaker_enabled = str_val.lower() in ("true", "1", "yes")

        # Write or update .env file on disk safely
        existing_lines: List[str] = []
        if ENV_FILE_PATH.exists():
            existing_lines = ENV_FILE_PATH.read_text(encoding="utf-8").splitlines()
        elif (BASE_DIR / ".env.example").exists():
            existing_lines = (BASE_DIR / ".env.example").read_text(encoding="utf-8").splitlines()

        updated_keys = set()
        new_lines: List[str] = []
        for line in existing_lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                key_part = stripped.split("=", 1)[0].strip()
                if key_part in env_updates and "•" not in str(env_updates[key_part]):
                    new_lines.append(f'{key_part}="{env_updates[key_part]}"')
                    updated_keys.add(key_part)
                    continue
            new_lines.append(line)

        for k, v in env_updates.items():
            if k not in updated_keys and v is not None and "•" not in str(v):
                new_lines.append(f'{k}="{v}"')

        ENV_FILE_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


settings = Settings()
