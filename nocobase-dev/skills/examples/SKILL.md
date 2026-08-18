---
name: examples
description: "Use when the user asks for an end-to-end example, walkthrough, or sample of doing something in NocoBase v2 — \"show me how to\", \"walk me through\", \"give me a complete example\", \"sample script for NocoBase\". Indexes worked scenarios that mix REST API and `nb` CLI calls."
---

# NocoBase v2 — worked examples

Three end-to-end scenarios that exercise both surfaces (REST API + `nb` CLI) and demonstrate when to pick each. Each scenario is a self-contained walkthrough.

## Scenarios

| # | File | Mix | What it teaches |
|---|---|---|---|
| 1 | `references/scenarios/create-collection-via-api.md` | API only | Define a `posts` collection with two fields, write a record, list with a filter, then verify via `nb api collections list`. |
| 2 | `references/scenarios/run-workflow-via-cli.md` | CLI + API | Trigger a workflow with `nb api workflows trigger`, then poll executions through `/api/executions:list` until `status: 1`. |
| 3 | `references/scenarios/enable-plugin-and-create-api-key.md` | CLI + API | Enable the `api-keys` plugin, create a token via the API, then make an authorised call as the new bot identity. |

## How to use these

- Read the matching file when the user asks for a "complete example" or one of the listed flows.
- Follow the steps in order — each scenario assumes the previous step succeeded.
- Replace placeholders: `${NB_URL}`, `${TOKEN}`, and any collection/workflow names with real values.
- If the user requests a related but different scenario, treat the closest scenario as a template and adapt it; do not invent new patterns when an existing one fits.

## Where to look next

- For the full HTTP endpoint catalogue → `api-reference`.
- For the full `nb` command catalogue → `cli-recipes`.
- For schema/field design patterns → `nocobase-data-modeling`.
- For workflow internals (nodes, branches, executions) → `nocobase-workflow-manage`.
- For ACL on the role attached to a token → `nocobase-acl-manage`.
