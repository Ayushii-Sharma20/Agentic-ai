# API Documentation

Base URL: `http://localhost:8000/api/v1`

---

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
  "url": "https://example.com/terms",
  "from_cache": false,
  "text_length": 12345,
  "summary": {
    "summary": "Plain-English summary...",
    "key_points": ["Point 1", "Point 2"],
    "data_collection": "What data is collected",
    "user_rights": "What rights you have",
    "company_rights": "What the company can do",
    "word_count": 3200
  },
  "clauses": {
    "total_clauses_found": 4,
    "clauses": [
      {
        "type": "arbitration",
        "title": "Mandatory Arbitration",
        "excerpt": "All disputes shall be resolved...",
        "explanation": "You cannot sue in regular court",
        "severity": "high"
      }
    ]
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