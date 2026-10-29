"""
Local Doctor with Ollama Engine for Dark Studio Platform.
Uses local GPU-accelerated Ollama (Llama 3.1) to diagnose 0-view videos
and rewrite their titles, descriptions, and tags using the Simons Formula,
saving 100% cloud API tokens.
"""

from __future__ import annotations

import json
import logging
import os
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger("local_doctor_ollama")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
CREDENTIALS_DIR = BASE_DIR / "workspace/credentials"
REWORK_LOG = BASE_DIR / "workspace/automation/rework_log.json"

CH1_ID = "UC8RJWr3b2pKtnU1wOhV_bDQ"
CH2_ID = "UCE6Ch6nhxI81Z6ILQIw23_Q"
CH3_ID = "UCIjEnT4adPYVyi0UlrCITBA"
CH4_ID = "UCbO67ez7TKOJ8C_kpUF4t5Q"


def get_ollama_host() -> str:
    """Detecta automaticamente o endpoint do Ollama local no host ou WSL."""
    env_host = os.getenv("OLLAMA_HOST", "").strip()
    if env_host:
        return env_host if env_host.startswith("http") else f"http://{env_host}"
    
    # 1. Localhost direto
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=0.5) as resp:
            if resp.status == 200:
                return "http://localhost:11434"
    except Exception:
        pass

    # 2. Host Windows via default gateway do WSL
    try:
        with open("/proc/net/route") as f:
            for line in f:
                fields = line.strip().split()
                if len(fields) >= 3 and fields[1] == "00000000":
                    ip_hex = fields[2]
                    ip = ".".join(str(int(ip_hex[i:i+2], 16)) for i in (6, 4, 2, 0))
                    with urllib.request.urlopen(f"http://{ip}:11434/api/tags", timeout=1.0) as resp:
                        if resp.status == 200:
                            return f"http://{ip}:11434"
    except Exception:
        pass

    return "http://172.30.176.1:11434"


