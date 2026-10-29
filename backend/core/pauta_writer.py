"""
Redator de pautas: transforma um outlier validado (tema + fatos da fonte) em um pacote ORIGINAL
(1 Longo + 4 Shorts) para o canal. O vídeo-fonte é sinal de tema e referência factual; nada é copiado.

Integridade:
- Sem API Gemini => retorna None (NUNCA fabrica roteiro de fallback).
- Guard de plágio: sobreposição de 8-gramas com a transcrição-fonte > 4% => rejeita.
- Fatos têm nível de confiança; muitos fatos de baixa confiança => pauta vai para revisão humana.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger("pauta_writer")

CHANNEL_STYLE: Dict[int, str] = {
    1: (
        "Canal 'A Via da Descoberta' (mistérios históricos, engenharia extrema, desastres investigados). Tom: documentário "
        "investigativo sóbrio. Gancho com a contradição, o perigo ou o fato inacreditável. Finais de Short: pergunta de julgamento "
        "(ex.: negligência ou acidente inevitável?)."
    ),
    2: (
        "Canal 'Finanças Quânticas' (Wall Street quantitativo, algoritmos, quebras de mercado). Tom: analítico e acessível. "
        "O gancho quantifica fortunas/perdas/tempo logo na 1ª frase. Explique HFT, spoofing, arbitragem etc. com metáforas do cotidiano. "
        "Narrativa 'o gênio contra o sistema'."
    ),
    3: (
        "Canal 'Bio Hack Longevidade' (neurociência aplicada, ritmos biológicos, longevidade). Tom: científico e prático. "
        "Estrutura Problema -> Consequência -> Solução rápida. Gancho com dado ou pergunta que toque uma dor real. "
        "PROIBIDO: promessas de cura, dosagens, conselho médico individual; descreva mecanismos e evidências com cautela."
    ),
}

RULES = """
REGRAS DE ROTEIRO E ENGENHARIA DE RETENÇÃO (validadas no YouTube Studio dos nossos canais):
- Short: 85 a 110 palavras (a voz fala ~2 palavras/s; o Short deve durar 40-55 s).
  * REGRA DOS 2 SEGUNDOS NO GANCHO: A PRIMEIRA frase (<= 20 palavras) DEVE abrir com a CONSEQUÊNCIA, PERIGO, DANO OU FATO CHOCANTE
    (ex: 'Dois matemáticos faliram Wall Street em 4 horas por este erro', 'Esta massa emite tanta radiação que 300 segundos eram fatais').
    PROIBIDO abrir com nomes teóricos frios ('A Fórmula de...', 'O Conceito de...', 'Os Ciclos de...') ou saudações ('Hoje vamos ver...').
  * FIM EM LOOP: PROIBIDO pedir inscrição/like/seguir no texto do áudio. Termine com uma pergunta de opinião que conecte ao gancho.
  * Cada Short cobre um ângulo diferente e deixa uma ponta solta crucial que só o Longo resolve.
- Longo: 520 a 650 palavras (cerca de 3,5 a 4,5 minutos). Gancho de alta tensão nos primeiros 15 segundos. A cada 60-90 segundos
  uma quebra de expectativa ou nova pergunta ('Mas o que ninguém sabia era que...'). Frases curtas, ritmo cinematográfico contínuo.
- MINIATURAS (THUMBNAILS - 2 A 3 PALAVRAS COM SENTIDO CONTEXTUAL):
  * Tanto para o Longo quanto para cada Short, gere 'thumb_headline': exatamente 2 ou 3 palavras em CAIXA ALTA que façam sentido contextual
    profundo com a história e gerem curiosidade irresistível (ex: 'FALHA MORTAL', '24 HORAS', 'PROIBIDO PELA FÍSICA', 'BILHÕES EVAPORARAM',
    'ARQUIVO SECRETO', 'ERRO FATAL'). Nunca use palavras desconexas da narrativa nem repita o título idêntico.
- BUSCAS VISUAIS WIKIMEDIA COMMONS (VISUAL QUERIES):
  * Exatamente 8 a 10 buscas em INGLÊS focadas em ENTIDADES FÍSICAS REAIS: nomes próprios de figuras históricas, locais geográficos exatos,
    modelos de aeronaves/máquinas/reatores, documentos desclassificados ou fotos de época. PROIBIDO termos conceituais abstratos ('Trading', 'Dopamine').
- Escreva em português do Brasil, números por extenso ou falados em voz alta, sem emojis, sem marcações de cena.
- ORIGINALIDADE: reescreva tudo com suas palavras e outra estrutura. Não cite o canal-fonte nem copie trechos.
- FATOS: use apenas fatos da transcrição ou registros históricos/científicos consolidados. Liste fatos com confiança alta/media/baixa.
- Título do Longo: <= 60 caracteres, mistério central nos primeiros 40. Títulos de Short: <= 52 caracteres + ' #Shorts'.
"""


def _ngrams(text: str, n: int = 8) -> set:
    w = re.findall(r"\w+", text.lower())
    return {" ".join(w[i:i + n]) for i in range(max(0, len(w) - n + 1))}


def plagiarism_ratio(generated: str, source: str) -> float:
    g = _ngrams(generated)
    if not g or not source:
        return 0.0
    return len(g & _ngrams(source)) / float(len(g))


def _words(t: str) -> int:
    return len(re.findall(r"\w+", t))


def validate_package(pkg: Dict[str, Any], source_transcript: str) -> List[str]:
    """Retorna lista de problemas (vazia = aprovado)."""
    problems: List[str] = []
    long = pkg.get("long") or {}
    shorts = pkg.get("shorts") or []
    lw = _words(long.get("narration_text", ""))
    if not (250 <= lw <= 700):
        problems.append(f"longo com {lw} palavras (esperado 250-650)")
    if not (2 <= len(shorts) <= 4):
        problems.append(f"{len(shorts)} shorts (esperado 2 a 4)")
    for i, s in enumerate(shorts, 1):
        sw = _words(s.get("narration_text", ""))
        if not (75 <= sw <= 125):
            problems.append(f"short {i} com {sw} palavras (esperado 85-110)")
    all_text = long.get("narration_text", "") + " " + " ".join(s.get("narration_text", "") for s in shorts)
    ratio = plagiarism_ratio(all_text, source_transcript)
    if ratio > 0.04:
        problems.append(f"sobreposição com a fonte {ratio:.1%} (> 4%)")
    pkg["plagiarism_ratio"] = round(ratio, 4)
    return problems


def write_pauta(channel_num: int, candidate: Dict[str, Any], transcript: str) -> Optional[Dict[str, Any]]:
    from backend.core.llm_engine import get_llm_engine

    eng = get_llm_engine()
    if eng.client is None:
        logger.error("Gemini indisponível: pauta NÃO será gerada (sem fallback fabricado).")
        return None
    try:
        from google.genai import types as genai_types  # type: ignore
    except Exception:  # noqa: BLE001
        return None

    prompt = f"""
