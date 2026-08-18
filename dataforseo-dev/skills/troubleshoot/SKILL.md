---
name: troubleshoot
description: This skill should be used when the user encounters "DataForSEO errors", "DataForSEO not working", "DataForSEO connection issues", "debug DataForSEO", "DataForSEO MCP problems", or needs to diagnose and fix common problems with DataForSEO MCP tools.
---

# Troubleshoot

Diagnose and fix common problems with DataForSEO MCP tools — connection failures, authentication errors, parameter mistakes, empty results, and cost management.

## Quick Diagnostics

When something is not working, run this sequence to isolate the problem:

### Step 1 — Connectivity Test
```
Tool: serp_locations
Input: {
  "country_iso_code": "US"
}
```

This is the lightest DataForSEO call. If it returns location data, the MCP server is running and authenticated. If it fails, the problem is connection or auth.

### Step 2 — Check the Error
- **No response / timeout** → MCP server is not running. See "MCP Server Startup Issues" below.
- **401 Unauthorized** → Wrong credentials. See "Authentication Errors" below.
- **400 Bad Request** → Invalid parameters. See "Parameter Errors" below.
- **500 Internal Server Error** → DataForSEO server issue. See "When to Escalate" below.

### Step 3 — Verify Tool Name
DataForSEO MCP exposes 70+ tools. Confirm you are calling the correct tool name. Tool names follow a pattern: `{api_group}_{endpoint}` (e.g., `backlinks_summary`, `on_page_lighthouse`, `serp_organic_live_advanced`). If a tool is not found, the MCP server may be an older version — see "MCP Server Startup Issues" for update instructions.

## Authentication Errors

DataForSEO uses **username and password** (not API keys). These are set as environment variables in the MCP configuration.

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Wrong or missing credentials | Verify `DATAFORSEO_USERNAME` and `DATAFORSEO_PASSWORD` in `.mcp.json` env block |
| 403 Forbidden | Account suspended or plan limits exceeded | Log in at app.dataforseo.com to check account status |
| "Invalid credentials" in response | Typo in username or password | Copy-paste credentials directly from DataForSEO dashboard |

The `.mcp.json` should contain:
```json
{
  "mcpServers": {
    "dataforseo": {
      "command": "npx",
      "args": ["-y", "dataforseo-mcp-server@latest"],
      "env": {
        "DATAFORSEO_USERNAME": "${DATAFORSEO_USERNAME}",
        "DATAFORSEO_PASSWORD": "${DATAFORSEO_PASSWORD}"
      }
    }
  }
}
```

The `${DATAFORSEO_USERNAME}` and `${DATAFORSEO_PASSWORD}` placeholders are resolved from your environment. Verify these are set in your shell profile or Claude Desktop settings.

## MCP Server Startup Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Tool not found" | MCP server not started or wrong package | Restart Claude Code; verify `.mcp.json` exists in plugin root |
| "npx: command not found" | Node.js not installed or not in PATH | Install Node.js >= v20 from nodejs.org |
| Server starts then crashes | npx cache corrupted | Run `npx clear-npx-cache` then restart |
| Old tool names / missing tools | Cached old package version | Run `npx clear-npx-cache` to force re-download of `@latest` |
| "ENOENT" or "spawn error" | `npx` path not found by Claude Code | Use absolute path to npx: replace `"command": "npx"` with full path (e.g., `"/usr/local/bin/npx"`) |

To verify Node.js version: `node --version` (must be >= v20).

## Parameter Errors

### Location Names
Location must be the **exact full country name**, not an ISO code.

| Wrong | Correct |
|-------|---------|
| `"US"` | `"United States"` |
| `"UK"` | `"United Kingdom"` |
| `"DE"` | `"Germany"` |

Use `serp_locations` to find exact location names and codes:
```
Tool: serp_locations
Input: {
  "country_iso_code": "US"
}
```

### Required Fields
Each tool has required parameters. Common missing fields:
- `on_page_lighthouse` requires `url`
- `backlinks_summary` requires `target` (domain or URL)
- `content_analysis_phrase_trends` requires `keyword` AND `date_from`
- `ai_opt_llm_ment_search` requires `targets` array with at least one object

### Filter Syntax
DataForSEO uses a specific filter format: `["field", "operator", "value"]`. Nested filters use arrays of arrays. Check available filters per endpoint:
```
Tool: backlinks_available_filters
Input: {}
```
```
Tool: dataforseo_labs_available_filters
Input: {}
```
```
Tool: ai_optimization_llm_mentions_filters
Input: {}
```

## Empty Results

| Scenario | Likely Cause | Action |
|----------|-------------|--------|
| Backlinks return empty | Domain is new or has no indexed backlinks | Verify domain has been live and linked to for 30+ days |
| Keyword volume = 0 | Keyword has no search data in that location | Try broader keyword or different location |
| LLM mentions return empty | Domain not cited by LLMs for tracked queries | Normal for smaller/newer sites — focus on content optimization |
| SERP returns no results | Wrong location/language combination | Check valid combinations with `serp_locations` |
| Content analysis returns empty | Keyword too niche or misspelled | Try broader or alternative phrasing |

Empty results are NOT errors. They mean DataForSEO has no data for that query — which is itself valuable information (your keyword may be too niche or your domain too new).

## Cost Model

DataForSEO charges **per API call**, not by rate limits or monthly subscriptions (though minimums may apply). Each MCP tool call translates to one or more API requests.

Key cost facts:
- **Every tool call costs credits.** Be intentional — do not call tools speculatively.
- **Different endpoints have different costs.** Lighthouse and SERP scraping cost more than keyword data.
- **Bulk endpoints are cheaper per-unit** than individual calls (e.g., `backlinks_bulk_ranks` vs. calling `backlinks_summary` in a loop).
- **Monitor usage** at [app.dataforseo.com](https://app.dataforseo.com) under Account > API Usage.
- **Set budget alerts** in the DataForSEO dashboard to avoid unexpected charges.

## Common Error Codes

| HTTP Status | DataForSEO Code | Meaning | Action |
|-------------|----------------|---------|--------|
| 200 | 20000 | Success | Response contains data |
| 200 | 20100 | Task created | Async task queued (not used in live endpoints) |
| 400 | 40000 | Bad request | Check required parameters |
| 400 | 40001 | Invalid field | Parameter name or value is wrong |
| 400 | 40002 | Invalid value | Value format or range is incorrect |
| 401 | 40100 | Unauthorized | Check credentials |
| 402 | 40200 | Payment required | Account balance depleted |
| 403 | 40300 | Forbidden | Endpoint not available on your plan |
| 404 | 40400 | Not found | Endpoint does not exist — check tool name |
| 429 | 42900 | Rate limited | Too many concurrent requests — add delays |
| 500 | 50000 | Internal error | DataForSEO server issue — retry or escalate |

## When to Escalate

- **Persistent 500 errors** → Check [DataForSEO status page](https://status.dataforseo.com). If the service is up, contact DataForSEO support with the request payload and error response.
- **Data seems wrong** → Compare DataForSEO results with a manual Google search for the same query in the same location. Note that DataForSEO data may lag by hours or days.
- **MCP server crashes repeatedly** → Check Node.js version (`node --version` must be >= v20). Try `npx clear-npx-cache` and restart. If it persists, check the npm package page for known issues.
- **Tool exists in docs but not in MCP** → The MCP server may not expose all DataForSEO endpoints. Check the `dataforseo-mcp-server` npm package documentation for the list of supported tools.
- **Account or billing issues** → These cannot be resolved through the MCP. Log in at [app.dataforseo.com](https://app.dataforseo.com) or contact DataForSEO support directly.
