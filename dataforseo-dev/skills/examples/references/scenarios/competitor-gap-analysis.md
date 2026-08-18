# Scenario: Competitor Gap Analysis

Analyze the competitive landscape for a B2B SaaS domain and find keyword/backlink gaps.

## Step 1: Identify Competitors

```
Tool: mcp__dataforseo__dataforseo_labs_google_competitors_domain
Input: {
  "target": "example.com",
  "location_name": "United States",
  "language_code": "en",
  "exclude_top_domains": true,
  "limit": 15
}
```

Review returned domains. Pick the top 3-5 most relevant competitors (ignore generic sites like Wikipedia, Reddit).

## Step 2: Compare Domain Metrics

```
Tool: mcp__dataforseo__dataforseo_labs_google_domain_rank_overview
Input: {
  "target": "example.com",
  "location_name": "United States",
  "language_code": "en"
}
```

Repeat for each competitor. Compare:
- `organic.count` — total ranking keywords
- `organic.etv` — estimated traffic value
- `organic.pos_1` through `organic.pos_10` — positions distribution

## Step 3: Find Keyword Gaps

```
Tool: mcp__dataforseo__dataforseo_labs_google_domain_intersection
Input: {
  "targets": {
    "1": "competitor1.com",
    "2": "example.com"
  },
  "location_name": "United States",
  "language_code": "en",
  "limit": 100,
  "filters": [["keyword_data.keyword_info.search_volume", ">", 100]],
  "order_by": ["keyword_data.keyword_info.search_volume,desc"]
}
```

Filter for keywords where the competitor ranks but you don't (intersection_result shows which targets rank).

## Step 4: Analyze SERP for Top Opportunities

Pick the top 5 gap keywords and check SERP difficulty:

```
Tool: mcp__dataforseo__serp_organic_live_advanced
Input: {
  "keyword": "best project management tool for agencies",
  "location_name": "United States",
  "language_code": "en",
  "depth": 20
}
```

Assess: Are top results dominated by high-authority sites? Is there room for a new entrant?

## Step 5: Backlink Gap Analysis

```
Tool: mcp__dataforseo__backlinks_competitors
Input: {
  "target": "example.com",
  "limit": 20
}
```

Then compare referring domains:

```
Tool: mcp__dataforseo__backlinks_bulk_ranks
Input: {
  "targets": ["example.com", "competitor1.com", "competitor2.com", "competitor3.com"]
}
```

## Step 6: Content Gap via Page Intersection

```
Tool: mcp__dataforseo__dataforseo_labs_google_relevant_pages
Input: {
  "target": "competitor1.com",
  "location_name": "United States",
  "language_code": "en",
  "limit": 20
}
```

Find competitor's top pages by traffic. Identify content types you're missing (guides, comparisons, tools).

## Expected Output

A competitive analysis report containing:
- Competitor domain metrics comparison table
- 20-50 keyword gap opportunities with volume and difficulty
- Backlink gap: domains linking to competitors but not you
- Content gap: page types and topics competitors cover that you don't
- Priority recommendations: quick win keywords, link building targets, content to create
