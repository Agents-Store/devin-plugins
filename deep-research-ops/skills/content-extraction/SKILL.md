---
name: content-extraction
description: Content reading and extraction guidelines — reading URLs, scraping pages, crawling sites, extracting PDFs, and taking screenshots. Use when reading web content, extracting structured data from pages, or processing documents.
---

# Content Extraction

Reading and extracting content from web pages, PDFs, and entire sites. All calls use `~~capability` with fallback (see CONNECTORS.md).

## Reading a Single URL — `~~scrape`

### Fallback chain:
```
1. Jina — fast, clean markdown
2. Firecrawl — JS rendering, advanced options
On error → next provider.
```

### Basic usage:
```
~~scrape("https://example.com/article")
→ Returns clean markdown content
```

### For JS-heavy pages:
```
If ~~scrape returns empty, try provider with waitFor/JS rendering support.
```

## Reading Multiple URLs — `~~batch_scrape`

### Fallback chain:
```
1. Jina parallel — batch all URLs at once
2. Sequential ~~scrape per URL individually
```

### Workflow: search → rank → read
```
1. ~~search(query) → list of URLs
2. Rank by relevance → top-5
3. ~~batch_scrape(top_5_urls) → content
```

## Crawling a Site — `~~crawl`

### Fallback chain:
```
1. Firecrawl crawl → crawl_id, then poll status until "completed"
2. Firecrawl map → list of URLs, then ~~batch_scrape(selected_urls)
```

### With filtering:
```
Crawl with limit, includePaths, excludePaths to control scope.
```

## Structured Data Extraction — `~~extract`

### Fallback chain:
```
1. Firecrawl extract — LLM extraction with JSON schema
2. Firecrawl scrape with JSON options
```

### With JSON schema:
```
~~extract(urls, prompt, schema) → structured data matching your schema
```

## Browser Sessions

For dynamic pages requiring interaction (Firecrawl only):
```
1. Create browser session → session_id
2. Execute browser actions (navigate, click, type, screenshot)
3. Delete browser session
```

## PDF Processing

```
Extract figures, tables, equations from PDF documents.
Useful for academic papers from arXiv or any PDF URL.
```

## Autonomous Research Agent

For complex multi-step research (Firecrawl only):
```
1. Start agent with prompt and optional URLs → agent_id
2. Poll agent status until "completed" (may take 1-5 minutes)
```

## Utility Tools

| Tool | Purpose |
|------|---------|
| Screenshot | Capture a webpage for visual reports |
| Date detection | Detect page publication date for freshness |

## Best Practices

1. **Always start with ~~scrape** — uses fallback chain automatically
2. **JS-heavy pages** — use provider with waitFor/JS rendering
3. **3+ URLs** — use ~~batch_scrape for parallel reading
4. **Large sites** — ~~crawl with limit and depth
5. **PDFs** — use PDF extraction for academic papers
6. **Structured data** — ~~extract with JSON schema
7. **Check dates** — detect page date to filter stale content
8. **Browser sessions** — only for SPA, always delete session after use

## Common Errors

| Error | Fix |
|-------|-----|
| Empty content | Try next provider in fallback chain |
| Timeout | Try lighter alternative (map instead of crawl) |
| 403 Forbidden | Try provider with proxy/stealth support |
| PDF extraction failed | Check URL, try ~~scrape instead |
| Crawl stuck | Set limit and depth, or use map + batch_scrape |
