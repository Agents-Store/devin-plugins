# Backlinks and Keywords Data API Endpoints

## Backlinks API

### Backlinks Summary
```bash
POST /v3/backlinks/summary/live
Body: [{
  "target": "example.com",
  "include_subdomains": true,
  "exclude_internal_backlinks": true
}]
```
Returns: total backlinks, referring_domains, referring_main_domains, rank, broken_backlinks, broken_pages.

### Get Backlinks
```bash
POST /v3/backlinks/backlinks/live
Body: [{
  "target": "example.com",
  "limit": 100,
  "mode": "one_per_domain",
  "order_by": ["rank,desc"],
  "filters": [["dofollow", "=", true]]
}]
```
Modes: `as_is` (all links), `one_per_domain`, `one_per_anchor`.

### Referring Domains
```bash
POST /v3/backlinks/referring_domains/live
Body: [{
  "target": "example.com",
  "limit": 50,
  "order_by": ["rank,desc"]
}]
```

### Anchors
```bash
POST /v3/backlinks/anchors/live
Body: [{
  "target": "example.com",
  "limit": 50,
  "order_by": ["backlinks,desc"]
}]
```

### Competitors (Backlink)
```bash
POST /v3/backlinks/competitors/live
Body: [{
  "target": "example.com",
  "limit": 20
}]
```
Finds domains with similar backlink profiles.

### Bulk Spam Score
```bash
POST /v3/backlinks/bulk_spam_score/live
Body: [{
  "targets": ["example.com", "competitor.com", "suspicious-site.com"]
}]
```
Returns spam_score (0-100) for up to 1000 targets.

### Bulk Ranks
```bash
POST /v3/backlinks/bulk_ranks/live
Body: [{
  "targets": ["example.com", "competitor1.com", "competitor2.com"]
}]
```
Returns rank (similar to Domain Authority) for up to 1000 targets.

### Timeseries Summary
```bash
POST /v3/backlinks/timeseries_summary/live
Body: [{
  "target": "example.com",
  "date_from": "2024-01-01",
  "date_to": "2024-12-31"
}]
```
Returns backlink count changes over time.

## Keywords Data API

### Google Ads Search Volume
```bash
POST /v3/keywords_data/google_ads/search_volume/live
Body: [{
  "keywords": ["seo tools", "keyword research"],
  "location_name": "United States",
  "language_code": "en"
}]
```
Returns: search_volume, competition, cpc, monthly_searches (12-month history).

### Google Trends Explore
```bash
POST /v3/keywords_data/google_trends/explore/live
Body: [{
  "keywords": ["chatgpt", "gemini", "claude"],
  "location_name": "United States",
  "time_range": "past_12_months",
  "type": "web"
}]
```
Returns relative popularity index (0-100) over time.

### DataForSEO Trends Explore
```bash
POST /v3/keywords_data/dataforseo_trends/explore/live
Body: [{
  "keywords": ["ai seo", "llm optimization"],
  "location_name": "United States",
  "time_range": "past_12_months",
  "type": "web"
}]
```
DataForSEO's own trend data with more granularity than Google Trends.

### DataForSEO Trends Demographics
```bash
POST /v3/keywords_data/dataforseo_trends/demography/live
Body: [{
  "keywords": ["project management software"],
  "location_name": "United States",
  "time_range": "past_12_months"
}]
```
Returns age and gender breakdown of keyword searchers.
