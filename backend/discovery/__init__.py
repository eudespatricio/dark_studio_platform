"""
Dark Studio Platform — Discovery Module (Niche Scanner & Outlier Hunter).

Responsável por:
1. Avaliar nichos globais e calcular o Niche Opportunity Score (NOS de 0 a 100).
2. Selecionar automaticamente os Top 3 Nichos mais lucrativos e com maior gap de idioma.
3. Caçar vídeos Outliers (>= 3.0x a média do canal, alto VPH) e extrair picos de retenção
   (Most Replayed Heatmaps) para alimentar a esteira Long-Form (16:9) + Shorts (9:16).
"""

from backend.discovery.niche_scanner import (
    ChannelBlueprint,
    NicheMetrics,
    NicheOpportunityResult,
    NicheScanner,
)
from backend.discovery.outlier_hunter import (
    HeatmapPeak,
    OutlierCandidate,
    OutlierHunter,
    ShortCutRecommendation,
)

__all__ = [
    "ChannelBlueprint",
    "NicheMetrics",
    "NicheOpportunityResult",
    "NicheScanner",
    "HeatmapPeak",
    "OutlierCandidate",
    "OutlierHunter",
    "ShortCutRecommendation",
]
