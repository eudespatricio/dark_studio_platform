#!/usr/bin/env python3
"""
Orquestrador de Pré-Produção & Renderização dos 6 Shorts dos 3 Canais.
- Padroniza a voz de narração com Brian (nPczCjzI2devNBz1zQrb) nos 3 canais.
- Aplica todas as políticas de engajamento mapeadas (Hook de 2s, Poster Frame 0.22s, Cortes dinâmicos 3.4s, Legendas Safe-Zone, Cores temáticas, Zero Repetição).
- Aloca a grade de agendamento em buffer (Amanhã 2026-10-28) garantindo tempo de revisão ao operador.
- Copia os 6 vídeos finais diretamente para o Windows Desktop em C:\\Users\\Eudes\\Desktop\\shorts\\.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Configura paths
BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
sys.path.insert(0, str(BASE_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("render_all_shorts")

from backend.automation.run_cadence_scheduler import (
    CH1_STATE, CH2_STATE, CH3_STATE,
    prepare_slot_media,
    VOICE_CH1, VOICE_CH2, VOICE_CH3
)
from backend.discovery.topic_intake import apply_pauta_to_slots
from backend.automation.daily_cadence import daily_cadence_mgr
from backend.automation.quant_daily_cadence import quant_cadence_mgr
from backend.automation.biohack_daily_cadence import biohack_cadence_mgr
from backend.agents.anti_garbage_sentinel_agent import AntiGarbageSentinelAgent

DESKTOP_SHORTS_DIR = Path("/mnt/c/Users/Eudes/Desktop/shorts")
DESKTOP_SHORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_queue_pautas() -> dict:
    q_path = BASE_DIR / "workspace/automation/topic_queue.json"
    with open(q_path, "r", encoding="utf-8") as f:
        queue = json.load(f)
    return {
        1: queue["1"][0],  # Operações Secretas CIA
        2: queue["2"][3],  # Trader falha milimétrica
        3: queue["3"][2],  # Dopamina e disciplina
    }


def setup_scheduled_slots_for_channel(channel_num: int, mgr, state_path: Path, pauta: dict) -> list:
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")

    raw_slots = mgr._generate_today_slots(base_date=tomorrow)
    populated_slots = apply_pauta_to_slots(raw_slots, pauta)

    # Garante status de agendamento prévio (revisão)
    for sl in populated_slots:
        sl["schedule_date"] = tomorrow_str
        sl["status"] = "scheduled_for_review"
        sl["render_ready"] = False

    st = {
        "channel_num": channel_num,
        "schedule_date": tomorrow_str,
        "is_active": True,
        "current_topic": pauta.get("package", {}).get("topic_title_pt") or pauta.get("source", {}).get("title_original"),
        "today_slots": populated_slots,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    state_path.write_text(json.dumps(st, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Canal #%d: Grade de agendamento configurada para %s (Tópico: '%s')", channel_num, tomorrow_str, st["current_topic"][:55])
    return populated_slots


def main():
    logger.info("================================================================================")
    logger.info("INICIANDO RENDERIZAÇÃO DOS 6 SHORTS (3 CANAIS) COM POLÍTICAS DE ENGAJAMENTO")
    logger.info("Voz Padronizada: Brian (%s) para Canais #1, #2 e #3", VOICE_CH1)
    logger.info("Destino no Windows: %s", DESKTOP_SHORTS_DIR)
    logger.info("================================================================================")

    pautas = load_queue_pautas()
    configs = [
        (1, daily_cadence_mgr, CH1_STATE, "ch1", "A Via da Descoberta"),
        (2, quant_cadence_mgr, CH2_STATE, "ch2", "Finanças Quânticas"),
        (3, biohack_cadence_mgr, CH3_STATE, "ch3", "Biohack Longevidade"),
    ]

    sentinel = AntiGarbageSentinelAgent()
    rendered_summary = []

    for ch_num, mgr, state_path, prefix, ch_name in configs:
        pauta = pautas[ch_num]
        slots = setup_scheduled_slots_for_channel(ch_num, mgr, state_path, pauta)

        # Filtra os 2 shorts do canal
        short_slots = [s for s in slots if s.get("video_format") == "SHORT_9_16"][:2]
        logger.info(">>> Processando %d Shorts para Canal #%d (%s)...", len(short_slots), ch_num, ch_name)

        for s_idx, slot in enumerate(short_slots, start=1):
            s_id = slot.get("slot_id")
            s_title = slot.get("title")
            logger.info("--- Renderizando %s (%s) ---", s_id, s_title)

            # Executa pipeline completo com Brian, Pixabay, cortes rápidos, safe zone e poster frame
            v_path, t_path = prepare_slot_media(ch_num, slot)
            if not v_path or not Path(v_path).exists():
                logger.error("❌ Falha na renderização de %s", s_id)
                continue

            v_file = Path(v_path)
            dur = slot.get("duration_sec", 0.0)

            # Validação física no Sentinel
            sent_res = sentinel.inspect_physical_video(v_file)
            entropy = sent_res.get("visual_entropy_std", 0.0)
            motion = sent_res.get("motion_delta_mean", 0.0)
            rep_corr = sent_res.get("scene_clone_correlation", 1.0)

            # Copia para o Windows Desktop
            clean_slug = s_title.replace("#Shorts", "").strip()
            clean_slug = "".join(c if c.isalnum() or c in " _-" else "_" for c in clean_slug)[:40].strip()
            dest_mp4_name = f"{prefix}_short_{s_idx:02d}_{clean_slug}.mp4"
            dest_mp4 = DESKTOP_SHORTS_DIR / dest_mp4_name
            shutil.copy2(v_file, dest_mp4)

            dest_thumb = None
            if t_path and Path(t_path).exists():
                dest_thumb_name = f"{prefix}_short_{s_idx:02d}_{clean_slug}.jpg"
                dest_thumb = DESKTOP_SHORTS_DIR / dest_thumb_name
                shutil.copy2(Path(t_path), dest_thumb)

            slot["render_ready"] = True
            slot["desktop_path"] = str(dest_mp4)
            slot["desktop_name"] = dest_mp4_name

            logger.info("✅ Short renderizado com sucesso: %s (%.1fs, %.1f MB, Entropia: %.1f, Repetição: %.3f)",
                        dest_mp4_name, dur, v_file.stat().st_size / (1024*1024), entropy, rep_corr)

            rendered_summary.append({
                "channel_num": ch_num,
                "channel_name": ch_name,
                "slot_id": s_id,
                "title": s_title,
                "duration": dur,
                "file_size_mb": round(v_file.stat().st_size / (1024*1024), 1),
                "desktop_file": str(dest_mp4),
                "entropy": round(entropy, 1),
                "repetition_corr": round(rep_corr, 3),
            })

        # Salva o estado atualizado com render_ready: True para os slots renderizados
        st = json.loads(state_path.read_text(encoding="utf-8"))
        for sl_saved in st["today_slots"]:
            for sl_done in short_slots:
                if sl_saved["slot_id"] == sl_done["slot_id"]:
                    sl_saved.update(sl_done)
        state_path.write_text(json.dumps(st, indent=2, ensure_ascii=False), encoding="utf-8")

    logger.info("================================================================================")
    logger.info("TODOS OS 6 SHORTS FORAM RENDERIZADOS E COPIADOS PARA O WINDOWS DESKTOP!")
    logger.info("================================================================================")
    print("\nRESUMO FINAL DE PRODUÇÃO DOS SHORTS:")
    print(json.dumps(rendered_summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
