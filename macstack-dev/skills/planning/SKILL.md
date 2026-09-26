---
name: planning
description: This skill should be used when the user asks to "add a task", "what's left to do", "что осталось сделать", "завести задачу", "план работ", "backlog", "milestone status", "sync tasks with the tracker", "синхронизировать задачи", "what should I work on next", "какая веха дальше", "add to the backlog", "отметить задачу выполненной", "block this on", "plan the changes", "what needs building", "turn the requirements into tasks", "which cases have no plan", or mentions TASKS.md, milestones, M<n>-T<n> ids, or the team's task tracker. Owns TASKS.md — milestones, tasks, backlog — turns unplanned requirements into task entries, and reconciles bidirectionally with whatever tracker the project is bound to, without ever naming a specific product.
---

# Planning — from a requirement to a task somebody can pick up

`TASKS.md` says what will be done, in what order, and how it will be known done. It
sits beside `USER-CASES.md` (the bar), `OPEN-QUESTIONS.md` (owed / deferred) and the
team's own task tracker — where the *conversation* happens: comments, attachments,
assignment, notifications. `TASKS.md` is the **source of truth** for scope and order;
the tracker is never edited around it.

## A task in this file can be finished today

`TASKS.md` is a **queue somebody picks from**, not an inventory of everything that will
ever be built. So one rule governs what may enter it:

> **A requirement that depends on an unanswered client question does not become a task.**
> The question in `OPEN-QUESTIONS.md` §A holds that work until it is answered; the task
> is written the day the answer lands.

Owner's ruling, 2026-08-27, and it replaces the older `blocked_by`-on-a-task practice for
the client-question case. The reason is what happens to a person: they open the file, take
the top item, get two hours in, and hit a sentence nobody can write but the client. Now the
work is half-done, the branch is open, and the queue lied. A `blocked` status does not fix
that — it only tells you afterwards, and only if you read the field before starting.

`blocked_by` stays for **internal** blockers — one task waiting on another task, or on a §B
item whose trigger has fired. Those a team can unblock by itself. A client question it
cannot, and that is the whole difference.

**What keeps the work visible** is the §A item's own `Куда пойдёт` / *where the answer
goes*: it names the screens and behaviour the answer unlocks. That is the record. Absence
from `TASKS.md` is not cancellation — it is the statement that nobody can start yet.

`uncovered.py` enforces this: a case whose text names a live §A id is reported under
*awaiting the client* and **gets no skeleton from `--emit`**, which says out loud how many
it withheld and which.

Open `${CLAUDE_PLUGIN_ROOT}/skills/documents/references/doc-contracts.json`
(`documents.tasks`) for the anchors, id patterns and required fields first — this
skill assumes both and does not repeat them beyond the worked examples below.
Headings and prose follow `docs.language`; anchors and ids never translate.

## Layout and ids

```
<!-- macstack:section=howto -->        ## How to use this file
<!-- macstack:section=milestones -->   ## Milestones          M<n>
<!-- macstack:section=tasks -->        ## Tasks               M<n>-T<n>, grouped under their milestone
<!-- macstack:section=backlog -->      ## Backlog             BL-<n>, no milestone yet
<!-- macstack:section=journal -->      ## Journal             two columns: date, what changed
```

One anchor line immediately above the heading it marks, byte-exact, re-inserted
idempotently — never a reason to rewrite the file. ASCII only inside every id token
— a Cyrillic look-alike greps as absent. Ids are never renumbered, never reused; a
dropped task is struck, not deleted:

```
~~M11-T9~~ · DROPPED 2026-08-24 — superseded by M11-T14, same acceptance
```

## Status vocabulary

The tokens are the tracker's, and they come from **one place** — `fields.status.enum`
in the document contract, which is what lint rule 12.14 judges against. Do not write a
status from memory: this table used to list `doing` and `blocked`, which that rule
rejects, so following it produced a lint error on the next run.

| Status | Glyph | Means |
|---|---|---|
| `backlog` | ▫ | no milestone yet; exempt from needing a `tracker` id |
| `todo` | · | not started |
| `in_progress` | ▶ | active now |
| `done` | ✓ | acceptance passed |
| `cancelled` | ✕ | called off; exempt from needing a `tracker` id |
| `dropped` | ⊘ | struck — see the form above |

