# Batch Provisioning Strategies

Preset provisioning suites for common use cases. Each suite defines a set of related workflows to deploy together, including search queries, import order, and shared credential requirements.

## How to Use These Suites

1. **Select a suite** matching the user's needs
2. **Search** for each workflow category using the suggested queries
3. **Analyze** top candidates for quality, node compatibility, and credential overlap
4. **Plan import order** — deploy dependency-free workflows first
5. **Batch deploy** with a shared tag for identification
6. **Configure credentials** — set up shared credentials once, map to all workflows
7. **Activate** one-by-one after verification

---

## Suite: Startup Essentials

**Target:** Early-stage teams needing core automation for communication, CRM, and ops.
**Workflows:** 10
**Shared credentials:** Slack OAuth, Gmail/SMTP, CRM API key, GitHub token, calendar API

### Workflow Categories

| # | Category | Search Query | Priority | Dependencies |
|---|----------|-------------|----------|--------------|
| 1 | Slack notification hub | `"slack notification webhook channel"` | High | None |
| 2 | Email forwarding/routing | `"email forwarding filter routing"` | High | None |
| 3 | CRM contact sync | `"CRM sync contacts hubspot salesforce"` | High | None |
| 4 | Calendar automation | `"google calendar event reminder notification"` | Medium | Slack (#1) |
| 5 | GitHub PR notifications | `"github pull request notification slack"` | Medium | Slack (#1) |
| 6 | Error alerting | `"error monitoring alert notification"` | High | Slack (#1) |
| 7 | Daily standup summary | `"daily standup summary slack schedule"` | Low | Slack (#1) |
| 8 | Customer onboarding sequence | `"customer onboarding email sequence drip"` | Medium | Email (#2), CRM (#3) |
| 9 | Invoice generation | `"invoice generate PDF send email"` | Medium | Email (#2) |
| 10 | Backup automation | `"database backup schedule cloud storage"` | High | None |

### Import Order (dependency-aware)

```
Phase 1 (no dependencies):
  → Slack notification hub
  → Email forwarding/routing
  → CRM contact sync
  → Error alerting
  → Backup automation

Phase 2 (depends on Phase 1):
  → Calendar automation (needs Slack)
  → GitHub PR notifications (needs Slack)
  → Invoice generation (needs Email)

Phase 3 (depends on Phase 1+2):
  → Customer onboarding sequence (needs Email + CRM)
  → Daily standup summary (needs Slack)
```

### Credential Groups

| Credential | Type | Used By |
|-----------|------|---------|
| Slack OAuth | OAuth2 | #1, #4, #5, #6, #7 |
| Gmail / SMTP | OAuth2 or API | #2, #8, #9 |
| CRM (HubSpot/Salesforce) | API Key | #3, #8 |
| GitHub | Personal Access Token | #5 |
| Google Calendar | OAuth2 | #4 |
| Cloud Storage (S3/GCS) | API Key | #10 |

---

## Suite: DevOps Monitoring

**Target:** Engineering teams needing CI/CD visibility, incident management, and operational awareness.
**Workflows:** 8
**Shared credentials:** GitHub token, Slack OAuth, monitoring API (Datadog/Grafana), cloud provider credentials

### Workflow Categories

| # | Category | Search Query | Priority | Dependencies |
|---|----------|-------------|----------|--------------|
| 1 | GitHub PR/issue tracker | `"github pull request issue tracker notification"` | High | None |
| 2 | CI/CD pipeline notifications | `"CI CD pipeline build status notification"` | High | None |
| 3 | Server health monitoring | `"server health check uptime monitor"` | High | None |
| 4 | Error log aggregation | `"error log aggregate collect notify"` | High | None |
| 5 | Deployment automation | `"deploy automation staging production"` | Medium | CI/CD (#2) |
| 6 | Incident response | `"incident response alert escalation pagerduty"` | High | Error logs (#4) |
| 7 | Uptime monitoring | `"uptime monitor website check HTTP"` | Medium | None |
| 8 | Release notes generator | `"release notes changelog generate github"` | Low | GitHub (#1) |

### Import Order

```
Phase 1 (no dependencies):
  → GitHub PR/issue tracker
  → CI/CD pipeline notifications
  → Server health monitoring
  → Error log aggregation
  → Uptime monitoring

Phase 2 (depends on Phase 1):
  → Deployment automation (needs CI/CD)
  → Incident response (needs Error logs)
  → Release notes generator (needs GitHub)
```

### Credential Groups

| Credential | Type | Used By |
|-----------|------|---------|
| GitHub | Personal Access Token | #1, #2, #5, #8 |
| Slack OAuth | OAuth2 | #1, #2, #3, #4, #6 |
| Monitoring (Datadog/Grafana) | API Key | #3, #4 |
| Cloud Provider (AWS/GCP) | API Key/Role | #5, #7 |
| PagerDuty / OpsGenie | API Key | #6 |
| SMTP / Email | API Key | #6, #7 |

---

## Suite: Marketing Automation

**Target:** Marketing teams needing campaign management, lead handling, and content distribution.
**Workflows:** 8
**Shared credentials:** Social media OAuth tokens, email marketing API, CRM API, analytics API

### Workflow Categories

| # | Category | Search Query | Priority | Dependencies |
|---|----------|-------------|----------|--------------|
| 1 | Social media scheduler | `"social media post schedule twitter linkedin"` | High | None |
| 2 | Email campaign trigger | `"email campaign trigger mailchimp sendgrid"` | High | None |
| 3 | Lead scoring | `"lead scoring qualification CRM"` | Medium | None |
| 4 | Form submission handler | `"form submission webhook lead capture"` | High | None |
| 5 | Newsletter automation | `"newsletter automated send subscriber"` | Medium | Email (#2) |
| 6 | Analytics report | `"analytics report weekly google analytics"` | Medium | None |
| 7 | Content approval workflow | `"content approval review workflow slack"` | Low | Slack |
| 8 | Audience segmentation | `"audience segment tag filter CRM"` | Low | CRM/Lead scoring (#3) |

### Import Order

```
Phase 1 (no dependencies):
  → Social media scheduler
  → Email campaign trigger
  → Lead scoring
  → Form submission handler
  → Analytics report

Phase 2 (depends on Phase 1):
  → Newsletter automation (needs Email)
  → Content approval workflow (needs Slack)
  → Audience segmentation (needs CRM/Lead scoring)
```

### Credential Groups

| Credential | Type | Used By |
|-----------|------|---------|
| Twitter/X | OAuth2 | #1 |
| LinkedIn | OAuth2 | #1 |
| Mailchimp / SendGrid | API Key | #2, #5 |
| CRM (HubSpot/Salesforce) | API Key | #3, #4, #8 |
| Google Analytics | OAuth2 | #6 |
| Slack OAuth | OAuth2 | #7 |
| Typeform / Google Forms | API Key | #4 |

---

## Batch Deployment Protocol

### Tagging convention

When deploying a suite, tag all workflows with a consistent prefix:

```
Tag format: suite-{suite-name}-{date}
Example:    suite-startup-essentials-2026-04-07
```

This enables:
- Listing all workflows from a batch: `~~workflow_list` and filter by tag
- Rolling back a batch: identify all tagged workflows and deactivate/delete
- Auditing: track which suites are deployed on an instance

### Pre-deployment checklist

Before deploying any suite:

1. **Check instance readiness** — run `~~instance_audit` or `~~health_check`
2. **List existing workflows** — `~~workflow_list` to detect naming conflicts
3. **Check existing credentials** — `~~credential_manage` to find reusable credentials
4. **Verify n8n version** — some templates require specific minimum versions
5. **Plan webhook paths** — ensure no webhook URL collisions between workflows

### Conflict resolution

| Conflict | Resolution |
|----------|-----------|
| Workflow name already exists | Append suffix: `{name} (batch-{date})` |
| Webhook path collision | Modify webhook path in the new workflow before import |
| Credential type already configured | Reuse existing credential — map it to the new workflows |
| Node type not available | Check if community node needs installation, or find alternative template |

### Post-deployment verification

After deploying a suite:

1. **List deployed workflows** — verify all expected workflows exist
2. **Check each workflow status** — should be inactive (not auto-activated)
3. **Test one workflow** — pick the simplest, configure its credentials, activate, and trigger a test
4. **Configure credentials** — set up all shared credentials, then map to each workflow
5. **Activate progressively** — activate workflows one at a time, verify each before moving to the next
