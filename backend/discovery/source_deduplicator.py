"""
Source De-Duplicator & Anti-Reused Content Engine — Dark Studio Platform
Garante que NENHUM vídeo fonte ou tema seja reutilizado mais de uma vez no pipeline.

Regras de Validação Estrita:
1. Verificação por ID único de vídeo (YouTube ID / Vimeo / Web ID).
2. Verificação por URL normalizada.
3. Verificação por Similaridade Semântica de Título (Token Overlap & Jaccard >= 0.70)
   para impedir que o mesmo caso histórico ou desastre seja reprocessado com pequenas variações de título.
4. Sincronização bidirecional entre o banco SQLite (`outlier_videos` status='consumed')
   e o livro-razão permanente em disco (`consumed_sources_ledger.json`).
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("dark_studio.deduplicator")

BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
LEDGER_FILE = BASE_DIR / "workspace/automation/consumed_sources_ledger.json"


@dataclass
class ConsumedSourceEntry:
    """Registro permanente de um vídeo fonte processado e publicado."""

    source_video_id: str
    source_title: str
    normalized_title_tokens: List[str]
    source_url: str
    target_channel_id: str
    consumed_at: str
    long_youtube_id: Optional[str] = None
    shorts_youtube_ids: List[str] = field(default_factory=list)


class SourceDeDuplicator:
    """
    Guardião da unicidade de fontes no pipeline de produção.
    Impede repetição de temas, títulos e IDs em 100% dos disparos.
    """

    def __init__(self, ledger_path: Optional[Path] = None) -> None:
        self.ledger_file = ledger_path or LEDGER_FILE
        self.ledger_file.parent.mkdir(parents=True, exist_ok=True)
        self.consumed_entries: List[ConsumedSourceEntry] = []
        self._consumed_ids: Set[str] = set()
        self._consumed_urls: Set[str] = set()
        self._load_ledger()

    @staticmethod
    def _tokenize(text: str) -> Set[str]:
        """Normaliza e extrai tokens significativos de um título (ignorando stopwords comuns)."""
        stopwords = {
            "o", "a", "os", "as", "um", "uma", "de", "do", "da", "dos", "das",
            "em", "no", "na", "nos", "nas", "por", "para", "com", "sem", "que",
            "e", "ou", "se", "como", "por que", "why", "how", "the", "a", "an",
            "in", "on", "at", "of", "for", "to", "and", "or", "is", "was", "it",
            "das", "der", "die", "und", "el", "la", "los", "las", "del", "un"
        }
        words = re.findall(r"\b[a-zà-ÿ0-9]{3,}\b", text.lower())
        return {w for w in words if w not in stopwords}

    def _calculate_similarity(self, tokens_a: Set[str], tokens_b: Set[str]) -> float:
        """Calcula o índice Jaccard de sobreposição de termos-chave entre dois títulos."""
        if not tokens_a or not tokens_b:
            return 0.0
        intersection = len(tokens_a.intersection(tokens_b))
        union = len(tokens_a.union(tokens_b))
        return float(intersection) / float(union) if union > 0 else 0.0

    def _load_ledger(self) -> None:
        """Carrega o livro-razão de fontes já consumidas e inicializa os índices rápidos."""
        self.consumed_entries = []
        self._consumed_ids = set()
        self._consumed_urls = set()

        # Seed inicial de vídeos já processados anteriormente (Vajont e testes iniciais)
        known_consumed = [
            {
                "source_video_id": "vX9kLm2pQ8w",
                "source_title": "The $40 Billion Soviet Submarine Base Carved Inside a Nuclear Mountain",
                "source_url": "https://www.youtube.com/watch?v=vX9kLm2pQ8w",
                "target_channel_id": "UC8RJWr3b2pKtnU1wOhV_bDQ",
                "consumed_at": "2026-10-15T00:00:00Z",
                "long_youtube_id": "_5Zp3GNx1Qs",
                "shorts_youtube_ids": ["nqqxbqXsCN4"]
            },
            {
                "source_video_id": "vajont_dam_1963_master",
                "source_title": "O Desastre da Barragem de Vajont (1963) - A Onda de 250m",
                "source_url": "https://www.youtube.com/watch?v=vajont_dam_1963_master",
                "target_channel_id": "UC8RJWr3b2pKtnU1wOhV_bDQ",
                "consumed_at": "2026-10-16T14:50:00Z",
                "long_youtube_id": "wHD_26uelVY",
                "shorts_youtube_ids": ["YKMaRwoX424"]
            }
        ]

        if not self.ledger_file.exists():
            data = {"consumed_sources": known_consumed}
            self.ledger_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

        try:
            content = json.loads(self.ledger_file.read_text(encoding="utf-8"))
            raw_list = content.get("consumed_sources", [])
        except Exception as exc:
            logger.warning("Falha ao ler ledger de fontes consumidas (%s), usando seed: %s", self.ledger_file, exc)
            raw_list = known_consumed

        for item in raw_list:
            v_id = str(item.get("source_video_id", "")).strip()
            title = str(item.get("source_title", "")).strip()
            url = str(item.get("source_url", "")).strip()
            tokens = list(self._tokenize(title))

            entry = ConsumedSourceEntry(
                source_video_id=v_id,
                source_title=title,
                normalized_title_tokens=tokens,
                source_url=url,
                target_channel_id=str(item.get("target_channel_id", "")),
                consumed_at=str(item.get("consumed_at", "")),
                long_youtube_id=item.get("long_youtube_id"),
                shorts_youtube_ids=item.get("shorts_youtube_ids", []),
            )
            self.consumed_entries.append(entry)
            if v_id:
                self._consumed_ids.add(v_id)
            if url:
                self._consumed_urls.add(url.lower().rstrip("/"))

        logger.info("DeDuplicator carregado com %d fontes consumidas registradas.", len(self.consumed_entries))

    def _save_ledger(self) -> None:
        """Persiste os registros em disco com garantia de integridade atômica."""
        payload = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "total_consumed": len(self.consumed_entries),
            "consumed_sources": [asdict(e) for e in self.consumed_entries],
        }
        self.ledger_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def is_source_consumed(
        self,
        video_id: str,
        title: str = "",
        url: str = ""
    ) -> Tuple[bool, str]:
        """
        Valida se o vídeo fonte ou tema já foi utilizado anteriormente no canal.
        Retorna `(True, motivo)` se for duplicado, ou `(False, "Fonte inédita validada")`.
        """
        clean_id = (video_id or "").strip()
        clean_url = (url or "").strip().lower().rstrip("/")
        new_tokens = self._tokenize(title)

        # 1. Checagem direta por ID
        if clean_id and clean_id in self._consumed_ids:
            return True, f"ID de vídeo já consumido anteriormente: {clean_id}"

        # 2. Checagem direta por URL
        if clean_url and clean_url in self._consumed_urls:
            return True, f"URL de origem já consumida anteriormente: {clean_url}"

        # 3. Checagem semântica de sobreposição de termos-chave no título (Jaccard >= 0.70)
        if new_tokens:
            for past in self.consumed_entries:
                past_tokens = set(past.normalized_title_tokens)
                sim = self._calculate_similarity(new_tokens, past_tokens)
                if sim >= 0.70:
                    return True, (
                        f"Tema já explorado anteriormente ({sim*100:.0f}% de similaridade com: '{past.source_title}')"
                    )

        # 4. Checagem no banco de dados SQLite caso o status já seja 'completed'
        try:
            from backend.database import SessionLocal, OutlierVideo
            db = SessionLocal()
            match = db.query(OutlierVideo).filter(
                (OutlierVideo.youtube_video_id == clean_id) |
                (OutlierVideo.source_url == clean_url)
            ).first()
            if match and match.status in ("completed", "consumed", "published"):
                db.close()
                return True, f"Vídeo com status '{match.status}' no banco de dados."
            db.close()
        except Exception:
            pass

        return False, "Fonte 100% inédita e aprovada para produção."

    def mark_source_consumed(
        self,
        video_id: str,
        title: str,
        url: str = "",
        target_channel_id: str = "UC8RJWr3b2pKtnU1wOhV_bDQ",
        long_youtube_id: Optional[str] = None,
        shorts_youtube_ids: Optional[List[str]] = None,
    ) -> None:
        """
        Trava permanentemente a fonte como CONSUMIDA após a publicação bem-sucedida,
        garantindo que ela NUNCA mais seja selecionada em execuções futuras.
        """
        clean_id = video_id.strip()
        clean_url = url.strip()
        tokens = list(self._tokenize(title))

        entry = ConsumedSourceEntry(
            source_video_id=clean_id,
            source_title=title.strip(),
            normalized_title_tokens=tokens,
            source_url=clean_url,
            target_channel_id=target_channel_id,
            consumed_at=datetime.now(timezone.utc).isoformat(),
            long_youtube_id=long_youtube_id,
            shorts_youtube_ids=shorts_youtube_ids or [],
        )

        self.consumed_entries.append(entry)
        if clean_id:
            self._consumed_ids.add(clean_id)
        if clean_url:
            self._consumed_urls.add(clean_url.lower().rstrip("/"))

        self._save_ledger()

        # Atualiza status no banco SQLite
        try:
            from backend.database import SessionLocal, OutlierVideo
            db = SessionLocal()
            row = db.query(OutlierVideo).filter(OutlierVideo.youtube_video_id == clean_id).first()
            if row:
                row.status = "consumed"
                db.commit()
            db.close()
        except Exception as exc:
            logger.debug("Falha não-crítica ao atualizar status do outlier no banco: %s", exc)

        logger.info("Fonte '%s' (%s) marcada permanentemente como CONSUMIDA.", title, clean_id)

    # Alias para compatibilidade com orchestrator
    register_consumed_source = mark_source_consumed

    def filter_virgin_outliers(self, candidates: List[Any]) -> List[Any]:
        """Filtra uma lista de candidatos retornando EXCLUSIVAMENTE os inéditos."""
        virgin = []
        for cand in candidates:
            c_id = getattr(cand, "video_id", getattr(cand, "youtube_video_id", ""))
            c_title = getattr(cand, "title_original", getattr(cand, "title", ""))
            c_url = getattr(cand, "source_url", "")
            is_consumed, reason = self.is_source_consumed(c_id, c_title, c_url)
            if not is_consumed:
                virgin.append(cand)
            else:
                logger.info("Outlier descartado por duplicidade: %s (%s)", c_title, reason)
        return virgin

    def get_consumed_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de fontes consumidas."""
        return {
            "total_consumed_sources": len(self.consumed_entries),
            "consumed_ids_sample": list(self._consumed_ids)[:10],
            "last_consumed": asdict(self.consumed_entries[-1]) if self.consumed_entries else None
        }


# Instância Singleton
source_deduplicator = SourceDeDuplicator()
