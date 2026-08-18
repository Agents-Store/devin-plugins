---
name: task-decomposition
description: Task decomposition — INVEST criteria, vertical slicing, epic-to-subtask breakdown, story splitting patterns. Use when breaking down epics, stories, or large work items into smaller pieces.
---

# Task Decomposition

This skill covers breaking down large work items into smaller, actionable pieces using Agile best practices — INVEST criteria, vertical slicing, and story splitting patterns.

## Tool Name Resolution

Tools below are referenced by their **action name** only (e.g., `create_work_item`). Resolve the real tool names for your current Plane MCP server or connector through the `connector-bootstrap` skill. Match by action suffix — never assume a prefix.

## Available Tools

| Tool | Description |
|------|-------------|
| `retrieve_work_item` | Get work item details by UUID |
| `retrieve_work_item_by_identifier` | Get work item by project identifier + number (e.g., MP-1) |
| `create_work_item` | Create child work item (with `parent` field for hierarchy) |
| `update_work_item` | Update work item fields |
| `create_epic` | Create an epic for grouping stories |
| `list_epics` | List existing epics |
| `list_work_item_relations` | Check dependencies and relations |
| `create_work_item_relation` | Create blocking/relates_to relations |
| `list_labels` | Get available labels |
| `create_label` | Create labels like "needs-refinement" |

## Decomposition Hierarchy

```
Initiative (optional, workspace-level)
  └── Epic (large feature, spans multiple sprints)
        └── Story (user-facing value, completable in 1 sprint)
              └── Task (technical work item, 1-3 days)
                    └── Subtask (small unit of work, < 1 day)
```

### Creating the Hierarchy in Plane

**Epic → Stories:**
```
create_epic({
  project_id: "<id>",
  name: "User Authentication",
  description_html: "<p>Complete auth system with signup, login, and password reset</p>",
  priority: "high"
})
→ epic_id

create_work_item({
  project_id: "<id>",
  name: "User can sign up with email",
  parent: "<epic_id>",
  description_html: "<p>As a new user, I want to sign up with email...</p>",
  point: 5
})
```

**Story → Tasks:**
```
create_work_item({
  project_id: "<id>",
  name: "Implement signup API endpoint",
  parent: "<story_id>",
  point: 3
})
```

## INVEST Criteria

Every user story should meet ALL six INVEST criteria:

| Criterion | What It Means | Plane Validation |
|-----------|--------------|-----------------|
| **I**ndependent | Can be developed without depending on other stories | Check `list_work_item_relations` — no `blocked_by` relations |
| **N**egotiable | Details can be discussed, not a rigid contract | Description uses "As a... I want... so that..." format |
| **V**aluable | Delivers value to user or business | Ties to an epic or has clear business justification |
| **E**stimable | Team can estimate the effort | Has enough detail for story points |
| **S**mall | Completable within a sprint | `point` ≤ 8 (flag > 8 for splitting) |
| **T**estable | Has clear acceptance criteria | `description_html` contains testable criteria |

### INVEST Validation Workflow

```
1. retrieve_work_item({ project_id, work_item_id })
   → Get item details

2. Check each criterion:
   I: list_work_item_relations({ project_id, work_item_id })
      → Verify no hard blocked_by dependencies
   N: Check description has user story format
   V: Check parent epic exists or description states value
   E: Check description has enough technical detail
   S: Check point ≤ 8
   T: Check description_html contains acceptance criteria

3. Report:
   [OK] Independent — no blocking dependencies
   [FAIL] Small — 13 points, recommend splitting
   [OK] Testable — 3 acceptance criteria found
   ...
```

## Vertical Slicing (Critical!)

**CORRECT — Vertical Slice:**
Each story spans the full stack and delivers user-visible functionality.

```
Story: "User can log in with email"
  → Frontend: login form
  → API: auth endpoint
  → Database: user lookup
  → Result: User sees dashboard after login
```

**INCORRECT — Horizontal Slice (Anti-Pattern):**
Stories split by architecture layer — breaks Independence and Value.

```
[FAIL] Story 1: "Create database schema for users"
[FAIL] Story 2: "Build API endpoints for auth"
[FAIL] Story 3: "Create login UI"
→ None deliver value alone, all depend on each other
```

