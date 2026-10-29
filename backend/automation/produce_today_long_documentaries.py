"""
PRODUÇÃO E PUBLICAÇÃO IMEDIATA DOS DOCUMENTÁRIOS LONGOS DE HOJE (2026-10-18)
1. Canal #1: "O Erro de Projeto que Destruiu Chernobyl: O Segredo do Reator 4 [DOCUMENTÁRIO]" (16:9, ~8m30s)
2. Canal #2: "O Colapso do LTCM (1998): Quando Prêmios Nobel Quase Destruíram Wall Street [DOCUMENTÁRIO]" (16:9, ~9m10s)
Passa pelo AntiGarbageSentinelAgent e publica PÚBLICO (PUBLIC) no YouTube.
"""

from __future__ import annotations

import json
import logging
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("produce_long_docs")

CH1_ID = "UC8RJWr3b2pKtnU1wOhV_bDQ"
CH2_ID = "UCE6Ch6nhxI81Z6ILQIw23_Q"
VOICE_CH1 = "pNInz6obpgDQGcFmaJgB"  # Adam
VOICE_CH2 = "ErXwobaYiN019PkySvjV"  # George

AUDIO_DIR = BASE_DIR / "workspace/audio"
RENDERS_DIR = BASE_DIR / "workspace/renders"
THUMB_DIR = BASE_DIR / "workspace/thumbnails"
RAW_THUMBS_DIR = BASE_DIR / "workspace/thumbnails/raw_sources"
SCENES_DIR = BASE_DIR / "workspace/scenes"
MUSIC_DIR = BASE_DIR / "assets/music"
CH1_STATE = BASE_DIR / "workspace/automation/daily_cadence_state.json"
CH2_STATE = BASE_DIR / "workspace/automation/quant_cadence_state.json"

for d in (AUDIO_DIR, RENDERS_DIR, THUMB_DIR, RAW_THUMBS_DIR, SCENES_DIR):
    d.mkdir(parents=True, exist_ok=True)


