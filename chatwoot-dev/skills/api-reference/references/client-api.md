# Chatwoot Client / Public API

Public, unauthenticated widget API for building custom chat front-ends. Identifies the channel by `inbox_identifier` and the contact by `source_id` / `contact_identifier` — no access token. Base: `${CHATWOOT_BASE_URL}/public/api/v1`.

Authoritative schemas: `openapi/client_swagger.json` (9 paths, 12 operations). Grep it for request bodies, query params, and response shapes.

```bash
jq -r '.paths | keys[]' openapi/client_swagger.json
```

## Identity verification (`identifier_hash`)

When an inbox uses identity verification, the contact endpoints (create, show, update) check `identifier_hash` = hex HMAC-SHA256 of the contact `identifier`, keyed with the inbox's identity-verification secret (the web widget channel's `hmac_token`). The server recomputes the hash from the **current** secret on every such call and fails the request on mismatch; an empty hash is accepted only while verification is not mandatory (`hmac_mandatory` off).

> **After a secret rotation, recompute.** v4.18.0 added rotation of the inbox identity-verification secret in the dashboard. Because the server compares against the current secret, hashes your backend computed with the old secret stop matching after a rotation. This is reasoned from `app/controllers/public/api/v1/inboxes/contacts_controller.rb`, not exercised on a live instance: after rotating, update the secret in your backend and re-test the contact create/update call.

## Contacts API

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| POST | `/inboxes/{inbox_identifier}/contacts` | `create-a-contact` | Create a contact |
| GET | `/inboxes/{inbox_identifier}/contacts/{contact_identifier}` | `get-details-of-a-contact` | Get a contact |
| PATCH | `/inboxes/{inbox_identifier}/contacts/{contact_identifier}` | `update-a-contact` | Update a contact |

## Conversations API

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/inboxes/{inbox_identifier}/contacts/{contact_identifier}/conversations` | `list-all-contact-conversations` | List all conversations |
| POST | `/inboxes/{inbox_identifier}/contacts/{contact_identifier}/conversations` | `create-a-conversation` | Create a conversation |
| GET | `/inboxes/{inbox_identifier}/contacts/{contact_identifier}/conversations/{conversation_id}` | `get-single-conversation` | Get a single conversation |
| POST | `/inboxes/{inbox_identifier}/contacts/{contact_identifier}/conversations/{conversation_id}/toggle_status` | `resolve-conversation` | Resolve a conversation |
| POST | `/inboxes/{inbox_identifier}/contacts/{contact_identifier}/conversations/{conversation_id}/toggle_typing` | `toggle-typing-status` | Toggle typing status |
| POST | `/inboxes/{inbox_identifier}/contacts/{contact_identifier}/conversations/{conversation_id}/update_last_seen` | `update-last-seen` | Update last seen and mark messages read |

## Messages API

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/inboxes/{inbox_identifier}/contacts/{contact_identifier}/conversations/{conversation_id}/messages` | `list-all-conversation-messages` | List all messages |
| POST | `/inboxes/{inbox_identifier}/contacts/{contact_identifier}/conversations/{conversation_id}/messages` | `create-a-message` | Create a message |
| PATCH | `/inboxes/{inbox_identifier}/contacts/{contact_identifier}/conversations/{conversation_id}/messages/{message_id}` | `update-a-message` | Update a message |
