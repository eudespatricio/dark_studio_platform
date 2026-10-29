"""
Social Strategy & Retention Architecture — Diretoria de Crescimento YouTube (16:9 & 9:16).

Define:
1. Frameworks de retenção de Vídeo Longo (16:9) com Hook de 15s (Zero Intro Lenta) e
   Open Loops a cada 90 segundos.
2. Frameworks de Shorts (9:16) com corte em pico *Most Replayed*, Loop Infinito (Seamless Loop)
   e Funil de Conversão para o Vídeo Longo via `Related Video`.
3. Personas detalhadas dos Top 3 Canais Dark (`Atlas Invisível`, `Código Oculto`, `Mente Soberana`).
4. Geradores de Prompts de Transcriação Cultural para o Gemini (proibindo tradução literal e
   adaptando referências, moedas e metáforas para o público alvo).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class HookRuleSet:
    """Regras inegociáveis para os primeiros 15 segundos de qualquer Vídeo Longo (16:9) ou Short (9:16)."""

    max_hook_duration_sec: int = 15
    first_frame_pattern_interrupt: str = (
        "Iniciar no meio da tensão ou com afirmação contraintuitiva nos primeiros 2.5 segundos. "
        "PROIBIDO usar 'Olá pessoal', 'Bem-vindos ao canal' ou vinhetas de logo."
    )
    thumbnail_title_validation_sec: int = 5
    open_loop_injection_sec: int = 12
    visual_pacing_cuts_first_15s: int = 6  # Mudança de estímulo visual a cada ~2.5s no Hook


@dataclass
class OpenLoopCadence:
    """Arquitetura de re-engajamento (Micro-Tension Loops) ao longo do vídeo 16:9."""

    interval_seconds: int = 90
    pattern_types: List[str] = field(
        default_factory=lambda: [
            "Falsa Resolução ('Tudo parecia resolvido, até que um documento vazado às 3h da manhã mudou tudo...')",
            "Pergunta Não Respondida ('Mas se o dinheiro não estava no banco, para onde foram os R$ 800 milhões?')",
            "Inversão de Perspectiva ('O que a mídia chamou de erro foi, na verdade, uma jogada calculada.')",
            "Contagem Regressiva ('Restavam apenas 18 minutos antes do servidor central travar.')",
        ]
    )
    mid_roll_cta_rule: str = (
        "Inserir CTA orgânico de inscrição somente após entregar o primeiro grande Payoff "
        "(entre o minuto 03:30 e 05:00), conectado à temática do canal, sem quebrar a música de fundo."
    )


@dataclass
class ShortsFunnelStrategy:
    """Estratégia de funil bidirecional: Shorts (9:16) -> Vídeo Longo (16:9)."""

    short_duration_sweet_spot_sec: tuple[int, int] = (38, 55)
    hook_window_sec: float = 1.8
    subtitle_style: str = (
        "Legendas dinâmicas palavra-por-palavra centralizadas na zona segura (safe zone), "
        "destacando verbos de ação e valores financeiros em amarelo/vermelho vibrante."
    )
    seamless_loop_technique: str = (
        "A última frase do Short deve terminar com um conector gramatical que se completa "
        "exatamente com a primeira frase do segundo 0.0 ('...e é exatamente por isso que -> [INÍCIO]')."
    )
    related_video_bridge: str = (
        "Nos últimos 4 segundos do Short, interromper a revelação principal no clímax e exibir "
        "seta animada apontando para o 'Vídeo Relacionado' nativo do YouTube Shorts player."
    )
    target_conversion_rate_pct: float = 5.0


@dataclass
class ChannelPersona:
    """Identidade narrativa, tonalidade e regras de transcriação de cada um dos Top 3 Canais."""

    channel_id: str
    channel_name: str
    niche_id: str
    archetype: str
    voice_id: str
    speaking_rate_wpm: int
    tone_keywords: List[str]
    forbidden_cliches: List[str]
    cultural_adaptation_rules: List[str]
    signature_sign_off: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SocialStrategyDirector:
    """
    Orquestrador da Estratégia de Retenção, Transcriação Cultural e Funil Multi-Formato.
    """

    def __init__(self) -> None:
        self.hook_rules = HookRuleSet()
        self.open_loop_cadence = OpenLoopCadence()
        self.shorts_funnel = ShortsFunnelStrategy()
        self.channel_personas: Dict[str, ChannelPersona] = self._build_top_3_personas()

    @staticmethod
    def _build_top_3_personas() -> Dict[str, ChannelPersona]:
        return {
            "geopolitics_economic_collapses": ChannelPersona(
                channel_id="ch_01_atlas_invisivel",
                channel_name="Atlas Invisível",
                niche_id="geopolitics_economic_collapses",
                archetype="Estrategista Geopolítico & Analista de Inteligência",
                voice_id="pt-BR-AntonioNeural",
                speaking_rate_wpm=155,
                tone_keywords=[
                    "Analítico",
                    "Cinematográfico",
                    "Autoritativo",
                    "Investigativo",
                    "Sóbrio",
                ],
                forbidden_cliches=[
                    "Oi galera, tudo bem?",
                    "Deixe seu like e ative o sininho antes de começar",
                    "Neste vídeo vamos falar sobre",
                ],
                cultural_adaptation_rules=[
                    "Converter valores monetários para Reais (R$) ou manter Dólares (US$) com comparativo direto ao PIB brasileiro ou obras conhecidas no Brasil.",
                    "Conectar impactos de cadeias globais (petróleo, fertilizantes, semicondutores) ao bolso e cotidiano do espectador brasileiro.",
                    "Manter imparcialidade documental rigorosa com dados verificáveis.",
                ],
                signature_sign_off=(
                    "No tabuleiro global, nenhum movimento é por acaso. "
                    "Inscreva-se no Atlas Invisível para enxergar o que os mapas oficiais escondem."
                ),
            ),
            "cyber_heists_ai_investigative": ChannelPersona(
                channel_id="ch_02_codigo_oculto",
                channel_name="Código Oculto",
                niche_id="cyber_heists_ai_investigative",
                archetype="Investigador Forense Digital & Narrador Cyber-Noir",
                voice_id="pt-BR-NicolauNeural",
                speaking_rate_wpm=162,
                tone_keywords=[
                    "Tenso",
                    "Imersivo",
                    "Misterioso",
                    "Ágil",
                    "Cirúrgico",
                ],
                forbidden_cliches=[
                    "Fala pessoal do canal",
                    "Como vocês já sabem",
                    "Sem mais delongas",
                ],
                cultural_adaptation_rules=[
                    "Explicar conceitos técnicos (Zero-Day, Phishing, Smart Contracts, Deepfake) usando analogias visuais de assaltos a bancos físicos (estilo La Casa de Papel / Mr. Robot).",
                    "Substituir referências bancárias americanas obscuras por equivalentes compreensíveis (PIX, Banco Central, grandes corretoras).",
                    "Construir a narrativa como uma contagem regressiva minuto a minuto.",
                ],
                signature_sign_off=(
                    "Na era digital, a fechadura mais frágil continua sendo a mente humana. "
                    "Você está no Código Oculto."
                ),
            ),
            "dark_psychology_power_dynamics": ChannelPersona(
                channel_id="ch_03_mente_soberana",
                channel_name="Mente Soberana",
                niche_id="dark_psychology_power_dynamics",
                archetype="Mentor Maquiavélico-Estoico & Filósofo do Comportamento",
                voice_id="pt-BR-DonatoNeural",
                speaking_rate_wpm=142,
                tone_keywords=[
                    "Hipnótico",
                    "Filosófico",
                    "Provocativo",
                    "Estratégico",
                    "Íntimo",
                ],
                forbidden_cliches=[
                    "Dica rápida de hoje",
                    "Compartilhe com seus amigos no WhatsApp",
                    "Espero que tenham gostado",
                ],
                cultural_adaptation_rules=[
                    "Usar a segunda pessoa do singular ('Você já percebeu como...') para criar intimidade psicológica imediata.",
                    "Ancorar leis psicológicas (Robert Greene, Schopenhauer, Jung, Cialdini) em situações reais de ambiente corporativo, negociação e relacionamentos modernos.",
                    "Posicionar o conhecimento como 'defesa mental e soberania pessoal', nunca como incentivo antiético.",
                ],
                signature_sign_off=(
                    "Quem não compreende as regras invisíveis do jogo está condenado a ser peça. "
                    "Assuma o controle no Mente Soberana."
                ),
            ),
        }

    def get_persona(self, niche_id: str) -> ChannelPersona:
        """Retorna a persona configurada para o nicho ou a persona documental padrão."""
        return self.channel_personas.get(
            niche_id,
            self.channel_personas["geopolitics_economic_collapses"],
        )

    def build_longform_transcreation_prompt(
        self,
        niche_id: str,
        source_title: str,
        source_transcript: str,
        source_language: str,
        target_duration_minutes: int = 14,
    ) -> str:
        """
        Gera o Prompt Mestre para o Gemini realizar a Transcriação Cultural de alta retenção
        para Vídeo Longo (16:9), aplicando Hook de 15s, Open Loops a cada 90s e B-Roll Cues.
        """
        persona = self.get_persona(niche_id)
        target_word_count = target_duration_minutes * persona.speaking_rate_wpm

        cultural_rules_text = "\n".join(
            f"  - {rule}" for rule in persona.cultural_adaptation_rules
        )
        forbidden_text = ", ".join(f'"{c}"' for c in persona.forbidden_cliches)

        return f"""# ROLE & DIRETRIZ EXECUTIVA — TRANSCRIAÇÃO CULTURAL DE ALTA RETENÇÃO (16:9)
