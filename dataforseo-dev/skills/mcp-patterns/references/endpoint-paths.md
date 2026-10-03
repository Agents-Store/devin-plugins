# Endpoint paths — task, REST path, minimal body

One table per API group. Every row is one call:

```
api_request({method: "POST", path: "<path>", data: [<body>]})
```

Rows marked GET use `method: "GET"` and no `data`. The server appends `.ai` to the path for you; pass `noAiMode: true` only when you need the full response (see the `mcp-patterns` skill).

- **Bodies show required fields only**, plus the location and language pair most endpoints need. `location_code: 2840` is United States, `language_code: "en"` is English; `location_name: "United States"` works in place of the code.
- **Before the first paid call to any path, read its page**: `docs_search({url: "<path without /v3/>"})`. It lists the optional fields, the limits and the Pricing link. Paths here were checked against the DataForSEO v3 documentation index on 2026-10-02.
- **Live endpoints take one task per request**: `data` is an array holding one object.
- **A row that names a limit** (700 keywords, 1000 targets) states what the docs allow today; the docs page wins if it says otherwise.
- **Filters** are `[["field", "operator", value], "and", ["field2", "operator", value2]]`; sorting is `["field,desc"]`. Field names per API: `docs_search({url: "backlinks/filters"})`, `docs_search({url: "dataforseo_labs/filters"})`, `docs_search({url: "ai_optimization/llm_mentions/filters"})`.

## SERP

| Task | Path | Minimal body |
|---|---|---|
| Google organic results | `/v3/serp/google/organic/live/advanced` | `{"keyword": "best crm software", "location_code": 2840, "language_code": "en", "depth": 10}` — `depth` max 200, billed per 10 results |
| Google AI Mode answer | `/v3/serp/google/ai_mode/live/advanced` | `{"keyword": "best crm software", "location_code": 2840, "language_code": "en"}` |
| Google Maps, News, Images, Autocomplete | `/v3/serp/google/maps/live/advanced`, `/v3/serp/google/news/live/advanced`, `/v3/serp/google/images/live/advanced`, `/v3/serp/google/autocomplete/live/advanced` | same body as organic; confirm per endpoint with `docs_search` |
| Bing organic results | `/v3/serp/bing/organic/live/advanced` | `{"keyword": "best crm software", "location_code": 2840, "language_code": "en"}` |
| YouTube search | `/v3/serp/youtube/organic/live/advanced` | `{"keyword": "seo tutorial", "location_code": 2840, "language_code": "en"}` |
| YouTube video metadata | `/v3/serp/youtube/video_info/live/advanced` | `{"video_id": "<id>", "location_code": 2840, "language_code": "en"}` |
| YouTube video comments | `/v3/serp/youtube/video_comments/live/advanced` | `{"video_id": "<id>", "location_code": 2840, "language_code": "en", "depth": 20}` |
| YouTube video subtitles | `/v3/serp/youtube/video_subtitles/live/advanced` | `{"video_id": "<id>", "location_code": 2840, "language_code": "en"}` |
| Google locations (GET; countries only in `.ai` mode, add a country code for its cities) | `/v3/serp/google/locations` | none; cities of one country: `/v3/serp/google/locations/US` |
| Google languages (GET) | `/v3/serp/google/languages` | none |
| YouTube locations (GET) | `/v3/serp/youtube/locations` | none |

## DataForSEO Labs (Google)

