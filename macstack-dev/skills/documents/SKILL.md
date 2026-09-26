---
name: documents
description: This skill should be used when the user asks to "create the macstack folder", "set up project docs", "where do user cases live", "add a screen", "add a trigger", "standardize the project documents", "repair the macstack folder", "migrate docs into macstack", mentions `macstack/`, OVERVIEW, USER-CASES, UX-UI, AUTOMATION, HANDBOOK, OPEN-QUESTIONS, DECISIONS, the client inbox or the document log — and BEFORE any other skill reads or writes anything under `macstack/`. Defines the folder standard AND the document shape: layout, path resolution, ID spaces, the pointer bindings, the bullet-label form, the language rule, the immutability guardrails, rendering and migration.
---

# The `macstack/` folder — standard

`macstack.json` holds the machine-readable facts. Everything a human needs and JSON
cannot hold — what the product is in plain words, cases per role, what each screen
must never show, who does what and what starts it, why a decision was taken and what
it costs if wrong, what is still owed by the client — lives beside it as markdown in
the same folder.

Structure is defined once in
`${CLAUDE_PLUGIN_ROOT}/skills/documents/references/doc-contracts.json`, which both
this skill (the writer) and `lint` (the checker) read. Never restate that file's
anchors, YAML keys or ID patterns from memory — open it.

**Shape before content:** read `references/format-rules.md` before writing a single
line. A client document is headings and bullet lists — nothing else. No fenced blocks,
no tables, no journal section. The machine half lives in `macstack.json`, and each
entity carries an invisible pointer to it. A document written in the v1 table shape or
the v2 yaml shape passes no check in this plugin.

## Layout

```
macstack/
├── README.md          the map — six entries in this folder, this is the first  [generated]
├── macstack.json      the spec — machine-readable facts, always English
│
├── client/            WHAT A HUMAN WRITES AND A CLIENT READS — the source of truth
│   ├── OVERVIEW.md            the product, its goals, who it is for, the glossary
│   ├── USER-CASES.md          what a person must get, per role, with its UX bar  ← the bar
│   ├── UX-UI.md               the interface bar, then per screen what must NOT be visible
│   ├── AUTOMATION.md          trigger → task → workflow → role
│   ├── HANDBOOK.md            how to actually work with the platform
│   └── OPEN-QUESTIONS.md      §A owed by the client · §B deferred by us
│
├── generated/         BUILT FROM A SOURCE — never edited by hand
│   ├── ARCHITECTURE.md        how it is built, from macstack.json
│   ├── TEST-CASES.md          how each acceptance bullet is verified
│   └── INDEX.md               every case, screen and trigger, plus the coverage count
│
├── inbox/             WHAT THE CLIENT SENT, exactly as sent · README.md = manifest
│
└── history/           JOURNALS AND RECORDS
    ├── ledger.jsonl · TASKS.md · DECISIONS.md · CHANGELOG.md
    └── handoffs/ · archive/
```

**Six entries in the root, and the count is a constraint.** The field's own criticism
of spec-driven tooling is that a specification spread over many files becomes more
tedious to review than the code it describes. A fifth folder needs an argument that
beats that.

`docs/` stays the **engineering** folder — `architecture.md`, `api-conventions.md`,
`code-style.md`, deployment runbooks do not move here. `macstack/` must stay a folder
you can hand to a client whole.

There is no physical client/technical split beyond these four: the documents cross-cite
each other constantly, and more trees would multiply every relative link. Audience is
declared in `docs.files.<key>.audience` and in the `-business.md` suffix, not in the
path. `docs.files.<key>` uses the document keys from `doc-contracts.json` — `overview`,
`user_cases`, `ux_ui`, `automation`, `handbook`, `open_questions`, `test_cases`,
`architecture`, `index`, `readme`, `tasks`, `decisions`, `changelog`, `log` — not
filenames.

## The six client documents

Each answers one question, and none answers another's.

