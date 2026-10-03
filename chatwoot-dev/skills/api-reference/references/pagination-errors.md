# Chatwoot API — Cross-Cutting Conventions

Rules that apply across the Application, Platform, and Client APIs. Read this alongside the
per-family guides. Authoritative schemas are in `openapi/*.json`.

## Authentication

| API | Header | Value |
|-----|--------|-------|
| Application | `api-access-token` | User access token (`${CHATWOOT_API_KEY}`) from Profile Settings → Access Token |
| Platform | `api-access-token` | Platform app token (installation Super Admin) |
| Client / Public | _none_ | Identified by `inbox_identifier` in the path + contact `source_id` |

A token used against the wrong family returns `401`/`403` even if the token itself is valid
(e.g. a user token on `/platform/...`).

```bash
curl -s -H "api-access-token: ${CHATWOOT_API_KEY}" \
  "${CHATWOOT_BASE_URL}/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}/conversations" | jq .
```

### Header spelling: send `api-access-token` (hyphens)

Chatwoot's OpenAPI names the header `api_access_token` (underscores). Send the hyphenated
`api-access-token` instead:

- **Same header for Chatwoot.** Both spellings reach the Rails app as the Rack variable
  `HTTP_API_ACCESS_TOKEN`, and the server reads exactly that variable
  (`app/controllers/concerns/access_token_auth_helper.rb`). The token check is identical.
- **Different path through proxies.** nginx treats a request header whose name contains an
  underscore as invalid and, with its defaults (`underscores_in_headers off`,
  `ignore_invalid_headers on`), silently ignores it. Caddy 2.6.4 and newer strip such headers
  as well (reported in chatwoot/cli#41). The token never reaches Chatwoot and a valid token
  gets `401`. Hyphens are legal everywhere, so the hyphenated spelling always arrives.
- The official `chatwoot` CLI switched to `api-access-token` in v0.7.0 for exactly this reason.

If you must keep the underscore spelling behind nginx, set `underscores_in_headers on;` in the
`http` or `server` block of the proxy; the hyphen needs no proxy change.

### Bearer tokens (Chatwoot v4.19.0 and later)

From v4.19.0 Chatwoot also accepts `Authorization: Bearer <token>` with the same user,
agent-bot and platform tokens, and the upstream OpenAPI says the custom header "will be
deprecated in a future release" (no date given). v4.18.0, the latest release as of 2026-10-03,
reads only the custom header, so a Bearer request to it returns `401`. Use `api-access-token`
until every instance you target runs v4.19.0 or later.

## Response envelopes

Two shapes appear — always confirm in the spec:

- **Wrapped lists** (most Application list endpoints): `{ "data": { "meta": {...}, "payload": [...] } }`
- **Bare** object or array (show/create/update on many resources, and the Client API)

```bash
# conversations is wrapped
jq '.data.payload[].id'   # conversations list
# messages list is a bare object with .payload
jq '.payload[].content'   # messages list
```

## Pagination

Most list endpoints paginate with a `page` query param (1-based), often 25 items/page.
Some accept `since`/`before` or resource-specific filters. Conversation listing also returns
counts under `data.meta` (`mine_count`, `assigned_count`, `all_count`).

```bash
curl -s -H "api-access-token: ${CHATWOOT_API_KEY}" \
  "${CHATWOOT_BASE_URL}/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}/contacts?page=2" | jq '.meta'
```

Never assume a single response is the complete set — page until the payload is empty or the
returned count is reached.

## Errors

Error bodies follow the `bad_request_error` schema:

```json
{ "description": "string", "errors": [ { "field": "...", "message": "...", "code": "..." } ] }
```

| Status | Meaning | Typical cause |
|--------|---------|---------------|
| 401 | Unauthorized | Missing/invalid `api-access-token`, a proxy that dropped an underscore `api_access_token` header, or the right token for the wrong API family |
| 403 | Forbidden | Token lacks the role/permission for the action (e.g. agent token on admin op) |
| 404 | Not Found | Wrong `account_id`, wrong base URL, or the resource id does not exist |
| 422 | Unprocessable | Invalid/missing fields — check the request body against the spec |
| 429 | Too Many Requests | Rate limited — back off and retry |

## Rate limits

Chatwoot Cloud applies per-account and per-IP rate limiting; limits are not guaranteed in the
OpenAPI spec and differ on self-hosted. Treat `429` as a signal to add exponential backoff,
and batch work rather than firing unbounded parallel requests.

## Message types and content types

Messages carry a numeric `message_type` and a `content_type`:

| `message_type` | Meaning |
|----------------|---------|
| 0 | incoming (from the contact) |
| 1 | outgoing (from an agent/bot) |
| 2 | activity (system event) |
| 3 | template |

When creating a message you may pass `message_type` as the string `"incoming"` or
`"outgoing"`, and `private: true` for an internal note. `content_type` enum values include:
`text`, `input_text`, `input_textarea`, `input_email`, `input_select`, `cards`, `form`,
`article`, `incoming_email`, `input_csat`, `integrations`, `sticker`, `voice_call`.
Interactive content (cards/forms/selects) is configured via `content_attributes`.

## Attachments

To attach files when creating a message, send `multipart/form-data` with one or more
`attachments[]` parts instead of a JSON body:

```bash
curl -s -X POST \
  -H "api-access-token: ${CHATWOOT_API_KEY}" \
  -F "content=See attached" \
  -F "attachments[]=@/path/to/file.pdf" \
  "${CHATWOOT_BASE_URL}/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}/conversations/123/messages" | jq .
```

## Conversation status, priority, assignment

- Status values: `open`, `resolved`, `pending`, `snoozed`. Toggle via the conversation
  `toggle_status` endpoint or `PATCH` where supported.
- Priority: `urgent`, `high`, `medium`, `low`, or null.
- Assignment uses `assignee_id` (agent) and `team_id` (team) on the assignments endpoint.

For exact endpoints see `application-api.md`; for exact bodies query
`openapi/application_swagger.json`.
