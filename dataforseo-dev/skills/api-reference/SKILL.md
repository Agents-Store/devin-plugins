---
name: api-reference
description: This skill should be used when the user asks for "DataForSEO API endpoints", "DataForSEO REST API", "DataForSEO curl examples", "DataForSEO API documentation", "DataForSEO HTTP requests", or needs specific HTTP endpoint details for DataForSEO.
disable-model-invocation: true
---

# DataForSEO REST API Reference

Curated REST API endpoints for direct HTTP access. For full documentation, see [docs.dataforseo.com/v3](https://docs.dataforseo.com/v3/). For complete OpenAPI schema, see [github.com/dataforseo/OpenApiDocumentation](https://github.com/dataforseo/OpenApiDocumentation).

## Authentication

DataForSEO uses HTTP Basic Authentication (base64-encoded `username:password`):

```bash
curl -X POST "https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_ideas/live" \
  -H "Authorization: Basic $(echo -n "${DATAFORSEO_USERNAME}:${DATAFORSEO_PASSWORD}" | base64)" \
  -H "Content-Type: application/json" \
  -d '[{"keywords": ["seo tools"], "location_name": "United States", "language_code": "en", "limit": 10}]'
```

**Base URL:** `https://api.dataforseo.com`
**Method:** All data endpoints use `POST`
**Body:** JSON array of task objects `[{...}, {...}]`

## API Convention

All endpoints follow: `POST /v3/{api_module}/{search_engine}/{endpoint}/{mode}`

| Module | Path Prefix | Example |
|--------|------------|---------|
| SERP | `/v3/serp/google/organic/live/advanced` | Organic SERP results |
| Labs | `/v3/dataforseo_labs/google/keyword_ideas/live` | Keyword ideas |
| Backlinks | `/v3/backlinks/backlinks/live` | Backlink list |
| Keywords Data | `/v3/keywords_data/google_ads/search_volume/live` | Search volume |
| OnPage | `/v3/on_page/lighthouse/live/json` | Lighthouse audit |
| Content Analysis | `/v3/content_analysis/search/live` | Content citations |
| Domain Analytics | `/v3/domain_analytics/technologies/domain_technologies/live` | Tech stack |
| AI Optimization | `/v3/content_analysis/ai_optimization/llm_mentions/search` | LLM mentions |

## Response Format

```json
{
  "version": "0.1.20241203",
  "status_code": 20000,
  "status_message": "Ok.",
  "tasks": [{
    "id": "...",
    "status_code": 20000,
    "result": [{ ... }],
    "result_count": 10,
    "cost": 0.075
  }]
}
```

**Status codes:** 20000 = success, 40000+ = client error, 50000+ = server error.

## Top 5 Endpoints

### Keyword Overview
```bash
POST /v3/dataforseo_labs/google/keyword_ideas/live
Body: [{"keywords": ["project management"], "location_name": "United States", "language_code": "en", "limit": 20}]
```

### SERP Analysis
```bash
POST /v3/serp/google/organic/live/advanced
Body: [{"keyword": "best crm software", "location_name": "United States", "language_code": "en", "depth": 20}]
```

### Backlinks Summary
```bash
POST /v3/backlinks/summary/live
Body: [{"target": "example.com", "include_subdomains": true}]
```

### Lighthouse Audit
```bash
POST /v3/on_page/lighthouse/live/json
Body: [{"url": "https://example.com", "for_mobile": false}]
```

### Domain Technologies
```bash
POST /v3/domain_analytics/technologies/domain_technologies/live
Body: [{"target": "example.com"}]
```

## Detailed Endpoint References

- [SERP and Labs endpoints](references/api-serp-labs.md)
- [Backlinks and Keywords Data endpoints](references/api-backlinks-keywords.md)
- [OnPage, Content Analysis, Domain Analytics, AI Optimization endpoints](references/api-onpage-content-domain.md)
