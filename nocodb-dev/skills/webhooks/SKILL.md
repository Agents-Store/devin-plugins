---
name: webhooks
description: |
  Configure NocoDB webhooks (HookV3) — triggers, conditions, and notification targets (URL, Email, Messaging, Script). Use when:
  - "add a webhook"
  - "fire a Slack message on insert"
  - "send email when a record changes"
  - "trigger n8n on update"
  - "list webhooks on a table"
  - "delete a hook"
---

# Webhooks (HookV3)

NocoDB webhooks fire on record events and dispatch to a notification target (URL, Email, Messaging service, or a Script). All hook lifecycle goes through the **REST API** or the **`nc` CLI**.

The schema reference is `HookV3*` in `api-reference/references/nocodb-openapi.json`:

```bash
jq '.components.schemas.HookV3Create' skills/api-reference/references/nocodb-openapi.json
```

## Hook Anatomy (v3)

```json
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
| `notification` | Yes | One of four types (see below) |
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
    "cc":      "manager@example.com",
    "subject": "New {{record.Status}} ticket: {{record.Title}}",
    "body":    "<p>Ticket #{{record.Id}} was just created.</p>"
  }
}
```

Requires the NocoDB SMTP plugin to be configured.

### Messaging — Slack / Teams / Discord / Mattermost

```json
{
  "type": "Messaging",
  "payload": {
    "channel": "Slack",
    "webhook_url": "https://hooks.slack.com/services/...",
    "body": ":rocket: New high-priority bug: *{{record.Title}}*"
  }
}
```

`channel`: `Slack`, `MicrosoftTeams`, `Discord`, `Mattermost`. Each channel formats the message slightly differently — see `HookNotificationV3Messaging` schema for the exact shape.

### Script (Enterprise only)

```json
{
  "type": "Script",
  "payload": {
    "script_id": "<scriptId>"
  }
}
```

The Script must already exist on the same base. Scripts run in NocoDB's sandboxed JS environment.

## Create a Hook

CLI:

```bash
nc hook:create <baseId> <tableId> '<HookV3Create JSON>'
```

API:

```bash
curl -sS -X POST \
  -H "xc-token: $NOCODB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d @hook.json \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/tables/$TABLE_ID/hooks"
```

## Worked Example — Slack on Bug Inserts

```bash
nc hook:create $BASE_ID $BUGS_TABLE_ID '{
  "title": "Slack on new bug",
  "event": "record",
  "operation": ["insert"],
  "notification": {
    "type": "Messaging",
    "payload": {
      "channel": "Slack",
      "webhook_url": "https://hooks.slack.com/services/T000/B000/XXXX",
      "body": ":bug: *New bug:* {{record.Title}}\nReported by {{record.ReporterEmail}}\nhttps://nocodb.example.com/dashboard/#/nc/{{record.Id}}"
    }
  },
  "active": true
}'
```

> v3 hooks have no top-level `condition` field. To fire only on high-priority bugs, choose one of:
> 1. **Move the gate into the body** — the destination evaluates `{{record.Priority}}` and ignores Low/Medium.
> 2. **Use a `Script` notification** — write a script that inspects the record and dispatches conditionally.
> 3. **Use `trigger_fields`** for `update` events (fires only when those columns change).

## List Hooks

```bash
nc hook:list <baseId> <tableId>
```

API:

```bash
curl -sS \
  -H "xc-token: $NOCODB_API_TOKEN" \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/tables/$TABLE_ID/hooks"
```

## Update a Hook

```bash
nc hook:update <hookId> '{"active":false}'
nc hook:update <hookId> '{"notification":{"type":"URL","payload":{...}}}'
```

API:

```bash
curl -sS -X PATCH \
  -H "xc-token: $NOCODB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"active":false}' \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/hooks/$HOOK_ID"
```

## Delete a Hook

```bash
nc hook:delete <hookId>
```

API:

```bash
curl -sS -X DELETE \
  -H "xc-token: $NOCODB_API_TOKEN" \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/hooks/$HOOK_ID"
```

## Testing a Hook

NocoDB has a built-in test fire (Enterprise UI) that does not insert/update real data. Via API/CLI, the safest test is:

1. Create a single test record matching the condition.
2. Confirm the destination receives the payload.
3. Delete the test record.

Or temporarily set `active: false` while developing, then enable.

## Conditions vs Per-View Filters

Hook conditions evaluate at the record level using the same operator grammar as view filters (`eq`, `neq`, `gt`, `gte`, `like`, `in`, `blank`, `notblank`, etc.) — see `cli-reference/references/view-filter-sort.md`. The condition runs **once per affected record** for bulk operations, so a `bulkInsert` of 1000 records can fire 1000 hooks.

## Pre-Flight Checklist

1. **Destination ready.** The URL endpoint is live; the Slack webhook is provisioned; the email recipient mailbox exists; the Script exists on the same base.
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
