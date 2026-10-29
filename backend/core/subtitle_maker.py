"""
Gerador Profissional de Legendas Dinâmicas .ASS (Advanced SubStation Alpha v4.00+).
Suporta retenção máxima estilo Alex Hormozi / CapCut com sincronia palavra por palavra,
destaque de cor ativa (amarelo/verde neon) e animação pop-in para:
- 16:9 Horizontal (1920x1080) - Legenda cinematográfica inferior
- 9:16 Vertical (1080x1920) - Legenda centralizada de alto impacto para Shorts/Reels/TikTok
"""

from __future__ import annotations

import math
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union


@dataclass
class WordTimestamp:
    """Representa uma única palavra com seus tempos de início e fim em segundos."""

    word: str
    start: float
    end: float
    confidence: float = 0.99
    highlight: bool = False

    def duration(self) -> float:
        return max(0.05, self.end - self.start)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SubtitleStyleProfile:
    """Perfil tipográfico e posicional para geração de arquivo .ASS."""

    name: str
    aspect_ratio: str
    play_res_x: int
    play_res_y: int
    font_name: str
    font_size: int
    primary_color: str  # Formato ASS: &HAABBGGRR
    secondary_color: str
    active_word_color: str  # Amarelo Neon (&H0000FFFF) ou Verde Neon (&H0014FF39)
    emphasis_word_color: str
    outline_color: str
    back_color: str
    bold: int
    outline: float
    shadow: float
    alignment: int  # 2 = Bottom Center (16:9), 5 = Middle Center (9:16)
    margin_l: int
    margin_r: int
    margin_v: int
    max_words_per_chunk: int
    uppercase: bool = True
    pop_in_tag: str = r"\fscx115\fscy115\t(0,80,\fscx100\fscy100)"


# Perfis oficiais 16:9 e 9:16
PROFILE_16_9 = SubtitleStyleProfile(
    name="Cinema16x9",
    aspect_ratio="16:9",
    play_res_x=1920,
    play_res_y=1080,
    font_name="Montserrat ExtraBold",
    font_size=62,
    primary_color="&H00FFFFFF",       # Branco puro
    secondary_color="&H00B0B0B0",     # Cinza claro
    active_word_color="&H0000FFFF",   # Amarelo Neon (BGR: 00 FF FF)
    emphasis_word_color="&H0014FF39", # Verde Neon (BGR: 14 FF 39)
    outline_color="&H00000000",       # Contorno preto profundo
    back_color="&H80000000",          # Sombra semi-transparente
    bold=-1,
    outline=4.0,
    shadow=2.5,
    alignment=2,                      # Parte inferior centralizada
    margin_l=120,
    margin_r=120,
    margin_v=78,
    max_words_per_chunk=6,
    uppercase=False,
    pop_in_tag=r"\fscx108\fscy108\t(0,70,\fscx100\fscy100)",
)

PROFILE_9_16 = SubtitleStyleProfile(
    name="Hormozi9x16",
    aspect_ratio="9:16",
    play_res_x=1080,
    play_res_y=1920,
    font_name="Montserrat Black",
    font_size=60,                      # Otimizado: legibilidade máxima sem estourar 1080px de largura
    primary_color="&H00FFFFFF",       # Branco puro
    secondary_color="&H00E0E0E0",     # Cinza suave
    active_word_color="&H0000FFFF",   # Amarelo Neon vibrante
    emphasis_word_color="&H0014FF39", # Verde Neon vibrante
    outline_color="&H00000000",       # Contorno preto nítido
    back_color="&H96000000",          # Sombra densa
    bold=-1,
    outline=4.5,
    shadow=3.0,
    alignment=5,                      # Centro absoluto da tela (estilo Hormozi/CapCut)
    margin_l=120,                     # Margem de segurança lateral contra botões do YouTube Shorts
    margin_r=120,
    margin_v=160,
    max_words_per_chunk=2,            # 1 a 2 palavras por bloco visual para impacto imediato
    uppercase=True,
    pop_in_tag=r"\fscx108\fscy108\t(0,60,\fscx100\fscy100)",
)


POWER_KEYWORDS = {
    "segredo", "bilhões", "milhões", "dinheiro", "nunca", "sempre", "proibido",
    "oculto", "verdade", "perigo", "agora", "choque", "impossível", "erro",
    "morte", "vida", "poder", "império", "colapso", "milionário", "fortuna",
    "secret", "billion", "million", "never", "shocking", "truth", "danger",
}


