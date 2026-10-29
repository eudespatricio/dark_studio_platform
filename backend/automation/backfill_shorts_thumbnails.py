"""
Backfill de Miniaturas Profissionais 9:16 (720x1280) para todos os YouTube Shorts ativos.
Usa fotos reais de arquivo com padrão Cinema Pro 2.0 e envia via YouTube Data API v3.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
sys.path.insert(0, str(BASE_DIR))

from google.oauth2.credentials import Credentials  # type: ignore
from google.auth.transport.requests import Request  # type: ignore
from googleapiclient.discovery import build  # type: ignore
from googleapiclient.http import MediaFileUpload  # type: ignore

from backend.media.thumbnail_maker import ThumbnailMaker
from backend.publisher.youtube_uploader import YouTubeMultiChannelUploader

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("backfill_shorts_thumbnails")

CH1_ID = "UC8RJWr3b2pKtnU1wOhV_bDQ"  # A Via da Descoberta
CH2_ID = "UCE6Ch6nhxI81Z6ILQIw23_Q"  # Finanças Quânticas

# Configuração de Thumbnails de Alto CTR para Shorts
SHORTS_SPECS = [
    # CHANNEL 1: A Via da Descoberta
    {
        "channel_id": CH1_ID,
        "video_id": "2fnYVfSW98s",
        "title": "O PÉ DE ELEFANTE: A Massa Mais Perigosa do Planeta Terra",
        "badge": "RADIAÇÃO FATAL",
        "headline": "O PÉ DE ELEFANTE",
        "accent_color": (0, 245, 212),
        "bg_path": BASE_DIR / "workspace/thumbnails/raw_sources/kola_borehole_real.jpg",
    },
    {
        "channel_id": CH1_ID,
        "video_id": "-eajFdOyVf8",
        "title": "A CIDADE FANTASMA: 48 Horas para Evacuar Pripyat",
        "badge": "ZONA PROIBIDA",
        "headline": "CIDADE FANTASMA",
        "accent_color": (250, 204, 21),
        "bg_path": BASE_DIR / "workspace/thumbnails/raw_sources/kola_borehole_real.jpg",
    },
    {
        "channel_id": CH1_ID,
        "video_id": "KGDqQkuxsDw",
        "title": "A PÁ DE DOIS MINUTOS: Os Biorrobôs no Teto de Chernobyl",
        "badge": "MISSÃO SUICIDA",
        "headline": "OS BIORROBÔS",
        "accent_color": (0, 245, 212),
        "bg_path": BASE_DIR / "workspace/thumbnails/raw_sources/kola_borehole_real.jpg",
    },
    {
        "channel_id": CH1_ID,
        "video_id": "sDzxoTvc79I",
        "title": "O GRAFITE SECRETO: A Falha Oculta da Engenharia Soviética",
        "badge": "FALHA SECRETA",
        "headline": "GRAFITE MORTAL",
        "accent_color": (250, 204, 21),
        "bg_path": BASE_DIR / "workspace/thumbnails/raw_sources/kola_borehole_real.jpg",
    },
    {
        "channel_id": CH1_ID,
        "video_id": "qu2EWQmdxX8",
        "title": "CHERNOBYL: O Botão AZ-5 que Desencadeou a Explosão",
        "badge": "ERRO DE PROJETO",
        "headline": "BOTÃO AZ-5",
        "accent_color": (0, 245, 212),
        "bg_path": BASE_DIR / "workspace/thumbnails/raw_sources/kola_borehole_real.jpg",
    },
    {
        "channel_id": CH1_ID,
        "video_id": "7DS42MTuYB0",
        "title": "KOLA SG-3: Por Que a URSS Lacrou o Poço com 12 Parafusos?",
        "badge": "SEGREDOS DA URSS",
        "headline": "POÇO LACRADO",
        "accent_color": (0, 245, 212),
        "bg_path": BASE_DIR / "workspace/thumbnails/raw_sources/kola_borehole_real.jpg",
    },
    {
        "channel_id": CH1_ID,
        "video_id": "v5RC2xaWA3M",
        "title": "ANOMALIA A 12.000 METROS: A Água Fervente Proibida pela Física",
        "badge": "ANOMALIA REAL",
        "headline": "12.000 METROS",
        "accent_color": (250, 204, 21),
        "bg_path": BASE_DIR / "workspace/thumbnails/raw_sources/kola_borehole_real.jpg",
    },
    {
        "channel_id": CH1_ID,
        "video_id": "WdAdL_DVpCQ",
        "title": "12.262 METROS: O Buraco Mais Profundo Já Feito pelo Homem",
        "badge": "RECORDE MUNDIAL",
        "headline": "BURACO PROIBIDO",
        "accent_color": (0, 245, 212),
        "bg_path": BASE_DIR / "workspace/thumbnails/raw_sources/kola_borehole_real.jpg",
    },

    # CHANNEL 2: Finanças Quânticas
    {
        "channel_id": CH2_ID,
        "video_id": "xJqON6F8Zss",
        "title": "LTCM: A Equação que Quebrou Wall Street em 1998",
        "badge": "ALERTA CRÍTICO",
        "headline": "O BUG DE 440 MILHÕES",
        "accent_color": (250, 204, 21),
        "bg_path": BASE_DIR / "workspace/scenes/flash_crash/real_photo_01_nyse_floor.jpg",
    },
    {
        "channel_id": CH2_ID,
        "video_id": "6WnDvzK9TD4",
        "title": "A FÓRMULA DE KELLY: O critério matemático que quebrou cassinos e fundos",
        "badge": "FÓRMULA SECRETA",
        "headline": "CRITÉRIO DE KELLY",
        "accent_color": (16, 185, 129),
        "bg_path": BASE_DIR / "workspace/scenes/quant/chart_04_kelly_criterion.png",
    },
    {
        "channel_id": CH2_ID,
        "video_id": "5rVp_Gchz4k",
        "title": "FLASH CRASH: Como um Algoritmo Apagou US$ 1 Trilhão em 36 Minutos",
        "badge": "COLAPSO HFT",
        "headline": "FLASH CRASH",
        "accent_color": (250, 204, 21),
        "bg_path": BASE_DIR / "workspace/scenes/flash_crash/real_photo_01_nyse_floor.jpg",
    },
    {
        "channel_id": CH2_ID,
        "video_id": "Vb-MMJJXuMc",
        "title": "JIM SIMONS: O Matemático que Decifrou Wall Street",
        "badge": "ALGORITMO OCULTO",
        "headline": "JIM SIMONS",
        "accent_color": (16, 185, 129),
        "bg_path": BASE_DIR / "workspace/scenes/quant/simons_2007.jpg",
    },
]


def build_authenticated_service(channel_id: str):
    uploader = YouTubeMultiChannelUploader()
    tp = uploader._has_valid_oauth_token(channel_id)
    if not tp or not tp.exists():
        raise RuntimeError(f"Token OAuth não encontrado para o canal {channel_id}")
    creds = Credentials.from_authorized_user_file(str(tp))
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        tp.write_text(creds.to_json(), encoding="utf-8")
    return build("youtube", "v3", credentials=creds)


def main():
    tm = ThumbnailMaker()
    services = {
        CH1_ID: build_authenticated_service(CH1_ID),
        CH2_ID: build_authenticated_service(CH2_ID),
    }

    success_count = 0
    total = len(SHORTS_SPECS)

    for idx, spec in enumerate(SHORTS_SPECS, 1):
        vid = spec["video_id"]
        ch_id = spec["channel_id"]
        logger.info("[%d/%d] Processando miniatura 9:16 para Short: %s (%s)", idx, total, vid, spec["title"])

        # 1. Gera a miniatura vertical 9:16 (720x1280)
        artifact = tm.create_thumbnail(
            headline_text=spec["headline"],
            badge_text=spec["badge"],
            job_id=f"backfill_{vid}",
            background_image_path=spec["bg_path"] if spec["bg_path"].exists() else None,
            accent_color_rgb=spec["accent_color"],
            topic_context=spec["title"],
            aspect_ratio="9:16",
        )
        thumb_path = artifact.output_jpg_path
        logger.info("  Miniatura gerada: %s (%d bytes)", thumb_path, artifact.file_size_bytes)

        # 2. Upload da miniatura para o YouTube via Data API
        try:
            yt = services[ch_id]
            req = yt.thumbnails().set(
                videoId=vid,
                media_body=MediaFileUpload(thumb_path, mimetype="image/jpeg"),
            )
            res = req.execute()
            logger.info("  Miniatura enviada com sucesso ao YouTube para %s! Itens retornados: %s", vid, list(res.get("items", [{}])[0].keys()))
            success_count += 1
        except Exception as err:
            logger.error("  Erro ao enviar miniatura para %s: %s", vid, err)

    logger.info("=== BACKFILL CONCLUÍDO: %d de %d miniaturas atualizadas com sucesso ===", success_count, total)


if __name__ == "__main__":
    main()
