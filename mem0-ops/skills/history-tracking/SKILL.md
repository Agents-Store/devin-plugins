---
name: history-tracking
description: Memory history and change tracking — view evolution of memories over time, audit modifications, and track knowledge changes. This skill should be used when the user asks to see memory changes, audit modifications, or track how information evolved.
---

# History & Change Tracking

Track how memories evolve over time — view changes, audit modifications, and investigate knowledge evolution.

## Available Tools

| Tool | Purpose | Required Params |
|------|---------|----------------|
| get_memory_history | View change history | memory_id |
| get_memory | Get current state | memory_id |

## Viewing History

Tool: `get_memory_history`

```
get_memory_history({ memory_id: "abc-123" })
```

Returns a timeline of all changes made to the memory, including timestamps and old/new values.

## Common Workflows

### Full Audit Trail
```
1. get_memory(memory_id) -> show current state
2. get_memory_history(memory_id) -> show all changes
3. Present as timeline: date, action, old value -> new value
```

### Verify Recent Update
```
1. update_memory(memory_id, new_data)
2. get_memory_history(memory_id) -> confirm change recorded
3. Show before/after comparison
```

### Investigate Unexpected Content
```
1. get_memory(memory_id) -> see current (unexpected) content
2. get_memory_history(memory_id) -> find when it changed
3. Identify the problematic update
4. update_memory(memory_id, correct_data) -> fix if needed
```

### Knowledge Evolution Report
```
1. get_all_memories(user_id) -> list all memories
2. For key memories: get_memory_history(memory_id)
3. Report on frequently changed memories
4. Flag memories with many revisions for review
```

### Manual Rollback
```
1. get_memory_history(memory_id) -> find previous correct value
2. update_memory(memory_id, previous_value) -> restore
3. get_memory(memory_id) -> verify restoration
```

## Best Practices

1. **Check history before updating** — understand context of current content
2. **Use history for debugging** — unexpected content often has a traceable cause
3. **Present as timeline** — chronological format is easiest to understand
4. **Combine with get_memory** — show current state alongside history
5. **Flag frequent changes** — memories updated often may need better structure
6. **Track provenance** — history helps identify who/what changed information
