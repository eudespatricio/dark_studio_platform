"""
ElevenLabs TTS Engine for Dark Studio Platform.
Supports distinct voice profiles for each of the Top 3 Channels, SHA-256 disk caching
to prevent duplicate API credit consumption, exact character FinOps tracking, and
realistic synthesized WAV/MP3 fallback generation when ELEVENLABS_API_KEY is not set.
"""

from __future__ import annotations

import hashlib
import logging
import math
import os
import struct
import time
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
load_dotenv(BASE_DIR / ".env")

logger = logging.getLogger("dark_studio.tts_engine")


@dataclass
class VoiceProfile:
    """Dedicated ElevenLabs voice configuration per Dark Channel."""
    channel_id: str
    channel_name: str
    voice_id: str
    voice_name: str
    model_id: str = "eleven_multilingual_v2"
    stability: float = 0.42
    similarity_boost: float = 0.82
    style: float = 0.35
    use_speaker_boost: bool = True
    speaking_rate_wpm: int = 158


@dataclass
class TTSFinOpsRecord:
    """Single TTS call cost/usage record for FinOps monitoring."""
    timestamp: float
    channel_id: str
    voice_id: str
    model_id: str
    characters: int
    cache_hit: bool
    estimated_cost_usd: float
    audio_path: str
    duration_sec: float


