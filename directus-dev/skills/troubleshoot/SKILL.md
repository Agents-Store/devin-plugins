---
name: troubleshoot
description: Directus troubleshooting — common errors, diagnostics, MCP connection issues, permission problems, schema conflicts. This skill should be used when the user encounters "Directus errors", "Directus not working", "Directus connection issues", "Directus 403/422/500 errors", or needs to diagnose and fix problems.
---

# Troubleshooting

Common errors, diagnostics, and fixes for Directus MCP and API.

## Quick Diagnostics

### Check MCP Connection

Call the `schema` tool with no parameters. If it returns collections, MCP is connected.

```text
Tool: schema
Input: {}
```

If this fails, the MCP server is not reachable or the token is invalid.

### Check API Health

```bash
# Liveness: public, answers once the HTTP server runs (no database check)
curl "${DIRECTUS_URL}/server/ping"
# Should return: "pong"

# Dependency health (database, Redis, storage, email).
# Directus 12 answers 403 FORBIDDEN without a token.
curl "${DIRECTUS_URL}/server/health" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}"

# Test token validity
curl "${DIRECTUS_URL}/users/me" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}"
```

## MCP-Specific Errors

### "action is required"

**Cause:** Missing `action` parameter in MCP tool call.

**Fix:** Always include `"action": "read"` (or create/update/delete):
```json
{ "action": "read", "collection": "posts", "query": { "limit": 10 } }
```

### "collection is required"

**Cause:** `items`, `fields` tools need a collection name.

**Fix:** Add `"collection": "your_collection_name"`.

### "data must be an array"

**Cause:** Items create expects `data` as an array.

**Fix:** Wrap single items in an array:
```json
{ "action": "create", "collection": "posts", "data": [{ "title": "Test" }] }
```

### Empty response from schema

**Cause:** User has no read permissions on collections.

