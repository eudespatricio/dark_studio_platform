"""
Music Bridge Adapter — Dark Studio Platform <-> Music_Band Engine
Provides decoupled zero-friction integration for Slot #4 (Ain't No Human).
All musical generation, validation and scheduling stay inside Music_Band.
Dark Studio acts strictly as Distributor/Publisher (OAuth2, YouTube API & Metrics).
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

MUSIC_BAND_DIR = Path("/home/eudespatricio/Music_Band").resolve()
MUSIC_RELEASES_DIR = MUSIC_BAND_DIR / "releases"
MUSIC_CATALOG_FILE = MUSIC_RELEASES_DIR / "release_catalog.json"

MUSIC_CHANNEL_ID = "UCbO67ez7TKOJ8C_kpUF4t5Q"
MUSIC_CHANNEL_HANDLE = "@aintnohumanoficial"

class MusicBridge:
    """Decoupled bridge between Dark Studio Platform and Music_Band releases."""

    COPYRIGHT_MARKER = "© "

    @staticmethod
    def build_copyright_block(title: str) -> str:
        """Bloco de direitos autorais: obra própria gerada com Suno (assinatura Pro), com divulgação honesta de IA."""
        year = datetime.now(timezone.utc).year
        return (
            f"© {year} Eudes Patricio (Ain't No Human). Todos os direitos reservados.\n"
            f"Obra original: \"{title}\" — composição, direção criativa, curadoria, edição e masterização "
            "por Eudes Patricio. Vocais e instrumentação gerados com inteligência artificial (Suno, plano Pro); "
            "os direitos comerciais das faixas pertencem a Eudes Patricio, titular do canal, conforme os termos da assinatura Suno Pro.\n"
            "Esta música é conteúdo sintético declarado. Não é permitido reuploadar, remixar para monetização "
            "ou usar em Content ID sem autorização. Propriedade intelectual de Eudes Patricio. Licenciamento: contato pelo próprio canal."
        )

    @classmethod
    def with_copyright(cls, description: str, title: str) -> str:
        if cls.COPYRIGHT_MARKER + str(datetime.now(timezone.utc).year) in (description or "") or "Todos os direitos reservados" in (description or ""):
            return description
        return f"{(description or '').rstrip()}\n\n{cls.build_copyright_block(title)}"

    def sync_catalog(self) -> bool:
        """Regenera o release_catalog.json do Music_Band (fonte única: manifestos) via CLI oficial dele."""
        import subprocess, sys
        cli = MUSIC_BAND_DIR / "pipeline" / "release_cli.py"
        try:
            r = subprocess.run([sys.executable, str(cli), "sync"], capture_output=True, text=True, timeout=60, cwd=str(MUSIC_BAND_DIR))
            return r.returncode == 0
        except Exception as exc:  # noqa: BLE001
            logger.warning("Falha ao sincronizar catálogo Music_Band: %s", exc)
            return False

    def reconcile_published(self) -> Dict[str, Any]:
        """Pós-estreia: marca PUBLISHED no manifesto quando o vídeo ficou público e posta o comentário de abertura (1x)."""
        from backend.publisher.cadence_guard_filter import cadence_guard_filter
        done = {"published": [], "commented": [], "errors": []}
        if cadence_guard_filter.is_quota_tripped():
            return done
        for rel in self.list_releases():
            vid = rel.get("youtube_published_video_id")
            if not vid or rel.get("status") == "PUBLISHED" and rel.get("pinned_comment_posted") is True:
                continue
            try:
                yt = cadence_guard_filter._get_youtube_service(MUSIC_CHANNEL_ID)
                items = yt.videos().list(part="status", id=vid).execute().get("items", [])
                if not items or items[0]["status"]["privacyStatus"] != "public":
                    continue
                mp = Path(rel["manifest_path"])
                data = json.loads(mp.read_text(encoding="utf-8"))
                if data.get("status") != "PUBLISHED":
                    data["status"] = "PUBLISHED"
                    done["published"].append(rel["release_id"])
                if data.get("pinned_comment") and data.get("pinned_comment_posted") is not True:
                    yt.commentThreads().insert(part="snippet", body={"snippet": {"videoId": vid, "topLevelComment": {"snippet": {"textOriginal": data["pinned_comment"]}}}}).execute()
                    data["pinned_comment_posted"] = True
                    done["commented"].append(rel["release_id"])
                mp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            except Exception as exc:  # noqa: BLE001
                done["errors"].append(f"{rel.get('release_id')}: {str(exc)[:160]}")
        if done["published"] or done["commented"]:
            self.sync_catalog()
        return done

    def publish_pending_shorts(self, release_id: Optional[str] = None) -> Dict[str, Any]:
        """Envia os Shorts entregues pelo Music_Band (manifest["shorts"]) após o Long ter ID real no YouTube.
        Respeita o cooldown de 90min do Dark: se bloqueado, tenta de novo no próximo ciclo (sem alterar estado)."""
        from backend.publisher.cadence_guard_filter import cadence_guard_filter
        if cadence_guard_filter.is_quota_tripped():
            logger.debug("⚡ [QUOTA CIRCUIT BREAKER] Cota do YouTube esgotada. Music_Band adia envio de Shorts.")
            return {"uploaded": [], "deferred": ["quota_tripped"], "errors": []}

        from backend.publisher.youtube_uploader import YouTubeMultiChannelUploader, UploadMetadata
        out: Dict[str, Any] = {"uploaded": [], "deferred": [], "errors": []}
        uploader = YouTubeMultiChannelUploader()
        for rel in self.list_releases():
            if release_id and rel.get("release_id") != release_id:
                continue
            long_id = rel.get("youtube_published_video_id")
            shorts = rel.get("shorts") or []
            if not long_id or not shorts:
                continue
            mp = Path(rel["manifest_path"])
            data = json.loads(mp.read_text(encoding="utf-8"))
            changed = False
            for sh in data.get("shorts", []):
                if sh.get("youtube_video_id") or not sh.get("video_file") or not Path(sh["video_file"]).exists():
                    continue
                meta = UploadMetadata(
                    channel_id=MUSIC_CHANNEL_ID, niche_id="cyber_rnb_night_drive",
                    title=sh.get("title", rel.get("title", ""))[:95],
                    description=self.with_copyright(sh.get("description", ""), rel.get("title", "")),
                    tags=sh.get("tags", rel.get("tags", [])), video_format="SHORT_9_16",
                    category_id=str(rel.get("category_id", "10")), default_language="pt-BR",
                    privacy_status=sh.get("privacy_status", "public"),
                    publish_at_iso=sh.get("scheduled_publish_time"), contains_synthetic_media=True,
                    related_long_video_id=long_id, thumbnail_path=sh.get("thumbnail_file"),
                )
                try:
                    rc = uploader.upload_video(sh["video_file"], meta)
                except Exception as exc:  # noqa: BLE001
                    out["errors"].append(f"{sh.get('short_id')}: {exc}")
                    continue
                if not rc.youtube_video_id or rc.state.value == "FAILED":
                    out["errors"].append(f"{sh.get('short_id')}: {rc.error_or_warning}")
                elif rc.state.value == "BLOCKED":
                    out["deferred"].append(f"{sh.get('short_id')}: {rc.error_or_warning}")
                else:
                    sh["youtube_video_id"] = rc.youtube_video_id
                    sh["upload_state"] = rc.state.value
                    sh["watch_url"] = rc.watch_url
                    out["uploaded"].append(sh.get("short_id"))
                    changed = True
                break  # 1 Short por ciclo (cooldown de 90min por canal)
            if changed:
                mp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        if out["uploaded"]:
            self.sync_catalog()
        return out

    def refresh_remote_description(self, release_id: str) -> Dict[str, Any]:
        """Atualiza a descrição de um release já enviado (videos.update) com o bloco de copyright."""
        rel = self.get_release(release_id)
        vid = (rel or {}).get("youtube_published_video_id")
        if not vid:
            return {"success": False, "error": "Release sem youtube_published_video_id."}
        from backend.publisher.cadence_guard_filter import cadence_guard_filter
        yt = cadence_guard_filter._get_youtube_service(MUSIC_CHANNEL_ID)
        item = yt.videos().list(part="snippet", id=vid).execute()["items"][0]
        sn = item["snippet"]
        sn["description"] = self.with_copyright(rel.get("description", ""), rel.get("title", ""))
        yt.videos().update(part="snippet", body={"id": vid, "snippet": sn}).execute()
        return {"success": True, "video_id": vid}

    def __init__(self, releases_dir: Optional[Path] = None):
        if releases_dir:
            self.releases_dir = releases_dir
        else:
            local_ws = Path(__file__).resolve().parent.parent.parent / "workspace" / "music_releases"
            if local_ws.exists():
                self.releases_dir = local_ws
            else:
                self.releases_dir = MUSIC_RELEASES_DIR
        self.catalog_file = self.releases_dir / "release_catalog.json"

    def list_releases(self) -> List[Dict[str, Any]]:
        """Scans and returns all releases from Music_Band with their manifest details."""
        releases: List[Dict[str, Any]] = []

        if not self.releases_dir.exists():
            return releases

        try:
            # Scan all directories in releases/
            for p in sorted(self.releases_dir.iterdir()):
                if p.is_dir():
                    manifest_file = p / "release_manifest.json"
                    if manifest_file.exists():
                        try:
                            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
                            # Verify file presence
                            vid = manifest.get("video_file")
                            manifest["video_ready"] = bool(vid and Path(vid).exists() and Path(vid).stat().st_size > 1000)
                            thumb = manifest.get("thumbnail_file")
                            manifest["thumbnail_ready"] = bool(thumb and Path(thumb).exists())
                            manifest["manifest_path"] = str(manifest_file)
                            releases.append(manifest)
                        except Exception as e:
                            logger.error(f"Error parsing manifest {manifest_file}: {e}")
        except Exception as dir_err:
            logger.warning(f"Error reading releases directory {self.releases_dir}: {dir_err}")

        return releases

    def get_release(self, release_id: str) -> Optional[Dict[str, Any]]:
        """Gets a single release by its release_id."""
        for r in self.list_releases():
            if r.get("release_id") == release_id:
                return r
        return None

    def publish_release(self, release_id: str, force_now: bool = False) -> Dict[str, Any]:
        """
        Publishes or schedules a completed release to YouTube via Dark Studio YouTubeUploader.
        """
        release = self.get_release(release_id)
        if not release:
            return {"success": False, "error": f"Release '{release_id}' não encontrado em Music_Band."}

        video_path = release.get("video_file")
        if not video_path or not Path(video_path).exists():
            return {
                "success": False,
                "error": f"Arquivo de vídeo final não encontrado: {video_path}. Renderize o vídeo primeiro no Music_Band."
            }

        from backend.publisher.youtube_uploader import YouTubeMultiChannelUploader, UploadMetadata

        # Scheduled time (if not force_now)
        scheduled_iso = None if force_now else release.get("scheduled_publish_time")

        metadata = UploadMetadata(
            channel_id=MUSIC_CHANNEL_ID,
            niche_id="cyber_rnb_night_drive",
            title=release.get("title", "Ain't No Human - Cyber-R&B Release"),
            description=self.with_copyright(release.get("description", ""), release.get("title", "")),
            tags=release.get("tags", []),
            video_format="LONG_16_9",
            category_id=str(release.get("category_id", "10")),
            default_language="pt-BR",
            privacy_status=release.get("privacy_status", "public"),
            publish_at_iso=scheduled_iso,
            contains_synthetic_media=True,
            self_declared_made_for_kids=False,
            thumbnail_path=release.get("thumbnail_file")
        )

        uploader = YouTubeMultiChannelUploader()
        try:
            receipt = uploader.upload_video(video_path=video_path, metadata=metadata)

            if not receipt.youtube_video_id or receipt.state.value in ("FAILED", "BLOCKED"):
                return {
                    "success": False,
                    "error": receipt.error_or_warning or "Falha no envio para o YouTube.",
                    "receipt": receipt.to_dict()
                }

            # Update manifest with result
            manifest_path = Path(release["manifest_path"])
            manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest_data["status"] = "SCHEDULED_ON_YOUTUBE" if scheduled_iso else "PUBLISHED"
            manifest_data["youtube_published_video_id"] = receipt.youtube_video_id
            manifest_data["published_at"] = datetime.now(timezone.utc).isoformat()
            manifest_data["upload_receipt"] = receipt.to_dict()
            manifest_path.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False), encoding="utf-8")

            # Comentário de abertura do manifesto (best-effort; vídeo agendado/privado pode recusar comentários)
            pinned = release.get("pinned_comment")
            if pinned:
                try:
                    from backend.publisher.cadence_guard_filter import cadence_guard_filter
                    yt = cadence_guard_filter._get_youtube_service(MUSIC_CHANNEL_ID)
                    yt.commentThreads().insert(part="snippet", body={"snippet": {
                        "videoId": receipt.youtube_video_id,
                        "topLevelComment": {"snippet": {"textOriginal": pinned}}}}).execute()
                    manifest_data["pinned_comment_posted"] = True
                except Exception as c_err:  # noqa: BLE001
                    manifest_data["pinned_comment_posted"] = False
                    logger.warning("Comentário do release não postado (%s): %s", release_id, c_err)
                manifest_path.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False), encoding="utf-8")

            self.sync_catalog()
            return {
                "success": True,
                "receipt": receipt.to_dict(),
                "scheduled": bool(scheduled_iso),
                "scheduled_time": scheduled_iso
            }
        except Exception as exc:
            logger.exception("MusicBridge upload failed: %s", exc)
            return {"success": False, "error": str(exc)}

music_bridge = MusicBridge()
