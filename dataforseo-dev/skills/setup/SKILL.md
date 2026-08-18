---
name: setup
description: This skill should be used when the user asks to "verify DataForSEO connection", "check DataForSEO MCP", "test DataForSEO setup", "is DataForSEO working", or needs to confirm that the DataForSEO MCP integration is operational.
---

# DataForSEO Setup Verification

Verify that the DataForSEO MCP connection is working correctly.

## Prerequisites

- DataForSEO MCP server configured (via plugin's `.mcp.json` or user settings)
- Valid DataForSEO account with API access (username + password)
- Node.js >= v20.0.0 installed

## Verification Steps

### 1. Check MCP Connection

Run a lightweight read operation to verify connectivity:

```
Tool: mcp__dataforseo__serp_locations
Input: { "country_iso_code": "US" }
```

**Expected result:** Returns a list of US locations without errors.

### 2. Test Authenticated API Access

Run a keyword data request to verify credentials work:

```
Tool: mcp__dataforseo__dataforseo_labs_google_keyword_overview
Input: { "keywords": ["test"], "location_name": "United States", "language_code": "en" }
```

**Expected result:** Returns keyword metrics (search_volume, cpc, competition).

### 3. Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Connection refused | MCP server not started | Check Node.js version (`node -v` must be >= 20) |
| 401 Unauthorized | Wrong credentials | Verify `DATAFORSEO_USERNAME` and `DATAFORSEO_PASSWORD` env vars |
| `npx` error | Package not found | Run `npx -y dataforseo-mcp-server@latest` manually to test |
| Timeout | Network or firewall | Check internet connectivity to `api.dataforseo.com` |
| Empty results | Account has no credits | Check balance at app.dataforseo.com |

### 4. Credential Format

DataForSEO uses **username/password authentication** (not API keys):
- `DATAFORSEO_USERNAME` — your account email (e.g., `user@example.com`)
- `DATAFORSEO_PASSWORD` — your account password

Obtain credentials at [app.dataforseo.com](https://app.dataforseo.com).

## What This Skill Does NOT Cover

- Creating a DataForSEO account (see [dataforseo.com](https://dataforseo.com))
- Billing and credit management (see app.dataforseo.com dashboard)
- Configuring environment variables (set `DATAFORSEO_USERNAME` and `DATAFORSEO_PASSWORD` in your environment)
