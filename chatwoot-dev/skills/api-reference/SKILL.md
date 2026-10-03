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
| Application | `/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}/...` | `api-access-token` header (user token) | `references/application-api.md` | `references/openapi/application_swagger.json` |
| Platform | `/platform/api/v1/...` | `api-access-token` header (platform app token) | `references/platform-api.md` | `references/openapi/platform_swagger.json` |
| Client / Public | `/public/api/v1/inboxes/{inbox_identifier}/...` | none (inbox identifier + contact `source_id`) | `references/client-api.md` | `references/openapi/client_swagger.json` |

Cross-cutting rules (auth header, pagination, errors, rate limits, `message_type`/`content_type`
enums, attachments) live in `references/pagination-errors.md`. The CSAT survey page is in
`references/openapi/other_swagger.json`.

## Bundled specs

Vendored from `chatwoot/chatwoot` `develop` at commit `843385f` (2026-10-02, `swagger/tag_groups/`):
Application 124 operations, Platform 18, Client 12, CSAT page 1. The latest release, v4.18.0, has
122 / 17 / 12 / 1; the three newer operations are marked `develop` only in
`references/application-api.md` and `references/platform-api.md`, which also carry the
"Recent additions" write-ups for **campaigns**, **WhatsApp message templates**, the branded email
layout and message-status updates.

## Authentication

Send the token in the **`api-access-token`** header (hyphens; the upstream OpenAPI spells it
`api_access_token`, which is the same header but gets dropped by nginx and Caddy 2.6.4+ unless the
proxy is told otherwise). `Authorization: Bearer` works only on Chatwoot v4.19.0 and later. Why and
how to check: `references/pagination-errors.md` → Authentication.

```bash
curl -s -H "api-access-token: ${CHATWOOT_API_KEY}" \
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
curl -s -H "api-access-token: ${CHATWOOT_API_KEY}" \
  "${CHATWOOT_BASE_URL}/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}/conversations?status=open&inbox_id=5" \
  | jq '.data.payload[] | {id, status, contact: .meta.sender.name}'
```
</example>

<example>
Context: List the WhatsApp templates of inbox 15 (read-only), then the account's campaigns.
```bash
curl -s -H "api-access-token: ${CHATWOOT_API_KEY}" \
  "${CHATWOOT_BASE_URL}/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}/inboxes/15/message_templates" | jq '.payload, .meta'
curl -s -H "api-access-token: ${CHATWOOT_API_KEY}" \
  "${CHATWOOT_BASE_URL}/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}/campaigns" \
  | jq '.[] | {id, title, campaign_type, campaign_status}'
```
Creating or changing a campaign sends messages to real contacts: confirm first (see
`references/application-api.md` → Campaigns).
</example>

<example>
Context: Send an outgoing reply to conversation 123.
```bash
curl -s -X POST \
  -H "api-access-token: ${CHATWOOT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"content":"Thanks, looking into it now.","message_type":"outgoing"}' \
  "${CHATWOOT_BASE_URL}/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}/conversations/123/messages" | jq .
```
</example>

<example>
Context: Provision a new account with the Platform API (super-admin token).
```bash
curl -s -X POST \
  -H "api-access-token: ${CHATWOOT_PLATFORM_TOKEN}" \
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
