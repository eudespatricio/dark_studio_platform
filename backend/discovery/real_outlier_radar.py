"""
Radar real de outliers por tema de canal (substitui o pool simulado de outlier_hunter._get_seed_outlier_pool).

Fluxo: busca (yt-dlp, sem gastar cota da YouTube Data API) -> metadados completos dos melhores candidatos ->
média recente do canal-fonte -> outlier_score = views / média -> VPH -> filtros -> deduplicação -> fila de pautas.

Regras de integridade:
- Nada é inventado: todo número vem do yt-dlp. Se o YouTube bloquear/limitar, o candidato é descartado e o erro registrado.
- Idempotente por dia (intake_state.json) para nunca virar loop de busca.
- O vídeo-fonte é SINAL DE TEMA + fatos; o roteiro final é reescrito de forma original (ver core/pauta_writer.py).
"""

from __future__ import annotations

import json
import logging
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
AUTOMATION_DIR = BASE_DIR / "workspace/automation"
THEMES_FILE = AUTOMATION_DIR / "channel_topic_themes.json"
QUEUE_FILE = AUTOMATION_DIR / "topic_queue.json"

logger = logging.getLogger("real_outlier_radar")

MIN_OUTLIER_SCORE = 3.0
MIN_VPH = 5.0                 # views/hora mínimas (evergreen: bem abaixo do 150 do radar simulado)
MAX_AGE_DAYS = 1825           # evergreen: a demanda comprovada pelo score vale mais que a data (5 anos)
MIN_DURATION_SEC = 300        # fonte com pelo menos 5 min (documentário/explicação)
MAX_DURATION_SEC = 5400
MIN_VIEWS = 20_000
SEARCH_RESULTS_PER_QUERY = 25
ENRICH_PER_CHANNEL = 15       # mais candidatos avaliados para garantir acervo robusto
CHANNEL_AVG_SAMPLE = 12

DEFAULT_THEMES: Dict[str, Dict[str, Any]] = {
    "1": {
        "name": "A Via da Descoberta",
        "niche": "Mistérios históricos, engenharia extrema e desastres investigados",
        "queries": [
            "desastre de engenharia colapso documentário",
            "mistério histórico arquivos desclassificados documentário",
            "engineering disaster investigation documentary",
            "declassified secret operation documentary",
            "catástrofe industrial o que realmente aconteceu",
        ],
    },
    "2": {
        "name": "Finanças Quânticas",
        "niche": "Wall Street quantitativo, algoritmos, quebras de mercado e fundos",
        "queries": [
            "hedge fund quant collapse documentary",
            "flash crash algorithmic trading explained",
            "high frequency trading scandal documentary",
            "fundo quantitativo história Wall Street documentário",
            "fraude financeira trader documentário",
        ],
    },
    "3": {
        "name": "Bio Hack Longevidade",
        "niche": "Neurociência aplicada, longevidade, ritmos biológicos e protocolos de foco",
        "queries": [
            "neurociência foco dopamina protocolo explicado",
            "longevidade NAD autofagia jejum ciência",
            "circadian rhythm cortisol morning light neuroscience",
            "ultradian rhythm focus neuroscience explained",
            "mitocôndria envelhecimento ciência documentário",
        ],
    },
}


