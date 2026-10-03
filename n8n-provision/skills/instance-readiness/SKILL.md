---
name: instance-readiness
description: |
  Assess n8n instance readiness before provisioning. Runs health checks, inventories workflows and credentials, detects conflicts, verifies community nodes, and produces a readiness report with pass/warn/fail ratings.
  Use when: "check n8n instance", "is n8n ready for provisioning", "n8n health check", "verify n8n instance", "pre-provisioning check", "audit n8n before import", "instance readiness report"
---

# Instance Readiness

Assess whether an n8n instance is ready to receive new workflows. Produces a structured readiness report with pass/warn/fail ratings for each check category. All calls use `~~capability` with automatic fallback (see CONNECTORS.md).

**Health is not security.** `~~instance_health` (`n8n_health_check`) answers "is the instance alive and is the API key accepted". `~~instance_audit` (`n8n_audit_instance`) is a **security audit** and belongs to Step 7. Do not use the audit as a health check.

## Readiness Assessment Overview

Run the full assessment in this order:

```
1. Health Check         → Is the instance alive, responsive, and what can the key do?
2. Workflow Inventory   → What already exists? Any conflicts?
3. Credential Inventory → What credentials are configured?
4. Community Nodes      → Are required community nodes installed?
5. Webhook Conflicts    → Any duplicate webhook paths?
6. Resource Capacity    → Can the instance handle more workflows?
7. Security Posture     → Is the instance properly secured?
```

## Step 1: Health Check

```
~~instance_health
```

`n8n_health_check` returns `status` (`healthy` / `degraded` / `error`), `instanceId`, `features`, `mcpVersion` and `performance.responseTimeMs`. Use `mode: "diagnostic"` when it fails. Extract and evaluate:

| Metric | Source | Pass | Warn | Fail |
|--------|--------|------|------|------|
| Instance reachable | `status`, `performance.responseTimeMs` | `healthy`, responds < 5s | `degraded`, or 5-15s | `error` / no response / timeout |
| API key accepted | The call itself succeeds | Works | — | 401 (expired or wrong key) |
| Features | `features` | Features the plan needs are on | — | A needed feature is off |

**There is no version, uptime, queue or database field.** n8n stopped reporting its version to API clients in 1.119.0, so `n8nVersion` is normally absent (a `n8nVersionNote` says so) — that is neither an error nor worth a retry. Check **capabilities** instead of comparing versions:

| Question | How to find out |
|----------|-----------------|
| What can this API key do? | `GET /api/v1/discover` lists the surface and scopes the key can use; or try the call and read the `403`. Scopes exist only on Enterprise; elsewhere a key has the full rights of its user |
| Can it publish? | Needs the `workflow:activate` scope and the `workflow:publish` permission (`PUBLISH_FORBIDDEN` otherwise, n8n 2.39+) |
| Is the instance current? | When the owner knows the version: compare with the `stable` dist-tag (`npm view n8n dist-tags`). `latest` is the same as `stable` |
| Uptime, queue, memory | `/healthz` always; `/metrics` only when the instance sets `N8N_METRICS=true` |

## Step 2: Workflow Inventory

```
~~workflow_list
```

Analyze the results:

| Metric | Pass | Warn | Fail |
|--------|------|------|------|
| Total workflow count | < 50 | 50-100 | > 100 (performance risk) |
| Published workflows (`active`) | < 30 | 30-60 | > 60 |
| Unpublished (draft) workflows | Any count (no risk) | — | — |

**Conflict detection:** Compare each planned import name against existing workflows. Exact match = CONFLICT (must rename or skip). Partial match = WARNING (review for duplication). No match = CLEAR.

## Step 3: Credential Inventory

Call `~~credential_manage` (action: list) to map existing credentials by name, type, and usage count. Compare against planned imports to identify reusable vs missing credentials. See `credential-planning` skill for full credential analysis.

## Step 4: Community Node Verification

