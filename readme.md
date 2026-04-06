# AI Terms Analyzer

A Chrome extension + FastAPI backend that analyzes Terms & Conditions using a **3-agent AI pipeline** with Hugging Face transformers. Instantly understand what you're agreeing to before clicking "I Accept".

## Features

- **Summarizer Agent** — Plain-English summary of the full document
- **Clause Detection Agent** — Detects arbitration, auto-renewal, data-selling, and other risky clauses
- **Risk Assessment Agent** — Overall risk score (0–100) with grade and recommendations
- Parallel agent execution for fast results
- Response caching to avoid redundant API calls
- Chrome extension popup with floating analysis box

## Project Structure

```
ai-terms-analyzer/
├── backend/          # FastAPI app with 3-agent pipeline
├── extension/        # Chrome extension (MV3)
├── scripts/          # Setup and utility scripts
├── docs/             # API, architecture, deployment docs
└── docker-compose.yml
```

## Quick Start

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Docker

```bash
docker-compose up --build
```

### 3. Chrome Extension

1. Open `chrome://extensions`
2. Enable **Developer mode**
3. Click **Load unpacked** → select the `extension/` folder

## API

```
POST /api/v1/analyze
{
  "text": "<T&C document text>",
  "url": "https://example.com/tos"  // optional
}
```

See [docs/API.md](docs/API.md) for full documentation.

## Running Tests

```bash
cd backend
pytest tests/ -v
```

## Tech Stack

- **Backend**: Python, FastAPI, Anthropic Claude API
- **Extension**: Vanilla JS, Chrome MV3
- **Infra**: Docker, docker-compose

## License

MIT