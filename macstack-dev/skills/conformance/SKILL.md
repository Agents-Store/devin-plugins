---
name: conformance
description: This skill should be used when the user asks to "check the implementation against the documents", "audit the platform", "does the code do what the spec says", "test the whole stack against the requirements", "conformance review", "what is actually built", or runs /macstack-dev:check --code. Produces a dated audit pair — a technical conformance review and its business-language twin — with one verdict per case id.
---

# Audit the implementation against the documents

Every other check in this plugin asks whether the documents are well formed. This one
asks whether they are **true**.

It is read-only against the source tree, and it starts from a **case id**: does the code
do what this case promises? That is the boundary with `code-audit`, which starts from a
file and asks the opposite question — what is in the code that no document mentions.
Two skills, two directions, one source tree. Overlap them and you get two answers to one
question with no way to tell which is current.

**The durable output is a verdict per case, written into `history/ledger.jsonl` as
`kind: "audit"`.** A verdict keyed by id is data: `uncovered.py` reads it to know which
cases are already confirmed built, so the work list stops counting them as unplanned.

A dated markdown report is not the output. `history/reviews/` was exactly that and it is
now in `archive/`: a report goes stale faster than anyone rereads it, while the verdict
inside it stays useful for months. Print the run's findings to the terminal, put the
verdicts in the ledger, and put what must be built into `TASKS.md`.

What the client is told about the audit belongs in `CHANGELOG.md`, in their language,
and only for what actually reached them. An audit only an engineer can read is an audit
the person paying for the platform cannot act on — but the answer to that is one honest
paragraph, not a second full document that has to be kept in step with the first.

## What it reads

| Source | What it asks of the code |
|---|---|
| `client/USER-CASES.md` | does each acceptance bullet hold? |
| `client/UX-UI.md` | is each `forbidden` item actually unreachable on that screen? |
| `client/AUTOMATION.md` | does each trigger exist, fire from the declared source, and raise what it claims? |
| `generated/TEST-CASES.md` | which of these are already proven by a named test, and which need a human? |
| `generated/ARCHITECTURE.md` | **the map** — where to look |

Use the architecture document as the map. A blind recursive `grep` over `src/` is the
wrong instrument twice over: it finds the word rather than the behaviour, and in an
iCloud-backed folder it hangs for minutes on files that are not local. Read the map,
open the files it names, and fall back to a scoped search only when the map is silent —
which is itself a finding.

## Verdicts

One per case id, from a closed set. `plan` reads these to tell real work from a document
nobody has checked, and it can only do that if "done" is one token rather than six
phrasings of it.

- **`implemented`** — the behaviour exists and something proves it.
- **`partial`** — part of the acceptance list holds and part does not. Name which
  bullets, by id.
- **`absent`** — nothing in the code answers this case.
- **`externally-blocked`** — the code is complete and cannot be exercised because
  something outside it is missing: a credential, a client input, a third-party account.
  Name the `A<n>` it waits on.

A verdict without evidence is an opinion. Evidence cites a **test title** or a named
symbol — never `file.ts:120`, which is banned outright because line numbers rot the
moment the file above them grows.

## What a verdict row carries

One row per case, keyed by its id:

```json
{"date":"2026-08-27","doc":"client/USER-CASES.md","item":"C-04","kind":"audit",
 "now":"implemented","why":"src/workflows/attendance.ts + entry.double-checkin.spec.ts",
 "by":"claude"}
```

`now` is the verdict, `why` is the evidence — the surfaces that implement it and the
test that proves it. That is enough for the next run to see what changed and for
`uncovered.py` to stop reporting a built case as unplanned.

The arithmetic goes to the terminal: per role and in total, how many of each verdict, and
how many cases have no scenario test at all.

## What it does NOT do

- **It does not fix anything.** The output is a verdict and a list; the fix is
  `/macstack-dev:plan` and then a coding session.
- **It does not enumerate the code.** Starting from a file and asking what the
  documents are missing is `code-audit`. This skill starts from a case id.
- **It does not move `reviewed` dates by itself** for documents it did not actually
  check. A review dated later than `reviewed` moves that date forward — but only for the
  documents whose content this run examined. Marking all six because one was audited is
  how a document goes stale while lint stays green.
- **It does not invent a test.** A bullet that cannot be verified because the case never
  names the fact needed to verify it is a hole in `USER-CASES.md`, not in the tests. Say
  that, and stop.

## Feeding the loop

The audit verdicts in the ledger are what `/macstack-dev:plan` reads before reporting a
work list. Measured when this link was first built: a gap report that ignored the audit
announced 63 unplanned cases where 35 were already confirmed implemented. Reading the
verdicts cut it to 8. **A gap report that ignores what has already been checked reports
the size of the document, not the size of the work.**

## Running it from another agent

The procedure above names no tool that only one coding agent has. It is a document set,
a map and a set of verdicts, and a session in Codex or any other agent reads them the
same way — which is the point of `/macstack-dev:start` writing the spec block into both
`CLAUDE.md` and `AGENTS.md`.
