---
name: estimation
description: Estimation — story points, Fibonacci scale, t-shirt sizing, relative estimation, planning poker facilitation. Use when estimating work items or running estimation sessions.
---

# Estimation

This skill covers story point estimation techniques — Fibonacci scale, t-shirt sizing, planning poker, and batch estimation workflows in Plane.

## Tool Name Resolution

Tools below are referenced by their **action name** only (e.g., `update_work_item`). Resolve the real tool names for your current Plane MCP server or connector through the `connector-bootstrap` skill. Match by action suffix — never assume a prefix.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_work_items` | List items to find unestimated ones |
| `retrieve_work_item` | Get item details for estimation context |
| `update_work_item` | Set story points (`point` field) |
| `list_cycle_work_items` | Get sprint items for estimation |
| `search_work_items` | Find reference stories |
| `list_work_item_relations` | Check dependencies that affect estimates |

## Fibonacci Story Point Scale

| Points | Meaning | Example |
|--------|---------|---------|
| **1** | Trivial — well-understood, minimal effort | Fix a typo, update a config value |
| **2** | Small — clear approach, low risk | Add a field to a form, simple API change |
| **3** | Moderate — clear approach, some work | New API endpoint with validation, simple UI component |
| **5** | Significant — some unknowns, multiple components | Feature with frontend + backend + tests |
| **8** | Large — considerable unknowns, consider splitting | Complex feature, new integration, significant refactor |
| **13** | Very large — **should be split** | Multi-component feature, new subsystem |
| **21** | Epic-sized — **must be split** | Entire feature area, architectural change |

**Rule:** Items > 8 points should be decomposed using the **task-decomposition** skill before entering a sprint.

## T-Shirt Sizing

Alternative for quick, high-level estimation:

| T-Shirt | Story Points | When to Use |
|---------|-------------|-------------|
| **XS** | 1 | Config change, copy update |
| **S** | 2 | Simple, well-defined task |
| **M** | 3 | Standard feature work |
| **L** | 5 | Multi-part feature |
| **XL** | 8 | Complex feature (consider splitting) |
| **XXL** | 13 | Too large — must split |

**Use T-shirt sizing for:** Roadmap planning, initial backlog triage, quick group estimation sessions.
**Convert to Fibonacci for:** Sprint planning, velocity tracking, capacity calculation.

## Planning Poker Facilitation

### Process (Interactive)

```
For each unestimated work item:

1. PRESENT the item:
   "Item: [name]
    Description: [summary]
    Acceptance criteria: [list]"

2. ASK for initial reactions:
   "Any questions about scope or approach?"

3. REQUEST estimates:
   "Please estimate using Fibonacci (1, 2, 3, 5, 8, 13, 21)"

4. EVALUATE responses:
   - If consensus (all same ±1): assign that value
   - If divergent: ask highest and lowest to explain reasoning

5. RE-VOTE after discussion (if needed)

6. ASSIGN the agreed estimate:
   update_work_item({
     project_id: "<id>",
     work_item_id: "<id>",
     point: <agreed_points>
   })
```

### AI-Assisted Estimation (When Team Not Available)

When estimating solo or with AI assistance:

```
1. Retrieve item details
2. Analyze complexity factors:
   - How many components are touched? (frontend, backend, DB, external APIs)
   - How well-understood is the approach?
   - Are there unknowns or research needed?
   - Are there dependencies on other items?
   - How much testing is required?

3. Apply heuristic:
   1 component, clear approach     → 1-2 points
   2 components, clear approach    → 3 points
   2-3 components, some unknowns   → 5 points
   3+ components, significant work → 8 points
   Research needed, many unknowns  → 13+ (flag for splitting)

4. Compare to reference stories for calibration
```

## Relative Estimation

### Setting Up Reference Stories

```
1. search_work_items({ query: "<find a well-understood completed item>" })
   → Pick 1-3 completed items as references

2. Establish baseline:
   "Login with email" = 3 points (reference)

3. For each new item, compare:
   - "Is this bigger or smaller than the reference?"
   - "How many times bigger/smaller?"
   - Map to nearest Fibonacci number
```

### Estimation Anchors

Create a team-specific reference table:

| Points | Reference Story | Why |
|--------|----------------|-----|
| 1 | "Fix button color" | Single CSS change, no logic |
| 3 | "Add email to user profile" | Form field + API + DB migration |
| 5 | "Password reset flow" | UI + API + email service + security |
| 8 | "OAuth integration" | External API + callback handling + token management |

## Batch Estimation Workflow

For estimating multiple backlog items at once:

```
1. Get unestimated items:
   list_work_items({ project_id: "<id>" })
   → Filter where point is null/0

2. Sort by priority (estimate high-priority first)

3. For each item:
   a. Read name + description
   b. Assess complexity (components, unknowns, dependencies)
   c. Compare to reference stories
   d. Suggest estimate with reasoning:
      "Suggested: 5 points — touches frontend + API, clear approach, similar to [reference]"
   e. On confirmation:
      update_work_item({
        project_id: "<id>",
        work_item_id: "<item_id>",
        point: 5
      })

4. Summary:
   | Item | Points | Rationale |
   |------|--------|-----------|
   | Login page | 5 | FE + API, similar to signup |
   | Fix 404 page | 1 | Single template change |

   Total estimated: 15 items, 47 points
   Items flagged for splitting: 2 (> 8 points)
```

## Estimation Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Estimating in hours | Hours vary by person, not comparable | Use story points (relative sizing) |
| Anchoring | First estimate biases all others | Use hidden cards (planning poker) |
| Padding | Adding "safety buffer" to each item | Use sprint-level buffer (15%) instead |
| Precision bias | Debating 3 vs 5 for too long | If unsure, pick the higher number |
| Not re-estimating | Scope changes but estimate stays | Re-estimate when requirements change |

## When to Flag for Decomposition

Automatically flag items for splitting (link to **task-decomposition** skill) when:

- Story points > 8
- Description is vague or lacks acceptance criteria
- Item touches more than 3 components/systems
- Team cannot agree on estimate (spread > 2 Fibonacci numbers)
- Estimate includes significant research/spike work

## Best Practices

1. **Estimate as a team** — diversity of perspective improves accuracy
2. **Use relative sizing** — "bigger than X, smaller than Y"
3. **Don't estimate bugs at 0** — even trivial bugs take time to verify
4. **Re-estimate when scope changes** — original estimate may be invalid
5. **Track accuracy** — compare estimates to actuals to improve over time
6. **Estimate the work, not the person** — points are team-agnostic
7. **Spike before estimating** — if too many unknowns, create a timeboxed spike first
