# OnPage, Content Analysis, Domain Analytics, and AI Optimization API Endpoints

## OnPage API

### Lighthouse Audit
```bash
POST /v3/on_page/lighthouse/live/json
Body: [{
  "url": "https://example.com",
  "for_mobile": false,
  "categories": ["performance", "accessibility", "best-practices", "seo"]
}]
```
Returns Google Lighthouse scores and detailed audit results.

### Instant Pages (On-Page Analysis)
```bash
POST /v3/on_page/instant_pages
Body: [{
  "url": "https://example.com/page",
  "enable_javascript": true
}]
```
Returns page-level SEO data: meta tags, headings, images, links, word count, page speed metrics.

### Content Parsing
```bash
POST /v3/on_page/content_parsing/live
Body: [{
  "url": "https://example.com/blog/article",
  "enable_javascript": true
}]
```
Returns structured content: headings, paragraphs, links, images with alt text.

## Content Analysis API

### Search (Keyword Citations)
```bash
POST /v3/content_analysis/search/live
Body: [{
  "keyword": "project management",
  "limit": 20,
  "search_mode": "one_per_domain",
  "page_type": ["blogs", "news"],
  "order_by": ["content_info.sentiment_connotations.joy,desc"]
}]
```
Returns pages citing the keyword with sentiment analysis and domain metrics.

### Summary (Keyword Overview)
```bash
POST /v3/content_analysis/summary/live
Body: [{
  "keyword": "artificial intelligence",
  "page_type": ["news", "blogs"]
}]
```
Returns citation count, sentiment distribution, top categories, connotation types.

### Phrase Trends
```bash
POST /v3/content_analysis/phrase_trends/live
Body: [{
  "keyword": "generative ai",
  "date_from": "2024-01-01",
  "date_to": "2024-12-31",
  "date_group": "month"
}]
```
Returns citation count trends over time, grouped by day/week/month.

## Domain Analytics API

### Technology Detection
```bash
POST /v3/domain_analytics/technologies/domain_technologies/live
Body: [{
  "target": "example.com"
}]
```
Returns detected technologies: CMS, frameworks, analytics tools, CDN, hosting, ecommerce platforms.

### WHOIS Overview
```bash
POST /v3/domain_analytics/whois/overview/live
Body: [{
  "limit": 10,
  "filters": [["domain", "like", "%example%"]]
}]
```
Returns domain registration data enriched with backlink stats and traffic metrics.

## AI Optimization API

### LLM Mentions Search
```bash
POST /v3/content_analysis/ai_optimization/llm_mentions/search
Body: [{
  "target": [{"domain": "example.com", "search_scope": ["answer"]}],
  "platform": "chat_gpt",
  "location_name": "United States",
  "language_code": "en",
  "limit": 50
}]
```
Returns queries where ChatGPT or Google AI mentions the target domain.

### LLM Mentions Aggregated Metrics
```bash
POST /v3/content_analysis/ai_optimization/llm_mentions/agg_metrics
Body: [{
  "target": [{"keyword": "best crm software", "match_type": "word_match"}],
  "platform": "chat_gpt",
  "location_name": "United States",
  "language_code": "en"
}]
```
Returns aggregated visibility scores across all matching queries.

### ChatGPT Scraper
```bash
POST /v3/content_analysis/ai_optimization/chat_gpt_scraper/live
Body: [{
  "keyword": "best project management tools 2024",
  "location_name": "United States",
  "language_code": "en"
}]
```
Returns ChatGPT's actual response for the query, including cited URLs and recommendations.

### LLM Response
```bash
POST /v3/content_analysis/ai_optimization/llm_response/live
Body: [{
  "keyword": "compare monday.com vs asana",
  "model": "gpt-4",
  "location_name": "United States",
  "language_code": "en"
}]
```
Returns the actual LLM response for the specified model and query.
