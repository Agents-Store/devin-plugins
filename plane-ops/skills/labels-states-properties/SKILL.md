---
name: labels-states-properties
description: Design taxonomies for Plane projects — labels, workflow states, work item types, and custom properties. Use when the user asks how to organize labels, design a state machine, set up custom fields, configure work item types, decide between label/property/type, or audit a noisy taxonomy. Covers naming conventions, recommended sets, and the difference between the four metadata mechanisms.
---

# Labels, States, Types, and Properties

Plane gives you four metadata mechanisms for work items. Pick the right one or your project becomes a tag soup nobody can search.

## The Four Mechanisms

| Mechanism | Purpose | Cardinality | Workflow effect |
|---|---|---|---|
| **State** | where the item is in the workflow | one per item | drives boards, burndown, velocity |
| **Work item type** | what kind of work it is | one per item | can drive different fields, templates |
| **Property** | structured, queryable attribute | one or many depending on type | reportable filter values |
| **Label** | freeform tag | many per item | grouping, filter shortcut |

### Decision tree

```
Need a different workflow / different fields?
  → Work item type   (e.g. Bug vs Spike)

Need a structured value you'll filter or report by?
  → Property         (e.g. severity = S1, environment = prod)

Need a yes/no flag the team will toggle?
  → Label            (e.g. needs-design, flaky, carryover)

Need to track the state of work?
  → State            (e.g. In Review, Done)
```

If the answer is "I'm not sure", default to **label**. Labels are cheap to create and cheap to delete. Properties have schema cost. Types have workflow cost.

## Labels — Naming Convention

Use **prefixed namespaces** so labels stay searchable. Without prefixes, you end up with `bug`, `Bug`, `bug-fix`, `Bug Fix`, `BUG`, `defect`, all meaning the same thing.

Recommended namespaces:

| Prefix | Purpose | Examples |
|---|---|---|
| `type/` | nature of work (when not using work item types) | `type/bug`, `type/feature`, `type/chore`, `type/spike`, `type/tech-debt` |
| `area/` | code area or product surface | `area/api`, `area/web`, `area/mobile`, `area/infra`, `area/auth` |
| `priority/` | urgency (when not using built-in priority) | `priority/p0`, `priority/p1`, `priority/p2` |
| `status/` | secondary status the workflow doesn't capture | `status/needs-info`, `status/blocked-external`, `status/needs-design`, `status/ready-for-review` |
| `customer/` | per-customer requests (only if you track this) | `customer/acme`, `customer/contoso` |
| `release/` | release earmarks | `release/v2.0`, `release/v2.1` |

Rules:
- One namespace per label. Don't combine (`type/bug-priority/p0`).
- Lower-kebab-case after the slash. No spaces.
- Choose a stable color per namespace (red for `type/bug`, blue for `area/*`, etc.) — labels become visually scannable on the board.
- Quarterly audit: list all labels, drop any with <3 uses or stale by >6 months.

## Work Item States — Designing the State Machine

Plane groups states into five fixed buckets. **Velocity counts only items moved into a state in the `completed` group during the cycle.** If you put "Done" in `started`, your burndown lies.

### Recommended state sets

**Standard Scrum (most teams):**

| Group | States | Notes |
|---|---|---|
| backlog | Backlog | unrefined ideas |
| unstarted | Ready | meets Definition of Ready |
| started | In Progress | actively worked |
| started | In Review | PR open, awaiting review |
| completed | Done | meets Definition of Done |
| cancelled | Cancelled | will not do |

**Kanban with QA gate:**

| Group | States |
|---|---|
| backlog | Backlog |
| unstarted | Ready, Blocked |
| started | In Progress, In Review, In QA |
| completed | Done |
| cancelled | Won't Fix |

**Support / triage:**

| Group | States |
|---|---|
| backlog | New |
| unstarted | Triaged, Needs Info |
| started | In Progress, Waiting on Customer |
| completed | Resolved |
| cancelled | Closed (no action) |

