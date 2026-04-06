from fastapi import APIRouter, HTTPException, status
from ..models.schemas import AnalysisRequest, AnalysisResponse, HealthCheck
from ..config import get_settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()

# Get global pipeline instance from main
def get_pipeline():
    """Get the global pipeline instance"""
    from ..main import pipeline_instance
    if pipeline_instance is None:
        raise RuntimeError("Pipeline not initialized")
    return pipeline_instance

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    try:
        pipeline = get_pipeline()
        return HealthCheck(
            status="healthy",
            version=settings.API_VERSION,
            agents_loaded=True
        )
    except RuntimeError:
        return HealthCheck(
            status="initializing",
            version=settings.API_VERSION,
            agents_loaded=False
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
        pipeline = get_pipeline()
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