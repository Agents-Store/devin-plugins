---
name: mcp-patterns
description: This skill should be used when the user asks about "web search MCP tools", "which search tools are available", "firecrawl tools", "exa tools", "jina tools", "perplexity tools", "how to use search MCP", "scraping MCP tools", "media search tools", or needs to know which MCP operations are available across web search and scraping services. Also triggers when doing any web research, URL fetching, or page content extraction — including during planning, exploration, or data source analysis.
---

# Web Search & Scraping MCP Tool Patterns

Reference for the MCP tools of 5 bundled servers — Firecrawl (27), Jina (12), Perplexity (4), Exa (2 default + 2 opt-in), Context7 (2) — plus REST recipes for Pexels and Unsplash media search. Use the routing table below to find the right tool for your task, then see the per-service reference files for detailed parameters.

## Tool names

The skills use the bare tool names (`read_url`, `firecrawl_scrape`, `resolve-library-id`). Because this plugin declares the servers in its own `.mcp.json`, Claude Code registers them as `mcp__plugin_web-search-dev_<server>__<tool>` — for example `mcp__plugin_web-search-dev_jina__read_url` or `mcp__plugin_web-search-dev_context7__resolve-library-id`. The server names are `firecrawl`, `exa`, `perplexity`, `jina`, `context7`.

## Tool Priority — ALWAYS prefer MCP tools over WebFetch

When MCP scraping/search tools from this plugin are available, they MUST be used instead of the built-in `WebFetch` tool. This applies to ALL web content operations — user-requested scraping, your own research, data source exploration, and planning phases.

**Priority order for reading a URL:**
1. `read_url` (Jina) — fastest, clean markdown, use first
2. `firecrawl_scrape` — if JS rendering needed or Jina fails
3. `WebFetch` — ONLY as last resort if all MCP tools are unavailable

**Priority order for web search:**
1. `web_search_exa` — semantic search, best for finding specific content
2. `perplexity_search` — AI-synthesized answers with citations
3. `firecrawl_search` — search + scrape in one step
4. `WebSearch` — ONLY as last resort if all MCP tools are unavailable

**Why:** MCP tools provide cleaner output, better JS rendering, structured extraction, and parallel operations. `WebFetch` is a basic fallback with limited capabilities that often fails on dynamic sites and rate-limits quickly.

## Quick Decision Guide

Pick a service based on what you need:

- **Need JS rendering / site crawling / structured extraction?** → **Firecrawl** (`firecrawl_scrape` with `formats: ["json"]`, `firecrawl_crawl`, `firecrawl_agent`)
- **Need fast page reading / batch operations / only the relevant passages?** → **Jina** `read_url` (up to 5 URLs, `question` for targeted passages)
- **Need semantic search?** → **Exa**
- **Need code examples / GitHub issues / dev docs?** → **Firecrawl** `firecrawl_developer_search`
- **Need AI-synthesized answer with citations?** → **Perplexity**
- **Need current framework docs?** → **Context7**
- **Need stock photos or videos?** → **Pexels** REST (photos + videos) or **Unsplash** REST (photos) — see `references/media-tools.md`
- **Need web images (not stock)?** → **Jina** `search_images` with `return_url: true`

## Task Routing Table

Pick the right tool by what you need to do:

