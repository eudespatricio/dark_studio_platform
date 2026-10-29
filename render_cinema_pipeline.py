"""
Motor Audiovisual de Pós-Produção Cinematográfica — Dark Studio Platform
Renderiza os vídeos de padrão Documentário / Cinema para o canal 'A Via da Descoberta':
1. Mini-Doc 16:9 (2m35s) — 9 cenas históricas reais com Ken Burns 60fps, color grading, SFX e BGM orquestral
2. Short 9:16 (45s) — Formato vertical de alta retenção no pico da tragédia
"""

import math
import os
import re
import subprocess
from pathlib import Path
from PIL import Image

BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
FFMPEG = "/home/eudespatricio/.local/bin/ffmpeg"
SCENES_DIR = BASE_DIR / "workspace" / "scenes"
RENDERS_DIR = BASE_DIR / "workspace" / "renders"
AUDIO_DIR = BASE_DIR / "workspace" / "audio"
MUSIC_DIR = BASE_DIR / "assets" / "music"
SFX_DIR = BASE_DIR / "assets" / "sfx"
THUMBS_DIR = BASE_DIR / "workspace" / "thumbnails"

RENDERS_DIR.mkdir(parents=True, exist_ok=True)
THUMBS_DIR.mkdir(parents=True, exist_ok=True)

def get_audio_duration(path: Path) -> float:
    cmd = [FFMPEG, "-i", str(path)]
    p = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", p.stderr)
    if m:
        return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    return 155.0

