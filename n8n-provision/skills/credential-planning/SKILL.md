---
name: credential-planning
description: |
  Plan and prepare credentials before importing workflows to an n8n instance. Extracts credential requirements from workflow JSON, checks existing credentials, groups by service, and produces a setup checklist.
  Use when: "plan credentials for import", "what credentials needed", "n8n credential setup", "prepare credentials before import", "credential requirements", "which credentials do I need", "credential checklist"
---

# Credential Planning

Analyze workflow JSON to extract all credential requirements, map them against existing instance credentials, and produce a prioritized setup plan. All calls use `~~capability` with automatic fallback (see CONNECTORS.md).

## Extraction: Read Credential Requirements from Workflow JSON

Parse the workflow JSON to find every credential dependency:

```
FOR each node in workflow.nodes[]:
  IF node.credentials exists:
    FOR each credential_type in node.credentials:
      Record:
        - node_name: node.name
        - node_type: node.type
        - credential_type: credential key name
        - credential_id: referenced ID (will not transfer)
```

**Where credentials live in the JSON:**

```json
{
  "nodes": [
    {
      "name": "Send Slack Message",
      "type": "n8n-nodes-base.slack",
      "credentials": {
        "slackOAuth2Api": {
          "id": "123",
          "name": "Slack Account"
        }
      }
    }
  ]
}
```

> The `id` and `name` reference the SOURCE instance credentials. They will NOT work on the target instance. New credentials must be created or existing ones linked.

## Check Existing Credentials

Query the target instance for already-configured credentials:

```
1. ~~credential_manage (action: list)
   → Returns all credentials on the instance with types and names

2. Match existing credentials against extracted requirements:
   → MATCH: credential type exists → reuse it
   → PARTIAL: credential type exists but for a different account → may need a new one
   → MISSING: credential type not found → must create
```

**Matching output table:**

| Credential Type | Required By | Existing on Instance | Action |
|----------------|-------------|---------------------|--------|
| slackOAuth2Api | Slack Alert, Slack Digest | Slack — Main Workspace | Reuse |
| gmailOAuth2 | Email Notifier | — | Create new |
| postgresDb | Data Sync | PostgreSQL Production | Verify connection |

## Group by Service

Consolidate credentials so each service is configured once:

```
Service: Slack
  Credential type: slackOAuth2Api
  Used by: [Slack Alert, Slack Digest, Slack Onboarding]
  Action: Create ONE credential, link to all 3 workflows

Service: Gmail
  Credential type: gmailOAuth2
  Used by: [Email Notifier, Daily Report]
  Action: Create ONE credential, link to both workflows

Service: PostgreSQL
  Credential type: postgresDb
  Used by: [Data Sync]
  Action: Create ONE credential
```

This prevents duplicate credential creation and simplifies ongoing management.

## Common Credential Types

| Type | Auth Method | Setup Complexity | Typical Setup Steps |
|------|------------|------------------|-------------------|
| **OAuth2** | Browser-based authorization flow | Medium | 1. Create OAuth app in service console 2. Add client ID + secret in n8n 3. Authorize via browser redirect |
| **API Key** | Static key string | Low | 1. Generate key in service dashboard 2. Paste into n8n credential |
| **Header Auth** | Custom header name + value | Low | 1. Determine header name (e.g., `X-API-Key`) 2. Add name and value in n8n |
| **Basic Auth** | Username + password | Low | 1. Enter username 2. Enter password |
| **Connection String** | Host, port, user, password, database | Medium | 1. Gather connection details 2. Test connectivity 3. Configure in n8n |
| **Bearer Token** | Token string in Authorization header | Low | 1. Generate token from service 2. Paste into n8n credential |

## Setup Order

Follow this sequence to minimize back-and-forth:

1. **Shared credentials first** — identify types used by 2+ workflows, sort by dependency count (most first), create and test each
2. **Specific credentials second** — remaining types used by single workflows, create in deployment priority order
3. **Verify** — call `~~credential_manage` (action: list), cross-reference against requirements, flag any still missing

## Security Best Practices

| Practice | Implementation |
|----------|---------------|
| **Use environment variables** | Store secrets in n8n environment variables, reference as `{{ $env.SLACK_TOKEN }}` |
| **Least privilege** | Grant only the permissions each workflow needs — no admin tokens for read-only operations |
| **Rotate keys regularly** | Set a rotation schedule (90 days for API keys, 365 for OAuth) |
| **No shared admin credentials** | Each service integration gets its own credential, not a personal admin account |
| **Audit credential usage** | Periodically check which workflows use which credentials via `~~credential_manage` |
| **Document credential owners** | Track who created each credential and who manages the underlying service account |

## Post-Import Credential Linking

After workflows are imported (inactive), link credentials in the n8n editor: open each workflow, click nodes with credential warnings, select or create the matching credential, save, and test with sample data before activating.

## Credential Planning Checklist

- [ ] All credential types extracted from workflow JSON
- [ ] Existing instance credentials inventoried via `~~credential_manage`
- [ ] Requirements matched against existing credentials
- [ ] Shared credentials identified and prioritized
- [ ] Setup order determined (shared first, specific second)
- [ ] Security practices reviewed (env vars, least privilege)
- [ ] All credentials created and tested
- [ ] All imported workflows linked to correct credentials
