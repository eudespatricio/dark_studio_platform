"""
Visual Cinema Director Agent (Diretor de Fotografia, Ken Burns e Anti-Content-ID).
Audits visual variety, color grading, Ken Burns camera motion, and thumbnail presence.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from backend.agents.base_agent import AgentVote, BaseStudioAgent


class VisualCinemaDirectorAgent(BaseStudioAgent):
    def __init__(self) -> None:
        super().__init__(
            agent_id="visual_cinema_director",
            agent_name="Visual Cinema & Anti-Content-ID Director",
            role="Diretor de Fotografia Documental, Ken Burns & Originalidade",
            weight=0.20,
        )

    def evaluate(self, context: Dict[str, Any]) -> AgentVote:
        visual_entropy = float(context.get("visual_entropy_std", 38.0) or 38.0)
        motion_delta = float(context.get("motion_delta_mean", 4.2) or 4.2)
        thumbnail_path = str(context.get("thumbnail_path", "") or "")
        scene_diversity = int(context.get("distinct_scenes_detected", 6) or 6)
        scene_clone_correl = float(context.get("scene_clone_correlation", 0.0) or 0.0)
        branding_hallucination = bool(context.get("branding_logo_hallucination", False))

        recommendations: List[str] = []
        score = 76.0
        veto = False

        if branding_hallucination:
            score = 0.0
            veto = True
            recommendations.append(
                "VETO DIRETOR DE FOTOGRAFIA: Avatar/Logo do canal detectado como B-roll. Proibido usar imagens de branding como cena narrativa."
            )
        if scene_clone_correl > 0.72:
            score = min(score, 25.0)
            veto = True
            recommendations.append(
                f"VETO DIRETOR DE FOTOGRAFIA: Cenas repetidas da mesma imagem-base (correlação={scene_clone_correl:.2f}). Exigido vídeo/imagens reais distintas por cena."
            )

        if visual_entropy >= 28.0:
            score += 10.0
        elif visual_entropy >= 15.0:
            score += 4.0
        else:
            score -= 30.0
            recommendations.append(
                f"Entropia visual baixa (std={visual_entropy:.1f}). Risco de fundo escuro/monótono sem B-roll cinematográfico."
            )

        if motion_delta >= 1.2:
            score += 8.0
        else:
            score -= 20.0
            recommendations.append(
                f"Movimento entre quadros baixo (delta={motion_delta:.2f}). Ativar Ken Burns (zoompan) e transições entre cenas."
            )

        if scene_diversity >= 4:
            score += 6.0
        else:
            score -= 10.0
            recommendations.append(
                "Aumentar variedade de lâminas visuais e gráficos de apoio ao longo da narrativa."
            )

        thumb_ok = bool(thumbnail_path and Path(thumbnail_path).exists())
        if not thumb_ok and thumbnail_path:
            recommendations.append("Gerar Thumbnail 1280x720 dedicada antes da publicação.")

        score = 0.0 if veto else max(0.0, min(100.0, round(score, 1)))
        approved = (not veto) and (score >= 70.0)

        rationale = (
            f"Entropia Visual: {visual_entropy:.1f} std | Movimento Ken Burns: {motion_delta:.2f} delta | "
            f"Diversidade de cenas: {scene_diversity} ambientes | Correlação inter-cenas: {scene_clone_correl:.2f}."
        )

        return AgentVote(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            role=self.role,
            approved=approved,
            veto=veto,
            score=score,
            confidence=0.91,
            weight=self.weight,
            rationale=rationale,
            metrics={
                "visual_entropy_std": round(visual_entropy, 2),
                "motion_delta_mean": round(motion_delta, 2),
                "distinct_scenes_detected": scene_diversity,
                "thumbnail_verified": thumb_ok,
            },
            recommendations=recommendations,
        )
