---
name: competitor-analysis
description: This skill should be used when the user asks about "competitor analysis", "competitor research", "domain comparison", "who ranks for", "competitive landscape", "competitor keywords", "competitor traffic", or needs to analyze and compare domains using DataForSEO.
---

# Competitor Analysis Workflows

Chained workflows for analyzing, comparing, and benchmarking competitor domains using DataForSEO MCP tools. All tool references use the `mcp__dataforseo__` prefix.

## Workflow 1: Domain Overview

Build a high-level snapshot of any domain's organic and paid performance.

### Step 1 — Get Domain Rank Overview

Call `dataforseo_labs_google_domain_rank_overview` for each domain you want to analyze. This returns organic traffic estimates, keyword counts, backlink counts, and rank position distribution.

```
Tool: dataforseo_labs_google_domain_rank_overview
Params:
  target: "competitor.com"
  location_name: "United States"
  language_code: "en"
```

### Step 2 — Repeat for Your Domain

Run the same call for your own domain. Compare side-by-side: organic keyword count, estimated traffic value, top-3 positions, and backlink metrics.

### Step 3 — Check Historical Trends

Call `dataforseo_labs_google_historical_rank_overview` for each domain to see how these metrics have changed over time. This reveals whether competitors are growing or declining.

```
Tool: dataforseo_labs_google_historical_rank_overview
Params:
  target: "competitor.com"
  location_name: "United States"
  language_code: "en"
```

Build a comparison table: domain, organic keywords, estimated traffic, estimated traffic value, backlinks, referring domains, and trend direction.

## Workflow 2: Discover Competitors

Find domains that compete for the same organic keywords.

### Step 1 — Identify Organic Competitors

Call `dataforseo_labs_google_competitors_domain` with your target domain. Set `exclude_top_domains` to `true` to filter out generic giants (Wikipedia, YouTube, etc.) and surface relevant competitors.

```
Tool: dataforseo_labs_google_competitors_domain
Params:
  target: "yourdomain.com"
  location_name: "United States"
  language_code: "en"
  exclude_top_domains: true
  limit: 50
```

### Step 2 — Profile Each Competitor

For the top 5-10 competitors returned, call `dataforseo_labs_google_domain_rank_overview` on each to get their full metrics.

### Step 3 — Identify Common Keywords

Call `dataforseo_labs_google_ranked_keywords` on the most relevant competitors to see which keywords they rank for and at what positions.

Sort competitors by `avg_position` and `intersections` (number of shared keywords) to prioritize the most direct competitors.

## Workflow 3: Keyword Intersection

Find shared and unique keywords across 2-3 domains.

### Step 1 — Run Domain Intersection

Call `dataforseo_labs_google_domain_intersection` with your domain and competitor domains as targets. The tool compares up to 20 domains and returns keywords where the specified domains overlap or diverge.

```
Tool: dataforseo_labs_google_domain_intersection
Params:
  targets:
    1: "yourdomain.com"
    2: "competitor1.com"
    3: "competitor2.com"
  location_name: "United States"
  language_code: "en"
  limit: 500
```

### Step 2 — Analyze Gaps

Filter results to find keywords where competitors rank but you do not. These are your keyword gap opportunities. Filter further by search_volume > 100 and keyword_difficulty < 50 for actionable targets.

### Step 3 — Analyze Overlaps

Filter for keywords where all domains rank. Compare position distributions. Keywords where competitors rank in positions 1-3 but you rank 10+ indicate areas for content improvement.

## Workflow 4: SERP Competition

Analyze who competes for specific keyword clusters in search results.

### Step 1 — Identify SERP Competitors

Call `dataforseo_labs_google_serp_competitors` with a set of target keywords to see which domains appear most frequently across those SERPs.

```
Tool: dataforseo_labs_google_serp_competitors
Params:
  keywords: ["project management software", "task management tool", "team collaboration app"]
  location_name: "United States"
  language_code: "en"
```

### Step 2 — Deep-Dive on Top Competitors

For the top-ranking domains returned, call `dataforseo_labs_google_ranked_keywords` filtered to your keyword cluster to see their exact positions and page URLs.

### Step 3 — Inspect Individual SERPs

