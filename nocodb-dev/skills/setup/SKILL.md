---
name: setup
description: |
  Verify NocoDB connection for schema-development work — both transports (MCP + CLI/API). Use when:
  - "check NocoDB dev setup"
  - "verify NocoDB API access"
  - "is the nc CLI working?"
  - "can I modify schema?"
  - "test NocoDB MCP connection"
---

# NocoDB Dev Setup Verification

`nocodb-dev` uses two NocoDB surfaces:

- **MCP** — discovery only (`getTablesList`, `getTableSchema`, `getBaseInfo`). Authenticated by `xc-mcp-token`.
- **CLI / REST API** — every schema write (table, field, view, hook). Authenticated by an API token.

Both must work before you can plan and apply schema changes safely.

## Required Environment Variables

| Variable | Required | Surface | Description |
|----------|----------|---------|-------------|
| `NOCODB_MCP_URL` | Yes (MCP) | MCP | Full MCP endpoint URL **including the path-id**, e.g. `https://your-instance.com/mcp/ncc17zpg5n7v9vs8`. From NocoDB → Integrations → MCP. |
| `NOCODB_MCP_TOKEN` | Yes (MCP) | MCP | `xc-mcp-token` minted in NocoDB → Integrations → MCP. |
| `NOCODB_URL` | Yes (CLI/API) | API/CLI | Base instance URL, e.g. `https://your-instance.com`. Used by `nc` and direct REST calls. |
| `NOCODB_API_TOKEN` | Yes (CLI/API) | API/CLI | API token from NocoDB → Account Settings → API Tokens. |
| `NOCODB_VERBOSE` | No | CLI | Set to `1` to print resolved IDs from the CLI. |

The two token pairs are **distinct**. Sharing one variable across both transports is the regression captured in `LEARNINGS.md` of the `nocodb-ops` plugin (2026-05-06).

## Verification Steps

Run in order. Stop at the first failure and consult the troubleshooting table.

### Step 1 — MCP discovery

Call `mcp__nocodb__getTablesList` with no parameters.

- **Pass:** returns a list of table names and IDs.
- **Fail:** see Troubleshooting → MCP rows.

### Step 2 — MCP schema read

Pick any table ID from Step 1. Call `mcp__nocodb__getTableSchema` with `tableId`.

- **Pass:** returns columns + views.
- **Fail:** the token may lack base-level access.

### Step 3 — CLI base list

```bash
nc base:list
```

- **Pass:** returns one or more base IDs (prefix `p`).
- **Fail:** see Troubleshooting → CLI rows.

### Step 4 — CLI table list

Using a base ID from Step 3:

```bash
nc table:list <baseId>
```

- **Pass:** returns table IDs (prefix `m`).
- **Fail:** the API token may not be shared with that base.

### Step 5 — Optional API ping

```bash
curl -sS -H "xc-token: $NOCODB_API_TOKEN" "$NOCODB_URL/api/v3/data/<baseId>/<tableId>/count" | jq
```

- **Pass:** returns `{ "count": <number> }`.
- **Fail:** likely auth or path issue — confirm token has `read` scope on the base.

## Troubleshooting

| Symptom | Surface | Likely cause | Fix |
|---------|---------|--------------|-----|
| "Protected resource does not match" | MCP | `NOCODB_MCP_URL` is missing the `/mcp/<path-id>` suffix | Use the full MCP endpoint URL from NocoDB → Integrations → MCP |
| 401 Unauthorized | MCP | `NOCODB_MCP_TOKEN` invalid/expired | Regenerate the token in NocoDB → Integrations → MCP |
| 401 Unauthorized | CLI/API | `NOCODB_API_TOKEN` invalid/expired | Regenerate in NocoDB → Account Settings → API Tokens |
| 403 Forbidden | Either | Token lacks permission for the base | Share the base with the token's user, or use a higher-privilege token |
| `nc: command not found` | CLI | CLI not installed | `npx skills add nocodb/agent-skills` |
| "Tool not found" `mcp__nocodb__*` | MCP | Server name mismatch | Confirm `.mcp.json` names the server `nocodb` (not `nocodb-1`) |
| Connection refused | Either | Server down or wrong host | `curl -sSI $NOCODB_URL` to confirm reachability |
| Empty `nc base:list` | CLI | Token has no shared bases | Have an admin share at least one base with the token's user |

## What This Skill Does NOT Cover

- Provisioning a NocoDB instance (admin task).
- Generating tokens (done in NocoDB UI).
- Selecting which base / source to operate on (use the **table-management** skill).
- Schema modification itself (use **table-management**, **field-management**, **view-management**, **webhooks**).

## After Verification

Once all steps pass:

1. Read **mcp-patterns** to understand what the MCP can and cannot do.
2. Read **api-reference** when you need the REST API surface.
3. Read **cli-reference** for `nc` command syntax.
4. Use **table-management**, **field-management**, **view-management**, **webhooks** to make changes.
