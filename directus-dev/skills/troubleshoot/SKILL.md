---
name: troubleshoot
description: Directus troubleshooting — common errors, diagnostics, MCP connection issues, permission problems, schema conflicts. This skill should be used when the user encounters "Directus errors", "Directus not working", "Directus connection issues", "Directus 403/422/500 errors", or needs to diagnose and fix problems.
---

# Troubleshooting

Common errors, diagnostics, and fixes for Directus MCP and API.

## Quick Diagnostics

### Check MCP Connection

Call the `schema` tool with no parameters. If it returns collections, MCP is connected.

```json
Tool: schema
Input: {}
```

If this fails, the MCP server is not reachable or the token is invalid.

### Check API Health

```bash
# Simple ping
curl "${DIRECTUS_URL}/server/ping"
# Should return: "pong"

# Detailed health
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

**Fix:** Check the MCP user's role has read access to `directus_collections`, `directus_fields`, `directus_relations`.

### Tool not found

**Cause:** MCP server ID doesn't match tool prefix.

**Fix:** List available tools. If your MCP server is registered as `directus-1`, tools are `mcp__directus-1__*`, not `mcp__directus__*`.

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
- Check user's role permissions: Settings > Roles > [role] > Permissions
- Common missing permissions:
  - Read on system collections (`directus_collections`, `directus_fields`)
  - Create/Update on target collections
  - Schema management permissions for collection/field creation
- For MCP: ensure the MCP user has permissions matching intended operations

**403 on file assets (`/assets/{id}`)** — the most common 403 issue when integrating with frontends:
- Directus file assets require authentication by default — unauthenticated requests to `/assets/{id}` return 403
- **Fix option 1:** Add `?access_token=TOKEN` to asset URLs (quick, works for server-rendered pages)
- **Fix option 2:** Grant the Public role read access to `directus_files` (Settings > Roles > Public > directus_files > enable Read) — preferred for public-facing sites
- When using `next/image`, the 403 manifests as broken/missing images with no obvious error since Next.js proxies through `/_next/image`

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

### 500 Internal Server Error

**Cause:** Server-side error.

**Fix:**
- Check Directus server logs
- May indicate database connection issues
- May indicate extension errors

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
```json
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

### Check What a Role Can Do

```bash
curl "${DIRECTUS_URL}/permissions?filter[role][_eq]=ROLE_UUID" \
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
