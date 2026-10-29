"""
YouTube Channel Cleaner & Duplicate Purge Tool - Dark Studio AI Platform
Permite auditar e deletar com segurança vídeos duplicados, floodados ou com 0 views
via YouTube Data API v3.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("youtube_cleaner")

BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
CREDENTIALS_DIR = BASE_DIR / "workspace/credentials"

# Lista de vídeos defeituosos identificados na auditoria forense do Canal #2 (Finanças Quânticas)
DEFECTIVE_VIDEOS_CH2 = [
    # Lote 1: Clones duplicados postados em rajada hoje (01:54 a 01:59 UTC)
    {
        "id": "38NgiCis_BU",
        "title": "LTCM: Quando 2 Prêmios Nobel Quebraram Wall Street",
        "reason": "Clone duplicado de PWwcOwApqJ8 (postado em intervalo de 1 min - flood anti-spam)",
        "views": 0
    },
    {
        "id": "rtPrI7STnMM",
        "title": "ALAVANCAGEM 100:1: O Erro Fatal que Quase Explodiu",
        "reason": "Clone duplicado de mXxRjiF4pXE (postado em intervalo de 1 min - flood anti-spam)",
        "views": 0
    },
    {
        "id": "sD-J7TxS16E",
        "title": "A REUNIÃO SECRETA: O Resgate de US$ 3.6 Bilhões no",
        "reason": "Clone duplicado de wDrNsJWWsC8 (postado em intervalo de 1 min - flood anti-spam)",
        "views": 0
    },
    {
        "id": "Dy8g0sk0jTc",
        "title": "ED THORP: O Homem que Derrotou a Roleta e Wall Str",
        "reason": "Clone duplicado de -LBH--tjd9w (postado em intervalo de 1 min - flood anti-spam)",
        "views": 0
    },
    # Lote 2: Vídeos de 17/10 que subiram simultaneamente no mesmo minuto (23:06 UTC)
    {
        "id": "9v2QOf36bQI",
        "title": "GUERRA DOS MICROSSEGUNDOS: Gastaram US$ 300 Milhões",
        "reason": "Subiu no exato minuto 23:06 com outros 2 vídeos; estagnado em 0 views há mais de 30 horas",
        "views": 0
    },
    {
        "id": "MmF40JljOqI",
        "title": "CADEIAS DE MARKOV: A Equação que Previu o Pânico",
        "reason": "Subiu no exato minuto 23:06 com outros 2 vídeos; estagnado em 0 views há mais de 30 horas",
        "views": 0
    },
    {
        "id": "unZRHWYNDu4",
        "title": "KNIGHT CAPITAL: O Bug de US$ 440 Milhões que Quebr",
        "reason": "Subiu no exato minuto 23:06 com outros 2 vídeos; estagnado em 1 view há mais de 30 horas",
        "views": 1
    }
]


def purge_defective_videos(channel_id: str, video_list: List[Dict[str, Any]], dry_run: bool = True) -> List[str]:
    """Deleta os vídeos defeituosos via API do YouTube ou simula a exclusão."""
    tok = CREDENTIALS_DIR / f"{channel_id}_token.json"
    if not tok.exists():
        logger.error("Token não encontrado para canal %s", channel_id)
        return []

    creds = Credentials.from_authorized_user_file(str(tok))
    yt = build("youtube", "v3", credentials=creds)

    deleted_ids = []
    for item in video_list:
        vid = item["id"]
        title = item["title"]
        reason = item["reason"]

        if dry_run:
            logger.info("[DRY-RUN] Vídeo sinalizado para exclusão: %s | '%s' | Motivo: %s", vid, title, reason)
            deleted_ids.append(vid)
        else:
            try:
                logger.info("Deletando vídeo %s ('%s')...", vid, title)
                yt.videos().delete(id=vid).execute()
                logger.info("SUCESSO: Vídeo %s excluído permanentemente do YouTube.", vid)
                deleted_ids.append(vid)
            except Exception as e:
                logger.error("Falha ao deletar vídeo %s: %s", vid, e)

    return deleted_ids


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Cleaner")
    parser.add_argument("--execute", action="store_true", help="Executa a exclusão real (sem flag roda em dry-run)")
    parser.add_argument("--channel", default="UCE6Ch6nhxI81Z6ILQIw23_Q", help="Channel ID")
    args = parser.parse_args()

    is_dry = not args.execute
    mode_str = "MODO SIMULAÇÃO (DRY-RUN)" if is_dry else "MODO REAL DE EXCLUSÃO"
    print(f"=== YOUTUBE VIDEO PURGE TOOL ({mode_str}) ===")
    res = purge_defective_videos(args.channel, DEFECTIVE_VIDEOS_CH2, dry_run=is_dry)
    print(f"Total de vídeos processados: {len(res)}")
