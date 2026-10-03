---
name: troubleshoot
description: This skill should be used when the user encounters "DataForSEO errors", "DataForSEO not working", "DataForSEO connection issues", "debug DataForSEO", "DataForSEO MCP problems", "tool not found" for a DataForSEO tool, or needs to diagnose and fix common problems with the DataForSEO MCP server.
---

# Troubleshoot

Diagnose and fix common problems with the DataForSEO v3 MCP server: connection failures, authentication errors, wrong request bodies, empty results and cost surprises.

## Quick Diagnostics

Run this sequence to isolate the problem. Steps 1 and 2 cost nothing.

### Step 1 — Is the server running?
```
docs_list_sections()
```

This needs no credentials. If it returns the 13 section names, the MCP server is running. If the tool does not exist or the call fails, the problem is the server startup (see "MCP Server Startup Issues").

### Step 2 — Do the credentials work?
```
api_request({method: "GET", path: "/v3/appendix/user_data", noAiMode: true})
```

DataForSEO does not charge for this endpoint. `status_code` 20000 with a `money.balance` means authentication works. If it fails, see "Authentication Errors".

### Step 3 — Check the error
- **No response or timeout**: the MCP server is not running. See "MCP Server Startup Issues".
- **401 Unauthorized**: wrong credentials. See "Authentication Errors".
- **400 Bad Request or a 40xxx task code**: invalid request body. See "Request Errors".
- **500 Internal Server Error**: DataForSEO server issue. See "When to Escalate".

### Step 4 — Check the tool name
The v3 server has **four tools** and no others: `docs_list_sections`, `docs_index`, `docs_search` and `api_request`. A "tool not found" for any other name (for example `backlinks_summary`, `on_page_lighthouse` or `serp_organic_live_advanced`) means the call comes from the v2 server, whose per-endpoint tools were removed. Send the same request through `api_request` with the endpoint's REST path (see the `mcp-patterns` skill).

## Authentication Errors

