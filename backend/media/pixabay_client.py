"""
Pixabay Media Client for Dark Studio Platform (`backend/media/pixabay_client.py`).
Provides automated retrieval and streaming downloads of HD stock video clips (.mp4)
and high-resolution photography (.jpg) for rich cinematic documentary B-roll.
"""

from __future__ import annotations

import hashlib
import logging
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

logger = logging.getLogger("dark_studio.pixabay_client")

BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
DEFAULT_PIXABAY_DIR = BASE_DIR / "workspace/scenes/pixabay"


BANNED_TAGS = {
    "suscribe", "suscribete", "suscríbete", "subscribe", "subscribir", "intro", "outro",
    "like", "share", "channel", "canal", "youtube", "pantalla final", "call to action",
    "watermark", "lower third", "template", "animacion de texto", "outro screen",
    "ending", "end screen", "suscripcion", "suscripción", "bell icon", "campanita"
}


class PixabayClient:
    """Cliente para a API do Pixabay com suporte a busca e download de vídeos e imagens HD."""

    PHOTO_API = "https://pixabay.com/api/"
    VIDEO_API = "https://pixabay.com/api/videos/"

    def __init__(self, api_key: Optional[str] = None, target_dir: Optional[Path] = None):
        cfg_key = ""
        try:
            from backend import config
            cfg_key = getattr(config, "PIXABAY_API_KEY", "")
        except Exception:
            pass

        self.api_key = (
            api_key
            or cfg_key
            or os.getenv("PIXABAY_API_KEY")
            or os.getenv("pixabaykey", "")
        ).strip()
        self.target_dir = target_dir or DEFAULT_PIXABAY_DIR
        self.target_dir.mkdir(parents=True, exist_ok=True)

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 15)

    def search_videos(
        self,
        query: str,
        orientation: str = "horizontal",
        limit: int = 5,
        min_width: int = 1280,
    ) -> List[Dict[str, Any]]:
        """Busca vídeos stock MP4 no Pixabay."""
        if not self.is_configured:
            logger.warning("Pixabay API key não configurada.")
            return []

        params = {
            "key": self.api_key,
            "q": query,
            "orientation": orientation,
            "per_page": max(3, min(limit * 2, 25)),
            "safesearch": "true",
        }
        try:
            resp = requests.get(self.VIDEO_API, params=params, timeout=12)
            resp.raise_for_status()
            data = resp.json()
            hits = data.get("hits", [])
            results = []

            for hit in hits:
                if hit.get("isLowQuality"):
                    continue
                tags_str = (hit.get("tags") or "").lower()
                name_str = (hit.get("name") or "").lower()
                if any(b in tags_str or b in name_str for b in BANNED_TAGS):
                    continue

                vids = hit.get("videos", {})
                cand = vids.get("large") or vids.get("medium")
                if not cand or not cand.get("url"):
                    continue
                if cand.get("width", 0) < min_width and vids.get("medium", {}).get("width", 0) < 1280:
                    continue

                results.append({
                    "id": hit.get("id"),
                    "tags": hit.get("tags", ""),
                    "duration": hit.get("duration", 0),
                    "width": cand.get("width", 1920),
                    "height": cand.get("height", 1080),
                    "url": cand.get("url"),
                    "query": query,
                    "kind": "video",
                })
                if len(results) >= limit:
                    break
            return results
        except Exception as exc:
            logger.warning("Erro ao buscar vídeos no Pixabay para '%s': %s", query, exc)
            return []

    def download_video(self, item: Dict[str, Any], target_dir: Optional[Path] = None, prefix: str = "pixabay_vid") -> Optional[Path]:
        """Baixa o arquivo .mp4 para o diretório de cenas."""
        url = item.get("url")
        if not url:
            return None

        dest_dir = target_dir or self.target_dir
        dest_dir.mkdir(parents=True, exist_ok=True)
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:10]
        safe_prefix = re.sub(r"\W+", "_", prefix)[:20]
        dest_file = dest_dir / f"{safe_prefix}_{item.get('id', 'vid')}_{url_hash}.mp4"

        if dest_file.exists() and dest_file.stat().st_size > 50_000:
            return dest_file

        for attempt in range(2):
            try:
                time.sleep(0.25)
                with requests.get(url, stream=True, timeout=30) as resp:
                    if resp.status_code == 429:
                        time.sleep(1.5)
                        continue
                    resp.raise_for_status()
                    with open(dest_file, "wb") as f:
                        for chunk in resp.iter_content(chunk_size=65536):
                            f.write(chunk)
                if dest_file.stat().st_size > 50_000:
                    logger.info("Vídeo Pixabay baixado: %s (%.1f MB)", dest_file.name, dest_file.stat().st_size / (1024 * 1024))
                    return dest_file
                dest_file.unlink(missing_ok=True)
                return None
            except Exception as exc:
                if attempt == 0:
                    time.sleep(1.0)
                    continue
                logger.warning("Falha ao baixar vídeo Pixabay de %s: %s", url, exc)
                dest_file.unlink(missing_ok=True)
                return None
        return None

    def search_photos(
        self,
        query: str,
        orientation: str = "horizontal",
        limit: int = 5,
        min_width: int = 1280,
    ) -> List[Dict[str, Any]]:
        """Busca fotografias HD no Pixabay."""
        if not self.is_configured:
            return []

        params = {
            "key": self.api_key,
            "q": query,
            "image_type": "photo",
            "orientation": orientation,
            "per_page": max(3, min(limit, 20)),
            "safesearch": "true",
        }
        try:
            resp = requests.get(self.PHOTO_API, params=params, timeout=12)
            resp.raise_for_status()
            data = resp.json()
            hits = data.get("hits", [])
            results = []

            for hit in hits:
                if hit.get("isLowQuality"):
                    continue
                tags_str = (hit.get("tags") or "").lower()
                name_str = (hit.get("name") or "").lower()
                if any(b in tags_str or b in name_str for b in BANNED_TAGS):
                    continue

                img_url = hit.get("largeImageURL") or hit.get("fullHDURL") or hit.get("webformatURL")
                if not img_url:
                    continue
                w = hit.get("imageWidth", 0)
                if w < min_width and hit.get("webformatWidth", 0) < 900:
                    continue

                results.append({
                    "id": hit.get("id"),
                    "tags": hit.get("tags", ""),
                    "width": hit.get("imageWidth", 1920),
                    "height": hit.get("imageHeight", 1080),
                    "url": img_url,
                    "query": query,
                    "kind": "image",
                })
                if len(results) >= limit:
                    break
            return results
        except Exception as exc:
            logger.warning("Erro ao buscar fotos no Pixabay para '%s': %s", query, exc)
            return []

    def download_photo(self, item: Dict[str, Any], target_dir: Optional[Path] = None, prefix: str = "pixabay_img") -> Optional[Path]:
        """Baixa foto HD do Pixabay."""
        url = item.get("url")
        if not url:
            return None

        dest_dir = target_dir or self.target_dir
        dest_dir.mkdir(parents=True, exist_ok=True)
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:10]
        safe_prefix = re.sub(r"\W+", "_", prefix)[:20]
        dest_file = dest_dir / f"{safe_prefix}_{item.get('id', 'img')}_{url_hash}.jpg"

        if dest_file.exists() and dest_file.stat().st_size > 20_000:
            return dest_file

        for attempt in range(2):
            try:
                time.sleep(0.20)
                with requests.get(url, stream=True, timeout=20) as resp:
                    if resp.status_code == 429:
                        time.sleep(1.5)
                        continue
                    resp.raise_for_status()
                    with open(dest_file, "wb") as f:
                        for chunk in resp.iter_content(chunk_size=65536):
                            f.write(chunk)
                if dest_file.stat().st_size > 20_000:
                    logger.info("Foto Pixabay baixada: %s (%.1f KB)", dest_file.name, dest_file.stat().st_size / 1024)
                    return dest_file
                dest_file.unlink(missing_ok=True)
                return None
            except Exception as exc:
                if attempt == 0:
                    time.sleep(1.0)
                    continue
                logger.warning("Falha ao baixar foto Pixabay de %s: %s", url, exc)
                dest_file.unlink(missing_ok=True)
                return None
        return None

    def fetch_broll_batch(
        self,
        queries: List[str],
        target_dir: Optional[Path] = None,
        max_videos: int = 15,
        max_photos: int = 15,
        orientation: str = "horizontal",
    ) -> List[Tuple[str, Path]]:
        """
        Executa busca em lote para as queries informadas, baixando vídeos e imagens HD.
        Retorna lista de tuplas ('video', Path) e ('image', Path).
        """
        assets: List[Tuple[str, Path]] = []
        dest_dir = target_dir or self.target_dir

        # 1. Baixar vídeos primeiro (maior valor de retenção)
        vids_got = 0
        for q in queries:
            if vids_got >= max_videos:
                break
            items = self.search_videos(q, orientation=orientation, limit=2)
            for it in items:
                p = self.download_video(it, target_dir=dest_dir, prefix=f"vid_{q[:12]}")
                if p:
                    assets.append(("video", p))
                    vids_got += 1
                if vids_got >= max_videos:
                    break

        # 2. Baixar fotos
        photos_got = 0
        for q in queries:
            if photos_got >= max_photos:
                break
            items = self.search_photos(q, orientation=orientation, limit=3)
            for it in items:
                p = self.download_photo(it, target_dir=dest_dir, prefix=f"img_{q[:12]}")
                if p:
                    assets.append(("image", p))
                    photos_got += 1
                if photos_got >= max_photos:
                    break

        logger.info(
            "Pixabay Batch finalizado para %d queries -> %d vídeos e %d fotos obtidos",
            len(queries), vids_got, photos_got
        )
        return assets