def get_media_duration(path: Path) -> float:
    p = subprocess.run(["ffmpeg", "-i", str(path)], stderr=subprocess.PIPE, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", p.stderr)
    if m:
        return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    return 510.0


# ==============================================================================
# ROTEIROS COMPLETOS DOS DOCUMENTÁRIOS LONGOS (>8 MINUTOS)
# ==============================================================================
CHERNOBYL_CHAPTERS = [
    # Cap 1: O Teste Noturno e a Cidade Adormecida (00:00 - 01:45)
    (
        "Na madrugada de vinte e seis de abril de mil novecentos e oitenta e seis, a cidade ucraniana de Pripyat "
        "dormia sob a tranquilidade típica de uma das comunidades mais prósperas e privilegiadas da União Soviética. "
        "Fundada apenas dezesseis anos antes para abrigar os cientistas, engenheiros e operadores da Usina Nuclear Vladimir Lenin, "
        "conhecida mundialmente como Chernobyl, a cidade modelo ostentava jardins amplos, escolas modernas e um parque de diversões "
        "que estava programado para ser inaugurado no feriado de Primeiro de Maio. "
        "A menos de três quilômetros dali, no bloco quatro da usina, uma equipe de operadores preparava-se para conduzir um teste elétrico "
        "que havia sido adiado por meses: comprovar se as turbinas desacelerando poderiam fornecer energia de emergência suficiente "
        "para alimentar as bombas de água do reator durante os quarenta segundos necessários para os geradores a diesel assumirem a carga. "
        "Nenhum daqueles homens imaginava que a cadeia de decisões tomadas naquela sala de controle nas horas seguintes, "
        "combinada a uma falha fatal de projeto ocultada pelo próprio governo soviético, resultaria na pior catástrofe nuclear da história humana."
    ),
    # Cap 2: O Envenenamento por Xenônio e as Ordens Fatais (01:45 - 03:30)
    (
        "Para realizar o teste, a potência do reator RBMK-1000 precisava ser reduzida para setecentos megawatts térmicos. "
        "Porém, devido a uma exigência da rede elétrica de Kiev, o procedimento foi suspenso durante a tarde e adiado para o turno da madrugada, "
        "composto por engenheiros mais jovens e menos experientes. "
        "Quando o rebaixamento de potência finalmente começou, o reator entrou em uma armadilha química invisível conhecida como envenenamento por xenônio. "
        "O xenônio-135, um subproduto da fissão que normalmente é queimado em potências altas, começou a se acumular rapidamente no núcleo, "
        "absorvendo nêutrons como uma esponja e derrubando a potência de Chernobyl para níveis perigosamente baixos, próximos de trinta megawatts. "
        "Diante do desespero de ver o teste abortado e sob pressão implacável dos superiores que exigiam o cumprimento da meta, "
        "os operadores cometeram o erro de retirar manualmente quase todas as duzentas e onze barras de controle de absorção de nêutrons do reator, "
        "violando frontalmente as diretrizes mais básicas de margem de segurança da física nuclear."
    ),
    # Cap 3: O Botão AZ-5 e o Segredo do Grafite (03:30 - 05:15)
    (
        "À uma hora, vinte e três minutos e quatro segundos, o teste foi iniciado com o desligamento das válvulas da turbina. "
        "O fluxo de água diminuiu, o líquido residual dentro do núcleo começou a ferver violentamente e a formação de vapor — "
        "devido ao coeficiente de reatividade de vazio positivo intrínseco aos reatores RBMK — começou a gerar mais potência, criando um ciclo de realimentação térmico. "
        "Percebendo a anomalia nos sensores, às uma hora, vinte e três minutos e quarenta segundos, o operador Leonid Toptunov acionou o botão AZ-5: "
        "o protocolo de emergência máxima projetado para derrubar todas as barras de controle de volta ao núcleo e congelar a reação nuclear. "
        "Mas era ali que residia o pecado mortal da engenharia soviética. "
        "Para economizar custos de fabricação, as pontas das barras de controle de boro eram revestidas com grafite, um moderador de nêutrons. "
        "Ao entrarem no núcleo, o grafite deslocou a água e provocou um salto térmico instantâneo na base do reator, centenas de vezes superior ao suportado. "
        "Os canais de combustível entortaram pelo calor, travando as barras na metade do caminho e transformando o reator em uma bomba de vapor incontrolável."
    ),
    # Cap 4: A Explosão e os Heróis Esquecidos (05:15 - 07:00)
    (
        "À uma hora, vinte e três minutos e quarenta e quatro segundos, duas explosões brutais estilhaçaram o teto do bloco quatro. "
        "A tampa superior de concreto e aço de mil toneladas, carinhosamente chamada de Elena pelos engenheiros, "
        "foi arremessada no ar como uma moeda, rompendo todos os canais de combustível e expondo o núcleo incandescente ao céu da noite. "
        "Um feixe luminoso azulado de radiação ionizante rasgou a atmosfera. "
        "Bombeiros militares de Pripyat correram para apagar as chamas no teto de betume sem nenhuma proteção antirradiação, "
        "segurando pedaços de grafite altamente contaminado com as próprias mãos desprotegidas. "
        "Nos dias subsequentes, mineiros de Tula cavaram um túnel sob o reator em temperaturas asfixiantes para instalar uma placa de resfriamento de nitrogênio líquido, "
        "e pilotos de helicóptero lançaram toneladas de chumbo, areia e boro diretamente dentro da cratera ardente. "
        "Mais de seiscentos mil liquidadores de todas as repúblicas soviéticas foram convocados para conter o abismo radioativo, "
        "sacrificando a própria saúde para salvar a Europa continental de um desastre ainda mais inimaginável."
    ),
    # Cap 5: A Cicatriz Eterna e as Lições da Verdade (07:00 - 08:45)
    (
        "Apenas após sensores de monitoramento de radiação na Suécia dispararem alarmes a mais de mil quilômetros de distância, "
        "Moscou foi forçada a admitir publicamente o desastre para o mundo. "
        "Uma zona de exclusão de trinta quilômetros de raio foi traçada, convertendo mais de dois mil e seiscentos quilômetros quadrados "
        "em um monumento silencioso à arrogância humana e à cultura do sigilo estatal. "
        "O reator quatro foi coberto pelo sarcófago de concreto em tempo recorde e, décadas depois, pelo colossal Novo Confinamento Seguro de trinta e seis mil toneladas. "
        "Como declarou o cientista Valery Legasov antes de seu trágico suicídio: todo segredo que contamos gera uma dívida com a verdade, "
        "e cedo ou tarde essa dívida é cobrada. "
        "O legado de Chernobyl reformulou para sempre os protocolos de segurança nuclear, governança e transparência da humanidade. "
        "Inscreva-se no canal A Via da Descoberta para mais investigações documentais profundas."
    ),
]

LTCM_CHAPTERS = [
    # Cap 1: Os Reis do Olimpo Quantitativo (00:00 - 01:50)
    (
        "Em 1994, quando a tecnologia da computação começava a revolucionar os mercados globais, "
        "um seleto grupo de mentes brilhantes reuniu-se em Greenwich, Connecticut, para criar o fundo de investimentos "
        "mais reverenciado e intelectualmente intimidador de toda a história financeira: o Long-Term Capital Management, ou LTCM. "
        "Liderado por John Meriwether, o lendário e temido operador de títulos do banco Salomon Brothers, o fundo reuniu uma verdadeira elite acadêmica: "
        "professores do Instituto de Tecnologia de Massachusetts, matemáticos de Harvard e os dois maiores economistas teóricos da era moderna: "
        "Robert Merton e Myron Scholes. "
        "Três anos mais tarde, em 1997, Merton e Scholes receberiam o Prêmio Nobel de Economia justamente pelo desenvolvimento da Fórmula de Black-Scholes, "
        "o cálculo diferencial estocástico que permitiu pela primeira vez na história humana precificar opções e derivativos com precisão científica. "
        "Com investidores implorando para aportar capital e pagando as taxas mais exorbitantes de Wall Street, "
        "o LTCM parecia uma máquina perfeita, guiada pela certeza de que a matemática pura havia finalmente dominado a incerteza do capitalismo."
    ),
    # Cap 2: A Máquina de Arbitragem e o Retorno Impossível (01:50 - 03:40)
    (
        "A estratégia central do LTCM não consistia em adivinhar para onde as ações de uma empresa iriam subir ou descer. "
        "Eles operavam através da chamada arbitragem de convergência de renda fixa. "
        "Os modelos de Merton e Scholes analisavam simultaneamente milhares de títulos soberanos ao redor do mundo, "
        "identificando distorções minúsculas de spread entre títulos recém-emitidos de alta liquidez e títulos mais antigos de risco quase idêntico. "
        "Como a diferença de preço entre esses papéis costumava ser de frações microscópicas de centavo, o fundo aplicava uma ferramenta extrema: "
        "alavancagem financeira massiva. "
        "Para cada dólar de capital próprio de seus investidores, o LTCM tomava emprestados vinte, trinta e até cem dólares dos maiores bancos de investimento mundiais. "
        "Nos primeiros três anos, a estratégia operou como um relógio suíço: o fundo entregou retornos inacreditáveis de quarenta por cento ao ano, "
        "transformando os sócios em bilionários instantâneos e convencendo Wall Street de que o risco havia sido matematicamente extinto da face da Terra."
    ),
    # Cap 3: A Falha Oculta da Distribuição Normal e as Caudas Longas (03:40 - 05:30)
    (
        "No entanto, por trás da aparente perfeição daquelas equações diferenciais, escondia-se uma falha conceitual letal. "
        "Todos os modelos de risco do LTCM, incluindo o sistema Value at Risk (VaR), baseavam-se na premissa de que os retornos dos mercados financeiros "
        "distribuem-se de acordo com uma curva de sino normal gaussiana clássica. "
        "De acordo com a matemática de Merton e Scholes, a probabilidade de o fundo sofrer uma perda simultânea em todas as suas posições globais "
        "era de um evento para cada cem mil anos — o equivalente estatístico a um asteroide atingir o prédio da sede em Greenwich. "
        "O que os Prêmios Nobel ignoraram foi a realidade física das finanças: em tempos de pânico extremo, a correlação entre ativos que historicamente "
        "não tinham nenhuma relação sobe instantaneamente para um. "
        "Os mercados não possuem caudas finas; eles são dominados por eventos de caudas longas (fat tails), "
        "onde o medo coletivo destrói a racionalidade dos preços e a liquidez evapora na velocidade da luz."
    ),
    # Cap 4: O Calote Russo e a Fuga em Cascata da Liquidez (05:30 - 07:20)
    (
        "Em dezessete de agosto de mil novecentos e noventa e oito, o cisne negro perfeito materializou-se no horizonte. "
        "Abalada pela crise dos tigres asiáticos e por uma queda severa nas receitas de petróleo, a Rússia desvalorizou o rublo "
        "e declarou calote unilateral em sua dívida interna soberana de títulos GKO. "
        "O choque paralisou os investidores institucionais globais. Em pânico absoluto, bancos e fundos do planeta inteiro começaram a vender "
        "desesperadamente tudo o que possuíssem de risco para comprar títulos do Tesouro Americano de curtíssimo prazo. "
        "Os spreads que os modelos do LTCM previam que iriam se fechar começaram a se abrir de forma exponencial e violenta. "
        "Em questão de trinta dias, o capital próprio do fundo derreteu de quatro bilhões de dólares para apenas quinhentos milhões. "
        "Com posições abertas que ultrapassavam um trilhão de dólares em valor nocional de derivativos em mais de setenta e cinco mil contratos, "
        "o LTCM não conseguia liquidar suas apostas sem quebrar o preço de todos os ativos do planeta. "
        "Os maiores gênios da matemática estavam a quarenta e oito horas da insolvência absoluta."
    ),
    # Cap 5: O Resgate Secreto do Federal Reserve e o Legado de Risco (07:20 - 09:10)
    (
        "Na tarde de vinte e três de setembro de mil novecentos e noventa e oito, temendo que a liquidação forçada do LTCM "
        "arrastasse consigo todo o sistema bancário ocidental e congelasse a economia global, "
        "o presidente do Federal Reserve de Nova York, William McDonough, convocou os presidentes dos quatorze maiores bancos de Wall Street "
        "para uma reunião a portas fechadas na sede do banco central americano. "
        "Executivos do Goldman Sachs, Morgan Stanley, Merrill Lynch e JP Morgan foram colocados diante de um ultimato: "
        "ou injetavam conjuntamente três vírgula seis bilhões de dólares para assumir noventa por cento do LTCM e conduzir uma liquidação ordenada ao longo de anos, "
        "ou o colapso começaria na manhã seguinte. "
        "Os bancos concordaram com o resgate histórico, e o LTCM foi gradualmente desmontado e fechado em dois mil. "
        "O desastre provou de forma indelével que a inteligência acadêmica e os diplomas de prestígio tornam-se pó quando encontram a superalavancagem "
        "e a cegueira arrogante diante do desconhecido. "
        "Inscreva-se no canal Finanças Quânticas para continuar decifrando a verdadeira ciência dos mercados."
    ),
]


def render_long_documentary(
    channel_num: int,
    slug_prefix: str,
    chapters: List[str],
    voice_id: str,
    bgm_filename: str,
    long_title: str,
    long_desc: str,
    long_tags: List[str],
    thumb_headline_lines: Tuple[str, str, str, str],
    thumb_bg_path: Path,
) -> Dict[str, Any]:
    from backend.core.tts_engine import TTSEngine
    from backend.core.subtitle_maker import get_subtitle_maker
    from backend.agents.anti_garbage_sentinel_agent import AntiGarbageSentinelAgent
    from backend.publisher.youtube_uploader import UploadMetadata, YouTubeMultiChannelUploader
    from backend.automation.run_cadence_scheduler import get_available_cinema_assets
    from backend.automation.rebuild_and_validate_both_channels import render_single_scene_clip

    tts = TTSEngine()
    sm = get_subtitle_maker()
    ch_id = CH1_ID if channel_num == 1 else CH2_ID
    ch_name = "A Via da Descoberta" if channel_num == 1 else "Finanças Quânticas"

    logger.info("=" * 70)
    logger.info("PRODUZINDO DOCUMENTÁRIO LONGO PARA %s: '%s'", ch_name, long_title)
    logger.info("=" * 70)

    final_mp4 = RENDERS_DIR / f"{slug_prefix}_16x9.mp4"
    if final_mp4.exists() and final_mp4.stat().st_size > 10 * 1024 * 1024:
        logger.info("Vídeo Longo já renderizado em disco: %s (%.1f MB). Pulando re-renderização...", final_mp4.name, final_mp4.stat().st_size / (1024 * 1024))
        final_dur = get_media_duration(final_mp4)
    else:
        # 1. Narração dos 5 Capítulos
        chap_files: List[Path] = []
        for c_idx, c_text in enumerate(chapters, 1):
            res = tts.synthesize_speech(
                text=c_text,
                voice_id=voice_id,
                output_filename=f"{slug_prefix}_cap_{c_idx:02d}.mp3",
                force_refresh=False,
            )
            chap_files.append(Path(res["audio_path"]))

        concat_txt = AUDIO_DIR / f"{slug_prefix}_concat.txt"
        with open(concat_txt, "w", encoding="utf-8") as f:
            for cf in chap_files:
                f.write(f"file '{cf.resolve()}'\n")

        long_voice_mp3 = AUDIO_DIR / f"{slug_prefix}_voice_master.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(long_voice_mp3)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        raw_dur = get_media_duration(long_voice_mp3)

        # 2. Masterização de Áudio com Trilha & Ducking (-14 LUFS)
        bgm_path = MUSIC_DIR / bgm_filename
        long_master_wav = RENDERS_DIR / f"{slug_prefix}_master.wav"
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(long_voice_mp3),
                "-stream_loop", "-1", "-i", str(bgm_path),
                "-filter_complex",
                "[0:a]loudnorm=I=-14:TP=-1.5:LRA=11[v];[1:a]volume=-21dB[b];[v][b]amix=inputs=2:duration=first:dropout_transition=3[aout]",
                "-map", "[aout]",
                "-t", f"{raw_dur:.2f}",
                str(long_master_wav),
            ],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        final_dur = get_media_duration(long_master_wav)
        logger.info("Áudio Masterizado (-14 LUFS): %.1fs (%.2f minutos)", final_dur, final_dur / 60.0)

        # 3. Legendas .ASS Dinâmicas 16:9
        long_ass = RENDERS_DIR / f"{slug_prefix}.ass"
        color_mode = "yellow" if channel_num == 1 else "green"
        long_ass.write_text(
            sm.build_ass_content(
                words_or_text=" ".join(chapters),
                aspect_ratio="16:9",
                total_duration=final_dur,
                active_color_mode=color_mode,
                title=long_title,
            ),
            encoding="utf-8",
        )

        # 4. Renderização de 24 Cenas com Ken Burns e Vídeos em Movimento
        assets = get_available_cinema_assets(channel_num)
        num_scenes = 24
        seg_dur = final_dur / num_scenes
        motions = ["zoom_in", "pan_right", "zoom_out", "pan_left", "zoom_in_slow"]
        scenes_dir = SCENES_DIR / ("peigneur" if channel_num == 1 else "flash_crash")
        clip_paths: List[Path] = []

        for s_i in range(num_scenes):
            asset_kind, asset_path = assets[s_i % len(assets)]
            motion = motions[s_i % len(motions)]
            clip_out = scenes_dir / f"{slug_prefix}_scene_{s_i+1:02d}.mp4"
            clip_paths.append(clip_out)
            render_single_scene_clip(asset_kind, asset_path, clip_out, seg_dur, motion, aspect="16:9", fps=30)

        concat_scenes = scenes_dir / f"{slug_prefix}_scenes_concat.txt"
        with open(concat_scenes, "w", encoding="utf-8") as f:
            for cp in clip_paths:
                f.write(f"file '{cp.resolve()}'\n")

        video_track = RENDERS_DIR / f"{slug_prefix}_video_track.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_scenes), "-c", "copy", str(video_track)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )

        escaped_ass = str(long_ass.resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(video_track),
                "-i", str(long_master_wav),
                "-vf", f"ass=filename='{escaped_ass}'",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "21", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k",
                "-t", f"{final_dur:.2f}",
                str(final_mp4),
            ],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        logger.info("Vídeo Longo renderizado com sucesso: %s (%.1f MB)", final_mp4.name, final_mp4.stat().st_size / (1024 * 1024))

    # 5. Thumbnail de Alto Impacto
    from backend.media.thumbnail_maker import get_thumbnail_maker
    tm = get_thumbnail_maker()
    t_res = tm.create_thumbnail(
        headline_text=f"{thumb_headline_lines[1]} {thumb_headline_lines[2]}",
        badge_text=thumb_headline_lines[0],
        job_id=slug_prefix,
        background_image_path=str(thumb_bg_path),
        accent_color_rgb=(0, 245, 212) if channel_num == 1 else (16, 185, 129),
        topic_context=thumb_headline_lines[3],
    )
    thumb_path = Path(t_res.output_png_path)

    # 6. Auditoria AntiGarbageSentinel
    sentinel = AntiGarbageSentinelAgent()
    vote = sentinel.evaluate({"video_path": str(final_mp4), "format": "long_16x9", "min_long_duration_sec": 300.0})
    if vote.veto:
        logger.error("VETO do Sentinel para Documentário Longo: %s", vote.rationale)
        raise RuntimeError(f"Veto Sentinel: {vote.rationale}")

    # 7. Upload Oficial PÚBLICO ao YouTube
    uploader = YouTubeMultiChannelUploader()
    meta = UploadMetadata(
        channel_id=ch_id,
        niche_id="mystery_doc" if channel_num == 1 else "quant_finance",
        title=long_title[:95],
        description=long_desc,
        tags=long_tags,
        category_id="27",
        privacy_status="public",
        video_format="LONG_16_9",
        thumbnail_path=str(thumb_path),
        contains_synthetic_media=True,
    )
    logger.info("Publicando Documentário Longo Oficial ao vivo em %s...", ch_name)
    receipt = uploader.upload_video(str(final_mp4), meta)
    logger.info("SUCESSO: Documentário publicado ao vivo! Watch URL: %s", receipt.watch_url)

    return {
        "video_id": receipt.youtube_video_id,
        "watch_url": receipt.watch_url,
        "duration_sec": final_dur,
        "file_path": str(final_mp4),
        "title": long_title,
    }