Você é roteirista-chefe de um canal de documentários curtos no YouTube.
{CHANNEL_STYLE.get(channel_num, CHANNEL_STYLE[1])}
{RULES}

TEMA SINALIZADO PELO VÍDEO-FONTE (outlier {candidate.get('outlier_score')}x, {candidate.get('views')} views):
Título original: {candidate.get('title_original')}
TRANSCRIÇÃO DE REFERÊNCIA (apenas para extrair fatos; NÃO copie):
{transcript[:9000] if transcript else '(sem legenda disponível: use somente fatos amplamente estabelecidos sobre o tema)'}

Retorne EXCLUSIVAMENTE um JSON válido:
{{
  "topic_title_pt": "tema em português em uma frase",
  "core_conflict": "o conflito central em 1 frase",
  "long": {{
    "title": "título <= 60 caracteres com mistério nos primeiros 40",
    "hook": "primeira frase com alta tensão",
    "narration_text": "roteiro completo do longo (520-650 palavras)",
    "thumb_headline": "2 a 3 palavras contextualizadas em CAIXA ALTA"
  }},
  "shorts": [
    {{
      "angle_name": "ângulo específico",
      "title": "TÍTULO <= 52 caracteres #Shorts",
      "hook": "primeira frase com consequência/perigo direto",
      "narration_text": "roteiro do short (85-110 palavras)",
      "thumb_headline": "2 a 3 palavras contextualizadas em CAIXA ALTA"
    }}
  ],
  "facts": [{{"claim": "...", "confidence": "alta|media|baixa"}}],
  "tags": ["8 a 12 tags em português"],
  "visual_queries": ["8 a 10 buscas em INGLÊS no Wikimedia Commons focadas em pessoas, lugares, documentos e máquinas reais"]
}}
"""
    import time as _time

    import os as _os

    # Cadeia de modelos: principal -> fallbacks (cota diaria do 3.8 Flash e 20 RPD no free tier)
    models = [eng.model_name] + [m.strip() for m in _os.getenv("PAUTA_FALLBACK_MODELS", "gemini-3.5-flash-lite,gemini-3.1-flash-lite").split(",") if m.strip()]
    resp = None
    for model in models:
        for attempt, wait in enumerate((0, 5), 1):
            if wait:
                _time.sleep(wait)
            try:
                cfg = genai_types.GenerateContentConfig(
                    temperature=0.8,
                    response_mime_type="application/json",
                    http_options=genai_types.HttpOptions(timeout=45000),
                )
                resp = eng.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=cfg,
                )
                break
            except Exception as exc:  # noqa: BLE001
                msg = str(exc)
                quota = "429" in msg or "RESOURCE_EXHAUSTED" in msg
                server_err = any(code in msg for code in ("503", "504", "UNAVAILABLE", "DEADLINE_EXCEEDED", "timed out", "timeout", "Timeout"))
                logger.warning("Gemini %s tentativa %d falhou (%s)", model, attempt, msg[:80])
                if quota or server_err:
                    break  # sem espera desnecessaria; pula direto para o proximo modelo da cadeia
        if resp is not None:
            try:
                eng._extract_json(getattr(resp, "text", "") or "")
            except Exception as exc:  # noqa: BLE001
                logger.warning("JSON invalido de %s (%s) - proximo modelo", model, str(exc)[:60])
                resp = None
                continue
            logger.info("Pauta gerada com %s", model)
            break
    if resp is None:
        logger.error("Falha ao gerar pauta (canal %s) após retentativas.", channel_num)
        return None
    try:
        raw = getattr(resp, "text", "") or ""
        pkg = eng._extract_json(raw)
        usage = getattr(resp, "usage_metadata", None)
        eng._record_usage(
            operation="pauta_writer",
            input_tokens=int(getattr(usage, "prompt_token_count", 0) or len(prompt) // 4),
            output_tokens=int(getattr(usage, "candidates_token_count", 0) or len(raw) // 4),
            used_fallback=False,
            channel_id=str(channel_num),
            video_id=candidate.get("video_id", ""),
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Falha ao gerar pauta (canal %s): %s", channel_num, exc)
        return None

    problems = validate_package(pkg, transcript)
    low = sum(1 for f in pkg.get("facts", []) if str(f.get("confidence", "")).lower() == "baixa")
    total = max(1, len(pkg.get("facts", [])))
    pkg["validation_problems"] = problems
    pkg["needs_review"] = bool(problems) or (low / total > 0.3) or not pkg.get("facts")
    return pkg
