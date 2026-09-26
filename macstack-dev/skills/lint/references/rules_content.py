# -*- coding: utf-8 -*-
"""Group 12, content and truth: 12.11, 12.12, 12.22, 12.23, 12.27, 12.32, 12.35.

Everything here checks that a document's CLAIMS are backed by something — a test,
the spec, another document, git history — not just that its shape parses. Shape is
rule group 12.21 and friends; this module is the half that can be right in form and
still be lying.

Two things are read off the document's own LINES rather than through v3's per-item
`.sections` dict, and both were measured, not assumed. `.sections` is built by v3.read()
in one pass with no closing rule: the last label declared keeps swallowing every line
until the next heading, and any line matching `**word** …` opens a new label. On the
live corpus that costs both directions at once — C-08's acceptance list ends after one
bullet because its second line begins `**запланировано** ·`, while X-08's picks up a
bullet from after the list. Counted through `.sections`: 369. Counted off the lines the
way a person reading the file would: 378, which is what awk says too. A rule that has
to be right, not approximately right, reads the lines.
"""
import io
import os
import re
import subprocess

from lint_folder import rule, Finding, ERROR, WARNING
import v3

HEADING = re.compile(r'^#{1,6}\s')
BOLD_HEAD = re.compile(r'^\*\*(.+?)[.:]?\*\*\s*$')
BULLET_LINE = re.compile(r'^[-*]\s')
HR = re.compile(r'^(-{3,}|\*{3,}|_{3,})$')

# v3.READ speaks every field label the client documents use; 'covers' and 'kind'
# are two of them, so borrow the translation instead of hand-copying the words a
# second time and letting them drift the way the shipped `gate` labels once did.
_TC_LABELS = {}
for _tbl in (v3.READ.get('ru') or {}, v3.READ.get('en') or {}):
    for _lab, _key in _tbl.items():
        if _key in ('covers', 'kind'):
            _TC_LABELS[_lab] = _key

# `steps` IS in doc-contracts.json's `prose` catalogue (ru «Шаги», en "Steps",
# de "Schritte") and is read from there — a second place declaring the same word is
# how 12.31's 103 findings happened. These three are genuinely absent from the
# catalogue in every language; they are a local stand-in taken from TEST-CASES.md's
# own «как читать» paragraph («предусловия и шаги», «улику», «что должно получиться»),
# not invented, and a project writing in a fourth language gets the English word until
# the contract grows them. That gap belongs to shared data this module does not own.
_TC_PROSE_LOCAL = {
    'ru': {'preconditions': u'Предусловия', 'evidence': u'Улика',
           'expected': u'Что должно получиться'},
    'en': {'preconditions': 'Preconditions', 'evidence': 'Evidence',
           'expected': 'Expected'},
}

_BARE_FILE = re.compile(
    r'^[\w./-]+\.(ts|tsx|js|jsx|mjs|cjs|py|go|rb|java|kt|swift)$', re.I)


# ---------------------------------------------------------------- shared readers
def _norm(label):
    return (label or '').strip().rstrip('.:').lower()


def _block_bullets(lines, start, end, label):
    """Top-level bullets of ONE `**Label:**` block, read off the document's lines.

    A blank line does NOT close the list. It used to, and one blank between
    `**Готово, если:**` and its bullets — markdown that renders identically, and
    exactly what a client leaves behind after editing — silently deleted all six of
    X-01's acceptance bullets: 378 findings became 372 and the case vanished from
    the rule entirely. A list ends where a reader sees it end: the next heading,
    the next bold block header, a pointer comment, a horizontal rule, or an
    unindented line that is not a bullet. Indented lines are continuations of the
    bullet above and are neither counted nor treated as the end.
    """
    want = _norm(label)
    out, in_block = [], False
    for n in range(start, min(end, len(lines))):
        line = lines[n]
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(' \t'))
        if indent == 0:
            m = BOLD_HEAD.match(stripped)
            if m:
                if in_block:
                    break
                in_block = _norm(m.group(1)) == want
                continue
            if (HEADING.match(line) or stripped.startswith('<!--')
                    or HR.match(stripped)):
                if in_block:
                    break
                continue
        if not in_block:
            continue
        if not stripped:
            continue
        if indent:
            continue
        if BULLET_LINE.match(stripped):
            out.append((n, stripped))
        else:
            break
    return out


