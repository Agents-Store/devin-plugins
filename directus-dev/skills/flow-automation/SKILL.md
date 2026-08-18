---
name: flow-automation
description: Flow automation — triggers, operations, data chains, event hooks, webhooks, schedules. This skill should be used when the user asks to create automation flows, set up triggers, configure operations, build event-driven workflows, schedule tasks, or trigger flows programmatically in Directus.
---

# Flow Automation

Complete reference for the `flows`, `operations`, and `trigger-flow` MCP tools.

## Concepts

- **Flow** = Trigger + Chain of Operations
- Each flow has ONE trigger and a series of operations forming a data chain
- Operations connect via `resolve` (success) and `reject` (failure) paths
- Data passes through the chain using `{{ operation_key }}` variables

## Trigger Types

| Trigger | When It Fires | Key Options |
|---------|---------------|-------------|
| `event` | On item CRUD (hook) | `type` (filter/action), `scope` (items.create, items.update, items.delete), `collections` |
| `webhook` | HTTP request to flow URL | `method` (GET/POST), `async` |
| `schedule` | Cron expression | `cron` (e.g., `"0 9 * * 1"` = Monday 9am) |
| `operation` | Called by another flow | — |
| `manual` | User triggers from app | `collections`, `requireSelection`, `fields` |

## Creating a Flow

```json
Tool: flows
Input: {
  "action": "create",
  "data": {
    "name": "Notify on New Post",
    "trigger": "event",
    "status": "active",
    "accountability": "all",
    "icon": "notifications",
    "color": "#FF9800",
    "description": "Send notification when a new post is created",
    "options": {
      "type": "action",
      "scope": ["items.create"],
      "collections": ["posts"]
    }
  }
}
```

### Trigger Options by Type

**Event trigger:**
```json
"options": {
  "type": "action",
  "scope": ["items.create", "items.update"],
  "collections": ["posts"]
}
```
- `type: "filter"` — runs before the operation (can block it)
- `type: "action"` — runs after the operation

**Schedule trigger:**
```json
"options": {
  "cron": "0 */6 * * *"
}
```

**Manual trigger:**
```json
"options": {
  "collections": ["posts"],
  "requireSelection": true,
  "fields": [
    { "field": "reason", "type": "string", "name": "Reason" }
  ]
}
```

**Webhook trigger:**
```json
"options": {
  "method": "POST",
  "async": false
}
```

## Operation Types

| Type | Description | Key Options |
|------|-------------|-------------|
| `condition` | If/else branching | `filter` (condition rules) |
| `item-create` | Create items | `collection`, `payload` |
| `item-read` | Read items | `collection`, `query` |
| `item-update` | Update items | `collection`, `payload`, `query` |
| `item-delete` | Delete items | `collection`, `query` |
| `mail` | Send email | `to`, `subject`, `body` |
| `notification` | In-app notification | `recipient`, `subject`, `message` |
| `request` | HTTP request | `url`, `method`, `headers`, `body` |
| `sleep` | Wait/delay | `milliseconds` |
| `log` | Log to console | `message` |
| `exec` | Run custom code | `code` |
| `transform` | Transform data | `json` |
| `trigger` | Chain to another flow | `flow` |

## Creating Operations

```json
Tool: operations
Input: {
  "action": "create",
  "data": {
    "flow": "flow-uuid-here",
    "key": "check_status",
    "type": "condition",
    "name": "Check if Published",
    "options": {
      "filter": {
        "$trigger": {
          "payload": {
            "status": { "_eq": "published" }
          }
        }
      }
    },
    "position_x": 20,
    "position_y": 1,
    "resolve": "next-op-uuid-or-null",
    "reject": null
  }
}
```

## Connecting Operations

Operations form a chain through `resolve` and `reject` UUIDs:

1. Create all operations first (with `resolve: null`, `reject: null`)
2. Update each operation with the correct `resolve`/`reject` UUIDs
3. Update the flow with `operation: "first-op-uuid"` to set the entry point

```json
Tool: flows
Input: {
  "action": "update",
  "key": "flow-uuid",
  "data": { "operation": "first-operation-uuid" }
}
```

## Data Chain Variables

Access data from triggers and previous operations:

