from transformers import pipeline
import re
from .base_agent import BaseAgent
from ..config import get_settings

settings = get_settings()


class SummarizerAgent(BaseAgent):
    """Agent responsible for simple, human-friendly summarization"""

    def __init__(self):
        super().__init__("SummarizerAgent")
        self.model = None  # not used (fast mode)

    def load(self):
        """Optional model load (not needed for fast mode)"""
        try:
            self.model = pipeline(
                "summarization",
                model=settings.SUMMARIZER_MODEL,
                device=-1
            )
            self.is_loaded = True
        except Exception as e:
            raise RuntimeError(f"Failed to load summarizer: {e}")

    def _make_simple_summary(self, text: str) -> str:
        text = text.lower()

        issues = []

        # 🔍 Detect issues
        if "data" in text:
            issues.append("collects your data")

        if "share" in text or "third party" in text:
            issues.append("may share your data with other companies")

        if "cookies" in text or "track" in text:
            issues.append("tracks your activity")

        if "location" in text:
            issues.append("tracks your location")

        if "ads" in text or "advertising" in text:
            issues.append("shows targeted ads")

        # 🧠 No issue fallback
        if not issues:
            issues.append("has no major problems")

        # 🎯 Decision logic
        if len(issues) >= 3:
            decision = "Avoid if possible"
            emoji = "🔴"
        elif len(issues) >= 1:
            decision = "Be careful before accepting"
            emoji = "🟡"
        else:
            decision = "Safe to accept"
            emoji = "🟢"

        # 🧾 Build natural sentence
        if len(issues) == 1:
            explanation = issues[0]
        elif len(issues) == 2:
            explanation = f"{issues[0]} and {issues[1]}"
        else:
            explanation = ", ".join(issues[:-1]) + f", and {issues[-1]}"

        # 📦 Final summary output
        summary = (
            "🧾 Simple explanation:\n\n"
            f"👉 This website {explanation}.\n\n\n"
            "⚠ What it means for you:\n\n"
        )

        # Impact line
        if "share" in explanation:
            summary += "🔁 Your data may be shared with other companies.\n\n"
        elif "track" in explanation:
            summary += "👀 Your activity may be tracked.\n\n"
        elif "data" in explanation:
            summary += "📊 Your personal data is collected.\n\n"
        else:
            summary += "✅ No major risks detected.\n\n"

        # 🎯 Final advice
        summary += f"\n{emoji} Final advice:\n\n👉 {decision}"

        return summary

    def process(self, input_data: dict) -> dict:
        """Main summarization logic"""

        text = input_data.get("text", "")

        if not text:
            return {
                "summary": "No content to analyze.",
                "chunks_processed": 0,
                "original_length": 0,
                "summary_length": 0
            }

        combined_summary = self._make_simple_summary(text)

        return {
            "summary": combined_summary,
            "chunks_processed": 1,
            "original_length": len(text),
            "summary_length": len(combined_summary)
        }