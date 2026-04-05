from transformers import pipeline
import re
from typing import List, Tuple
from .base_agent import BaseAgent
from ..config import get_settings
from ..models.schemas import DetectedClause, RiskLevel

settings = get_settings()

class ClauseDetectionAgent(BaseAgent):
    """Agent responsible for detecting and classifying clauses"""
    
    def __init__(self):
        super().__init__("ClauseDetectionAgent")
        
        # Risky keywords for each category
        self.risk_patterns = {
            "data collection": {
                "high": ["personally identifiable", "sensitive data", "financial information", "health data"],
                "medium": ["device information", "location data", "browsing history"],
                "keywords": ["collect", "gather", "obtain", "record"]
            },
            "data sharing with third parties": {
                "high": ["sell", "monetize", "share with anyone", "unlimited sharing"],
                "medium": ["share with partners", "share with affiliates", "third-party analytics"],
                "keywords": ["share", "disclose", "provide to", "third party"]
            },
            "tracking and cookies": {
                "high": ["cross-site tracking", "sell browsing data", "track across devices"],
                "medium": ["advertising cookies", "analytics", "behavioral tracking"],
                "keywords": ["cookie", "track", "monitor", "pixel"]
            },
            "liability limitation": {
                "high": ["no liability", "unlimited damage", "waive all claims"],
                "medium": ["limited liability", "cap damages", "as-is"],
                "keywords": ["liability", "disclaimer", "warranty", "responsible"]
            },
            "arbitration clause": {
                "high": ["binding arbitration", "waive right to sue", "no class action"],
                "medium": ["dispute resolution", "mediation"],
                "keywords": ["arbitration", "dispute", "legal action"]
            }
        }
    
    def load(self):
        """Load zero-shot classification model"""
        try:
            self.model = pipeline(
                "zero-shot-classification",
                model=settings.CLASSIFIER_MODEL,
                device=-1
            )
            self.is_loaded = True
        except Exception as e:
            raise RuntimeError(f"Failed to load clause detector: {e}")
    
    def _extract_sentences(self, text: str) -> List[Tuple[str, int, int]]:
        """Extract sentences with their positions"""
        sentences = []
        for match in re.finditer(r'[^.!?]+[.!?]', text):
            sentence = match.group(0).strip()
            if len(sentence) > 20:  # Ignore very short sentences
                sentences.append((sentence, match.start(), match.end()))
        return sentences
    
    def _assess_clause_risk(self, category: str, text: str) -> RiskLevel:
        """Determine risk level based on keywords"""
        text_lower = text.lower()
        
        if category not in self.risk_patterns:
            return RiskLevel.MEDIUM
        
        patterns = self.risk_patterns[category]
        
        # Check high-risk patterns
        for pattern in patterns.get("high", []):
            if pattern.lower() in text_lower:
                return RiskLevel.HIGH
        
        # Check medium-risk patterns
        for pattern in patterns.get("medium", []):
            if pattern.lower() in text_lower:
                return RiskLevel.MEDIUM
        
        return RiskLevel.LOW
    
    def _generate_explanation(self, category: str, risk: RiskLevel) -> str:
        """Generate user-friendly explanation"""
        explanations = {
            "data collection": {
                RiskLevel.HIGH: "This collects very sensitive personal information that could be misused.",
                RiskLevel.MEDIUM: "This collects some personal data. Review what's being collected.",
                RiskLevel.LOW: "Basic data collection for service functionality."
            },
            "data sharing with third parties": {
                RiskLevel.HIGH: "Your data can be sold or shared widely without restrictions.",
                RiskLevel.MEDIUM: "Your data is shared with partner companies for specific purposes.",
                RiskLevel.LOW: "Limited data sharing with service providers only."
            },
            "tracking and cookies": {
                RiskLevel.HIGH: "Extensive tracking across websites and devices for advertising.",
                RiskLevel.MEDIUM: "Uses cookies for analytics and advertising.",
                RiskLevel.LOW: "Basic cookies for website functionality."
            },
            "liability limitation": {
                RiskLevel.HIGH: "Company takes no responsibility even if they cause serious harm.",
                RiskLevel.MEDIUM: "Company limits how much you can claim in damages.",
                RiskLevel.LOW: "Standard liability terms."
            },
            "arbitration clause": {
                RiskLevel.HIGH: "You cannot sue in court or join class-action lawsuits.",
                RiskLevel.MEDIUM: "Disputes must go through arbitration first.",
                RiskLevel.LOW: "Standard dispute resolution process."
            }
        }
        
        return explanations.get(category, {}).get(
            risk,
            "Review this clause carefully."
        )
    
    def process(self, input_data: dict) -> dict:
        """
        Detect and classify clauses
        
        Args:
            input_data: {"text": str}
        
        Returns:
            {"clauses": List[DetectedClause], "total_found": int}
        """
        text = input_data["text"]
        
        # Extract sentences
        sentences = self._extract_sentences(text)
        
        detected_clauses = []
        
        for sentence, start, end in sentences:
            # Classify sentence
            result = self.model(
                sentence,
                candidate_labels=settings.CLAUSE_CATEGORIES,
                multi_label=True
            )
            
            # Get top classification
            top_label = result['labels'][0]
            top_score = result['scores'][0]
            
            # Only keep if confidence > 0.5
            if top_score < 0.5:
                continue
            
            # Assess risk
            risk = self._assess_clause_risk(top_label, sentence)
            
            # Skip low-risk clauses unless very confident
            if risk == RiskLevel.LOW and top_score < 0.7:
                continue
            
            clause = DetectedClause(
                category=top_label,
                text=sentence,
                confidence=round(top_score, 2),
                risk_level=risk,
                explanation=self._generate_explanation(top_label, risk),
                position={"start": start, "end": end}
            )
            
            detected_clauses.append(clause)
        
        # Sort by risk level then confidence
        risk_order = {RiskLevel.HIGH: 0, RiskLevel.MEDIUM: 1, RiskLevel.LOW: 2}
        detected_clauses.sort(
            key=lambda x: (risk_order[x.risk_level], -x.confidence)
        )
        
        return {
            "clauses": detected_clauses,
            "total_found": len(detected_clauses),
            "sentences_analyzed": len(sentences)
        }