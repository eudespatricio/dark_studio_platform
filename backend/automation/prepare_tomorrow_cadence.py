"""
Cadence Preparator for Tomorrow (2026-10-20) — Dark Studio AI Platform
Prepara a grade inédita de 7 slots diários (6 Shorts + 1 Longo Documental Completo) por canal para 20/10/2026:
1. 07:15 BRT — Pico Matinal / Deslocamento de Ônibus & Metrô
2. 11:15 BRT — Abertura do Almoço Brasileiro (Início da Janela das 11h)
3. 13:45 BRT — Pós-Almoço / Café & Retorno ao Trabalho
4. 16:00 BRT — Aquecimento Tarde / Retorno do Trabalho / Fechamento B3
5. 17:30 BRT — Documentário Completo 16:9 (Indexação 2h Pré-Horário Nobre)
6. 19:45 BRT — Feeder Horário Nobre (T+2h15m -> Documentário 16:9)
7. 21:45 BRT — Fechamento Noturno / Mobile no Leito
Respeita estritamente o intervalo de proteção de cadência (>= 90 minutos) e zero colisão com Bhopal/Knight Capital (19/10).
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("prepare_tomorrow_cadence")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
CH1_STATE = BASE_DIR / "workspace/automation/daily_cadence_state.json"
CH2_STATE = BASE_DIR / "workspace/automation/quant_cadence_state.json"
CH3_STATE = BASE_DIR / "workspace/automation/biohack_cadence_state.json"

TOMORROW_STR = "2026-10-20"
CH1_ID = "UC8RJWr3b2pKtnU1wOhV_bDQ"
CH2_ID = "UCE6Ch6nhxI81Z6ILQIw23_Q"
CH3_ID = "UCIjEnT4adPYVyi0UlrCITBA"

# ==============================================================================
# CANAL 1: A VIA DA DESCOBERTA — A ERUPÇÃO LÍMNICA DO LAGO NYOS (1986)
# Calibrado com a Heurística Outlier: Números Superlativos Concretos + Perigo Físico
# ==============================================================================
CH1_TOMORROW_SLOTS = [
    {
        "slot_id": "slot_short_01",
        "time_brt": "07:15",
        "video_format": "SHORT_9_16",
        "title": "1.746 VIDAS EM 15 MINUTOS: O Lago que Sufocou um Vale Inteiro #Shorts",
        "script_hook": "Na noite de 21 de agosto de 1986, um lago vulcânico liberou 1,6 milhão de toneladas de gás invisível.",
        "narration_text": (
            "Na noite de vinte e um de agosto de mil novecentos e oitenta e seis, o calmo Lago Nyos, em Camarões, "
            "sofreu um fenômeno geológico raro chamado erupção límnica. Um milhão e seiscentas mil toneladas de dióxido de carbono "
            "acumuladas sob pressão no fundo da cratera explodiram para a superfície a cem quilômetros por hora. "
            "Por ser mais densa que o ar, uma nuvem invisível de cinquenta metros de altura desceu a montanha em silêncio absoluto, "
            "apagando o oxigênio de três vilarejos e tirando mil setecentas e quarenta e seis vidas em quinze minutos. "
            "Inscreva-se no canal A Via da Descoberta para investigações científicas reais."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
        "status_label": "PROGRAMADO (DESLOCAMENTO MATINAL 07:15)"
    },
    {
        "slot_id": "slot_short_02",
        "time_brt": "11:15",
        "video_format": "SHORT_9_16",
        "title": "208 METROS DE PROFUNDIDADE: A Bomba Líquida Sob o Lago Nyos #Shorts",
        "script_hook": "A duzentos e oito metros de profundidade, a pressão da água transformou o fundo do lago em uma câmara de magma pressurizada.",
        "narration_text": (
            "Como um lago comum pôde se transformar em uma arma química natural? "
            "O Lago Nyos repousa exatamente sobre uma câmara de magma ativo a duzentos e oito metros de profundidade. "
            "Durante séculos, milhões de toneladas de gás vulcânico infiltraram-se pela rocha porosa e ficaram presas no fundo "
            "pelo peso colossal de duzentos milhões de metros cúbicos de água fria. "
            "Bastou um único deslizamento de terra na encosta para destampar essa garrafa de champanhe geológica. "
            "Acompanhe o documentário completo no canal A Via da Descoberta."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
        "status_label": "PROGRAMADO (ABERTURA ALMOÇO 11:15)"
    },
    {
        "slot_id": "slot_short_03",
        "time_brt": "13:45",
        "video_format": "SHORT_9_16",
        "title": "ONDA DE 100 METROS: O Tsunami Vertical Dentro de uma Cratera #Shorts",
        "script_hook": "Quando a bolha de gás subiu do fundo do Lago Nyos, ela levantou uma coluna de água de cem metros de altura.",
        "narration_text": (
            "Quando os geólogos chegaram à cratera do Lago Nyos dois dias após a tragédia, encontraram as árvores arrancadas "
            "nos paredões de rocha a cem metros acima do nível da água. "
            "A descompressão súbita de trezentos milhões de metros cúbicos de gás gerou um gêiser supersônico que esvaziou "
            "um metro inteiro do nível do lago em segundos, transformando a água cristalina em um vermelho ferrugem profundo "
            "ao trazer ferro oxidado das profundezas. "
            "Inscreva-se no canal A Via da Descoberta e assista à investigação completa."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
        "status_label": "PROGRAMADO (PÓS-ALMOÇO 13:45)"
    },
    {
        "slot_id": "slot_short_04",
        "time_brt": "16:00",
        "video_format": "SHORT_9_16",
        "title": "NUVEM DE 50 METROS: Por Que o Fogo Apagou Antes do Desastre #Shorts",
        "script_hook": "As lamparinas de querosene de toda a cidade apagaram no mesmo segundo sem que houvesse vento.",
        "narration_text": (
            "O primeiro sinal de que algo terrível descia a montanha de Nyos não foi um estrondo, mas o apagar simultâneo "
            "de todas as fogueiras e lamparinas a vinte e cinco quilômetros de distância. "
            "A parede invisível de dióxido de carbono tinha cinquenta metros de espessura e uma vez e meia a densidade do ar atmosférico. "
            "Ela empurrou todo o oxigênio respirável para cima, fazendo motores de carros pararem na estrada em questão de segundos. "
            "Conheça os fatos científicos no canal A Via da Descoberta."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
        "status_label": "PROGRAMADO (TARDE 16:00)"
    },
    {
        "slot_id": "slot_long_01",
        "time_brt": "17:30",
        "video_format": "LONG_16_9",
        "title": "1,6 Milhão de Toneladas de Gás: O Mistério Físico do Lago Nyos (1986) [DOCUMENTÁRIO]",
        "script_hook": "A investigação científica de como um lago vulcânico a 208 metros de profundidade liberou uma nuvem invisível de 50 metros de altura.",
        "narration_text": (
            "Na noite de vinte e um de agosto de mil novecentos e oitenta e seis, um vale inteiro no noroeste de Camarões "
            "foi atingido por uma das anomalias físicas mais extremas já registradas pela ciência moderna. "
            "Sem terremoto devastador, sem lava vulcânica e sem explosão de fogo, mil setecentas e quarenta e seis pessoas "
            "e mais de três mil e quinhentos animais perderam a vida em menos de quinze minutos em um raio de vinte e cinco quilômetros. "
            "Quando as primeiras equipes de cientistas e médicos chegaram aos vilarejos de Nyos, Cha e Subum, "
            "encontraram casas intactas, panelas ainda sobre os fogões e nenhuma marca de destruição mecânica. "
            "O que havia acontecido naquela madrugada desafiava tudo o que se conhecia sobre vulcanologia tradicional. "
            "A resposta estava oculta a duzentos e oito metros de profundidade, no fundo do Lago Nyos. "
            "Diferente dos lagos de regiões temperadas, onde as águas frias do inverno afundam e misturam as camadas inferiores, "
            "o Lago Nyos fica nos trópicos e possui uma estratificação térmica permanente. "
            "Abaixo dele, a poucos quilômetros na crosta terrestre, existe uma câmara de magma ativo que libera continuamente "
            "dióxido de carbono puro através de fissuras nas rochas. "
            "Durante centenas de anos, esse gás subiu até o fundo do lago e dissolveu-se na água gelada sob uma pressão de vinte atmosferas. "
            "Cada litro de água nas profundezas continha cinco litros de gás comprimido, acumulando um milhão e seiscentas mil toneladas "
            "de dióxido de carbono prontas para expandir. "
            "Às vinte e uma horas daquela noite, um deslizamento de rochas na parede da cratera empurrou a água profunda para cima. "
            "Assim que essa massa líquida subiu para zonas de menor pressão, o gás entrou em ebulição explosiva em reação em cadeia. "
            "Uma coluna supersônica de água e gás de cem metros de altura rasgou a superfície, varrendo a vegetação das encostas "
            "e trazendo ferro dissolvido que tingiu o lago de vermelho. "
            "Imediatamente, trezentos milhões de metros cúbicos de dióxido de carbono formaram um rio invisível de cinquenta metros de altura. "
            "Por ser cinquenta por cento mais pesado que o ar que respiramos, esse rio gasoso não subiu para o céu: "
            "ele escorreu pelos vales a cinquenta quilômetros por hora, deslocando o oxigênio do solo. "
            "As poucas pessoas que sobreviveram estavam em colinas elevadas acima da faixa de cinquenta metros da nuvem. "
            "Para impedir que a tragédia se repetisse, a partir de dois mil e um, engenheiros franceses e camaroneses instalaram "
            "tubos gigantes de polietileno cravados a duzentos metros de profundidade, criando chaminés permanentes de degaseificação "
            "que hoje aliviam a pressão do fundo do Lago Nyos em forma de fontes artificiais contínuas. "
            "Inscreva-se no canal A Via da Descoberta e ative as notificações para nossas próximas investigações científicas."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
        "status_label": "PROGRAMADO (DOCUMENTÁRIO NOBRE 16:9)"
    },
    {
        "slot_id": "slot_short_05",
        "time_brt": "19:45",
        "video_format": "SHORT_9_16",
        "title": "O TUBO DE 203 METROS: Como Engenheiros Desarmaram o Lago Nyos #Shorts",
        "script_hook": "Para evitar uma nova explosão de gás, engenheiros cravaram tubos gigantes no fundo da cratera.",
        "narration_text": (
            "Após a catástrofe de mil novecentos e oitenta e seis, medições revelaram que o Lago Nyos estava recarregando "
            "milhões de toneladas de gás vulcânico no fundo da cratera. "
            "Em dois mil e um, engenheiros instalaram tubos verticais de duzentos e três metros de comprimento ligando o fundo à superfície. "
            "Uma bomba puxou os primeiros metros de água saturada e a própria pressão do gás criou um gêiser autossustentável de cinquenta metros "
            "que desarma o lago lentamente todos os dias. "
            "Assista ao documentário completo no canal A Via da Descoberta."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
        "status_label": "PROGRAMADO (FEEDER NOITE 19:45)"
    },
    {
        "slot_id": "slot_short_06",
        "time_brt": "21:45",
        "video_format": "SHORT_9_16",
        "title": "LAGO KIVU: A Bomba de 300 Bilhões de Metros Cúbicos de Gás #Shorts",
        "script_hook": "Existe um lago na África duas mil vezes maior que o Lago Nyos que guarda 300 bilhões de metros cúbicos de gás.",
        "narration_text": (
            "Se o Lago Nyos assustou a comunidade científica, o Lago Kivu, na fronteira entre Ruanda e o Congo, tira o sono dos geofísicos. "
            "Ele é duas mil vezes maior e esconde nas suas profundezas trezentos bilhões de metros cúbicos de dióxido de carbono "
            "misturados com sessenta bilhões de metros cúbicos de gás metano inflamável. "
            "Hoje, usinas flutuantes extraem esse metano do fundo do lago para gerar eletricidade e reduzir o risco para dois milhões de moradores. "
            "Inscreva-se no canal A Via da Descoberta."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
        "status_label": "PROGRAMADO (LATE NIGHT 21:45)"
    },
]

# ==============================================================================
# CANAL 2: FINANÇAS QUÂNTICAS — EDWARD THORP: O PAI DOS QUANTS (MIT -> WALL ST)
# Calibrado com a Heurística Outlier: "A Jornada do Gênio Contra o Sistema" + Cifras Reais
# ==============================================================================
CH2_TOMORROW_SLOTS = [
    {
        "slot_id": "slot_quant_short_01",
        "time_brt": "07:15",
        "video_format": "SHORT_9_16",
        "title": "EDWARD THORP: O Professor do MIT que Quebrou Las Vegas e Wall Street #Shorts",
        "script_hook": "Antes de Jim Simons, um físico e matemático do MIT provou que os cassinos e a Bolsa podiam ser batidos com código.",
        "narration_text": (
            "Em mil novecentos e sessenta e um, o professor de matemática do MIT Edward Thorp usou um supercomputador IBM 704 "
            "para simular milhões de mãos de Blackjack e descobriu a falha estatística que os cassinos juravam não existir. "
            "Financiado pela máfia de Nova York com dez mil dólares, ele dobrou o capital em um único fim de semana em Reno. "
            "Quando os cassinos o expulsaram, Thorp levou suas equações para Wall Street e fundou o primeiro hedge fund quantitativo da história, "
            "rendendo vinte por cento ao ano durante duas décadas sem um único trimestre negativo. "
            "Inscreva-se no canal Finanças Quânticas."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
        "status_label": "PROGRAMADO (DESLOCAMENTO MATINAL 07:15)"
    },
    {
        "slot_id": "slot_quant_short_02",
        "time_brt": "11:15",
        "video_format": "SHORT_9_16",
        "title": "O COMPUTADOR SECRETO DO MIT: A Máquina que Previa a Roleta em 1961 #Shorts",
        "script_hook": "Edward Thorp e Claude Shannon construíram no porão do MIT o primeiro computador vestível da história para vencer a roleta.",
        "narration_text": (
            "Quinze anos antes da fundação da Apple, Edward Thorp juntou-se a Claude Shannon, o pai da Teoria da Informação, "
            "em um laboratório secreto no MIT. Eles compraram uma roleta profissional de Las Vegas e descobriram que, medindo "
            "a velocidade da esfera com um microinterruptor no sapato, um computador do tamanho de um maço de cigarros "
            "previa o octante exato onde a bola cairia, gerando uma vantagem matemática de quarenta e quatro por cento sobre a casa. "
            "Inscreva-se no canal Finanças Quânticas para conhecer a história real dos algoritmos."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
        "status_label": "PROGRAMADO (ABERTURA ALMOÇO 11:15)"
    },
    {
        "slot_id": "slot_quant_short_03",
        "time_brt": "13:45",
        "video_format": "SHORT_9_16",
        "title": "230 TRIMESTRES SEM PERDER: O Fundo Quantitativo Princeton Newport #Shorts",
        "script_hook": "De 1969 a 1988, o fundo de Edward Thorp bateu o S&P 500 pelo dobro da rentabilidade sem nenhum trimestre no vermelho.",
        "narration_text": (
            "Como um fundo de investimentos consegue operar por dezenove anos seguidos sem registrar um único trimestre de prejuízo? "
            "Em mil novecentos e sessenta e nove, Edward Thorp fundou a Princeton Newport Partners aplicando arbitragem estatística delta-neutra. "
            "Enquanto Wall Street operava no grito e na intuição, os computadores de Thorp vendiam opções supervalorizadas "
            "e compravam as ações subjacentes na proporção matemática exata, lucrando faça chuva ou faça sol no mercado. "
            "Acompanhe o documentário completo no canal Finanças Quânticas."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
        "status_label": "PROGRAMADO (PÓS-ALMOÇO 13:45)"
    },
    {
        "slot_id": "slot_quant_short_04",
        "time_brt": "16:00",
        "video_format": "SHORT_9_16",
        "title": "ANTES DE BLACK-SCHOLES: A Equação Secreta de US$ 100 Milhões de Thorp #Shorts",
        "script_hook": "Cinco anos antes de Black e Scholes publicarem a fórmula que ganhou o Nobel, Edward Thorp já a usava em segredo.",
        "narration_text": (
            "Em mil novecentos e setenta e três, Fischer Black e Myron Scholes revolucionaram as finanças publicando a famosa equação "
            "de precificação de opções. Mas poucos sabem que Edward Thorp havia deduzido a mesma fórmula cinco anos antes, em mil novecentos e sessenta e sete. "
            "Em vez de publicar em revistas acadêmicas, Thorp guardou a equação a sete chaves e a utilizou para extrair centenas de milhões de dólares "
            "em warrants mal precificados na Bolsa de Nova York. "
            "Inscreva-se no canal Finanças Quânticas."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
        "status_label": "PROGRAMADO (FECHAMENTO DE PREGÃO 16:00)"
    },
    {
        "slot_id": "slot_quant_long_01",
        "time_brt": "17:30",
        "video_format": "LONG_16_9",
        "title": "Edward Thorp: O Matemático do MIT que Derrotou Las Vegas e Wall Street [DOCUMENTÁRIO]",
        "script_hook": "A história real do cientista que inventou o primeiro computador vestível com Claude Shannon e construiu o primeiro fundo quantitativo invicto.",
        "narration_text": (
            "Muito antes de Jim Simons fundar a Renaissance Technologies e antes dos servidores de High Frequency Trading dominarem Nova York, "
            "um único professor de matemática do MIT provou que tanto os cassinos de Las Vegas quanto os bancos de Wall Street "
            "possuíam falhas estruturais que podiam ser exploradas pela física e pela estatística. "
            "O nome dele é Edward Oakley Thorp, o verdadeiro pai das finanças quantitativas modernas. "
            "Nascido durante a Grande Depressão, Thorp cresceu fascinado por resolver problemas que o consenso acadêmico declarava impossíveis. "
            "Em mil novecentos e cinquenta e nove, enquanto lecionava matemática no MIT, ele decidiu testar se o jogo de Blackjack "
            "poderia ser vencido matematicamente. Sem dinheiro para testar nas mesas reais, Thorp programou um mainframe IBM 704 "
            "usando cartões perfurados para processar milhões de combinações de baralho. "
            "O computador revelou algo extraordinário: como as cartas já jogadas não voltam imediatamente para o baralho, "
            "o jogo não possui probabilidades independentes. Quando restam mais cartas altas de dez e ases no monte, "
            "a vantagem matemática vira a favor do jogador. "
            "Ao lado de Claude Shannon, o lendário criador da Teoria da Informação no MIT, Thorp foi ainda mais longe: "
            "em mil novecentos e sessenta e um, eles construíram em segredo o primeiro computador vestível da história humana. "
            "Do tamanho de um maço de cigarros e acionado com os dedos dos pés dentro do sapato, o dispositivo media a velocidade "
            "do rotor e da bola de marfim na roleta, transmitindo tons musicais por um microfone no ouvido para indicar onde a bola cairia, "
            "gerando quarenta e quatro por cento de retorno positivo. "
            "Mas quando os cassinos de Nevada mudaram as regras e passaram a persegui-lo, Thorp olhou para o maior cassino do planeta: Wall Street. "
            "Na década de sessenta, o mercado de derivativos e warrants era precificado no palpite. "
            "Em mil novecentos e sessenta e sete, seis anos antes da publicação da equação de Black-Scholes que venceria o Prêmio Nobel, "
            "Edward Thorp desenvolveu sua própria fórmula estocástica de precificação de opções e fundou o fundo Princeton Newport Partners. "
            "Combinando o Critério de Kelly para dimensionamento ótimo de capital com o hedge dinâmico delta-neutro, "
            "o fundo de Thorp isolava o risco de quedas da bolsa. Durante o crash da década de setenta e a Segunda-Feira Negra de mil novecentos e oitenta e sete, "
            "enquanto Wall Street entrava em colapso, o algoritmo de Thorp fechou positivo, acumulando dezenove anos ininterruptos "
            "com retorno composto superior a vinte por cento ao ano sem um único trimestre de perda. "
            "Mais tarde, em mil novecentos e noventa e um, ao auditar as operações de um gestor famoso chamado Bernard Madoff, "
            "a equipe de Thorp verificou que metade das opções listadas nos extratos de Madoff jamais haviam sido negociadas na bolsa, "
            "desmascarando matematicamente a maior pirâmide financeira da história dezessete anos antes da SEC descobrir. "
            "Inscreva-se no canal Finanças Quânticas e ative o sino para dominar a ciência dos grandes gênios do mercado."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
        "status_label": "PROGRAMADO (DOCUMENTÁRIO NOBRE 16:9)"
    },
    {
        "slot_id": "slot_quant_short_05",
        "time_brt": "19:45",
        "video_format": "SHORT_9_16",
        "title": "COMO UM MATEMÁTICO DESMASCAROU MADOFF 17 ANOS ANTES DA SEC #Shorts",
        "script_hook": "Em 1991, Edward Thorp analisou os extratos de Bernard Madoff e provou em 48 horas que os lucros eram matematicamente impossíveis.",
        "narration_text": (
            "Dezessete anos antes de Bernard Madoff ser preso pela fraude de sessenta e quatro bilhões de dólares, "
            "o matemático Edward Thorp foi contratado para auditar os retornos perfeitos de Madoff em mil novecentos e noventa e um. "
            "Thorp cruzou os boletos de opções de Madoff com o volume real registrado na Bolsa de Chicago. "
            "O resultado foi implacável: em metade dos dias, o volume total negociado no mundo inteiro era zero, "
            "provando que as operações nunca existiram. Thorp retirou seus clientes imediatamente. "
            "Inscreva-se no canal Finanças Quânticas."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
        "status_label": "PROGRAMADO (FEEDER NOITE 19:45)"
    },
    {
        "slot_id": "slot_quant_short_06",
        "time_brt": "21:45",
        "video_format": "SHORT_9_16",
        "title": "STATISTICAL ARBITRAGE: A Máquina de Dinheiro que Thorp Criou em 1980 #Shorts",
        "script_hook": "Como comprar mil ações e vender outras mil ao mesmo tempo para lucrar mesmo se a Bolsa cair 20%?",
        "narration_text": (
            "Nos anos oitenta, Edward Thorp criou o algoritmo mud-pack, o precursor da arbitragem estatística moderna usada por fundos bilionários. "
            "O computador ranqueava todas as ações da Bolsa de Nova York que tinham caído demais em relação aos seus pares do mesmo setor. "
            "Ele comprava a cesta das ações mais descontadas e vendia a descoberto a mesma quantia financeira das ações mais esticadas, "
            "neutralizando o risco do mercado e capturando lucro puro na reversão à média. "
            "Aprenda finanças quantitativas no canal Finanças Quânticas."
        ),
        "status": "scheduled",
        "privacy_status": "public",
        "youtube_video_id": None,
        "watch_url": None,
        "status_label": "PROGRAMADO (LATE NIGHT 21:45)"
    },
]

# ==============================================================================
# CANAL 3: BIO HACK LONGEVIDADE — AUTOFAGIA CELULAR, SAÚDE MITOCONDRIAL & FOCO
# ==============================================================================
from backend.automation.biohack_daily_cadence import biohack_cadence_mgr
CH3_TOMORROW_SLOTS = biohack_cadence_mgr._generate_today_slots()


def prepare_tomorrow():
    """Grava os estados de cadência para o dia de amanhã (2026-10-20) com temas 100% inéditos."""
    logger.info("PREPARANDO GRADE INÉDITA DE AMANHÃ (%s)...", TOMORROW_STR)

    # 1. Canal #1
    s1 = {
        "is_active": True,
        "target_channel": {"name": "A Via da Descoberta", "handle": "@AViadaDescoberta", "id": CH1_ID},
        "schedule_date": TOMORROW_STR,
        "current_topic": "A Erupção Límnica do Lago Nyos (1986): 1,6 Milhão de Toneladas de Gás Invisível",
        "today_slots": CH1_TOMORROW_SLOTS,
        "last_cycle_timestamp": datetime.now(timezone.utc).isoformat()
    }
    CH1_STATE.write_text(json.dumps(s1, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Canal #1 preparado para %s com 7 slots inéditos (Lago Nyos)!", TOMORROW_STR)

    # 2. Canal #2
    s2 = {
        "is_active": True,
        "target_channel": {"name": "Finanças Quânticas", "handle": "@FinancasQuanticasOficial", "id": CH2_ID},
        "schedule_date": TOMORROW_STR,
        "current_topic": "Edward Thorp (MIT -> Wall Street): O Pai dos Quants e o Fundo de 230 Trimestres Invictos",
        "today_slots": CH2_TOMORROW_SLOTS,
        "last_cycle_timestamp": datetime.now(timezone.utc).isoformat()
    }
    CH2_STATE.write_text(json.dumps(s2, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Canal #2 preparado para %s com 7 slots inéditos (Edward Thorp)!", TOMORROW_STR)

    # 3. Canal #3: Bio Hack Longevidade
    s3 = {
        "is_active": True,
        "target_channel": {"name": "Bio Hack Longevidade", "handle": "@BioHackLongevidade", "id": CH3_ID},
        "schedule_date": TOMORROW_STR,
        "current_topic": "Autofagia Celular & Saúde Mitocondrial: O Prêmio Nobel que Decifrou o Rejuvenescimento Biológico",
        "today_slots": CH3_TOMORROW_SLOTS,
        "last_cycle_timestamp": datetime.now(timezone.utc).isoformat()
    }
    CH3_STATE.write_text(json.dumps(s3, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Canal #3 (Bio Hack Longevidade) preparado para %s com %d slots inéditos!", TOMORROW_STR, len(CH3_TOMORROW_SLOTS))


if __name__ == "__main__":
    prepare_tomorrow()
