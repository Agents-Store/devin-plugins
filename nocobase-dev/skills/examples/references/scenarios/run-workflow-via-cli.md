# Scenario 2 — Trigger a workflow from CLI, monitor via API

Goal: kick off a workflow from a terminal where `nb` is available, then poll the executions endpoint over HTTP until completion. Demonstrates a typical mixed-surface usage: write via CLI (clean local syntax, no auth setup), read via API (queryable from any host).

## Prerequisites

- A workflow keyed `order-fulfilment` already exists and is enabled. If not, `nocobase-workflow-manage` covers creation.
- Local `nb` CLI installed (`npm install -g @nocobase/cli@beta`) and pointed at the right project.
- A bearer token for the API polling step (`auth` skill).

```bash
export NB_URL="https://app.example.com"
export TOKEN="<your-bearer-token>"
H='Authorization: Bearer '"${TOKEN}"
```

## 1. Trigger the workflow

```bash
nb api workflows trigger \
   --tk order-fulfilment \
   --data '{"orderId":100,"customer":{"id":7}}'
```

Output includes the `executionId`. Capture it:

```bash
EXEC_ID=$(nb api workflows trigger --tk order-fulfilment \
            --data '{"orderId":100}' --json | jq -r '.data.executionId')
```

## 2. Poll until done

`status` codes: `0` = queued, `1` = resolved, `-1` = failed, `2` = cancelled.

```bash
while :; do
  STATUS=$(curl -s -H "$H" \
    "${NB_URL}/api/executions:get?filterByTk=${EXEC_ID}" \
    | jq -r '.data.status')
  echo "execution ${EXEC_ID} status=${STATUS}"
  case "$STATUS" in
    1|-1|2) break ;;
    *) sleep 2 ;;
  esac
done
```

## 3. Inspect failed jobs

```bash
curl -H "$H" \
  "${NB_URL}/api/jobs:list?filter=%7B%22executionId%22%3A${EXEC_ID}%7D&pageSize=200" \
  | jq '.data[] | {id, status, nodeId, result}'
```

## 4. Cancel a stuck execution (rare)

```bash
curl -X POST -H "$H" \
     "${NB_URL}/api/executions:cancel?filterByTk=${EXEC_ID}"
```

## 5. Why mix CLI and API here

- `nb api workflows trigger` is the safest local trigger — no token to manage, no host/CORS concerns.
- The polling loop lives in monitoring or CI infrastructure where the API is the only option.
- If the whole pipeline runs server-side from another service, replace step 1 with `POST /api/workflows:trigger?filterByTk=order-fulfilment` and skip the CLI entirely.

## Common gotchas

- `--tk` accepts either the numeric primary key or the workflow `key` (string). Prefer the string key — it survives backups and migrations.
- A workflow that is *disabled* returns `400 disabled workflow` from both surfaces. Enable it via `nocobase-workflow-manage` first.
- Long-running async branches (manual approvals, schedules) keep `status: 0` indefinitely — use `userWorkflowTasks` and `flow_nodes` test endpoints to advance them.
