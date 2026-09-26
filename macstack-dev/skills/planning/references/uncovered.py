#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Which client requirements have no plan yet — and which already passed a check.

Sits between `client/USER-CASES.md` (what the client agreed must be true) and
`history/TASKS.md` (what will be done about it). Answers three questions a person cannot
answer by reading either file alone:

  1. Which cases nobody scheduled AND no audit has confirmed — the real work list.
  2. Which cases an audit already found implemented — planning those wastes everyone's time.
  3. Which cases are waiting on the client — an open question they depend on is unanswered.
     Those are NOT work and do NOT become tasks: `TASKS.md` is a queue somebody picks
     from, and a task that cannot be finished without a client answer stops the person
     who picked it. The question in `OPEN-QUESTIONS.md` §A already holds the work; the
     task is written the day the answer lands (owner's ruling, 2026-08-27).
  4. Which tasks point at a case that no longer exists — a plan for a requirement withdrawn.

The third input is the `audit` rows of `history/ledger.jsonl`. Without them the report says
"N cases with no plan" on a project where nearly all of them are built, which is true and
useless: a work list nobody believes is a work list nobody reads.

v3 change: `client/USER-CASES.md` and `client/OPEN-QUESTIONS.md` moved to headings-and-
bullets — no anchor names the kind of a heading the way v2's `<!-- macstack:case=C-04 -->`
did, so `mdblocks.entities(blocks, 'case')` saw an empty document and this script reported
all 78 live cases as unplanned, silently. They now read through `v3` instead. A case is
identified by its HEADING ID (`^[A-Z]-\\d{2}$`), never by its pointer: the comment above a
case reads `<!-- macstack:ref=roles[id=coach].cases -->` — the OWNING ROLE's glob-covered
case list in macstack.json — and repeats no case id, so matching cases by pointer target
finds zero of them on the live corpus. 27 cases (`X-`, `S-`, `Z-` — cross-cutting, end-to-end
scenarios, prohibitions) carry no such pointer at all and belong to no single role; they are
still collected by heading id like every other case, never dropped for lacking one. (The role
itself, when a case has one, is the `id=` inside that pointer — nothing here reads it off a
bullet, because no bullet carries it.)

`history/TASKS.md` and `history/reviews/*-conformance.md` are unaffected by this port and
still read through `mdblocks` — they carry their own migration later, and reading them here
would collide with it.

WHAT IT DOES NOT DO: decide which files a task touches or what proves it done. That is
judgement over the codebase, and a machine that guesses it produces a plan nobody can
trust. It emits the SKELETON — id, name, the pointer back to the case — and the agent or
the human fills `files` and `acceptance` by reading the code.

Usage: uncovered.py <macstack-dir> [--emit]   (--emit prints ready v2 task skeletons)
"""
import sys, os, io, re

sys.path.insert(0, os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', 'documents', 'references')))
from mdblocks import parse, entities, dump_yaml  # noqa: E402  — TASKS.md + reviews only
import v3                                        # noqa: E402  — USER-CASES.md + OPEN-QUESTIONS.md
from i18n import doc_lang, msg  # noqa: E402

CASE_ID = re.compile(r'\b(C?[A-Z]-\d{2})\b')
CASE_HEADING = re.compile(r'^C?[A-Z]-\d{2}$')    # a case's own heading id, full match
OPEN_ID = re.compile(r'\b([AB]\d+)\b')
# Fallback for the v1 table format: | C-01 | Implemented | evidence... |
LEGACY_ROW = re.compile(r'^\|\s*\*?\*?([A-Z]-\d+)\*?\*?\s*\|\s*([^|]+?)\s*\|', re.M)
DONE_SYNONYMS = ('implemented', 'выполнено', 'реализовано', 'passes', 'ok')
PRIORITY_ORDER = ('critical', 'important', 'nice-to-have')


def read(path):
    with io.open(path, encoding='utf-8') as f:
        return f.read()


def title_of(item):
    """v3 already splits '<id> · Title' at read time; struck titles ('~~Title~~ · CLOSED
    …') keep their tildes, same as v2's heading text did, so callers see the same thing."""
    return (item.title or '').strip()


def case_full_text(item):
    return '\n'.join(item.body)


def acceptance_count(item):
    """Every dash-bullet in the entity's body. A case has exactly one bulleted section
    (`**Готово, если:**` / `**Done if:**`) on the live corpus, so counting body-wide
    dashes gives the same number as counting that section alone, without hard-coding
    the section's label in a language it might not be written in."""
    return sum(1 for line in item.body if line.strip().startswith('- '))


def live_open_ids(oq_path, lang):
    """Open-item ids from OPEN-QUESTIONS.md that are not struck (closed/promoted).

    Deferred-work items (`### B1 — Сделать до того…`) use an em-dash heading v3's
    id/title split does not recognise, so they never carry an id. They were outside this
    set before the port too, and not by accident: the v2 file this document replaced
    anchored §A and nothing else — all 25 of its `macstack:open=` anchors are A-items.

    Struck-ness is read off the WHOLE heading line, the way v2 read it, and not off
    `Item.title`: v3 strips the tildes while splitting the id, so `~~A6~~ · Payment terms`
    parses to a clean id and a clean title and would read as still open. An open question
    blocks every case citing it, so a closed one that still looks open blocks them forever.
    """
    if not os.path.exists(oq_path):
        return set()
    doc = v3.load_doc(oq_path, lang)
    out = set()
    for it in doc.items:
        if not (it.id and OPEN_ID.match(it.id)):
            continue
        heading = doc.lines[it.head_line].lstrip('#').strip()
        if not heading.startswith('~~'):
            out.add(it.id)
    return out


def read_verdicts(path):
    """-> (yaml_verdicts, legacy_verdicts), both {case_id: raw value/text}.

    yaml_verdicts comes from `finding` entities' yaml `verdict` field (closed enum).
    legacy_verdicts comes from the old table format and is only a fallback — the
    caller prefers yaml_verdicts for any id present in both.
    """
    raw = read(path)
    legacy = {}
    for m in LEGACY_ROW.finditer(raw):
        cid, text = m.group(1), m.group(2).strip()
        if cid not in legacy:
            legacy[cid] = text
    _, blocks = parse(raw)
    yml = {}
    for b in entities(blocks, 'finding'):
        v = b.yaml.get('verdict')
        if v:
            yml[b.id] = v
    return yml, legacy


def classify(cid, covered, yml, legacy):
    """-> (state, verdict_text) — state in ('planned', 'done', 'partial', 'todo')."""
    if cid in covered:
        return 'planned', None
    if cid in yml:
        v = yml[cid]
        if v == 'implemented':
            return 'done', v
        if v in ('partial', 'externally-blocked'):
            return 'partial', v
        return 'todo', v            # 'absent' — nobody built it; this IS the work
    if cid in legacy:
        v = legacy[cid]
        if any(d in v.lower() for d in DONE_SYNONYMS):
            return 'done', v
        return 'partial', v
    return 'todo', None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    root = args[0] if args else 'macstack'
    emit = '--emit' in sys.argv
    lang = doc_lang(root)

    uc_p = os.path.join(root, 'client', 'USER-CASES.md')
    tk_p = os.path.join(root, 'history', 'TASKS.md')
    oq_p = os.path.join(root, 'client', 'OPEN-QUESTIONS.md')
    for p in (uc_p, tk_p):
        if not os.path.exists(p):
            print('missing: %s' % p)
            return 1

    cases = [i for i in v3.load(uc_p, lang) if i.id and CASE_HEADING.match(i.id)]

    # `TASKS.md` живёт в двух формах: v2 — якорь `<!-- macstack:task= -->` плюс блок
    # yaml, и v3 — заголовок `### M15-T1 · Название` с буллетами. Читаем v3 ПЕРВЫМ,
    # потому что документ мог быть переведён, а читатель за ним не пошёл — и тогда
    # `entities(...,'task')` возвращает пустоту молча. Измерено 2026-08-27 на
    # живом проекте: отчёт сказал «запланировано 0» и предложил завести восемь
    # задач, все восемь из которых уже лежали в файле. Это ровно та ложная работа,
    # против которой написан абзац про вердикты аудита выше.
    class _Task(object):
        __slots__ = ('id', 'yaml')

        def __init__(self, ident, fields):
            self.id, self.yaml = ident, fields

    TASK_ID = re.compile(r'^M\d+-T\d+$')
    MIL_ID = re.compile(r'^M\d+$')
    tasks, milestones = [], []
    try:
        v3_items = v3.load(tk_p, lang)
    except Exception:
        v3_items = []
    v3_tasks = [i for i in v3_items if i.id and TASK_ID.match(i.id)]
    if v3_tasks:
        for i in v3_tasks:
            y = dict(i.fields)
            if not y.get('spec'):
                # В v3 связь с кейсом несёт буллет «Закрывает» -> поле `closes`.
                cl = y.get('closes')
                if isinstance(cl, (list, tuple)):
                    cl = ' '.join(str(x) for x in cl)
                if cl:
                    y['spec'] = str(cl)
            tasks.append(_Task(i.id, y))
        milestones = [_Task(i.id, dict(i.fields))
                      for i in v3_items if i.id and MIL_ID.match(i.id)]
    if not tasks:
        _, tk_blocks = parse(read(tk_p))
        tasks = entities(tk_blocks, 'task')
        milestones = entities(tk_blocks, 'milestone')

    live_a = live_open_ids(oq_p, lang)

    # Вердикт аудита — данные, а не документ: он спрашивается по id кейса, а не
    # перечитывается подряд, и отчёт устаревает быстрее, чем его читают. Строки
    # `audit` в журнале правок и есть этот вердикт; markdown-отчёты уехали в
    # archive/ вместе с остальными рабочими продуктами.
    yml, legacy, rev_name = {}, {}, None
    _here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.normpath(
        os.path.join(_here, '..', '..', 'documents', 'references')))
    import ledger as _L                # намеренно без try: если журнал не читается,
                                       # отчёт скажет «ничего не проверено» — и это
                                       # ложь, которую тихий except делает незаметной
    rows = [r for r in _L.read(root) if r.get('kind') == 'audit']
    for r in sorted(rows, key=lambda x: x.get('date') or ''):
        if r.get('item') and r.get('now'):
            legacy[r['item']] = r['now']
            rev_name = r.get('source') or rev_name

    DEAD = ('cancelled', 'dropped', 'отменена', 'снята')
    covered = {}
    for t in tasks:
        spec = str(t.yaml.get('spec') or '')
        for cid in CASE_ID.findall(spec):
            covered.setdefault(cid, []).append((t.id, t.yaml.get('status')))
    # Кейс, чья единственная задача снята, всё равно считается решённым: снятие — это
    # тоже решение, и оно записано в самой задаче с причиной. Но молчать об этом нельзя,
    # иначе снятая работа исчезает из виду. Поэтому — отдельная строка отчёта.
    withdrawn = {cid: v for cid, v in covered.items()
                 if v and all(str(s or '').lower() in DEAD for _, s in v)}

    known = {c.id for c in cases}
    orphan = []
    for t in tasks:
        spec = str(t.yaml.get('spec') or '')
        for cid in CASE_ID.findall(spec):
            if cid not in known:
                orphan.append((t.id, spec))

    blocked = {}
    for c in cases:
        hits = sorted({a for a in OPEN_ID.findall(case_full_text(c)) if a in live_a})
        if hits:
            blocked[c.id] = hits

    rows = [(c,) + classify(c.id, covered, yml, legacy) for c in cases]
    planned = [r for r in rows if r[1] == 'planned']
    done = [r for r in rows if r[1] == 'done']
    partial = [r for r in rows if r[1] == 'partial']
    unc_all = [r for r in rows if r[1] == 'todo']
    # Ждущие ответа клиента отделяются ДО отчёта и до --emit: они не работа.
    await_client = [r for r in unc_all if r[0].id in blocked]
    unc = [r for r in unc_all if r[0].id not in blocked]

    print(msg(lang, 'cases_total', n=len(cases)))
    print('  ' + msg(lang, 'cases_planned', n=len(planned)))
    print('  ' + msg(lang, 'cases_audited', n=len(done)) + (' (%s)' % rev_name if rev_name else ''))
    print('  ' + msg(lang, 'cases_partial', n=len(partial)))
    print('  ' + msg(lang, 'cases_open', n=len(unc)))
    print('  ' + msg(lang, 'cases_await', n=len(await_client)))

    if partial:
        print('\n=== audit found partial or blocked (%d) ===' % len(partial))
        for c, st, v in partial:
            print('    %-7s %-52s %s' % (c.id, title_of(c)[:52], (v or '')[:34]))

    if withdrawn:
        print('\n=== planned once, then withdrawn (%d) ===' % len(withdrawn))
        for cid, v in sorted(withdrawn.items()):
            print('    %-7s %s' % (cid, ', '.join('%s (%s)' % (i, s) for i, s in v)))
        print('    still counted as planned — the reason is written in the struck task')

    print('\n=== not planned and not checked ===')
    by_pri = {}
    for c, st, v in unc:
        pri = c.get('priority') or '—'
        by_pri.setdefault(pri, []).append(c)
    order = list(PRIORITY_ORDER) + [p for p in by_pri if p not in PRIORITY_ORDER]
    for pri in order:
        if pri not in by_pri:
            continue
        group = by_pri[pri]
        print('\n  [%s] %d' % (pri, len(group)))
        for c in group:
            mark = '  ⏸ ' + ','.join(blocked[c.id]) if c.id in blocked else ''
            print('    %-7s %s%s' % (c.id, title_of(c)[:66], mark))
            print('        spec: client/USER-CASES.md %s — %d пункт(ов) приёмки' % (c.id, acceptance_count(c)))

    if await_client:
        print('\n=== awaiting the client — no task is written for these (%d) ===' % len(await_client))
        for c, st, v in await_client:
            print('    %-7s %-52s ⏸ %s' % (c.id, title_of(c)[:52], ','.join(blocked[c.id])))
        print('    the answer lands -> the question closes -> the task is written then')

    if orphan:
        print('\n=== tasks pointing at a missing case (%d) ===' % len(orphan))
        for tid, spec in orphan:
            print('    %-10s -> %s' % (tid, spec[:60]))

    if emit and unc:
        print('\n' + '=' * 72)
        print('TASK SKELETONS — files and acceptance are filled in by reading the code, never by the machine\n')
        mil = milestones[-1].id if milestones else 'M1'
        tpat = re.compile(r'^%s-T\d+$' % re.escape(mil))
        n = len([t for t in tasks if tpat.match(t.id)])
        for c, st, v in unc:
            n += 1
            task_id = '%s-T%d' % (mil, n)
            yaml_fields = {
                'status': 'todo',
                'tracker': None,
                'milestone': mil,
                'spec': 'client/USER-CASES.md#%s' % c.id,
                'files': [],
                'acceptance': None,
            }
            print('<!-- macstack:task=%s -->' % task_id)
            print('### %s · %s' % (task_id, title_of(c)))
            print()
            print('```yaml')
            print(dump_yaml(yaml_fields))
            print('```')
            print()
            print('<!-- macstack:notes -->')
            print()
        if await_client:
            print('# %d case(s) awaiting the client got NO skeleton: %s'
                  % (len(await_client), ', '.join(c.id for c, _, _ in await_client)))
    elif unc:
        print()
        print(msg(lang, 'emit_hint'))

    return 0


if __name__ == '__main__':
    sys.exit(main())
