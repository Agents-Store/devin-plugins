---
name: site-audit
description: This skill should be used when the user asks about "site audit", "on-page audit", "lighthouse audit", "page speed", "technical SEO audit", "crawl site", "page analysis", "content analysis", "technology detection", or needs to analyze website pages and content using DataForSEO.
---

# Site Audit

Perform technical SEO audits, content analysis, technology detection, and domain intelligence using DataForSEO on-page, content analysis, and domain analytics tools.

## Available Tools

| Tool | Description |
|------|-------------|
| `on_page_lighthouse` | Run Google Lighthouse audit on a URL |
| `on_page_instant_pages` | Get page-level optimization data (meta, headings, links, images) |
| `on_page_content_parsing` | Extract structured content from a page |
| `content_analysis_search` | Search web content by keyword with sentiment and metrics |
| `content_analysis_summary` | Get aggregated content metrics for a keyword |
| `content_analysis_phrase_trends` | Track phrase popularity trends over time |
| `domain_analytics_technologies_domain_technologies` | Detect technologies used on a domain |
| `domain_analytics_whois_overview` | Get WHOIS registration data for a domain |

## Workflow 1: Single Page Audit

Run a comprehensive technical audit of one URL. Start with Lighthouse for performance scores, then get page optimization details, and optionally extract content structure.

### Step 1 — Lighthouse Audit
```
Tool: on_page_lighthouse
Input: {
  "url": "https://example.com/landing-page",
  "for_mobile": true
}
```

