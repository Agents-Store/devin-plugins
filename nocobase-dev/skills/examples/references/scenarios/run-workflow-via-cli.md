# Scenario 2 — Run a workflow manually, monitor via API

Goal: start one workflow run by hand (REST, or the `nb` twin), then poll the executions endpoint until the run ends. Typical for testing a new workflow or re-running one from a script.

## Prerequisites

- A workflow already exists and is **enabled**. If not, `nocobase-workflow-manage` covers creation.
- The workflow's **integer id** — the manual-run endpoint does not accept the workflow `key`:

  ```bash
  curl -H "$H" "${NB_URL}/api/workflows:list?filter=%7B%22key%22%3A%22order-fulfilment%22%7D" \
    | jq '.data[] | {id, key, enabled, current}'
  ```

  Use the row with `current: true`.
- A bearer token (`auth` skill). Optional: the `nb` CLI with an env (`cli-recipes`) for the CLI form in step 1.

```bash
export NB_URL="https://app.example.com"
export TOKEN="<your-bearer-token>"
H='Authorization: Bearer '"${TOKEN}"
J='Content-Type: application/json'
WF_ID=12     # the workflow id from the lookup above
```

## 1. Run the workflow

`POST /api/workflows:execute?filterByTk=<id>` — the **entire JSON body is the trigger context**; there is no `values` envelope or other wrapper around it. The shape depends on the trigger type: a collection-event trigger reads `data` (the record), a schedule trigger reads `date`, and so on. Optional `autoRevision=1` creates a new revision after the first execution of a never-executed version.

```bash
curl -s -X POST -H "$H" -H "$J" \
     -d '{"data":{"id":100,"status":"paid","customer":{"id":7}}}' \
     "${NB_URL}/api/workflows:execute?filterByTk=${WF_ID}"
```

Response: `{ "execution": { "id": …, "status": … }, "newVersionId": … }` (the object may sit under a `data` key). Capture the execution id:

```bash
EXEC_ID=$(curl -s -X POST -H "$H" -H "$J" \
            -d '{"data":{"id":100,"status":"paid"}}' \
            "${NB_URL}/api/workflows:execute?filterByTk=${WF_ID}" \
          | jq -r '.data.execution.id // .execution.id')
```

The CLI twin (the `nb api workflow` group is generated from the app's OpenAPI — confirm the command with `nb api workflow workflows execute -h`):

```bash
nb api workflow workflows execute --filter-by-tk "${WF_ID}" --body-file context.json -j
```

## 2. Poll until done

`status` codes: `null` = queued, `0` = started (running, possibly waiting on an async node), `1` = resolved, `-1` = failed, `-2` = error, `-3` = aborted, `-4` = canceled, `-5` = rejected, `-6` = retry needed. Anything other than `null` or `0` is a final state.

```bash
while :; do
  STATUS=$(curl -s -H "$H" \
    "${NB_URL}/api/executions:get?filterByTk=${EXEC_ID}" \
    | jq -r '.data.status')
  echo "execution ${EXEC_ID} status=${STATUS}"
  case "$STATUS" in
    null|0) sleep 2 ;;
    *) break ;;
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

The execution and its pending jobs normally end as `-3` (aborted).

## 5. Why REST is the primary path here

- It works from any host and any pipeline, and the polling loop lives in monitoring or CI where HTTP is the only option anyway.
- The request shape is fixed by the bundled OpenAPI (`/workflows:execute`), so it does not depend on which commands the connected app generated for `nb`.
- Use the CLI twin when you are already in a terminal with an env configured — it carries the credential for you.
- `:trigger` is a different action that exists only for custom-action triggers (a "Trigger Workflow" button); it is not the manual-run endpoint. See `nocobase-workflow-manage`.

## Common gotchas

- `filterByTk` must be the numeric workflow **id**; a key such as `order-fulfilment` is rejected. Look the id up first (above).
- The body is required by the spec and must be a JSON object holding the trigger context itself — not wrapped in `values` or `data` unless the trigger's own context has that key.
- A workflow that is *disabled* is not triggered — expect a `400`. Enable it via `nocobase-workflow-manage` first.
- Long-running async branches (manual approvals, schedules) keep `status: 0` indefinitely — use `userWorkflowTasks` and `flow_nodes` test endpoints to advance them.
