"""
YouTube Multi-Channel Uploader — Orquestrador de Publicação 16:9 e 9:16 (YouTube Data API v3).

Funcionalidades principais:
1. Gerenciamento isolado de credenciais OAuth2 por canal (Top 3 Canais Dark).
2. Declaração nativa de conteúdo sintético/alterado (`containsSyntheticMedia=True`) em
   conformidade com as diretrizes do YouTube para vozes/visuais gerados com IA.
3. Agendamento Inteligente (Smart Scheduling): agenda o Vídeo Longo (16:9) no horário nobre
   de cada nicho e escalona automaticamente os Shorts (9:16) com linkagem para o vídeo longo
   (`related_video_id`).
"""

from __future__ import annotations

import logging
import os
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from backend.config import AUTO_PUBLISH_ENABLED
from backend.domain.publication_policy import (
    POLICY_VERSION,
    UploadState,
    resolve_format_rules,
)

logger = logging.getLogger(__name__)

VideoFormat = Literal["LONG_16_9", "SHORT_9_16"]


@dataclass
class UploadMetadata:
    """Metadados completos para upload e empacotamento SEO no YouTube."""

    channel_id: str
    niche_id: str
    title: str
    description: str
    tags: List[str]
    video_format: VideoFormat = "LONG_16_9"
    category_id: str = "27"  # 27 = Education / 28 = Science & Technology / 25 = News & Politics
    default_language: str = "pt-BR"
    privacy_status: Literal["private", "unlisted", "public"] = "public"
    publish_at_iso: Optional[str] = None
    contains_synthetic_media: bool = True
    self_declared_made_for_kids: bool = False
    related_long_video_id: Optional[str] = None
    thumbnail_path: Optional[str] = None
    ab_test_titles: List[str] = field(default_factory=list)


@dataclass
class UploadReceipt:
    """Recibo auditável de publicação ou agendamento no YouTube."""

    youtube_video_id: Optional[str]
    channel_id: str
    video_format: VideoFormat
    title: str
    privacy_status: str
    scheduled_publish_at: Optional[str]
    contains_synthetic_media: bool
    related_long_video_id: Optional[str]
    thumbnail_uploaded: bool
    studio_url: str
    watch_url: str
    simulated: bool
    state: UploadState = UploadState.PENDING
    policy_version: str = POLICY_VERSION
    artifact_sha256: Optional[str] = None
    oauth_authorized: bool = False
    error_or_warning: Optional[str] = None
    uploaded_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if isinstance(d.get("state"), UploadState):
            d["state"] = d["state"].value
        return d


