# Exa MCP Tools (2 default + 2 opt-in)

Exa excels at **semantic search** — finding pages by meaning, not just keywords. Best for documentation discovery and category-specific searches.

| Tool | Availability |
|------|--------------|
| `web_search_exa` | Default |
| `web_fetch_exa` | Default |
| `web_search_advanced_exa` | Opt-in (filters, dates, summaries, subpages) |
| `agent_run` | Needs an API key or OAuth; default on the **hosted** MCP once authenticated, opt-in on the bundled **npx** server |

## web_search_exa
General web search with semantic understanding. The schema is strict (`additionalProperties: false`) — it accepts **only** `query` and `numResults`. Any other key is rejected.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Natural-language description of the ideal page, not just keywords |
| `numResults` | number | No | Results to return (default: 10) |

```
Tool: web_search_exa
Input: {
  "query": "blog post comparing React Server Components best practices",
  "numResults": 10
}
```

**Category focus** is done inline in the query string, not via a parameter. The live tool supports only two inline categories: `category:company` (companies) and `category:people` (LinkedIn profiles):

```
Tool: web_search_exa
Input: {
  "query": "category:company Vercel",
  "numResults": 5
}
```

Other categories (`news`, `publication`, `pdf`, `github`, `personal site`, `financial report`), **domain scoping, date filters and search-type control are not available on `web_search_exa`** — they live on the opt-in `web_search_advanced_exa` tool (see below).

## web_fetch_exa
Read one or more URLs as clean markdown. Use after `web_search_exa` when highlights are insufficient. The schema is strict (`additionalProperties: false`).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `urls` | string[] | Yes | URLs to read — batch multiple URLs in one call |
| `maxCharacters` | number | No | Max characters to return per page (default: 3000) |

```
Tool: web_fetch_exa
Input: {
  "urls": ["https://nextjs.org/docs/app/building-your-application/data-fetching"],
  "maxCharacters": 50000
}
```

**Code/dev search:** Exa has no code-search MCP tool. Use `firecrawl_developer_search` (Firecrawl MCP) or `web_search_advanced_exa` with `includeDomains: ["github.com"]` (opt-in, see below). Exa's code vertical is available via the REST API only.

## Enabling the opt-in tools

An explicit tool list **replaces** the defaults, so always list every tool you want.

- **Bundled stdio server (this plugin's `.mcp.json`, `npx exa-mcp-server`)** — set the `ENABLED_TOOLS` environment variable (`TOOLS` also works) in the shell that launches Claude Code:

  ```
  ENABLED_TOOLS=web_search_exa,web_fetch_exa,web_search_advanced_exa,agent_run
  ```

  `agent_run` additionally requires `EXA_API_KEY` to be set.
- **Hosted MCP** (`https://mcp.exa.ai/mcp`) — use the `tools` query parameter:

  ```
  https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa,web_search_advanced_exa,agent_run
  ```

  Authenticate with OAuth (`https://mcp.exa.ai/mcp?login`) or an `x-api-key` header. On the hosted server `agent_run` is enabled by default as soon as you authenticate, without a `tools` parameter; only advanced search needs the opt-in.

## web_search_advanced_exa
Advanced search with full filter control. This is the only MCP tool that accepts domain, date and category filters, and it combines search with content extraction in one call. Field names below are taken from `exa-mcp-server` 3.4.x; if a client reports a different schema, trust the client.

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Search query (required) |
| `numResults` | number | 1-100 (default 10) |
| `type` | string | `auto` (default, high quality), `fast`, `instant` |
| `category` | string | `company`, `publication`, `news`, `pdf`, `github`, `personal site`, `people`, `financial report` |
| `includeDomains` / `excludeDomains` | string[] | Domain allow / deny lists |
| `startPublishedDate` / `endPublishedDate` | string | `YYYY-MM-DD` publish-date window |
| `startCrawlDate` / `endCrawlDate` | string | `YYYY-MM-DD` crawl-date window |
| `includeText` / `excludeText` | string[] | Text must contain ALL / must not contain ANY (deprecated in the REST API) |
| `userLocation` | string | ISO country code for geo-targeting |
| `moderation` | boolean | Filter unsafe content |
| `additionalQueries` | string[] | Query variations to widen coverage |
| `textMaxCharacters` | number | Max characters of text per result |
| `contextMaxCharacters` | number | Max characters of the combined context string (off by default) |
| `enableSummary` / `summaryQuery` | boolean / string | Summaries, optionally focused by a query |
| `enableHighlights` | boolean | Highlights extraction |
| `highlightsMaxCharacters` / `highlightsQuery` | number / string | Highlight budget and relevance query |
| `maxAgeHours` | number | Max age of cached content; `0` always fetches fresh |
| `livecrawlTimeout` | number | Timeout (ms) for a live fetch |
| `subpages` / `subpageTarget` | number / string[] | Crawl 1-10 subpages per result, steered by keywords |

`highlightsNumSentences` and `highlightsPerUrl` are deprecated — use `highlightsMaxCharacters`.

**Domain-scoped search:**
```
Tool: web_search_advanced_exa
Input: {
  "query": "authentication middleware",
  "includeDomains": ["github.com", "stackoverflow.com"],
  "numResults": 15,
  "enableHighlights": true
}
```

**Important:** `category: "company"` and `category: "people"` disable date, text and `excludeDomains` filters — combining them causes a 400 error.

The `deep-lite` / `deep` / `deep-reasoning` search types belong to the REST API only.

## agent_run
Run, or resume, a multi-step Exa Agent task: research, list-building, enrichment and structured output. Runs can take several minutes and are billed by usage.

Provide **exactly one** of `query` (start a run) or `runId` (resume); a resume call accepts nothing else.

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Natural-language research or enrichment objective |
| `runId` | string | `agent_run_...` id from an earlier call that reported `status: "running"` — pick the same run back up, never start a duplicate |
| `previousRunId` | string | Completed `agent_run_...` id used as context for a new follow-up run |
| `systemPrompt` | string | Extra guidance for researching or judging results |
| `outputSchema` | object | JSON Schema for the answer (prefer a top-level object with bounded arrays and source fields) |
| `input.data` / `input.exclusion` | object[] | Rows to enrich / entities to skip |
| `dataSources` | `{provider}[]` | Up to 5 Exa Connect providers |
| `effort` | string | `minimal`, `low` (MCP default), `medium`, `high`, `xhigh`, `auto` |

```
Tool: agent_run
Input: {
  "query": "List 10 headless CMS vendors with pricing model and open-source licence",
  "outputSchema": {
    "type": "object",
    "properties": {
      "vendors": { "type": "array", "maxItems": 10, "items": { "type": "object", "properties": {
        "name": { "type": "string" }, "pricing": { "type": "string" }, "licence": { "type": "string" }, "source": { "type": "string" }
      } } }
    }
  },
  "effort": "medium"
}
```

If the result says `status: "running"`, call `agent_run` again with `{ "runId": "<id>" }`.

## Pricing

See https://exa.ai/pricing for current pricing. The hosted MCP works anonymously with free rate limits (HTTP 429 means you hit them) — add an API key or sign in for your own plan limits.
