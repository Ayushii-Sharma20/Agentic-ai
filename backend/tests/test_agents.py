# backend/tests/test_agents.py
import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Allow imports from backend root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.schemas import RiskLevel, DetectedClause
from app.agents.risk_agent import RiskAssessmentAgent




SAMPLE_TEXT = """
We collect personally identifiable information including your name, email address, phone number,
financial information, and health data when you register. We may share your data with third party
advertising partners and sell aggregated data. By using this service, you agree to binding
arbitration and waive your right to join class action lawsuits. We may terminate your account
at any time without notice. We reserve the right to change these terms at any time.
"""

def make_clause(risk: RiskLevel, confidence: float = 0.9, category: str = "data collection") -> DetectedClause:
    return DetectedClause(
        category=category,
        text="Sample clause text for testing purposes.",
        confidence=confidence,
        risk_level=risk,
        explanation="Test explanation.",
    )



class TestRiskAssessmentAgent:
    def setup_method(self):
        self.agent = RiskAssessmentAgent()

    def test_no_clauses_returns_zero_score(self):
        result = self.agent.process({"clauses": []})
        assert result["risk_score"] == 0
        assert result["risk_level"] == RiskLevel.LOW

    def test_single_high_risk_clause(self):
        clauses = [make_clause(RiskLevel.HIGH)]
        result = self.agent.process({"clauses": clauses})
        assert result["risk_level"] in (RiskLevel.HIGH, RiskLevel.MEDIUM)
        assert result["risk_score"] > 0

    def test_multiple_high_risk_pushes_to_high(self):
        clauses = [make_clause(RiskLevel.HIGH) for _ in range(3)]
        result = self.agent.process({"clauses": clauses})
        assert result["risk_level"] == RiskLevel.HIGH
        assert result["recommendation"].value in ("Read Carefully", "Not Recommended")

    def test_all_low_risk(self):
        clauses = [make_clause(RiskLevel.LOW, confidence=0.6) for _ in range(5)]
        result = self.agent.process({"clauses": clauses})
        assert result["risk_level"] == RiskLevel.LOW
        assert result["recommendation"].value == "Safe to Accept"

    def test_score_normalized_0_to_100(self):
        clauses = [make_clause(RiskLevel.HIGH, confidence=1.0) for _ in range(10)]
        result = self.agent.process({"clauses": clauses})
        assert 0 <= result["risk_score"] <= 100

    def test_key_concerns_max_3(self):
        clauses = [make_clause(RiskLevel.HIGH, category=f"category_{i}") for i in range(5)]
        result = self.agent.process({"clauses": clauses})
        assert len(result["key_concerns"]) <= 3

    def test_counts_by_risk_level(self):
        clauses = [
            make_clause(RiskLevel.HIGH),
            make_clause(RiskLevel.HIGH),
            make_clause(RiskLevel.MEDIUM),
            make_clause(RiskLevel.LOW),
        ]
        result = self.agent.process({"clauses": clauses})
        assert result["high_risk_count"] == 2
        assert result["medium_risk_count"] == 1
        assert result["total_clauses_analyzed"] == 4

    def test_execute_wraps_process(self):
        clauses = [make_clause(RiskLevel.MEDIUM)]
        result = self.agent.execute({"clauses": clauses})
        assert result["success"] is True
        assert "result" in result
        assert "execution_time" in result


class TestSummarizerAgent:
    def setup_method(self):
        # Import here so model is not loaded during setup
        from app.agents.summarize_agent import SummarizerAgent
        self.agent = SummarizerAgent()

    def test_chunk_text_splits_correctly(self):
        text = ". ".join(["This is a sentence"] * 100)
        chunks = self.agent._chunk_text(text, max_length=200)
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 220  # some tolerance

    def test_simplify_language_replaces_jargon(self):
        text = "You must indemnify the company pursuant to the agreement."
        simplified = self.agent._simplify_language(text)
        assert "indemnify" not in simplified.lower()
        assert "pursuant to" not in simplified.lower()

    def test_grade8_splits_long_sentences(self):
        long_sentence = "The company will collect and use and share your personal information and financial data and health records and browsing history in many ways."
        result = self.agent._ensure_grade8_readability(long_sentence)
        # Should be split into shorter parts
        assert len(result) > 0

    @patch('app.agents.summarize_agent.pipeline')
    def test_process_calls_model(self, mock_pipeline):
        mock_model = MagicMock()
        mock_model.return_value = [{'summary_text': 'Test summary output.'}]
        mock_pipeline.return_value = mock_model

        self.agent.model = mock_model
        self.agent.is_loaded = True

        result = self.agent.process({"text": SAMPLE_TEXT})
        assert "summary" in result
        assert "chunks_processed" in result
        assert isinstance(result["summary"], str)



class TestClauseDetectionAgent:
    def setup_method(self):
        from app.agents.clause_agent import ClauseDetectionAgent
        self.agent = ClauseDetectionAgent()

    def test_extract_sentences_returns_list(self):
        sentences = self.agent._extract_sentences(SAMPLE_TEXT)
        assert isinstance(sentences, list)
        assert len(sentences) > 0
        # Each item should be (sentence, start, end)
        for item in sentences:
            assert len(item) == 3

    def test_assess_clause_risk_high(self):
        risk = self.agent._assess_clause_risk(
            "data collection",
            "We collect personally identifiable and health data from users."
        )
        assert risk == RiskLevel.HIGH

    def test_assess_clause_risk_medium(self):
        risk = self.agent._assess_clause_risk(
            "data collection",
            "We collect device information and location data."
        )
        assert risk == RiskLevel.MEDIUM

    def test_assess_clause_risk_unknown_category(self):
        risk = self.agent._assess_clause_risk("unknown_category", "some text here")
        assert risk == RiskLevel.MEDIUM  # default

    def test_generate_explanation_returns_string(self):
        from app.models.schemas import RiskLevel
        explanation = self.agent._generate_explanation("arbitration clause", RiskLevel.HIGH)
        assert isinstance(explanation, str)
        assert len(explanation) > 10

    @patch('app.agents.clause_agent.pipeline')
    def test_process_filters_low_confidence(self, mock_pipeline):
        mock_model = MagicMock()
        # Return low confidence for all
        mock_model.return_value = {
            'labels': ['data collection'],
            'scores': [0.3]  # below threshold
        }
        mock_pipeline.return_value = mock_model

        self.agent.model = mock_model
        self.agent.is_loaded = True

        result = self.agent.process({"text": SAMPLE_TEXT})
        assert result["clauses"] == []