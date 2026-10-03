---
name: workflows
description: |
  List, execute, and inspect NocoDB Workflows (the platform's built-in automation engine) via Meta API v3; author drafts over MCP on Cloud/licensed. Use when:
  - "list NocoDB workflows"
  - "execute a workflow"
  - "view workflow execution"
  - "trigger workflow on demand"
  - "fetch execution results"
---

# Workflows & Executions

NocoDB Workflows is the platform's built-in automation engine — a node-graph editor inside the NocoDB UI. The **REST** surface (Meta API v3) for Workflows is **read + execute only**: you can list workflows, fetch their definitions, run them on demand, list executions, and read execution details. REST does not expose workflow **authoring**.

**Authoring over MCP (Cloud / licensed self-hosted).** The MCP server can write **drafts**: `listTools category: "workflows"` (and `"workflow-nodes"`) reveals `createWorkflow`, `updateWorkflow`, `duplicateWorkflow`, `deleteWorkflow`, `publishWorkflow`, the single-node tools (`addWorkflowNode`, `updateWorkflowNode`, `deleteWorkflowNode`, `connectWorkflowNodes`, `disconnectWorkflowNodes`) and `validateWorkflowNode`. Read `getWorkflowAuthoringInstructions` and `listWorkflowNodeTypes` before writing a draft. Only the draft is writable; every node must be tested (`validateWorkflowNode`) before `publishWorkflow` puts it live, and **enabling an automation and its `run_as` identity stay in the UI** — a human sets those. Writes replace the whole draft graph (last write wins against anyone editing in the UI), so `getWorkflow` first, change the graph it returns, and send it back. Community Edition has no workflow tools: author in the UI.

> For automations that must run across several systems, an external orchestrator (n8n, Trigger.dev) is still the better fit — see the related plugins.

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
curl -sS -H "xc-token: ${NOCODB_TOKEN}" \
  "${NOCODB_URL}/api/v3/meta/bases/$BASE_ID/workflows"
```

Returns a `WorkflowList` — array of `{ id, title, description, status, created_at, updated_at }`.

## Get Workflow Definition

```bash
curl -sS -H "xc-token: ${NOCODB_TOKEN}" \
  "${NOCODB_URL}/api/v3/meta/bases/$BASE_ID/workflows/$WORKFLOW_ID"
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
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "trigger_data": { "customer_id": "rec_abc123", "amount": 1500 }
  }' \
  "${NOCODB_URL}/api/v3/meta/bases/$BASE_ID/workflows/$WORKFLOW_ID/execute"
```

The body is `WorkflowExecuteReq`: one optional key, `trigger_data`, the object handed to the workflow's trigger node (the spec: "Data to pass to the workflow trigger"). Which keys the trigger expects is defined by the trigger node in the workflow definition (`GET .../workflows/$WORKFLOW_ID`). The response is `{ "id": "<execution id>" }` and the run is queued, not finished: poll `/executions/{id}` for the result.

## List Recent Executions

```bash
curl -sS -H "xc-token: ${NOCODB_TOKEN}" \
  "${NOCODB_URL}/api/v3/meta/bases/$BASE_ID/workflows/$WORKFLOW_ID/executions"
```

Returns a `WorkflowExecutionList`: `{ "list": [ { id, workflow_id, status, started_at, finished_at, created_at } ] }`, paged with the `limit` (default 25) and `offset` query parameters. `status` is one of `running`, `waiting`, `completed`, `error`, `cancelled`, `skipped`; `completed`, `error`, `cancelled` and `skipped` are final, and `waiting` is a run paused by a delay or wait-until node.

## Inspect One Execution

```bash
curl -sS -H "xc-token: ${NOCODB_TOKEN}" \
  "${NOCODB_URL}/api/v3/meta/bases/$BASE_ID/workflows/$WORKFLOW_ID/executions/$EXECUTION_ID"
```

Returns a `WorkflowExecutionGetResponse` with:

- Top-level: `id`, `workflow_id`, `status`, `started_at`, `finished_at`, `created_at`
- `execution_data` (`WorkflowExecutionData`) with the full run state:
  - `nodeResults` — array of `WorkflowNodeExecutionResult` (per node: `nodeTitle`, `status` of `pending`, `running`, `success`, `error` or `skipped`, `input`, `output`, `error`, `logs`)
  - `triggerData` — what `/execute` was given as `trigger_data`
  - `loops` — `WorkflowLoopData` per iterate node, keyed by node id
  - `currentNodeId`, `pausedAt`, `resumeAt` — where a `running` or `waiting` run is

This is your debugging surface: when a run ends in `error`, the `error` of the failing entry in `execution_data.nodeResults` tells you which node broke.

## Common Patterns

### Trigger on a record event

A workflow can be wired in the NocoDB UI to a Hook event. Programmatically you'd:

1. Create the workflow in NocoDB UI (graph + variables).
2. Configure a hook with `notification.type: "Script"` whose script calls the `/execute` endpoint with the triggering record's data — see the **webhooks** and **api-reference** skills.

### Poll until done

```bash
EXEC_ID=$(curl -sS -X POST -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" -d '{"trigger_data":{}}' \
  "${NOCODB_URL}/api/v3/meta/bases/$BASE_ID/workflows/$WORKFLOW_ID/execute" | jq -r '.id')

while :; do
  STATUS=$(curl -sS -H "xc-token: ${NOCODB_TOKEN}" \
    "${NOCODB_URL}/api/v3/meta/bases/$BASE_ID/workflows/$WORKFLOW_ID/executions/$EXEC_ID" | jq -r '.status')
  case "$STATUS" in
    completed|error|cancelled|skipped) echo "Done: $STATUS"; break ;;   # running and waiting are not final
    *) sleep 2 ;;
  esac
done
```

### List failures from the last hour

```bash
curl -sS -H "xc-token: ${NOCODB_TOKEN}" \
  "${NOCODB_URL}/api/v3/meta/bases/$BASE_ID/workflows/$WORKFLOW_ID/executions" \
  | jq '[ .list[] | select(.status=="error") | select((.started_at // "") > (now - 3600 | strftime("%Y-%m-%dT%H:%M:%SZ"))) ]'
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `/execute` rejected with a 4xx, or the run ends in `error` at the trigger | `trigger_data` is not an object, or does not match what the trigger node expects | Fetch the workflow definition; align `trigger_data` with its trigger node |
| 404 on `/execute` | Workflow not published/enabled, or wrong `workflow_id` | List workflows; confirm the automation is published and enabled (a human enables it in the UI) |
| Execution stuck `running` | A node is awaiting an external callback | Check that node's expected callback URL; cancel via NocoDB UI |
| Execution `waiting` | A delay or wait-until node paused it | `execution_data.resumeAt` says when it continues; keep polling |
| `error` set on an `execution_data.nodeResults` entry | The named node failed | Open the workflow in NocoDB UI, inspect that node's config |
| Race: `/execute` returns before result is available | Async by design | Poll `/executions/{execution_id}`, or rely on workflow callbacks |

## What This Skill Does NOT Cover

- **Authoring** workflows in depth (node configuration forms, expression syntax) — use the MCP authoring instructions or the NocoDB UI; enabling and `run_as` are UI-only.
- **Workflow templates** or marketplace integration.
- **Cross-platform automation** (use n8n / Trigger.dev for that, with workflows reaching out via HTTP).

## See Also

- **api-reference** skill — full Meta API v3 reference
- `references/nocodb-meta-openapi.json` — OpenAPI source for all `Workflow*` schemas
- **webhooks** skill — for event-driven triggers that can launch workflows via Script notifications
