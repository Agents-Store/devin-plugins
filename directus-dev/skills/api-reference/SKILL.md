---
name: api-reference
description: Directus REST API endpoints, curl examples, authentication patterns, schema migration pipeline. This skill should be used when the user asks for "Directus API endpoints", "Directus REST API", "Directus curl examples", "Directus API documentation", "Directus HTTP requests", or needs specific endpoint details for scripting.
disable-model-invocation: true
---

# Directus REST API Reference

Curated REST API endpoints for scripting and direct HTTP access. For full docs, see https://docs.directus.io/reference/introduction.html

## Authentication

### Static Token (recommended for scripts)

```bash
curl -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  "${DIRECTUS_URL}/items/posts"
```

### Login for Temporary JWT

```bash
curl -X POST "${DIRECTUS_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret"}' | jq .data
```

Returns `access_token` (~900s TTL) and `refresh_token`.

### Refresh Token

```bash
curl -X POST "${DIRECTUS_URL}/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

## Core Item Endpoints

### List Items

```bash
GET /items/{collection}?fields=id,title,status&limit=25&sort=-date_created

curl -s -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  "${DIRECTUS_URL}/items/posts?fields=id,title,status&limit=25&sort=-date_created" | jq .
```

### Get Single Item

```bash
GET /items/{collection}/{id}

curl -s -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  "${DIRECTUS_URL}/items/posts/uuid-here" | jq .data
```

### Create Item

```bash
POST /items/{collection}

curl -s -X POST \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Post", "status": "draft"}' \
  "${DIRECTUS_URL}/items/posts" | jq .data
```

### Update Item

```bash
PATCH /items/{collection}/{id}

curl -s -X PATCH \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"status": "published"}' \
  "${DIRECTUS_URL}/items/posts/uuid-here" | jq .data
```

### Delete Item

```bash
DELETE /items/{collection}/{id}

curl -s -X DELETE \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  "${DIRECTUS_URL}/items/posts/uuid-here"
```

## Query Parameters

| Parameter | Example | Description |
|-----------|---------|-------------|
| `fields` | `fields=id,title,author.name` | Field selection (dot notation for relations) |
| `filter` | `filter[status][_eq]=published` | Filter with operators |
| `sort` | `sort=-date_created,title` | Sort (prefix `-` for descending) |
| `limit` | `limit=25` | Max results |
| `offset` | `offset=50` | Skip N results |
| `page` | `page=3` | Page number (with limit) |
| `search` | `search=keyword` | Full-text search |
| `deep` | `deep[comments][_limit]=5` | Nested relation queries |
| `aggregate` | `aggregate[count]=*` | Aggregation |
| `groupBy` | `groupBy[]=status` | Group results |
| `meta` | `meta=total_count,filter_count` | Include metadata |

## Schema Migration Pipeline

### Export Schema Snapshot

```bash
curl -s -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  "${DIRECTUS_URL}/schema/snapshot" | jq . > schema-snapshot.json
```

### Compare Snapshots (Diff)

```bash
curl -s -X POST \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d @schema-snapshot.json \
  "${DIRECTUS_URL}/schema/diff" | jq . > schema-diff.json
```

### Apply Diff (Migrate)

```bash
curl -s -X POST \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d @schema-diff.json \
  "${DIRECTUS_URL}/schema/apply"
```

This enables CI/CD schema deployments across environments.

## Response Format

```json
{
  "data": [ ... ],
  "meta": {
    "total_count": 100,
    "filter_count": 42
  }
}
```

Single items: `{ "data": { ... } }`

## Utility Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/server/ping` | GET | Health check (returns "pong") |
| `/server/health` | GET | Detailed health status |
| `/server/info` | GET | Server metadata |
| `/utils/cache/clear` | POST | Clear server cache |
| `/utils/hash` | POST | Generate hash |
| `/utils/random/string` | GET | Random string |
| `/utils/export/{collection}` | GET | Export data (CSV, JSON, XML, YAML) |
| `/utils/import/{collection}` | POST | Import data into collection |

## Detailed References

- [endpoints-items.md](references/endpoints-items.md) — Full items API with all query combinations, batch operations
- [endpoints-schema.md](references/endpoints-schema.md) — Collections, fields, relations, schema migration
- [endpoints-system.md](references/endpoints-system.md) — Users, roles, permissions, auth, activity, settings