- **`OVERVIEW.md`** — *what is this and who is it for.* Goals, the audience, the
  high-level processes, the invariants, what the platform refuses to do, and the
  glossary that fixes the English terminology. It **names** the roles and points at
  `AUTOMATION.md`; it does not define them. Splitting a role's definition across two
  documents is how the two start disagreeing.
- **`USER-CASES.md`** — *what a person must be able to get.* Per role, with a priority,
  its own experience requirements and an acceptance list whose bullets are individually
  addressable. The acceptance bar for everything downstream.
- **`UX-UI.md`** — *what the interface must be.* Cross-cutting first — navigation,
  empty/loading/error states, responsive behaviour, accessibility, tone — then per
  screen: what is on it, what can be done, and what must **not** be visible there. A
  prohibition written per screen is checkable by opening that screen; the same
  prohibition written once in `USER-CASES.md` is a rule somebody has to remember to
  apply on fifty-seven routes.
- **`AUTOMATION.md`** — *what happens by itself, and who is responsible.* The universal
  trigger → task → workflow → role model. A trigger declares both its `type` (the
  mechanism) and its `source` (interface · backend · integration · schedule · manual),
  because the client cares about the second and the engineer about the first, and
  neither implies the other.
- **`HANDBOOK.md`** — *how a person actually uses it on a Tuesday.* Seeded from the
  cases and screens, then written by a human. This is the document the client's own
  staff reads, and it is the reason the case documents can stay abstract.
- **`OPEN-QUESTIONS.md`** — *what is not decided, and by whom.* §A owed by the client,
  §B deferred by the team with the trigger that ends the deferral.

## Path resolution

Resolve once, at the start of every operation, in this order:

1. `<repo>/macstack/macstack.json` — canonical.
2. `<repo>/macstack.json` — legacy. Works, but say so and offer migration mode.
3. Search upward from cwd to the git root.

**Both 1 and 2 present is an ERROR**, never a silent choice — two specs mean two
truths. Report both paths and stop: the remedy is migration mode, which relocates the
legacy root file into the folder (or `git rm`s it once the moved copy is verified).

## The id prefix names the file

An id is read by a person before it is read by a program, and the person's first
question is always "which file is that in". So the prefix answers it:

| Prefix | Kind | File |
|---|---|---|
| `CC-14` `CT-19` `CO-16` `CX-03` `CZ-14` `CS-04` | case | `client/USER-CASES.md` |
| `QA27` `QB3` | open item | `client/OPEN-QUESTIONS.md` |
| `D58` | decision | `history/DECISIONS.md` |
| `M15` `M15-T11` `BL-7` | milestone · task · backlog | `history/TASKS.md` |
| `R-2026-08-28` | release | `history/CHANGELOG.md` |

The **first** letter names the file; the **second** narrows the kind — the role a
case belongs to (`C` coach, `T` training centre, `O` admin, plus the reserved
`X` cross-cutting, `S` scenario, `Z` prohibition), or who owes an open item (`A`
the client, `B` us, deferred).

`M15-T11` is the one that looks like an exception and is not: `M` names the
MILESTONE and `T` names the task inside it, so the id reads "task 11 of milestone
15" and both live in `TASKS.md`. The form is deliberate — a commit subject ending
`(M15-T11)` links the commit to the task for free.

**One-letter case ids and un-prefixed open items are LEGACY.** `C-14`, `T-19`,
`A27` are still accepted so that projects already under way keep linting, and
every reader of an old document keeps finding what it cites. They are not written
any more. The old form had two defects a reader hit immediately: nothing in `A27`
said which file to open, and `T` meant a training-centre case in `T-19` and a task
in `M15-T11` — the same letter, two spaces, no way to tell them apart by looking.

To convert a project: `python3 references/migrate_ids.py <root>` shows the change,
`--apply` writes it. It renames only ids DECLARED as headings in the two client
documents — never a look-alike from someone else's paper, and never anything under
`inbox/` or `history/handoffs/`, which are immutable and already in the client's
hands.

## Ten invariants

