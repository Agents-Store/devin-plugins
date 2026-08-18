# Scenario: Market Research

**Query:** "AI code assistant market 2026 — размер, игроки, тренды"
**Type:** Market Research
**Depth:** deep
**Template:** Deep Research Report

## Step-by-Step Execution

### Step 1: CLASSIFY
```
Signals: "market", "размер", "игроки", "тренды" → Market Research
Depth: deep (broad market analysis)
```

### Step 2: PLAN
```
expand_query({ query: "AI code assistant market" })

Queries:
1. "AI code assistant market size revenue 2026"
2. "AI coding tools market growth forecast"
3. "GitHub Copilot Cursor Cody market share"
4. "AI developer tools funding investment 2025 2026"
5. "AI code completion market trends predictions"
6. "enterprise AI coding adoption statistics"
7. "AI code assistant startup landscape"
```

### Step 3: SEARCH
```
~~search("AI code assistant market size and growth in 2026")
→ Perplexity for AI-synthesized market data with citations

~~search("AI code assistant market revenue forecast")
→ Exa with research_paper category filter

~~batch_search([
  "GitHub Copilot revenue market share 2026",
  "Cursor AI funding valuation",
  "AI coding tools enterprise adoption rate",
  "AI developer productivity tools market"
])
```

### Step 4: READ
```
Rank by relevance("AI code assistant market", all_urls)
~~batch_scrape(top_8_urls)

Detect dates on URLs → filter for recent data only
```

### Step 5: EXTRACT
```
Extract from each source:
- Market size figures ($B)
- Growth rates (CAGR %)
- Key player names and market share
- Funding rounds
- Adoption statistics
```

### Step 6: SYNTHESIZE
```
deduplicate_strings(all_market_data)
Cross-check market size: compare figures from multiple sources
Flag single-source claims as Low confidence
Identify data gaps (e.g., private company revenue)
```

### Step 7: REPORT
Output: Deep Research Report with:
- Executive Summary (market size, growth, key players)
- Background (evolution from autocomplete to AI coding)
- Findings by segment (individual, team, enterprise)
- Data & Metrics table (market size, CAGR, funding)
- Key player profiles
- Gaps (private revenue data, emerging startups)
- Recommendations
- Methodology (7 queries, 8 pages, Perplexity + Exa + Jina)

### Expected Capabilities Used
`~~search`, `~~batch_search`, `~~batch_scrape`, relevance ranking, date detection, deduplication
