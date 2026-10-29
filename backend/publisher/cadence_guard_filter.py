"""
Cadence & Anti-Spam Guard Filter - Dark Studio Platform
Previne as 3 principais causas de estagnação e penalização algorítmica:
1. Flood Anti-Spam Throttle: Impede qualquer upload se o último vídeo no canal foi postado há menos de 90 minutos.
2. Duplicação de Conteúdo: Bloqueia re-uploads de títulos ou temas idênticos/semelhantes nos últimos 7 dias.
3. Quebra de Contexto (Context Lock): Garante que 100% dos Shorts (9:16) estejam formalmente amarrados
   ao Documentário Longo (16:9) do nicho, injetando o link na descrição, CTA na narração e comentário fixado.
4. Livro-Razão (Ledger) & Quota Circuit Breaker: Registra cada publicação de forma imutável em
   `workspace/automation/uploaded_videos_ledger.json`, evita chamadas redundantes à YouTube Data API v3
   quando em cooldown local ou `quotaExceeded`, e enfileira ações pós-upload (thumbnails/comentários)
   em `workspace/automation/pending_post_actions.json` para execução automática no reset de cota (04:00 BRT).
"""

from __future__ import annotations

import fcntl
import json
import logging
import os
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger("cadence_guard")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
CREDENTIALS_DIR = BASE_DIR / "workspace/credentials"
LEDGER_FILE = BASE_DIR / "workspace/automation/uploaded_videos_ledger.json"
QUOTA_STATE_FILE = BASE_DIR / "workspace/automation/quota_circuit_breaker.json"
PENDING_ACTIONS_FILE = BASE_DIR / "workspace/automation/pending_post_actions.json"

MIN_COOLDOWN_MINUTES = 90.0  # Regra de Ouro: Mínimo 90 minutos entre uploads por canal
DEDUPLICATION_WINDOW_DAYS = 7