Você é o Roteirista-Chefe e Estrategista de Retenção do canal Dark "{persona.channel_name}" ({persona.archetype}).
Sua missão NÃO é traduzir literalmente o roteiro original em {source_language}, mas executar uma **TRANSCRIAÇÃO CULTURAL COMPLETA** para Português do Brasil (pt-BR), reestruturando a narrativa para atingir >55% de retenção média (AVD).

## DADOS DA FONTE VALIDADA (OUTLIER >= 3.0x)
- Título Original ({source_language}): {source_title}
- Nicho Estratégico: {niche_id}
- Duração Alvo: ~{target_duration_minutes} minutos (~{target_word_count} palavras a {persona.speaking_rate_wpm} WPM)
- Tonalidade da Voz ({persona.voice_id}): {", ".join(persona.tone_keywords)}

## REGRAS DE ENGENHARIA DE RETENÇÃO (OBRIGATÓRIAS)
1. **HOOK IMPLACÁVEL NOS PRIMEIROS 15 SEGUNDOS (00:00 - 00:15)**:
   - {self.hook_rules.first_frame_pattern_interrupt}
   - Valide a promessa do título/thumbnail nos primeiros 5 segundos.
   - Plante uma pergunta central intrigante (Open Loop Principal) aos 12 segundos.
   - Frases estritamente proibidas: {forbidden_text}.

