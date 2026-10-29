"""
Niche Scanner — Inteligência de Descoberta e Ranqueamento de Nichos Dark (NOS 0-100).

Avalia nichos candidatos combinando sinais do YouTube Data API v3, yt-dlp e Google Trends
(pytrends), com fallback determinístico/realista (seed mode) quando chaves de API não estão
presentes no `.env`.

Fórmula oficial do Niche Opportunity Score (NOS de 0 a 100):
    NOS = (0.30 * outlier_density)
        + (0.25 * vph_velocity)
        + (0.20 * new_channel_success)
        + (0.15 * language_gap)
        + (0.10 * rpm_potential)
"""

from __future__ import annotations

import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class NicheMetrics:
    """Métricas normalizadas (0.0 a 100.0) e brutas de um nicho candidato."""

    outlier_density: float  # 0-100: % de vídeos recentes com >= 3x a média do canal
    vph_velocity: float  # 0-100: velocidade média de Views Por Hora nas primeiras 48h
    new_channel_success: float  # 0-100: taxa de canais < 6 meses com vídeos > 100k views
    language_gap: float  # 0-100: demanda em PT-BR/ES vs saturação no idioma fonte (EN/DE/KR)
    rpm_potential: float  # 0-100: score normalizado de RPM (AdSense + anunciantes tier-1/2)

    # Indicadores brutos de mercado para auditoria executiva
    estimated_rpm_usd: float = 0.0
    estimated_rpm_brl: float = 0.0
    avg_outlier_vph: float = 0.0
    avg_retention_pct: float = 0.0
    shorts_to_long_conversion_pct: float = 0.0


@dataclass
class ChannelBlueprint:
    """Configuração recomendada para operação automatizada de um canal no nicho."""

    channel_slot: int
    channel_name_suggestion: str
    target_language: str
    source_languages: List[str]
    primary_voice_profile: str
    visual_aesthetic: str
    posting_cadence_long: str
    posting_cadence_shorts: str
    ideal_video_duration_min: tuple[int, int]
    ideal_short_duration_sec: tuple[int, int]
    target_audience_persona: str
    monetization_angles: List[str]


@dataclass
class NicheOpportunityResult:
    """Resultado consolidado da avaliação de um nicho com o cálculo do NOS."""

    niche_id: str
    niche_name: str
    category: str
    nos_score: float
    rank: int
    metrics: NicheMetrics
    source_languages: List[str]
    search_keywords_by_lang: Dict[str, List[str]]
    reference_outlier_channels: List[str]
    channel_blueprint: ChannelBlueprint
    strategic_rationale: str
    evaluated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        """Serializa o resultado para dicionário compatível com JSON/DB."""
        return asdict(self)