Set `for_mobile: true` for mobile-first analysis (Google's default ranking signal). The response includes scores for performance, accessibility, best_practices, and seo (each 0-1, multiply by 100 for percentage). Drill into specific audits in the `audits` object for actionable recommendations.

### Step 2 — Page Optimization Data
```
Tool: on_page_instant_pages
Input: {
  "url": "https://example.com/landing-page"
}
```

Returns page-level SEO signals: title tag, meta description, canonical URL, heading structure (h1-h6 counts), internal/external link counts, image alt text coverage, page size, load time, and HTTP status. Use this to identify missing meta tags, broken heading hierarchy, or oversized pages.

### Step 3 — Content Extraction
```
Tool: on_page_content_parsing
Input: {
  "url": "https://example.com/landing-page"
}
```

Extracts structured content: paragraphs, headings, lists, and tables in clean format. Use this to analyze content quality, keyword density, or feed text into further analysis.

## Workflow 2: Content Landscape Analysis

Understand how a topic is covered across the web — what content exists, overall sentiment, and trend direction.

### Step 1 — Search Content
```
Tool: content_analysis_search
Input: {
  "keyword": "headless CMS comparison",
  "search_mode": "as_is",
  "limit": 50
}
```

Returns up to 50 pages matching the keyword with metadata: page type (ecommerce, news, blog, message-board, organization), sentiment (positive/negative/neutral), word count, date published, and social metrics. Use `search_mode: "as_is"` for exact phrase or `"relevance"` for semantic matching.

### Step 2 — Summary Metrics
```
Tool: content_analysis_summary
Input: {
  "keyword": "headless CMS comparison"
}
```

Returns aggregated metrics: total pages found, average sentiment score, content type distribution, and top domains covering the topic. Use this for a quick market snapshot before diving into individual pages.

### Step 3 — Phrase Trends
```
Tool: content_analysis_phrase_trends
Input: {
  "keyword": "headless CMS comparison",
  "date_from": "2025-01-01"
}
```

**The `date_from` parameter is required.** Returns trend data showing how content publication volume for this phrase changed over time. Use this to identify rising topics, seasonal patterns, or declining interest. Set `date_from` to 6-12 months back for meaningful trends.

## Workflow 3: Technology Detection

Discover the full technology stack of any domain — CMS, frameworks, analytics, CDN, hosting, email services, and more.

```
Tool: domain_analytics_technologies_domain_technologies
Input: {
  "target": "example.com"
}
```

Returns categorized technology list: content management systems (WordPress, Shopify), JavaScript frameworks (React, Next.js), analytics (Google Analytics, Hotjar), CDN (Cloudflare, Fastly), hosting provider, advertising platforms, email services, and more. Each technology includes category, name, and version when detectable.

Use cases:
- Competitive intelligence — see what tools competitors use
- Sales prospecting — find companies using a specific technology
- Migration planning — understand the current stack before proposing changes

## Workflow 4: Domain Intelligence

Get registration and ownership data for any domain.

```
Tool: domain_analytics_whois_overview
Input: {
  "target": "example.com"
}
```

Returns WHOIS data: registrar, creation date, expiration date, updated date, name servers, registrant organization (when not privacy-protected), and domain status codes. Enriched with backlink summary stats when available.

Use cases:
- Due diligence — verify domain age and ownership
- Competitor research — find related domains by registrant
- Expired domain hunting — check expiration dates

## Interpreting Lighthouse Scores

| Score Range | Rating | Action |
|-------------|--------|--------|
| 90-100 | Good (green) | Maintain current optimizations |
| 50-89 | Needs Improvement (orange) | Address specific audit failures |
| 0-49 | Poor (red) | Prioritize immediate fixes |

Key Lighthouse audit categories:
- **Performance** — LCP, FID, CLS, TTFB, speed index. Most impactful for rankings.
- **Accessibility** — Color contrast, ARIA labels, heading order, alt text. Affects both SEO and compliance.
- **Best Practices** — HTTPS, console errors, deprecated APIs, image aspect ratios.
- **SEO** — Crawlability, meta tags, structured data, mobile viewport, link text.

Always check the `audits` object for specific failing items. Each audit has a `score` (0-1), `title`, and `description` explaining what to fix.

## Content Analysis Metrics

When interpreting `content_analysis_search` results:

| Metric | Values | Meaning |
|--------|--------|---------|
| `sentiment_connotations` | positive / negative / neutral | Overall tone of the content |
| `connotation_types` | anger, happiness, sadness, fear, love, fun | Emotional tone breakdown |
| `page_types` | ecommerce, news, blogs, message-boards, organization | Content category |
| `social_metrics` | facebook, twitter shares | Content virality indicators |
| `word_count` | integer | Content depth — higher often means more comprehensive |
| `spam_score` | 0-100 | Quality indicator — lower is better |

## Integration with Other Skills

- **Lighthouse finds slow performance** → Use keyword-research skill to check if ranking is affected, then optimize
- **Content analysis reveals competitor coverage gaps** → Use competitor-analysis skill to find their keyword strategy
- **Technology detection reveals outdated CMS** → Document in audit findings for migration recommendation
- **WHOIS shows expiring competitor domains** → Monitor with periodic checks

<example>
User: "Run a full technical audit on our homepage at https://acme.co"

1. Call on_page_lighthouse with url="https://acme.co" and for_mobile=true
2. Call on_page_instant_pages with url="https://acme.co"
3. Call on_page_content_parsing with url="https://acme.co"
4. Call domain_analytics_technologies_domain_technologies with target="acme.co"
5. Compile findings: Lighthouse scores, missing meta tags, heading hierarchy issues, technology stack
6. Present prioritized recommendations: critical (performance), important (SEO), nice-to-have (best practices)
</example>

<example>
User: "How is the topic 'AI code review' being covered online? Show me trends."

1. Call content_analysis_search with keyword="AI code review" and limit=50
2. Call content_analysis_summary with keyword="AI code review"
3. Call content_analysis_phrase_trends with keyword="AI code review" and date_from="2025-04-01"
4. Analyze: total coverage volume, dominant page types (blogs vs news), sentiment distribution
5. Report trend direction (growing/stable/declining) with monthly volume chart
6. Identify top 5 domains dominating this topic and their content angles
</example>
