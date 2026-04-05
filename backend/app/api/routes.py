from fastapi import APIRouter, HTTPException, status
from ..models.schemas import AnalysisRequest, AnalysisResponse, HealthCheck
from ..pipeline.analyzer_pipeline import AnalyzerPipeline
from ..config import get_settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()

# Initialize pipeline (singleton)
pipeline = AnalyzerPipeline()

@router.on_event("startup")
async def startup_event():
    """Initialize pipeline on startup"""
    try:
        pipeline.initialize()
        logger.info("Pipeline ready")
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    return HealthCheck(
        status="healthy" if pipeline.is_initialized else "initializing",
        version=settings.API_VERSION,
        agents_loaded=pipeline.is_initialized
    )

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_terms(request: AnalysisRequest):
    """
    Analyze Terms & Conditions or Privacy Policy
    
    Returns comprehensive analysis with:
    - Summary
    - Detected clauses
    - Risk assessment
    - Recommendation
    """
    try:
        result = pipeline.analyze(
            text=request.text,
            url=request.url
        )
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis failed. Please try again."
        )