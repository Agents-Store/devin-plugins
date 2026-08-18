# Scenario: Automation Suite Deployment

Walkthrough: Deploy a coordinated "Slack + GitHub DevOps" suite of 5 related workflows that share credentials and work together to provide full development team visibility.

## User Request

> "Set up our n8n instance with a complete Slack + GitHub DevOps monitoring suite — PR notifications, issue tracking, deployment alerts, error reporting, and an automated standup bot."

## Target Suite: 5 Workflows

| # | Workflow | Trigger | Slack Channel | GitHub Scope |
|---|----------|---------|---------------|-------------|
| 1 | PR Notifications | GitHub webhook (PR events) | #pull-requests | All repos |
| 2 | Issue Tracker | GitHub webhook (issue events) | #issues | All repos |
| 3 | Deployment Alerts | GitHub webhook (deployment events) | #deployments | Production repos |
| 4 | Error Reporting | Webhook (error service callback) | #errors | N/A |
| 5 | Standup Bot | Schedule (daily 9am) | #standup | All repos |

## Step 1: Pre-flight Checks

### Check instance health

```
~~instance_audit
```

Verify: instance is reachable, n8n version is current, no health issues.

### List existing workflows

```
~~workflow_list
```

Check for:
- Existing workflows with similar names (avoid conflicts)
- Existing GitHub or Slack workflows (we may want to enhance rather than duplicate)

### Check existing credentials

```
~~credential_manage (action: list)
```

Look for:
- Existing Slack OAuth credential → reuse if available
- Existing GitHub credential → reuse if available

**If credentials exist:** Note their IDs for mapping to new workflows. No need to create duplicates.

## Step 2: Identify Shared Credentials

This suite needs only 2 credential types shared across all 5 workflows:

| Credential | Type | Used By | Notes |
|-----------|------|---------|-------|
| Slack OAuth2 | OAuth2 | All 5 workflows | Single app with access to all target channels |
| GitHub PAT | Personal Access Token | #1, #2, #3, #5 | Needs `repo` and `read:org` scopes |

**Key insight:** By identifying shared credentials upfront, we configure them once and reuse across all workflows. This is a major advantage of suite deployment over individual imports.

## Step 3: Search for Templates

Search for all 5 workflows. For each, we want the best match from the official library.

### 3a: PR Notifications

```
~~template_search("github pull request notification slack review approved merged")
```

**Selection criteria:**
- Webhook trigger (not polling) for real-time
- Handles multiple PR events: opened, approved, merged, closed
- Rich Slack message formatting (author, title, URL, status)
- totalViews > 5,000

Pick the best match. Note template ID.

### 3b: Issue Tracker

```
~~template_search("github issue tracker notification slack new assigned")
```

**Selection criteria:**
- Webhook trigger for real-time
- Handles: issue opened, assigned, labeled, closed
- Includes issue metadata in Slack message
- Supports label-based routing (bug vs feature vs question)

### 3c: Deployment Alerts

```
~~template_search("github deployment status notification slack CI CD")
```

**Selection criteria:**
- Webhook trigger on deployment status events
- Shows: environment (staging/production), status (success/failure), commit info
- Color-coded messages (green for success, red for failure)

**Note:** If no good official template exists, search community sources:

```
~~search("github deployment alert slack n8n workflow site:github.com")
```

### 3d: Error Reporting

```
~~template_search("error alert notification slack webhook incoming")
```

**Selection criteria:**
- Generic webhook trigger (receives error events from any error tracking service)
- Formats error details: message, stack trace, frequency
- Supports deduplication or throttling to avoid notification spam

### 3e: Standup Bot

```
~~template_search("daily standup summary slack github schedule automated")
```

**Selection criteria:**
- Schedule trigger (cron: daily at a specific time)
- Queries GitHub for: PRs merged yesterday, issues created, commits
- Compiles a summary message
- Posts to a Slack channel

## Step 4: Analyze All 5 Templates

Fetch full details for all selected templates:

```
~~template_get(id={pr_notifications_id})
~~template_get(id={issue_tracker_id})
~~template_get(id={deploy_alerts_id})
~~template_get(id={error_reporting_id})
~~template_get(id={standup_bot_id})
```

### Compatibility check for each

