# OnPage Tools

3 tools for page-level auditing, performance analysis, and content extraction. All prefixed with `mcp__dataforseo__`.

## Tool Reference

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `on_page_lighthouse` | Run a Google Lighthouse audit on a URL | `url` (required), `enable_javascript`, `custom_user_agent`, `accept_language`, `full_data` |
| `on_page_instant_pages` | Get instant page analysis with SEO metrics | `url` (required), `enable_javascript`, `custom_user_agent`, `accept_language`, `custom_js` |
| `on_page_content_parsing` | Extract and parse page content | `url` (required), `enable_javascript`, `custom_user_agent`, `accept_language` |

## Parameter Details

### Common Parameters

- `url` -- full URL to analyze, including protocol. Example: `"https://example.com/page"`.
- `enable_javascript` -- boolean. Set `true` for JavaScript-rendered pages (SPAs, React apps). Default `false`.
- `custom_user_agent` -- override the user agent string. Useful for testing mobile rendering.
- `accept_language` -- set the Accept-Language header. Example: `"en-US"`, `"de-DE"`.

### Tool-Specific Parameters

- `full_data` (Lighthouse only) -- boolean. When `true`, returns the complete Lighthouse report with all audits and metrics. Default `false` returns a summary.
- `custom_js` (instant_pages only) -- string of JavaScript to execute on the page before analysis. Useful for triggering lazy-loaded content or closing modals.

## What Each Tool Returns

### on_page_lighthouse

Returns Core Web Vitals (LCP, FID, CLS, TTFB), performance score, accessibility score, SEO score, and best practices score. With `full_data: true`, includes individual audit results with recommendations.

### on_page_instant_pages

Returns page-level SEO metrics: title, meta description, H1-H6 tags, word count, internal/external links, images with alt text status, canonical URL, status code, and load time.

### on_page_content_parsing

Returns the extracted text content, structured data (JSON-LD, microdata), Open Graph tags, meta tags, and the page's plain text content stripped of HTML.

## Usage Examples

### Run a full page audit

```
Step 1 -- Tool: mcp__dataforseo__on_page_lighthouse
Params:
  url: "https://example.com"
  enable_javascript: true
  full_data: true

Step 2 -- Tool: mcp__dataforseo__on_page_instant_pages
Params:
  url: "https://example.com"
  enable_javascript: true
```

Combine Lighthouse (performance/accessibility) with instant_pages (on-page SEO elements) for a complete picture.

### Extract content for analysis

```
Tool: mcp__dataforseo__on_page_content_parsing
Params:
  url: "https://example.com/blog/article"
  enable_javascript: false
```

Use this to extract structured content for competitor analysis, content gap identification, or schema markup review.

## Tips

- Always set `enable_javascript: true` for modern SPAs and JavaScript-heavy sites.
- Lighthouse with `full_data: true` is expensive. Use the summary mode first, then drill into full data only when needed.
- `on_page_content_parsing` is the fastest and cheapest of the three -- use it when you only need content, not performance metrics.
- These tools analyze one URL per call. For site-wide audits, combine with SERP or Labs tools to discover key pages first, then audit them individually.
