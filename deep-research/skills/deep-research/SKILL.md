---
name: deep-research
description: Main research automation skill. 7-step algorithm for comprehensive research with 6 research types, query planning, parallel search, extraction, synthesis, and structured reporting. Use when conducting any multi-step research task.
---

# Deep Research

Core algorithm for comprehensive research. 7 steps, 6 research types. All calls use `~~capability` with automatic fallback between providers (see CONNECTORS.md for chains).

## 6 Research Types

| Type | Trigger Signals | Focus | Report Template |
|------|----------------|-------|----------------|
| **Competitive Analysis** | "competitors", "vs", "compare", "alternatives" | Sites, products, prices, positioning | Comparison Table |
| **Market Research** | "market", "trends", "TAM", "forecast" | Size, growth, segments, players | Deep Research Report |
| **Technical Audit** | "architecture", "stack", "how does it work", "best practices" | Technologies, performance, patterns | Deep Research Report |
| **Person/Company Lookup** | name, company, "who is", "about company" | Biography, history, key facts | Executive Summary |
| **Topic Deep Dive** | "explain", "deep dive", "in detail", "comprehensive" | All angles, history, current state | Deep Research Report |
| **News & Trends** | "news", "latest", "recent", year/date | Events, developments, timeline | Executive Summary |

## 7-Step Algorithm

### Step 1: CLASSIFY

Determine the research type from signals in the user's query.

```
Input: user query
Logic: match keywords to research type (see table above)
Output: research_type + depth_level
If ambiguous: ask user to clarify
```

**Depth levels:**

| Level | Queries | Pages | Description |
|-------|---------|-------|-------------|
| quick | 2-3 | 3 | Quick overview |
| standard | 4-5 | 5 | Standard research |
| deep | 6-7 | 8-10 | Deep analysis |

### Step 2: PLAN

Form 3-7 search queries from different angles.

```
1. expand_query(topic) → related terms
2. Generate queries covering different angles:
   - Direct: "{topic} overview"
   - Comparison: "{topic} vs alternatives"
   - Expert: "{topic} expert analysis review"
   - Data: "{topic} statistics data 2026"
   - Trends: "{topic} trends forecast"
```

**IMPORTANT — Named Entity Discovery:**

If the query contains a specific product/project/brand/tool name, FIRST run the Exhaustive Discovery Protocol (see `search-strategies` skill) BEFORE general research.

**Query patterns by type:**

| Type | Query patterns |
|------|---------------|
| Competitive Analysis | "{product} pricing", "{product} vs {competitor}", "{product} reviews", "{product} features comparison" |
| Market Research | "{industry} market size", "{industry} trends 2026", "{industry} key players", "{industry} growth forecast" |
| Technical Audit | "{technology} architecture", "{technology} best practices", "{technology} performance benchmarks", "{technology} documentation" |
| Person/Company Lookup | "{name} background", "{company} about", "{company} funding revenue", "{name} interview" |
| Topic Deep Dive | "{topic} explained", "{topic} history evolution", "{topic} current state", "{topic} future predictions" |
| News & Trends | "{topic} latest news", "{topic} recent developments", "{topic} 2026 updates" |

### Step 3: SEARCH

Search using `~~search` / `~~batch_search` with automatic fallback (see CONNECTORS.md for provider order).

```
1. IF named entity (product/project/brand):
   → Run Exhaustive Discovery Protocol FIRST
   → Use found URLs as primary sources

2. ~~batch_search(queries) — parallel search
   Fallback: ~~search(query) for each query individually

3. For scientific topics:
   ~~academic_search(query) — add academic results

4. For facts:
   ~~search(query) — AI-synthesized answers

5. On error from any provider → try next in chain (see CONNECTORS.md)
```

**Tool selection by type:**

| Type | Primary | Additional |
|------|---------|-----------|
| Competitive Analysis | `~~search` | `~~extract` for pricing |
| Market Research | `~~search` | `~~search` (different provider for details) |
| Technical Audit | `~~code_search` | `~~search` for docs |
| Person/Company Lookup | **Exhaustive Discovery Protocol** | `~~search` for facts |
| Topic Deep Dive | `~~batch_search` | `~~academic_search` for papers |
| News & Trends | `~~search` | `~~search` (with date filter) |

### Step 4: READ

Read top-5 pages using `~~scrape` / `~~batch_scrape` with fallback.

```
1. Collect all URLs from search results
2. Rank by relevance → top results
3. Select top-5 (or top-N based on depth)
4. ~~batch_scrape(top_urls) → get content
   Fallback: ~~scrape per URL individually

Priority:
- Official sites > reputable sources > blogs
- Recent > older (check publication date)
- Primary sources > secondary
```

### Step 5: EXTRACT

Extract key data from the content read.

```
From each page extract:
- Key facts and claims
- Numbers, metrics, data points
- Direct quotes (with attribution)
- Dates and timeline events

Tools:
- Text classification → categorize content
- ~~extract(urls, schema) → structured data
- For PDFs: PDF extraction → full text
```

### Step 6: SYNTHESIZE

Combine data, deduplicate, cross-check.

```
1. Deduplicate → remove redundant info
2. Cross-check: compare facts from different sources
   - Same fact from 3+ sources → High confidence
   - Same fact from 2 sources → Medium confidence
   - Single source only → Low confidence (flag it)
3. Identify contradictions → note in Gaps section
4. Identify information gaps → note what was NOT found
```

### Step 7: REPORT

Generate a structured report.

```
1. Select template based on research_type
   (see report-generation skill for full templates)

2. Fill in all sections:
   - Key Findings with inline citations
   - Data tables with sources
   - Quotes with attribution
   - Gaps & Limitations

3. ALWAYS include Methodology:
   - Research type
   - Providers used (which responded, which failed)
   - Search queries (full list)
   - Pages analyzed (count)
   - Date of research
   - Limitations

4. Output the report in markdown
```

## Quality Checklist

Before delivering any report, verify:

- [ ] Research type correctly classified
- [ ] Minimum 3 search queries from different angles
- [ ] At least 3-5 pages read and analyzed
- [ ] Every fact has a URL source
- [ ] Data cross-checked across sources
- [ ] Confidence levels assigned (High/Medium/Low)
- [ ] Gaps and limitations documented
- [ ] Methodology section complete
- [ ] Date of research included
- [ ] Report uses correct template for research type
