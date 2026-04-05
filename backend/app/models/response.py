# backend/app/models/response.py
from pydantic import BaseModel
from typing import List, Optional, Any
from .schemas import RiskLevel, Recommendation, DetectedClause


class AgentResult(BaseModel):
    """Result wrapper for individual agent execution"""
    agent: str
    success: bool
    execution_time: float
    result: Optional[Any] = None
    error: Optional[str] = None


class PipelineStatus(BaseModel):
    """Status of the 3-agent pipeline"""
    is_initialized: bool
    agents: List[str]
    total_agents: int = 3


class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str
    error_type: Optional[str] = None


class CacheStats(BaseModel):
    """Cache statistics"""
    total_entries: int
    live_entries: int
    expired_entries: int
    ttl_seconds: int


class AnalysisSummary(BaseModel):
    """Lightweight summary for list views"""
    url: Optional[str]
    risk_level: RiskLevel
    risk_score: int
    recommendation: Recommendation
    clause_count: int
    high_risk_count: int
    processing_time: float