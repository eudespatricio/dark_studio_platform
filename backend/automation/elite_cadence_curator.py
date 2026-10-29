"""
ELITE CADENCE CURATOR & CINEMATIC ASSET DISPATCHER
Garante que 100% dos slots em todos os canais (atuais e futuros) operem no
PADRÃO DE ELITE do Dark Studio:
1. Roteiros autorais densos (zero templates curtos ou repetitivos).
2. Infográficos técnicos e diagramas gerados programaticamente.
3. Mapeamento estrito 1-a-1 de B-Rolls e fotografias históricas/científicas reais.
4. Thumbnail Cinema Pro 2.0 com Poster Frame Frame 0 limpo nos primeiros 0.22s.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("elite_curator")

BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
SCENES_DIR = BASE_DIR / "workspace/scenes"


# ==============================================================================
# CANAL 1: A VIA DA DESCOBERTA — O COLAPSO DA REPRESA DE BANQIAO (1975)
# ==============================================================================

BANQIAO_SCRIPTS = {
    "slot_long_01": {
        "title": "O Colapso da Represa de Banqiao (1975): A Catástrofe das 62 Represas que Ocultaram por 30 Anos [DOCUMENTÁRIO]",
        "script_hook": "Em agosto de 1975, o colapso de uma única barragem na província de Henan desencadeou o maior desastre da história da engenharia mundial.",
        "narration_text": (
            "Na primeira semana de agosto de mil novecentos e setenta e cinco, o supertufão Nina perdeu velocidade "
            "ao atingir o interior da China e colidiu com uma frente fria sobre as montanhas da província de Henan. "
            "O que se seguiu foi uma anomalia atmosférica sem precedentes: em apenas vinte e quatro horas, "
            "desabaram mil e sessenta milímetros de chuva sobre a bacia do Rio Ru — uma quantidade de água que ultrapassava "
            "a precipitação média de um ano inteiro em um único dia. "
            "A represa de Banqiao, construída na década de mil novecentos e cinquenta com consultoria de engenheiros soviéticos, "
            "foi projetada como a 'Barragem de Ferro', supostamente indestrutível. Mas havia uma falha mortal de cálculo: "
            "sua capacidade máxima de vertedouro foi dimensionada para cheias de trezentos milímetros. "
            "À medida que o reservatório recebia mais de setecentos milhões de metros cúbicos de água, os operadores tentaram "
            "abrir as comportas de alívio. No entanto, as ordens de evacuação e abertura foram atrasadas pelo comando militar regional, "
            "que temia inundar as linhas ferroviárias estratégicas a jusante. Quando a autorização finalmente chegou, "
            "as linhas telegráficas já haviam sido arrancadas pelas inundações e as comportas estavam parcialmente soterradas por sedimentos. "
            "À uma hora da manhã de oito de agosto, uma onda galgou a crista da barragem de terra de vinte e quatro metros. "
            "A erosão por galgamento foi instantânea e violenta: a muralha de concreto e argila rompeu-se em segundos, "
            "liberando uma onda de choque líquida de dez metros de altura que avançou a cinquenta quilômetros por hora. "
            "O tsunami interno precipitou o colapso em cadeia de outras sessenta e uma represas menores ao longo de todo o vale. "
            "Onze milhões de pessoas foram desabrigadas e os relatórios oficiais foram imediatamente classificados como segredo de Estado. "
            "Durante trinta anos, o mundo não soube a dimensão real da tragédia — até que em dois mil e cinco, arquivos desclassificados "
            "revelaram o custo devastador de ignorar os avisos da engenharia hidráulica em favor da burocracia política. "
            "Inscreva-se no canal A Via da Descoberta para investigações históricas profundas e análises documentais completas."
        ),
    },
    "slot_short_01": {
        "title": "62 REPRESAS EM CADEIA: O maremoto interno que varreu 11 milhões de pessoas #Shorts",
        "script_hook": "Quando a represa principal rompeu, uma muralha líquida de dez metros viajou a cinquenta quilômetros por hora.",
        "narration_text": (
            "À uma da manhã de oito de agosto de mil novecentos e setenta e cinco, a represa de Banqiao colapsou. "
            "Setecentos milhões de metros cúbicos de água represada criaram uma onda de dez metros de altura que avançou "
            "sobre o vale do Rio Ru. Em menos de duas horas, a força do impacto causou o efeito dominó mais devastador da história: "
            "sessenta e uma outras represas menores romperam em sequência. Onze milhões de pessoas foram atingidas e vilarejos inteiros "
            "desapareceram do mapa em plena madrugada. Conheça a história completa no documentário do canal A Via da Descoberta."
        ),
    },
    "slot_short_02": {
        "title": "TUFÃO NINA: A chuva de 1.000 milímetros que a engenharia achava impossível #Shorts",
        "script_hook": "Em apenas vinte e quatro horas, caiu a quantidade de chuva prevista para mais de trezentos e sessenta dias.",
        "narration_text": (
            "A engenharia soviética construiu a represa de Banqiao para resistir a uma chuva de mil anos: trezentos milímetros em um dia. "
            "Mas em mil novecentos e setenta e cinco, o supertufão Nina estacionou sobre as montanhas de Henan. "
            "Em vinte e quatro horas, o pluviômetro marcou mil e sessenta milímetros — o recorde mundial absoluto da época. "
            "A 'Barragem de Ferro' foi engolida por mais do que o triplo da sua capacidade máxima de transbordamento. "
            "Assista ao documentário completo no canal A Via da Descoberta."
        ),
    },
    "slot_short_03": {
        "title": "AS COMPORTAS PRESAS: O erro fatal de comunicação que selou o destino do vale #Shorts",
        "script_hook": "Os engenheiros pediram autorização para abrir as comportas de emergência, mas a ordem foi negada.",
        "narration_text": (
            "Antes da represa romper, a equipe técnica de Banqiao tentou abrir os vertedouros para aliviar a pressão da água. "
            "Mas as autoridades regionais proibiram o escoamento temendo inundar plantações e estradas a jusante. "
            "Quando a situação ficou desesperadora e a ordem finalmente mudou, os postes de telégrafo já tinham sido derrubados "
            "pela tempestade. A mensagem nunca chegou. Sem contato, a represa encheu até o limite e arrebentou às cegas na escuridão. "
            "Inscreva-se no canal A Via da Descoberta."
        ),
    },
    "slot_short_04": {
        "title": "30 ANOS DE SEGREDO: O relatório desclassificado que revelou o maior colapso da história #Shorts",
        "script_hook": "Durante três décadas, o maior desastre de barragens do planeta permaneceu sob sigilo absoluto.",
        "narration_text": (
            "Por trinta anos, o mundo ocidental não teve ideia de que sessenta e duas represas haviam desmoronado na China em uma única noite. "
            "Milhares de vidas perdidas e milhões de refugiados foram classificados como segredo de segurança nacional. "
            "A verdade só começou a vir a público em dois mil e cinco, quando documentos confidenciais de hidrologia foram desclassificados. "
            "O monumento que hoje ergue-se na província de Henan é um lembrete eterno do perigo da negligência estrutural. "
            "Inscreva-se no canal A Via da Descoberta para mais mistérios reais."
        ),
    },
}


# ==============================================================================
# CANAL 2: FINANÇAS QUÂNTICAS — O FLASH CRASH DE 2010
# ==============================================================================

FLASH_CRASH_SCRIPTS = {
    "slot_quant_long_01": {
        "title": "O Flash Crash de 2010: Como um Algoritmo de Spoofing Apagou US$ 1 Trilhão em 36 Minutos [DOCUMENTÁRIO]",
        "script_hook": "Às duas horas e quarenta e dois minutos de seis de maio de 2010, Wall Street vivenciou o colapso mais rápido da história dos mercados financeiros.",
        "narration_text": (
            "Na tarde de seis de maio de dois mil e dez, os mercados norte-americanos operavam sob forte tensão geopolítica "
            "devido à crise da dívida grega na Europa. Pouco após as duas horas da tarde no horário de Nova York, "
            "uma grande gestora institucional executou uma ordem de venda algorítmica de setenta e cinco mil contratos "
            "futuros do E-mini S&P 500 na Bolsa Mercantil de Chicago, avaliada em mais de quatro bilhões de dólares. "
            "No entanto, o verdadeiro gatilho do caos estava a milhares de quilômetros dali, em uma casa suburbana nos arredores de Londres. "
            "Um operador independente chamado Navinder Singh Sarao operava um algoritmo customizado conectado à plataforma da CME. "
            "Seu código executava uma tática predatória conhecida como spoofing dinâmico: o software inundava o livro de ofertas "
            "com dezenas de milhares de ordens falsas de venda nos patamares logo acima do preço de mercado. "
            "As ordens permaneciam ativas por apenas milissegundos e eram automaticamente modificadas ou canceladas antes de qualquer execução. "
            "Os algoritmos de negociação de alta frequência das principais firmas de Wall Street interpretaram essa enxurrada de ordens falsas "
            "como uma gigantesca pressão real de venda institucional. Em fração de segundos, os robôs formadores de mercado "
            "desligaram seus algoritmos de liquidez e recuaram suas cotações de compra para evitar perdas catastróficas. "
            "Criou-se um vácuo absoluto de compradores. Sem contraparte no livro de ofertas, o Dow Jones Industrial Average "
            "despencou quase mil pontos em questão de minutos. Ações de empresas gigantes como Procter and Gamble e General Electric "
            "foram negociadas a centavos, enquanto outras subiram para cem mil dólares por ação. "
            "Cerca de um trilhão de dólares em valor de mercado evaporou em trinta e seis minutos — até que as travas automáticas "
            "da bolsa pausaram as negociações por cinco segundos, permitindo que a liquidez real retornasse e recuperasse a maior parte das perdas. "
            "O Flash Crash de dois mil e dez expôs pela primeira vez a fragilidade oculta da infraestrutura algorítmica global. "
            "Inscreva-se no canal Finanças Quânticas para dominar a matemática avançada e os segredos do mercado quantitativo."
        ),
    },
    "slot_quant_short_01": {
        "title": "US$ 1 TRILHÃO EM 36 MINUTOS: O trader do quarto dos pais que fez Wall Street evaporar #Shorts",
        "script_hook": "Às duas e quarenta e dois da tarde, um trilhão de dólares evaporou de Wall Street em 36 minutos por causa de um homem de pijama num quarto suburbano.",
        "narration_text": (
            "Às duas e quarenta e dois da tarde de seis de maio de dois mil e dez, um trilhão de dólares evaporou das telas da bolsa de Nova York. "
            "Em trinta e seis minutos, ações gigantescas foram executadas por centavos de dólar. Quando o FBI e os reguladores rastrearam "
            "o epicentro da anomalia global, não encontraram um banco em Manhattan — encontraram Navinder Sarao, um operador caseiro de trinta e seis anos "
            "que manipulou os maiores robôs de alta frequência do planeta direto do quarto dos pais nos subúrbios de Londres. "
            "Conheça a história forense completa no documentário do canal Finanças Quânticas."
        ),
    },
    "slot_quant_short_02": {
        "title": "ALGORITMOS DE SPOOFING: Como ordens falsas de milissegundos enganam os robôs de HFT #Shorts",
        "script_hook": "O truque que quebrou os algoritmos de Wall Street é proibido por lei: o spoofing de alta frequência.",
        "narration_text": (
            "Como um único operador moveu o mercado global? Sarao programou seu algoritmo para emitir duzentos milhões de dólares "
            "em ordens de venda falsas no livro da CME. As ordens mudavam de preço a cada doze milissegundos, empurrando o mercado para baixo. "
            "Os robôs de arbitragem leram a pressão como real e venderam em pânico. No fundo do poço, Sarao cancelou as vendas e comprou tudo a preço de liquidação. "
            "Inscreva-se no canal Finanças Quânticas para aprender estratégias quantitativas reais."
        ),
    },
    "slot_quant_short_03": {
        "title": "O EFEITO CASCATA: Quando os robôs de liquidez desligaram ao mesmo tempo na NYSE #Shorts",
        "script_hook": "Ações da Procter & Gamble despencaram de sessenta dólares para trinta e nove em menos de três minutos.",
        "narration_text": (
            "No Flash Crash de dois mil e dez, o perigo não foi apenas a ordem de venda — foi o que aconteceu quando os algoritmos de liquidez recuaram. "
            "Projetados para operar onde há fluxo calmo, os robôs de HFT desligaram suas cotações simultaneamente ao detectar volatilidade extrema. "
            "O mercado entrou em queda livre no vazio. Uma ação da Accenture foi executada por apenas um centavo de dólar antes do mercado reiniciar. "
            "Assista ao documentário completo no canal Finanças Quânticas."
        ),
    },
    "slot_quant_short_04": {
        "title": "DA CASA DOS PAIS PARA O TRIBUNAL: A caçada internacional ao trader Navinder Sarao #Shorts",
        "script_hook": "Foram necessários cinco anos de investigação forense de dados para que os Estados Unidos conseguissem prendê-lo.",
        "narration_text": (
            "Mesmo faturando mais de quarenta milhões de dólares com seus algoritmos, Navinder Sarao continuava morando com os pais "
            "e usando um carro popular modesto. Em dois mil e quinze, agentes federais bateram à sua porta com um pedido formal de extradição "
            "do Departamento de Justiça norte-americano. Seu caso reescreveu para sempre as regras de microestrutura e auditoria algorítmica de mercado. "
            "Inscreva-se no canal Finanças Quânticas para mais bastidores da ciência dos mercados."
        ),
    },
}


# ==============================================================================
# CANAL 3: BIO HACK LONGEVIDADE — NEUROBIOLOGIA DO FOCO EXTREMO & BDNF
# ==============================================================================

BIOHACK_FOCUS_SCRIPTS = {
    "slot_biohack_long_01": {
        "title": "A Neurobiologia do Foco Extremo: Como Acetilcolina e BDNF Religam o Cérebro Adulto [DOCUMENTÁRIO]",
        "script_hook": "Por que sustentar a atenção profunda é fisicamente desconfortável nos primeiros minutos e como desbloquear o hiperfoco?",
        "narration_text": (
            "A capacidade biológica de focar a mente em uma única tarefa complexa por longos períodos é uma das habilidades "
            "mais raras e termodinamicamente custosas do corpo humano. O cérebro consome cerca de vinte por cento de toda a energia metabólica, "
            "e por razões evolutivas de conservação de glicose, sua tendência natural é o rastreamento difuso do ambiente em busca de novidades. "
            "Quando você inicia um bloco de trabalho de alto esforço cognitivo, a sensação imediata de agitação e inquietação mental "
            "não é falta de força de vontade: é a liberação fisiológica de noradrenalina pelo locus coeruleus. "
            "A noradrenalina cria o estresse de erro necessário para alertar os circuitos neurais de que um aprendizado crítico está em andamento. "
            "Se você resiste à tentação de checar o celular nos primeiros dez minutos, o prosencéfalo basal e o córtex pré-frontal "
            "começam a secretar acetilcolina. A acetilcolina funciona como um holofote químico: ela aumenta a relação sinal-ruído dos neurônios, "
            "silenciando estímulos periféricos e marcando as sinapses exatas que devem ser fortalecidas. "
            "A neurociência moderna comprovou que o cérebro humano opera em ciclos ultradianos de noventa minutos. "
            "Ao longo dessa janela de ouro, a dopamina basal mantém o impulso motivacional e o alinhamento com a meta, enquanto a atividade "
            "eletroencefalográfica transita de ondas Beta para frequências Gamma de alta coerência. "
            "Após noventa minutos, os reservatórios de neurotransmissores esgotam-se, os níveis de adenosina acumulam-se no tecido cerebral "
            "e a fadiga sináptica impõe uma pausa obrigatória de descompressão. "
            "No entanto, marcar as sinapses durante o foco profundo é apenas a primeira metade do processo biológico. "
            "Para consolidar permanentemente essas conexões e ativar a neuroplasticidade no cérebro adulto, entra em ação o BDNF, "
            "o fator neurotrófico derivado do cérebro. Sem o BDNF, as marcações de acetilcolina degradam-se em menos de vinte e quatro horas. "
            "Protocolos horméticos específicos são os maiores indutores conhecidos de BDNF na medicina moderna: o exercício aeróbico "
            "em frequência cardíaca de Zona Dois por quarenta e cinco minutos, a exposição controlada ao contraste térmico e, acima de tudo, "
            "a fase de sono profundo de ondas lentas, onde o sistema glinfático remove toxinas metabólicas e o cérebro consolida memórias permanentes. "
            "Ao alinhar sua rotina com a farmacologia endógena do cérebro, o foco profundo deixa de ser um esforço exaustivo e torna-se um estado biológico previsível. "
            "Inscreva-se no canal Bio Hack Longevidade para dominar os protocolos científicos de alta performance biológica."
        ),
    },
    "slot_biohack_short_01": {
        "title": "A BARREIRA DOS 10 MINUTOS: Por que seu cérebro resiste ao foco profundo antes de liberar acetilcolina #Shorts",
        "script_hook": "A sensação de tédio e vontade de fugir nos primeiros minutos de estudo não é fraqueza — é química cerebral.",
        "narration_text": (
            "Nos primeiros dez minutos de foco profundo, seu cérebro sofre uma descarga de noradrenalina. "
            "Ela gera uma sensação física de desconforto projetada para economizar energia metabólica. "
            "A maioria das pessoas desiste e pega o celular exatamente nesse ponto. Mas se você sustenta o esforço, "
            "o córtex pré-frontal libera acetilcolina, silenciando o ruído ao redor e criando o foco em túnel perfeito. "
            "Conheça o protocolo completo no documentário do canal Bio Hack Longevidade."
        ),
    },
    "slot_biohack_short_02": {
        "title": "CICLOS DE 90 MINUTOS: A neurociência dos ritmos ultradianos para produtividade máxima #Shorts",
        "script_hook": "Tentar trabalhar focado por quatro horas seguidas sem pausas destrói sua neuroplasticidade.",
        "narration_text": (
            "A biologia humana não foi projetada para foco linear. O cérebro opera em ritmos ultradianos de noventa minutos, "
            "tanto de dia quanto durante o sono REM. Nos primeiros vinte minutos você aquece, dos vinte aos setenta e cinco minutos "
            "atinge o pico cognitivo, e nos últimos quinze minutos a fadiga sináptica se instala. "
            "Trabalhar em blocos de noventa minutos com pausas de vinte minutos dobra a retenção e o aprendizado. "
            "Inscreva-se no canal Bio Hack Longevidade para mais protocolos."
        ),
    },
    "slot_biohack_short_03": {
        "title": "O FERTILIZANTE SINÁPTICO: Como elevar o BDNF e acelerar o aprendizado após os 25 anos #Shorts",
        "script_hook": "O cérebro adulto só cria novas conexões neurais se receber este sinalizador biológico específico.",
        "narration_text": (
            "Após os vinte e cinco anos, as janelas de neuroplasticidade passiva se fecham. Para religar seus circuitos cognitivos, "
            "você precisa de BDNF: o fator de crescimento que estimula a neurogênese no hipocampo. "
            "Trinta minutos de corrida ou ciclismo em Zona Dois combinados com exposição ao frio elevam o BDNF em até setenta por cento, "
            "preparando seu cérebro para aprender o dobro na sessão seguinte. "
            "Assista ao documentário completo no canal Bio Hack Longevidade."
        ),
    },
    "slot_biohack_short_04": {
        "title": "LUZ SOLAR & CORTISOL: O protocolo matinal de 15 minutos para ancorar sua dopamina basal #Shorts",
        "script_hook": "O maior erro cometido logo ao acordar é olhar para a tela brilhante antes de ver a luz do sol.",
        "narration_text": (
            "A luz solar direta nos primeiros quinze minutos da manhã ativa as células ganglionares intrínsecas da retina. "
            "Esse estímulo dispara um pulso saudável de cortisol matinal que programa o relógio biológico central no hipotálamo, "
            "elevando a dopamina basal e garantindo energia sustentada durante o dia e melatonina de qualidade à noite. "
            "Elimine a fadiga mental com este protocolo simples. Inscreva-se no canal Bio Hack Longevidade."
        ),
    },
}


# ==============================================================================
# DISPATCHER DE ATIVOS TEMÁTICOS EXCLUSIVOS POR CANAL E POR SLOT
# ==============================================================================

def get_channel_elite_assets(channel_num: int, slot_id: str, seed_key: str = "") -> List[Tuple[str, Path]]:
    """
    Retorna o acervo 100% temático de infográficos, fotografias históricas e vídeos
    específicos para o slot solicitado, eliminando o shuffle aleatório genérico.
    """
    assets: List[Tuple[str, Path]] = []
    
    if channel_num == 1:
        # CANAL 1: A VIA DA DESCOBERTA (BANQIAO)
        banqiao_dir = SCENES_DIR / "banqiao"
        diag1 = banqiao_dir / "diag_01_rainfall_nina_vs_capacity.png"
        diag2 = banqiao_dir / "diag_02_dam_overtopping_failure.png"
        diag3 = banqiao_dir / "diag_03_cascade_failure_62_dams.png"
        
        valley_img = banqiao_dir / "banqiao_dam_valley.jpg"
        spillway_img = banqiao_dir / "banqiao_spillway_gates.jpg"
        aftermath_img = banqiao_dir / "flood_aftermath_ru_valley.jpg"
        henan_img = banqiao_dir / "henan_province_valley_1975.jpg"
        
        flood_vid = banqiao_dir / "dam_break_flood_surge.webm"
        vortex_vid = banqiao_dir / "water_vortex_overtopping.webm"
        
        c_scene1 = SCENES_DIR / "clip_scene_01.mp4"
        c_scene2 = SCENES_DIR / "clip_scene_02.mp4"
        c_scene3 = SCENES_DIR / "clip_scene_03.mp4"
        c_scene4 = SCENES_DIR / "clip_scene_04.mp4"
        c_scene5 = SCENES_DIR / "clip_scene_05.mp4"
        c_scene6 = SCENES_DIR / "clip_scene_06.mp4"

        if "short_01" in slot_id:
            # 62 Represas em Cadeia (Maremoto Interno) - 6 assets distintos garantidos
            assets = [("image", diag3), ("video", flood_vid), ("image", aftermath_img), ("video", c_scene1), ("image", valley_img), ("video", vortex_vid)]
        elif "short_02" in slot_id:
            # Tufão Nina / Chuva de 1000mm - 6 assets distintos garantidos
            assets = [("image", diag1), ("video", vortex_vid), ("image", valley_img), ("video", c_scene2), ("image", henan_img), ("video", flood_vid)]
        elif "short_03" in slot_id:
            # As Comportas Presas - 6 assets distintos garantidos
            assets = [("image", spillway_img), ("image", diag2), ("video", flood_vid), ("image", valley_img), ("video", c_scene3), ("image", aftermath_img)]
        elif "short_04" in slot_id:
            # 30 Anos de Segredo (D+1) - 6 assets distintos garantidos
            assets = [("image", aftermath_img), ("image", diag3), ("image", henan_img), ("video", flood_vid), ("video", c_scene4), ("image", spillway_img)]
        else:
            # Long Documentary 16:9 - 14 assets distintos de alta fidelidade
            assets = [
                ("image", diag1), ("video", vortex_vid), ("image", valley_img),
                ("image", diag2), ("video", flood_vid), ("image", spillway_img),
                ("image", diag3), ("image", aftermath_img), ("image", henan_img),
                ("video", c_scene1), ("video", c_scene2), ("video", c_scene3),
                ("video", c_scene4), ("video", c_scene5)
            ]

    elif channel_num == 2:
        # CANAL 2: FINANÇAS QUÂNTICAS (FLASH CRASH 2010)
        fc_dir = SCENES_DIR / "flash_crash"
        diag_drop = fc_dir / "anim_diag_01_flash_crash_dow.mp4" if (fc_dir / "anim_diag_01_flash_crash_dow.mp4").exists() else fc_dir / "diag_01_flash_crash_dow_drop.png"
        diag_spoof = fc_dir / "diag_02_spoofing_orderbook_depth.png"
        
        nyse_img = fc_dir / "real_photo_01_nyse_floor.jpg"
        cme_img = fc_dir / "real_photo_02_cme_chicago.jpg"
        wallst_img = fc_dir / "real_photo_03_wall_street.jpg"
        canary_img = fc_dir / "real_photo_05_canary_wharf.jpg"
        
        v1 = fc_dir / "ch2_flash_crash_9min_real_scene_01.mp4"
        v2 = fc_dir / "ch2_flash_crash_9min_real_scene_03.mp4"
        v3 = fc_dir / "ch2_flash_crash_9min_real_scene_07.mp4"
        v4 = fc_dir / "ch2_flash_crash_9min_real_scene_10.mp4"
        v5 = fc_dir / "ch2_flash_crash_9min_real_short_01.mp4"

        v6 = fc_dir / "ch2_flash_crash_9min_real_scene_04.mp4"
        v7 = fc_dir / "ch2_flash_crash_9min_real_scene_05.mp4"
        v8 = fc_dir / "ch2_flash_crash_9min_real_scene_06.mp4"
        v9 = fc_dir / "ch2_flash_crash_9min_real_scene_08.mp4"

        if "short_01" in slot_id:
            assets = [("video" if str(diag_drop).endswith(".mp4") else "image", diag_drop), ("video", v1), ("image", nyse_img), ("video", v5), ("image", wallst_img), ("video", v6)]
        elif "short_02" in slot_id:
            assets = [("image", diag_spoof), ("video", v2), ("image", cme_img), ("video", v3), ("image", canary_img), ("video", v7)]
        elif "short_03" in slot_id:
            assets = [("image", nyse_img), ("video" if str(diag_drop).endswith(".mp4") else "image", diag_drop), ("video", v4), ("image", wallst_img), ("video", v8), ("image", cme_img)]
        elif "short_04" in slot_id:
            assets = [("image", canary_img), ("image", diag_spoof), ("video", v1), ("image", wallst_img), ("video", v9), ("video", v2)]
        else:
            assets = [
                ("video" if str(diag_drop).endswith(".mp4") else "image", diag_drop), ("video", v1), ("image", nyse_img),
                ("image", diag_spoof), ("video", v2), ("image", cme_img),
                ("video", v3), ("image", wallst_img), ("video", v4),
                ("image", canary_img), ("video", v5), ("video", v6),
                ("video", v7), ("video", v8)
            ]

    else:
        # CANAL 3: BIO HACK LONGEVIDADE (NEUROBIOLOGIA & FOCO)
        bio_dir = SCENES_DIR / "biohack"
        charts_dir = bio_dir / "charts"
        real_dir = bio_dir / "real_sources"
        clips_dir = bio_dir / "remodeled_clips"
        
        diag_focus = charts_dir / "anim_diag_06_ultradian_focus.mp4" if (charts_dir / "anim_diag_06_ultradian_focus.mp4").exists() else charts_dir / "diag_06_ultradian_focus_phases.png"
        diag_bdnf = charts_dir / "diag_07_bdnf_neurogenesis_curve.png"
        diag_circadian = charts_dir / "diag_01_circadian_cortisol_dopamine.png"
        
        retina_img = real_dir / "circadian_retina_iprgc.jpg"
        synapse_img = real_dir / "synapse_neurotransmission_tem.jpg"
        hippo_img = real_dir / "hippocampus_neurogenesis_confocal.jpg"
        fmri_img = real_dir / "fmri_brain_activation_scan.jpg"
        
        c_syn1 = clips_dir / "clip_synapse_01.mp4"
        c_syn2 = clips_dir / "clip_synapse_02.mp4"
        c_micro = clips_dir / "clip_microtubule_01.mp4"
        c_circ = clips_dir / "clip_circadian_01.mp4"

        c_atp1 = clips_dir / "clip_atp_01.mp4"
        c_atp2 = clips_dir / "clip_atp_02.mp4"
        c_cell1 = clips_dir / "clip_cell_struct_01.mp4"
        c_cell2 = clips_dir / "clip_cell_struct_02.mp4"

        if "short_01" in slot_id:
            assets = [("video" if str(diag_focus).endswith(".mp4") else "image", diag_focus), ("video", c_syn1), ("image", fmri_img), ("video", c_syn2), ("image", retina_img), ("video", c_atp1)]
        elif "short_02" in slot_id:
            assets = [("video" if str(diag_focus).endswith(".mp4") else "image", diag_focus), ("video", c_syn2), ("image", synapse_img), ("video", c_micro), ("image", hippo_img), ("video", c_cell1)]
        elif "short_03" in slot_id:
            assets = [("image", diag_bdnf), ("video", c_syn1), ("image", hippo_img), ("video", c_micro), ("image", fmri_img), ("video", c_atp2)]
        elif "short_04" in slot_id:
            assets = [("image", diag_circadian), ("video", c_circ), ("image", retina_img), ("video", c_cell2), ("image", synapse_img), ("video", c_syn2)]
        else:
            assets = [
                ("video" if str(diag_focus).endswith(".mp4") else "image", diag_focus), ("video", c_syn1), ("image", fmri_img),
                ("image", diag_bdnf), ("video", c_syn2), ("image", synapse_img),
                ("image", diag_circadian), ("video", c_micro), ("image", hippo_img),
                ("video", c_circ), ("image", retina_img), ("video", c_atp1),
                ("video", c_atp2), ("video", c_cell1)
            ]

    # Validação e fallback limpo
    valid_assets = [(k, p) for k, p in assets if p.exists() and p.stat().st_size > 10_000]
    return valid_assets


def enrich_slot_with_elite_scripts(channel_num: int, slot: Dict[str, Any]) -> Dict[str, Any]:
    """Injeta roteiro autoral de alta densidade no slot."""
    slot_id = slot.get("slot_id", "")
    
    if channel_num == 1:
        data = BANQIAO_SCRIPTS.get(slot_id, {})
    elif channel_num == 2:
        data = FLASH_CRASH_SCRIPTS.get(slot_id, {})
    else:
        data = BIOHACK_FOCUS_SCRIPTS.get(slot_id, {})
        
    if data:
        slot["title"] = data["title"]
        slot["script_hook"] = data["script_hook"]
        slot["narration_text"] = data["narration_text"]
        
    return slot
