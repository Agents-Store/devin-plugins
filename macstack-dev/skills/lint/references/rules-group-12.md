# Rule group 12 — the `macstack/` folder, rule by rule

Forty-one rules, `12.0`–`12.40`. Each one is a program: they live in
`lint_folder.py` and the `rules_*.py` modules beside it, which register themselves on
import. **A rule described here and not implemented there is not a rule** — 12.36 stood
in this file for three releases with no code behind it, and nothing said so. A
three-line cross-check now compares `@rule(...)` in the code against this list.

Read the shape from
`${CLAUDE_PLUGIN_ROOT}/skills/documents/references/doc-contracts.json` — every rule
here is checked against that file, never against memory.

## Contents

- Layout and identity — 12.0 · 12.1 · 12.2 · 12.3 · 12.4 · 12.5
- Content and truth — 12.6 – 12.27
- Shape, pointers and language — 12.21 · 12.24 · 12.28 – 12.35
- Prose the client reads — 12.30 · 12.33 · 12.37
- The folder around the documents — 12.36 · 12.38 · 12.39 · 12.40

Numbers are historical, not thematic: a rule keeps the number it was born with, because
a renumbering breaks every report, every commit message and every LEARNINGS entry that
ever cited one.

---

### Layout and identity

12.0 **A declared entity kind is actually found** — for every entity kind the
     contract declares in a document, the loader returns at least one. This rule
     protects the other thirty-eight from the failure that keeps recurring here: a
     filter that matches nothing returns an empty list, thirty-five rules run over it,
     and every one of them passes. A green report and a broken folder look identical.
     It has fired for real: after the schema gave cases their own records and the
     pointers were repointed from `roles[].cases` to `cases[id=…]`, the kind filter
     still matched the old collection and silently returned zero.
     Any rule that can return "nothing to check" must be able to tell that apart from
     "checked, and it was fine" — otherwise it is decoration.

12.1 **Layout** — `docs.root` resolves and holds exactly SIX entries: `README.md`,
     `macstack.json` and the four folders `client/`, `generated/`, `inbox/`,
     `history/`. Dot-files do not count — `.DS_Store` and friends are the operating
     system's litter, not the project's documents, and failing a folder for them
     teaches people to ignore the rule. A seventh real entry is an error, not a
     preference. Every document in the contract whose `path` is a FIXED NAME exists at
     that path. Documents whose `path` carries a `<placeholder>` (`delta`, `rulings`,
     `review`) are dated instances, not required files — their directories are created
     lazily and their absence in a fresh folder is correct.
     **`docs.files` must name every fixed-path document.** Checking only that the
     entries present resolve is a rule that passes in a vacuum: `docs.files` is
     authored, so naming nothing at all used to approve an empty folder.
     Exactly one `macstack.json` in the repo.
12.2 **Headers and pointers** — each document carries its `<!-- macstack:doc= -->`
     header, and every entity heading carries a `<!-- macstack:ref= -->` pointer unless
     its contract puts it in the reserved `none` class. The per-kind anchors of v1 and
     v2 (`macstack:case=`, `macstack:screen=`) are gone: there is one pointer form, and
     what it means is decided by the binding its contract declares — see 12.28 and 12.29.
12.3 **ID integrity** — unique per space; ASCII-only inside an ID token — the homoglyph
     rule: a Cyrillic capital KA (U+041A) renders exactly like `K` (U+004B), greps as
     absent and silently breaks every cross-reference check, so compare codepoints
     rather than glyphs; no gaps in D-numbering; A/B numbers never reused after a
     strike.
12.4 **Cross-file refs** — every `D<n>` cited anywhere resolves in `DECISIONS.md`;
     every `A<n>` **and every `B<n>`** in `lifecycle.*` resolves to a live item; every
     `roles[].cases` prefix yields ≥1 case heading; every case-section letter maps to
     exactly one role; every `<case>.T<n>` carries a case that still exists; every
     `covers` in `TEST-CASES.md` names an acceptance id that still exists; every
     `blocked_by` in `TASKS.md` resolves to a live task or open item; every `screens`
     entry in a case resolves to a screen in `UX-UI.md`; every `triggers` entry
     resolves to a trigger in `AUTOMATION.md`.
12.5 **Checked copies** — `open_questions[].summary` equals the first sentence of its
     markdown item; for every versioned document, `docs.files.<key>.version` equals the
     version in the document's own header. Two places now, not three: the journal row
     was the third, and client documents no longer carry a journal (12.33).
     The old three-way check passed on a document declaring `version=3.0` in its header
     and "Версия 1.8" in its body, because the journal matcher only recognised one row
     shape and the v3 rows were invisible to it. A comparison that cannot see one of its
     operands reports agreement.
