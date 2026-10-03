---
name: troubleshoot
description: |
  Diagnose and fix NocoDB errors, connection issues, and MCP problems. Use when:
  - "NocoDB not working"
  - "connection error"
  - "getting 401 error"
  - "MCP tool not responding"
  - "debug NocoDB"
  - "filter not working"
  - "timeout error"
---

# NocoDB Troubleshooting

Diagnose issues with NocoDB connections, authentication, data operations, and MCP tools.

## Environment Variables

Verify these are set correctly before debugging further:

| Variable | Used by | Check |
|----------|---------|-------|
| `NOCODB_MCP_URL` | MCP | The full MCP endpoint URL — Cloud / licensed: `https://your-instance.com/mcp`; Community Edition: `https://your-instance.com/mcp/<ncId>` |
| `NOCODB_MCP_TOKEN` | MCP | A valid MCP token (`xc-mcp-token` header; created with the MCP connection — see **setup**) |
| `NOCODB_URL` | REST (optional) | Base instance URL (e.g., `https://your-instance.com`) |
| `NOCODB_TOKEN` | REST (optional) | NocoDB API token (NocoDB → Team & Settings → API Tokens) |
| `NOCODB_VERBOSE` | Official script | Optional — set to `1` to see resolved IDs from `nocodb.sh` |

## Quick Diagnostics

Run these checks first to isolate the problem:

1. **Test MCP connection** -- call `mcp__plugin_nocodb-ops_nocodb__getTablesList` with no parameters. If it returns tables, the connection is healthy.
2. **Test authentication** -- a 401 response from MCP means `NOCODB_MCP_TOKEN` is wrong, **revoked**, or the connection was restricted (its Tools & Permissions allowlist) — recreate or re-open the connection where it was created (see **setup**). A 401 from the REST API means `NOCODB_TOKEN` is invalid (regenerate in NocoDB → Team & Settings → API Tokens).
3. **Ask the server who you are** -- `whoami` names the user, the pinned base and the permissions of the credential (Cloud / licensed). A 403 is usually the intersection of that grant with the user's role, not a bug.
4. **Check the edition** -- `listTools category: "records"` working means Cloud / licensed; if it is absent the server is Community Edition and offers the record tools only. View, filter and sort management through MCP exists only on Cloud / licensed (see **nocodb-dev**).

## Connection Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ECONNREFUSED` | NocoDB server is down or unreachable | Verify the server is running and the URL is correct in `.mcp.json` |
| `ETIMEDOUT` | Network timeout reaching the server | Check firewall rules, VPN status, and server availability |
| `ENOTFOUND` | DNS resolution failed for the NocoDB URL | Verify the hostname is correct and DNS is working |
| `CERT_HAS_EXPIRED` | SSL certificate expired on the server | Renew the certificate or set `NODE_TLS_REJECT_UNAUTHORIZED=0` for testing only |
| `ECONNRESET` | Connection dropped mid-request | Retry the request; check server logs for crashes |

## Authentication Errors

| Code | Meaning | Fix |
|------|---------|-----|
| 401 Unauthorized | Token is invalid, revoked, restricted, or missing | Recreate the MCP connection / token and update `NOCODB_MCP_TOKEN` (REST: regenerate the API token under Team & Settings → API Tokens and update `NOCODB_TOKEN`) |
| 403 Forbidden | Token lacks permission for this resource | Share the base or table with the token's user account |
| 403 on write operations | The credential or its user has read-only access | Use a connection with edit access or adjust the user's role |
| Token format error | Wrong token type passed | Use the MCP token for MCP and the API token for REST; do not pass a JWT session token |

## Data Errors

| Code | Meaning | Fix |
|------|---------|-----|
| 404 Not Found | Table, record, or field ID does not exist | Verify the ID is correct; check if the item was deleted |
| 409 Conflict | Duplicate value on a unique field | Change the value or remove the unique constraint |
| 422 Unprocessable | Invalid field value or missing required field | Check the field type and constraints; validate input data |
| 422 on create | Required fields missing from the payload | Include all required fields in the create request |
| 413 Payload Too Large | Request body exceeds size limit | Reduce batch size — MCP write tools take at most 100 records per call anyway |

