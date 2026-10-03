# Record-Driven Background Workflows

Three workflow shapes for work that starts from records in another system (a database, NocoDB, NocoBase, a CRM) and writes a status back. They are sketches to adapt, not full walkthroughs — the node-level detail lives in the skills named under each one. All node names are the n8n 2.x editor names.

Use n8n for these while a run is short and visual. Hand work that runs for minutes, needs durable retries or streams model output to a code-first background task runner instead (Trigger.dev is the one in this stack).

## 1. Scheduled sync

```
[Schedule Trigger] → [Read records: status = "queued"] → [Loop Over Items]
   → [Transform (Set / Code)] → [HTTP Request: external API] → [Update record: status = "synced"]
```

- Read only what is waiting (a status or a "changed since" filter), in pages — never the whole table on every tick
- Put the status update inside the loop, after the external call succeeds, so a failure leaves the record `queued` for the next tick
- On the network node set Retry On Fail (`retryOnFail`, `maxTries`, `waitBetweenTries`) before wiring any error path
- Depth: `n8n-workflow-patterns` (scheduled tasks), `n8n-node-configuration`

## 2. Webhook-triggered processing

```
[Webhook] → [Validate payload (IF / Code)] → [Switch on event type]
   ├─ insert → [Process new record]   → [Respond to Webhook: 200]
   ├─ update → [Sync changes]         → [Respond to Webhook: 200]
   └─ delete → [Clean up]             → [Respond to Webhook: 200]
```

- The body arrives under `{{ $json.body }}`; read the event type from the payload field the sender uses (for NocoDB, `type` — `records.after.insert`, `records.after.update`, `records.after.delete`)
- The Webhook node has a test URL and a production URL; only the production URL receives events, and only after the workflow is **published** (n8n 2.x: the draft becomes live on Publish)
- Pick the response mode on purpose: *Respond to Webhook* node when the caller needs the result, *Immediately* when the sender only needs an acknowledgement — and answer fast, because senders time out and retry. Work that takes longer than a few seconds belongs behind an immediate response or in a background task
- Make the processing idempotent: the same event can arrive twice, so look the record up by its id and skip what is already done
- Depth: `n8n-workflow-patterns` (webhook processing), `n8n-error-handling` (response shapes)

## 3. Error recovery

```
Main workflow → Settings → Error workflow → this one:

[Error Trigger] → [Log failure to an error table/record] → [Check retry count]
   ├─ below max → [Wait] → [Retry the failed execution]
   └─ at max    → [Send alert]
```

- The Error Trigger runs in its own workflow, which you select in the failing workflow's settings; it receives the failed workflow's name, the execution id and URL, and the error message
- Store the original payload (or the record id) with the failure — the error item does not reliably carry it — so a retry has something to run on
- Retry with the public API: `POST /executions/{executionId}/retry` (HTTP Request node with an n8n API credential; scope `execution:retry`). `{"loadWorkflow": true}` runs the currently saved workflow instead of the version that failed — use it after you have fixed the cause. It answers with the id of the new execution (see the `api-reference` skill). Alternatively re-invoke the workflow's own door: its webhook URL or an Execute Workflow node with the stored payload
- Count attempts on the record, not in workflow memory, and stop at a maximum: an unbounded retry loop turns one bad record into an outage
- Depth: `n8n-error-handling` (`ERROR_WORKFLOWS.md`, node error outputs), `n8n-subworkflows`

## Credentials and environment values

n8n 2.x blocks `$env` in expressions and Code nodes by default (`N8N_BLOCK_ENV_ACCESS_IN_NODE`). Keep tokens in credentials (HTTP Request → Header Auth) and base URLs fixed in the node; do not build `{{ $env.SOME_URL }}` into a workflow. See `n8n-code-javascript` and `n8n-self-hosting` (security) for the opt-in and what it costs.