def call_ollama(prompt: str, model: str = "llama3.1:latest", timeout: int = 40) -> str:
    """Envia prompt para o Ollama local e retorna a resposta."""
    host = get_ollama_host()
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.4,
            "top_p": 0.9,
        }
    }
    req = urllib.request.Request(
        f"{host}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res.get("response", "").strip()


def parse_rework_output(raw_text: str, current_title: str, is_short_hint: bool = True) -> Dict[str, Any]:
    """Extrai NOVO_TITULO, DESCRICAO e TAGS do texto retornado pelo Ollama."""
    new_title = ""
    description = ""
    tags = []

    m_title = re.search(r"NOVO_TITULO:\s*(.+)", raw_text, re.IGNORECASE)
    if m_title:
        new_title = m_title.group(1).strip().strip('"').strip("'")
    
    m_desc = re.search(r"DESCRICAO:\s*(.+?)(?=TAGS:|$)", raw_text, re.IGNORECASE | re.DOTALL)
    if m_desc:
        description = m_desc.group(1).strip()
    
    m_tags = re.search(r"TAGS:\s*(.+)", raw_text, re.IGNORECASE | re.DOTALL)
    if m_tags:
        raw_tags = m_tags.group(1).strip().split(",")
        tags = [t.strip().strip("#").strip() for t in raw_tags if len(t.strip()) > 1]
    
    # Se falhar no regex, fallback inteligente
    if not new_title:
        new_title = current_title
    if "#Shorts" not in new_title and ("#Shorts" in current_title or "short" in current_title.lower()):
        new_title = f"{new_title[:65]} #Shorts"
    elif not is_short_hint and "[DOCUMENTÁRIO]" not in new_title:
        new_title = f"{new_title[:75]} [DOCUMENTÁRIO]"
    
    if len(tags) < 5:
        tags = ["YouTube Shorts", "Ciência", "História", "Wall Street", "Curiosidades", "Documentário", "Fatos Reais"]

    return {
        "new_title": new_title[:95],
        "description": description or current_title,
        "tags": tags[:15]
    }


def validate_title_quality(new_title: str, current_title: str, is_short: bool) -> Tuple[bool, str]:
    """
    Validação programática de qualidade da Fórmula Simons:
    1. Rejeita títulos idênticos ou com alta similaridade (>75%).
    2. Garante comprimento de alto impacto (20 a 95 caracteres).
    3. Exige tags de formato (#Shorts ou [DOCUMENTÁRIO]).
    4. Exige gatilho numérico ou entidade factual / paradoxo de choque.
    """
    t_clean = (new_title or "").strip()
    cur_clean = (current_title or "").strip()

    if not t_clean:
        return False, "Título vazio."

    # 1. Check de Identidade exata
    if t_clean.lower() == cur_clean.lower():
        return False, "Título gerado é idêntico ao título atual."

    # 2. Similaridade de vocabulário (Jaccard)
    words_cur = set(re.findall(r"\w+", cur_clean.lower()))
    words_new = set(re.findall(r"\w+", t_clean.lower()))
    stopwords = {
        "de", "a", "o", "que", "e", "do", "da", "em", "um", "para", "é", "com",
        "não", "uma", "os", "no", "se", "na", "por", "mais", "as", "dos", "como",
        "mas", "foi", "ao", "ele", "shorts", "documentário", "documentario"
    }
    w_cur_sig = words_cur - stopwords
    w_new_sig = words_new - stopwords
    if w_cur_sig and w_new_sig:
        inter = len(w_cur_sig & w_new_sig)
        union = len(w_cur_sig | w_new_sig)
        sim = inter / union if union > 0 else 0.0
        if sim >= 0.75:
            return False, f"Similaridade excessiva com título atual ({round(sim * 100)}%). Requer novo ângulo de curiosidade."

    # 3. Comprimento
    if len(t_clean) < 20:
        return False, "Título muito curto (mínimo 20 caracteres)."
    if len(t_clean) > 95:
        return False, "Título muito longo (máximo 95 caracteres)."

    # 4. Formato e Sufixo
    if is_short:
        if "#Shorts" not in t_clean and "#shorts" not in t_clean.lower():
            return False, "Short exige tag #Shorts no título."
    else:
        if "[DOCUMENTÁRIO]" not in t_clean and "DOCUMENTÁRIO" not in t_clean.upper():
            return False, "Documentário Longo exige sufixo [DOCUMENTÁRIO]."

    # 5. Gatilho Numérico ou Palavra de Choque/Curiosidade (Fórmula Simons)
    has_number = bool(re.search(r"\d+", t_clean))
    power_keywords = [
        "SEGREDO", "ERRO", "COLAPSO", "GOLPE", "CÓDIGO", "MISTÉRIO", "IMPOSSÍVEL",
        "PROIBIDO", "DESCOBERTA", "VERDADE", "FALHA", "RISCO", "PERDA", "MILHÕES",
        "BILHÕES", "DÓLARES", "WALL STREET", "HACK", "CÉREBRO", "DOPAMINA", "URSS",
        "CIA", "TRUQUE", "EQUAÇÃO", "ANOMALIA", "INVISÍVEL"
    ]
    has_power = any(pw in t_clean.upper() for pw in power_keywords)
    if not has_number and not has_power:
        return False, "Falta âncora de alto CTR (número concreto ou palavra de impacto/risco)."

    return True, "Aprovado"


def is_in_rework_cooldown(video_id: str, cooldown_hours: float = 72.0) -> bool:
    """Verifica se o vídeo já foi retrabalhado no período de carência/cooldown."""
    if not REWORK_LOG.exists():
        return False
    try:
        history = json.loads(REWORK_LOG.read_text(encoding="utf-8"))
        now = datetime.now(timezone.utc)
        for entry in reversed(history):
            if entry.get("video_id") == video_id:
                reworked_at = entry.get("reworked_at")
                if reworked_at:
                    dt = datetime.fromisoformat(reworked_at.replace("Z", "+00:00"))
                    if (now - dt).total_seconds() < cooldown_hours * 3600.0:
                        return True
    except Exception:
        pass
    return False


def rework_video_with_ollama(channel_id: str, video_id: str, current_title: str, views: int) -> Optional[Dict[str, Any]]:
    """Gera otimização com Ollama, valida qualidade programaticamente e atualiza metadados + thumbnail."""
    tok = CREDENTIALS_DIR / f"{channel_id}_token.json"
    if not tok.exists():
        logger.error("Token não encontrado para canal %s", channel_id)
        return None

    # 1. Cooldown de 72h por vídeo
    if is_in_rework_cooldown(video_id, cooldown_hours=72.0):
        logger.info("Vídeo %s retrabalhado recentemente (< 72h). Em cooldown algorítmico do YouTube.", video_id)
        return None

    is_short = "#Shorts" in current_title or "short" in current_title.lower()
    format_str = "YouTube Shorts (9:16 vertical)" if is_short else "Documentário (16:9 widescreen)"

    base_prompt = f"""Você é o diretor de SEO e retenção algorítmica do YouTube Dark Studio.
Temos um vídeo educativo estagnado com apenas {views} visualizações.
Título atual: {current_title}
Formato: {format_str}

Aplique a Fórmula Simons de Alto CTR:
1. Âncora de entidade notória histórica, científica ou financeira (ex: cientista, usina, Wall Street, banco, KGB, etc.)
2. Número concreto extremo (ex: valores em dólares, metros, graus, segundos, porcentagens)
3. Gancho verbal de paradoxo ou risco crítico.
4. Título deve ter menos de 75 caracteres e terminar com {'#Shorts' if is_short else '[DOCUMENTÁRIO]'}.
5. Crie exatamente 13 a 15 tags de cauda longa de alta relevância separadas por vírgula.
6. Crie uma sinopse investigativa instigante de 2 a 3 linhas.

Responda rigorosamente no formato abaixo:
NOVO_TITULO: <titulo>
DESCRICAO: <sinopse>
TAGS: <tag1, tag2, tag3, ..., tag15>"""

    try:
        # 2. Loop de Auto-Retrabalho: até 3 tentativas para garantir título inédito e de alta qualidade
        parsed: Optional[Dict[str, Any]] = None
        last_reason = ""

        for attempt in range(1, 4):
            if attempt == 1:
                cur_prompt = base_prompt
            else:
                logger.info("Tentativa %d de auto-retrabalho para vídeo %s (Motivo: %s)", attempt, video_id, last_reason)
                cur_prompt = (
                    f"{base_prompt}\n\n"
                    f"⚠️ ATENÇÃO: A sugestão anterior foi REJEITADA: {last_reason}.\n"
                    f"Crie um título TOTALMENTE INÉDITO, com ângulo e vocabulário diferentes de '{current_title}'. "
                    f"Use número real e gancho instigante da Fórmula Simons!"
                )

            logger.info("Solicitando otimização ao Ollama para vídeo %s (Tentativa %d/3)...", video_id, attempt)
            raw_resp = call_ollama(cur_prompt)
            candidate = parse_rework_output(raw_resp, current_title, is_short_hint=is_short)

            valid, reason = validate_title_quality(candidate["new_title"], current_title, is_short)
            if valid:
                parsed = candidate
                logger.info("Título validado com sucesso na tentativa %d: '%s'", attempt, parsed["new_title"])
                break
            else:
                last_reason = reason
                logger.warning("Tentativa %d rejeitada pelo Quality Guard: %s ('%s')", attempt, reason, candidate["new_title"])

        if not parsed:
            logger.warning(
                "Ollama não gerou variação de qualidade suficiente para vídeo %s após 3 tentativas. "
                "Retrabalho abortado para poupar 50 unidades de cota da YouTube API.",
                video_id
            )
            return None

        # Conecta no YouTube e valida carência de 24h
        creds = Credentials.from_authorized_user_file(str(tok))
        yt = build("youtube", "v3", credentials=creds)

        v_info = yt.videos().list(part="snippet", id=video_id).execute()
        if not v_info.get("items"):
            logger.error("Vídeo %s não encontrado na API do YouTube", video_id)
            return None

        old_sn = v_info["items"][0]["snippet"]
        pub_str = old_sn.get("publishedAt")
        if pub_str:
            pub_dt = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
            elapsed_hours = (datetime.now(timezone.utc) - pub_dt).total_seconds() / 3600.0
            if elapsed_hours < 24.0:
                logger.info("Vídeo %s publicado há apenas %.1f horas (< 24h). Em carência algorítmica; retrabalho abortado para preservar indexação inicial.", video_id, elapsed_hours)
                return None

        old_desc = old_sn.get("description", "")
        # Preserva capítulos e estrutura se for documentário longo estruturado
        if "CAPÍTULOS" in old_desc or "00:00" in old_desc or len(old_desc) > 500:
            logger.info("Vídeo %s possui descrição documental rica com capítulos. Preservando capítulos e estrutura.", video_id)
            if "⏳ CAPÍTULOS:" in old_desc:
                parts = old_desc.split("⏳ CAPÍTULOS:", 1)
                final_desc = f"{parsed['description']}\n\n⏳ CAPÍTULOS:{parts[1]}".strip()
            elif "CAPÍTULOS:" in old_desc:
                parts = old_desc.split("CAPÍTULOS:", 1)
                final_desc = f"{parsed['description']}\n\nCAPÍTULOS:{parts[1]}".strip()
            else:
                final_desc = old_desc
        else:
            # Branding personalizado por nicho do canal
            if "UCE6Ch6" in channel_id or channel_id in ("2", "ch_2"):
                ch_tag = "#FinancasQuanticas #WallStreet #Investimentos #TradingQuantitativo"
            elif "UCIjEnT" in channel_id or channel_id in ("3", "ch_3"):
                ch_tag = "#BioHackLongevidade #Neurociencia #Dopamina #SaudeOtimizada"
            else:
                ch_tag = "#AViadaDescoberta #HistoriaReal #Ciencia #Documentario"
            final_desc = f"{parsed['description']}\n\n{ch_tag}"

        update_body = {
            "id": video_id,
            "snippet": {
                "title": parsed["new_title"],
                "description": final_desc,
                "tags": parsed["tags"],
                "categoryId": old_sn.get("categoryId", "27"),
                "defaultLanguage": old_sn.get("defaultLanguage", "pt-BR")
            }
        }
        yt.videos().update(part="snippet", body=update_body).execute()
        logger.info("SUCESSO: Vídeo %s atualizado no YouTube para: '%s'", video_id, parsed["new_title"])

        # 3. Avaliação e Regeneração de Thumbnail (Para Documentários Longos 16:9)
        thumbnail_updated = False
        thumb_headline_used = ""
        if not is_short:
            try:
                from backend.media.thumbnail_maker import ThumbnailMaker
                from googleapiclient.http import MediaFileUpload

                maker = ThumbnailMaker(thumbnails_dir=BASE_DIR / "workspace/thumbnails")
                headline_words = [
                    w for w in re.findall(r"[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{3,}", parsed["new_title"].upper())
                    if w not in ("DOCUMENTÁRIO", "DOCUMENTARIO", "SHORTS", "PARA", "COMO", "ONDE", "QUEM", "ESSE", "ESSA")
                ]
                thumb_headline = " ".join(headline_words[:3]) or "CASO REAL"
                thumb_headline_used = thumb_headline

                # Paleta de cor de destaque por canal
                acc_rgb = (255, 215, 0)  # Amarelo Ouro Canal 1
                if "UCE6Ch6" in channel_id or channel_id in ("2", "ch_2"):
                    acc_rgb = (16, 185, 129)  # Verde Neon Canal 2
                elif "UCIjEnT" in channel_id or channel_id in ("3", "ch_3"):
                    acc_rgb = (6, 182, 212)  # Ciano Elétrico Canal 3

                thumb_art = maker.create_thumbnail(
                    headline_text=thumb_headline,
                    badge_text="DOCUMENTÁRIO",
                    job_id=f"rework_{video_id}",
                    accent_color_rgb=acc_rgb,
                    topic_context=parsed["new_title"],
                    aspect_ratio="16:9"
                )

                if thumb_art and Path(thumb_art.output_jpg_path).exists():
                    yt.thumbnails().set(
                        videoId=video_id,
                        media_body=MediaFileUpload(thumb_art.output_jpg_path, mimetype="image/jpeg")
                    ).execute()
                    thumbnail_updated = True
                    logger.info("Thumbnail de alto CTR gerada e atualizada no YouTube para vídeo %s ('%s')", video_id, thumb_headline)
            except Exception as t_err:
                logger.warning("Falha ao atualizar thumbnail para vídeo %s: %s", video_id, t_err)

        entry = {
            "video_id": video_id,
            "old_title": current_title,
            "new_title": parsed["new_title"],
            "views_before": views,
            "tags_added": len(parsed["tags"]),
            "thumbnail_regenerated": thumbnail_updated,
            "thumbnail_headline": thumb_headline_used,
            "format": "SHORT_9_16" if is_short else "LONG_16_9",
            "reworked_at": datetime.now(timezone.utc).isoformat(),
            "engine": "ollama_llama3.1_local"
        }

        # Salva no log histórico
        history = []
        if REWORK_LOG.exists():
            try:
                history = json.loads(REWORK_LOG.read_text(encoding="utf-8"))
            except Exception:
                pass
        history.append(entry)
        REWORK_LOG.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")

        return entry

    except Exception as exc:
        logger.error("Erro ao retrabalhar vídeo %s via Ollama: %s", video_id, exc)
        return None


def run_full_zero_views_audit(apply_rework: bool = True) -> List[Dict[str, Any]]:
    """Varre todos os vídeos recentes dos canais ativos e aplica retrabalho inteligente em vídeos estagnados (>24h)."""
    channels = {
        CH1_ID: "A Via da Descoberta",
        CH2_ID: "Finanças Quânticas",
        CH3_ID: "Bio Hack Longevidade",
        CH4_ID: "Ain't No Human"
    }
    
    stagnant_videos = []
    
    for ch_id, ch_name in channels.items():
        tok = CREDENTIALS_DIR / f"{ch_id}_token.json"
        if not tok.exists():
            continue
        try:
            creds = Credentials.from_authorized_user_file(str(tok))
            yt = build("youtube", "v3", credentials=creds)
            ch = yt.channels().list(part="contentDetails", id=ch_id).execute()
            uploads_id = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            items = yt.playlistItems().list(part="snippet", playlistId=uploads_id, maxResults=15).execute()
            vids = [it["snippet"]["resourceId"]["videoId"] for it in items.get("items", [])]
            if not vids:
                continue
            
            v_stats = yt.videos().list(part="snippet,statistics", id=",".join(vids)).execute()
            for v in v_stats.get("items", []):
                vid = v["id"]
                title = v["snippet"]["title"]
                views = int(v["statistics"].get("viewCount", 0))
                
                # Vídeos estagnados com 0 views
                if views == 0:
                    stagnant_videos.append({
                        "channel_id": ch_id,
                        "channel_name": ch_name,
                        "video_id": vid,
                        "current_title": title,
                        "views": views
                    })
        except Exception as e:
            logger.error("Erro ao auditar canal %s (%s): %s", ch_name, ch_id, e)

    logger.info("Encontrados %d vídeos com 0 visualizações.", len(stagnant_videos))
    
    reworked_results = []
    if apply_rework:
        for item in stagnant_videos:
            res = rework_video_with_ollama(
                item["channel_id"],
                item["video_id"],
                item["current_title"],
                item["views"]
            )
            if res:
                reworked_results.append(res)
    
    return reworked_results or stagnant_videos


if __name__ == "__main__":
    import sys
    do_apply = "--apply" in sys.argv
    results = run_full_zero_views_audit(apply_rework=do_apply)
    print(json.dumps(results, indent=2, ensure_ascii=False))
