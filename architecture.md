# Architecture

## Overview

```
Browser (Chrome Extension)
        │
        │  POST /api/v1/analyze  (text + url)
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
│  │  │  │  Agent    │──┼──┼──┼──► Anthropic API
│  │  │  └───────────┘  │  │  │
│  │  │  ┌───────────┐  │  │  │
│  │  │  │  Clause   │  │  │  │
│  │  │  │  Agent    │──┼──┼──┼──► Anthropic API
│  │  │  └───────────┘  │  │  │
│  │  └─────────────────┘  │  │
│  │          │             │  │
│  │  ┌───────▼───────────┐ │  │
│  │  │    Stage 2        │ │  │
│  │  │  ┌─────────────┐  │ │  │
│  │  │  │    Risk     │  │ │  │
│  │  │  │   Agent     │──┼─┼──┼──► Anthropic API
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
- **Output**: Summary, key points, data collection info, user/company rights
- **Runs**: In parallel with ClauseAgent

### Agent 2: ClauseAgent
- **Input**: Raw T&C text
- **Output**: List of detected clauses with type, excerpt, explanation, severity
- **Runs**: In parallel with SummarizerAgent

### Agent 3: RiskAgent
- **Input**: Raw T&C text + ClauseAgent output (as context)
- **Output**: Risk scores, grade, recommendations, TL;DR
- **Runs**: After Stages 1 & 2 complete (uses clause context)

## Caching Strategy

Results are cached by `SHA-256(text)` in an in-memory LRU cache (default 100 entries, 1hr TTL). This avoids redundant API calls when the same T&C is analyzed multiple times. For production, swap in Redis.

## Extension ↔ Backend Flow

1. User visits a page with T&C text
2. `content.js` detects and extracts T&C text from the DOM
3. User clicks the extension popup → triggers analysis
4. `api.js` POSTs text to `/api/v1/analyze`
5. Backend runs 3-agent pipeline
6. Extension renders summary, clauses, and risk score in floating box