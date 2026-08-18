---
name: setup
description: This skill should be used when the user asks to "set up Chatwoot API", "get a Chatwoot access token", "configure CHATWOOT_API_KEY", "install the Chatwoot CLI", "connect to Chatwoot", "verify Chatwoot is working", or needs to obtain credentials and confirm REST API / CLI access to a Chatwoot account (cloud or self-hosted).
---

# Chatwoot Setup & Verification

Get a Chatwoot access token, set the environment variables this plugin uses, install the
`chatwoot` CLI (optional), and confirm the REST API answers. Do this before any
api-reference, cli-recipes, or webhooks-automation work.

## 1. Know which API you need

Chatwoot exposes three API families, each with its own token type. Pick the right one — the
single most common setup mistake is using the wrong token for the wrong API.

| API | Base path | Token / auth | Use for |
|-----|-----------|--------------|---------|
| **Application** | `/api/v1/accounts/{account_id}/...` | User **access token** (`api_access_token` header) | Agent/account automation: conversations, messages, contacts, inboxes, reports |
| **Platform** | `/platform/api/v1/...` | **Platform app** token (`api_access_token` header) | Super-admin provisioning: create accounts, users, account-users, agent bots |
| **Client / Public** | `/public/api/v1/inboxes/{inbox_identifier}/...` | **No token** (uses `inbox_identifier` + contact `source_id`) | Building a custom chat widget for end users |

`CHATWOOT_API_KEY` in this plugin = your **Application** user access token unless you are
explicitly doing Platform provisioning.

## 2. Get an access token

1. Sign in to Chatwoot (cloud `https://app.chatwoot.com` or your self-hosted URL).
2. Open **Profile Settings → Access Token** (avatar → Profile Settings).
3. Copy the token. It carries your agent/admin permissions — treat it as a secret.

Find your **Account ID** in the dashboard URL: `.../app/accounts/{account_id}/...`.

For the **Platform** API, the platform app token is configured by the installation owner
(Super Admin console / `installation_config`), not in Profile Settings.

## 3. Set environment variables

This plugin references these in every curl and CLI example:

```bash
export CHATWOOT_BASE_URL="https://app.chatwoot.com"   # or your self-hosted origin, no trailing slash
export CHATWOOT_API_KEY="your_access_token"            # Application user access token
export CHATWOOT_ACCOUNT_ID="1"                         # numeric account id from the dashboard URL
```

Keep these out of source control (use a secrets manager or untracked `.env`). The auth
header Chatwoot expects is literally `api_access_token` — not `Authorization: Bearer`.

## 4. Install the CLI (optional)

The official `chatwoot` CLI is the fastest path for triage and scripting.

```bash
# macOS / Linux — detects OS/arch, verifies SHA256
curl -fsSL https://chwt.app/install-cli | sh

# Configure (prompts for Base URL, API Key, Account ID; key stored in OS keyring)
chatwoot auth login

# Headless / CI — skip the keyring by exporting the key
export CHATWOOT_API_KEY="your_access_token"
```

Non-secret config lives at `~/.chatwoot/config.yaml`. See the `cli-recipes` skill for usage.
If you use Claude Code/Cursor, you can also install the upstream agent skill with
`npx skills add chatwoot/cli`.

## 5. Verify it works

Application API — a clean conversation list confirms token + account + base URL:

```bash
curl -s -H "api_access_token: ${CHATWOOT_API_KEY}" \
  "${CHATWOOT_BASE_URL}/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}/conversations" | jq '.data.meta'
```

Confirm identity (who the token belongs to):

```bash
curl -s -H "api_access_token: ${CHATWOOT_API_KEY}" \
  "${CHATWOOT_BASE_URL}/api/v1/profile" | jq '{id, name, email, role}'
```

CLI check:

```bash
chatwoot me            # current identity
chatwoot convs         # your open conversations
```

A `200` with JSON means you are ready. A `401` means the token or the `api_access_token`
header is wrong; a `404` usually means a wrong `account_id` or base URL — see the
`troubleshoot` skill.

## What this skill does NOT cover

- Endpoint-by-endpoint request/response details — see the `api-reference` skill (and the
  bundled OpenAPI specs).
- Everyday terminal workflows — see the `cli-recipes` skill.
- Webhooks, automation rules, and agent bots — see the `webhooks-automation` skill.
- Diagnosing errors — see the `troubleshoot` skill.
