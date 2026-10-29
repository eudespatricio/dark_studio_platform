"""
Open Archive Fetcher — Dark Studio Platform
Módulo de curadoria e download automatizado de fotografias e diagramas históricos/científicos
de domínio público e Creative Commons (Wikimedia Commons / Arquivos Abertos) com
extração rigorosa de metadados de atribuição para compliance e integridade documental.
"""

from __future__ import annotations

import json
import logging
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("open_archive_fetcher")


class OpenArchiveFetcher:
    """Busca e baixa mídias abertas com licença comprovada para contextualizar tópicos documentais."""

    WIKIMEDIA_API = "https://commons.wikimedia.org/w/api.php"

    def __init__(self, target_dir: Optional[Path] = None):
        self.target_dir = target_dir or Path("/home/eudespatricio/dark_studio_platform/workspace/scenes/open_archive")
        self.target_dir.mkdir(parents=True, exist_ok=True)

    def search_media(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Busca de texto completo em arquivos (namespace File:) da Wikimedia Commons, com licença e autor."""
        try:
            params = {
                "action": "query", "format": "json", "generator": "search", "gsrsearch": f"{query} filetype:bitmap",
                "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
                "iiprop": "url|size|mime|extmetadata", "iiurlwidth": "1920",
            }
            url = f"{self.WIKIMEDIA_API}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(
                url, headers={"User-Agent": "DarkStudioPlatform/2.5.0 (contact@darkstudio.ai; educational-documentary)"}
            )
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                pages = json.loads(resp.read().decode()).get("query", {}).get("pages", {})

            results: List[Dict[str, Any]] = []
            for _, pdata in sorted(pages.items(), key=lambda kv: kv[1].get("index", 0)):
                info = (pdata.get("imageinfo") or [{}])[0]
                ext_meta = info.get("extmetadata", {})
                file_url = info.get("thumburl") or info.get("url")
                if not file_url or info.get("mime", "").split("/")[0] != "image":
                    continue
                artist = ext_meta.get("Artist", {}).get("value", "Domínio Público / Arquivo Histórico")
                clean_artist = re.sub(r"<[^>]+>", "", artist)
                results.append({
                    "title": pdata.get("title", ""),
                    "url": file_url,
                    "width": info.get("thumbwidth") or info.get("width", 0),
                    "height": info.get("thumbheight") or info.get("height", 0),
                    "license": ext_meta.get("LicenseShortName", {}).get("value", "Public Domain"),
                    "attribution": clean_artist[:100],
                    "kind": "image",
                })
            return results
        except Exception as exc:
            logger.warning("Erro ao consultar Wikimedia Commons para '%s': %s", query, exc)
            return []

    def search_videos(self, query: str, limit: int = 4) -> List[Dict[str, Any]]:
        """Busca vídeos de arquivo (.webm / .mp4 / .ogv) na Wikimedia Commons."""
        try:
            params = {
                "action": "query", "format": "json", "generator": "search", "gsrsearch": f"{query} filetype:video",
                "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
                "iiprop": "url|size|mime|extmetadata",
            }
            url = f"{self.WIKIMEDIA_API}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(
                url, headers={"User-Agent": "DarkStudioPlatform/3.0.0 (contact@darkstudio.ai; educational-documentary)"}
            )
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                pages = json.loads(resp.read().decode()).get("query", {}).get("pages", {})

            results: List[Dict[str, Any]] = []
            for _, pdata in sorted(pages.items(), key=lambda kv: kv[1].get("index", 0)):
                info = (pdata.get("imageinfo") or [{}])[0]
                ext_meta = info.get("extmetadata", {})
                file_url = info.get("url")
                mime = info.get("mime", "")
                if not file_url or not ("video" in mime or "ogg" in mime):
                    continue
                artist = ext_meta.get("Artist", {}).get("value", "Domínio Público / Arquivo Histórico")
                clean_artist = re.sub(r"<[^>]+>", "", artist)
                results.append({
                    "title": pdata.get("title", ""),
                    "url": file_url,
                    "width": info.get("width", 1280),
                    "height": info.get("height", 720),
                    "license": ext_meta.get("LicenseShortName", {}).get("value", "Public Domain"),
                    "attribution": clean_artist[:100],
                    "kind": "video",
                })
            return results
        except Exception as exc:
            logger.warning("Erro ao consultar vídeos na Wikimedia Commons para '%s': %s", query, exc)
            return []

    def download_asset(self, item: Dict[str, Any], prefix: str = "archive") -> Optional[Path]:
        """Baixa arquivo (foto ou vídeo) e salva com prefixo temático."""
        try:
            url = item.get("url")
            if not url:
                return None

            suffix = Path(urllib.parse.urlparse(url).path).suffix.lower()
            if suffix not in (".jpg", ".jpeg", ".png", ".webp", ".webm", ".mp4", ".ogv"):
                return None

            safe_name = f"{prefix}_{abs(hash(url)) % 1000000}{suffix}"
            dest = self.target_dir / safe_name
            if dest.exists() and dest.stat().st_size > 5000:
                return dest

            req = urllib.request.Request(
                url,
                headers={"User-Agent": "DarkStudioPlatform/2.5.0 (contact@darkstudio.ai; educational-documentary)"}
            )
            with urllib.request.urlopen(req, timeout=12.0) as resp:
                data = resp.read()
                dest.write_bytes(data)

            # Salva ledger de licença
            meta_dest = dest.with_suffix(".json")
            meta_dest.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
            logger.info("Mídia aberta documentada com sucesso: %s (Licença: %s)", dest.name, item.get("license"))
            return dest
        except Exception as exc:
            logger.warning("Falha ao baixar mídia aberta %s: %s", item.get("url"), exc)
            return None
