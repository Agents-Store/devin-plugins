---
name: webhooks
description: |
  Configure NocoDB webhooks (HookV3) — triggers, field scoping, and notification targets (URL, Email, Slack/Discord/Telegram/Whatsapp/Twilio messaging, Script). Use when:
  - "add a webhook"
  - "fire a Slack message on insert"
  - "send email when a record changes"
  - "trigger n8n on update"
  - "list webhooks on a table"
  - "delete a hook"
---

# Webhooks (HookV3)

NocoDB webhooks fire on record events and dispatch to a notification target (URL, Email, a messaging service, or a Script). Hook APIs are available on cloud-hosted Business and above and on licensed self-hosted deployments. Hook lifecycle goes through the MCP `hooks` category on **Cloud / licensed** (`listTools category: "hooks"`, then `callTool`) or through the **REST API** (`curl` on Meta API v3) on Community Edition / as a fallback. See **mcp-patterns** for the contract.

The schema reference is `HookV3*` in `api-reference/references/nocodb-meta-openapi.json`:

```bash
jq '.components.schemas.HookV3Create' skills/api-reference/references/nocodb-meta-openapi.json
```

## Hook Anatomy (v3)

```jsonc
{
  "title":          "<display name>",
  "description":    "Optional",
  "event":          "record",                          // "record" | "manual"
  "operation":      ["insert", "update"],              // array of "insert" | "update" | "delete"
  "notification":   { "type": "...", "payload": { ... } },
  "trigger_fields": ["<columnId>", "<columnId>"],
  "active":         true
}
```

Required: `title`, `operation`, `notification`.

| Key | Required | Notes |
|-----|----------|-------|
| `title` | Yes | Free text — keep distinct so logs are readable |
| `event` | No | `record` (default) fires on the chosen `operation`(s); `manual` fires only when explicitly invoked from a Button or Script |
| `operation` | Yes | **Array** of `insert` / `update` / `delete`. One hook can listen to multiple operations |
| `notification` | Yes | URL, Email, a messaging service or Script (see below) |
| `trigger_fields` | No | Array of column IDs — for `update` events, only fire when one of these fields changed |
| `active` | No | Default `true`; set `false` to disable without deleting |
| `description` | No | Free text |

> **v3 simplifications you may have seen elsewhere don't apply:**
> - There is no `before` / `after` distinction — all v3 hooks are async-after-commit.
> - There is no top-level `condition` filter. To gate by record state, use `trigger_fields` for change-detection on update, or use a `Script` notification for richer logic.
> - There is no separate `bulkInsert` / `bulkUpdate` / `bulkDelete` operation — `insert` / `update` / `delete` cover both single-record and bulk operations; the destination payload contains `record` (single) or `records` (bulk).

## Notification Types

### URL — generic webhook

```json
{
  "type": "URL",
  "payload": {
    "method":  "POST",
    "path":    "https://hooks.example.com/nocodb",
    "body":    "{\"id\": \"{{record.Id}}\", \"title\": \"{{record.Title}}\"}",
    "headers": [ { "name": "Authorization", "value": "Bearer ${API_KEY}" } ]
  }
}
```

`{{record.<FieldName>}}` is the templating syntax. Both single-record and bulk operations send a JSON body — check `record` for single, `records` for bulk.

### Email

```json
{
  "type": "Email",
  "payload": {
    "to":      "ops@example.com",
    "subject": "New {{record.Status}} ticket: {{record.Title}}",
    "body":    "<p>Ticket #{{record.Id}} was just created.</p>"
  }
}
```

`to`, `subject` and `body` are all required. Requires the NocoDB SMTP plugin to be configured.

### Messaging — Slack / Discord / Telegram / Whatsapp / Twilio

The notification `type` **is** the service; the payload carries the message `body`:

```json
{
  "type": "Slack",
  "payload": {
    "body": ":rocket: New high-priority bug: *{{record.Title}}*"
  }
}
```

`type`: `Slack`, `Discord`, `Telegram`, `Whatsapp`, `Twilio` (per `HookNotificationV3Messaging`). The spec's `payload` has no channel or webhook-URL key — the connection to the service comes from the matching NocoDB notification plugin / integration, so configure it in NocoDB first.

### Script

```json
{
  "type": "Script",
  "payload": {
    "scriptId": "<scriptId>"
  }
}
```