1. **`inbox/` is immutable.** Never edit, rename or delete anything in it. A source
   already committed in this repo at a stable path is **not copied** into `inbox/` —
   cite it by path. A copy diverges from its original with the first edit, and an
   immutable zone cannot be fixed afterwards. The one writable file is
   `inbox/README.md`, the manifest.
2. **ASCII only** in `inbox/` filenames and inside every ID token. Refuse at the
   moment of adding: the zone is immutable, so a bad name can never be corrected.
   Watch the homoglyphs: U+041A CYRILLIC CAPITAL KA renders identically to ASCII `K`,
   so an id typed with it greps as absent and silently breaks every cross-reference
   check. Same trap with А О С Е Р Т Х. Verify the codepoint, not the glyph.
3. **Anchors, not headings.** Every section and every entity is marked by an HTML
   comment on the line above it (`<!-- macstack:case=C-04 -->`,
   `<!-- macstack:acceptance -->`). Headings and prose are written in `docs.language`;
   **anchors and YAML keys are never translated** — the checker greps the anchor, which
   is what makes the folder language-independent. Re-insert missing anchors
   idempotently; a stripped anchor is never a reason to rewrite the document.
4. **Closed items are struck, not deleted:** `~~A6~~ · CLOSED D14, 2026-08-24`.
   Numbers are never reused.
5. **No line-number pointers.** Never `src/foo.ts:214` — cite a symbol name or a test
   title. Line numbers rot the moment the file above them grows, and a pointer at a
   closing brace is worse than none because it reads as authoritative.
6. **A delta is not a spec.** It names its bar (`USER-CASES.md`) and stays the history
   of an analysis.
7. **A generated document is never edited by hand.** `README.md`,
   `generated/ARCHITECTURE.md`, `generated/INDEX.md` and `generated/TEST-CASES.md`
   carry a `generated` banner naming their source and are rebuilt by `render.py`. A
   hand edit is lost on the next render, and lint reports the difference (12.18)
   rather than quietly overwriting it. What a human needs to add about a generated
   subject belongs where the source points back: architecture arguments and measured
   traps in `docs/architecture.md`, what a role MEANS to a person in `USER-CASES.md`.
8. **Every living document carries a journal, and every edit writes a row.** Client
   documents carry `version | date | what changed | source`; internal ones carry
   `date | what changed`. An edit appends a row **and** bumps the version in three
   places that must agree — the header anchor, the last journal row, and
   `docs.files.<key>.version`. Write-once documents — rulings, reviews, deltas, the
   inbox manifest — carry none: their date is in the filename, and editing one of them
   is itself the defect.
9. **The client's documents are the SOURCE, not an output.** `AUTOMATION.md` and
   `UX-UI.md` were generated from `macstack.json` until the direction was inverted. A
   client cannot correct a generated file, and the client is the one who knows whether
   a task belongs to a role or whether a number may appear on a screen. Now they are
   authored, their entity blocks are the machine source, and `sync` reconciles the
   spec's business half against them. What is not derivable from any client document —
   code paths, engines, entities, software, implementation status — stays the
   architect's and is never written by that tool.
10. **`reviewed` is not `updated`.** `updated` is when the text last changed;
   `reviewed` is when the document was last checked AGAINST THE CODE. Only the second
   one expires (`freshness_days` on the document, else `docs.freshness_days`, else
   30), because only the second one is a claim about the world. A document can be edited daily and be wrong the whole time.

## Who owns what

`macstack.json` owns the ID-space binding and machine-readable state. The markdown owns
the text and allocates the IDs. A copy is permitted only where a machine can prove it
is still a copy.

