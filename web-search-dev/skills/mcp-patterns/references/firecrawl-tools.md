# Firecrawl MCP Tools (34 tools)

Verified against the tool snapshot of `firecrawl-mcp` 3.41.x (Node.js >= 22), the package this plugin starts through `npx`. An authenticated session lists 34 tools, the two optional feedback tools included.

| Group | Tools |
|-------|-------|
| Scrape / search / parse | `firecrawl_scrape`, `firecrawl_search`, `firecrawl_parse` |
| Crawl | `firecrawl_crawl`, `firecrawl_check_crawl_status`, `firecrawl_map` |
| Agent | `firecrawl_agent`, `firecrawl_agent_status` |
| Interact | `firecrawl_interact`, `firecrawl_interact_stop` |
| Developer, government + research | `firecrawl_developer_search`, `firecrawl_gov_search`, `firecrawl_research_search_papers`, `firecrawl_research_read_paper`, `firecrawl_research_inspect_paper`, `firecrawl_research_related_papers`, `firecrawl_research_lookup_protein` |
| Alexandria | `alexandria_library_search` (explore, free), `alexandria_library_read` (execute, billed) |
| People, companies, jobs | `people_company_search`, `people_company_enrich`, `jobs_search` |
| Account + team skills | `firecrawl_credit_usage`, `firecrawl_save_skill` |
| Monitors (8) | `firecrawl_monitor_create`, `_list`, `_get`, `_update`, `_delete`, `_run`, `_check`, `_checks` |
| Feedback | `firecrawl_feedback`, `firecrawl_search_feedback` |

## Access tiers