def load_themes() -> Dict[str, Dict[str, Any]]:
    if THEMES_FILE.exists():
        try:
            return json.loads(THEMES_FILE.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            logger.warning("channel_topic_themes.json inválido (%s); usando padrão.", exc)
    AUTOMATION_DIR.mkdir(parents=True, exist_ok=True)
    THEMES_FILE.write_text(json.dumps(DEFAULT_THEMES, indent=2, ensure_ascii=False), encoding="utf-8")
    return DEFAULT_THEMES


def _ydl(opts: Optional[Dict[str, Any]] = None):
    import yt_dlp  # type: ignore

    base = {"quiet": True, "no_warnings": True, "skip_download": True, "socket_timeout": 20, "retries": 2}
    base.update(opts or {})
    return yt_dlp.YoutubeDL(base)


def search_flat(query: str, n: int = SEARCH_RESULTS_PER_QUERY) -> List[Dict[str, Any]]:
    with _ydl({"extract_flat": "in_playlist"}) as y:
        res = y.extract_info(f"ytsearch{n}:{query}", download=False)
    return [e for e in (res or {}).get("entries", []) if e and e.get("id")]


def channel_recent_avg_views(channel_id: str, exclude_video_id: str) -> Optional[float]:
    """Média de views dos últimos vídeos do canal-fonte (exclui o próprio candidato)."""
    try:
        with _ydl({"extract_flat": "in_playlist", "playlistend": CHANNEL_AVG_SAMPLE}) as y:
            res = y.extract_info(f"https://www.youtube.com/channel/{channel_id}/videos", download=False)
        views = [int(e["view_count"]) for e in (res or {}).get("entries", [])
                 if e and e.get("id") != exclude_video_id and e.get("view_count") is not None]
        return (sum(views) / len(views)) if len(views) >= 3 else None
    except Exception as exc:  # noqa: BLE001
        logger.debug("média do canal %s indisponível: %s", channel_id, exc)
        return None


def fetch_full_info(video_id: str) -> Optional[Dict[str, Any]]:
    try:
        with _ydl() as y:
            return y.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
    except Exception as exc:  # noqa: BLE001
        logger.debug("extract_info falhou %s: %s", video_id, exc)
        return None


def fetch_transcript(info: Dict[str, Any], max_chars: int = 12000) -> str:
    """Legenda (manual ou automática) em texto corrido, sem baixar mídia. Vazio se indisponível."""
    import requests  # type: ignore

    for pool in ("subtitles", "automatic_captions"):
        caps = info.get(pool) or {}
        for lang in ("pt", "pt-BR", "en", "es"):
            for variant in caps.get(lang, []) or []:
                if variant.get("ext") == "json3":
                    try:
                        data = requests.get(variant["url"], timeout=20).json()
                        parts = ["".join(s.get("utf8", "") for s in ev.get("segs", []) if s) for ev in data.get("events", [])]
                        txt = re.sub(r"\s+", " ", " ".join(p for p in parts if p)).strip()
                        if txt:
                            return txt[:max_chars]
                    except Exception:  # noqa: BLE001
                        continue
    return ""


def _heatmap(info: Dict[str, Any]) -> List[Dict[str, float]]:
    return [
        {"start": float(h.get("start_time", 0)), "end": float(h.get("end_time", 0)), "intensity": float(h.get("value", 0))}
        for h in (info.get("heatmap") or [])
    ]


def discover_for_channel(channel_num: int, consumed_check=None, themes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Descobre, valida e retorna candidatos aprovados para um canal. Nunca lança exceção para o chamador."""
    themes = themes or load_themes()
    cfg = themes.get(str(channel_num), {})
    report: Dict[str, Any] = {"channel": channel_num, "searched": 0, "shortlist": 0, "validated": [], "rejected": [], "errors": []}
    seen: Dict[str, Dict[str, Any]] = {}
    for q in cfg.get("queries", []):
        try:
            for e in search_flat(q):
                dur = e.get("duration") or 0
                views = e.get("view_count") or 0
                if MIN_DURATION_SEC <= dur <= MAX_DURATION_SEC and views >= MIN_VIEWS:
                    seen.setdefault(e["id"], {**e, "_query": q})
            report["searched"] += 1
            time.sleep(0.6)
        except Exception as exc:  # noqa: BLE001
            report["errors"].append(f"busca '{q}': {str(exc)[:120]}")
    shortlist = sorted(seen.values(), key=lambda e: e.get("view_count") or 0, reverse=True)
    if consumed_check:
        shortlist = [e for e in shortlist if not consumed_check(e["id"], e.get("title", ""))]
    shortlist = shortlist[:ENRICH_PER_CHANNEL]
    report["shortlist"] = len(shortlist)

    now = datetime.now(timezone.utc)
    for e in shortlist:
        info = fetch_full_info(e["id"])
        if not info:
            report["errors"].append(f"{e['id']}: extração falhou")
            continue
        views = int(info.get("view_count") or 0)
        upl = info.get("upload_date")
        try:
            published = datetime.strptime(upl, "%Y%m%d").replace(tzinfo=timezone.utc)
        except Exception:  # noqa: BLE001
            report["errors"].append(f"{e['id']}: sem data de publicação")
            continue
        age_days = max(1, (now - published).days)
        hours = max(1.0, (now - published).total_seconds() / 3600.0)
        if age_days > MAX_AGE_DAYS:
            report["rejected"].append({"id": e["id"], "why": f"antigo ({age_days}d)"})
            continue
        avg = channel_recent_avg_views(info.get("channel_id", ""), e["id"]) if info.get("channel_id") else None
        if not avg:
            report["rejected"].append({"id": e["id"], "why": "sem média do canal-fonte (amostra < 3 vídeos)"})
            continue
        score = round(views / avg, 2)
        vph = round(views / hours, 2)
        if score < MIN_OUTLIER_SCORE or vph < MIN_VPH:
            report["rejected"].append({"id": e["id"], "why": f"score {score}x / VPH {vph}", "title": info.get("title", "")[:60]})
            continue
        report["validated"].append({
            "video_id": e["id"],
            "title_original": info.get("title", ""),
            "source_language": (info.get("language") or "und"),
            "source_channel": info.get("channel", ""),
            "source_channel_id": info.get("channel_id", ""),
            "channel_subscribers": info.get("channel_follower_count"),
            "views": views,
            "channel_avg_views": int(avg),
            "outlier_score": score,
            "vph": vph,
            "duration_sec": int(info.get("duration") or 0),
            "published_days_ago": age_days,
            "source_url": f"https://www.youtube.com/watch?v={e['id']}",
            "thumbnail_url": info.get("thumbnail", ""),
            "heatmap": _heatmap(info),
            "has_captions": bool(info.get("subtitles") or info.get("automatic_captions")),
            "matched_query": e.get("_query"),
            "discovered_at": now.isoformat(),
            "status": "queued",
        })
        time.sleep(0.8)
    report["validated"].sort(key=lambda c: c["outlier_score"] * 0.6 + min(c["vph"], 1000) / 1000 * 0.4, reverse=True)
    return report


def load_queue() -> Dict[str, List[Dict[str, Any]]]:
    if QUEUE_FILE.exists():
        try:
            return json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            pass
    return {"1": [], "2": [], "3": []}


def save_queue(q: Dict[str, List[Dict[str, Any]]]) -> None:
    from backend.publisher.cadence_guard_filter import atomic_write_json

    atomic_write_json(QUEUE_FILE, q)
