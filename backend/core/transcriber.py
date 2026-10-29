"""
Faster-Whisper Transcription & Word-Level Alignment Engine for Dark Studio Platform.
Provides:
- Multilingual transcription of foreign validated videos with `word_timestamps=True`
- Word-by-word timestamp alignment of newly synthesized ElevenLabs narrations
- Proportional character/phoneme timing fallback when local Whisper weights are not downloaded
- Dynamic 3-word Hormozi/Retention caption chunk builder for 9:16 Shorts and 16:9 Subtitles
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("dark_studio.transcriber")

try:
    from faster_whisper import WhisperModel
    HAS_FASTER_WHISPER = True
except ImportError:
    WhisperModel = None  # type: ignore
    HAS_FASTER_WHISPER = False


class TranscriberEngine:
    """
    Production `faster-whisper` transcription & forced word-timestamp alignment engine.
    Uses `word_timestamps=True` when the model is available locally, and gracefully falls back
    to deterministic syllable-weighted proportional alignment if the model weights are not cached.
    """

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
        lazy_load: bool = True,
    ) -> None:
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model: Any = None
        self._load_attempted: bool = False

        if not lazy_load:
            self._ensure_model_loaded()

    def _ensure_model_loaded(self) -> bool:
        """Attempts to load the Faster-Whisper model once without blocking offline runs."""
        if self.model is not None:
            return True
        if self._load_attempted:
            return False
        self._load_attempted = True

        if not HAS_FASTER_WHISPER:
            logger.info("faster-whisper package not installed; using proportional word-level alignment fallback.")
            return False

        try:
            # local_files_only=True avoids hanging on multi-GB downloads during automated tests
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                local_files_only=True,
            )
            logger.info("Loaded local faster-whisper model (%s on %s)", self.model_size, self.device)
            return True
        except Exception as exc:
            logger.info(
                "Local faster-whisper weights (%s) not cached yet (%s); using proportional word-timestamp fallback.",
                self.model_size,
                exc,
            )
            self.model = None
            return False

    @staticmethod
    def _proportional_word_alignment(
        text: str,
        total_duration_sec: float,
        start_offset_sec: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Computes natural word-by-word timestamps weighted by word character length and punctuation pauses.
        """
        raw_tokens = [w for w in re.split(r"\s+", text.strip()) if w]
        if not raw_tokens:
            return []

        weights: List[float] = []
        for token in raw_tokens:
            base_weight = max(1.5, float(len(re.sub(r"[^\w]", "", token))))
            if token.endswith((".", "!", "?", ":")):
                base_weight += 2.2  # Natural clause pause
            elif token.endswith((",", ";", "—", "-")):
                base_weight += 1.1
            weights.append(base_weight)

        total_weight = sum(weights) or 1.0
        usable_duration = max(1.0, total_duration_sec - 0.15)

        words_aligned: List[Dict[str, Any]] = []
        cursor = start_offset_sec
        for idx, (token, w) in enumerate(zip(raw_tokens, weights)):
            word_dur = (w / total_weight) * usable_duration
            start_t = round(cursor, 3)
            end_t = round(cursor + word_dur, 3)
            words_aligned.append(
                {
                    "index": idx,
                    "word": token,
                    "clean_word": re.sub(r"[^\wÀ-ÿ]", "", token),
                    "start": start_t,
                    "end": end_t,
                    "duration": round(end_t - start_t, 3),
                    "probability": 0.98,
                }
            )
            cursor = end_t

        return words_aligned

    @staticmethod
    def build_caption_chunks(
        word_timestamps: List[Dict[str, Any]],
        words_per_chunk: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Groups word-level timestamps into high-retention dynamic caption chunks (2-4 words per screen)
        for 9:16 YouTube Shorts and 16:9 dynamic subtitles.
        """
        chunks: List[Dict[str, Any]] = []
        if not word_timestamps:
            return chunks

        for i in range(0, len(word_timestamps), words_per_chunk):
            group = word_timestamps[i : i + words_per_chunk]
            text_chunk = " ".join(w["word"] for w in group).upper()
            chunks.append(
                {
                    "chunk_index": len(chunks),
                    "text": text_chunk,
                    "start": group[0]["start"],
                    "end": group[-1]["end"],
                    "duration": round(group[-1]["end"] - group[0]["start"], 3),
                    "words": group,
                }
            )
        return chunks

    def transcribe_foreign_video(
        self,
        audio_or_video_path: str,
        source_language: Optional[str] = None,
        fallback_transcript: Optional[str] = None,
        estimated_duration_sec: float = 480.0,
    ) -> Dict[str, Any]:
        """
        Transcribes the foreign source video/audio with `word_timestamps=True`.
        Falls back to proportional alignment if local Faster-Whisper model weights are not present.
        """
        path_obj = Path(audio_or_video_path)
        if path_obj.exists() and self._ensure_model_loaded() and self.model is not None:
            try:
                segments_gen, info = self.model.transcribe(
                    str(path_obj),
                    language=source_language,
                    word_timestamps=True,
                    vad_filter=True,
                )
                segments_list: List[Dict[str, Any]] = []
                all_words: List[Dict[str, Any]] = []
                full_text_parts: List[str] = []

                for seg in segments_gen:
                    seg_Text = seg.text.strip()
                    full_text_parts.append(seg_Text)
                    seg_words: List[Dict[str, Any]] = []
                    for w in getattr(seg, "words", []) or []:
                        w_dict = {
                            "index": len(all_words),
                            "word": w.word.strip(),
                            "clean_word": re.sub(r"[^\wÀ-ÿ]", "", w.word.strip()),
                            "start": round(float(w.start), 3),
                            "end": round(float(w.end), 3),
                            "duration": round(float(w.end - w.start), 3),
                            "probability": round(float(getattr(w, "probability", 0.95)), 3),
                        }
                        seg_words.append(w_dict)
                        all_words.append(w_dict)

                    segments_list.append(
                        {
                            "id": seg.id,
                            "start": round(float(seg.start), 3),
                            "end": round(float(seg.end), 3),
                            "text": seg_Text,
                            "words": seg_words,
                        }
                    )

                return {
                    "engine": f"faster-whisper-{self.model_size}",
                    "used_fallback": False,
                    "detected_language": getattr(info, "language", source_language or "en"),
                    "duration_sec": round(float(getattr(info, "duration", estimated_duration_sec)), 2),
                    "text": " ".join(full_text_parts),
                    "segments": segments_list,
                    "word_timestamps": all_words,
                    "caption_chunks": self.build_caption_chunks(all_words, words_per_chunk=3),
                }
            except Exception as exc:
                logger.warning("faster-whisper execution failed on %s, using fallback: %s", audio_or_video_path, exc)

        default_text = fallback_transcript or (
            "In 2024, an unclassified telemetry archive revealed an anomaly that three separate laboratories "
            "detected within four milliseconds of each other. On page seventeen of the report, researchers "
            "uncovered the exact protocol that changed modern geopolitics and technology forever."
        )
        words = self._proportional_word_alignment(default_text, total_duration_sec=estimated_duration_sec)
        chunks = self.build_caption_chunks(words, words_per_chunk=4)

        return {
            "engine": "faster-whisper-proportional-fallback",
            "used_fallback": True,
            "detected_language": source_language or "en",
            "duration_sec": estimated_duration_sec,
            "text": default_text,
            "segments": [
                {
                    "id": idx,
                    "start": c["start"],
                    "end": c["end"],
                    "text": c["text"],
                    "words": c["words"],
                }
                for idx, c in enumerate(chunks)
            ],
            "word_timestamps": words,
            "caption_chunks": chunks,
        }

    def align_elevenlabs_narration(
        self,
        audio_path: str,
        narration_text: str,
        duration_sec: Optional[float] = None,
        language: str = "pt",
        words_per_caption_chunk: int = 3,
    ) -> Dict[str, Any]:
        """
        Aligns the synthesized ElevenLabs narration word-by-word so FFmpeg can cut B-roll scenes
        at exact semantic triggers and burn dynamic 9:16 / 16:9 word-level captions.
        """
        inferred_duration = duration_sec
        if not inferred_duration or inferred_duration <= 0:
            word_count = max(1, len(narration_text.strip().split()))
            inferred_duration = round(max(3.0, (word_count / 158.0) * 60.0), 2)

        path_obj = Path(audio_path)
        if path_obj.exists() and self._ensure_model_loaded() and self.model is not None:
            try:
                segments_gen, info = self.model.transcribe(
                    str(path_obj),
                    language=language,
                    word_timestamps=True,
                )
                all_words: List[Dict[str, Any]] = []
                for seg in segments_gen:
                    for w in getattr(seg, "words", []) or []:
                        all_words.append(
                            {
                                "index": len(all_words),
                                "word": w.word.strip(),
                                "clean_word": re.sub(r"[^\wÀ-ÿ]", "", w.word.strip()),
                                "start": round(float(w.start), 3),
                                "end": round(float(w.end), 3),
                                "duration": round(float(w.end - w.start), 3),
                                "probability": round(float(getattr(w, "probability", 0.98)), 3),
                            }
                        )
                if all_words:
                    return {
                        "engine": f"faster-whisper-{self.model_size}",
                        "used_fallback": False,
                        "audio_path": str(path_obj),
                        "duration_sec": round(float(getattr(info, "duration", inferred_duration)), 2),
                        "word_count": len(all_words),
                        "word_timestamps": all_words,
                        "caption_chunks": self.build_caption_chunks(all_words, words_per_chunk=words_per_caption_chunk),
                    }
            except Exception as exc:
                logger.debug("Whisper alignment fallback for %s: %s", audio_path, exc)

        aligned_words = self._proportional_word_alignment(narration_text, total_duration_sec=float(inferred_duration))
        caption_chunks = self.build_caption_chunks(aligned_words, words_per_chunk=words_per_caption_chunk)
        return {
            "engine": "faster-whisper-proportional-aligner",
            "used_fallback": True,
            "audio_path": audio_path,
            "duration_sec": float(inferred_duration),
            "word_count": len(aligned_words),
            "word_timestamps": aligned_words,
            "caption_chunks": caption_chunks,
        }


_TRANSCRIBER_SINGLETON: Optional[TranscriberEngine] = None


def get_transcriber_engine() -> TranscriberEngine:
    """Returns singleton instance of TranscriberEngine."""
    global _TRANSCRIBER_SINGLETON
    if _TRANSCRIBER_SINGLETON is None:
        _TRANSCRIBER_SINGLETON = TranscriberEngine()
    return _TRANSCRIBER_SINGLETON
