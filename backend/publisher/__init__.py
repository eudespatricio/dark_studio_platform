"""
Dark Studio Platform — Publisher & Analytics Module.

Responsável por:
1. Upload multi-canal autenticado via YouTube Data API v3 (`YouTubeMultiChannelUploader`),
   incluindo declaração obrigatória de mídia sintética/alterada (`containsSyntheticMedia`)
   e agendamento inteligente de Vídeo Longo (16:9) + Shorts (9:16) vinculados.
2. Sincronização de telemetria pós-publicação (`YouTubeAnalyticsSync`) coletando Views,
   CTR %, Retenção Média %, AVD (Average View Duration) e VPH, com diagnósticos acionáveis.
"""

from backend.publisher.analytics_sync import (
    ChannelAnalyticsSummary,
    VideoPerformanceSnapshot,
    YouTubeAnalyticsSync,
)
from backend.publisher.youtube_uploader import (
    ScheduledReleasePlan,
    UploadMetadata,
    UploadReceipt,
    YouTubeMultiChannelUploader,
)

__all__ = [
    "ChannelAnalyticsSummary",
    "VideoPerformanceSnapshot",
    "YouTubeAnalyticsSync",
    "ScheduledReleasePlan",
    "UploadMetadata",
    "UploadReceipt",
    "YouTubeMultiChannelUploader",
]