| Variable | Source |
|----------|--------|
| `{{ $trigger }}` | Trigger data (payload, keys, collection) |
| `{{ $trigger.payload }}` | Item data that triggered the flow |
| `{{ $trigger.keys }}` | Primary keys of items |
| `{{ $trigger.collection }}` | Collection name |
| `{{ $trigger.body }}` | Webhook/manual trigger body |
| `{{ operation_key }}` | Output of a specific operation (use the `key` you set) |
| `{{ $accountability }}` | User who triggered the flow |

### Critical Syntax Rules

1. **Condition filters** — Use nested objects, NOT dot notation:
   ```json
   // CORRECT
   { "$trigger": { "payload": { "status": { "_eq": "published" } } } }

   // WRONG
   { "$trigger.payload.status": { "_eq": "published" } }
   ```

2. **Request headers** — Array of `{header, value}` objects, NOT key-value:
   ```json
   // CORRECT
   "headers": [
     { "header": "Content-Type", "value": "application/json" },
     { "header": "Authorization", "value": "Bearer token" }
   ]

   // WRONG
   "headers": { "Content-Type": "application/json" }
   ```

3. **Request body** — Stringified JSON, NOT native objects:
   ```json
   // CORRECT
   "body": "{\"message\": \"{{ $trigger.payload.title }}\"}"

   // WRONG
   "body": { "message": "{{ $trigger.payload.title }}" }
   ```

4. **Data chain references** — Use explicit operation keys:
   ```json
   // CORRECT (using operation key)
   "{{ read_user.email }}"

   // AVOID
   "{{ $last }}"
   ```

## Complete Flow Example

### "Send Slack Notification on New Published Post"

**Step 1: Create the flow:**
```json
Tool: flows
Input: {
  "action": "create",
  "data": {
    "name": "Notify Slack on Publish",
    "trigger": "event",
    "status": "active",
    "options": {
      "type": "action",
      "scope": ["items.create", "items.update"],
      "collections": ["posts"]
    }
  }
}
```

**Step 2: Create condition operation:**
```json
Tool: operations
Input: {
  "action": "create",
  "data": {
    "flow": "FLOW_UUID",
    "key": "is_published",
    "type": "condition",
    "name": "Is Published?",
    "options": {
      "filter": {
        "$trigger": {
          "payload": {
            "status": { "_eq": "published" }
          }
        }
      }
    },
    "position_x": 20,
    "position_y": 1
  }
}
```

**Step 3: Create HTTP request operation:**
```json
Tool: operations
Input: {
  "action": "create",
  "data": {
    "flow": "FLOW_UUID",
    "key": "send_slack",
    "type": "request",
    "name": "Send to Slack",
    "options": {
      "url": "https://hooks.slack.com/services/XXX",
      "method": "POST",
      "headers": [
        { "header": "Content-Type", "value": "application/json" }
      ],
      "body": "{\"text\": \"New post published: {{ $trigger.payload.title }}\"}"
    },
    "position_x": 40,
    "position_y": 1
  }
}
```

**Step 4: Connect operations:**
```json
Tool: operations
Input: {
  "action": "update",
  "key": "is_published",
  "data": { "resolve": "SEND_SLACK_UUID" }
}
```

**Step 5: Set flow entry point:**
```json
Tool: flows
Input: {
  "action": "update",
  "key": "FLOW_UUID",
  "data": { "operation": "IS_PUBLISHED_UUID" }
}
```

## Triggering Flows Programmatically

**Important:** Always read the flow definition first to understand requirements.

```json
Tool: flows
Input: { "action": "read", "key": "flow-uuid" }
```

Then trigger:

```json
Tool: trigger-flow
Input: {
  "id": "flow-uuid",
  "collection": "posts",
  "keys": ["item-uuid-1"],
  "data": { "custom_field": "value" }
}
```

## Managing Flows

### List All Flows

```json
Tool: flows
Input: {
  "action": "read",
  "query": {
    "fields": ["id", "name", "status", "trigger", "description"],
    "sort": ["name"]
  }
}
```

### Activate/Deactivate

```json
Tool: flows
Input: {
  "action": "update",
  "key": "flow-uuid",
  "data": { "status": "inactive" }
}
```

## Best Practices

- Use explicit operation keys (e.g., `"check_status"`, `"send_email"`) — never rely on `$last`
- Test with manual trigger first before switching to event/schedule
- Use condition operations to filter — avoid running all operations on every trigger
- Keep flows focused on a single responsibility
- Log important operations for debugging
- Set `accountability: "all"` for full audit trails
