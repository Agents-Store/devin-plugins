---
name: conversations
description: >
  This skill should be used when the user asks to "list Dify conversations",
  "get conversation history", "list messages in a Dify conversation", "rename a Dify
  conversation", "delete a conversation", or "get/update Dify conversation variables".
  Covers chat-history management for chat/agent/chatflow apps.
---

# Dify — Conversations & Messages

Managing chat history for conversational apps (chat / agent / chatflow). Completion and
Workflow apps have no conversations. For auth/base URL/`user` see the `setup` skill.

## GET /conversations — list a user's conversations

```bash
curl 'https://api.dify.ai/v1/conversations?user=user-123&limit=20' \
  --header 'Authorization: Bearer app-XXXX'
```

Query params: `user` (required), `last_id` (cursor pagination), `limit` (default 20),
`sort_by` (e.g. `-updated_at`, `created_at`).

```json
{
  "data": [
    { "id": "...", "name": "Intro to Dify", "inputs": {}, "status": "normal",
      "introduction": "", "created_at": 1700000000, "updated_at": 1700000100 }
  ],
  "has_more": false,
  "limit": 20
}
```

## GET /messages — list messages in a conversation

History is fetched via `/messages` with the `conversation_id` (reverse-chronological,
cursor-paginated by `first_id`).

```bash
curl 'https://api.dify.ai/v1/messages?conversation_id={conversation_id}&user=user-123&limit=20' \
  --header 'Authorization: Bearer app-XXXX'
```

Query params: `conversation_id` (required), `user` (required), `first_id` (cursor),
`limit` (default 20).

```json
{
  "data": [
    { "id": "...", "conversation_id": "...", "inputs": {}, "query": "Hi",
      "answer": "Hello!", "message_files": [],
      "feedback": { "rating": "like" }, "retriever_resources": [],
      "created_at": 1700000000 }
  ],
  "has_more": false,
  "limit": 20
}
```

## POST /conversations/{conversation_id}/name — rename

Set a name explicitly, or `auto_generate: true` to let the model title it.

```bash
curl -X POST 'https://api.dify.ai/v1/conversations/{conversation_id}/name' \
  --header 'Authorization: Bearer app-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{ "name": "Onboarding chat", "user": "user-123" }'

# or auto-generate
--data '{ "auto_generate": true, "user": "user-123" }'
```

Returns the updated conversation object.

## DELETE /conversations/{conversation_id} — delete

```bash
curl -X DELETE 'https://api.dify.ai/v1/conversations/{conversation_id}' \
  --header 'Authorization: Bearer app-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{ "user": "user-123" }'
```

Returns `{ "result": "success" }` (204 on some versions).

## GET /conversations/{conversation_id}/variables — list session variables

Conversation variables are session state set inside a chatflow (e.g. remembered prefs).

```bash
curl 'https://api.dify.ai/v1/conversations/{conversation_id}/variables?user=user-123' \
  --header 'Authorization: Bearer app-XXXX'
```

Query params also support `last_id`, `limit`. Returns a `data` array of
`{ id, name, value_type, value, description, created_at }`.

## PUT /conversations/{conversation_id}/variables/{variable_id} — update a variable

```bash
curl -X PUT 'https://api.dify.ai/v1/conversations/{conversation_id}/variables/{variable_id}' \
  --header 'Authorization: Bearer app-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{ "value": "new value", "user": "user-123" }'
```

## Endpoint summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/conversations` | GET | List a user's conversations |
| `/messages` | GET | List messages in a conversation |
| `/conversations/{id}/name` | POST | Rename (or auto-generate name) |
| `/conversations/{id}` | DELETE | Delete a conversation |
| `/conversations/{id}/variables` | GET | List session variables |
| `/conversations/{id}/variables/{variable_id}` | PUT | Update a session variable |

## Tips

- Pagination is **cursor-based**: pass `last_id` (conversations / variables) or `first_id`
  (messages) from the previous page; stop when `has_more` is `false`.
- The `user` must match the one used to create the conversation, or it won't be found
  (see `troubleshoot` → conversation isolation).
