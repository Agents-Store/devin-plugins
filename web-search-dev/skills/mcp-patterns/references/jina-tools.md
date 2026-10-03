# Jina MCP Tools (12 tools)

Jina provides a "Search Foundation" platform behind one remote MCP endpoint (`https://mcp.jina.ai/v1`, Streamable HTTP). One API key works across all tools. Strongest at **page reading, concurrent batch calls, and text re-ranking**.

The server exposes exactly 12 tools (reduced from 21 on 2026-09-18). Batching is built in: `read_url` takes up to 5 URLs in `url`, and `search_web`, `search_arxiv`, `search_ssrn`, `search_jina_blog` take up to 5 queries in `query` — an array runs every item concurrently in one round trip. `search_images` takes one query at a time.

| Group | Tools |
|-------|-------|
| Read (tag `read`) | `read_url`, `capture_screenshot_url` |
| Search (tag `search`) | `search_web`, `search_arxiv`, `search_ssrn`, `search_images`, `search_jina_blog` |
| Rerank (tag `rerank`) | `sort_by_relevance`, `deduplicate_strings` |
| Utility (tag `utility`) | `primer`, `guess_datetime_url`, `extract_pdf` |

## Reading

### read_url
Fetch a page or PDF as clean markdown. **Pass `question` to get only the passages that answer it** — far cheaper than reading the whole body into context.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string or string[] | Yes | One URL, or up to 5 URLs read in parallel |
| `question` | string | No | Return only the passages answering this question |
| `topk` | integer | No | Passages to return (1-50, default 1; needs `question`) |
| `chunk_size` | integer | No | Passage size in words (1-4096, default 100; needs `question`) |
| `ocr` | boolean | No | Read the rendered page as an image (scans, formulas, tables) — about 40x the tokens, one page per call |
| `page` | integer | No | Page to OCR (1-based; needs `ocr`) |
| `withAllLinks` | boolean | No | Also return every link on the page |
| `withAllImages` | boolean | No | Also return every image on the page |

```
Tool: read_url
Input: { "url": "https://nextjs.org/docs/getting-started" }
```

Targeted read (cheap):

```
Tool: read_url
Input: {
  "url": ["https://docs.example.com/limits", "https://docs.example.com/pricing"],
  "question": "What are the default rate limits?",
  "topk": 3
}
```

Works without an API key at a low rate limit (reader 20 RPM); with a key 500 RPM.

**Response size guard.** Claude Code and similar clients reject MCP tool responses above ~25k tokens, so the server truncates `read_url` output to fit and appends a `[jina-mcp] ...` note when it cut something. Prefer `question` for long pages, or raise the budget with `?max_tokens=50000` on the endpoint URL (`max_tokens=0` disables truncation).

### capture_screenshot_url
Screenshot a page when it must be seen rather than read.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | URL to capture |
| `firstScreenOnly` | boolean | No | First screen only (faster; default `false`) |
| `return_url` | boolean | No | Return URLs instead of base64 images (default `false`) |

By default the tool returns **base64 JPEG**, which fills the context quickly — pass `"return_url": true` unless you need the pixels.

## Search

### search_web
Search the web. Returns titles, URLs and engine snippets; read the chosen pages with `read_url` + `question`. A snippet is not a source for exact values — verify version numbers and commands on the page.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string or string[] | Yes | One query, or up to 5 queries run concurrently |
| `num` | integer | No | Results (1-100, default 30) |
| `gl` / `hl` | string | No | Country code / language code (e.g. `de`, `zh-cn`) |
| `location` | string | No | Geographic location |
| `tbs` | string | No | Age limit: `qdr:h`, `qdr:d`, `qdr:w`, `qdr:m`, `qdr:y` |

```
Tool: search_web
Input: {
  "query": ["Next.js app router middleware", "Next.js authentication patterns", "Next.js caching strategies"],
  "num": 10
}
```

### search_images
Search the web for images. **Returns base64 JPEGs by default — always pass `"return_url": true`** to get URLs and metadata instead.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Image search query (one at a time) |
| `num` | integer | No | Results (1-30, default 10) |
| `return_url` | boolean | No | Return URLs and metadata instead of base64 (default `false`) |
| `gl` / `hl` / `location` / `tbs` | string | No | Same as `search_web` |

```
Tool: search_images
Input: { "query": "modern dashboard UI design", "num": 10, "return_url": true }
```

### search_arxiv / search_ssrn / search_jina_blog
`search_arxiv` — arXiv preprints (physics, maths, CS, quantitative biology and finance). `search_ssrn` — SSRN working papers (social science, economics, law, finance, management). `search_jina_blog` — Jina AI news and blog posts (product announcements, model releases).

Each takes `query` (string or up to 5 strings), `num` (1-100, default 30) and `tbs`.

## Utility

### primer
Current time, user location and network environment. Call it before answering anything time- or location-dependent. No parameters.

### guess_datetime_url
Guess when a page was published or last updated, with a confidence score (HTTP headers, metadata, Schema.org, visible dates, feeds, sitemaps).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | URL to analyse |

### extract_pdf
Extract figures, tables and equations from a PDF as images, by arXiv id or URL.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | one of `id`/`url` | arXiv id, e.g. `2301.12345` |
| `url` | string | one of `id`/`url` | PDF URL |
| `type` | string | No | Comma-separated: `figure`, `table`, `equation` (default all) |
| `max_edge` | number | No | Longest image edge in px (default 1024) |

## Text processing

### sort_by_relevance
Rerank documents by relevance to a query with Jina Reranker.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Relevance query |
| `documents` | string[] | Yes | Up to 1024 documents |
| `top_n` | integer | No | Keep the best N |

### deduplicate_strings
Select the top-k semantically distinct strings, dropping near-duplicates.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `strings` | string[] | Yes | Up to 1000 strings |
| `k` | integer | No | How many to keep (omitted: chosen automatically) |

There are no MCP tools for classification, query expansion, image de-duplication or BibTeX search — use the model itself, or the REST classifier (see `api-reference`).

## Server-side tool filtering

Every registered tool costs context tokens for its name, description and schema, whether or not it is called. Filter on the endpoint URL (`https://mcp.jina.ai/v1?...`) so the client never sees unwanted tools:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `include_tools` / `exclude_tools` | Comma-separated tool names | `exclude_tools=search_ssrn,search_images` |
| `include_tags` / `exclude_tags` | Comma-separated tags (`search`, `read`, `utility`, `rerank`) | `include_tags=search,read` |
| `max_tokens` | Cap `read_url` response size in tokens (`0` disables) | `max_tokens=50000` |

Precedence: `exclude_tools`, then `exclude_tags`, then `include_tools`, then `include_tags`. To use a filter, register your own Jina MCP entry with the filtered URL instead of the bundled one.

## Rate Limits

Limits differ by product — reader (`r.jina.ai`) and search (`s.jina.ai`) have separate tiers:

| Tier | Reader RPM | Search RPM |
|------|------------|------------|
| No key | 20 | — (search requires a key) |
| With key | 500 | 100 |
| Premium | 5,000 | 1,000 |
