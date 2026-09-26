#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Migrate a macstack/ folder to the v2 layout and the v2 document format.

Two migrations, run in this order, both destructive, both dry-run by default.

LAYOUT — a flat or docs/-era folder into the four folders, plus the v2 renames
(BUSINESS-LOGIC -> OVERVIEW, SCREENS -> UX-UI, ROLES-AND-TASKS -> AUTOMATION).
Files move with `git mv` so history follows them, and every reference is re-pointed:
a document moving one level deeper turns `../docs/architecture.md` into
`../../docs/architecture.md`. Doing that by pattern breaks links that merely look
alike, so each reference is resolved against its OLD location and re-expressed
against the NEW one. A reference that does not resolve is REPORTED, never guessed at.

FORMAT — v1 tables into v2 entities. One row becomes one entity: the first column is
the id and the title, short factual columns become YAML keys, long prose columns
become anchored sections, and a column holding the same value on every row is stated
once and dropped.

The governing rule of the whole file: **convert what it can prove, report what it
cannot.** A converter that guesses at a client's words to fit a shape does more damage
than an unconverted document, because the damage is invisible afterwards. Where a
required section cannot be filled, it is written with the placeholder marker so the
document is structurally whole and the gap is still visible.

Usage: migrate.py <repo-root> [--apply] [--layout-only] [--format-only]
"""
import sys, os, io, re, subprocess, posixpath

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from i18n import doc_lang, msg                      # noqa: E402
import mdblocks as M                                # noqa: E402
import jsonedit as J                                # noqa: E402

TODO = '_TODO —'

# The gate column held whatever docs.language called it. A converter that accepted only
# the English enum silently set `gate: none` on every task of a Russian project — 33 of
# them on the live one — and `none` reads as "nobody owns this", which is the opposite
# of what the row said.
GATES = {
    'input': 'input', 'ввод': 'input', 'eingabe': 'input', 'ввід': 'input',
    'execute': 'execute', 'исполнение': 'execute', 'выполнение': 'execute',
    'ausführung': 'execute', 'виконання': 'execute',
    'approve': 'approve', 'решение': 'approve', 'утверждение': 'approve',
    'freigabe': 'approve', 'рішення': 'approve',
    'review': 'review', 'проверка': 'review', 'ревью': 'review',
    'prüfung': 'review', 'перевірка': 'review',
    '—': 'none', '-': 'none', '': 'none',
}

MOVES = [
    ('USER-CASES.md',        'client/USER-CASES.md'),
    ('BUSINESS-LOGIC.md',    'client/OVERVIEW.md'),
    ('OPEN-QUESTIONS.md',    'client/OPEN-QUESTIONS.md'),
    ('SCREENS.md',           'client/UX-UI.md'),
    ('ROLES-AND-TASKS.md',   'client/AUTOMATION.md'),
    ('ARCHITECTURE.md',      'generated/ARCHITECTURE.md'),
    ('TEST-CASES.md',        'generated/TEST-CASES.md'),
    ('TASKS.md',             'history/TASKS.md'),
    ('DECISIONS.md',         'history/DECISIONS.md'),
    ('CHANGELOG.md',         'history/CHANGELOG.md'),
    ('log.md',               'history/log.md'),
    ('decisions',            'history/decisions'),
    ('deltas',               'history/deltas'),
    ('reviews',              'history/reviews'),
    ('handoffs',             'history/handoffs'),
    # v1.8 -> v2 renames, already inside the four folders
    ('client/BUSINESS-LOGIC.md',  'client/OVERVIEW.md'),
    ('client/SCREENS.md',         'client/UX-UI.md'),
    ('client/ROLES-AND-TASKS.md', 'client/AUTOMATION.md'),
]
DROP = ['ROLES.md', 'client/ROLES.md']

REF = re.compile(r'(?P<open>\]\(|`)(?P<path>(?:\.\.?/)*[A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:md|json|html|pdf))(?P<close>\)|`)')


def sh(a, cwd):
    return subprocess.run(a, cwd=cwd, capture_output=True, text=True)


def slug(s):
    s = re.sub(r'`|\*|\[|\]', '', s or '').strip().lower()
    s = re.sub(r'[^a-z0-9Ѐ-ӿ]+', '-', s).strip('-')
    return re.sub(r'-+', '-', s) or 'x'


def ascii_slug(s, fallback='item'):
    """Slug for an ID token: ASCII only, per the homoglyph rule."""
    s = re.sub(r'[^A-Za-z0-9]+', '-', (s or '')).strip('-').lower()
    return re.sub(r'-+', '-', s) or fallback


# ============================================================ layout migration
def remap(p, m):
    if p in m:
        return m[p]
    for o, n in m.items():
        if p.startswith(o + '/'):
            return n + p[len(o):]
    return p


def migrate_layout(root, mroot, apply_, lang):
    moves = [(o, n) for o, n in MOVES
             if os.path.exists(os.path.join(mroot, o)) and not os.path.exists(os.path.join(mroot, n))]
    m = dict(moves)
    print('=== LAYOUT (%d) ===' % len(moves))
    for o, n in moves:
        print('  macstack/%-26s -> macstack/%s' % (o, n))
    for d in DROP:
        if os.path.exists(os.path.join(mroot, d)):
            print('  macstack/%-26s -> DROPPED (replaced by client/AUTOMATION.md)' % d)

    if apply_:
        for sub in ('client', 'generated', 'history'):
            os.makedirs(os.path.join(mroot, sub), exist_ok=True)
        for o, n in moves:
            os.makedirs(os.path.dirname(os.path.join(mroot, n)), exist_ok=True)
            r = sh(['git', 'mv', 'macstack/' + o, 'macstack/' + n], root)
            if r.returncode:
                print('  ! git mv %s: %s' % (o, r.stderr.strip()))
        for d in DROP:
            if os.path.exists(os.path.join(mroot, d)):
                sh(['git', 'rm', '-q', 'macstack/' + d], root)

    files = [f for f in sh(['git', 'ls-files'], root).stdout.split('\n')
             if f and f.endswith(('.md', '.ts', '.tsx', '.json', '.example'))]
    nf = nr = 0
    bad = []
    for f in files:
        old_f = f
        if f.startswith('macstack/'):
            inner = f[len('macstack/'):]
            for o, n in m.items():
                if inner == n or inner.startswith(n + '/'):
                    old_f = 'macstack/' + o + inner[len(n):]
                    break
        p = os.path.join(root, f)
        if not os.path.exists(p):
            continue
        try:
            txt = io.open(p, encoding='utf-8').read()
        except Exception:
            continue
        od, nd = posixpath.dirname(old_f), posixpath.dirname(f)
        cnt = [0]

        def fix(mt):
            ref = mt.group('path')
            if not ref.startswith('.'):
                if not ref.startswith('macstack/'):
                    return mt.group(0)
                tgt = 'macstack/' + remap(ref[len('macstack/'):], m)
                if tgt == ref:
                    return mt.group(0)
                cnt[0] += 1
                return mt.group('open') + tgt + mt.group('close')
            a_old = posixpath.normpath(posixpath.join(od, ref))
            a_new = ('macstack/' + remap(a_old[len('macstack/'):], m)) if a_old.startswith('macstack/') else a_old
            # Existence is checked against the OLD path: in a dry run the file has not
            # moved yet, and under --apply it already has. The old path is true before
            # the shuffle in both cases; the new one would lie in the first and stay
            # silent in the second.
            if not (os.path.exists(os.path.join(root, a_old)) or os.path.exists(os.path.join(root, a_new))):
                bad.append('%s -> %s' % (f, ref))
                return mt.group(0)
            rel = posixpath.relpath(a_new, nd or '.')
            if rel == ref:
                return mt.group(0)
            cnt[0] += 1
            return mt.group('open') + rel + mt.group('close')

        out = REF.sub(fix, txt)
        if cnt[0]:
            nf += 1
            nr += cnt[0]
            if apply_:
                io.open(p, 'w', encoding='utf-8').write(out)

    print('  references: %d files, %d links%s' % (nf, nr, '' if apply_ else '  (%s)' % msg(lang, 'dry_run')))
    if bad:
        print('  UNRESOLVED (%d) — check by hand:' % len(bad))
        for u in sorted(set(bad))[:15]:
            print('    ' + u)
    return len(moves)


# ============================================================ format migration
def read(p):
    return io.open(p, encoding='utf-8').read()


def header_of(text, doc_type, lang, version):
    m = re.match(r'^<!--\s*macstack:doc=(\S+)\s+lang=(\S+)\s+version=(\S+)\s*-->', text)
    if m:
        return M.doc_header(m.group(1), m.group(2), version)
    return M.doc_header(doc_type, lang, version)


def bump(v):
    try:
        parts = str(v).split('.')
        return '%d.0' % (int(parts[0]) + 1)
    except Exception:
        return '2.0'


def cur_version(text, default='1'):
    m = re.search(r'macstack:doc=\S+\s+lang=\S+\s+version=([0-9.]+)', text)
    return m.group(1) if m else default


def strip_index_tables(text):
    """Drop hand-written index tables. 12.27.

    An index is a table that DUPLICATES headings standing below it. A table of ids that
    has no headings below is not an index — it is the content, and dropping it destroys
    the document.

    This cost fifteen prohibitions on the live project. The Z- table listed what the
    platform must refuse; there were no `### Z-01` headings under it because the table
    WAS the list. The first cut of this rule only asked "does column one look like an
    id", answered yes, and deleted every one of them silently.
    """
    lines = text.splitlines()
    headings = set(re.findall(r'^#{2,6}\s+~*([A-Z]-\d{2})~*\s*[·.]', text, re.M))
    kill = set()
    for start, head, rows in M.tables(text):
        if not rows:
            continue
        first = [r[0] for r in rows if r]
        ids = [re.sub(r'[*~`\s]', '', c) for c in first]
        idish = sum(1 for c in ids if re.match(r'^[A-Z]-\d{2}$', c))
        # индексом считается только то, что дублирует заголовки ниже
        duplicated = sum(1 for c in ids if c in headings)
        if idish >= max(2, len(first) // 2) and duplicated >= max(2, idish // 2):
            end = start + 2 + len(rows)
            for i in range(start, end):
                kill.add(i)
            # also drop a lone anchor line directly above it
            if start and lines[start - 1].strip().startswith('<!-- macstack:table='):
                kill.add(start - 1)
    return '\n'.join(l for i, l in enumerate(lines) if i not in kill), len(kill)


def cell_to_lines(cell):
    """A prose cell into list items. <br> and '; ' are the two separators seen live."""
    cell = (cell or '').strip()
    if not cell or cell in ('—', '-'):
        return ['%s fill this in._' % TODO]
    parts = [p.strip(' ;.') for p in re.split(r'<br\s*/?>|(?<=[а-яa-z0-9\)])\.\s+(?=[А-ЯA-Z])', cell) if p.strip(' ;.')]
    if len(parts) <= 1:
        return ['- ' + cell.rstrip('.')]
    return ['- ' + p for p in parts]


def carry_journal(old_text, lang):
    """Lift the journal out of a document being rebuilt.

    convert_screens and convert_roles_tasks rebuild their document from the head plus the
    converted entities, which silently dropped everything after the first table — the
    journal included. A living document without a journal fails 12.19, and the rows lost
    are human history that nothing else holds. Found on the live project: UX-UI.md came
    out of the conversion with no journal at all."""
    keep, taking = [], False
    for line in old_text.splitlines():
        if 'macstack:section=journal' in line:
            taking = True
        if taking:
            keep.append(line)
    if keep:
        return keep
    head = (u'| дата | что изменилось |' if lang == 'ru' else u'| date | what changed |')
    return [M.anchor('section', 'journal'),
            u'## Журнал документа' if lang == 'ru' else '## Document journal', '',
            head, '|---|---|']


def convert_screens(text, spec, lang):
    """SCREENS.md 6-column table -> UX-UI.md screen entities."""
    ifaces = {}
    for i in (spec.get('interfaces') or []):
        if i.get('path'):
            ifaces[i['path']] = i.get('id')
    out, n = [], 0
    for start, head, rows in M.tables(text):
        if len(head) < 5:
            continue
        for r in rows:
            r = (r + [''] * 6)[:6]
            title, path, roles, content, actions, forbidden = r
            path_clean = path.strip(' `')
            ident = ifaces.get(path_clean) or ascii_slug(path_clean, ascii_slug(title, 'screen'))
            known = set(r.get('id') for r in (spec.get('roles') or []) if r.get('id'))
            role_ids, role_note = _roles_cell(roles, known)
            y = {'path': path_clean, 'roles': role_ids}
            fields = [('content', 'Что на экране', cell_to_lines(content)),
                      ('actions', 'Что можно сделать', cell_to_lines(actions)),
                      ('forbidden', 'Чего здесь быть не должно', cell_to_lines(forbidden))]
            if role_note:
                fields.insert(0, ('notes', None,
                                  ['%s the v1 document said "%s" here; name the role ids._' % (TODO, role_note)]))
            out.append(M.entity('screen', ident, title.strip(' `'), y, fields))
            n += 1
    return out, n


def _spec_index(spec):
    """name -> id for the things a client document names in words but the spec keys by id."""
    trg, tsk, rol = {}, {}, {}
    for x in (spec.get('triggers') or []):
        if x.get('name'):
            trg[x['name'].strip().lower()] = x.get('id')
    for pr in (spec.get('processes') or []):
        for x in (pr.get('tasks') or []):
            if x.get('name'):
                tsk[x['name'].strip().lower()] = x.get('id')
    for x in (spec.get('roles') or []):
        if x.get('name'):
            rol[x['name'].strip().lower()] = x.get('id')
        if x.get('id'):
            rol[x['id'].strip().lower()] = x.get('id')
    return trg, tsk, rol


def _roles_cell(cell, known):
    """Role ids from a 'who sees it' cell — only ones the spec actually declares.

    The live document wrote 'все без входа' there. Splitting that on whitespace produced
    three role ids that exist nowhere, and a fabricated id is worse than an empty field:
    every cross-reference check downstream believes it."""
    raw = (cell or '').strip()
    toks = [x.strip(' `*') for x in re.split(r'[,/·;]+', raw) if x.strip(' `*')]
    good = [x for x in toks if x in known]
    return good, (raw if raw and not good else None)


def convert_roles_tasks(text, lang, spec=None):
    """ROLES-AND-TASKS.md -> AUTOMATION.md role / task / trigger entities."""
    spec = spec or {}
    trg_by_name, tsk_by_name, rol_by_name = _spec_index(spec)
    roles, tasks, triggers = [], [], []
    lines = text.splitlines()

    # Roles were prose in v1: a heading, then two bold labels. The labels follow
    # docs.language, so match the SHAPE — a bold run ending in a colon — not the words.
    i = 0
    while i < len(lines):
        m = re.match(r'^###\s+(.*?)\s+[\u2014-]\s+`?([A-Za-z0-9][A-Za-z0-9._-]*)`?\s*$', lines[i])
        if not m:
            i += 1
            continue
        title, rid = m.group(1).strip(), m.group(2)
        vals, j = [], i + 1
        while j < len(lines) and not re.match(r'^#{2,3}\s', lines[j]):
            b = re.match(r'^\*\*(.+?):\*\*\s*(.*)$', lines[j].strip())
            if b:
                v = b.group(2).strip()
                k = j + 1
                while k < len(lines) and lines[k].strip() and \
                        not lines[k].lstrip().startswith(('**', '|', '#', '<!--')):
                    v += ' ' + lines[k].strip()
                    k += 1
                vals.append(v)
                j = k
                continue
            j += 1
        if vals:
            y = {'cases': ['%s-*' % rid[0].upper()]}
            for r in (spec.get('roles') or []):
                if r.get('id') == rid:
                    if r.get('cases'):
                        y['cases'] = r['cases']
                    if r.get('isolation'):
                        y['isolation'] = r['isolation']
            fields = [('sees', None, [vals[0]]),
                      ('can', None, [vals[1] if len(vals) > 1
                                     else '%s state what this role may do._' % TODO])]
            roles.append(M.entity('role', rid, title, y, fields))
        i = j
    cur_role = None
    for start, head, rows in M.tables(text):
        # the role this table sits under: nearest '### <name> — `<id>`' above it
        ctx = lines[max(0, start - 40):start]
        for l in reversed(ctx):
            m = re.match(r'^###\s+(.*?)\s+[—-]\s+`?([a-z0-9-]+)`?\s*$', l)
            if m:
                cur_role = (m.group(2), m.group(1))
                break
        if len(head) == 4 and rows and re.search(r'trig|триг', ' '.join(head), re.I):
            for r in rows:
                r = (r + [''] * 4)[:4]
                name, typ, when, raises = [x.strip(' `') for x in r]
                ident = (name if re.match(r'^trg-[a-z0-9-]+$', name)
                         else trg_by_name.get(name.strip().lower())
                         or 'trg-' + ascii_slug(name, 'x'))
                y = {'type': typ or 'manual',
                     'source': {'schedule': 'schedule', 'form': 'interface', 'webhook': 'integration',
                                'db_event': 'backend', 'manual': 'manual'}.get(typ, 'backend')}
                if when and when not in ('—', '-'):
                    y['schedule' if typ == 'schedule' else 'condition'] = when
                if raises and raises not in ('—', '-'):
                    y['raises'] = [raises]
                triggers.append(M.entity('trigger', ident, name, y,
                                         [('what_happens', None, ['%s describe what this raises and for whom._' % TODO])]))
        elif len(head) == 4 and rows:
            for r in rows:
                r = (r + [''] * 4)[:4]
                task, starts, gate, wf = [x.strip(' `') for x in r]
                ident = tsk_by_name.get(task.strip().lower()) or ascii_slug(task, 'task')
                y = {}
                if cur_role:
                    y['role'] = cur_role[0]
                y['gate'] = GATES.get(gate.strip().lower(), 'none')
                if starts and starts not in ('—', '-'):
                    y['trigger'] = starts
                if wf and wf not in ('—', '-'):
                    y['workflow'] = wf
                tasks.append(M.entity('role_task', ident, task, y,
                                      [('flow', None, ['%s describe how this happens._' % TODO])]))
    return roles, tasks, triggers


def convert_open_questions(text):
    """§A five-column table -> open entities. §B is already blocks."""
    out, n = [], 0
    for start, head, rows in M.tables(text):
        if len(head) < 4 or not rows:
            continue
        if not re.match(r'^\*{0,2}~*[A-B]\d+~*\*{0,2}$', (rows[0][0] or '').strip()):
            continue
        for r in rows:
            r = (r + [''] * 5)[:5]
            ident, what, asked, goes, if_wrong = [x.strip() for x in r]
            struck = '~~' in ident
            ident = re.sub(r'[~*`]', '', ident)
            y = {'owner': 'client'}
            if asked and asked not in ('—', '-'):
                y['asked_on'] = asked
            if goes and goes not in ('—', '-'):
                y['goes_to'] = re.sub(r'[`*]', '', goes)[:120]
            title = re.sub(r'\s+', ' ', re.sub(r'[*`]', '', what))[:90]
            fields = [('what', None, cell_to_lines(what)),
                      ('if_wrong', None, cell_to_lines(if_wrong))]
            body = M.entity('open', ident, title, y, fields)
            if struck:
                body = body.replace('### %s ·' % ident, '### ~~%s~~ ·' % ident, 1)
            out.append(body)
            n += 1
    return out, n


def convert_list_fields(text, anchor_kind, id_re):
    """`### <id> · <title>  status` + `- key: value` -> anchor + heading + yaml block.

    Used for TASKS.md and log.md, whose v1 shape was already a key/value list. This is
    the cheap conversion: the fields exist, they just were not fenced."""
    lines = text.splitlines()
    out, i, n = [], 0, 0
    while i < len(lines):
        m = re.match(r'^(#{2,3})\s+(?:\[(\d{4}-\d{2}-\d{2})\]\s+)?(%s)\s*(?:·|\|)?\s*(.*?)\s*$' % id_re, lines[i])
        if not m:
            out.append(lines[i]); i += 1; continue
        level, date, ident, rest = m.group(1), m.group(2), m.group(3), m.group(4)
        status = None
        sm = re.search(r'\s(todo|doing|blocked|done|dropped)\s*[·▶⏸✓⊘]?\s*$', rest)
        if sm:
            status = sm.group(1); rest = rest[:sm.start()].strip()
        j = i + 1
        y, body = {}, []
        while j < len(lines) and not re.match(r'^#{1,3}\s', lines[j]):
            km = re.match(r'^-\s+(\w[\w_]*):\s*(.*)$', lines[j])
            if km:
                key, val = km.group(1), km.group(2).strip()
                cont = j + 1
                while cont < len(lines) and re.match(r'^\s{2,}\S', lines[cont]) and not lines[cont].lstrip().startswith('- '):
                    val += ' ' + lines[cont].strip(); cont += 1
                j = cont - 1
                if val and val not in ('—', '-'):
                    y[key] = M._scalar(val) if not re.search(r'[,]', val) or key in ('acceptance', 'spec') else \
                        [x.strip() for x in val.split(',') if x.strip()]
            elif lines[j].strip():
                body.append(lines[j])
            j += 1
        if status:
            y = dict([('status', status)] + list(y.items()))
        if date:
            y = dict([('date', date)] + list(y.items()))
        fields = []
        if body:
            fields.append(('notes', None, [b for b in body if b.strip()]))
        blk = M.entity(anchor_kind, ident, rest or ident, y, fields, level=len(level))
        out.extend(blk.rstrip('\n').split('\n'))
        n += 1
        i = j
    return '\n'.join(out), n


def convert_cases(text):
    """`### C-04 · Title   [критично]` -> anchor + heading + yaml + anchored acceptance."""
    lines = text.splitlines()
    out, i, n = [], 0, 0
    while i < len(lines):
        m = re.match(r'^###\s+(~*[A-Z]-\d{2}~*)\s*·\s*(.*?)(?:\s{2,}\[(.+?)\])?\s*$', lines[i])
        if not m:
            out.append(lines[i]); i += 1; continue
        ident, title, prio = re.sub(r'~', '', m.group(1)), m.group(2), m.group(3)
        prio_map = {'критично': 'critical', 'важно': 'important', 'желательно': 'nice-to-have'}
        y = {}
        if prio:
            y['priority'] = prio_map.get(prio.strip().lower(), prio.strip())
        j, body = i + 1, []
        while j < len(lines) and not re.match(r'^#{1,3}\s', lines[j]):
            body.append(lines[j]); j += 1
        # split the acceptance block off: a bold line ending in ':' followed by bullets
        acc_at = None
        for k, l in enumerate(body):
            if re.match(r'^\*\*.*:\*\*\s*$', l.strip()) and k + 1 < len(body) and body[k + 1].lstrip().startswith('- '):
                acc_at = k
        out.append(M.anchor('case', ident))
        out.append('### %s · %s' % (ident, title))
        out.append('')
        if y:
            out += ['```yaml', M.dump_yaml(y), '```', '']
        if acc_at is None:
            out += [x for x in body]
            out += ['', M.anchor('acceptance'), '%s no acceptance list was found in the v1 document._' % TODO, '']
        else:
            intro = [x for x in body[:acc_at] if x.strip()]
            if intro:
                out += intro + ['']
            out.append(M.anchor('acceptance'))
            out += body[acc_at:]
        out.append('')
        n += 1
        i = j
    return '\n'.join(out), n


RENAMED_FROM = {
    'client/OVERVIEW.md':   ['client/BUSINESS-LOGIC.md', 'BUSINESS-LOGIC.md'],
    'client/UX-UI.md':      ['client/SCREENS.md', 'SCREENS.md'],
    'client/AUTOMATION.md': ['client/ROLES-AND-TASKS.md', 'ROLES-AND-TASKS.md'],
    'client/USER-CASES.md': ['USER-CASES.md'],
    'client/OPEN-QUESTIONS.md': ['OPEN-QUESTIONS.md'],
    'history/TASKS.md':     ['TASKS.md'],
    'history/log.md':       ['log.md'],
}


def resolve(mroot, rel):
    """The file's path now. A dry run happens BEFORE the layout rename, so the format
    pass has to accept the old name as well — otherwise it converts nothing and reports
    a success the run did not achieve."""
    p = os.path.join(mroot, rel)
    if os.path.exists(p):
        return p
    for old in RENAMED_FROM.get(rel, []):
        q = os.path.join(mroot, old)
        if os.path.exists(q):
            return q
    return None


WRITE_ONCE = ('history/decisions/', 'history/deltas/', 'history/reviews/', 'history/handoffs/')


def is_write_once(rel):
    """History is not rewritten to fit a new format.

    A ruling, a delta, a review and a handoff are write-once by contract: their date is
    in the filename and editing one of them is itself the defect. Converting them would
    make every returned client comment and every `applied` banner resolve against a file
    that no longer says what it said. They are reported and left alone."""
    rel = rel.replace(os.sep, '/')
    return any(rel.startswith(w) for w in WRITE_ONCE)


def convert_manifest(text):
    """inbox/README.md six-column table -> intake entities."""
    out, n = [], 0
    for start, head, rows in M.tables(text):
        if len(head) < 4 or not rows:
            continue
        for r in rows:
            r = (r + [''] * 6)[:6]
            fname, received, frm, chan, sup, proc = [x.strip(' `*') for x in r]
            if not fname or fname in ('—', '-'):
                continue
            y = {'received': received or None}
            for key, val in (('from', frm), ('channel', chan), ('supersedes', sup), ('processed_in', proc)):
                if val and val not in ('—', '-'):
                    y[key] = val
            out.append(M.entity('intake', fname, fname, y, []))
            n += 1
    return out, n


def convert_decisions(text):
    """DECISIONS.md five-column registry -> groups by the rulings file that holds the argument.

    The fifth column repeated the same path twenty-one times in a row in the live
    project. That column is the grouping, so it becomes the heading."""
    groups, order, n = {}, [], 0
    for start, head, rows in M.tables(text):
        if len(head) < 4 or not rows:
            continue
        if not re.match(r'^\*{0,2}D\d+', (rows[0][0] or '').strip()):
            continue
        for r in rows:
            r = (r + [''] * 5)[:5]
            ident, date, title, who, fil = [x.strip(' `*') for x in r]
            ident = re.sub(r'[~*`]', '', ident)
            key = fil or 'unfiled'
            if key not in groups:
                groups[key] = []
                order.append(key)
            groups[key].append('- **%s** · %s · %s — %s' % (ident, date or '—', title, who or '—'))
            n += 1
    out = []
    for key in order:
        slug_id = ascii_slug(os.path.basename(key).replace('.md', ''), 'unfiled')
        out.append(M.entity('rulings', slug_id, key, {'file': key},
                            [('decisions', None, groups[key])]))
    return out, n


def convert_milestones(text):
    """TASKS.md milestone table -> milestone entities with a falsifiable done_when list.

    The live document packed its criteria into one cell separated by <br>, which is the
    surest sign a cell wanted to be a list."""
    out, n = [], 0
    for start, head, rows in M.tables(text):
        if len(head) < 3 or not rows:
            continue
        if not re.match(r'^\*{0,2}M\d+\*{0,2}$', (rows[0][0] or '').strip()):
            continue
        for r in rows:
            r = (r + [''] * 4)[:4]
            ident, title, status, done = [x.strip(' `*') for x in r]
            ident = re.sub(r'[~*`]', '', ident)
            st = 'todo'
            for k in ('done', 'doing', 'blocked', 'dropped', 'todo'):
                if k in status.lower():
                    st = k
                    break
            if '✓' in status:
                st = 'done'
            elif '▶' in status:
                st = 'doing'
            elif '⏸' in status:
                st = 'blocked'
            elif '⊘' in status:
                st = 'dropped'
            crit = [c.strip(' ·-') for c in re.split(r'<br\s*/?>', done) if c.strip(' ·-')]
            body = ['- ' + c for c in crit] if crit else ['%s no falsifiable checks were recorded._' % TODO]
            out.append(M.entity('milestone', ident, title, {'status': st},
                                [('done_when', None, body)], level=2))
            n += 1
    return out, n


def migrate_format(mroot, spec, lang, apply_):
    changed = []

    def write(path, text, note):
        rel = os.path.relpath(path, mroot)
        changed.append((rel, note))
        if apply_:
            io.open(path, 'w', encoding='utf-8').write(text.rstrip('\n') + '\n')

    # --- USER-CASES.md: drop the index tables, convert the case headings
    p = resolve(mroot, 'client/USER-CASES.md')
    if p:
        t = read(p)
        t, killed = strip_index_tables(t)
        t, n = convert_cases(t)
        v = bump(cur_version(t, '1'))
        t = re.sub(r'^<!--\s*macstack:doc=.*?-->', M.doc_header('user_cases', lang, v), t, count=1)
        write(p, t, '%d cases converted, %d index rows dropped' % (n, killed))

    # --- UX-UI.md (already renamed by the layout pass)
    p = resolve(mroot, 'client/UX-UI.md')
    if p:
        t = read(p)
        ents, n = convert_screens(t, spec, lang)
        if n:
            head = t.split('<!-- macstack:table=')[0].rstrip()
            head = re.sub(r'^<!--\s*macstack:doc=.*?-->', M.doc_header('ux_ui', lang, bump(cur_version(t))), head, count=1)
            body = [head, '', M.anchor('section', 'screens'), '## Экраны' if lang == 'ru' else '## Screens', '']
            body += ents
            body += [''] + carry_journal(t, lang)
            write(p, '\n'.join(body), '%d screens converted from the 6-column table' % n)

    # --- AUTOMATION.md
    p = resolve(mroot, 'client/AUTOMATION.md')
    if p:
        t = read(p)
        roles, tasks, triggers = convert_roles_tasks(t, lang, spec)
        if roles or tasks or triggers:
            head = t.split('<!-- macstack:table=')[0].rstrip()
            head = re.sub(r'^<!--\s*macstack:doc=.*?-->', M.doc_header('automation', lang, bump(cur_version(t))), head, count=1)
            body = [head, '']
            if roles:
                body += [M.anchor('section', 'roles'), '## Роли' if lang == 'ru' else '## Roles', ''] + roles
            if tasks:
                body += [M.anchor('section', 'tasks'), '## Задачи' if lang == 'ru' else '## Tasks', ''] + tasks
            if triggers:
                body += [M.anchor('section', 'triggers'), '## Триггеры' if lang == 'ru' else '## Triggers', ''] + triggers
            body += [''] + carry_journal(t, lang)
            write(p, '\n'.join(body), '%d roles, %d tasks, %d triggers converted'
                  % (len(roles), len(tasks), len(triggers)))

    # --- OPEN-QUESTIONS.md §A
    p = resolve(mroot, 'client/OPEN-QUESTIONS.md')
    if p:
        t = read(p)
        ents, n = convert_open_questions(t)
        if n:
            keep = []
            lines = t.splitlines()
            kill = set()
            for start, head, rows in M.tables(t):
                if rows and re.match(r'^\*{0,2}~*[A-B]\d+~*', (rows[0][0] or '').strip()):
                    for i in range(start, start + 2 + len(rows)):
                        kill.add(i)
            for i, l in enumerate(lines):
                if i in kill:
                    if i == min(kill):
                        keep.extend(x.rstrip('\n') for x in ents)
                    continue
                keep.append(l)
            write(p, '\n'.join(keep), '%d client items converted from the 5-column table' % n)

    # --- TASKS.md and log.md: the key/value lists become fenced yaml
    for rel, kind, id_re, doc in (('history/TASKS.md', 'task', r'M\d+-T\d+|BL-\d+|M\d+', 'tasks'),
                                  ('history/log.md', 'entry', r'\w+', 'log')):
        p = resolve(mroot, rel)
        if not p:
            continue
        t = read(p)
        t2, n = convert_list_fields(t, kind, id_re)
        if n:
            write(p, t2, '%d entries fenced' % n)

    # --- inbox manifest
    p = resolve(mroot, 'inbox/README.md')
    if p:
        tx = read(p)
        ents, n = convert_manifest(tx)
        if n:
            head = tx.split('|')[0].rstrip()
            body = [head, ''] + ents
            write(p, '\n'.join(body), '%d intake entries converted' % n)

    # --- decisions registry
    p = resolve(mroot, 'history/DECISIONS.md')
    if p:
        tx = read(p)
        ents, n = convert_decisions(tx)
        if n:
            lines = tx.splitlines()
            kill = set()
            for start, head, rows in M.tables(tx):
                if rows and re.match(r'^\*{0,2}D\d+', (rows[0][0] or '').strip()):
                    for i in range(start, start + 2 + len(rows)):
                        kill.add(i)
            keep = []
            for i, l in enumerate(lines):
                if i in kill:
                    if i == min(kill):
                        keep.extend('\n'.join(ents).split('\n'))
                    continue
                keep.append(l)
            write(p, '\n'.join(keep), '%d decisions grouped by their rulings file' % n)

    # --- milestone table
    p = resolve(mroot, 'history/TASKS.md')
    if p:
        tx = read(p)
        ents, n = convert_milestones(tx)
        if n:
            lines = tx.splitlines()
            kill = set()
            for start, head, rows in M.tables(tx):
                if rows and re.match(r'^\*{0,2}M\d+\*{0,2}$', (rows[0][0] or '').strip()):
                    for i in range(start, start + 2 + len(rows)):
                        kill.add(i)
            keep = []
            for i, l in enumerate(lines):
                if i in kill:
                    if i == min(kill):
                        keep.extend('\n'.join(ents).split('\n'))
                    continue
                keep.append(l)
            write(p, '\n'.join(keep), '%d milestones converted' % n)

    # --- generated documents are deleted, not converted: they regenerate
    for rel in ('generated/ARCHITECTURE.md', 'generated/INDEX.md', 'README.md'):
        p = os.path.join(mroot, rel)
        if os.path.exists(p):
            changed.append((rel, 'deleted — regenerates with render.py'))
            if apply_:
                os.remove(p)

    print('\n=== FORMAT (%d) ===' % len(changed))
    for rel, note in changed:
        print('  %-32s %s' % (rel, note))
    return len(changed)


DOCS_FILES_RENAME = [
    ('business_logic', 'overview',   'client/OVERVIEW.md'),
    ('screens',        'ux_ui',      'client/UX-UI.md'),
    ('roles_tasks',    'automation', 'client/AUTOMATION.md'),
]
DOCS_FILES_NEW = [
    ('handbook', 'client/HANDBOOK.md', 'client'),
    ('index',    'generated/INDEX.md', 'both'),
    ('readme',   'README.md',          'internal'),
]


def migrate_spec(mroot, lang, apply_):
    """docs.files still names the documents by their v1 keys and paths after the move.

    Missed on the first run against the live project: every file had been renamed and the
    spec still pointed at BUSINESS-LOGIC.md, SCREENS.md and ROLES-AND-TASKS.md, which
    12.1 reads as three missing documents. A migration that renames files and leaves the
    index behind has not finished.

    Edited as TEXT, not reserialized. json.dump(indent=2) on a live spec turned 959 lines
    into 4119: the file is hand-formatted, short objects inlined, and no width heuristic
    reproduces that. A whole-file reformat makes a three-line change unreviewable."""
    import json
    sp = os.path.join(mroot, 'macstack.json')
    if not os.path.exists(sp):
        return 0
    raw = io.open(sp, encoding='utf-8').read()
    try:
        spec = json.loads(raw)
    except ValueError as e:
        print('  macstack.json does not parse: %s' % e)
        return 0
    files = ((spec.get('docs') or {}).get('files')) or {}
    if not files:
        return 0

    done = []
    for old, new_key, new_path in DOCS_FILES_RENAME:
        if old not in files or new_key in files:
            continue
        try:
            raw = J.set_value(raw, ['docs', 'files', old, 'path'], new_path)
            raw = J.rename_key(raw, ['docs', 'files'], old, new_key)
            done.append('%s -> %s' % (old, new_key))
        except Exception as e:                       # a spec shaped unexpectedly is reported
            print('  could not re-key %s: %s' % (old, e))

    for key, path, audience in DOCS_FILES_NEW:
        if key in files:
            continue
        entry = {'path': path, 'version': '1.0', 'audience': audience}
        if audience != 'internal':
            entry['language'] = (spec.get('docs') or {}).get('language', 'en')
        try:
            raw = J.insert_key(raw, ['docs', 'files'], key, entry)
            done.append('+ %s' % key)
        except Exception as e:
            print('  could not add %s: %s' % (key, e))

    if not done:
        return 0
    print('\n=== SPEC ===')
    for d in done:
        print('  docs.files  %s' % d)
    before = len(io.open(sp, encoding='utf-8').read().splitlines())
    print('  %d lines before, %d after — formatting preserved' % (before, len(raw.splitlines())))
    if apply_:
        io.open(sp, 'w', encoding='utf-8').write(raw)
    return len(done)


# ============================================================ report
def audit(mroot, lang, apply_=True):
    """What is still out of shape. Never fails the run."""
    print('\n=== REMAINING %s ===' % ('' if apply_ else '(state on disk now — a dry run changed nothing)'))
    hits = 0
    for dirpath, _, names in os.walk(mroot):
        for nm in sorted(names):
            if not nm.endswith('.md'):
                continue
            p = os.path.join(dirpath, nm)
            rel = os.path.relpath(p, mroot)
            try:
                t = read(p)
            except Exception:
                continue
            if is_write_once(rel):
                continue
            for line, cols, ln, cell, why in M.table_violations(t):
                print('  %s:%d  %s' % (rel, line, why))
                hits += 1
            r = M.foreign_ratio(t, lang)
            if r > 0.15:
                client = rel.replace(os.sep, '/').startswith('client/')
                print('  %s  %s language: %d%% of the prose is not %s'
                      % (rel, 'MUST FIX —' if client else 'note —', round(r * 100), lang))
                hits += 1 if client else 0
            todos = t.count(TODO)
            if todos:
                print('  %s  %d placeholder(s) a human must fill' % (rel, todos))
    if not hits:
        print('  none')
    return hits


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = set(a for a in sys.argv[1:] if a.startswith('--'))
    root = args[0] if args else '.'
    apply_ = '--apply' in flags
    mroot = os.path.join(root, 'macstack')
    if not os.path.isdir(mroot):
        mroot = root if os.path.exists(os.path.join(root, 'macstack.json')) else mroot
    if not os.path.isdir(mroot):
        print(msg('en', 'no_folder', dir=root))
        return 1
    lang = doc_lang(mroot)
    import json
    spec = {}
    sp = os.path.join(mroot, 'macstack.json')
    if os.path.exists(sp):
        try:
            spec = json.load(io.open(sp, encoding='utf-8'))
        except Exception:
            pass

    if '--format-only' not in flags:
        migrate_layout(root, mroot, apply_, lang)
    if '--layout-only' not in flags:
        migrate_format(mroot, spec, lang, apply_)
        migrate_spec(mroot, lang, apply_)
    audit(mroot, lang, apply_)

    if not apply_:
        print('\n%s. Read the first converted document, then re-run with --apply.' % msg(lang, 'dry_run'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
