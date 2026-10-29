"""
Multi-Agent Money-Making & Quality Governance Council for Dark Studio AI Platform.
Inspired by the Institutional Consensus Architecture of ia_trader.
"""

from backend.agents.base_agent import AgentVote, BaseStudioAgent
from backend.agents.rpm_maximizer_agent import RPMMaximizerAgent
from backend.agents.retention_architect_agent import RetentionArchitectAgent
from backend.agents.visual_cinema_director_agent import VisualCinemaDirectorAgent
from backend.agents.anti_garbage_sentinel_agent import AntiGarbageSentinelAgent
from backend.agents.growth_funnel_strategist_agent import GrowthFunnelStrategistAgent
from backend.agents.schedule_cadence_auditor_agent import (
    MARKET_RESEARCH_BENCHMARKS,
    MONETIZATION_RAMP_PLAN,
    ScheduleCadenceAuditorAgent,
)
from backend.agents.portfolio_fleet_manager_agent import (
    CATEGORY_CLUSTERS,
    PortfolioFleetManagerAgent,
)
from backend.agents.consensus_council import ConsensusCouncil, CouncilVerdict

__all__ = [
    "AgentVote",
    "BaseStudioAgent",
    "RPMMaximizerAgent",
    "RetentionArchitectAgent",
    "VisualCinemaDirectorAgent",
    "AntiGarbageSentinelAgent",
    "GrowthFunnelStrategistAgent",
    "ScheduleCadenceAuditorAgent",
    "PortfolioFleetManagerAgent",
    "MARKET_RESEARCH_BENCHMARKS",
    "MONETIZATION_RAMP_PLAN",
    "CATEGORY_CLUSTERS",
    "ConsensusCouncil",
    "CouncilVerdict",
]
