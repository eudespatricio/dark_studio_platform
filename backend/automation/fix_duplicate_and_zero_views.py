"""
FIX DUPLICATE & ZERO VIEWS SCRIPT (DARK STUDIO PLATFORM)
1. Respeita o Quota Circuit Breaker (zero chamadas desperdiçadas enquanto a cota não resetar às 04:05 BRT).
2. Altera os vídeos duplicados antigos (Chernobyl, Kola, Vajont, LTCM) para 'unlisted' uma única vez (idempotente).
3. Executa a fila `pending_post_actions.json` (thumbnails e comentários fixados de contexto adiados durante o pico de cota).
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("fix_duplicates")

CREDENTIALS_DIR = BASE_DIR / "workspace/credentials"
DONE_STATE_FILE = BASE_DIR / "workspace/automation/unlisted_duplicates_done.json"
CH1_ID = "UC8RJWr3b2pKtnU1wOhV_bDQ"
CH2_ID = "UCE6Ch6nhxI81Z6ILQIw23_Q"

# Vídeos antigos que subiram com o vídeo binário duplicado de 547 MB do Lago Peigneur
DUPLICATE_VIDEOS = {
    CH1_ID: [
        {"id": "qM_OTfIzoAE", "title": "O Erro de Projeto que Destruiu Chernobyl: O Segredo do Reator 4"},
        {"id": "UvXx5NPM6I0", "title": "O Poço Proibido de 12.262 Metros: O Que a URSS Escondeu em Kola"},
        {"id": "nGbH-hY8B2o", "title": "O Tsunami de 250 Metros que Engoliu 2.000 Vidas: O Desastre de Vajont"},
    ],
    CH2_ID: [
        {"id": "XLfPuc_glNU", "title": "O Colapso do LTCM (1998): Quando Prêmios Nobel Quebraram Wall Street"},
    ],
}


def _load_done_ids() -> set[str]:
    if not DONE_STATE_FILE.exists():
        return set()
    try:
        data = json.loads(DONE_STATE_FILE.read_text(encoding="utf-8"))
        return set(data.get("unlisted_ids", []))
    except Exception:
        return set()


def _save_done_ids(done_ids: set[str]) -> None:
    DONE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    DONE_STATE_FILE.write_text(
        json.dumps(
            {"updated_at": datetime.now(timezone.utc).isoformat(), "unlisted_ids": sorted(done_ids)},
            indent=2,
        ),
        encoding="utf-8",
    )


def set_videos_to_unlisted(ch_id: str, video_list: list, done_ids: set[str]) -> list:
    """Altera a privacidade dos vídeos duplicados para unlisted de forma idempotente."""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from backend.publisher.cadence_guard_filter import cadence_guard_filter

    pending = [item for item in video_list if item["id"] not in done_ids]
    if not pending:
        return []

    tok_file = CREDENTIALS_DIR / f"{ch_id}_token.json"
    if not tok_file.exists():
        tok_file = CREDENTIALS_DIR / ("channel_1_token.json" if ch_id == CH1_ID else "UCE6Ch6nhxI81Z6ILQIw23_Q_token.json")

    results = []
    try:
        creds = Credentials.from_authorized_user_file(str(tok_file))
        yt = build("youtube", "v3", credentials=creds, cache_discovery=False)

        for item in pending:
            v_id = item["id"]
            logger.info("Alterando vídeo %s ('%s') para UNLISTED...", v_id, item["title"][:40])
            try:
                v_res = yt.videos().list(part="status", id=v_id).execute()
                if not v_res.get("items"):
                    done_ids.add(v_id)
                    continue

                curr_item = v_res["items"][0]
                body = {
                    "id": v_id,
                    "status": {
                        "privacyStatus": "unlisted",
                        "selfDeclaredMadeForKids": curr_item.get("status", {}).get("selfDeclaredMadeForKids", False),
                    },
                }
                up_res = yt.videos().update(part="status", body=body).execute()
                new_status = up_res.get("status", {}).get("privacyStatus")
                logger.info("✅ Vídeo %s alterado com sucesso para status: %s", v_id, new_status)
                done_ids.add(v_id)
                results.append({"id": v_id, "status": "unlisted", "success": True})
            except Exception as err:
                if "quotaExceeded" in str(err):
                    cadence_guard_filter.trip_quota_breaker(str(err))
                    break
                logger.error("❌ Falha ao alterar vídeo %s: %s", v_id, err)
                results.append({"id": v_id, "error": str(err), "success": False})

    except Exception as exc:
        logger.error("Erro geral na conexão do canal %s: %s", ch_id, exc)

    return results


def run():
    from backend.publisher.cadence_guard_filter import cadence_guard_filter

    if cadence_guard_filter.is_quota_tripped():
        logger.debug("Quota Circuit Breaker ativo — aguardando reset das 04:05 BRT.")
        return

    done_ids = _load_done_ids()
    all_target_ids = {item["id"] for vlist in DUPLICATE_VIDEOS.values() for item in vlist}

    if not all_target_ids.issubset(done_ids):
        logger.info(">>> EXECUTANDO HIGIENIZAÇÃO DE VÍDEOS DUPLICADOS PARA UNLISTED...")
        set_videos_to_unlisted(CH1_ID, DUPLICATE_VIDEOS[CH1_ID], done_ids)
        if not cadence_guard_filter.is_quota_tripped():
            set_videos_to_unlisted(CH2_ID, DUPLICATE_VIDEOS[CH2_ID], done_ids)
        _save_done_ids(done_ids)

    if not cadence_guard_filter.is_quota_tripped():
        executed = cadence_guard_filter.process_pending_post_actions()
        if executed:
            logger.info("✅ %d ações pós-upload pendentes (thumbnails/comentários) concluídas!", executed)


if __name__ == "__main__":
    run()