| Concern | Owner | The other side holds |
|---|---|---|
| Role definition | `AUTOMATION.md` | `roles[]` id, acl, isolation; joined via `roles[].cases` |
| What a person gets | `USER-CASES.md` | `TEST-CASES.md` verifies each acceptance bullet by its id |
| What a screen shows and hides | `UX-UI.md` | `interfaces[]` id, name, path, roles |
| What starts what | `AUTOMATION.md` | `triggers[]`, `processes[].tasks[]`, `workflows[]` name and trigger |
| How a bullet is checked | `TEST-CASES.md` | ids carry the bullet they verify (`C-06.T3` covers `C-06.a2`) |
| What will be done, in what order | `TASKS.md` | `lifecycle.next_steps[]` and `milestones[]` as pointers; every task also lives in the team's tracker |
| What happened | `ledger.jsonl` | one row per edit and per client comment, keyed by the id of the thing that changed |
| What reached the client | `CHANGELOG.md` | curated from the log's `work` and `release` entries; never a commit history in disguise |
| Open questions | `OPEN-QUESTIONS.md` | `lifecycle.open_questions[]` as pointers |
| Owed by the client | `OPEN-QUESTIONS.md §A` | `lifecycle.needs_from_client[]` — a **derived view**: live §A client items only |
| Decisions | `DECISIONS.md` | registry and argument in one file; `lifecycle.decisions[]` points here by id |
| Prose, rationale, cost-if-wrong | markdown | JSON never |

Pointer form carries no prose, so there is nothing to drift. Where a human genuinely
needs text in the JSON, an optional `summary` (≤200 chars) **must equal the first
sentence** of its markdown item — mismatch is an ERROR, not a warning.

### Who may write into `client/`

A client document is not read-only, and it never was — `intake` has always edited it.
What has never been allowed is editing it **silently**. The rule is about the gate, not
about the file:

> Every write into `client/` passes delta → ruling → apply → journal, whoever proposed
> it — the client, the code, or a person. An edit with no ledger row keyed by the id
> that changed is a defect, and lint 12.36 says so.

Two skills own gates onto that loop, and no third writes there: **`intake`** for
material the client sends, **`reconcile`** for what the code turns out to say. Both use
the `v3` writer, which patches the named line and leaves the surrounding prose alone —
on the live corpus the model sees 955 of 3837 lines, so a tool that rebuilt the file
from its model would destroy three quarters of the client's document.

Three things stop a write and become a question instead, in either direction:

- **The client answered this statement.** A `comment` row against that id means they
  said something explicit about that sentence. Overruling it without asking is what the
  ledger and the review package exist to prevent.
- **It needs a new id.** Ids are decisions; workflows, tests and prose reference them.
- **It contradicts a ruling** in `history/DECISIONS.md`. A decision is overturned
  deliberately or not at all.

`generated/` is the opposite case: never hand-edited by anyone, rebuilt from its source,
and lint 12.18 reports the difference if somebody tried.

## Language

Read `docs.language` (ISO 639-1) from the spec; absent means English. Per-document
override lives in `docs.files.<key>.language`. Write headings and prose in that
language. Never translate: anchors, YAML keys, ID tokens, `docs.*` field names,
statuses, enum values, or anything inside `macstack.json`. For a document with
`audience: client`, confirm the output language before writing.

Terminology stays English even in a Russian document, and the mapping is collected in
the `glossary` section of `OVERVIEW.md`. Lint measures the ratio and errors past 15%.

## Creating or repairing the folder

1. Resolve the spec; read `docs.root` (default `macstack`), `docs.language`,
   `docs.files`. If the spec resolved to the legacy root path, create the folder
   around it as-is and report that relocating it is migration mode's job — do not
   move it here.
2. Create only what is missing — **never overwrite an existing document.** For a file
   that exists but lacks anchors or sections, add what is missing in place and report
   it; do not regenerate. Materialize eagerly: every document in the contract whose
   `path` is a fixed name, plus `inbox/` with its manifest. Create `handoffs/` and
   `archive/` **lazily, on first use** — git does not
   track an empty directory, so creating them up front either leaves untracked empties
   that vanish on clone or scatters four `.gitkeep` files. Their absence in a fresh
   folder is correct, not a gap; lint must not report it.
3. Seed each document from `doc-contracts.json`: the required anchors, the section
   headings in `docs.language`, and a one-line placeholder saying what belongs there.
   Seed `USER-CASES.md` role sections from `roles[]`, and back-fill `roles[].cases`
   with the matching ID prefix.