For the highest-priority keywords, call `serp_organic_live_advanced` to see the full SERP layout including featured snippets, people-also-ask, and other SERP features.

## Workflow 5: Content Gap Analysis

Find pages and content opportunities competitors have that you lack.

### Step 1 — Page Intersection

Call `dataforseo_labs_google_page_intersection` with competitor page URLs to find queries where their specific pages rank.

```
Tool: dataforseo_labs_google_page_intersection
Params:
  pages:
    1: "competitor1.com/blog/topic-guide"
    2: "competitor2.com/resources/topic-overview"
  location_name: "United States"
  language_code: "en"
  limit: 200
```

### Step 2 — Find Top Content

Call `dataforseo_labs_google_relevant_pages` on a competitor domain to discover their highest-performing pages by organic traffic.

```
Tool: dataforseo_labs_google_relevant_pages
Params:
  target: "competitor.com"
  location_name: "United States"
  language_code: "en"
  limit: 100
```

### Step 3 — Analyze Subdomains

Call `dataforseo_labs_google_subdomains` to see traffic distribution across competitor subdomains (blog, docs, app, etc.) and identify which content hubs drive the most traffic.

## Interpreting Results

Key metrics in domain rank overview and ranked keywords responses:

| Metric | Description | Use |
|--------|-------------|-----|
| `metrics.organic.count` | Total organic keywords the domain ranks for | Overall organic footprint |
| `metrics.organic.etv` | Estimated traffic value in USD | Monetization proxy |
| `metrics.organic.pos_1` | Keywords in position 1 | Brand/authority strength |
| `metrics.organic.pos_2_3` | Keywords in positions 2-3 | Near-top-of-funnel strength |
| `metrics.organic.pos_4_10` | Keywords in positions 4-10 | First page presence |
| `metrics.organic.pos_11_20` | Keywords in positions 11-20 | Page 2 — optimization targets |
| `metrics.organic.is_up` | Keywords that moved up | Positive momentum |
| `metrics.organic.is_down` | Keywords that moved down | Declining performance |
| `avg_position` | Average ranking position for intersection | Relative strength comparison |
| `intersections` | Number of shared keywords | Competitive overlap degree |

## Building a Competitive Report

Combine these workflows into a structured competitive analysis:

1. **Executive summary** — domain_rank_overview comparison table for all domains
2. **Competitor discovery** — competitors_domain results, ranked by relevance
3. **Keyword landscape** — domain_intersection showing shared, unique, and gap keywords
4. **Content analysis** — relevant_pages and subdomains for top competitors
5. **SERP features** — serp_organic_live_advanced showing feature ownership (snippets, PAA)
6. **Recommendations** — keywords to target (low difficulty gaps), content to create (competitor top pages you lack), positions to defend (keywords where you lead but competitors are closing)

<example>
User: "Compare our domain against two competitors"

Workflow:
1. Call dataforseo_labs_google_domain_rank_overview for "yourdomain.com", "competitor1.com", "competitor2.com" — three parallel calls
2. Build comparison table: organic keywords, etv, backlinks, referring domains, position distribution
3. Call dataforseo_labs_google_domain_intersection with all three domains, limit 500
4. Segment results: keywords only you rank for (strengths), keywords only competitors rank for (gaps), keywords all share (battlegrounds)
5. For gap keywords: filter by search_volume > 200 and keyword_difficulty < 50
6. Present: overview table, gap opportunity list, battleground keywords where you trail, and top recommended actions
</example>

<example>
User: "Who are our main organic competitors and what are they doing better?"

Workflow:
1. Call dataforseo_labs_google_competitors_domain with target "yourdomain.com", exclude_top_domains true, limit 30
2. Take top 5 competitors by intersection count
3. Call dataforseo_labs_google_domain_rank_overview on each of the 5 competitors
4. Call dataforseo_labs_google_relevant_pages on the top 2 competitors, limit 50 each
5. Call dataforseo_labs_google_domain_intersection with your domain vs. top competitor, limit 300
6. Present: competitor profiles (traffic, keywords, trend), their top-performing content pages, keyword gaps you should pursue, and content types that drive their traffic
</example>
