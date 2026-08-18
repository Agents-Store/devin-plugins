---
name: mcp-patterns
description: This skill should be used when the user asks about "web search MCP tools", "which search tools are available", "firecrawl tools", "exa tools", "jina tools", "perplexity tools", "how to use search MCP", "scraping MCP tools", "media search tools", or needs to know which MCP operations are available across web search and scraping services. Also triggers when doing any web research, URL fetching, or page content extraction — including during planning, exploration, or data source analysis.
---

# Web Search & Scraping MCP Tool Patterns

Reference for all available MCP tools across 7 services (65+ tools total). Use the routing table below to find the right tool for your task, then see the per-service reference files for detailed parameters.

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

- **Need JS rendering / site crawling / structured extraction?** → **Firecrawl**
- **Need fast page reading / batch operations?** → **Jina**
- **Need semantic search?** → **Exa**
- **Need code examples / GitHub issues / dev docs?** → **Firecrawl** `firecrawl_developer_search`
- **Need AI-synthesized answer with citations?** → **Perplexity**
- **Need current framework docs?** → **Context7**
- **Need stock photos or videos?** → **Pexels** (photos+videos) or **Unsplash** (photos)
- **Need web images (not stock)?** → **Jina** `search_images`

## Task Routing Table

Pick the right tool by what you need to do:

| Task | Best Tool | Fallback | Service |
|------|-----------|----------|---------|
| **Search the web** | `web_search_exa` | `perplexity_search` → `search_web` → `firecrawl_search` | Exa / Perplexity / Jina / Firecrawl |
| **Read a single page** | `read_url` | `firecrawl_scrape` | Jina / Firecrawl |
| **Read multiple pages** | `parallel_read_url` | Multiple `firecrawl_scrape` calls | Jina / Firecrawl |
| **Crawl entire site** | `firecrawl_crawl` | `firecrawl_map` + batch scrape | Firecrawl |
| **Map site URLs** | `firecrawl_map` | — | Firecrawl |
| **Extract structured data** | `firecrawl_extract` | `firecrawl_scrape` with jsonOptions | Firecrawl |
| **Search code examples** | `firecrawl_developer_search` | `web_search_advanced_exa` with `includeDomains: ["github.com"]` (opt-in) | Firecrawl / Exa |
| **AI-powered Q&A** | `perplexity_ask` | `perplexity_search` | Perplexity |
| **Deep research** | `perplexity_research` | `firecrawl_agent` | Perplexity / Firecrawl |
| **Reasoning/analysis** | `perplexity_reason` | — | Perplexity |
| **Search images** | `search_images` | `searchPhotos` (Pexels) → `get_search_photos` (Unsplash) | Jina / Pexels / Unsplash |
| **Search videos** | `searchVideos` | `getPopularVideos` | Pexels |
| **Take screenshot** | `capture_screenshot_url` | — | Jina |
| **Search framework docs** | `query-docs` | `perplexity_search` | Context7 / Perplexity |
| **Classify text** | `classify_text` | — | Jina |
| **Deduplicate content** | `deduplicate_strings` | — | Jina |
| **Rerank results** | `sort_by_relevance` | — | Jina |
| **Extract from PDF** | `extract_pdf` | — | Jina |
| **Browser automation** | `firecrawl_interact` | `firecrawl_scrape` with `actions` | Firecrawl |
| **Autonomous research** | `firecrawl_agent` | `perplexity_research` | Firecrawl / Perplexity |
| **Monitor page changes** | `firecrawl_monitor_create` | — | Firecrawl |
| **Parse files (PDF/DOCX)** | `firecrawl_parse` | `extract_pdf` (Jina) | Firecrawl / Jina |
| **Search academic papers** | `search_arxiv` (Jina) | `firecrawl_research_search_papers` | Jina / Firecrawl |
| **Search GitHub** | `firecrawl_research_search_github` | `web_search_advanced_exa` + github.com domain | Firecrawl / Exa |
| **Fetch page via Exa** | `web_fetch_exa` | `read_url` | Exa / Jina |

## Service Overview

| Service | Tools | Strengths |
|---------|-------|-----------|
| **Firecrawl** | 27 | JS rendering, site crawling, structured extraction, live-page interaction, file parsing, change monitors, research/developer search, autonomous agent |
| **Jina** | 21 | Fast page reading, parallel operations, image search, text classification, deduplication, PDF extraction |
| **Perplexity** | 4 | AI-synthesized answers, deep research, reasoning with citations |
| **Exa** | 2 default (+2 optional via remote MCP) | Semantic search, page fetching, category filtering |
| **Pexels** | 9 | Stock photos and videos with licensing |
| **Unsplash** | 4 | High-quality stock photos |
| **Context7** | 2 | Up-to-date framework/library documentation |

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
Tool: firecrawl_extract
Input: {
  "urls": ["https://example.com/products"],
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
```

### Find stock photos for an app

```
Tool: searchPhotos
Input: { "query": "modern office workspace", "per_page": 10, "orientation": "landscape" }
```

## Per-Service Tool References

For complete tool parameters and advanced usage, see the service-specific references:

- `references/firecrawl-tools.md` — 27 tools: scrape, search, crawl, map, extract, parse, agent, interact, monitors, research, developer search
- `references/exa-tools.md` — 2 default tools (web_search, web_fetch) + optional advanced search / agent via remote MCP
- `references/perplexity-tools.md` — 4 tools: search, ask, research, reason
- `references/jina-tools.md` — 21 tools: read, search, images, parallel, classify, deduplicate, PDF
- `references/media-tools.md` — 13 tools: Pexels photos/videos + Unsplash photos
- `references/context7-tools.md` — 2 tools: `resolve-library-id`, `query-docs`
