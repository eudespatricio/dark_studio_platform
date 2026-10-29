"""
Consensus Council (Comitê Deliberativo Multi-Agente — "Máquina de Fazer Dinheiro").
Modeled after ConsensusJudge in /home/eudespatricio/ia_trader/consensus_judge.py.
Coordinates the 5 specialized agents:
1. AntiGarbageSentinelAgent (Physical FFprobe/OpenCV Inspector — Absolute VETO Power)
2. RPMMaximizerAgent (AdSense Mid-Roll & High-CPM Arbitrage Director)
3. RetentionArchitectAgent (Cold-Open Hook, Scene Pacing & AVD Architect)
4. VisualCinemaDirectorAgent (Ken Burns Motion, B-Roll Entropy & Anti-Content-ID)
5. GrowthFunnelStrategistAgent (Shorts->Long Funnel & Strict Per-Channel OAuth Isolation)
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.agents.anti_garbage_sentinel_agent import AntiGarbageSentinelAgent
from backend.agents.base_agent import AgentVote
from backend.agents.growth_funnel_strategist_agent import GrowthFunnelStrategistAgent
from backend.agents.portfolio_fleet_manager_agent import PortfolioFleetManagerAgent
from backend.agents.retention_architect_agent import RetentionArchitectAgent
from backend.agents.rpm_maximizer_agent import RPMMaximizerAgent
from backend.agents.schedule_cadence_auditor_agent import ScheduleCadenceAuditorAgent
from backend.agents.visual_cinema_director_agent import VisualCinemaDirectorAgent


@dataclass
class CouncilVerdict:
    approved_for_publish: bool
    vetoed: bool
    veto_reasons: List[str]
    consensus_score: float
    grade: str
    estimated_rpm_usd: float
    midroll_eligible: bool
    votes: List[Dict[str, Any]]
    actionable_directives: List[str]
    evaluated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ConsensusCouncil:
    """
    Central Deliberative Governance Engine for Dark Studio (7 Specialized Agents).
    Runs inside the detached background worker and pre-upload gate.
    """

    # In-memory & disk-backed high performance cache with physical video mtime invalidation
    _cache_payload: Optional[Dict[str, Any]] = None
    _cache_timestamp: float = 0.0
    _cache_mtimes: Dict[str, float] = {}
    _cache_ttl_sec: float = 86400.0  # 24h TTL (invalidado instantaneamente se mtime dos MP4 mudar)
    _cache_lock: threading.Lock = threading.Lock()

    @classmethod
    def invalidate_cache(cls) -> None:
        """Forces cache invalidation (e.g. called after a video render pipeline completes)."""
        with cls._cache_lock:
            cls._cache_payload = None
            cls._cache_timestamp = 0.0
            cls._cache_mtimes.clear()

    def __init__(self, min_consensus_score: float = 78.0) -> None:
        self.min_consensus_score = min_consensus_score
        self.sentinel = AntiGarbageSentinelAgent()
        self.rpm_agent = RPMMaximizerAgent()
        self.retention_agent = RetentionArchitectAgent()
        self.visual_agent = VisualCinemaDirectorAgent()
        self.funnel_agent = GrowthFunnelStrategistAgent()
        self.cadence_agent = ScheduleCadenceAuditorAgent()
        self.fleet_agent = PortfolioFleetManagerAgent()
        self.agents = [
            self.sentinel,
            self.rpm_agent,
            self.retention_agent,
            self.visual_agent,
            self.funnel_agent,
            self.cadence_agent,
            self.fleet_agent,
        ]

    def deliberate(self, context: Dict[str, Any]) -> CouncilVerdict:
        """
        Executes all 5 agents in sequence (starting with the Physical Sentinel so its
        OpenCV/ffprobe telemetry enriches the shared context for the other agents).
        """
        working_ctx = dict(context)
        votes: List[AgentVote] = []
        veto_reasons: List[str] = []
        directives: List[str] = []

        for agent in self.agents:
            vote = agent.evaluate(working_ctx)
            votes.append(vote)
            if vote.veto:
                veto_reasons.append(f"[{agent.agent_name}] {vote.rationale}")
            for rec in vote.recommendations:
                if rec not in directives:
                    directives.append(rec)

        vetoed = len(veto_reasons) > 0
        total_weight = sum(v.weight for v in votes) or 1.0
        weighted_score = sum(v.score * v.weight for v in votes) / total_weight
        consensus_score = 0.0 if vetoed else round(weighted_score, 1)

        if vetoed:
            grade = "VETOADO (BLOQUEIO FÍSICO)"
        elif consensus_score >= 90.0:
            grade = "S (INSTITUCIONAL HIGH-RPM)"
        elif consensus_score >= 82.0:
            grade = "A (APROVADO COMERCIAL)"
        elif consensus_score >= self.min_consensus_score:
            grade = "B (APROVADO NO LIMIAR)"
        else:
            grade = "REPROVADO (ABAIXO DO PQS)"

        approved = (not vetoed) and (consensus_score >= self.min_consensus_score)

        rpm_vote = next((v for v in votes if v.agent_id == "rpm_maximizer"), None)
        est_rpm = (
            float(rpm_vote.metrics.get("estimated_rpm_usd", 9.50))
            if rpm_vote
            else 9.50
        )
        midroll = (
            bool(rpm_vote.metrics.get("midroll_eligible", False))
            if rpm_vote
            else False
        )

        return CouncilVerdict(
            approved_for_publish=approved,
            vetoed=vetoed,
            veto_reasons=veto_reasons,
            consensus_score=consensus_score,
            grade=grade,
            estimated_rpm_usd=est_rpm,
            midroll_eligible=midroll,
            votes=[v.to_dict() for v in votes],
            actionable_directives=directives,
        )

    def audit_channel_portfolio(self, project_root: Path, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Audits the physical rendered assets of the active channels on disk and returns
        a live executive status report for the UI Command Center and background worker.
        Uses in-memory cache with TTL (300s) and mtime check of video files to return in < 5ms.
        """
        renders_dir = project_root / "workspace" / "renders"
        token_dir = project_root / "workspace" / "youtube_tokens"

        sample_assets = [
            {
                "channel_id": 1,
                "channel_name": "A Via da Descoberta",
                "handle": "@AViadaDescoberta",
                "format": "long_16x9",
                "title": "O Colapso Silencioso da Engenharia Extrema: O Caso que Mudou a Ciência",
                "video_path": renders_dir / "ch1_via_descoberta_doc_16x9.mp4",
                "base_rpm_usd": 8.80,
                "outlier_score": 8.7,
                "min_long_duration_sec": 150.0,
            },
            {
                "channel_id": 2,
                "channel_name": "Finanças Quânticas",
                "handle": "@FinancasQuanticasOficial",
                "format": "long_16x9",
                "title": "A Equação Secreta de Jim Simons: Como o Medallion Fund Extraiu US$ 100 Bilhões de Wall Street",
                "video_path": renders_dir / "quant_long_11min_doc_16x9.mp4",
                "base_rpm_usd": 18.40,
                "outlier_score": 11.4,
                "require_full_doc": True,
                "min_long_duration_sec": 480.0,
            },
            {
                "channel_id": 2,
                "channel_name": "Finanças Quânticas",
                "handle": "@FinancasQuanticasOficial",
                "format": "short_9x16",
                "title": "Por que 99% dos Traders Perdem para os Algoritmos Quânticos de Wall Street #Shorts",
                "video_path": renders_dir / "quant_short_11min_9x16.mp4",
                "base_rpm_usd": 18.40,
                "outlier_score": 9.8,
            },
            {
                "channel_id": 3,
                "channel_name": "Bio Hack Longevidade",
                "handle": "@BioHackLongevidade",
                "format": "long_16x9",
                "title": "O Que Acontece com o Seu Cérebro e Mitocôndrias após 24 Horas de Autofagia (Neurociência Revelada) [DOCUMENTÁRIO]",
                "video_path": renders_dir / "cadence_ch3_slot_biohack_long_01_16x9.mp4",
                "base_rpm_usd": 14.50,
                "outlier_score": 13.4,
                "min_long_duration_sec": 180.0,
            },
            {
                "channel_id": 3,
                "channel_name": "Bio Hack Longevidade",
                "handle": "@BioHackLongevidade",
                "format": "short_9x16",
                "title": "16 HORAS DE JEJUM: O momento exato em que suas células devoram proteínas tóxicas #Shorts",
                "video_path": renders_dir / "cadence_ch3_slot_biohack_short_02_9x16.mp4",
                "base_rpm_usd": 14.50,
                "outlier_score": 13.4,
            },
        ]

        now = time.time()
        # Collect current mtimes of monitored video files
        current_mtimes: Dict[str, float] = {}
        for item in sample_assets:
            vp = item["video_path"]
            if vp.exists():
                try:
                    current_mtimes[str(vp)] = vp.stat().st_mtime
                except OSError:
                    pass

        # Check in-memory or disk cache validity (TTL & file mtimes)
        disk_cache_file = project_root / "workspace" / ".council_cache.json"
        if not force_refresh:
            with ConsensusCouncil._cache_lock:
                if (
                    ConsensusCouncil._cache_payload is not None
                    and (now - ConsensusCouncil._cache_timestamp) < ConsensusCouncil._cache_ttl_sec
                    and current_mtimes == ConsensusCouncil._cache_mtimes
                ):
                    cached_resp = dict(ConsensusCouncil._cache_payload)
                    cached_resp["cached"] = True
                    cached_resp["cache_age_seconds"] = round(now - ConsensusCouncil._cache_timestamp, 3)
                    return cached_resp

                if disk_cache_file.exists():
                    try:
                        disk_data = json.loads(disk_cache_file.read_text(encoding="utf-8"))
                        if (
                            disk_data.get("mtimes") == current_mtimes
                            and (now - float(disk_data.get("timestamp_epoch", 0))) < ConsensusCouncil._cache_ttl_sec
                            and isinstance(disk_data.get("payload"), dict)
                        ):
                            ConsensusCouncil._cache_payload = disk_data["payload"]
                            ConsensusCouncil._cache_timestamp = float(disk_data["timestamp_epoch"])
                            ConsensusCouncil._cache_mtimes = current_mtimes
                            cached_resp = dict(ConsensusCouncil._cache_payload)
                            cached_resp["cached"] = True
                            cached_resp["cache_age_seconds"] = round(now - ConsensusCouncil._cache_timestamp, 3)
                            return cached_resp
                    except Exception:
                        pass

        portfolio_audits: List[Dict[str, Any]] = []
        for item in sample_assets:
            vpath = item["video_path"]
            if not vpath.exists():
                continue
            verdict = self.deliberate(
                {
                    **item,
                    "video_path": str(vpath),
                    "token_dir": str(token_dir),
                    "description": (
                        f"Documentário oficial {item['channel_name']} com roteiro validado, "
                        "análise quantitativa, capítulos e fontes primárias."
                    ),
                    "tags": ["documentario", "financas", "ciencia", "algoritmos", "historia"],
                }
            )
            portfolio_audits.append(
                {
                    "channel_id": item["channel_id"],
                    "channel_name": item["channel_name"],
                    "handle": item["handle"],
                    "format": item["format"],
                    "title": item["title"],
                    "file_name": vpath.name,
                    "verdict": verdict.to_dict(),
                }
            )

        payload = {
            "council_status": "ACTIVE_AUTONOMOUS_GOVERNANCE",
            "agents_online": [
                {
                    "id": a.agent_id,
                    "name": a.agent_name,
                    "role": a.role,
                    "weight": a.weight,
                }
                for a in self.agents
            ],
            "min_consensus_score": self.min_consensus_score,
            "portfolio_audits": portfolio_audits,
            "cadence_benchmark_report": self.cadence_agent.generate_comparative_benchmark_report(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cached": False,
        }

        with ConsensusCouncil._cache_lock:
            ConsensusCouncil._cache_payload = payload
            ConsensusCouncil._cache_timestamp = time.time()
            ConsensusCouncil._cache_mtimes = current_mtimes
            try:
                disk_cache_file.parent.mkdir(parents=True, exist_ok=True)
                disk_cache_file.write_text(
                    json.dumps(
                        {
                            "timestamp_epoch": ConsensusCouncil._cache_timestamp,
                            "mtimes": current_mtimes,
                            "payload": payload,
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
            except Exception:
                pass

        return payload
