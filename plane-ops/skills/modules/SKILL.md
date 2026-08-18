---
name: modules
description: Plane modules — feature and workstream grouping that cuts across sprints. Use when the user wants to group related work items by feature area, track progress of a larger feature over multiple sprints, create or manage modules, or ask about workstream progress. Modules complement cycles (time-boxed) by organizing work around outcomes (scope-boxed).
---

# Modules

Modules in Plane group work items by **scope** (feature, workstream, or outcome), in contrast to cycles which group by **time** (sprints). A single module can span multiple sprints and contain items owned by different people.

## Tool Name Resolution

Resolve real tool names via the `connector-bootstrap` skill. Match by action suffix.

## Available Actions

| Action | Purpose |
|--------|---------|
| `list_modules` | List active modules in a project |
| `list_archived_modules` | List archived (completed) modules |
| `create_module` | Create a new module |
| `retrieve_module` | Get a module by UUID |
| `update_module` | Update module details (name, lead, target date) |
| `delete_module` | Delete a module |
| `archive_module` / `unarchive_module` | Archive lifecycle |
| `list_module_work_items` | Get work items in a module |
| `add_work_items_to_module` | Add items (bulk) |
| `remove_work_item_from_module` | Remove an item |

## When to Use a Module vs a Cycle

| Use a module when | Use a cycle when |
|-------------------|------------------|
| Grouping work around a feature or outcome | Grouping work into a time-boxed sprint |
| Work spans multiple sprints | Work is committed for the next 1–2 weeks |
| Tracking a workstream (mobile, billing, onboarding) | Tracking team commitment |
| Reporting progress to stakeholders by feature | Reporting progress to the team by sprint |

An item can live in **both** a module and a cycle simultaneously.

## Creating a Module

```
1. connector-bootstrap        → resolve tools and instance
2. list_projects              → pick project_id
3. get_project_members        → pick lead (UUID)
4. create_module({
     project_id,
     name: "Billing v2",
     description: "Revamp billing: Stripe migration, invoices, proration",
     lead: "<user_uuid>",
     members: ["<uuid>", "<uuid>"],
     start_date: "YYYY-MM-DD",
     target_date: "YYYY-MM-DD",
     status: "planned" | "in-progress" | "paused" | "completed" | "cancelled"
   })
```

## Adding Work Items to a Module

```
add_work_items_to_module({
  project_id,
  module_id,
  issue_ids: ["<uuid>", "<uuid>", ...]
})
```

Items can come from any state — backlog, in-progress, or done. Adding a done item is valid; it counts toward module completion.

## Module Progress Reporting

```
1. list_module_work_items({ project_id, module_id })
2. Group items by state group: backlog | unstarted | started | completed | cancelled
3. Calculate:
   - total_items, total_points
   - completed_items, completed_points
   - completion_rate = completed_points / total_points
4. Surface blockers: list_work_item_relations per item, filter active blocked_by
```

Reporting table:

```
| Module | Status | Lead | Completion | Blocked | Target |
|--------|--------|------|-----------|---------|--------|
| Billing v2 | in-progress | @alice | 34/52 (65%) | 2 | Apr 30 |
```

## Module Lifecycle

1. **Planned** — scope defined, lead assigned, items drafted
2. **In Progress** — first items moved to "started"
3. **Paused** — explicitly deprioritized; lead re-assigns team
4. **Completed** — all items Done or explicitly dropped
5. **Cancelled** — abandoned; archive after retrospective

Always archive completed/cancelled modules to keep the active list clean:

```
archive_module({ project_id, module_id })
```

**Caveat:** many Plane deployments reject `archive_module` on **active** modules (HTTP 400). Set `status: "completed"` or `"cancelled"` via `update_module` first, then archive. To remove an active module entirely, use `delete_module` directly.

**Caveat:** `update_module` on many deployments returns a response object with mostly `null` fields even when the update succeeded. Do not rely on the response — refetch via `retrieve_module` to get the post-update state.

## Best Practices

1. One lead per module — accountability is clearer.
2. Scope modules to 4–12 weeks of work. Smaller → use a cycle. Larger → use an epic or initiative.
3. Review module progress at each sprint review, not just at module end.
4. If a module stalls for 2 sprints, pause it explicitly — do not leave it "in progress".
5. Link the module's tracking page (see `pages-publishing`) in every work item description.
