---
name: competitor-analysis
description: This skill should be used when the user asks about "competitor analysis", "competitor research", "domain comparison", "who ranks for", "competitive landscape", "competitor keywords", "competitor traffic", or needs to analyze and compare domains using DataForSEO.
---

# Competitor Analysis Workflows

Chained workflows for analyzing, comparing and benchmarking competitor domains with DataForSEO. Every block below is one `api_request` call: the first line is the `method` and `path`, the second is `data`. Before the first call to a path, read its page with `docs_search` and agree a budget (`cost-awareness` skill). Paths and minimal bodies for the whole API are in `../mcp-patterns/references/endpoint-paths.md`.

## Workflow 1: Domain Overview

Build a high-level snapshot of any domain's organic and paid performance.

### Step 1 — Get Domain Rank Overview

Run it once per domain. It returns organic traffic estimates, keyword counts and the distribution of ranking positions.

```
POST /v3/dataforseo_labs/google/domain_rank_overview/live
data: [{"target": "competitor.com", "location_code": 2840, "language_code": "en"}]
```

### Step 2 — Repeat for Your Domain

Run the same call for your own domain and compare side by side: organic keyword count, estimated traffic value, top-3 positions.

### Step 3 — Check Historical Trends

Monthly snapshots show whether a competitor is growing or declining.

```
POST /v3/dataforseo_labs/google/historical_rank_overview/live
data: [{"target": "competitor.com", "location_code": 2840, "language_code": "en"}]
```

For backlink metrics, add one call to `/v3/backlinks/bulk_ranks/live` with `{"targets": [<all domains>]}`; it covers up to 1000 targets.

Build a comparison table: domain, organic keywords, estimated traffic, estimated traffic value, rank, trend direction.

## Workflow 2: Discover Competitors

Find domains that compete for the same organic keywords.

### Step 1 — Identify Organic Competitors

Set `exclude_top_domains` to `true` to drop the generic giants (Wikipedia, YouTube and the like) and surface relevant competitors.

```
POST /v3/dataforseo_labs/google/competitors_domain/live
data: [{"target": "yourdomain.com", "location_code": 2840, "language_code": "en",
        "exclude_top_domains": true, "limit": 50}]
```

### Step 2 — Profile Each Competitor

For the top 5 to 10 competitors, run domain rank overview (Workflow 1, Step 1).

### Step 3 — Identify Common Keywords

Ranked keywords on the most relevant competitors shows which keywords they rank for and at what positions.

```
POST /v3/dataforseo_labs/google/ranked_keywords/live
data: [{"target": "competitor.com", "location_code": 2840, "language_code": "en", "limit": 200}]
```

Sort competitors by `avg_position` and `intersections` (shared keywords) to find the most direct ones.

## Workflow 3: Keyword Intersection

Find shared and unique keywords between two domains. The endpoint compares exactly two domains; for a third, run it again with another pair.

### Step 1 — Run Domain Intersection

`intersections: true` returns the keywords both domains rank for; `false` returns the keywords `target1` ranks for and `target2` does not.

```
POST /v3/dataforseo_labs/google/domain_intersection/live
data: [{"target1": "yourdomain.com", "target2": "competitor1.com", "intersections": true,
        "location_code": 2840, "language_code": "en", "limit": 500}]
```

### Step 2 — Analyze Gaps

Swap the roles to get the gap: `target1` is the competitor, `target2` is you, `intersections` is `false`. Filter to search volume above 100 and keyword difficulty below 50 for actionable targets.

```
POST /v3/dataforseo_labs/google/domain_intersection/live
data: [{"target1": "competitor1.com", "target2": "yourdomain.com", "intersections": false,
        "location_code": 2840, "language_code": "en", "limit": 300,
        "filters": [["keyword_data.keyword_info.search_volume", ">", 100]]}]
```

### Step 3 — Analyze Overlaps

In the shared set, compare position distributions. Keywords where a competitor ranks 1 to 3 and you rank 10 or lower point at content to improve.

## Workflow 4: SERP Competition

Analyze who competes for specific keyword clusters in search results.

### Step 1 — Identify SERP Competitors

Which domains appear most often across the SERPs of a keyword set (up to 200 keywords).

```
POST /v3/dataforseo_labs/google/serp_competitors/live
data: [{"keywords": ["project management software", "task management tool", "team collaboration app"],
        "location_code": 2840, "language_code": "en"}]
```

### Step 2 — Deep-Dive on Top Competitors

Run ranked keywords (Workflow 2, Step 3) for the top domains, filtered to your keyword cluster, to see exact positions and page URLs.

