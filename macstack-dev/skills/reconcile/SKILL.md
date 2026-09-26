---
name: reconcile
description: This skill should be used when the user asks to "sync the code and the documents", "синхронизировать код и документы", "актуализировать документы по коду", "обнови документы, код ушёл вперёд", "bring the documents up to date with the code", "make the code match the documents", "everything has drifted, fix it", "полная сверка", or runs /macstack-dev:reconcile. Reconciles the whole macstack/ folder against the source tree in ONE declared direction — the code is master and the documents are corrected, or the documents are master and the gaps become tasks — and touches every document in the contract, not only the generated ones.
---

# Reconcile the whole folder with the code, in one declared direction

`update` closes the loop after a task. `check` reports without writing. This skill is
what you run when **code and documents have drifted apart wholesale** and somebody has
to decide which side is right.

That decision is the entire point, and it is not this skill's to make. `--master` is
**required**: there is no default, because a default is a silent choice of winner, and
every other refusal in this plugin exists to prevent exactly that.

| `--master=code` | `--master=docs` |
|---|---|
| The code is what the product IS. Documents that disagree are **corrected**. | The documents are the contract. Code that disagrees is **work**. |
| Documents get edited, through the gate below. | No document is edited. Disagreements become tasks. |
| Run it after a build phase, when the docs lag behind. | Run it before a client review or a release, when the contract must hold. |

Both directions run the same five stages. Only stage 4 differs — who yields.

## The five stages

### 1 · Measure — `conformance`

One verdict per case id into `history/ledger.jsonl` as `kind: audit`: `implemented`,
`partial`, `absent`, `externally-blocked`, each with its evidence. Nothing later in this
run may claim a case is built without a verdict saying so.

### 2 · Enumerate — `code-audit`

Start from the files and ask the opposite question: what does the code contain that no
document mentions? Three lists — **not in the documents · not in the code ·
contradicts** — sorted by blast radius, never by count.

Read `generated/ARCHITECTURE.md` as the map. A blind recursive grep finds the word
rather than the behaviour, and on an iCloud-backed folder it hangs for minutes.

### 3 · Spec — `sync`

Both halves: the business half against the authored documents, the technical half
against the code. It changes values, never ids — a new entity needs an id, and an id is
a decision.

### 4 · Resolve — the only stage that reads `--master`

**`--master=code`.** Each item on the *contradicts* and *not in the documents* lists
becomes an edit to the client document, applied through the loop `intake` already owns
— delta → ruling → apply → journal. Not a rewrite: `v3` patches the named line and
leaves the surrounding prose alone, which is what keeps three quarters of a client
document intact.

Three things stop an edit and turn it into a question instead:

- **The client answered this statement.** If `history/ledger.jsonl` holds a `comment`
  row from the client against this id, the code does not get to overrule it silently.
  The client said something explicit about this sentence; cancelling that without asking
  is what the ledger and the review package exist to prevent. Collect these and put them
  to the owner.
- **It needs a new id.** Ids are decisions — workflows, tests and prose reference them.
  Report and let a human allocate.
- **It contradicts a recorded ruling** in `history/DECISIONS.md`. A decision is
  overturned deliberately or not at all.

**`--master=docs`.** No client document is edited. Every item on the *not in the code*
list, and every case whose verdict is `absent` or `partial`, becomes a task through
`planning` — with its `Closes` pointer and its acceptance filled by reading the code,
never guessed. A case awaiting a live §A answer does **not** become a task.

### 5 · Settle — identical in both directions

- **Task statuses**, from the verdicts, both ways:
  ```bash
  python3 "${CLAUDE_PLUGIN_ROOT}/skills/planning/references/task_status.py" macstack --apply
  ```
- **Regenerate** `generated/` through `documents`, then re-derive `TEST-CASES.md` for
  the touched ids through `test-cases`.
- **`reviewed` dates** move forward **only for the documents this run actually examined
  against the code**. Marking all six because one was audited is how a document goes
  stale while lint stays green — and it is the difference the session-start hook and
  rule 12.17 both measure.
- **Journal** every edit, and write the `release` entry plus its `CHANGELOG.md` twin
  only for what actually reached users.
- **`lint`** last. A folder that fails lint is not handed to a client.

## Every document, or say why not

The report is a table with **one row per document in the contract** — all seventeen,
not the ones that happened to change. A document with no row is an error, not a
skipped step: "everything is synced" has to be checkable rather than claimed, and the
failure this whole folder exists to prevent is a document nobody looked at.

| Document | `--master=code` | `--master=docs` |
|---|---|---|
| `client/OVERVIEW.md` | corrected where the code contradicts it | contradictions → questions |
| `client/USER-CASES.md` | acceptance bullets corrected to what holds | gaps → tasks |
| `client/UX-UI.md` | screens and prohibitions corrected against the routes | gaps → tasks |
| `client/AUTOMATION.md` | triggers corrected against the schedulers that exist | gaps → tasks |
| `client/HANDBOOK.md` | steps corrected against the interface as built | gaps → tasks |
| `client/OPEN-QUESTIONS.md` | §A the code now answers → proposed for closing; §B whose trigger fired → flagged | unchanged; §B triggers flagged |
| `generated/ARCHITECTURE.md` · `INDEX.md` · `README.md` · `REQUIREMENTS.md` | regenerated | regenerated |
| `generated/TEST-CASES.md` | re-derived for the touched ids | re-derived for the touched ids |
| `history/TASKS.md` | statuses from the verdicts | statuses, plus the new tasks |
| `history/DECISIONS.md` | one ruling per contradiction, `cost-if-wrong` written now | same |
| `history/CHANGELOG.md` | only what reached users, in their words | same |
| `history/ledger.jsonl` | one row per edit, per verdict, per status move | same |
| `inbox/README.md` | untouched — `inbox/` is immutable | untouched |

A generated document is never hand-edited in either direction: it is rebuilt, and lint
12.18 reports the difference if somebody tried.

## What it refuses

- **To run without `--master`.** Print the table at the top and stop.
- **To edit a client statement the client answered**, in either direction.
- **To invent an id**, a milestone, or a tracker item.
- **To move a `reviewed` date for a document it did not read.**
- **To write a task for a case waiting on a live §A id.** The question holds that work;
  the task is written the day the answer lands.
- **To edit code.** Both directions read the source tree. `--master=docs` produces
  tasks, not commits.

## Then

`--master=code` ends at a client review: the documents moved, so
`/macstack-dev:review` shows the client what changed with each statement's history.
`--master=docs` ends at a plan: `/macstack-dev:plan` orders the new tasks, and the
handoff is a coding session, not this one.
