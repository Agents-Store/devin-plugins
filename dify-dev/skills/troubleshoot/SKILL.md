---
name: troubleshoot
description: >
  This skill should be used when a Dify API call fails or behaves unexpectedly — "Dify
  401 / 404 / 429 error", "Dify conversation not found", "Dify blocking timeout",
  "Dify rate limit", "why is my Dify conversation empty", "Dify user mismatch", or
  "Dify file upload not working". Error codes, limits, and common pitfalls.
---

# Dify API — Troubleshooting

For auth/base URL fundamentals see the `setup` skill.

## HTTP status & error format

Errors return JSON like:

```json
{ "status": 400, "code": "invalid_param", "message": "..." }
```

| Status | Common cause | Fix |
|--------|--------------|-----|
| 400 | Bad/missing param, malformed body | Validate against `GET /parameters`; ensure `inputs` keys match the app's variables |
| 401 | Missing/invalid API key | Send `Authorization: Bearer <key>`; use the **app** key for Service API, **dataset** key for Knowledge API |
| 403 | Action not allowed | e.g. `document_indexing` — can't delete a document mid-index; wait for `completed` |
| 404 | Resource not found | Wrong id, or **`user` mismatch** (see below); confirm base URL has `/v1` |
| 413 | Payload too large | Reduce file size; check the app's `file_upload` limits |
| 429 | Rate limited | Back off; honor `Retry-After`; see rate limits below |
| 500 | Server error | Retry with backoff; check self-hosted logs |
| 503 | Service unavailable | Model provider down or app not published; retry later |

## Common pitfalls

### Conversation/messages come back empty or 404
The `user` field is the scope key. If you create a conversation with `user: "a"` and then
list with `user: "b"`, you get nothing. **Use the same `user` string for the same person on
every call.** Also note: Service API users and WebApp users are **separate namespaces** —
a conversation created in the WebApp is not visible via the Service API and vice-versa.

### Blocking request times out (~100s)
On Dify Cloud, `blocking` mode is behind a ~100-second proxy timeout. Long generations or
multi-step workflows will drop the connection. **Use `response_mode: "streaming"`** for
chat UIs, long outputs, and workflows.

### `inputs` rejected / variable errors
The `inputs` object must contain exactly the variables defined in the app's
`user_input_form`. Call `GET /parameters` first and send `{}` only if the app has no
required variables.

### File upload not accepted
- Upload with `multipart/form-data` (use `--form`), not JSON.
- Include the `user` form field — it scopes the file.
- The file `type`/extension/size must be allowed by the app's `file_upload` config
  (`GET /parameters`). Reference it later with
  `{ "transfer_method": "local_file", "upload_file_id": "<id>" }`.

### Audio endpoints fail
`/audio-to-text` and `/text-to-audio` require the app to have an STT / TTS model configured.
Without it you'll get a model/config error — enable the model in the app settings.

### Stop endpoint does nothing
Stop only works in `streaming` mode, needs the **`task_id`** from a streamed event (not the
`message_id` / `workflow_run_id`), and the `user` must match the run's `user`.

### Wrong key for Knowledge Base calls
Knowledge Base / Datasets endpoints use a **Knowledge API key** (`dataset-…`), not an app
key (`app-…`). Using the app key returns 401/403.

## Rate limits

- Dify Cloud applies plan-based rate limits. Inspect response headers when present:
  `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.
- On 429, wait and retry with **exponential backoff**; honor `Retry-After` if returned.
- Self-hosted has no built-in API rate limiting (configure at your proxy/gateway).

## Debugging checklist

1. Base URL ends with `/v1`?
2. Correct key type (`app-…` for Service API, `dataset-…` for Knowledge API)?
3. `user` present and consistent?
4. `inputs` match `GET /parameters`?
5. Long output → `streaming` instead of `blocking`?
6. For stop/detail → using `task_id` vs `workflow_run_id` correctly?
7. Reproduce with curl `-v` to see status code and the `code`/`message` body.
