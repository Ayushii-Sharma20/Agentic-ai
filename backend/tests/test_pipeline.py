import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from app.pipeline.analyzer_pipeline import AnalyzerPipeline

SAMPLE_TC = """
Terms of Service - SampleApp

1. Data Collection
We collect your name, email, location, browsing history, and device identifiers.
We may share this data with third-party advertising partners.

2. Arbitration
All disputes shall be resolved through binding arbitration. You waive your right
to a jury trial and to participate in class action lawsuits.

3. Auto-Renewal
Your subscription automatically renews each month. Cancellation must be made
48 hours before the renewal date or you will be charged.

4. Limitation of Liability
SampleApp's liability is limited to $50 regardless of damages incurred.

5. Changes to Terms
We may update these terms at any time without notice. Continued use constitutes acceptance.
"""

MOCK_SUMMARY = {
    "summary": "SampleApp collects extensive data and shares it with advertisers.",
    "key_points": ["Data sharing with third parties", "Binding arbitration required"],
    "data_collection": "Name, email, location, browsing history, device IDs",
    "user_rights": "Limited — no class action, no jury trial",
    "company_rights": "Can share data, change terms anytime, auto-renew subscription",
    "word_count": 120,
}

MOCK_CLAUSES = {
    "clauses": [
        {
            "type": "arbitration",
            "title": "Mandatory Arbitration",
            "excerpt": "All disputes shall be resolved through binding arbitration.",
            "explanation": "You cannot sue in court.",
            "severity": "high",
        }
    ],
    "total_clauses_found": 1,
}

MOCK_RISK = {
    "overall_score": 25,
    "grade": "D",
    "risk_level": "high",
    "privacy_score": 20,
    "fairness_score": 30,
    "transparency_score": 40,
    "risks": [],
    "recommendations": ["Use a VPN", "Opt out of data sharing"],
    "tldr": "These terms heavily favor the company — proceed with caution.",
}


@pytest.fixture
def pipeline():
    return AnalyzerPipeline()


@pytest.mark.asyncio
async def test_pipeline_runs_all_agents(pipeline):
    with (
        patch.object(pipeline.summarizer, "run", new_callable=AsyncMock, return_value=MOCK_SUMMARY),
        patch.object(pipeline.clause_detector, "run", new_callable=AsyncMock, return_value=MOCK_CLAUSES),
        patch.object(pipeline.risk_assessor, "run", new_callable=AsyncMock, return_value=MOCK_RISK),
    ):
        result = await pipeline.analyze(SAMPLE_TC, url="https://example.com/tos")

    assert result["summary"] == MOCK_SUMMARY
    assert result["clauses"] == MOCK_CLAUSES
    assert result["risk"] == MOCK_RISK
    assert result["url"] == "https://example.com/tos"
    assert result["from_cache"] is False


@pytest.mark.asyncio
async def test_pipeline_caches_results(pipeline):
    with (
        patch.object(pipeline.summarizer, "run", new_callable=AsyncMock, return_value=MOCK_SUMMARY),
        patch.object(pipeline.clause_detector, "run", new_callable=AsyncMock, return_value=MOCK_CLAUSES),
        patch.object(pipeline.risk_assessor, "run", new_callable=AsyncMock, return_value=MOCK_RISK),
    ):
        result1 = await pipeline.analyze(SAMPLE_TC)
        result2 = await pipeline.analyze(SAMPLE_TC)  # should hit cache

    assert result1["from_cache"] is False
    assert result2["from_cache"] is True


@pytest.mark.asyncio
async def test_pipeline_passes_clause_context_to_risk_agent(pipeline):
    risk_mock = AsyncMock(return_value=MOCK_RISK)

    with (
        patch.object(pipeline.summarizer, "run", new_callable=AsyncMock, return_value=MOCK_SUMMARY),
        patch.object(pipeline.clause_detector, "run", new_callable=AsyncMock, return_value=MOCK_CLAUSES),
        patch.object(pipeline.risk_assessor, "run", risk_mock),
    ):
        await pipeline.analyze(SAMPLE_TC)

    # Verify risk agent was called with clause context
    call_kwargs = risk_mock.call_args
    assert call_kwargs.kwargs.get("context", {}).get("clauses") == MOCK_CLAUSES