def _has_block(lines, start, end, label):
    """Whether the block's header line is there at all — 12.21 owns its presence,
    but a finding that cannot say `absent` versus `empty` sends the reader to the
    wrong fix."""
    want = _norm(label)
    for n in range(start, min(end, len(lines))):
        line = lines[n]
        if len(line) - len(line.lstrip(' \t')):
            continue
        m = BOLD_HEAD.match(line.strip())
        if m and _norm(m.group(1)) == want:
            return True
    return False


def _case_acceptance_counts(lines, items, label):
    counts = {}
    for it in items:
        if it.level == 3 and it.id:
            counts[it.id] = len(_block_bullets(lines, it.head_line, it.span[1], label))
    return counts


def _testcase_pattern(c):
    pat = ((c.contract.get('id_spaces') or {}).get('testcase') or {}).get('pattern')
    return re.compile(pat) if pat else re.compile(r'^[A-Za-z]-\d{2}\.T\d+$')


def _tc_entity(c):
    for e in ((c.contract.get('documents') or {}).get('test_cases') or {}).get('entities') or []:
        if e.get('kind') == 'testcase':
            return e
    return {}


def _tc_prose_label(c, key, lang):
    if key in (c.contract.get('prose') or {}):
        return c.prose_label(key, lang)
    tbl = _TC_PROSE_LOCAL.get(lang) or _TC_PROSE_LOCAL['en']
    return tbl.get(key, key)


def _tc_split(text):
    """'~~C-04.T2~~ · DROPPED …' / 'C-06.T3 · Something' -> (id, title, struck)."""
    text = text.strip()
    if text.startswith('~~'):
        m = re.match(r'^~~(.+?)~~\s*·\s*(.*)$', text)
        if m:
            return m.group(1).strip(), m.group(2).strip(), True
        return None, text, True
    m = re.match(r'^(\S+)\s*·\s*(.*)$', text)
    if m:
        return m.group(1).strip(), m.group(2).strip(), False
    return None, text, False


def _read_testcases(text, id_pattern, lang):
    """Walk TEST-CASES.md by hand for the one heading shape v3.py cannot see.

    v3._split_heading() recognises case / open_item / milestone / Z-case id shapes
    — none of them is `<case>.T<n>`, the testcase id this document's contract
    heading form actually uses (`### C-06.T3 · …`). That regex lives in shared
    infra this module does not own (`documents/references/v3.py`); rather than
    edit it, this reuses v3's BULLET/PROSE line grammar and supplies the one
    missing heading match locally.

    ANY heading closes the entity, not just the next `###`. It used to be only the
    next `###`, so `## Журнал документа` and its table were appended to whatever
    prose block the last test had open: an `auto` test whose `**Улика:**` was empty
    passed the "must name the test title" check because the journal had filled it in.

    Returns (tests, strays) — strays are `###` headings shaped like an entity whose
    id does not parse. Dropping those silently is how a typo'd test id disappears
    from this rule AND from 12.11's coverage at the same time.
    """
    lines = text.split('\n')
    items, strays, cur = [], [], None
    for n, line in enumerate(lines):
        hm = v3.HEADING.match(line)
        if hm:
            if cur is not None:
                cur['end'] = n
                cur = None
            if len(hm.group(1)) != 3:
                continue
            ident, title, struck = _tc_split(hm.group(2))
            if ident and id_pattern.match(ident):
                cur = dict(id=ident, title=title, struck=struck, head_line=n,
                           fields={}, field_lines={}, sections={}, end=len(lines))
                items.append(cur)
            elif u'·' in hm.group(2):
                strays.append((n, hm.group(2).strip()))
            continue
        if cur is None:
            continue
        bm = v3.BULLET.match(line)
        if bm:
            key = _TC_LABELS.get(bm.group(1).strip().lower())
            if key:
                cur['fields'][key] = v3._value(bm.group(2), lang)
                cur['field_lines'][key] = n
            continue
        pm = v3.PROSE.match(line.strip())
        if pm:
            label = _norm(pm.group(1))
            sec = cur['sections'].setdefault(label, {'line': n, 'body': []})
            if pm.group(2).strip():
                sec['body'].append(pm.group(2))
            continue
        if cur['sections']:
            last = list(cur['sections'])[-1]
            cur['sections'][last]['body'].append(line)
    return items, strays


