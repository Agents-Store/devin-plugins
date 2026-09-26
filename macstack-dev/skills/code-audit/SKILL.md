---
name: code-audit
description: This skill should be used when the user asks "what is in the code that the documents do not know about", "сверь код с документами", "обнови документы по коду", "изучи код и найди несоответствия", "the docs are out of date, read the code", or runs /macstack-dev:check --code on a project whose macstack/ folder already exists. Enumerates what the code contains, compares it to the client documents and the spec, and proposes edits in the client → generated → macstack.json direction — it never edits a client document on its own.
---

# What is in the code that the documents do not know about

Two skills look at the same source tree and they are not the same question:

- **`conformance`** asks *"does the code do what the documents promise?"* — it starts
  from a case id and writes a **verdict**.
- **`code-audit`** asks *"what is in the code that the documents never mention?"* — it
  starts from a file and writes a **proposal**.

Without the second, the path from code back to the documents exists exactly once: the
first `/macstack-dev:start`. After that the code moves and the documents do not, and a
document that reads perfectly describes a system that no longer exists.

## Step 1 · Enumerate. Do not conclude.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/code-audit/references/inventory.py" <project> \
        [--json] [--kind entity]
```

It reads `macstack.json.software[].category`, picks the conventions for that stack, and
lists candidates: kind, name, path. It is not a Payload parser and not a Next.js parser —
this plugin is technology-agnostic, and a tool that knows one stack better than another
quietly makes every other project a second-class one.

It refuses to run without `macstack.json`: conventions come from the declared stack, not
from guessing at a file tree.

**It says out loud when a probe found nothing.** A convention the stack declares that
matches zero files is either the wrong convention or genuinely absent code — and those
must not look like "checked, all present". Same defect class as lint rule 12.0.

## Step 2 · Three lists, and nothing else

Match each candidate against `client/`, `generated/REQUIREMENTS.md` and `macstack.json`.
Every candidate lands in exactly one:

| List | Means | Becomes |
|---|---|---|
| **Not in the documents** | The code does something nobody wrote down | A proposed addition, or a ruling that it should be deleted |
| **Not in the code** | The documents promise something unbuilt | A task in `TASKS.md` |
| **Contradicts** | Both describe it, differently | A question for the owner — never a silent edit |

Sort by blast radius, not by count. Twenty missing admin screens matter less than one
role that can download what the documents say it cannot.

**Infrastructure gets a flag, not silence.** A file store, a delivery log, a numbering
sequence — these belong in `entities[]` like anything else the system stores, with
`technical: true` (schema rev 14). Without the flag, "not described to the client" and
"must not be described to the client" are indistinguishable, so the audit reports the
same infrastructure every run and the report stops being read. Leaving them out of the
spec entirely has the same effect for the same reason.

**An invented id is worse than an empty field.** An empty field is visible and somebody
asks about it. An invented id passes downstream and every check below it reports green.
When a candidate does not obviously map to an entity, say so and ask — the matching of
`Sessions.ts` to `session` or to part of `einsatz` is a domain question, not a file one.

## Matching, and where it fails — measured

Names are the only thing a file and a spec record share, and matching them by name works
for some kinds and not at all for others. On a live 33-collection project:

| Kind | Matched by name | What it means |
|---|---|---|
| entities | 18 of 18 | Collections and spec ids use one vocabulary. Reliable. |
| workflows | 3 of 17 | Two different vocabularies. Useless. |

Entities matched once plurals were handled — `coaches`↔`coach`, `time-entries`↔
`time-entry`, and the German `einsaetze`↔`einsatz`, which no regular rule produces. A
first pass without them reported 22 collections "missing from the documents" and 6 spec
entities "missing from the code": **28 findings, all false, and every one of them
plausible enough to act on.** Check the plural rules before believing a name-based list.

Workflows cannot be matched this way at all. The code names them for their domain
(`attendance`, `coach-confirm`); the spec names them for their step
(`wf-entry-capture`, `wf-mark-verified`). Both are right, and no normalisation bridges
them. So do not guess:

- record the mapping in the spec — `workflows[].source`, the path where it lives
  (schema rev 15), so the next audit is arithmetic instead of a re-derivation. Match by
  what each file DOES, not by what it is called, and let lint rule 12.39 keep the paths
  honest afterwards. One file may hold more than one workflow: `source` says where it
  lives, not that it lives there alone;
- or, until that is done, report the two lists side by side and say plainly that they
  are unmatched. Never turn an unmatched list into a count of missing work.

Reporting "14 of 17 workflows missing from the code" when they are all present under
other names is the worst available outcome: it is a confident number, it is wrong, and
somebody will schedule work against it.

Screens are the third case: 63 pages against 13 `interfaces[]`, because `interfaces[]`
holds **areas**, not pages — a recorded decision, not drift. A tool that reports 50
missing screens here has misread the model.

## Step 3 · Propose, in one direction only

`client/` → `generated/` → `macstack.json`. Never the reverse, and never silently.

This skill still only proposes. What APPLIES a proposal is a gate: `intake` for material
the client sent, **`reconcile` for what the code turns out to say** — see *Who may write
into `client/`* in `documents`. Applying here as well would put two writers on one file
with two sets of guard rails, and the first sign would be an edit with no ledger row.

Each contradiction goes to the owner as a question with two real options: the
recommendation you would defend, and "write it into `OPEN-QUESTIONS.md` and let the
client answer". Record the ruling in `history/DECISIONS.md` with its cost-if-wrong
clause written **now**, before the outcome is known.

Then it is the ordinary `intake` loop: apply, journal, task. Every applied edit gets a
row in `history/ledger.jsonl` keyed by the id that changed — an edit with no row is a
defect, and lint 12.36 says so.

## Step 4 · Coverage becomes work

What the documents promise and the code does not have becomes a task in `TASKS.md`, with
the case ids it closes, and goes to the tracker with `/macstack-dev:plan sync`.

The audit verdict per case goes into the ledger as `kind: "audit"` — not into a dated
markdown report. A verdict keyed by id is data: `uncovered.py` reads it to know which
cases are confirmed built. A report is a document, and it goes stale faster than anyone
rereads it.

## What this skill does NOT do

- It does not edit code. It reads.
- It does not edit a client document on its own. It proposes; the owner rules, and
  `reconcile` applies through the gate.
- It does not write verdicts — that is `conformance`. Overlapping the two produces two
  answers to one question and no way to tell which is current.
- It does not add a probe for a stack the spec does not declare. A convention table that
  grows by guessing is a table nobody can trust.

## Adding a stack

`PROBES` in `inventory.py` is keyed by `category` or `category:software-id`. The precise
key wins, and when it exists the generic one for that same software is not also run —
otherwise a Next.js project prints three warnings about having no Vue files, and a
warning that is always false teaches people to stop reading warnings.
