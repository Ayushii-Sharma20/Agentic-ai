# Deployment Guide

## Local Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker (Recommended)

```bash
docker-compose up --build
# Backend available at http://localhost:8000
```

## Production Deployment

### Environment Variables (Optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Random secret for security | Auto-generated |
| `APP_ENV` | Environment (`development`/`production`) | `development` |
| `DEBUG` | Enable debug mode | `true` in development |

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