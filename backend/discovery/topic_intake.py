"""
Intake diário de pautas (primeiro passo da aplicação): descobrir -> validar outlier -> deduplicar -> escrever pauta
original -> reunir acervo aberto -> enfileirar. O rollover da meia-noite consome a fila (nunca mais repete pautas).

Limites (anti-loop e custo):
- Fila máxima por canal = MAX_QUEUE_PER_CHANNEL (1-2 dias de conteúdo pré-produzido).
- Idempotente: intake_state.json guarda tentativas por canal/dia; backoff entre tentativas; teto de 3 por dia.
- Roda na janela noturna (03:00 BRT) ou manualmente (--force).
"""

from __future__ import annotations

import json
import logging
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.discovery import real_outlier_radar as radar

BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
INTAKE_STATE = BASE_DIR / "workspace/automation/intake_state.json"
AUTO_ASSETS = BASE_DIR / "workspace/scenes/auto"

MAX_QUEUE_PER_CHANNEL = 3
MAX_ATTEMPTS_PER_DAY = 3
RETRY_BACKOFF_SEC = 4 * 3600
INTAKE_WINDOW_BRT = (3, 4)

logger = logging.getLogger("topic_intake")


def _today_brt() -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=-3)).strftime("%Y-%m-%d")


def _load_state() -> Dict[str, Any]:
    if INTAKE_STATE.exists():
        try:
            return json.loads(INTAKE_STATE.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            pass
    return {}


def _save_state(st: Dict[str, Any]) -> None:
    from backend.publisher.cadence_guard_filter import atomic_write_json

    atomic_write_json(INTAKE_STATE, st)


def queue_depth(queue: Dict[str, List[Dict[str, Any]]], ch: int) -> int:
    return sum(1 for p in queue.get(str(ch), []) if p.get("status") == "scripted")


_DOC_TITLE_RE = re.compile(r"(memo|letter|document|report|page|transcript|telegram|manuscript|firman|newspaper|clipping|scan|form\b|\.pdf|\.tif)", re.I)


def image_quality(path: str) -> Dict[str, float]:
    """Métricas rápidas para triagem visual: fração clara, saturação média e contraste."""
    from PIL import Image  # type: ignore
    import numpy as np  # type: ignore

    im = Image.open(path).convert("RGB")
    im.thumbnail((256, 256))
    a = np.asarray(im).astype("float32")
    gray = a.mean(axis=2)
    mx, mn = a.max(axis=2), a.min(axis=2)
    sat = float(np.mean((mx - mn) / np.maximum(mx, 1)))
    return {"bright_frac": float(np.mean(gray > 190)), "sat": sat, "std": float(gray.std()), "mean": float(gray.mean())}


def is_document_scan(item: Dict[str, Any]) -> bool:
    """Página de texto/memorando/manuscrito: visual ruim para vídeo (parede de texto sob a legenda)."""
    if _DOC_TITLE_RE.search(item.get("title") or ""):
        return True
    try:
        q = image_quality(item["path"])
    except Exception:  # noqa: BLE001
        return False
    return q["bright_frac"] > 0.45 and q["sat"] < 0.18


def thumb_background_score(path: str) -> float:
    """Prefere fotos escuras/contrastadas com pessoas/lugares; penaliza páginas claras."""
    q = image_quality(path)
    return q["std"] * 0.5 + q["sat"] * 40 - q["bright_frac"] * 60 - abs(q["mean"] - 95) * 0.2


def best_thumbnail_background(paths: List[str]) -> Optional[str]:
    scored = []
    for pth in paths:
        try:
            scored.append((thumb_background_score(pth), pth))
        except Exception:  # noqa: BLE001
            continue
    return max(scored)[1] if scored else None


def _tokens(text: str) -> set:
    import unicodedata

    t = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode().lower()
    return {w for w in re.findall(r"[a-z0-9]{4,}", t)}


def align_assets_to_narration(assets_meta: List[Dict[str, Any]], narration: str, n_scenes: int) -> List[str]:
    """Ordena os assets cena a cena conforme o trecho da narração (nomes próprios em comum com título/busca do arquivo).
    Sem correspondência, usa rodízio do menos recentemente usado (variedade), nunca repetindo a cena anterior."""
    words = narration.split()
    if not assets_meta or not words or n_scenes < 1:
        return [a["path"] for a in assets_meta]
    per = max(1, len(words) // n_scenes)
    meta_tokens = [_tokens(f"{a.get('title', '')} {a.get('query', '')}") for a in assets_meta]
    last_used = [-99] * len(assets_meta)
    out: List[str] = []
    for i in range(n_scenes):
        chunk = " ".join(words[i * per:(i + 1) * per] if i < n_scenes - 1 else words[i * per:])
        ct = _tokens(chunk)
        best, best_score = None, -1e9
        for j, mt in enumerate(meta_tokens):
            overlap = len(ct & mt)
            recency = i - last_used[j]
            window = min(5, len(assets_meta) - 1)  # nunca repete imagem dentro da janela (Sentinel veta clonagem de cena)
            score = overlap * 10 + min(recency, 8) - (100 if recency <= window else 0)
            if score > best_score:
                best, best_score = j, score
        last_used[best] = i
        out.append(assets_meta[best]["path"])
    return out


def collect_assets(
    pauta_id: str,
    queries: List[str],
    per_query: int = 4,
    cap: int = 35,
    topic_title: str = "",
    channel_num: int = 1,
) -> List[Dict[str, Any]]:
    """
    Coleta acervo multimídia de alta retenção (Dark Cinema 3.0):
    - Pixabay API: Clipes de vídeo MP4 e fotografias HD
    - Wikimedia Commons: Fotos e vídeos de arquivo histórico
    - CinematicDocumentsGenerator: Memos secretos e manchetes de jornal
    """
    target_dir = AUTO_ASSETS / pauta_id
    target_dir.mkdir(parents=True, exist_ok=True)
    got: List[Dict[str, Any]] = []
    seen_paths = set()

    # 1. Pixabay Video & Photo
    try:
        from backend.media.pixabay_client import PixabayClient
        px = PixabayClient(target_dir=target_dir)
        if px.is_configured:
            for q in queries[:6]:
                for v_item in px.search_videos(q, limit=2):
                    vp = px.download_video(v_item, target_dir=target_dir, prefix="px_vid")
                    if vp and str(vp) not in seen_paths:
                        got.append({
                            "path": str(vp),
                            "kind": "video",
                            "license": "Pixabay Content License (Free Commercial Use)",
                            "attribution": "Pixabay Video Contributor",
                            "title": v_item.get("tags", q),
                            "query": q,
                        })
                        seen_paths.add(str(vp))
                    if len(got) >= 12:
                        break
                if len(got) >= 12:
                    break

            for q in queries[:8]:
                for img_item in px.search_photos(q, limit=2):
                    ip = px.download_photo(img_item, target_dir=target_dir, prefix="px_img")
                    if ip and str(ip) not in seen_paths:
                        got.append({
                            "path": str(ip),
                            "kind": "image",
                            "license": "Pixabay Content License (Free Commercial Use)",
                            "attribution": "Pixabay Contributor",
                            "title": img_item.get("tags", q),
                            "query": q,
                        })
                        seen_paths.add(str(ip))
                    if len(got) >= 24:
                        break
                if len(got) >= 24:
                    break
    except Exception as exc:
        logger.warning("Aviso ao buscar acervo Pixabay no intake: %s", exc)

    # 2. Wikimedia Commons (Arquivos Abertos)
    try:
        from backend.discovery.open_archive_fetcher import OpenArchiveFetcher
        fetcher = OpenArchiveFetcher(target_dir=target_dir)
        for q in queries[:8]:
            if len(got) >= cap:
                break
            for item in fetcher.search_media(q, limit=per_query):
                if item.get("width", 0) < 850:
                    continue
                p = fetcher.download_asset(item, prefix=re.sub(r"\W+", "_", q)[:20])
                if p and str(p) not in seen_paths:
                    entry = {
                        "path": str(p),
                        "kind": "video" if p.suffix.lower() in (".webm", ".mp4", ".ogv") else "image",
                        "license": item.get("license"),
                        "attribution": item.get("attribution"),
                        "title": item.get("title"),
                        "query": q,
                    }
                    if is_document_scan(entry):
                        continue
                    got.append(entry)
                    seen_paths.add(str(p))
                if len(got) >= cap:
                    break
            time.sleep(0.3)
    except Exception as exc:
        logger.warning("Aviso ao buscar acervo Wikimedia no intake: %s", exc)

    # 3. Gerar Documentos Cinemáticos de Época (Pillow)
    try:
        from backend.media.cinematic_documents_generator import CinematicDocumentsGenerator
        cdg = CinematicDocumentsGenerator(output_dir=target_dir)
        clean_title = (topic_title or pauta_id).replace("_", " ")

        memo_path = target_dir / f"declassified_memo_{pauta_id[:16]}.png"
        cdg.generate_declassified_memo(
            target_path=memo_path,
            agency_name="GOVERNMENT ARCHIVES // HISTORIC DOSSIER" if channel_num == 1 else ("FINANCIAL INTELLIGENCE REGULATOR" if channel_num == 2 else "BIO-MED RESEARCH ARCHIVES"),
            doc_title=clean_title[:55].upper(),
            highlight_quote=f"ANOMALY IDENTIFIED: {clean_title[:45].upper()}",
        )
        if str(memo_path) not in seen_paths:
            got.append({
                "path": str(memo_path),
                "kind": "image",
                "license": "Procedural Dark Studio Original",
                "attribution": "Dark Studio Platform",
                "title": "Declassified Incident Memo",
                "query": "declassified memo",
            })
            seen_paths.add(str(memo_path))

        news_path = target_dir / f"vintage_newspaper_{pauta_id[:16]}.png"
        cdg.generate_newspaper_clipping(
            target_path=news_path,
            headline=clean_title[:50].upper(),
            subheadline="Special Investigation Reveals Critical Timeline of Events",
        )
        if str(news_path) not in seen_paths:
            got.append({
                "path": str(news_path),
                "kind": "image",
                "license": "Procedural Dark Studio Original",
                "attribution": "Dark Studio Platform",
                "title": "Vintage Newspaper Clipping",
                "query": "vintage newspaper",
            })
            seen_paths.add(str(news_path))
    except Exception as exc:
        logger.warning("Aviso ao gerar documentos de apoio: %s", exc)

    logger.info("Coleta de acervo para %s finalizada: %d assets obtidos (cap=%d)", pauta_id, len(got), cap)
    return got


def run_intake(channels=(1, 2, 3), force: bool = False) -> Dict[str, Any]:
    from backend.core import pauta_writer
    from backend.discovery.source_deduplicator import source_deduplicator as sd

    today = _today_brt()
    state = _load_state()
    queue = radar.load_queue()
    for k in ("1", "2", "3"):
        queue.setdefault(k, [])
    result: Dict[str, Any] = {}

    for ch in channels:
        key = str(ch)
        cs = state.setdefault(key, {})
        if cs.get("date") != today:
            cs.update({"date": today, "attempts": 0, "last_attempt": 0})
        if queue_depth(queue, ch) >= MAX_QUEUE_PER_CHANNEL:
            result[key] = "fila cheia (teto de pré-produção)"
            continue
        if not force:
            if cs["attempts"] >= MAX_ATTEMPTS_PER_DAY:
                result[key] = "limite de tentativas diárias atingido"
                continue
            if time.time() - cs["last_attempt"] < RETRY_BACKOFF_SEC:
                result[key] = "aguardando backoff"
                continue
        cs["attempts"] += 1
        cs["last_attempt"] = time.time()
        _save_state(state)

        need = MAX_QUEUE_PER_CHANNEL - queue_depth(queue, ch)
        rep = radar.discover_for_channel(ch, consumed_check=lambda i, t: sd.is_source_consumed(i, t)[0])
        made = 0
        for cand in rep["validated"]:
            if made >= need:
                break
            info = radar.fetch_full_info(cand["video_id"]) or {}
            transcript = radar.fetch_transcript(info) if info else ""
            pkg = pauta_writer.write_pauta(ch, cand, transcript)
            if not pkg:
                continue
            pauta_id = f"p{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{ch}_{cand['video_id']}"
            assets = collect_assets(
                pauta_id,
                pkg.get("visual_queries", []),
                cap=35,
                topic_title=cand.get("title_original") or pkg.get("topic_title_pt", ""),
                channel_num=ch,
            )
            status = "scripted" if (not pkg["needs_review"] and len(assets) >= 12) else "needs_review"
            queue[key].append({
                "pauta_id": pauta_id, "channel": ch, "status": status, "created_at": datetime.now(timezone.utc).isoformat(),
                "source": {k: cand[k] for k in ("video_id", "title_original", "source_url", "outlier_score", "vph", "views", "channel_avg_views", "source_channel")},
                "package": pkg, "assets": assets,
                "review_reasons": pkg.get("validation_problems", []) + ([] if len(assets) >= 12 else [f"acervo aberto insuficiente ({len(assets)} mídias)"]),
            })
            # Reserva a fonte para nunca ser reaproveitada (mesmo que a pauta vá para revisão)
            sd.mark_source_consumed(cand["video_id"], cand["title_original"], cand["source_url"])
            made += 1
            radar.save_queue(queue)
        result[key] = {"discovered": len(rep["validated"]), "rejected": len(rep["rejected"]), "queued": made, "errors": rep["errors"][:3]}
    _save_state(state)
    radar.save_queue(queue)
    return result


def consume_next_pauta(channel_num: int) -> Optional[Dict[str, Any]]:
    """Usado pelo rollover: entrega a próxima pauta pronta (status scripted) e a marca como em produção."""
    queue = radar.load_queue()
    for p in queue.get(str(channel_num), []):
        if p.get("status") == "scripted":
            p["status"] = "in_production"
            p["used_on"] = _today_brt()
            radar.save_queue(queue)
            return p
    return None


def apply_pauta_to_slots(slots: List[Dict[str, Any]], pauta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Preenche os slots de horário (1 Longo + 4 Shorts) com o conteúdo original da pauta."""
    pkg = pauta["package"]
    shorts = list(pkg.get("shorts", []))
    asset_paths = [a["path"] for a in pauta.get("assets", [])]
    asset_meta = list(pauta.get("assets", []))
    si = 0
    for slot in slots:
        slot["pauta_id"] = pauta["pauta_id"]
        slot["asset_paths"] = asset_paths
        slot["asset_meta"] = asset_meta
        slot["source_video_id"] = pauta["source"]["video_id"]
        slot["render_ready"] = False
        slot["render_attempts"] = 0
        if slot["video_format"] == "LONG_16_9":
            slot["title"] = pkg["long"]["title"]
            slot["script_hook"] = pkg["long"].get("hook", "")
            slot["hook"] = pkg["long"].get("hook", "")
            slot["narration_text"] = pkg["long"]["narration_text"]
            slot["angle_name"] = "Documentário Longo 16:9"
            if pkg["long"].get("thumb_headline"):
                slot["thumb_headline"] = pkg["long"]["thumb_headline"]
            if pkg.get("tags"):
                slot["tags"] = pkg.get("tags")
        elif si < len(shorts):
            s = shorts[si]
            slot["title"] = s["title"] if "#Shorts" in s["title"] else f"{s['title']} #Shorts"
            slot["script_hook"] = s.get("hook", "")
            slot["narration_text"] = s["narration_text"]
            slot["angle_name"] = s.get("angle_name", f"Short {si + 1}")
            if s.get("thumb_headline"):
                slot["thumb_headline"] = s["thumb_headline"]
            si += 1
        slot["status"] = "ready_for_dispatch"
    return slots
