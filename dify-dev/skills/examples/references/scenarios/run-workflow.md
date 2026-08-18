# Scenario: Run a Workflow app

Call a Dify **Workflow** app as a backend function: inspect its inputs, run it (blocking and
streaming), fetch the run detail, and list logs.

```bash
BASE=https://api.dify.ai/v1          # or https://your-host/v1
KEY=app-XXXXXXXXXXXXXXXXXXXX
USER=user-123
```

## 1. Inspect inputs (setup skill)

```bash
curl "$BASE/info"       --header "Authorization: Bearer $KEY"   # mode should be "workflow"
curl "$BASE/parameters" --header "Authorization: Bearer $KEY"   # user_input_form → input keys
```

## 2. Run (blocking) — get outputs directly

```bash
curl -X POST "$BASE/workflows/run" \
  --header "Authorization: Bearer $KEY" \
  --header 'Content-Type: application/json' \
  --data "{
    \"inputs\": { \"text\": \"Summarize: Dify is an LLM app platform.\" },
    \"response_mode\": \"blocking\",
    \"user\": \"$USER\"
  }"
# → { "workflow_run_id": "<RID>", "data": { "status": "succeeded", "outputs": { ... } } }
```

Check `data.status == "succeeded"` before reading `data.outputs`.

## 3. Run (streaming) — observe node-by-node progress

```bash
curl -N -X POST "$BASE/workflows/run" \
  --header "Authorization: Bearer $KEY" \
  --header 'Content-Type: application/json' \
  --data "{
    \"inputs\": { \"text\": \"Summarize: Dify is an LLM app platform.\" },
    \"response_mode\": \"streaming\",
    \"user\": \"$USER\"
  }"
```

Events: `workflow_started` → `node_started`/`node_finished` … → `workflow_finished` (final
`outputs` on `workflow_finished.data`). To abort, POST the streamed `task_id` to
`/workflows/tasks/{task_id}/stop` with the same `user`.

## 4. Fetch a run's detail later (workflows skill)

```bash
RID=<workflow_run_id-from-step-2>
curl "$BASE/workflows/run/$RID" --header "Authorization: Bearer $KEY"
# → { "status": "...", "outputs": {...}, "elapsed_time": ..., "total_tokens": ... }
```

## 5. List recent runs

```bash
curl "$BASE/workflows/logs?page=1&limit=20" --header "Authorization: Bearer $KEY"

# filter by status
curl "$BASE/workflows/logs?status=failed&limit=20" --header "Authorization: Bearer $KEY"
```

## Notes

- Workflow apps have no `query` and no `conversation_id` — everything comes from `inputs`.
- `task_id` (for stop) is transient; `workflow_run_id` (for detail) is the persistent record.
- Prefer `streaming` for anything non-trivial to avoid the ~100s blocking timeout.
