"""
RPM Maximizer Agent (Diretor de Monetização, CPM/RPM e Arbitragem de AdSense).
Focuses on maximizing revenue per 1,000 views:
- Enforces >= 8m00s (480s) duration on full documentaries to unlock YouTube Mid-Roll Ads.
- Audits high-CPM advertiser lexical triggers (Quantitative Finance, Institutional Capital,
  Aerospace/Engineering, Cybersecurity, Macroeconomics).
- Evaluates estimated RPM ($8.50 - $28.00 USD) and mid-roll placement slots.
"""

from __future__ import annotations

from typing import Any, Dict, List

from backend.agents.base_agent import AgentVote, BaseStudioAgent


HIGH_CPM_KEYWORDS = {
    "quant": 4.5,
    "algoritmo": 3.5,
    "wall street": 4.5,
    "hedge fund": 5.0,
    "bilhões": 3.0,
    "capital": 3.0,
    "investimento": 3.5,
    "juros": 3.0,
    "fed": 3.5,
    "engenharia": 2.8,
    "nuclear": 2.5,
    "satélite": 2.8,
    "geopolítica": 2.5,
    "inteligência artificial": 4.0,
    "derivativos": 4.5,
    "liquidez": 3.8,
    "arbitragem": 4.2,
    "institucional": 3.5,
}


class RPMMaximizerAgent(BaseStudioAgent):
    def __init__(self) -> None:
        super().__init__(
            agent_id="rpm_maximizer",
            agent_name="RPM & Mid-Roll Maximizer",
            role="Diretor de Monetização AdSense & High-Ticket CPM",
            weight=0.20,
        )

    def evaluate(self, context: Dict[str, Any]) -> AgentVote:
        video_format = str(context.get("format", "long_16x9")).lower()
        duration_sec = float(context.get("duration_sec", 0.0) or 0.0)
        title = str(context.get("title", "") or "")
        script_text = str(context.get("script_text", "") or "")
        niche_rpm_base = float(context.get("base_rpm_usd", 9.50) or 9.50)

        combined_text = f"{title} {script_text}".lower()
        matched_keywords: List[str] = []
        cpm_boost = 0.0
        for kw, boost in HIGH_CPM_KEYWORDS.items():
            if kw in combined_text:
                matched_keywords.append(kw)
                cpm_boost += boost

        cpm_boost = min(14.0, cpm_boost)
        estimated_rpm = round(niche_rpm_base + (cpm_boost * 0.45), 2)

        recommendations: List[str] = []
        score = 78.0

        # Evaluate mid-roll eligibility for long-form videos
        midroll_eligible = False
        midroll_slots: List[str] = []
        if "short" in video_format or "9x16" in video_format:
            # Shorts monetization is feed-pool + funnel conversion driven
            if 30.0 <= duration_sec <= 59.5:
                score += 14.0
            else:
                score -= 15.0
                recommendations.append(
                    "Ajustar Short para a faixa de 45s-58s para maximizar loop e retenção no Shorts Feed."
                )
            estimated_rpm = round(min(estimated_rpm * 0.12, 0.35), 2)
        else:
            if duration_sec >= 480.0:
                midroll_eligible = True
                score += 15.0
                # Compute optimal natural break points for mid-rolls
                slot_1 = int(duration_sec * 0.22)
                slot_2 = int(duration_sec * 0.52)
                slot_3 = int(duration_sec * 0.78)
                midroll_slots = [
                    f"{slot_1 // 60:02d}:{slot_1 % 60:02d}",
                    f"{slot_2 // 60:02d}:{slot_2 % 60:02d}",
                    f"{slot_3 // 60:02d}:{slot_3 % 60:02d}",
                ]
            elif duration_sec >= 180.0:
                score -= 8.0
                recommendations.append(
                    f"Vídeo longo atual ({duration_sec:.0f}s) é um Mini-Doc (<8 min). Expandir para >= 480s (8+ min) desbloqueia Mid-Roll Ads e multiplica o RPM em 2.4x."
                )
            else:
                score -= 35.0
                recommendations.append(
                    f"Duração insuficiente ({duration_sec:.0f}s) para vídeo horizontal monetizável."
                )

        if len(matched_keywords) >= 3:
            score += 7.0
        else:
            recommendations.append(
                "Incluir mais termos de alto leilão (ex: Capital Institucional, Algoritmos, Liquidez, Engenharia) nos primeiros 60s e na descrição SEO."
            )

        score = max(0.0, min(100.0, round(score, 1)))
        approved = score >= 70.0

        rationale = (
            f"RPM estimado em US$ {estimated_rpm:.2f} | "
            f"Mid-Roll Ads (>8 min): {'ATIVO (' + ', '.join(midroll_slots) + ')' if midroll_eligible else 'N/A'} | "
            f"{len(matched_keywords)} gatilhos de alto CPM detectados."
        )

        return AgentVote(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            role=self.role,
            approved=approved,
            veto=False,
            score=score,
            confidence=0.92,
            weight=self.weight,
            rationale=rationale,
            metrics={
                "estimated_rpm_usd": estimated_rpm,
                "midroll_eligible": midroll_eligible,
                "midroll_slots": midroll_slots,
                "high_cpm_keywords_found": matched_keywords[:8],
            },
            recommendations=recommendations,
        )