### Step 3 — Inspect Individual SERPs

For the highest-priority keywords, read the full SERP including featured snippets, people-also-ask and other features.

```
POST /v3/serp/google/organic/live/advanced
data: [{"keyword": "<priority keyword>", "location_code": 2840, "language_code": "en", "depth": 10}]
```

## Workflow 5: Content Gap Analysis

Find pages and content opportunities competitors have that you lack.

### Step 1 — Page Intersection

Queries where specific competitor pages rank. `pages` is an object keyed "1", "2", and so on, with absolute URLs (up to 20; `*` is a wildcard).

```
POST /v3/dataforseo_labs/google/page_intersection/live
data: [{"pages": {"1": "https://competitor1.com/blog/topic-guide",
                  "2": "https://competitor2.com/resources/topic-overview"},
        "location_code": 2840, "language_code": "en", "limit": 200}]
```

### Step 2 — Find Top Content

A competitor's highest-performing pages by organic traffic.

```
POST /v3/dataforseo_labs/google/relevant_pages/live
data: [{"target": "competitor.com", "location_code": 2840, "language_code": "en", "limit": 100}]
```

### Step 3 — Analyze Subdomains

Traffic distribution across the competitor's subdomains (blog, docs, app) shows which content hubs drive the most traffic.

```
POST /v3/dataforseo_labs/google/subdomains/live
data: [{"target": "competitor.com", "location_code": 2840, "language_code": "en"}]
```

## Interpreting Results

Key metrics in domain rank overview and ranked keywords responses:

| Metric | Description | Use |
|--------|-------------|-----|
| `metrics.organic.count` | Total organic keywords the domain ranks for | Overall organic footprint |
| `metrics.organic.etv` | Estimated traffic value | Monetization proxy |
| `metrics.organic.pos_1` | Keywords in position 1 | Brand/authority strength |
| `metrics.organic.pos_2_3` | Keywords in positions 2-3 | Near-top-of-funnel strength |
| `metrics.organic.pos_4_10` | Keywords in positions 4-10 | First page presence |
| `metrics.organic.pos_11_20` | Keywords in positions 11-20 | Page 2, optimization targets |
| `metrics.organic.is_up` | Keywords that moved up | Positive momentum |
| `metrics.organic.is_down` | Keywords that moved down | Declining performance |
| `avg_position` | Average ranking position for intersection | Relative strength comparison |
| `intersections` | Number of shared keywords | Competitive overlap degree |

## Building a Competitive Report

1. **Executive summary**: the domain rank overview comparison table for all domains
2. **Competitor discovery**: competitors_domain results, ranked by relevance
3. **Keyword landscape**: shared, unique and gap keywords from domain_intersection
4. **Content analysis**: relevant_pages and subdomains for the top competitors
5. **SERP features**: the live SERP, showing feature ownership (snippets, people-also-ask)
6. **Recommendations**: keywords to target (low-difficulty gaps), content to create (competitor top pages you lack), positions to defend (keywords where you lead and competitors are closing)

<example>
User: "Compare our domain against two competitors"

Workflow:
1. docs_search for domain_rank_overview and domain_intersection; show the plan (3 overview calls, 2 intersection calls); get the user's budget
2. api_request POST /v3/dataforseo_labs/google/domain_rank_overview/live once each for "yourdomain.com", "competitor1.com", "competitor2.com"
3. Build the comparison table: organic keywords, etv, position distribution
4. POST /v3/dataforseo_labs/google/domain_intersection/live with target1 "competitor1.com", target2 "yourdomain.com", intersections false, limit 300; repeat for competitor2
5. For the gap keywords: search_volume > 200 and keyword_difficulty < 50 (score them with /v3/dataforseo_labs/google/bulk_keyword_difficulty/live)
6. Present: overview table, gap opportunity list, and the top recommended actions
</example>

<example>
User: "Who are our main organic competitors and what are they doing better?"

Workflow:
1. docs_search for the paths below; get the user's budget
2. api_request POST /v3/dataforseo_labs/google/competitors_domain/live with target "yourdomain.com", exclude_top_domains true, limit 30
3. Take the top 5 by intersection count
4. POST /v3/dataforseo_labs/google/domain_rank_overview/live on each of the 5
5. POST /v3/dataforseo_labs/google/relevant_pages/live on the top 2, limit 50 each
6. POST /v3/dataforseo_labs/google/domain_intersection/live, your domain against the top competitor, intersections false, limit 300
7. Present: competitor profiles (traffic, keywords, trend), their top-performing pages, the keyword gaps to pursue, and the content types that drive their traffic
</example>
