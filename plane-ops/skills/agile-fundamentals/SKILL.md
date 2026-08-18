---
name: agile-fundamentals
description: Single source of truth for Agile formulas, Definition of Ready, Definition of Done, MoSCoW priority mapping, WSJF scoring, capacity and velocity formulas, WIP limits, Fibonacci story points, and sprint buffer policy. Use whenever the user asks about story points, estimation, velocity, capacity, focus factor, WSJF, DoR/DoD, MoSCoW, Fibonacci, sprint buffer, or any Agile rule — and whenever any other plane-ops skill, command, or agent needs canonical Agile definitions. Do not duplicate these rules elsewhere — link here instead.
---

# Agile Fundamentals

Canonical reference for Agile rules, formulas, and mappings used across the plane-ops plugin. All other skills, commands, and agents link here instead of duplicating these rules.

## Core Formulas

### Capacity (no velocity history)

```
available_person_days = team_size × sprint_days
effective_days        = available_person_days × focus_factor   (default 0.7)
capacity_points       = effective_days × (1 − buffer)           (default buffer 0.15)
```

Baseline: ~1 story point per effective person-day for a startup team.

### Capacity (with velocity history)

```
capacity_points = average_velocity × (1 − buffer)   (default buffer 0.15)
```

Use the rolling average of the last 3–5 completed sprints. Drop outliers if any sprint deviates by more than 50% from the mean.

### Adjustments

- Subtract PTO: `capacity × (1 − pto_days / total_person_days)`
- First sprint: multiply by `0.6` to account for learning curve
- Holiday weeks: reduce proportionally to working days
- Overcommit pattern (completion rate < 70% for 2+ sprints): reduce capacity by 20%
- Undercommit pattern (finishing early 2+ sprints): increase capacity by 10%

### WIP Limit

```
wip_limit = floor(team_size × 1.5)
```

### WSJF (Weighted Shortest Job First)

```
WSJF = (Business Value + Time Criticality + Risk Reduction / Opportunity Enablement) / Job Size
```

Each factor is scored 1–10 on a modified Fibonacci scale (1, 2, 3, 5, 8, 13). Job Size uses the item's story points or a t-shirt size converted to points.

### Sprint Buffer

Always reserve **15%** of capacity unplanned for unexpected work, production issues, and reviews.

### Completion Rate

```
completion_rate = completed_points / planned_points
```

Healthy range: 80–100%. Above 100% consistently means undercommitment; below 70% means overcommitment.

## Definition of Ready (DoR)

A work item may enter a sprint only if **all** of these hold:

| # | Criterion | How to verify in Plane |
|---|-----------|-----------------------|
| 1 | Clear title and description with acceptance criteria | `name` is descriptive, `description_html` has AC |
| 2 | Estimated (Fibonacci 1, 2, 3, 5, 8) | `point` field is set and ≤ 8 |
| 3 | Dependencies identified, no unresolved blockers | `list_work_item_relations` — no active `blocked_by` |
| 4 | Small enough to complete in one sprint | `point` ≤ 8 (else decompose) |
| 5 | Assignee identified or assignable | `assignees` is set or can be set |
| 6 | Testable | Acceptance criteria are verifiable |

Items > 8 points must be decomposed via the `task-decomposition` skill before planning.

## Definition of Done (DoD)

A work item is Done only if **all** of these hold:

- [ ] Code merged to the main branch
- [ ] Automated tests pass in CI
- [ ] Acceptance criteria verified
- [ ] Peer review completed
- [ ] Documentation updated (user-facing and inline)
- [ ] Deployed to staging (or production for hot fixes)
- [ ] No known regressions
- [ ] Work item moved to the Done state group

Teams may extend this list but must not shorten it without a retro decision.

## MoSCoW → Plane Priority

| MoSCoW | Plane priority | When to use |
|--------|---------------|-------------|
| Must Have | `urgent` or `high` | Sprint goal depends on it; release blocker |
| Should Have | `medium` | Important but not blocking; defer if needed |
| Could Have | `low` | Nice to have; pick up if capacity allows |
| Won't Have (this time) | `none` | Explicitly out of scope |

## INVEST Criteria (for stories)

- **I**ndependent — can be built without waiting on other stories
- **N**egotiable — scope is a conversation, not a contract
- **V**aluable — delivers value to end users or stakeholders
- **E**stimable — the team can size it
- **S**mall — fits in one sprint (≤ 8 points)
- **T**estable — has verifiable acceptance criteria

## Fibonacci Story Points

Allowed values: **1, 2, 3, 5, 8**. Anything above 8 must be decomposed. Do not use 13, 21, or 40 — they signal insufficient decomposition.

T-shirt sizing equivalence (when used): `XS=1, S=2, M=3, L=5, XL=8`.

## Sprint Duration Guide

| Team size | Recommended duration | Planning time | Daily standup |
|-----------|---------------------|---------------|---------------|
| 1–3 | 1 week | 1 hour | 10 min |
| 4–7 | 1–2 weeks | 2 hours | 15 min |
| 8+ | 2 weeks | 3 hours | 15 min |

## Sprint Goal Template

> "By end of this sprint, **[users/customers]** can **[capability/feature]** so that **[business value]**."

A sprint goal must be:
- Outcome-focused (user value), not output-focused (feature list)
- Testable at sprint review
- Achievable within capacity
- Specific enough to guide daily trade-offs

## Core Agile Principles for Startups

1. Iterations over perfection — ship small increments frequently
2. Working software over documentation — bias toward action
3. Respond to change — adapt sprint scope when needed
4. Sustainable pace — protect team from overcommitment (focus factor 0.7)
5. Continuous improvement — every retro produces concrete action items
6. Minimize ceremony — just enough process to stay aligned, not more
7. Vertical slicing — deliver end-to-end value, not horizontal layers

## Sprint Lifecycle

```
1. Backlog Grooming  → prioritize and refine items (see backlog-management)
2. Sprint Planning   → select items, set goal, validate capacity (see sprint-planning)
3. Daily Standups    → track progress, surface blockers (see daily-standup)
4. Sprint Execution  → work items move through states
5. Sprint Review     → demo completed work, gather feedback (see sprint-review-retro)
6. Retrospective     → improve process, create action items (see sprint-review-retro)
7. Sprint Close      → transfer incomplete items, archive cycle
```
