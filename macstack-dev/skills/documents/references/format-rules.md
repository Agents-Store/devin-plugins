# How a macstack document is shaped

Every document under `macstack/` is written the same way, whatever it is about. A
client reads it as ordinary markdown; a parser reads the invisible pointers and the
bullet labels. Neither is bent to serve the other.

The structure below is declared once, in `doc-contracts.json`, and read by both the
writer and the linter — so the two cannot drift apart. This file explains **why** each
rule is what it is. When the two disagree, the contract is the fact and this file is
the argument.

---

## The shape, in five pieces

A client document is **headings and bullet lists**. Nothing else. No fenced blocks, no
tables, no HTML — except the two comments below, which are invisible when the document
is read.

### 1. The document header — one per file, first line

```markdown
<!-- macstack:doc=user_cases lang=ru version=3.0 -->
```

`lang` follows `docs.language`. `version` must equal `docs.files.<key>.version` in
`macstack.json`; if the two disagree, one of them is lying and lint says which.

### 2. The pointer — one above each entity heading

```markdown
<!-- macstack:ref=triggers[id=trg-week-close] -->
```

It names where the same data lives in `macstack.json`. It is a comment, so the client
never sees it, and it is the only machine syntax inside the prose. A section-level
pointer uses empty brackets — `<!-- macstack:ref=roles[] -->` — and means "this whole
section covers that collection".

### 3. The heading — carries the id

Two forms, and which one you use depends on whether the id is something people say out
loud:

```markdown
### C-04 · Отметиться на занятии (check-in)
### Закрытие полумесячного периода — `trg-week-close`
```

A short spoken id (`C-04`, `A5`, `Z-03`) goes first, before the title. A technical slug
goes last, in backticks, after an em dash. Both are ids; neither is decoration.

### 4. The field — a bullet with a bold label

```markdown
- **Насколько важно:** критично
- **Экраны:** `kalender`, `coach-portal`
```

The label is in the document's language and is declared in `doc-contracts.json`. The
value is a word, a number, or a comma-separated backticked list — ids for most fields,
repository-relative PATHS for `docs`, which points at plans and specs rather than at
collection entries and therefore declares no `resolves_to`.

**A bullet is a field only when its label is declared.** An undeclared bold-and-colon
opening is prose that happens to look like a field — a sentence in an ordinary list —
and inventing a field from it puts a key into the model that nothing reads. Lint
reports undeclared labels; the parser never guesses.

### 5. The prose block — a bold label on its own line

```markdown
**Готово, если:**
- на первом экране видна кнопка «Начать занятие» — без поиска и переходов;
- если коуч не в центре — отказ, который называет центр и расстояние до него;
```

Free prose between entities needs no label at all and is preserved exactly as written.

---

## Why not yaml, and why not a table

Both were tried on this project, and both failed the same way.

**v1 made the markdown table the machine interface**, deliberately: columns were read
by POSITION, because a header follows `docs.language` and matching on its text would
break the moment a project wrote in German. The reasoning was correct. The consequence
was not foreseen — once the grid is where the machine looks, every piece of prose that
needs to be machine-adjacent gets written into a cell. Measured on the live project
before the change: **56 tables across 20 documents, cells up to 1353 characters**, one
client-facing document six columns by thirty-seven rows at 600–880 characters a row.

**v2 replaced the grid with an anchor plus a fenced `yaml` block.** That fixed the
column-position problem and created a new one: markdown, yaml and tables stirred
together in one file, and a client who cannot tell which parts are safe to edit will
edit none of them.

**v3 removes the machine syntax from the document altogether.** The machine half lives
in `macstack.json`; the document keeps an invisible pointer to it. What is left is
something a person will actually correct.

The cost is one table of labels per language. That is the right price: the labels are
few, they are declared in one place, and a project writing in German gets German labels
rather than a document nobody edits.

---

## The pointer binds four different ways

This is the part that looks simpler than it is. The obvious rule — *the heading id
equals the pointer id* — is true in one document and false in two, and assuming it is
universal is the expensive mistake, because both plausible repairs are wrong: either
you invent spec entries that nothing else references, or you weaken the rule until it
stops catching a genuinely broken pointer.

Measured on the live corpus:

```
документ             заголовков  указателей  целей  совпадений  без указателя
AUTOMATION.md            49          49        49       49            0
OVERVIEW.md              18          18        18       18            0
OPEN-QUESTIONS.md        25          21        21       21            4
UX-UI.md                 37          37         9        9            0
USER-CASES.md            78          51         3        0           27
HANDBOOK.md               0           0         0        0            0
```