def _tc_section(c, t, key, lang):
    want = _norm(_tc_prose_label(c, key, lang))
    for lab, sec in t['sections'].items():
        if lab == want or lab == key:
            return sec
    return None


def _tc_section_text(c, t, key, lang):
    sec = _tc_section(c, t, key, lang)
    if not sec:
        return ''
    return ' '.join(b.strip() for b in sec['body'] if b.strip()).strip()


def _looks_like_bare_filename(text):
    """'a bare filename is not evidence' — a `file.ts:NNN` pointer is already
    banned everywhere by 12.8; this catches the filename ALONE, with the line
    number stripped off, which 12.8's pattern does not match."""
    text = text.strip().strip('`')
    if ' ' in text or not text:
        return False
    return bool(_BARE_FILE.match(text)) or ('/' in text and '.' in text.rsplit('/', 1)[-1])


def _covered_acceptance_ids(c):
    """Что покрыто по СГЕНЕРИРОВАННОМУ TEST-CASES.md.

    Формат сменился вместе с источником истины. Раньше покрытие объявлял сам
    документ полем `covers` у записи теста — то есть таблица соответствия,
    которую надо было вести руками и которая врала с того дня, как тест удалили.
    Теперь документ собирается из ЗАГОЛОВКОВ тестов, и строка выглядит так:

        - `C-04.a2` — `tests/int/entry-form.int.spec.ts`
        - `C-04.a3` — не покрыт

    Правило читает то же самое, что печатает генератор, поэтому «покрыто» в
    линтере и «покрыто» в документе не могут разойтись.
    """
    text = c.text.get('test_cases')
    if not text:
        return set()
    out = set()
    for line in text.split('\n'):
        m = re.match(r'^-\s+`(C?[A-Z]-\d{2}(?:\.a\d+)?)`\s+—\s+(.*)$', line.strip())
        if m and not re.search(r'не покрыт|not covered|nicht abgedeckt', m.group(2)):
            out.add(m.group(1))
    return out



# ---------------------------------------------------------------- 12.11
@rule('12.11', 'Every promise is verified')
def r_12_11(c):
    """Единица покрытия — КЕЙС, а не пункт приёмки.

    Первая версия считала по пунктам и требовала теста на каждый из 369. Это
    неверная единица: пункт приёмки — строка чек-листа внутри кейса, а не
    отдельный тест. «Кнопка видна», «геолокация проверяется», «отказ называет
    расстояние» — человек проходит это одним сценарием.

    Читает то же, что печатает генератор, поэтому «покрыто» здесь и «покрыто»
    в документе не могут разойтись.
    """
    text = c.text.get('test_cases')
    if not text:
        return [Finding('12.11', ERROR, 'generated/TEST-CASES.md', 0,
                        'does not exist — no promise can be shown as verified')]
    out = []
    for line in text.split('\n'):
        m2 = re.match(r'^-\s+`(C?[A-Z]-\d{2})`\s+(.*?)\s+—\s+(.*)$', line.strip())
        if not m2:
            continue
        cid, name, state = m2.group(1), m2.group(2), m2.group(3)
        if state.startswith('`'):
            continue                       # доказан сценарным тестом
        out.append(Finding('12.11', ERROR, 'client/USER-CASES.md', 0,
                           '%s %s — %s' % (cid, name[:40], state[:60])))
    return out