| Task | Path | Minimal body |
|---|---|---|
| Volume, CPC, difficulty for up to 700 keywords | `/v3/dataforseo_labs/google/keyword_overview/live` | `{"keywords": ["seo tools", "keyword research"], "location_code": 2840, "language_code": "en"}` |
| Keyword ideas from up to 200 seeds | `/v3/dataforseo_labs/google/keyword_ideas/live` | `{"keywords": ["project management"], "location_code": 2840, "language_code": "en", "limit": 100}` |
| Long-tail suggestions for one seed | `/v3/dataforseo_labs/google/keyword_suggestions/live` | `{"keyword": "project management", "location_code": 2840, "language_code": "en", "limit": 100}` |
| Semantically related keywords | `/v3/dataforseo_labs/google/related_keywords/live` | `{"keyword": "project management", "location_code": 2840, "language_code": "en", "limit": 100}` |
| Keywords a domain is relevant for | `/v3/dataforseo_labs/google/keywords_for_site/live` | `{"target": "example.com", "location_code": 2840, "language_code": "en", "limit": 100}` |
| Keywords a domain or page ranks for | `/v3/dataforseo_labs/google/ranked_keywords/live` | `{"target": "example.com", "location_code": 2840, "language_code": "en", "limit": 100}` |
| Organic competitors of a domain | `/v3/dataforseo_labs/google/competitors_domain/live` | `{"target": "example.com", "location_code": 2840, "language_code": "en", "exclude_top_domains": true, "limit": 20}` |
| Domains competing for a keyword set (up to 200 keywords) | `/v3/dataforseo_labs/google/serp_competitors/live` | `{"keywords": ["crm", "sales software"], "location_code": 2840, "language_code": "en"}` |
| Keyword gap: `target1` ranks, `target2` does not | `/v3/dataforseo_labs/google/domain_intersection/live` | `{"target1": "competitor.com", "target2": "example.com", "location_code": 2840, "language_code": "en", "intersections": false, "limit": 100}` — `true` returns the shared keywords instead |
| Queries where given pages rank | `/v3/dataforseo_labs/google/page_intersection/live` | `{"pages": {"1": "https://a.example/guide", "2": "https://b.example/guide"}, "location_code": 2840, "language_code": "en"}` |
| Domain traffic and ranking snapshot | `/v3/dataforseo_labs/google/domain_rank_overview/live` | `{"target": "example.com", "location_code": 2840, "language_code": "en"}` |
| Domain history, month by month | `/v3/dataforseo_labs/google/historical_rank_overview/live` | `{"target": "example.com", "location_code": 2840, "language_code": "en"}` |
| Keyword volume history (up to 700 keywords) | `/v3/dataforseo_labs/google/historical_keyword_data/live` | `{"keywords": ["seo tools"], "location_code": 2840, "language_code": "en"}` |
| SERP snapshots over time for a keyword | `/v3/dataforseo_labs/google/historical_serps/live` | `{"keyword": "seo tools", "location_code": 2840, "language_code": "en"}` |
| A domain's best pages by traffic | `/v3/dataforseo_labs/google/relevant_pages/live` | `{"target": "example.com", "location_code": 2840, "language_code": "en", "limit": 50}` |
| A domain's subdomains by traffic | `/v3/dataforseo_labs/google/subdomains/live` | `{"target": "example.com", "location_code": 2840, "language_code": "en"}` |
| Trending searches | `/v3/dataforseo_labs/google/top_searches/live` | `{"location_code": 2840, "language_code": "en", "limit": 50}` |
| Search intent of up to 1000 keywords | `/v3/dataforseo_labs/google/search_intent/live` | `{"keywords": ["buy running shoes", "what is seo"]}` — no location or language fields |
| Keyword difficulty for up to 1000 keywords | `/v3/dataforseo_labs/google/bulk_keyword_difficulty/live` | `{"keywords": ["seo tools", "backlink checker"], "location_code": 2840, "language_code": "en"}` |
| Traffic estimate for up to 1000 targets | `/v3/dataforseo_labs/google/bulk_traffic_estimation/live` | `{"targets": ["example.com", "competitor.com"], "location_code": 2840, "language_code": "en"}` |
| Labs locations and languages (GET) | `/v3/dataforseo_labs/locations_and_languages` | none |

## Backlinks

All paths end in `/live` and take a `target`: a domain or subdomain without `https://` and `www.`, or a page as an absolute URL.

