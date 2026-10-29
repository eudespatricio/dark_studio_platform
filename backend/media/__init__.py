"""
Pacote de Engenharia Audiovisual e Pós-Produção Automatizada (`backend.media`).
Exporta os motores de download (`yt-dlp` + Heatmap), separação de stems (`Demucs`),
análise de cenas e talking-head (`PySceneDetect` + `OpenCV`), reenquadramento vertical
inteligente 9:16 (`SmartCropper`), remixagem Anti-Content ID (`VideoRemixer`),
renderização FFmpeg dual 16:9 e 9:16 com mixagem -14 LUFS e sidechain ducking (`VideoRenderer`),
e geração de Thumbnails de alto CTR 1280x720 (`ThumbnailMaker`).
"""

from .audio_separator import (
    AudioSeparationResult,
    AudioSeparator,
    get_audio_separator,
)
from .downloader import (
    DownloadedMediaBundle,
    HeatmapPeak,
    MediaDownloader,
    get_downloader,
)
from .remixer import (
    AntiContentIDConfig,
    RemixedTimelineClip,
    RemixTimelinePlan,
    VideoRemixer,
    get_remixer,
)
from .scene_analyzer import (
    BoundingBox,
    SceneAnalysisReport,
    SceneAnalyzer,
    SceneSegment,
    get_scene_analyzer,
)
from .smart_cropper import (
    CropKeyframe,
    SmartCropper,
    SmartCropPlan,
    get_smart_cropper,
)
from .thumbnail_maker import (
    ThumbnailArtifact,
    ThumbnailMaker,
    get_thumbnail_maker,
)
from .video_renderer import (
    AudioMasteringSpec,
    RenderOutputArtifact,
    VideoRenderer,
    get_video_renderer,
)

__all__ = [
    "AudioMasteringSpec",
    "AudioSeparationResult",
    "AudioSeparator",
    "AntiContentIDConfig",
    "BoundingBox",
    "CropKeyframe",
    "DownloadedMediaBundle",
    "HeatmapPeak",
    "MediaDownloader",
    "RemixedTimelineClip",
    "RemixTimelinePlan",
    "RenderOutputArtifact",
    "SceneAnalysisReport",
    "SceneAnalyzer",
    "SceneSegment",
    "SmartCropper",
    "SmartCropPlan",
    "ThumbnailArtifact",
    "ThumbnailMaker",
    "VideoRemixer",
    "VideoRenderer",
    "get_audio_separator",
    "get_downloader",
    "get_remixer",
    "get_scene_analyzer",
    "get_smart_cropper",
    "get_thumbnail_maker",
    "get_video_renderer",
]
