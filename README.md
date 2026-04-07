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
| `AZURE_OPENAI_API_VERSION` | ❌ | `2025-01-01-preview` | API version string |
| `ALLOWED_ORIGINS` | ❌ | `*` | Comma-separated CORS origins (e.g. `https://app.hobbyiq.com`). Set explicitly in production. |

## Client examples

### JavaScript / Browser (fetch)

The server returns `Access-Control-Allow-Origin` headers so browser clients work out of the box. Set `ALLOWED_ORIGINS` to your web app's origin in production (see [Environment variables](#environment-variables)).

```js
fetch('https://<your-container-app-host>/api/v1/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: 'Should I buy or hold?', user_id: 'webuser' })
})
  .then(res => {
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  })
  .then(data => console.log(data.answer))
  .catch(err => console.error(err));
```

### iOS / Swift (URLSession)

```swift
import Foundation

struct QueryRequest: Encodable {
    let query: String
    let userId: String

    enum CodingKeys: String, CodingKey {
        case query
        case userId = "user_id"
    }
}

struct QueryResponse: Decodable {
    let userId: String
    let query: String
    let answer: String

    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case query
        case answer
    }
}

func askHobbyIQ(question: String, userId: String, completion: @escaping (Result<QueryResponse, Error>) -> Void) {
    let url = URL(string: "https://<your-container-app-host>/api/v1/query")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.addValue("application/json", forHTTPHeaderField: "Content-Type")

    let body = QueryRequest(query: question, userId: userId)
    request.httpBody = try? JSONEncoder().encode(body)

    URLSession.shared.dataTask(with: request) { data, response, error in
        if let error = error {
            completion(.failure(error))
            return
        }
        guard let data = data else {
            completion(.failure(URLError(.badServerResponse)))
            return
        }
        do {
            let result = try JSONDecoder().decode(QueryResponse.self, from: data)
            completion(.success(result))
        } catch {
            completion(.failure(error))
        }
    }.resume()
}

// Usage
askHobbyIQ(question: "Should I buy or hold?", userId: "test123") { result in
    switch result {
    case .success(let response):
        print(response.answer)
    case .failure(let error):
        print("Error:", error)
    }
}
```

**Response shape**

```json
{
  "user_id": "test123",
  "query": "Should I buy or hold?",
  "answer": "Based on current market trends..."
}
```

**Error responses**

| HTTP status | Meaning |
|-------------|---------|
| `422` | Invalid request body (missing `query` or `user_id`) |
| `502` | Azure OpenAI upstream error |
| `500` | Unexpected server error |
