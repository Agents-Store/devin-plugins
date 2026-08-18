# Scenario: Keyword Strategy for Product Launch

Build a comprehensive keyword strategy for launching a new project management SaaS product.

## Step 1: Seed Keyword Expansion

Start with 3-5 seed keywords and expand:

```
Tool: mcp__dataforseo__dataforseo_labs_google_keyword_ideas
Input: {
  "keywords": ["project management software", "task management tool", "team collaboration app"],
  "location_name": "United States",
  "language_code": "en",
  "limit": 100,
  "filters": [["keyword_info.search_volume", ">", 50]],
  "order_by": ["keyword_info.search_volume,desc"]
}
```

Collect the returned keywords into a master list.

## Step 2: Get Long-Tail Variations

Use keyword suggestions for each high-value seed:

```
Tool: mcp__dataforseo__dataforseo_labs_google_keyword_suggestions
Input: {
  "keyword": "project management software",
  "location_name": "United States",
  "language_code": "en",
  "limit": 50,
  "filters": [["keyword_info.search_volume", ">", 20], "and", ["keyword_info.keyword_difficulty", "<", 50]]
}
```

## Step 3: Bulk Metrics Check

Get metrics for all collected keywords at once:

```
Tool: mcp__dataforseo__dataforseo_labs_google_keyword_overview
Input: {
  "keywords": ["project management software", "free project management tool", "task tracker app", "...up to 700 keywords"],
  "location_name": "United States",
  "language_code": "en"
}
```

Extract: search_volume, keyword_difficulty, cpc, competition_level.

## Step 4: Classify Search Intent

```
Tool: mcp__dataforseo__dataforseo_labs_search_intent
Input: {
  "keywords": ["best project management software", "what is project management", "monday.com pricing", "buy project management tool"],
  "language_code": "en"
}
```

Group keywords by intent:
- **Informational** → Blog posts, guides
- **Commercial** → Comparison pages, reviews
- **Transactional** → Landing pages, pricing pages
- **Navigational** → Brand pages

## Step 5: Assess Difficulty

```
Tool: mcp__dataforseo__dataforseo_labs_bulk_keyword_difficulty
Input: {
  "keywords": ["project management software", "free task management", "team collaboration tool"],
  "location_name": "United States",
  "language_code": "en"
}
```

Prioritize keywords with difficulty < 40 and volume > 200 for quick wins.

## Step 6: Build Priority Matrix

Organize keywords into a priority matrix:

| Priority | Criteria | Action |
|----------|----------|--------|
| P0 (Quick wins) | Difficulty < 30, Volume > 100 | Target immediately |
| P1 (Strategic) | Difficulty 30-50, Volume > 500 | Build supporting content first |
| P2 (Long-term) | Difficulty > 50, Volume > 1000 | Build authority then target |
| P3 (Niche) | Difficulty < 20, Volume < 100 | Include in content naturally |

## Expected Output

A keyword strategy document containing:
- 50-200 prioritized keywords grouped by intent
- Difficulty and volume metrics for each
- Content type recommendations per keyword group
- Estimated traffic potential per priority tier
