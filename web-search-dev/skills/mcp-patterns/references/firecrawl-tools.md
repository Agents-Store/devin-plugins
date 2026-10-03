# Firecrawl MCP Tools (27 tools)

Verified against the live server and `firecrawl-mcp` 3.27.x (Node.js >= 22). The npm package lists 26 tools with its default profile; the live session exposes 27 when the optional feedback tools are counted.

| Group | Tools |
|-------|-------|
| Scrape / search / parse | `firecrawl_scrape`, `firecrawl_search`, `firecrawl_parse` |
| Crawl | `firecrawl_crawl`, `firecrawl_check_crawl_status`, `firecrawl_map` |
| Agent | `firecrawl_agent`, `firecrawl_agent_status` |
| Interact | `firecrawl_interact`, `firecrawl_interact_stop` |
| Developer + research | `firecrawl_developer_search`, `firecrawl_research_search_papers`, `firecrawl_research_read_paper`, `firecrawl_research_inspect_paper`, `firecrawl_research_related_papers` |
| Alexandria + account | `firecrawl_find_tools`, `firecrawl_credit_usage` |
| Monitors (8) | `firecrawl_monitor_create`, `_list`, `_get`, `_update`, `_delete`, `_run`, `_check`, `_checks` |
| Feedback | `firecrawl_feedback`, `firecrawl_search_feedback` |

## Access tiers