Extract required node types from planned workflow JSONs (filter to non-core nodes — those NOT starting with `n8n-nodes-base.` or `@n8n/n8n-nodes-langchain.`). Compare against the installed community packages: `GET /api/v1/community-packages` (needs the `communityPackage:*` scopes), or Settings > Community Nodes in the editor. Produce a gap report listing each required package with installed/missing status. **FAIL** if any required community node is missing.

Ways to install a missing package (Owner or Admin):

| Way | Notes |
|-----|-------|
| Settings > Community Nodes > Install | Easiest; verified packages only unless unverified packages are enabled |
| `POST /api/v1/community-packages` with `{name, version}` | Scope `communityPackage:install` |
| Environment: `N8N_COMMUNITY_PACKAGES_MANAGED_BY_ENV=true` plus `N8N_COMMUNITY_PACKAGES` (n8n 2.21+) | **Removes every package not on the list.** Check the full list with the owner before using it |
| Manual `npm i` inside the n8n nodes directory (`~/.n8n/nodes`), then restart | Required for queue mode and private packages |

From n8n 3.0 `N8N_UNVERIFIED_PACKAGES_ENABLED` defaults to `false`, so unverified packages need that variable set. Report the gap and the options; install only when the user agrees.

## Step 5: Webhook Conflict Detection

Extract webhook paths from planned imports (look for `n8n-nodes-base.webhook` nodes, read `node.parameters.path`). Compare against webhook paths in existing published workflows from `~~workflow_list`. Duplicate path = FAIL (two workflows cannot share a webhook path). Similar paths = WARN (review for intent).

## Step 6: Resource Capacity

Estimate whether the instance can handle additional workflows:

| Factor | Assessment Method | Threshold |
|--------|------------------|-----------|
| Published workflow count | Current published + planned to publish | Warn if total > 60 |
| Trigger density | Count trigger/webhook/schedule nodes | Warn if > 30 triggers total |
| Execution volume | Check recent execution history | Warn if > 1000 executions/day |
| Memory usage | `/metrics` (when `N8N_METRICS=true`) or the host's own monitoring | Warn if > 80% utilized |
| Storage | Database size trend | Warn if execution log growing rapidly |

## Step 7: Security Posture

```
~~instance_audit   # security audit, not a health check
```

`n8n_audit_instance` is the security audit. It combines n8n's built-in audit with a scan of the stored workflows and returns a markdown report with severity ratings and a remediation playbook.

| Check | Categories | Pass | Warn | Fail |
|-------|-----------|------|------|------|
| Built-in audit | `credentials`, `database`, `nodes`, `instance`, `filesystem` | No critical or high findings | Medium or low findings | Critical or high findings (for example a vulnerable community node, public registration) |
| Hardcoded secrets | custom scan `hardcoded_secrets` | None | — | Any secret in a workflow parameter |
| Webhooks | custom scan `unauthenticated_webhooks` | All webhooks authenticated | Some unauthenticated | Unauthenticated webhooks on workflows that write |
| Error handling | custom scan `error_handling` | Error workflow or error output set | Missing on some workflows | — |
| Data retention | custom scan `data_retention` | Pruning on | Manual pruning only | No pruning, data growth |

Use `categories` and `customChecks` to narrow the run on large instances (it fetches every workflow and can take 30 seconds). HTTPS in front of the instance is not part of the audit — ask the owner or look at the instance URL.

## Readiness Report Format

Produce the final report with these sections:

- **Header:** Instance URL, date, planned import count
- **Summary:** Overall rating — READY / READY WITH WARNINGS / NOT READY
- **Per-check sections:** Each step with key metrics and PASS/WARN/FAIL rating
- **Action Items:** Ordered by priority (CRITICAL first, then WARNING)
- **Conclusion:** How many critical items to resolve before provisioning

## Quick Check vs Full Assessment

| Mode | Steps Included | When to Use |
|------|---------------|-------------|
| **Quick** | Steps 1-2 only (health + workflow count) | Before a single workflow import |
| **Full** | All 7 steps | Before batch provisioning or first-time setup |