class TTSEngine:
    """
    Production ElevenLabs API client (`eleven_multilingual_v2` / `eleven_flash_v2_5`) with:
    - Dedicated voice profiles for the Top 3 Active Dark Channels
    - Deterministic SHA-256 disk cache (`workspace/audio/tts_cache/`) so repeated renders consume 0 credits
    - Exact character and USD cost accounting for FinOps
    - Local synthesized waveform fallback (`.wav` / `.mp3`) when `ELEVENLABS_API_KEY` is absent
    """

    # ElevenLabs Creator/Pro average cost per 1,000 characters (~$0.22 / 1K chars)
    COST_PER_1K_CHARS_USD = 0.22
    ELEVENLABS_API_BASE = "https://api.elevenlabs.io/v1"

    DEFAULT_CHANNEL_VOICES: Dict[str, VoiceProfile] = {
        "ch_1_investigativo": VoiceProfile(
            channel_id="ch_1_investigativo",
            channel_name="Arquivo Oculto & Geopolítica",
            voice_id="nPczCjzI2devNBz1zQrb",  # Brian - Deep Cinematic Narrative
            voice_name="Brian (Deep Cinematic Baritone)",
            model_id="eleven_multilingual_v2",
            stability=0.40,
            similarity_boost=0.84,
            style=0.38,
            speaking_rate_wpm=152,
        ),
        "ch_2_financas": VoiceProfile(
            channel_id="ch_2_financas",
            channel_name="Capital Invisível & Macroeconomia",
            voice_id="nPczCjzI2devNBz1zQrb",  # Brian - Deep Cinematic Narrative
            voice_name="Brian (Deep Cinematic Baritone)",
            model_id="eleven_multilingual_v2",
            stability=0.42,
            similarity_boost=0.84,
            style=0.35,
            speaking_rate_wpm=156,
        ),
        "ch_3_ciencia": VoiceProfile(
            channel_id="ch_3_ciencia",
            channel_name="Horizonte Quântico & Futurologia",
            voice_id="nPczCjzI2devNBz1zQrb",  # Brian - Deep Cinematic Narrative
            voice_name="Brian (Deep Cinematic Baritone)",
            model_id="eleven_multilingual_v2",
            stability=0.40,
            similarity_boost=0.84,
            style=0.38,
            speaking_rate_wpm=154,
        ),
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        default_model: str = "eleven_multilingual_v2",
    ) -> None:
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY", "").strip()
        self.default_model = default_model

        base_workspace = Path("/home/eudespatricio/dark_studio_platform/workspace/audio")
        self.cache_dir = Path(cache_dir) if cache_dir else (base_workspace / "tts_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.voice_profiles: Dict[str, VoiceProfile] = dict(self.DEFAULT_CHANNEL_VOICES)
        self.usage_history: List[TTSFinOpsRecord] = []
        self.total_characters_billed: int = 0
        self.total_characters_cached: int = 0
        self.total_cost_usd: float = 0.0

    def get_voice_profile(self, channel_id: str) -> VoiceProfile:
        """Returns the dedicated VoiceProfile for a given channel ID."""
        if channel_id in self.voice_profiles:
            return self.voice_profiles[channel_id]
        # Match by prefix or return Channel 1 default
        for key, profile in self.voice_profiles.items():
            if channel_id.lower() in key.lower():
                return profile
        return self.voice_profiles["ch_1_investigativo"]

    @staticmethod
    def compute_cache_hash(
        text: str,
        voice_id: str,
        model_id: str,
        stability: float,
        similarity_boost: float,
        style: float,
    ) -> str:
        """Computes a deterministic SHA-256 key so identical narrations never consume credits twice."""
        normalized_text = " ".join(text.strip().split())
        payload = f"{voice_id}|{model_id}|{stability:.2f}|{similarity_boost:.2f}|{style:.2f}|{normalized_text}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _estimate_duration_seconds(text: str, wpm: int = 158) -> float:
        words = max(1, len(text.strip().split()))
        return round(max(2.0, (words / float(wpm)) * 60.0), 2)

    @staticmethod
    def _generate_fallback_audio_file(target_path: Path, duration_sec: float, sample_rate: int = 24000) -> Path:
        """
        Generates a valid playable WAV/MP3-compatible audio file with subtle natural speech-envelope
        cadence so local FFmpeg pipelines and QA tests run without an ElevenLabs key.
        """
        target_path.parent.mkdir(parents=True, exist_ok=True)
        # Keep fallback file compact and fast while remaining 100% valid PCM WAV data
        capped_duration = min(max(duration_sec, 2.5), 15.0)
        num_samples = int(sample_rate * capped_duration)

        wav_path = target_path
        with wave.open(str(wav_path), "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit PCM
            wav_file.setframerate(sample_rate)

            frames = bytearray()
            for i in range(num_samples):
                t = i / float(sample_rate)
                # Syllabic amplitude envelope (~4 Hz speech cadence with natural pauses)
                syllable_env = max(0.0, math.sin(2.0 * math.pi * 3.8 * t))
                phrase_pause = 0.15 if (int(t * 1.2) % 4 == 3) else 1.0
                envelope = syllable_env * phrase_pause * 0.35

                # Warm baritone fundamental (115 Hz) + first two harmonics
                signal = (
                    0.60 * math.sin(2.0 * math.pi * 115.0 * t)
                    + 0.28 * math.sin(2.0 * math.pi * 230.0 * t)
                    + 0.12 * math.sin(2.0 * math.pi * 345.0 * t)
                )
                sample_val = int(max(-32767, min(32767, signal * envelope * 18000)))
                frames.extend(struct.pack("<h", sample_val))

            wav_file.writeframes(bytes(frames))

        return wav_path

    def synthesize_speech(
        self,
        text: str,
        channel_id: str = "ch_1_investigativo",
        voice_id: Optional[str] = None,
        model_id: Optional[str] = None,
        output_filename: Optional[str] = None,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Synthesizes narration audio via ElevenLabs API with SHA-256 caching and FinOps logging.
        Returns metadata including `audio_path`, `duration_sec`, `characters`, `cache_hit`,
        `estimated_cost_usd`, and `voice_profile`.
        """
        profile = self.get_voice_profile(channel_id)
        effective_voice_id = voice_id or profile.voice_id
        effective_model_id = model_id or profile.model_id

        clean_text = text.strip()

        # Dicionário de pronúncia e cadência cinematográfica
        # Melhora expressividade de termos técnicos e siglas nos 3 canais
        PRONUNCIATION_MAP = {
            "Banqiao": "Bân-tchiáu",
            "mTOR": "m-TÓR",
            "BDNF": "B-D-N-F",
            "HFT": "H-F-T",
            "NYSE": "N-Y-S-E",
            "CME": "C-M-E",
            "DJIA": "Dow Jones",
            "E-mini": "I-mini",
            "Navinder": "Na-vin-der",
            "Sarao": "Sa-ráu",
            "lipopolissacarídeo": "li-po-po-lis-sa-ca-rí-deo",
            "acetilcolina": "a-ce-til-co-li-na",
        }
        for orig, pron in PRONUNCIATION_MAP.items():
            if orig in clean_text:
                clean_text = clean_text.replace(orig, pron)

        # Inserção de micropausas naturais em pontuações dramáticas para enriquecer a locução neural
        clean_text = clean_text.replace(" — ", "... ").replace(" - ", ", ")
        char_count = len(clean_text)
        estimated_duration = self._estimate_duration_seconds(clean_text, profile.speaking_rate_wpm)

        cache_hash = self.compute_cache_hash(
            text=clean_text,
            voice_id=effective_voice_id,
            model_id=effective_model_id,
            stability=profile.stability,
            similarity_boost=profile.similarity_boost,
            style=profile.style,
        )

        ext = ".mp3" if self.api_key else ".wav"
        cached_file = self.cache_dir / f"{channel_id}_{cache_hash[:16]}{ext}"
        if output_filename:
            custom_target = Path(output_filename)
            if not custom_target.is_absolute():
                custom_target = self.cache_dir.parent / custom_target
        else:
            custom_target = cached_file

        # 1. Check SHA-256 Cache Hit
        if cached_file.exists() and cached_file.stat().st_size > 128 and not force_refresh:
            if custom_target != cached_file:
                custom_target.parent.mkdir(parents=True, exist_ok=True)
                custom_target.write_bytes(cached_file.read_bytes())

            self.total_characters_cached += char_count
            record = TTSFinOpsRecord(
                timestamp=time.time(),
                channel_id=channel_id,
                voice_id=effective_voice_id,
                model_id=effective_model_id,
                characters=char_count,
                cache_hit=True,
                estimated_cost_usd=0.0,
                audio_path=str(custom_target),
                duration_sec=estimated_duration,
            )
            self.usage_history.append(record)
            return {
                "status": "cached",
                "cache_hit": True,
                "cache_sha256": cache_hash,
                "channel_id": channel_id,
                "voice_id": effective_voice_id,
                "voice_name": profile.voice_name,
                "model_id": effective_model_id,
                "characters": char_count,
                "estimated_cost_usd": 0.0,
                "duration_sec": estimated_duration,
                "audio_path": str(custom_target),
            }

        # 2. Live ElevenLabs API Call if API key is present
        used_fallback = False
        if self.api_key:
            url = f"{self.ELEVENLABS_API_BASE}/text-to-speech/{effective_voice_id}"
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            }
            payload = {
                "text": clean_text,
                "model_id": effective_model_id,
                "voice_settings": {
                    "stability": profile.stability,
                    "similarity_boost": profile.similarity_boost,
                    "style": profile.style,
                    "use_speaker_boost": profile.use_speaker_boost,
                },
            }
            req_timeout = max(60, min(180, int(char_count / 25)))
            last_exc = None
            for attempt in range(1, 3):
                try:
                    response = requests.post(url, json=payload, headers=headers, timeout=req_timeout)
                    response.raise_for_status()
                    cached_file.write_bytes(response.content)
                    if custom_target != cached_file:
                        custom_target.parent.mkdir(parents=True, exist_ok=True)
                        custom_target.write_bytes(response.content)
                    last_exc = None
                    break
                except Exception as exc:
                    last_exc = exc
                    logger.warning("ElevenLabs tentativa %d/2 falhou (%s) timeout=%ds", attempt, str(exc)[:100], req_timeout)
                    if attempt < 2:
                        time.sleep(4)
            if last_exc is not None:
                logger.warning("ElevenLabs API falhou após retentativas, gerando local waveform fallback: %s", last_exc)
                used_fallback = True
                cached_file = self.cache_dir / f"{channel_id}_{cache_hash[:16]}.wav"
                self._generate_fallback_audio_file(cached_file, estimated_duration)
                if custom_target != cached_file:
                    custom_target.parent.mkdir(parents=True, exist_ok=True)
                    custom_target.write_bytes(cached_file.read_bytes())
        else:
            used_fallback = True
            cached_file = self.cache_dir / f"{channel_id}_{cache_hash[:16]}.wav"
            self._generate_fallback_audio_file(cached_file, estimated_duration)
            if custom_target != cached_file:
                custom_target.parent.mkdir(parents=True, exist_ok=True)
                custom_target.write_bytes(cached_file.read_bytes())

        cost_usd = round((char_count / 1000.0) * self.COST_PER_1K_CHARS_USD, 5)
        self.total_characters_billed += char_count
        self.total_cost_usd = round(self.total_cost_usd + cost_usd, 5)

        record = TTSFinOpsRecord(
            timestamp=time.time(),
            channel_id=channel_id,
            voice_id=effective_voice_id,
            model_id=effective_model_id,
            characters=char_count,
            cache_hit=False,
            estimated_cost_usd=cost_usd,
            audio_path=str(custom_target),
            duration_sec=estimated_duration,
        )
        self.usage_history.append(record)

        return {
            "status": "synthesized_fallback" if used_fallback else "synthesized_elevenlabs",
            "cache_hit": False,
            "used_fallback": used_fallback,
            "cache_sha256": cache_hash,
            "channel_id": channel_id,
            "voice_id": effective_voice_id,
            "voice_name": profile.voice_name,
            "model_id": effective_model_id,
            "characters": char_count,
            "estimated_cost_usd": cost_usd,
            "duration_sec": estimated_duration,
            "audio_path": str(custom_target),
        }

    def synthesize_dual_pipeline(
        self,
        long_script_blocks: List[Dict[str, Any]],
        short_script_text: str,
        channel_id: str = "ch_1_investigativo",
        job_id: str = "job_default",
    ) -> Dict[str, Any]:
        """
        Synthesizes both the 16:9 Long-Form narration and the 9:16 Short narration for a pipeline job,
        returning full audio paths, durations, and combined FinOps metrics.
        """
        long_text = " ".join(
            str(b.get("narration_text", "")).strip() for b in long_script_blocks if b.get("narration_text")
        ).strip()
        if not long_text:
            long_text = "Narração principal do documentário em formato longo dezesseis por nove."

        long_res = self.synthesize_speech(
            text=long_text,
            channel_id=channel_id,
            model_id="eleven_multilingual_v2",
            output_filename=f"{job_id}_long_16_9.wav",
        )
        short_res = self.synthesize_speech(
            text=short_script_text or "Narração dinâmica para YouTube Shorts focado em retenção máxima.",
            channel_id=channel_id,
            model_id="eleven_flash_v2_5",
            output_filename=f"{job_id}_short_9_16.wav",
        )

        total_chars = int(long_res["characters"]) + int(short_res["characters"])
        total_cost = round(float(long_res["estimated_cost_usd"]) + float(short_res["estimated_cost_usd"]), 5)

        return {
            "job_id": job_id,
            "channel_id": channel_id,
            "long_16_9_audio": long_res,
            "short_9_16_audio": short_res,
            "total_characters": total_chars,
            "total_estimated_cost_usd": total_cost,
        }

    def get_finops_summary(self) -> Dict[str, Any]:
        """Returns ElevenLabs character consumption, cache efficiency, and USD cost metrics."""
        total_chars = self.total_characters_billed + self.total_characters_cached
        cache_savings_usd = round((self.total_characters_cached / 1000.0) * self.COST_PER_1K_CHARS_USD, 4)
        return {
            "provider": "ElevenLabs TTS API",
            "models": ["eleven_multilingual_v2", "eleven_flash_v2_5"],
            "api_configured": bool(self.api_key),
            "total_requests": len(self.usage_history),
            "total_characters_billed": self.total_characters_billed,
            "total_characters_cached": self.total_characters_cached,
            "cache_hit_ratio_pct": round(
                (self.total_characters_cached / total_chars * 100.0) if total_chars > 0 else 0.0, 1
            ),
            "total_cost_usd": round(self.total_cost_usd, 4),
            "estimated_cache_savings_usd": cache_savings_usd,
            "voice_profiles": {
                cid: {
                    "channel_name": vp.channel_name,
                    "voice_id": vp.voice_id,
                    "voice_name": vp.voice_name,
                    "model_id": vp.model_id,
                }
                for cid, vp in self.voice_profiles.items()
            },
        }


_TTS_ENGINE_SINGLETON: Optional[TTSEngine] = None


def get_tts_engine() -> TTSEngine:
    """Returns singleton instance of TTSEngine."""
    global _TTS_ENGINE_SINGLETON
    if _TTS_ENGINE_SINGLETON is None:
        _TTS_ENGINE_SINGLETON = TTSEngine()
    return _TTS_ENGINE_SINGLETON