12.6 **`needs_from_client` is a view** — contains no closed items, omits no open §A
     client item.

### Shape (v3)

12.21 **Entities parse** — every entity heading matches its contract's `id_pattern`,
      carries every `bullets_required` label for its kind and no label the contract
      does not declare for it, and carries every `prose_required` block — with the
      conditional sets applied by the entity's own values. `bullets_conditional` reads
      "required unless": a screen must name its roles unless it declares itself public.
      `prose_required_except_prefix` reads by id: a `Z-` prohibition needs no acceptance
      list, because it states what must be refused and the refusal is the behaviour.
      `bullets_forbidden` is the mirror image: a case may not carry a `role` bullet,
      because the role is already the pointer one line above, and a second copy of a
      fact is the hand-maintained duplicate 12.27 exists to stop.
      Two formats died to get here. v1 read table columns BY POSITION — deliberately,
      because a header follows `docs.language` — and every paragraph that needed to sit
      near the machine moved into a cell. v2 replaced the grid with an anchor plus a
      fenced yaml block, and left markdown, yaml and tables stirred together in one
      file. v3 keeps the language independence and drops the machine syntax entirely.

12.28 **Every pointer resolves** — every `<!-- macstack:ref=P -->` resolves to a live
      path in `macstack.json`. `coll[]` is the whole collection; `a[].b[]` is the union
      of `b` over every `a`. Name the file, the line and the first segment that failed.

12.29 **The pointer binds the way its contract declares** — and this is the rule that
      looks simpler than it is. `identity`: the last `[id=…]` equals the heading id.
      `member`: the heading id satisfies the glob at the pointed path. `container`: the
      pointed entry exists and the heading id is unique in the document. `none`: no
      pointer at all, and the id prefix is one the contract reserves.
      Measured on a live project: AUTOMATION.md is 49 headings, 49 pointers and 49 id
      matches; UX-UI.md is 37 screens onto 9 `interfaces[]` entries; USER-CASES.md is 78
      headings, 51 pointers, 3 distinct targets and **zero** id matches, because
      `roles[].cases` holds the glob `"C-*"`. Assume identity is the only binding and
      one of two things follows: somebody invents 28 spec entries that nothing else
      references in order to satisfy the linter, or the rule is downgraded to a warning
      and stops catching the genuinely broken pointer in the document where it was true.

12.30 **A client document is headings and bullets, and nothing else** — zero fenced
      blocks, zero table rows, zero HTML other than the two macstack comments, no
      heading deeper than `####`. Applies to every document whose audience is `client`
      **or `both`**. There is no budget here and no exemption; 12.24's budget survives
      only where the reader is a machine or a programmer.
      `both` is not a loophole: OPEN-QUESTIONS.md is `both` because §A is owed by the
      client and §B is the team's, and classifying it that way quietly exempted it from
      every rule protecting the client's reading. It carried a journal for weeks.

12.31 **Every bullet label is declared** — `- **X:**` reverses through
      `fields.*.label`, `label_by_kind` or `label_aliases` for the document's language.
      An undeclared label is prose that happens to be bold, and the parser leaves it as
      prose rather than inventing a field from it — but the linter says so, because the
      alternative is a key in the model that nothing reads.
      This fired 103 times on first run against a corpus everyone believed was clean:
      the shipped table said "что требуется от человека" while all 33 live bullets say
      "что от человека требуется" — the same words, transposed.

12.33 **A client document carries no journal** — no `## История изменений` section and
      no `- **Версия N · date**` row. History lives in `history/`, and the client sees
      it per statement in the review package rather than as a wall of versions at the
      bottom of every document.

12.34 **Pointer uniqueness** — no two headings share an `identity` pointer. A
      `container` pointer may repeat; that is what makes it a container.

12.32 **Acceptance ids are stable** (warning) — a case's acceptance bullet count is
      not below what it was at the last tag unless the document version was bumped.
      The ids are positional within their entity, so inserting a bullet above an
      existing one moves every id below it — and a client quoting `C-04.a2` from an
      email last month then lands on a different sentence. When there is no tag to
      compare against, the rule reports nothing and says so rather than guessing.

12.35 **`generated/` carries everything `client/` says** — every id appearing in a
      client document also appears in `generated/REQUIREMENTS.md`, and the acceptance
      bullet counts match. This is what makes "absolutely all of it, in machine form"
      a check instead of a promise. While `REQUIREMENTS.md` does not exist, the rule
      emits one finding saying so — not one per id.

