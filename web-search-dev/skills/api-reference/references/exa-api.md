# Exa REST API

Base URL: `https://api.exa.ai`

## Search (Primary Endpoint)

```bash
curl -s -X POST https://api.exa.ai/search \
  -H "x-api-key: ${EXA_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "React server components patterns",
    "numResults": 10,
    "type": "auto"
  }' | jq .
```

## Search with Content Extraction

Get search results + full page content in one call:

```bash
curl -s -X POST https://api.exa.ai/search \
  -H "x-api-key: ${EXA_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Prisma ORM pagination example",
    "numResults": 5,
    "contents": {
      "text": { "maxCharacters": 5000 },
      "highlights": { "maxCharacters": 200 }
    }
  }' | jq .
```

## Domain-Scoped Search

```bash
curl -s -X POST https://api.exa.ai/search \
  -H "x-api-key: ${EXA_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "authentication middleware",
    "numResults": 10,
    "includeDomains": ["github.com", "stackoverflow.com"]
  }' | jq .
```

## Category Search

```bash
curl -s -X POST https://api.exa.ai/search \
  -H "x-api-key: ${EXA_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Vercel",
    "category": "company",
    "numResults": 5
  }' | jq .
```

**Warning:** `category: "company"` and `category: "people"` disable date, text, and excludeDomains filters.

## Date-Filtered Search

```bash
curl -s -X POST https://api.exa.ai/search \
  -H "x-api-key: ${EXA_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Next.js 15 new features",
    "numResults": 10,
    "startPublishedDate": "2025-01-01T00:00:00.000Z"
  }' | jq .
```

## Deep Search

```bash
curl -s -X POST https://api.exa.ai/search \
  -H "x-api-key: ${EXA_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Compare tRPC vs GraphQL for Next.js",
    "type": "deep",
    "numResults": 10
  }' | jq .
```

Types: `auto` (default), `fast`, `instant`, `deep-lite`, `deep`, `deep-reasoning`.

Search extras: `outputSchema` (`{ "type": "object" }` or `{ "type": "text" }` output modes), `systemPrompt`, and `additionalQueries` (deep types only).

## Search with Summary

```bash
curl -s -X POST https://api.exa.ai/search \
  -H "x-api-key: ${EXA_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tailwind CSS v4 migration guide",
    "numResults": 5,
    "contents": {
      "summary": { "query": "What changed in Tailwind v4?" }
    }
  }' | jq .
```

## Answer

Direct answer with citations:

```bash
curl -s -X POST https://api.exa.ai/answer \
  -H "x-api-key: ${EXA_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What changed in React 19 server components?"
  }' | jq .
```

## Contents

Get text/highlights/summary for URLs (or result ids from a previous search):

```bash
curl -s -X POST https://api.exa.ai/contents \
  -H "x-api-key: ${EXA_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://nextjs.org/docs/app/building-your-application/data-fetching"],
    "text": true,
    "highlights": true,
    "summary": true
  }' | jq .
```

## Agent API

Start a multi-step research run:

```bash
curl -s -X POST https://api.exa.ai/agent/runs \
  -H "x-api-key: ${EXA_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Compare the top 3 vector databases for a Next.js RAG app",
    "effort": "medium"
  }' | jq .
```

Effort tiers: `minimal`, `low`, `medium`, `high`, `xhigh`, `auto`, `max`. Supports `outputSchema` for structured results.

Poll a run:

```bash
curl -s https://api.exa.ai/agent/runs/${RUN_ID} \
  -H "x-api-key: ${EXA_API_KEY}" | jq .
```

## Response Format

```json
{
  "results": [
    {
      "title": "Page Title",
      "url": "https://example.com/page",
      "publishedDate": "2025-03-01",
      "score": 0.95,
      "text": "Full page content...",
      "highlights": ["Key excerpt..."],
      "summary": "AI-generated summary..."
    }
  ],
  "costDollars": { "total": 0.008 }
}
```

## Common Mistakes

- `useAutoprompt` is DEPRECATED — do not use
- `text`, `highlights`, `summary` must be nested inside `contents`
- `livecrawl: "always"` is deprecated — use `contents.maxAgeHours: 0`
- `numSentences`, `highlightsPerUrl`, `tokensNum` do not exist