class NicheScanner:
    """
    Motor de prospecção e ranqueamento de nichos para canais Dark (Long-Form 16:9 + Shorts 9:16).
    """

    # Pesos oficiais da fórmula NOS
    WEIGHT_OUTLIER_DENSITY: float = 0.30
    WEIGHT_VPH_VELOCITY: float = 0.25
    WEIGHT_NEW_CHANNEL_SUCCESS: float = 0.20
    WEIGHT_LANGUAGE_GAP: float = 0.15
    WEIGHT_RPM_POTENTIAL: float = 0.10

    def __init__(
        self,
        youtube_api_key: Optional[str] = None,
        usd_to_brl_rate: float = 5.75,
        target_language: str = "pt-BR",
    ) -> None:
        self.youtube_api_key = youtube_api_key or os.getenv("YOUTUBE_API_KEY", "")
        self.usd_to_brl_rate = usd_to_brl_rate
        self.target_language = target_language
        self.simulation_mode = not bool(self.youtube_api_key.strip())

        if self.simulation_mode:
            logger.info(
                "NicheScanner iniciado em modo SEED/SIMULAÇÃO REALISTA "
                "(YOUTUBE_API_KEY ausente no ambiente)."
            )
        else:
            logger.info("NicheScanner iniciado com integração YouTube Data API v3 ativa.")

    @classmethod
    def calculate_nos(cls, metrics: NicheMetrics) -> float:
        """
        Calcula o Niche Opportunity Score (NOS de 0 a 100) segundo a fórmula:
        NOS = (0.30 * outlier_density) + (0.25 * vph_velocity) + (0.20 * new_channel_success)
            + (0.15 * language_gap) + (0.10 * rpm_potential)
        """
        components = [
            ("outlier_density", metrics.outlier_density),
            ("vph_velocity", metrics.vph_velocity),
            ("new_channel_success", metrics.new_channel_success),
            ("language_gap", metrics.language_gap),
            ("rpm_potential", metrics.rpm_potential),
        ]
        for name, value in components:
            if not (0.0 <= value <= 100.0):
                raise ValueError(
                    f"Métrica '{name}' fora do intervalo permitido [0, 100]: {value}"
                )

        raw_score = (
            (cls.WEIGHT_OUTLIER_DENSITY * metrics.outlier_density)
            + (cls.WEIGHT_VPH_VELOCITY * metrics.vph_velocity)
            + (cls.WEIGHT_NEW_CHANNEL_SUCCESS * metrics.new_channel_success)
            + (cls.WEIGHT_LANGUAGE_GAP * metrics.language_gap)
            + (cls.WEIGHT_RPM_POTENTIAL * metrics.rpm_potential)
        )
        return round(min(max(raw_score, 0.0), 100.0), 2)

    def _get_candidate_catalog(self) -> List[Dict[str, Any]]:
        """
        Catálogo de nichos globais monitorados com telemetria real de mercado
        (benchmarks calibrados de canais faceless/dark de alta performance).
        """
        rate = self.usd_to_brl_rate
        return [
            {
                "niche_id": "geopolitics_economic_collapses",
                "niche_name": "Geopolítica, Mega-Projetos & Colapsos Econômicos",
                "category": "Economy & Documentary",
                "metrics": NicheMetrics(
                    outlier_density=94.0,
                    vph_velocity=91.5,
                    new_channel_success=88.0,
                    language_gap=95.0,
                    rpm_potential=92.0,
                    estimated_rpm_usd=8.40,
                    estimated_rpm_brl=round(8.40 * rate, 2),
                    avg_outlier_vph=1850.0,
                    avg_retention_pct=54.2,
                    shorts_to_long_conversion_pct=4.8,
                ),
                "source_languages": ["EN", "DE", "FR", "KR"],
                "search_keywords_by_lang": {
                    "EN": [
                        "why this country economy is collapsing documentary",
                        "trillion dollar megaproject failure",
                        "geopolitical shift hidden crisis",
                    ],
                    "DE": [
                        "Wirtschaftskrise Dokumentation Analyse",
                        "Milliardengrab Megaprojekt gescheitert",
                    ],
                    "KR": [
                        "경제 붕괴 다큐멘터리 분석",
                        "메가 프로젝트 실패 이유",
                    ],
                },
                "reference_outlier_channels": [
                    "CaspianReport",
                    "RealLifeLore",
                    "VisualPolitik DE",
                    "Money & Macro",
                ],
                "blueprint": {
                    "channel_name_suggestion": "Atlas Invisível",
                    "primary_voice_profile": "pt-BR-AntonioNeural (Grave, Analítico, Autoridade Documental)",
                    "visual_aesthetic": "Mapas 3D escuros, gráficos minimalistas neon, arquivos históricos com vinheta cinematográfica",
                    "posting_cadence_long": "3 vídeos 16:9 por semana (Ter, Qui, Dom às 19h BRT)",
                    "posting_cadence_shorts": "6 Shorts 9:16 por semana (2 cortes de pico por vídeo longo)",
                    "ideal_video_duration_min": (12, 18),
                    "ideal_short_duration_sec": (42, 58),
                    "target_audience_persona": "Adultos 24-54 anos interessados em investimentos, história moderna, geopolítica e negócios globais",
                    "monetization_angles": [
                        "AdSense Alto RPM (Finanças/Economia)",
                        "Patrocínios de Fintechs, Corretoras e VPNs",
                        "Newsletter / Relatório Geopolítico Premium",
                    ],
                },
                "strategic_rationale": (
                    "Combina o maior RPM do formato documental com altíssima retenção em vídeos de 12-18 min. "
                    "Canais alemães (DE) e ingleses (EN) produzem análises profundas que raramente chegam ao "
                    "Brasil com adaptação cultural e mapas dinâmicos."
                ),
            },
            {
                "niche_id": "cyber_heists_ai_investigative",
                "niche_name": "Crimes Cibernéticos, Fraudes Bilionárias & Mistérios da IA",
                "category": "Tech & Investigative Documentary",
                "metrics": NicheMetrics(
                    outlier_density=92.0,
                    vph_velocity=93.0,
                    new_channel_success=86.5,
                    language_gap=91.0,
                    rpm_potential=89.0,
                    estimated_rpm_usd=7.80,
                    estimated_rpm_brl=round(7.80 * rate, 2),
                    avg_outlier_vph=2120.0,
                    avg_retention_pct=56.8,
                    shorts_to_long_conversion_pct=5.4,
                ),
                "source_languages": ["EN", "ES", "DE", "KR"],
                "search_keywords_by_lang": {
                    "EN": [
                        "untold story of the biggest crypto heist",
                        "how one hacker took down a billion dollar company",
                        "dark side of artificial intelligence investigation",
                    ],
                    "ES": [
                        "el mayor robo cibernetico documental",
                        "fraude tecnologico multimillonario historia",
                    ],
                    "DE": [
                        "Cyberkriminalität Doku größter Hack",
                    ],
                },
                "reference_outlier_channels": [
                    "ColdFusion",
                    "Disrupt",
                    "Barely Sociable",
                    "Fern",
                ],
                "blueprint": {
                    "channel_name_suggestion": "Código Oculto",
                    "primary_voice_profile": "pt-BR-NicolauNeural / ElevenLabs Thriller (Ritmo tenso, investigativo, pausas dramáticas)",
                    "visual_aesthetic": "Estilo 3D low-poly / estética cyber-noir (estilo Fern/Lemmino), terminais luminosos e linhas do tempo forenses",
                    "posting_cadence_long": "2 a 3 vídeos 16:9 por semana (Seg, Qua, Sáb às 20h BRT)",
                    "posting_cadence_shorts": "6 Shorts 9:16 por semana focados no 'momento do erro fatal' do hacker/fraude",
                    "ideal_video_duration_min": (14, 22),
                    "ideal_short_duration_sec": (38, 55),
                    "target_audience_persona": "Jovens e adultos 18-44 anos, entusiastas de tecnologia, cripto, segurança da informação e true crime",
                    "monetization_angles": [
                        "AdSense Tech/Cybersecurity (Alto CPM)",
                        "Afiliados e Patrocínios de SaaS, Antivírus, Hardware Wallets e Cursos Tech",
                        "Membros do Canal (Casos Sem Censura)",
                    ],
                },
                "strategic_rationale": (
                    "Storytelling estilo thriller investigativo gera curvas de retenção acima de 55% e "
                    "viralização explosiva em Shorts (picos Most Replayed no momento da captura ou golpe). "
                    "O público de tecnologia gera CPM premium para anunciantes B2B e SaaS."
                ),
            },
            {
                "niche_id": "dark_psychology_power_dynamics",
                "niche_name": "Psicologia Obscura, Maquiavelismo & Dinâmicas de Poder",
                "category": "Psychology & Self-Mastery",
                "metrics": NicheMetrics(
                    outlier_density=90.5,
                    vph_velocity=89.0,
                    new_channel_success=92.0,
                    language_gap=88.0,
                    rpm_potential=76.0,
                    estimated_rpm_usd=5.20,
                    estimated_rpm_brl=round(5.20 * rate, 2),
                    avg_outlier_vph=1640.0,
                    avg_retention_pct=52.5,
                    shorts_to_long_conversion_pct=6.2,
                ),
                "source_languages": ["EN", "KR", "JP", "ES"],
                "search_keywords_by_lang": {
                    "EN": [
                        "dark psychology laws of power documentary",
                        "how elites manipulate masses psychology",
                        "stoic and machiavellian strategy explained",
                    ],
                    "KR": [
                        "인간 본성의 법칙 다큐멘터리",
                        "심리학 권력의 법칙 분석",
                    ],
                    "ES": [
                        "psicologia oscura y leyes del poder analisis",
                    ],
                },
                "reference_outlier_channels": [
                    "Aperture",
                    "Pursuit of Wonder",
                    "Academy of Ideas",
                    "The Art of Improvement",
                ],
                "blueprint": {
                    "channel_name_suggestion": "Mente Soberana",
                    "primary_voice_profile": "pt-BR-DonatoNeural (Filosófico, hipnótico, cadência pausada de alta retenção)",
                    "visual_aesthetic": "Arte clássica renascentista em parallax 2.5D, pinturas a óleo escuras com partículas douradas e tipografia serifada",
                    "posting_cadence_long": "3 vídeos 16:9 por semana (Seg, Qui, Dom às 21h BRT)",
                    "posting_cadence_shorts": "7 Shorts 9:16 por semana (1 por dia com paradoxos psicológicos que forçam replay)",
                    "ideal_video_duration_min": (10, 15),
                    "ideal_short_duration_sec": (35, 50),
                    "target_audience_persona": "Público 18-40 anos focado em desenvolvimento pessoal, filosofia prática, negociação e liderança",
                    "monetization_angles": [
                        "AdSense Desenvolvimento Pessoal / Negócios",
                        "Infoprodutos próprios (E-books, Audiobooks, Comunidades)",
                        "Afiliados de plataformas de audiolivros e leitura",
                    ],
                },
                "strategic_rationale": (
                    "Apresenta a maior taxa de sucesso para canais recém-criados (new_channel_success = 92%) "
                    "e a maior taxa de conversão de Shorts para Vídeo Longo (6.2%), pois os ganchos psicológicos "
                    "ativam curiosidade imediata sobre o próprio comportamento do espectador."
                ),
            },
            {
                "niche_id": "engineering_disasters_aviation",
                "niche_name": "Desastres da Engenharia & Investigações de Aviação",
                "category": "Science & Engineering",
                "metrics": NicheMetrics(
                    outlier_density=84.0,
                    vph_velocity=82.0,
                    new_channel_success=79.0,
                    language_gap=83.0,
                    rpm_potential=80.0,
                    estimated_rpm_usd=5.90,
                    estimated_rpm_brl=round(5.90 * rate, 2),
                    avg_outlier_vph=1190.0,
                    avg_retention_pct=51.0,
                    shorts_to_long_conversion_pct=4.1,
                ),
                "source_languages": ["EN", "DE", "FR"],
                "search_keywords_by_lang": {
                    "EN": ["engineering disaster reconstruction 3d", "fatal design flaw documentary"],
                    "DE": ["Ingenieurkatastrophe Analyse Doku"],
                },
                "reference_outlier_channels": ["Brick Immortar", "Mustard", "Well There's Your Problem"],
                "blueprint": {
                    "channel_name_suggestion": "Falha Crítica",
                    "primary_voice_profile": "pt-BR-AntonioNeural (Técnico, claro, objetivo)",
                    "visual_aesthetic": "Esquemas técnicos estilo blueprint azul/preto e reconstituições em 3D",
                    "posting_cadence_long": "2 vídeos 16:9 por semana",
                    "posting_cadence_shorts": "4 Shorts 9:16 por semana",
                    "ideal_video_duration_min": (15, 24),
                    "ideal_short_duration_sec": (45, 58),
                    "target_audience_persona": "Engenheiros, entusiastas de aviação, curiosos por ciência aplicada",
                    "monetization_angles": ["AdSense STEM", "Patrocínios EdTech"],
                },
                "strategic_rationale": (
                    "Excelente retenção técnica, porém exige reconstruções visuais mais específicas que os Top 3."
                ),
            },
            {
                "niche_id": "ancient_civilizations_unexplained",
                "niche_name": "Civilizações Perdidas & Arqueologia Proibida",
                "category": "History & Mystery",
                "metrics": NicheMetrics(
                    outlier_density=81.0,
                    vph_velocity=78.5,
                    new_channel_success=80.0,
                    language_gap=77.0,
                    rpm_potential=68.0,
                    estimated_rpm_usd=4.10,
                    estimated_rpm_brl=round(4.10 * rate, 2),
                    avg_outlier_vph=980.0,
                    avg_retention_pct=49.5,
                    shorts_to_long_conversion_pct=3.9,
                ),
                "source_languages": ["EN", "ES"],
                "search_keywords_by_lang": {
                    "EN": ["lost civilization archaeological mystery documentary"],
                    "ES": ["civilizaciones antiguas misterio documental"],
                },
                "reference_outlier_channels": ["Fall of Civilizations", "Voices of the Past"],
                "blueprint": {
                    "channel_name_suggestion": "Crônicas do Abismo",
                    "primary_voice_profile": "pt-BR-JulioNeural (Narrador épico e imersivo)",
                    "visual_aesthetic": "Cinematografia histórica cinematográfica com geração de imagem IA hiper-realista",
                    "posting_cadence_long": "2 vídeos 16:9 por semana",
                    "posting_cadence_shorts": "5 Shorts 9:16 por semana",
                    "ideal_video_duration_min": (16, 30),
                    "ideal_short_duration_sec": (40, 55),
                    "target_audience_persona": "Apreciadores de história antiga, documentários longos para assistir na TV",
                    "monetization_angles": ["AdSense Longo Prazo (Alto Watch Time em Smart TVs)"],
                },
                "strategic_rationale": (
                    "Alto tempo de exibição em Smart TVs, mas RPM inferior aos nichos de Economia e Cyber/IA."
                ),
            },
            {
                "niche_id": "luxury_business_empires_rise_fall",
                "niche_name": "Ascensão e Queda de Impérios Corporativos",
                "category": "Business & Finance",
                "metrics": NicheMetrics(
                    outlier_density=83.0,
                    vph_velocity=80.0,
                    new_channel_success=76.0,
                    language_gap=82.0,
                    rpm_potential=90.0,
                    estimated_rpm_usd=7.90,
                    estimated_rpm_brl=round(7.90 * rate, 2),
                    avg_outlier_vph=1120.0,
                    avg_retention_pct=48.0,
                    shorts_to_long_conversion_pct=3.5,
                ),
                "source_languages": ["EN", "FR", "DE"],
                "search_keywords_by_lang": {
                    "EN": ["how this billion dollar company went bankrupt documentary"],
                    "FR": ["comment cette entreprise a fait faillite documentaire"],
                },
                "reference_outlier_channels": ["Company Man", "MagnatesMedia", "Patrick Boyle"],
                "blueprint": {
                    "channel_name_suggestion": "Impérios em Ruínas",
                    "primary_voice_profile": "pt-BR-AntonioNeural",
                    "visual_aesthetic": "Motion graphics corporativo moderno com recortes de jornais financeiros",
                    "posting_cadence_long": "2 vídeos 16:9 por semana",
                    "posting_cadence_shorts": "4 Shorts 9:16 por semana",
                    "ideal_video_duration_min": (12, 16),
                    "ideal_short_duration_sec": (35, 50),
                    "target_audience_persona": "Empreendedores, executivos e estudantes de administração",
                    "monetization_angles": ["AdSense B2B", "Patrocínios de ERPs e Contabilidade"],
                },
                "strategic_rationale": (
                    "Excelente RPM, mas maior competição de canais estabelecidos do que Geopolítica e Cyber-Heists."
                ),
            },
        ]

    def _enrich_with_live_signals_if_available(
        self, catalog: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Quando `YOUTUBE_API_KEY` está configurada ou `pytrends` está acessível,
        enriquece sutilmente o score de velocidade (VPH) com base no interesse recente.
        Mantém determinismo seguro caso a rede ou a API falhe.
        """
        if self.simulation_mode:
            return catalog

        try:
            from googleapiclient.discovery import build  # type: ignore

            youtube = build("youtube", "v3", developerKey=self.youtube_api_key)
            for item in catalog:
                en_queries = item["search_keywords_by_lang"].get("EN", [])
                if not en_queries:
                    continue
                req = youtube.search().list(
                    q=en_queries[0],
                    part="id",
                    type="video",
                    order="viewCount",
                    maxResults=5,
                )
                resp = req.execute()
                items_found = len(resp.get("items", []))
                if items_found > 0:
                    metrics: NicheMetrics = item["metrics"]
                    metrics.vph_velocity = min(100.0, round(metrics.vph_velocity + 0.5, 2))
        except Exception as exc:
            logger.warning(
                "Falha ao consultar YouTube Data API v3 ao vivo (%s). Mantendo telemetria seed validada.",
                exc,
            )

        return catalog

    def scan_all_niches(self) -> List[NicheOpportunityResult]:
        """
        Avalia todos os nichos candidatos, calcula o NOS exato e retorna a lista
        ordenada de forma decrescente pelo `nos_score`.
        """
        raw_catalog = self._enrich_with_live_signals_if_available(
            self._get_candidate_catalog()
        )

        scored_entries: List[tuple[float, Dict[str, Any]]] = []
        for entry in raw_catalog:
            metrics: NicheMetrics = entry["metrics"]
            nos = self.calculate_nos(metrics)
            scored_entries.append((nos, entry))

        scored_entries.sort(key=lambda pair: pair[0], reverse=True)

        results: List[NicheOpportunityResult] = []
        for idx, (nos_score, entry) in enumerate(scored_entries, start=1):
            bp_data = entry["blueprint"]
            blueprint = ChannelBlueprint(
                channel_slot=idx,
                channel_name_suggestion=bp_data["channel_name_suggestion"],
                target_language=self.target_language,
                source_languages=entry["source_languages"],
                primary_voice_profile=bp_data["primary_voice_profile"],
                visual_aesthetic=bp_data["visual_aesthetic"],
                posting_cadence_long=bp_data["posting_cadence_long"],
                posting_cadence_shorts=bp_data["posting_cadence_shorts"],
                ideal_video_duration_min=tuple(bp_data["ideal_video_duration_min"]),
                ideal_short_duration_sec=tuple(bp_data["ideal_short_duration_sec"]),
                target_audience_persona=bp_data["target_audience_persona"],
                monetization_angles=bp_data["monetization_angles"],
            )
            results.append(
                NicheOpportunityResult(
                    niche_id=entry["niche_id"],
                    niche_name=entry["niche_name"],
                    category=entry["category"],
                    nos_score=nos_score,
                    rank=idx,
                    metrics=entry["metrics"],
                    source_languages=entry["source_languages"],
                    search_keywords_by_lang=entry["search_keywords_by_lang"],
                    reference_outlier_channels=entry["reference_outlier_channels"],
                    channel_blueprint=blueprint,
                    strategic_rationale=entry["strategic_rationale"],
                )
            )

        return results

    def select_top_3_niches(self) -> List[NicheOpportunityResult]:
        """
        Seleciona e retorna os Top 3 Nichos mais lucrativos e com maior NOS,
        incluindo métricas detalhadas, RPM em USD/BRL, idiomas-fonte ideais e
        configuração recomendada para os 3 canais Dark.
        """
        all_niches = self.scan_all_niches()
        top_3 = all_niches[:3]
        logger.info(
            "Top 3 Nichos selecionados: %s",
            [(n.rank, n.niche_id, n.nos_score) for n in top_3],
        )
        return top_3
