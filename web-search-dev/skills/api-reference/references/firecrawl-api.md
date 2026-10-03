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

For one known URL, use `/v2/scrape` with a `json` format (see "Scrape a Page" above). For several unknown URLs or data spread across sites, use the research agent below — it is the successor of the legacy extract endpoint.

The legacy `POST /v2/extract` endpoint (`urls`, `prompt`, `schema`, `enableWebSearch`) still exists but is in maintenance mode and its use is discouraged:

```bash
curl -s -X POST https://api.firecrawl.dev/v2/extract \
  -H "Authorization: Bearer ${FIRECRAWL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://example.com/pricing"],
    "prompt": "Extract pricing plans",
    "schema": { "type": "object", "properties": { "plans": { "type": "array", "items": { "type": "object" } } } }
  }' | jq .
```

## Start Research Agent

`model` defaults to `spark-2` and every run executes on it (`spark-1-mini` / `spark-1-pro` are still accepted but deprecated and route to `spark-2`). Control depth with `effort` (`low`, `medium`, `high`) and spend with `maxCredits`.

```bash
curl -s -X POST https://api.firecrawl.dev/v2/agent \
  -H "Authorization: Bearer ${FIRECRAWL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Find the top 5 headless CMS platforms and compare their pricing",
    "effort": "medium",
    "maxCredits": 500
  }' | jq .
```

Returns a job id; poll `GET /v2/agent/{jobId}` until it completes (`DELETE` cancels). Optional fields: `urls`, `schema`, `strictConstrainToURLs`, `webhook`.

## Interact With a Scraped Page

Scrape the page first (the response carries a scrape job id), then run code in its live browser session and stop it when done:

```bash
curl -s -X POST https://api.firecrawl.dev/v2/scrape/${SCRAPE_ID}/interact \
  -H "Authorization: Bearer ${FIRECRAWL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{ "code": "await page.title()", "language": "node", "timeout": 30 }' | jq .

curl -s -X DELETE https://api.firecrawl.dev/v2/scrape/${SCRAPE_ID}/interact \
  -H "Authorization: Bearer ${FIRECRAWL_API_KEY}"
```

`POST /v2/interact` creates a standalone session instead (`ttl`, `activityTtl`, `profile`).

## Developer Index and Research Papers

```bash
# GitHub issues, merged PRs, READMEs, docs
curl -s -G https://api.firecrawl.dev/v2/search/developer \
  -H "Authorization: Bearer ${FIRECRAWL_API_KEY}" \
  --data-urlencode "query=nextjs hydration mismatch date formatting" -d "k=5" | jq .

# Papers (also /{id} and /{id}/similar)
curl -s -G https://api.firecrawl.dev/v2/search/research/papers \
  -H "Authorization: Bearer ${FIRECRAWL_API_KEY}" \
  --data-urlencode "query=retrieval augmented generation" -d "k=10" | jq .
```

The developer endpoint also filters by `types`, `repos`, `language`, `topic`, `license`, `min_stars`, `max_stars`, `archived`, `fork`.

## Credit Usage

```bash
curl -s https://api.firecrawl.dev/v2/team/credit-usage \
  -H "Authorization: Bearer ${FIRECRAWL_API_KEY}" | jq .
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
