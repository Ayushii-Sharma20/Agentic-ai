# API Documentation

Base URL: `http://localhost:8000/api/v2`

---

## GET /health

Health check endpoint.

### Response

```json
{
  "status": "healthy",
  "version": "2.0.0",
  "agents_loaded": true
}
```

## POST /analyze

Analyze a Terms & Conditions document through the 3-agent pipeline.

### Request

```json
{
  "text": "Full text of the T&C document...",
  "url": "https://example.com/terms"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| text | string | Yes | Raw text extracted from the T&C page (min 100 chars) |
| url | string | No | Source URL for reference |

### Response

```json
{
  "summary": "Plain-English summary of the document...",
  "risk_level": "Medium",
  "risk_score": 45,
  "recommendation": "Read Carefully",
  "clauses": [
    {
      "category": "data collection",
      "text": "We collect personally identifiable information...",
      "confidence": 0.85,
      "risk_level": "High",
      "explanation": "This collects very sensitive personal information...",
      "position": {
        "start": 123,
        "end": 456
      }
    }
  ],
  "key_concerns": [
    "Data collection: This collects very sensitive personal information...",
    "Arbitration clause: You cannot sue in court or join class-action lawsuits."
  ],
  "processing_time": 2.34
}
```

| Field | Type | Description |
|-------|------|-------------|
| summary | string | AI-generated plain-English summary |
| risk_level | string | Overall risk: "Low", "Medium", "High" |
| risk_score | int | Risk score 0-100 |
| recommendation | string | User recommendation: "Safe to Accept", "Read Carefully", "Not Recommended" |
| clauses | array | Detected clauses with details |
| key_concerns | array | Top risk concerns |
| processing_time | float | Processing time in seconds |
  },
  "risk": {
    "overall_score": 35,
    "grade": "D",
    "risk_level": "high",
    "privacy_score": 30,
    "fairness_score": 25,
    "transparency_score": 50,
    "risks": [
      {
        "category": "privacy",
        "title": "Data Sold to Third Parties",
        "description": "Your data may be sold to advertisers",
        "severity": "high"
      }
    ],
    "recommendations": ["Opt out of marketing emails", "Use a disposable email"],
    "tldr": "These terms heavily favor the company — proceed with caution."
  }
}
```

### Error Responses

| Status | Meaning |
|--------|---------|
| 400 | Text too short or missing |
| 500 | Pipeline or API error |

---

## GET /analyze/status

Check if the pipeline is operational.

```json
{
  "status": "ready",
  "agents": ["summarizer", "clause_detector", "risk_assessor"]
}
```

---

## GET /health

Health check endpoint.

```json
{ "status": "ok", "version": "1.0.0" }
```