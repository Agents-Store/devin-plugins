# Everyday Plane Command Flows

Reference scenarios for the day-to-day commands added in plane-ops 1.3. Each flow is a copy-pasteable sequence using the new high-level commands instead of raw MCP calls.

---

## 1. Create a Spec Page for a New Feature

**Goal:** Document a feature design before implementation, link it from the epic.

```
/page create project "TaskFlow" "Checkout v2 — Design Doc" --from-template spec
/epic update "TaskFlow" "Checkout Rewrite" --description "Tracking page: <page-url>"
```

The spec template includes Problem, Goals, Non-goals, Proposed Solution, API Changes, Rollout Plan, Open Questions, and Linked Work — see `pages-publishing` skill.

**Variation — meeting notes from a kickoff:**
```
/page create project "TaskFlow" "Checkout v2 Kickoff — 2026-04-08" --from-template meeting-notes
```

**Variation — record an architectural decision:**
```
/page create project "TaskFlow" "ADR-014 — Use Stripe Checkout vs Custom Form" --from-template decision-log
```

---

## 2. Daily Time Logging Loop

**Goal:** Engineer logs time at end of each work session, not in batch.

Morning:
```
/my-work --cycle current
```

After a 2.5h debug session on PROJ-148:
```
/log-time "TaskFlow" PROJ-148 2h30m "Debug Safari cookie issue, identified SameSite root cause"
```

End of week summary for the team:
```
/log-time summary "TaskFlow"
```

---

## 3. Link a PR to a Work Item and Move to Review

**Goal:** Engineer finishes implementation, opens PR, updates Plane in one go.

```
/link add "TaskFlow" PROJ-148 https://github.com/org/repo/pull/420
/work-item update "TaskFlow" PROJ-148 --state "In Review"
/comment add "TaskFlow" PROJ-148 "Ready for review. Tested on Safari 16/17, Chrome, Firefox."
/assign "TaskFlow" PROJ-148 alice --replace
```

The PR link will be discoverable by release-notes generation and by reviewers landing on the item.

---

## 4. Bug Triage with Custom Properties

**Goal:** New bug filed via intake — needs full classification.

Setup (one-time, per project):
```
/work-item-type create "TaskFlow" --name Bug --icon bug --color #e11d48
/property create "TaskFlow" --name severity --type select --options "S0,S1,S2,S3" --required --type-id <bug-type-id>
/property create "TaskFlow" --name environment --type select --options "prod,staging,dev" --required --type-id <bug-type-id>
/property create "TaskFlow" --name "customers affected" --type number --type-id <bug-type-id>
```

Per-bug flow:
```
/triage-intake "TaskFlow"
# Accept the bug → creates PROJ-160 of type Bug
/work-item update "TaskFlow" PROJ-160 --severity S1 --environment prod --customers-affected 12
/label apply "TaskFlow" --item PROJ-160 area/checkout
/assign "TaskFlow" PROJ-160 alice
```

---

## 5. Sprint Carryover with Bulk Tools

**Goal:** Sprint 14 ends with 3 incomplete items — move them to Sprint 15 with a `carryover` label.

Preferred (atomic, server-side):
```
/cycles transfer "TaskFlow" --from "Sprint 14" --to "Sprint 15"
```

Then mark the moved items as carryover for retro analysis:
```
/find --cycle "Sprint 15" --state "In Progress"
/bulk-update "TaskFlow" PROJ-148 PROJ-152 PROJ-156 --label add:status/carryover
```

---

## 6. Set Up a New Project Taxonomy

**Goal:** Brand new project, configure the taxonomy before the first sprint.

```
/setup-project "Mobile App"
/state list "Mobile App"
/state create "Mobile App" --name "In QA" --group started --color #f59e0b --sequence 35
/label create "Mobile App" "type/bug" --color #e11d48
/label create "Mobile App" "type/feature" --color #10b981
/label create "Mobile App" "area/auth"
/label create "Mobile App" "area/checkout"
/label create "Mobile App" "priority/p0" --color #dc2626
/label create "Mobile App" "priority/p1" --color #f97316
/work-item-type create "Mobile App" --name Story --default
/work-item-type create "Mobile App" --name Bug
/work-item-type create "Mobile App" --name Spike
/property create "Mobile App" --name timebox --type number --type-id <spike-type-id>
```

See `labels-states-properties` skill for the design rationale behind each choice.

---

## 7. Find an Item Fast

**Goal:** Look up an item by identifier, by query, or by filter.

```
/find PROJ-148                                # direct lookup
/find "Safari login bug"                      # full-text search
/find --assignee me --state "In Progress"     # personal WIP
/find --label priority/p0 --limit 5           # what's burning
```

---

## 8. Audit "Who Broke Production"

**Goal:** A bug regressed — find when it happened and who touched it.

```
/history "TaskFlow" PROJ-148 --since 2026-04-01
```

Look for state regressions (highlighted in red), assignment changes, label removals around the time the bug was filed. Cross-reference with `/log-time list "TaskFlow" PROJ-148`.

---

## 9. Block / Unblock Across the Sprint

**Goal:** Surface and clear blockers daily.

Mark blocker:
```
/relate blocked-by "TaskFlow" PROJ-150 PROJ-148
```

Standup view of all blockers in the active sprint:
```
/dependencies "TaskFlow" --cycle current
```

Once cleared:
```
/relate remove "TaskFlow" PROJ-150 PROJ-148
/work-item update "TaskFlow" PROJ-150 --state "In Progress"
```

---

## 10. Pre-Flight Before Destructive Operations

**Goal:** Make sure you're talking to the right Plane instance before deleting anything.

```
/whoami
/projects list
# verify the workspace and project context
/cycles delete "TaskFlow" "Sprint 09"
```

`/whoami` is cheap insurance against accidentally running destructive operations on the wrong workspace.
