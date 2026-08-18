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
| `NOCODB_MCP_URL` | MCP | Must be the full MCP endpoint URL (e.g., `https://your-instance.com/mcp/your-path`) |
| `NOCODB_MCP_TOKEN` | MCP | Must be a valid `xc-mcp-token` value (NocoDB → Integrations → MCP) |
| `NOCODB_URL` | CLI / API | Base instance URL (e.g., `https://your-instance.com`) |
| `NOCODB_API_TOKEN` | CLI / API | NocoDB API token (NocoDB → Account Settings → API Tokens) |
| `NOCODB_VERBOSE` | CLI | Optional — set to `1` to see resolved IDs in CLI output |

## Quick Diagnostics

Run these checks first to isolate the problem:

1. **Test MCP connection** -- call `mcp__nocodb__getTablesList` with no parameters. If it returns tables, the connection is healthy.
2. **Test authentication** -- a 401 response from MCP means `NOCODB_MCP_TOKEN` is invalid or expired (regenerate in NocoDB → Integrations → MCP). A 401 from the CLI/API means `NOCODB_API_TOKEN` is invalid (regenerate in NocoDB → Account Settings → API Tokens).
3. **Check API version** -- confirm your NocoDB instance version supports the operations you need. View/filter/sort management requires v0.200+ or Enterprise.

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
| 401 Unauthorized | Token is invalid, expired, or missing | Regenerate the API token in NocoDB settings and update `.mcp.json` |
| 403 Forbidden | Token lacks permission for this resource | Share the base or table with the token's user account |
| 403 on write operations | Token has read-only access | Create a new token with full access or adjust user role |
| Token format error | Wrong token type passed | Use an API token (starts with prefix), not a JWT session token |

## Data Errors

| Code | Meaning | Fix |
|------|---------|-----|
| 404 Not Found | Table, record, or field ID does not exist | Verify the ID is correct; check if the item was deleted |
| 409 Conflict | Duplicate value on a unique field | Change the value or remove the unique constraint |
| 422 Unprocessable | Invalid field value or missing required field | Check the field type and constraints; validate input data |
| 422 on create | Required fields missing from the payload | Include all required fields in the create request |
| 413 Payload Too Large | Request body exceeds size limit | Reduce batch size for bulk operations (max ~1000 records) |

## Performance Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Slow responses (>5s) | Large table without pagination | Add `pageSize` limit; never request all records at once |
| Timeout on list queries | Complex filter on unindexed field | Simplify the filter or request fewer fields |
| Rate limiting (429) | Too many requests per minute | Add delays between batch operations; reduce parallelism |
| Slow attachment uploads | Large file size | Compress files before upload; check storage backend speed |
| Memory errors | Requesting thousands of records | Paginate with `page` and `size` parameters |

## MCP-Specific Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| "Tool not found" | MCP server name mismatch | Verify the server is named `nocodb` in `.mcp.json` |
| Wrong parameter format | Passing string instead of object | Check parameter types in the MCP tool schema |
| Filter returns no results | Incorrect where syntax | Use `(Field,operator,value)` format with exact field names |
| Filter syntax error | Missing parentheses or wrong operator | Wrap each condition in `()` and use valid operators like `eq`, `gt`, `like` |
| Linked records not showing | Link field not expanded | Use the `fields` parameter to include the link field name |
| Empty response on valid table | View filter hiding records | Query without `viewId` to get all records regardless of view filters |
| Create returns error | JSON parsing failure | Validate JSON payload; escape special characters in values |

## Common Filter Mistakes

| Wrong | Right | Issue |
|-------|-------|-------|
| `Status = Active` | `(Status,eq,Active)` | Must use parenthesized comma syntax |
| `(status,eq,Active)` | `(Status,eq,Active)` | Field names are case-sensitive |
| `(Amount,>,500)` | `(Amount,gt,500)` | Use named operators, not symbols |
| `(Date,eq,today)` | `(Date,today,)` | Date operators go in the operator position |
| `(A,eq,1) AND (B,eq,2)` | `(A,eq,1)~and(B,eq,2)` | Use `~and` not `AND` |

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
