---
name: crm-boards-tasks
description: CRM Kanban boards and task management — create boards, manage columns, create and track tasks. Use when organizing work, managing projects, or tracking task completion.
---

# CRM Boards & Tasks

This skill covers Kanban board setup and task management for project organization.

## Available Tools

| Tool | Description |
|------|-------------|
| `crm_boards_list` | List all Kanban boards |
| `crm_boards_show` | Get board details |
| `crm_boards_create` | Create a new board |
| `crm_boards_update` | Update board settings |
| `crm_boards_steps_create` | Add a column to a board |
| `crm_boards_steps_update` | Update a board column |
| `crm_tasks_list` | List tasks with filters |
| `crm_tasks_show` | Get task details |
| `crm_tasks_create` | Create a new task |
| `crm_tasks_update` | Update task fields |
| `crm_tasks_comments_create` | Add comment to a task |

## Board Management

### List Boards
```
Tool: crm_boards_list
Input: {}

Returns all Kanban boards with IDs and names.
```

### Create Board
```
Tool: crm_boards_create
Input: {"name": "Marketing Tasks"}

Returns new board ID.
```

### Get Board Details
```
Tool: crm_boards_show
Input: {"id": "<board-id>"}

Returns board with columns (steps) and configuration.
```

### Update Board
```
Tool: crm_boards_update
Input: {"id": "<board-id>", "name": "Q1 Marketing Tasks"}
```

### Add Board Column
```
Tool: crm_boards_steps_create
Input: {"board_id": "<board-id>", "name": "In Progress", "position": 2}
```

### Update Board Column
```
Tool: crm_boards_steps_update
Input: {"id": "<step-id>", "name": "Review", "position": 3}
```

## Task Management

### List Tasks
```
Tool: crm_tasks_list
Input: {"limit": 50, "offset": 0}

Returns tasks with name, status, assignee, due date.
```

### Create Task
```
Tool: crm_tasks_create
Input: {
  "name": "Prepare Q1 report",
  "board_id": "<board-id>",
  "step_id": "<step-id>",
  "due_date": "2026-03-15"
}

Returns new task ID.
```

### Get Task Details
```
Tool: crm_tasks_show
Input: {"id": "<task-id>"}

Returns full task record with description, assignee, dates, and custom fields.
```

### Update Task
```
Tool: crm_tasks_update
Input: {"id": "<task-id>", "name": "Prepare Q1 report (updated)", "step_id": "<new-step-id>"}

Use step_id to move task between board columns.
```

### Add Comment to Task
```
Tool: crm_tasks_comments_create
Input: {"id": "<task-id>", "text": "Draft completed, ready for review."}
```

## Common Workflows

### Set Up Project Board
```
1. crm_boards_create(name="Project X") -> Get board ID
2. crm_boards_steps_create(board_id, name="Backlog", position=1)
3. crm_boards_steps_create(board_id, name="In Progress", position=2)
4. crm_boards_steps_create(board_id, name="Review", position=3)
5. crm_boards_steps_create(board_id, name="Done", position=4)
```

### Create and Track Tasks
```
1. crm_tasks_create(name, board_id, step_id, due_date) -> Create task
2. crm_tasks_update(id, step_id=next_step) -> Move through columns
3. crm_tasks_comments_create(id, text) -> Document progress
```

### Review Task Board
```
1. crm_boards_list() -> Find board
2. crm_boards_show(board_id) -> Get columns
3. crm_tasks_list() -> List all tasks, group by step
```

## Best Practices

1. **Create boards with clear columns** matching your workflow stages
2. **Set due dates** on tasks for deadline tracking
3. **Move tasks** between columns to reflect actual status
4. **Add comments** for status updates and handoff notes
5. **Use separate boards** for different teams or projects
