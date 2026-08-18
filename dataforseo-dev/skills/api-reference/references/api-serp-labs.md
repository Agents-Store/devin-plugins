# SERP and DataForSEO Labs API Endpoints

## SERP API

### Google Organic SERP
```bash
POST /v3/serp/google/organic/live/advanced
Body: [{
  "keyword": "best project management software",
  "location_name": "United States",
  "language_code": "en",
  "depth": 30,
  "device": "desktop"
}]
```
Returns: Organic results with position, URL, title, snippet, SERP features.

### YouTube Search
```bash
POST /v3/serp/youtube/organic/live/advanced
Body: [{
  "keyword": "seo tutorial",
  "location_name": "United States",
  "language_code": "en"
}]
```

### SERP Locations Lookup
```bash
POST /v3/serp/google/locations
Body: [{"country": "US"}]
```
Returns available location codes for SERP queries.

## DataForSEO Labs API

### Keyword Ideas
```bash
POST /v3/dataforseo_labs/google/keyword_ideas/live
Body: [{
  "keywords": ["project management", "task tracking"],
  "location_name": "United States",
  "language_code": "en",
  "limit": 50,
  "filters": [["keyword_info.search_volume", ">", 100], "and", ["keyword_info.keyword_difficulty", "<", 40]]
}]
```
Returns: Related keywords with search_volume, cpc, competition, keyword_difficulty.

### Keyword Overview (Bulk Metrics)
```bash
POST /v3/dataforseo_labs/google/keyword_overview/live
Body: [{
  "keywords": ["seo tools", "keyword research", "backlink checker"],
  "location_name": "United States",
  "language_code": "en"
}]
```
Returns metrics for up to 700 keywords in a single call.

### Ranked Keywords
```bash
POST /v3/dataforseo_labs/google/ranked_keywords/live
Body: [{
  "target": "ahrefs.com",
  "location_name": "United States",
  "language_code": "en",
  "limit": 100,
  "order_by": ["ranked_serp_element.serp_item.rank_group,asc"]
}]
```

### Competitors Domain
```bash
POST /v3/dataforseo_labs/google/competitors_domain/live
Body: [{
  "target": "example.com",
  "location_name": "United States",
  "language_code": "en",
  "exclude_top_domains": true,
  "limit": 20
}]
```

### Domain Intersection
```bash
POST /v3/dataforseo_labs/google/domain_intersection/live
Body: [{
  "targets": {
    "1": "example.com",
    "2": "competitor.com"
  },
  "location_name": "United States",
  "language_code": "en",
  "limit": 50
}]
```
Returns keywords where both domains rank (or only one does).

### Search Intent
```bash
POST /v3/dataforseo_labs/google/search_intent/live
Body: [{
  "keywords": ["buy running shoes", "what is seo", "nike store near me"],
  "language_code": "en"
}]
```
Returns intent classification: informational, navigational, commercial, transactional.

### Bulk Keyword Difficulty
```bash
POST /v3/dataforseo_labs/bulk_keyword_difficulty/live
Body: [{
  "keywords": ["seo tools", "keyword research tool", "backlink checker"],
  "location_name": "United States",
  "language_code": "en"
}]
```

### Historical Rank Overview
```bash
POST /v3/dataforseo_labs/google/historical_rank_overview/live
Body: [{
  "target": "example.com",
  "location_name": "United States",
  "language_code": "en"
}]
```
Returns monthly ranking snapshots over time.