def main():
    # 1. Produz e publica Chernobyl Longo (Canal 1)
    ch1_res = render_long_documentary(
        channel_num=1,
        slug_prefix="ch1_chernobyl_long_doc",
        chapters=CHERNOBYL_CHAPTERS,
        voice_id=VOICE_CH1,
        bgm_filename="gathering_darkness.mp3",
        long_title="O Erro de Projeto que Destruiu Chernobyl: O Segredo do Reator 4 [DOCUMENTÁRIO]",
        long_desc=(
            "Na madrugada de 26 de abril de 1986, um teste de segurança no reator 4 da Usina Nuclear de Chernobyl desencadeou "
            "a maior catástrofe atômica da civilização moderna.\n\n"
            "Neste documentário investigativo completo do canal A Via da Descoberta, reconstruímos minuto a minuto a física por trás "
            "do envenenamento por xenônio, o defeito mortal nas barras de grafite do botão AZ-5 e o sacrifício de 600.000 liquidadores.\n\n"
            "⏳ CAPÍTULOS:\n"
            "00:00 - O Teste Noturno e a Cidade Adormecida de Pripyat\n"
            "01:45 - O Envenenamento por Xenônio e as Ordens Fatais\n"
            "03:30 - O Botão AZ-5 e o Segredo de Estado do Grafite\n"
            "05:15 - A Explosão e os Heróis Esquecidos (Liquidadores)\n"
            "07:00 - A Cicatriz Eterna e as Lições da Verdade\n\n"
            "#AViaDaDescoberta #Chernobyl #Documentario #HistoriaReal #Ciencia #UniaoSovietica"
        ),
        long_tags=[
            "Chernobyl", "Reator 4", "Documentário Completo", "História Real", "URSS",
            "Pripyat", "Desastres da Engenharia", "A Via da Descoberta", "Ciência Proibida",
            "Botão AZ5", "Física Nuclear"
        ],
        thumb_headline_lines=("DOCUMENTÁRIO COMPLETO", "CHERNOBYL:", "REATOR 4", "O Erro Secreto de Projeto"),
        thumb_bg_path=RAW_THUMBS_DIR / "kola_borehole_real.jpg",
    )

    # 2. Produz e publica LTCM Longo (Canal 2)
    ch2_res = render_long_documentary(
        channel_num=2,
        slug_prefix="ch2_ltcm_long_doc",
        chapters=LTCM_CHAPTERS,
        voice_id=VOICE_CH2,
        bgm_filename="echoes_of_time.mp3",
        long_title="O Colapso do LTCM (1998): Quando Prêmios Nobel Quebraram Wall Street [DOCUMENTÁRIO]",
        long_desc=(
            "Em 1998, o fundo hedge Long-Term Capital Management (LTCM), gerido pelos próprios ganhadores do Prêmio Nobel "
            "de Economia que criaram a fórmula de Black-Scholes, acumulou US$ 1 trilhão em apostas e quebrou em 6 semanas.\n\n"
            "Neste documentário completo do canal Finanças Quânticas, dissecamos a matemática da arbitragem de convergência, "
            "a alavancagem suicida de 100 para 1, o calote da Rússia e a reunião secreta no Federal Reserve que salvou o capitalismo ocidental.\n\n"
            "⏳ CAPÍTULOS:\n"
            "00:00 - Os Reis do Olimpo Quantitativo\n"
            "01:50 - A Máquina de Arbitragem e o Retorno Impossível\n"
            "03:40 - A Falha Oculta da Curva Normal e Caudas Longas\n"
            "05:30 - O Calote Russo e a Fuga em Cascata da Liquidez\n"
            "07:20 - A Reunião Secreta no FED e o Resgate de US$ 3.6 Bilhões\n\n"
            "#FinancasQuanticas #LTCM #WallStreet #TradingQuantitativo #BlackScholes #Documentario"
        ),
        long_tags=[
            "LTCM", "Long Term Capital Management", "Wall Street", "Prêmio Nobel", "Black Scholes",
            "Crise de 1998", "Trading Quantitativo", "Finanças Quânticas", "Documentário",
            "Bolsa de Valores", "Hedge Funds", "Federal Reserve"
        ],
        thumb_headline_lines=("DOCUMENTÁRIO COMPLETO", "LTCM 1998:", "QUASE QUEBROU", "O Sistema Financeiro"),
        thumb_bg_path=SCENES_DIR / "flash_crash/real_photo_01_nyse_floor.jpg",
    )

    # 3. Atualiza os JSONs de estado com os novos IDs reais
    if CH1_STATE.exists():
        s1 = json.loads(CH1_STATE.read_text(encoding="utf-8"))
        for slot in s1.get("today_slots", []):
            if slot.get("slot_id") == "slot_long_01":
                slot["status"] = "published"
                slot["youtube_video_id"] = ch1_res["video_id"]
                slot["watch_url"] = ch1_res["watch_url"]
                slot["published_at"] = datetime.now(timezone.utc).isoformat()
        CH1_STATE.write_text(json.dumps(s1, indent=2, ensure_ascii=False), encoding="utf-8")

    if CH2_STATE.exists():
        s2 = json.loads(CH2_STATE.read_text(encoding="utf-8"))
        for slot in s2.get("today_slots", []):
            if slot.get("slot_id") == "slot_quant_long_01":
                slot["status"] = "published"
                slot["youtube_video_id"] = ch2_res["video_id"]
                slot["watch_url"] = ch2_res["watch_url"]
                slot["published_at"] = datetime.now(timezone.utc).isoformat()
        CH2_STATE.write_text(json.dumps(s2, indent=2, ensure_ascii=False), encoding="utf-8")

    logger.info("AMBOS OS DOCUMENTÁRIOS LONGOS FORAM PUBLICADOS AO VIVO NO YOUTUBE!")
    print("CH1 Chernobyl:", ch1_res["watch_url"])
    print("CH2 LTCM:", ch2_res["watch_url"])


if __name__ == "__main__":
    main()
