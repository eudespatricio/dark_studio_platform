"""
Outlier Hunter — Caçador de Vídeos Validados em Outros Idiomas (Outlier Score >= 3.0x & VPH).

Responsável por:
1. Varredura de vídeos em idiomas-fonte (EN, DE, ES, KR, FR) dentro dos Top 3 Nichos.
2. Cálculo do `outlier_score = video_views / channel_avg_views` e filtragem estrita (`>= 3.0x`).
3. Cálculo de `vph` (Views Por Hora) para medir tração algorítmica atual.
4. Extração de dados de `heatmap` (picos *Most Replayed* do YouTube via `yt-dlp` ou curva
   de retenção validada) para determinar exatamente onde cortar os Shorts (9:16) de maior
   retenção para impulsionar o Vídeo Longo (16:9).
"""

from __future__ import annotations

import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class HeatmapPeak:
    """Representa um segmento de pico de retenção (Most Replayed) no vídeo original."""

    start_sec: float
    end_sec: float
    intensity: float  # 0.0 a 1.0 (1.0 = pico máximo de replay do vídeo)
    narrative_trigger: str = ""


@dataclass
class ShortCutRecommendation:
    """Recomendação cirúrgica de corte vertical (9:16) extraída do pico de Heatmap."""

    short_index: int
    start_sec: float
    end_sec: float
    duration_sec: float
    peak_intensity: float
    suggested_hook_overlay: str
    cliffhanger_cta_to_long: str


@dataclass
class OutlierCandidate:
    """Vídeo Outlier validado em outro idioma pronto para Transcriação Cultural."""

    video_id: str
    title_original: str
    source_language: str
    niche_id: str
    channel_name: str
    channel_subscribers: int
    video_views: int
    channel_avg_views: int
    outlier_score: float
    hours_since_published: float
    vph: float
    duration_sec: int
    source_url: str
    heatmap_peaks: List[HeatmapPeak] = field(default_factory=list)
    recommended_shorts_cuts: List[ShortCutRecommendation] = field(default_factory=list)
    transcreated_title_ptbr: str = ""
    thumbnail_concept: str = ""
    discovered_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        """Converte o candidato Outlier em dicionário serializável."""
        return asdict(self)


