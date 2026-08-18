---
name: epics-initiatives-milestones
description: Long-horizon planning in Plane — epics, initiatives, and milestones. Use when the user wants to create an epic, group epics under an initiative, track a release milestone, build a roadmap, or report progress on a long-running goal that spans multiple sprints or modules. Clarifies the difference between the three and when to use which.
---

# Epics, Initiatives, and Milestones

Long-horizon planning sits above sprints and modules. This skill covers the three Plane entities used for it and when to choose each.

## Tool Name Resolution

Resolve real tool names via the `connector-bootstrap` skill.

## The Three Hierarchies

| Entity | Scope | Typical duration | Owner | Lives in |
|--------|-------|------------------|-------|----------|
| **Epic** | A large feature or theme containing many work items | 1–3 months | Tech lead / PM | A single project |
| **Initiative** | A cross-project strategic goal containing epics and projects | 1–2 quarters | Department head / founder | Workspace |
| **Milestone** | A fixed date by which a set of work items must be done (a release, launch, or deadline) | Point in time | PM / release manager | A single project |

A work item can belong to an epic, a module, a cycle, and a milestone simultaneously.

## Available Actions

### Epics
`list_epics`, `create_epic`, `retrieve_epic`, `update_epic`, `delete_epic`

### Initiatives
`list_initiatives`, `create_initiative`, `retrieve_initiative`, `update_initiative`, `delete_initiative`

### Milestones
`list_milestones`, `create_milestone`, `retrieve_milestone`, `update_milestone`, `delete_milestone`, `add_work_items_to_milestone`, `remove_work_items_from_milestone`, `list_milestone_work_items`

## Creating an Epic

```
1. connector-bootstrap  → resolve tools
2. list_projects        → pick project_id
3. create_epic({
     project_id,
     name: "Multi-tenant support",
     description_html: "<h3>Goal</h3>…<h3>Success metrics</h3>…",
     lead: "<user_uuid>",
     start_date, target_date,
     priority
   })
```

Add child work items by setting the epic as the parent (check the exact field name in the tool schema — typically `parent` or `epic_id` on the child work item).

## Creating an Initiative

Initiatives are **workspace-level** — they do NOT take a `project_id`. Use them to express strategic bets that span several projects:

```
create_initiative({
  name: "International expansion Q3",
  description_html: "<h3>Why</h3>…<h3>Bets</h3>…<h3>Out of scope</h3>…",
  lead: "<user_uuid>",                       // may default to null
  start_date: "YYYY-MM-DD",
  end_date: "YYYY-MM-DD"                      // note: end_date, not target_date for initiatives
})
```

New initiatives are typically created in `DRAFT` state. Move them to active state separately if your instance supports it. Link epics and projects to the initiative per your instance's schema — this varies widely between Plane deployments.

## Creating a Milestone

Milestones answer the question "what must ship by this date?".

**Field name caveat:** most Plane deployments use **`title`** for the milestone name, NOT `name`. Verify the tool schema before the first call. The `description` field may or may not be supported on your instance — start minimal and add fields only after confirming they work.

```
1. create_milestone({
     project_id,
     title: "v2.0 Public Beta",               // usually "title", NOT "name"
     target_date: "YYYY-MM-DD"
   })

2. add_work_items_to_milestone({
     project_id,
     milestone_id,
     issue_ids: [...]                         // plural; see Known Limitations below
   })
```

## Reporting Progress

### Epic progress

```
1. list_work_items({ project_id, filter: parent = epic_id })
2. Group by state group; sum points
3. completion_rate = completed_points / total_points
4. Forecast: project remaining points at current velocity → target_date slippage
```

### Milestone health

```
1. list_milestone_work_items({ project_id, milestone_id })
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

Aggregate completion across all linked epics and projects. Report per-epic and overall.

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
