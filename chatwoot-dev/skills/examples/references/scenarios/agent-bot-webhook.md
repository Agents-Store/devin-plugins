# Scenario: Agent bot driven by a webhook

Goal: stand up a bot that receives `message_created` events for an inbox and replies through
the Application API. Combines `webhooks-automation` (events, signatures, bots) with
`api-reference` (sending messages).

## 1. Create the bot

```bash
BOT=$(curl -s -X POST \
  -H "api_access_token: ${CHATWOOT_PLATFORM_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name":"Triage Bot","outgoing_url":"https://example.com/bot","bot_type":"webhook"}' \
  "${CHATWOOT_BASE_URL}/platform/api/v1/agent_bots")
echo "$BOT" | jq '{id, name, access_token}'
```

Assign the bot to an inbox in the dashboard (Inbox Settings → Bot) or via the account-scoped
`agent_bots` endpoints. The bot's own `access_token` can be used as `CHATWOOT_API_KEY` for
its replies.

## 2. Receive events and reply

```python
from flask import Flask, request
import os, hashlib, hmac, requests

app = Flask(__name__)
BASE, TOKEN, ACC = (os.environ[k] for k in
                    ("CHATWOOT_BASE_URL", "CHATWOOT_API_KEY", "CHATWOOT_ACCOUNT_ID"))
SECRET = os.environ.get("CHATWOOT_WEBHOOK_SECRET")  # set if the webhook is signed

def signed_ok():
    if not SECRET:
        return True
    ts = request.headers.get("X-Chatwoot-Timestamp", "")
    sig = request.headers.get("X-Chatwoot-Signature", "")
    expected = "sha256=" + hmac.new(
        SECRET.encode(), f"{ts}.".encode() + request.get_data(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, sig)

@app.post("/bot")
def bot():
    if not signed_ok():
        return "bad signature", 401
    e = request.get_json(force=True)
    if e.get("event") == "message_created" and e.get("message_type") == "incoming":
        conv = e["conversation"]["id"]
        requests.post(
            f"{BASE}/api/v1/accounts/{ACC}/conversations/{conv}/messages",
            headers={"api_access_token": TOKEN},
            json={"content": "Got it — an agent will follow up shortly.",
                  "message_type": "outgoing"},
            timeout=10,
        )
    return "", 200
```

## 3. Guardrails

- Only react to `message_type == "incoming"` — replying to your own outgoing messages loops.
- De-duplicate retried deliveries on `X-Chatwoot-Delivery`.
- For anything sent to a real customer, confirm tone/content before enabling.
- To hand off to a human, `unassign` the bot or set conversation status to `open` for the
  team queue (see `application-api.md` → Conversations / Conversation Assignments).
