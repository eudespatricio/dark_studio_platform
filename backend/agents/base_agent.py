"""
Base Agent Contract for the Dark Studio Multi-Agent Council.
Every specialized agent emits a structured AgentVote with score (0-100),
confidence (0.0-1.0), veto power, and actionable diagnostics.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass
class AgentVote:
    agent_id: str
    agent_name: str
    role: str
    approved: bool
    veto: bool
    score: float  # 0.0 to 100.0
    confidence: float  # 0.0 to 1.0
    weight: float  # Relative weight in council consensus
    rationale: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BaseStudioAgent(ABC):
    """Abstract base class for all autonomous agents in the Dark Studio Council."""

    def __init__(self, agent_id: str, agent_name: str, role: str, weight: float = 0.20):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.role = role
        self.weight = weight

    @abstractmethod
    def evaluate(self, context: Dict[str, Any]) -> AgentVote:
        """
        Inspects the pipeline job, script, channel metadata, or physical media files
        and returns an immutable AgentVote.
        """
        raise NotImplementedError