| Check | What to Verify |
|-------|---------------|
| Node types | All nodes are built-in (no community nodes unless explicitly accepted) |
| typeVersion | Current versions — no deprecated node versions |
| Credential types | Only `slackOAuth2Api` and `githubApi` (matching our plan) |
| Webhook paths | No collisions between the 3 webhook-triggered workflows |
| Slack channel references | Configurable (not hardcoded to a specific channel) |

### Webhook path planning

Three workflows use webhooks. Ensure unique paths:

```
Workflow 1 (PR):         /webhook/github-pr-events
Workflow 2 (Issues):     /webhook/github-issue-events
Workflow 3 (Deploys):    /webhook/github-deploy-events
Workflow 4 (Errors):     /webhook/error-reporting
```

If templates use default webhook paths, we'll need to modify them after import to avoid collisions.

## Step 5: Plan Batch Import Order

These workflows have minimal interdependencies, but we follow a logical order:

```
Phase 1 — Foundation (no dependencies):
  1. Error Reporting (standalone, no GitHub dependency)
  2. PR Notifications (standalone)
  3. Issue Tracker (standalone)
  4. Deployment Alerts (standalone)

Phase 2 — Aggregator (depends on GitHub data):
  5. Standup Bot (queries GitHub activity from previous day)
```

The standup bot is last because it aggregates data that the other workflows help create visibility into.

## Step 6: Batch Deploy

Deploy all 5 workflows with a consistent batch tag.

```
~~template_deploy(id={error_reporting_id}, name="DevOps: Error Reporting", tags=["suite-devops-slack-github-2026-04-07"])
~~template_deploy(id={pr_notifications_id}, name="DevOps: PR Notifications", tags=["suite-devops-slack-github-2026-04-07"])
~~template_deploy(id={issue_tracker_id}, name="DevOps: Issue Tracker", tags=["suite-devops-slack-github-2026-04-07"])
~~template_deploy(id={deploy_alerts_id}, name="DevOps: Deployment Alerts", tags=["suite-devops-slack-github-2026-04-07"])
~~template_deploy(id={standup_bot_id}, name="DevOps: Daily Standup Bot", tags=["suite-devops-slack-github-2026-04-07"])
```

**If any template was sourced from community (not official library):**

```
~~workflow_validate({community_json})
~~workflow_create({name: "DevOps: ...", workflow_json: {...}, tags: [...]})
```

All workflows are created in **inactive** state.

## Step 7: Verify Batch Deployment

```
~~workflow_list
```

**Expected:** 5 new workflows with "DevOps:" prefix:

| Workflow | Status | Tags |
|----------|--------|------|
| DevOps: Error Reporting | inactive | suite-devops-slack-github-2026-04-07 |
| DevOps: PR Notifications | inactive | suite-devops-slack-github-2026-04-07 |
| DevOps: Issue Tracker | inactive | suite-devops-slack-github-2026-04-07 |
| DevOps: Deployment Alerts | inactive | suite-devops-slack-github-2026-04-07 |
| DevOps: Daily Standup Bot | inactive | suite-devops-slack-github-2026-04-07 |

**Check webhook paths:** Ensure no two workflows claim the same webhook URL.

## Step 8: Configure Shared Credentials

### Slack OAuth2 (shared by all 5 workflows)

1. **Create credential** (if not reusing an existing one):
   - n8n Credentials > New > Slack OAuth2 API
   - Create a Slack App at api.slack.com/apps
   - Required scopes: `chat:write`, `channels:read`, `channels:join`
   - Install to workspace, complete OAuth flow in n8n

2. **Map to all workflows:**
   - Open each of the 5 workflows
   - Select the Slack OAuth2 credential for every Slack node
   - This is the same credential across all 5 — set once, reference by name

### GitHub Personal Access Token (shared by 4 workflows)

1. **Create credential** (if not reusing):
   - n8n Credentials > New > GitHub API
   - Generate PAT at github.com/settings/tokens
   - Required scopes: `repo`, `read:org`
   - Enter token in n8n

2. **Map to workflows:**
   - Open workflows #1, #2, #3, #5
   - Select the GitHub credential for all GitHub nodes

## Step 9: Configure GitHub Webhooks

For the 3 webhook-triggered workflows, set up GitHub organization webhooks:

### Organization-level webhook (recommended)

One webhook can serve all 3 workflows by routing events:

1. Go to GitHub Organization Settings > Webhooks > Add webhook
2. **Payload URL:** Your n8n instance webhook URL
3. **Content type:** application/json
4. **Events to subscribe:**
   - Pull requests (for PR Notifications)
   - Issues (for Issue Tracker)
   - Deployment statuses (for Deployment Alerts)

**But wait — we have 3 different webhook URLs.** Two options:

**Option A: One GitHub webhook per workflow**
- Create 3 separate webhooks, each pointing to the specific workflow's webhook URL
- Each subscribes only to relevant events
- Cleaner separation, easier to debug

**Option B: Single webhook with routing**
- Create 1 GitHub webhook pointing to a router workflow
- The router workflow inspects the event type and forwards to the correct workflow
- More complex but fewer GitHub webhooks to manage

**Recommendation:** Option A (3 separate webhooks) for simplicity.

### Workflow-specific webhook setup

| Workflow | GitHub Webhook URL | Events |
|----------|-------------------|--------|
| PR Notifications | `https://n8n.example.com/webhook/github-pr-events` | Pull requests |
| Issue Tracker | `https://n8n.example.com/webhook/github-issue-events` | Issues |
| Deployment Alerts | `https://n8n.example.com/webhook/github-deploy-events` | Deployment statuses |

## Step 10: Configure Slack Channels

Each workflow posts to a specific Slack channel. Configure in each workflow:

| Workflow | Channel | Channel ID |
|----------|---------|-----------|
| PR Notifications | #pull-requests | Look up in Slack |
| Issue Tracker | #issues | Look up in Slack |
| Deployment Alerts | #deployments | Look up in Slack |
| Error Reporting | #errors | Look up in Slack |
| Standup Bot | #standup | Look up in Slack |

**Create channels first** if they don't exist. Then update each workflow's Slack node with the correct channel ID.

## Step 11: Activate One-by-One with Testing

Activate in order of simplicity and risk:

### 11a: Error Reporting (simplest — generic webhook)

1. Activate the workflow
2. Send a test webhook:
   ```
   curl -X POST https://n8n.example.com/webhook/error-reporting \
     -H "Content-Type: application/json" \
     -d '{"error": "Test error", "service": "api", "severity": "warning"}'
   ```
3. Verify message appears in #errors channel
4. Check message formatting is correct

### 11b: PR Notifications

1. Activate the workflow
2. Create a test PR in a repository (or use an existing one)
3. Verify notification appears in #pull-requests
4. Test: approve the PR, verify updated notification
5. Test: merge the PR, verify merge notification

### 11c: Issue Tracker

1. Activate the workflow
2. Create a test issue in a repository
3. Verify notification appears in #issues
4. Test: assign the issue, verify update
5. Close the test issue

### 11d: Deployment Alerts

1. Activate the workflow
2. Trigger a deployment (or create a test deployment via GitHub API)
3. Verify alert appears in #deployments
4. Check both success and failure formatting if possible

### 11e: Standup Bot (last — schedule-based)

1. Activate the workflow
2. Execute manually first to verify output
3. Check that the summary accurately reflects yesterday's GitHub activity
4. Verify it posts to #standup
5. Let it run on schedule the next morning to confirm cron works

## Final State

```
Suite: Slack + GitHub DevOps (5 workflows)
Tag: suite-devops-slack-github-2026-04-07

Credentials:
  - Slack OAuth2 → shared by all 5 workflows
  - GitHub PAT → shared by 4 workflows

GitHub Webhooks:
  - 3 org-level webhooks → PR, Issues, Deployments

Slack Channels:
  - #pull-requests, #issues, #deployments, #errors, #standup

Status: All 5 workflows active and tested
```

## Maintenance Notes

- **Standup bot schedule:** Adjust cron if the team's standup time changes
- **New repos:** If new repositories are added to the org, the org-level webhooks automatically cover them
- **Channel changes:** If Slack channels are renamed, update channel IDs in the workflows
- **Credential rotation:** When GitHub PAT expires, update the single credential — all 4 workflows inherit the change
- **Rollback:** Deactivate all workflows by tag, remove GitHub webhooks
