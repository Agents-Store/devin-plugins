---
name: troubleshoot
description: This skill should be used when an Outline REST API call fails or behaves unexpectedly — "Outline returns 401 / 403 / 404 / 429 / 400", "Outline API key not working", "can't find the document", "empty data / missing results", "self-hosted Outline URL not working", "SSL error", or any Outline error response. Maps symptoms to causes and fixes.
---

# Outline Troubleshooting

Match the symptom, apply the fix. Most Outline API failures come from a bad base URL, a missing/scoped key, a title used where an id is required, or forgetting that everything is a `POST` with a JSON body.

## 401 Unauthorized

**Cause:** the key is missing, wrong, revoked, or not sent as a Bearer token.

- Confirm the header is exactly `Authorization: Bearer ${OUTLINE_API_KEY}` and the key begins with `ol_api_`.
- Verify the key still exists under **Settings → API & Apps** (revoked keys always `401`; `apiKeys.list` shows the key's name, `last4` and `expiresAt` — an expired key no longer authenticates).
- Did anything call `auth.delete` (sign out)? It rotates the user's token secret, which ends that user's browser sessions and session tokens (JWTs). Personal `ol_api_` keys are separate records, so it most likely does **not** revoke one — but if keys stopped working right after a sign-out, check `apiKeys.list` before assuming.
- Confirm `OUTLINE_API_KEY` is actually set in the environment: `[ -n "$OUTLINE_API_KEY" ] && echo set || echo MISSING`.
- Re-run the `setup` check: `POST /auth.info`. A `200` there means the key is fine and the problem is elsewhere.

## 403 Forbidden (policy / permission)

**Cause:** authenticated, but a **policy** denies this action on this object — or the key is **scoped** too narrowly.

- Most responses carry a `policies` array; it describes what the key may do. A `403` is a real boundary — don't try to route around it.
- Admin-only actions (`users.update_role`, `users.suspend/activate/delete`, `documents.empty_trash`, `dataAttributes.*`) need an admin key.
- If a call that used to work now `403`s, the key may be scoped (e.g. `documents:read` only). Mint a key with the needed scope (`write`, `documents.*`, etc.). After upgrading to Outline v1.10.1+ re-check scoped keys: scopes are validated more strictly at the model layer.
- `webhookSubscriptions.*` are admin-only; `apiKeys.list` with `userId` (other users' keys) is admin-only.
- Gated features: `documents.answerQuestion` and `dataAttributes.*` require a Business/Enterprise plan and, for AI answers, the workspace setting enabled.

## 404 / "Not found"

**Cause:** almost always a **title or wrong id used where a UUID/`urlId` is required**, or the object is archived/trashed.

- Resolve first: `documents.search_titles` / `documents.search` for documents, `collections.list` for collections. Keep the returned `id`.
- `documents.info` accepts a UUID, a `urlId` (e.g. `hDYep1TPAM`), or a `shareId` — make sure you're passing one of those, not the title.
- Archived/trashed docs won't appear in normal lists — use `documents.archived` / `documents.deleted`, then `documents.restore`.

## 400 Validation error

**Cause:** malformed body or a missing required field.

- Send `-H "Content-Type: application/json"` and a valid JSON body. Even no-arg calls need `-d '{}'`.
- Check required fields per method (see the reference file). E.g. publishing a document needs `collectionId` **or** `parentDocumentId`; `shares.create` needs exactly one of `documentId`/`collectionId`; `documents.update` with `editMode:"patch"` also needs `findText`.
- `collections.create`/`collections.update` reject a body that has **both** `description` and `data` (Outline v1.9.0+) — send one. `comments.create`/`comments.update` need `text` **or** `data`. `webhookSubscriptions.create` needs `name`, `url` and `events`, and a cloud workspace requires an `https` URL. Text limits: document `title` ≤100, `text` ≤1,536,000 chars, comment `text` ≤10000 chars.
- `views.create` is gone from the published spec (and may be rejected on newer servers, which tightened its authentication) — don't call it.
- Escape newlines in JSON string values (`\n`). Building the body with `jq -n` avoids quoting mistakes:
  ```bash
  jq -n --arg id "$DOC_ID" --arg t "$(cat body.md)" '{id:$id, text:$t}'
  ```

## 409 Conflict on `documents.update`

**Cause:** you sent `lastRevision` and the document's current revision no longer matches — someone saved in between (optimistic concurrency). Re-read with `documents.info`, merge your change into the latest `text`, and retry with the new `revision` number. Omit `lastRevision` only if overwriting is acceptable.

## 429 Too Many Requests

**Cause:** rate limiting (mutating endpoints are stricter than reads).

- The response includes a `Retry-After` header (seconds). Inspect with `curl -s -D - … | grep -i retry-after` and back off that long.
- Outline v1.7.1+ raised the default model-creation limits from 10 to 25 per minute; on a **self-hosted** instance an admin can tune limits with the `RATE_LIMITER_MULTIPLIER` environment variable (on self-hosted, a persistent `429` may mean the limits need tuning).
- Add a small `sleep` between bulk writes; raise `limit` (e.g. to 100) on reads to make fewer requests.

## Empty `.data` or "missing" results

**Cause:** pagination, or reading the wrong envelope field.

- The payload is under `.data` — `jq '.data'`, not the root. Some lists nest it (`.data.users`, `.data.stars`) — check the reference file.
- Lists return one page (**default limit 25**). Walk pages with `{"limit":100,"offset":0}`, then `offset:100`, … until a short page returns, or follow `pagination.nextPath`.
- Search is restricted to documents the key can access — a scoped/low-privilege key sees fewer results.

## Self-hosted: connection / URL / SSL problems

- `OUTLINE_API_URL` must include `/api` (e.g. `https://wiki.acme.com/api`) and must **not** end in a method name. Endpoints are `${OUTLINE_API_URL%/}/<method>`.
- A `404` on every call usually means the `/api` segment is missing or doubled.
- Self-signed certificate? curl will refuse by default. Verify the cert is valid; only as a last resort for a trusted internal host use `curl -k` (insecure — don't use against cloud).
- Wrong scheme/host returns connection errors, not JSON — confirm the workspace is reachable in a browser first.

## Optional convenience MCP

If you'd rather call tools than curl for the most common search/read/create/edit operations, use Outline's **built-in MCP server** (announced 2026-02-18; self-hosted needs Outline v1.6.0+, and it is off by default for workspaces that existed before then): Streamable HTTP at `<workspace-origin>/mcp` (self-hosted: your domain + `/mcp`; this is **not** `OUTLINE_API_URL`), OAuth sign-in by default or `Authorization: Bearer <api-key>`; enable it under **Settings → Workspace → AI**, and run `claude mcp add --transport http outline <workspace-origin>/mcp` (details in the plugin `README.md`). If it will not connect, an admin may have disabled it. Community Outline MCP servers also exist and use the same `OUTLINE_API_KEY`/`OUTLINE_API_URL` variables: Python [`Vortiago/mcp-outline`](https://github.com/Vortiago/mcp-outline), npm [`outline-mcp-server`](https://www.npmjs.com/package/outline-mcp-server), Rust [`nizovtsevnv/outline-mcp-rs`](https://github.com/nizovtsevnv/outline-mcp-rs). They cover a convenient subset — for full coverage (admin, OAuth, data attributes, file ops) use the REST endpoints in `api-reference`. These are not dependencies of this plugin.