@rule('12.12', 'Test cases are well formed')
def r_12_12(c):
    text = c.text.get('test_cases')
    if not text:
        return []
    lang = v3.header(text).get('lang') or c.lang
    tests, strays = _read_testcases(text, _testcase_pattern(c), lang)
    p = c.path_of('test_cases')
    path = c.rel(p) if p else 'generated/TEST-CASES.md'
    ent = _tc_entity(c)
    when = ent.get('sections_required_when') or {}
    always = list(ent.get('prose_required') or [])
    kinds = sorted(when) or ['auto', 'manual']
    out = []

    for n, txt in strays:
        out.append(Finding('12.12', ERROR, path, n + 1,
                           'heading %r is shaped like a test and carries no id this '
                           'document can address — it is invisible to 12.11 as well'
                           % txt[:60]))

    for t in tests:
        ln = t['head_line'] + 1
        if t['struck']:
            if not re.search(u'—\\s*\\S', t['title']):
                out.append(Finding('12.12', ERROR, path, ln,
                                   '%s is struck but names no reason after —' % t['id']))
            continue
        if 'covers' not in t['fields']:
            out.append(Finding('12.12', ERROR, path,
                               t['field_lines'].get('kind', t['head_line']) + 1,
                               '%s: no covers' % t['id']))
        for key in always:
            if not _tc_section_text(c, t, key, lang):
                out.append(Finding('12.12', ERROR, path, ln,
                                   '%s: every test must declare "%s"'
                                   % (t['id'], _tc_prose_label(c, key, lang))))
        if 'kind' not in t['fields']:
            out.append(Finding('12.12', ERROR, path, ln, '%s: no kind' % t['id']))
            continue
        kind = t['fields']['kind']
        kln = t['field_lines']['kind'] + 1
        if kind not in kinds:
            out.append(Finding('12.12', ERROR, path, kln,
                               '%s: kind %r is none of %s'
                               % (t['id'], kind, ', '.join(kinds))))
            continue
        for key in when.get(kind) or []:
            # Evidence is not just any required block: a filename is a pointer that
            # rots, and what has to be there is a test title somebody can run.
            if key == 'evidence':
                sec = _tc_section(c, t, 'evidence', lang)
                evln = sec['line'] + 1 if sec else kln
                body = _tc_section_text(c, t, 'evidence', lang)
                if not body:
                    out.append(Finding('12.12', ERROR, path, evln,
                                       '%s: an auto test must name the test title that '
                                       'proves it' % t['id']))
                elif _looks_like_bare_filename(body):
                    out.append(Finding('12.12', ERROR, path, evln,
                                       '%s: evidence is a bare filename, not a test title '
                                       'that can be found and run: %s' % (t['id'], body)))
            elif not _tc_section_text(c, t, key, lang):
                out.append(Finding('12.12', ERROR, path, kln,
                                   '%s: a %s test must declare "%s"'
                                   % (t['id'], kind, _tc_prose_label(c, key, lang))))
    return out


