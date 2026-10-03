---
name: epics-initiatives-milestones
description: Long-horizon planning in Plane — epics, initiatives, and milestones. Use when the user wants to create an epic, group epics under an initiative, track a release milestone, build a roadmap, or report progress on a long-running goal that spans multiple sprints or modules. Clarifies the difference between the three and when to use which.
---

# Epics, Initiatives, and Milestones

Long-horizon planning sits above sprints and modules. This skill covers the three Plane entities used for it and when to choose each.

## Tool Name Resolution

Plane MCP exposes one tool per resource and the operation goes into the `action` parameter: `initiative(action=create, ...)`. This skill writes calls in that form. Resolve the real tool names (`mcp__<server>__<resource>`) through the `connector-bootstrap` skill - never assume a server prefix.

## The Three Hierarchies

| Entity | Scope | Typical duration | Owner | Lives in |
|--------|-------|------------------|-------|----------|
| **Epic** | A large feature or theme containing many work items | 1–3 months | Tech lead / PM | A single project |
| **Initiative** | A cross-project strategic goal containing epics and projects | 1–2 quarters | Department head / founder | Workspace |
| **Milestone** | A fixed date by which a set of work items must be done (a release, launch, or deadline) | Point in time | PM / release manager | A single project |

A work item can belong to an epic, a module, a cycle, and a milestone simultaneously.

## Available Calls

### Epics - there are no epic tools

An epic is a **work item whose type is named "Epic"**. All epic operations are `workitem` calls plus one lookup of the type id:

| Operation | Call |
|-----------|------|
| Find the Epic type | `workitem_type(action=resolve, project_id, name="Epic")` - `id` is the `type_id`; finds or creates the type, never duplicates |
| Create | `workitem(action=create, project_id, name, type_id=<epic-type-id>, ...)` |
| List epics | `workitem(action=list, project_id, pql='type = "<epic-type-id>"')` |
| Read / update / delete | `workitem(action=retrieve\|update\|delete, project_id, workitem_id)` |
| Children | the `parent` field of the child work item |
| List children | `workitem(action=list, project_id, pql='childOf("<epic identifier or uuid>")')` |

### Initiatives
`initiative(action=list|retrieve|create|update|delete)`, `list_projects`, `add_projects`, `remove_projects`, `list_workitems`, `manage_workitems`

### Milestones
`milestone(action=list|retrieve|create|update|delete)`, `list_workitems`, `manage_workitems`

## Creating an Epic

```
1. connector-bootstrap  → resolve tools
2. project(action=list) → pick project_id
3. workitem_type(action=resolve, project_id=<id>, name="Epic")
   → the returned id is the epic type_id
4. workitem(action=create,
     project_id=<id>,
     name="Multi-tenant support",
     type_id=<epic-type-id>,
     description_html="<h3>Goal</h3>…<h3>Success metrics</h3>…",
     assignees=[<lead_user_uuid>],
     start_date="YYYY-MM-DD", target_date="YYYY-MM-DD",
     priority="high")
```

Add child work items by setting the epic as the parent: `workitem(action=create, ..., parent=<epic_workitem_id>)`, or `workitem(action=update, ..., parent=<epic_workitem_id>)` for an existing item. A parent is set on the child, never on the epic.

Epics need the project's `epics` and `workitem_types` features: check with `project(action=get_features, project_id)` and, with the user's consent, enable with `project(action=update_features, project_id, epics=true, workitem_types=true)`. If a call is refused because the plan does not include work item types, say so; the epic then has to be an ordinary work item with a parent-child tree.

`isEpic()` is also a PQL predicate ("issue type is epic" per `get_pql_reference`). Whether a type created or found by `workitem_type(action=resolve, name="Epic")` counts as an epic for it depends on how Plane flags epic types - confirm on your instance; the `type = "<epic-type-id>"` filter does not depend on that.

## Creating an Initiative

Initiatives are **workspace-level** - they do NOT take a `project_id`. Use them to express strategic bets that span several projects:

