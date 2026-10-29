"""
Copywriting Engine de Alto Nível — "Puro Creme do Milho Verde"
Frameworks de Retenção Psicológica, Ganchos Hipnóticos e Arquitetura de Títulos de Alto CTR
para o canal "A Via da Descoberta" e canais Dark Documentais de Elite.

Pilares fundamentais:
1. Teoria da Lacuna de Informação (George Loewenstein Information Gap):
   Cria uma coceira cognitiva imediata que o cérebro humano é biologicamente incapaz de ignorar.
2. Regra Anti-Tédio dos 3 Primeiros Segundos:
   Elimina qualquer introdução passiva. Entra no ponto mais tenso ou com uma inversão de premissa.
3. Micro-Tension Loops (Open Loops encadeados a cada 60-90 segundos).
4. Fórmulas de Títulos A/B de Alta Conversão (Sem sensacionalismo barato, com curiosidade irresistível).
5. Gerador dos 5 Ângulos Virais para Shorts (9:16) a partir de uma mesma investigação histórica.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class HighCTRTitlePack:
    """Pacote de Títulos A/B otimizados para CTR e algoritmo do YouTube."""

    title_curiosity_gap: str     # Ângulo A: Revelação de Arquivo / Conspiração Oculta
    title_scale_contrast: str    # Ângulo B: Escala Monstruosa / Números Específicos
    title_psychological_why: str # Ângulo C: O 'Porquê' Inquietante / O Erro Humano
    recommended_thumbnail_headline: str # 2 a 4 palavras de impacto para a Thumb
    badge_text: str              # Selo da Thumb (ex: "ARQUIVO REAL", "DESASTRE OCULTO")

    def to_list(self) -> List[str]:
        return [
            self.title_curiosity_gap,
            self.title_scale_contrast,
            self.title_psychological_why,
        ]


@dataclass
class ShortNarrativeAngle:
    """Estrutura de Roteiro dedicada para 1 dos 5 Shorts Diários."""

    slot_time_brt: str          # Horário de publicação (ex: "10:00")
    angle_name: str             # Nome do ângulo psicológico
    hook_0_3s: str              # Gancho fulminante nos primeiros 3 segundos
    narration_script_35_45s: str# Roteiro completo de narração (sem corte repentino)
    thumbnail_text: str         # Texto de capa do Short
    caption_power_words: List[str] # Palavras-chave que receberão destaque neon
    cta_to_long_video: str      # Ponte irresistível apontando para o Vídeo Longo (16:9)


class EliteCopywritingEngine:
    """
    Motor de Copywriting documental de altíssima conversão.
    Transforma dados brutos e históricos em narrativas magnéticas.
    """

    CHANNEL_NAME = "A Via da Descoberta"
    CHANNEL_HANDLE = "@AViadaDescoberta"

    # Verbos de alto impacto e substantivos magnéticos para títulos
    POWER_VERBS = [
        "Engoliu", "Desabou", "Apagou", "Escondeu", "Ignorou",
        "Destruiu", "Colapsou", "Silenciou", "Descobriu", "Rasgou"
    ]

    @classmethod
    def polish_title(cls, raw_title: str) -> str:
        """
        Limpa e lapida qualquer título bruto removendo marcas técnicas,
        ajustando pontuação e garantindo estilo 'puro creme'.
        """
        clean = re.sub(r"^\s*\[[^\]]+\]\s*", "", raw_title).strip()
        clean = re.sub(r"\s+", " ", clean)
        # Remove hashtags soltas no meio do título
        clean = re.sub(r"\s*#\w+", "", clean).strip()
        return clean[:100]

    @classmethod
    def generate_ab_titles(cls, subject: str, core_conflict: str, specific_number: str = "") -> HighCTRTitlePack:
        """
        Gera uma tríade de títulos A/B de padrão 'puro creme do milho verde'.
        """
        subject_clean = subject.strip()
        num_str = specific_number.strip() if specific_number else "Milhões"

        # Ângulo A: O Segredo de Arquivo / Mistério
        title_a = f"O Segredo de {num_str} Que a História Tentou Apagar: {subject_clean}"
        if len(title_a) > 95:
            title_a = f"O Que Esconderam Sobre: {subject_clean}"

        # Ângulo B: Contraste Brutal / Impacto de Escala
        title_b = f"O Tsunami de {num_str} Que Engoliu Uma Cidade em Minutos ({subject_clean})"
        if len(title_b) > 95:
            title_b = f"O Colapso de {num_str} que Ninguém Pôde Deter ({subject_clean})"

        # Ângulo C: O Erro Humano Inexplicável
        title_c = f"Por Que os Engenheiros Ignoraram o Aviso Que Custou {num_str} Vidas?"
        if len(title_c) > 95:
            title_c = f"O Erro Fatal Por Trás de {subject_clean}"

        headline_words = subject_clean.split()[:3]
        thumb_headline = " ".join(headline_words).upper()
        if len(thumb_headline) > 20:
            thumb_headline = "O ERRO FATAL"

        return HighCTRTitlePack(
            title_curiosity_gap=title_a[:100],
            title_scale_contrast=title_b[:100],
            title_psychological_why=title_c[:100],
            recommended_thumbnail_headline=thumb_headline,
            badge_text="ARQUIVO REAL",
        )

    @classmethod
    def craft_4_shorts_angles(
        cls,
        case_title: str,
        case_summary: str,
        long_video_id: Optional[str] = None
    ) -> List[ShortNarrativeAngle]:
        """
        Constrói 4 roteiros de Shorts totalmente autônomos e subsequentes ao Documentário Longo (11:00 BRT):
        - Short 1: 13:45 BRT - O Gancho Pós-Almoço / O Mistério Inicial
        - Short 2: 17:00 BRT - A Decisão Crítica / Os Avisos Ignorados (Volta pra Casa)
        - Short 3: 20:15 BRT - A Força Monstruosa / O Encobrimento Revelado (Horário Nobre Noturno)
        - Short 4: 06:30 BRT - A Lição Histórica / O Monumento ao Erro (Deslocamento Matinal D+1)
        """
        long_url = f"https://www.youtube.com/watch?v={long_video_id}" if long_video_id else ""
        bridge_suffix = (
            "▶ Assista ao documentário completo no canal: " + (long_url or "A Via da Descoberta")
        )

        return [
            # Short 1: 13:45 BRT - O Gancho Pós-Almoço
            ShortNarrativeAngle(
                slot_time_brt="13:45",
                angle_name="O Mistério dos Primeiros Segundos",
                hook_0_3s="Em menos de quatro minutos, uma cidade inteira foi varrida do mapa sem deixar rastros.",
                narration_script_35_45s=(
                    "Às dez e trinta e nove da noite, o chão tremeu antes de qualquer som. "
                    "Duzentos e setenta milhões de metros cúbicos de montanha desabaram direto na água. "
                    "O que subiu não foi apenas uma onda — foi uma muralha líquida de duzentos e cinquenta metros "
                    "que saltou a represa intacta e apagou duas mil vidas em minutos. "
                    "O documentário completo com os documentos desclassificados está disponível agora no nosso canal."
                ),
                thumbnail_text="APAGADOS DO MAPA",
                caption_power_words=["QUATRO MINUTOS", "VARRIDA", "250 METROS", "APAGOU", "DOCUMENTOS"],
                cta_to_long_video=bridge_suffix,
            ),
            # Short 2: 17:00 BRT - O Erro Crítico / A Decisão Estúpida ou Gananciosa
            ShortNarrativeAngle(
                slot_time_brt="17:00",
                angle_name="Os Avisos Ignorados",
                hook_0_3s="Eles sabiam que a montanha ia desabar semanas antes da tragédia acontecer.",
                narration_script_35_45s=(
                    "Os sensores já registravam que o Monte Toc estava se movendo trinta centímetros por dia. "
                    "Moradores locais ouviram estrondos profundos na rocha e pediram socorro. "
                    "Mesmo assim, para não atrasar a entrega da obra mais lucrativa da Europa, "
                    "a ordem foi continuar enchendo o reservatório. "
                    "O resultado foi a maior catástrofe que a engenharia moderna já presenciou."
                ),
                thumbnail_text="ELES SABIAM!",
                caption_power_words=["SABIAM", "SE MOVENDO", "ESTRONDOS", "LUCRO", "CATÁSTROFE"],
                cta_to_long_video=bridge_suffix,
            ),
            # Short 3: 20:15 BRT - A Força Monstruosa / Horário Nobre
            ShortNarrativeAngle(
                slot_time_brt="20:15",
                angle_name="A Força das Duas Bombas Atômicas",
                hook_0_3s="Uma onda de choque de ar com a violência de duas bombas nucleares varreu o vale.",
                narration_script_35_45s=(
                    "Quando a montanha atingiu o reservatório, o ar foi comprimido com tanta violência "
                    "que o vento arrancou os telhados de Longarone antes mesmo da água chegar. "
                    "Cinqüenta milhões de metros cúbicos de água caíram em queda livre de quinhentos metros de altura. "
                    "A pressão foi tão devastadora que transformou concreto e rocha em pó. "
                    "Veja os registros fotográficos originais no vídeo completo no canal."
                ),
                thumbnail_text="DUAS BOMBAS ATÔMICAS",
                caption_power_words=["DUAS BOMBAS", "VENTO", "50 MILHÕES", "PÓ", "REGISTROS"],
                cta_to_long_video=bridge_suffix,
            ),
            # Short 4: 06:30 BRT (D+1) - A Lição / Deslocamento Matinal Ônibus & Metrô
            ShortNarrativeAngle(
                slot_time_brt="06:30",
                angle_name="O Monumento ao Erro",
                hook_0_3s="A represa mais alta do mundo continua inteira até hoje — mas o lago desapareceu.",
                narration_script_35_45s=(
                    "A muralha de concreto de duzentos e sessenta metros resistiu a todo o impacto sem uma única rachadura. "
                    "A engenharia da barragem era perfeita. "
                    "O erro fatal foi a arrogância de achar que poderiam domar uma montanha inteira. "
                    "Hoje, a represa ergue-se vazia nos Alpes italianos, como uma cicatriz eterna do preço da ambição humana. "
                    "Inscreva-se na Via da Descoberta para mais mistérios da história."
                ),
                thumbnail_text="MONUMENTO VAZIO",
                caption_power_words=["INTEIRA", "SEM RACHADURA", "ARROGÂNCIA", "CICATRIZ", "VIA DA DESCOBERTA"],
                cta_to_long_video=bridge_suffix,
            ),
        ]

    @classmethod
    def craft_5_shorts_angles(
        cls,
        case_title: str,
        case_summary: str,
        long_video_id: Optional[str] = None
    ) -> List[ShortNarrativeAngle]:
        """Wrapper de compatibilidade retroativa que redireciona para a nova esteira de 4 ângulos."""
        return cls.craft_4_shorts_angles(case_title, case_summary, long_video_id)

    @classmethod
    def generate_optimized_description(
        cls,
        title: str,
        summary: str,
        video_format: str = "LONG_16_9",
        related_long_url: Optional[str] = None
    ) -> str:
        """
        Gera a descrição perfeita de SEO e retenção com o nome oficial do canal,
        chamadas de ação orgânicas e tags de alta conversão.
        """
        clean_title = cls.polish_title(title)
        lines: List[str] = []

        if video_format == "LONG_16_9":
            lines.append(f"📌 {clean_title}")
            lines.append("")
            lines.append(summary.strip())
            lines.append("")
            lines.append("──────────────────────────────────────────")
            lines.append("🔔 INSCREVA-SE NO CANAL:")
            lines.append(f"Faça parte da nossa comunidade investigativa e desvende os mistérios mais fascinantes da história, da ciência e dos arquivos desclassificados.")
            lines.append(f"Canal: {cls.CHANNEL_NAME} ({cls.CHANNEL_HANDLE})")
            lines.append(f"Produzido para o canal {cls.CHANNEL_NAME} via Dark Studio Platform.")
            lines.append("──────────────────────────────────────────")
            lines.append("CAPÍTULOS:")
            lines.append("00:00 - O Ponto de Tensão Inicial")
            lines.append("00:45 - Os Sinais que Ninguém Quis Ver")
            lines.append("01:30 - O Momento do Colapso")
            lines.append("02:15 - A Devastação e os Registros de 1963")
            lines.append("02:50 - O Que a História Escondeu")
            lines.append("")
            lines.append(f"#Historia #Misterios #Documentario #FatosReais #{cls.CHANNEL_NAME.replace(' ', '')}")
        else:
            lines.append(f"📌 {clean_title}")
            lines.append("")
            lines.append(summary.strip()[:200])
            if related_long_url:
                lines.append("")
                lines.append(f"▶ Assista ao documentário completo: {related_long_url}")
            lines.append("")
            lines.append(f"Canal: {cls.CHANNEL_NAME} ({cls.CHANNEL_HANDLE})")
            lines.append(f"Produzido para o canal {cls.CHANNEL_NAME} via Dark Studio Platform.")
            lines.append("")
            lines.append(f"#Shorts #Historia #Curiosidades #{cls.CHANNEL_NAME.replace(' ', '')}")

        return "\n".join(lines)
