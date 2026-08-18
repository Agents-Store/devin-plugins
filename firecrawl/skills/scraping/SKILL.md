---
name: scraping
description: Single URL scraping — formats, selectors, wait strategies, headers. This skill should be used when the user asks to scrape a web page, get content from a URL, convert a page to markdown, or extract text from a site.
---

# URL Scraping

This skill covers scraping single URLs with Firecrawl — output formats, content selection, wait strategies, and authentication.

## Available Tools

| Tool | Description |
|------|-------------|
| `scrape_url` | Scrape a single URL and return content |

## Basic Scraping

```
Tool: scrape_url
Input: {
  "url": "https://example.com/page",
  "formats": ["markdown"]
}

Returns: Page content in specified format with metadata (title, description, status code).
```

## Output Formats

| Format | Description | Best For |
|--------|-------------|----------|
| markdown | Clean text with formatting | Content analysis, LLM processing |
| html | Cleaned HTML | Structure preservation |
| rawHtml | Complete HTML source | Full page with scripts/styles |
| screenshot | Page screenshot | Visual inspection |
| links | All links on page | URL discovery |

### Multiple Formats
```
Tool: scrape_url
Input: {
  "url": "https://example.com",
  "formats": ["markdown", "links"]
}
```

## Content Selection

### Include Only Specific Elements
```
Tool: scrape_url
Input: {
  "url": "https://example.com/article",
  "formats": ["markdown"],
  "includeTags": ["article", "main", ".content"]
}
```

### Exclude Elements
```
Tool: scrape_url
Input: {
  "url": "https://example.com/article",
  "formats": ["markdown"],
  "excludeTags": ["nav", "footer", ".sidebar", ".ads"]
}
```

## Advanced Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `onlyMainContent` | boolean | Extract only main content, strip boilerplate (default: true) |
| `mobile` | boolean | Render page as mobile device |
| `prompt` | string | LLM prompt to extract specific info during scrape |
| `schema` | object | JSON schema for structured extraction during scrape |
| `skipTlsVerification` | boolean | Skip TLS certificate verification |

### Main Content Only
```
Tool: scrape_url
Input: {
  "url": "https://example.com/article",
  "formats": ["markdown"],
  "onlyMainContent": true
}
```

### Mobile Rendering
```
Tool: scrape_url
Input: {
  "url": "https://example.com/page",
  "formats": ["markdown"],
  "mobile": true
}
```

### LLM-Powered Extraction During Scrape
```
Tool: scrape_url
Input: {
  "url": "https://example.com/pricing",
  "formats": ["markdown"],
  "prompt": "Extract the pricing information and plan details"
}
```

### Structured Extraction During Scrape
```
Tool: scrape_url
Input: {
  "url": "https://example.com/product",
  "formats": ["markdown"],
  "schema": {
    "type": "object",
    "properties": {
      "name": { "type": "string" },
      "price": { "type": "number" }
    }
  }
}
```

## Wait Strategies

For pages with dynamic content (JavaScript-rendered):

### Wait for Selector
```
Tool: scrape_url
Input: {
  "url": "https://example.com/spa",
  "formats": ["markdown"],
  "waitFor": ".product-list"
}
```

### Wait for Fixed Time (ms)
```
Tool: scrape_url
Input: {
  "url": "https://example.com/slow-page",
  "formats": ["markdown"],
  "timeout": 30000
}
```

## Headers and Cookies

### Custom Headers
```
Tool: scrape_url
Input: {
  "url": "https://example.com/api-docs",
  "formats": ["markdown"],
  "headers": {
    "Authorization": "Bearer token123",
    "Accept-Language": "en-US"
  }
}
```

## Common Workflows

### Scrape and Analyze Content
```
1. scrape_url(url, formats=["markdown"]) -> Get clean text
2. Analyze content (summarize, extract key points, etc.)
```

### Scrape with Link Discovery
```
1. scrape_url(url, formats=["markdown", "links"]) -> Get content + all links
2. Filter links matching pattern
3. Scrape specific linked pages
```

### Scrape Authenticated Page
```
1. scrape_url(url, headers={Authorization: "Bearer ..."}) -> Get protected content
```

## Error Handling Patterns

### Common Failure Scenarios
- **URL unreachable** → verify URL is accessible; check for typos, DNS issues, or geo-blocking
- **Timeout** → increase `timeout` parameter, or switch to async batch scrape for slow pages
- **Rate limited (429)** → add delays between requests; reduce concurrency
- **Content blocked** → try `mobile: true` for mobile rendering, or set custom `headers` (User-Agent)
- **Empty content** → page may require JavaScript; use `waitFor` with a CSS selector that appears after load
- **Authentication required** → use `headers` with auth tokens, or use browser sessions for login flows

### Defensive Workflow
1. Start with a single `scrape_url` to test if the page is accessible
2. If empty content: add `waitFor` parameter with a page-specific selector
3. If blocked: try with `mobile: true` or custom User-Agent header
4. For many URLs: switch to `batch_scrape` (see batch-operations skill)
5. For authenticated pages: use browser sessions (see browser-sessions skill)

## Best Practices

1. **Use markdown format by default** — cleanest output for analysis
2. **Exclude nav/footer** — focus on main content with excludeTags
3. **Use waitFor for SPAs** — dynamic pages need time to render
4. **Check status codes** — verify page loaded successfully
5. **Respect rate limits** — don't scrape too many pages too fast
6. **Use includeTags for precision** — target specific page sections
