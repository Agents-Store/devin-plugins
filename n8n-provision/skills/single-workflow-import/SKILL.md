---
name: single-workflow-import
description: |
  Import and deploy a single workflow to an n8n instance from the official template library or community JSON source. Handles validation, auto-fix, credential stripping, and post-import verification.
  Use when: "import n8n workflow", "deploy n8n template", "install n8n automation", "add workflow to n8n", "import template to n8n", "deploy workflow from JSON", "install community workflow"
---

# Single Workflow Import

Import one workflow into a running n8n instance. Three paths depending on the source — a template in the n8n-mcp local database, a template only on `api.n8n.io`, or community JSON. All calls use `~~capability` with automatic fallback (see CONNECTORS.md).

Every imported workflow arrives **unpublished** (a draft). n8n 2.x replaced "activate" with **publish**; this skill never publishes without an explicit user request.

## Pre-Import Checklist

Run these checks before any import:

1. **Verify instance connectivity** — call `~~instance_health` to confirm the n8n instance is reachable and the API key works.
2. **Check for duplicate names** — call `~~workflow_list` and compare the incoming workflow name against existing workflows. If a duplicate exists, append a suffix (e.g., `Workflow Name (2)`) or ask the user.
3. **Check capabilities, not versions** — n8n stopped reporting its version to API clients in 1.119.0, so `n8n_health_check` usually has no `n8nVersion`. Probe what the key can do instead (`GET /api/v1/discover`, or just try the call) and read the `typeVersion` of each node in the workflow against what the instance accepts.
4. **Check the source** — a paid template (`purchaseUrl` set or `price` > 0; a missing `price` = free) needs the user's go-ahead; a template whose nodes fall in the n8n 3.0 removal list needs the `workflow-analysis` report first. **Price is only on `api.n8n.io` search items**, not on `get_template` or the by-ID endpoints: for a bare template ID, look the item up first (`GET /api/templates/search?rows=20&search=<url-encoded title>`, title from `/api/workflows/templates/<id>`, match on `id`; recipe in `template-discovery/references/TEMPLATE_API.md`). If no search item matches, say so and ask the user before importing — never read "no data" as "free".

If any check fails, stop and report before proceeding.

## Import Path 1: Template in the local database

Use this path when `get_template` finds the template.

```
Step 1: ~~template_get(templateId, mode="full")
        → n8n-mcp get_template; mode is nodes_only | structure | full
        → "Template <id> not found" → go to Path 1b

Step 2: ~~workflow_validate(workflow)
        → validate_workflow({workflow: {nodes, connections}}) on the template's workflow JSON
        → If validation fails → see Error Handling below

Step 3: ~~template_deploy(templateId, name?)
        → n8n_deploy_template: deploys, then auto-fixes
        → Strips credentials (they are NOT transferred)
        → Returns workflowId, requiredCredentials, autoFixStatus, fixesApplied
```

