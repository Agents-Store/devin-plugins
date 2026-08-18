---
name: instance-readiness
description: |
  Assess n8n instance readiness before provisioning. Runs health checks, inventories workflows and credentials, detects conflicts, verifies community nodes, and produces a readiness report with pass/warn/fail ratings.
  Use when: "check n8n instance", "is n8n ready for provisioning", "n8n health check", "verify n8n instance", "pre-provisioning check", "audit n8n before import", "instance readiness report"
---

# Instance Readiness

Assess whether an n8n instance is ready to receive new workflows. Produces a structured readiness report with pass/warn/fail ratings for each check category. All calls use `~~capability` with automatic fallback (see CONNECTORS.md).

## Readiness Assessment Overview

Run the full assessment in this order:

```
1. Health Check         → Is the instance alive and responsive?
2. Workflow Inventory   → What already exists? Any conflicts?
3. Credential Inventory → What credentials are configured?
4. Community Nodes      → Are required community nodes installed?
5. Webhook Conflicts    → Any duplicate webhook paths?
6. Resource Capacity    → Can the instance handle more workflows?
7. Security Posture     → Is the instance properly secured?
```

## Step 1: Health Check

```
~~instance_audit
```

Extract and evaluate:

| Metric | Source | Pass | Warn | Fail |
|--------|--------|------|------|------|
| Instance reachable | Audit response | Responds < 5s | Responds 5-15s | No response / timeout |
| n8n version | Audit `.version` | Latest stable or N-1 | N-2 or N-3 | More than 3 versions behind |
| Uptime | Audit `.uptime` | > 24 hours | 1-24 hours | < 1 hour (recent restart) |
| Queue health | Audit `.queue` | No backed-up executions | < 50 queued | > 50 queued |
| Database | Audit `.database` | Connected, responsive | Slow queries detected | Connection errors |

## Step 2: Workflow Inventory

```
~~workflow_list
```

Analyze the results:

| Metric | Pass | Warn | Fail |
|--------|------|------|------|
| Total workflow count | < 50 | 50-100 | > 100 (performance risk) |
| Active workflows | < 30 | 30-60 | > 60 |
| Inactive workflows | Any count (no risk) | — | — |

**Conflict detection:** Compare each planned import name against existing workflows. Exact match = CONFLICT (must rename or skip). Partial match = WARNING (review for duplication). No match = CLEAR.

## Step 3: Credential Inventory

Call `~~credential_manage` (action: list) to map existing credentials by name, type, and usage count. Compare against planned imports to identify reusable vs missing credentials. See `credential-planning` skill for full credential analysis.

## Step 4: Community Node Verification

Extract required node types from planned workflow JSONs (filter to non-core nodes — those NOT starting with `n8n-nodes-base.`). Compare against installed community nodes from `~~instance_audit` or n8n settings. Produce a gap report listing each required package with installed/missing status. **FAIL** if any required community node is missing.

## Step 5: Webhook Conflict Detection

Extract webhook paths from planned imports (look for `n8n-nodes-base.webhook` nodes, read `node.parameters.path`). Compare against webhook paths in existing active workflows from `~~workflow_list`. Duplicate path = FAIL (two workflows cannot share a webhook path). Similar paths = WARN (review for intent).

## Step 6: Resource Capacity

Estimate whether the instance can handle additional workflows:

| Factor | Assessment Method | Threshold |
|--------|------------------|-----------|
| Active workflow count | Current active + planned active | Warn if total > 60 |
| Trigger density | Count trigger/webhook/cron nodes | Warn if > 30 triggers total |
| Execution volume | Check recent execution history | Warn if > 1000 executions/day |
| Memory usage | Instance audit resource metrics | Warn if > 80% utilized |
| Storage | Database size trend | Warn if execution log growing rapidly |

## Step 7: Security Posture

| Check | Pass | Warn | Fail |
|-------|------|------|------|
| API key configured | Key is set and non-default | — | No API key or using default |
| HTTPS enabled | Instance served over HTTPS | HTTP with reverse proxy | Plain HTTP exposed |
| Authentication | Users require login | Single-user mode | No authentication |
| Environment variables | Secrets stored in env vars | Mixed (some hardcoded) | Secrets hardcoded in workflows |
| Execution data pruning | Auto-prune enabled | Manual pruning only | No pruning (data growth risk) |

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