| Task | Best Tool | Fallback | Service |
|------|-----------|----------|---------|
| **Search the web** | `web_search_exa` | `perplexity_search` → `search_web` → `firecrawl_search` | Exa / Perplexity / Jina / Firecrawl |
| **Read a single page** | `read_url` | `firecrawl_scrape` | Jina / Firecrawl |
| **Read multiple pages** | `read_url` with `url: [..up to 5..]` | Multiple `firecrawl_scrape` calls | Jina / Firecrawl |
| **Answer a question from a page** | `read_url` with `question` | `firecrawl_scrape` with `formats: ["query"]` | Jina / Firecrawl |
| **Crawl entire site** | `firecrawl_crawl` | `firecrawl_map` + batch scrape | Firecrawl |
| **Map site URLs** | `firecrawl_map` | — | Firecrawl |
| **Extract structured data (one URL)** | `firecrawl_scrape` with `formats: ["json"]` + `jsonOptions` | — | Firecrawl |
| **Structured data from unknown URLs / several sites** | `firecrawl_agent` + `firecrawl_agent_status` | `perplexity_research` | Firecrawl / Perplexity |
| **Typed provider data (companies, filings, prices)** | `firecrawl_search` with `sources: ["alexandria"]` → `firecrawl_find_tools` | `firecrawl_agent` | Firecrawl |
| **Search code examples / GitHub issues / dev docs** | `firecrawl_developer_search` | `web_search_advanced_exa` with `includeDomains: ["github.com"]` (opt-in) | Firecrawl / Exa |
| **AI-powered Q&A** | `perplexity_ask` | `perplexity_search` | Perplexity |
| **Deep research** | `perplexity_research` | `firecrawl_agent` | Perplexity / Firecrawl |
| **Reasoning/analysis** | `perplexity_reason` | — | Perplexity |
| **Search images** | `search_images` (`return_url: true`) | Pexels REST `/v1/search` → Unsplash REST `/search/photos` | Jina / Pexels / Unsplash |
| **Search videos** | Pexels REST `/v1/videos/search` | Pexels REST `/v1/videos/popular` | Pexels |
| **Take screenshot** | `capture_screenshot_url` | — | Jina |
| **Search framework docs** | `query-docs` | `perplexity_search` | Context7 / Perplexity |
| **Deduplicate content** | `deduplicate_strings` | — | Jina |
| **Rerank results** | `sort_by_relevance` | — | Jina |
| **Extract figures/tables/equations from a PDF** | `extract_pdf` | — | Jina |
| **Browser automation** | `firecrawl_interact` | `firecrawl_scrape` with `actions` | Firecrawl |
| **Autonomous research** | `firecrawl_agent` | `perplexity_research` | Firecrawl / Perplexity |
| **Monitor page changes** | `firecrawl_monitor_create` | — | Firecrawl |
| **Parse local files (PDF/DOCX/XLSX)** | `firecrawl_parse` | `read_url` for a PDF at a URL | Firecrawl / Jina |
| **Search academic papers** | `search_arxiv` (Jina) | `firecrawl_research_search_papers` | Jina / Firecrawl |
| **Multi-step research with structured output** | `agent_run` (Exa, needs API key) | `firecrawl_agent` | Exa / Firecrawl |
| **Check Firecrawl credits** | `firecrawl_credit_usage` | — | Firecrawl |
| **Fetch page via Exa** | `web_fetch_exa` | `read_url` | Exa / Jina |

## Service Overview

| Service | Tools | Strengths |
|---------|-------|-----------|
| **Firecrawl** | 27 | JS rendering, site crawling, structured extraction, live-page interaction, file parsing, change monitors, research/developer search, autonomous agent |
| **Jina** | 12 | Fast page reading with batch (up to 5 URLs) and question mode, web/academic/image search, reranking, deduplication, PDF extraction |
| **Perplexity** | 4 | AI-synthesized answers, deep research, reasoning with citations (`messages` input) |
| **Exa** | 2 default (+2 opt-in) | Semantic search, page fetching, advanced filters, Exa Agent (`agent_run`) |
| **Context7** | 2 | Up-to-date framework/library documentation |
| **Pexels** | REST | Stock photos and videos with licensing |
| **Unsplash** | REST | High-quality stock photos (API guidelines apply) |

## Quick Usage Examples

### Search and read a page

```
Step 1 — Search:
Tool: web_search_exa
Input: { "query": "Next.js 15 server actions guide", "numResults": 5 }

Step 2 — Read the best result:
Tool: read_url
Input: { "url": "<best_url_from_step_1>" }
```

### Extract structured data from a product page

```
Tool: firecrawl_scrape
Input: {
  "url": "https://example.com/products/item-1",
  "formats": ["json"],
  "jsonOptions": {
    "prompt": "Extract product name, price, and description",
    "schema": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "price": { "type": "number" },
        "description": { "type": "string" }
      }
    }
  }
}
```

### Read only the relevant passages of several pages

```
Tool: read_url
Input: {
  "url": ["https://docs.example.com/limits", "https://docs.example.com/pricing"],
  "question": "What are the default rate limits?"
}
```

### Find stock photos for an app (REST)

```bash
curl -s -H "Authorization: ${PEXELS_API_KEY}" \
  "https://api.pexels.com/v1/search?query=modern+office+workspace&per_page=10&orientation=landscape"
```

## Per-Service Tool References

For complete tool parameters and advanced usage, see the service-specific references:

- `references/firecrawl-tools.md` — 27 tools: scrape, search, crawl, map, parse, agent, interact, monitors, research, developer search, Alexandria, credit usage
- `references/exa-tools.md` — 2 default tools (web_search, web_fetch) + opt-in advanced search and `agent_run`
- `references/perplexity-tools.md` — 4 tools: search, ask, research, reason (`messages` input)
- `references/jina-tools.md` — 12 tools: read, search, images, screenshot, rerank, deduplicate, PDF, utility
- `references/media-tools.md` — Pexels and Unsplash REST (curl), rate limits, Unsplash API checklist
- `references/context7-tools.md` — 2 tools: `resolve-library-id` (needs `query` + `libraryName`), `query-docs`