| Binding | What it asserts | Where |
|---|---|---|
| `identity` | the last `[id=…]` equals the heading id | triggers, tasks, roles, goals, results, integrations, open items |
| `container` | the pointed entry exists; the heading id is unique in the document | screens — 37 of them onto 9 `interfaces[]` entries |
| `member` | the heading id satisfies the glob at the pointed path | cases — `roles[id=coach].cases` holds `["C-*"]`, not objects |
| `none` | no pointer, and the id prefix is reserved | `X-`, `S-`, `Z-` cases belong to every role, so to none |

`interfaces[]` staying at AREA level is a recorded decision, not an omission: nine
areas, thirty-seven screens. A screen heading carries the route slug; the pointer
carries the area. Never conflate them.

---

## Worked examples, taken from the live project

### A case — `client/USER-CASES.md`

```markdown
<!-- macstack:ref=roles[id=coach].cases -->
### C-04 · Отметиться на занятии (check-in)

- **Насколько важно:** критично

Коуч пришёл в центр и за две секунды отмечает начало занятия — одной кнопкой,
ничего не выбирая.

**Готово, если:**
- на первом экране видна кнопка «Начать занятие» для ближайшего занятия;
- геолокация запрашивается и проверяется сама;
- если коуч не в центре — отказ, который называет центр и расстояние до него;
- после отметки экран показывает время check-in, а кнопка меняется на «Закончить».
```

The role is **not** a bullet. It is the pointer, one line above. A second copy of a
fact the pointer already carries is the hand-maintained duplicate that rule 12.27
exists to stop.

Each `Готово, если` bullet is individually addressable — `C-04.a3` — and that address
is what a client's comment and a test's `covers` resolve against. Ids come from the
bullet's position **within its own entity**, never from its position in a review
package: insert a bullet above another and every id below it in that package would
move, so a client quoting `C-04.a2` from an email last month would land on a different
sentence.

A `Z-` prohibition has no acceptance list. It states what must be refused; the refusal
is the behaviour.

### A trigger — `client/AUTOMATION.md`

```markdown
<!-- macstack:ref=triggers[id=trg-week-close] -->
### Закрытие полумесячного периода — `trg-week-close`

- **Что это за событие:** расписание
- **Кто его создаёт:** часы, по расписанию
- **Когда срабатывает:** `0 6 1,16 * *`
- **Что поднимает:** workflow `wf-week-close-prompt`
- **Чьи задачи двигает:** Коуч, Контактное лицо тренинг-центра

**Что происходит.** 1-го и 16-го числа платформа собирает период, который только что
закончился, и создаёт проекцию к подтверждению — только непустую.
```

Two fields are required, `type` and `source`, and the client asks the second question
first: *who made this happen — a person, the backend, or something outside?* The rest
are partial by nature, not by neglect — `Когда срабатывает` only on a scheduled
trigger (4 of 13), `За чем следит` only on a data-event one (3 of 13).

### A task — `client/AUTOMATION.md`

```markdown
<!-- macstack:ref=processes[id=time-tracking].tasks[id=log-hours] -->
#### Запросить исправление посчитанного времени — `log-hours`

- **Кто делает:** Коуч (`coach`)
- **Что от человека требуется:** внести данные

**Что происходит.** Коуч видит, что платформа посчитала не то время, и открывает
запрос на исправление. Комментарий обязателен — без него запрос не отправляется.
```

The chain is **trigger → task → workflow**, and tasks are grouped under high-level
**processes**. In macstack a *process* is the big thing a business does; a *workflow*
is the small deterministic thing software runs. They are not synonyms and the word
"flow" is not a section name.

Note the level: a task is `####`, one below the process it belongs to. Nesting is the
grouping, and the pointer says the same thing again for the machine.

### A screen — `client/UX-UI.md`

```markdown
<!-- macstack:ref=interfaces[id=coach-portal] -->
### Календарь коуча — `kalender`

- **Адрес:** `/kalender`
- **Кто видит:** `coach`

**Что на экране**
- Тот же месяц отдельной страницей, назначения по дням с местом и ролью

**Что можно сделать**
- Листать месяцы; открыть день

**Чего здесь быть не должно**
- Данных других коучей
- Сумм тренинг-центра — коуч видит только свою сторону
```

Look at the two ids: the heading says `kalender`, the pointer says `coach-portal`. This
is the `container` binding, and it is why "heading id equals pointer id" cannot be the
rule — here the pointer names the area the screen lives in, not the screen.

All three prose blocks are required on every screen, and the third is the one that
earns the document its keep: what must **never** appear here. A screen with `Открытый
доступ: да` has no role list — `register` is the one such screen — and that is a rule,
not an omission.

### A goal — `client/OVERVIEW.md`

