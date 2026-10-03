---
name: webhooks
description: |
  Use NocoDB webhooks from the business side — which events exist, how to set one up in the UI, what the receiving system gets (payload), conditions, the Button trigger, and testing. Use when:
  - "trigger something when a record changes"
  - "send NocoDB data to n8n / another system"
  - "set up a webhook in NocoDB"
  - "what does the NocoDB webhook payload look like"
  - "fire a webhook from a button"
  - "webhook only when status becomes ..."
  - "list the webhooks on a table"
---

# NocoDB Webhooks

A webhook makes NocoDB call another system when something happens to a table: a record is added, changed or deleted, or someone presses a button. This skill is the **receiving-side and UI view** — events, payload, conditions, testing. Creating, replacing and deleting hooks as code (the Meta API v3 / MCP `hooks` category, notification types such as Email, Slack, Script) is covered by `nocodb-dev:webhooks`.

Checked against the NocoDB docs ("Create Webhook") and a live MCP server in October 2026.

## Events

| Source | Events | Edition |
|--------|--------|---------|
| **Record** | *Send Me Everything*, *After Insert*, *After Update*, *After Delete* | all |
| **Button** | fires when a Button field is clicked | all |
| **View** | *Send Me Everything*, *After Create*, *After Update*, *After Delete* | paid plans (cloud and self-hosted) |
| **Field** | *Send Me Everything*, *After Create*, *After Update*, *After Delete* | paid plans |
| **Comment** | *Comment Added*, *Edited*, *Deleted*, *Resolved*, *Reopened* | paid plans |

- There are **no separate bulk events**: *After Insert*, *After Update* and *After Delete* cover "one or more records" — a bulk import or a change applied to every record in a view still arrives as these events, with several rows in one payload
- Paid plans also unlock: watching specific fields on *After Update*, firing on one form's submissions only (*After Insert*), and the *Run Script* action

## Set One Up in the UI

1. Open the table → **Tools** (toolbar) → **Webhooks** → **Add New Webhook**
2. Give it a descriptive title (`Orders - New Order Created`)
3. Choose the source (Record, View, Field, Comment or Button) and the event
4. Optional: add **conditions** (Record events only) and, on *After Update*, the fields to watch
5. Choose the action — **HTTP Request** (method GET, POST, PUT, DELETE, PATCH or HEAD, URL, headers, body) or **Run Script** (paid)
6. Press **Test webhook** — it sends a sample payload so you can see the receiver react
7. **Create Webhook**

The default body is `{{ json event }}`, the complete event as JSON. A custom body can be a Handlebars template that sends only some fields. If the receiver needs `Content-Type: application/json`, add the header yourself.

Webhook URLs and tokens sit in the NocoDB webhook configuration, so use the **production** URL of the receiver (for n8n, the Webhook node's production URL, which works once the workflow is published) and prefer an `Authorization` header over a secret inside the URL.

## What the Receiver Gets

Default body, record event (version `v3`):

```json
{
  "type": "records.after.insert",
  "id": "<event id>",
  "version": "v3",
  "data": {
    "table_id": "<tableId>",
    "table_name": "Orders",
    "view_id": "<viewId>",
    "view_name": "Orders",
    "rows": [
      { "Id": 1, "Title": "New Order", "Status": "pending", "CreatedAt": "2026-10-03T10:40:20.998Z", "UpdatedAt": "2026-10-03T10:40:20.998Z" }
    ]
  }
}
```

| Key | Meaning |
|-----|---------|
| `type` | `records.after.insert`, `records.after.update`, `records.after.delete` |
| `id`, `version` | the event id and the payload version (`"v3"`) |
| `data.table_id`, `data.table_name` | which table — use the id, not the name, in follow-up calls |
| `data.view_id`, `data.view_name` | the view the change came through |
| `data.rows` | **an array** — one entry per affected record, field title → value |
| `data.previous_rows` | *After Update* only: the same records before the change (`rows` holds the new state) |

Receiver rules:

- Loop over `data.rows`; never read only `rows[0]`
- Look the record up by its `Id` and skip what is already done — treat the receiver as one that may see the same change twice
- Answer with a quick `2xx` and do slow work afterwards (hand long jobs to a background task runner)
- Log `type` and `id` while debugging

## Conditions

Record events can carry conditions (AND/OR groups of field comparisons, for example *Status = Complete* AND *Priority = High*). A condition fires **on the transition**: the webhook runs only when the record goes from "condition not met" to "condition met" during the event, not on every later edit of a record that already matches. Conditions do not apply to Button webhooks.

**Mind the loop.** An automation that writes its status or result back to the same table fires *After Update* again. Gate the webhook with a condition on the status transition (for example `status` = `pending`, set by whoever requests a run, while the automation only writes `processing`, `completed`, `failed`), watch only the business fields on paid plans, or keep job state in a separate table.

## Button Trigger

A Button field can start a webhook, which makes a record a remote control for an automation: the user presses the button on the row, NocoDB calls the receiver with that record. Use it for "approve", "send invoice", "start the import" — actions that should happen on purpose, not on every edit.

## Webhooks Through MCP

| Edition | What works |
|---------|------------|
| **Community** | No hook tools — use the UI (or the REST API, see `nocodb-dev:webhooks`) |
| **Cloud / licensed** | `listHooks` (`tableId`) and `getHook` (`hookId`) are listed directly; `createHook`, `updateHook` and `deleteHook` sit behind `listTools` with `category: "hooks"` and run through `callTool` |

```
mcp__plugin_nocodb-ops_nocodb__listHooks   { "tableId": "<tableId>" }
mcp__plugin_nocodb-ops_nocodb__getHook     { "hookId": "<hookId>" }
```

`updateHook` replaces the whole webhook: read it with `getHook` first and send every field you want to keep, `notification` included. Hook creation and the notification types are in `nocodb-dev:webhooks`; the full tool contract is in **mcp-patterns**.

## Checklist

- The receiver URL is live and the workflow behind it is published
- *Test webhook* succeeded against the production URL
- The receiver loops over `data.rows` and tolerates a repeated event
- A condition is set when only one state change should fire it
- When "nothing happens", list the table's webhooks (`listHooks` or the Webhooks tool) and check the event, the conditions and whether the webhook is active