# ---------------------------------------------------------------- 12.22
@rule('12.22', "The spec agrees with AUTOMATION.md")
def r_12_22(c):
    doc = c.docs.get('automation')
    if doc is None:
        return []
    out = []
    path = c.rel(doc.path)

    _, role_items = c.entities_of('automation', 'role')
    doc_roles = dict((it.id, it) for it in role_items if it.id)
    spec_roles = set(r.get('id') for r in (c.spec.get('roles') or []) if r.get('id'))
    for rid in sorted(spec_roles - set(doc_roles)):
        out.append(Finding('12.22', ERROR, path, 0,
                           'role %s is in the spec, named by no document' % rid))
    for rid in sorted(set(doc_roles) - spec_roles):
        it = doc_roles[rid]
        out.append(Finding('12.22', ERROR, path, (it.head_line or 0) + 1,
                           'role %s is in the document, not in the spec' % rid))

    # Only a task with a `human` block is AUTOMATION.md's business — a workflow-only
    # task is the machine half, and the document explicitly does not own it (see the
    # entity's own note: "never a vague both").
    _, task_items = c.entities_of('automation', 'role_task')
    doc_tasks = dict((it.id, it) for it in task_items if it.id)
    spec_human = {}
    for proc in c.spec.get('processes') or []:
        for t in proc.get('tasks') or []:
            if t.get('human') and t.get('id'):
                spec_human[t['id']] = t['human']
    for tid in sorted(set(spec_human) - set(doc_tasks)):
        out.append(Finding('12.22', ERROR, path, 0,
                           'task %s has a human gate in the spec, named by no document'
                           % tid))
    for tid in sorted(set(doc_tasks) - set(spec_human)):
        it = doc_tasks[tid]
        out.append(Finding('12.22', ERROR, path, (it.head_line or 0) + 1,
                           'task %s is in the document, but the spec has no human '
                           'gate for it' % tid))
    for tid in sorted(set(doc_tasks) & set(spec_human)):
        it = doc_tasks[tid]
        want = spec_human[tid].get('gate')
        got = it.fields.get('gate')
        if got != want:
            out.append(Finding('12.22', ERROR, path, (it.head_line or 0) + 1,
                               'task %s: document says gate %r, spec says %r'
                               % (tid, got, want)))

    _, trig_items = c.entities_of('automation', 'trigger')
    doc_trigs = dict((it.id, it) for it in trig_items if it.id)
    spec_trigs = set(t.get('id') for t in (c.spec.get('triggers') or []) if t.get('id'))
    for tid in sorted(spec_trigs - set(doc_trigs)):
        out.append(Finding('12.22', ERROR, path, 0,
                           'trigger %s is in the spec, named by no document' % tid))
    for tid in sorted(set(doc_trigs) - spec_trigs):
        it = doc_trigs[tid]
        out.append(Finding('12.22', ERROR, path, (it.head_line or 0) + 1,
                           'trigger %s is in the document, not in the spec' % tid))
    return out


# ---------------------------------------------------------------- 12.23
_OPENABLE = set(['web', 'admin_ui', 'dashboard', 'approval_center', 'form'])
_SCREEN_REF = re.compile(r'^interfaces\[id=([^\]]+)\]$')


