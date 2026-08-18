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
1. ~~instance_audit
   → Confirm instance is healthy, note version and resource usage
   → STOP if instance is unhealthy or unreachable

2. ~~workflow_list
   → Inventory all existing workflows
   → Record names and IDs for conflict detection

3. ~~credential_manage (action: list)
   → Inventory all existing credentials
   → Map credential types already available
```

**Pre-flight pass/fail criteria:**

| Check | Pass | Fail |
|-------|------|------|
| Instance reachable | Responds to audit | Timeout or error |
| Version compatible | Meets minimum version for all planned workflows | Version too old for required nodes |
| Resource headroom | Can handle N additional workflows | Memory or execution limits near capacity |
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

Tag every workflow in the batch for tracking:

- **Naming convention:** `[Batch-001] Original Workflow Name`
- **Tagging:** Apply a shared tag (e.g., `batch-001`, `provisioned-2026-04`)
- Increment batch number if the instance has previous batches

## Execution

Deploy workflows one-by-one with validation between each:

```
FOR each workflow in ordered_plan:

  1. ~~workflow_validate(workflow_json)
     → If FAIL: log error, skip this workflow, continue to next
     → If PASS: proceed

  2. Deploy:
     → Official template: ~~template_deploy(templateId)
     → Community JSON: ~~workflow_create(workflow_json)
     → Set active: false
     → Apply batch tag and naming convention

  3. ~~workflow_list → confirm deployment
     → Verify node count matches source

  4. Log result:
     → SUCCESS: record workflow ID, name, node count
     → FAILURE: record error, mark as skipped

  5. Brief pause between deployments to avoid rate limiting
```

## Rollback Strategy

If a workflow fails mid-batch, do NOT undo successful deployments — they are inactive and harmless. Instead:

1. **Document the failure** — record which workflow failed and why
2. **List what was deployed** — provide the user a clear inventory of successful imports
3. **Provide fix instructions** — for each failure, describe what the user must resolve
4. Fix the issue and re-run only the failed items

## Post-Flight Verification

After all deployments complete:

```
1. ~~workflow_list → verify all batch workflows present
   → Match expected count vs actual count

2. Generate credential setup checklist:
   → List every unique credential type needed
   → Note which credentials already exist on the instance
   → Mark which workflows need each credential

3. Summary report:
   → Total deployed / skipped / failed
   → Credential setup tasks remaining
   → Recommended activation order
```

**Post-flight checklist template:**

| # | Workflow | Status | Credentials Needed | Notes |
|---|----------|--------|--------------------|-------|
| 1 | Data Transform | Deployed | None | Ready to activate |
| 2 | Slack Alert | Deployed | Slack OAuth2 | Configure credential |
| 3 | CRM Sync | Skipped | — | Missing community node |

## Preset Suites

Reference preset workflow suites from `references/BATCH_STRATEGIES.md`:

| Suite | Target Audience | Typical Workflows |
|-------|----------------|-------------------|
| **startup-essentials** | New teams | Slack notifications, email alerts, data backups, uptime monitoring |
| **devops** | Engineering teams | CI/CD notifications, error alerting, deployment tracking, log aggregation |
| **marketing-automation** | Marketing teams | Lead capture, email sequences, social posting, analytics reports |
| **customer-support** | Support teams | Ticket routing, SLA monitoring, satisfaction surveys, escalation alerts |

Each suite defines a curated list of template IDs and community workflows with dependency ordering pre-calculated.

## Dry-Run Mode

Analyze and plan without deploying. Parse all sources, run `~~workflow_validate` on each, identify credential requirements, check name conflicts via `~~workflow_list`, and detect missing community nodes. Output a deployment plan document with no changes to the instance. Use dry-run to preview the batch before committing.
