# Exa MCP Tools (2 default + 2 optional)

Exa excels at **semantic search** — finding pages by meaning, not just keywords. Best for documentation discovery and category-specific searches. The default MCP server exposes `web_search_exa` and `web_fetch_exa`; advanced search and the Exa Agent must be enabled explicitly (see below).

## web_search_exa
General web search with semantic understanding. The schema is strict (`additionalProperties: false`) — it accepts **only** `query` and `numResults`. Any other key is rejected.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Natural language search query |
| `numResults` | integer | No | Results to return (1-100, default: 10) |

```
Tool: web_search_exa
Input: {
  "query": "React server components best practices 2025",
  "numResults": 10
}
```

**Category focus** is done inline in the query string, not via a parameter — prefix the query with `category:<type>` where `<type>` is one of `company`, `publication`, `news`, `personal site`, `people`:

```
Tool: web_search_exa
Input: {
  "query": "category:company Vercel",
  "numResults": 5
}
```

**Domain scoping, date filters, and search-type control are NOT available on `web_search_exa`** — they live on the opt-in `web_search_advanced_exa` tool (see below).

## web_fetch_exa
Read one or more URLs as clean markdown. Replaces the old `crawling_exa` tool. The schema is strict (`additionalProperties: false`).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `urls` | string[] | Yes | URLs to read — batch multiple URLs in one call |
| `maxCharacters` | integer | No | Max characters to return per page (default: 3000) |

```
Tool: web_fetch_exa
Input: {
  "urls": ["https://nextjs.org/docs/app/building-your-application/data-fetching"],
  "maxCharacters": 50000
}
```

**Code/dev search:** the old `get_code_context_exa` tool no longer exists. Use `firecrawl_developer_search` (Firecrawl MCP) or `web_search_advanced_exa` with `includeDomains: ["github.com"]` (opt-in, see below). Exa's code vertical is available via the REST API only.

## Optional Tools (via remote MCP)

`web_search_advanced_exa` and the new `agent_run` (multi-step Exa Agent) are not served by default. Enable them via the remote MCP URL with a `tools` query parameter and `x-api-key` header:

```
https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa,web_search_advanced_exa,agent_run
```

### web_search_advanced_exa
Advanced search with full filter control. This is the only MCP tool that accepts domain, date, and category filters.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query |
| `numResults` | integer | No | Results count |
| `type` | string | No | `auto`, `fast`, `instant` |
| `category` | string | No | `company`, `publication`, `news`, `pdf`, `github`, `personal site`, `people`, `financial report` |
| `includeDomains` | string[] | No | Only search these domains |
| `excludeDomains` | string[] | No | Exclude these domains |
| `startPublishedDate` | string | No | ISO 8601 start date filter |
| `endPublishedDate` | string | No | ISO 8601 end date filter |
| `contents` | object | No | Content extraction options |
| `contents.text` | object | No | `{ maxCharacters, includeHtmlTags }` |
| `contents.highlights` | object | No | `{ maxCharacters, query }` |
| `contents.summary` | object | No | `{ query }` |

Note: the academic category is `publication` (there is no `research paper` value), and `includeText`/`excludeText` are not available on either MCP tool. The `deep-lite`/`deep`/`deep-reasoning` search types belong to the REST API only.

**Domain-scoped search:**
```
Tool: web_search_advanced_exa
Input: {
  "query": "authentication middleware",
  "includeDomains": ["github.com", "stackoverflow.com"],
  "numResults": 15
}
```

**Important:** `category: "company"` and `category: "people"` disable date, text, and excludeDomains filters — using them together causes a 400 error.

This tool combines search + content extraction in one call — useful when you need both results and page content.

### agent_run
Run a multi-step Exa Agent research task (backed by the Agent API `POST /agent/runs`).

## Pricing

See https://exa.ai/pricing for current pricing. MCP has a free tier with rate limits — add your API key for higher limits.
