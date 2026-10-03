# Scenario: Keyword Strategy for a Product Launch

Build a keyword strategy for launching a new project management SaaS product. Each step is one `api_request` call with the method, path and `data` shown. Read each path's page with `docs_search` and agree a budget first.

## Step 1: Seed Keyword Expansion

Start with 3 to 5 seed keywords and expand:

```
POST /v3/dataforseo_labs/google/keyword_ideas/live
data: [{"keywords": ["project management software", "task management tool", "team collaboration app"],
        "location_code": 2840, "language_code": "en", "limit": 100,
        "filters": [["keyword_info.search_volume", ">", 50]],
        "order_by": ["keyword_info.search_volume,desc"]}]
```

Collect the returned keywords into a master list.

## Step 2: Get Long-Tail Variations

Use keyword suggestions for each high-value seed:

```
POST /v3/dataforseo_labs/google/keyword_suggestions/live
data: [{"keyword": "project management software", "location_code": 2840, "language_code": "en",
        "limit": 50,
        "filters": [["keyword_info.search_volume", ">", 20], "and", ["keyword_properties.keyword_difficulty", "<", 50]]}]
```

## Step 3: Bulk Metrics Check

Get metrics for all collected keywords at once (up to 700):

```
POST /v3/dataforseo_labs/google/keyword_overview/live
data: [{"keywords": ["project management software", "free project management tool", "task tracker app"],
        "location_code": 2840, "language_code": "en"}]
```

Extract search_volume, keyword_difficulty, cpc and competition_level.

## Step 4: Classify Search Intent

```
POST /v3/dataforseo_labs/google/search_intent/live
data: [{"keywords": ["best project management software", "what is project management", "monday.com pricing", "buy project management tool"]}]
```

Group the keywords by intent:
- **Informational**: blog posts, guides
- **Commercial**: comparison pages, reviews
- **Transactional**: landing pages, pricing pages
- **Navigational**: brand pages

## Step 5: Assess Difficulty

```
POST /v3/dataforseo_labs/google/bulk_keyword_difficulty/live
data: [{"keywords": ["project management software", "free task management", "team collaboration tool"],
        "location_code": 2840, "language_code": "en"}]
```

Prioritize keywords with difficulty below 40 and volume above 200 for quick wins.

## Step 6: Build the Priority Matrix

| Priority | Criteria | Action |
|----------|----------|--------|
| P0 (Quick wins) | Difficulty < 30, Volume > 100 | Target immediately |
| P1 (Strategic) | Difficulty 30-50, Volume > 500 | Build supporting content first |
| P2 (Long-term) | Difficulty > 50, Volume > 1000 | Build authority, then target |
| P3 (Niche) | Difficulty < 20, Volume < 100 | Include in content naturally |

## Expected Output

A keyword strategy document containing:
- 50-200 prioritized keywords grouped by intent
- Difficulty and volume metrics for each
- Content type recommendations per keyword group
- Estimated traffic potential per priority tier
