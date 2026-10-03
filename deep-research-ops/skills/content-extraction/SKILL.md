---
name: content-extraction
description: Content reading and extraction guidelines — reading URLs, scraping pages, crawling sites, extracting PDFs, and taking screenshots. Use when reading web content, extracting structured data from pages, or processing documents.
---

# Content Extraction

Reading and extracting content from web pages, PDFs, and entire sites. All calls use `~~capability` with fallback (see CONNECTORS.md).

## Reading a Single URL — `~~scrape`

### Fallback chain:
```
1. Jina read_url — fast, clean markdown (pages and PDFs)
2. Firecrawl scrape — JS rendering, advanced options
3. Exa fetch (pass maxCharacters: 20000 — the default is 3000 per page) — last resort
On error → next provider.
```

### Basic usage:
```
~~scrape("https://example.com/article")
→ Returns clean markdown content
```

### Cheap mode — only the relevant passages:
```
~~scrape(url, question: "What are the default rate limits?", topk: 3)
→ Returns only the passages that answer the question, not the whole page
   (Jina read_url question/topk; fallback: Firecrawl scrape in "query" format)
```
Use it by default in READ. Read in full when you need exact quotes or tables, or the passages were not enough.

### For JS-heavy pages:
```
If ~~scrape returns empty, try provider with waitFor/JS rendering support.
```

## Reading Multiple URLs — `~~batch_scrape`

### Fallback chain:
```
1. Jina read_url with an array — up to 5 URLs in one call
2. Exa fetch with several URLs in one call (maxCharacters: 20000; default is 3000 per page)
3. Sequential ~~scrape per URL individually
```
More than 5 URLs → split into batches of 5. Only the Jina call honours `question`; the fallbacks return full pages, so select the passages yourself (or use the Firecrawl "query" format per URL).

### Workflow: search → rank → read
```
1. ~~search(query) → list of URLs
2. Rank by relevance → top-5
3. ~~batch_scrape(top_5_urls) → content
```

## Crawling a Site — `~~crawl`

### Fallback chain:
```
1. Firecrawl crawl — waits for the crawl to finish and returns the data
   (check-status only to pick up a crawl started earlier or cut off)
2. Firecrawl map → list of URLs, then ~~batch_scrape(selected_urls)
```

### With filtering:
```
Crawl with limit, includePaths, excludePaths to control scope.
```

## Structured Data Extraction — `~~extract`

### Fallback chain:
```
1. Firecrawl scrape in "json" format with a prompt and schema — one URL per call
2. Firecrawl agent — when the URLs are not known or the data is spread across sites
3. ~~scrape, then extract the fields yourself
```

### With JSON schema (known URL):
```
~~extract(url, prompt, schema) → structured data matching your schema
→ repeat for each URL
```

### Unknown URLs or several sites:
```
1. Start the agent with a prompt, optional seed URLs, schema and a credit limit → job id
2. Poll the job every 15-30 seconds until "completed" or "failed" (1-3 minutes)
```
The agent spends credits — always set a limit.

## Browser Sessions

For dynamic pages requiring interaction (Firecrawl only):
```
1. Open a page with a natural-language instruction → scrapeId
2. Follow up on the same scrapeId (navigate, click, type)
3. Stop the session
```
The session acts on the live site — form submissions have side effects.

## PDF Processing

```
Text of a PDF: ~~scrape(pdf_url) — read_url and Firecrawl scrape both read PDFs.
Figures, tables, equations: PDF extraction (by arXiv id or URL) returns them as images.
Papers from the paper index: ~~academic_search read-paper step returns the passages
that answer a question.
```

## Autonomous Research Agent

For complex multi-step research — the `~~deep_agent` capability (see CONNECTORS.md):
```
1. Start the agent with a prompt and optional URLs → job id
2. Poll the job every 15-30 seconds until "completed" (typically 1-3 minutes)
```

## Utility Tools

| Tool | Purpose |
|------|---------|
| Screenshot | Capture a webpage for visual reports (ask for URLs, not base64 images) |
| Date detection | Detect page publication date for freshness |

## Best Practices

1. **Always start with ~~scrape** — uses fallback chain automatically
2. **JS-heavy pages** — use provider with waitFor/JS rendering
3. **3+ URLs** — use ~~batch_scrape for parallel reading
4. **Large sites** — ~~crawl with limit and depth
5. **PDFs** — use PDF extraction for academic papers
6. **Structured data** — ~~extract with JSON schema
7. **Check dates** — detect page date to filter stale content
8. **Browser sessions** — only for SPA, always stop the session after use
9. **Long pages** — pass a `question` to read only the relevant passages

## Common Errors

| Error | Fix |
|-------|-----|
| Empty content | Try next provider in fallback chain |
| Timeout | Try lighter alternative (map instead of crawl) |
| 403 Forbidden | Try provider with proxy/stealth support |
| PDF extraction failed | Check URL, try ~~scrape instead |
| Crawl stuck | Set limit and depth, or use map + batch_scrape |
