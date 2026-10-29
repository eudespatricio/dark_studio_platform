"""
Produce and Publish Correct Short for LTCM (Canal 2 - Finanças Quânticas)
Amarrado formalmente ao Documentário Longo XLfPuc_glNU com CadenceGuardFilter ativo.
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("produce_ltcm_short")

CH2_ID = "UCE6Ch6nhxI81Z6ILQIw23_Q"
VOICE_CH2 = "ErXwobaYiN019PkySvjV"  # George
LONG_DOC_ID = "XLfPuc_glNU"
LONG_DOC_URL = f"https://www.youtube.com/watch?v={LONG_DOC_ID}"

AUDIO_DIR = BASE_DIR / "workspace/audio"
RENDERS_DIR = BASE_DIR / "workspace/renders"
MUSIC_DIR = BASE_DIR / "assets/music"
SCENES_DIR = BASE_DIR / "workspace/scenes"
CH2_STATE = BASE_DIR / "workspace/automation/quant_cadence_state.json"


def main():
    from backend.core.tts_engine import TTSEngine
    from backend.core.subtitle_maker import get_subtitle_maker
    from backend.agents.anti_garbage_sentinel_agent import AntiGarbageSentinelAgent
    from backend.publisher.youtube_uploader import UploadMetadata, YouTubeMultiChannelUploader
    from backend.automation.rebuild_and_validate_both_channels import render_single_scene_clip
    from backend.publisher.cadence_guard_filter import cadence_guard_filter

    logger.info("=== PRODUZINDO SHORT CORRETO AMARRADO AO DOCUMENTÁRIO LTCM (%s) ===", LONG_DOC_ID)

    # 1. Verifica Cooldown e Integridade via Guard Filter
    can_upload, elap, cool_msg = cadence_guard_filter.check_cooldown(CH2_ID)
    if not can_upload:
        logger.error("BLOQUEIO DE SEGURANÇA: %s", cool_msg)
        return

    tts = TTSEngine()
    sm = get_subtitle_maker()

    title = "LTCM: A Equação que Quebrou Wall Street em 1998 #Shorts"
    hook = "Dois ganhadores do Prêmio Nobel inventaram uma fórmula matemática que quase faliu o sistema financeiro mundial."
    narration = (
        "Em 1997, os economistas Robert Merton e Myron Scholes ganharam o Prêmio Nobel pela famosa fórmula de Black-Scholes. "
        "Eles fundaram o hedge fund Long-Term Capital Management, operando com alavancagem de cem para um e mais de um trilhão "
        "de dólares em derivativos. Parecia infalível, até que a Rússia decretou moratória em 1998 e os modelos ruíram em semanas, "
        "forçando o Federal Reserve a trancar os chefes de Wall Street numa sala para um resgate de três bilhões de dólares. "
        "A investigação completa sobre este colapso está no documentário aqui no canal Finanças Quânticas."
    )

    # 2. Narração ElevenLabs
    slug = "ch2_ltcm_short_correto_01"
    res_tts = tts.synthesize_speech(
        text=narration,
        voice_id=VOICE_CH2,
        output_filename=f"{slug}_voice.mp3",
        force_refresh=True,
    )
    voice_path = Path(res_tts["audio_path"])

    # 3. Masterização de Áudio com Trilha & Ducking (-14 LUFS)
    bgm_path = MUSIC_DIR / "echoes_of_time.mp3"
    master_wav = RENDERS_DIR / f"{slug}_master.wav"
    raw_dur = float(res_tts.get("duration_sec", 42.0))
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(voice_path),
            "-stream_loop", "-1", "-i", str(bgm_path),
            "-filter_complex",
            "[0:a]loudnorm=I=-14:TP=-1.5:LRA=11[v];[1:a]volume=-22dB[b];[v][b]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "[aout]",
            "-t", f"{raw_dur:.2f}",
            str(master_wav),
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    # 4. Legendas .ASS Dinâmicas 9:16 (Verde Quântico)
    ass_path = RENDERS_DIR / f"{slug}.ass"
    ass_content = sm.build_ass_content(
        words_or_text=narration,
        aspect_ratio="9:16",
        total_duration=raw_dur,
        active_color_mode="green",
        title=title,
    )
    ass_path.write_text(ass_content, encoding="utf-8")

    # 5. Montagem de Cenas 9:16
    assets = [
        ("image", SCENES_DIR / "flash_crash/real_photo_01_nyse_floor.jpg"),
        ("image", SCENES_DIR / "quant/datacenter_servers.jpg"),
        ("image", SCENES_DIR / "flash_crash/real_photo_03_wall_street.jpg"),
        ("image", SCENES_DIR / "quant/chart_03_order_book_hft.png"),
        ("image", SCENES_DIR / "quant/chart_05_fat_tails.png"),
    ]
    num_scenes = 5
    seg_dur = raw_dur / num_scenes
    motions = ["zoom_in", "pan_right", "zoom_out", "pan_left", "zoom_in_slow"]
    scenes_dir = SCENES_DIR / "flash_crash"
    clip_paths = []
    for s_i in range(num_scenes):
        ak, ap = assets[s_i % len(assets)]
        mot = motions[s_i % len(motions)]
        c_out = scenes_dir / f"{slug}_scene_{s_i+1:02d}.mp4"
        clip_paths.append(c_out)
        render_single_scene_clip(ak, ap, c_out, seg_dur, mot, aspect="9:16", fps=30)

    concat_scenes = scenes_dir / f"{slug}_scenes_concat.txt"
    with open(concat_scenes, "w", encoding="utf-8") as f:
        for cp in clip_paths:
            f.write(f"file '{cp.resolve()}'\n")

    video_track = RENDERS_DIR / f"{slug}_video_track.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_scenes), "-c", "copy", str(video_track)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    final_mp4 = RENDERS_DIR / f"{slug}_9x16.mp4"
    escaped_ass = str(ass_path.resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(video_track),
            "-i", str(master_wav),
            "-vf", f"ass=filename='{escaped_ass}'",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "21", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-t", f"{raw_dur:.2f}",
            str(final_mp4),
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    logger.info("Short 9:16 Renderizado com Sucesso: %s (%.1f MB)", final_mp4.name, final_mp4.stat().st_size / (1024 * 1024))

    # 6. Auditoria AntiGarbageSentinel
    sentinel = AntiGarbageSentinelAgent()
    vote = sentinel.evaluate({"video_path": str(final_mp4), "format": "short_9x16"})
    if vote.veto:
        logger.error("VETO do Sentinel para Short: %s", vote.rationale)
        return

    # 7. Upload ao YouTube com Context Lock & Cadence Guard
    uploader = YouTubeMultiChannelUploader()
    desc = (
        f"{title}\n\n"
        f"{hook}\n\n"
        f"Inscreva-se no canal Finanças Quânticas para entender os modelos matemáticos que governam Wall Street.\n\n"
        f"#Shorts #FinancasQuanticas #WallStreet #LTCM #Matematica"
    )
    meta = UploadMetadata(
        channel_id=CH2_ID,
        niche_id="quant_finance",
        title=title[:95],
        description=desc,
        tags=["LTCM", "Finanças Quânticas", "Wall Street", "Prêmio Nobel", "Matemática", "Shorts"],
        category_id="27",
        privacy_status="public",
        video_format="SHORT_9_16",
        contains_synthetic_media=True,
        related_long_video_id=LONG_DOC_ID,
    )

    logger.info("Publicando Short amarrado ao documentário %s...", LONG_DOC_ID)
    receipt = uploader.upload_video(str(final_mp4), meta)

    if receipt.youtube_video_id.startswith("BLOCKED_") or receipt.simulated:
        logger.error("Falha no upload do Short: %s", receipt.error_or_warning)
        return

    logger.info("SUCESSO ABSOLUTO: Short publicado ao vivo e amarrado ao Documentário!")
    logger.info("Watch URL: %s", receipt.watch_url)
    logger.info("Long Amarrado: %s", LONG_DOC_URL)

    # 8. Atualiza o estado da cadência de Finanças Quânticas
    if CH2_STATE.exists():
        s2 = json.loads(CH2_STATE.read_text(encoding="utf-8"))
        # Atualiza slot 1 com os dados reais
        for slot in s2.get("today_slots", []):
            if slot.get("slot_id") == "slot_quant_short_01":
                slot["status"] = "published"
                slot["title"] = title
                slot["youtube_video_id"] = receipt.youtube_video_id
                slot["watch_url"] = receipt.watch_url
                slot["related_long_video_id"] = LONG_DOC_ID
                slot["published_at"] = datetime.now(timezone.utc).isoformat()
                slot["status_label"] = "PUBLICADO AO VIVO (PÚBLICO) - AMARRADO AO DOCUMENTÁRIO"
                break
        CH2_STATE.write_text(json.dumps(s2, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
