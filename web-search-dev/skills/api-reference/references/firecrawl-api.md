# Firecrawl REST API

Base URL: `https://api.firecrawl.dev`

## Scrape a Page

```bash
curl -s -X POST https://api.firecrawl.dev/v2/scrape \
  -H "Authorization: Bearer ${FIRECRAWL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/page",
    "formats": ["markdown", "links"],
    "onlyMainContent": true
  }' | jq .
```

Responses are cached by default (`maxAge` defaults to 2 days) — pass `"maxAge": 0` to force a fresh scrape.

With structured JSON extraction (object-style format):
```bash
curl -s -X POST https://api.firecrawl.dev/v2/scrape \
  -H "Authorization: Bearer ${FIRECRAWL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/pricing",
    "formats": [
      "markdown",
      {
        "type": "json",
        "prompt": "Extract plan names and prices",
        "schema": {
          "type": "object",
          "properties": {
            "plans": { "type": "array", "items": { "type": "object", "properties": { "name": { "type": "string" }, "price": { "type": "string" } } } }
          }
        }
      }
    ]
  }' | jq .
```

With JS rendering wait:
```bash
curl -s -X POST https://api.firecrawl.dev/v2/scrape \
  -H "Authorization: Bearer ${FIRECRAWL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/spa",
    "formats": ["markdown"],
    "waitFor": 3000
  }' | jq .
```

## Search the Web

```bash
curl -s -X POST https://api.firecrawl.dev/v2/search \
  -H "Authorization: Bearer ${FIRECRAWL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Next.js server components tutorial",
    "limit": 10
  }' | jq .
```

## Start a Crawl

```bash
curl -s -X POST https://api.firecrawl.dev/v2/crawl \
  -H "Authorization: Bearer ${FIRECRAWL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://docs.example.com",
    "limit": 50,
    "maxDiscoveryDepth": 3,
    "sitemap": "include",
    "includePaths": ["/docs/*"],
    "scrapeOptions": {
      "formats": ["markdown"]
    }
  }' | jq .
```

Or configure the crawler with a natural-language prompt:

```bash
curl -s -X POST https://api.firecrawl.dev/v2/crawl \
  -H "Authorization: Bearer ${FIRECRAWL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://docs.example.com",
    "prompt": "Get all docs pages",
    "limit": 50
  }' | jq .
```

Returns `{ "id": "crawl-job-id" }`. Check status:

```bash
curl -s https://api.firecrawl.dev/v2/crawl/${CRAWL_ID} \
  -H "Authorization: Bearer ${FIRECRAWL_API_KEY}" | jq .
```

## Map Site URLs

```bash
curl -s -X POST https://api.firecrawl.dev/v2/map \
  -H "Authorization: Bearer ${FIRECRAWL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "limit": 100
  }' | jq .
```

## Extract Structured Data

```bash
curl -s -X POST https://api.firecrawl.dev/v2/extract \
  -H "Authorization: Bearer ${FIRECRAWL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://example.com/pricing"],
    "prompt": "Extract pricing plans",
    "schema": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "plan": { "type": "string" },
          "price": { "type": "string" },
          "features": { "type": "array", "items": { "type": "string" } }
        }
      }
    }
  }' | jq .
```

## Start Research Agent

```bash
curl -s -X POST https://api.firecrawl.dev/v2/agent \
  -H "Authorization: Bearer ${FIRECRAWL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Find the top 5 headless CMS platforms and compare their pricing",
    "model": "spark-1-mini"
  }' | jq .
```

## Batch Scrape

```bash
curl -s -X POST https://api.firecrawl.dev/v2/batch/scrape \
  -H "Authorization: Bearer ${FIRECRAWL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://example.com/page1",
      "https://example.com/page2",
      "https://example.com/page3"
    ],
    "formats": ["markdown"]
  }' | jq .
```

## Error Codes

| Code | Meaning |
|------|---------|
| 401 | Missing or invalid API key |
| 402 | Payment required (insufficient credits) |
| 429 | Rate limit exceeded |
| 500 | Server error |
