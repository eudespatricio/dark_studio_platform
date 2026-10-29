"""
AUTONOMOUS AGENTS DISPATCHER & DAY ROLLOVER (TODAY: 2026-10-18)
Executa a virada de data imediata, gera e publica os slots de hoje
para ambos os canais através do Conselho de Agentes:
1. Canal #1 (A Via da Descoberta) — Tema: "O Desastre de Chernobyl: O Teste de Segurança que Destruiu o Reator 4"
2. Canal #2 (Finanças Quânticas) — Tema: "O Colapso do LTCM (1998): Quando Prêmios Nobel Quebraram Wall Street"
3. Preenche o Buffer de Conteúdo e dispara publicação imediata da janela do dia.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("autonomous_agents")

CH1_ID = "UC8RJWr3b2pKtnU1wOhV_bDQ"
CH2_ID = "UCE6Ch6nhxI81Z6ILQIw23_Q"
CH3_ID = "UCIjEnT4adPYVyi0UlrCITBA"
VOICE_CH1 = "pNInz6obpgDQGcFmaJgB"
VOICE_CH2 = "ErXwobaYiN019PkySvjV"
VOICE_CH3 = "VR6AewLTigWG4xSOukaG"

CH1_STATE = BASE_DIR / "workspace/automation/daily_cadence_state.json"
CH2_STATE = BASE_DIR / "workspace/automation/quant_cadence_state.json"
CH3_STATE = BASE_DIR / "workspace/automation/biohack_cadence_state.json"
AUDIO_DIR = BASE_DIR / "workspace/audio"
RENDERS_DIR = BASE_DIR / "workspace/renders"
THUMB_DIR = BASE_DIR / "workspace/thumbnails"
RAW_THUMBS_DIR = THUMB_DIR / "raw_sources"
SCENES_DIR = BASE_DIR / "workspace/scenes"
MUSIC_DIR = BASE_DIR / "assets/music"

TODAY_STR = datetime.now().strftime("%Y-%m-%d")


# ==============================================================================
# 1. GRADE DO DIA (2026-10-18) COM ROTEIROS DE ALTO CTR & CONSELHO DE AGENTES
# ==============================================================================
CH1_TODAY_SLOTS = [
    {
        "slot_id": "slot_short_01",
        "time_brt": "13:15",
        "video_format": "SHORT_9_16",
        "title": "CHERNOBYL: O Botão AZ-5 que Desencadeou a Explosão #Shorts",
        "script_hook": "Às vinte e três horas e quarenta do dia 25 de abril de 1986, um engenheiro apertou o botão de emergência AZ-5 esperando desligar o reator quatro de Chernobyl.",
        "narration_text": (
            "Às vinte e três horas e quarenta de vinte e cinco de abril de mil novecentos e oitenta e seis, "
            "um operador apertou o botão de emergência AZ-5 para desligar o reator quatro de Chernobyl. "
            "O que ninguém na sala de controle sabia era que as pontas das barras de controle eram feitas de grafite, "
            "que ao invés de frear a reação, aceleraram a fissão nuclear instantaneamente. "
            "Em quatro segundos, a potência subiu cem vezes o limite do reator, explodindo a tampa de mil toneladas de concreto. "
            "Inscreva-se no canal A Via da Descoberta para investigações completas."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
    },
    {
        "slot_id": "slot_long_01",
        "time_brt": "13:30",
        "video_format": "LONG_16_9",
        "title": "O Erro de Projeto que Destruiu Chernobyl: O Segredo do Reator 4 [DOCUMENTÁRIO]",
        "script_hook": "O teste de segurança que deveria comprovar a autonomia da usina transformou-se na maior catástrofe nuclear da civilização.",
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
    },
    {
        "slot_id": "slot_short_02",
        "time_brt": "15:30",
        "video_format": "SHORT_9_16",
        "title": "O GRAFITE SECRETO: A Falha Oculta da Engenharia Soviética #Shorts",
        "script_hook": "Por que o manual de instrução do reator RBMK escondia o defeito mais letal do projeto?",
        "narration_text": (
            "Por que o governo soviético classificou como segredo de estado o fato de que as barras de controle do reator RBMK tinham pontas de grafite? "
            "Durante anos antes de Chernobyl, reatores em Leningrado apresentaram picos de potência durante o desligamento de emergência, "
            "mas os relatórios foram censurados pela KGB para proteger a reputação da tecnologia nacional. "
            "O preço do segredo foi cobrado em vidas humanas na Ucrânia. "
            "Assista ao documentário completo no canal A Via da Descoberta."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
    },
    {
        "slot_id": "slot_short_03",
        "time_brt": "17:30",
        "video_format": "SHORT_9_16",
        "title": "A PÁ DE DOIS MINUTOS: Os Biorrobôs no Teto de Chernobyl #Shorts",
        "script_hook": "Quando robôs eletrônicos da Alemanha pifavam devido à radiação extrema, homens foram convocados.",
        "narration_text": (
            "Quando robôs eletrônicos modernos trazidos da Alemanha queimavam seus circuitos em segundos devido aos níveis brutais de radiação, "
            "o comando soviético tomou uma decisão desesperada: enviar soldados humanos com coletes de chumbo improvisados, "
            "conhecidos como biorrobôs. Cada homem tinha exatamente noventa segundos para correr até o teto, "
            "jogar uma pá de grafite radioativo dentro da cratera e voltar. "
            "Conheça a história real no canal A Via da Descoberta."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
    },
    {
        "slot_id": "slot_short_04",
        "time_brt": "19:45",
        "video_format": "SHORT_9_16",
        "title": "A CIDADE FANTASMA: 48 Horas para Evacuar Pripyat #Shorts",
        "script_hook": "Cinquenta mil pessoas viveram suas rotinas normais enquanto a radiação invisível cobria cada centímetro da cidade.",
        "narration_text": (
            "No dia seguinte à explosão de Chernobyl, cinquenta mil moradores de Pripyat continuavam nas ruas, passeando em parques e assistindo casamentos. "
            "Somente trinta e seis horas depois vieram os alto-falantes militares avisando que todos deveriam deixar seus lares em duas horas "
            "levando apenas documentos, pois voltariam em três dias. Ninguém nunca mais voltou. "
            "Inscreva-se no canal A Via da Descoberta."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
    },
    {
        "slot_id": "slot_short_05",
        "time_brt": "21:30",
        "video_format": "SHORT_9_16",
        "title": "O PÉ DE ELEFANTE: A Massa Mais Perigosa do Planeta Terra #Shorts",
        "script_hook": "Nas ruínas do subsolo de Chernobyl, formou-se um mineral radioativo inédito chamado corium.",
        "narration_text": (
            "Abaixo do reator quatro de Chernobyl, o combustível nuclear derretido misturou-se com areia e concreto, "
            "formando uma massa negra de centenas de toneladas apelidada de Pé de Elefante. "
            "Nos primeiros meses, ficar ao lado dessa formação por apenas trezentos segundos causava morte certa por envenenamento radioativo. "
            "Até hoje ela permanece emitindo calor nas profundezas da usina. "
            "Inscreva-se no canal A Via da Descoberta."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
    },
]

CH2_TODAY_SLOTS = [
    {
        "slot_id": "slot_quant_short_01",
        "time_brt": "13:20",
        "video_format": "SHORT_9_16",
        "title": "LTCM: Quando 2 Prêmios Nobel Quebraram Wall Street em 1998 #Shorts",
        "script_hook": "Os dois maiores economistas do mundo inventaram a fórmula de derivativos mais famosa da história e fundaram um fundo com alavancagem de 100 para 1.",
        "narration_text": (
            "Em 1997, Robert Merton e Myron Scholes ganharam o Prêmio Nobel de Economia pela famosa equação de Black-Scholes. "
            "Eles eram sócios do fundo hedge Long-Term Capital Management, que operava com alavancagem colossal de cem para um, "
            "acumulando mais de cem bilhões de dólares em apostas no mercado de títulos. "
            "Mas em agosto de 1998, a Rússia decretou calote em sua dívida soberana e a matemática perfeita dos gênios ruiu em seis semanas, "
            "forçando o Federal Reserve a organizar um resgate histórico para salvar o sistema financeiro mundial. "
            "Inscreva-se no canal Finanças Quânticas para entender a física dos mercados."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
    },
    {
        "slot_id": "slot_quant_long_01",
        "time_brt": "13:45",
        "video_format": "LONG_16_9",
        "title": "O Colapso do LTCM (1998): Quando a Matemática Quase Destruiu o Capitalismo [DOCUMENTÁRIO]",
        "script_hook": "A ascensão e queda do fundo hedge mais sofisticado da história humana.",
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
    },
    {
        "slot_id": "slot_quant_short_02",
        "time_brt": "15:30",
        "video_format": "SHORT_9_16",
        "title": "ALAVANCAGEM 100:1: O Erro Fatal que Quase Explodiu o FED #Shorts",
        "script_hook": "Por que modelos matemáticos perfeitos quebram na vida real?",
        "narration_text": (
            "Os modelos quantitativos do LTCM previam que o risco de perder todo o capital era de uma chance em cem mil anos. "
            "O problema? Eles assumiram uma distribuição normal gaussiana, ignorando as caudas longas do comportamento humano em pânico. "
            "Com apenas quatro bilhões de dólares em capital próprio, o fundo mantinha posições de um trilhão em derivativos. "
            "Quando a crise estourou, a liquidez evaporou e a alavancagem virou uma guilhotina matemática. "
            "Inscreva-se no canal Finanças Quânticas."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
    },
    {
        "slot_id": "slot_quant_short_03",
        "time_brt": "17:30",
        "video_format": "SHORT_9_16",
        "title": "A REUNIÃO SECRETA: O Resgate de US$ 3.6 Bilhões no Banco Central #Shorts",
        "script_hook": "Em vinte e três de setembro de 1998, os quatorze maiores bancos de Wall Street reuniram-se a portas fechadas.",
        "narration_text": (
            "Em vinte e três de setembro de mil novecentos e noventa e oito, o presidente do Federal Reserve de Nova York trancou os chefes "
            "dos quatorze maiores bancos de investimento dos Estados Unidos em uma sala e disse: "
            "se o LTCM liquidar suas posições a mercado amanhã, o sistema bancário ocidental inteiro quebra. "
            "Em poucas horas, os bancos concordaram em colocar três vírgula seis bilhões de dólares para assumir o controle do fundo. "
            "Conheça a verdade dos bastidores no canal Finanças Quânticas."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
    },
    {
        "slot_id": "slot_quant_short_04",
        "time_brt": "19:45",
        "video_format": "SHORT_9_16",
        "title": "ED THORP: O Homem que Derrotou a Roleta e Wall Street com Matemática #Shorts",
        "script_hook": "Antes de Jim Simons, um professor de matemática do MIT inventou o primeiro computador vestível e o primeiro hedge fund quantitativo.",
        "narration_text": (
            "Edward Thorp provou na década de sessenta que os cassinos de Las Vegas podiam ser batidos através da contagem de cartas no Blackjack "
            "e da física computacional na roleta. Quando os cassinos o baniram, ele levou seus modelos estocásticos para a Bolsa de Nova York, "
            "criando a arbitragem estatística de warrants e operando quase trinta anos sem registrar um único trimestre de prejuízo. "
            "Inscreva-se no canal Finanças Quânticas."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
    },
    {
        "slot_id": "slot_quant_short_05",
        "time_brt": "21:30",
        "video_format": "SHORT_9_16",
        "title": "O CISNE NEGRO: Por Que a Curva Normal Engana 99% dos Traders #Shorts",
        "script_hook": "Os livros didáticos ensinam que retornos financeiros seguem a curva de sino de Gauss.",
        "narration_text": (
            "Se os mercados financeiros seguissem a distribuição normal gaussiana, eventos como o Crash de 1987, o colapso de 2008 e o Flash Crash "
            "só aconteceriam uma vez a cada idade do universo. Na realidade, os mercados têm caudas gordas e assimetria selvagem. "
            "Grandes gestores quantitativos lucram justamente calibrando seus algoritmos para sobreviver e faturar onde os modelos comuns quebram. "
            "Inscreva-se no canal Finanças Quânticas para aprender matemática avançada de mercado."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
    },
]


def rollover_and_activate_today():
    """Ativa a grade de hoje consumindo a FILA DE PAUTAS (descobertas pelo radar de outliers e roteirizadas).
    Sem pauta pronta no canal => grade vazia (nunca repete a pauta de ontem)."""
    today_date = datetime.now().strftime("%Y-%m-%d")
    logger.info("ATIVANDO GRADE DE HOJE: %s", today_date)

    from backend.automation.daily_cadence import daily_cadence_mgr
    from backend.automation.quant_daily_cadence import quant_cadence_mgr
    from backend.automation.biohack_daily_cadence import biohack_cadence_mgr
    from backend.discovery.topic_intake import apply_pauta_to_slots, consume_next_pauta

    plan = [
        (1, daily_cadence_mgr, CH1_STATE, "A Via da Descoberta", "@AViadaDescoberta", CH1_ID),
        (2, quant_cadence_mgr, CH2_STATE, "Finanças Quânticas", "@FinancasQuanticasOficial", CH2_ID),
        (3, biohack_cadence_mgr, CH3_STATE, "Bio Hack Longevidade", "@BioHackLongevidade", CH3_ID),
    ]
    for ch_num, mgr, state_path, name, handle, ch_id in plan:
        pauta = consume_next_pauta(ch_num)
        if pauta:
            slots = apply_pauta_to_slots(mgr._generate_today_slots(), pauta)
            topic = pauta["package"].get("topic_title_pt") or pauta["source"]["title_original"]
            logger.info("Canal #%d: pauta '%s' (outlier %sx) ativada com %d slots.", ch_num, topic[:60], pauta["source"]["outlier_score"], len(slots))
        else:
            slots, topic = [], "SEM PAUTA PRONTA (fila vazia ou em revisão)"
            logger.warning("Canal #%d: fila de pautas vazia; grade de hoje não terá conteúdo (sem repetir pauta antiga).", ch_num)
        state = {
            "is_active": True,
            "target_channel": {"name": name, "handle": handle, "id": ch_id},
            "schedule_date": today_date,
            "current_topic": topic,
            "today_slots": slots,
            "last_cycle_timestamp": datetime.now(timezone.utc).isoformat(),
        }
        state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def execute_now():
    """Inicializa/atualiza a grade do dia (2026-10-20) para os 3 canais sem forçar disparo fora do horário."""
    rollover_and_activate_today()
    from backend.automation.biohack_daily_cadence import biohack_cadence_mgr
    biohack_cadence_mgr._ensure_sync_file()
    logger.info("Grade de hoje (%s) ativada para os Canais #1, #2 e #3!", datetime.now().strftime("%Y-%m-%d"))


if __name__ == "__main__":
    execute_now()
