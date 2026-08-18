---
name: project-setup
description: Agile-ready project setup — states, labels, work item types, properties, and feature configuration for Agile workflows. Use when setting up a new project or configuring an existing project for Agile.
---

# Project Setup

This skill covers configuring a Plane project with Agile-optimized states, labels, work item types, and features for startup teams.

## Tool Name Resolution

Tools below are referenced by their **action name** only (e.g., `create_project`). Resolve the real tool names for your current Plane MCP server or connector through the `connector-bootstrap` skill. Match by action suffix — never assume a prefix.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_projects` | Check existing projects |
| `create_project` | Create new project |
| `update_project` | Update project settings |
| `update_project_features` | Enable/disable project features |
| `get_project_features` | Check current feature flags |
| `list_states` | List existing states |
| `create_state` | Create workflow states |
| `update_state` | Modify states |
| `list_labels` | List existing labels |
| `create_label` | Create categorization labels |
| `list_work_item_types` | Check existing types |
| `create_work_item_type` | Create work item types |
| `create_work_item_property` | Add custom properties to types |

## Full Project Setup Workflow

### Step 1: Create or Select Project

```
Option A — New project:
create_project({
  name: "My Startup App",
  identifier: "MSA",
  description: "Main product development project"
})

Option B — Existing project:
list_projects()
→ Find project by name, get project_id
```

### Step 2: Enable Agile Features

```
update_project_features({
  project_id: "<id>",
  cycles: true,      // Sprints
  modules: true,     // Feature grouping
  epics: true,       // Large feature tracking
  pages: true,       // Documentation, retro notes
  views: true,       // Custom filtered views
  intakes: true,     // Bug/feature request intake
  work_item_types: true  // Story, Task, Bug distinction
})
```

### Step 3: Create Workflow States

Recommended state workflow for startups:

```
create_state({ project_id, name: "Backlog",     color: "#a3a3a3", group: "backlog",    sequence: 1 })
create_state({ project_id, name: "Todo",         color: "#3b82f6", group: "unstarted",  sequence: 2 })
create_state({ project_id, name: "In Progress",  color: "#f59e0b", group: "started",    sequence: 3 })
create_state({ project_id, name: "In Review",    color: "#8b5cf6", group: "started",    sequence: 4 })
create_state({ project_id, name: "Done",         color: "#22c55e", group: "completed",  sequence: 5 })
create_state({ project_id, name: "Cancelled",    color: "#ef4444", group: "cancelled",  sequence: 6 })
```

**State group mapping:**
| Group | Purpose | States |
|-------|---------|--------|
| `backlog` | Unrefined items | Backlog |
| `unstarted` | Refined, ready for sprint | Todo |
| `started` | Active work | In Progress, In Review |
| `completed` | Done | Done |
| `cancelled` | Dropped | Cancelled |

### Step 4: Create Labels

**Type labels:**
```
create_label({ project_id, name: "bug",         color: "#ef4444" })  // Red
create_label({ project_id, name: "feature",     color: "#3b82f6" })  // Blue
create_label({ project_id, name: "tech-debt",   color: "#8b5cf6" })  // Purple
create_label({ project_id, name: "spike",       color: "#06b6d4" })  // Cyan
create_label({ project_id, name: "chore",       color: "#6b7280" })  // Gray
```

**Status labels:**
```
create_label({ project_id, name: "ready",            color: "#22c55e" })  // Green
create_label({ project_id, name: "needs-refinement",  color: "#f59e0b" })  // Amber
create_label({ project_id, name: "blocked",           color: "#ef4444" })  // Red
create_label({ project_id, name: "retro-action",      color: "#ec4899" })  // Pink
create_label({ project_id, name: "quick-win",         color: "#10b981" })  // Emerald
```

**MoSCoW labels (optional, if using labels instead of priority field):**
```
create_label({ project_id, name: "must-have",    color: "#dc2626" })  // Red
create_label({ project_id, name: "should-have",  color: "#f97316" })  // Orange
create_label({ project_id, name: "could-have",   color: "#eab308" })  // Yellow
create_label({ project_id, name: "wont-have",    color: "#9ca3af" })  // Gray
```

### Step 5: Create Work Item Types

```
create_work_item_type({
  project_id: "<id>",
  name: "Story",
  description: "User-facing feature delivering business value"
})

create_work_item_type({
  project_id: "<id>",
  name: "Task",
  description: "Technical work item supporting a story"
})

create_work_item_type({
  project_id: "<id>",
  name: "Bug",
  description: "Defect or unexpected behavior to fix"
})

create_work_item_type({
  project_id: "<id>",
  name: "Spike",
  description: "Time-boxed research to reduce uncertainty"
})
```

### Step 6: Create Custom Properties (Optional)

For WSJF scoring or additional metadata:

```
create_work_item_property({
  project_id: "<id>",
  type_id: "<story_type_id>",
  display_name: "Business Value",
  property_type: "DECIMAL",
  description: "Business value score for WSJF (1-10)"
})

create_work_item_property({
  project_id: "<id>",
  type_id: "<story_type_id>",
  display_name: "Risk Level",
  property_type: "OPTION",
  options: [
    { "name": "Low" },
    { "name": "Medium" },
    { "name": "High" },
    { "name": "Critical" }
  ]
})
```

## Setup Templates

### Lean Template (1-3 person team)

Minimal setup for maximum speed:

```
States: Backlog → Todo → In Progress → Done
Labels: bug, feature, tech-debt, ready, blocked
Types:  Story, Bug (that's it — keep it simple)
Features: cycles + pages
```

### Standard Template (4-7 person team)

Full Agile setup:

```
States: Backlog → Todo → In Progress → In Review → Done → Cancelled
Labels: All type labels + status labels + MoSCoW labels
Types:  Story, Task, Bug, Spike
Features: cycles + modules + epics + pages + views
Properties: Business Value, Risk Level
```

## Verification Checklist

After setup, verify:

```
1. list_states({ project_id })
   → Should show 4-6 states in correct groups

2. list_labels({ project_id })
   → Should show all created labels

3. list_work_item_types({ project_id })
   → Should show Story, Task, Bug (at minimum)

4. get_project_features({ project_id })
   → cycles: true, modules: true (at minimum)
```

## Best Practices

1. **Start lean** — you can always add more states/labels later
2. **Don't over-configure** — 6 states max, team should memorize the workflow
3. **Consistent colors** — red = danger/bug, green = done/ready, blue = feature
4. **Enable cycles first** — sprints are the foundation of Agile
5. **Add types only if needed** — for 1-3 person teams, priority + labels is enough
