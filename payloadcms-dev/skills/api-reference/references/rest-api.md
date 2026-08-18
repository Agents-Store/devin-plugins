# REST API — Endpoint Reference

Every collection auto-mounts a CRUD endpoint set under `/api/<collection-slug>`. Globals get `/api/globals/<slug>`. Auth-enabled collections add `/api/<slug>/login`, `/logout`, etc.

## Collection CRUD

| Method | Path | Body | Purpose |
| --- | --- | --- | --- |
| `GET` | `/api/<slug>` | — | List with `where`, `sort`, `limit`, `page`, `depth` |
| `POST` | `/api/<slug>` | JSON doc | Create |
| `GET` | `/api/<slug>/:id` | — | Find by ID |
| `PATCH` | `/api/<slug>/:id` | JSON partial | Update one |
| `DELETE` | `/api/<slug>/:id` | — | Delete one |
| `PATCH` | `/api/<slug>` | `?where=…` + JSON | Bulk update |
| `DELETE` | `/api/<slug>` | `?where=…` | Bulk delete |
| `POST` | `/api/<slug>/:id/duplicate` | — | Duplicate (if not disabled) |

### List

```bash
curl 'https://app.example.com/api/posts?where[status][equals]=published&sort=-publishedAt&limit=20&depth=2' \
  -H "Authorization: JWT $TOKEN"
```

Response:
```json
{
  "docs": [/* … */],
  "totalDocs": 234,
  "limit": 20,
  "totalPages": 12,
  "page": 1,
  "hasNextPage": true,
  "hasPrevPage": false,
  "nextPage": 2,
  "prevPage": null
}
```

Additional list/read query params: `select` (field projection), `populate` (per-relationship field selection on populated docs), `joins` (control join-field pagination/sort per join field), and `trash=true` (include soft-deleted docs on collections with `trash: true` — see the `data-management` skill).

### Find by ID

```bash
curl 'https://app.example.com/api/posts/675abc?depth=1'
```

### Create

```bash
curl -X POST 'https://app.example.com/api/posts' \
  -H "Authorization: JWT $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"title":"Hello","status":"draft"}'
```

For upload collections, send `multipart/form-data` with a `file` field and a `_payload` field carrying JSON metadata:
```bash
curl -X POST 'https://app.example.com/api/media' \
  -H "Authorization: JWT $TOKEN" \
  -F 'file=@./image.jpg' \
  -F '_payload={"alt":"Cover"}'
```

### Update

```bash
curl -X PATCH 'https://app.example.com/api/posts/675abc' \
  -H "Authorization: JWT $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"status":"published"}'
```

### Bulk update

```bash
curl -X PATCH 'https://app.example.com/api/posts?where[archived][equals]=true' \
  -H "Authorization: JWT $TOKEN" \
  -d '{"hidden":true}'
```

Response: `{ docs: [...], errors: [...] }`.

### Delete

```bash
curl -X DELETE 'https://app.example.com/api/posts/675abc' \
  -H "Authorization: JWT $TOKEN"
```

### Count

```bash
curl 'https://app.example.com/api/posts/count?where[status][equals]=published' \
  -H "Authorization: JWT $TOKEN"
```

Returns `{ "totalDocs": N }`.

## Globals

| Method | Path | Body | Purpose |
| --- | --- | --- | --- |
| `GET` | `/api/globals/<slug>` | — | Read |
| `POST` | `/api/globals/<slug>` | JSON | Update (yes, POST) |

```bash
curl 'https://app.example.com/api/globals/site-settings'

curl -X POST 'https://app.example.com/api/globals/site-settings' \
  -H 'Content-Type: application/json' \
  -H "Authorization: JWT $TOKEN" \
  -d '{"siteName":"My App"}'
```

## Auth

For collections with `auth: true` (e.g. `users`):

| Method | Path | Body | Purpose |
| --- | --- | --- | --- |
| `POST` | `/api/<slug>/login` | `{ email, password }` | Returns `{ user, token, exp }`, sets cookie |
| `POST` | `/api/<slug>/logout` | — | Clears cookie |
| `POST` | `/api/<slug>/forgot-password` | `{ email }` | Sends reset email |
| `POST` | `/api/<slug>/reset-password` | `{ token, password }` | Set new password |
| `POST` | `/api/<slug>/verify/:token` | — | Verify email |
| `POST` | `/api/<slug>/unlock` | `{ email }` | Admin-only unlock |
| `GET`  | `/api/<slug>/me` | — | Current user (from JWT/cookie) |
| `POST` | `/api/<slug>/refresh-token` | — | Refresh JWT |

### Login

```bash
curl -X POST 'https://app.example.com/api/users/login' \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","password":"secret"}'
```

Response:
```json
{
  "message": "Auth Passed",
  "user": { "id": "...", "email": "..." },
  "token": "eyJ…",
  "exp": 1735689600
}
```

Use `Authorization: JWT <token>` on subsequent calls, or rely on the auto-set HTTP-only cookie.

### Me

```bash
curl 'https://app.example.com/api/users/me' -H "Authorization: JWT $TOKEN"
```

Returns the user and their `collection` permissions.

## Versions

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/<slug>/versions` | List versions across all docs |
| `GET` | `/api/<slug>/versions/:id` | Single version by version-id |
| `POST` | `/api/<slug>/versions/:id` | Restore version |
| `GET` | `/api/globals/<slug>/versions` | Global versions |

## Uploads

Get a file:
```bash
curl 'https://app.example.com/api/media/file/<filename>'
# Resized variant:
curl 'https://app.example.com/api/media/file/<filename>?size=thumbnail'
```

## Jobs

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/payload-jobs/run?limit&queue&allQueues` | Process the queue (POST only via the `X-Payload-HTTP-Method-Override: GET` header) |
| `GET` | `/api/payload-jobs/handle-schedules` | Enqueue due scheduled jobs |
| `GET` | `/api/payload-jobs` | List jobs (collection CRUD) |

```bash
curl 'https://app.example.com/api/payload-jobs/run?limit=100&queue=nightly' \
  -H "Authorization: Bearer $CRON_SECRET"
```

Gate the run endpoint via `jobs.access.run` in config — see the `jobs-queue` skill.

## Where Encoding

REST callers pass `where` as a flattened query string. The library `qs-esm` (Payload-maintained ESM fork of `qs`, the same the docs use) is the easiest way:

```ts
import { stringify } from 'qs-esm'

const url = `/api/posts${stringify(
  {
    where: {
      and: [
        { status: { equals: 'published' } },
        { 'author.email': { contains: '@example.com' } },
      ],
    },
    sort: '-publishedAt',
    depth: 2,
    limit: 20,
  },
  { addQueryPrefix: true },
)}`
```

## Custom Endpoints

Add via `endpoints` on a collection or root config — they get mounted at `/api/<collection>/<path>` or `/api/<path>`. See the `collections` skill.

## Error Codes

| Status | Meaning |
| --- | --- |
| `400` | Validation error (body shape) |
| `401` | Missing or invalid auth |
| `403` | Authenticated but not allowed |
| `404` | Not found |
| `429` | Rate limited (admin login attempts) |
| `500` | Server error |

Body:
```json
{ "errors": [{ "message": "…", "name": "…" }] }
```

## CORS

Set via `payload.config.ts`:
```ts
cors: ['https://my-frontend.com'],         // Array of origins, or '*' for any
csrf: ['https://my-frontend.com'],
```

By default the admin URL is allowed. Add public frontends explicitly.
