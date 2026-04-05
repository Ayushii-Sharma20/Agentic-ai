# Deployment Guide

## Local Development

```bash
cd backend
cp .env.example .env
# Set ANTHROPIC_API_KEY in .env

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker (Recommended)

```bash
cp backend/.env.example backend/.env
# Set ANTHROPIC_API_KEY in backend/.env

docker-compose up --build
# Backend available at http://localhost:8000
```

## Production Deployment

### Environment Variables (Required)

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `SECRET_KEY` | Random secret (use `openssl rand -hex 32`) |
| `APP_ENV` | Set to `production` |
| `DEBUG` | Set to `false` |

### Recommended: Railway / Render / Fly.io

1. Push the `backend/` folder to a new repo or connect this repo
2. Set environment variables in the platform dashboard
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Chrome Extension

For public distribution:
1. Run `scripts/build_extension.sh` to create a production zip
2. Upload to the [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
3. Update `extension/utils/api.js` → set `BASE_URL` to your production backend URL

For local/team use:
1. Open `chrome://extensions`
2. Enable **Developer mode**
3. Click **Load unpacked** → select the `extension/` folder

## Health Check

```
GET /health → { "status": "ok" }
GET /api/v1/analyze/status → { "status": "ready" }
```