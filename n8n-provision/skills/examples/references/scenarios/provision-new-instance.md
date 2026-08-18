# Scenario: Provision a New n8n Instance

Complete walkthrough for setting up a fresh n8n instance with 10 foundational workflows covering communication, monitoring, CRM, and ops automation.

## Prerequisites

- n8n instance running and accessible via API
- API key with Owner-level permissions
- MCP server configured with instance URL and API key
- Credentials ready: Slack OAuth, Gmail/SMTP, GitHub PAT, Google Calendar OAuth

## Step 1: Check Instance Readiness

Verify the instance is healthy and empty before provisioning.

```
~~instance_audit
```

Expected result:
- Instance is reachable
- n8n version is current (1.x+)
- No critical health issues

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
~~template_get(id={best_match_id})
```

Verify: nodes are all built-in, credential type is `slackOAuth2Api`.

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

Look for: schedule trigger → execute command/HTTP → upload to S3/storage.

## Step 4: Analyze Top Results

For each of the 5 selected templates, fetch full details:

```
~~template_get(id={slack_hub_id})
~~template_get(id={email_forward_id})
~~template_get(id={crm_sync_id})
~~template_get(id={error_alert_id})
~~template_get(id={backup_id})
```

For each, check:
- [ ] All node types are available (no community nodes requiring installation)
- [ ] Credential types match what we planned
- [ ] No deprecated nodes (check `typeVersion`)
- [ ] Workflow complexity is manageable (< 20 nodes)
- [ ] Description is clear about what it does

**If a template is unsuitable:** Search again with modified keywords, or check community sources.

## Step 5: Batch Deploy Phase 1

Deploy all 5 Phase 1 workflows with a batch tag.

```
~~template_deploy(id={slack_hub_id}, name="Slack Notification Hub", tags=["suite-startup-essentials-2026-04-07"])
~~template_deploy(id={email_forward_id}, name="Email Forwarding", tags=["suite-startup-essentials-2026-04-07"])
~~template_deploy(id={crm_sync_id}, name="CRM Contact Sync", tags=["suite-startup-essentials-2026-04-07"])
~~template_deploy(id={error_alert_id}, name="Error Alerting", tags=["suite-startup-essentials-2026-04-07"])
~~template_deploy(id={backup_id}, name="Backup Automation", tags=["suite-startup-essentials-2026-04-07"])
```

All workflows are imported in **inactive** state.

## Step 6: Verify Phase 1

```
~~workflow_list
```

Confirm all 5 workflows appear. Check:
- Names are correct
- Status is inactive
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

Analyze, then deploy:

```
~~template_deploy(id={calendar_id}, name="Calendar Automation", tags=["suite-startup-essentials-2026-04-07"])
~~template_deploy(id={github_pr_id}, name="GitHub PR Notifications", tags=["suite-startup-essentials-2026-04-07"])
~~template_deploy(id={invoice_id}, name="Invoice Generation", tags=["suite-startup-essentials-2026-04-07"])
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

Analyze, then deploy:

```
~~template_deploy(id={onboarding_id}, name="Customer Onboarding Sequence", tags=["suite-startup-essentials-2026-04-07"])
~~template_deploy(id={standup_id}, name="Daily Standup Summary", tags=["suite-startup-essentials-2026-04-07"])
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

## Step 10: Activate Progressively

Activate workflows one at a time, testing each:

```
Activation order (lowest risk first):
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
5. Once test passes: activate the workflow

## Final State

After completing all steps:
- 10 workflows deployed and active
- 6 credential sets configured
- All workflows tagged with `suite-startup-essentials-2026-04-07`
- Instance is fully provisioned for basic startup automation

## Rollback

If something goes wrong and you need to undo:

```
~~workflow_list → filter by tag "suite-startup-essentials-2026-04-07"
```

Deactivate all tagged workflows first, then delete if needed. Credentials can remain — they don't cause harm when unused.