2. **ARQUITETURA DE OPEN LOOPS A CADA 90 SEGUNDOS**:
   - A cada ~220 palavras (~90 segundos de locução), antes de fechar um raciocínio, abra um novo ciclo de curiosidade (Micro-Cliffhanger).
   - Utilize conectores de tensão: *"Mas esse era apenas o erro visível..."*, *"O que ninguém na sala de reuniões sabia era que..."*.

3. **ADAPTAÇÃO CULTURAL PROFUNDA (PT-BR)**:
{cultural_rules_text}

4. **CTA ORGÂNICO E ENCERRAMENTO ABRUPTO (ANTI-QUEDA FINAL)**:
   - Insira 1 único CTA orgânico após o primeiro grande Payoff (~04:00).
   - Nos últimos 20 segundos do vídeo, NÃO diga "Então em resumo" ou "Por hoje é só". Entregue a revelação final de impacto seguida de: "{persona.signature_sign_off}".

5. **MARCAÇÕES TÉCNICAS PARA O MOTOR DE MÍDIA (B-ROLL & SFX)**:
   - A cada bloco de 2 a 3 frases, insira tags `[VISUAL_PROMPT: descrição detalhada em inglês para geração/busca de cena 16:9]` e `[SFX: whoosh/low_boom/tension_riser]`.

