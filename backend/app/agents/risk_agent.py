from typing import List
from .base_agent import BaseAgent
from ..models.schemas import DetectedClause, RiskLevel, Recommendation
from ..config import get_settings

settings = get_settings()

class RiskAssessmentAgent(BaseAgent):
    """Agent responsible for overall risk assessment"""
    
    def __init__(self):
        super().__init__("RiskAssessmentAgent")
        self.is_loaded = True  # No model to load
    
    def load(self):
        """No model loading needed"""
        pass
    
    def _calculate_risk_score(self, clauses: List[DetectedClause]) -> int:
        """Calculate 0-100 risk score"""
        if not clauses:
            return 0
        
        risk_weights = {
            RiskLevel.HIGH: 30,
            RiskLevel.MEDIUM: 15,
            RiskLevel.LOW: 5
        }
        
        total_score = 0
        for clause in clauses:
            # Weight by confidence
            score = risk_weights[clause.risk_level] * clause.confidence
            total_score += score
        
        # Normalize to 0-100
        max_possible = len(clauses) * 30  # All high-risk with 100% confidence
        normalized = min(100, int((total_score / max_possible) * 100)) if max_possible > 0 else 0
        
        return normalized
    
    def _determine_risk_level(self, risk_score: int, clauses: List[DetectedClause]) -> RiskLevel:
        """Determine overall risk level"""
        high_risk_count = sum(1 for c in clauses if c.risk_level == RiskLevel.HIGH)
        
        # Any high-risk clause pushes to at least medium
        if high_risk_count >= 2 or risk_score >= 60:
            return RiskLevel.HIGH
        elif high_risk_count >= 1 or risk_score >= 30:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_recommendation(self, risk_level: RiskLevel, clauses: List[DetectedClause]) -> Recommendation:
        """Generate user recommendation"""
        high_risk_count = sum(1 for c in clauses if c.risk_level == RiskLevel.HIGH)
        
        if risk_level == RiskLevel.HIGH or high_risk_count >= 3:
            return Recommendation.AVOID
        elif risk_level == RiskLevel.MEDIUM:
            return Recommendation.REVIEW
        else:
            return Recommendation.SAFE
    
    def _extract_key_concerns(self, clauses: List[DetectedClause]) -> List[str]:
        """Extract top concerns for user"""
        concerns = []
        
        # Group by category
        high_risk_clauses = [c for c in clauses if c.risk_level == RiskLevel.HIGH]
        
        for clause in high_risk_clauses[:3]:  # Top 3 concerns
            concerns.append(f"{clause.category.title()}: {clause.explanation}")
        
        if not concerns:
            concerns.append("No major concerns detected, but always read carefully.")
        
        return concerns
    
    def process(self, input_data: dict) -> dict:
        """
        Perform risk assessment
        
        Args:
            input_data: {"clauses": List[DetectedClause]}
        
        Returns:
            {
                "risk_score": int,
                "risk_level": RiskLevel,
                "recommendation": Recommendation,
                "key_concerns": List[str]
            }
        """
        clauses = input_data["clauses"]
        
        # Calculate risk
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
            "high_risk_count": sum(1 for c in clauses if c.risk_level == RiskLevel.HIGH),
            "medium_risk_count": sum(1 for c in clauses if c.risk_level == RiskLevel.MEDIUM)
        }