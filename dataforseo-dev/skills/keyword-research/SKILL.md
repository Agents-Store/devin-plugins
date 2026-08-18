---
name: keyword-research
description: This skill should be used when the user asks about "keyword research", "find keywords", "keyword ideas", "search volume", "keyword difficulty", "long-tail keywords", "keyword gap analysis", "keyword strategy", or needs to discover and evaluate keywords using DataForSEO.
---

# Keyword Research Workflows

Chained workflows for discovering, evaluating, and prioritizing keywords using DataForSEO MCP tools. All tool references use the `mcp__dataforseo__` prefix.

## Workflow 1: Topic-Based Keyword Research

Start from a broad topic and expand into a prioritized keyword list.

### Step 1 — Generate Seed Ideas

Call `dataforseo_labs_google_keyword_ideas` with 2-5 seed keywords. Set `location_name` and `language_code` to match the target market. Set `limit` to 100-200 for the initial pass.

```
Tool: dataforseo_labs_google_keyword_ideas
Params:
  keywords: ["project management software", "task management tool"]
  location_name: "United States"
  language_code: "en"
  limit: 200
```

### Step 2 — Get Metrics in Bulk

Collect all discovered keywords and pass them to `dataforseo_labs_google_keyword_overview` for metrics. This tool accepts up to 700 keywords in a single call, making it far more cost-efficient than fetching metrics one-by-one.

```
Tool: dataforseo_labs_google_keyword_overview
Params:
  keywords: [<all keywords from Step 1>]
  location_name: "United States"
  language_code: "en"
```

### Step 3 — Classify Search Intent

Pass the keyword list to `dataforseo_labs_search_intent` to classify each keyword as informational, navigational, commercial, or transactional. Use this to segment your final list by funnel stage.

```
Tool: dataforseo_labs_search_intent
Params:
  keywords: [<keywords from Step 2>]
  language_code: "en"
```

### Step 4 — Assess Difficulty in Bulk

Filter to promising candidates and run `dataforseo_labs_bulk_keyword_difficulty` to get difficulty scores for the entire set at once.

```
Tool: dataforseo_labs_bulk_keyword_difficulty
Params:
  keywords: [<filtered keywords>]
  location_name: "United States"
  language_code: "en"
```

Combine the results: sort by search_volume descending, filter by keyword_difficulty < 40 for quick wins, and group by search intent.

## Workflow 2: Competitor-Based Keyword Discovery

Extract keyword opportunities from a competitor domain.

### Step 1 — Pull Competitor Keywords

Call `dataforseo_labs_google_keywords_for_site` with the competitor domain to discover all keywords the domain is associated with.

```
Tool: dataforseo_labs_google_keywords_for_site
Params:
  target: "competitor.com"
  location_name: "United States"
  language_code: "en"
  limit: 500
```

### Step 2 — Check Current Rankings

Use `dataforseo_labs_google_ranked_keywords` to see which keywords the competitor actually ranks for and at what positions.

```
Tool: dataforseo_labs_google_ranked_keywords
Params:
  target: "competitor.com"
  location_name: "United States"
  language_code: "en"
  limit: 500
```

### Step 3 — Get Full Metrics

Pass the discovered keywords to `dataforseo_labs_google_keyword_overview` to retrieve search volume, CPC, competition, and difficulty.

Focus on keywords where the competitor ranks in positions 4-20 (vulnerable positions) and where search volume exceeds 100.

## Workflow 3: Keyword Gap Analysis

Find keywords competitors rank for but your domain does not.

### Step 1 — Intersect Domains

Call `dataforseo_labs_google_domain_intersection` with your domain and 1-2 competitor domains. Set `intersections` to identify keywords unique to competitors.

```
Tool: dataforseo_labs_google_domain_intersection
Params:
  targets:
    1: "competitor1.com"
    2: "competitor2.com"
  exclude_targets: ["yourdomain.com"]
  location_name: "United States"
  language_code: "en"
  limit: 300
```

### Step 2 — Evaluate Difficulty

Pass gap keywords to `dataforseo_labs_bulk_keyword_difficulty` to find low-difficulty opportunities the competitors hold that you can capture.

### Step 3 — Validate with SERP

For the top 10-20 candidates, run `serp_organic_live_advanced` to see the current SERP landscape and assess whether you can realistically compete.

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

Use full country names for `location_name`: "United States", "United Kingdom", "Germany", "France", "Australia". Use ISO 639-1 codes for `language_code`: "en", "de", "fr", "es", "pt".

Retrieve available locations via `kw_data_google_ads_locations` if unsure about the exact name string.

## Filtering Syntax

DataForSEO Labs endpoints accept nested filter arrays. Use the following format:

```json
[
  ["keyword_info.search_volume", ">", 100],
  "and",
  ["keyword_info.keyword_difficulty", "<", 30]
]
```

Common filter fields:
- `keyword_info.search_volume` — monthly searches
- `keyword_info.keyword_difficulty` — difficulty score
- `keyword_info.cpc` — cost per click
- `keyword_info.competition_level` — "LOW", "MEDIUM", "HIGH"
- `serp_info.se_results_count` — total SERP results for the keyword

Combine conditions with `"and"` / `"or"` strings between filter arrays.

## Cost Optimization

1. **Use keyword_overview first.** It processes up to 700 keywords in one API call. Always batch keywords through this before using more expensive endpoints like keyword_ideas or keyword_suggestions.
2. **Use bulk endpoints.** `bulk_keyword_difficulty` and `bulk_traffic_estimation` process many keywords at once for a fraction of the per-keyword cost.
3. **Set limits.** Always set `limit` on discovery endpoints (keyword_ideas, keywords_for_site) to avoid pulling thousands of results when 200-500 suffice.
4. **Filter server-side.** Pass filters in the API call rather than retrieving all results and filtering client-side.

<example>
User: "Find easy keywords for a SaaS project management tool"

Workflow:
1. Call dataforseo_labs_google_keyword_ideas with seeds ["project management software", "task management app", "team collaboration tool"], location_name "United States", language_code "en", limit 200
2. Collect all returned keywords → pass to dataforseo_labs_google_keyword_overview (batch of up to 700)
3. Filter results: search_volume > 200 AND keyword_difficulty < 35
4. Pass filtered set to dataforseo_labs_search_intent to classify intent
5. Sort by search_volume descending, group by intent
6. Present: table of keywords with volume, difficulty, CPC, intent — prioritize commercial/transactional intent with low difficulty
</example>

<example>
User: "What keywords does ahrefs.com rank for that we don't?"

Workflow:
1. Call dataforseo_labs_google_domain_intersection with targets {"1": "ahrefs.com"}, exclude_targets ["yourdomain.com"], location_name "United States", language_code "en", limit 300
2. Pass resulting keyword list to dataforseo_labs_bulk_keyword_difficulty to assess ranking feasibility
3. Filter: keyword_difficulty < 50 AND search_volume > 500
4. For top 10 keywords, call serp_organic_live_advanced to inspect current SERP composition
5. Present: gap keywords sorted by opportunity score (high volume + low difficulty), with SERP context for top picks
</example>