12.36 **A document that moved has a row in the ledger** — an authored client
      document declaring a version in its header has at least one row in
      `history/ledger.jsonl` that names it. The ledger is what lets the review package
      show a client, per statement, what moved since they last read it and what they
      said about it; an edit with no row means the next package presents a changed
      sentence as if it had always said that.
      What this checks and what it does not: it compares the document against the
      ledger at file granularity, not edit by edit — proving that EVERY individual
      edit was recorded would need the git history, and a rule that claims more than
      it measures is worse than no rule. Generated documents are exempt: their edits
      belong to their generator, and 12.18 covers those.

12.37 **The first bullet is not the heading again** — an entity whose opening bullet
      restates its own title makes the client read the same sentence twice. Twenty-two
      of thirty-six blocks in one live document did exactly that.

12.38 **`client/` holds documents, and nothing else** — any file there that is not one
      of the six is incoming material: a client's own draft, a screenshot, a `.docx`
      saved beside the documents. Its place is `inbox/`, where it is immutable and has
      a manifest row, and from there `/macstack-dev:intake` merges it.
      Leaving it in `client/` creates a seventh document that no renderer, no package
      and no spec knows about — and a month later nobody can say whether it is a
      source of truth or somebody's draft.

12.39 **A workflow's `source` path still exists** — `workflows[].source` says where the
      workflow lives in code. Rename or delete the file and the field stays behind, and
      the next audit reports green against a path that is gone. An empty `source` is not
      an error — the workflow may not be written yet; a filled-in wrong one is.
      The field exists because names do not bridge the two sides: measured on a live
      project, code names a workflow for its domain and the spec for its step, and only
      3 of 17 match. A link that cannot be derived has to be stored, and a stored link
      has to be checked — otherwise it is worse than none, because it is believed.

12.40 **The project tells its agents when to update the folder** — `CLAUDE.md` and
      `AGENTS.md` each name `/macstack-dev:update` and `/macstack-dev:intake`, not just
      the path to `macstack/`. A block that says "read macstack.json first" and stays
      silent about what to do afterwards produces an agent that reads the folder and
      lets it go stale. "Keep the documents current" with no trigger and no command
      named is a wish, not an instruction.
      Two command names, not the whole table: wording gets rewritten, and a rule that
      quibbles about phrasing gets routed around. These two are what keep the folder
      updated at all. Both files, because the documents are read by whichever agent the
      team runs — a specification only Claude Code can find is one half the team cannot
      use.


12.24 **Tables stay inside the budget** — in `history/` and `generated/` only; in
      `client/` a table is an error outright (12.30). At most 4 columns, at most 80
      characters a cell, at least 3 rows, and no `<br>`, bold, code fence or pipe
      inside a cell. Report the file, the table's anchor or heading, the column
      count and the longest cell verbatim, because "this table is too wide" is not
      actionable and "cell 4 of row 12 is 876 characters" is.
      The budget exists because every oversized table measured in the field started as
      a reasonable one and grew a paragraph at a time.
12.25 **The document is written in its declared language** — measure the ratio of
      letters from the wrong alphabet outside code spans, YAML blocks, anchors and ID
      tokens against `docs.files.<key>.language` or `docs.language`. Past 15% it is an
      ERROR for a document whose `audience` is `client`, a WARNING otherwise, and **not
      measured at all for a `generated` document**. The severity split is the whole point:
      the rule exists so the client can read the documents written for them. An internal
      journal drifting into English costs nothing; a client document doing it costs the
      review. A generated document is exempt because its body is identifiers — software
      ids, entity names, workflow names — which the language rule forbids translating, so
      measuring it would demand the one thing the standard prohibits.
      Terminology is excluded by the measurement, not by an exception list: it sits in
      code spans, YAML blocks and ID tokens, all of which are stripped before counting.
      Anything a renderer emits that IS an identifier must be backticked for the same
      reason — an unquoted workflow name put a generated index at 45% foreign when every
      Russian word in it was Russian.
      A live project ran `docs.language: ru` with one client document 100% English and
      another at 21% Cyrillic — Russian headings over an English body copied out of the
      spec. Both read as finished documents and neither was one.
12.27 **No hand-written index** — an authored document contains no index, summary or
      coverage table of the entities below it. It is a second copy that drifts the
      first time somebody edits one and not the other: a live `USER-CASES.md` printed
      all 63 of its cases twice, once as index rows and once as headings, with zero
      divergence — 15% of the file existing only to be kept in sync by hand. Indexes
      live in `generated/INDEX.md`.

### Content and truth

12.7 **Inbox hygiene** — ASCII-only filenames; every inbox file has an entry in
     `inbox/README.md`; no content-modifying commit has touched an inbox path after
     its add commit.
12.8 **No rotting pointers** — no `path.ext:NNN` line-number citation anywhere under
     `macstack/`; no link resolving outside the repo root.
12.9 **No secrets anywhere under `macstack/`** — extends rule 10 past
     `resources.accesses`.
