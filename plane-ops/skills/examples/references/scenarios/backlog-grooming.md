# Scenario: Backlog Grooming Session

End-to-end scenario for grooming a backlog of 20 items for a startup team.

## Context

- **Team:** 4-person startup team
- **Project:** "ShopFlow" (identifier: SF)
- **Current state:** Backlog has 20 items, many unrefined
- **Goal:** Prepare backlog for next 2 sprint plannings

---

## Step 1: Assess Backlog Health

```
list_work_items({ project_id }) → 20 items

Initial Health Report:
┌─────────────────────────────────────┐
│ BACKLOG HEALTH                      │
├─────────────────────────────────────┤
│ Total items:      20                │
│ Estimated:         8 (40%)          │
│ Has priority:     10 (50%)          │
│ Has description:  12 (60%)          │
│ Oversized (>8pt):  3 (15%)         │
│ Health Score:     35% — UNHEALTHY   │
└─────────────────────────────────────┘
```

---

## Step 2: Prioritize with MoSCoW

Review each item with the product owner:

| Item | Current Priority | MoSCoW | New Priority |
|------|-----------------|--------|-------------|
| SF-10 Checkout flow | none | Must Have | urgent |
| SF-11 Payment integration | none | Must Have | high |
| SF-12 Product search | low | Should Have | medium |
| SF-13 User reviews | none | Could Have | low |
| SF-14 Admin dashboard | medium | Must Have | high |
| SF-15 Email notifications | none | Could Have | low |
| SF-16 Social login | none | Won't Have | none |
| ... | | | |

```
For each item:
  update_work_item({ project_id, work_item_id, priority: "high" })
```

---

## Step 3: Estimate Unestimated Items

12 items need estimates. Using reference story calibration:

**Reference:** SF-10 "Checkout flow" = 8 points (known complexity)

| Item | Components | Unknowns | Relative | Points |
|------|-----------|----------|----------|--------|
| SF-11 Payment integration | BE + External API | High | Bigger than SF-10 | 13 → SPLIT |
| SF-12 Product search | FE + BE + DB | Medium | Similar to checkout | 8 |
| SF-13 User reviews | FE + BE + DB | Low | Smaller | 5 |
| SF-14 Admin dashboard | FE + BE | Medium | Similar | 8 |
| SF-15 Email notifications | BE + Email service | Low | Much smaller | 3 |
| SF-17 Cart persistence | FE + BE | Low | Small | 3 |
| SF-18 Order history | FE + BE | Low | Small-medium | 5 |
| SF-19 Inventory tracking | BE + DB | Medium | Medium | 5 |
| SF-20 Shipping calculator | BE + External API | Medium | Medium | 5 |
| SF-21 Discount codes | FE + BE | Low | Small | 3 |
| SF-22 Product images | FE + Storage | Low | Small | 2 |
| SF-23 SEO meta tags | FE | Low | Trivial | 1 |

```
For each:
  update_work_item({ project_id, work_item_id, point: N })
```

---

## Step 4: Decompose Oversized Items

3 items > 8 points need splitting:

### SF-11 Payment Integration (13 pts)
Split by payment method:

```
create_work_item → "SF-24 Stripe card payments" (5 pts, parent: SF-11)
create_work_item → "SF-25 PayPal integration" (5 pts, parent: SF-11)
create_work_item → "SF-26 Payment error handling" (3 pts, parent: SF-11)

create_work_item_relation → SF-25 start_after SF-24
create_work_item_relation → SF-26 start_after SF-24
```

### SF-08 User management (13 pts)
Split by CRUD:

```
create_work_item → "SF-27 User registration & login" (5 pts, parent: SF-08)
create_work_item → "SF-28 User profile view & edit" (3 pts, parent: SF-08)
create_work_item → "SF-29 Password reset flow" (3 pts, parent: SF-08)
create_work_item → "SF-30 Account deletion" (2 pts, parent: SF-08)
```

### SF-09 Product catalog (13 pts)
Split by workflow:

```
create_work_item → "SF-31 Product listing page" (5 pts, parent: SF-09)
create_work_item → "SF-32 Product detail page" (3 pts, parent: SF-09)
create_work_item → "SF-33 Category filtering" (3 pts, parent: SF-09)
create_work_item → "SF-34 Product sorting" (2 pts, parent: SF-09)
```

---

## Step 5: Add Missing Descriptions

5 items lack adequate descriptions. Add acceptance criteria:

```
update_work_item({
  project_id, work_item_id: "SF-12",
  description_html: "
    <h3>User Story</h3>
    <p>As a shopper, I want to search for products by name so that I can quickly find what I need.</p>
    <h3>Acceptance Criteria</h3>
    <ul>
      <li>Search bar visible on all pages</li>
      <li>Results appear as user types (debounced, 300ms)</li>
      <li>Results show product name, image, price</li>
      <li>Empty state for no results</li>
      <li>Search works with partial matches</li>
    </ul>
  "
})
```

---

## Step 6: Label Items

```
create_label({ project_id, name: "ready", color: "#22c55e" })
create_label({ project_id, name: "needs-refinement", color: "#f59e0b" })

For groomed items:
  update_work_item({ labels: ["ready-label-id"] })

For items still needing work:
  update_work_item({ labels: ["needs-refinement-label-id"] })
```

---

## Step 7: Final Health Check

```
┌─────────────────────────────────────┐
│ BACKLOG HEALTH (After Grooming)     │
├─────────────────────────────────────┤
│ Total items:      29 (was 20)       │
│ Estimated:        27 (93%) [OK]        │
│ Has priority:     29 (100%) [OK]       │
│ Has description:  25 (86%) [OK]        │
│ Oversized (>8pt):  1 (3%) [OK]        │
│ Ready for sprint: 22 (76%) [OK]       │
│ Health Score:     82% — GOOD        │
└─────────────────────────────────────┘

Improvement: 35% → 82% (+47%)
```

---

## Next Sprint Candidates (by priority)

| Priority | Items | Points |
|----------|-------|--------|
| Urgent | SF-10 Checkout flow | 8 |
| High | SF-24 Stripe payments, SF-14 Admin dashboard, SF-27 Registration | 18 |
| Medium | SF-12 Search, SF-18 Order history, SF-19 Inventory | 18 |
| Low | SF-13 Reviews, SF-15 Email, SF-21 Discounts | 11 |

**For next sprint (capacity ~20 pts):**
SF-10 (8) + SF-24 (5) + SF-27 (5) + SF-22 (2) = 20 pts

---

## Key Takeaways

1. **Grooming expanded the backlog** — 20 items became 29 after decomposition (that's expected and healthy)
2. **All items now estimated** — team can plan sprints with confidence
3. **No more oversized items** — everything is ≤ 8 points
4. **Clear priorities** — MoSCoW mapped to Plane priority field
5. **Health score doubled** — from 35% to 82%
6. **2 sprints of ready work** — ~40 points ready, team velocity ~18-20 pts
