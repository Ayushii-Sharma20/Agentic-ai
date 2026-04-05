from transformers import pipeline
import re
from .base_agent import BaseAgent
from ..config import get_settings

settings = get_settings()

class SummarizerAgent(BaseAgent):
    """Agent responsible for text summarization"""
    
    def __init__(self):
        super().__init__("SummarizerAgent")
        self.jargon_map = {
            "arbitration": "private dispute resolution (not court)",
            "indemnify": "take responsibility for",
            "pursuant to": "according to",
            "notwithstanding": "despite",
            "terminate": "end or cancel",
            "aggregate": "combined",
            "cookies": "small tracking files",
            "third parties": "other companies",
            "affiliates": "partner companies",
            "liability": "legal responsibility"
        }
    
    def load(self):
        """Load summarization model"""
        try:
            self.model = pipeline(
                "summarization",
                model=settings.SUMMARIZER_MODEL,
                device=-1  # CPU, use 0 for GPU
            )
            self.is_loaded = True
        except Exception as e:
            raise RuntimeError(f"Failed to load summarizer: {e}")
    
    def _chunk_text(self, text: str, max_length: int = 1024) -> list:
        """Split text into chunks for processing"""
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _simplify_language(self, text: str) -> str:
        """Replace legal jargon with simple terms"""
        simplified = text
        for jargon, simple in self.jargon_map.items():
            simplified = re.sub(
                rf'\b{jargon}\b',
                simple,
                simplified,
                flags=re.IGNORECASE
            )
        return simplified
    
    def _ensure_grade8_readability(self, text: str) -> str:
        """Simplify to 8th-grade reading level"""
        # Split long sentences
        sentences = re.split(r'[.!?]', text)
        simplified_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If sentence too long (>25 words), try to split
            words = sentence.split()
            if len(words) > 25:
                # Split at conjunctions
                parts = re.split(r'\b(and|but|or|however|therefore)\b', sentence)
                simplified_sentences.extend([p.strip() for p in parts if p.strip()])
            else:
                simplified_sentences.append(sentence)
        
        return '. '.join(simplified_sentences) + '.'
    
    def process(self, input_data: dict) -> dict:
        """
        Generate user-friendly summary
        
        Args:
            input_data: {"text": str}
        
        Returns:
            {"summary": str, "chunks_processed": int}
        """
        text = input_data["text"]
        
        # Chunk text if too long
        chunks = self._chunk_text(text, settings.CHUNK_SIZE)
        
        summaries = []
        for chunk in chunks[:3]:  # Limit to 3 chunks for speed
            if len(chunk) < 100:
                continue
                
            summary = self.model(
                chunk,
                max_length=settings.MAX_SUMMARY_LENGTH,
                min_length=settings.MIN_SUMMARY_LENGTH,
                do_sample=False
            )[0]['summary_text']
            
            summaries.append(summary)
        
        # Combine summaries
        combined_summary = ' '.join(summaries)
        
        # Post-process
        combined_summary = self._simplify_language(combined_summary)
        combined_summary = self._ensure_grade8_readability(combined_summary)
        
        return {
            "summary": combined_summary,
            "chunks_processed": len(chunks),
            "original_length": len(text),
            "summary_length": len(combined_summary)
        }