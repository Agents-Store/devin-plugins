---
name: journal
description: This skill should be used when the user wants to "write a changelog", "log what I did", "record today's work", "what shipped", "что сделали", "лог разработки", "записать в журнал", "release notes", "what changed for the client", "закрыть веху", "cut a release" — or whenever ANY document under `macstack/` is edited, because every edit gets a row in `history/ledger.jsonl` keyed by the id of the thing that changed. Owns the ledger and its curated, client-facing `history/CHANGELOG.md`.
---

# The ledger and its client-facing changelog

`history/ledger.jsonl` is the raw record — one JSON object per line, one line per
event, keyed by **the id of the statement that changed**. `history/CHANGELOG.md` is
its curated, client-facing derivative: the same raw → curated relationship this folder
already runs from `inbox/` to the documents intake produces.

Nobody reads the ledger to find out what shipped; nobody reads `CHANGELOG.md` to find
out why a sentence in the user cases is different this week. Confusing the two produces
either a changelog no client can parse, or a client document carrying a wall of
versions at the bottom of every file.

## Why a ledger and not a journal

Until v3 this was a session journal, and its entries were about the **session**: material
came in, a package went out, work was done. Useful, and it never answered the one
question the loop actually needs answered — *which statement moved?*

That gap had a visible cost. A review package could not tell a client "this sentence is
not what you read last time, and here is what you said about it", so every round the
client re-read text they had already approved. And the per-document journals that tried
to fill the gap sat inside the client's own documents, growing by a row a week, mixing
"the hour is now the billing unit" with "converted to the v2 block format".

So: one append-only stream, keyed by item id. The client documents carry no journal at
all (lint 12.33). What the client sees is the package, marked per statement.

## A row

```json
{"date": "2026-08-26", "doc": "client/USER-CASES.md", "item": "C-04",
 "kind": "changed", "was": "критично", "now": "важно",
 "why": "client comment in the 2026-08-25 package",
 "source": "handoff:2026-08-25-user-cases-rev2",
 "task": "M15-T2", "decision": "D42", "by": "claude"}
```

`date`, `doc`, `item` and `kind` are required. A row without an item id is refused on
append: a row nothing can find is not a record.

## The nine kinds

| Kind | What it records |
|---|---|
| `added` `changed` `removed` | the statement itself |
| `comment` | the client said something **about** it |
| `answer` | we replied to that comment |
| `audit` | a conformance run reached a verdict on it |
| `handoff` | a review package went to the client |
| `release` | something reached the people who use it |
| `work` | a task was finished |

One stream for all nine on purpose: the package needs them interleaved in time for a
single statement, and a client's comment and the edit it caused are the same story.

The last three carry an `item` of `project` or `doc:<key>` rather than a statement id,
because a package and a release are events about the whole thing.

**`intake` and `merge` have no kind of their own**, and that is deliberate. The trace
of a merge is the edits it produced. A row saying "material was merged" sitting beside
the rows saying what the merge changed is a summary of its own neighbours — and it is
the row that goes stale first, because nobody updates a summary when they fix one of
the things it summarises.

## Writing rows

Use `${CLAUDE_PLUGIN_ROOT}/skills/documents/references/ledger.py`; never append by hand.

```python
import ledger
ledger.append(root, {
    'date': today, 'doc': 'client/USER-CASES.md', 'item': 'C-04.a3',
    'kind': 'changed', 'was': old_text, 'now': new_text,
    'why': 'D42 — unselected rows stay open', 'decision': 'D42', 'by': 'claude'})
```

`was` matters more than it looks. Without it the package can say a statement changed
and not what it changed **from**, and the client's first question is exactly that.

Reading back: `ledger.by_item(root, 'C-04')` is one statement's whole story, oldest
first — what the package prints beside it. `ledger.changed_since(root, date)` is the
CHANGED marks. `ledger.last_handoff(root)` is the date those marks are measured from,
and it reads the date out of the **package's own name**, not out of a row's `date`: a
comment carries the day the client wrote it and an answer the day we replied, and
either would move the mark past statements the client has never seen.

## The curation pass — ledger → `CHANGELOG.md`

A release entry is written for a person who does not read code, from the `release` and
`work` rows since the last one. Drop everything with no user-visible effect: a changelog
that mirrors the ledger is a git log with extra steps.

The exception: if the work notes say something did not work and the client saw it, the
changelog does not get to quietly omit it.

`CHANGELOG.md` is newest first, and each entry carries the same id as its `release` row
(lint 12.15 pairs them in both directions).

## Supersession — never delete

A row is never edited or removed. Something wrong gets a later row that says so, and
both stay. The ledger is append-only for the same reason `inbox/` and `handoffs/` are
immutable: a client's comment resolves against what was actually said at the time, and
rewriting the record makes every past conversation unresolvable.

## Not a git log

Git already records what changed in the code. The ledger records what changed in the
**agreement** — and the two are not the same document. A row whose whole content could
be read off `git log` is a row not worth writing.

## Routing

| Task | Skill |
|---|---|
| Client material arrived | `intake` |
| A package went out, or answers came back | `client-package` |
| A task was finished, documents swept | `sync`, then a `work` row here |
| The folder standard and `ledger.py` itself | `documents` |
