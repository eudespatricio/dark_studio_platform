"""
Script de Renderização e Publicação Real — Canal Finanças Quânticas
Canal: @FinancasQuanticasOficial (ID: UCE6Ch6nhxI81Z6ILQIw23_Q)
Produz:
1. Vídeo Longo 16:9 (1920x1080 Full HD, Narração George ElevenLabs, LUT Emerald, Thumb 1280x720)
2. Short 9:16 (1080x1920 Full HD, Legendas Hormozi Neon, Link Relacionado ao Longo)
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("quant_pipeline")

BASE_DIR = Path("/home/eudespatricio/dark_studio_platform")
AUDIO_DIR = BASE_DIR / "workspace" / "audio"
RENDERS_DIR = BASE_DIR / "workspace" / "renders"
THUMB_DIR = BASE_DIR / "workspace" / "thumbnails"

CHANNEL_ID = "UCE6Ch6nhxI81Z6ILQIw23_Q"
VOICE_ID = "ErXwobaYiN019PkySvjV" # George

LONG_TITLE = "O Algoritmo de US$ 100 Bilhões de Jim Simons: A Matemática que Decifrou Wall Street"
SHORT_TITLE = "JIM SIMONS: O Matemático que Decifrou Wall Street #Shorts"

SHORT_TEXT = (
    "Em 1988, um ex-decifrador de códigos da Guerra Fria decidiu que nunca mais tentaria "
    "prever o mercado usando teorias econômicas tradicionais. Jim Simons demitiu todos os "
    "analistas de ações e contratou apenas astrofísicos, matemáticos puros e programadores. "
    "Nascia o Medallion Fund, o fundo de investimentos mais lucrativo de toda a história humana, "
    "com um retorno médio inacreditável superior a sessenta e seis por cento ao ano. "
    "O segredo? Equações diferenciais não lineares e modelos de Markov capazes de detectar anomalias "
    "invisíveis aos olhos humanos em frações de segundo. "
    "Conheça a investigação completa no canal Finanças Quânticas."
)

LONG_TEXT = (
    "Em Wall Street, existe uma regra não escrita que dita que nenhum investidor no mundo consegue bater o mercado de forma consistente ao longo de décadas. "
    "Warren Buffett e Peter Lynch construíram suas reputações analisando balanços patrimoniais, fluxo de caixa e a psicologia humana. "
    "Mas em 1988, nos arredores de Nova York, um matemático de renome internacional e ex-decifrador de códigos do Departamento de Defesa americano decidiu que tudo isso era ilusão. "
    "Seu nome era Jim Simons. "
    "Simons fundou a Renaissance Technologies com uma premissa radical: o comportamento dos preços dos ativos não obedece à razão econômica, mas sim a padrões probabilísticos ocultos em meio a montanhas de ruído caótico. "
    "Em vez de contratar corretores ou especialistas em finanças, Simons recrutou exclusivamente Ph.Ds em física teórica, matemática pura, criptografia e inteligência artificial. "
    "Eles criaram o lendário Medallion Fund, um algoritmo completamente autônomo que operava sem qualquer intervenção humana e que acumulou mais de cem bilhões de dólares em lucros operacionais líquidos. "
    "Entre 1988 e 2021, o Medallion gerou um retorno médio anual assombroso de sessenta e seis por cento antes das taxas, um desempenho que pulverizou qualquer outro investidor registrado na história do capitalismo global. "
    "Neste documentário exclusivo do canal Finanças Quânticas, desvendamos como a física quântica e as cadeias ocultas de Markov substituíram o instinto humano e revolucionaram para sempre a arquitetura dos mercados financeiros globais."
)

def step1_synthesize_audios():
    from backend.core.tts_engine import TTSEngine
    tts = TTSEngine()
    
    logger.info("1/5: Sintetizando narração do Short 9:16 com a voz do George...")
    res_short = tts.synthesize_speech(
        text=SHORT_TEXT,
        voice_id=VOICE_ID,
        output_filename="quant_short_simons_master.mp3"
    )
    short_audio = Path(res_short["audio_path"])
    logger.info("Short áudio gerado: %s (%.1fs)", short_audio, res_short.get("duration_sec", 30.0))

    logger.info("2/5: Sintetizando narração do Vídeo Longo 16:9 com a voz do George...")
    res_long = tts.synthesize_speech(
        text=LONG_TEXT,
        voice_id=VOICE_ID,
        output_filename="quant_long_simons_master.mp3"
    )
    long_audio = Path(res_long["audio_path"])
    logger.info("Longo áudio gerado: %s (%.1fs)", long_audio, res_long.get("duration_sec", 125.0))
    
    return short_audio, long_audio

def step2_generate_subtitles(short_audio: Path, long_audio: Path):
    from backend.core.subtitle_maker import SubtitleMaker
    sm = SubtitleMaker(output_dir=RENDERS_DIR)

    logger.info("3/5: Gerando legendas dinâmicas .ASS estilo Quantum Tech Neon...")
    short_ass_path = RENDERS_DIR / "quant_short_simons.ass"
    sm.generate_ass(
        words_or_text=SHORT_TEXT,
        output_path=short_ass_path,
        aspect_ratio="9:16",
        total_duration=36.0,
        active_color_mode="green",
        title="Jim Simons Short"
    )

    long_ass_path = RENDERS_DIR / "quant_long_simons.ass"
    sm.generate_ass(
        words_or_text=LONG_TEXT,
        output_path=long_ass_path,
        aspect_ratio="16:9",
        total_duration=128.0,
        active_color_mode="green",
        title="Jim Simons Documentario"
    )

    return short_ass_path, long_ass_path

def step3_render_videos(short_audio: Path, long_audio: Path, short_ass: Path, long_ass: Path):
    short_mp4 = RENDERS_DIR / "quant_short_simons_9x16.mp4"
    long_mp4 = RENDERS_DIR / "quant_long_simons_16x9.mp4"
    thumb_png = THUMB_DIR / "quant_long_simons_thumb.png"

    # 1. Gera Thumbnail oficial de Alto CTR com Pillow
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGB", (1280, 720), "#080c14")
    draw = ImageDraw.Draw(im)
    # Gradiente e linhas quânticas
    for y in range(720):
        c_val = int(10 + (y / 720.0) * 18)
        draw.line([(0, y), (1280, y)], fill=(8, c_val, 20))
    # Grid de dados
    for x in range(0, 1280, 40):
        draw.line([(x, 0), (x, 720)], fill=(16, 185, 129, 30))
    # Box de badge
    draw.rounded_rectangle([80, 70, 360, 115], radius=8, fill="#10B981")
    draw.text((95, 80), "FINANÇAS QUANTICAS", fill="#000000")
    # Texto principal
    draw.text((80, 160), "O ALGORITMO", fill="#FFFFFF")
    draw.text((80, 260), "DE $100 BILHÕES", fill="#10B981")
    draw.text((80, 380), "Como Jim Simons Decifrou Wall Street", fill="#00F5D4")
    draw.rectangle([80, 480, 1200, 484], fill="#10B981")
    draw.text((80, 520), "66% AO ANO // MEDALLION FUND // MODELOS DE MARKOV", fill="#94A3B8")
    im.save(thumb_png)
    logger.info("Thumbnail salva em %s", thumb_png)

    # 2. Render Short 9:16 (1080x1920)
    logger.info("Renderizando Short 9:16 com FFmpeg...")
    # Usa color cinemático com ruído e matriz esmeralda
    cmd_short = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x080c14:s=1080x1920:r=30",
        "-i", str(short_audio),
        "-filter_complex",
        f"[0:v]geq=r='10+random(1)*15':g='18+random(1)*35':b='14+random(1)*20',eq=contrast=1.15:saturation=1.2,ass={short_ass}[vout];[1:a]loudnorm=I=-14:TP=-1.5:LRA=11[aout]",
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-t", "36.0",
        str(short_mp4)
    ]
    subprocess.run(cmd_short, check=True)
    logger.info("Short 9:16 renderizado com sucesso: %s (%.2f MB)", short_mp4, short_mp4.stat().st_size / (1024*1024))

    # 3. Render Long 16:9 (1920x1080)
    logger.info("Renderizando Long 16:9 com FFmpeg...")
    cmd_long = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x080c14:s=1920x1080:r=30",
        "-i", str(long_audio),
        "-filter_complex",
        f"[0:v]geq=r='8+random(1)*12':g='16+random(1)*28':b='18+random(1)*22',eq=contrast=1.12:saturation=1.18,ass={long_ass}[vout];[1:a]loudnorm=I=-14:TP=-1.5:LRA=11[aout]",
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-t", "128.0",
        str(long_mp4)
    ]
    subprocess.run(cmd_long, check=True)
    logger.info("Long 16:9 renderizado com sucesso: %s (%.2f MB)", long_mp4, long_mp4.stat().st_size / (1024*1024))

    return short_mp4, long_mp4, thumb_png

def step4_upload_both(short_mp4: Path, long_mp4: Path, thumb_png: Path):
    from backend.publisher.youtube_uploader import YouTubeMultiChannelUploader, UploadMetadata
    uploader = YouTubeMultiChannelUploader()

    # 1. Upload Long 16:9
    logger.info("4/5: Enviando Documentário Longo 16:9 para o canal Finanças Quânticas...")
    long_desc = (
        "Em 1988, Jim Simons fundou o Medallion Fund com uma premissa radical: "
        "o mercado financeiro obedece a leis matemáticas e probabilidades ocultas, "
        "não a sentimentos humanos ou análises econômicas tradicionais.\n\n"
        "Com um retorno médio assombroso de 66% ao ano, o fundo gerou mais de US$ 100 bilhões "
        "em lucros operacionais líquidos. Entenda neste documentário como a física teórica, "
        "a criptografia e algoritmos de milissegundos decifraram Wall Street.\n\n"
        "⏳ CAPÍTULOS:\n"
        "00:00 - O Quebrador de Códigos da Guerra Fria\n"
        "00:45 - A Fundação da Renaissance Technologies\n"
        "01:30 - O Segredo do Medallion Fund (66% a.a.)\n"
        "02:00 - O Futuro do Mercado Quantitativo e IA\n\n"
        "🔔 Inscreva-se no canal @FinancasQuanticasOficial e ative as notificações.\n\n"
        "#FinancasQuanticas #JimSimons #TradingQuantitativo #Algoritmos #WallStreet #Matematica"
    )
    long_meta = UploadMetadata(
        channel_id=CHANNEL_ID,
        niche_id="quant_finance",
        title=LONG_TITLE,
        description=long_desc,
        tags=["Jim Simons", "Finanças Quânticas", "Medallion Fund", "Trading Quantitativo", "Algoritmos Wall Street", "Matemática Financeira", "IA no Mercado", "Renaissance Technologies"],
        category_id="27",
        privacy_status="public",
        video_format="LONG_16_9",
        thumbnail_path=str(thumb_png),
        contains_synthetic_media=True
    )
    long_receipt = uploader.upload_video(str(long_mp4), long_meta)
    logger.info("Recibo Vídeo Longo: %s", long_receipt)

    # 2. Upload Short 9:16 vinculando ao Longo
    logger.info("5/5: Enviando YouTube Short 9:16 para o canal Finanças Quânticas...")
    short_desc = (
        "O ex-decifrador de códigos que gerou 66% ao ano demitindo economistas e contratando astrofísicos.\n\n"
        f"▶ Assista ao documentário completo: https://www.youtube.com/watch?v={long_receipt.youtube_video_id}\n\n"
        "#Shorts #FinancasQuanticas #JimSimons #Trading #Curiosidades #Investimentos"
    )
    short_meta = UploadMetadata(
        channel_id=CHANNEL_ID,
        niche_id="quant_finance",
        title=SHORT_TITLE,
        description=short_desc,
        tags=["Jim Simons", "Shorts", "Finanças Quânticas", "Algoritmos", "Trading", "Matemática"],
        category_id="27",
        privacy_status="public",
        video_format="SHORT_9_16",
        related_long_video_id=long_receipt.youtube_video_id,
        contains_synthetic_media=True
    )
    short_receipt = uploader.upload_video(str(short_mp4), short_meta)
    logger.info("Recibo YouTube Short: %s", short_receipt)

    return long_receipt, short_receipt

if __name__ == "__main__":
    logger.info("Iniciando pipeline de produção real para Finanças Quânticas...")
    s_audio, l_audio = step1_synthesize_audios()
    s_ass, l_ass = step2_generate_subtitles(s_audio, l_audio)
    s_mp4, l_mp4, thumb = step3_render_videos(s_audio, l_audio, s_ass, l_ass)
    l_rc, s_rc = step4_upload_both(s_mp4, l_mp4, thumb)

    print("\n" + "="*70)
    print("  SUCESSO ABSOLUTO! VÍDEO LONGO E SHORT PUBLICADOS NO YOUTUBE")
    print("  Canal: Finanças Quânticas (@FinancasQuanticasOficial)")
    print("="*70)
    print(f"Vídeo Longo 16:9 ID: {l_rc.youtube_video_id}")
    print(f"Watch URL:            {l_rc.watch_url}")
    print(f"Status:               {l_rc.privacy_status} (Simulado: {l_rc.simulated})")
    print("-" * 70)
    print(f"YouTube Short 9:16 ID: {s_rc.youtube_video_id}")
    print(f"Watch URL:             {s_rc.watch_url}")
    print(f"Status:                {s_rc.privacy_status} (Simulado: {s_rc.simulated})")
    print("="*70 + "\n")
