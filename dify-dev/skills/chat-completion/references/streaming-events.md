# Dify Streaming (SSE) Events

When `response_mode` is `streaming`, Dify returns **Server-Sent Events**. Each event is a
line `data: {json}\n\n`. Parse the JSON and switch on its `event` field. Send the
`Accept: text/event-stream` semantics by simply reading the response as a stream (curl
prints events as they arrive).

```bash
curl -N -X POST 'https://api.dify.ai/v1/chat-messages' \
  --header 'Authorization: Bearer app-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{ "query": "Hello", "inputs": {}, "response_mode": "streaming", "user": "user-123" }'
```

`-N` (`--no-buffer`) makes curl print each event immediately.

## Chat / Chatflow event types

| `event` | Meaning | Key fields |
|---------|---------|-----------|
| `message` | Incremental answer chunk — append to the response | `answer` (chunk), `message_id`, `conversation_id`, `task_id` |
| `message_file` | A file/image produced as output | `type`, `url`, `belongs_to` |
| `message_end` | End of the message; carries final metadata | `metadata.usage`, `metadata.retriever_resources`, `conversation_id`, `message_id` |
| `tts_message` | Base64 audio chunk (apps with TTS auto-play) | `audio`, `message_id` |
| `tts_message_end` | End of TTS stream | `message_id` |
| `message_replace` | Replace the whole answer (content moderation) | `answer` |
| `workflow_started` | (chatflow) workflow run began | `data.id`, `data.workflow_id` |
| `node_started` | (chatflow) a node began | `data.node_id`, `data.node_type`, `data.title` |
| `node_finished` | (chatflow) a node finished | `data.status`, `data.outputs`, `data.elapsed_time` |
| `workflow_finished` | (chatflow) workflow finished | `data.status`, `data.outputs`, `data.total_tokens` |
| `error` | Stream error; stop reading | `status`, `code`, `message` |
| `ping` | Keep-alive heartbeat every ~10s — ignore | — |

A typical chat stream: `message` × N → `message_end`. A chatflow stream interleaves
`workflow_started` → (`node_started`/`node_finished`) × N → `message` × N →
`workflow_finished` → `message_end`.

## Workflow app event types

Workflow apps (`/workflows/run`) emit the workflow events without the chat `message`
wrapper. The final output is in `workflow_finished.data.outputs`.

| `event` | Meaning |
|---------|---------|
| `workflow_started` | Run began (`task_id`, `workflow_run_id`) |
| `node_started` | Node began |
| `node_finished` | Node finished (status, outputs) |
| `workflow_finished` | Run finished (status, outputs, elapsed_time, total_tokens) |
| `tts_message` / `tts_message_end` | Audio chunks if TTS enabled |
| `error` | Run error |
| `ping` | Heartbeat |

## Completion app event types

| `event` | Meaning |
|---------|---------|
| `message` | Incremental text chunk |
| `message_end` | End + usage metadata |
| `message_replace` | Moderation replacement |
| `tts_message` / `tts_message_end` | Audio chunks if TTS enabled |
| `error` | Error |
| `ping` | Heartbeat |

## Parsing notes

- The `task_id` (present on streamed events) is what you pass to the **stop** endpoints.
- `conversation_id` first appears on chat events — capture it from the early events (or
  `message_end`) to continue the conversation later.
- Always handle `error` events: read `code` for programmatic handling and stop consuming.
- `ping` events carry no payload of interest; skip them.
- Token usage and `retriever_resources` (RAG citations) are only complete at `message_end`
  / `workflow_finished` — don't rely on them mid-stream.