**Fix:** Check that a policy attached to the MCP user (directly or through the user's role) grants read access to `directus_collections`, `directus_fields`, `directus_relations`.

### Tool not found

**Cause:** MCP server ID doesn't match tool prefix.

**Fix:** List available tools. If your MCP server is registered as `directus-1`, tools are `mcp__directus-1__*`, not `mcp__directus__*`.

### Only `search`, `execute` and `schema` are listed

**Cause:** The MCP URL ends in `?tool_mode=registry`. Registry mode exposes three root tools instead of the individual ones.

**Fix:** Either work through them (`search` finds a tool and loads its input details, `execute` runs it with the tool name and input, `schema` reads the data model directly) or connect to plain `/mcp` if your client has its own tool search. See the `mcp-tools` skill.

### `/mcp` does not respond (`403 MCP must be enabled`)

**Cause:** MCP is disabled by default (the server answers `403 FORBIDDEN`, "MCP must be enabled"), or Directus is below v11.12, or (Directus 12) the instance is over its license limits and the grace period has ended. In that locked-down state GraphQL, WebSockets and MCP are disabled and `/items` calls fail.

**Fix:**
- Enable it in Settings → AI → Model Context Protocol (an administrator can block that toggle with `MCP_ENABLED=false`)
- Check the version with `GET /server/info` (a token is needed for details)
- For a license lock-down, an admin signs in to the Data Studio, where the resolution flow asks for a license or for usage to come back inside the Core tier limits. No data is deleted by enforcement.

### OAuth sign-in loops or is refused

**Cause:** The OAuth server is off or the client registration method is not enabled.

**Fix:** Set `MCP_OAUTH_ENABLED=true`, enable `MCP_OAUTH_CIMD_ENABLED` (preferred) or `MCP_OAUTH_DCR_ENABLED` for clients that need Dynamic Client Registration, set `PUBLIC_URL` to the externally visible URL, restart, then switch the same options on in Settings → AI → Model Context Protocol. If the client cannot do OAuth, use a static token.

## HTTP Status Errors

### 401 Unauthorized

**Cause:** Missing, expired, or invalid token.

**Fix:**
- Check token is included in header: `Authorization: Bearer TOKEN`
- For JWTs: token may have expired (default 900s) — refresh it
- For static tokens: verify in User Directory > user profile > Token field

### 403 Forbidden

**Cause:** User has valid token but insufficient permissions.

**Fix:**
- Permissions live in policies (Directus 11+). Open Settings → Access Policies → [policy] → Permissions, for every policy that reaches the user. The user's effective permissions are the aggregate of the policies attached directly to the user, to the user's role and to that role's parent roles
- A policy with an IP allowlist is dropped entirely when the request comes from another IP
- Common missing permissions:
  - Read on system collections (`directus_collections`, `directus_fields`)
  - Create/Update on target collections
  - Schema management permissions for collection/field creation
- For MCP: ensure the MCP user has permissions matching intended operations
- Since 12.4.0, update/delete by `query` also needs read on the collection's primary key
- Error `COLLECTION_INACTIVE` (403): the collection's status is Inactive, usually because the instance went over its license collection limit. Set it back to Active in the collection settings, or add a license

**403 on file assets (`/assets/{id}`)** — the most common 403 issue when integrating with frontends:
- Directus file assets require authentication by default — unauthenticated requests to `/assets/{id}` return 403
- **Fix option 1 (everything is public):** Grant the Public policy read access to `directus_files` (Settings → Access Policies → Public → `directus_files` → enable Read). Everything unauthenticated requests can reach is controlled by that one policy, so keep it minimal. Without a license this must be an unrestricted rule: a folder filter or a field list is a custom permission rule, and creating it answers `403 RESOURCE_RESTRICTED` (`custom_permission_rules_enabled`; seen on Directus 12.4.1). The consequence is that **every** file of the instance becomes downloadable, and listable through `GET /files`, by anyone. Do not use this on an instance that also stores private uploads
- **Fix option 2 (private or mixed files):** Serve assets through a server route of your own that adds the token server-side, and restrict it to the files you mean to publish (for example by folder, checked in the route)
- **Do not put `?access_token=` into a URL that reaches a browser** (`<img src>`, HTML, or `next/image`, whose `/_next/image?url=` carries the whole source URL into the page): the token is then readable by every visitor and lands in access logs. A static token in a URL is for server-to-server calls only
- When using `next/image`, the 403 manifests as broken/missing images with no obvious error since Next.js proxies through `/_next/image`

**403 on `/server/health`** — Directus 12 requires a token for it. Use `/server/ping` for liveness probes and send a token only when you need dependency status.

### 404 Not Found

**Cause:** Collection, item, or endpoint doesn't exist.

**Fix:**
- Verify collection name with `schema` tool (discovery mode)
- Check item UUID exists before updating/deleting
- Confirm API endpoint path is correct

### 409 Conflict

**Cause:** Unique constraint violation or concurrent modification.

**Fix:**
- Check for duplicate values on unique fields
- Re-read the item before retrying update
- For collections: check if name already exists

### 422 Unprocessable Entity

**Cause:** Validation error — required field missing, wrong data type, or constraint violation.

**Fix:**
- Read the schema to understand required fields: `schema` tool with `keys: ["collection"]`
- Check field types match expected values
- Common issues:
  - String field receiving a number
  - Non-nullable field missing in create
  - UUID field receiving invalid format
  - Relation field referencing non-existent target

### 429 Too Many Requests

**Cause:** Rate limiting.

**Fix:** Wait and retry with exponential backoff. Reduce batch sizes.

### 413 Content Too Large

**Cause:** An import or a schema snapshot (`/schema/diff`, `/schema/apply`, `/utils/import/{collection}`) is larger than `IMPORT_MAX_FILE_SIZE`, which defaults to `50mb` since Directus 12.2.0.

**Fix:** Split the file, or raise `IMPORT_MAX_FILE_SIZE`.

### 500 Internal Server Error

**Cause:** Server-side error.

**Fix:**
- Check Directus server logs
- May indicate database connection issues
- May indicate extension errors
- On Directus 12.4.0, reading `directus_folders` as a non-admin fails with 500 (breaks the File Library and `GET /folders`). Upgrade to 12.4.1 or later

## Directus 12 Notes

| Symptom | Cause | Fix |
|---------|-------|-----|
| SSO users cannot log in, custom permission rules ignored, custom LLM connections fail | Directus 12 enforces licensing. SSO, custom permission rules and custom or self-hosted LLMs need a licensed tier. Upgraded instances get a 30 day grace period | Add a license, or return to Core tier features. Admin sees a reminder at login during the grace period |
| GraphQL, WebSockets and MCP stopped, `/items` calls fail, non-admins cannot log in | Grace period ended and the instance is over its limits | Resolve through the Data Studio resolution flow (license or reduced usage). No data is deleted |
| `LIMIT_EXCEEDED` ("flows limit exceeded", and similar for other resources) when creating something | The Core tier has entitlement limits (user seats, collections, flows and more, see the Directus pricing page). A fresh unlicensed instance hits the flows limit quickly | Delete unused resources or add a license |
| `403 COLLECTION_INACTIVE` on REST, GraphQL, WebSockets, MCP or a flow operation | Collection status is Inactive (12.4.0+) | Set the collection back to Active, or add a license |
| `403` from `/server/health` | Token now required | Use `/server/ping`, or send a token |
| `413` on import or schema diff | `IMPORT_MAX_FILE_SIZE` default `50mb` (12.2.0+) | Raise the limit |
| `ILLEGAL_ASSET_TRANSFORMATION` | Output above `ASSETS_TRANSFORM_IMAGE_MAX_OUTPUT_DIMENSION` (default `6000`, 12.3.0+) at any step of the transformation | Lower the requested size or raise the variable |
| Client IPs show the proxy address, IP allowlists misbehave behind a reverse proxy | `IP_TRUST_PROXY` now defaults to `false` | Set `IP_TRUST_PROXY=true` (or a narrower trust setting) when you run behind a proxy |
| WebSocket connections rejected | `CORS_ORIGIN` is enforced for WebSockets (12.1.0+) | Add the client origin to `CORS_ORIGIN` |
| Flow Update or Delete Items operation does nothing and returns `null` | Empty or missing `key` and `query` no longer target every item (12.3.0+) | Set a `key`, or an explicit `query` such as `{"limit": -1}`. See `flow-automation` |
| `npm`/`npx` missing inside the container | Hardened image (12.1.0+) | Build extensions outside the container, see the Docker local dev skill |

## Schema Errors

### "Collection already exists"

**Fix:** Use `schema` tool to check existing collections before creating.

### "Field already exists"

**Fix:** Read fields first: `fields` tool with `action: "read"` and `collection` name.

### "Related collection does not exist"

**Cause:** Creating a relation to a collection that hasn't been created yet.

**Fix:** Create collections in dependency order. Independent collections first, then dependent ones.

### "Invalid foreign key"

**Cause:** Relation target doesn't exist or field type doesn't match.

**Fix:**
- Ensure both collections exist
- Ensure the M2O field is `uuid` type (matching the target's primary key type)
- Ensure the relation field has been created before creating the relation

## Flow Errors

### Operations not executing

**Cause:** Operations not connected via resolve/reject.

**Fix:**
1. Read the flow: `flows` tool with `action: "read"` and flow key
2. Verify `operation` field on the flow points to the first operation
3. Verify each operation's `resolve`/`reject` points to the next operation

### Condition not matching

**Cause:** Wrong filter syntax in condition operation.

**Fix:** Use nested objects, NOT dot notation:
```jsonc
// CORRECT
{ "$trigger": { "payload": { "status": { "_eq": "published" } } } }

// WRONG — will never match
{ "$trigger.payload.status": { "_eq": "published" } }
```

### Request operation failing

**Cause:** Wrong header or body format.

**Fix:**
- Headers must be array: `[{ "header": "Content-Type", "value": "application/json" }]`
- Body must be stringified JSON: `"{\"key\": \"value\"}"`

### Data chain variable empty

**Cause:** Referencing wrong operation key.

**Fix:** Use the exact `key` value set on the operation. Don't use `$last`.

## Performance Issues

### Slow Queries

- Add `fields` parameter — don't fetch all fields
- Use `limit` — don't fetch all records
- Simplify `deep` queries — nested relation queries are expensive
- Filter at API level, not in code

### Large Batch Operations

- Process in batches of 10-25 items
- Add delays between batches if hitting rate limits
- Use `offset` pagination instead of fetching everything

### MCP Response Timeout

- Reduce query complexity (fewer nested relations)
- Add `limit` to all queries
- Split large operations into smaller sequential calls

## Permission Debugging

### Check What a User Can Do

Permissions belong to policies. Start from what the current token can do:

```bash
curl "${DIRECTUS_URL}/permissions/me" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" | jq .data
```

It lists every collection with an `access` level per action (`none`, `partial`, `full`).

### Find Which Policies Reach a User

```bash
curl "${DIRECTUS_URL}/users/<user-uuid>?fields=email,policies.policy.name,role.name,role.policies.policy.name,role.parent.policies.policy.name" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" | jq .data
```

### Check What a Policy Grants

```bash
curl "${DIRECTUS_URL}/permissions?filter[policy][_eq]=<policy-uuid>&limit=-1" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" | jq '.data[] | {collection, action}'
```

### Common Permission Setup for MCP User

Minimum permissions for a developer MCP user:

| Collection | Actions |
|-----------|---------|
| All user collections | Create, Read, Update, Delete |
| `directus_collections` | Create, Read, Update, Delete |
| `directus_fields` | Create, Read, Update, Delete |
| `directus_relations` | Create, Read, Update, Delete |
| `directus_files` | Create, Read, Update, Delete |
| `directus_folders` | Create, Read, Update, Delete |
| `directus_flows` | Create, Read, Update, Delete |
| `directus_operations` | Create, Read, Update, Delete |
| `directus_users` | Read |
| `directus_roles` | Read |

Enable "Allow Deletes" in MCP settings if deletion via MCP is needed.
