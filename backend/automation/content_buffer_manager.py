"""
Content Buffer Manager (Estoque Antecipado de Vídeos Prontos).
Mantém uma fila de segurança de vídeos pré-renderizados, pré-legendados
e pré-auditados pelo AntiGarbageSentinelAgent no diretório `workspace/buffer/`:
- Meta de Estoque por Canal: Mínimo de 1 Longo (16:9) + 3 Shorts (9:16).
- Gatilho Automático (Refill Trigger): Se o estoque cair abaixo da meta,
  produz os próximos conteúdos em segundo plano.
- Publicação Instantânea: Ao chegar o horário de um slot, o vídeo é
  despachado do buffer em < 5 segundos sem esperar tempo de renderização.
"""

from __future__ import annotations

import json
import logging
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from backend.agents.anti_garbage_sentinel_agent import AntiGarbageSentinelAgent

logger = logging.getLogger("content_buffer_manager")
BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
BUFFER_DIR = BASE_DIR / "workspace/buffer"
BUFFER_CH1 = BUFFER_DIR / "ch1"
BUFFER_CH2 = BUFFER_DIR / "ch2"

for b in (BUFFER_CH1, BUFFER_CH2):
    b.mkdir(parents=True, exist_ok=True)


class ContentBufferManager:
    """Gerenciador de Buffer e Estoque de Conteúdo Pré-Renderizado."""

    TARGET_SHORTS = 3
    TARGET_LONGS = 1

    def get_inventory(self, channel_num: int) -> Dict[str, List[Path]]:
        ch_dir = BUFFER_CH1 if channel_num == 1 else BUFFER_CH2
        shorts = sorted(list(ch_dir.glob("*_9x16.mp4")))
        longs = sorted(list(ch_dir.glob("*_16x9.mp4")))
        return {"shorts": shorts, "longs": longs}

    def has_available_item(self, channel_num: int, video_format: str) -> Optional[Dict[str, Any]]:
        """Verifica se há um vídeo pronto no buffer para o formato desejado."""
        ch_dir = BUFFER_CH1 if channel_num == 1 else BUFFER_CH2
        pattern = "*_9x16.mp4" if "9x16" in video_format or "short" in video_format.lower() else "*_16x9.mp4"
        items = sorted(list(ch_dir.glob(pattern)))
        for mp4 in items:
            meta_file = mp4.with_suffix(".json")
            if meta_file.exists():
                try:
                    meta = json.loads(meta_file.read_text(encoding="utf-8"))
                    meta["video_path"] = str(mp4)
                    return meta
                except Exception:
                    pass
        return None

    def consume_item(self, channel_num: int, video_path: str | Path) -> None:
        """Remove o item do buffer após a publicação e arquiva o recibo."""
        p = Path(video_path)
        meta_file = p.with_suffix(".json")
        p.unlink(missing_ok=True)
        meta_file.unlink(missing_ok=True)
        logger.info("Item consumido do buffer do Canal #%d: %s", channel_num, p.name)

    def stage_into_buffer(
        self,
        channel_num: int,
        source_mp4: Path,
        title: str,
        description: str,
        tags: List[str],
        video_format: str,
        thumbnail_path: Optional[str] = None
    ) -> bool:
        """Audita com AntiGarbageSentinel e guarda o vídeo pronto no buffer com metadados."""
        sentinel = AntiGarbageSentinelAgent()
        vote = sentinel.evaluate({"video_path": str(source_mp4), "format": video_format})
        if vote.veto:
            logger.error("VETO ao tentar estocar vídeo no buffer: %s", vote.rationale)
            return False

        ch_dir = BUFFER_CH1 if channel_num == 1 else BUFFER_CH2
        dest_mp4 = ch_dir / source_mp4.name
        shutil.copy2(source_mp4, dest_mp4)

        meta = {
            "title": title,
            "description": description,
            "tags": tags,
            "video_format": video_format,
            "thumbnail_path": thumbnail_path,
            "staged_at": datetime.now(timezone.utc).isoformat(),
            "pqs_score": vote.score,
            "metrics": vote.metrics
        }
        dest_meta = dest_mp4.with_suffix(".json")
        dest_meta.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("Vídeo estocado com sucesso no buffer do Canal #%d: %s", channel_num, dest_mp4.name)
        return True


content_buffer = ContentBufferManager()
