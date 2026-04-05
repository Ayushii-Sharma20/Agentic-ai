from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Recommendation(str, Enum):
    SAFE = "Safe to Accept"
    REVIEW = "Read Carefully"
    AVOID = "Not Recommended"

class DetectedClause(BaseModel):
    category: str
    text: str
    confidence: float = Field(..., ge=0, le=1)
    risk_level: RiskLevel
    explanation: str
    position: Optional[dict] = None  # {start: int, end: int}

class AnalysisRequest(BaseModel):
    text: str = Field(..., min_length=100)
    url: Optional[str] = None
    
class AnalysisResponse(BaseModel):
    summary: str
    risk_level: RiskLevel
    risk_score: int = Field(..., ge=0, le=100)
    recommendation: Recommendation
    clauses: List[DetectedClause]
    key_concerns: List[str]
    processing_time: float
    
class HealthCheck(BaseModel):
    status: str
    version: str
    agents_loaded: bool