---
name: site-audit
description: This skill should be used when the user asks about "site audit", "on-page audit", "lighthouse audit", "page speed", "technical SEO audit", "crawl site", "page analysis", "content analysis", "technology detection", or needs to analyze website pages and content using DataForSEO.
---

# Site Audit

Perform technical SEO audits, content analysis, technology detection and domain intelligence with the DataForSEO OnPage, Content Analysis and Domain Analytics APIs. Every block below is one `api_request` call: the first line is the `method` and `path`, the second is `data`. Before the first call to a path, read its page with `docs_search` and agree a budget (`cost-awareness` skill). Paths and minimal bodies for the whole API are in `../mcp-patterns/references/endpoint-paths.md`.

## Endpoints used

| Path | What it gives |
|------|---------------|
| `/v3/on_page/lighthouse/live/json` | Google Lighthouse audit of a URL |
| `/v3/on_page/instant_pages` | Page-level optimization data (meta, headings, links, images) |
| `/v3/on_page/content_parsing/live` | Structured content extracted from a page |
| `/v3/content_analysis/search/live` | Web content citing a keyword, with sentiment and metrics |
| `/v3/content_analysis/summary/live` | Aggregated content metrics for a keyword |
| `/v3/content_analysis/phrase_trends/live` | Phrase popularity over time |
| `/v3/domain_analytics/technologies/domain_technologies/live` | Technologies used on a domain |
| `/v3/domain_analytics/whois/overview/live` | WHOIS registration data with filters |

## Workflow 1: Single Page Audit

Run a technical audit of one URL. Start with Lighthouse for performance scores, then get page optimization details, and optionally extract the content structure.

### Step 1 — Lighthouse Audit
```
POST /v3/on_page/lighthouse/live/json
data: [{"url": "https://example.com/landing-page", "for_mobile": true}]
```

Set `for_mobile: true` for mobile-first analysis (Google's default ranking signal). The response has scores for performance, accessibility, best_practices and seo (each 0 to 1; multiply by 100 for a percentage). Drill into the `audits` object for actionable recommendations. The server trims the Lighthouse payload by default. The full payload needs a field-config entry with an empty field list for `/v3/on_page/lighthouse/live/json` (the server's `--configuration` option), which changes the server's startup arguments, so ask the user before widening it.

### Step 2 — Page Optimization Data
```
POST /v3/on_page/instant_pages
data: [{"url": "https://example.com/landing-page"}]
```

Returns page-level SEO signals: title tag, meta description, canonical URL, heading structure, internal and external link counts, image alt text coverage, page size, load time and HTTP status. Use it to find missing meta tags, a broken heading hierarchy or oversized pages.

### Step 3 — Content Extraction
```
POST /v3/on_page/content_parsing/live
data: [{"url": "https://example.com/landing-page"}]
```

Extracts structured content: paragraphs, headings, lists and tables. Use it to judge content quality and keyword density, or to feed text into further analysis.

## Workflow 2: Content Landscape Analysis

Understand how a topic is covered across the web: what content exists, the overall sentiment, and the trend.

### Step 1 — Search Content
```
POST /v3/content_analysis/search/live
data: [{"keyword": "headless CMS comparison", "search_mode": "as_is", "limit": 50}]
```

Returns pages matching the keyword with page type (ecommerce, news, blog, message-board, organization), sentiment, word count, publication date and social metrics. `search_mode` is `as_is` (all citations) or `one_per_domain` (one citation per domain).

### Step 2 — Summary Metrics
```
POST /v3/content_analysis/summary/live
data: [{"keyword": "headless CMS comparison"}]
```

Returns aggregated metrics: total citations, sentiment distribution, content type distribution and top domains. A quick market snapshot before diving into pages.

### Step 3 — Phrase Trends
```
POST /v3/content_analysis/phrase_trends/live
data: [{"keyword": "headless CMS comparison", "date_from": "2025-01-01", "date_group": "month"}]
```

**`date_from` is required.** Returns how often the phrase appears over time. Set `date_from` 6 to 12 months back for meaningful trends.

## Workflow 3: Technology Detection

Discover the technology stack of any domain: CMS, frameworks, analytics, CDN, hosting, email services and more.

```
POST /v3/domain_analytics/technologies/domain_technologies/live
data: [{"target": "example.com"}]
```

Returns a categorized list: content management systems (WordPress, Shopify), JavaScript frameworks, analytics, CDN, hosting provider, advertising platforms, email services. Each entry has a category, a name and a version when detectable.

