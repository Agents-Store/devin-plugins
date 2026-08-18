# Scenario: Chatbot integration

Build a chat experience on top of a Dify Chatbot/Agent/Chatflow app: discover the app,
start a conversation, continue it, stream a response, and read history.

Set up shell variables:

```bash
BASE=https://api.dify.ai/v1          # or https://your-host/v1
KEY=app-XXXXXXXXXXXXXXXXXXXX
USER=user-123                        # your stable end-user id
```

## 1. Discover the app (setup skill)

```bash
curl "$BASE/info"       --header "Authorization: Bearer $KEY"
curl "$BASE/parameters" --header "Authorization: Bearer $KEY"
```

`/info` confirms `mode` (`chat`/`agent-chat`/`advanced-chat`). `/parameters` →
`user_input_form` tells you which variables go in `inputs`.

## 2. Start a new conversation (chat-completion skill)

Omit `conversation_id` to start fresh. Capture the returned `conversation_id`.

```bash
curl -X POST "$BASE/chat-messages" \
  --header "Authorization: Bearer $KEY" \
  --header 'Content-Type: application/json' \
  --data "{
    \"query\": \"Hi! What can you do?\",
    \"inputs\": {},
    \"response_mode\": \"blocking\",
    \"user\": \"$USER\"
  }"
# → { "answer": "...", "conversation_id": "<CID>", "message_id": "<MID>", ... }
```

## 3. Continue the conversation

Pass the `conversation_id` from step 2:

```bash
CID=<conversation_id-from-step-2>

curl -X POST "$BASE/chat-messages" \
  --header "Authorization: Bearer $KEY" \
  --header 'Content-Type: application/json' \
  --data "{
    \"query\": \"Summarize that in one sentence.\",
    \"inputs\": {},
    \"response_mode\": \"blocking\",
    \"user\": \"$USER\",
    \"conversation_id\": \"$CID\"
  }"
```

## 4. Stream a response (recommended for UIs)

```bash
curl -N -X POST "$BASE/chat-messages" \
  --header "Authorization: Bearer $KEY" \
  --header 'Content-Type: application/json' \
  --data "{
    \"query\": \"Tell me a short story.\",
    \"inputs\": {},
    \"response_mode\": \"streaming\",
    \"user\": \"$USER\",
    \"conversation_id\": \"$CID\"
  }"
```

Append each `message` event's chunk; finalize on `message_end`. (See the `chat-completion`
skill's streaming-events reference.)

## 5. Suggested follow-ups & feedback

```bash
MID=<message_id>

curl "$BASE/messages/$MID/suggested?user=$USER" --header "Authorization: Bearer $KEY"

curl -X POST "$BASE/messages/$MID/feedback" \
  --header "Authorization: Bearer $KEY" \
  --header 'Content-Type: application/json' \
  --data "{ \"rating\": \"like\", \"user\": \"$USER\" }"
```

## 6. Read history (conversations skill)

```bash
# List the user's conversations
curl "$BASE/conversations?user=$USER&limit=20" --header "Authorization: Bearer $KEY"

# List messages in one conversation
curl "$BASE/messages?conversation_id=$CID&user=$USER&limit=20" \
  --header "Authorization: Bearer $KEY"
```

## Notes

- Keep `$USER` identical for the same person across all calls, or history won't line up.
- New conversation = omit `conversation_id`; continue = include it.
- For long replies always prefer `streaming` to avoid the ~100s blocking timeout.