| Task | Path | Minimal body |
|---|---|---|
| Profile summary | `/v3/backlinks/summary/live` | `{"target": "example.com"}` |
| Individual backlinks | `/v3/backlinks/backlinks/live` | `{"target": "example.com", "mode": "one_per_domain", "limit": 100, "order_by": ["rank,desc"]}` — modes `as_is`, `one_per_domain`, `one_per_anchor` |
| Anchor text distribution | `/v3/backlinks/anchors/live` | `{"target": "example.com", "limit": 100, "order_by": ["backlinks,desc"]}` |
| Referring domains | `/v3/backlinks/referring_domains/live` | `{"target": "example.com", "limit": 100, "order_by": ["rank,desc"]}` |
| Referring IP networks | `/v3/backlinks/referring_networks/live` | `{"target": "example.com", "limit": 100}` |
| Pages of a domain with link data | `/v3/backlinks/domain_pages/live` | `{"target": "example.com", "limit": 100}` |
| Page-level link summary | `/v3/backlinks/domain_pages_summary/live` | `{"target": "example.com", "limit": 100}` |
| Domains with a similar link profile | `/v3/backlinks/competitors/live` | `{"target": "example.com", "limit": 20}` |
| Link gap: domains linking to the targets but not to the excluded ones | `/v3/backlinks/domain_intersection/live` | `{"targets": {"1": "competitor1.com", "2": "competitor2.com"}, "exclude_targets": ["example.com"], "limit": 100}` |
| Link gap for specific pages | `/v3/backlinks/page_intersection/live` | `{"targets": {"1": "https://a.example/guide", "2": "https://b.example/guide"}, "limit": 100}` |
| Backlink counts, up to 1000 targets | `/v3/backlinks/bulk_backlinks/live` | `{"targets": ["example.com", "competitor.com"]}` |
| Rank, up to 1000 targets | `/v3/backlinks/bulk_ranks/live` | `{"targets": ["example.com", "competitor.com"]}` |
| Referring domain counts, up to 1000 targets | `/v3/backlinks/bulk_referring_domains/live` | `{"targets": ["example.com", "competitor.com"]}` |
| New and lost backlinks, up to 1000 targets | `/v3/backlinks/bulk_new_lost_backlinks/live` | `{"targets": ["example.com"], "date_from": "2026-01-01"}` |
| New and lost referring domains | `/v3/backlinks/bulk_new_lost_referring_domains/live` | `{"targets": ["example.com"], "date_from": "2026-01-01"}` |
| Page-level metrics, up to 1000 targets | `/v3/backlinks/bulk_pages_summary/live` | `{"targets": ["https://example.com/page"]}` |
| Spam score, up to 1000 targets | `/v3/backlinks/bulk_spam_score/live` | `{"targets": ["example.com", "suspicious-site.com"]}` |
| Backlink totals over time | `/v3/backlinks/timeseries_summary/live` | `{"target": "example.com", "date_from": "2025-01-01"}` |
| New vs lost links over time | `/v3/backlinks/timeseries_new_lost_summary/live` | `{"target": "example.com", "date_from": "2025-01-01"}` |
| Rank history | `/v3/backlinks/history/live` | `{"target": "example.com", "date_from": "2025-01-01"}` |

## Keywords Data

| Task | Path | Minimal body |
|---|---|---|
| Google Ads search volume, up to 1000 keywords | `/v3/keywords_data/google_ads/search_volume/live` | `{"keywords": ["seo tools"], "location_code": 2840, "language_code": "en"}` |
| Google Ads keyword ideas | `/v3/keywords_data/google_ads/keywords_for_keywords/live` | `{"keywords": ["seo tools"], "location_code": 2840, "language_code": "en"}` |
| Google Ads keywords for a site | `/v3/keywords_data/google_ads/keywords_for_site/live` | `{"target": "example.com", "location_code": 2840, "language_code": "en"}` |
| Google Trends, up to 5 keywords | `/v3/keywords_data/google_trends/explore/live` | `{"keywords": ["chatgpt", "gemini"], "location_code": 2840, "time_range": "past_12_months"}` |
| DataForSEO Trends | `/v3/keywords_data/dataforseo_trends/explore/live` | `{"keywords": ["ai seo"], "location_code": 2840, "time_range": "past_12_months", "type": "web"}` |
| Searcher age and gender | `/v3/keywords_data/dataforseo_trends/demography/live` | `{"keywords": ["project management software"], "location_code": 2840, "time_range": "past_12_months"}` |
| Interest by subregion | `/v3/keywords_data/dataforseo_trends/subregion_interests/live` | `{"keywords": ["project management software"], "location_code": 2840, "time_range": "past_12_months"}` |
| Google Ads locations (GET) | `/v3/keywords_data/google_ads/locations` | none |

## OnPage

| Task | Path | Minimal body |
|---|---|---|
| Lighthouse audit | `/v3/on_page/lighthouse/live/json` | `{"url": "https://example.com", "for_mobile": true, "categories": ["performance", "seo"]}` — the server trims this payload by default |
| Page-level SEO data | `/v3/on_page/instant_pages` | `{"url": "https://example.com/page", "enable_javascript": true}` |
| Structured page content | `/v3/on_page/content_parsing/live` | `{"url": "https://example.com/blog/post", "enable_javascript": true}` |
| Crawl a whole site (task-based) | `/v3/on_page/task_post` | `{"target": "example.com", "max_crawl_pages": 10}`; read the crawl with `GET /v3/on_page/summary/<id>` and `POST /v3/on_page/pages` with `{"id": "<id>", "limit": 50}` |