## Story Splitting Patterns

When a story is too large (> 8 points), use these patterns to split:

### 1. Split by Workflow Step
```
Original: "User can manage their profile" (13 pts)
Split:
  → "User can view their profile" (3 pts)
  → "User can edit profile name and bio" (5 pts)
  → "User can change profile picture" (5 pts)
```

### 2. Split by Business Rule
```
Original: "System processes payments" (21 pts)
Split:
  → "System processes credit card payments" (8 pts)
  → "System processes PayPal payments" (5 pts)
  → "System handles payment failures and retries" (5 pts)
```

### 3. Split by Data Variation
```
Original: "Import data from external sources" (13 pts)
Split:
  → "Import data from CSV files" (5 pts)
  → "Import data from JSON API" (5 pts)
  → "Import data from Excel files" (3 pts)
```

### 4. Split by CRUD Operations
```
Original: "Manage blog posts" (13 pts)
Split:
  → "Create and publish a blog post" (5 pts)
  → "View and list blog posts" (3 pts)
  → "Edit existing blog post" (3 pts)
  → "Delete a blog post" (2 pts)
```

### 5. Split by Happy Path vs Edge Cases
```
Original: "User registration with validation" (13 pts)
Split:
  → "User can register with valid email and password" (5 pts)
  → "Show validation errors for invalid input" (3 pts)
  → "Handle duplicate email registration" (2 pts)
  → "Send email verification after registration" (3 pts)
```

### 6. Split by Platform/Interface
```
Original: "Notification system" (21 pts)
Split:
  → "In-app notifications" (8 pts)
  → "Email notifications" (5 pts)
  → "Push notifications" (8 pts)
```

## Decomposition Workflow

### Step-by-step Process

```
1. Retrieve the work item:
   retrieve_work_item_by_identifier({ project_identifier: "MP", issue_identifier: 42 })

2. Analyze against INVEST:
   - Is it > 8 points? → needs splitting
   - Is description vague? → needs refinement first
   - Has acceptance criteria? → if not, define before splitting

3. Choose splitting pattern:
   - Identify the right pattern from the 6 above
   - Ensure each child delivers standalone value

4. Create child items:
   For each sub-item:
   create_work_item({
     project_id: "<id>",
     name: "<child story name>",
     parent: "<parent_work_item_id>",
     description_html: "<p>As a [user]... acceptance criteria...</p>",
     point: <estimated_points>,
     priority: "<inherited or adjusted>",
     labels: ["<inherited labels>"]
   })

5. Update parent:
   update_work_item({
     project_id: "<id>",
     work_item_id: "<parent_id>",
     description_html: "<p>Parent epic/story. See child items for implementation.</p>"
   })

6. Set relations if needed:
   create_work_item_relation({
     project_id: "<id>",
     work_item_id: "<child1_id>",
     relation_type: "blocked_by",
     issues: ["<child0_id>"]
   })
```

## Point Distribution After Splitting

When splitting a parent item, the sum of child points should roughly equal the original:

```
Original: 13 points
Children: 5 + 5 + 3 = 13 points [OK]

Original: 21 points
Children: 8 + 5 + 5 + 3 = 21 points [OK]
```

If the sum exceeds the original, the original was likely underestimated. If it's less, some scope may have been implicitly dropped — verify with the team.

## User Story Template

```html
<h3>User Story</h3>
<p>As a <strong>[user type]</strong>, I want to <strong>[action]</strong> so that <strong>[value/benefit]</strong>.</p>

<h3>Acceptance Criteria</h3>
<ul>
  <li>Given [context], when [action], then [expected result]</li>
  <li>Given [context], when [action], then [expected result]</li>
</ul>

<h3>Technical Notes</h3>
<p>[Any technical considerations, API endpoints, data models]</p>
```

## Best Practices

1. **Always split vertically** — each piece should deliver user value
2. **Keep the smallest item ≥ 1 point** — anything smaller is overhead
3. **Maximum 8 points per item** — larger items hide complexity
4. **Preserve the parent** — keep it as a grouping epic/story
5. **Don't over-decompose** — 3-5 children per parent is ideal
6. **Decompose just-in-time** — split 1-2 sprints ahead, not the entire backlog
