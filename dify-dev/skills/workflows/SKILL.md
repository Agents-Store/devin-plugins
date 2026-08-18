---
name: workflows
description: >
  This skill should be used when the user asks to "run a Dify workflow",
  "call /workflows/run", "execute a Dify workflow app via API", "get a workflow run
  result", "list Dify workflow logs", "stop a Dify workflow task", or work with
  Chatflow/Workflow node events. Covers Workflow-type apps (no conversation wrapper).
---

# Dify — Workflows

Running **Workflow-type apps** via the API. These execute a graph of nodes and return
structured `outputs` — no conversation, no `query`. For auth/base URL see `setup`; for the
SSE node events see the `chat-completion` skill's
[references/streaming-events.md](../chat-completion/references/streaming-events.md).

> Chat**flow** apps are sent via `/chat-messages` (see `chat-completion` skill) but emit the
> same workflow node events. Plain **Workflow** apps use the `/workflows/run` endpoints here.

## POST /workflows/run — execute a workflow

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `inputs` | object | yes | Workflow input variables (keys from `GET /parameters`) |
| `response_mode` | string | yes | `streaming` or `blocking` |
| `user` | string | yes | End-user identifier |
| `files` | array | no | Multimodal inputs (see `setup` skill) |

```bash
curl -X POST 'https://api.dify.ai/v1/workflows/run' \
  --header 'Authorization: Bearer app-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{
    "inputs": { "text": "Summarize this paragraph..." },
    "response_mode": "blocking",
    "user": "user-123"
  }'
```

Blocking response (shape):

```json
{
  "task_id": "...",
  "workflow_run_id": "...",
  "data": {
    "id": "...",
    "workflow_id": "...",
    "status": "succeeded",
    "outputs": { "result": "..." },
    "error": null,
    "elapsed_time": 1.23,
    "total_tokens": 500,
    "total_steps": 5,
    "created_at": 1700000000,
    "finished_at": 1700000002
  }
}
```

In streaming mode you receive `workflow_started` → `node_started`/`node_finished` … →
`workflow_finished`; the final `outputs` are on `workflow_finished.data`.

## POST /workflows/run-by-id — run a specific published version

Run a particular workflow id (e.g. a specific published version) rather than the default.

```bash
curl -X POST 'https://api.dify.ai/v1/workflows/run-by-id/{workflow_id}' \
  --header 'Authorization: Bearer app-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{ "inputs": {}, "response_mode": "blocking", "user": "user-123" }'
```

## GET /workflows/run/{workflow_run_id} — get run detail

Fetch the result/status of a past run (use `workflow_run_id` from the run response).

```bash
curl 'https://api.dify.ai/v1/workflows/run/{workflow_run_id}' \
  --header 'Authorization: Bearer app-XXXX'
```

```json
{
  "id": "...",
  "workflow_id": "...",
  "status": "succeeded|running|failed|stopped",
  "inputs": "{...}",
  "outputs": { "...": "..." },
  "error": null,
  "elapsed_time": 1.23,
  "total_tokens": 500,
  "total_steps": 5,
  "created_at": 1700000000,
  "finished_at": 1700000002
}
```

## POST /workflows/tasks/{task_id}/stop — stop a running task

Streaming runs only. `user` must match the one that started the run.

```bash
curl -X POST 'https://api.dify.ai/v1/workflows/tasks/{task_id}/stop' \
  --header 'Authorization: Bearer app-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{ "user": "user-123" }'
```

Returns `{ "result": "success" }`.

## GET /workflows/logs — list workflow runs

```bash
curl 'https://api.dify.ai/v1/workflows/logs?page=1&limit=20' \
  --header 'Authorization: Bearer app-XXXX'
```

Query params: `keyword`, `status` (`succeeded`/`failed`/`stopped`/`running`), `page`,
`limit`, and (for chatflow) `created_by_end_user_session_id`,
`created_by_account`. Returns a paginated `data` array of run summaries.

## Endpoint summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/workflows/run` | POST | Execute the workflow app |
| `/workflows/run-by-id/{workflow_id}` | POST | Execute a specific workflow version |
| `/workflows/run/{workflow_run_id}` | GET | Get a run's status & outputs |
| `/workflows/tasks/{task_id}/stop` | POST | Stop a streaming run |
| `/workflows/logs` | GET | List past runs |

## Tips

- `status` values: `running`, `succeeded`, `failed`, `stopped`. Always check it before
  reading `outputs`.
- `task_id` (transient, for stop) ≠ `workflow_run_id` (persistent record, for detail).
- For long workflows prefer `streaming` — `blocking` is subject to the ~100s timeout on Cloud.
