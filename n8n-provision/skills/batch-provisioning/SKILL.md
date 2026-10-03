---
name: batch-provisioning
description: |
  Provision an n8n instance with multiple workflows in a single batch operation. Handles dependency ordering, credential grouping, progress tracking, rollback strategy, and post-flight verification.
  Use when: "provision n8n instance", "batch import workflows", "set up n8n with workflows", "deploy multiple templates", "bootstrap n8n", "install workflow suite", "bulk deploy workflows"
---

# Batch Provisioning

Deploy multiple workflows to an n8n instance in one coordinated operation. Handles dependency ordering, shared credentials, progress tracking, and rollback. All calls use `~~capability` with automatic fallback (see CONNECTORS.md).

## Pre-Flight Checks

Run all pre-flight checks before deploying anything:

```
1. ~~instance_health
   → Confirm the instance is reachable and the API key works (status, responseTimeMs)
   → STOP if instance is unhealthy or unreachable
   → The response has no version, uptime or queue fields — probe capabilities instead
     (see instance-readiness)

2. ~~workflow_list
   → Inventory all existing workflows
   → Record names and IDs for conflict detection

3. ~~credential_manage (action: list)
   → Inventory all existing credentials
   → Map credential types already available

4. Community nodes and Data Tables the plan needs
   → Missing community packages: see instance-readiness, Step 4 (they can be installed
     through the API or an environment variable, with warnings listed there)
   → A template that uses a Data Table needs the table to exist first: ~~datatable_manage
```

**Pre-flight pass/fail criteria:**

| Check | Pass | Fail |
|-------|------|------|
| Instance reachable | `~~instance_health` returns `healthy` | Timeout or error |
| Capabilities | The key can create (and, if publishing is planned, publish) and the node types of all planned workflows exist on the instance | `403`, unknown node type, `typeVersion` the instance rejects |
| Resource headroom | Workflow and trigger counts leave room for N more (see instance-readiness) | Counts near the limits, or `/healthz` / metrics show pressure |
| No name conflicts | No duplicate workflow names | Conflicts found — resolve before proceeding |

## Planning Phase

### Group by Credential Dependency

Organize workflows into groups that share credentials:

```
Group A: Slack credentials  → [Slack Alert, Slack Onboarding, Slack Digest]
Group B: Gmail credentials  → [Email Notifier, Daily Report Sender]
Group C: No credentials     → [Data Transform, Schedule Cleanup]
Group D: Multiple services  → [CRM Sync (Slack + HubSpot)]
```

### Determine Deployment Order

1. **No-credential workflows first** — deploy and verify independently
2. **Shared-credential groups next** — set up the credential once, then deploy all workflows using it
3. **Multi-credential workflows last** — these depend on credentials from earlier groups

### Assign Batch Identifier

Mark every workflow in the batch for tracking:

- **Naming convention:** `[Batch-001] Original Workflow Name`
- **Tagging:** Apply a shared tag (e.g., `batch-001`, `provisioned-2026-10`) after each deployment. Neither `n8n_deploy_template` nor `n8n_create_workflow` accepts tags: call `~~workflow_update` (`n8n_update_partial_workflow`) with operation `addTag`. Look up existing tags with `n8n_list_catalog({kind: "tags"})`
- **Folders and projects (optional):** a folder or project groups a batch better than tags alone. Create the folder with `n8n_manage_folders`, then place each workflow with `parentFolderId` on `n8n_create_workflow` or the `moveToFolder` operation (n8n 2.32+). Folders need n8n 2.19+ and a registered (free) Community licence plus `folder:*` scopes; placement is write-only, so verify it through the folder's counts, not by reading the workflow. `projectId` targets a project (Enterprise)
- Increment batch number if the instance has previous batches

## Execution

Deploy workflows one-by-one with validation between each:

```
FOR each workflow in ordered_plan:

  1. ~~workflow_validate(workflow_json)
     → If FAIL: log error, skip this workflow, continue to next
     → If PASS: proceed

  2. Deploy (the workflow is created unpublished):
     → Official template in the n8n-mcp database: ~~template_deploy(templateId, name)
     → Official template only on api.n8n.io ("not found" from get_template), or community JSON:
       ~~workflow_create(name, nodes, connections, settings)  (see single-workflow-import)
     → Apply batch tag (~~workflow_update, addTag) and naming convention
     → ~~workflow_autofix in preview mode; apply after review

  3. ~~workflow_list → confirm deployment
     → Verify node count matches source

  4. Log result:
     → SUCCESS: record workflow ID, name, node count
     → FAILURE: record error, mark as skipped

  5. Brief pause between deployments to avoid rate limiting
```

## Rollback Strategy

If a workflow fails mid-batch, do NOT undo successful deployments — they are unpublished drafts and harmless. Instead:

1. **Document the failure** — record which workflow failed and why
2. **List what was deployed** — provide the user a clear inventory of successful imports
3. **Provide fix instructions** — for each failure, describe what the user must resolve
4. Fix the issue and re-run only the failed items

To undo a whole batch the user asked to remove, list it by tag (`n8n_list_workflows({tags: ["<batch-tag>"]})`), show the list, and archive or delete only on explicit confirmation.

## Post-Flight Verification

After all deployments complete:

```
1. ~~workflow_list → verify all batch workflows present
   → Match expected count vs actual count

2. ~~instance_audit (security audit) as a post-flight check
   → Hardcoded secrets and unauthenticated webhooks in the new workflows
   → Findings are reported, not fixed — show them to the user

3. Generate credential setup checklist:
   → List every unique credential type needed
   → Note which credentials already exist on the instance
   → Mark which workflows need each credential

4. Summary report:
   → Total deployed / skipped / failed
   → Credential setup tasks remaining
   → Recommended publish order (workflows stay drafts until the user publishes them)
```

**Post-flight checklist template:**

| # | Workflow | Status | Credentials Needed | Notes |
|---|----------|--------|--------------------|-------|
| 1 | Data Transform | Deployed | None | Ready to publish |
| 2 | Slack Alert | Deployed | Slack OAuth2 | Configure credential |
| 3 | CRM Sync | Skipped | — | Missing community node |

## Preset Suites

Reference preset workflow suites from `references/BATCH_STRATEGIES.md`:

| Suite | Target Audience | Typical Workflows |
|-------|----------------|-------------------|
| **startup-essentials** | New teams | Slack notifications, email alerts, data backups, uptime monitoring |
| **devops** | Engineering teams | CI/CD notifications, error alerting, deployment tracking, log aggregation |
| **marketing-automation** | Marketing teams | Lead capture, email sequences, social posting, analytics reports |

Each suite defines search queries per workflow category (not template IDs), with dependency ordering pre-calculated. Run each query through `~~template_search` (n8n-mcp, then `api.n8n.io`) and pick the best match; the library changes, so IDs would go stale.

## Dry-Run Mode

Analyze and plan without deploying. Parse all sources, run `~~workflow_validate` on each, identify credential requirements, check name conflicts via `~~workflow_list`, and detect missing community nodes. Output a deployment plan document with no changes to the instance. Use dry-run to preview the batch before committing.
