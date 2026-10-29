"""
Core AI Engines for Dark Studio Platform:
- llm_engine: Google Gemini API (google-genai) for script transcreation, multimodal analysis & FinOps token tracking
- tts_engine: ElevenLabs API for multi-channel voice synthesis with SHA-256 caching & character cost tracking
- transcriber: Faster-Whisper integration with word-level timestamp alignment
"""

from .llm_engine import LLMEngine, get_llm_engine
from .tts_engine import TTSEngine, get_tts_engine
from .transcriber import TranscriberEngine, get_transcriber_engine
from .subtitle_maker import SubtitleMaker, get_subtitle_maker
from .quality_scorer import QualityScorer

__all__ = [
    "LLMEngine",
    "get_llm_engine",
    "TTSEngine",
    "get_tts_engine",
    "TranscriberEngine",
    "get_transcriber_engine",
    "SubtitleMaker",
    "get_subtitle_maker",
    "QualityScorer",
]