```markdown
<!-- macstack:ref=goals[id=pilot-live] -->
### Пилот работает и им пользуются — `pilot-live`

- **К какому сроку:** 30 сентября 2026
- **Чем измеряем:** активных участников пилота
- **Цель:** 10 человек

MVP в боевой эксплуатации — **без обучения**. Это и есть проверка: если человеку
нужно объяснять, как отметить занятие, платформа не готова.
```

A goal without a date and a number is a wish. All three fields are required.

Results use the same three fields under a different label for one of them — goals say
«Чем измеряем», results say «Что измеряем» — which is why the contract carries
`label_by_kind`. One field, two words, both legitimate; a single label silently dropped
every bullet that used the other one.

### An open item — `client/OPEN-QUESTIONS.md`

```markdown
<!-- macstack:ref=lifecycle.needs_from_client[id=A5] -->
### A5 · Точные формулировки об освобождении и о §19 Kleinunternehmer

- **Куда пойдёт:** `company.vat_note_exempt_4nr21` / `company.vat_note_kleinunternehmer`,
  заполняются на `/settings/firma`

**Что будет, если этого нет или оно неверно**
- Отрендерить можно любое предложение; ручаться за него мы не можем
```

§A is what the client owes; §B is what the team deferred, and a deferred item carries
the trigger that ends the deferral — «Станет небезопасно в тот момент, когда…». A
deferral without that sentence is not a decision, it is a hope.

A closed item keeps its heading, struck through, and loses its pointer: it is no longer
something the client owes.

### A task and its milestone — `history/TASKS.md`

```markdown
### M16-T3 · Половина дневной ставки при работе меньше 4,5 часов

- **Состояние:** todo
- **Заведена:** 2026-08-29
- **Закрывает:** `CC-08`
- **Документы:** `docs/superpowers/plans/2026-08-29-m16.md` → Задача 3

**Готово, если:** день на 3 ч даёт `quantity 0.5` в обе стороны; замена `<` на `<=`
краснит случай «ровно 4,5 — полный день».
```

`Документы` is where a plan written by another tool is named — `superpowers`, a design
doc, the client PDF a requirement came out of. `TASKS.md` says what the work IS; the
plan says how, and the only thing joining them is this bullet. Written once, in the
session that produced both — after which nobody greps a plans directory on the chance
something is in it.

The same bullet is legal on a milestone, and for the sharper reason: milestone criteria
are falsifiable and short **on purpose**, so there is nowhere to expand them unless the
expansion is linked.

---

## What is forbidden in `client/`, and why

- **No fenced blocks.** Not yaml, not json, not a diagram. A client cannot tell which
  parts of a fenced block are safe to edit, so they edit none of the file.
- **No tables.** Including the document journal, which is why there is no journal here
  at all — history lives in `history/`, and the client sees it in the review package,
  per item, rather than as a wall of versions at the bottom of every document.
- **No headings deeper than `####`.**
- **No fabricated id.** If a converter or an audit cannot tell which entity something
  belongs to, it writes `<!-- macstack:ref=TODO reason=… -->` and the linter fails it
  loudly. A plausible wrong id is worse than a missing one, because every
  cross-reference check downstream believes it and reports green.
- **No placeholder over content.** If a tool cannot tell what a block of prose meant,
  it leaves the prose exactly where it is and reports the file.

Tables survive in `history/` and `generated/`, where the reader is a machine or a
programmer, and they are held to a budget lint measures: 4 columns, 80 characters a
cell, 3 rows, no `<br>`, no bold in a long cell.

---

## Language

Prose and labels follow `docs.language`. Ids, field keys, pointer paths and everything
inside backticks are ASCII and are never translated — that is what lets one parser read
a Russian document and a German one.

`macstack.json` is always Latin script. The sync refuses to carry Cyrillic into it, and
that guard stays: a spec half in one alphabet is a spec no external tool can read.
Domain terms that are already Latin — `Einsatz`, `Gutschrift`, `Vorsteuerabzug` — pass
untouched, because translating a term from a contract makes it less precise, not more.

---

## Before you write anything

1. Read `doc-contracts.json` for the document you are about to touch. Which sections,
   which entity kinds, which labels are required for that kind.
2. Never re-render an authored document from a model. **75% of a live client document
   is prose no model represents** — measured: 955 machine-owned lines out of 3837.
   Patch the line you mean to change and leave the rest alone; `v3.set_field` does
   exactly this and returns `False` when the value has not actually changed.
3. Whole-file writes are legal in exactly two places: seeding a file that does not
   exist yet, and rendering something under `generated/`.
4. Every edit gets a row in `history/ledger.jsonl`, keyed by the id of the thing that
   changed. An edit with no row is a defect — that ledger is what lets the client see,
   per statement, what changed since they last read it and what they said about it.
