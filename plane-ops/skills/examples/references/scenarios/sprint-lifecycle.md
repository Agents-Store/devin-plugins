# Scenario: Complete Sprint Lifecycle

End-to-end scenario for a 3-person startup team running a 1-week sprint.

## Context

- **Team:** Alice (frontend), Bob (backend), Carol (fullstack)
- **Project:** "TaskFlow" (identifier: TF)
- **Sprint duration:** 1 week (Monday to Friday)
- **Historical velocity:** ~18 points/sprint

---

## Monday: Sprint Planning

### 1. Calculate Capacity

```
Team: 3 people × 5 days = 15 person-days
Focus factor: 15 × 0.7 = 10.5 effective days
Historical velocity: 18 points
Capacity: min(18, 10.5 × 2) × 0.85 = ~15 points
```

### 2. Select Items from Backlog

| # | Item | Priority | Points | Assignee |
|---|------|----------|--------|----------|
| 1 | TF-30 User profile page | high | 5 | Alice |
| 2 | TF-31 API rate limiting | high | 3 | Bob |
| 3 | TF-32 Fix login redirect | urgent | 2 | Carol |
| 4 | TF-33 Dashboard charts | medium | 5 | Carol |
| **Total** | | | **15** | |

### 3. Sprint Goal

> "By end of this sprint, users have a profile page and the API is stable under load"

### 4. Create Sprint

```
create_cycle → "Sprint 8 — Profile & API Stability"
add_work_items_to_cycle → [TF-30, TF-31, TF-32, TF-33]
```

---

## Tuesday: Daily Standup

### Status Check

```
list_cycle_work_items → group by assignee and state

Alice: TF-30 User profile page → In Progress (started yesterday)
Bob:   TF-31 API rate limiting → In Progress
Carol: TF-32 Fix login redirect → Done [DONE] (2 pts)
       TF-33 Dashboard charts → Todo

Sprint: 2/15 points done (13%), Day 2 of 5
WIP: 2/4 limit — Healthy
```

---

## Wednesday: Mid-Sprint Check

### Status

```
Alice: TF-30 → In Review (5 pts, awaiting review)
Bob:   TF-31 → In Progress (day 2)
Carol: TF-32 → Done [DONE]
       TF-33 → In Progress (started today)

Sprint: 2/15 done (13%), 1 in review, 2 in progress
Note: TF-30 in review — will be done once approved
```

### Blocker Detected

Bob reports TF-31 needs a library upgrade first.

```
create_work_item → "TF-34 Upgrade rate-limit library" (1 pt, parent: TF-31)
create_work_item_relation → TF-31 blocked_by TF-34
```

---

## Thursday: Progress Update

### Status

```
Alice: TF-30 → Done [DONE] (5 pts, review approved)
Bob:   TF-34 → Done [DONE] (1 pt, library upgraded)
       TF-31 → In Progress (blocker resolved)
Carol: TF-33 → In Progress (day 2)

Sprint: 8/16 done (50%), Day 4 of 5
(16 because TF-34 was added mid-sprint)
On track for ~14 pts completion
```

---

## Friday: Sprint Review & Retro

### Sprint Review

```
list_cycle_work_items → categorize results

COMPLETED (14 points):
  [DONE] TF-30 User profile page (5 pts) — Alice
  [DONE] TF-31 API rate limiting (3 pts) — Bob
  [DONE] TF-32 Fix login redirect (2 pts) — Carol
  [DONE] TF-33 Dashboard charts (5 pts) — Carol (finished Friday AM)
  [DONE] TF-34 Library upgrade (1 pt) — Bob (added mid-sprint)

NOT COMPLETED: None!

Completion: 16/16 points (100%)
Velocity: 16 points (was 18 historical, 16 is fine)
```

### Retrospective (Start-Stop-Continue)

```
START:
- Code reviews within 4 hours
- Writing acceptance criteria before sprint

STOP:
- Adding items mid-sprint without discussion
- Skipping daily standup on Fridays

CONTINUE:
- Pair programming for complex tasks
- Breaking down large items before sprint
```

### Action Items

```
create_work_item → "[RETRO] Set up review SLA — 4hr turnaround"
  assignee: Alice, label: retro-action, target: next sprint

create_work_item → "[RETRO] Add acceptance criteria template"
  assignee: Bob, label: retro-action, target: next sprint
```

### Close Sprint

```
archive_cycle → Sprint 8 archived
create_project_page → "Retro — Sprint 8 (2025-03-14)"
```

---

## Key Takeaways

1. **15 points planned, 16 delivered** — mid-sprint addition (1 pt) was small and acceptable
2. **Blocker handled quickly** — detected Wednesday, resolved Thursday
3. **100% completion** — team committed conservatively (15 pts vs 18 velocity) and delivered
4. **2 retro actions** — specific, assignable, measurable improvements
5. **Sprint goal met** — profile page shipped, API is stable
