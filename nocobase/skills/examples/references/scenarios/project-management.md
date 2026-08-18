# Scenario: Project Management Application

Project management app with tasks, assignments, timelines, and kanban boards.

## Entity Model

```
projects ──< milestones
    │
    └──< tasks ──< task_comments
         │
    tasks >──< team_members (via task_assignments)
```

## Collections

### projects
| Field | Type | Config |
|-------|------|--------|
| name | string | required, primary display |
| description | richText | |
| status | singleSelect | Planning, Active, On Hold, Completed, Archived |
| priority | singleSelect | Low, Medium, High, Critical |
| startDate | date | |
| endDate | date | |
| budget | decimal | |
| owner | belongsTo | → users |
| milestones | hasMany | → milestones |
| tasks | hasMany | → tasks |

### milestones
| Field | Type | Config |
|-------|------|--------|
| title | string | required, primary display |
| dueDate | date | |
| status | singleSelect | Pending, In Progress, Completed |
| project | belongsTo | → projects |
| tasks | hasMany | → tasks |

### tasks
| Field | Type | Config |
|-------|------|--------|
| title | string | required, primary display |
| description | richText | |
| status | singleSelect | To Do, In Progress, Review, Done |
| priority | singleSelect | Low, Medium, High, Critical |
| dueDate | date | |
| estimatedHours | float | |
| actualHours | float | |
| project | belongsTo | → projects |
| milestone | belongsTo | → milestones |
| parent | belongsTo | → tasks (self, tree structure) |
| children | hasMany | → tasks (subtasks) |
| assignees | belongsToMany | → users (via task_assignments) |
| comments | hasMany | → task_comments |
| sequence | sequence | `TASK-{0000}` |

### task_assignments (through table)
| Field | Type | Config |
|-------|------|--------|
| task | belongsTo | → tasks |
| user | belongsTo | → users |
| role | singleSelect | Lead, Contributor, Reviewer |
| assignedAt | datetime | |

### task_comments
| Field | Type | Config |
|-------|------|--------|
| content | richText | required |
| task | belongsTo | → tasks |
| author | belongsTo | → users |

## Workflows

### Task Assigned → Notify
```
Trigger: task_assignments.afterCreate
1. Query: Get task and assignee details
2. Request: Send email/Slack notification
   "You've been assigned to task {{task.title}} in project {{task.project.name}}"
```

### Task Overdue → Alert
```
Trigger: Schedule (daily at 9:00 AM)
1. Query: Tasks where dueDate < today AND status NOT IN (Done)
2. Loop: For each overdue task
   2a. Query: Get assignees
   2b. Request: Send overdue notification
```

### All Tasks Done → Complete Milestone
```
Trigger: tasks.afterUpdate
Condition: status changed to "Done"
1. Query: Count tasks in same milestone where status != "Done"
2. Condition: remaining == 0?
   Yes → Update: milestone.status = "Completed"
   No → (skip)
```

### Project Status Auto-Update
```
Trigger: tasks.afterUpdate
1. Query: All tasks in project
2. Calculation:
   - done_count / total_count
   - If all done → "Completed"
   - If any in_progress → "Active"
   - Else → current status
3. Update: project.status = calculated_status
```

## UI Design

### Menu Structure
```
Projects
  ├── Dashboard (Charts)
  ├── All Projects (Table)
  ├── My Tasks (Filtered Table)
  ├── Calendar (Calendar block)
  └── Team (Table)
```

### Project Detail Page
```
Layout: Project header + Tabs

Tab 1: Task Board (Kanban)
  - Group by: status
  - Cards: title, priority, assignees, dueDate
  - Drag-drop status changes

Tab 2: Task List (Table)
  - Tree display (parent/child tasks)
  - Columns: title, status, priority, assignees, dueDate
  - Filters: status, priority, assignee
  - Inline edit: status, priority

Tab 3: Timeline (Gantt)
  - Start: startDate or createdAt
  - End: dueDate
  - Group by: milestone

Tab 4: Milestones (Table)
  - Columns: title, dueDate, status, task count
```

### My Tasks Page
```
Table block (filtered: assignees includes current user):
  - Columns: title, project.name, status, priority, dueDate
  - Default sort: dueDate ASC
  - Quick filters: status, priority
  - Group by: project (optional)
```

### Dashboard
```
Blocks:
  - Chart: Tasks by Status (pie chart)
  - Chart: Tasks Created vs Completed (line, by week)
  - Counter: Overdue Tasks (red)
  - Counter: Active Projects
  - Table: My Upcoming Tasks (top 10, sorted by dueDate)
```
