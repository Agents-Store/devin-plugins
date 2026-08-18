---
name: api-reference
description: This skill should be used when the user asks for "PayloadCMS REST endpoint", "Payload curl example", "Payload GraphQL query syntax", "Payload Local API method signature", "Payload login endpoint", "Payload auth headers", or needs the exact HTTP/method signature for a Payload API call.
disable-model-invocation: true
---

# PayloadCMS — API Reference

Endpoint-by-endpoint reference. Triggered only on explicit user request — heavy content lives in `references/` files below.

## Three API Surfaces

| Surface | Endpoint | When to use |
| --- | --- | --- |
| **Local API** | In-process JS calls (`payload.find`, …) | Server-side code, hooks, scripts, server components |
| **REST API** | `/api/<collection>/...` | Browser fetch, external services, mobile apps |
| **GraphQL** | `/api/graphql` | Typed frontends, codegen pipelines, federation |

All three share the same `where` query syntax, access control rules, and hook firing order.

Typed external client: `@payloadcms/sdk` — the official REST SDK (same 3.x version line) for browser/service callers; mirrors Local API options over HTTP.

## Reference Files

- [`references/local-api.md`](references/local-api.md) — every method on the `payload` instance with full TypeScript signatures.
- [`references/rest-api.md`](references/rest-api.md) — every REST route grouped by collection-CRUD, globals, auth, uploads, versions, jobs.
- [`references/graphql-api.md`](references/graphql-api.md) — auto-generated schema rules, query/mutation patterns, custom resolvers.

## Auth Headers (cross-API)

| Header | Purpose |
| --- | --- |
| `Authorization: JWT <token>` | Authenticate as a user. Token comes from `/api/<auth-collection>/login`. |
| `Authorization: <api-key-collection> API-Key <key>` | API key auth (when `auth.useAPIKey: true`). |
| `Cookie: payload-token=<jwt>` | HTTP-only cookie set by `/login`. Browser sessions use this. |

## Base URL

The Payload server URL is the Next.js dev/prod URL — typically:
- Dev: `http://localhost:3000`
- Prod: `https://your-app.com`

All routes shown in references are relative to that base.

## Common Query Parameters (REST)

| Param | Type | Example |
| --- | --- | --- |
| `where` | JSON-encoded object | `?where[status][equals]=published` |
| `sort` | string | `?sort=-publishedAt,title` |
| `limit` | number | `?limit=50` |
| `page` | number | `?page=2` |
| `depth` | 0–10 | `?depth=2` |
| `select` | object | `?select[title]=true&select[slug]=true` |
| `locale` | string | `?locale=es` |
| `fallback-locale` | string | `?fallback-locale=en` |
| `draft` | boolean | `?draft=true` |

Use the `qs-esm` library (Payload-maintained) to encode complex where clauses from the browser.

## Error Format

REST/GraphQL errors return:
```json
{
  "errors": [
    { "message": "You are not allowed to perform this action.", "name": "Forbidden" }
  ]
}
```

HTTP status codes: 400 (validation), 401 (auth missing), 403 (access denied), 404 (not found), 500 (server).

Local API throws typed `APIError` / `ValidationError` instances — catch and inspect `.status` / `.name`.

## Don't Hardcode URLs

Inside generated app code, prefer the alias:
```ts
import config from '@payload-config'
const payload = await getPayload({ config })
```

For external clients, read base URL from env (`NEXT_PUBLIC_PAYLOAD_URL`). Never hardcode `localhost` or production hosts in committed code.

---

**This skill has `disable-model-invocation: true`** — Claude will not auto-trigger it. Users must reference it explicitly ("show me the REST endpoint for…") or another skill must link to it. See the linked reference files for the full content.