def atomic_write_json(file_path: Path, data: Any, indent: int = 2) -> None:
    """Writes JSON atomically via temporary file and atomic replace with fcntl lock."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = file_path.with_suffix(f".tmp.{os.getpid()}.{datetime.now().microsecond}")
    try:
        content = json.dumps(data, indent=indent, ensure_ascii=False)
        with open(tmp_path, "w", encoding="utf-8") as f:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            except (IOError, OSError):
                pass
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            except (IOError, OSError):
                pass
        os.replace(tmp_path, file_path)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise


class CadenceGuardException(Exception):
    """Exceção levantada quando uma regra do Cadence Guard é violada."""
    pass


class CooldownViolationError(CadenceGuardException):
    """Violação do intervalo mínimo de 90 minutos (Anti-Spam)."""
    pass


class DuplicateContentError(CadenceGuardException):
    """Tentativa de publicar conteúdo duplicado nos últimos 7 dias."""
    pass


class ContextLockError(CadenceGuardException):
    """Short sem documento longo amarrado."""
    pass


class CadenceGuardFilter:
    """Guarda arquitetural de integridade de cadência, quota circuit-breaker e funnel."""

    def __init__(self):
        self._ensure_ledger_exists()
        self._ensure_pending_actions_exists()
        self._api_cache: Dict[str, Tuple[float, Any]] = {}

    def _ensure_ledger_exists(self) -> None:
        if not LEDGER_FILE.exists():
            initial_data = {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "description": "Livro-razão imutável de publicações e vinculações Long-Short",
                "uploads": []
            }
            LEDGER_FILE.parent.mkdir(parents=True, exist_ok=True)
            atomic_write_json(LEDGER_FILE, initial_data)

    def _ensure_pending_actions_exists(self) -> None:
        if not PENDING_ACTIONS_FILE.exists():
            PENDING_ACTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
            atomic_write_json(
                PENDING_ACTIONS_FILE,
                {"updated_at": datetime.now(timezone.utc).isoformat(), "actions": []},
            )

    # ==========================================================================
    # QUOTA CIRCUIT BREAKER (Previne 14.400 chamadas/dia & Flood de 403)
    # ==========================================================================
    def _next_pacific_midnight_utc(self, from_dt: Optional[datetime] = None) -> datetime:
        """A cota da YouTube Data API reseta à meia-noite PT (07:00 UTC em PDT / 08:00 UTC em PST)."""
        now = from_dt or datetime.now(timezone.utc)
        reset_candidate = now.replace(hour=7, minute=5, second=0, microsecond=0)
        if reset_candidate <= now:
            reset_candidate += timedelta(days=1)
        return reset_candidate

    def is_quota_tripped(self) -> bool:
        """Retorna True se o circuit-breaker de cota do YouTube estiver aberto (bloqueando leituras remotas)."""
        if not QUOTA_STATE_FILE.exists():
            return False
        try:
            data = json.loads(QUOTA_STATE_FILE.read_text(encoding="utf-8"))
            if not data.get("tripped"):
                return False
            reset_at_str = data.get("reset_at_utc")
            if reset_at_str:
                reset_dt = datetime.fromisoformat(reset_at_str)
                if datetime.now(timezone.utc) >= reset_dt:
                    # Reset atingido! Fecha o disjuntor
                    atomic_write_json(
                        QUOTA_STATE_FILE,
                        {"tripped": False, "cleared_at": datetime.now(timezone.utc).isoformat()},
                    )
                    return False
            return True
        except Exception:
            return False

    def trip_quota_breaker(self, reason: str = "quotaExceeded") -> None:
        """Aciona o circuit-breaker de cota até o próximo reset oficial (04:05 BRT / 07:05 UTC)."""
        try:
            if self.is_quota_tripped():
                return
            reset_dt = self._next_pacific_midnight_utc()
            payload = {
                "tripped": True,
                "tripped_at_utc": datetime.now(timezone.utc).isoformat(),
                "reset_at_utc": reset_dt.isoformat(),
                "reason": str(reason)[:300],
            }
            QUOTA_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            atomic_write_json(QUOTA_STATE_FILE, payload)
            logger.warning(
                "⚡ [QUOTA CIRCUIT BREAKER] Cota diária da YouTube API atingida. "
                "Chamadas de leitura suspensas até %s (04:05 BRT). Operando 100%% via Ledgers Locais.",
                reset_dt.strftime("%Y-%m-%d %H:%M UTC"),
            )
        except Exception as e:
            logger.debug("Aviso ao gravar quota_circuit_breaker: %s", e)

    def has_sufficient_upload_quota(self, channel_id: str = "1", min_required: int = 1600) -> Tuple[bool, int, int]:
        """Calcula de forma local-first se há cota suficiente para um novo upload no projeto GCP do canal (custo: 1600)."""
        if self.is_quota_tripped():
            return False, 10000, 0
        try:
            now_utc = datetime.now(timezone.utc)
            cycle_today = now_utc.replace(hour=7, minute=0, second=0, microsecond=0)
            cycle_start = cycle_today if now_utc >= cycle_today else cycle_today - timedelta(days=1)
            total_limit = 10000
            units_used = 60  # baseline operacional por projeto

            cid_clean = str(channel_id).strip()
            is_p2 = cid_clean in (
                "3", "ch3", "biohack", "biohacklongevidade", "longevidade", "UCIjEnT4adPYVyi0UlrCITBA",
                "4", "ch4", "aintnohuman", "aintnohumanoficial", "music", "UCbO67ez7TKOJ8C_kpUF4t5Q",
            )
            p2_cids = {"UCIjEnT4adPYVyi0UlrCITBA", "UCbO67ez7TKOJ8C_kpUF4t5Q", "3", "4"}

            if LEDGER_FILE.exists():
                data = json.loads(LEDGER_FILE.read_text(encoding="utf-8"))
                for up in data.get("uploads", []):
                    ts = up.get("uploaded_at")
                    up_cid = str(up.get("channel_id", ""))
                    # Filtra uploads pertencentes ao mesmo projeto GCP
                    up_is_p2 = up_cid in p2_cids
                    if is_p2 != up_is_p2:
                        continue
                    if ts:
                        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        if dt >= cycle_start:
                            units_used += 1600
            remaining = max(0, total_limit - units_used)
            return (remaining >= min_required), units_used, remaining
        except Exception:
            return True, 0, 10000

    def _get_youtube_service(self, channel_id: str):
        tok = CREDENTIALS_DIR / f"{channel_id}_token.json"
        if not tok.exists():
            if channel_id in ("1", "ch_1", "ch-1", "UC8RJWr3b2pKtnU1wOhV_bDQ"):
                tok = CREDENTIALS_DIR / "UC8RJWr3b2pKtnU1wOhV_bDQ_token.json"
            elif channel_id in ("2", "ch_2", "ch-2", "UCE6Ch6nhxI81Z6ILQIw23_Q"):
                tok = CREDENTIALS_DIR / "UCE6Ch6nhxI81Z6ILQIw23_Q_token.json"
            elif channel_id in ("3", "ch_3", "ch-3", "@BioHackLongevidade", "UCIjEnT4adPYVyi0UlrCITBA"):
                for cand in ("UCIjEnT4adPYVyi0UlrCITBA_token.json", "channel_3_token.json", "token_ch3.json"):
                    if (CREDENTIALS_DIR / cand).exists():
                        tok = CREDENTIALS_DIR / cand
                        break
        if not tok.exists():
            raise FileNotFoundError(f"Token OAuth não encontrado para o canal {channel_id}")
        creds = Credentials.from_authorized_user_file(str(tok))
        if creds and creds.expired and creds.refresh_token:
            try:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                tok.write_text(creds.to_json(), encoding="utf-8")
            except Exception as ref_err:
                logger.warning("Falha ao renovar token OAuth do canal %s: %s", channel_id, ref_err)
        return build("youtube", "v3", credentials=creds, cache_discovery=False)

    def _get_latest_from_ledger(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Obtém o último upload registrado localmente (Ledger + State JSONs) a custo zero de API."""
        candidates: List[Dict[str, Any]] = []
        try:
            if LEDGER_FILE.exists():
                data = json.loads(LEDGER_FILE.read_text(encoding="utf-8"))
                for u in data.get("uploads", []):
                    if u.get("channel_id") == channel_id and u.get("uploaded_at"):
                        dt = datetime.fromisoformat(u["uploaded_at"].replace("Z", "+00:00"))
                        candidates.append({
                            "video_id": u.get("video_id", ""),
                            "title": u.get("title", ""),
                            "published_at": dt,
                        })
        except Exception:
            pass

        # Verifica também o state file diário do canal
        if channel_id in ("1", "ch_1", "ch-1", "UC8RJWr3b2pKtnU1wOhV_bDQ"):
            state_path = BASE_DIR / "workspace/automation/daily_cadence_state.json"
        elif channel_id in ("3", "ch_3", "ch-3", "@BioHackLongevidade", "UCIjEnT4adPYVyi0UlrCITBA"):
            state_path = BASE_DIR / "workspace/automation/biohack_cadence_state.json"
        elif channel_id in ("2", "ch_2", "ch-2", "UCE6Ch6nhxI81Z6ILQIw23_Q", "@FinancasQuanticasOficial"):
            state_path = BASE_DIR / "workspace/automation/quant_cadence_state.json"
        else:
            state_path = None

        try:
            if state_path and state_path.exists():
                st = json.loads(state_path.read_text(encoding="utf-8"))
                for s in st.get("today_slots", []):
                    if s.get("status") == "published" and s.get("published_at") and s.get("youtube_video_id"):
                        dt = datetime.fromisoformat(s["published_at"].replace("Z", "+00:00"))
                        candidates.append({
                            "video_id": s["youtube_video_id"],
                            "title": s.get("title", ""),
                            "published_at": dt,
                        })
        except Exception:
            pass

        if not candidates:
            return None
        candidates.sort(key=lambda x: x["published_at"], reverse=True)
        return candidates[0]

    def get_latest_upload_info(self, channel_id: str, verify_remote: bool = False) -> Optional[Dict[str, Any]]:
        """
        Obtém o upload mais recente de forma Local-First:
        1. Consulta imediatamente o Ledger Local (`uploaded_videos_ledger.json`).
        2. Se o Ledger Local já indicar que o último vídeo tem < 90 min (em cooldown) OU se `verify_remote=False`,
           retorna o dado local sem gastar cota da API do YouTube.
        3. Só consulta a API do YouTube se `verify_remote=True` E o circuit-breaker não estiver ativado.
        """
        local_latest = self._get_latest_from_ledger(channel_id)
        now = datetime.now(timezone.utc)

        if local_latest:
            elapsed_local = (now - local_latest["published_at"]).total_seconds() / 60.0
            if elapsed_local < MIN_COOLDOWN_MINUTES or not verify_remote or self.is_quota_tripped():
                return local_latest

        if not verify_remote or self.is_quota_tripped():
            return local_latest

        try:
            yt = self._get_youtube_service(channel_id)
            ch_resp = yt.channels().list(part="contentDetails", mine=True).execute()
            if not ch_resp.get("items"):
                return local_latest
            uploads_playlist_id = ch_resp["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            pl_resp = yt.playlistItems().list(part="snippet", playlistId=uploads_playlist_id, maxResults=5).execute()
            items = pl_resp.get("items", [])
            if not items:
                return local_latest

            latest = items[0]["snippet"]
            pub_at_str = latest["publishedAt"]
            pub_dt = datetime.fromisoformat(pub_at_str.replace("Z", "+00:00"))
            remote_info = {
                "video_id": latest["resourceId"]["videoId"],
                "title": latest["title"],
                "published_at": pub_dt,
            }
            if local_latest and local_latest["published_at"] > remote_info["published_at"]:
                return local_latest
            return remote_info
        except Exception as e:
            if "quotaExceeded" in str(e):
                self.trip_quota_breaker(str(e))
            else:
                logger.warning("Falha ao consultar upload recente na API do YouTube (%s): %s", channel_id, e)
            return local_latest

    def check_cooldown(
        self,
        channel_id: str,
        force_bypass: bool = False,
        verify_remote: bool = False,
    ) -> Tuple[bool, float, Optional[str]]:
        """
        Verifica se passaram pelo menos 90 minutos desde o último upload neste canal.
        Retorna: (is_allowed, elapsed_minutes, reason_or_message)
        """
        if force_bypass:
            logger.warning("[GUARD BYPASS] Cooldown bypass explicitamente solicitado.")
            return True, 999.0, "Cooldown bypass permitido por flag de override."

        info = self.get_latest_upload_info(channel_id, verify_remote=verify_remote)
        if not info:
            return True, 999.0, "Canal sem uploads recentes."

        now = datetime.now(timezone.utc)
        last_dt = info["published_at"]
        elapsed = (now - last_dt).total_seconds() / 60.0

        if elapsed < MIN_COOLDOWN_MINUTES:
            remaining = MIN_COOLDOWN_MINUTES - elapsed
            msg = (
                f"BLOQUEIO ANTI-SPAM (COOLDOWN): O último vídeo ('{info['title'][:40]}') foi publicado há "
                f"{elapsed:.1f} minutos. O intervalo mínimo é de {MIN_COOLDOWN_MINUTES:.0f} minutos. "
                f"Faltam {remaining:.1f} minutos para liberar novo upload no canal {channel_id}."
            )
            return False, elapsed, msg

        return True, elapsed, f"Cooldown aprovado: {elapsed:.1f} min decorridos."

    def check_duplicate(self, channel_id: str, candidate_title: str) -> Tuple[bool, Optional[str]]:
        """
        Verifica se o título já foi publicado nos últimos 7 dias (Ledger Local + Sync JSONs + API se disponível).
        """
        def normalize_title(t: str) -> str:
            clean = re.sub(r"[#\[\],.:!?()\"'-]", " ", t.lower())
            clean = re.sub(r"\b(shorts|short|documentario|documentário)\b", " ", clean)
            return " ".join(clean.split())

        norm_candidate = normalize_title(candidate_title)
        cand_words = set(norm_candidate.split())

        # 1. Verifica no ledger imutável
        try:
            data = json.loads(LEDGER_FILE.read_text(encoding="utf-8"))
            cutoff = datetime.now(timezone.utc) - timedelta(days=DEDUPLICATION_WINDOW_DAYS)
            for item in data.get("uploads", []):
                if item.get("channel_id") == channel_id:
                    up_dt = datetime.fromisoformat(item["uploaded_at"].replace("Z", "+00:00"))
                    if up_dt >= cutoff:
                        existing_norm = normalize_title(item["title"])
                        exist_words = set(existing_norm.split())
                        if cand_words and exist_words:
                            overlap = len(cand_words & exist_words) / float(len(cand_words | exist_words))
                            if overlap > 0.75:
                                msg = (
                                    f"DUPLICADO: Título '{candidate_title}' tem {overlap*100:.0f}% de similaridade "
                                    f"com '{item['title']}' publicado em {item['uploaded_at']}."
                                )
                                logger.warning("[GUARD VETO] %s", msg)
                                return False, msg
        except Exception as e:
            logger.warning("Falha ao checar duplicatas no ledger: %s", e)

        # 2. Verifica nos arquivos locais de sincronização do canal
        if channel_id in ("1", "ch_1", "ch-1", "UC8RJWr3b2pKtnU1wOhV_bDQ"):
            sync_file = BASE_DIR / "workspace/automation/channel_1_sync.json"
        elif channel_id in ("3", "ch_3", "ch-3", "@BioHackLongevidade", "UCIjEnT4adPYVyi0UlrCITBA"):
            sync_file = BASE_DIR / "workspace/automation/channel_3_biohack_sync.json"
        else:
            sync_file = BASE_DIR / "workspace/automation/channel_2_quant_sync.json"
        try:
            if sync_file.exists():
                sdata = json.loads(sync_file.read_text(encoding="utf-8"))
                for vid, vinfo in sdata.get("live_videos", {}).items():
                    if vinfo.get("audit_flag") == "MARKED_UNLISTED_DUPLICATE":
                        continue
                    pub_title = vinfo.get("title", "")
                    existing_norm = normalize_title(pub_title)
                    exist_words = set(existing_norm.split())
                    if cand_words and exist_words:
                        overlap = len(cand_words & exist_words) / float(len(cand_words | exist_words))
                        if overlap > 0.78:
                            msg = f"DUPLICADO LOCAL: Título '{candidate_title}' colide com vídeo ativo '{pub_title}' ({vid})."
                            logger.warning("[GUARD VETO] %s", msg)
                            return False, msg
        except Exception:
            pass

        # 3. Verifica na API apenas se o circuit breaker não estiver aberto
        if not self.is_quota_tripped():
            try:
                yt = self._get_youtube_service(channel_id)
                ch_resp = yt.channels().list(part="contentDetails", mine=True).execute()
                if ch_resp.get("items"):
                    uploads_pl = ch_resp["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
                    pl_items = yt.playlistItems().list(part="snippet", playlistId=uploads_pl, maxResults=15).execute().get("items", [])
                    for pi in pl_items:
                        pub_title = pi["snippet"]["title"]
                        existing_norm = normalize_title(pub_title)
                        exist_words = set(existing_norm.split())
                        if cand_words and exist_words:
                            overlap = len(cand_words & exist_words) / float(len(cand_words | exist_words))
                            if overlap > 0.78:
                                msg = f"DUPLICADO API: Título '{candidate_title}' é quase idêntico a vídeo recente na API ('{pub_title}')."
                                logger.warning("[GUARD VETO] %s", msg)
                                return False, msg
            except Exception as e:
                if "quotaExceeded" in str(e):
                    self.trip_quota_breaker(str(e))
                else:
                    logger.warning("Falha ao checar duplicatas na API: %s", e)

        return True, "Sem duplicatas detectadas."

    def resolve_active_long_documentary(self, channel_id: str) -> Optional[Dict[str, str]]:
        """
        Identifica dinamicamente o documentário longo (16:9) ativo do canal para amarração de contexto:
        1. Prioriza o documentário `LONG_16_9` publicado no ciclo atual do canal (`daily_cadence_state.json` / `quant_cadence_state.json`).
        2. Em seguida, busca o último `LONG_16_9` válido registrado em `uploaded_videos_ledger.json` (excluindo duplicados marcados para unlisted).
        3. Fallback para os documentários pilares de maior retenção comprovada de cada canal.
        """
        is_ch1 = channel_id in ("1", "ch_1", "ch-1", "UC8RJWr3b2pKtnU1wOhV_bDQ")
        is_ch3 = channel_id in ("3", "ch_3", "ch-3", "@BioHackLongevidade", "UCIjEnT4adPYVyi0UlrCITBA")
        unlisted_ids = {"qM_OTfIzoAE", "UvXx5NPM6I0", "nGbH-hY8B2o", "XLfPuc_glNU"}

        # 1. Verifica na grade ativa do dia
        if is_ch1:
            state_file = BASE_DIR / "workspace/automation/daily_cadence_state.json"
        elif is_ch3:
            state_file = BASE_DIR / "workspace/automation/biohack_cadence_state.json"
        else:
            state_file = BASE_DIR / "workspace/automation/quant_cadence_state.json"
        try:
            if state_file.exists():
                st = json.loads(state_file.read_text(encoding="utf-8"))
                for slot in st.get("today_slots", []):
                    if (
                        slot.get("video_format") == "LONG_16_9"
                        and slot.get("youtube_video_id")
                        and slot["youtube_video_id"] not in unlisted_ids
                    ):
                        return {
                            "long_id": slot["youtube_video_id"],
                            "title": slot.get("title", "Documentário Oficial Completo"),
                            "topic": st.get("current_topic", ""),
                        }
        except Exception:
            pass

        # 2. Verifica no Ledger de Uploads
        if is_ch1:
            target_cid = "UC8RJWr3b2pKtnU1wOhV_bDQ"
        elif is_ch3:
            target_cid = "UCIjEnT4adPYVyi0UlrCITBA"
        else:
            target_cid = "UCE6Ch6nhxI81Z6ILQIw23_Q"
        try:
            if LEDGER_FILE.exists():
                ldata = json.loads(LEDGER_FILE.read_text(encoding="utf-8"))
                long_uploads = [
                    u for u in ldata.get("uploads", [])
                    if u.get("channel_id") == target_cid
                    and u.get("format") == "LONG_16_9"
                    and u.get("video_id") not in unlisted_ids
                ]
                if long_uploads:
                    latest_long = long_uploads[-1]
                    return {
                        "long_id": latest_long["video_id"],
                        "title": latest_long.get("title", "Documentário Investigativo Completo"),
                        "topic": latest_long.get("title", ""),
                    }
        except Exception:
            pass

        # 3. Fallback para os documentários pilares validados de cada canal (100% originais e públicos)
        if is_ch1:
            return {
                "long_id": "gLS17ef32dc",
                "title": "O Erro de 14 Polegadas que Engoliu um Lago Inteiro: O Desastre do Lago Peigneur [DOCUMENTÁRIO]",
                "topic": "Lago Peigneur",
            }
        if is_ch3:
            return {
                "long_id": "UCIjEnT4adPYVyi0UlrCITBA_PILOTO",
                "title": "Autofagia Celular: O Prêmio Nobel que Descobriu Como o Corpo Se Regenera no Jejum [DOCUMENTÁRIO]",
                "topic": "Autofagia & Longevidade Celular",
            }
        return {
            "long_id": "bSNqaJ7H2VA",
            "title": "O Algoritmo de US$ 100 Bilhões de Jim Simons: A Matemática que Decifrou Wall Street [DOCUMENTÁRIO]",
            "topic": "Jim Simons & Medallion",
        }

    def enforce_context_lock(
        self,
        channel_id: str,
        video_format: str,
        title: str,
        description: str,
        related_long_video_id: Optional[str] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Para vídeos em formato SHORT (9:16), garante que estejam amarrados ao Long Documentary ativo.
        Para vídeos LONG_16_9, NÃO injeta link de outro vídeo longo para evitar auto-referência cruzada.
        """
        if video_format != "SHORT_9_16":
            return description, None

        target_long_info = self.resolve_active_long_documentary(channel_id)
        target_long_id = related_long_video_id or (target_long_info["long_id"] if target_long_info else None)

        if not target_long_id:
            raise ContextLockError(f"ERRO DE CONTEXTO: Nenhum Documentário Longo ativo encontrado para o canal {channel_id}.")

        long_watch_url = f"https://www.youtube.com/watch?v={target_long_id}"
        long_title = target_long_info["title"] if target_long_info else "o Documentário Investigativo Completo"

        context_block = (
            f"\n\n══════════════════════════════════════════════\n"
            f"🎬 ASSISTA AO DOCUMENTÁRIO COMPLETO (16:9):\n"
            f"👉 {long_watch_url}\n"
            f"Investigação completa: {long_title}\n"
            f"══════════════════════════════════════════════\n"
        )

        if target_long_id not in description:
            enhanced_desc = f"👉 Documentário Completo: {long_watch_url}\n\n{title}\n{context_block}\n{description}"
        else:
            enhanced_desc = description

        logger.info("[GUARD CONTEXT LOCK] Short '%s' formalmente amarrado ao Long %s (%s).", title[:35], target_long_id, long_watch_url)
        return enhanced_desc, target_long_id

    def enqueue_pending_action(self, action_type: str, channel_id: str, video_id: str, payload: Dict[str, Any]) -> None:
        """Enfileira ações pós-upload (thumbnail ou comentário fixado) que falharam por quotaExceeded."""
        try:
            self._ensure_pending_actions_exists()
            data = json.loads(PENDING_ACTIONS_FILE.read_text(encoding="utf-8"))
            actions = data.get("actions", [])
            # Evita duplicar a mesma ação para o mesmo vídeo
            for act in actions:
                if act.get("action_type") == action_type and act.get("video_id") == video_id and act.get("status") == "pending":
                    return
            actions.append({
                "action_type": action_type,
                "channel_id": channel_id,
                "video_id": video_id,
                "payload": payload,
                "status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
            data["actions"] = actions
            data["updated_at"] = datetime.now(timezone.utc).isoformat()
            atomic_write_json(PENDING_ACTIONS_FILE, data)
            logger.info("📌 [DEFERRED QUEUE] Ação '%s' para o vídeo %s enfileirada para execução pós-reset de cota.", action_type, video_id)
        except Exception as e:
            logger.warning("Falha ao enfileirar ação pós-upload: %s", e)

    def process_pending_post_actions(self) -> int:
        """Executa todas as ações pendentes (thumbnails e comentários) assim que a cota da API estiver disponível."""
        if self.is_quota_tripped() or not PENDING_ACTIONS_FILE.exists():
            return 0
        try:
            data = json.loads(PENDING_ACTIONS_FILE.read_text(encoding="utf-8"))
            actions = data.get("actions", [])
            completed_count = 0
            changed = False

            from googleapiclient.http import MediaFileUpload

            for act in actions:
                if act.get("status") != "pending":
                    continue

                # Evita retry frenético: espera pelo menos 10 minutos entre tentativas da mesma ação
                last_attempt = act.get("last_attempt_at")
                if last_attempt:
                    try:
                        last_dt = datetime.fromisoformat(last_attempt)
                        if (datetime.now(timezone.utc) - last_dt).total_seconds() < 600:
                            continue
                    except Exception:
                        pass

                ch_id = act["channel_id"]
                vid = act["video_id"]
                atype = act["action_type"]
                payload = act.get("payload", {})

                attempts = act.get("attempts", 0) + 1
                act["attempts"] = attempts
                act["last_attempt_at"] = datetime.now(timezone.utc).isoformat()
                changed = True

                try:
                    yt = self._get_youtube_service(ch_id)
                    if atype == "set_thumbnail":
                        tpath = payload.get("thumbnail_path")
                        if tpath and Path(tpath).exists():
                            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(tpath)).execute()
                            act["status"] = "completed"
                            act["completed_at"] = datetime.now(timezone.utc).isoformat()
                            completed_count += 1
                            logger.info("✅ [DEFERRED QUEUE] Thumbnail aplicada com sucesso no vídeo %s!", vid)
                        else:
                            act["status"] = "failed"
                            act["error"] = f"Arquivo de thumbnail não encontrado: {tpath}"
                            logger.warning("❌ [DEFERRED QUEUE] Thumbnail cancelada no vídeo %s: arquivo inexistente.", vid)
                    elif atype == "post_comment":
                        long_id = payload.get("long_video_id")
                        if long_id:
                            ok = self.post_pinned_context_comment(ch_id, vid, long_id, enqueue_on_fail=False)
                            if ok:
                                act["status"] = "completed"
                                act["completed_at"] = datetime.now(timezone.utc).isoformat()
                                completed_count += 1
                            else:
                                if attempts >= 3:
                                    act["status"] = "failed"
                                    act["error"] = "Excedido limite de 3 tentativas para fixar comentário."
                                    logger.warning("❌ [DEFERRED QUEUE] Desistindo de post_comment no vídeo %s após 3 tentativas (evita dreno de cota).", vid)
                except Exception as exc:
                    err_str = str(exc)
                    act["error"] = err_str
                    if "quotaExceeded" in err_str:
                        # Se foi falta de cota, não consome tentativa da ação
                        act["attempts"] = max(0, attempts - 1)
                        self.trip_quota_breaker(err_str)
                        break
                    
                    is_perm = any(phrase in err_str.lower() for phrase in ["insufficient permissions", "forbidden", "commentsdisabled"])
                    if is_perm or attempts >= 3:
                        act["status"] = "failed"
                        logger.warning("❌ [DEFERRED QUEUE] Ação %s no vídeo %s falhou permanentemente: %s", atype, vid, err_str)
                    else:
                        logger.warning("Aviso ao processar ação pendente (%s / %s, tentativa %d/3): %s", atype, vid, attempts, exc)

            if changed:
                data["updated_at"] = datetime.now(timezone.utc).isoformat()
                atomic_write_json(PENDING_ACTIONS_FILE, data)
            return completed_count
        except Exception as e:
            logger.warning("Erro ao processar fila de ações pós-upload: %s", e)
            return 0

    def post_pinned_context_comment(
        self,
        channel_id: str,
        short_video_id: str,
        long_video_id: str,
        enqueue_on_fail: bool = True,
    ) -> bool:
        """Posta um comentário no Short amarrando o espectador ao Documentário Longo."""
        if self.is_quota_tripped():
            if enqueue_on_fail:
                self.enqueue_pending_action(
                    "post_comment",
                    channel_id,
                    short_video_id,
                    {"long_video_id": long_video_id},
                )
            return False

        try:
            yt = self._get_youtube_service(channel_id)
            comment_text = (
                f"🎬 Assista à investigação completa no documentário oficial (16:9):\n"
                f"👉 https://www.youtube.com/watch?v={long_video_id}\n\n"
                f"Inscreva-se no canal para não perder os próximos episódios!"
            )
            body = {
                "snippet": {
                    "videoId": short_video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": comment_text
                        }
                    }
                }
            }
            res = yt.commentThreads().insert(part="snippet", body=body).execute()
            comment_id = res.get("id")
            logger.info("[GUARD COMMENT] Comentário de contexto publicado com sucesso no Short %s (Comment ID: %s)", short_video_id, comment_id)
            return True
        except Exception as e:
            err_str = str(e)
            if "quotaExceeded" in err_str:
                self.trip_quota_breaker(err_str)

            is_perm = any(phrase in err_str.lower() for phrase in ["insufficient permissions", "forbidden", "commentsdisabled"])
            if enqueue_on_fail and not is_perm:
                self.enqueue_pending_action(
                    "post_comment",
                    channel_id,
                    short_video_id,
                    {"long_video_id": long_video_id},
                )
                logger.warning("[GUARD COMMENT] Não foi possível fixar comentário imediato no Short %s (enfileirado): %s", short_video_id, e)
            else:
                logger.warning("[GUARD COMMENT] Não foi possível fixar comentário no Short %s (permanente, não enfileirado): %s", short_video_id, e)
            return False

    def record_upload(
        self,
        channel_id: str,
        video_id: str,
        title: str,
        video_format: str,
        related_long_video_id: Optional[str] = None,
        notes: str = ""
    ) -> None:
        """Registra o upload com integridade garantida no livro-razão e sincroniza com os ledgers dos canais."""
        now_iso = datetime.now(timezone.utc).isoformat()
        watch_url = (
            f"https://www.youtube.com/shorts/{video_id}"
            if video_format == "SHORT_9_16"
            else f"https://www.youtube.com/watch?v={video_id}"
        )
        try:
            data = json.loads(LEDGER_FILE.read_text(encoding="utf-8"))
            record = {
                "channel_id": channel_id,
                "video_id": video_id,
                "title": title,
                "format": video_format,
                "related_long_video_id": related_long_video_id,
                "uploaded_at": now_iso,
                "watch_url": watch_url,
                "notes": notes
            }
            data["uploads"].append(record)
            data["last_updated"] = now_iso
            atomic_write_json(LEDGER_FILE, data)
            logger.info("[GUARD LEDGER] Upload registrado no livro-razão: %s (%s)", video_id, title[:40])
        except Exception as e:
            logger.error("Erro ao gravar no ledger: %s", e)

        # Atualiza também os arquivos de sync do canal para visibilidade imediata na UI
        is_ch1 = channel_id in ("1", "ch_1", "ch-1", "UC8RJWr3b2pKtnU1wOhV_bDQ")
        is_ch3 = channel_id in ("3", "ch_3", "ch-3", "@BioHackLongevidade", "UCIjEnT4adPYVyi0UlrCITBA")
        if is_ch1:
            sync_targets = [
                BASE_DIR / "workspace/automation/channel_1_sync.json",
                BASE_DIR / "workspace/automation/channel_youtube_sync.json",
            ]
        elif is_ch3:
            sync_targets = [BASE_DIR / "workspace/automation/channel_3_biohack_sync.json"]
        elif channel_id in ("2", "ch_2", "ch-2", "UCE6Ch6nhxI81Z6ILQIw23_Q", "@FinancasQuanticasOficial"):
            sync_targets = [BASE_DIR / "workspace/automation/channel_2_quant_sync.json"]
        else:
            # Canal 4 (música) e demais: nunca poluir o sync do Ch2.
            sync_targets = []
        for sp in sync_targets:
            try:
                if sp.exists():
                    sdata = json.loads(sp.read_text(encoding="utf-8"))
                    lv = sdata.setdefault("live_videos", {})
                    if video_id not in lv:
                        lv[video_id] = {
                            "video_id": video_id,
                            "job_code": f"YT-{video_id[:6].upper()}",
                            "format_type": video_format,
                            "title": title,
                            "is_live": True,
                            "privacy_status": "public",
                            "watch_url": watch_url,
                            "studio_url": f"https://studio.youtube.com/video/{video_id}/edit",
                            "published_at": now_iso,
                            "views": 0,
                            "likes": 0,
                            "comments": 0,
                        }
                        sdata["videos_count"] = len(lv)
                        sdata["last_synced_at"] = now_iso
                        atomic_write_json(sp, sdata)
            except Exception as sync_err:
                logger.debug("Aviso ao sincronizar ledger do canal (%s): %s", sp.name, sync_err)


cadence_guard_filter = CadenceGuardFilter()