`status` and `tracker` are the two REQUIRED task fields. A task with no `tracker`
id is a lint ERROR — see Tracker sync below.

`blocked` is not a status. An INTERNAL blocker is the `blocked_by` bullet on a task
that stays `todo`; a task waiting on a client answer does not exist yet at all (see the
rule at the top).

**The same status is written twice** — the bullet in `TASKS.md` and, when the spec
mirrors it, `lifecycle.tasks[].status` in `macstack.json`. They must agree, and nothing
cross-checks them yet; the schema accepts both vocabularies so that a mirror of a real
`TASKS.md` validates, but writing the tracker five in both is what keeps them readable.

## One task, worked

The document is `format: v3` — headings and bullets, no YAML block. The pointer above
the heading names the case the task closes; the bullets carry the state.

````markdown
<!-- macstack:ref=cases[id=C-02] -->
### M2-T3 · Verify email before first login

- **Status:** in_progress
- **Opened:** 2026-08-24
- **Started:** 2026-08-28
- **Closes:** C-02
- **Tracker:** TRACK-142
- **Files:** `src/auth/verify.ts`, `src/auth/routes.ts`

**Acceptance:**
- `auth.int.spec.ts` — "rejects unverified login". Remove the verify guard and that
  named test reddens. That is the check.
````

The status lives in a bullet, not in the heading — v1 put a glyph after the title and
every tool had to parse a heading to learn a state. The glyph stays in the `INDEX.md`
render, where it is for the reader.

`Closes` points, it never restates — the pointer plus the acceptance is the row's whole
value; a paraphrase only drifts. Acceptance names the test(s) and what each asserts —
where the project mutation-tests, "remove X and this named test reddens" is the
strongest form. `Files` is the expected footprint; correct it as the task's shape
changes. `blocked_by` holds task or §B ids — **never an §A id**: a task waiting on a
client answer does not exist yet, which is the rule at the top of this file, and an
earlier version of this very example broke it.

## One milestone, worked

````markdown
### M2 · Auth hardening

- **Status:** in_progress
- **Target:** 2026-09-15

<!-- macstack:done_when -->
- works in every role area at both narrow and wide viewport
- migrations proven, up and down, against a seeded snapshot
- `auth.pinning.spec.ts` unchanged and green
- full suite, zero skipped
- the `AuthContext` shape frozen for M3 and M4
- email verification required before the first booking action
- failed-login rate limit holds under the load test in CI

Order is strict: M2-T1 → M2-T2 → M2-T3 — the migration must land before the route
guard or local dev breaks mid-branch. Do not reorder without re-opening this note.
````

`done_when` is a list of FALSIFIABLE checks, typically 5–7; "works well" is not
one. Five recur across milestones — offer as the default, then add 2–3 specific to
this one: works in every role area at both viewports · migrations proven · a named
pinning test unchanged and green · full suite, zero skipped · a contract frozen for
downstream milestones. State an ordering note, with its reason, only when task
order genuinely may not change.

## Every document the work produced is NAMED — `docs`

`TASKS.md` says what the work IS. Anything that says HOW — a plan written by
`superpowers:writing-plans`, a design spec, the client PDF the requirement came out
of — lives in another file, and the link between the two exists only in the session
that wrote both. Close that session and the plan is unfindable: nobody greps
`docs/superpowers/plans/` on the chance something is there.

So a task or a milestone whose work is described elsewhere carries a **`docs`**
bullet listing every such file:

```markdown
### M16-T3 · Half the day rate below 4.5 hours

- **Status:** todo
- **Opened:** 2026-08-29
- **Closes:** `CC-08`
- **Documents:** `docs/superpowers/plans/2026-08-29-m16.md`, `macstack/inbox/client-portal-spec.pdf`
```

Three rules, and the third is the one that gets forgotten:

- **A plan file created during planning is ALWAYS linked** — from the milestone, and
  from every task it covers. Point at the section too when the plan is long
  (`…/2026-08-29-m16.md → Task 3`): a nine-task plan opened at the top makes the
  reader hunt for their own task.
- **An external skill or plugin counts.** `superpowers:writing-plans`,
  `superpowers:brainstorming`, a design doc from any other plugin — the file it left
  behind is a document of this project now, whoever generated it.
