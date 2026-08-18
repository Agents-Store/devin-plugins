# Chatwoot Client / Public API

Public, unauthenticated widget API for building custom chat front-ends. Identifies the channel by `inbox_identifier` and the contact by `source_id` / `contact_identifier` — no access token. Base: `${CHATWOOT_BASE_URL}/public/api/v1`.

Authoritative schemas: `openapi/client_swagger.json` (9 paths, 12 operations). Grep it for request bodies, query params, and response shapes.

```bash
jq -r '.paths | keys[]' openapi/client_swagger.json
```

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
| POST | `/inboxes/{inbox_identifier}/contacts/{contact_identifier}/conversations/{conversation_id}/update_last_seen` | `update-last-seen` | Update last seen |

## Messages API

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/inboxes/{inbox_identifier}/contacts/{contact_identifier}/conversations/{conversation_id}/messages` | `list-all-conversation-messages` | List all messages |
| POST | `/inboxes/{inbox_identifier}/contacts/{contact_identifier}/conversations/{conversation_id}/messages` | `create-a-message` | Create a message |
| PATCH | `/inboxes/{inbox_identifier}/contacts/{contact_identifier}/conversations/{conversation_id}/messages/{message_id}` | `update-a-message` | Update a message |