## Content Analysis

| Task | Path | Minimal body |
|---|---|---|
| Pages citing a keyword | `/v3/content_analysis/search/live` | `{"keyword": "project management", "limit": 20, "search_mode": "one_per_domain", "page_type": ["blogs", "news"]}` |
| Citation totals and sentiment | `/v3/content_analysis/summary/live` | `{"keyword": "artificial intelligence", "page_type": ["news", "blogs"]}` |
| Mentions over time (`date_from` required) | `/v3/content_analysis/phrase_trends/live` | `{"keyword": "generative ai", "date_from": "2025-01-01", "date_group": "month"}` |
| Sentiment breakdown | `/v3/content_analysis/sentiment_analysis/live` | `{"keyword": "generative ai"}` |
| Rating distribution | `/v3/content_analysis/rating_distribution/live` | `{"keyword": "generative ai"}` |

## Domain Analytics

| Task | Path | Minimal body |
|---|---|---|
| Technologies on a domain | `/v3/domain_analytics/technologies/domain_technologies/live` | `{"target": "example.com"}` |
| Domains using a technology | `/v3/domain_analytics/technologies/domains_by_technology/live` | `{"technologies": ["WordPress"], "limit": 10}` |
| WHOIS records with filters | `/v3/domain_analytics/whois/overview/live` | `{"limit": 10, "filters": [["domain", "like", "%example%"]]}` |

## AI Optimization

`target` is an array of entities. A domain entity is `{"domain": "example.com"}` (optional `search_filter`: `include` or `exclude`, `search_scope`: `["any"]`, `["sources"]` or `["search_results"]`). A keyword entity is `{"keyword": "best crm", "match_type": "word_match"}` (`match_type` also `partial_match`; `search_scope` values `any`, `question`, `answer`, `brand_entities`, `fan_out_queries`). A request needs at least one included entity, up to 10 in all. `platform` is `chat_gpt` or `google`; ChatGPT data exists for United States and English only.

| Task | Path | Minimal body |
|---|---|---|
| Queries and answers that mention a target | `/v3/ai_optimization/llm_mentions/search_mentions/live` | `{"target": [{"domain": "example.com", "search_scope": ["sources"]}], "platform": "chat_gpt", "location_code": 2840, "language_code": "en", "limit": 50}` |
| Aggregated visibility of one target | `/v3/ai_optimization/llm_mentions/target_metrics/live` | `{"target": [{"domain": "example.com"}], "platform": "chat_gpt", "location_code": 2840, "language_code": "en"}` |
| Compare 2 to 10 targets side by side | `/v3/ai_optimization/llm_mentions/multi_target_metrics/live` | `{"targets": [{"key": "us", "target": [{"domain": "example.com"}]}, {"key": "rival", "target": [{"domain": "rival.com"}]}], "platform": "chat_gpt", "location_code": 2840, "language_code": "en"}` |
| Domains most cited for a topic | `/v3/ai_optimization/llm_mentions/top_mentioned_domains/live` | `{"target": [{"keyword": "best crm"}], "platform": "chat_gpt", "location_code": 2840, "language_code": "en", "limit": 20}` |
| Pages most cited for a topic | `/v3/ai_optimization/llm_mentions/top_mentioned_pages/live` | same body as top domains |
| Brands most mentioned for a topic | `/v3/ai_optimization/llm_mentions/top_mentioned_brands/live` | same body as top domains |
| Brand categories most mentioned | `/v3/ai_optimization/llm_mentions/top_mentioned_brand_categories/live` | same body as top domains |
| Cheaper `_lite` variants | `/v3/ai_optimization/llm_mentions/target_metrics_lite/live`, `/v3/ai_optimization/llm_mentions/top_mentioned_domains_lite/live`, `/v3/ai_optimization/llm_mentions/top_mentioned_pages_lite/live`, `/v3/ai_optimization/llm_mentions/top_mentioned_brands_lite/live`, `/v3/ai_optimization/llm_mentions/top_mentioned_brand_categories_lite/live` | same bodies as the full endpoints; read the docs page for what the lite version drops |
| Mentions over months | `/v3/ai_optimization/llm_mentions/historical/live` | `{"target": [{"domain": "example.com"}], "platform": "chat_gpt", "location_code": 2840, "language_code": "en"}` |
| Change between periods | `/v3/ai_optimization/llm_mentions/timeseries_delta/live` | `{"target": [{"domain": "example.com"}], "date_from": "2026-01-01", "date_to": "2026-06-30", "group_range": "month"}` |
| New and lost mentions over time | `/v3/ai_optimization/llm_mentions/timeseries_new_lost/live` | `{"target": [{"domain": "example.com"}], "date_from": "2026-01-01", "date_to": "2026-06-30", "group_range": "month"}` |
| What ChatGPT shows for a query (answer, sources, brands) | `/v3/ai_optimization/chat_gpt/llm_scraper/live/advanced` | `{"keyword": "best crm for startups", "location_code": 2840, "language_code": "en"}` |
| What Gemini shows for a query | `/v3/ai_optimization/gemini/llm_scraper/live/advanced` | `{"keyword": "best crm for startups", "location_code": 2840, "language_code": "en"}` |
| Ask ChatGPT through the API | `/v3/ai_optimization/chat_gpt/llm_responses/live` | `{"user_prompt": "compare monday.com and asana", "model_name": "<id from the models endpoint>"}` |
| Ask Claude | `/v3/ai_optimization/claude/llm_responses/live` | same body as ChatGPT |
| Ask Gemini | `/v3/ai_optimization/gemini/llm_responses/live` | same body as ChatGPT |
| Ask Perplexity | `/v3/ai_optimization/perplexity/llm_responses/live` | same body as ChatGPT |
| Search volume inside AI answers, up to 1000 keywords | `/v3/ai_optimization/ai_keyword_data/keywords_search_volume/live` | `{"keywords": ["best crm for startups"], "location_code": 2840, "language_code": "en"}` |
| Model ids (GET) | `/v3/ai_optimization/chat_gpt/llm_responses/models`, `/v3/ai_optimization/claude/llm_responses/models`, `/v3/ai_optimization/gemini/llm_responses/models`, `/v3/ai_optimization/perplexity/llm_responses/models` | none |
| Supported locations and languages (GET) | `/v3/ai_optimization/llm_mentions/locations_and_languages`, `/v3/ai_optimization/ai_keyword_data/locations_and_languages`, `/v3/ai_optimization/chat_gpt/llm_scraper/locations` | none |

