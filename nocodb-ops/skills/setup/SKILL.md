---
name: setup
description: |
  Verify NocoDB connection and MCP setup. Use when:
  - "check my NocoDB connection"
  - "verify MCP is working"
  - "test NocoDB setup"
  - "is NocoDB connected?"
  - "troubleshoot NocoDB access"
---

# NocoDB Setup Verification

## Prerequisites

Before running verification, confirm these environment variables are set:

| Variable | Required | Description |
|----------|----------|-------------|
| `NOCODB_MCP_URL` | Yes (MCP) | Full NocoDB MCP endpoint URL including path (e.g., `https://your-instance.com/mcp/your-path-id`). Get this from NocoDB → Integrations → MCP. |
| `NOCODB_MCP_TOKEN` | Yes (MCP) | NocoDB `xc-mcp-token` used by the MCP server. Generate in NocoDB → Integrations → MCP. |
| `NOCODB_URL` | Yes (CLI / API) | Base NocoDB instance URL (e.g., `https://your-instance.com`). Used by the CLI and direct REST API calls. |
| `NOCODB_API_TOKEN` | Yes (CLI / API) | NocoDB API token. Generate in NocoDB → Account Settings → API Tokens. |
| `NOCODB_VERBOSE` | No | Set to `1` to show resolved IDs |

The plugin's `.mcp.json` uses `${NOCODB_MCP_URL}` and `${NOCODB_MCP_TOKEN}` (via `xc-mcp-token` header) to configure the `nocodb` HTTP MCP server. The CLI uses `${NOCODB_URL}` and `${NOCODB_API_TOKEN}`.

Also confirm:
1. **MCP server connected** -- the `nocodb` entry is active
2. **Base accessible** -- at least one NocoDB base is shared with your token

## Verification Steps

Run these checks in order. Stop at the first failure and check the troubleshooting table below.

### Step 1 -- Test connection

Call `mcp__nocodb__getTablesList` with no parameters.

- **Pass:** Returns a list of table names and IDs.
- **Fail:** Connection error or authentication error. See troubleshooting.

### Step 2 -- Verify read access

Pick any table ID from Step 1. Call `mcp__nocodb__queryRecords` with that `tableId` and `pageSize: 1`.

- **Pass:** Returns one record (or an empty list if the table has no data).
- **Fail:** Permission error or invalid table ID.

### Step 3 -- Verify count access

Call `mcp__nocodb__countRecords` with the same `tableId`.

- **Pass:** Returns a number (even zero is fine).
- **Fail:** Aggregation permissions may be restricted.

### Step 4 -- Verify base info

Call `mcp__nocodb__getBaseInfo` with no parameters.

- **Pass:** Returns base name, ID, and metadata.
- **Fail:** Token may lack base-level access.

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| "Protected resource does not match" | `NOCODB_MCP_URL` is missing the `/mcp/{path-id}` suffix | Use full MCP endpoint URL from NocoDB Integrations page |
| Connection refused | MCP server not running or wrong URL | Check `.mcp.json` URL and restart MCP |
| 401 Unauthorized | Invalid or expired `NOCODB_MCP_TOKEN` (`xc-mcp-token`) | Regenerate the MCP token in NocoDB → Integrations → MCP |
| 403 Forbidden | Token lacks permission for this base | Share the base with your token's user |
| Timeout | Network issue or server overloaded | Check server status, try again |
| Empty table list | No tables in the base, or wrong base | Verify base ID in MCP config |
| "Tool not found" | MCP server name mismatch | Confirm the server is named `nocodb` in `.mcp.json` |

## What This Skill Does NOT Cover

- **Installing or configuring the MCP server** -- that is an admin task handled during provisioning.
- **Creating API tokens** -- generate tokens in your NocoDB instance under Account Settings.
- **Database or base creation** -- create bases through the NocoDB web interface first.

## After Verification

Once all steps pass, you are ready to:

- Browse tables and schemas with the **mcp-patterns** skill
- Create, read, update, and delete records with the **record-management** skill
- Build filtered views and reports with other plugin skills