**Research / discovery:**

| Group | States |
|---|---|
| backlog | Idea |
| unstarted | Approved |
| started | Researching, Drafting |
| completed | Decided |
| cancelled | Abandoned |

### State design rules

1. **Max 6 states across started + unstarted** — beyond that, the board becomes a horizontal scroll wasteland.
2. **Don't add per-team states** like "In Alice's review". Use assignee for that.
3. **Sequence matters for burndown** — order states left-to-right in the natural flow. `update_state` accepts `sequence`.
4. **Renaming is safe**, deleting is not — items in a deleted state break. Migrate first via `/bulk-update --state new`.
5. **Pick one default state** for new items (usually `Backlog` or `New`).

## Work Item Types

Custom types let you give different kinds of work different fields and templates. Use them when the *workflow itself* differs.

### When to use a type vs a label

| Use a TYPE when... | Use a LABEL when... |
|---|---|
| different fields (Bug needs severity, Spike needs timebox) | same fields, different categorization |
| different default state machine | same workflow |
| different velocity treatment (Spikes don't count points) | counts the same |
| reporting needs the breakdown | nice-to-have filtering |

### Recommended type sets

**Product team:** `Story`, `Bug`, `Task`, `Spike`, `Tech Debt`
**Platform team:** `Feature`, `Bug`, `Incident`, `Runbook Item`, `RFC`
**Support team:** `Ticket`, `Bug`, `Question`, `Escalation`

**Maximum: 6 types.** Beyond that, taxonomy fatigue dominates and people start mistyping.

## Custom Properties

Properties are typed fields. They are the right mechanism for **structured, queryable, reportable** data.

### Property data types

| Type | Use for |
|---|---|
| `text` | freeform short string (root cause one-liner) |
| `number` | counts, ratios, customer impact |
| `select` | one-of fixed options (severity, environment) |
| `multi-select` | many-of fixed options (affected platforms) |
| `date` | deadlines, discovery dates |
| `boolean` | yes/no flags that need filtering (use a label for casual flags) |
| `user` | secondary owners (reviewer, QA lead) |
| `url` | links beyond `/link add` (vendor docs) |

### Example property sets per type

**Bug type:**
- `severity` (select: S0, S1, S2, S3) — required
- `environment` (select: prod, staging, dev) — required
- `affected platforms` (multi-select: web, ios, android, api) — required
- `root cause` (text)
- `customers affected` (number)
- `regression?` (boolean)

**Spike type:**
- `timebox` (number, hours) — required
- `outcome` (text)

**Story type:**
- `customer` (select: from CRM list)
- `value` (select: must, should, could, won't) — required for Definition of Ready

### Property design rules

1. **Mark required only what blocks Definition of Ready.** Over-requiring kills throughput.
2. **Don't change a property's data type** after rollout — existing values become invalid.
3. **`select` is better than `text`** for anything that will be filtered. `text` becomes inconsistent within a week.
4. **Scope properties to a type** when possible (severity only on Bug). Project-wide properties bloat the form.
5. **Pair properties with views** — a property without a view that uses it is ceremony.

## Maintenance — Quarterly Taxonomy Audit

Run this every quarter:

1. **Labels** — list all labels. Drop any with <3 uses or no use in the last 90 days. Merge near-duplicates.
2. **States** — check distribution. If items pile up in one state, the workflow has a bottleneck not captured by a state.
3. **Types** — check usage. If a type has <5% of items, fold it into another.
4. **Properties** — check fill rate. If a property is filled <30% of the time, it's not pulling its weight — remove or make optional.

Bad taxonomy is technical debt that compounds. A 30-minute quarterly audit prevents a 3-day cleanup later.

## Cross-references

- See `agile-fundamentals` for Definition of Ready / Definition of Done — these reference required properties.
- See `velocity-metrics` for how state groups affect velocity calculation.
- Use commands: `/label`, `/state`, `/work-item-type`, `/property`.