@rule('12.23', 'Every screen is declared')
def r_12_23(c):
    doc = c.docs.get('ux_ui')
    if doc is None:
        return []
    out = []
    path = c.rel(doc.path)
    _, screens = c.entities_of('ux_ui', 'screen')

    bound = set()
    by_path = {}
    for it in screens:
        m = _SCREEN_REF.match(it.ref or '')
        if m:
            bound.add(m.group(1))
        p = it.fields.get('path')
        if p:
            by_path.setdefault(p, []).append(it)

    ifaces = dict((i.get('id'), i) for i in (c.spec.get('interfaces') or []))
    for iid in sorted(ifaces):
        i = ifaces[iid]
        if i.get('type') in _OPENABLE and iid not in bound:
            out.append(Finding('12.23', ERROR, path, 0,
                               'interfaces[id=%s] (%s) — a person opens it, and no '
                               'screen in UX-UI.md resolves to it' % (iid, i.get('type'))))

    for p in sorted(by_path):
        its = by_path[p]
        if len(its) > 1:
            ids = ', '.join(sorted(it.id for it in its))
            for it in its:
                out.append(Finding('12.23', ERROR, path, (it.head_line or 0) + 1,
                                   'address %s is shared by %d screens: %s'
                                   % (p, len(its), ids)))

    # SKILL.md qualifies this with "wherever the project declares a prohibition
    # touching that role". Nothing in the spec or the contract says which role a
    # prohibition touches, so the blanket form is what can honestly be computed: it
    # is a strict superset and cannot miss a true positive.
    #
    # Counted off the lines, not off `it.sections`. v3 hands every trailing line to
    # the last label it saw, so an EMPTIED forbidden block followed by any bullet at
    # all inside the same screen reads as full: emptying `register`'s block and
    # leaving one unrelated bullet behind made this rule go quiet.
    lang = doc.header.get('lang') or c.lang
    forb_label = c.prose_label('forbidden', lang)
    for it in screens:
        a, b = it.head_line, it.span[1]
        if not _block_bullets(doc.lines, a, b, forb_label):
            why = ('is empty' if _has_block(doc.lines, a, b, forb_label)
                   else 'is not in this screen at all')
            out.append(Finding('12.23', ERROR, path, (it.head_line or 0) + 1,
                               '%s: "%s" %s — a screen with nothing forbidden is '
                               'a prohibition nobody checked' % (it.id, forb_label, why)))
    return out


# ---------------------------------------------------------------- 12.27
def _index_runs(c, doc, min_run=3):
    """A run of structural lines that enumerates headings appearing further down.

    Two constraints beyond "names a later heading", and both are what an index IS
    rather than a guess: the cited ids are DISTINCT (an index lists each entity
    once) and they come in the SAME ORDER as the headings they point at (an index
    mirrors the document). Without them three ordinary cross-reference bullets —
    "геолокация разобрана в C-06 / спор по часам — в C-14 / счёт за месяц — в C-10",
    which is prose a client writes — were reported as a hand-written index.
    A cross-reference list that happens to run in document order still trips this;
    there is nothing in the data that separates that case from a real index.
    """
    ids = set(it.id for it in doc.items if it.id)
    if not ids:
        return []
    head_line_of = {}
    for it in doc.items:
        if it.id and it.id not in head_line_of:
            head_line_of[it.id] = it.head_line
    pat = re.compile(r'(?<![\w-])(?:' +
                     '|'.join(re.escape(i) for i in sorted(ids, key=len, reverse=True)) +
                     r')(?![\w-])')
    out, run = [], []

    def flush():
        cited = [r[1] for r in run]
        heads = [head_line_of[i] for i in cited]
        if (len(run) >= min_run and len(set(cited)) == len(cited)
                and heads == sorted(heads)):
            n0, ident0, text0 = run[0]
            out.append(Finding('12.27', ERROR, c.rel(doc.path), n0 + 1,
                               'a run of %d lines each naming an id that is also a '
                               'heading further down this document (starting at %s: '
                               '%s) — a hand-written index; generate it into '
                               'generated/INDEX.md instead' % (len(run), ident0, text0)))
        del run[:]

    for n, line in enumerate(doc.lines):
        s = line.strip()
        structural = s.startswith('|') or bool(re.match(r'^[-*]\s', s))
        if not structural:
            flush()
            continue
        m = pat.search(line)
        if not m or head_line_of.get(m.group(0), -1) <= n:
            flush()
            continue
        run.append((n, m.group(0), s[:60]))
    flush()
    return out


@rule('12.27', 'No hand-written index')
def r_12_27(c):
    out = []
    for key in sorted(c.docs):
        out.extend(_index_runs(c, c.docs[key]))
    return out


# ---------------------------------------------------------------- 12.32
def _run_git(cwd, args):
    try:
        r = subprocess.run(['git'] + args, cwd=cwd, capture_output=True,
                           text=True, timeout=15)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    return r.stdout


def _latest_tag(root):
    out = _run_git(root, ['describe', '--tags', '--abbrev=0'])
    return out.strip() if out else None


