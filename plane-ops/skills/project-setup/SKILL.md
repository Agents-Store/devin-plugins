---
name: project-setup
description: Agile-ready project setup — states, labels, work item types, properties, and feature configuration for Agile workflows. Use when setting up a new project or configuring an existing project for Agile.
---

# Project Setup

This skill covers configuring a Plane project with Agile-optimized states, labels, work item types, and features for startup teams.

## Tool Name Resolution

Plane MCP exposes one tool per resource and the operation goes into the `action` parameter: `project(action=create, ...)`. This skill writes calls in that form. Resolve the real tool names (`mcp__<server>__<resource>`) for your current Plane connection through the `connector-bootstrap` skill - never assume a server prefix.

## Available Tools

| Call | Description |
|------|-------------|
| `project(action=list)` | Check existing projects (paginated: follow `next_cursor`) |
| `project(action=create)` | Create new project (`name` and `identifier` are required) |
| `project(action=update)` | Update project settings (timezone, default state, estimate, time tracking, ...) |
| `project(action=get_features)` | Check current feature flags |
| `project(action=update_features)` | Enable/disable project features |
| `state(action=list)` / `state(action=create)` / `state(action=update)` | List, create and modify workflow states |
| `label(action=list)` / `label(action=create)` | List and create categorization labels |
| `workitem_type(action=list)` / `workitem_type(action=resolve)` | Check existing types / get-or-create a type |
| `workitem_property(action=create)` | Add custom properties to types |
| `project_estimate(action=create\|create_points\|link)` | Estimate system (points scale) for the project |

## Full Project Setup Workflow

### Step 1: Create or Select Project

```
Option A — New project:
project(action=create,
  name="My Startup App",
  identifier="MSA",
  description="Main product development project")

Option B — Existing project:
project(action=list)
→ Find project by name, get project_id (follow next_cursor if needed)
```

### Step 2: Enable Agile Features

```
project(action=update_features,
  project_id=<id>,
  cycles=true,          // Sprints
  modules=true,         // Feature grouping
  epics=true,           // Large feature tracking
  pages=true,           // Documentation, retro notes
  views=true,           // Custom filtered views
  intakes=true,         // Bug/feature request intake
  workitem_types=true)  // Story, Task, Bug distinction
// omitted flags are left as they are; also available: parallel_cycles, project_updates, workflows
```

### Step 3: Create Workflow States

Recommended state workflow for startups:

```
state(action=create, project_id=<id>, name="Backlog", color="#a3a3a3", group="backlog", sequence=1)
state(action=create, project_id=<id>, name="Todo", color="#3b82f6", group="unstarted", sequence=2)
state(action=create, project_id=<id>, name="In Progress", color="#f59e0b", group="started", sequence=3)
state(action=create, project_id=<id>, name="In Review", color="#8b5cf6", group="started", sequence=4)
state(action=create, project_id=<id>, name="Done", color="#22c55e", group="completed", sequence=5)
state(action=create, project_id=<id>, name="Cancelled", color="#ef4444", group="cancelled", sequence=6)
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
label(action=create, project_id=<id>, name="bug", color="#ef4444")  // Red
label(action=create, project_id=<id>, name="feature", color="#3b82f6")  // Blue
label(action=create, project_id=<id>, name="tech-debt", color="#8b5cf6")  // Purple
label(action=create, project_id=<id>, name="spike", color="#06b6d4")  // Cyan
label(action=create, project_id=<id>, name="chore", color="#6b7280")  // Gray
```

**Status labels:**
```
label(action=create, project_id=<id>, name="ready", color="#22c55e")  // Green
label(action=create, project_id=<id>, name="needs-refinement", color="#f59e0b")  // Amber
label(action=create, project_id=<id>, name="blocked", color="#ef4444")  // Red
label(action=create, project_id=<id>, name="retro-action", color="#ec4899")  // Pink
label(action=create, project_id=<id>, name="quick-win", color="#10b981")  // Emerald
```

**MoSCoW labels (optional, if using labels instead of priority field):**
```
label(action=create, project_id=<id>, name="must-have", color="#dc2626")  // Red
label(action=create, project_id=<id>, name="should-have", color="#f97316")  // Orange
label(action=create, project_id=<id>, name="could-have", color="#eab308")  // Yellow
label(action=create, project_id=<id>, name="wont-have", color="#9ca3af")  // Gray
```

### Step 5: Create Work Item Types

```
workitem_type(action=resolve, project_id=<id>, name="Story")   // User-facing feature delivering business value
workitem_type(action=resolve, project_id=<id>, name="Task")    // Technical work item supporting a story
workitem_type(action=resolve, project_id=<id>, name="Bug")     // Defect or unexpected behavior to fix
workitem_type(action=resolve, project_id=<id>, name="Spike")   // Time-boxed research to reduce uncertainty
```

`resolve` finds or creates the named type for the project (exact, case-sensitive match) and never duplicates it; where the workspace owns the type vocabulary it imports the workspace type instead, which is the only valid path there. Use `workitem_type(action=create, name, description, project_id)` only when you need to set a `description` and the project owns its types. The returned `id` is the `type_id` for `workitem(action=create)` and the `workitem_type_id` for properties.

### Step 6: Create Custom Properties (Optional)

For WSJF scoring or additional metadata:

```
workitem_property(action=create,
  project_id=<id>,
  workitem_type_id=<story_type_id>,
  display_name="Business Value",
  property_type="DECIMAL",
  description="Business value score for WSJF (1-10)")

workitem_property(action=create,
  project_id=<id>,
  workitem_type_id=<story_type_id>,
  display_name="Risk Level",
  property_type="OPTION",
  options=[{"name": "Low"}, {"name": "Medium"}, {"name": "High"}, {"name": "Critical"}])
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
1. state(action=list, project_id=<id>)
   → Should show 4-6 states in correct groups (Plane keeps its own Triage state, not listed)

2. label(action=list, project_id=<id>)
   → Should show all created labels

3. workitem_type(action=list, project_id=<id>)
   → Should show Story, Task, Bug (at minimum)

4. project(action=get_features, project_id=<id>)
   → cycles: true, modules: true (at minimum)
```

## Best Practices

1. **Start lean** — you can always add more states/labels later
2. **Don't over-configure** — 6 states max, team should memorize the workflow
3. **Consistent colors** — red = danger/bug, green = done/ready, blue = feature
4. **Enable cycles first** — sprints are the foundation of Agile
5. **Add types only if needed** — for 1-3 person teams, priority + labels is enough