class SubtitleMaker:
    """
    Motor gerador de legendas .ASS palavra-a-palavra com suporte a 16:9 e 9:16.
    Implementa highlight dinâmico por palavra falada, pop-in elástico e
    fallback de alinhamento temporal caso apenas o texto bruto seja fornecido.
    """

    def __init__(self, output_dir: Optional[Union[str, Path]] = None) -> None:
        base_dir = Path("/home/eudespatricio/dark_studio_platform/workspace/renders")
        self.output_dir = Path(output_dir) if output_dir else base_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def format_ass_time(seconds: float) -> str:
        """
        Converte segundos (float) para o formato de tempo do padrão ASS: H:MM:SS.cc
        (centésimos de segundo).
        """
        seconds = max(0.0, float(seconds))
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centiseconds = int(round((seconds - math.floor(seconds)) * 100))
        if centiseconds >= 100:
            centiseconds = 99
        return f"{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"

    @staticmethod
    def get_profile(
        aspect_ratio: str = "16:9",
        active_color_mode: str = "yellow",
    ) -> SubtitleStyleProfile:
        """Retorna o perfil configurado para 16:9 ou 9:16."""
        normalized = aspect_ratio.strip().lower()
        is_vertical = normalized in {"9:16", "vertical", "short", "shorts", "reels", "1080x1920"}
        base = PROFILE_9_16 if is_vertical else PROFILE_16_9

        active_color = base.active_word_color
        if active_color_mode.lower() in {"green", "neon_green", "verde"}:
            active_color = "&H0014FF39"
        elif active_color_mode.lower() in {"yellow", "neon_yellow", "amarelo"}:
            active_color = "&H0000FFFF"
        elif active_color_mode.lower() in {"cyan", "neon_cyan", "azul", "blue"}:
            active_color = "&H00F5F500"

        return SubtitleStyleProfile(
            **{
                **asdict(base),
                "active_word_color": active_color,
            }
        )

    def normalize_words(
        self,
        words_or_text: Union[str, Sequence[Union[WordTimestamp, Dict[str, Any]]]],
        total_duration: Optional[float] = None,
        start_offset: float = 0.0,
    ) -> List[WordTimestamp]:
        """
        Normaliza diferentes formatos de entrada (lista de dicts do Whisper,
        objetos WordTimestamp ou string de roteiro puro) em uma lista contínua
        de `WordTimestamp`.
        """
        if isinstance(words_or_text, str):
            return self._estimate_word_timestamps_from_text(
                words_or_text,
                total_duration=total_duration,
                start_offset=start_offset,
            )

        normalized: List[WordTimestamp] = []
        for item in words_or_text:
            if isinstance(item, WordTimestamp):
                normalized.append(item)
            elif isinstance(item, dict):
                # Verifica se é um segmento contendo lista 'words'
                if "words" in item and isinstance(item["words"], list):
                    for sub in item["words"]:
                        w_text = str(sub.get("word") or sub.get("text") or "").strip()
                        if not w_text:
                            continue
                        w_start = float(sub.get("start", 0.0)) + start_offset
                        w_end = float(sub.get("end", w_start + 0.25)) + start_offset
                        normalized.append(
                            WordTimestamp(
                                word=w_text,
                                start=w_start,
                                end=max(w_start + 0.05, w_end),
                                confidence=float(sub.get("confidence", sub.get("probability", 0.98))),
                                highlight=bool(sub.get("highlight", False)),
                            )
                        )
                else:
                    w_text = str(item.get("word") or item.get("text") or "").strip()
                    if not w_text:
                        continue
                    # Se o dict tem múltiplas palavras sem sub-timestamps, divide proporcionalmente
                    tokens = w_text.split()
                    seg_start = float(item.get("start", 0.0)) + start_offset
                    seg_end = float(item.get("end", seg_start + max(0.3, len(tokens) * 0.32))) + start_offset
                    if len(tokens) > 1:
                        normalized.extend(
                            self._estimate_word_timestamps_from_text(
                                w_text,
                                total_duration=max(0.2, seg_end - seg_start),
                                start_offset=seg_start,
                            )
                        )
                    else:
                        clean_tok = re.sub(r"[^\wÀ-ÿ]", "", w_text).lower()
                        normalized.append(
                            WordTimestamp(
                                word=w_text,
                                start=seg_start,
                                end=max(seg_start + 0.05, seg_end),
                                confidence=float(item.get("confidence", item.get("probability", 0.98))),
                                highlight=bool(item.get("highlight", clean_tok in POWER_KEYWORDS)),
                            )
                        )

        # Garante que nenhuma legenda sobreponha o Poster Frame inicial nos primeiros 0.25s
        if normalized and normalized[0].start < 0.25:
            normalized[0].start = 0.25
            normalized[0].end = max(0.35, normalized[0].end)

        return normalized

    def _estimate_word_timestamps_from_text(
        self,
        text: str,
        total_duration: Optional[float] = None,
        start_offset: float = 0.0,
    ) -> List[WordTimestamp]:
        """
        Gera timestamps palavra-a-palavra realistas baseados no peso fonético
        (comprimento de caracteres + pausas de pontuação) quando apenas o texto é fornecido.
        """
        raw_tokens = [tok.strip() for tok in re.split(r"\s+", text.strip()) if tok.strip()]
        if not raw_tokens:
            return []

        weights: List[float] = []
        pauses: List[float] = []
        for tok in raw_tokens:
            clean = re.sub(r"[^\wÀ-ÿ]", "", tok).lower()
            char_weight = max(1.0, len(clean) ** 0.75)
            weights.append(char_weight)
            if tok.endswith((".", "!", "?", "...")):
                pauses.append(0.18)
            elif tok.endswith((",", ";", ":", "—", "-")):
                pauses.append(0.09)
            else:
                pauses.append(0.01)

        if total_duration is None or total_duration <= 0:
            # Taxa média de locução dinâmica: ~2.9 palavras por segundo
            total_duration = max(1.2, len(raw_tokens) * 0.34 + sum(pauses))

        total_pause = min(total_duration * 0.28, sum(pauses))
        pause_scale = (total_pause / sum(pauses)) if sum(pauses) > 0 else 0.0
        speaking_budget = max(0.2, total_duration - total_pause)
        total_weight = sum(weights) or 1.0

        cursor = start_offset
        result: List[WordTimestamp] = []
        for idx, tok in enumerate(raw_tokens):
            word_dur = speaking_budget * (weights[idx] / total_weight)
            pause_dur = pauses[idx] * pause_scale
            start_t = round(cursor, 3)
            end_t = round(cursor + max(0.06, word_dur), 3)
            clean_tok = re.sub(r"[^\wÀ-ÿ]", "", tok).lower()
            is_power = clean_tok in POWER_KEYWORDS or any(ch.isdigit() for ch in tok)
            result.append(
                WordTimestamp(
                    word=tok,
                    start=start_t,
                    end=end_t,
                    confidence=0.95,
                    highlight=is_power,
                )
            )
            cursor = end_t + pause_dur

        return result

    def group_words_into_chunks(
        self,
        words: Sequence[WordTimestamp],
        max_words_per_chunk: int = 4,
        max_chars_per_chunk: int = 28,
        pause_threshold: float = 0.45,
    ) -> List[List[WordTimestamp]]:
        """
        Agrupa palavras em blocos visuais curtos respeitando pausas naturais,
        pontuação forte e limite de palavras/caracteres do perfil (9:16 ou 16:9).
        """
        chunks: List[List[WordTimestamp]] = []
        current_chunk: List[WordTimestamp] = []
        current_chars = 0

        for idx, word_obj in enumerate(words):
            w_len = len(word_obj.word)
            if current_chunk:
                prev_word = current_chunk[-1]
                silence_gap = word_obj.start - prev_word.end
                ended_sentence = prev_word.word.endswith((".", "!", "?", ":", ";"))
                exceeds_words = len(current_chunk) >= max_words_per_chunk
                exceeds_chars = (current_chars + 1 + w_len) > max_chars_per_chunk

                if exceeds_words or exceeds_chars or silence_gap >= pause_threshold or ended_sentence:
                    chunks.append(current_chunk)
                    current_chunk = []
                    current_chars = 0

            current_chunk.append(word_obj)
            current_chars += w_len + (1 if current_chars > 0 else 0)

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    @staticmethod
    def _escape_ass_text(text: str) -> str:
        """Escapa chaves e barras especiais do formato ASS."""
        return text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")

    def build_ass_content(
        self,
        words_or_text: Union[str, Sequence[Union[WordTimestamp, Dict[str, Any]]]],
        aspect_ratio: str = "9:16",
        total_duration: Optional[float] = None,
        active_color_mode: str = "yellow",
        title: str = "Dark Studio Platform Dynamic Subtitles",
        source_credit: Optional[str] = None,
    ) -> str:
        """
        Constrói o conteúdo completo do arquivo `.ASS` com cabeçalho `[Script Info]`,
        `[V4+ Styles]` e eventos `[Events]` palavra por palavra com animação pop-in.
        """
        profile = self.get_profile(aspect_ratio=aspect_ratio, active_color_mode=active_color_mode)
        words = self.normalize_words(words_or_text, total_duration=total_duration)

        max_chars = 14 if profile.aspect_ratio == "9:16" else 44
        chunks = self.group_words_into_chunks(
            words,
            max_words_per_chunk=profile.max_words_per_chunk,
            max_chars_per_chunk=max_chars,
        )

        header = [
            "[Script Info]",
            f"; Script generated by Dark Studio Platform - {profile.name}",
            f"Title: {title}",
            "ScriptType: v4.00+",
            "WrapStyle: 0",
            "ScaledBorderAndShadow: yes",
            "YCbCr Matrix: TV.709",
            f"PlayResX: {profile.play_res_x}",
            f"PlayResY: {profile.play_res_y}",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
            "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
            "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            (
                f"Style: {profile.name},{profile.font_name},{profile.font_size},"
                f"{profile.primary_color},{profile.secondary_color},{profile.outline_color},{profile.back_color},"
                f"{profile.bold},0,0,0,100,100,1.0,0,1,{profile.outline:.1f},{profile.shadow:.1f},"
                f"{profile.alignment},{profile.margin_l},{profile.margin_r},{profile.margin_v},1"
            ),
            (
                # Estilo Lower-Third Elegante para Fontes e Créditos Documentais (discreto, topo/canto superior ou inferior seguro)
                "Style: SourceCredit,Arial,28,&H00D0D0D0,&H00FFFFFF,&H00000000,&H80000000,"
                "0,0,0,0,100,100,0.5,0,1,2.0,1.5,7,40,40,60,1" if profile.aspect_ratio == "9:16" else
                "Style: SourceCredit,Arial,22,&H00E0E0E0,&H00FFFFFF,&H00000000,&H80000000,"
                "0,0,0,0,100,100,0.5,0,1,1.8,1.2,7,50,50,45,1"
            ),
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        ]

        dialogue_lines: List[str] = []
        if source_credit:
            safe_credit = self._escape_ass_text(source_credit.strip())
            # Exibe lower-third discreto com fade-in e fade-out elegante nos primeiros segundos
            credit_line = (
                f"Dialogue: 1,0:00:01.00,0:00:08.50,SourceCredit,,0,0,0,,"
                f"{{\\fad(500,500)}}FONTES: {safe_credit}"
            )
            dialogue_lines.append(credit_line)

        for chunk in chunks:
            if not chunk:
                continue

            # Para cada palavra ativa no bloco, emitimos uma linha Dialogue cobrindo o intervalo
            # exato da palavra falada, destacando-a com cor neon + escala e aplicando pop-in
            for active_idx, active_word in enumerate(chunk):
                # Garante que nos primeiros 0.25s (Poster Frame / Thumbnail) nenhuma legenda seja exibida
                start_sec = max(0.25, active_word.start) if profile.aspect_ratio == "9:16" else active_word.start
                start_ts = self.format_ass_time(start_sec)
                # Garante continuidade visual até a próxima palavra do mesmo bloco
                if active_idx + 1 < len(chunk):
                    end_sec = max(start_sec + 0.10, max(active_word.end, chunk[active_idx + 1].start))
                else:
                    end_sec = max(start_sec + 0.10, active_word.end)
                end_ts = self.format_ass_time(end_sec)

                rendered_tokens: List[str] = []
                for token_idx, token_obj in enumerate(chunk):
                    raw_word = token_obj.word.upper() if profile.uppercase else token_obj.word
                    safe_word = self._escape_ass_text(raw_word)

                    if token_idx == active_idx:
                        # Palavra sendo pronunciada no momento: destaque Amarelo/Verde Neon
                        highlight_color = (
                            profile.emphasis_word_color
                            if token_obj.highlight
                            else profile.active_word_color
                        )
                        active_tag = (
                            f"{{\\1c{highlight_color}\\3c{profile.outline_color}"
                            f"\\bord{profile.outline + 1.0:.1f}\\fscx112\\fscy112}}"
                            f"{safe_word}"
                            f"{{\\1c{profile.primary_color}\\bord{profile.outline:.1f}\\fscx100\\fscy100}}"
                        )
                        rendered_tokens.append(active_tag)
                    elif token_idx < active_idx:
                        # Palavra já pronunciada no bloco atual: branco sólido
                        rendered_tokens.append(
                            f"{{\\1c{profile.primary_color}}}{safe_word}"
                        )
                    else:
                        # Palavra futura no bloco: leve atenuação para guiar leitura ocular
                        rendered_tokens.append(
                            f"{{\\1c{profile.secondary_color}}}{safe_word}"
                        )

                # No início do bloco ou em cada palavra do Short 9:16, aplica animação pop-in
                if active_idx == 0 or profile.aspect_ratio == "9:16":
                    line_prefix = f"{{{profile.pop_in_tag}}}"
                else:
                    line_prefix = ""

                line_text = line_prefix + " ".join(rendered_tokens)
                dialogue_lines.append(
                    f"Dialogue: 0,{start_ts},{end_ts},{profile.name},,0,0,0,,{line_text}"
                )

        return "\n".join(header + dialogue_lines) + "\n"

    def generate_ass(
        self,
        words_or_text: Union[str, Sequence[Union[WordTimestamp, Dict[str, Any]]]],
        output_path: Optional[Union[str, Path]] = None,
        aspect_ratio: str = "9:16",
        total_duration: Optional[float] = None,
        active_color_mode: str = "yellow",
        title: str = "Dark Studio Platform Dynamic Subtitles",
    ) -> Dict[str, Any]:
        """
        Gera e salva o arquivo `.ASS` no disco, retornando metadados detalhados
        (caminho do arquivo, contagem de palavras, blocos, duração coberta e perfil).
        """
        profile = self.get_profile(aspect_ratio=aspect_ratio, active_color_mode=active_color_mode)
        words = self.normalize_words(words_or_text, total_duration=total_duration)
        ass_content = self.build_ass_content(
            words,
            aspect_ratio=aspect_ratio,
            total_duration=total_duration,
            active_color_mode=active_color_mode,
            title=title,
        )

        if output_path is None:
            suffix = "9x16" if profile.aspect_ratio == "9:16" else "16x9"
            output_file = self.output_dir / f"subtitles_{suffix}.ass"
        else:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

        output_file.write_text(ass_content, encoding="utf-8")

        computed_duration = (words[-1].end - words[0].start) if words else (total_duration or 0.0)
        return {
            "subtitle_path": str(output_file.resolve()),
            "aspect_ratio": profile.aspect_ratio,
            "resolution": f"{profile.play_res_x}x{profile.play_res_y}",
            "style_name": profile.name,
            "word_count": len(words),
            "duration_sec": round(float(computed_duration), 3),
            "pop_in_animation": profile.pop_in_tag,
            "active_word_color": profile.active_word_color,
        }

    def generate_dual_profiles(
        self,
        words_or_text: Union[str, Sequence[Union[WordTimestamp, Dict[str, Any]]]],
        base_name: str = "project",
        total_duration: Optional[float] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Gera simultaneamente os arquivos `.ASS` para o vídeo Longo (16:9) e para o Short (9:16).
        """
        safe_base = re.sub(r"[^a-zA-Z0-9_-]", "_", base_name)
        long_path = self.output_dir / f"{safe_base}_16x9.ass"
        short_path = self.output_dir / f"{safe_base}_9x16.ass"

        return {
            "16:9": self.generate_ass(
                words_or_text,
                output_path=long_path,
                aspect_ratio="16:9",
                total_duration=total_duration,
                active_color_mode="yellow",
            ),
            "9:16": self.generate_ass(
                words_or_text,
                output_path=short_path,
                aspect_ratio="9:16",
                total_duration=total_duration,
                active_color_mode="green",
            ),
        }


_SUBTITLE_MAKER_INSTANCE: Optional[SubtitleMaker] = None


def get_subtitle_maker(output_dir: Optional[Union[str, Path]] = None) -> SubtitleMaker:
    """Singleton factory para `SubtitleMaker`."""
    global _SUBTITLE_MAKER_INSTANCE
    if _SUBTITLE_MAKER_INSTANCE is None or output_dir is not None:
        _SUBTITLE_MAKER_INSTANCE = SubtitleMaker(output_dir=output_dir)
    return _SUBTITLE_MAKER_INSTANCE