def main():
    print("=" * 70)
    print("  DARK STUDIO PLATFORM — RENDERIZADOR CINEMATOGRÁFICO DE DOCUMENTÁRIOS")
    print("=" * 70)

    voice_path = AUDIO_DIR / "piloto_minidoc_16x9_voice.mp3"
    if not voice_path.exists():
        print("[ERRO] Arquivo de voz não encontrado:", voice_path)
        return

    dur = get_audio_duration(voice_path)
    print(f"[OK] Duração total da locução ElevenLabs: {dur:.2f}s ({dur/60:.1f} minutos)")

    # 1. Roteiro completo do Mini-Doc
    full_text = (
        "Em 9 de outubro de 1963, exatamente às vinte e duas horas e trinta e nove minutos, "
        "os moradores do vale do Piave, no norte da Itália, foram acordados por um estrondo ensurdecedor vindo do alto das montanhas. "
        "Não era um terremoto comum. Uma massa colossal de duzentos e setenta milhões de metros cúbicos de rocha — "
        "o equivalente ao dobro do volume de toda a represa — havia se desprendido do Monte Toc e despencado em queda livre direto no reservatório de Vajont. "
        "O impacto foi tão violento que gerou uma onda de choque de ar com a força equivalente a duas bombas atômicas de Hiroshima. "
        "Segundos depois, uma muralha líquida de duzentos e cinquenta metros de altura se ergueu na escuridão, "
        "saltando por cima da represa mais alta do planeta sem que a estrutura de concreto sofresse uma única rachadura. "
        "Quatrocentos metros abaixo, a cidade de Longarone dormia em silêncio. A maioria dos habitantes não teve sequer tempo de abrir os olhos. "
        "Em menos de quatro minutos, a onda de lama e detritos engoliu ruas, casas e duas mil vidas humanas, transformando uma cidade próspera em um descampado de pedra e lama. "
        "Mas a parte mais aterrorizante dessa história não é o poder brutal da natureza. "
        "É o fato de que os engenheiros e diretores da empresa SADE sabiam exatamente que isso iria acontecer. "
        "Três anos antes do desastre, relatórios confidenciais de geólogos renomados alertavam que a encosta inteira do Monte Toc era geologicamente instável "
        "e repousava sobre uma camada escorregadia de argila. O nome Monte Toc, no dialeto local dos camponeses, significava literalmente a montanha que cai aos pedaços. "
        "Ainda assim, cegos pela ambição de erguer o maior megaprojeto hidrelétrico da Europa e faturar bilhões de liras com subsídios estatais, "
        "os executivos continuaram enchendo a represa. Quando os instrumentos de medição mostraram que a montanha estava se movendo um metro por dia, "
        "eles simplesmente falsificaram os laudos e ameaçaram de processo os jornalistas que tentavam alertar a população. "
        "Quando a montanha finalmente cedeu, a água encontrou uma barreira de concreto indestrutível — "
        "e a única rota de fuga foi descer furiosamente em direção aos inocentes. "
        "Até hoje, a Represa de Vajont permanece de pé nas Dolomitas: uma cicatriz fria de concreto que não produz uma única gota de energia, "
        "servindo apenas como um monumento perpétuo ao preço da arrogância humana."
    )

    # 2. Gerar Legendas .ASS Dinâmicas de Alta Legibilidade
    print("\n[1/5] Gerando legendas dinâmicas .ASS estilo Hormozi...")
    from backend.core.subtitle_maker import get_subtitle_maker
    sm = get_subtitle_maker()

    ass_16x9_path = RENDERS_DIR / "piloto_minidoc_16x9.ass"
    ass_16_content = sm.build_ass_content(
        words_or_text=full_text,
        aspect_ratio="16:9",
        total_duration=dur,
        active_color_mode="yellow",
        title="O Desastre da Represa de Vajont",
    )
    ass_16x9_path.write_text(ass_16_content, encoding="utf-8")
    print("      Legenda 16:9 salva em:", ass_16x9_path)

    # 3. Sequência de 9 Cenas Históricas Reais com Ken Burns Motion
    print("\n[2/5] Produzindo clips com efeito Ken Burns em fotos históricas reais de 1963...")
    scene_specs = [
        ("vajont_dam_color.jpg", 18.0, "zoom_in", "A represa mais alta do mundo"),
        ("vajont_gorge_prima.jpg", 17.0, "zoom_out", "O desfiladeiro selvagem antes da obra"),
        ("vajont_valley_1955.jpg", 17.0, "pan_right", "O vale do Piave em 1955"),
        ("vajont_dam_canyon.jpg", 18.0, "zoom_in", "A colossal muralha de 262 metros"),
        ("vajont_dam_huge.jpg", 18.0, "pan_left", "O reservatório enchendo e a montanha instável"),
        ("vajont_before_after.jpg", 17.0, "zoom_in_fast", "O desprendimento de 270 milhões de m³"),
        ("longarone_town_1963.jpg", 18.0, "zoom_out", "A cidade de Longarone antes do impacto"),
        ("longarone_disastro_1963.jpg", 18.0, "pan_right", "A devastação de lama e 2.000 mortos"),
        ("vajont_cemetery_after.jpg", max(15.0, dur - 141.0), "zoom_in", "A cicatriz eterna de concreto"),
    ]

    clip_paths = []
    for idx, (img_name, seg_dur, motion, label) in enumerate(scene_specs, 1):
        img_p = SCENES_DIR / img_name
        clip_out = SCENES_DIR / f"clip_scene_{idx:02d}.mp4"
        clip_paths.append(clip_out)

        # Monta a expressão do Ken Burns
        fps = 25
        frames_total = int(seg_dur * fps)
        if motion == "zoom_in":
            z_expr = "min(zoom+0.0007,1.15)"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"
        elif motion == "zoom_out":
            z_expr = "max(1.0,1.14-0.0007*on)"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"
        elif motion == "zoom_in_fast":
            z_expr = "min(zoom+0.0014,1.25)"
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

        # Filtro: escala para cobrir 1920x1080 -> zoompan -> vinheta suave -> leve granulação analógica
        vf = (
            f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
            f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}':d={frames_total}:s=1920x1080:fps={fps},"
            f"vignette=PI/4.5,noise=alls=6:allf=t"
        )

        cmd = [
            FFMPEG, "-y",
            "-loop", "1", "-i", str(img_p),
            "-t", f"{seg_dur:.2f}",
            "-vf", vf,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
            str(clip_out)
        ]
        print(f"      Renderizando Cena {idx}/9: {label} ({seg_dur:.1f}s)...")
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Cria lista de concat
    concat_list = SCENES_DIR / "concat_minidoc.txt"
    with open(concat_list, "w") as f:
        for p in clip_paths:
            f.write(f"file '{p.resolve()}'\n")

    # 4. Mixagem de Áudio Profissional (Sidechain Ducking + SFX Impact)
    print("\n[3/5] Masterizando áudio (-14 LUFS) + BGM Orquestral + Sound Design (SFX)...")
    bgm_path = MUSIC_DIR / "gathering_darkness.mp3"
    sfx_boom = SFX_DIR / "cinematic_sub_boom.wav"
    sfx_rumble = SFX_DIR / "landslide_rumble.wav"

    # 5. Render Final 16:9 Mini-Doc
    print("\n[4/5] Renderizando Vídeo Longo 16:9 Mini-Doc em Full HD (1920x1080)...")
    out_16x9 = RENDERS_DIR / "piloto_via_descoberta_16x9.mp4"

    # Filter complex de áudio:
    # 0: video concat
    # 1: voiceover mp3
    # 2: bgm mp3
    # 3: sfx boom (t=0s)
    # 4: sfx rumble (t=90s)
    filter_complex_16 = (
        f"[0:v]ass={ass_16x9_path}[vout];"
        f"[1:a]loudnorm=I=-14:TP=-1.5:LRA=11,asplit=2[voice_sc][voice_mix];"
        f"[2:a]volume=0.18[bgm_base];"
        f"[bgm_base][voice_sc]sidechaincompress=threshold=0.03:ratio=5:attack=30:release=350[bgm_ducked];"
        f"[3:a]volume=0.85,adelay=0|0[sfx_b];"
        f"[4:a]volume=0.75,adelay=88000|88000[sfx_r];"
        f"[voice_mix][bgm_ducked][sfx_b][sfx_r]amix=inputs=4:duration=first:dropout_transition=3[aout]"
    )

    cmd_16 = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-i", str(voice_path),
        "-i", str(bgm_path),
        "-i", str(sfx_boom),
        "-i", str(sfx_rumble),
        "-filter_complex", filter_complex_16,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", "25",
        "-c:a", "aac", "-b:a", "256k",
        "-shortest", str(out_16x9)
    ]
    subprocess.run(cmd_16, check=True)
    size_mb = out_16x9.stat().st_size / (1024 * 1024)
    print(f"      Mini-Doc 16:9 gerado: {out_16x9} ({size_mb:.2f} MB)")

    # 6. Render Final do Short 9:16 (50 segundos focados no Clímax da Onda)
    print("\n[5/5] Renderizando YouTube Short 9:16 (1080x1920) Vertical...")
    out_9x16 = RENDERS_DIR / "piloto_via_descoberta_9x16.mp4"
    ass_9x16_path = RENDERS_DIR / "piloto_minidoc_9x16.ass"

    short_text = (
        "Uma montanha inteira desabou em queda livre direto no reservatório de Vajont. "
        "O impacto gerou uma onda de choque de ar com a força de duas bombas atômicas. "
        "Uma muralha líquida de duzentos e cinquenta metros de altura saltou a represa e engoliu duas mil pessoas em minutos."
    )
    ass_9_content = sm.build_ass_content(
        words_or_text=short_text,
        aspect_ratio="9:16",
        total_duration=38.0,
        active_color_mode="yellow",
        title="O Tsunami de Vajont Short",
    )
    ass_9x16_path.write_text(ass_9_content, encoding="utf-8")

    # Short extrai o trecho mais intenso (a partir de 1m20s do vídeo longo)
    cmd_short = [
        FFMPEG, "-y",
        "-ss", "00:01:18", "-i", str(out_16x9),
        "-t", "38",
        "-vf", f"crop=ih*(9/16):ih,scale=1080:1920,ass={ass_9x16_path}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
        "-c:a", "aac", "-b:a", "192k",
        str(out_9x16)
    ]
    subprocess.run(cmd_short, check=True)
    short_mb = out_9x16.stat().st_size / (1024 * 1024)
    print(f"      Short 9:16 gerado: {out_9x16} ({short_mb:.2f} MB)")

    # 7. Nova Thumbnail de Alto Impacto
    print("\n[BÔNUS] Criando Thumbnail de Alta Performance com Foto Histórica Real...")
    from backend.media.thumbnail_maker import get_thumbnail_maker
    tm = get_thumbnail_maker()
    thumb_path = tm.create_thumbnail(
        headline_text="ONDA DE 250M!",
        badge_text="DESASTRE REAL",
        job_id="piloto_via_descoberta",
        background_image_path="/home/eudespatricio/dark_studio_platform/workspace/scenes/vajont_dam_canyon.jpg",
        accent_color_rgb=(0, 245, 212),
        topic_context="Desastre da Barragem de Vajont"
    )
    print(f"      Thumbnail gerada: {thumb_path.output_png_path}")

    print("\n" + "=" * 70)
    print("  RENDERIZAÇÃO CINEMATOGRÁFICA CONCLUÍDA COM SUCESSO!")
    print("=" * 70)

if __name__ == "__main__":
    main()
