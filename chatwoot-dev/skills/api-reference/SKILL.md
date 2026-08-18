---
name: api-reference
description: This skill should be used when the user asks for "Chatwoot API endpoints", "Chatwoot REST API", "Chatwoot curl examples", "Chatwoot Application/Platform/Public API", "Chatwoot API documentation", or needs specific HTTP endpoint, request, or response details for Chatwoot.
disable-model-invocation: true
---

# Chatwoot API Reference

Complete REST API coverage for Chatwoot. Official docs: https://developers.chatwoot.com.
This skill maps every API family to a detailed guide and to the **bundled OpenAPI specs** —
grep those specs for exact request bodies, query params, and response schemas.

## The three API families

| Family | Base path | Auth | Guide | OpenAPI spec |
|--------|-----------|------|-------|--------------|
| Application | `/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}/...` | `api_access_token` header (user token) | `references/application-api.md` | `references/openapi/application_swagger.json` |
| Platform | `/platform/api/v1/...` | `api_access_token` header (platform app token) | `references/platform-api.md` | `references/openapi/platform_swagger.json` |
| Client / Public | `/public/api/v1/inboxes/{inbox_identifier}/...` | none (inbox identifier + contact `source_id`) | `references/client-api.md` | `references/openapi/client_swagger.json` |

Cross-cutting rules (auth, pagination, errors, rate limits, `message_type`/`content_type`
enums, attachments) live in `references/pagination-errors.md`. The CSAT survey page is in
`references/openapi/other_swagger.json`.

## Authentication

Chatwoot uses a custom header — **not** `Authorization: Bearer`:

```bash
curl -s -H "api_access_token: ${CHATWOOT_API_KEY}" \
  "${CHATWOOT_BASE_URL}/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}/conversations" | jq .
```

## Finding an exact endpoint in the bundled specs

The guides list every endpoint, but the OpenAPI JSON has the authoritative schemas. To look
one up, grep the spec for the operationId or path:

```bash
DIR="$(dirname "$0")/references/openapi"   # or the skill's references/openapi directory
jq -r '.paths | keys[]' "$DIR/application_swagger.json" | grep -i conversation
jq '.paths["/api/v1/accounts/{account_id}/conversations"].post.requestBody' \
  "$DIR/application_swagger.json"
```

## Examples

<example>
Context: List open conversations in an inbox.
```bash
curl -s -H "api_access_token: ${CHATWOOT_API_KEY}" \
  "${CHATWOOT_BASE_URL}/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}/conversations?status=open&inbox_id=5" \
  | jq '.data.payload[] | {id, status, contact: .meta.sender.name}'
```
</example>

<example>
Context: Send an outgoing reply to conversation 123.
```bash
curl -s -X POST \
  -H "api_access_token: ${CHATWOOT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"content":"Thanks, looking into it now.","message_type":"outgoing"}' \
  "${CHATWOOT_BASE_URL}/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}/conversations/123/messages" | jq .
```
</example>

<example>
Context: Provision a new account with the Platform API (super-admin token).
```bash
curl -s -X POST \
  -H "api_access_token: ${CHATWOOT_PLATFORM_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name":"Acme Inc"}' \
  "${CHATWOOT_BASE_URL}/platform/api/v1/accounts" | jq .
```
</example>

## Notes

- All write requests (`POST`/`PATCH`/`PUT`/`DELETE`) that send messages or change shared
  state are effectively irreversible — confirm intent before running them.
- Application list endpoints wrap results as `{ "data": { "meta": {...}, "payload": [...] } }`;
  many other endpoints return a bare array or object. Check the spec for the exact shape.
- For full schemas, query `references/openapi/*.json` — do not guess field names.
