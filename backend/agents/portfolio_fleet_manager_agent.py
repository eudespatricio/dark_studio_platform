"""
Portfolio Fleet Manager Agent — Multi-Channel Category Cluster Scaling Engine
(`backend/agents/portfolio_fleet_manager_agent.py`).

Removes the legacy 3-channel ceiling and transforms Dark Studio into an
N-Channel Multi-Category Media Holding ("Máquina de Fazer Dinheiro em Escala"):
- Organizes channels into Macro-Category Clusters (`CATEGORY_CLUSTERS`), each with its own:
  * YouTube Category ID, RPM/CPM floor & ceiling, and Advertiser Lexical Triggers
  * Category-specific Prime-Time Schedule (BRT / UTC-3)
  * Dynamic 3-Phase Ramp-Up -> Post-Monetization Normalization lifecycle
  * Strict OAuth2 Credential Isolation (`workspace/youtube_tokens/{channel_uid}_token.json`)
  * Dedicated Voice Archetype & Visual Cinema LUT Preset
- Supports dynamic provisioning of unlimited channels (Slot #1..#N) into any category.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from backend.agents.base_agent import AgentVote, BaseStudioAgent
from backend.agents.schedule_cadence_auditor_agent import ScheduleCadenceAuditorAgent


CATEGORY_CLUSTERS: Dict[str, Dict[str, Any]] = {
    "CLUSTER_FINANCE_QUANT": {
        "cluster_id": "CLUSTER_FINANCE_QUANT",
        "cluster_name": "Finanças Quantitativas, Wall Street & Macroeconomia",
        "youtube_category_id": "27",  # Education / Finance
        "base_rpm_usd": 18.40,
        "rpm_range_usd": [12.50, 28.00],
        "target_ctr_pct": 8.4,
        "target_avd_pct": 48.5,
        "visual_lut_preset": "emerald_obsidian_matrix_lut",
        "voice_archetype": "Analytical Institutional Baritone",
        "prime_schedule_brt": {
            "ramp_phase_1": {
                "long_slots": ["17:30"],
                "short_slots": ["09:30", "12:15", "15:30", "19:45", "21:30"],
                "cadence_label": "FASE 1 (RAMPA YPP): 1 Doc Longo (17:30) + 5 Shorts/dia",
            },
            "normalized_phase_3": {
                "long_days": ["Terça 17:30", "Quinta 17:30", "Domingo 11:30"],
                "short_slots": ["12:15", "19:45"],
                "cadence_label": "FASE 3 (NORMALIZADO): 3 Super-Docs/sem (15-20m) + 2 Shorts/dia",
            },
        },
    },
    "CLUSTER_HISTORY_ENGINEERING": {
        "cluster_id": "CLUSTER_HISTORY_ENGINEERING",
        "cluster_name": "Mistérios Históricos, Engenharia Extrema & Arquivos Secretos",
        "youtube_category_id": "27",  # Education / History & Science
        "base_rpm_usd": 8.80,
        "rpm_range_usd": [6.50, 13.50],
        "target_ctr_pct": 9.5,
        "target_avd_pct": 50.0,
        "visual_lut_preset": "noir_archival_amber_cyan_lut",
        "voice_archetype": "Deep Documentary Storyteller",
        "prime_schedule_brt": {
            "ramp_phase_1": {
                "long_slots": ["12:30", "17:30"],
                "short_slots": ["09:45", "12:15", "15:30", "19:45", "21:45"],
                "cadence_label": "FASE 1 (RAMPA YPP): 1–2 Docs Longos (12:30/17:30) + 5 Shorts/dia",
            },
            "normalized_phase_3": {
                "long_days": ["Terça 17:30", "Quinta 17:30", "Sábado 17:30", "Domingo 11:30"],
                "short_slots": ["12:15", "19:45"],
                "cadence_label": "FASE 3 (NORMALIZADO): 4 Super-Docs/sem (12-18m) + 2 Shorts/dia",
            },
        },
    },
    "CLUSTER_NEURO_BIOHACKING": {
        "cluster_id": "CLUSTER_NEURO_BIOHACKING",
        "cluster_name": "Neurociência Aplicada, Dopamina, Biohacking & Alta Performance",
        "youtube_category_id": "28",  # Science & Technology
        "base_rpm_usd": 11.20,
        "rpm_range_usd": [8.00, 16.50],
        "target_ctr_pct": 8.8,
        "target_avd_pct": 47.0,
        "visual_lut_preset": "bioluminescent_neural_violet_lut",
        "voice_archetype": "Calm Clinical Neuro-Narrator",
        "prime_schedule_brt": {
            "ramp_phase_1": {
                "long_slots": ["17:30"],
                "short_slots": ["08:30", "12:15", "15:30", "19:45", "21:30"],
                "cadence_label": "FASE 1 (RAMPA YPP): 1 Doc Longo (17:30) + 5 Shorts/dia",
            },
            "normalized_phase_3": {
                "long_days": ["Segunda 17:30", "Quarta 17:30", "Sábado 11:30"],
                "short_slots": ["12:15", "19:45"],
                "cadence_label": "FASE 3 (NORMALIZADO): 3 Super-Docs/sem + 2 Shorts/dia",
            },
        },
    },
    "CLUSTER_AI_CYBER_GEOPOLITICS": {
        "cluster_id": "CLUSTER_AI_CYBER_GEOPOLITICS",
        "cluster_name": "Inteligência Artificial, Guerra Cibernética & Geopolítica Tech",
        "youtube_category_id": "28",  # Science & Technology
        "base_rpm_usd": 14.90,
        "rpm_range_usd": [10.50, 22.00],
        "target_ctr_pct": 8.6,
        "target_avd_pct": 49.0,
        "visual_lut_preset": "cyber_cobalt_telemetry_lut",
        "voice_archetype": "Sharp Tech Investigative Narrator",
        "prime_schedule_brt": {
            "ramp_phase_1": {
                "long_slots": ["17:30"],
                "short_slots": ["09:15", "12:15", "15:30", "19:30", "21:30"],
                "cadence_label": "FASE 1 (RAMPA YPP): 1 Doc Longo (17:30) + 5 Shorts/dia",
            },
            "normalized_phase_3": {
                "long_days": ["Terça 17:30", "Sexta 17:30", "Domingo 15:00"],
                "short_slots": ["12:15", "19:30"],
                "cadence_label": "FASE 3 (NORMALIZADO): 3 Super-Docs/sem + 2 Shorts/dia",
            },
        },
    },
    "CLUSTER_AEROSPACE_MEGaprojects": {
        "cluster_id": "CLUSTER_AEROSPACE_MEGaprojects",
        "cluster_name": "Aeroespacial, Megaprojetos Bilionários & Defesa Militar",
        "youtube_category_id": "28",
        "base_rpm_usd": 10.60,
        "rpm_range_usd": [7.80, 15.80],
        "target_ctr_pct": 9.2,
        "target_avd_pct": 51.0,
        "visual_lut_preset": "orbital_titanium_gold_lut",
        "voice_archetype": "Epic Engineering Documentary Voice",
        "prime_schedule_brt": {
            "ramp_phase_1": {
                "long_slots": ["17:30"],
                "short_slots": ["09:30", "12:15", "15:30", "19:45", "21:45"],
                "cadence_label": "FASE 1 (RAMPA YPP): 1 Doc Longo (17:30) + 5 Shorts/dia",
            },
            "normalized_phase_3": {
                "long_days": ["Quarta 17:30", "Sábado 17:30", "Domingo 11:30"],
                "short_slots": ["12:15", "19:45"],
                "cadence_label": "FASE 3 (NORMALIZADO): 3 Super-Docs/sem + 2 Shorts/dia",
            },
        },
    },
    "CLUSTER_MUSIC_CYBER_RNB": {
        "cluster_id": "CLUSTER_MUSIC_CYBER_RNB",
        "cluster_name": "Cyber-R&B, Lo-Fi & Long-Form Music",
        "youtube_category_id": "10",  # Music
        "base_rpm_usd": 6.80,
        "rpm_range_usd": [4.50, 11.20],
        "target_ctr_pct": 7.5,
        "target_avd_pct": 68.0,
        "visual_lut_preset": "cyberpunk_neon_nightdrive_lut",
        "voice_archetype": "Synthia 4.0 & Algorhythm (Autonomous Duo)",
        "prime_schedule_brt": {
            "ramp_phase_1": {
                "long_slots": ["18:00"],
                "short_slots": [],
                "cadence_label": "Agenda Autônoma Music_Band (Sessões 60min & Singles)",
            },
            "normalized_phase_3": {
                "long_days": ["Sexta 18:00"],
                "short_slots": [],
                "cadence_label": "Sessões Longas Semanais (Music_Band Engine)",
            },
        },
    },
}


class PortfolioFleetManagerAgent(BaseStudioAgent):
    """
    Agente Gestor de Portfólio Multi-Canal em Escala (Holding de Canais por Categoria).
    Governa N canais simultâneos, alocando cada canal em seu Cluster de Categoria,
    controlando a transição automática da Rampa (Fase 1) para Normalização (Fase 3)
    e evitando competição entre canais do mesmo grupo.
    """

    def __init__(self) -> None:
        super().__init__(
            agent_id="portfolio_fleet_manager",
            agent_name="Multi-Channel Category Fleet Manager",
            role="Diretor de Escala Multi-Canal por Categoria & Alocação de Capital",
            weight=0.15,
        )

    @staticmethod
    def resolve_cluster_for_channel(niche_or_name: str, channel_id: int = 1) -> Dict[str, Any]:
        import re
        text = str(niche_or_name or "").lower()
        if channel_id == 4 or any(k in text for k in ("human", "rnb", "music", "música", "lo-fi", "lofi", "synthia")):
            return CATEGORY_CLUSTERS["CLUSTER_MUSIC_CYBER_RNB"]
        if channel_id == 2 or any(k in text for k in ("finan", "quant", "wall street", "macro", "economia", "trade")):
            return CATEGORY_CLUSTERS["CLUSTER_FINANCE_QUANT"]
        if channel_id == 3 or any(k in text for k in ("neuro", "córtex", "cortex", "biohack", "dopamina", "mente")):
            return CATEGORY_CLUSTERS["CLUSTER_NEURO_BIOHACKING"]
        if re.search(r"\b(ia|ai|cyber|inteligencia artificial|algoritm\w*|tech|geopol\w*)\b", text):
            return CATEGORY_CLUSTERS["CLUSTER_AI_CYBER_GEOPOLITICS"]
        if any(k in text for k in ("aero", "espacial", "militar", "megaprojeto", "defesa")):
            return CATEGORY_CLUSTERS["CLUSTER_AEROSPACE_MEGAPROJECTS"]
        return CATEGORY_CLUSTERS["CLUSTER_HISTORY_ENGINEERING"]

    def evaluate(self, context: Dict[str, Any]) -> AgentVote:
        channel_id = int(context.get("channel_id", 1) or 1)
        channel_name = str(context.get("channel_name", "") or context.get("title", ""))
        cluster = self.resolve_cluster_for_channel(channel_name, channel_id)
        subscribers = int(context.get("subscribers", 14) or 14)
        watch_hours = float(context.get("watch_hours", 18.0) or 18.0)
        is_monetized = bool(context.get("is_monetized", False))

        ramp_info = ScheduleCadenceAuditorAgent.detect_channel_ramp_phase(
            subscribers=subscribers,
            watch_hours=watch_hours,
            is_monetized=is_monetized,
        )

        score = 92.0
        recommendations: List[str] = []

        rationale = (
            f"Cluster [{cluster['cluster_name']}] | Slot #{channel_id} | "
            f"Estágio: {ramp_info['active_phase_name']} | "
            f"RPM Alvo do Cluster: US$ {cluster['base_rpm_usd']:.2f}."
        )

        return AgentVote(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            role=self.role,
            approved=True,
            veto=False,
            score=score,
            confidence=0.95,
            weight=self.weight,
            rationale=rationale,
            metrics={
                "cluster_id": cluster["cluster_id"],
                "cluster_name": cluster["cluster_name"],
                "base_rpm_usd": cluster["base_rpm_usd"],
                "ramp_phase": ramp_info["active_phase_id"],
                "schedule_policy": cluster["prime_schedule_brt"],
            },
            recommendations=recommendations,
        )

    def get_fleet_overview(self, db_channels: List[Any]) -> Dict[str, Any]:
        """
        Builds a full multi-channel fleet overview grouped by Category Cluster,
        showing active channels, their Ramp Phase (Phase 1 vs Phase 3), and expansion slots.
        """
        fleet_channels: List[Dict[str, Any]] = []
        for ch in db_channels:
            ch_dict = ch.to_dict() if hasattr(ch, "to_dict") else dict(ch)
            ch_id = int(ch_dict.get("id", 1))
            cluster = self.resolve_cluster_for_channel(
                f"{ch_dict.get('name', '')} {ch_dict.get('sub_niche', '')}",
                channel_id=ch_id,
            )
            subs = int(ch_dict.get("subscribers", 0) or 0)
            views = int(ch_dict.get("total_views", 0) or 0)
            est_watch_hours = round(max(12.0, views * 0.08), 1)
            is_monetized = subs >= 1000 and est_watch_hours >= 4000.0

            ramp = ScheduleCadenceAuditorAgent.detect_channel_ramp_phase(
                subscribers=subs,
                watch_hours=est_watch_hours,
                is_monetized=is_monetized,
            )

            posting_cadence = cluster["prime_schedule_brt"]["ramp_phase_1"].get("cadence_label")
            is_music = (ch_id == 4 or cluster["cluster_id"] == "CLUSTER_MUSIC_CYBER_RNB")

            fleet_channels.append(
                {
                    **ch_dict,
                    "cluster_id": cluster["cluster_id"],
                    "cluster_name": cluster["cluster_name"],
                    "cluster_base_rpm_usd": cluster["base_rpm_usd"],
                    "posting_cadence": posting_cadence,
                    "channel_type": "music" if is_music else "documentary",
                    "ramp_status": ramp,
                    "active_schedule_policy": (
                        cluster["prime_schedule_brt"]["normalized_phase_3"]
                        if ramp["active_phase_id"] == "PHASE_3_MONETIZED_NORMALIZATION"
                        else cluster["prime_schedule_brt"]["ramp_phase_1"]
                    ),
                    "post_monetization_schedule_policy": cluster["prime_schedule_brt"]["normalized_phase_3"],
                }
            )

        return {
            "architecture": "N-Channel Category-Clustered Media Fleet",
            "total_channels_registered": len(fleet_channels),
            "available_category_clusters": list(CATEGORY_CLUSTERS.values()),
            "channels": fleet_channels,
            "scaling_guidelines": {
                "max_channels_per_oauth_token": 1,
                "stagger_offset_between_same_cluster_channels_min": 45,
                "phase_1_ignition_rule": "Novos canais entram automaticamente na Fase 1 (Rampa YPP: 5 Shorts + 1–2 Longos/dia) até atingir 1.000 inscritos e 4.000h.",
                "phase_3_normalization_rule": "Canais monetizados migram automaticamente para a Fase 3 (Normalização: 3–4 Super-Docs/semana + 2 Shorts/dia) liberando GPU/API para novos canais em Rampa.",
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
