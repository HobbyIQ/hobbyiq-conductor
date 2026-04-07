# hobbyiq-conductor

AI-powered conductor service for sports-card and collectibles hobby queries, built with FastAPI and Azure OpenAI.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness / readiness probe |
| `POST` | `/api/v1/query` | Submit a hobby question |

### Query request body

```json
{
  "query": "Should I sell my Elly De La Cruz auto?",
  "user_id": "test-user"
}
```

### Example curl

```bash
curl -X POST https://<your-container-app-host>/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Should I sell my Elly De La Cruz auto?", "user_id":"test-user"}'
```

## Local development

```bash
# 1. Copy and fill in the environment variables
cp .env.example .env

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server (loads .env automatically via python-dotenv)
uvicorn app.main:app --reload
```

## Docker

```bash
docker build -t hobbyiq-conductor .
docker run -p 8000:8000 --env-file .env hobbyiq-conductor
```

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AZURE_OPENAI_API_KEY` | ✅ | — | Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | ✅ | — | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_DEPLOYMENT` | ✅ | — | Deployment / model name (e.g. `gpt-4o`) |
| `AZURE_OPENAI_API_VERSION` | ❌ | `2024-02-01` | API version string |