- **Keyless hosted** (`https://mcp.firecrawl.dev/v2/mcp`, no API key): exactly 3 tools — `firecrawl_scrape`, `firecrawl_search`, `firecrawl_parse` — rate-limited.
- **Search-only hosted endpoint** (`https://mcp.firecrawl.dev/v2/mcp-search`): 8 tools — `firecrawl_search` (no page content), `firecrawl_developer_search`, the four `firecrawl_research_*` tools, `firecrawl_find_tools`, `firecrawl_scrape`.
- **API key or OAuth** (this plugin: `FIRECRAWL_API_TOKEN` mapped to the server's `FIRECRAWL_API_KEY`): the full set, including crawl, map, agent, monitors, Alexandria and credit usage.
- **Node.js >= 22** is required to run the `firecrawl-mcp` package through `npx`.

## Scraping

### firecrawl_scrape
Scrape a single URL and return content in one or more formats, or run a catalogued Alexandria provider call (pass `alexandria` instead of `url` — see Alexandria below).

In the MCP schema `formats` takes **plain strings only**. Options live in separate parameters; object-style formats (`{ "type": "json", ... }`) exist only in the REST API and SDKs.

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | string | URL to scrape (exactly one of `url` / `alexandria`) |
| `formats` | string[] | `markdown`, `html`, `rawHtml`, `screenshot`, `links`, `summary`, `changeTracking`, `branding`, `json`, `query`, `audio` |
| `jsonOptions` | object | `{ prompt, schema }` — used when `formats` contains `json` |
| `queryOptions` | object | `{ prompt, mode }` — used when `formats` contains `query`; `mode` is `directQuote` or `freeform` (default) |
| `screenshotOptions` | object | `{ fullPage, quality, viewport: { width, height } }` |
| `parsers` / `pdfOptions` | string[] / object | `["pdf"]` and `{ maxPages }` |
| `onlyMainContent` | boolean | Strip navigation, footers, ads |
| `includeTags` / `excludeTags` | string[] | HTML tag filters |
| `waitFor` | number | Wait for JS rendering (ms) |
| `maxAge` | number | Cache tolerance in ms (default: 2 days — `0` forces a fresh scrape) |
| `actions` | array | Page interactions: `wait`, `click`, `write`, `press`, `scroll`, `screenshot`, `scrape`, `executeJavascript`, `generatePDF` |
| `proxy` | string | `basic`, `stealth`, `enhanced`, `auto` |
| `location` | object | `{ country, languages }` |
| `mobile` | boolean | Emulate a mobile device |
| `profile` | object | `{ name, saveChanges }` — persistent cookies/session state shared between scrape and interact |
| `redactPII`, `lockdown`, `zeroDataRetention` | boolean | Privacy controls (`zeroDataRetention` needs an eligible account) |
| `storeInCache`, `removeBase64Images`, `skipTlsVerification` | boolean | Misc |

```
Tool: firecrawl_scrape
Input: {
  "url": "https://example.com/page",
  "formats": ["markdown", "links"],
  "onlyMainContent": true
}
```

**Structured data from one URL** — this replaces the old dedicated extract tool, which no longer exists (calls return `DEPRECATED_TOOL`):

```
Tool: firecrawl_scrape
Input: {
  "url": "https://example.com/pricing",
  "formats": ["json"],
  "jsonOptions": {
    "prompt": "Extract all pricing plans with name, price, and features",
    "schema": {
      "type": "object",
      "properties": {
        "plans": {
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
    }
  }
}
```

For several unknown URLs or data spread across sites use `firecrawl_agent` (below).

**Targeted Q&A on a page** (`query` format):

```
Tool: firecrawl_scrape
Input: {
  "url": "https://example.com/docs/limits",
  "formats": ["query"],
  "queryOptions": { "prompt": "What is the default rate limit?", "mode": "directQuote" }
}
```

**Design tokens** — `formats: ["branding"]` returns colours, fonts and logo of a site.

### firecrawl_search
Search the web, optionally scraping each result.

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Search query (required) |
| `limit` | number | Max results (1-100; REST default is 10) |
| `sources` | array | `web`, `news`, `images`, `alexandria` |
| `categories` | array | `research`, `pdf`, `developer` |
| `includeDomains` / `excludeDomains` | string[] | Mutually exclusive |
| `filter` | string | Extra result filter string |
| `tbs` | string | Time filter (e.g. `qdr:d`) |
| `location` | string | Geographic location |
| `scrapeOptions` | object | Scrape options applied to every result (same fields as `firecrawl_scrape`) |
| `highlights` | boolean | Query-relevant excerpts for web/news results (default on) |
| `domainTools`, `toolDetail` | boolean / string | Alexandria discovery controls (`compact`, `summary`, `full`) |

There is **no `lang` or `country` parameter** in the MCP schema. For authenticated sessions `sources` defaults to `web` + `alexandria` (provider matches appear in `data.tools`) — pass `"sources": ["web"]` when you only want web results.

```
Tool: firecrawl_search
Input: {
  "query": "Next.js server components tutorial",
  "limit": 10,
  "sources": ["web"]
}
```

`categories: ["developer"]` searches the developer index next to web results; `categories: ["research"]` restricts web results to research-affiliated sites.

### firecrawl_parse
Convert a **local file** (PDF, DOCX, DOC, ODT, RTF, XLSX, XLS, HTML) into markdown, JSON, summary or targeted answers. Remote URLs belong in `firecrawl_scrape` (add `parsers: ["pdf"]` for PDFs).

| Parameter | Type | Description |
|-----------|------|-------------|
| `filePath` | string | Local file path (local MCP) — on the hosted MCP the first call returns upload instructions |
| `uploadRef` | string | Hosted phase two: the reference returned after uploading the file |
| `formats` | string[] | `markdown`, `html`, `rawHtml`, `links`, `summary`, `json`, `query` |
| `jsonOptions`, `queryOptions`, `pdfOptions`, `redactPII` | object / boolean | Same shape as in scrape |

Hosted flow: call 1 with `filePath` returns upload instructions and a `nextToolCall`; upload locally; call 2 with the returned `uploadRef`. Never send both fields together.

## Crawling

### firecrawl_crawl
Start a multi-page crawl, **poll it to a terminal state and return the final status plus collected data** in one call (no manual polling). Results can be large — keep `limit` conservative.

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | string | Starting URL (required) |
| `limit` | number | Max pages |
| `maxDiscoveryDepth` | number | Max link-discovery depth |
| `prompt` | string | Natural-language crawl config |
| `sitemap` | string | `skip`, `include`, `only` |
| `crawlEntireDomain`, `allowSubdomains`, `allowExternalLinks` | boolean | Scope controls |
| `includePaths` / `excludePaths` | string[] | Path filters |
| `ignoreQueryParameters`, `deduplicateSimilarURLs` | boolean | URL normalisation |
| `delay` / `maxConcurrency` | number | Politeness controls |
| `scrapeOptions` | object | Options for each page (same fields as `firecrawl_scrape`) |
| `webhook` / `webhookHeaders` | string / object | Webhook notifications (unavailable in safe mode) |

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
Read the state of an existing crawl by `id`. Needed only to pick up a job that was started earlier or cut off; a normal `firecrawl_crawl` call already returns the final data.

### firecrawl_map
List the URLs under a site without fetching content.

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | string | Website URL (required) |
| `limit` | number | Max URLs |
| `search` | string | Narrow the list by keyword |
| `sitemap` | string | `include`, `skip`, `only` |
| `includeSubdomains`, `ignoreQueryParameters` | boolean | Coverage controls |

```
Tool: firecrawl_map
Input: { "url": "https://example.com", "limit": 100 }
```

## Agent (structured data from unknown URLs)

### firecrawl_agent
Research agent: searches, navigates and reads pages, then returns JSON assembled across sources. Use it for an entity plus its fields, for lists and datasets, and when the URLs are not known. For one known URL use `firecrawl_scrape` with `formats: ["json"]`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `prompt` | string | What to research and which fields to return (required, max 10 000 chars) |
| `urls` | string[] | Seed URLs |
| `schema` | object | JSON schema for the output |
| `effort` | string | `low`, `medium`, `high` |
| `mode` | string | `extract` (default — full result every turn) or `chat` (short replies on follow-ups) |
| `threadId` | string (UUID) | Continue an earlier thread with a follow-up `prompt` |
| `strictConstrainToURLs` | boolean | Visit only the supplied `urls` |
| `maxCredits` | integer | Spend limit (default 2500) |
| `exchange` | object | Alexandria provider settings (`enabled`, `toolkits`, `maxCalls`, `onTermsRequired`, `approve` / `decline`) |

There is no `model` parameter in the MCP tool (the REST API runs on `spark-2`). The call returns only a job ID plus a `threadId`; read the result with `firecrawl_agent_status` every 15-30 seconds until `completed` or `failed` (typically 1-3 minutes). Agent runs spend credits — set `maxCredits`.

```
Tool: firecrawl_agent
Input: {
  "prompt": "Find the top 5 headless CMS platforms with their starting price and open-source licence",
  "schema": {
    "type": "object",
    "properties": {
      "cms": { "type": "array", "items": { "type": "object", "properties": {
        "name": { "type": "string" }, "startingPrice": { "type": "string" }, "licence": { "type": "string" }
      } } }
    }
  },
  "effort": "medium",
  "maxCredits": 500
}
```

### firecrawl_agent_status
Poll an agent job by `id`; returns progress or the final data.

## Interact (live browser)

### firecrawl_interact
Drive a live browser session with a natural-language `prompt` or executable `code`. Acts on the real site — form submissions have side effects.

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` / `scrapeId` | string | **Exactly one**: open a fresh page, or continue on an existing scrape |
| `prompt` / `code` | string | **Exactly one**: natural-language instruction, or code to run |
| `language` | string | For `code`: `bash`, `python`, `node` |
| `timeout` | number | Seconds, 1-300 |
| `scrapeOptions` | object | Scrape options for URL mode |

URL mode returns a `scrapeId`; reuse it for follow-up calls and close the session with `firecrawl_interact_stop`.

```
Tool: firecrawl_interact
Input: { "url": "https://example.com/login", "prompt": "Log in with the provided credentials and open the dashboard" }
```

### firecrawl_interact_stop
Stop the session for a `scrapeId` and release its resources.

## Developer search and research

### firecrawl_developer_search
Search an index of public repositories, GitHub issues, merged PRs, READMEs and documentation. Use it for code examples, error messages and library behaviour (this is also the replacement for the removed GitHub-search research tool).

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Natural-language developer question (required) |
| `k` | integer | Results to return (1-100, default 10) |
| `skills` | string | `"only"` — search agent-skill files only |

```
Tool: firecrawl_developer_search
Input: { "query": "nextjs hydration mismatch date formatting", "k": 5 }
```

### Research (papers) — 4 tools
Index covers PubMed, bioRxiv, medRxiv, arXiv and other scientific sources.

| Tool | Purpose | Key parameters |
|------|---------|----------------|
| `firecrawl_research_search_papers` | Search metadata and abstracts | `query`, `k` (default 40), `authors`, `categories`, `from`, `to` |
| `firecrawl_research_read_paper` | Passages relevant to a question | `paperId` (e.g. `arxiv:1706.03762`, `doi:...`), `question`, `k` |
| `firecrawl_research_inspect_paper` | Canonical metadata | `paperId` |
| `firecrawl_research_related_papers` | Citation-graph candidates | `seed_ids` (1-10), `intent`, `mode` (`similar`, `citers`, `references`), `k`, `rerank` |

## Alexandria (data-provider catalogue)

Alexandria returns typed, sourced records (companies, people, filings, prices, packages, places, jobs, ...) from catalogued providers. **Requires an API key on a team with Alexandria access** — keyless sessions get an error.

1. **Discover**: `firecrawl_search` with `"sources": ["web", "alexandria"]` (matches arrive in `data.tools`), or `firecrawl_find_tools` (free) — no arguments lists categories; narrow with `categories`, `providers`, `capabilities`, or semantic `query` / `urls`.
2. **Read the contract** with `firecrawl_find_tools({ providers: [...], capabilities: [...] })`.
3. **Execute** through `firecrawl_scrape` with `alexandria` instead of `url`:

```
Tool: firecrawl_scrape
Input: {
  "alexandria": [
    { "provider": "<provider>", "capability": "<capability>", "options": { } }
  ]
}
```

Up to ten calls per request; reuse the returned `requestId` when retrying. Providers whose data terms the team has not accepted fail with `THIRD_PARTY_DATA_TERMS_REQUIRED`. Accepting terms is a legal act: show the user the terms (`terms/show`), get explicit consent, and only then run `terms/accept` — a data request is not consent.

### firecrawl_credit_usage
Read-only account balance. `{ "view": "current" }` (default) returns `remainingCredits`, `planCredits`, `billingPeriodStart`, `billingPeriodEnd`; `{ "view": "historical" }` returns per-period `creditsUsed`; `byApiKey: true` splits by key.

## Monitors

Recurring scrape, crawl or search checks with diffs and change alerts.

| Tool | Purpose |
|------|---------|
| `firecrawl_monitor_create` | Create a monitor: `page`/`pages` or `queries` plus a plain-language `goal`, `scheduleText`, `webhookUrl`, `email` — or an advanced `body` |
| `firecrawl_monitor_list` | List monitors (`limit`, `offset`) |
| `firecrawl_monitor_get` | One monitor's configuration and state (`id`) |
| `firecrawl_monitor_update` | Patch name, status, schedule, targets, goal, webhook (`id`, `body`) |
| `firecrawl_monitor_delete` | Permanently delete a monitor |
| `firecrawl_monitor_run` | Queue an immediate check |
| `firecrawl_monitor_check` | One check with page-level results (`pageStatus`: `same`, `new`, `changed`, `removed`, `error`) |
| `firecrawl_monitor_checks` | Check history (`status` filter) |

With a `goal`, checks can include a meaningful-change judgement. Monitors schedule future network calls — confirm with the user before creating one.

## Feedback

`firecrawl_feedback` and `firecrawl_search_feedback` report result or search quality. Setting `FIRECRAWL_NO_SEARCH_FEEDBACK=1` / `FIRECRAWL_NO_ENDPOINT_FEEDBACK=1` removes them from the tool list.