- **Keyless hosted** (`https://mcp.firecrawl.dev/v2/mcp`, no API key): exactly 3 tools — `firecrawl_scrape`, `firecrawl_search`, `firecrawl_parse` — rate-limited.
- **Search-only hosted endpoint** (`https://mcp.firecrawl.dev/v2/mcp-search`): a reduced search surface — `firecrawl_search` (no page content), developer / government / paper search, `firecrawl_scrape`, Alexandria discovery, people-company and jobs search. This plugin's server does not use it.
- **API key or OAuth** (this plugin: `FIRECRAWL_API_TOKEN` mapped to the server's `FIRECRAWL_API_KEY`): the full set, including crawl, map, agent, monitors, Alexandria and credit usage.
- **Node.js >= 22** is required to run the `firecrawl-mcp` package through `npx`.

## Scraping

### firecrawl_scrape
Scrape a single URL and return content in one or more formats. `url` is the only required parameter (the scheme may be omitted; it is read as https).

In the MCP schema `formats` takes **plain strings only**. Options live in separate parameters; object-style formats (`{ "type": "json", ... }`) exist only in the REST API and SDKs. `firecrawl_scrape` lists **no `json` format and no `jsonOptions`** and no longer lists `alexandria` (provider calls go through `alexandria_library_read`); the `scrapeOptions` of search, crawl and interact and `firecrawl_parse` still list `json` / `jsonOptions`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | string | URL to scrape (required) |
| `formats` | string[] | `markdown`, `html`, `rawHtml`, `screenshot`, `links`, `images`, `summary`, `changeTracking`, `branding`, `query`, `audio` |
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
| `domainTools`, `toolDetail` | boolean / string | Add Alexandria tools matched to the page's domain to the result (`compact`, `summary`, `full`) |

```
Tool: firecrawl_scrape
Input: {
  "url": "https://example.com/page",
  "formats": ["markdown", "links"],
  "onlyMainContent": true
}
```

**Structured data from known URLs** — the old dedicated extract tool no longer exists (calls return `DEPRECATED_TOOL`) and `firecrawl_scrape` takes no `json` format. For a few values, scrape with `formats: ["query"]` (below) or `["markdown"]` and pick the fields out yourself. When the result must follow a JSON schema, run `firecrawl_agent` on the URL(s) with `strictConstrainToURLs` and poll `firecrawl_agent_status`:

```
Tool: firecrawl_agent
Input: {
  "prompt": "Extract all pricing plans with name, price, and features",
  "urls": ["https://example.com/pricing"],
  "strictConstrainToURLs": true,
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
  },
  "maxCredits": 100
}
```

For unknown URLs or data spread across sites drop `strictConstrainToURLs` (see `firecrawl_agent` below).

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
| `categories` | array | `research`, `pdf`, `developer`, `gov` (`gov` cannot be combined with other categories) |
| `includeDomains` / `excludeDomains` | string[] | Mutually exclusive |
| `filter` | string | Extra result filter string |
| `tbs` | string | Time filter (e.g. `qdr:d`) |
| `location` | string | Geographic location |
| `scrapeOptions` | object | Scrape options applied to every result (same fields as `firecrawl_scrape`, plus `json` / `jsonOptions`) |
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
| `jsonOptions`, `queryOptions`, `pdfOptions`, `redactPII` | object / boolean | `{ prompt, schema }` for `json`; the others have the same shape as in scrape |

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
| `scrapeOptions` | object | Options for each page (same fields as `firecrawl_scrape`, plus `json` / `jsonOptions`) |
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
Research agent: searches, navigates and reads pages, then returns JSON assembled across sources. Use it for an entity plus its fields, for lists and datasets, and when the URLs are not known. For one known URL, `firecrawl_scrape` (`markdown` or `query`) is cheaper; add `urls` with `strictConstrainToURLs` when a schema-bound result is needed.

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
| `scrapeOptions` | object | Scrape options for URL mode (same fields as `firecrawl_scrape`, plus `json` / `jsonOptions`; `profile` reuses state saved by earlier team sessions) |

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

### firecrawl_gov_search
Search US federal, state and local statutes, regulations, codes, court opinions and other government publications for questions that need primary text. Parameters: `query` (required), `k`, and optional filters `jurisdiction`, `court`, `courtType`, `cites`, `domain`. Clarify a missing jurisdiction or as-of date first; no hits does not mean no applicable law exists.

### Research (papers) — 5 tools
Index covers PubMed, bioRxiv, medRxiv, arXiv and other scientific sources.

| Tool | Purpose | Key parameters |
|------|---------|----------------|
| `firecrawl_research_search_papers` | Search metadata and abstracts | `query`, `k` (default 40), `authors`, `categories`, `from`, `to` |
| `firecrawl_research_read_paper` | Passages relevant to a question | `paperId` (e.g. `arxiv:1706.03762`, `doi:...`), `question`, `k` |
| `firecrawl_research_inspect_paper` | Canonical metadata | `paperId` |
| `firecrawl_research_related_papers` | Citation-graph candidates | `seed_ids` (1-10), `intent`, `mode` (`similar`, `citers`, `references`), `k`, `rerank` |
| `firecrawl_research_lookup_protein` | UniProtKB/Swiss-Prot curator statements on one protein's location and function, with evidence labels | `protein` (accession, entry name, gene symbol or exact name), `organism` (default human) |

## Alexandria (data-provider catalogue)

Alexandria returns typed, sourced records (companies, people, filings, prices, packages, places, jobs, ...) from catalogued providers. **Requires an API key on a team with Alexandria access** — keyless sessions get an error. `firecrawl_find_tools` and the `alexandria` body of `firecrawl_scrape` are no longer listed (a hosted server may still answer legacy calls for older clients); discovery and execution are two dedicated tools.

1. **Discover** (free): `firecrawl_search` with `"sources": ["web", "alexandria"]` (matches arrive in `data.tools`), or `alexandria_library_search` — a read-only shell over the catalogue with `ls`, `tree`, `cat`, `head`, `tail`, `grep`, `find`, `wc`, `sort`, `uniq`, `cut`, `tr`, `sed`, `jq`, `xargs` and pipes, input `{ "command": "..." }`. `ls /library` lists the categories, `cat /library/README.md` explains the layout, `grep -ril "<keyword>" /library | head -20` finds providers. For a business workflow (prospect lists, competitor or market research, monitoring) check the team's and Firecrawl's skills first: `cat /library/skills/search/<a-few-words-joined-by-hyphens>`.
2. **Read the contract** with `cat /library/<category>/<provider>/<capability>.md` — inputs (including `requiresOneOf` groups), outputs and the call to send; recorded example responses sit under `/examples/<provider>/<capability>.json`.
3. **Execute** with `alexandria_library_read` (billed per executed capability): `calls` takes 1-10 entries `{ provider, capability, options }`, the options follow the contract:

```
Tool: alexandria_library_read
Input: {
  "calls": [
    { "provider": "<provider>", "capability": "<capability>", "options": { } }
  ]
}
```

Results come back in call order in `data.alexandria`; one call can fail while the others succeed, and a result too large to return inline is read in slices through its `nextTool`. Reuse the returned `requestId` (idempotency key) when retrying; `timeout` is in milliseconds. For named people and companies use `people_company_enrich` / `people_company_search`, for job postings `jobs_search`, instead of calling those providers directly.

Providers whose data terms the team has not accepted fail with `THIRD_PARTY_DATA_TERMS_REQUIRED`. Read the agreement with `alexandria_library_read` and `{ "provider": "firecrawl", "capability": "terms/show", "options": { "provider": "<provider>" } }`, show it to the user and stop: an organization admin accepts terms in the Firecrawl dashboard, not through this connection, and a data request is not consent. After the admin confirms, repeat the identical call.

### People, companies and jobs
- `people_company_enrich` — a named person (name with company or domain, LinkedIn URL, email) or company: profile or firmographics, and with `contact_fields` (`work_email`, `personal_email`, `mobile`) paid contact details; up to 10 records per call, `max_credits` caps the spend.
- `people_company_search` — find people or companies you cannot name yet: `entity` (`person` / `company`) plus `filters`; rows carry no emails or phones.
- `jobs_search` — job postings by `query` / `location`, one posting by `url` (open or closed), or a company's open roles via `company`.

### firecrawl_save_skill
Create or change one of the team's skills (instructions an agent follows, naming capabilities as `@provider/capability`), listed under `/library/skills/team/<slug>`. Free; save only what the user asked for. Library skills cannot be changed — copy one with `from`.

### firecrawl_credit_usage
Read-only account balance. `{ "view": "current" }` (default) returns `remainingCredits`, `planCredits`, `billingPeriodStart`, `billingPeriodEnd`; `{ "view": "historical" }` returns per-period `creditsUsed`; `byApiKey: true` splits by key.

## Monitors

Recurring scrape, crawl or search checks with diffs and change alerts.

| Tool | Purpose |
|------|---------|
| `firecrawl_monitor_create` | Create a monitor: `page`/`pages` or `queries` plus a plain-language `goal`, `scheduleText`, `webhookUrl`, `email` — or an advanced `body` |
| `firecrawl_monitor_list` | List monitors (`limit`, `offset`) |
| `firecrawl_monitor_get` | One monitor's configuration and state (`id`) |
| `firecrawl_monitor_update` | Patch a monitor (`id` plus at least one change): `status` (`active` / `paused`), `scheduleText` or `cron` with `timezone` (UTC when omitted), or a partial monitor in `body` (name, targets, goal, webhook, ...) |
| `firecrawl_monitor_delete` | Permanently delete a monitor |
| `firecrawl_monitor_run` | Queue an immediate check |
| `firecrawl_monitor_check` | One check with page-level results (`pageStatus`: `same`, `new`, `changed`, `removed`, `error`) |
| `firecrawl_monitor_checks` | Check history (`status` filter) |

With a `goal`, checks can include a meaningful-change judgement. Monitors schedule future network calls — confirm with the user before creating one.

## Feedback

`firecrawl_feedback` and `firecrawl_search_feedback` report result or search quality. Setting `FIRECRAWL_NO_SEARCH_FEEDBACK=1` / `FIRECRAWL_NO_ENDPOINT_FEEDBACK=1` removes them from the tool list.
