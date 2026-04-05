import time
import logging
from typing import Dict
from ..agents.summarizer_agent import SummarizerAgent
from ..agents.clause_agent import ClauseDetectionAgent
from ..agents.risk_agent import RiskAssessmentAgent
from ..models.schemas import AnalysisResponse

logger = logging.getLogger(__name__)

class AnalyzerPipeline:
    """Orchestrates the 3-agent analysis pipeline"""
    
    def __init__(self):
        self.summarizer = SummarizerAgent()
        self.clause_detector = ClauseDetectionAgent()
        self.risk_assessor = RiskAssessmentAgent()
        self.is_initialized = False
    
    def initialize(self):
        """Load all agents"""
        logger.info("Initializing 3-agent pipeline...")
        start_time = time.time()
        
        try:
            self.summarizer.load()
            logger.info("✓ Summarizer loaded")
            
            self.clause_detector.load()
            logger.info("✓ Clause detector loaded")
            
            self.risk_assessor.load()
            logger.info("✓ Risk assessor loaded")
            
            self.is_initialized = True
            logger.info(f"Pipeline initialized in {time.time() - start_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Pipeline initialization failed: {e}")
            raise
    
    def analyze(self, text: str, url: str = None) -> AnalysisResponse:
        """
        Run full 3-agent analysis pipeline
        
        Flow:
        1. Summarizer Agent → Generate summary
        2. Clause Detection Agent → Extract clauses
        3. Risk Assessment Agent → Calculate risk
        
        Args:
            text: T&C or Privacy Policy text
            url: Optional source URL
        
        Returns:
            AnalysisResponse with all results
        """
        if not self.is_initialized:
            raise RuntimeError("Pipeline not initialized. Call initialize() first.")
        
        pipeline_start = time.time()
        
        # AGENT 1: Summarization
        logger.info("Running Agent 1: Summarizer...")
        summary_result = self.summarizer.execute({"text": text})
        
        if not summary_result["success"]:
            raise RuntimeError(f"Summarizer failed: {summary_result['error']}")
        
        summary = summary_result["result"]["summary"]
        
        # AGENT 2: Clause Detection
        logger.info("Running Agent 2: Clause Detector...")
        clause_result = self.clause_detector.execute({"text": text})
        
        if not clause_result["success"]:
            raise RuntimeError(f"Clause detector failed: {clause_result['error']}")
        
        clauses = clause_result["result"]["clauses"]
        
        # AGENT 3: Risk Assessment
        logger.info("Running Agent 3: Risk Assessor...")
        risk_result = self.risk_assessor.execute({"clauses": clauses})
        
        if not risk_result["success"]:
            raise RuntimeError(f"Risk assessor failed: {risk_result['error']}")
        
        risk_data = risk_result["result"]
        
        # Combine results
        total_time = time.time() - pipeline_start
        
        response = AnalysisResponse(
            summary=summary,
            risk_level=risk_data["risk_level"],
            risk_score=risk_data["risk_score"],
            recommendation=risk_data["recommendation"],
            clauses=clauses,
            key_concerns=risk_data["key_concerns"],
            processing_time=round(total_time, 2)
        )
        
        logger.info(f"Pipeline completed in {total_time:.2f}s")
        logger.info(f"Result: {risk_data['risk_level'].value} risk, {len(clauses)} clauses")
        
        return response