from abc import ABC, abstractmethod
import time
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all agents in the pipeline"""
    
    def __init__(self, name: str):
        self.name = name
        self.model = None
        self.is_loaded = False
        
    @abstractmethod
    def load(self):
        """Load model and resources"""
        pass
    
    @abstractmethod
    def process(self, input_data: Any) -> Dict:
        """Process input and return results"""
        pass
    
    def execute(self, input_data: Any) -> Dict:
        """Execute agent with timing and error handling"""
        start_time = time.time()
        
        try:
            if not self.is_loaded:
                logger.warning(f"{self.name} not loaded, loading now...")
                self.load()
            
            result = self.process(input_data)
            execution_time = time.time() - start_time
            
            logger.info(f"{self.name} completed in {execution_time:.2f}s")
            
            return {
                "success": True,
                "agent": self.name,
                "result": result,
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"{self.name} failed: {str(e)}")
            return {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "execution_time": time.time() - start_time
            }