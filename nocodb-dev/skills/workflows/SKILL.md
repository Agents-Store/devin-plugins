---
name: workflows
description: |
  List, execute, and inspect NocoDB Workflows (the platform's built-in automation engine) via Meta API v3. Use when:
  - "list NocoDB workflows"
  - "execute a workflow"
  - "view workflow execution"
  - "trigger workflow on demand"
  - "fetch execution results"
---

# Workflows & Executions

NocoDB Workflows is the platform's built-in automation engine — a node-graph editor inside the NocoDB UI. The Meta API v3 surface for Workflows is **read + execute only**: you can list workflows, fetch their definitions, run them on demand, list executions, and read execution details. Workflow **authoring** (creating / editing the node graph) lives in the NocoDB UI; this API does not expose it.

> If you need to *create* automations programmatically, integrate with an external orchestrator (n8n, Trigger.dev) instead — see the related plugins. NocoDB Workflows is a no-code in-UI tool.

## Endpoints

| Path | Method | Purpose |
|------|--------|---------|
| `/api/v3/meta/bases/{base_id}/workflows` | `GET` | List workflows in a base |
| `/api/v3/meta/bases/{base_id}/workflows/{workflow_id}` | `GET` | Get one workflow definition (nodes + edges) |
| `/api/v3/meta/bases/{base_id}/workflows/{workflow_id}/execute` | `POST` | Execute the workflow on demand |
| `/api/v3/meta/bases/{base_id}/workflows/{workflow_id}/executions` | `GET` | List recent executions |
| `/api/v3/meta/bases/{base_id}/workflows/{workflow_id}/executions/{execution_id}` | `GET` | Get one execution (per-node results) |

## List Workflows

```bash
curl -sS -H "xc-token: $NOCODB_API_TOKEN" \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/workflows"
```

Returns a `WorkflowList` — array of `{ id, title, description, status, created_at, updated_at }`.

## Get Workflow Definition

```bash
curl -sS -H "xc-token: $NOCODB_API_TOKEN" \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/workflows/$WORKFLOW_ID"
```

Returns a `WorkflowGetResponse` containing:

- `nodes` — array of `WorkflowNode` (each node has type, position, config, ports)
- `edges` — array of `WorkflowEdge` (source/target node IDs)
- `variables` — array of `WorkflowVariableDefinition` (input variables the workflow expects)
- `options` — `WorkflowOptions`

> Probe the spec for the full graph shape:
> ```bash
> jq '.components.schemas.WorkflowGetResponse' \
>    skills/api-reference/references/nocodb-meta-openapi.json
> ```

## Execute a Workflow

```bash
curl -sS -X POST \
  -H "xc-token: $NOCODB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input":   { "customer_id": "rec_abc123", "amount": 1500 },
    "trigger": "manual"
  }' \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/workflows/$WORKFLOW_ID/execute"
```

`input` keys must match the workflow's `WorkflowVariableDefinition` names. The response returns the new `execution_id` — poll `/executions/{execution_id}` to get the result, or stream the dashboard.

## List Recent Executions

```bash
curl -sS -H "xc-token: $NOCODB_API_TOKEN" \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/workflows/$WORKFLOW_ID/executions"
```

Returns a `WorkflowExecutionList` — array of `{ id, status, started_at, finished_at, trigger, error? }`. Status values: `pending`, `running`, `succeeded`, `failed`, `cancelled`.

## Inspect One Execution

```bash
curl -sS -H "xc-token: $NOCODB_API_TOKEN" \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/workflows/$WORKFLOW_ID/executions/$EXECUTION_ID"
```

Returns a `WorkflowExecutionGetResponse` with:

- Top-level: `id`, `status`, `started_at`, `finished_at`, `trigger`, `input`, `output`, `error`
- `node_results` — array of `WorkflowNodeExecutionResult` (status, input, output, error per node)
- `loop_data` — `WorkflowLoopData` for loop nodes

This is your debugging surface: when a workflow fails, the per-node `error` tells you which node broke.

## Common Patterns

### Trigger on a record event

A workflow can be wired in the NocoDB UI to a Hook event. Programmatically you'd:

1. Create the workflow in NocoDB UI (graph + variables).
2. Configure a hook with `notification.type: "Script"` whose script calls the `/execute` endpoint with the triggering record's data — see the **webhooks** and **api-reference** skills.

### Poll until done

```bash
EXEC_ID=$(curl -sS -X POST -H "xc-token: $NOCODB_API_TOKEN" \
  -d '{"trigger":"manual"}' \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/workflows/$WORKFLOW_ID/execute" | jq -r '.id')

while :; do
  STATUS=$(curl -sS -H "xc-token: $NOCODB_API_TOKEN" \
    "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/workflows/$WORKFLOW_ID/executions/$EXEC_ID" | jq -r '.status')
  case "$STATUS" in
    succeeded|failed|cancelled) echo "Done: $STATUS"; break ;;
    *) sleep 2 ;;
  esac
done
```

### List failures from the last hour

```bash
curl -sS -H "xc-token: $NOCODB_API_TOKEN" \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/workflows/$WORKFLOW_ID/executions" \
  | jq '[ .executions[] | select(.status=="failed") | select(.started_at > (now - 3600 | strftime("%Y-%m-%dT%H:%M:%SZ"))) ]'
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 422 on `/execute` | `input` keys don't match workflow variables | Fetch the workflow definition; align `input` to declared `variables` |
| 404 on `/execute` | Workflow disabled or wrong `workflow_id` | List workflows; confirm `status` is enabled |
| Execution stuck `running` | A node is awaiting an external callback | Check that node's expected callback URL; cancel via NocoDB UI |
| Per-node `error` field populated | The named node failed | Open the workflow in NocoDB UI, inspect that node's config |
| Race: `/execute` returns before result is available | Async by design | Poll `/executions/{execution_id}`, or rely on workflow callbacks |

## What This Skill Does NOT Cover

- **Authoring** workflows (creating nodes, connecting edges) — done in the NocoDB UI.
- **Workflow templates** or marketplace integration.
- **Cross-platform automation** (use n8n / Trigger.dev for that, with workflows reaching out via HTTP).

## See Also

- **api-reference** skill — full Meta API v3 reference
- `references/nocodb-meta-openapi.json` — OpenAPI source for all `Workflow*` schemas
- **webhooks** skill — for event-driven triggers that can launch workflows via Script notifications
