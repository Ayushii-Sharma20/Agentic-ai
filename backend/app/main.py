from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .api.routes import router
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

settings = get_settings()

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

@app.get("/")
async def root():
    return {
        "message": "AI Terms Analyzer API",
        "version": settings.API_VERSION,
        "docs": "/docs"
    }