## TRANSCRIÇÃO DE REFERÊNCIA ({source_language}):
\"\"\"
{source_transcript}
\"\"\"

Retorne o roteiro final estruturado em blocos temporais (00:00-00:15 Hook, Atos Narrativos com Open Loops a cada 90s, Clímax e Fechamento).
"""

    def build_shorts_extraction_prompt(
        self,
        niche_id: str,
        long_video_title_ptbr: str,
        heatmap_peak_context: str,
        target_duration_sec: int = 48,
    ) -> str:
        """
        Gera o Prompt para criar o roteiro de YouTube Shorts (9:16) derivado do pico
        *Most Replayed* do vídeo longo, com Seamless Loop e ponte para `Related Video`.
        """
        persona = self.get_persona(niche_id)
        return f"""# ROLE & DIRETRIZ — ROTEIRO DE SHORTS (9:16) COM LOOP INFINITO E FUNIL PARA VÍDEO LONGO
Você é o Especialista em Viralização Vertical do canal "{persona.channel_name}".
Extraia um roteiro de Short de exatamente {target_duration_sec} segundos baseado no pico *Most Replayed* do nosso vídeo longo: "{long_video_title_ptbr}".

## CONTEXTO DO PICO DE RETENÇÃO (MOST REPLAYED):
{heatmap_peak_context}

## ESTRUTURA CIRÚRGICA DO SHORT (9:16):
1. **SEGUNDOS 0.0 a 2.0 (VISUAL & AUDIO HOOK)**:
   - Comece com uma afirmação chocante de no máximo 8 palavras que complete gramaticalmente a última frase do vídeo (Seamless Loop).
2. **SEGUNDOS 2.0 a {target_duration_sec - 6}.0 (ESCALADA DE TENSÃO)**:
   - Frases curtas, sem pausas respiratórias longas, corte visual a cada 1.8s.
3. **ÚLTIMOS 6 SEGUNDOS (CLIFFHANGER + PONTE PARA VÍDEO RELACIONADO)**:
   - Interrompa a história exatamente antes da consequência final.
   - Insira o CTA de Funil: *"Mas o que aconteceu nas 24 horas seguintes chocou os investigadores. Toque no vídeo relacionado aqui embaixo para assistir ao documentário completo..."*
   - Termine com um conector aberto que se encaixe perfeitamente na primeira palavra do segundo 0.0.
"""

    def build_seo_packaging_prompt(
        self,
        niche_id: str,
        source_title: str,
        outlier_score: float,
    ) -> str:
        """
        Gera o Prompt para empacotamento de CTR (3 variações de Título A/B/C + Prompt de Thumbnail).
        """
        persona = self.get_persona(niche_id)
        return f"""# EMPACOTAMENTO DE ALTO CTR (TÍTULOS A/B/C + THUMBNAIL 16:9)
Canal: {persona.channel_name} | Nicho: {niche_id}
Vídeo Outlier Base ({outlier_score}x a média do canal): "{source_title}"

Gere:
1. **3 Títulos em PT-BR (máx. 58 caracteres)** focados em:
   - Opção A (Curiosidade Extrema / Gap de Informação)
   - Opção B (Ameaça / Consequência / Escala Bilionária)
   - Opção C (Paradoxo Contraintuitivo)
2. **Conceito de Thumbnail (Regra dos 3 Elementos)**:
   - Fundo (Contexto escuro contrastante)
   - Elemento Central em Primeiro Plano (Foco ocular imediato)
   - Texto de Apoio na Thumbnail (2 a 3 palavras em caixa alta que NÃO repetem o título)
3. **Descrição SEO + Tags + Capítulo Timestamps (00:00)**.
"""