## Merchant, App Data, Business Data

These three sections are new to the plugin. Each has a Live mode for some endpoints and a task-based mode (`task_post`, then `tasks_ready` and `task_get`) for the rest; list a section with `docs_index({section: "Merchant API"})` before picking.

| Task | Path | Minimal body |
|---|---|---|
| Amazon product search | `/v3/merchant/amazon/products/live/advanced` | `{"keyword": "usb c hub", "location_code": 2840, "language_code": "en_US"}` |
| Amazon product page by ASIN | `/v3/merchant/amazon/asin/live/advanced` | `{"asin": "<asin>", "location_code": 2840, "language_code": "en_US"}` |
| Amazon sellers of an ASIN | `/v3/merchant/amazon/sellers/live/advanced` | `{"asin": "<asin>", "location_code": 2840, "language_code": "en_US"}` |
| Google Play app search in the DataForSEO database | `/v3/app_data/google/app_listings/search/live` | `{"title": "vpn", "limit": 10}` |
| App Store app search in the DataForSEO database | `/v3/app_data/apple/app_listings/search/live` | `{"title": "vpn", "limit": 10}` |
| Local business search in the DataForSEO database | `/v3/business_data/business_listings/search/live` | `{"categories": ["pizza_restaurant"], "title": "pizza", "limit": 10}` |
| Google Business profile of one business | `/v3/business_data/google/my_business_info/live` | `{"keyword": "<business name>", "location_name": "New York,New York,United States", "language_code": "en"}` |
| Questions and answers on a Google listing | `/v3/business_data/google/questions_and_answers/live` | `{"keyword": "<business name>", "location_name": "New York,New York,United States", "language_code": "en"}` |

## Not here

- Google Merchant, App Data app info and reviews, Business Data reviews and extended reviews, Tripadvisor and Trustpilot are task-based only. Read their pages with `docs_index` and `docs_search` and treat each as a multi-call workflow that costs more than one request.
- The **Databases** section describes separate bulk data products, not request/response endpoints; read its overview with `docs_search({url: "databases/overview"})` before assuming anything.
- The **Appendix** holds the status codes (`docs_search({url: "appendix/errors"})`), the free sandbox, and the free account endpoint `GET /v3/appendix/user_data` that the `cost-awareness` skill uses to read the balance.
