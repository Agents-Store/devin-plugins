# Scenario: Complete Database Setup

End-to-end database setup in NocoDB from scratch — creating reference tables, main tables, relations, views, and importing initial data.

## Goal

Build a project management database with:
- **Projects** — main projects
- **Tasks** — tasks within projects
- **Team Members** — people assigned to tasks
- **Statuses** — reference table for task statuses

## Step-by-Step

### 1. Create Reference Table: Statuses

Not needed as a separate table — use SingleSelect on Tasks instead. This keeps things simple.

### 2. Create Team Members Table

```
create_table({
  name: "Team Members",
  columns: [
    { name: "Name", type: "SingleLineText" },
    { name: "Email", type: "Email" },
    { name: "Role", type: "SingleSelect", options: ["Developer", "Designer", "PM", "QA"] },
    { name: "Active", type: "Checkbox" }
  ]
})
→ tbl_members
```

### 3. Create Projects Table

```
create_table({
  name: "Projects",
  columns: [
    { name: "Name", type: "SingleLineText" },
    { name: "Description", type: "LongText" },
    { name: "Status", type: "SingleSelect", options: ["Planning", "Active", "On Hold", "Completed"] },
    { name: "StartDate", type: "Date" },
    { name: "DueDate", type: "Date" },
    { name: "Budget", type: "Currency" }
  ]
})
→ tbl_projects
```

### 4. Create Tasks Table

```
create_table({
  name: "Tasks",
  columns: [
    { name: "Title", type: "SingleLineText" },
    { name: "Description", type: "LongText" },
    { name: "Status", type: "SingleSelect", options: ["To Do", "In Progress", "Review", "Done"] },
    { name: "Priority", type: "SingleSelect", options: ["Low", "Medium", "High", "Critical"] },
    { name: "DueDate", type: "Date" },
    { name: "EstimatedHours", type: "Number" }
  ]
})
→ tbl_tasks
```

### 5. Add Relations

```
// Task → Project (many tasks belong to one project)
create_column({
  table_id: tbl_tasks,
  name: "Project",
  type: "LinkToAnotherRecord",
  linked_table_id: tbl_projects,
  relation_type: "hm"
})

// Task → Assignee (many tasks assigned to one member)
create_column({
  table_id: tbl_tasks,
  name: "Assignee",
  type: "LinkToAnotherRecord",
  linked_table_id: tbl_members,
  relation_type: "hm"
})
```

### 6. Add Lookups and Rollups

```
// In Projects table: count of tasks
list_columns(tbl_projects) → find "Tasks" reverse link column ID
create_column({
  table_id: tbl_projects,
  name: "Task Count",
  type: "Rollup",
  relation_column_id: <tasks_link>,
  rollup_column_id: <task_id>,
  rollup_function: "count"
})

// In Tasks table: lookup project name
create_column({
  table_id: tbl_tasks,
  name: "Project Name",
  type: "Lookup",
  relation_column_id: <project_link>,
  lookup_column_id: <project_name>
})

// In Tasks table: lookup assignee email
create_column({
  table_id: tbl_tasks,
  name: "Assignee Email",
  type: "Lookup",
  relation_column_id: <assignee_link>,
  lookup_column_id: <member_email>
})
```

### 7. Add Formula Fields

```
// In Tasks: days until due
create_column({
  table_id: tbl_tasks,
  name: "Days Until Due",
  type: "Formula",
  formula: "DATETIME_DIFF({DueDate}, NOW(), 'days')"
})

// In Projects: progress formula (requires task count and done count)
// This would need a Rollup for done tasks first
```

### 8. Create Views

```
// Tasks: Kanban board
create_view({ table_id: tbl_tasks, title: "Task Board", type: "Kanban", group_by: "Status" })

// Tasks: My tasks (filtered grid)
create_view({ table_id: tbl_tasks, title: "High Priority", type: "Grid" })
update_view({ filters: [{ field: "Priority", op: "eq", value: "High" }] })

// Projects: Overview grid
create_view({ table_id: tbl_projects, title: "All Projects", type: "Grid" })

// Tasks: Calendar view
create_view({ table_id: tbl_tasks, title: "Timeline", type: "Calendar", date_field: "DueDate" })
```

### 9. Import Sample Data

```
bulk_create_records(tbl_members, [
  { Name: "Alice Chen", Email: "alice@team.com", Role: "Developer", Active: true },
  { Name: "Bob Kim", Email: "bob@team.com", Role: "Designer", Active: true },
  { Name: "Carol Lopez", Email: "carol@team.com", Role: "PM", Active: true }
])

bulk_create_records(tbl_projects, [
  { Name: "Website Redesign", Status: "Active", StartDate: "2024-01-15", Budget: 50000 },
  { Name: "Mobile App", Status: "Planning", StartDate: "2024-03-01", Budget: 80000 }
])
```

## Result

A fully functional project management database with:
- 3 interconnected tables
- Relations, lookups, and rollups
- Kanban board, calendar, and filtered views
- Sample data for testing
