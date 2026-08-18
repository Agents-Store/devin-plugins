# Firecrawl MCP Tools (27 tools)

Keyless free tier exposes scrape, search, and parse (plus interact per the npm README) with usage limits. The full tool set requires an API key.

## Scraping

### firecrawl_scrape
Scrape a single URL and extract content in multiple formats.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | URL to scrape |
| `formats` | array | No | String formats: `markdown`, `html`, `rawHtml`, `links`, `summary`, `images`; object formats: `{ "type": "json", "prompt", "schema" }`, `{ "type": "screenshot", "fullPage", "quality", "viewport" }`, `changeTracking` |
| `onlyMainContent` | boolean | No | Extract only main content (default: true) |
| `waitFor` | integer | No | Wait for JS rendering (ms) |
| `includeTags` | string[] | No | Only include these HTML tags |
| `excludeTags` | string[] | No | Exclude these HTML tags |
| `maxAge` | integer | No | Cache tolerance in ms (default: 2 days — set `0` for a fresh scrape) |
| `parsers` | array | No | File parsers, e.g. `[{ "type": "pdf" }]` |
| `actions` | array | No | Page interactions: click, type, scroll, wait, screenshot |

```
Tool: firecrawl_scrape
Input: {
  "url": "https://example.com/page",
  "formats": ["markdown", "links"],
  "onlyMainContent": true
}
```

### firecrawl_search
Search the web and optionally scrape results.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query |
| `limit` | integer | No | Max results (default: 5) |
| `sources` | array | No | Result sources: `web`, `news`, `images` |
| `lang` | string | No | Language code |
| `country` | string | No | Country code |
| `scrapeOptions` | object | No | Options for scraping each result |
| `tbs` | string | No | Time filter |
| `location` | string | No | Geographic location |

```
Tool: firecrawl_search
Input: {
  "query": "Next.js server components tutorial",
  "limit": 10
}
```

## Crawling

### firecrawl_crawl
Start an async crawl of an entire website.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | Starting URL |
| `limit` | integer | No | Max pages to crawl |
| `maxDiscoveryDepth` | integer | No | Max link-discovery depth |
| `prompt` | string | No | Natural-language crawl config — Firecrawl derives crawler options from it |
| `sitemap` | string | No | `skip`, `include`, or `only` |
| `crawlEntireDomain` | boolean | No | Crawl the whole domain, not just child paths |
| `includePaths` | string[] | No | Only crawl matching paths |
| `excludePaths` | string[] | No | Skip matching paths |
| `allowSubdomains` | boolean | No | Include subdomains |
| `scrapeOptions` | object | No | Options for each scraped page |

Returns a `jobId` — check status with `firecrawl_check_crawl_status`.

```
Tool: firecrawl_crawl
Input: {
  "url": "https://docs.example.com",
  "limit": 50,
  "maxDiscoveryDepth": 3,
  "includePaths": ["/docs/*"]
}
```

### firecrawl_check_crawl_status
Poll a crawl job for results.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Crawl job ID from firecrawl_crawl |

### firecrawl_map
Discover all URLs on a website (fast, no content extraction).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | Website URL |
| `limit` | integer | No | Max URLs to return |
| `includeSubdomains` | boolean | No | Include subdomains |
| `search` | string | No | Filter URLs by keyword |

```
Tool: firecrawl_map
Input: { "url": "https://example.com", "limit": 100 }
```

## Extraction

### firecrawl_extract
Extract structured data from web pages using LLM.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `urls` | string[] | Yes | URLs to extract from |
| `prompt` | string | No | Natural language extraction instructions |
| `schema` | object | No | JSON schema for output structure |
| `enableWebSearch` | boolean | No | Allow web search to find additional data |

```
Tool: firecrawl_extract
Input: {
  "urls": ["https://example.com/pricing"],
  "prompt": "Extract all pricing plans with name, price, and features",
  "schema": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "plan": { "type": "string" },
        "price": { "type": "string" },
        "features": { "type": "array", "items": { "type": "string" } }
      }
    }
  }
}
```

## Agent

### firecrawl_agent
Start an autonomous web research agent.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Research task description |
| `urls` | string[] | No | Starting URLs |
| `model` | string | No | `spark-1-mini` (default) or `spark-1-pro` |
| `maxCredits` | integer | No | Credit limit for the task |
| `schema` | object | No | JSON schema for structured output |

Returns a `jobId` — check with `firecrawl_agent_status`.

### firecrawl_agent_status
Check agent job status and retrieve results.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Agent job ID |

## Interact

### firecrawl_interact
Operate dynamic pages in a live browser session via a natural-language prompt or code. Replaces the old `firecrawl_browser_*` tools.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | Page to open |
| `prompt` | string | Yes | Natural-language instructions (or code) for driving the page — login, click, navigate, fill forms |

```
Tool: firecrawl_interact
Input: {
  "url": "https://example.com/login",
  "prompt": "Log in with the provided credentials and open the dashboard"
}
```

### firecrawl_interact_stop
Close a live interaction session.

## Parsing

### firecrawl_parse
Convert files — PDF, DOCX, and other document formats — into LLM-ready output.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | File URL to parse |

## Developer Search

### firecrawl_developer_search
Search the developer index: GitHub issues, merged PRs, READMEs, and documentation. Use for code examples, error messages, and library usage questions.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Developer-oriented search query |

```
Tool: firecrawl_developer_search
Input: { "query": "nextjs hydration mismatch date formatting" }
```

## Monitors

Track page changes on a schedule with webhook/email alerts.

| Tool | Purpose |
|------|---------|
| `firecrawl_monitor_create` | Create a monitor for a URL (recurring scrapes + change detection) |
| `firecrawl_monitor_list` | List all monitors |
| `firecrawl_monitor_get` | Get a monitor's config |
| `firecrawl_monitor_update` | Update a monitor |
| `firecrawl_monitor_delete` | Delete a monitor |
| `firecrawl_monitor_run` | Trigger a monitor run now |
| `firecrawl_monitor_check` | Get a single check result |
| `firecrawl_monitor_checks` | List check history for a monitor |

## Research

Academic-paper and GitHub research tools.

| Tool | Purpose |
|------|---------|
| `firecrawl_research_search_papers` | Search academic papers |
| `firecrawl_research_read_paper` | Read a paper's full content |
| `firecrawl_research_inspect_paper` | Inspect a paper's metadata/structure |
| `firecrawl_research_related_papers` | Find related papers |
| `firecrawl_research_search_github` | Search GitHub repositories |

## Feedback

### firecrawl_feedback
Submit feedback about tool results.

### firecrawl_search_feedback
Submit feedback about search quality.
