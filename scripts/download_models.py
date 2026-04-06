#!/usr/bin/env python
"""
Pre-download all required models for faster startup
Run this before Docker build: python scripts/download_models.py
"""

import logging
import os
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models to download
SUMMARIZER_MODEL = "sshleifer/distilbart-cnn-12-6"
CLASSIFIER_MODEL = "facebook/bart-large-mnli"

def download_models():
    """Download and cache all models"""
    logger.info("📥 Starting model downloads...")
    
    try:
        logger.info(f"📦 Downloading summarizer: {SUMMARIZER_MODEL}")
        pipeline("summarization", model=SUMMARIZER_MODEL, device=-1)
        logger.info("✅ Summarizer downloaded")
        
        logger.info(f"📦 Downloading classifier: {CLASSIFIER_MODEL}")
        pipeline("zero-shot-classification", model=CLASSIFIER_MODEL, device=-1)
        logger.info("✅ Classifier downloaded")
        
        logger.info("🎉 All models successfully downloaded and cached!")
        
    except Exception as e:
        logger.warning(f"⚠️  Model download failed (will download on first use): {e}")
        # Don't fail the Docker build if download fails

if __name__ == "__main__":
    download_models()
