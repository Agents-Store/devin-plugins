---
name: keyword-research
description: This skill should be used when the user asks about "keyword research", "find keywords", "keyword ideas", "search volume", "keyword difficulty", "long-tail keywords", "keyword gap analysis", "keyword strategy", or needs to discover and evaluate keywords using DataForSEO.
---

# Keyword Research Workflows

Chained workflows for discovering, evaluating and prioritizing keywords with DataForSEO. Every block below is one `api_request` call: the first line is the `method` and `path`, the second is `data`. Before the first call to a path, read its page with `docs_search` and agree a budget (`cost-awareness` skill). Paths and minimal bodies for the whole API are in `../mcp-patterns/references/endpoint-paths.md`.

## Workflow 1: Topic-Based Keyword Research

Start from a broad topic and expand into a prioritized keyword list.

### Step 1 — Generate Seed Ideas

Send 2 to 5 seed keywords to keyword ideas. Set the location and language for the target market and a `limit` of 100 to 200 for the first pass; in the default `.ai` mode an unset `limit` is 10.

```
POST /v3/dataforseo_labs/google/keyword_ideas/live
data: [{"keywords": ["project management software", "task management tool"],
        "location_code": 2840, "language_code": "en", "limit": 200}]
```

### Step 2 — Get Metrics in Bulk

Collect the keywords and send them to keyword overview for volume, CPC, competition and difficulty. One call takes up to 700 keywords, far cheaper than one call per keyword.

```
POST /v3/dataforseo_labs/google/keyword_overview/live
data: [{"keywords": [<all keywords from Step 1>], "location_code": 2840, "language_code": "en"}]
```

### Step 3 — Classify Search Intent

Search intent labels each keyword informational, navigational, commercial or transactional, so the list can be split by funnel stage. It takes up to 1000 keywords and has no location or language field.

```
POST /v3/dataforseo_labs/google/search_intent/live
data: [{"keywords": [<keywords from Step 2>]}]
```

### Step 4 — Assess Difficulty in Bulk

Filter to the promising candidates, then score the whole set in one call.

```
POST /v3/dataforseo_labs/google/bulk_keyword_difficulty/live
data: [{"keywords": [<filtered keywords>], "location_code": 2840, "language_code": "en"}]
```

Combine the results: sort by search volume descending, keep difficulty under 40 for quick wins, group by search intent.

## Workflow 2: Competitor-Based Keyword Discovery

Extract keyword opportunities from a competitor domain.

### Step 1 — Pull Competitor Keywords

Keywords for site returns the keywords a domain is relevant for.

```
POST /v3/dataforseo_labs/google/keywords_for_site/live
data: [{"target": "competitor.com", "location_code": 2840, "language_code": "en", "limit": 500}]
```

### Step 2 — Check Current Rankings

Ranked keywords shows where the domain actually ranks, with the position of each.

```
POST /v3/dataforseo_labs/google/ranked_keywords/live
data: [{"target": "competitor.com", "location_code": 2840, "language_code": "en", "limit": 500}]
```

### Step 3 — Get Full Metrics

Send the discovered keywords to keyword overview (Workflow 1, Step 2). Focus on keywords where the competitor ranks in positions 4 to 20 (vulnerable positions) and volume exceeds 100.

## Workflow 3: Keyword Gap Analysis

Find keywords a competitor ranks for and your domain does not.

### Step 1 — Intersect Domains

Domain intersection compares two domains. With `intersections: false` it returns the keywords `target1` ranks for and `target2` does not, so put the competitor first and your own domain second. With `true` it returns the keywords both rank for.

```
POST /v3/dataforseo_labs/google/domain_intersection/live
data: [{"target1": "competitor1.com", "target2": "yourdomain.com", "intersections": false,
        "location_code": 2840, "language_code": "en", "limit": 300}]
```

Repeat with the second competitor in `target1`.

### Step 2 — Evaluate Difficulty

Pass the gap keywords to bulk keyword difficulty (Workflow 1, Step 4) to find low-difficulty keywords the competitors hold and you can take.

### Step 3 — Validate with the SERP

For the 10 to 20 best candidates, read the live SERP and judge whether you can compete. This is the most expensive step; run it last, on a short list.

