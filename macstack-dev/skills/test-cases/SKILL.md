---
name: test-cases
description: This skill should be used when the user asks to "make test cases", "составить тест-кейсы", "generate tests from the user cases", "как это проверять", "написать сценарии проверки", "acceptance checklist", "what do we test for C-04", "обновить тест-кейсы под новую версию кейсов", or wants a QA/acceptance plan derived from USER-CASES.md, AUTOMATION.md and UX-UI.md. Derives TEST-CASES.md from the acceptance bullets, triggers and screen prohibitions of those three documents — one test per claim, each tagged auto or manual — and keeps them in step.
---

# Test Cases — derived from the verifiable claims

Documents form a chain, and this one is the middle link:

| Document | Answers |
|---|---|
| `client/USER-CASES.md`, `client/AUTOMATION.md`, `client/UX-UI.md` | What must be true for a person, a schedule/event, or a screen — the bar |
| **`generated/TEST-CASES.md`** | **How each of those statements is verified** |
| `history/reviews/*-conformance.md` | What was actually found the day someone checked |

`TEST-CASES.md` is standing and versioned; a review is dated and disposable. Never
merge them, and never let a review become the only place a check is written down.

Open `${CLAUDE_PLUGIN_ROOT}/skills/documents/references/doc-contracts.json`
(`documents.test_cases`) for the anchors, the id pattern and the required item fields.
Headings and prose follow `docs.language`; anchors, ids and YAML keys never translate.

## The derivation rule — three sources, not one

**Every verifiable claim gets at least one test.** A claim with no test is an
unverified promise, and lint reports it. Three documents make verifiable claims,
and each feeds a different part of `TEST-CASES.md`:

- **`client/USER-CASES.md`** — every acceptance bullet under a case's `acceptance`
  section is a claim: what must be true for the person once the case is done.
- **`client/AUTOMATION.md`** — every entry in `triggers` is a claim: what must
  fire, and when — on a schedule, on an event, on a form submit. A trigger that
  never gets exercised is as unverified as an acceptance bullet nobody checked.
- **`client/UX-UI.md`** — every line under a screen's `forbidden` section is a
  claim: what must NOT be visible or possible on that screen. A screen
  prohibition is the mirror of an acceptance bullet — it says what must not
  happen instead of what must.

Section order mirrors `USER-CASES.md` exactly (`crosscutting`, `roles`, `scenarios`,
`prohibitions`) so the two read side by side; trigger- and screen-derived tests are
cross-referenced from there via `trigger`/`screen`, not filed under a fourth section.

## Ids

The test id is still `<case-id>.T<n>` — `C-06.T3`, `Z-08.T1`, `S-02.T4` — even when
the test is derived from a trigger or a screen: it files under the case that
trigger or screen serves. Traceability is built into the id: `grep 'C-06\.'` finds
every test for that case. ASCII only, per the folder standard. Numbers are never
reused once struck.

The id names WHERE the test lives; the `covers` YAML key names WHAT it verifies —
and since v2 that is the acceptance bullet itself (`C-06.a2`), not just the case
(`C-06`). A case can carry a dozen acceptance bullets; a `covers` that only names
the case cannot tell you which of them has a test and which doesn't. This is what
turns the coverage count in `INDEX.md` into something checkable rather than
plausible — "C-06 is covered" becomes "C-06.a1 through .a4 are covered, .a5 is not."
A trigger- or screen-derived test sets `trigger: trg-...` or `screen: ...` instead,
naming the entry in `AUTOMATION.md`/`UX-UI.md` it verifies.

## Anatomy of one test

````markdown
<!-- macstack:test=C-06.T3 -->
### C-06.T3 · Предупреждение без геолокации

```yaml
covers: C-06.a2
kind: manual
role: coach
```

<!-- macstack:preconditions -->
**Предусловия**
Коуч авторизован; геолокация в браузере запрещена.

<!-- macstack:steps -->
**Шаги**
1. Открыть первый экран.
2. Нажать «Начать занятие».

