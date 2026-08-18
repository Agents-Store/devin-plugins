---
name: webhooks-automation
description: This skill should be used when the user wants to "set up a Chatwoot webhook", "verify a Chatwoot webhook signature", "build a Chatwoot agent bot", "handle Chatwoot events", "create an automation rule", or build event-driven integrations and bots on top of Chatwoot (webhooks, automation rules, agent bots, integration hooks).
---

# Chatwoot Webhooks & Automation

Build *on* Chatwoot: receive events via webhooks, verify their signatures, react with an
agent bot, and automate routing with automation rules. Endpoints and schemas are in the
`api-reference` skill (`references/application-api.md`, `references/platform-api.md`) and the
bundled `openapi/*.json` specs.

## Webhooks

Register a webhook on the account to receive HTTP POSTs when events occur.

```bash
curl -s -X POST \
  -H "api_access_token: ${CHATWOOT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/chatwoot/webhook",
       "subscriptions":["conversation_created","message_created","conversation_status_changed"]}' \
  "${CHATWOOT_BASE_URL}/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}/webhooks" | jq .
```

Subscribable events:

`conversation_created`, `conversation_updated`, `conversation_status_changed`,
`contact_created`, `contact_updated`, `message_created`, `message_updated`,
`webwidget_triggered`, `conversation_typing_on`, `conversation_typing_off`.

### Verifying webhook signatures

When the webhook has a `secret`, signed deliveries include headers:

- `X-Chatwoot-Timestamp` — delivery timestamp
- `X-Chatwoot-Signature` — `sha256=` + HMAC-SHA256 of `"{timestamp}.{raw_request_body}"` using the secret
- `X-Chatwoot-Delivery` — delivery id (when available)

Always compute the HMAC over the **raw** request body (before JSON parsing) and compare with
a constant-time check.

```python
import hashlib, hmac

def verify(secret: str, timestamp: str, raw_body: bytes, signature_header: str) -> bool:
    signed = f"{timestamp}.".encode() + raw_body
    expected = "sha256=" + hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)
```

## Agent bots

An agent bot is a programmatic participant that receives a conversation's events at its
`outgoing_url` and replies through the Application API. Create bots with the Platform API (or
the account-scoped `agent_bots` endpoints — see `references/application-api.md`), then assign
the bot to an inbox.

```bash
# Create a bot (platform token)
curl -s -X POST \
  -H "api_access_token: ${CHATWOOT_PLATFORM_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name":"Triage Bot","outgoing_url":"https://example.com/bot","bot_type":"webhook"}' \
  "${CHATWOOT_BASE_URL}/platform/api/v1/agent_bots" | jq .
```

The bot endpoint receives `message_created` payloads; reply by POSTing back to the
conversation. A minimal receiver + reply loop:

```python
from flask import Flask, request, abort
import os, requests

app = Flask(__name__)
BASE = os.environ["CHATWOOT_BASE_URL"]
TOKEN = os.environ["CHATWOOT_API_KEY"]           # bot or agent access token
ACC = os.environ["CHATWOOT_ACCOUNT_ID"]

@app.post("/bot")
def bot():
    e = request.get_json(force=True)
    if e.get("event") == "message_created" and e.get("message_type") == "incoming":
        conv = e["conversation"]["id"]
        requests.post(
            f"{BASE}/api/v1/accounts/{ACC}/conversations/{conv}/messages",
            headers={"api_access_token": TOKEN},
            json={"content": "Thanks! An agent will be with you shortly.",
                  "message_type": "outgoing"},
            timeout=10,
        )
    return "", 200
```

Reply only to `message_type == "incoming"` events to avoid reacting to your own outgoing
messages (an infinite loop). Confirm tone/content before enabling auto-replies in production.

## Automation rules

Automation rules run actions when an event matches conditions — no external service needed.
Event names: `conversation_created`, `conversation_updated`, `message_created`.

```bash
curl -s -X POST \
  -H "api_access_token: ${CHATWOOT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
        "name": "Label help requests",
        "event_name": "message_created",
        "active": true,
        "conditions": [
          {"attribute_key":"content","filter_operator":"contains","values":["help"],"query_operator":null}
        ],
        "actions": [
          {"action_name":"add_label","action_params":["support"]}
        ]
      }' \
  "${CHATWOOT_BASE_URL}/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}/automation_rules" | jq .
```

Each condition has `attribute_key`, `filter_operator` (e.g. `contains`, `equal_to`),
`values`, and `query_operator` (`and`/`or`/null to chain). Common actions: `add_label`,
`assign_agent`, `assign_team`, `mute_conversation`, `send_message`, `change_priority`.
See `automation_rule_item` in `openapi/application_swagger.json` for the full schema.

## Integration hooks

Account/inbox integrations (e.g. Dialogflow, Slack, webhook-type apps) are managed under
`integrations` — list apps, then create a hook with the app's `settings`. See the
`Integrations` section of `references/application-api.md`.

## When to use the Client (Public) API instead

If you are building the *customer-facing* widget rather than reacting to events server-side,
create contacts/conversations/messages through the unauthenticated Public API — see
`references/client-api.md`.