12.10 **No parallel spec** — a delta older than 30 days with neither an applied
      banner nor a superseded note.
12.11 **Every acceptance bullet is verified** — each acceptance bullet in
      `USER-CASES.md` is covered by at least one test in `TEST-CASES.md`, matched by
      the bullet's id. An uncovered bullet is an unverified promise; that is the whole
      point of the document.
12.12 **Test cases are well formed** — every test declares `covers` and `kind`; a
      `manual` test also declares preconditions and steps; an `auto` test names the
      test title that proves it (a bare filename is not evidence, and a `file.ts:NNN`
      pointer is already banned by 12.8); a struck test states why.
12.13 **The journal is typed** — every `history/ledger.jsonl` row declares a `kind` and carries
      that kind's required fields and sections per the contract. There is one shape,
      keyed by kind: v1 declared a flat six-field requirement AND a per-kind table that
      disagreed with it, so a `work` entry was contractually required to carry a
      `delta`.
12.14 **Every task is tracked in both places** — every task in `TASKS.md` declares a
      `tracker` id. The file is the source of truth for what the work IS; the team's
      tracker is where the conversation about it happens, and a task in only one of
      them is a task half the team cannot see. Also: `status` declared and one of the
      five; a struck task states why.
12.15 **A release is paired** — every `release` row in `history/ledger.jsonl` has a `CHANGELOG.md`
      entry with the same id, and every `CHANGELOG.md` entry has its `release` entry in
      the log. `CHANGELOG.md` is ordered newest first.
12.16 **Milestones are falsifiable** — every milestone declares a non-empty
      `done_when`, and a milestone marked `done` has every check recorded as met. A
      milestone whose tasks are all `done` but whose checks are not recorded is not
      done — it is unverified.
12.26 **A finished task left a trace** — every task at `done ✓` is named by a `work`
      row in `history/ledger.jsonl`. Without this the closing half of the loop is unenforced: a
      task can be marked done, the documents never re-checked, and every staleness
      rule below stays quiet because nothing recorded that anything happened.
12.17 **Documents have a shelf life** — every document with a `docs.files` entry
      carries `reviewed`, the date it was last checked AGAINST THE CODE. Past its
      budget it is a WARNING; past twice that, an ERROR. The budget resolves per
      document — `docs.files.<key>.freshness_days`, then the folder-wide
      `docs.freshness_days`, then 30 — so a business-logic document can outlive a
      user-cases document instead of both sharing one number that fits neither. An
      `audit` row in the ledger (or an archived `reviews/<date>-*-conformance.md`)
      dated later than `reviewed` counts as the check and moves the date forward. The
      date and the budget are computed by `hooks/macstack_freshness.py`, which the
      session-start hook calls too — a second copy here once told the user something
      the hook contradicted. This is the one rule aimed at the failure the whole
      folder exists to prevent: a document that reads perfectly and describes a system
      that no longer exists. Everything else here checks shape; this checks that truth
      has been looked at recently.
12.18 **A generated document equals its source** — for every document whose contract
      carries `generated`, re-render and compare. A difference is an ERROR and is
      exactly one of two things: somebody edited the rendered file by hand, or the
      source moved and nobody re-rendered. Both are the same defect from the reader's
      side — the document lies — so both are reported the same way, naming which. The
      remedy is a re-render, never a hand fix.
      This now includes `README.md` and `generated/INDEX.md`. v1 declared `README.md`
      generated and shipped no generator for it, which made this rule unsatisfiable for
      that document across three releases.
12.19 **The journal is not empty** — a document whose contract declares a `journal`
      section has at least one row in it, and no row is dated later than the document's
      `updated`.
12.20 **Every handoff is recorded** — each file in `handoffs/` has a `handoff` entry in
      `history/ledger.jsonl` naming it, and each `handoff` row names a file that exists. The mirror
      of 12.7 for the outbound direction: when the client's edits come back, the only
      way to know WHICH version they reviewed is that entry. An artifact handoff also
      records its URL and version label.
12.22 **The spec agrees with the client's documents** — `sync` reports no disagreement
      between `client/AUTOMATION.md` and the business half of `macstack.json`: same
      roles, same human tasks, same gates, same triggers. A spec that disagrees with the
      document the client signed off on is the failure the whole folder exists to
      prevent. Additions and removals are ERRORS here even though `sync` will not apply
      them: they mean a human still owes an id.
12.23 **Every screen is declared** — every `interfaces[]` entry a person opens (`web`,
      `admin_ui`, `dashboard`, `approval_center`, `form`) has an entity in
      `client/UX-UI.md`, and every screen's `path` belongs to a declared interface. The
      `forbidden` section is non-empty wherever the project declares a prohibition
      touching that role — an empty one there is a promise nobody checked.