```
POST /v3/serp/google/organic/live/advanced
data: [{"keyword": "<candidate>", "location_code": 2840, "language_code": "en", "depth": 10}]
```

## Interpreting Keyword Metrics

| Metric | Description | Guidance |
|--------|-------------|----------|
| `search_volume` | Average monthly searches | >100 for niche, >1000 for broad targeting |
| `keyword_difficulty` | 0-100 score of ranking difficulty | <30 easy, 30-60 moderate, >60 hard |
| `cpc` | Cost per click in Google Ads (USD) | Higher CPC signals commercial intent |
| `competition` | 0-1 advertiser competition density | >0.5 indicates high commercial value |
| `competition_level` | LOW / MEDIUM / HIGH | Quick filter for paid competition |
| `search_intent` | informational / navigational / commercial / transactional | Align with content type |

## Location and Language Parameters

Use `location_code` (2840 is United States) or the full country name in `location_name`, and an ISO 639-1 `language_code` such as "en", "de", "fr", "es", "pt". If unsure of a code, look it up for free:

```
GET /v3/dataforseo_labs/locations_and_languages
```

## Filtering Syntax

Labs endpoints accept nested filter arrays in the request:

```json
[
  ["keyword_info.search_volume", ">", 100],
  "and",
  ["keyword_properties.keyword_difficulty", "<", 30]
]
```

Common filter fields:
- `keyword_info.search_volume` — monthly searches
- `keyword_properties.keyword_difficulty` — difficulty score (it lives in `keyword_properties`, not `keyword_info`)
- `keyword_info.cpc` — cost per click
- `keyword_info.competition_level` — "LOW", "MEDIUM", "HIGH"
- `serp_info.se_results_count` — total SERP results for the keyword

On `keyword_ideas` and `keyword_suggestions` these paths are as written. Endpoints that wrap each item in `keyword_data` (`related_keywords`, `ranked_keywords`, `domain_intersection`) prefix them: `keyword_data.keyword_properties.keyword_difficulty`, `keyword_data.keyword_info.search_volume`.

The full field list for an endpoint is on its `docs_search` page and at `docs_search({url: "dataforseo_labs/filters"})`.

## Cost Optimization

1. **Use keyword overview first.** It takes up to 700 keywords in one call. Run the keywords through it before any more expensive endpoint.
2. **Use bulk endpoints.** `bulk_keyword_difficulty` (1000 keywords) and `bulk_traffic_estimation` (1000 targets) replace loops.
3. **Set limits.** Always set `limit` on discovery endpoints (keyword ideas, keywords for site); 200 to 500 rows usually suffice.
4. **Filter server-side.** Put `filters` and `order_by` in the request rather than fetching everything and filtering afterwards.

<example>
User: "Find easy keywords for a SaaS project management tool"

Workflow:
1. docs_search for the four paths below, show the plan (4 calls, limit 200 on the first), get the user's budget
2. api_request POST /v3/dataforseo_labs/google/keyword_ideas/live with seeds ["project management software", "task management app", "team collaboration tool"], location_code 2840, language_code "en", limit 200
3. Pass the keywords to /v3/dataforseo_labs/google/keyword_overview/live (one call, up to 700)
4. Keep search_volume > 200 and keyword_difficulty < 35
5. Pass the survivors to /v3/dataforseo_labs/google/search_intent/live
6. Present: table of keywords with volume, difficulty, CPC and intent; commercial and transactional intent with low difficulty first
</example>

<example>
User: "What keywords does ahrefs.com rank for that we don't?"

Workflow:
1. docs_search for /v3/dataforseo_labs/google/domain_intersection/live; get the user's budget
2. api_request POST that path with target1 "ahrefs.com", target2 "yourdomain.com", intersections false, location_code 2840, language_code "en", limit 300
3. Pass the keyword list to /v3/dataforseo_labs/google/bulk_keyword_difficulty/live
4. Keep keyword_difficulty < 50 and search_volume > 500
5. For the top 10, read the live SERP at /v3/serp/google/organic/live/advanced
6. Present: gap keywords sorted by opportunity (high volume, low difficulty), with SERP context for the top picks
</example>
