#!/usr/bin/env python3
"""
Script to run the AI Terms Analyzer backend for testing.
"""

import uvicorn
import os
import sys

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

if __name__ == "__main__":
    print("Starting AI Terms Analyzer backend...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 