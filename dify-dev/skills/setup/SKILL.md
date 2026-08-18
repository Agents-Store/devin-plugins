---
name: setup
description: >
  This skill should be used when the user asks how to "connect to the Dify API",
  "authenticate with Dify", "get a Dify API key", "what is the Dify base URL",
  "blocking vs streaming in Dify", "the Dify user field", "send files to a Dify app",
  or needs the app metadata endpoints (/info, /parameters, /meta, /site). Foundation
  for every other Dify API call.
---

# Dify API — Setup & Fundamentals

Everything common to every Dify Service API call: base URL, authentication, the `user`
field, response modes, file inputs, and the app metadata endpoints.

## Base URL

| Deployment | Base URL |
|------------|----------|
| Dify Cloud | `https://api.dify.ai/v1` |
| Self-hosted | `https://{your-host}/v1` |

Every path in this plugin is relative to the base URL. Examples use `https://api.dify.ai/v1`.

## Authentication

Dify uses **per-app API keys** (not a single account key). Each app has its own key,
created in Dify Studio → your app → **API Access** → **API Key**. The Knowledge Base /
Datasets API uses a separate **Knowledge API key** (Knowledge → API).

Send it as a Bearer token on every request:

```bash
curl https://api.dify.ai/v1/info \
  --header 'Authorization: Bearer app-XXXXXXXXXXXXXXXXXXXX'
```

> Keep API keys **server-side**. Never ship them in browser/mobile clients — Dify keys grant
> full access to the app's API.

## The `user` field (required)

Almost every endpoint requires a `user` parameter — a string that uniquely identifies the
end user *within your application*. It scopes all data: conversations, messages, files, and
workflow runs are isolated per `user`.

- It is **your** identifier (email, UUID, session id) — not a Dify account.
- It must be **consistent** for the same person across calls, or they lose their history.
- Service API users and WebApp users are **separate namespaces** even with identical strings.

Pass it in the JSON body for POST/PUT, or as a query param for GET/DELETE:

```bash
# POST — in body
--data '{ "user": "user-123", ... }'

# GET / DELETE — in query
'https://api.dify.ai/v1/conversations?user=user-123'
```

## Response modes

| Mode | When to use | Behavior |
|------|-------------|----------|
| `blocking` | Simple request/response, short outputs | One JSON response when generation finishes. **~100s timeout** (Cloudflare on Cloud). |
| `streaming` | Chat UIs, long outputs, workflows | Server-Sent Events (SSE) streamed as they're produced. **Recommended.** |

Set it in the request body: `"response_mode": "streaming"` or `"blocking"`. See the
`chat-completion` and `workflows` skills for the SSE event types.

## File inputs

Endpoints that accept `files` (chat, completion, workflow) take an array of file objects.
Two transfer methods:

```jsonc
// 1) Reference a remote URL directly
{ "type": "image", "transfer_method": "remote_url", "url": "https://example.com/cat.png" }

// 2) Reference a previously uploaded file (see files-audio skill → /files/upload)
{ "type": "image", "transfer_method": "local_file", "upload_file_id": "<id-from-upload>" }
```

`type` is one of `image`, `document`, `audio`, `video`. Allowed types/sizes depend on the
app's model and its `file_upload` config (see `GET /parameters`).

## App metadata endpoints

Read-only endpoints to discover how an app is configured. No `user` needed.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/info` | GET | App name, description, `mode` (`chat`/`agent-chat`/`completion`/`workflow`/`advanced-chat`), icon |
| `/parameters` | GET | Input form (`user_input_form`), opening statement, suggested questions, file upload config, speech settings |
| `/meta` | GET | Tool icons and model metadata |
| `/site` | GET | WebApp display settings (title, copyright, privacy policy, disclaimer) |

```bash
# What kind of app is this key for?
curl https://api.dify.ai/v1/info \
  --header 'Authorization: Bearer app-XXXX'

# What inputs does it expect? (drives the `inputs` object you must send)
curl https://api.dify.ai/v1/parameters \
  --header 'Authorization: Bearer app-XXXX'
```

`GET /parameters` is the key one before sending messages — its `user_input_form` lists the
variable names that go into the `inputs` object of `/chat-messages` or `/completion-messages`.

## App types at a glance

| App type | Send endpoint | Conversations | Workflow events |
|----------|---------------|---------------|-----------------|
| Chatbot / Agent | `/chat-messages` | yes | no |
| Chatflow (advanced-chat) | `/chat-messages` | yes | yes |
| Workflow | `/workflows/run` | no | yes |
| Completion | `/completion-messages` | no | no |

## Next steps

- Sending messages → `chat-completion` skill
- Running workflow apps → `workflows` skill
- Managing chat history → `conversations` skill
- Uploading files / audio → `files-audio` skill
- Knowledge bases / RAG → `knowledge-base` skill
- Errors & limits → `troubleshoot` skill
