---
name: single-workflow-import
description: |
  Import and deploy a single workflow to an n8n instance from the official template library or community JSON source. Handles validation, auto-fix, credential stripping, and post-import verification.
  Use when: "import n8n workflow", "deploy n8n template", "install n8n automation", "add workflow to n8n", "import template to n8n", "deploy workflow from JSON", "install community workflow"
---

# Single Workflow Import

Import one workflow into a running n8n instance. Two paths depending on source — official template or community JSON. All calls use `~~capability` with automatic fallback (see CONNECTORS.md).

## Pre-Import Checklist

Run these checks before any import:

1. **Verify instance connectivity** — call `~~instance_audit` to confirm the n8n instance is reachable and healthy.
2. **Check for duplicate names** — call `~~workflow_list` and compare the incoming workflow name against existing workflows. If a duplicate exists, append a suffix (e.g., `Workflow Name (2)`) or ask the user.
3. **Confirm n8n version compatibility** — note the instance version from the audit. Some nodes require minimum versions.

If any check fails, stop and report before proceeding.

## Import Path 1: Official Template

Use this path when the workflow comes from the n8n template library (has a numeric template ID).

```
Step 1: ~~template_get(templateId, detail_level="full")
        → Retrieve the full template JSON with node definitions

Step 2: ~~workflow_validate(workflow_json)
        → Check for structural errors, missing node types, invalid connections
        → If validation fails → see Error Handling below

Step 3: ~~template_deploy(templateId)
        → Deploys with auto-fix enabled
        → Automatically strips credentials (they are NOT transferred)
        → Returns the new workflow ID
```

**Auto-fix options** available through `~~template_deploy`:
- Fixes missing connection references
- Resolves deprecated node type names
- Strips credential data (credentials must be reconfigured manually)
- Adjusts node positions for readability

## Import Path 2: Community JSON

Use this path for workflows from GitHub, n8n community forums, blog posts, or any raw JSON source.

```
Step 1: Fetch the raw JSON
        → If URL provided: download the JSON file directly
        → If file provided: read from local path
        → Verify it is valid JSON with a "nodes" array and "connections" object

Step 2: ~~workflow_validate(workflow_json)
        → Check structure, node types, connections
        → If validation fails → see Error Handling below

Step 3: ~~workflow_create(workflow_json)
        → Creates the workflow on the instance
        → Set active: false (always import as inactive)
        → Returns the new workflow ID
```

## Credential Reconfiguration

Credentials are NEVER transferred during import — this is by design for security.

After importing, guide the user through credential setup:

| Step | Action |
|------|--------|
| 1 | Open the imported workflow in the n8n editor |
| 2 | Identify nodes with missing credentials (shown with warning icons) |
| 3 | For each node, select or create the appropriate credential |
| 4 | Use `~~credential_manage` to list existing credentials that may already match |
| 5 | Test each credential connection before activating the workflow |

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
3. Check all connections are intact
4. Review any auto-fix changes applied during deploy
```

## Activation Safety Protocol

Follow this sequence strictly:

1. **Import as inactive** — never activate on import
2. **Configure credentials** — link all required credentials
3. **Review trigger nodes** — check webhook URLs, cron schedules, polling intervals
4. **Test manually** — use n8n's "Test Workflow" button with sample data
5. **Activate** — only after successful manual test

> WARNING: Activating a workflow with webhook triggers immediately exposes those endpoints. Verify webhook paths do not conflict with existing workflows.

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Validation failure: unknown node type | Community node not installed | Install the required community node package first |
| Validation failure: invalid connections | Node IDs reference non-existent nodes | Re-map connections or remove broken references |
| Deploy timeout | Instance overloaded or unreachable | Retry after confirming instance health via `~~instance_audit` |
| Duplicate workflow name | Name already exists on instance | Rename the workflow before import or append a numeric suffix |
| Missing community nodes | Workflow uses nodes not in the base install | List missing nodes, install them, then retry import |
| JSON parse error | Malformed source file | Validate the JSON structure before attempting import |

## Decision Tree

```
Is the source an official n8n template ID?
├─ YES → Path 1: ~~template_get → ~~workflow_validate → ~~template_deploy
└─ NO
   ├─ Is it a raw JSON file or URL?
   │  └─ YES → Path 2: fetch JSON → ~~workflow_validate → ~~workflow_create
   └─ Is it a community forum/blog link?
      └─ YES → Extract JSON from page → Path 2
```
