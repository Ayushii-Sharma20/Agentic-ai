# Architecture

## Overview

```
Browser (Chrome Extension)
        │
        │  POST /api/v2/analyze  (text + url)
        ▼
┌─────────────────────────────┐
│       FastAPI Backend        │
│                             │
│  ┌───────────────────────┐  │
│  │   AnalyzerPipeline    │  │
│  │                       │  │
│  │  ┌─────────────────┐  │  │
│  │  │  Stage 1 (async)│  │  │
│  │  │  ┌───────────┐  │  │  │
│  │  │  │Summarizer │  │  │  │
│  │  │  │  Agent    │──┼──┼──┼──► Hugging Face Models
│  │  │  └───────────┘  │  │  │
│  │  │  ┌───────────┐  │  │  │
│  │  │  │  Clause   │  │  │  │
│  │  │  │  Agent    │──┼──┼──┼──► Hugging Face Models
│  │  │  └───────────┘  │  │  │
│  │  └─────────────────┘  │  │
│  │          │             │  │
│  │  ┌───────▼───────────┐ │  │
│  │  │    Stage 2        │ │  │
│  │  │  ┌─────────────┐  │ │  │
│  │  │  │    Risk     │  │ │  │
│  │  │  │   Agent     │──┼─┼──┼──► Rule-based Analysis
│  │  │  └─────────────┘  │ │  │
│  │  └───────────────────┘ │  │
│  └───────────────────────┘  │
│           │                  │
│       Cache Layer            │
│      (in-memory / Redis)     │
└─────────────────────────────┘
        │
        ▼
   JSON Response
```

## Agent Descriptions

### Agent 1: SummarizerAgent
- **Input**: Raw T&C text
- **Output**: Plain-English summary
- **Model**: Hugging Face summarization model (sshleifer/distilbart-cnn-12-6)
- **Runs**: In parallel with ClauseAgent

### Agent 2: ClauseAgent
- **Input**: Raw T&C text
- **Output**: List of detected clauses with category, text, confidence, risk level, explanation
- **Model**: Hugging Face zero-shot classification model (facebook/bart-large-mnli)
- **Runs**: In parallel with SummarizerAgent

### Agent 3: RiskAgent
- **Input**: Detected clauses
- **Output**: Risk score, level, recommendation, key concerns
- **Logic**: Rule-based analysis of clause risks
- **Runs**: After Stages 1 & 2 complete

## Caching Strategy

Results are cached by `SHA-256(text)` in an in-memory LRU cache (default 100 entries, 1hr TTL). This avoids redundant API calls when the same T&C is analyzed multiple times. For production, swap in Redis.

## Extension ↔ Backend Flow

1. User visits a page with T&C text
2. `content.js` detects and extracts T&C text from the DOM
3. User clicks the extension popup → triggers analysis
4. `api.js` POSTs text to `/api/v2/analyze`
5. Backend runs 3-agent pipeline
6. Extension renders summary, clauses, and risk score in floating box