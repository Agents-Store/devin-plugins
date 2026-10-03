# Scenario: Provision a New n8n Instance

Complete walkthrough for setting up a fresh n8n instance with 10 foundational workflows covering communication, monitoring, CRM, and ops automation.

## Prerequisites

- n8n instance running and accessible via API
- n8n API key (Settings > n8n API) of a user who can create workflows. Listing credentials needs an Owner or Admin user; publishing needs the `workflow:activate` scope and the `workflow:publish` permission
- MCP server configured with instance URL and API key
- Credentials ready: Slack OAuth, Gmail/SMTP, GitHub PAT, Google Calendar OAuth

## Step 1: Check Instance Readiness

Verify the instance is healthy and empty before provisioning.

```
~~instance_health
```

Expected result:
- `status` is `healthy`, the API key is accepted
- Response time is reasonable (`performance.responseTimeMs`)
- n8n 2.x capabilities: n8n no longer reports its version to API clients, so probe what the key can do (`GET /api/v1/discover`) instead of comparing version numbers

```
~~workflow_list
```

Expected: empty or near-empty list. If workflows exist, note them to avoid naming conflicts.

```
~~credential_manage (action: list)
```

Expected: check what credentials already exist. We'll reuse any that match our needs.

**Decision point:** If the instance has issues, fix them before proceeding. See the `troubleshoot` skill.

## Step 2: Plan Credentials

Based on the Startup Essentials suite (see `BATCH_STRATEGIES.md`), we need these credential groups:

| Credential | Type | Needed By |
|-----------|------|-----------|
| Slack | OAuth2 | Notification hub, calendar alerts, PR notifications, error alerting, standup summary |
| Gmail / SMTP | OAuth2 or App Password | Email forwarding, onboarding sequence, invoice generation |
| CRM (HubSpot) | API Key | Contact sync, onboarding sequence |
| GitHub | Personal Access Token | PR notifications |
| Google Calendar | OAuth2 | Calendar automation |
| AWS S3 | Access Key | Backup automation |

**Action:** Confirm with the user which services they use. Adjust the suite if they use different providers (e.g., Outlook instead of Gmail, GitLab instead of GitHub).

## Step 3: Search for Templates — Phase 1 (No Dependencies)

Search for the 5 workflows that have no dependencies on other workflows.

### 3a: Slack Notification Hub

```
~~template_search("slack notification hub webhook channel routing")
```

Review top 3 results. Look for:
- Webhook trigger → Slack message node pattern
- Support for multiple channels
- totalViews > 5,000

Pick the best match. Note the template ID.

```
~~template_get(templateId={best_match_id}, mode="full")
```

Verify: nodes are all built-in, credential type is `slackOAuth2Api`. If `get_template` answers `Template <id> not found`, fetch the template from `api.n8n.io` (see `template-discovery`); the same applies to every `~~template_get` below.

### 3b: Email Forwarding/Routing

```
~~template_search("email forwarding filter routing gmail")
```

Look for: IMAP/Gmail trigger → filter/switch → send email pattern.

### 3c: CRM Contact Sync

```
~~template_search("CRM sync contacts hubspot webhook")
```

Look for: webhook or schedule trigger → API call → CRM update pattern.

### 3d: Error Alerting

```
~~template_search("error monitoring alert notification slack webhook")
```

Look for: webhook trigger (receives error events) → format message → Slack notification.

### 3e: Backup Automation

```
~~template_search("database backup schedule S3 cloud storage")
```

Look for: schedule trigger → database export or HTTP call → upload to S3/storage. Skip templates built on the Execute Command node — n8n 2.x disables it by default.

## Step 4: Analyze Top Results

For each of the 5 selected templates, fetch full details:

```
~~template_get(templateId={slack_hub_id}, mode="full")
~~template_get(templateId={email_forward_id}, mode="full")
~~template_get(templateId={crm_sync_id}, mode="full")
~~template_get(templateId={error_alert_id}, mode="full")
~~template_get(templateId={backup_id}, mode="full")
```

For each, check:
- [ ] All node types are available (no community nodes requiring installation)
- [ ] Credential types match what we planned
- [ ] No deprecated nodes (check `typeVersion`)
- [ ] Workflow complexity is manageable (< 20 nodes)
- [ ] Description is clear about what it does

**If a template is unsuitable:** Search again with modified keywords, or check community sources.

## Step 5: Batch Deploy Phase 1

Deploy all 5 Phase 1 workflows, then add the batch tag to each.

```
~~template_deploy(templateId={slack_hub_id}, name="Slack Notification Hub")
~~template_deploy(templateId={email_forward_id}, name="Email Forwarding")
~~template_deploy(templateId={crm_sync_id}, name="CRM Contact Sync")
~~template_deploy(templateId={error_alert_id}, name="Error Alerting")
~~template_deploy(templateId={backup_id}, name="Backup Automation")
```

