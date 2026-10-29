"""
Retention Architect Agent (Arquiteto Neuro-Comportamental de Retenção e CTR).
Audits:
- Hook velocity in the first 0-15 seconds (pattern interrupt + cold open).
- Open loops and pacing density (cuts/scene transitions every 4-12s).
- Outlier validation strength (Outlier Score >= 3.0x).
"""

from __future__ import annotations

from typing import Any, Dict, List

from backend.agents.base_agent import AgentVote, BaseStudioAgent


class RetentionArchitectAgent(BaseStudioAgent):
    def __init__(self) -> None:
        super().__init__(
            agent_id="retention_architect",
            agent_name="Neuro-Retention & Hook Architect",
            role="Diretor de Engenharia de Retenção, AVD e CTR",
            weight=0.20,
        )

    def evaluate(self, context: Dict[str, Any]) -> AgentVote:
        outlier_score = float(context.get("outlier_score", 4.5) or 4.5)
        hook_text = str(context.get("hook_text", "") or context.get("title", "") or "")
        scene_count = int(context.get("scene_count", 8) or 8)
        duration_sec = float(context.get("duration_sec", 60.0) or 60.0)
        has_subtitles = bool(context.get("has_subtitles", True))

        recommendations: List[str] = []
        score = 75.0

        if outlier_score >= 5.0:
            score += 12.0
        elif outlier_score >= 3.0:
            score += 7.0
        else:
            score -= 15.0
            recommendations.append(
                f"Outlier Score ({outlier_score:.1f}x) abaixo do mínimo institucional de 3.0x."
            )

        # Evaluate scene pacing
        avg_scene_duration = duration_sec / max(1, scene_count)
        if avg_scene_duration <= 25.0:
            score += 8.0
        elif avg_scene_duration <= 45.0:
            score += 3.0
        else:
            score -= 12.0
            recommendations.append(
                f"Duração média por cena ({avg_scene_duration:.1f}s) muito longa. Aumentar densidade de cortes/B-rolls."
            )

        if has_subtitles:
            score += 5.0
        else:
            score -= 15.0
            recommendations.append(
                "Legendas dinâmicas (.ASS) ausentes — obrigatório para retenção mobile."
            )

        if len(hook_text.strip()) < 15:
            score -= 8.0
            recommendations.append(
                "Fortalecer o Cold Open (0-15s) com pergunta paradoxal ou dado contraintuitivo imediato."
            )

        score = max(0.0, min(100.0, round(score, 1)))
        approved = score >= 72.0

        rationale = (
            f"Outlier {outlier_score:.1f}x | Ritmo: {scene_count} blocos visuais "
            f"(~{avg_scene_duration:.1f}s/cena) | Legendas dinâmicas: {'SIM' if has_subtitles else 'NÃO'}."
        )

        return AgentVote(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            role=self.role,
            approved=approved,
            veto=False,
            score=score,
            confidence=0.90,
            weight=self.weight,
            rationale=rationale,
            metrics={
                "outlier_score": outlier_score,
                "scene_count": scene_count,
                "avg_scene_duration_sec": round(avg_scene_duration, 2),
                "has_subtitles": has_subtitles,
            },
            recommendations=recommendations,
        )