## Performance Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Slow responses (>5s) | Large table without pagination | Add `pageSize` limit; never request all records at once |
| Timeout on list queries | Complex filter on unindexed field | Simplify the filter or request fewer fields |
| Rate limiting (429) | Too many requests per minute | Add delays between batch operations; reduce parallelism |
| Slow attachment uploads | Large file size | Compress files before upload; check storage backend speed |
| Memory errors | Requesting thousands of records | Paginate with `page` and `pageSize` (default 50, max 200) |

## MCP-Specific Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| "Tool not found" for `mcp__plugin_nocodb-ops_nocodb__<tool>` | The plugin's MCP server did not start (missing `NOCODB_MCP_URL` / `NOCODB_MCP_TOKEN`), or the tool is a hidden one | Set both variables in the shell that launched Claude Code and restart; for hidden tools (`upsertRecords`, `importCsv`, `listTrash`, …) call `listTools(category)` then `callTool` |
| Input validation error on `records` | More than 100 records in one write call | Split into batches of 100 or fewer; the whole call was rejected, nothing was written |
| `Expected object, received string at sort[0]` | `sort` sent as strings (`"-Date"`, `["Name"]`) | `sort: [{ "field": "Date", "direction": "desc" }]` |
| `'<date>' is not supported` | Bare date after the operator in a `where` string | `(Date,gte,exactDate,2026-06-01)`; structured: `sub_operator: "exactDate"` |
| `Operation btw is not supported for type <T>` | `btw` / `nbtw` on a number, rating, duration, date or checkbox field | Two bounds: `(F,gte,A)~and(F,lte,B)` |
| Aggregate: `Required at aggregations` / `Required at filterGroups` | Wrong parameter names, or `filterGroups` missing | `aggregations: [{field, type}]` and `filterGroups: [{ "alias": "All" }]` — both required |
| Wrong parameter format | Passing string instead of object | Check parameter types in the MCP tool schema |
| Filter returns no results | Incorrect where syntax, or a trailing space in a name or value | Use `(Field,operator,value)` with exact field names, or the structured `filter` |
| Filter syntax error | Missing parentheses or wrong operator | Wrap each condition in `()` and use valid operators like `eq`, `gt`, `like` |
| Linked records not showing | Link field not expanded | Use the `fields` parameter to include the link field name |
| Empty response on valid table | View filter hiding records | Query without `viewId` to get all records regardless of view filters |
| Create returns error | JSON parsing failure | Validate JSON payload; escape special characters in values |

## Common Filter Mistakes

| Wrong | Right | Issue |
|-------|-------|-------|
| `Status = Active` | `(Status,eq,Active)` | Must use parenthesized comma syntax |
| `(status,eq,Active)` | `(Status,eq,Active)` | Field names in `where` are case-sensitive (the structured `filter` is not) |
| `(Amount,>,500)` | `(Amount,gt,500)` | Use named operators, not symbols |
| `(Due,lt,YYYY-MM-DD)` | `(Due,lt,exactDate,YYYY-MM-DD)` | A date field needs a sub-operator; `today`, `daysAgo,7`, `exactDate,<date>` … |
| `(Due,btw,A,B)` on a date or number | `(Due,gte,exactDate,A)~and(Due,lte,exactDate,B)` | `btw` / `nbtw` are rejected on those types |
| `(A,eq,1) AND (B,eq,2)` | `(A,eq,1)~and(B,eq,2)` | Use `~and` not `AND` |
| `(A,eq,1)~and (B,eq,2)` | `(A,eq,1)~and(B,eq,2)` | No whitespace after `~and` / `~or` / `~not` |

## When to Escalate

Escalate to an administrator or NocoDB support when:

- **500 Internal Server Error** persists after retrying -- indicates a server-side bug
- **Data corruption** -- records show wrong values or disappear unexpectedly
- **MCP server crashes** repeatedly -- check MCP server logs for stack traces
- **Permission model broken** -- user has correct role but still gets 403
- **Replication lag** -- reads return stale data after successful writes (self-hosted clusters)

## Diagnostic Checklist

Use this checklist to report issues:

1. NocoDB instance URL and version
2. Error message (exact text)
3. HTTP status code (if applicable)
4. MCP tool name and parameters used
5. Whether the same operation works in the NocoDB web interface
6. Whether the issue is consistent or intermittent