Each call returns a `workflowId`. The deploy tools take no tags, so tag every new workflow with the batch tag:

```
~~workflow_update(id={workflowId}, operations: [{type: "addTag", tag: "suite-startup-essentials-2026-10-05"}])
```

A template that was only found on `api.n8n.io` is created with `~~workflow_create` (name, nodes, connections, settings) instead of `~~template_deploy`; the tag step is the same.

All workflows are imported as **unpublished drafts**.

## Step 6: Verify Phase 1

```
~~workflow_list
```

Confirm all 5 workflows appear. Check:
- Names are correct
- Status is unpublished
- Tags are applied

## Step 7: Search and Deploy Phase 2

Now search for workflows that depend on Phase 1 (Slack, Email).

### 7a: Calendar Automation (depends on Slack)

```
~~template_search("google calendar event notification slack reminder")
```

### 7b: GitHub PR Notifications (depends on Slack)

```
~~template_search("github pull request notification slack")
```

### 7c: Invoice Generation (depends on Email)

```
~~template_search("invoice generate PDF email send")
```

Analyze, then deploy and tag each result with `addTag` as in Step 5:

```
~~template_deploy(templateId={calendar_id}, name="Calendar Automation")
~~template_deploy(templateId={github_pr_id}, name="GitHub PR Notifications")
~~template_deploy(templateId={invoice_id}, name="Invoice Generation")
```

## Step 8: Search and Deploy Phase 3

### 8a: Customer Onboarding Sequence (depends on Email + CRM)

```
~~template_search("customer onboarding email sequence drip campaign")
```

### 8b: Daily Standup Summary (depends on Slack)

```
~~template_search("daily standup summary slack schedule automated")
```

Analyze, then deploy and tag each result as in Step 5:

```
~~template_deploy(templateId={onboarding_id}, name="Customer Onboarding Sequence")
~~template_deploy(templateId={standup_id}, name="Daily Standup Summary")
```

## Step 9: Configure Credentials

Now set up credentials and map them to workflows. This is best done in the n8n UI.

### Slack OAuth (used by 5 workflows)

1. In n8n: Settings > Credentials > New > Slack OAuth2 API
2. Follow OAuth flow to authorize
3. Edit each Slack workflow → select this credential for all Slack nodes

### Gmail/SMTP (used by 3 workflows)

1. New credential: Gmail OAuth2 API (or SMTP if preferred)
2. Authorize
3. Map to: Email Forwarding, Customer Onboarding, Invoice Generation

### HubSpot API (used by 2 workflows)

1. New credential: HubSpot API
2. Enter API key
3. Map to: CRM Contact Sync, Customer Onboarding

### GitHub PAT (used by 1 workflow)

1. New credential: GitHub API
2. Enter Personal Access Token
3. Map to: GitHub PR Notifications

### Google Calendar OAuth (used by 1 workflow)

1. New credential: Google Calendar OAuth2 API
2. Authorize
3. Map to: Calendar Automation

### AWS S3 (used by 1 workflow)

1. New credential: AWS API
2. Enter Access Key + Secret Key
3. Map to: Backup Automation

## Step 10: Publish Progressively

In n8n 2.x a workflow is **published** (it was "activated" in 1.x). Publish workflows one at a time, testing each, and only with the user's go-ahead:

```
Publish order (lowest risk first):
1. Backup Automation → trigger manually, verify backup created
2. Error Alerting → send test webhook, verify Slack message
3. Slack Notification Hub → send test webhook, verify routing
4. Email Forwarding → send test email, verify forwarding
5. CRM Contact Sync → create test contact, verify sync
6. GitHub PR Notifications → create test PR, verify notification
7. Calendar Automation → create test event, verify reminder
8. Invoice Generation → trigger with test data, verify PDF
9. Customer Onboarding → trigger with test contact, verify sequence
10. Daily Standup Summary → wait for scheduled trigger, verify summary
```

For each workflow:
1. Open in n8n UI
2. Click "Execute Workflow" for manual test
3. Check execution output — all nodes should show green checkmarks
4. If errors: check credential mapping and node configuration
5. Once test passes: publish the workflow (Publish button, `~~workflow_publish`, or `publish_workflow` in the native MCP)

## Final State

After completing all steps:
- 10 workflows deployed and published
- 6 credential sets configured
- All workflows tagged with `suite-startup-essentials-2026-10-05`
- Instance is fully provisioned for basic startup automation

## Rollback

If something goes wrong and you need to undo:

```
~~workflow_list → filter by tag "suite-startup-essentials-2026-10-05"
```

Unpublish all tagged workflows first (`unpublish_workflow` in the native MCP, or the `deactivateWorkflow` operation of `n8n_update_partial_workflow`), then archive or delete them only on explicit confirmation. Credentials can remain — they don't cause harm when unused.
