---
name: chat-completion
description: >
  This skill should be used when the user asks to "send a chat message to Dify",
  "call /chat-messages", "use the Dify completion API", "/completion-messages",
  "stream a Dify chat response", "stop Dify generation", "get suggested questions",
  or "submit message feedback / like a message". Covers conversational (chat/agent/
  chatflow) and stateless (completion) message sending.
---

# Dify — Chat & Completion Messages

Sending messages to Dify apps and managing the message lifecycle. For auth, base URL, the
`user` field, and response modes, see the `setup` skill. For SSE event details see
[references/streaming-events.md](references/streaming-events.md).

## POST /chat-messages — chat / agent / chatflow apps

Stateful conversation. Omit `conversation_id` (or send `""`) to start a new conversation;
pass the returned `conversation_id` to continue it.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `query` | string | yes | The user's message |
| `inputs` | object | yes* | App variables from `GET /parameters` (`{}` if none) |
| `response_mode` | string | yes | `streaming` or `blocking` |
| `user` | string | yes | End-user identifier |
| `conversation_id` | string | no | Continue an existing conversation |
| `files` | array | no | Multimodal inputs (see `setup` skill) |
| `auto_generate_name` | bool | no | Auto-title the conversation (default `true`) |

```bash
curl -X POST 'https://api.dify.ai/v1/chat-messages' \
  --header 'Authorization: Bearer app-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{
    "query": "What is Dify?",
    "inputs": {},
    "response_mode": "streaming",
    "user": "user-123",
    "conversation_id": ""
  }'
```

Blocking response (shape):

```json
{
  "event": "message",
  "task_id": "...",
  "message_id": "...",
  "conversation_id": "...",
  "mode": "chat",
  "answer": "Dify is an LLM app development platform...",
  "metadata": { "usage": { "total_tokens": 42 }, "retriever_resources": [] },
  "created_at": 1700000000
}
```

In streaming mode the answer arrives across `message` events and ends with `message_end`
(carrying `conversation_id`, `message_id`, and `metadata.usage`). See the references file.

## POST /completion-messages — text generation (completion) apps

Stateless, single-shot. No `conversation_id`. The prompt comes from `inputs` (the app's
defined variables); `query` is usually `""`.

```bash
curl -X POST 'https://api.dify.ai/v1/completion-messages' \
  --header 'Authorization: Bearer app-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{
    "inputs": { "topic": "renewable energy" },
    "response_mode": "blocking",
    "user": "user-123"
  }'
```

Returns the same `message`/`message_end` shape with `"mode": "completion"`.

## Stop generation (streaming only)

Use the `task_id` from any streamed event. The `user` must match the one that started it.

```bash
# Chat / chatflow
curl -X POST 'https://api.dify.ai/v1/chat-messages/{task_id}/stop' \
  --header 'Authorization: Bearer app-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{ "user": "user-123" }'

# Completion
curl -X POST 'https://api.dify.ai/v1/completion-messages/{task_id}/stop' \
  --header 'Authorization: Bearer app-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{ "user": "user-123" }'
```

Returns `{ "result": "success" }`.

## GET /messages/{message_id}/suggested — next questions

Returns AI-suggested follow-up questions for a message (if enabled on the app).

```bash
curl 'https://api.dify.ai/v1/messages/{message_id}/suggested?user=user-123' \
  --header 'Authorization: Bearer app-XXXX'
```

```json
{ "result": "success", "data": ["How do I deploy it?", "Is it open source?"] }
```

## POST /messages/{message_id}/feedback — like / dislike

```bash
curl -X POST 'https://api.dify.ai/v1/messages/{message_id}/feedback' \
  --header 'Authorization: Bearer app-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{ "rating": "like", "content": "Helpful!", "user": "user-123" }'
```

`rating` is `like`, `dislike`, or `null` (to revoke). Returns `{ "result": "success" }`.

## GET /app/feedbacks — list app feedbacks

```bash
curl 'https://api.dify.ai/v1/app/feedbacks?page=1&limit=20' \
  --header 'Authorization: Bearer app-XXXX'
```

Returns `{ "data": [ { "id", "message_id", "rating", "content", "from_end_user_id", "created_at" } ] }`.

## Endpoint summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/chat-messages` | POST | Send a chat/agent/chatflow message |
| `/chat-messages/{task_id}/stop` | POST | Stop a streaming chat response |
| `/completion-messages` | POST | Send a completion (text-gen) request |
| `/completion-messages/{task_id}/stop` | POST | Stop a streaming completion |
| `/messages/{message_id}/suggested` | GET | Suggested follow-up questions |
| `/messages/{message_id}/feedback` | POST | Like / dislike a message |
| `/app/feedbacks` | GET | List all feedbacks for the app |

Related: chat history & message listing → `conversations` skill · SSE events →
[references/streaming-events.md](references/streaming-events.md).