DataForSEO authenticates with an **API login and an API password**, set as environment variables in the MCP configuration. The API password is generated at [app.dataforseo.com/api-access](https://app.dataforseo.com/api-access) and is **not** the account password.

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Wrong or missing credentials | Verify `DATAFORSEO_USERNAME` (or `DATAFORSEO_LOGIN`) and `DATAFORSEO_PASSWORD` |
| 401 with the account password | The account password was used | Use the API password from the API Access page |
| 403 Forbidden | Account suspended or plan limits exceeded | Log in at app.dataforseo.com to check account status |
| "Invalid credentials" in the response | Typo in the login or password | Copy and paste both from the API Access page |

The plugin's `.mcp.json` should contain:
```json
{
  "mcpServers": {
    "dataforseo": {
      "command": "npx",
      "args": ["-y", "dataforseo-mcp-server@3"],
      "env": {
        "DATAFORSEO_USERNAME": "${DATAFORSEO_USERNAME}",
        "DATAFORSEO_PASSWORD": "${DATAFORSEO_PASSWORD}"
      }
    }
  }
}
```

The server accepts `DATAFORSEO_USERNAME` as an alias of its own variable `DATAFORSEO_LOGIN`. The `${...}` placeholders are resolved from your environment; verify both are set in your shell profile or the Claude Code settings `env` block, and restart Claude Code after changing them.

## MCP Server Startup Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| The DataForSEO tools are missing | Server not started or wrong package | Restart Claude Code; verify `.mcp.json` exists in the plugin root |
| "npx: command not found" | Node.js not installed or not in PATH | Install Node.js 22 or newer from nodejs.org |
| Server starts then crashes | Node.js too old, or a corrupted npx cache | `node --version` must be 22 or newer; run `npx clear-npx-cache` and restart |
| Old per-endpoint tool names appear | A cached v2 package | Run `npx clear-npx-cache` to force a fresh download of `dataforseo-mcp-server@3` |
| "ENOENT" or "spawn error" | `npx` path not found by Claude Code | Use the absolute path to npx: replace `"command": "npx"` with the full path (for example `"/usr/local/bin/npx"`) |

To verify the Node.js version: `node --version` (22 or newer).

## Request Errors

### Find the right body

Do not guess field names. Read the endpoint's page, which lists every field, which are required, and the limits:
```
docs_search({url: "backlinks/summary/live"})
```
Add `needCodeExample: true` for a complete example request. Example bodies for every endpoint are in `../mcp-patterns/references/endpoint-paths.md`.

### Location and language
Send `location_code` (2840 is United States) or `location_name` with the full name; one of the two is required on most endpoints. An ISO code such as `"US"` in `location_name` is rejected.

| Wrong | Correct |
|-------|---------|
| `"location_name": "US"` | `"location_name": "United States"` or `"location_code": 2840` |
| `"location_name": "UK"` | `"location_name": "United Kingdom"` or `"location_code": 2826` |
| `"language_code": "English"` | `"language_code": "en"` or `"language_name": "English"` |

Look names and codes up with a free GET:
```
api_request({method: "GET", path: "/v3/serp/google/locations/US"})
```

### Required fields
Each endpoint has required fields. Common misses:
- `/v3/on_page/lighthouse/live/json` needs `url`
- `/v3/backlinks/summary/live` needs `target` (a domain without `https://` and `www.`, or an absolute page URL)
- `/v3/content_analysis/phrase_trends/live` needs `keyword` and `date_from`
- `/v3/dataforseo_labs/google/domain_intersection/live` needs `target1` and `target2`, not a `targets` object
- `/v3/ai_optimization/llm_mentions/search_mentions/live` needs a `target` array with at least one included entity
- `/v3/ai_optimization/chat_gpt/llm_responses/live` needs `user_prompt` and `model_name`
- A Live endpoint takes one task: `data` is an array with one object

### Filter syntax
Filters are `[["field", "operator", value], "and", ["field2", "operator", value2]]`. Field names are per API; list them with:
```
docs_search({url: "backlinks/filters"})
docs_search({url: "dataforseo_labs/filters"})
docs_search({url: "ai_optimization/llm_mentions/filters"})
```

### The response looks cut down
That is `.ai` mode, the default: empty fields are dropped, `limit` and `depth` default to 10, and the envelope has no `cost`. Set `limit` or `depth` explicitly, or send the call with `noAiMode: true` if a field you need is missing.

## Empty Results

| Scenario | Likely Cause | Action |
|----------|-------------|--------|
| Backlinks return empty | Domain is new or has no indexed backlinks | Verify the domain has been live and linked to for 30+ days |
| Keyword volume is 0 | No search data for that keyword in that location | Try a broader keyword or a different location |
| LLM mentions return empty | Domain not cited by LLMs for the tracked queries | Normal for smaller or newer sites; focus on content optimization |
| LLM mentions empty for a non-US location | ChatGPT data is United States and English only | Use `"platform": "google"` or the US location |
| SERP returns no results | Wrong location and language combination | Check valid combinations with the locations and languages GET endpoints |
| Content analysis returns empty | Keyword too niche or misspelled | Try broader or alternative phrasing |

Empty results are not errors. DataForSEO has no data for that query, which is itself information.

## Cost Model

DataForSEO bills **per request**, and prices differ per endpoint; some are billed per result row or per 10 SERP results. The documentation tools and the lookup GETs are free; every `api_request` to a data endpoint is paid.

- **Every data request costs money.** Do not call speculatively. The `cost-awareness` skill is the gate.
- **Bulk endpoints are cheaper per unit** than loops (for example `/v3/backlinks/bulk_ranks/live` against many summary calls).
- **Monitor usage** at [app.dataforseo.com](https://app.dataforseo.com) under Account, API Usage.
- **Set budget alerts** in the DataForSEO dashboard.

## Common Error Codes

| HTTP Status | DataForSEO Code | Meaning | Action |
|-------------|----------------|---------|--------|
| 200 | 20000 | Success | Response contains data |
| 200 | 20100 | Task created | Async task queued (not used by Live endpoints) |
| 400 | 40000 | Bad request | Check required parameters |
| 400 | 40001 | Invalid field | Parameter name or value is wrong |
| 400 | 40002 | Invalid value | Value format or range is incorrect |
| 401 | 40100 | Unauthorized | Check credentials |
| 402 | 40200 | Payment required | Account balance depleted |
| 403 | 40300 | Forbidden | Endpoint not available on your plan |
| 404 | 40400 | Not found | The path does not exist; check it against `docs_index` |
| 429 | 42900 | Rate limited | Too many requests; add delays |
| 500 | 50000 | Internal error | DataForSEO server issue; retry or escalate |

The full list: `docs_search({url: "appendix/errors"})`.

## When to Escalate

- **Persistent 500 errors**: check the [DataForSEO status page](https://status.dataforseo.com). If the service is up, contact DataForSEO support with the request body and the error response.
- **Data seems wrong**: compare DataForSEO results with a manual Google search for the same query in the same location. DataForSEO data may lag by hours or days.
- **MCP server crashes repeatedly**: check `node --version` (22 or newer), try `npx clear-npx-cache` and restart. If it persists, check the npm package page for known issues.
- **An endpoint is in the docs but the call fails**: confirm the path with `docs_index` and the body with `docs_search`; the server forwards whatever you send.
- **Account or billing issues**: these cannot be resolved through the MCP. Log in at [app.dataforseo.com](https://app.dataforseo.com) or contact DataForSEO support.