Use cases:
- Competitive intelligence: see what tools competitors use
- Sales prospecting: find companies using a specific technology (`/v3/domain_analytics/technologies/domains_by_technology/live`)
- Migration planning: understand the current stack before proposing changes

## Workflow 4: Domain Intelligence

WHOIS overview searches registration records by filter.

```
POST /v3/domain_analytics/whois/overview/live
data: [{"limit": 10, "filters": [["domain", "like", "%example%"]]}]
```

Returns registrar, creation, expiration and update dates, name servers, registrant organization (when not privacy-protected) and domain status codes, enriched with backlink stats and traffic metrics when available.

Use cases:
- Due diligence: verify domain age and ownership
- Competitor research: find related domains by registrant
- Expired domain hunting: check expiration dates

## Whole-site crawl (task-based)

The three OnPage calls above audit single pages. A crawl of a whole site is task-based: `POST /v3/on_page/task_post` with `{"target": "example.com", "max_crawl_pages": 10}`, then `GET /v3/on_page/summary/<id>` and `POST /v3/on_page/pages` with `{"id": "<id>"}`. It costs more than a single-page audit, so plan it as its own budget line and read `docs_search({url: "on_page/task_post"})` first.

## Interpreting Lighthouse Scores

| Score Range | Rating | Action |
|-------------|--------|--------|
| 90-100 | Good (green) | Maintain current optimizations |
| 50-89 | Needs Improvement (orange) | Address specific audit failures |
| 0-49 | Poor (red) | Prioritize immediate fixes |

Key Lighthouse audit categories:
- **Performance**: LCP, CLS, TTFB, speed index. Most impactful for rankings.
- **Accessibility**: color contrast, ARIA labels, heading order, alt text. Affects both SEO and compliance.
- **Best Practices**: HTTPS, console errors, deprecated APIs, image aspect ratios.
- **SEO**: crawlability, meta tags, structured data, mobile viewport, link text.

Always check the `audits` object for specific failing items. Each audit has a `score` (0 to 1), a `title` and a `description` explaining what to fix.

## Content Analysis Metrics

When interpreting content analysis search results:

| Metric | Values | Meaning |
|--------|--------|---------|
| `sentiment_connotations` | positive / negative / neutral | Overall tone of the content |
| `connotation_types` | anger, happiness, sadness, fear, love, fun | Emotional tone breakdown |
| `page_types` | ecommerce, news, blogs, message-boards, organization | Content category |
| `social_metrics` | facebook, twitter shares | Content virality indicators |
| `word_count` | integer | Content depth; higher often means more comprehensive |
| `spam_score` | 0-100 | Quality indicator; lower is better |

## Integration with Other Skills

- **Lighthouse finds slow performance**: use the keyword-research skill to check whether ranking is affected, then optimize
- **Content analysis reveals competitor coverage gaps**: use the competitor-analysis skill to find their keyword strategy
- **Technology detection reveals an outdated CMS**: document it in the audit findings for a migration recommendation
- **WHOIS shows expiring competitor domains**: monitor with periodic checks

<example>
User: "Run a full technical audit on our homepage at https://acme.co"

1. docs_search for the four paths below; show the plan (4 calls); get the user's budget
2. api_request POST /v3/on_page/lighthouse/live/json with url "https://acme.co", for_mobile true
3. POST /v3/on_page/instant_pages with url "https://acme.co"
4. POST /v3/on_page/content_parsing/live with url "https://acme.co"
5. POST /v3/domain_analytics/technologies/domain_technologies/live with target "acme.co"
6. Compile the findings: Lighthouse scores, missing meta tags, heading hierarchy issues, technology stack
7. Present prioritized recommendations: critical (performance), important (SEO), nice-to-have (best practices)
</example>

<example>
User: "How is the topic 'AI code review' being covered online? Show me trends."

1. docs_search for the three content analysis paths; show the plan (3 calls); get the user's budget
2. api_request POST /v3/content_analysis/search/live with keyword "AI code review", limit 50
3. POST /v3/content_analysis/summary/live with keyword "AI code review"
4. POST /v3/content_analysis/phrase_trends/live with keyword "AI code review", date_from "2026-01-01", date_group "month"
5. Analyze: total coverage, dominant page types (blogs against news), sentiment distribution
6. Report the trend direction (growing, stable, declining) with the monthly counts
7. Name the top 5 domains on this topic and their angles
</example>