```
initiative(action=create,
  name="International expansion Q3",
  description_html="<h3>Why</h3>…<h3>Bets</h3>…<h3>Out of scope</h3>…",
  lead=<user_uuid>,
  start_date="YYYY-MM-DD",
  end_date="YYYY-MM-DD",              // end_date, not target_date, for initiatives
  state="DRAFT")                      // DRAFT | PLANNED | ACTIVE | COMPLETED | CLOSED
```

`create` takes no project list. Link projects and epics afterwards, then read the links back (both calls return nothing):

```
initiative(action=add_projects, initiative_id=<id>, project_ids=[<project_uuid>, ...])
initiative(action=list_projects, initiative_id=<id>)

initiative(action=manage_workitems, initiative_id=<id>, add_ids=[<epic work item id>, ...])
initiative(action=list_workitems, initiative_id=<id>)
```

A work item of any type can be linked to an initiative, so link the epic work items. The tool needs the workspace's native initiatives feature: check `workspace(action=get_features)` and, with the user's consent, enable it with `workspace(action=update_features, initiatives=true)`. While it is off, `initiative` tells you that initiatives are stored as "Initiative" work items (`workitem_type(action=resolve, name="Initiative")`), and linking projects or work items is not possible.

## Creating a Milestone

Milestones answer the question "what must ship by this date?". A milestone has a **`title`** (not `name`) and a `target_date`:

```
1. milestone(action=create,
     project_id=<id>,
     title="v2.0 Public Beta",
     target_date="YYYY-MM-DD")

2. milestone(action=manage_workitems,
     project_id=<id>,
     milestone_id=<milestone_id>,
     add_ids=[<work item uuid>, ...])      // returns nothing

3. milestone(action=list_workitems, project_id=<id>, milestone_id=<milestone_id>)
   → read the membership back
```

## Reporting Progress

### Epic progress

```
1. workitem(action=count, project_id=<id>,
            pql='childOf("<epic identifier>")', group_by=state__group)
   → child counts per state group in one call
2. workitem(action=list, project_id=<id>, pql='childOf("<epic identifier>")', fields="id,name,point,estimate_point,state")
   → sum points by state group (counts have no points)
3. completion_rate = completed_points / total_points
4. Forecast: project remaining points at current velocity → target_date slippage
```

### Milestone health

```
1. workitem(action=count, project_id=<id>,
            pql='milestone = "<milestone_id>"', group_by=state__group)
   milestone(action=list_workitems, project_id=<id>, milestone_id=<milestone_id>)
2. Days to target_date
3. Remaining points
4. Velocity-based ETA: remaining_points / weekly_velocity
5. Risk: Red / Yellow / Green based on ETA vs target_date buffer
```

Risk thresholds:

- **Green**: ETA < target_date with ≥ 20% buffer
- **Yellow**: ETA ≤ target_date with < 20% buffer
- **Red**: ETA > target_date

### Initiative rollup

Aggregate completion across all linked epics and projects: `initiative(action=list_workitems)` gives the epics, `initiative(action=list_projects)` the projects; then count each epic's children as above. Report per-epic and overall.

## When to Use Which

- Shipping a named release? → **Milestone**
- A feature area owned by one tech lead? → **Epic**
- A company-wide strategic bet? → **Initiative**
- Tracking a workstream that has no fixed date? → **Module** (see `modules` skill)
- Time-boxed iteration? → **Cycle** (see `sprint-planning` skill)

## Best Practices

1. Do not create an epic for work smaller than a month — use a module or just work items.
2. Every milestone must have an explicit owner and a non-movable target date. If it moves, re-plan, don't silently slip.
3. Review epic/initiative progress monthly, not weekly — these are long horizons.
4. Link a tracking page (see `pages-publishing`) to every epic and initiative for stakeholder updates.
5. Always decompose an epic into sprintable work items (≤ 8 points each) before planning the first sprint that touches it.
