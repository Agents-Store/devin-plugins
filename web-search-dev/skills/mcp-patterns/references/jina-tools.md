# Jina MCP Tools (21 tools)

Jina provides a unified "Search Foundation" platform. One API key works across all tools. Strongest at **page reading, parallel operations, and text processing**.

## Reading

### read_url
Extract clean markdown from any web page.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | URL to read |

```
Tool: read_url
Input: { "url": "https://nextjs.org/docs/getting-started" }
```

Works without API key (20 RPM limit). With key: 500 RPM.

### parallel_read_url
Read multiple URLs simultaneously.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `urls` | string[] | Yes | URLs to read in parallel |

```
Tool: parallel_read_url
Input: { "urls": [
  "https://docs.example.com/page1",
  "https://docs.example.com/page2",
  "https://docs.example.com/page3"
]}
```

## Search

### search_web
Search the entire web.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query |
| `num` | integer | No | Number of results |

```
Tool: search_web
Input: { "query": "React hooks best practices", "num": 10 }
```

### parallel_search_web
Run multiple web searches simultaneously.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `queries` | string[] | Yes | Multiple search queries |

```
Tool: parallel_search_web
Input: { "queries": [
  "Next.js app router middleware",
  "Next.js authentication patterns",
  "Next.js caching strategies"
]}
```

### search_images
Search for images across the web.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Image search query |
| `num` | integer | No | Number of results |

```
Tool: search_images
Input: { "query": "modern dashboard UI design", "num": 10 }
```

### search_arxiv
Search academic papers on arXiv.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Academic search query |
| `num` | integer | No | Number of results |

### parallel_search_arxiv
Multiple arXiv searches simultaneously.

### search_ssrn
Search SSRN academic papers.

### parallel_search_ssrn
Multiple SSRN searches simultaneously.

### search_jina_blog
Search Jina AI news and blog posts.

### search_bibtex
Search for BibTeX citations (DBLP + Semantic Scholar).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Paper or author query |

## Utility Tools

### capture_screenshot_url
Capture screenshots of web pages.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | URL to screenshot |

### guess_datetime_url
Analyze a page for its publish/update datetime.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | URL to analyze |

### extract_pdf
Extract figures, tables, and equations from PDF documents.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | PDF URL |

### expand_query
Expand and rewrite search queries for better results.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Query to expand |

```
Tool: expand_query
Input: { "query": "react state management" }
```

Returns multiple expanded queries for broader search coverage.

## Text Processing

### classify_text
Classify text into user-defined labels (zero-shot).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `texts` | string[] | Yes | Texts to classify |
| `labels` | string[] | Yes | Classification labels |

```
Tool: classify_text
Input: {
  "texts": ["This product is amazing!", "Terrible experience"],
  "labels": ["positive", "negative", "neutral"]
}
```

### sort_by_relevance
Rerank documents by relevance to a query.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Relevance query |
| `documents` | string[] | Yes | Documents to rerank |

### deduplicate_strings
Get semantically unique strings from a list.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `strings` | string[] | Yes | Strings to deduplicate |

### deduplicate_images
Get semantically unique images from a list.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `images` | string[] | Yes | Image URLs to deduplicate |

## Context

### primer
Get contextual information about the current session (time, location, network).

No parameters required.

### show_api_key
Return the API key configured for the current session.

No parameters required.

## Rate Limits

Limits differ by product — reader (`r.jina.ai`) and search (`s.jina.ai`) have separate tiers:

| Tier | Reader RPM | Search RPM |
|------|------------|------------|
| No key | 20 | — (search requires a key) |
| With key | 500 | 100 |
| Premium | 5,000 | 1,000 |
