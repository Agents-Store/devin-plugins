# Jina REST API

Multiple base URLs — each service has its own endpoint.

## Reader API — Read Any URL

```bash
# Simple: prepend r.jina.ai to any URL
curl -s "https://r.jina.ai/https://nextjs.org/docs" \
  -H "Authorization: Bearer ${JINA_API_KEY}" | head -100
```

### With Options

```bash
curl -s "https://r.jina.ai/https://example.com/page" \
  -H "Authorization: Bearer ${JINA_API_KEY}" \
  -H "X-Return-Format: markdown" \
  -H "X-With-Generated-Alt: true" | head -200
```

### Extract Structured Data

```bash
curl -s "https://r.jina.ai/https://example.com/products" \
  -H "Authorization: Bearer ${JINA_API_KEY}" \
  -H "X-Json-Schema: {\"type\":\"object\",\"properties\":{\"title\":{\"type\":\"string\"},\"price\":{\"type\":\"number\"}}}"
```

### With CSS Selector

```bash
curl -s "https://r.jina.ai/https://example.com" \
  -H "Authorization: Bearer ${JINA_API_KEY}" \
  -H "X-Target-Selector: article.main-content"
```

## Search API — Web Search

```bash
curl -s "https://s.jina.ai/?q=React+hooks+best+practices" \
  -H "Authorization: Bearer ${JINA_API_KEY}" \
  -H "Accept: application/json"
```

### With Filters

```bash
curl -s "https://s.jina.ai/?q=Next.js+middleware&num=10" \
  -H "Authorization: Bearer ${JINA_API_KEY}" \
  -H "Accept: application/json" \
  -H "X-Site: nextjs.org"
```

Result count is controlled by the `num` field of the search request (query parameter or POST body) — there is no `X-Num` header.

## Embeddings API

```bash
curl -s -X POST https://api.jina.ai/v1/embeddings \
  -H "Authorization: Bearer ${JINA_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "jina-embeddings-v5-text-small",
    "input": ["How to implement search in a web app"]
  }' | jq .
```

## Reranker API

```bash
curl -s -X POST https://api.jina.ai/v1/rerank \
  -H "Authorization: Bearer ${JINA_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "jina-reranker-v3.5",
    "query": "best database for real-time apps",
    "documents": [
      "PostgreSQL is great for complex queries",
      "Redis excels at real-time data",
      "MongoDB offers flexible schemas"
    ]
  }' | jq .
```

## Classifier API

```bash
curl -s -X POST https://api.jina.ai/v1/classify \
  -H "Authorization: Bearer ${JINA_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": ["This product is amazing!", "Terrible experience"],
    "labels": ["positive", "negative", "neutral"]
  }' | jq .
```

## Segmenter API (Free)

```bash
curl -s -X POST https://api.jina.ai/v1/segment \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Long text to split into semantic chunks..."
  }' | jq .
```

No API key needed. Tokens not counted.

## Screenshot

```bash
curl -s "https://r.jina.ai/https://example.com" \
  -H "Authorization: Bearer ${JINA_API_KEY}" \
  -H "X-Return-Format: screenshot" -o screenshot.png
```

## Key Headers

| Header | Description |
|--------|-------------|
| `X-Return-Format` | `markdown`, `html`, `text`, `screenshot` |
| `X-With-Generated-Alt` | Auto-generate image alt text via VLM |
| `X-Target-Selector` | CSS selector to extract specific content |
| `X-Wait-For-Selector` | Wait for element before extraction |
| `X-Json-Schema` | JSON schema for structured extraction |
| `X-Instruction` | Natural language extraction instruction |
| `X-Site` | Restrict search to a domain |

Number of search results is set with the `num` request field of `s.jina.ai` (query parameter or body), not a header.

## Rate Limits

Reader (`r.jina.ai`) and Search (`s.jina.ai`) have separate limits:

| Tier | Reader RPM | Search RPM |
|------|------------|------------|
| No key | 20 | — (search requires a key) |
| With key | 500 | 100 |
| Premium | 5,000 | 1,000 |
