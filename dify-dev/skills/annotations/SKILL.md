---
name: annotations
description: >
  This skill should be used when the user asks to "list/create/update/delete Dify
  annotations", "call /apps/annotations", "set up Dify annotation reply", "enable
  annotation reply", "disable annotation reply", or "check annotation reply status".
  Covers the annotation (curated Q&A) subsystem.
---

# Dify — Annotations

Annotations are curated question→answer pairs. With **annotation reply** enabled, incoming
questions similar to a stored question are answered directly from the annotation (bypassing
the LLM), using an embedding model for similarity. For auth/base URL see `setup`.

## GET /apps/annotations — list

```bash
curl 'https://api.dify.ai/v1/apps/annotations?page=1&limit=20' \
  --header 'Authorization: Bearer app-XXXX'
```

Query params: `page`, `limit`, `keyword` (search). Returns a paginated `data` array of
`{ id, question, answer, hit_count, created_at }`.

## POST /apps/annotations — create

```bash
curl -X POST 'https://api.dify.ai/v1/apps/annotations' \
  --header 'Authorization: Bearer app-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{ "question": "What are your hours?", "answer": "9am–5pm, Mon–Fri." }'
```

Returns the created annotation `{ id, question, answer, hit_count, created_at }`.

## PUT /apps/annotations/{annotation_id} — update

```bash
curl -X PUT 'https://api.dify.ai/v1/apps/annotations/{annotation_id}' \
  --header 'Authorization: Bearer app-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{ "question": "What are your opening hours?", "answer": "9am–6pm, Mon–Fri." }'
```

## DELETE /apps/annotations/{annotation_id} — delete

```bash
curl -X DELETE 'https://api.dify.ai/v1/apps/annotations/{annotation_id}' \
  --header 'Authorization: Bearer app-XXXX'
```

Returns 204 No Content.

## Annotation reply settings

### POST /apps/annotation-reply/{action} — enable or disable

`{action}` is `enable` or `disable`. Enabling requires an embedding model; this runs
**asynchronously** and returns a `job_id`.

```bash
# Enable (returns a job_id)
curl -X POST 'https://api.dify.ai/v1/apps/annotation-reply/enable' \
  --header 'Authorization: Bearer app-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{
    "embedding_provider_name": "openai",
    "embedding_model_name": "text-embedding-3-small",
    "score_threshold": 0.9
  }'

# Disable
curl -X POST 'https://api.dify.ai/v1/apps/annotation-reply/disable' \
  --header 'Authorization: Bearer app-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{}'
```

Response: `{ "job_id": "...", "job_status": "waiting" }`.

### GET /apps/annotation-reply/{action}/status/{job_id} — check status

Poll the job created by enable/disable.

```bash
curl 'https://api.dify.ai/v1/apps/annotation-reply/enable/status/{job_id}' \
  --header 'Authorization: Bearer app-XXXX'
```

Response: `{ "job_id": "...", "job_status": "completed", "error_msg": "" }`.

## Endpoint summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/apps/annotations` | GET | List annotations |
| `/apps/annotations` | POST | Create an annotation |
| `/apps/annotations/{id}` | PUT | Update an annotation |
| `/apps/annotations/{id}` | DELETE | Delete an annotation |
| `/apps/annotation-reply/{action}` | POST | Enable/disable annotation reply (async → `job_id`) |
| `/apps/annotation-reply/{action}/status/{job_id}` | GET | Check enable/disable job status |

## Tips

- The `score_threshold` (0–1) controls how close an incoming question must be to trigger a
  stored answer — higher = stricter.
- The embedding provider/model must be configured in the workspace and support the chosen
  index. Enable/disable is async — confirm via the status endpoint before relying on it.
- `hit_count` shows how often an annotation has answered a query.
