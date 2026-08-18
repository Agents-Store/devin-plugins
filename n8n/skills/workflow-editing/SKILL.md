---
name: workflow-editing
description: Workflow editing — adding/removing nodes, updating connections, modifying node parameters. This skill should be used when the user asks to edit, modify, or update an existing workflow, add or remove nodes, or change node settings.
---

# Workflow Editing

This skill covers editing existing n8n workflows — adding nodes, removing nodes, updating connections, and modifying node parameters.

## Available Tools

| Tool | Description |
|------|-------------|
| `get_workflow` | Get full workflow details (current state) |
| `update_workflow` | Save modified workflow |
| `deactivate_workflow` | Deactivate before editing |
| `activate_workflow` | Re-activate after editing |
| `execute_workflow` | Test changes |
| `get_execution` | Verify execution results |

## Safe Editing Process

**Always follow this order when editing active workflows:**

```
1. get_workflow(id) -> Get current full structure
2. deactivate_workflow(id) -> Prevent mid-edit executions
3. Modify the nodes and connections
4. update_workflow(id, modified_data) -> Save changes
5. execute_workflow(id) -> Test with sample data
6. get_execution(exec_id) -> Verify node outputs
7. activate_workflow(id) -> Re-enable for production
```

## Adding a Node

### Process
```
1. get_workflow(id) -> Get current nodes[] and connections{}
2. Add new node object to nodes[]
3. Update connections{} to wire the new node
4. update_workflow(id, { nodes, connections })
```

### Example: Insert Node Between Two Existing Nodes

Before: `Webhook → Process Data`
After: `Webhook → Validate → Process Data`

```
1. get_workflow(id) -> Get nodes and connections
2. Add node:
   {
     "name": "Validate",
     "type": "conditional",  // platform-specific: e.g. "n8n-nodes-base.if"
     "position": [350, 300],
     "parameters": {
       "conditions": { "string": [{ "value1": "={{ $json.email }}", "operation": "isNotEmpty" }] }
     }
   }
3. Update connections:
   "Webhook" → "Validate" (was "Webhook" → "Process Data")
   "Validate" true → "Process Data"
   "Validate" false → (error handling or stop)
4. update_workflow(id, { nodes, connections })
```

## Removing a Node

### Process
```
1. get_workflow(id)
2. Remove node from nodes[]
3. Remove all connections referencing the removed node
4. Reconnect remaining nodes to maintain flow
5. update_workflow(id, { nodes, connections })
```

### Example: Remove a Middle Node

Before: `A → B → C`
After: `A → C`

```
1. Remove B from nodes[]
2. Remove "A" → "B" and "B" → "C" connections
3. Add "A" → "C" connection
4. update_workflow(id, { nodes, connections })
```

## Updating Node Parameters

### Process
```
1. get_workflow(id)
2. Find target node in nodes[]
3. Modify its parameters
4. update_workflow(id, { nodes, connections })
```

### Example: Change HTTP URL
```
Find node by name "Fetch Data" in nodes[]
Update: node.parameters.url = "https://new-api.example.com/v2/data"
update_workflow(id, { nodes, connections })
```

### Example: Change Schedule Interval
```
Find "Schedule" node in nodes[]
Update: node.parameters.rule.interval = [{ "field": "minutes", "minutesInterval": 15 }]
update_workflow(id, { nodes, connections })
```

## Common Editing Tasks

### Add Error Handling
```
1. get_workflow(id) → find the critical node
2. Add an error handler node (e.g., type: error-trigger)
3. Connect the critical node's error output to handler
4. In the handler: log error details, send notification, or retry
5. Save and test by deliberately causing an error
```

### Common Editing Errors
- **Broken connections after removing node** → always reconnect remaining nodes; check both incoming and outgoing connections
- **Duplicate node names** → node names must be unique within a workflow; rename before saving
- **Invalid expressions after node rename** → expressions reference node names; if you rename "Fetch Data" to "Get Orders", update all `$node["Fetch Data"]` references
- **Lost parameters on node type change** → when replacing a node type, parameters don't carry over; configure new node from scratch
- **Position overlaps** → adjust position coordinates so nodes don't visually overlap in the editor

### Safe Rollback Pattern
```
1. get_workflow(id) → save a copy of the original nodes[] and connections{}
2. Make your edits
3. update_workflow(id, modified_data)
4. execute_workflow(id) → test
5. If test fails: update_workflow(id, original_data) → restore original
```

### Replace a Node Type
```
1. Get workflow -> find target node
2. Note its connections (incoming and outgoing)
3. Replace the node with new type and parameters
4. Reuse the same connections
5. Save and test
```

### Reorder Nodes (Add Between)
```
1. Get workflow -> find insertion point
2. Add new node
3. Break connection: Source → Old Target
4. Add connections: Source → New Node → Old Target
5. Save and test
```

## Connection Manipulation Reference

### Get incoming connections for a node
Scan all connections objects — find entries where target `"node"` matches your node name.

### Get outgoing connections for a node
Look up `connections[nodeName]` — it lists all outputs and their targets.

### Move a connection
Remove old entry from source's connection array, add new entry pointing to new target.

## Best Practices

1. **Always get current state** — never edit from memory, always `get_workflow` first
2. **Deactivate active workflows** — prevent executions during edit
3. **Test after every change** — `execute_workflow` + `get_execution`
4. **Preserve node names** — renaming nodes breaks existing connections
5. **Update positions** — adjust node `position` coordinates for clean layout
6. **One change at a time** — for complex edits, make incremental changes and test each
