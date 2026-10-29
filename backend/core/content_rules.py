"""
Regras de conteúdo derivadas dos diagnósticos do YouTube Studio (2026-10-22) — ver
docs/YOUTUBE_STUDIO_INSIGHTS_2026-10-22.md e docs/TEAM_ENRICHMENT_PLAN.md.

Princípios:
- Determinístico (mesmo slot -> mesmo resultado; não quebra cache/hash de render).
- Cada regra aplicada fica registrada em slot["rules_applied"] para o experimento controlado.
- Regras de gancho/título só avisam ou ajustam metadado de envio; nunca inventam fatos.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any, Dict, List, Tuple

# Interruptores (para o experimento de 1 variável por vez)
RULE_STRIP_SUBSCRIBE_CTA_SHORTS = True
RULE_COMMENT_QUESTION_SHORTS = True
RULE_SHORTEN_UPLOAD_TITLE = True
RULE_THUMB_MAX_WORDS = 4

TITLE_MAX_CHARS = 60

_CTA_RE = re.compile(r"(inscrev|se inscreva|siga o canal|ative o sino|deixe seu like|curta o v[ií]deo)", re.I)
_DANGLING = {"que", "de", "do", "da", "dos", "das", "e", "a", "o", "com", "para", "por", "um", "uma", "em", "no", "na", "como", "ao", "à", "ou"}
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")

# Aberturas passivas/conceituais que derrubam "continuaram assistindo" (Studio: Bio Hack e Finanças)
_PASSIVE_OPENERS = (
    "hoje vamos", "neste vídeo", "nesse vídeo", "bem-vindo", "bem vindo", "olá", "oi pessoal",
    "a biologia humana não foi projetada", "você sabia que", "vamos falar", "vou falar",
)

# Perguntas de julgamento para os últimos segundos (rotação determinística; hipótese a medir em comentários)
_QUESTIONS: Dict[int, List[str]] = {
    1: [
        "Você acha que isso foi negligência ou um acidente inevitável?",
        "Se estivesse lá, você teria percebido o erro a tempo?",
        "Quem você acha que realmente falhou nesta história?",
    ],
    2: [
        "Isso foi falha de sistema ou ganância humana?",
        "Você confiaria seu dinheiro a esse algoritmo?",
        "Esse tipo de colapso pode acontecer de novo?",
    ],
    3: [
        "Você testaria esse protocolo? Conta nos comentários.",
        "Qual desses hábitos você já sente no seu dia a dia?",
        "Isso muda a forma como você organiza o seu dia?",
    ],
}


def _pick(options: List[str], key: str) -> str:
    return options[int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16) % len(options)]


def strip_trailing_cta(narration: str) -> Tuple[str, bool]:
    """Remove frases de pedido de inscrição/like nas últimas 3 sentenças (fim de Short deve ser loop, sem despedida)."""
    sentences = [x for x in _SENT_SPLIT.split(narration.strip()) if x]
    changed = False
    while sentences and _CTA_RE.search(sentences[-1]) and len(sentences) > 2:
        sentences.pop()
        changed = True
    return " ".join(sentences), changed


def hook_flags(narration: str) -> List[str]:
    """Avisos sobre a primeira frase (gancho dos 2-3 s). Não veta."""
    first = (_SENT_SPLIT.split(narration.strip())[:1] or [""])[0].strip()
    flags: List[str] = []
    low = first.lower()
    if any(low.startswith(p) for p in _PASSIVE_OPENERS):
        flags.append("abertura_passiva")
    if len(first.split()) > 22:
        flags.append("gancho_longo(>22 palavras)")
    if not (re.search(r"\d", first) or "?" in first or re.search(r"\b(nunca|ninguém|segredo|proibid|fatal|morreu|apagou|ocult)", low)):
        flags.append("sem_numero_pergunta_ou_conflito")
    return flags


def shorten_upload_title(title: str, is_short: bool, max_chars: int = TITLE_MAX_CHARS) -> str:
    """Título de envio <= max_chars (mobile): preserva o mistério à frente e a tag #Shorts; remove a tag [DOCUMENTÁRIO]."""
    t = re.sub(r"\s*\[DOCUMENT[ÁA]RIO\]\s*", " ", title).strip()
    tag = ""
    if "#Shorts" in t:
        t = t.replace("#Shorts", "").strip()
        tag = " #Shorts"
    budget = max_chars - len(tag)
    if len(t) <= budget:
        return (t + tag).strip()
    # corta no melhor limite: antes do último ':' / ',' / espaço que caiba no orçamento
    cut = t[:budget]
    for sep in (":", ",", " "):
        k = cut.rfind(sep)
        if k >= int(budget * 0.55):
            cut = cut[:k]
            break
    words = cut.rstrip(" :,-").split()
    while len(words) > 3 and words[-1].lower() in _DANGLING:
        words.pop()  # não termina em "que", "de", "com"...
    return (" ".join(words).rstrip(" :,-") + tag).strip()


def thumb_headline(title: str, max_words: int = 3, max_chars: int = 28) -> str:
    """Texto de miniatura: estritamente 2 a 3 palavras completas de alto impacto (nunca corta palavras ao meio)."""
    head = title.split(":")[0].replace("#Shorts", "").replace("[DOCUMENTÁRIO]", "").strip()
    dangling = {"o", "a", "os", "as", "um", "uma", "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas", "por", "para", "com", "que", "e"}
    words = [w for w in head.split() if w.lower() not in dangling]
    if len(words) > max_words:
        words = words[:max_words]
    if len(words) < 2:
        words = [w for w in head.split()][:max_words]
    out_words: List[str] = []
    curr_len = 0
    for w in words:
        w_clean = re.sub(r"[^\w\dÀ-ÿ]", "", w).upper()
        if not w_clean:
            continue
        extra = 1 if out_words else 0
        if curr_len + len(w_clean) + extra <= max_chars:
            out_words.append(w_clean)
            curr_len += len(w_clean) + extra
        else:
            break
    if not out_words:
        first_word = words[0] if words else "SEGREDO"
        out_words = [re.sub(r"[^\w\dÀ-ÿ]", "", first_word).upper()]
    return " ".join(out_words)


def apply_narration_rules(channel_num: int, narration: str, is_short: bool, slot_id: str) -> Tuple[str, List[str]]:
    """Aplica as regras de roteiro. Retorna (narração, regras_aplicadas)."""
    applied: List[str] = []
    text = narration
    if is_short and RULE_STRIP_SUBSCRIBE_CTA_SHORTS:
        text, changed = strip_trailing_cta(text)
        if changed:
            applied.append("sem_cta_inscricao_no_fim")
    if is_short and RULE_COMMENT_QUESTION_SHORTS and not text.rstrip().endswith("?"):
        q = _pick(_QUESTIONS.get(channel_num, _QUESTIONS[1]), f"{slot_id}:{channel_num}")
        text = text.rstrip().rstrip(".") + ". " + q
        applied.append("pergunta_de_comentario_final")
    flags = hook_flags(text)
    if flags:
        applied.append("AVISO_gancho:" + ",".join(flags))
    return text, applied
