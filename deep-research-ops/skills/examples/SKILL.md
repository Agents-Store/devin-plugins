---
name: examples
description: Tool call patterns, end-to-end research workflow examples, and scenario references for all 6 research types. Use when you need reference implementations or complete research examples.
---

# Examples & References

Patterns and multi-step workflows. All calls use `~~capability` with fallback (see CONNECTORS.md).

## Reference Files

| File | Description |
|------|-------------|
| [tool-patterns.md](references/mcp/tool-patterns.md) | Tool call patterns organized by capability |
| [workflow-examples.md](references/mcp/workflow-examples.md) | Multi-step workflow examples |
| [competitive-analysis.md](references/scenarios/competitive-analysis.md) | Scenario: competitor comparison |
| [market-research.md](references/scenarios/market-research.md) | Scenario: market research |
| [technical-audit.md](references/scenarios/technical-audit.md) | Scenario: technical audit |
| [person-company-lookup.md](references/scenarios/person-company-lookup.md) | Scenario: person/company lookup |
| [topic-deep-dive.md](references/scenarios/topic-deep-dive.md) | Scenario: topic deep dive |
| [news-trends.md](references/scenarios/news-trends.md) | Scenario: news & trends |

## Quick Reference: Capabilities

| Capability | What it does | Fallback order |
|-----------|-------------|----------------|
| `~~search` | Find pages on the web | `web_search_exa` → `perplexity_search` → `search_web` → `firecrawl_search` |
| `~~answer` | Short AI answer with citations | `perplexity_ask` → `perplexity_reason` → `perplexity_search` / `~~search` results + your own cited synthesis |
| `~~scrape` | Read a single page (with `question`: only the relevant passages) | `read_url` → `firecrawl_scrape` → `web_fetch_exa` (`maxCharacters: 20000`) |
| `~~batch_search` | Search multiple queries (≤5 per call) | `search_web` with an array → one `web_search_exa` per query |
| `~~batch_scrape` | Read multiple pages (≤5 per call) | `read_url` with an array → `web_fetch_exa` (`maxCharacters: 20000`) → one `firecrawl_scrape` per URL (fallbacks return full pages, no `question`) |
| `~~crawl` | Crawl entire site | `firecrawl_crawl` → `firecrawl_map` + batch scrape |
| `~~extract` | Structured data extraction | `firecrawl_scrape` (JSON format) → `firecrawl_agent` for unknown URLs |
| `~~academic_search` | Scientific papers | `firecrawl_research_search_papers` → `search_arxiv` / `search_ssrn` → `perplexity_search` |
| `~~code_search` | Code examples, issues, docs | `firecrawl_developer_search` → `web_search_advanced_exa` (opt-in) → search + "github" |
| `~~deep_agent` | Heavy research pass for depth `deep` | `agent_run` → `firecrawl_agent` → `perplexity_research` |

## Quick Workflow Patterns

### Quick Search with Fallback
```
1. ~~search(query) → results
2. If error → next provider automatically
3. ~~scrape(best_url) → content
4. If error → next provider automatically
```

### Parallel Research Batch
```
1. Plan related terms and 3-5 queries yourself
2. ~~batch_search(queries[]) → batch results
3. Rank by relevance → top results
4. ~~batch_scrape(top_5, question, topk) → only the relevant passages
5. Deduplicate → clean data
```

### Full 7-Step Research
```
1. CLASSIFY → research type + depth
2. PLAN → 3-7 queries from different angles
3. SEARCH → ~~batch_search / ~~search (with fallback); depth deep adds ~~deep_agent
4. READ → ~~batch_scrape top-5 with a question (with fallback)
5. EXTRACT → key facts, data, quotes
6. SYNTHESIZE → deduplicate + cross-check
7. REPORT → template + methodology
```

## Conventions

- All workflows use `~~capability` placeholders — see CONNECTORS.md for provider mapping
- Fallback chains apply automatically on errors or empty results
- All reports include Methodology section
- Every fact must have a URL source
