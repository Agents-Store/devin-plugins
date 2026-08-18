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
| `~~search` | Find pages on the web | Exa → Perplexity → Jina → Firecrawl |
| `~~scrape` | Read a single page | Jina → Firecrawl |
| `~~batch_search` | Search multiple queries | Jina parallel → multiple Exa |
| `~~batch_scrape` | Read multiple pages | Jina parallel → multiple Firecrawl |
| `~~crawl` | Crawl entire site | Firecrawl crawl → map + batch_scrape |
| `~~extract` | Structured data extraction | Firecrawl extract → scrape + JSON |
| `~~academic_search` | Scientific papers | arXiv → SSRN → Perplexity |
| `~~code_search` | Code examples | Exa code → search + "github" |

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
1. Expand query → related terms
2. ~~batch_search(queries[]) → batch results
3. Rank by relevance → top results
4. ~~batch_scrape(top_5) → content
5. Deduplicate → clean data
```

### Full 7-Step Research
```
1. CLASSIFY → research type + depth
2. PLAN → expand query + 3-7 queries
3. SEARCH → ~~batch_search / ~~search (with fallback)
4. READ → ~~batch_scrape top-5 (with fallback)
5. EXTRACT → key facts, data, quotes
6. SYNTHESIZE → deduplicate + cross-check
7. REPORT → template + methodology
```

## Conventions

- All workflows use `~~capability` placeholders — see CONNECTORS.md for provider mapping
- Fallback chains apply automatically on errors or empty results
- All reports include Methodology section
- Every fact must have a URL source