4. **Seed the authored client documents once, then hand them over.** `seed.py` writes
   a first `AUTOMATION.md`, `UX-UI.md` and `HANDBOOK.md` from what the spec and the
   cases already know, and REFUSES to overwrite them afterwards. A blank page is a bad
   start when the spec already knows the roles and the routes; a machine guess written
   over a client's correction is worse.
5. **Render the generated documents** with `render.py` — `README.md`,
   `generated/ARCHITECTURE.md`, `generated/INDEX.md` — never by hand.
6. Scaffolding does not write to `ledger.jsonl`. That ledger records material coming in,
   work done and things going out; a freshly created folder has no entry, and that
   absence is correct, not forgotten.
7. `.gitignore` — leave `inbox/` committed (an immutable zone must be durable).
   Respect the existing `*.local.md` convention for sensitive companions.
8. Add the `docs` section to `macstack.json` if absent, then run `lint`.

Prototypes may seed `macstack/README.md` and nothing else — a parent's cases and open
questions are not this project's.

## Rendering

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/documents/references/render.py" macstack [--date YYYY-MM-DD] [--check]
python3 "${CLAUDE_PLUGIN_ROOT}/skills/documents/references/seed.py"   macstack [--force]
```

`render.py` is deterministic by design: lint 12.18 re-renders and compares, so a
renderer whose output varies between runs would make that rule permanently red.
Everything is a pure function of the source — no timestamps in the body, no hash-order
iteration, no prose invented at render time. The one exception is the journal, which
is human history: rows are read back out of the existing file and carried forward, and
a new row is appended only when the rendered body actually changed. That is what keeps
a second run byte-identical to the first.

`--check` renders into memory and reports differences without writing. A difference is
exactly one of two things — somebody edited the rendered file by hand, or the source
moved and nobody re-rendered — and both are the same defect from the reader's side, so
both are reported, naming which.

## Migration mode

Two conversions, both destructive, both gated. Run them on a branch.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/documents/references/migrate.py" <repo> [--apply]
```

Without `--apply` it is a dry run and writes nothing.

**Layout migration** moves an existing `docs/`-era or flat `macstack/` into the four
folders with `git mv`, recomputing every relative link against the old location, and
relocates a legacy root `macstack.json`.

**Format migration** converts v1 table-shaped documents into v2 entities. Per the
conversion checklist in `references/format-rules.md`:

- one row becomes one entity; the first column becomes the id and the title;
- short factual columns become YAML keys, long prose columns become anchored sections;
- a column holding the same value on every row is stated once in the section intro and
  dropped — a live `ARCHITECTURE.md` had three such columns, `payload` fifteen times,
  `custom` seventeen times, `—` six times;
- an index table above the entities is deleted, not converted: it regenerates;
- `BUSINESS-LOGIC.md → OVERVIEW.md`, `SCREENS.md → UX-UI.md`,
  `ROLES-AND-TASKS.md → AUTOMATION.md`, and `HANDBOOK.md` is seeded empty;
- one journal row is appended saying the document was converted, and the version is
  bumped in the header, the journal and `docs.files`.

**Gates.** Show the diff of the first converted document and stop for confirmation
before converting the rest. Never convert and commit in one step: the whole point of
the dry run is that a human reads the first conversion before trusting the other
nineteen.

## Routing

| Task | Skill |
|---|---|
| How a document is shaped | `references/format-rules.md`, in this skill |
| Client material arrived, or "improve X" | `intake` |
| Turn the acceptance bullets into checks | `test-cases` |
| Plan work, or reconcile with the tracker | `planning` |
| Record what was built, or cut a release | `journal` |
| Reconcile the spec with the documents and the code | `sync` |
| Check the implementation against the documents | `conformance` |
| Hand the client something to correct | `client-package` |
| Validate the folder and the spec, or ask where we are | `lint` |
| The spec itself | `spec-authoring` |