- **The link is one-way and this file owns it.** A plan does not have to point back;
  it is written once and goes stale. `TASKS.md` is maintained, so the pointer lives
  here. If a plan is superseded, the task's `docs` moves — the plan file is not edited
  to say so.

`docs` is optional by design: a one-line task with no separate plan does not get an
empty bullet. But **the moment a plan file exists, the link is not optional** — an
unlinked plan is work the next person redoes.

## Tracker sync — reconcile, never push

`TASKS.md` is the record; the tracker is the conversation. Never let one side
clobber the other silently, never invent a tracker id.

1. **Discover the binding** — `macstack.json` → `resources.bindings` for an entry
   that looks like a task tracker (project/workspace id, issue states), or a
   binding file in the project root. None found → say so and ask which tracker
   the team uses. Never assume a product.
2. **Discover the tools** — search the session's MCP tools at runtime for ones
   that read/write work items under that binding; never hard-code a tool name.
3. **Read both sides** — every `TASKS.md` task (id, status, title, `tracker` id)
   and every item under the bound project/workspace in the tracker.
4. **Diff, then stop for a human on any disagreement:**
   - Task with no `tracker` id → create it in the tracker, write back the id it
     returns. Never invent one.
   - Tracker item with no matching task → propose a new `BL-<n>` or `M<n>-T<n>`
     row; never add it unasked.
   - Status differs on one side only → surface the proposed update to the other
     side; a human confirms before either is written.
   - Status changed on **both** sides since the last sync → a conflict — present
     both values and ask, never pick a winner.
5. **No tracker tools available** → do the file-only half, report exactly which
   tasks lack a `tracker` id or have an unsynced status; never claim a sync happened.

## §B is debt kept; a task is debt scheduled

§B records what the team **consciously accepted**, and both its required fields
argue why *not* to act now (`reason-safe-to-defer`, `trigger-that-makes-it-unsafe`).
`TASKS.md` says what *will* be done — a §B item can sit for a year and stay
correct; it becomes a task only when its trigger fires. **Promotion**: add the
task with its own `spec`/`acceptance`, then strike the §B row pointing at the new
id — `~~B7~~ · PROMOTED 2026-08-24 → M3-T2` — leaving its original text untouched.

A `BL-<n>` backlog row is a task with no milestone yet: same required fields minus
`blocked_by`. Promoting one into a milestone keeps the same `tracker` id (never a
second tracker item) and strikes the `BL-<n>` row the same way. A commit subject
ending `(M11-T9)` links a commit to its task for free — worth the convention.

## Routing

| Situation | Do |
|---|---|
| No `TASKS.md` yet | `macstack-dev:documents` scaffolds it |
| "add a task" / "завести задачу" | Append under its milestone (or `backlog`), `todo`, `tracker` filled or created |
| "what's left" / "что осталось сделать" / "what should I work on next" | List `todo`/`doing` tasks not `blocked`, ordered by milestone |
| "milestone status" | Report the milestone's `done_when` checks, pass/fail |
| "sync tasks with the tracker" / "синхронизировать задачи" | Run the reconcile procedure above |
| Debt that's fine to sit | `OPEN-QUESTIONS.md` §B, not here |
| Work that needs a client answer first | `OPEN-QUESTIONS.md` §A, not here — and no task until the answer lands |
| An §A item just got answered | Write the task now; the question closes with a pointer to its id |
| A §B trigger just fired | Promote it — see above |
| "what needs building" / nothing planned yet | Run the gap pass below |
| A task just reached `done` | `/macstack-dev:update` — it sweeps the documents |
| "the code already does this" / statuses look wrong | `task_status.py` — see *Keeping the statuses honest* |
| Code and documents have drifted apart wholesale | `/macstack-dev:reconcile --master=code\|docs` |
| After any change | `macstack-dev:lint` |

## Finding the work nobody planned

