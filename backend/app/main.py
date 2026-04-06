import os
import certifi

os.environ['SSL_CERT_FILE'] = certifi.where()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .api.routes import router
from .pipeline.analyzer_pipeline import AnalyzerPipeline
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
settings = get_settings()

# Global pipeline instance to persist models in memory
pipeline_instance = None

# Create app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="3-Agent AI Pipeline for Terms & Conditions Analysis"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v2")

@app.on_event("startup")
async def startup_event():
    """Preload models on startup to avoid cold start delays"""
    global pipeline_instance
    logger.info("🚀 Preloading AI models...")
    try:
        pipeline_instance = AnalyzerPipeline()
        pipeline_instance.initialize()
        logger.info("✅ Models preloaded and ready!")
    except Exception as e:
        logger.error(f"❌ Failed to preload models: {e}")
        raise

@app.get("/")
async def root():
    return {
        "message": "AI Terms Analyzer API",
        "version": settings.API_VERSION,
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "ok", "models_loaded": pipeline_instance is not None}