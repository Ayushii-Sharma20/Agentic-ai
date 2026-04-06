import time
import logging
import concurrent.futures

from ..agents.summarize_agent import SummarizerAgent
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

        # Thread pool
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)

        # Cache
        self.cache = {}

    def initialize(self):
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

    def preprocess_text(self, text: str) -> str:
        chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
        return " ".join(chunks[:3])

    def analyze(self, text: str, url: str = None) -> AnalysisResponse:
        if not self.is_initialized:
            raise RuntimeError("Pipeline not initialized")

        pipeline_start = time.time()

        # 🔥 Preprocess
        text = self.preprocess_text(text)

        # 🔥 Cache check
        cache_key = hash(text)
        if cache_key in self.cache:
            logger.info("⚡ Returning cached result")
            return self.cache[cache_key]

        logger.info("Running agents in optimized parallel mode...")

        # Parallel execution
        future_summary = self.executor.submit(
            self.summarizer.execute, {"text": text}
        )
        future_clause = self.executor.submit(
            self.clause_detector.execute, {"text": text}
        )

        summary_result = future_summary.result()
        clause_result = future_clause.result()

        # Extract summary
        if not summary_result["success"]:
            raise RuntimeError(summary_result["error"])
        summary = summary_result["result"]["summary"]

        # Extract clauses
        if not clause_result["success"]:
            logger.warning("Clause detection failed")
            raw_clauses = []
        else:
            raw_clauses = clause_result["result"]["clauses"]

        # 🔥 Convert DetectedClause → dict (CRITICAL FIX)
        clauses = [
            c.dict() if hasattr(c, "dict") else c
            for c in raw_clauses
        ]

        # Risk assessment
        future_risk = self.executor.submit(
            self.risk_assessor.execute,
            {"clauses": clauses}
        )

        risk_result = future_risk.result()

        if not risk_result["success"]:
            raise RuntimeError(risk_result["error"])

        risk_data = risk_result["result"]

        total_time = time.time() - pipeline_start

        # Final response
        response = AnalysisResponse(
            summary=summary,
            risk_level=risk_data["risk_level"],
            risk_score=risk_data["risk_score"],
            recommendation=risk_data["recommendation"],
            clauses=clauses,  # ✅ now JSON safe
            key_concerns=risk_data["key_concerns"],
            processing_time=round(total_time, 2)
        )

        logger.info(f"⚡ Pipeline completed in {total_time:.2f}s")

        # Cache result
        self.cache[cache_key] = response

        return response