The Script must already exist on the same base (Script APIs: cloud Enterprise or licensed self-hosted). `method` (default `POST`) and `path` are optional. Scripts run in NocoDB's sandboxed JS environment.

All notification types also accept `include_user`, `trigger_form` and `trigger_form_id`.

## Create a Hook

REST:

```bash
curl -sS -X POST \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d @hook.json \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/tables/${TABLE_ID}/hooks"
```

MCP (Cloud / licensed):

```
mcp__plugin_nocodb-dev_nocodb__listTools  category: "hooks"
mcp__plugin_nocodb-dev_nocodb__callTool   name: "createHook"
  arguments: { tableId: "<tableId>", title: "Slack on new bug", event: "record",
               operation: ["insert"], notification: { type: "Slack", payload: { body: "..." } },
               active: true }
```

`trigger_fields` in the MCP tool requires `operation` to include `"update"` and `event` `"record"`; any other combination is rejected.

## Worked Example — Slack on Bug Inserts

```bash
curl -sS -X POST \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Slack on new bug",
    "event": "record",
    "operation": ["insert"],
    "notification": {
      "type": "Slack",
      "payload": {
        "body": ":bug: *New bug:* {{record.Title}}\nReported by {{record.ReporterEmail}}"
      }
    },
    "active": true
  }' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/tables/${BUGS_TABLE_ID}/hooks"
```

> v3 hooks have no top-level `condition` field. To fire only on high-priority bugs, choose one of:
> 1. **Move the gate into the body** — the destination evaluates `{{record.Priority}}` and ignores Low/Medium.
> 2. **Use a `Script` notification** — write a script that inspects the record and dispatches conditionally.
> 3. **Use `trigger_fields`** for `update` events (fires only when those columns change).

## List Hooks

```bash
curl -sS \
  -H "xc-token: ${NOCODB_TOKEN}" \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/tables/${TABLE_ID}/hooks"
```

MCP: `listHooks` / `getHook` (read tools, always listed).

## Update a Hook

```bash
curl -sS -X PATCH \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"active":false}' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/hooks/${HOOK_ID}"
```

To change the target, send a new `notification` object (`{"notification":{"type":"URL","payload":{...}}}`).

The MCP `updateHook` is a **full replacement**, not a patch: read the hook with `getHook` first and resend every key you want to keep, including `notification` — anything omitted is rejected rather than preserved.

## Delete a Hook

```bash
curl -sS -X DELETE \
  -H "xc-token: ${NOCODB_TOKEN}" \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/hooks/${HOOK_ID}"
```

MCP: `callTool name: "deleteHook"  arguments: { hookId: "<hookId>" }`.

## Testing a Hook

NocoDB has a built-in test fire in its UI that does not insert/update real data. Via API / MCP, the safest test is:

1. Create a single test record matching the condition.
2. Confirm the destination receives the payload.
3. Delete the test record.

Or temporarily set `active: false` while developing, then enable.

## Pre-Flight Checklist

1. **Destination ready.** The URL endpoint is live; the messaging integration (Slack, Discord, …) is configured in NocoDB; the email recipient mailbox exists; the Script exists on the same base.
2. **Templating fields.** Every `{{record.<X>}}` references a column that exists on the table. Misspellings render literally as `{{record.Misspell}}`.
3. **Idempotency.** All v3 hooks are async-after-commit and NocoDB retries on non-2xx responses; the destination must tolerate replays.
4. **Bulk awareness.** Bulk operations fire one hook per affected record — destinations should batch on their side if they care.
5. **Secrets.** Don't bake long-lived secrets into the body; prefer Authorization headers — and rotate them at the destination.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Hook never fires | `active: false`; wrong `operation` array | Check status; verify `operation` includes the action you expect |
| Hook fires twice | Two hooks with overlapping `operation` arrays on the same table | List hooks and de-dup |
| `{{record.Field}}` literal in body | Field name typo or case mismatch | Match the column title exactly (case-sensitive) |
| 401 on URL hook | Destination requires auth | Add `Authorization` header in `payload.headers` |
| `update` hook fires when unrelated fields change | `trigger_fields` not set | Add `trigger_fields: ["<id>", ...]` so only changes to those columns fire |
| Bulk-update sends per-record payloads instead of one batched body | NocoDB v3 sends one HTTP request per affected record | Process them in your destination; there's no batched-bulk operation in v3 |
