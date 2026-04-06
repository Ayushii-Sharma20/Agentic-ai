from abc import ABC, abstractmethod
import time
import logging
import hashlib
import json
from typing import Any, Dict
from ..config import get_settings
from ..utils.cache import InMemoryCache

logger = logging.getLogger(__name__)
settings = get_settings()

class BaseAgent(ABC):
    """Base class for all agents in the pipeline"""
    
    def __init__(self, name: str):
        self.name = name
        self.model = None
        self.is_loaded = False
        self.cache = InMemoryCache(ttl=settings.CACHE_TTL) if settings.ENABLE_CACHE else None
        
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
            
            if self.cache:
                key = hashlib.sha256(json.dumps(input_data, sort_keys=True).encode()).hexdigest()
                cached_result = self.cache.get_by_key(key)
                if cached_result:
                    logger.info(f"{self.name} cache hit")
                    return {
                        "success": True,
                        "agent": self.name,
                        "result": cached_result,
                        "execution_time": 0.0
                    }
            
            result = self.process(input_data)
            execution_time = time.time() - start_time
            
            if self.cache:
                self.cache.set_by_key(key, result)
            
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