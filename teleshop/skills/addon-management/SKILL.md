---
name: addon-management
description: Addon and workflow management — listing, toggling, executing, scheduling, and configuring variables. Use when managing store addons, running automation workflows, or configuring addon schedules.
---

# Addon Management

This skill covers addon/workflow operations — listing available addons, enabling/disabling them, configuring variables and schedules, and executing addon workflows.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_workflows` | List all available addons and their status |
| `toggle_workflow` | Enable or disable an addon |
| `get_workflow_variables` | Get addon configuration variables |
| `set_workflow_variables` | Update addon configuration variables |
| `execute_workflow` | Manually run an addon workflow |
| `get_workflow_schedule` | Get addon execution schedule |
| `set_workflow_schedule` | Set addon execution schedule |
| `clear_workflow_schedule` | Remove addon schedule (stop auto-execution) |

## Listing Addons

```
Tool: list_workflows
Input: {}

Returns list of all addons with their IDs, names, descriptions,
enabled/disabled status, and last execution time.
```

## Enabling/Disabling Addons

```
Tool: toggle_workflow
Input: {"id": "addon-123"}

Toggles the addon between enabled and disabled state.
```

## Addon Variables (Configuration)

### Get Current Configuration
```
Tool: get_workflow_variables
Input: {"id": "addon-123"}

Returns all configurable variables for this addon with
their current values, types, and descriptions.
```

### Update Configuration
```
Tool: set_workflow_variables
Input: {
  "id": "addon-123",
  "variables": {
    "sync_interval": "30",
    "source_url": "https://example.com/feed.xml",
    "auto_publish": "true"
  }
}
```

## Executing Addons

### Manual Execution
```
Tool: execute_workflow
Input: {"id": "addon-123"}

Triggers immediate execution of the addon workflow.
Useful for testing or one-time runs.
```

## Schedule Management

### Get Current Schedule
```
Tool: get_workflow_schedule
Input: {"id": "addon-123"}

Returns the current execution schedule (cron expression or interval).
```

### Set Schedule
```
Tool: set_workflow_schedule
Input: {
  "id": "addon-123",
  "schedule": "0 */6 * * *"
}

Sets the addon to run on a schedule (e.g., every 6 hours).
```

### Remove Schedule
```
Tool: clear_workflow_schedule
Input: {"id": "addon-123"}

Stops automatic execution. Addon can still be run manually.
```

## Common Workflows

### Discover and Configure Addons
```
1. list_workflows() -> See all available addons
2. get_workflow_variables(id) -> Check configuration options
3. set_workflow_variables(id, variables) -> Configure
4. toggle_workflow(id) -> Enable the addon
5. execute_workflow(id) -> Test run
```

### Set Up Scheduled Addon
```
1. list_workflows() -> Find the addon
2. set_workflow_variables(id, variables) -> Configure
3. set_workflow_schedule(id, schedule="0 0 * * *") -> Run daily at midnight
4. toggle_workflow(id) -> Enable
```

### Troubleshoot Addon
```
1. list_workflows() -> Check addon status
2. get_workflow_variables(id) -> Verify configuration
3. get_workflow_schedule(id) -> Check schedule
4. execute_workflow(id) -> Manual test run
5. Review results and adjust variables if needed
```

### Pause Addon Temporarily
```
1. toggle_workflow(id) -> Disable
2. ... (maintenance or investigation) ...
3. toggle_workflow(id) -> Re-enable
4. execute_workflow(id) -> Verify it runs correctly
```

## Best Practices

1. **List addons first** to see available options and their current state
2. **Configure variables** before enabling an addon
3. **Test with manual execution** before setting up a schedule
4. **Use toggle** to temporarily disable instead of clearing the schedule
5. **Review variables** periodically to ensure configuration is current
6. **Clear schedule** if you only need one-time runs