The link between `client/USER-CASES.md` — what a person must get — and `TASKS.md` —
what will be done about it. Without it a requirement reaches the code through
somebody's memory, and nothing afterwards can say which change answered which
requirement.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/planning/references/uncovered.py" macstack [--emit]
```

It reads three inputs — the cases, the tasks, and the newest
`history/reviews/*-conformance.md` — and sorts every case into four states:

| State | Means | Do |
|---|---|---|
| planned | a task already names it | nothing |
| audited: done | the newest review found it implemented | nothing |
| audited: partial | found partial or externally blocked | read the verdict first |
| **neither** | nobody planned it, nobody checked it | **this is the work** |
| **awaiting the client** | its text names a live §A id | not work, and not a task — chase the answer |

**Read the verdicts before reporting a number.** The first version of this reported
63 cases with no plan where 35 were already confirmed implemented by an audit — true,
and useless. A work list nobody believes is a work list nobody reads. Reading the
review cut the same report to 8. A gap report that ignores what has already been
checked reports the size of the document, not the size of the work.

`--emit` prints task skeletons. The skeleton is not the deliverable — `files` and
`acceptance` come back empty, and filling them is the only real work in this pass:

1. Open `generated/ARCHITECTURE.md` and find where this behaviour belongs. Use the map,
   not a blind recursive grep — in an iCloud-backed folder that hangs for minutes, and
   it finds the word rather than the behaviour either way.
2. Write `files` as the expected footprint.
3. Write `acceptance` as a named test and what it asserts. Strongest form: *remove X and
   this named test reddens*. A bare filename is not acceptance; a line number is banned.
4. Do **not** carry a client question through as `blocked_by`: a case naming a live §A id
   is not planned at all, and the script already withheld its skeleton. Carry through only
   an internal blocker — another task, or a §B item whose trigger fired.

### Three things this refuses to do

- **Guess `files` or `acceptance` without reading the code.** If the codebase does not
  answer where something belongs, that is a finding — say so and leave the field empty
  rather than filling it plausibly. A plausible wrong path costs more than an empty one,
  because somebody will follow it.
- **Plan a case an audit already passed.**
- **Plan a case that is waiting on the client.** Report it under *awaiting the client*,
  name the §A ids, and stop. Writing the task anyway is how a queue acquires an item
  nobody can finish.
- **Invent a milestone.** A new milestone is a decision about scope and dates and it
  belongs to the owner. The script takes the last `M<n>` from `TASKS.md`; going past it
  is a question, not a default.

### Then stop

Do not start coding here. The handoff is the point: open plan mode and say *"take
M15-T2 from macstack/history/TASKS.md"*. A planning session that slides into
implementation produces a task list nobody finished writing and a change nobody
reviewed the plan for.

## Keeping the statuses honest — the same link, read backwards

The gap pass above asks *"does this case have a task?"*. The opposite question — *"is
this task still true?"* — was asked by nothing, and both of its answers were silent:

- a task sits `todo` while the code has done the work for weeks. The list shows an
  amount of work that does not exist, and somebody plans what is already built;
- a task sits `done` while the audit found `absent`. **This one is worse:** the list
  looks shorter than the truth, so nobody goes looking for what is presumed finished.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/planning/references/task_status.py" macstack [--apply]
```

It reads `TASKS.md`, the `audit` rows of the ledger, and the `Closes` bullet that ties
them, then moves statuses **in both directions**. Closing without reopening would be a
ratchet: a work list that can only ever shrink.

| It reads | It writes |
|---|---|
| every case a task `Closes` is `implemented` | `done`, plus today's `Finished` date |
| any of them is `absent` | back to `todo` |
| any of them is `partial` | back to `in_progress` |
| `externally-blocked` | nothing — the code is finished and the blocker is outside it |
| `backlog`, `cancelled`, `dropped` | nothing — those are decisions, and an audit measures code |

Four refusals, each for a reason worth keeping:

- **Evidence must be newer than the claim.** A verdict dated before the task's own
  `Opened`/`Started`/`Finished` is stale and is reported, never applied — otherwise an
  audit run before the work reopens a task closed after it, and the script argues with
  the person who knows more.
- **Every case must be confirmed** before a task closes; **any one** failing reopens it.
  Both rules lean the same way: do not call finished what nothing proves.
- **The status vocabulary comes from the contract**, never from this file. Writing a
  token lint 12.14 rejects is how a green run becomes a red one on the next pass.
- **Without `--apply` it writes nothing.** Each applied move is one `changed` row in
  the ledger with its evidence, so a status that moved can be explained six months on.

Run it before reporting any work list — a number that counts built work is the same
defect the gap pass already fixed once, arriving from the other side.