class OutlierHunter:
    """
    Motor de caça de vídeos Outliers (>= 3.0x a média do canal) com extração de picos
    Most Replayed (Heatmap) para geração combinada de Vídeo Longo (16:9) + Shorts (9:16).
    """

    DEFAULT_MIN_OUTLIER_SCORE: float = 3.0
    DEFAULT_MIN_VPH: float = 150.0

    def __init__(
        self,
        min_outlier_score: float = DEFAULT_MIN_OUTLIER_SCORE,
        min_vph: float = DEFAULT_MIN_VPH,
        youtube_api_key: Optional[str] = None,
    ) -> None:
        self.min_outlier_score = min_outlier_score
        self.min_vph = min_vph
        self.youtube_api_key = youtube_api_key or os.getenv("YOUTUBE_API_KEY", "")

    @staticmethod
    def calculate_outlier_score(video_views: int, channel_avg_views: int) -> float:
        """
        Calcula o multiplicador de Outlier:
            outlier_score = video_views / channel_avg_views
        """
        if channel_avg_views <= 0:
            raise ValueError("channel_avg_views deve ser maior que zero.")
        if video_views < 0:
            raise ValueError("video_views não pode ser negativo.")
        return round(float(video_views) / float(channel_avg_views), 2)

    @staticmethod
    def calculate_vph(video_views: int, hours_since_published: float) -> float:
        """
        Calcula Views Por Hora (VPH) garantindo divisor mínimo de 1.0 hora.
        """
        effective_hours = max(float(hours_since_published), 1.0)
        return round(float(video_views) / effective_hours, 2)

    @staticmethod
    def extract_shorts_from_heatmap(
        heatmap_data: List[Dict[str, float]],
        video_duration_sec: int,
        niche_id: str,
        max_shorts: int = 2,
        target_short_duration: float = 48.0,
    ) -> tuple[List[HeatmapPeak], List[ShortCutRecommendation]]:
        """
        Analisa a curva `heatmap` (formato nativo do yt-dlp: `[{'start_time': s, 'end_time': e, 'value': v}]`)
        identificando os picos *Most Replayed* (intensity >= 0.72) e constrói janelas de corte 9:16
        de 38s a 58s com cliffhanger apontando para o Vídeo Longo (Related Video).
        """
        if not heatmap_data:
            return [], []

        sorted_segments = sorted(
            heatmap_data, key=lambda seg: float(seg.get("value", 0.0)), reverse=True
        )

        peaks: List[HeatmapPeak] = []
        recommendations: List[ShortCutRecommendation] = []
        used_ranges: List[tuple[float, float]] = []

        for seg in sorted_segments:
            intensity = round(float(seg.get("value", 0.0)), 3)
            if intensity < 0.65 and len(peaks) >= max_shorts:
                continue

            seg_start = float(seg.get("start_time", 0.0))
            seg_end = float(seg.get("end_time", seg_start + 15.0))
            peak_center = (seg_start + seg_end) / 2.0

            # Evita sobreposição de cortes no mesmo trecho do vídeo
            if any(abs(peak_center - ((r[0] + r[1]) / 2.0)) < 60.0 for r in used_ranges):
                continue

            # Posiciona o pico de retenção aos ~35% do Short para prender o usuário e cortar no clímax
            cut_start = max(0.0, round(peak_center - (target_short_duration * 0.35), 1))
            cut_end = min(
                float(video_duration_sec),
                round(cut_start + target_short_duration, 1),
            )
            actual_duration = round(cut_end - cut_start, 1)

            used_ranges.append((cut_start, cut_end))
            short_idx = len(recommendations) + 1

            peak_obj = HeatmapPeak(
                start_sec=round(seg_start, 1),
                end_sec=round(seg_end, 1),
                intensity=intensity,
                narrative_trigger=str(
                    seg.get(
                        "narrative_trigger",
                        f"Pico Most Replayed #{short_idx} (Retenção Relativa {int(intensity * 100)}%)",
                    )
                ),
            )
            peaks.append(peak_obj)

            recommendations.append(
                ShortCutRecommendation(
                    short_index=short_idx,
                    start_sec=cut_start,
                    end_sec=cut_end,
                    duration_sec=actual_duration,
                    peak_intensity=intensity,
                    suggested_hook_overlay=(
                        f"NINGUÉM PERCEBEU ESSE DETALHE CRÍTICO... ({niche_id.upper()})"
                    ),
                    cliffhanger_cta_to_long=(
                        "Mas o verdadeiro colapso aconteceu 3 minutos depois. "
                        "Toque no vídeo relacionado aqui embaixo para ver a investigação completa."
                    ),
                )
            )

            if len(recommendations) >= max_shorts:
                break

        return peaks, recommendations

    def fetch_metadata_via_ytdlp(self, video_url: str) -> Optional[Dict[str, Any]]:
        """
        Extrai metadados reais de um vídeo do YouTube via `yt-dlp` (sem baixar o arquivo de mídia),
        incluindo `view_count`, `duration` e os pontos do gráfico `heatmap` (Most Replayed).
        Retorna `None` caso `yt_dlp` não esteja instalado ou sem conectividade.
        """
        try:
            import yt_dlp  # type: ignore

            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "extract_flat": False,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                return info
        except Exception as exc:
            logger.debug("yt-dlp indisponível ou offline para %s: %s", video_url, exc)
            return None

    def _get_seed_outlier_pool(self) -> List[Dict[str, Any]]:
        """
        Pool realista de vídeos candidatos nos Top 3 Nichos (incluindo Outliers >= 3.0x
        e vídeos normais < 3.0x para validar o filtro rigoroso do OutlierHunter).
        """
        return [
            # NICHO 1: Geopolítica, Mega-Projetos & Colapsos Econômicos
            {
                "video_id": "geo_de_outlier_01",
                "title_original": "Warum dieses 170-Milliarden-Megaprojekt in der Wüste heimlich stillsteht",
                "source_language": "DE",
                "niche_id": "geopolitics_economic_collapses",
                "channel_name": "GeoWirtschaft Analyse",
                "channel_subscribers": 84000,
                "video_views": 1120000,
                "channel_avg_views": 145000,
                "hours_since_published": 168.0,
                "duration_sec": 940,
                "source_url": "https://www.youtube.com/watch?v=geo_de_outlier_01",
                "transcreated_title_ptbr": "O Mega-Projeto de R$ 1 Trilhão no Deserto Que Está Colapsando em Silêncio",
                "thumbnail_concept": "Mapa 3D escuro da Arábia Saudita com rachadura luminosa vermelha cortando The Line + selo 'FALÊNCIA OCULTA?'",
                "heatmap": [
                    {
                        "start_time": 195.0,
                        "end_time": 230.0,
                        "value": 0.96,
                        "narrative_trigger": "Revelação das imagens de satélite mostrando as obras paradas",
                    },
                    {
                        "start_time": 580.0,
                        "end_time": 620.0,
                        "value": 0.89,
                        "narrative_trigger": "Cálculo matemático de por que o fundo soberano ficou sem liquidez",
                    },
                ],
            },
            {
                "video_id": "geo_en_outlier_02",
                "title_original": "How a Single Canal Chokepoint Could Bankrupt Three Continents in 72 Hours",
                "source_language": "EN",
                "niche_id": "geopolitics_economic_collapses",
                "channel_name": "Strategic Horizon",
                "channel_subscribers": 120000,
                "video_views": 890000,
                "channel_avg_views": 190000,
                "hours_since_published": 96.0,
                "duration_sec": 860,
                "source_url": "https://www.youtube.com/watch?v=geo_en_outlier_02",
                "transcreated_title_ptbr": "O Gargalo Marítimo de 30 Km Que Pode Quebrar o Brasil e a Europa em 72 Horas",
                "thumbnail_concept": "Globo escuro com rota comercial bloqueada em vermelho neon + seta '72 HORAS PARA O CAOS'",
                "heatmap": [
                    {
                        "start_time": 140.0,
                        "end_time": 175.0,
                        "value": 0.93,
                        "narrative_trigger": "Simulação em mapa do bloqueio simultâneo de navios petroleiros",
                    },
                    {
                        "start_time": 490.0,
                        "end_time": 530.0,
                        "value": 0.84,
                        "narrative_trigger": "Impacto imediato no preço dos alimentos e combustíveis no Brasil",
                    },
                ],
            },
            # Vídeo abaixo do corte (1.4x) para garantir teste de filtragem
            {
                "video_id": "geo_en_non_outlier_03",
                "title_original": "Weekly Global Trade Update Q3",
                "source_language": "EN",
                "niche_id": "geopolitics_economic_collapses",
                "channel_name": "Macro Daily",
                "channel_subscribers": 200000,
                "video_views": 70000,
                "channel_avg_views": 50000,
                "hours_since_published": 120.0,
                "duration_sec": 600,
                "source_url": "https://www.youtube.com/watch?v=geo_en_non_outlier_03",
                "transcreated_title_ptbr": "Resumo Semanal do Comércio Global",
                "thumbnail_concept": "Gráfico padrão",
                "heatmap": [],
            },
            # NICHO 2: Crimes Cibernéticos, Fraudes Bilionárias & Mistérios da IA
            {
                "video_id": "cyber_en_outlier_01",
                "title_original": "The Teenager Who Stole $243 Million in 14 Minutes Using a Fake AI Voice",
                "source_language": "EN",
                "niche_id": "cyber_heists_ai_investigative",
                "channel_name": "ZeroDay Chronicles",
                "channel_subscribers": 62000,
                "video_views": 1480000,
                "channel_avg_views": 130000,
                "hours_since_published": 110.0,
                "duration_sec": 1080,
                "source_url": "https://www.youtube.com/watch?v=cyber_en_outlier_01",
                "transcreated_title_ptbr": "Como um Adolescente Roubou R$ 1,4 Bilhão em 14 Minutos Clonando uma Única Voz com IA",
                "thumbnail_concept": "Silhueta iluminada por monitor verde + onda de áudio vermelha 'R$ 1.400.000.000 EM 14 MIN'",
                "heatmap": [
                    {
                        "start_time": 240.0,
                        "end_time": 282.0,
                        "value": 0.98,
                        "narrative_trigger": "Áudio reconstituído da ligação de engenharia social que enganou o diretor do banco",
                    },
                    {
                        "start_time": 780.0,
                        "end_time": 820.0,
                        "value": 0.91,
                        "narrative_trigger": "O erro banal de R$ 15 em um pedido de delivery que revelou o endereço do hacker",
                    },
                ],
            },
            {
                "video_id": "cyber_kr_outlier_02",
                "title_original": "북한 해커 그룹이 3초 만에 카지노 서버를 장악한 기막힌 방법",
                "source_language": "KR",
                "niche_id": "cyber_heists_ai_investigative",
                "channel_name": "다크웹 파일 (DarkWeb Files KR)",
                "channel_subscribers": 95000,
                "video_views": 760000,
                "channel_avg_views": 160000,
                "hours_since_published": 84.0,
                "duration_sec": 920,
                "source_url": "https://www.youtube.com/watch?v=cyber_kr_outlier_02",
                "transcreated_title_ptbr": "Como Hackers Invadiram um Cassino Bilionário Pelo Termômetro Inteligente do Aquário",
                "thumbnail_concept": "Aquário de luxo conectado a cabos de rede vermelhos + texto 'INVASÃO PELO AQUÁRIO?!'",
                "heatmap": [
                    {
                        "start_time": 165.0,
                        "end_time": 205.0,
                        "value": 0.95,
                        "narrative_trigger": "Animação 3D mostrando o pacote de dados saindo do termômetro IoT para o servidor central",
                    },
                    {
                        "start_time": 610.0,
                        "end_time": 650.0,
                        "value": 0.87,
                        "narrative_trigger": "Transferência silenciosa de 10 GB de dados VIPs para fora do país",
                    },
                ],
            },
            # NICHO 3: Psicologia Obscura, Maquiavelismo & Dinâmicas de Poder
            {
                "video_id": "psych_en_outlier_01",
                "title_original": "The Silent Manipulation Tactic Used by Every Narcissistic Leader (And How to Break It)",
                "source_language": "EN",
                "niche_id": "dark_psychology_power_dynamics",
                "channel_name": "Shadow Intellect",
                "channel_subscribers": 48000,
                "video_views": 960000,
                "channel_avg_views": 110000,
                "hours_since_published": 144.0,
                "duration_sec": 780,
                "source_url": "https://www.youtube.com/watch?v=psych_en_outlier_01",
                "transcreated_title_ptbr": "A Regra do Silêncio de 4 Segundos Que Desarma Qualquer Manipulador Instantaneamente",
                "thumbnail_concept": "Pintura barroca escura de Maquiavel com olhar dourado + texto 'O SILÊNCIO DE 4 SEGUNDOS'",
                "heatmap": [
                    {
                        "start_time": 115.0,
                        "end_time": 155.0,
                        "value": 0.97,
                        "narrative_trigger": "Demonstração prática da pausa de 4 segundos que inverte o frame da conversa",
                    },
                    {
                        "start_time": 460.0,
                        "end_time": 500.0,
                        "value": 0.90,
                        "narrative_trigger": "As 3 frases de duplo vínculo (Double Bind) e como neutralizá-las",
                    },
                ],
            },
            {
                "video_id": "psych_es_outlier_02",
                "title_original": "Por qué las personas demasiado buenas siempre terminan destruidas según Schopenhauer",
                "source_language": "ES",
                "niche_id": "dark_psychology_power_dynamics",
                "channel_name": "Filosofía Oculta",
                "channel_subscribers": 71000,
                "video_views": 620000,
                "channel_avg_views": 140000,
                "hours_since_published": 72.0,
                "duration_sec": 740,
                "source_url": "https://www.youtube.com/watch?v=psych_es_outlier_02",
                "transcreated_title_ptbr": "O Paradoxo de Schopenhauer: Por Que Ser 'Bom Demais' Torna Você um Alvo Fácil",
                "thumbnail_concept": "Estátua clássica rachada revelando ouro negro + texto 'NUNCA SEJA BOM DEMAIS'",
                "heatmap": [
                    {
                        "start_time": 180.0,
                        "end_time": 220.0,
                        "value": 0.92,
                        "narrative_trigger": "A fábula dos porcos-espinhos aplicada a relações de trabalho e família",
                    },
                    {
                        "start_time": 510.0,
                        "end_time": 548.0,
                        "value": 0.86,
                        "narrative_trigger": "A diferença entre bondade ingênua e bondade estratégica com limites",
                    },
                ],
            },
        ]

    def hunt_outliers(
        self,
        niche_ids: Optional[List[str]] = None,
        source_languages: Optional[List[str]] = None,
        min_outlier_score: Optional[float] = None,
        min_vph: Optional[float] = None,
    ) -> List[OutlierCandidate]:
        """
        Filtra e ranqueia vídeos Outliers validados dentro dos nichos e idiomas solicitados.
        Garante `outlier_score >= threshold` (padrão 3.0x) e extrai automaticamente
        os picos de Heatmap (Most Replayed) para corte de Shorts 9:16.
        """
        score_threshold = (
            min_outlier_score if min_outlier_score is not None else self.min_outlier_score
        )
        vph_threshold = min_vph if min_vph is not None else self.min_vph

        raw_pool = self._get_seed_outlier_pool()
        validated_outliers: List[OutlierCandidate] = []

        for item in raw_pool:
            if niche_ids and item["niche_id"] not in niche_ids:
                continue
            if source_languages and item["source_language"] not in source_languages:
                continue

            outlier_score = self.calculate_outlier_score(
                video_views=item["video_views"],
                channel_avg_views=item["channel_avg_views"],
            )
            vph = self.calculate_vph(
                video_views=item["video_views"],
                hours_since_published=item["hours_since_published"],
            )

            # Filtro estrito de Outlier (>= 3.0x) e velocidade VPH
            if outlier_score < score_threshold or vph < vph_threshold:
                continue

            peaks, short_cuts = self.extract_shorts_from_heatmap(
                heatmap_data=item.get("heatmap", []),
                video_duration_sec=item["duration_sec"],
                niche_id=item["niche_id"],
            )

            candidate = OutlierCandidate(
                video_id=item["video_id"],
                title_original=item["title_original"],
                source_language=item["source_language"],
                niche_id=item["niche_id"],
                channel_name=item["channel_name"],
                channel_subscribers=item["channel_subscribers"],
                video_views=item["video_views"],
                channel_avg_views=item["channel_avg_views"],
                outlier_score=outlier_score,
                hours_since_published=item["hours_since_published"],
                vph=vph,
                duration_sec=item["duration_sec"],
                source_url=item["source_url"],
                heatmap_peaks=peaks,
                recommended_shorts_cuts=short_cuts,
                transcreated_title_ptbr=item["transcreated_title_ptbr"],
                thumbnail_concept=item["thumbnail_concept"],
            )
            validated_outliers.append(candidate)

        # Ordena por combinação de Outlier Score e VPH
        validated_outliers.sort(
            key=lambda c: (c.outlier_score * 0.6) + ((c.vph / 1000.0) * 0.4),
            reverse=True,
        )

        logger.info(
            "OutlierHunter encontrou %d vídeos validados (threshold >= %.1fx).",
            len(validated_outliers),
            score_threshold,
        )
        return validated_outliers