<!-- macstack:expected -->
**Ожидаемо**
Показан текст, объясняющий последствие — ручная проверка и возможная задержка
оплаты; формулировка не обвиняет и не выглядит отказом.
````

`covers` and `kind` are always required in the YAML block; `expected` is always
required in prose. A `manual` test additionally needs `preconditions` and `steps`;
an `auto` test additionally needs `evidence` (and skips `preconditions`/`steps`).
One anchor above the heading, one YAML block right under it, prose in anchored
sections below — the shape every document under `macstack/` uses; see
`${CLAUDE_PLUGIN_ROOT}/skills/documents/references/format-rules.md` for the full rule.

## auto or manual

| Tag | Use when | Evidence |
|---|---|---|
| `auto` | The assertion is decidable by a machine: a state change, a refusal, an arithmetic result, a field value, a permission boundary | The **title** of the automated test that proves it — never a `file.ts:214` pointer, which rots. `attendance.int.spec.ts — "allows check-in without geolocation"` |
| `manual` | The assertion is about tone, layout, readability, a real device, a third-party surface, or anything needing a person's judgement | `— (человек)`. Steps must be followable by someone who has never seen the code |

Do not tag something `auto` because it *could* be automated one day. The tag describes
how it is checked today; an untagged aspiration is how a coverage table starts lying.

`kind` lives on the **test**, never on the case or the file. One case routinely
mixes both — a state change is `auto`, the tone of the warning next to it is
`manual` — so "is C-06 auto or manual" is not a question this document can answer;
"is C-06.T3 auto or manual" is.

## Three shapes worth naming

- **`Z-` prohibitions** need two assertions, not one: the platform refuses, **and** the
  refusal explains itself. A refusal that succeeds silently fails the case.
- **`S-` end-to-end scenarios** are ordered, and each step names the case it exercises.
  They are the only place ordering between cases is asserted.
- **`X-` cross-cutting cases** apply to every role. Either write one test per role, or
  one test that names the roles it must be run as — say which, do not leave it implied.

## Regenerating without destroying work

Update **by id**, never by rewriting the file.

1. Read the current versions of `USER-CASES.md`, `AUTOMATION.md` and `UX-UI.md`
   against what the `TEST-CASES.md` journal last recorded for each. All equal →
   nothing to do unless asked.
2. For each acceptance bullet, trigger and screen `forbidden` line: an existing
   test that covers it stays as written — hand-refined steps and evidence are the
   point of this document and are never regenerated over.
3. A claim with no test → add one, numbered after the highest `.T<n>` for the case
   it files under.
4. A test whose covered bullet/trigger/prohibition no longer exists →
   **strike, do not delete**: `~~C-04.T2~~ · СНЯТ в v1.9 — пункт удалён`. Struck
   ids are never reused.
5. Bump the header to the versions derived from and add a journal row naming
   which source changed.
6. Refresh the document's own `coverage` section: per role, cases · acceptance
   bullets · tests · auto/manual split · bullets with no test. `generated/INDEX.md`
   carries the parallel summary across all client documents — refresh it too.

## When a test cannot be written

If verifying a claim requires a fact the source document does not state — a
threshold, a message, a deadline, a schedule — **do not invent it here.** The gap
is in `USER-CASES.md`, `AUTOMATION.md` or `UX-UI.md`, not in the tests. Raise it:
a question for the client goes to `client/OPEN-QUESTIONS.md §A`; a wording change
to an agreed case, trigger or screen goes through `macstack-dev:intake` as a
contradiction. A test case that quietly invents its own acceptance criterion
becomes a second specification, and the folder exists to prevent exactly that.

## Routing

| Situation | Do |
|---|---|
| No `TEST-CASES.md` yet | Generate the full set from `USER-CASES.md`, `AUTOMATION.md` and `UX-UI.md` |
| A source document bumped a version | Re-derive incrementally per the steps above |
| A claim is untestable as written | `intake` (contradiction) or `client/OPEN-QUESTIONS.md §A` |
| Recording what a test run actually found | `history/reviews/<date>-<slug>-conformance.md`, not here |
| After any change | `macstack-dev:lint` |
