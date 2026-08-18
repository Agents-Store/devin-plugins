---
name: memory-crud
description: Memory CRUD operations — add, get, update, delete memories, and batch operations. This skill should be used when the user asks to create, read, update, or delete memories, or perform bulk memory management.
---

# Memory CRUD Operations

Covers all memory lifecycle operations — adding, retrieving, updating, deleting, and batch management.

## Available Tools

| Tool | Purpose | Required Params |
|------|---------|----------------|
| add_memories | Add new memories | messages[] |
| get_memory | Get single memory | memory_id |
| get_all_memories | List all memories | — |
| update_memory | Update content | memory_id, data |
| delete_memory | Delete memory | memory_id |
| batch_update_memories | Bulk update (max 100) | memories[] |
| batch_delete_memories | Bulk delete (max 100) | memory_ids[] |

## Adding Memories

Tool: `add_memories`

### Messages Format
```
add_memories({
  messages: [
    {"role": "user", "content": "The project uses React 18 with TypeScript"},
    {"role": "assistant", "content": "Noted: React 18 + TypeScript stack"}
  ],
  user_id: "project-alpha",
  metadata: {"category": "tech-stack", "project": "alpha"},
  infer: true
})
```

### Parameters

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| messages | array | Yes | Array of {role, content} objects |
| user_id | string | No | Scope to a specific user |
| agent_id | string | No | Scope to a specific agent |
| app_id | string | No | Scope to a specific app |
| run_id | string | No | Scope to a specific run |
| metadata | object | No | Key-value tags for categorization |
| infer | boolean | No | true = extract facts from conversation, false = store literally |

### When to Use infer

| infer | Use Case |
|-------|----------|
| true (default) | Conversational input — system extracts key facts automatically |
| false | Structured facts — store the exact text as-is |

## Getting Memories

### Single Memory
```
get_memory({ memory_id: "abc-123" })
```

### All Memories with Pagination
```
get_all_memories({
  user_id: "project-alpha",
  page: 1,
  page_size: 50,
  limit: 100
})
```

### Pagination Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| limit | int | 0 (all) | Maximum total results |
| page | int | 0 | Page number |
| page_size | int | 0 | Results per page |

## Updating Memories

Tool: `update_memory`

```
update_memory({
  memory_id: "abc-123",
  data: "The project migrated from React 18 to React 19"
})
```

**Important:** The `data` parameter must be a **string**, not an object.

## Deleting Memories

Tool: `delete_memory`

```
delete_memory({ memory_id: "abc-123" })
```

**Best practice:** Always `get_memory` first to show what will be deleted, then confirm with the user.

## Batch Operations

### Batch Update (max 100)
```
batch_update_memories({
  memories: [
    { "memory_id": "abc-123", "data": "Updated fact 1" },
    { "memory_id": "def-456", "data": "Updated fact 2" }
  ]
})
```

### Batch Delete (max 100)
```
batch_delete_memories({
  memory_ids: ["abc-123", "def-456", "ghi-789"]
})
```

**If more than 100 items:** Split into chunks of 100 and execute sequentially.

## Common Workflows

### Add and Verify
```
1. add_memories(messages, user_id) -> get created IDs
2. search_memories(query) -> confirm stored correctly
```

### Safe Update
```
1. get_memory(memory_id) -> show current content
2. Confirm change with user
3. update_memory(memory_id, new_data)
4. get_memory(memory_id) -> verify update
```

### Cleanup Stale Memories
```
1. get_all_memories(user_id) -> list all
2. Identify outdated entries
3. batch_delete_memories(stale_ids) -> remove
4. get_all_memories(user_id) -> verify cleanup
```

### Bulk Content Correction
```
1. search_memories(query) -> find memories to fix
2. Prepare updates array
3. batch_update_memories(updates) -> apply all at once
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Memory not found | Invalid memory_id | Verify ID with search_memories first |
| Batch too large | >100 items | Split into chunks of 100 |
| Empty results | Missing user_id scope | Add user_id parameter |
| data must be string | Passing object to update | Convert to string |
| Duplicate content | Not checking before add | search_memories before add_memories |

## Best Practices

1. **Scope with IDs** — always use user_id/agent_id for multi-tenant setups
2. **infer=true for conversations** — let the system extract key facts
3. **infer=false for structured data** — store exact text when precision matters
4. **Search before adding** — avoid duplicates
5. **Batch for efficiency** — use batch operations instead of loops (max 100)
6. **Verify destructive ops** — get_memory before delete, confirm with user
7. **Use metadata** — tag memories for easier categorization and filtering
