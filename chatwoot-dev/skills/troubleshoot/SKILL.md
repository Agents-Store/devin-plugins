---
name: troubleshoot
description: This skill should be used when the user hits "Chatwoot API errors", "Chatwoot 401/403/404", "Chatwoot CLI not working", "Chatwoot webhook signature mismatch", "Chatwoot token not authorized", or needs to diagnose and fix problems with the Chatwoot API, CLI, or webhooks.
---

# Chatwoot Troubleshooting

Diagnose and fix the common failure modes for the Chatwoot API, CLI, and webhooks.

## Quick diagnostics

```bash
# 1. Is the base URL reachable?
curl -sI "${CHATWOOT_BASE_URL}" | head -1

# 2. Is the token valid and which identity is it?
curl -s -H "api_access_token: ${CHATWOOT_API_KEY}" \
  "${CHATWOOT_BASE_URL}/api/v1/profile" | jq '{id, name, role}'

# 3. Does the account scope resolve?
curl -s -o /dev/null -w "%{http_code}\n" -H "api_access_token: ${CHATWOOT_API_KEY}" \
  "${CHATWOOT_BASE_URL}/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}/conversations"
```

## Authentication & authorization

| Symptom | Cause | Fix |
|---------|-------|-----|
| `401 Unauthorized` | Missing/typo'd `api_access_token` header | Send `-H "api_access_token: ${CHATWOOT_API_KEY}"` — not `Authorization: Bearer` |
| `401` with a valid token | Right token, **wrong API family** | User token works on `/api/v1/...`, not `/platform/...`. Use the platform app token for Platform endpoints |
| `403 Forbidden` | Token role too low | The action needs admin/agent permission the token lacks — use a token with the right role |
| Platform calls all `401` | Platform API not enabled / wrong token | Platform token comes from the installation Super Admin, not Profile Settings |

## Wrong scope / not found

| Symptom | Cause | Fix |
|---------|-------|-----|
| `404` on every account call | Wrong `account_id` | Read it from the dashboard URL `.../app/accounts/{id}/...` |
| `404` / HTML instead of JSON | Wrong base URL or trailing slash | Set `CHATWOOT_BASE_URL` to the origin only (e.g. `https://app.chatwoot.com`), no trailing `/` |
| Self-hosted `404`/`502` | Reverse proxy or path prefix | Confirm the instance origin and that `/api/v1` is exposed |

## Request body errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `422 Unprocessable` | Missing/invalid fields | Compare the body to the schema: `jq '.paths["<path>"].post.requestBody' openapi/application_swagger.json` |
| Message sends but is empty/wrong type | Wrong `message_type`/`content_type` | Use `message_type: "outgoing"` (or `"incoming"`), `private: true` for notes |
| Attachment ignored | Sent as JSON | Use `multipart/form-data` with `attachments[]` (see `pagination-errors.md`) |

## CLI issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `auth login` hangs/fails | Run in a non-TTY (CI/agent) | Don't script `auth login`; export `CHATWOOT_API_KEY` and keep `~/.chatwoot/config.yaml` (or pass `-a`) |
| Agent can't parse output | Default text format | Pass `-o json` (or `-q`); never grep text output |
| `convs` returns "too few" | Defaults to your open queue | Add `--assignee all` and the right `-s` status |
| Labels got wiped | `label` replaces the set | Fetch existing first and merge; use `set -o pipefail` (see `cli-recipes`) |
| Keyring error on login | No system keyring (headless Linux) | Use the `CHATWOOT_API_KEY` env var instead of the keyring |
| Want to see the HTTP call | Debugging an odd result | Re-run with `-v` to print request/response |

## Webhook problems

| Symptom | Cause | Fix |
|---------|-------|-----|
| Signature never matches | HMAC over parsed JSON | Compute HMAC-SHA256 over the **raw** body as `"{timestamp}.{raw_body}"`, compare to `X-Chatwoot-Signature` (`sha256=...`) |
| No deliveries arrive | URL unreachable / not subscribed | Verify the endpoint is public + returns `2xx`; check `subscriptions` includes the event |
| Bot replies in a loop | Reacting to its own messages | Only act on `message_type == "incoming"` |
| Duplicate handling | Retried deliveries | De-duplicate on `X-Chatwoot-Delivery` |

## Rate limiting

`429 Too Many Requests` → add exponential backoff, reduce concurrency, and batch reads with
pagination instead of firing unbounded parallel requests. Limits differ between Cloud and
self-hosted.

## When to escalate

- Consistent `5xx` on Cloud → check https://status.chatwoot.com; on self-hosted check the
  Rails/Sidekiq logs.
- Suspected token compromise → rotate the access token in Profile Settings immediately.