@dataclass
class ScheduledReleasePlan:
    """Plano integrado de lançamento (1 Vídeo Longo 16:9 + N Shorts 9:16 de funil)."""

    long_video_receipt: UploadReceipt
    shorts_receipts: List[UploadReceipt]
    funnel_strategy_notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class YouTubeMultiChannelUploader:
    """
    Orquestrador multi-canal para upload no YouTube Data API v3 com agendamento
    inteligente e flag de mídia sintética/alterada (`containsSyntheticMedia`).
    """

    # Horários nobres em UTC (equivalentes a 19h, 20h e 21h BRT / UTC-3)
    PRIME_TIME_UTC_HOUR_BY_NICHE: Dict[str, int] = {
        "geopolitics_economic_collapses": 22,  # 19:00 BRT
        "cyber_heists_ai_investigative": 23,  # 20:00 BRT
        "dark_psychology_power_dynamics": 0,  # 21:00 BRT
    }

    CATEGORY_ID_BY_NICHE: Dict[str, str] = {
        "geopolitics_economic_collapses": "25",  # News & Politics / Documentary
        "cyber_heists_ai_investigative": "28",  # Science & Technology
        "dark_psychology_power_dynamics": "27",  # Education
    }

    CHANNEL_DISPLAY_NAMES: Dict[str, str] = {
        "UC8RJWr3b2pKtnU1wOhV_bDQ": "A Via da Descoberta",
        "@AViadaDescoberta": "A Via da Descoberta",
        "ch_1_investigativo": "A Via da Descoberta",
        "ch_1": "A Via da Descoberta",
        "ch-1": "A Via da Descoberta",
        "1": "A Via da Descoberta",
        "UCE6Ch6nhxI81Z6ILQIw23_Q": "Finanças Quânticas",
        "@FinancasQuanticasOficial": "Finanças Quânticas",
        "ch_2_financas": "Finanças Quânticas",
        "ch_2": "Finanças Quânticas",
        "ch-2": "Finanças Quânticas",
        "2": "Finanças Quânticas",
        "UCIjEnT4adPYVyi0UlrCITBA": "Bio Hack Longevidade",
        "@BioHackLongevidade": "Bio Hack Longevidade",
        "ch_3_ciencia": "Bio Hack Longevidade",
        "ch_3": "Bio Hack Longevidade",
        "ch-3": "Bio Hack Longevidade",
        "3": "Bio Hack Longevidade",
        "UCbO67ez7TKOJ8C_kpUF4t5Q": "Ain't No Human",
        "@aintnohumanoficial": "Ain't No Human",
        "ch_4_music": "Ain't No Human",
        "ch_4": "Ain't No Human",
        "ch-4": "Ain't No Human",
        "4": "Ain't No Human",
    }

    def _get_channel_display_name(self, channel_id: str) -> str:
        return self.CHANNEL_DISPLAY_NAMES.get(str(channel_id), "A Via da Descoberta")

    def __init__(self, credentials_dir: Optional[str] = None) -> None:
        self.credentials_dir = Path(
            credentials_dir
            or os.getenv("YOUTUBE_CREDENTIALS_DIR", "workspace/credentials")
        )

    def compute_next_prime_slot(
        self,
        niche_id: str,
        base_time: Optional[datetime] = None,
        offset_hours: int = 0,
    ) -> str:
        """
        Calcula o próximo horário nobre de publicação em formato ISO-8601 UTC (`YYYY-MM-DDTHH:MM:SSZ`),
        garantindo antecedência mínima de 2 horas para processamento de resolução 4K/HD pelo YouTube.
        """
        now_utc = base_time or datetime.now(timezone.utc)
        target_hour = self.PRIME_TIME_UTC_HOUR_BY_NICHE.get(niche_id, 22)

        candidate = now_utc.replace(
            hour=target_hour, minute=0, second=0, microsecond=0
        )
        if candidate <= now_utc + timedelta(hours=2):
            candidate += timedelta(days=1)

        final_slot = candidate + timedelta(hours=offset_hours)
        return final_slot.strftime("%Y-%m-%dT%H:%M:%SZ")

    def build_youtube_api_body(self, metadata: UploadMetadata) -> Dict[str, Any]:
        """
        Constrói o payload oficial do recurso `videos.insert` da YouTube Data API v3,
        incluindo `containsSyntheticMedia` e agendamento `publishAt`.
        """
        description = metadata.description.strip()
        if (
            metadata.video_format == "SHORT_9_16"
            and "#Shorts" not in description
            and "#shorts" not in description
        ):
            description = f"{description}\n\n#Shorts #Documentario"

        if metadata.video_format == "SHORT_9_16" and metadata.related_long_video_id:
            description = (
                f"{description}\n\n"
                f"▶ Assista à investigação completa (16:9): https://www.youtube.com/watch?v={metadata.related_long_video_id}"
            )

        # Rodapé genérico "Produzido ... via Dark Studio Platform" removido (política de autenticidade).

        status_block: Dict[str, Any] = {
            "privacyStatus": "private" if metadata.publish_at_iso else metadata.privacy_status,
            "selfDeclaredMadeForKids": metadata.self_declared_made_for_kids,
            "containsSyntheticMedia": metadata.contains_synthetic_media,
        }
        if metadata.publish_at_iso:
            status_block["publishAt"] = metadata.publish_at_iso

        # Sanitiza título: remove quaisquer tags de teste entre colchetes como [CINEMA V2], [TESTE], etc.
        clean_title = re.sub(r"^\s*\[[^\]]+\]\s*", "", metadata.title).strip()
        if not clean_title:
            clean_title = metadata.title.strip()

        return {
            "snippet": {
                "title": clean_title[:100],
                "description": description[:5000],
                "tags": metadata.tags[:35],
                "categoryId": metadata.category_id
                or self.CATEGORY_ID_BY_NICHE.get(metadata.niche_id, "27"),
                "defaultLanguage": metadata.default_language,
                "defaultAudioLanguage": metadata.default_language,
            },
            "status": status_block,
        }

    def _has_valid_oauth_token(self, channel_id: str) -> Optional[Path]:
        """
        Strict per-channel OAuth2 token lookup.
        NEVER falls back to another channel's token to prevent cross-channel uploads.
        """
        cid_clean = str(channel_id).strip()
        if cid_clean in ("1", "channel_1", "ch-1", "ch_1", "UC8RJWr3b2pKtnU1wOhV_bDQ"):
            candidate_names = [
                "UC8RJWr3b2pKtnU1wOhV_bDQ_token.json",
                "channel_1_token.json",
            ]
        elif cid_clean in ("2", "channel_2", "ch-2", "ch_2", "UCE6Ch6nhxI81Z6ILQIw23_Q"):
            candidate_names = [
                "UCE6Ch6nhxI81Z6ILQIw23_Q_token.json",
                "channel_2_token.json",
            ]
        elif cid_clean in ("3", "channel_3", "ch-3", "ch_3", "@BioHackLongevidade", "UCIjEnT4adPYVyi0UlrCITBA"):
            candidate_names = [
                "UCIjEnT4adPYVyi0UlrCITBA_token.json",
                "channel_3_token.json",
                "client_secret_ch3.json",
                "token_ch3.json",
            ]
        elif cid_clean in ("4", "channel_4", "ch-4", "ch_4", "@aintnohumanoficial", "UCbO67ez7TKOJ8C_kpUF4t5Q"):
            candidate_names = [
                "UCbO67ez7TKOJ8C_kpUF4t5Q_token.json",
                "channel_4_token.json",
            ]
        else:
            candidate_names = [
                f"{cid_clean}_token.json",
                f"{cid_clean}.json",
            ]

        dirs_to_check = [
            self.credentials_dir,
            Path("/home/eudespatricio/dark_studio_platform/workspace/youtube_tokens"),
            Path("/home/eudespatricio/dark_studio_platform/workspace/credentials"),
            Path("/home/eudespatricio/dark_studio_platform/workspace/tokens"),
        ]
        for d in dirs_to_check:
            for name in candidate_names:
                p = d / name
                if p.exists() and p.is_file():
                    return p
        return None

    @staticmethod
    def get_canonical_channel_id(channel_id: str) -> Optional[str]:
        """Maps channel slugs, numbers or handles to their canonical YouTube Channel ID."""
        cid = str(channel_id).strip()
        if cid in ("1", "channel_1", "ch-1", "ch_1", "UC8RJWr3b2pKtnU1wOhV_bDQ"):
            return "UC8RJWr3b2pKtnU1wOhV_bDQ"
        if cid in ("2", "channel_2", "ch-2", "ch_2", "UCE6Ch6nhxI81Z6ILQIw23_Q"):
            return "UCE6Ch6nhxI81Z6ILQIw23_Q"
        if cid in ("3", "channel_3", "ch-3", "ch_3", "@BioHackLongevidade", "UCIjEnT4adPYVyi0UlrCITBA"):
            return "UCIjEnT4adPYVyi0UlrCITBA"
        if cid in ("4", "channel_4", "ch-4", "ch_4", "@aintnohumanoficial", "UCbO67ez7TKOJ8C_kpUF4t5Q"):
            return "UCbO67ez7TKOJ8C_kpUF4t5Q"
        if cid.startswith("UC"):
            return cid
        return None

    def upload_video(
        self,
        video_path: str,
        metadata: UploadMetadata,
    ) -> UploadReceipt:
        """
        Realiza o upload fail-closed de um vídeo (16:9 ou 9:16) para o canal especificado.
        Executa verificação criptográfica de token, validação de canal OAuth2 real
        e auditoria física completa via AntiGarbageSentinelAgent antes de qualquer envio.
        """
        video_file = Path(video_path)
        token_path = self._has_valid_oauth_token(metadata.channel_id)
        _is_music = metadata.channel_id in ("4", "UCbO67ez7TKOJ8C_kpUF4t5Q") or str(metadata.category_id) == "10"
        rules = resolve_format_rules(metadata.video_format, is_music=_is_music)

        # 1. Trava Estrita de Pré-Upload: Cadence Guard Filter (Cooldown 90m + Anti-Duplicata + Context Lock)
        try:
            from backend.publisher.cadence_guard_filter import cadence_guard_filter

            # Trava de Contexto (Context Lock): vincula Short ao Documentário Longo ativo
            metadata.description, metadata.related_long_video_id = cadence_guard_filter.enforce_context_lock(
                channel_id=metadata.channel_id,
                video_format=metadata.video_format,
                title=metadata.title,
                description=metadata.description,
                related_long_video_id=metadata.related_long_video_id,
            )

            # Trava de Cooldown (Mínimo 90 minutos entre uploads para evitar flag anti-spam)
            ok_cool, elap_min, cool_msg = cadence_guard_filter.check_cooldown(metadata.channel_id)
            if not ok_cool:
                error_msg = f"BLOQUEIO CADENCE GUARD (COOLDOWN): {cool_msg}"
                logger.warning(error_msg)
                return UploadReceipt(
                    state=UploadState.BLOCKED,
                    youtube_video_id="BLOCKED_COOLDOWN",
                    channel_id=metadata.channel_id,
                    video_format=metadata.video_format,
                    title=metadata.title,
                    privacy_status="blocked",
                    scheduled_publish_at=None,
                    contains_synthetic_media=metadata.contains_synthetic_media,
                    related_long_video_id=metadata.related_long_video_id,
                    thumbnail_uploaded=False,
                    studio_url="",
                    watch_url="",
                    simulated=False,
                    oauth_authorized=bool(token_path),
                    error_or_warning=error_msg,
                )

            # Trava de Duplicata (Previne re-uploads acidentais de títulos idênticos em 7 dias)
            ok_dup, dup_msg = cadence_guard_filter.check_duplicate(metadata.channel_id, metadata.title)
            if not ok_dup:
                error_msg = f"BLOQUEIO CADENCE GUARD (DUPLICATA): {dup_msg}"
                logger.warning(error_msg)
                return UploadReceipt(
                    state=UploadState.BLOCKED,
                    youtube_video_id="BLOCKED_DUPLICATE",
                    channel_id=metadata.channel_id,
                    video_format=metadata.video_format,
                    title=metadata.title,
                    privacy_status="blocked",
                    scheduled_publish_at=None,
                    contains_synthetic_media=metadata.contains_synthetic_media,
                    related_long_video_id=metadata.related_long_video_id,
                    thumbnail_uploaded=False,
                    studio_url="",
                    watch_url="",
                    simulated=False,
                    oauth_authorized=bool(token_path),
                    error_or_warning=error_msg,
                )
        except Exception as guard_err:
            error_msg = f"FAIL-CLOSED CADENCE GUARD ERRO: {guard_err}"
            logger.error(error_msg)
            return UploadReceipt(
                state=UploadState.BLOCKED,
                youtube_video_id="BLOCKED_GUARD_ERROR",
                channel_id=metadata.channel_id,
                video_format=metadata.video_format,
                title=metadata.title,
                privacy_status="blocked",
                scheduled_publish_at=None,
                contains_synthetic_media=metadata.contains_synthetic_media,
                related_long_video_id=metadata.related_long_video_id,
                thumbnail_uploaded=False,
                studio_url="",
                watch_url="",
                simulated=False,
                oauth_authorized=bool(token_path),
                error_or_warning=error_msg,
            )

        body = self.build_youtube_api_body(metadata)

        # 2. Trava Estrita de Pré-Upload via AntiGarbageSentinelAgent (Auditoria Física Fail-Closed)
        sentinel_sha256 = None
        try:
            from backend.agents.anti_garbage_sentinel_agent import AntiGarbageSentinelAgent

            sentinel = AntiGarbageSentinelAgent()
            sentinel_vote = sentinel.evaluate(
                {
                    "video_path": str(video_file),
                    "format": metadata.video_format,
                    "min_long_duration_sec": rules.min_duration_sec,
                    "channel_id": metadata.channel_id,
                    "category_id": metadata.category_id,
                    "is_music": metadata.channel_id == "UCbO67ez7TKOJ8C_kpUF4t5Q" or str(metadata.category_id) == "10",
                }
            )
            sentinel_sha256 = sentinel_vote.metrics.get("artifact_sha256")
            if sentinel_vote.veto:
                error_msg = f"BLOQUEIO ANTI-GARBAGE SENTINEL: {sentinel_vote.rationale}"
                logger.error(error_msg)
                return UploadReceipt(
                    state=UploadState.BLOCKED,
                    youtube_video_id="BLOCKED_MOCKUP",
                    channel_id=metadata.channel_id,
                    video_format=metadata.video_format,
                    title=metadata.title,
                    privacy_status="blocked",
                    scheduled_publish_at=None,
                    contains_synthetic_media=metadata.contains_synthetic_media,
                    related_long_video_id=metadata.related_long_video_id,
                    thumbnail_uploaded=False,
                    studio_url="",
                    watch_url="",
                    simulated=False,
                    artifact_sha256=sentinel_sha256,
                    oauth_authorized=bool(token_path),
                    error_or_warning=error_msg,
                )
        except Exception as cv_err:
            error_msg = f"FAIL-CLOSED SENTINEL ERRO: {cv_err}"
            logger.error(error_msg)
            return UploadReceipt(
                state=UploadState.BLOCKED,
                youtube_video_id="BLOCKED_SENTINEL_ERROR",
                channel_id=metadata.channel_id,
                video_format=metadata.video_format,
                title=metadata.title,
                privacy_status="blocked",
                scheduled_publish_at=None,
                contains_synthetic_media=metadata.contains_synthetic_media,
                related_long_video_id=metadata.related_long_video_id,
                thumbnail_uploaded=False,
                studio_url="",
                watch_url="",
                simulated=False,
                oauth_authorized=bool(token_path),
                error_or_warning=error_msg,
            )

        if not token_path or not video_file.exists():
            warn_reason = (
                "Token OAuth2 não encontrado em workspace/credentials/"
                if not token_path
                else f"Vídeo {video_path} não encontrado no disco"
            )
            return UploadReceipt(
                state=UploadState.FAILED,
                youtube_video_id=None,
                channel_id=metadata.channel_id,
                video_format=metadata.video_format,
                title=body["snippet"]["title"],
                privacy_status="failed",
                scheduled_publish_at=None,
                contains_synthetic_media=metadata.contains_synthetic_media,
                related_long_video_id=metadata.related_long_video_id,
                thumbnail_uploaded=False,
                studio_url="",
                watch_url="",
                simulated=False,
                artifact_sha256=sentinel_sha256,
                oauth_authorized=bool(token_path),
                error_or_warning=warn_reason,
            )

        # 3. Trava de Safety Mode (P0.1: Default AUTO_PUBLISH_ENABLED=false exige aprovação manual)
        if not AUTO_PUBLISH_ENABLED and metadata.privacy_status == "public":
            logger.info("SAFETY MODE ATIVO: AUTO_PUBLISH_ENABLED=false. Upload público retido para aprovação manual.")
            return UploadReceipt(
                state=UploadState.DRY_RUN_COMPLETED,
                youtube_video_id=None,
                channel_id=metadata.channel_id,
                video_format=metadata.video_format,
                title=body["snippet"]["title"],
                privacy_status="held_for_safety",
                scheduled_publish_at=body["status"].get("publishAt"),
                contains_synthetic_media=metadata.contains_synthetic_media,
                related_long_video_id=metadata.related_long_video_id,
                thumbnail_uploaded=False,
                studio_url="",
                watch_url="",
                simulated=True,
                artifact_sha256=sentinel_sha256,
                oauth_authorized=True,
                error_or_warning="SAFETY MODE: Publicação ao vivo bloqueada (AUTO_PUBLISH_ENABLED=false). Execute com aprovação humana ou defina AUTO_PUBLISH_ENABLED=true.",
            )

        # 3.5. Checagem Preventiva de Quota Circuit Breaker (Zero API Calls se cota esgotada)
        from backend.publisher.cadence_guard_filter import cadence_guard_filter
        if cadence_guard_filter.is_quota_tripped():
            logger.warning("⚡ [QUOTA CIRCUIT BREAKER] Cota diária do YouTube esgotada. Upload de '%s' abortado preventivamente.", metadata.title)
            return UploadReceipt(
                state=UploadState.BLOCKED,
                youtube_video_id=None,
                channel_id=metadata.channel_id,
                video_format=metadata.video_format,
                title=body["snippet"]["title"],
                privacy_status="blocked",
                scheduled_publish_at=None,
                contains_synthetic_media=metadata.contains_synthetic_media,
                related_long_video_id=metadata.related_long_video_id,
                thumbnail_uploaded=False,
                studio_url="",
                watch_url="",
                simulated=False,
                artifact_sha256=sentinel_sha256,
                oauth_authorized=True,
                error_or_warning="QUOTA_EXCEEDED: Cota diária da YouTube Data API esgotada. Aguardando janela de reset às 04:05 BRT.",
            )

        # 4. Transmissão Real para YouTube Data API v3 com Checagem Estrita de Identidade OAuth (C6)
        try:
            from google.oauth2.credentials import Credentials  # type: ignore
            from google.auth.transport.requests import Request  # type: ignore
            from googleapiclient.discovery import build  # type: ignore
            from googleapiclient.http import MediaFileUpload  # type: ignore

            creds = Credentials.from_authorized_user_file(str(token_path))
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                token_path.write_text(creds.to_json(), encoding="utf-8")
                try:
                    os.chmod(str(token_path), 0o600)
                except Exception:
                    pass

            youtube = build("youtube", "v3", credentials=creds)

            # Strict OAuth channel identity check: verify token matches expected channel ID
            expected_cid = self.get_canonical_channel_id(metadata.channel_id)
            mine_res = youtube.channels().list(part="id,snippet", mine=True).execute()
            items = mine_res.get("items", [])
            if not items:
                err_msg = f"BLOQUEIO DE SEGURANÇA OAUTH: Token para canal {metadata.channel_id} não retornou canais válidos em mine=True."
                logger.error(err_msg)
                return UploadReceipt(
                    state=UploadState.BLOCKED,
                    youtube_video_id=None,
                    channel_id=metadata.channel_id,
                    video_format=metadata.video_format,
                    title=body["snippet"]["title"],
                    privacy_status="blocked",
                    scheduled_publish_at=None,
                    contains_synthetic_media=metadata.contains_synthetic_media,
                    related_long_video_id=metadata.related_long_video_id,
                    thumbnail_uploaded=False,
                    studio_url="",
                    watch_url="",
                    simulated=False,
                    artifact_sha256=sentinel_sha256,
                    oauth_authorized=True,
                    error_or_warning=err_msg,
                )

            actual_cid = items[0]["id"]
            if expected_cid and actual_cid != expected_cid:
                err_msg = (
                    f"BLOQUEIO DE SEGURANÇA OAUTH (C6): Token pertence ao canal {actual_cid} "
                    f"('{items[0].get('snippet', {}).get('title')}'), mas o upload tem como alvo "
                    f"{expected_cid} ({metadata.channel_id}). Abortado para impedir cross-upload!"
                )
                logger.error(err_msg)
                return UploadReceipt(
                    state=UploadState.BLOCKED,
                    youtube_video_id=None,
                    channel_id=metadata.channel_id,
                    video_format=metadata.video_format,
                    title=body["snippet"]["title"],
                    privacy_status="blocked",
                    scheduled_publish_at=None,
                    contains_synthetic_media=metadata.contains_synthetic_media,
                    related_long_video_id=metadata.related_long_video_id,
                    thumbnail_uploaded=False,
                    studio_url="",
                    watch_url="",
                    simulated=False,
                    artifact_sha256=sentinel_sha256,
                    oauth_authorized=True,
                    error_or_warning=err_msg,
                )

            media = MediaFileUpload(
                str(video_file),
                chunksize=10 * 1024 * 1024,
                resumable=True,
                mimetype="video/mp4",
            )
            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media,
            )
            response = request.execute()
            yt_video_id = str(response["id"])

            thumb_uploaded = False
            if metadata.thumbnail_path and Path(metadata.thumbnail_path).exists():
                try:
                    from backend.publisher.cadence_guard_filter import cadence_guard_filter
                    if cadence_guard_filter.is_quota_tripped():
                        cadence_guard_filter.enqueue_pending_action(
                            "set_thumbnail",
                            metadata.channel_id,
                            yt_video_id,
                            {"thumbnail_path": str(metadata.thumbnail_path)},
                        )
                    else:
                        youtube.thumbnails().set(
                            videoId=yt_video_id,
                            media_body=MediaFileUpload(metadata.thumbnail_path),
                        ).execute()
                        thumb_uploaded = True
                except Exception as t_err:
                    logger.warning("Falha ao subir thumbnail (enfileirada para pós-reset): %s", t_err)
                    try:
                        from backend.publisher.cadence_guard_filter import cadence_guard_filter
                        if "quotaExceeded" in str(t_err):
                            cadence_guard_filter.trip_quota_breaker(str(t_err))
                        cadence_guard_filter.enqueue_pending_action(
                            "set_thumbnail",
                            metadata.channel_id,
                            yt_video_id,
                            {"thumbnail_path": str(metadata.thumbnail_path)},
                        )
                    except Exception:
                        pass

            # Registro no Livro-Razão e Fixação de Comentário de Contexto (Context Lock)
            try:
                from backend.publisher.cadence_guard_filter import cadence_guard_filter
                cadence_guard_filter.record_upload(
                    channel_id=metadata.channel_id,
                    video_id=yt_video_id,
                    title=body["snippet"]["title"],
                    video_format=metadata.video_format,
                    related_long_video_id=metadata.related_long_video_id,
                    notes="Upload ao vivo via YouTube Data API v3"
                )
                if metadata.video_format == "SHORT_9_16" and metadata.related_long_video_id:
                    cadence_guard_filter.post_pinned_context_comment(
                        channel_id=metadata.channel_id,
                        short_video_id=yt_video_id,
                        long_video_id=metadata.related_long_video_id
                    )
            except Exception as post_err:
                logger.warning("Aviso nas ações pós-upload (ledger/comentário): %s", post_err)

            is_scheduled = bool(body["status"].get("publishAt"))
            return UploadReceipt(
                state=UploadState.SCHEDULED if is_scheduled else UploadState.UPLOADED,
                youtube_video_id=yt_video_id,
                channel_id=metadata.channel_id,
                video_format=metadata.video_format,
                title=body["snippet"]["title"],
                privacy_status=body["status"]["privacyStatus"],
                scheduled_publish_at=body["status"].get("publishAt"),
                contains_synthetic_media=body["status"]["containsSyntheticMedia"],
                related_long_video_id=metadata.related_long_video_id,
                thumbnail_uploaded=thumb_uploaded,
                studio_url=f"https://studio.youtube.com/video/{yt_video_id}/edit",
                watch_url=(
                    f"https://www.youtube.com/shorts/{yt_video_id}"
                    if metadata.video_format == "SHORT_9_16"
                    else f"https://www.youtube.com/watch?v={yt_video_id}"
                ),
                simulated=False,
                artifact_sha256=sentinel_sha256,
                oauth_authorized=True,
            )
        except Exception as exc:
            err_msg = f"Falha no upload ao vivo para o canal {metadata.channel_id}: {exc}"
            logger.error(err_msg)
            return UploadReceipt(
                state=UploadState.FAILED,
                youtube_video_id=None,
                channel_id=metadata.channel_id,
                video_format=metadata.video_format,
                title=body["snippet"]["title"],
                privacy_status="failed",
                scheduled_publish_at=body["status"].get("publishAt"),
                contains_synthetic_media=body["status"]["containsSyntheticMedia"],
                related_long_video_id=metadata.related_long_video_id,
                thumbnail_uploaded=False,
                studio_url="",
                watch_url="",
                simulated=False,
                artifact_sha256=sentinel_sha256,
                oauth_authorized=True,
                error_or_warning=str(exc),
            )

    def schedule_synchronized_release(
        self,
        long_video_path: str,
        long_metadata: UploadMetadata,
        shorts_payloads: List[tuple[str, UploadMetadata]],
        base_time: Optional[datetime] = None,
    ) -> ScheduledReleasePlan:
        """
        Orquestra o lançamento sincronizado de 1 Vídeo Longo (16:9) + N Shorts (9:16):
        - Vídeo Longo é agendado para o próximo horário nobre do nicho (T+0h).
        - Se o upload do Vídeo Longo falhar ou for bloqueado pelo gate, aborta imediatamente os Shorts!
        - Short #1 é agendado para T+2h (impulso inicial de tráfego com link Related Video).
        - Short #2 é agendado para T+24h (segunda onda de descoberta para manter VPH alto).
        """
        if not long_metadata.publish_at_iso:
            long_metadata.publish_at_iso = self.compute_next_prime_slot(
                niche_id=long_metadata.niche_id,
                base_time=base_time,
                offset_hours=0,
            )

        long_receipt = self.upload_video(long_video_path, long_metadata)

        # FAIL-CLOSED (P0.6): Se o Long falhou ou foi bloqueado, NUNCA publicar Shorts apontando para o vazio!
        if (
            not long_receipt.youtube_video_id
            or str(long_receipt.youtube_video_id).startswith("BLOCKED")
            or long_receipt.state in (UploadState.BLOCKED, UploadState.FAILED)
        ):
            abort_reason = long_receipt.error_or_warning or "Vídeo Longo retido ou sem ID do YouTube"
            logger.error("Abortando lançamento sincronizado de Shorts: %s", abort_reason)
            return ScheduledReleasePlan(
                long_video_receipt=long_receipt,
                shorts_receipts=[],
                funnel_strategy_notes=f"Lançamento de Shorts abortado: Vídeo Longo não foi publicado ({abort_reason}).",
            )

        shorts_receipts: List[UploadReceipt] = []
        hour_offsets = [2, 24, 48]

        for idx, (short_path, short_meta) in enumerate(shorts_payloads):
            offset = hour_offsets[idx] if idx < len(hour_offsets) else (idx + 1) * 24
            short_meta.video_format = "SHORT_9_16"
            short_meta.related_long_video_id = long_receipt.youtube_video_id
            if not short_meta.publish_at_iso:
                short_meta.publish_at_iso = self.compute_next_prime_slot(
                    niche_id=long_metadata.niche_id,
                    base_time=base_time,
                    offset_hours=offset,
                )
            short_receipt = self.upload_video(short_path, short_meta)
            shorts_receipts.append(short_receipt)

        return ScheduledReleasePlan(
            long_video_receipt=long_receipt,
            shorts_receipts=shorts_receipts,
            funnel_strategy_notes=(
                f"Vídeo Longo ({long_receipt.youtube_video_id}) agendado para "
                f"{long_receipt.scheduled_publish_at} com {len(shorts_receipts)} Shorts "
                f"escalonados vinculados via Related Video e containsSyntheticMedia=True."
            ),
        )


# Backward compatibility alias
YouTubeUploader = YouTubeMultiChannelUploader