def _git_root(root):
    out = _run_git(root, ['rev-parse', '--show-toplevel'])
    return out.strip() if out else None


def _git_show(root, tag, rel_path):
    rel_path = rel_path.replace(os.sep, '/')
    return _run_git(root, ['show', '%s:%s' % (tag, rel_path)])


@rule('12.32', 'Acceptance ids are stable', WARNING)
def r_12_32(c):
    doc = c.docs.get('user_cases')
    if doc is None:
        return []
    tag = _latest_tag(c.root)
    if not tag:
        return []                       # no tag reachable — nothing to compare against
    groot = _git_root(c.root)
    if not groot:
        return []
    rel = os.path.relpath(doc.path, groot)
    old_text = _git_show(c.root, tag, rel)
    if not old_text:
        return []                       # file did not exist at that tag — nothing to compare
    lang = doc.header.get('lang') or c.lang
    label = c.prose_label('acceptance', lang)
    old_hdr = v3.header(old_text)
    if (old_hdr.get('version') or None) != (doc.header.get('version') or None):
        return []                       # version bumped — the drop, if any, was declared
    old_doc = v3.read_doc(old_text)
    old_counts = _case_acceptance_counts(old_doc.lines, old_doc.items, label)
    now_counts = _case_acceptance_counts(doc.lines, doc.items, label)
    out = []
    for cid in sorted(old_counts):
        was, now = old_counts[cid], now_counts.get(cid, 0)
        if now < was:
            it = doc.item(cid)
            ln = (it.head_line + 1) if it else 0
            out.append(Finding('12.32', WARNING, c.rel(doc.path), ln,
                               '%s had %d acceptance bullets at %s, has %d now, and '
                               'the document version was not bumped (still %s)'
                               % (cid, was, tag, now, doc.header.get('version'))))
    return out


# ---------------------------------------------------------------- 12.35
@rule('12.35', 'Generated carries everything client says')
def r_12_35(c):
    req_path = os.path.join(c.root, 'generated', 'REQUIREMENTS.md')
    if not os.path.exists(req_path):
        return [Finding('12.35', ERROR, 'generated/REQUIREMENTS.md', 0,
                        'does not exist — every id named in client/*.md must appear '
                        'here once it is generated; right now none of them can be')]
    try:
        req_text = io.open(req_path, encoding='utf-8').read()
    except IOError:
        return []
    out = []
    # Документ, СОБРАННЫЙ из других, не утверждает собственных требований — он
    # объясняет, как пользоваться уже обещанным. HANDBOOK.md ссылается на кейсы
    # (`Кейсы: CC-02`), и обещание живёт там; его собственные id — адреса процедур,
    # чтобы клиент мог прокомментировать одну из них, а ledger записать правку.
    # Требовать их в REQUIREMENTS.md значит требовать, чтобы «как это делают во
    # вторник» стояло рядом с «что обещано», а render_requirements этот документ и
    # не читает. Признак берётся из самого контракта — `derived_seed`, — а не из
    # списка имён: третий такой документ унаследует правило без правки здесь.
    # Измерено 2026-08-29: заполненный HANDBOOK.md дал 41 находку этого правила,
    # и все 41 были ложными.
    for key in [k for k in c.client_keys()
                if (c.path_of(k) or '').replace(os.sep, '/').find('/client/') >= 0
                and not ((c.contract.get('documents') or {}).get(k) or {}).get('derived_seed')]:
        doc = c.docs[key]
        for it in doc.items:
            if not it.id:
                continue
            if not re.search(r'(?<![\w-])' + re.escape(it.id) + r'(?![\w-])', req_text):
                out.append(Finding('12.35', ERROR, c.rel(doc.path), (it.head_line or 0) + 1,
                                   '%s: named here, absent from generated/REQUIREMENTS.md'
                                   % it.id))
    return out
