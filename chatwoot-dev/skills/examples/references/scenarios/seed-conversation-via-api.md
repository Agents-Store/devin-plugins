# Scenario: Seed a conversation via the Public/Client API

Goal: create a contact, open a conversation, and post a message the way a **custom chat
widget** would — using the unauthenticated Public API. No access token; the channel is
identified by its `inbox_identifier` and the contact by the `source_id` returned on creation.

Find the `inbox_identifier` in the inbox's Web Widget settings (or via the Application API
`inboxes` endpoint, `channel.webhook`/identifier fields).

```bash
INBOX_ID="your_inbox_identifier"
BASE="${CHATWOOT_BASE_URL}"   # e.g. https://app.chatwoot.com
```

## 1. Create a contact

```bash
CONTACT=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"name":"Jane Doe","email":"jane@example.com"}' \
  "${BASE}/public/api/v1/inboxes/${INBOX_ID}/contacts")
echo "$CONTACT" | jq '{source_id, pubsub_token, name}'
SOURCE_ID=$(echo "$CONTACT" | jq -r '.source_id')
```

`source_id` is the contact identifier for every subsequent Public API call; `pubsub_token`
is used to subscribe to the websocket for live updates.

## 2. Create a conversation

```bash
CONV=$(curl -s -X POST -H "Content-Type: application/json" \
  "${BASE}/public/api/v1/inboxes/${INBOX_ID}/contacts/${SOURCE_ID}/conversations")
CONV_ID=$(echo "$CONV" | jq -r '.id')
echo "conversation: $CONV_ID"
```

## 3. Post a message from the contact

```bash
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"content":"Hi, I need help with my order."}' \
  "${BASE}/public/api/v1/inboxes/${INBOX_ID}/contacts/${SOURCE_ID}/conversations/${CONV_ID}/messages" \
  | jq '{id, content, message_type}'
```

## 4. Read messages back

```bash
curl -s "${BASE}/public/api/v1/inboxes/${INBOX_ID}/contacts/${SOURCE_ID}/conversations/${CONV_ID}/messages" | jq .
```

## Notes

- Other Public endpoints: `toggle_typing` (`?typing_status=on|off`), `toggle_status`
  (resolve), `update_last_seen`. See `references/client-api.md`.
- The agent side of this conversation is then handled through the **Application API**
  (assign, reply, resolve) — that is where `CHATWOOT_API_KEY` is required.
