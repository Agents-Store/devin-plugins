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
POST /v3/ai_optimization/llm_mentions/search_mentions/live
Body: [{
  "target": [{"domain": "example.com", "search_scope": ["sources"]}],
  "platform": "chat_gpt",
  "location_code": 2840,
  "language_code": "en",
  "limit": 50
}]
```
Returns the questions and answers in which ChatGPT or Google AI mentions the target. ChatGPT data exists for United States and English only.

### LLM Mentions Target Metrics
```bash
POST /v3/ai_optimization/llm_mentions/target_metrics/live
Body: [{
  "target": [{"keyword": "best crm software", "match_type": "word_match"}],
  "platform": "chat_gpt",
  "location_code": 2840,
  "language_code": "en"
}]
```
Returns aggregated mention metrics for the target. To compare 2 to 10 targets, use `/v3/ai_optimization/llm_mentions/multi_target_metrics/live`; the other LLM Mentions endpoints are listed in the `mcp-patterns` skill's `endpoint-paths.md`.

### ChatGPT LLM Scraper
```bash
POST /v3/ai_optimization/chat_gpt/llm_scraper/live/advanced
Body: [{
  "keyword": "best project management tools",
  "location_code": 2840,
  "language_code": "en"
}]
```
Returns what ChatGPT shows for the query: the answer as typed items, cited sources, brand entities and the search results it looked at. The Gemini version is `/v3/ai_optimization/gemini/llm_scraper/live/advanced`.

### LLM Responses
```bash
POST /v3/ai_optimization/chat_gpt/llm_responses/live
Body: [{
  "user_prompt": "compare monday.com vs asana",
  "model_name": "<id from GET /v3/ai_optimization/chat_gpt/llm_responses/models>"
}]
```
Returns the model's answer to your prompt. The same body works for `/v3/ai_optimization/claude/llm_responses/live`, `/v3/ai_optimization/gemini/llm_responses/live` and `/v3/ai_optimization/perplexity/llm_responses/live`.