**Options of `n8n_deploy_template`** (all default to `true`):
- `autoFix` — repairs expression format (missing `=` prefix) and `typeVersion` problems after deployment
- `autoUpgradeVersions` — upgrades nodes to the newest `typeVersion` the server supports
- `stripCredentials` — removes credential references (credentials must be set up on the target instance)
- `name` — custom workflow name (default: the template's name)

It does not repair missing connection references and does not move nodes. Use `requiredCredentials` from the result as the input to `credential-planning`, and read `fixesApplied` to see what changed.

## Import Path 1b: Template only on api.n8n.io

Use this path when the template ID is valid on n8n.io but the local database answers "not found" (for example template 2947). `n8n_deploy_template` reads the same local database, so it fails too — build the workflow from the public API instead.

```
Step 1: Fetch the template
        → curl -s https://api.n8n.io/api/workflows/templates/<id> -o /tmp/template-<id>.json
        → HTTP 404 = no such template; report and stop
        → The workflow JSON is .workflow (see template-discovery/references/TEMPLATE_API.md)

Step 2: Build the payload — keep only name, nodes, connections, settings
        → Drop id, meta, tags, active, versionId, pinData (read-only or source-instance data)
        → Remove each node's "credentials" block; note the credential types for credential-planning
        → The TEMPLATE_API.md snippet does both and prints requiredCredentials

Step 3: ~~workflow_validate(payload)
        → validate_workflow({workflow: payload})

Step 4: ~~workflow_create(payload)
        → n8n_create_workflow({name, nodes, connections, settings})
        → Always created unpublished; there is no "active" parameter
        → Returns the new workflow ID

Step 5: ~~workflow_autofix(workflowId)  — preview first
        → n8n_autofix_workflow({id}) shows proposed fixes without changing anything
        → Apply with applyFixes: true after reviewing (expression format, typeVersions, webhook paths)
```

Library templates often contain nodes that n8n 2.0 switched off or n8n 3.0 removes. The autofix preview lists version upgrades and migration notes (`postUpdateGuidance`) — read them before applying.

## Import Path 2: Community JSON

Use this path for workflows from GitHub, n8n community forums, blog posts, or any raw JSON source.

```
Step 1: Fetch the raw JSON
        → If URL provided: download the JSON file directly
        → If file provided: read from local path
        → Verify it is valid JSON with a "nodes" array and "connections" object

Step 2: Build the payload (name, nodes, connections, settings only; strip credentials)
        → Same as Path 1b, Step 2

Step 3: ~~workflow_validate(payload)
        → validate_workflow({workflow: payload}) — checks structure, node types, connections
        → If validation fails → see Error Handling below

Step 4: ~~workflow_create(payload)
        → n8n_create_workflow — creates the workflow, unpublished
        → Returns the new workflow ID

Step 5: ~~workflow_autofix(workflowId) in preview mode, apply after review
```

## Credential Reconfiguration

Credentials are NEVER transferred during import — this is by design for security.

After importing, guide the user through credential setup:

| Step | Action |
|------|--------|
| 1 | Open the imported workflow in the n8n editor |
| 2 | Identify nodes with missing credentials (shown with warning icons) |
| 3 | For each node, select or create the appropriate credential |
| 4 | Use `~~credential_manage` to list existing credentials that may already match; token and key credentials can be created through it (`getSchema`, then `create`), OAuth2 credentials need a browser consent in the editor |
| 5 | Test each credential connection before publishing the workflow |

**Common credential types encountered:**

| Service Category | Typical Auth Method | Notes |
|-----------------|-------------------|-------|
| Email (Gmail, Outlook) | OAuth2 | Requires browser-based authorization |
| Messaging (Slack, Discord) | OAuth2 or Bot Token | Bot tokens are simpler to set up |
| Databases (Postgres, MySQL) | Connection string | Host, port, user, password, database |
| APIs (REST, GraphQL) | API Key or Header Auth | Check the service's docs for key format |
| Cloud (AWS, GCP) | Access Key + Secret | Use IAM roles with least privilege |

## Post-Import Verification

After a successful import, verify the deployment:

```
1. ~~workflow_list → confirm the new workflow appears
2. Compare node count:
   → Source JSON node count vs deployed workflow node count
   → Mismatch indicates dropped nodes — investigate
3. ~~workflow_validate by id → n8n_validate_workflow({id}) checks the workflow now on the instance
4. Review any auto-fix changes applied during deploy (fixesApplied / autofix preview)
```

## Publish Safety Protocol

In n8n 2.x a saved workflow is a **draft**; what runs in production is the **published version**. Editing a published workflow leaves the edit as a draft until it is published again. Follow this sequence strictly:

1. **Import as draft** — never publish on import
2. **Configure credentials** — link all required credentials
3. **Review trigger nodes** — check webhook paths, schedules, polling intervals
4. **Test manually** — use n8n's "Execute workflow" button with sample data
5. **Publish** — only after a successful manual test **and** an explicit user request: `~~workflow_publish` (`n8n_update_partial_workflow` operation `activateWorkflow`, or native `publish_workflow`), or the Publish button in the editor

> WARNING: Publishing a workflow with webhook triggers immediately exposes those endpoints. Verify webhook paths do not conflict with existing workflows. Publishing is asynchronous and can end partial or failed — check the result.
>
> Publishing needs the `workflow:activate` scope on the API key and the `workflow:publish` permission on the project; without them the call fails with `PUBLISH_FORBIDDEN` (n8n 2.39+). A `409` means an open workflow review or a webhook path collision blocks it. "Activate" is the old name for the same step.

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `Template <id> not found` from `get_template` or `n8n_deploy_template` | The template is not in the n8n-mcp local database (about 2,350 of 12,900) | Use Path 1b: fetch from `api.n8n.io`, then `~~workflow_create` |
| HTTP 404 from `api.n8n.io` | No template with that ID | Verify the ID; search by keyword instead |
| Validation failure: unknown node type | Community node not installed | Install the required community node package first |
| Validation failure: invalid connections | Connections reference node names that do not exist | Re-map connections or remove broken references |
| Create fails: unknown property | Payload carried `id`, `meta`, `tags`, `active` or `versionId` | Rebuild the payload from `name, nodes, connections, settings` only |
| Deploy timeout | Instance overloaded or unreachable | Retry after confirming instance health via `~~instance_health` |
| Duplicate workflow name | Name already exists on instance | Rename the workflow before import or append a numeric suffix |
| Missing community nodes | Workflow uses nodes not in the base install | List missing nodes, install them, then retry import |
| JSON parse error | Malformed source file | Validate the JSON structure before attempting import |
| `PUBLISH_FORBIDDEN` | Key lacks `workflow:activate` or user lacks `workflow:publish` | Use a key and user with publish rights, or publish in the editor |

## Decision Tree

```
Is the source an official n8n template ID?
├─ YES
│  ├─ get_template finds it → Path 1: ~~template_get → ~~workflow_validate → ~~template_deploy
│  └─ "not found" → Path 1b: api.n8n.io → payload → ~~workflow_validate → ~~workflow_create → ~~workflow_autofix
└─ NO
   ├─ Is it a raw JSON file or URL?
   │  └─ YES → Path 2: fetch JSON → payload → ~~workflow_validate → ~~workflow_create
   └─ Is it a community forum/blog link?
      └─ YES → Extract JSON from page → Path 2
```
