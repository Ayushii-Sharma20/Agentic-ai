from typing import List
from .base_agent import BaseAgent
from ..models.schemas import RiskLevel, Recommendation
from ..config import get_settings

settings = get_settings()


class RiskAssessmentAgent(BaseAgent):
    """Agent responsible for overall risk assessment"""

    def __init__(self):
        super().__init__("RiskAssessmentAgent")
        self.is_loaded = True

    def load(self):
        pass

    def _get_risk_level(self, clause):
        # 🔥 handle dict OR object
        return clause["risk_level"] if isinstance(clause, dict) else clause.risk_level

    def _get_confidence(self, clause):
        return clause["confidence"] if isinstance(clause, dict) else clause.confidence

    def _get_category(self, clause):
        return clause["category"] if isinstance(clause, dict) else clause.category

    def _get_explanation(self, clause):
        return clause["explanation"] if isinstance(clause, dict) else clause.explanation

    def _calculate_risk_score(self, clauses: List) -> int:
        if not clauses:
            return 0

        risk_weights = {
            RiskLevel.HIGH: 30,
            RiskLevel.MEDIUM: 15,
            RiskLevel.LOW: 5
        }

        total_score = 0

        for clause in clauses:
            risk_level = self._get_risk_level(clause)
            confidence = self._get_confidence(clause)

            # 🔥 convert string → enum if needed
            if isinstance(risk_level, str):
                risk_level = RiskLevel(risk_level)

            total_score += risk_weights[risk_level] * confidence

        max_possible = len(clauses) * 30
        return min(100, int((total_score / max_possible) * 100)) if max_possible > 0 else 0

    def _determine_risk_level(self, risk_score: int, clauses: List) -> RiskLevel:
        high_risk_count = sum(
            1 for c in clauses if self._get_risk_level(c) == RiskLevel.HIGH
        )

        if high_risk_count >= 2 or risk_score >= 60:
            return RiskLevel.HIGH
        elif high_risk_count >= 1 or risk_score >= 30:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _generate_recommendation(self, risk_level: RiskLevel, clauses: List) -> Recommendation:
        high_risk_count = sum(
            1 for c in clauses if self._get_risk_level(c) == RiskLevel.HIGH
        )

        if risk_level == RiskLevel.HIGH or high_risk_count >= 3:
            return Recommendation.AVOID
        elif risk_level == RiskLevel.MEDIUM:
            return Recommendation.REVIEW
        else:
            return Recommendation.SAFE

    def _extract_key_concerns(self, clauses: List) -> List[str]:
        concerns = []

        high_risk_clauses = [
            c for c in clauses if self._get_risk_level(c) == RiskLevel.HIGH
        ]

        for clause in high_risk_clauses[:3]:
            category = self._get_category(clause)
            explanation = self._get_explanation(clause)
            concerns.append(f"{category.title()}: {explanation}")

        if not concerns:
            concerns.append("No major concerns detected, but always read carefully.")

        return concerns

    def process(self, input_data: dict) -> dict:
        clauses = input_data.get("clauses", [])

        risk_score = self._calculate_risk_score(clauses)
        risk_level = self._determine_risk_level(risk_score, clauses)
        recommendation = self._generate_recommendation(risk_level, clauses)
        key_concerns = self._extract_key_concerns(clauses)

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "recommendation": recommendation,
            "key_concerns": key_concerns,
            "total_clauses_analyzed": len(clauses),
            "high_risk_count": sum(
                1 for c in clauses if self._get_risk_level(c) == RiskLevel.HIGH
            ),
            "medium_risk_count": sum(
                1 for c in clauses if self._get_risk_level(c) == RiskLevel.MEDIUM
            )
        }