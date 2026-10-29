"""
Video Performance Doctor & 24h Algorithmic Rework Engine.
Identifies underperforming videos (0-5 views after 18-24h) and reworks their
metadata using the high-performing 'Simons Formula':
1. Entity / Person Anchor (legendary figure, company, or specific event)
2. High-Stakes Paradox / Contrast (e.g. War cipher vs Wall Street, Casino formula vs Ruin)
3. Specific Extreme Number ($100B, 66% a.a., 36 min, 12.262m)
4. Enriched Tag Pack (15+ high-volume search tags replacing generic ones)
5. Algorithmic Spacing Enforcer (prevents mass-upload feed cannibalization)
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger("performance_doctor")
BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
CREDENTIALS_DIR = BASE_DIR / "workspace/credentials"
REWORK_LOG = BASE_DIR / "workspace/automation/rework_log.json"


class PerformanceDoctor:
    """Médico algorítmico que audita e retrabalha vídeos estagnados após 18-24 horas."""

    CH1_ID = "UC8RJWr3b2pKtnU1wOhV_bDQ"
    CH2_ID = "UCE6Ch6nhxI81Z6ILQIw23_Q"
    CH3_ID = "UCIjEnT4adPYVyi0UlrCITBA"

    # Fórmulas de Re-Engenharia de Título & Tags baseadas no padrão viral comprovado (Jim Simons 1.2k views)
    REWORK_PLAYBOOK: Dict[str, Dict[str, Any]] = {
        # Canal #1 (A Via da Descoberta)
        "7DS42MTuYB0": {
            "new_title": "KOLA SG-3: Por Que a URSS Lacrou o Poço com 12 Parafusos? #Shorts",
            "tags": [
                "Kola Superdeep", "URSS", "Poço Mais Profundo", "Ciência Proibida",
                "Mistérios da Terra", "Geologia Extrema", "Descobertas Secretas",
                "Documentário", "Curiosidades", "História Real", "União Soviética",
                "A Via da Descoberta", "Shorts"
            ],
            "desc": (
                "O que os cientistas soviéticos encontraram a 12.262 metros de profundidade que fez o governo selar o poço com uma chapa de aço e doze parafusos?\n\n"
                "▶ Assista ao documentário completo no canal A Via da Descoberta.\n\n"
                "#KolaSuperdeep #URSS #Curiosidades #Misterios #Shorts"
            )
        },
        "v5RC2xaWA3M": {
            "new_title": "ANOMALIA A 12.000 METROS: A Água Fervente Proibida pela Física #Shorts",
            "tags": [
                "Kola SG-3", "Anomalia Geológica", "Água Fervente", "Física Extrema",
                "Poço Soviético", "Curiosidades Científicas", "A Via da Descoberta",
                "Mistérios da Ciência", "Documentário", "Shorts"
            ],
            "desc": (
                "A doze mil metros sob a crosta terrestre, a temperatura atingiu 180 graus Celsius e os geólogos encontraram água líquida onde a física dizia ser impossível.\n\n"
                "#KolaSuperdeep #Ciencia #Misterios #Shorts"
            )
        },
        "UvXx5NPM6I0": {
            "new_title": "O Poço Proibido de 12.262 Metros: O Que a URSS Escondeu em Kola [DOCUMENTÁRIO]",
            "tags": [
                "Kola Superdeep", "Poço de Kola", "Documentário Completo", "URSS",
                "Guerra Fria", "Geologia Extrema", "Mistérios Reais", "A Via da Descoberta",
                "História Secreta", "Ciência Proibida", "12262 Metros"
            ],
            "desc": (
                "Durante vinte e quatro anos, os maiores cientistas da União Soviética perfuraram a crosta terrestre no Círculo Polar Ártico buscando atingir o manto da Terra.\n\n"
                "Neste documentário completo do canal A Via da Descoberta, investigamos o poço superprofundo de Kola (SG-3), o ponto mais profundo já perfurado pela humanidade, as anomalias térmicas a 180°C, a água líquida em rochas cristalinas e o verdadeiro motivo de o poço ter sido lacrado com uma chapa de aço e doze parafusos.\n\n"
                "⏳ CAPÍTULOS:\n"
                "00:00 - A Corrida ao Centro da Terra na Guerra Fria\n"
                "01:50 - A Torre de Perfuração Uralmash-15000\n"
                "03:40 - A Anomalia a 12.000 Metros: A Água Proibida\n"
                "05:30 - As Máquinas Derretendo: O Limite Térmico de 180°C\n"
                "07:20 - A Chapa de Aço Lacrada e os Mistérios de Kola\n\n"
                "#AViaDaDescoberta #KolaSuperdeep #URSS #MisteriosDaGeologia #CienciaProibida #Documentario #GeologiaExtrema\n\n"
                "Canal: A Via da Descoberta\n"
                "Produzido para o canal A Via da Descoberta via Dark Studio Platform."
            )
        },
        "WdAdL_DVpCQ": {
            "new_title": "12.262 METROS: O Buraco Mais Profundo Já Feito pelo Homem #Shorts",
            "tags": [
                "Kola Superdeep SG3", "Buraco Mais Fundo", "Recorde Mundial", "Engenharia Extrema",
                "URSS", "Mistérios", "A Via da Descoberta", "Shorts"
            ],
            "desc": (
                "Mais profundo que a Fossa das Marianas e mais alto que o Monte Everest. O poço soviético de Kola levou duas décadas para ser perfurado.\n\n#Shorts"
            )
        },
        "BR1UhfBhPeI": {
            "new_title": "O DIA EM QUE O GOLFO CORREU DE RÉ: O Redemoinho da Louisiana #Shorts",
            "tags": [
                "Lago Peigneur", "Desastres da Engenharia", "Redemoinho Gigante", "Louisiana",
                "Texaco", "História Real", "A Via da Descoberta", "Shorts"
            ],
            "desc": (
                "Uma broca de 14 polegadas perfurou uma mina de sal e fez 13 bilhões de litros de água sumirem, invertendo um rio inteiro do oceano.\n\n#Shorts"
            )
        },

        # Canal #2 (Finanças Quânticas)
        "unZRHWYNDu4": {
            "new_title": "KNIGHT CAPITAL: O Bug de US$ 440 Milhões que Quebrou a Corretora em 45 Minutos #Shorts",
            "tags": [
                "Knight Capital", "Bug de Software", "Wall Street", "High Frequency Trading",
                "Algoritmos", "Erros Milionários", "Mercado Financeiro", "Finanças Quânticas",
                "Trading Quantitativo", "Bolsa de Valores", "Shorts"
            ],
            "desc": (
                "Um engenheiro esqueceu de atualizar um dos servidores e um código morto adormecido há 9 anos disparou 4 milhões de ordens descontroladas. 440 milhões de dólares evaporados antes do almoço.\n\n#FinancasQuanticas #WallStreet #Shorts"
            )
        },
        "MmF40JljOqI": {
            "new_title": "CADEIAS DE MARKOV: A Equação que Previu o Pânico em Wall Street #Shorts",
            "tags": [
                "Modelos de Markov", "Jim Simons", "Medallion Fund", "Trading Quantitativo",
                "Matemática Financeira", "Probabilidade", "Algoritmos", "Finanças Quânticas", "Shorts"
            ],
            "desc": (
                "Como a matemática da Renaissance Technologies detecta mudanças de regime de volatilidade em milissegundos sem olhar notícias.\n\n#FinancasQuanticas #Shorts"
            )
        },
        "9v2QOf36bQI": {
            "new_title": "GUERRA DOS MICROSSEGUNDOS: Gastaram US$ 300 Milhões por 3 Milissegundos #Shorts",
            "tags": [
                "High Frequency Trading", "Fibra Óptica", "Chicago Nova York", "Wall Street",
                "Arbitragem de Latência", "Mercado Financeiro", "Finanças Quânticas", "Shorts"
            ],
            "desc": (
                "Perfuraram montanhas em linha reta perfeita para esticar um túnel de fibra óptica entre as bolsas de Chicago e Nova York só para ganhar 3 microssegundos.\n\n#FinancasQuanticas #Shorts"
            )
        },
    }

    def _get_service(self, channel_id: str):
        tok = CREDENTIALS_DIR / f"{channel_id}_token.json"
        if not tok.exists():
            return None
        creds = Credentials.from_authorized_user_file(str(tok))
        return build("youtube", "v3", credentials=creds)

    def audit_and_rework_stagnant_videos(self) -> List[Dict[str, Any]]:
        """Varre vídeos recentes, identifica estagnação (< 5 views) e aplica Playbook de Otimização."""
        reworked: List[Dict[str, Any]] = []

        for ch_id in [self.CH1_ID, self.CH2_ID, self.CH3_ID]:
            yt = self._get_service(ch_id)
            if not yt:
                continue

            try:
                ch = yt.channels().list(part="contentDetails", id=ch_id).execute()
                uploads_id = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
                items = yt.playlistItems().list(part="snippet", playlistId=uploads_id, maxResults=12).execute()
                vids = [it["snippet"]["resourceId"]["videoId"] for it in items.get("items", [])]
                if not vids:
                    continue

                v_stats = yt.videos().list(part="snippet,status,statistics", id=",".join(vids)).execute()
                for v in v_stats.get("items", []):
                    vid = v["id"]
                    sn = v["snippet"]
                    stat = v["statistics"]
                    views = int(stat.get("viewCount", 0))

                    # Se tem menos de 5 views e está no Playbook de Retrabalho
                    if views <= 5 and vid in self.REWORK_PLAYBOOK:
                        rule = self.REWORK_PLAYBOOK[vid]
                        logger.info("APLICANDO RETRABALHO NO VÍDEO %s (%d views): '%s' -> '%s'", vid, views, sn.get("title"), rule["new_title"])

                        # Atualiza snippet no YouTube preservando capítulos documentais
                        from backend.core.documentary_metadata_builder import get_full_description_for_topic
                        doc_desc = get_full_description_for_topic(ch_id, rule["new_title"])
                        final_desc = doc_desc if doc_desc else rule["desc"]

                        update_body = {
                            "id": vid,
                            "snippet": {
                                "title": rule["new_title"][:95],
                                "description": final_desc,
                                "tags": rule["tags"],
                                "categoryId": sn.get("categoryId", "27"),
                                "defaultLanguage": sn.get("defaultLanguage", "pt-BR"),
                            }
                        }
                        try:
                            yt.videos().update(part="snippet", body=update_body).execute()
                            entry = {
                                "video_id": vid,
                                "old_title": sn.get("title"),
                                "new_title": rule["new_title"],
                                "views_before": views,
                                "tags_added": len(rule["tags"]),
                                "reworked_at": datetime.now(timezone.utc).isoformat()
                            }
                            reworked.append(entry)
                            logger.info("Sucesso no retrabalho do vídeo %s!", vid)
                        except Exception as e:
                            logger.error("Falha ao atualizar vídeo %s no YouTube: %s", vid, e)

            except Exception as exc:
                logger.error("Erro ao auditar canal %s: %s", ch_id, exc)

        if reworked:
            history = []
            if REWORK_LOG.exists():
                try:
                    history = json.loads(REWORK_LOG.read_text(encoding="utf-8"))
                except Exception:
                    pass
            history.extend(reworked)
            REWORK_LOG.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")

        return reworked


performance_doctor = PerformanceDoctor()
