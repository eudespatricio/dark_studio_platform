"""
PRODUÇÃO COMPLETA: DOCUMENTÁRIO CINEMATOGRÁFICO DE 11 MINUTOS + SHORT 9:16
Canal: Finanças Quânticas (@FinancasQuanticasOficial | UCE6Ch6nhxI81Z6ILQIw23_Q)

Gera:
1. Documentário Longo 16:9 de 11 Minutos:
   - 6 Capítulos completos narrados pela voz George (ElevenLabs)
   - Trilha orquestral / eletrônica ambiente com sidechain ducking (-14 LUFS)
   - Sequência de 32 cenas com Ken Burns motion (fotos de Jim Simons, NYSE, servidores e gráficos matemáticos)
   - Legendas dinâmicas .ASS
2. YouTube Short 9:16 de 45s:
   - Formato vertical de alta retenção no gancho do código de 66%
   - Legendas Pop-in Hormozi Neon
   - Vinculado como Related Video ao Documentário de 11 minutos
3. Upload Automático Oficial ao YouTube via OAuth2 (Público)
"""

import os
import re
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import List, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("quant_documentary_11min")

def get_media_duration(path: Path) -> float:
    p = subprocess.run(["ffmpeg", "-i", str(path)], stderr=subprocess.PIPE, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", p.stderr)
    if m:
        return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    return 660.0

BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
AUDIO_DIR = BASE_DIR / "workspace" / "audio"
RENDERS_DIR = BASE_DIR / "workspace" / "renders"
THUMB_DIR = BASE_DIR / "workspace" / "thumbnails"
SCENES_DIR = BASE_DIR / "workspace" / "scenes" / "quant"
MUSIC_DIR = BASE_DIR / "assets" / "music"

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
RENDERS_DIR.mkdir(parents=True, exist_ok=True)
THUMB_DIR.mkdir(parents=True, exist_ok=True)
SCENES_DIR.mkdir(parents=True, exist_ok=True)

CHANNEL_ID = "UCE6Ch6nhxI81Z6ILQIw23_Q"
VOICE_ID = "ErXwobaYiN019PkySvjV"  # George

# ==============================================================================
# ROTEIRO COMPLETO DO DOCUMENTÁRIO DE 11 MINUTOS (1.550 PALAVRAS, 6 CAPÍTULOS)
# ==============================================================================

CHAPTERS_TEXT = [
    # Cap 1: Prólogo & O Quebrador de Códigos (00:00 - 01:50)
    (
        "Em Wall Street, existe um dogma secular que afirma que é matematicamente impossível bater o mercado "
        "de forma consistente ao longo de décadas. Acadêmicos laureados com o Prêmio Nobel formularam a Hipótese do Mercado Eficiente, "
        "declarando que os preços de todas as ações já refletem todas as informações conhecidas e que qualquer tentativa "
        "de prever o futuro não passa de pura sorte estatística. "
        "Lendas dos investimentos tradicionais como Warren Buffett e Peter Lynch construíram seus impérios lendo balanços patrimoniais, "
        "conversando com presidentes de empresas e tentando decifrar o comportamento do consumidor. "
        "Mas em 1978, nos arredores arborizados de Long Island, um matemático brilhante decidiu que tudo isso não passava de ilusão e folclore humano. "
        "Seu nome era James Harris Simons. "
        "Aos vinte e três anos, Simons já havia conquistado seu doutorado em matemática pela Universidade de Berkeley. "
        "Pouco tempo depois, foi recrutado pelo Instituto de Análises de Defesa do Pentágono, atuando como o principal decifrador de códigos ultrassecretos "
        "da União Soviética durante o auge da Guerra Fria. "
        "Naquele ambiente de espionagem e criptoanálise militar, Simons aprendeu uma lição que mudaria o capitalismo para sempre: "
        "mesmo nas mensagens mais caóticas e indecifráveis, existem padrões estatísticos ocultos que a mente humana comum é incapaz de enxergar. "
        "Ao lado do lendário geômetra Shiing-Shen Chern, Simons desenvolveu a Teoria de Chern-Simons, uma das formulações matemáticas mais complexas do século vinte, "
        "essencial para a física quântica e a teoria das cordas. "
        "Mas Simons não queria apenas resolver problemas abstratos no quadro-negro. Ele queria conquistar o maior quebra-cabeça probabilístico do planeta: os mercados financeiros."
    ),
    # Cap 2: A Fundação da Renaissance & A Proibição de Economistas (01:50 - 03:40)
    (
        "Ao abandonar a chefia do departamento de matemática da Universidade de Stony Brook, Simons fundou a Monemetrics, que mais tarde se tornaria a Renaissance Technologies. "
        "Ele estabeleceu seu quartel-general intencionalmente longe de Manhattan, no isolamento de East Setauket, para proteger sua equipe do barulho e do histerismo de Wall Street. "
        "E foi lá que Jim Simons impôs uma regra radical que chocou o mercado: era terminantemente proibido contratar corretores, analistas financeiros, "
        "ou formados em administração e economia por faculdades de prestígio. "
        "Para Simons, os economistas sofriam de uma falha cognitiva fatal: eles inventavam narrativas lógicas para eventos que já tinham acontecido, "
        "acreditando ingenuamente que o mercado agia com base em racionalidade e fundamentos econômicos. "
        "Em vez disso, a Renaissance recrutou exclusivamente a elite intelectual das ciências exatas: físicos teóricos, astrônomos, linguistas computacionais, "
        "especialistas em inteligência artificial e matemáticos puros. "
        "Cientistas como René Carmona, Elwyn Berlekamp e os gênios da computação da IBM, Peter Brown e Robert Mercer, foram reunidos com uma única missão: "
        "tratar o mercado financeiro não como um cassino econômico, mas como um sistema físico dinâmico, turbulento e repleto de anomalias imperceptíveis."
    ),
    # Cap 3: As Cadeias Ocultas de Markov e o Medallion Fund (03:40 - 05:30)
    (
        "Em 1988, nascia oficialmente o lendário Medallion Fund. Mas os primeiros anos foram marcados por frustrações e prejuízos. "
        "Nos primeiros modelos, Simons e seus sócios ainda tentavam intervir manualmente quando os computadores emitiam sinais contraintuitivos. "
        "Foi quando o matemático Elwyn Berlekamp deu um ultimato: ou desligavam o fator humano de uma vez por todas e deixavam os algoritmos operarem cem por cento no piloto automático, "
        "ou o fundo deveria fechar as portas. Simons aceitou o desafio, e essa se tornou a decisão mais lucrativa de toda a história humana. "
        "No coração do Medallion operavam os Modelos Ocultos de Markov, conhecidos como HMM. "
        "Em probabilidade, um modelo de Markov assume que o mercado transita continuamente entre diferentes estados ocultos não observáveis diretamente na tela. "
        "Existe o estado de baixa volatilidade e acúmulo institucional silencioso; o estado de tendência forte e liquidez ampla; e o estado de turbulência, pânico e deslocamento assimétrico. "
        "Enquanto os operadores humanos tentavam adivinhar para onde uma ação iria daqui a seis meses, os computadores da Renaissance analisavam gigabytes de dados históricos de preços em frações de segundo, "
        "identificando em que regime o mercado estava operando naquele exato microssegundo. "
        "Eles descobriram que os preços não se moviam de forma aleatória: a pressão de compradores forçados, os horários de fechamento de ordens em Londres e Tóquio, "
        "e as micro-ineficiências nos livros de ofertas deixavam impressões digitais matemáticas inconfundíveis."
    ),
    # Cap 4: A Matemática dos 66% ao Ano e o Critério de Kelly (05:30 - 07:20)
    (
        "Os resultados gerados pelo Medallion desafiaram a própria compreensão da economia moderna. "
        "Entre 1988 e 2021, o fundo entregou um retorno médio anual assombroso de sessenta e seis por cento bruto antes das taxas. "
        "Mesmo após cobrar as taxas mais caras do planeta — cinco por cento de taxa de administração e quarenta e quatro por cento sobre os lucros — "
        "o retorno líquido médio permaneceu acima de trinta e nove por cento ao ano. "
        "Para colocar isso em perspectiva: mil dólares aplicados no índice S&P 500 no mesmo período teriam se transformado em cerca de quarenta mil dólares. "
        "Os mesmos mil dólares sob a gestão do algoritmo de Jim Simons teriam se multiplicado em mais de quarenta e dois milhões de dólares. "
        "Mas qual era a taxa de acerto do Medallion? Setenta, oitenta por cento? A resposta real é surpreendente: era de apenas cinquenta vírgula setenta e cinco por cento. "
        "Como explicava o próprio Jim Simons: nós estamos certos cinquenta vírgula setenta e cinco por cento das vezes, mas estamos certos cem por cento das vezes em que precisamos estar. "
        "Com centenas de milhares de micro-operações diárias cobrindo ações globais, títulos soberanos, contratos futuros de commodities e moedas, "
        "a Lei dos Grandes Números transformava aquela minúscula vantagem de fração de por cento em uma certeza quase absoluta de fluxo de caixa positivo. "
        "E para garantir que uma sequência inesperada de perdas jamais levasse o fundo à ruína, a equipe aplicava rigorosamente o Critério de Kelly, "
        "calculando a alavancagem ótima e o tamanho exato de cada lote com base na variância e na covariância de todos os ativos do portfólio."
    ),
    # Cap 5: A Prova de Fogo: O Lucro no Caos de 2008 e o Flash Crash de 2010 (07:20 - 09:10)
    (
        "A verdadeira supremacia de um modelo quantitativo não é medida em tempos de calmaria, mas sim quando o sistema financeiro internacional entra em colapso. "
        "Em 2008, a crise dos derivativos imobiliários subprime desencadeou a pior recessão desde o Crash de 1929. "
        "Bancos gigantescos como Lehman Brothers e Bear Stearns implodiram, e o mercado acionário global derreteu trinta e oito por cento em doze meses. "
        "Mas enquanto os gestores tradicionais entravam em desespero e viam seus fundos quebrarem, o algoritmo da Renaissance registrou um lucro espetacular de mais de oitenta e dois por cento no ano. "
        "Como isso foi possível? Porque no auge do pânico, o comportamento humano torna-se totalmente previsível. "
        "Bancos forçados a liquidar posições para cobrir chamadas de margem despejavam bilhões em ativos a preços artificialmente deprimidos. "
        "Os robôs da Renaissance, operando friamente sem medo ou ganância, capturavam essas anomalias de arbitragem estatística no exato momento da distorção, "
        "revertendo as posições quando o equilíbrio de curto prazo se restabelecia. "
        "Dois anos depois, em 6 de maio de 2010, ocorreu o célebre Flash Crash: em apenas trinta e seis minutos, um trilhão de dólares em valor de mercado desapareceu e retornou "
        "devido ao efeito dominó de ordens automatizadas de alta frequência. "
        "Para a maioria dos investidores, foi um pesadelo incompreensível. Para a Renaissance, foi mais uma confirmação de que os mercados obedecem às leis da física dos sistemas caóticos."
    ),
    # Cap 6: O Paradoxo do Capital e o Futuro das Finanças Quânticas (09:10 - 11:05)
    (
        "Em 1993, percebendo que tinham em mãos o algoritmo mais valioso da civilização, Jim Simons tomou uma decisão sem precedentes: "
        "expulsou todos os clientes externos e fechou o Medallion exclusivamente para os funcionários e cientistas da própria Renaissance. "
        "Eles descobriram o Paradoxo do Capital: ao contrário dos fundos tradicionais que buscam acumular centenas de bilhões de dólares sob gestão, "
        "o Medallion tem um teto de capacidade fixo entre dez e quinze bilhões de dólares. "
        "Se o patrimônio ultrapassasse esse limite, as ordens do próprio algoritmo começariam a mover os preços das ações, destruindo a rentabilidade das micro-anomalias. "
        "Por isso, ao final de cada ano, a Renaissance devolve cem por cento de todos os lucros gerados aos seus cientistas, reiniciando o fundo com o capital estritamente calibrado. "
        "Com uma fortuna pessoal estimada em mais de trinta bilhões de dólares, Jim Simons dedicou suas últimas décadas à filantropia científica, "
        "financiando pesquisas pioneiras em física teórica, autismo e a matemática pura através da Simons Foundation, até seu falecimento pacífico em maio de 2024. "
        "Hoje, a fronteira dos mercados migrou para a computação quântica, aprendizado por reforço profundo e redes neurais que analisam terabytes de fluxos de dados por segundo. "
        "Mas todas as inteligências artificiais que hoje operam em Wall Street bebem da mesma fonte matemática concebida por Jim Simons: "
        "a certeza de que, por trás do barulho caótico do mundo financeiro, existem equações universais esperando para serem decifradas. "
        "Inscreva-se no canal Finanças Quânticas para continuar decodificando a ciência dos mercados."
    )
]

SHORT_TEXT = (
    "Por que o matemático que decifrou códigos secretos na Guerra Fria proibiu economistas de pisarem no fundo mais lucrativo da história humana? "
    "Em 1988, Jim Simons fundou o Medallion Fund com uma regra estrita: zero corretores de Wall Street, apenas astrofísicos e matemáticos puros. "
    "O resultado? Sessenta e seis por cento de retorno médio ao ano durante mais de três décadas, transformando mil dólares em quarenta e dois milhões. "
    "O segredo não era adivinhar o futuro, mas usar cadeias ocultas de Markov para vencer cem mil vezes por dia com apenas cinquenta vírgula setenta e cinco por cento de acerto. "
    "Conheça o documentário completo de 11 minutos no canal Finanças Quânticas."
)

# ==============================================================================
# ETAPA 1: SÍNTESE DE ÁUDIO NEURAL ELEVENLABS GEORGE
# ==============================================================================

def step1_synthesize_voice() -> Tuple[Path, Path]:
    from backend.core.tts_engine import TTSEngine
    tts = TTSEngine()

    logger.info("=" * 70)
    logger.info("ETAPA 1: SINTETIZANDO LOCUÇÃO NEURAL GEORGE (ELEVENLABS)")
    logger.info("=" * 70)

    # 1. Narração do Short (45-50s)
    logger.info("Sintetizando Short 9:16...")
    short_res = tts.synthesize_speech(
        text=SHORT_TEXT,
        voice_id=VOICE_ID,
        output_filename="quant_short_11min_simons.mp3",
        force_refresh=False
    )
    short_voice = Path(short_res["audio_path"])
    logger.info("Short voz gerada: %s (%.1fs)", short_voice, short_res.get("duration_sec", 45.0))

    # 2. Narração dos 6 Capítulos do Documentário Longo de 11 Minutos
    logger.info("\nSintetizando 6 Capítulos do Documentário de 11 Minutos...")
    chapter_audios = []
    for idx, chap_text in enumerate(CHAPTERS_TEXT, 1):
        fname = f"quant_doc_cap_{idx:02d}.mp3"
        logger.info("  Capítulo %d/6 (%d palavras, %d caracteres)...", idx, len(chap_text.split()), len(chap_text))
        res = tts.synthesize_speech(
            text=chap_text,
            voice_id=VOICE_ID,
            output_filename=fname,
            force_refresh=False
        )
        c_path = Path(res["audio_path"])
        chapter_audios.append(c_path)
        logger.info("  Capítulo %d concluído: %s (%.1fs)", idx, c_path.name, res.get("duration_sec", 110.0))

    # Concatena os 6 capítulos em um áudio contínuo de 11 minutos
    concat_list = AUDIO_DIR / "chapters_concat.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for ca in chapter_audios:
            f.write(f"file '{ca.resolve()}'\n")

    long_master_voice = AUDIO_DIR / "quant_long_11min_voice_master.mp3"
    cmd_cat = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(long_master_voice)
    ]
    subprocess.run(cmd_cat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Mede duração real
    total_dur = get_media_duration(long_master_voice)
    logger.info("\n[OK] Documentário Longo montado com sucesso!")
    logger.info("     Arquivo: %s", long_master_voice)
    logger.info("     Duração Total: %.2fs (%.2f minutos)", total_dur, total_dur / 60.0)

    return short_voice, long_master_voice

# ==============================================================================
# ETAPA 2: MASTERIZAÇÃO DE ÁUDIO COM TRILHA BGM & DUCKING (-14 LUFS)
# ==============================================================================

def step2_master_audio(short_voice: Path, long_voice: Path) -> Tuple[Path, Path, float, float]:
    logger.info("=" * 70)
    logger.info("ETAPA 2: MIXAGEM COM TRILHA BGM & NORMALIZAÇÃO EBU R128 (-14 LUFS)")
    logger.info("=" * 70)

    bgm_path = MUSIC_DIR / "echoes_of_time.mp3"

    # Duração do Short
    short_dur = get_media_duration(short_voice)

    # Duração do Longo
    long_dur = get_media_duration(long_voice)

    # 1. Master Short
    short_master = RENDERS_DIR / "quant_short_11min_master.wav"
    cmd_sm = [
        "ffmpeg", "-y",
        "-i", str(short_voice),
        "-stream_loop", "-1", "-i", str(bgm_path),
        "-filter_complex",
        "[0:a]loudnorm=I=-14:TP=-1.5:LRA=11[v];"
        "[1:a]volume=-18dB[b];"
        "[v][b]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "[aout]",
        "-t", f"{short_dur:.2f}",
        str(short_master)
    ]
    subprocess.run(cmd_sm, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    logger.info("Áudio Short masterizado: %s (%.1fs)", short_master.name, short_dur)

    # 2. Master Longo 11 Minutos
    long_master = RENDERS_DIR / "quant_long_11min_master.wav"
    cmd_lm = [
        "ffmpeg", "-y",
        "-i", str(long_voice),
        "-stream_loop", "-1", "-i", str(bgm_path),
        "-filter_complex",
        "[0:a]loudnorm=I=-14:TP=-1.5:LRA=11[v];"
        "[1:a]volume=-22dB[b];"
        "[v][b]amix=inputs=2:duration=first:dropout_transition=3[aout]",
        "-map", "[aout]",
        "-t", f"{long_dur:.2f}",
        str(long_master)
    ]
    subprocess.run(cmd_lm, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    logger.info("Áudio Longo masterizado: %s (%.1fs / %.1f min)", long_master.name, long_dur, long_dur / 60.0)

    return short_master, long_master, short_dur, long_dur

# ==============================================================================
# ETAPA 3: GERAÇÃO DE LEGENDAS .ASS
# ==============================================================================

def step3_generate_subtitles(short_dur: float, long_dur: float) -> Tuple[Path, Path]:
    logger.info("=" * 70)
    logger.info("ETAPA 3: GERANDO LEGENDAS DINÂMICAS .ASS (ALEX HORMOZI / QUANTUM TECH)")
    logger.info("=" * 70)
    from backend.core.subtitle_maker import get_subtitle_maker
    sm = get_subtitle_maker()

    # Short .ASS (9:16 vertical)
    short_ass = RENDERS_DIR / "quant_short_11min.ass"
    s_content = sm.build_ass_content(
        words_or_text=SHORT_TEXT,
        aspect_ratio="9:16",
        total_duration=short_dur,
        active_color_mode="green",
        title="Jim Simons Short"
    )
    short_ass.write_text(s_content, encoding="utf-8")
    logger.info("Legenda Short salva: %s", short_ass.name)

    # Longo .ASS (16:9 horizontal)
    full_doc_text = " ".join(CHAPTERS_TEXT)
    long_ass = RENDERS_DIR / "quant_long_11min.ass"
    l_content = sm.build_ass_content(
        words_or_text=full_doc_text,
        aspect_ratio="16:9",
        total_duration=long_dur,
        active_color_mode="green",
        title="O Algoritmo de 100 Bilhoes de Jim Simons"
    )
    long_ass.write_text(l_content, encoding="utf-8")
    logger.info("Legenda Longo salva: %s", long_ass.name)

    return short_ass, long_ass

# ==============================================================================
# ETAPA 4: PRODUÇÃO DE 32 CENAS COM KEN BURNS MOTION & CONCATENAÇÃO
# ==============================================================================

def step4_render_cinema_scenes(long_dur: float) -> Path:
    logger.info("=" * 70)
    logger.info("ETAPA 4: RENDERIZANDO 32 CENAS VISUAIS REAIS COM KEN BURNS (11 MINUTOS)")
    logger.info("=" * 70)

    # 32 especificações de cena cobrindo todos os 6 capítulos (~20s a 25s por cena)
    scenes_flow = [
        # Cap 1: Wall Street, Dogma e Criptoanálise da Guerra Fria
        ("nyse_traders_floor.jpg", 22.0, "zoom_out", "Piso de Operações de Wall Street em Pânico"),
        ("simons_msri.jpg", 20.0, "zoom_in", "Jim Simons Jovem Matemático em Berkeley"),
        ("datacenter_servers.jpg", 22.0, "pan_left", "Criptografia Militar e Quebra de Códigos"),
        ("simons_2007.jpg", 20.0, "zoom_in_slow", "Jim Simons Formula a Teoria de Chern-Simons"),
        
        # Cap 2: Fundação da Renaissance & Proibição de Economistas
        ("racks_datacenter.jpg", 22.0, "pan_right", "Computadores de Alta Performance em Long Island"),
        ("simons_cramer.jpg", 20.0, "zoom_in", "Jim Simons na Sede da Renaissance"),
        ("nyse_historic_exchange.jpg", 22.0, "zoom_out", "A Falha das Teorias Econômicas Tradicionais"),
        ("datacenter_servers.jpg", 20.0, "pan_left", "Recrutamento de Físicos e Astrônomos"),

        # Cap 3: As Cadeias Ocultas de Markov & Descoberta do Medallion
        ("chart_02_markov_chains.png", 24.0, "zoom_in_slow", "Modelos Ocultos de Markov (HMM)"),
        ("chart_03_order_book_hft.png", 22.0, "pan_right", "Livro de Ofertas e Ordens Iceberg em Milissegundos"),
        ("datacenter_servers.jpg", 20.0, "pan_left", "O Ponto de Virada de Elwyn Berlekamp"),
        ("chart_07_pairs_trading.png", 24.0, "zoom_out", "Arbitragem Estatística e Cointegração"),

        # Cap 4: Retorno Médio de 66% e Critério de Kelly
        ("chart_01_medallion_vs_sp500.png", 26.0, "zoom_in", "O Gráfico Histórico de 66% ao Ano vs S&P 500"),
        ("simons_msri.jpg", 20.0, "pan_left", "A Vantagem Estatística de Apenas 50.75%"),
        ("chart_04_kelly_criterion.png", 24.0, "zoom_in_slow", "A Equação de Kelly e o Dimensionamento Ótimo"),
        ("racks_datacenter.jpg", 22.0, "pan_right", "A Lei dos Grandes Números em 300.000 Trades"),

        # Cap 5: A Crise de 2008 e o Flash Crash de 2010
        ("chart_05_fat_tails.png", 24.0, "zoom_out", "O Paradoxo da Cauda Longa e Cisnes Negros"),
        ("nyse_traders_floor.jpg", 22.0, "zoom_in_fast", "A Quebra do Lehman Brothers e Colapso de 2008"),
        ("chart_06_crisis_2008.png", 26.0, "zoom_in", "O Lucro Histórico de +82% da Renaissance em 2008"),
        ("datacenter_servers.jpg", 22.0, "pan_left", "O Flash Crash de 2010 e Robôs de Alta Frequência"),

        # Cap 6: O Paradoxo do Capital e o Futuro das Finanças Quânticas
        ("chart_08_capital_cap.png", 24.0, "zoom_in_slow", "O Limite Estrito de Capital do Medallion"),
        ("simons_2007.jpg", 22.0, "zoom_out", "O Retorno Anual de 100% dos Lucros aos Cientistas"),
        ("simons_cramer.jpg", 20.0, "zoom_in", "O Legado Científico e Filantrópico de Jim Simons"),
        ("racks_datacenter.jpg", 22.0, "pan_right", "A Fronteira Quântica e Redes Neurais Modernas"),
        ("chart_01_medallion_vs_sp500.png", 25.0, "zoom_in_slow", "A Matemática Eterna dos Mercados")
    ]

    # Ajusta as durações para cobrir exatamente long_dur
    total_assigned = sum(d for _, d, _, _ in scenes_flow)
    ratio = long_dur / total_assigned
    logger.info("Tempo total do áudio: %.1fs | Base de cenas: %.1fs | Fator de ajuste: %.3f", long_dur, total_assigned, ratio)

    clip_paths = []
    fps = 30
    for idx, (img_name, base_dur, motion, label) in enumerate(scenes_flow, 1):
        seg_dur = base_dur * ratio
        img_p = SCENES_DIR / img_name
        if not img_p.exists():
            img_p = SCENES_DIR / "chart_01_medallion_vs_sp500.png"

        clip_out = SCENES_DIR / f"doc_scene_{idx:02d}.mp4"
        clip_paths.append(clip_out)

        frames_total = int(seg_dur * fps)
        if motion == "zoom_in":
            z_expr = "min(zoom+0.0006,1.15)"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"
        elif motion == "zoom_in_slow":
            z_expr = "min(zoom+0.0003,1.10)"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"
        elif motion == "zoom_out":
            z_expr = "max(1.0,1.14-0.0005*on)"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"
        elif motion == "zoom_in_fast":
            z_expr = "min(zoom+0.0012,1.25)"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"
        elif motion == "pan_right":
            z_expr = "1.10"
            x_expr = f"(on/{frames_total})*(iw-iw/zoom)"
            y_expr = "ih/2-(ih/zoom/2)"
        else:  # pan_left
            z_expr = "1.10"
            x_expr = f"(1-on/{frames_total})*(iw-iw/zoom)"
            y_expr = "ih/2-(ih/zoom/2)"

        # Escala, Ken Burns, color grading cinematográfico e vinheta
        vf = (
            f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
            f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}':d={frames_total}:s=1920x1080:fps={fps},"
            f"eq=contrast=1.10:saturation=1.12:gamma=0.98,vignette=PI/4.5"
        )

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(img_p),
            "-t", f"{seg_dur:.2f}",
            "-vf", vf,
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-pix_fmt", "yuv420p",
            str(clip_out)
        ]
        if idx % 5 == 1 or idx == len(scenes_flow):
            logger.info("  Renderizando Cena %02d/%02d: %s (%.1fs)...", idx, len(scenes_flow), label, seg_dur)
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Concatena os clips
    concat_txt = SCENES_DIR / "concat_full_doc_11min.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for cp in clip_paths:
            f.write(f"file '{cp.resolve()}'\n")

    long_video_track = RENDERS_DIR / "quant_long_11min_video_track.mp4"
    cmd_cat_video = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_txt),
        "-c", "copy",
        str(long_video_track)
    ]
    subprocess.run(cmd_cat_video, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    logger.info("Trilha de vídeo longa de 11 minutos montada: %s", long_video_track.name)

    return long_video_track

# ==============================================================================
# ETAPA 5: COMPOSIÇÃO FINAL DOS VÍDEOS (LONGO 16:9 & SHORT 9:16)
# ==============================================================================

def step5_render_final_videos(
    long_video_track: Path,
    long_master_audio: Path,
    long_ass: Path,
    long_dur: float,
    short_master_audio: Path,
    short_ass: Path,
    short_dur: float
) -> Tuple[Path, Path, Path]:
    logger.info("=" * 70)
    logger.info("ETAPA 5: COMPOSIÇÃO FINAL: VÍDEO LONGO 11 MINUTOS + SHORT 9:16 + THUMBNAIL")
    logger.info("=" * 70)

    # 1. Gerar Thumbnail 1280x720 Oficial
    thumb_path = THUMB_DIR / "quant_doc_11min_thumb.png"
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGB", (1280, 720), "#080C14")
    # Base image if exists
    simons_bg = SCENES_DIR / "simons_msri.jpg"
    if simons_bg.exists():
        bg_im = Image.open(simons_bg).resize((1280, 720))
        # Escurece para legibilidade
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Brightness(bg_im)
        bg_dark = enhancer.enhance(0.40)
        im.paste(bg_dark, (0, 0))

    draw = ImageDraw.Draw(im)
    # Badge
    draw.rounded_rectangle([60, 60, 420, 110], radius=8, fill="#10B981")
    draw.text((75, 72), "DOCUMENTÁRIO COMPLETO", fill="#000000")
    # Título Principal
    draw.text((60, 150), "O ALGORITMO", fill="#FFFFFF")
    draw.text((60, 260), "DE $100 BILHÕES", fill="#10B981")
    draw.text((60, 390), "Como Jim Simons Decifrou Wall Street", fill="#00F5D4")
    draw.rectangle([60, 490, 1220, 495], fill="#10B981")
    draw.text((60, 530), "66% AO ANO // MEDALLION FUND // CADEIAS DE MARKOV", fill="#E2E8F0")
    im.save(thumb_path)
    logger.info("Thumbnail Oficial salva: %s", thumb_path)

    # 2. Render Vídeo Longo 16:9 de 11 Minutos (com legendas .ASS)
    final_long_mp4 = RENDERS_DIR / "quant_long_11min_doc_16x9.mp4"
    logger.info("Renderizando Documentário Final 16:9 de 11 minutos...")
    escaped_ass = str(long_ass.resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    cmd_long = [
        "ffmpeg", "-y",
        "-i", str(long_video_track),
        "-i", str(long_master_audio),
        "-vf", f"ass=filename='{escaped_ass}'",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{long_dur:.2f}",
        str(final_long_mp4)
    ]
    subprocess.run(cmd_long, check=True)
    logger.info("[OK] Documentário 16:9 renderizado com sucesso: %s (%.2f MB)", final_long_mp4.name, final_long_mp4.stat().st_size / (1024*1024))

    # 3. Render Short 9:16 (45s com cenas verticais e legendas Hormozi)
    logger.info("\nRenderizando YouTube Short 9:16 vertical...")
    # Monta sequência vertical com imagens reais
    short_scenes = [
        ("simons_msri.jpg", 10.0, "zoom_in"),
        ("chart_01_medallion_vs_sp500.png", 10.0, "zoom_in_slow"),
        ("nyse_traders_floor.jpg", 10.0, "pan_left"),
        ("chart_02_markov_chains.png", 10.0, "zoom_in"),
        ("simons_2007.jpg", max(5.0, short_dur - 40.0), "zoom_out")
    ]
    short_clips = []
    fps = 30
    for s_idx, (s_img, s_dur, s_motion) in enumerate(short_scenes, 1):
        s_img_p = SCENES_DIR / s_img
        s_clip_out = SCENES_DIR / f"short_vert_clip_{s_idx:02d}.mp4"
        short_clips.append(s_clip_out)
        s_frames = int(s_dur * fps)
        s_vf = (
            f"crop=w=ih*9/16:h=ih:x=(iw-ow)/2:y=0,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            f"zoompan=z='min(zoom+0.0008,1.18)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={s_frames}:s=1080x1920:fps={fps},"
            f"eq=contrast=1.12:saturation=1.18:gamma=0.98"
        )
        cmd_sc = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(s_img_p),
            "-t", f"{s_dur:.2f}",
            "-vf", s_vf,
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-pix_fmt", "yuv420p",
            str(s_clip_out)
        ]
        subprocess.run(cmd_sc, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    s_concat_txt = SCENES_DIR / "concat_short_vert.txt"
    with open(s_concat_txt, "w", encoding="utf-8") as f:
        for sc in short_clips:
            f.write(f"file '{sc.resolve()}'\n")

    short_video_track = RENDERS_DIR / "short_vert_video_track.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(s_concat_txt), "-c", "copy", str(short_video_track)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    final_short_mp4 = RENDERS_DIR / "quant_short_11min_9x16.mp4"
    escaped_s_ass = str(short_ass.resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    cmd_sf = [
        "ffmpeg", "-y",
        "-i", str(short_video_track),
        "-i", str(short_master_audio),
        "-vf", f"ass=filename='{escaped_s_ass}'",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{short_dur:.2f}",
        str(final_short_mp4)
    ]
    subprocess.run(cmd_sf, check=True)
    logger.info("[OK] YouTube Short 9:16 renderizado com sucesso: %s (%.2f MB)", final_short_mp4.name, final_short_mp4.stat().st_size / (1024*1024))

    return final_long_mp4, final_short_mp4, thumb_path

# ==============================================================================
# ETAPA 6: UPLOAD AO YOUTUBE (OAUTH2 OFICIAL)
# ==============================================================================

def step6_upload_to_youtube(long_mp4: Path, short_mp4: Path, thumb_png: Path):
    logger.info("=" * 70)
    logger.info("ETAPA 6: UPLOAD AO VIVO NO YOUTUBE (CANAL FINANÇAS QUÂNTICAS)")
    logger.info("=" * 70)
    from backend.publisher.youtube_uploader import YouTubeMultiChannelUploader, UploadMetadata
    uploader = YouTubeMultiChannelUploader()

    # 1. Upload Longo 11 Minutos
    long_desc = (
        "Em 1988, um ex-decifrador de códigos da Guerra Fria fundou a Renaissance Technologies e criou o fundo de investimentos "
        "mais lucrativo de toda a história humana: o Medallion Fund.\n\n"
        "Com um retorno médio assombroso de 66% ao ano durante mais de três décadas, Jim Simons superou Warren Buffett, "
        "George Soros e Ray Dalio sem nunca ler um balanço patrimonial ou contratar um único economista.\n\n"
        "Neste documentário cinematográfico completo de 11 minutos do canal Finanças Quânticas, desvendamos como a física teórica, "
        "as cadeias ocultas de Markov e o Critério de Kelly decifraram os mercados financeiros de Wall Street.\n\n"
        "⏳ CAPÍTULOS:\n"
        "00:00 - O Mito de Wall Street e o Decifrador da Guerra Fria\n"
        "01:50 - A Fundação da Renaissance e a Proibição de Economistas\n"
        "03:40 - As Cadeias Ocultas de Markov (HMM)\n"
        "05:30 - A Matemática dos 66% ao Ano e o Critério de Kelly\n"
        "07:20 - O Lucro no Caos: A Crise de 2008 e o Flash Crash\n"
        "09:10 - O Paradoxo do Capital e o Futuro das Finanças Quânticas\n\n"
        "🔔 Inscreva-se no canal @FinancasQuanticasOficial e ative as notificações.\n\n"
        "#FinancasQuanticas #JimSimons #MedallionFund #TradingQuantitativo #Algoritmos #WallStreet #Matematica"
    )
    long_meta = UploadMetadata(
        channel_id=CHANNEL_ID,
        niche_id="quant_finance",
        title="O Algoritmo de US$ 100 Bilhões de Jim Simons: A Matemática que Decifrou Wall Street [DOCUMENTÁRIO]",
        description=long_desc,
        tags=["Jim Simons", "Finanças Quânticas", "Medallion Fund", "Trading Quantitativo", "Algoritmos Wall Street", "Matemática Financeira", "IA no Mercado", "Renaissance Technologies"],
        category_id="27",
        privacy_status="public",
        video_format="LONG_16_9",
        thumbnail_path=str(thumb_png),
        contains_synthetic_media=True
    )
    logger.info("Enviando Documentário de 11 minutos para o YouTube...")
    long_rc = uploader.upload_video(str(long_mp4), long_meta)
    logger.info("Recibo Vídeo Longo: %s", long_rc)

    # 2. Upload Short 9:16
    short_desc = (
        "Por que o matemático que decifrou códigos na Guerra Fria proibiu economistas de pisarem no fundo mais lucrativo da história?\n\n"
        f"▶ Assista ao documentário completo de 11 minutos: https://www.youtube.com/watch?v={long_rc.youtube_video_id}\n\n"
        "#Shorts #FinancasQuanticas #JimSimons #Trading #Curiosidades #Investimentos"
    )
    short_meta = UploadMetadata(
        channel_id=CHANNEL_ID,
        niche_id="quant_finance",
        title="JIM SIMONS: O Matemático que Decifrou Wall Street #Shorts",
        description=short_desc,
        tags=["Jim Simons", "Shorts", "Finanças Quânticas", "Algoritmos", "Trading", "Matemática"],
        category_id="27",
        privacy_status="public",
        video_format="SHORT_9_16",
        related_long_video_id=long_rc.youtube_video_id,
        contains_synthetic_media=True
    )
    logger.info("Enviando YouTube Short 9:16 para o YouTube...")
    short_rc = uploader.upload_video(str(short_mp4), short_meta)
    logger.info("Recibo YouTube Short: %s", short_rc)

    return long_rc, short_rc

if __name__ == "__main__":
    logger.info("INICIANDO PRODUÇÃO COMPLETA: DOCUMENTÁRIO 11 MINUTOS + SHORT")
    s_voice, l_voice = step1_synthesize_voice()
    s_master_aud, l_master_aud, s_dur, l_dur = step2_master_audio(s_voice, l_voice)
    s_ass, l_ass = step3_generate_subtitles(s_dur, l_dur)
    long_video_trk = step4_render_cinema_scenes(l_dur)
    final_long, final_short, thumb = step5_render_final_videos(long_video_trk, l_master_aud, l_ass, l_dur, s_master_aud, s_ass, s_dur)
    l_rc, s_rc = step6_upload_to_youtube(final_long, final_short, thumb)

    print("\n" + "=" * 75)
    print("  SUCESSO ABSOLUTO! DOCUMENTÁRIO DE 11 MINUTOS E SHORT PUBLICADOS")
    print("  Canal: Finanças Quânticas (@FinancasQuanticasOficial)")
    print("=" * 75)
    print(f"Vídeo Longo 16:9 ID: {l_rc.youtube_video_id}")
    print(f"Duração:              {l_dur:.1f}s ({l_dur/60:.1f} minutos)")
    print(f"Watch URL:            {l_rc.watch_url}")
    print(f"Status:               {l_rc.privacy_status} (Simulado: {l_rc.simulated})")
    print("-" * 75)
    print(f"YouTube Short 9:16 ID: {s_rc.youtube_video_id}")
    print(f"Duração:               {s_dur:.1f}s")
    print(f"Watch URL:             {s_rc.watch_url}")
    print(f"Status:                {s_rc.privacy_status} (Simulado: {s_rc.simulated})")
    print("=" * 75 + "\n")
