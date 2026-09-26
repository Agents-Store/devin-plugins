# -*- coding: utf-8 -*-
"""Rule group 12, `history/` half — the journal, the task list, the releases.

None of the three documents here are `format: v3` (see `doc-contracts.json`):
`log.md`, `TASKS.md` and `CHANGELOG.md` are still the anchored-yaml shape
`mdblocks` reads, and `Ctx` only puts a `v3.Doc` in `c.docs` for a `v3` contract
entry — these three live in `c.text` as raw strings instead.

`mdblocks.parse()` gets the nesting, the section grouping and the one fenced
`yaml` block right, but it tracks a line number for an anchor's OWN line and for
nothing else — no heading line, nothing inside a body. Every rule below needs a
line to report, so `_entities()` re-walks the same anchor/heading/fence grammar
(`mdblocks.ANCHOR`, `.HEADING`, `.FENCE`, `.parse_yaml` — the same primitives,
not a second guess at them) keeping a line number on every piece it keeps. This
is the local workaround the brief for this module allows: `lint_folder.py` and
`mdblocks.py` are not mine to change, and the gap was real.

TWO SHAPES, NOT ONE. An earlier draft of this module read the anchored shape and
only that, which is the shape `migrate.py` leaves behind. But the contract's own
`heading` for a log entry is `## [<YYYY-MM-DD>] <kind> | <title>` and every
example in `skills/journal/SKILL.md` — the skill that tells an author how to
write one — is unanchored. A log written the way the plugin documents was
therefore invisible: a `work` entry with a nonsense kind went unreported, and,
worse, a CORRECT document was reported broken (12.20 announced an unrecorded
handoff file, 12.26 a done task with no `work` entry, both of which the log named
in plain sight). So `_entities` recognises an entity by its anchor OR by a heading
whose leading token matches that entity's `id_space` pattern from the contract —
never by guessing at a shape neither of those two declares.

BODIES END. The same draft ended an entity's body only at the next anchor of the
same kind, so bullets belonging to a LATER entry silenced a required-field
finding on an EARLIER one: appending a `work` entry that happened to carry
`source:` dropped 12.13 from 19 findings to 18. A body now ends at the next
entity, at a `section=` anchor, and at any heading no deeper than the entity's
own — which is where a reader would end it too.

FIELD BLOCKS ARE ADDRESSED. `field_body` keeps each `<!-- macstack:<field> -->`
block's own lines, because "the milestone has a bullet somewhere" is not the
question 12.16 asks: an empty `done_when` beside a chatty `notes` passed, and a
`не выполнено` written in `notes` about something else failed a done milestone.

Rewiring note for whoever restructures `history/`: 12.13, 12.19, 12.20 and
12.26 all read `log.md`'s `entries` section directly; 12.14, 12.16 and 12.26
read `TASKS.md`'s `milestones`/`tasks` sections; 12.15 reads both `log.md` and
`CHANGELOG.md`'s `releases` section. Whatever replaces `log.md` with a machine
ledger needs equivalents of `_log_entries()` and of `_fields()`'s bold/plain/yaml
union — nothing here assumes markdown past that one call site per rule.
"""
import datetime, os, re

from lint_folder import rule, Finding, ERROR, WARNING
import mdblocks

# Only for the catalogue of journal headings, per language — the renderer owns
# that list, and a second copy of it here would be the thing rule 12.5 forbids.
try:
    import render as _render
except Exception:                                                 # noqa: BLE001
    _render = None

BOLD_FIELD = re.compile(r'^\s*[-*]\s+\*\*([A-Za-z][A-Za-z_]*):\*\*\s*(.*)$')
PLAIN_FIELD = re.compile(r'^\s*[-*]\s+([A-Za-z][A-Za-z_]*):\s*(.*)$')
BULLET = re.compile(r'^\s*[-*]\s+\S')
STRUCK = re.compile(r'^~~(.+?)~~\s*(.*)$')
DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
ISO = re.compile(r'\d{4}-\d{2}-\d{2}')
# The contract's own heading for a log entry, and the one every example in the
# `journal` skill writes: `## [2026-08-24] work | M11 — split the export run`.
# The brackets are optional because the corpus has them off as often as on.
ENTRY_HEAD = re.compile(
    r'^#{2,6}\s+\[?(\d{4}-\d{2}-\d{2})\]?\s+([A-Za-z][A-Za-z0-9_-]*)\s*[|·—–-]\s*\S')
ID_HEAD = re.compile(r'^#{2,6}\s+(\S+)')
JOURNAL_ITEM = re.compile(r'^\s*[-*]\s+\*\*(\d{4}-\d{2}-\d{2})\*\*\s*[—–-]?\s*(.*)$')
SEP = re.compile(r'^\s*[|·—–-]\s*')
DECOR = u'~*`'
# "не выполнено" is the literal marker the live corpus uses on M15's checks (see
# the lint brief); the English forms are the same idea for a document that never
# switches alphabets. Not exhaustive by design — a marker this rule does not
# know about is a marker it says nothing about, which is the honest failure mode.
UNMET = re.compile(r'не\s+выполнен\w*|\bnot\s+met\b|\bnot\s+fulfilled\b|\bunmet\b|[✗❌]', re.I)


# ---------------------------------------------------------------- shared reading
def _head_entity(raw, id_pattern, dated_head):
    """(id, {extra fields}) when this heading STARTS an entity, else None.

    Recognition is by the contract, never by shape alone: a dated head must carry
    an ISO date and a kind, and an id head's leading token must match the
    `id_spaces` pattern of the entity being looked for. `## Вехи` is not a
    milestone because `Вехи` does not match `^M[0-9]+$`, and that is the only
    reason it is not — no heading is excluded by a list of words.
    """
    if dated_head:
        m = ENTRY_HEAD.match(raw)
        return (m.group(2), {'date': m.group(1)}) if m else None
    if not id_pattern:
        return None
    m = ID_HEAD.match(raw)
    if not m:
        return None
    tok = m.group(1).strip(DECOR)
    return (tok, {}) if re.match(id_pattern, tok) else None


def _entities(text, anchor_kind, section=None, id_pattern=None, dated_head=False,
              siblings=()):
    """Every entity of one kind in `text`, in order, with a line on every piece.

    Each item: `id` (the anchor's ident or the heading's leading token, unstruck),
    `heading` (raw heading text, struck marker and all), `yaml` (the one fenced
    block, if any), `body` ([(1-indexed line, raw line), ...]), `field_body`
    ({`<!-- macstack:<field> -->` name: its own [(line, raw)]}), `blocks` (those
    field names in order), `line` (the heading's 1-indexed line, 0 when the entity
    carried no heading), `level`, `struck` and `why` (whether a struck heading
    names a reason after an em dash, per `TASKS.md`'s `struck_form`).

    `section` restricts to entities whose nearest enclosing `section=` anchor has
    that id — `log.md` anchors its own section titles as stray `entry` entities,
    and without this a `howto` heading would be graded as a malformed journal
    entry. A document carrying no `section=` anchor at all is not filtered: the
    anchors are a migration artefact, and demanding one would make every rule
    here silent on a hand-written file, which is the failure this module exists
    to stop being.
    """
    lines = text.splitlines()
    sectioned = any(mdblocks.ANCHOR.match(l) and mdblocks.ANCHOR.match(l).group(1) == 'section'
                    for l in lines)
    if not sectioned:
        section = None
    out, cur_section, cur, field = [], None, None, None
    in_fence, fence_lines, fence_lang = False, [], None

    def keep(pairs):
        cur['body'].extend(pairs)
        if field is not None:
            cur['field_body'].setdefault(field, []).extend(pairs)

    def begin(ident, lineno, heading, level, extra=None):
        if section is not None and cur_section != section:
            return None
        e = {'id': ident, 'heading': heading, 'level': level, 'yaml': {}, 'body': [],
             'field_body': {}, 'blocks': [], 'line': lineno, 'extra': extra or {}}
        out.append(e)
        return e

    for i, raw in enumerate(lines):
        n = i + 1
        fm = mdblocks.FENCE.match(raw)
        if in_fence:
            if fm and fm.group(1) is None:
                if fence_lang == 'yaml' and cur is not None and not cur['yaml']:
                    cur['yaml'] = mdblocks.parse_yaml('\n'.join(t for _, t in fence_lines))
                elif cur is not None:
                    keep(fence_lines)
                in_fence = False
            else:
                fence_lines.append((n, raw))
            continue
        if fm:
            in_fence, fence_lines, fence_lang = True, [], fm.group(1)
            continue
        am = mdblocks.ANCHOR.match(raw)
        if am:
            kind, ident = am.group(1), am.group(2)
            if kind == 'section':
                cur_section, cur, field = ident, None, None
            elif kind == anchor_kind:
                cur, field = begin(ident, None, None, None), None
            elif kind in siblings:
                cur, field = None, None          # a neighbouring entity starts here
            elif cur is not None:
                field = kind                     # a field block inside this entity
                cur['blocks'].append(kind)
                cur['field_body'].setdefault(kind, [])
            continue
        hm = mdblocks.HEADING.match(raw)
        if hm:
            level, title = len(hm.group(1)), hm.group(2)
            if cur is not None and cur['line'] is None:
                cur['heading'], cur['line'], cur['level'] = title, n, level
                continue
            new = _head_entity(raw, id_pattern, dated_head)
            if new is not None:
                cur, field = begin(new[0], n, title, level, new[1]), None
            elif cur is not None and cur['level'] is not None and level <= cur['level']:
                cur, field = None, None          # an unrelated heading ends the entity
            continue
        if cur is not None and raw.strip():
            keep([(n, raw)])
    if in_fence and cur is not None:              # unterminated fence — don't lose the tail
        if fence_lang == 'yaml' and not cur['yaml']:
            cur['yaml'] = mdblocks.parse_yaml('\n'.join(t for _, t in fence_lines))
        else:
            keep(fence_lines)
    for e in out:
        if e['line'] is None:
            e['line'] = 0
        m = STRUCK.match((e['heading'] or '').strip())
        e['struck'] = bool(m)
        e['why'] = bool(m and '—' in (m.group(2) or ''))
    return out


def _fields(e):
    """{lowercase key: value} — the yaml block first (how `TASKS.md` stores
    `status`/`tracker`), then anything the heading itself declared (an unanchored
    log entry carries its date there and nowhere else), then any bold
    (`- **key:** …`) or plain (`- key: …`) bullet of the same shape (how
    `log.md`'s `handoff`/`work`/`release` fields are written per the `journal`
    skill's own examples) — whichever the entity actually used, a rule asking
    "does it have `key`" gets one answer."""
    out = {}
    for k, v in (e.get('yaml') or {}).items():
        out[str(k).lower()] = v
    for k, v in (e.get('extra') or {}).items():
        out.setdefault(str(k).lower(), v)
    for _, raw in e.get('body') or []:
        m = BOLD_FIELD.match(raw) or PLAIN_FIELD.match(raw)
        if m:
            out.setdefault(m.group(1).lower(), m.group(2).strip())
    return out


def _as_list(v):
    """A field's value as flat string tokens, whichever shape it was written in:
    a plain bullet (`- tasks: M11-T42, M11-T43`, a comma/space string) or a YAML
    `tasks: [M11-T42, M11-T43]` inside the fence — `parse_yaml` already turns the
    second into a real list, so treating both alike here is what keeps a caller
    from having to know which one a given entry happened to use."""
    if v is None:
        return []
    if isinstance(v, (list, tuple)):
        return [str(x).strip('` ') for x in v if str(x).strip('` ')]
    return [t.strip('` ') for t in re.split(r'[,\s]+', str(v)) if t.strip('` ')]


def _as_text(v):
    """A field's value as one string — guards a `.strip()`/regex call against a
    value that came back as a YAML list or number instead of the plain scalar
    the field is documented to be."""
    if v is None:
        return None
    if isinstance(v, (list, tuple)):
        return str(v[0]) if v else None
    return str(v)


def _entity_decl(c, doc_key, kind):
    for e in ((c.contract.get('documents') or {}).get(doc_key) or {}).get('entities') or []:
        if e.get('kind') == kind:
            return e
    return None


def _id_pattern(c, decl):
    """The `id_spaces` pattern this entity's ids live in, or None.

    Read off the entity's own `id_space` rather than hard-coded, so a renamed or
    re-patterned space moves both the writer and this reader at once."""
    space = (decl or {}).get('id_space')
    return ((c.contract.get('id_spaces') or {}).get(space) or {}).get('pattern')


def _relpath(c, key, fallback):
    p = c.path_of(key)
    return c.rel(p) if p else fallback


def _log_entries(c):
    """Every `log.md` journal entry, anchored or written the documented way."""
    text = c.text.get('log')
    if text is None:
        return []
    return _entities(text, 'entry', section='entries', dated_head=True)


# ---------------------------------------------------------------- 12.13

@rule('12.14', 'Every task is tracked in both places')
def r_12_14(c):
    """The file says what the work IS; the tracker is where the conversation happens.

    A task living in only one of the two is a task half the team cannot see. A task
    still in `backlog` is exempt: it has not been sent anywhere yet, and demanding a
    tracker id from it demands that somebody invent one.
    """
    out = []
    doc = c.docs.get('tasks')
    if doc is None:
        return out
    decl = None
    for e in ((c.contract.get('documents') or {}).get('tasks') or {}).get('entities') or []:
        if e['kind'] == 'task':
            decl = e
    states = set((c.contract.get('fields') or {}).get('status', {}).get('enum') or [])
    exempt = {'backlog', 'cancelled'}
    for it in doc.items:
        if it.level < 3 or not it.id or not re.match(r'^M\d+-T\d+$', it.id):
            continue
        ln = (it.head_line or 0) + 1
        st = str(it.get('status') or '').strip().lower()
        if not st:
            out.append(Finding('12.14', ERROR, 'history/TASKS.md', ln,
                               '%s declares no status' % it.id))
        elif states and st not in states:
            out.append(Finding('12.14', ERROR, 'history/TASKS.md', ln,
                               '%s has status %r, not one of %s'
                               % (it.id, st, ', '.join(sorted(states)))))
        if not it.get('tracker') and st not in exempt:
            out.append(Finding('12.14', ERROR, 'history/TASKS.md', ln,
                               '%s is %s and carries no tracker id' % (it.id, st or '—')))
        head = doc.lines[it.head_line] if it.head_line is not None else ''
        if '~~' in head and 'why' not in ' '.join(it.body).lower() \
                and not re.search(r'снят|cancel|отменен', ' '.join(it.body), re.I):
            out.append(Finding('12.14', ERROR, 'history/TASKS.md', ln,
                               '%s is struck through and does not say why' % it.id))
    return out

@rule('12.16', 'Milestones are falsifiable')
def r_12_16(c):
    text = c.text.get('tasks')
    decl = _entity_decl(c, 'tasks', 'milestone')
    if text is None:
        return []
    p = _relpath(c, 'tasks', 'history/TASKS.md')
    want = ((decl or {}).get('prose_required') or ['done_when'])[0]
    out = []
    for e in _entities(text, 'milestone', section='milestones',
                       id_pattern=_id_pattern(c, decl), siblings=('task', 'backlog')):
        block = e['field_body'].get(want)
        # No block at all: the milestone may be written without anchors, so every
        # bullet it carries is a candidate check. With a block, only its own lines
        # count — an empty `done_when` beside a chatty `notes` is still empty.
        source = e['body'] if block is None else block
        checks = [(ln, raw) for ln, raw in source if BULLET.match(raw)]
        if not checks:
            out.append(Finding('12.16', ERROR, p, e['line'],
                               '%s declares no %s checks%s'
                               % (e['id'], want,
                                  ' — the block is there and empty' if block is not None else '')))
            continue
        if _as_text(_fields(e).get('status')) == 'done':
            for ln, raw in checks:
                if UNMET.search(raw):
                    out.append(Finding('12.16', ERROR, p, ln,
                                       '%s is status: done but a check is recorded unmet: %s'
                                       % (e['id'], raw.strip()[:120])))
    return out


# ---------------------------------------------------------------- 12.19
def _journal_heads():
    """Every spelling of the journal heading the renderer knows, lowercased."""
    heads = set()
    for table in ((getattr(_render, 'HEAD', None) or {}).values()):
        j = (table or {}).get('journal')
        if j:
            heads.add(j.strip().lower())
    return heads or {u'журнал документа',
                     'document journal'}


def _journal(text, columns):
    """(1-indexed line of the journal heading or None, [(line, date, what)]).

    Rows come in two shapes and both are live: a table (`TASKS.md`,
    `CHANGELOG.md`, `DECISIONS.md`, `TEST-CASES.md`) and the list the renderer
    now writes (`README.md`, `INDEX.md`, `ARCHITECTURE.md`). The date column is
    located through the contract's `journal_columns` rather than assumed first —
    `TEST-CASES.md` puts `version` there, and a reader that assumes would call
    its journal empty.
    """
    heads = _journal_heads()
    lines = text.split('\n')
    start = None
    for i, l in enumerate(lines):
        am = mdblocks.ANCHOR.match(l)
        if am and am.group(1) == 'section' and am.group(2) == 'journal':
            start = i
        elif l.startswith('## ') and l[3:].strip().lower() in heads:
            start = i
    if start is None:
        return None, []
    cols = [str(x).strip().lower() for x in (columns or [])]
    di = cols.index('date') if 'date' in cols else 0
    wi = cols.index('what changed') if 'what changed' in cols else -1
    rows = []
    for j in range(start + 1, len(lines)):
        l = lines[j]
        am = mdblocks.ANCHOR.match(l)
        if (am and am.group(1) == 'section') or l.startswith('## '):
            break
        m = JOURNAL_ITEM.match(l)
        if m:
            rows.append((j + 1, m.group(1), m.group(2).strip()))
            continue
        if l.strip().startswith('|') and not re.match(r'^\s*\|[\s:|-]+\|\s*$', l):
            cells = [x.strip() for x in l.strip().strip('|').split('|')]
            date = cells[di] if di < len(cells) and DATE.match(cells[di]) else None
            if date is None:
                date = next((x for x in cells if DATE.match(x)), None)
            if date is None:
                continue                       # a header row, or a row with no date
            what = cells[wi] if -len(cells) <= wi < len(cells) else ''
            rows.append((j + 1, date, what))
    return start + 1, rows


# ---------------------------------------------------------------- журнал правок
def _ledger(c):
    """Записи journal-а, или пустой список, когда его ещё нет."""
    try:
        return _LEDGER.read(c.root)
    except Exception:                                             # noqa: BLE001
        return []


try:
    import ledger as _LEDGER
except ImportError:                                               # pragma: no cover
    _LEDGER = None


@rule('12.13', 'Every ledger row is well formed')
def r_12_13(c):
    """Was "the journal is typed", about history/log.md, which no longer exists.

    log.md recorded SESSIONS — a merge happened, a package went out — and never said
    which statement moved, so a review package could not tell a client what had changed
    since they last read it. The ledger records the item; this rule moved with it.
    """
    out = []
    if _LEDGER is None:
        return out
    decl = ((c.contract.get('documents') or {}).get('ledger') or {}).get('record') or {}
    req = decl.get('required') or ['date', 'doc', 'item', 'kind']
    kinds = set(decl.get('kinds') or [])
    known = set(req) | set(decl.get('optional') or [])
    path = 'history/ledger.jsonl'
    for n, r in enumerate(_ledger(c), 1):
        for k in req:
            if not r.get(k):
                out.append(Finding('12.13', ERROR, path, n,
                                   'row %d declares no %s — a row nothing can place is '
                                   'a row nothing can find' % (n, k)))
        if kinds and r.get('kind') not in kinds:
            out.append(Finding('12.13', ERROR, path, n,
                               'row %d has kind %r, not one of %s'
                               % (n, r.get('kind'), ', '.join(sorted(kinds)))))
        for k in sorted(set(r) - known):
            out.append(Finding('12.13', WARNING, path, n,
                               'row %d carries %r, which the contract does not declare'
                               % (n, k)))
        if r.get('kind') == 'changed' and 'now' not in r and 'why' not in r:
            out.append(Finding('12.13', ERROR, path, n,
                               'row %d says something changed and not what to' % n))
    return out


@rule('12.15', 'A release is paired')
def r_12_15(c):
    """Every `release` row has a CHANGELOG entry with the same id, and the reverse."""
    out = []
    ch = c.text.get('changelog') or ''
    rel = [r for r in _ledger(c) if r.get('kind') == 'release']
    ids = set(re.findall(r'^#{2,3}\s*(\S+)', ch, re.M))
    for r in rel:
        tag = str(r.get('item') or '')
        if tag and tag not in ch:
            out.append(Finding('12.15', ERROR, 'history/ledger.jsonl', 0,
                               'release %s is in the ledger and not in CHANGELOG.md' % tag))
    dates = re.findall(r'(\d{4}-\d{2}-\d{2})', ch)
    if dates and dates != sorted(dates, reverse=True):
        out.append(Finding('12.15', ERROR, 'history/CHANGELOG.md', 0,
                           'entries are not newest first'))
    return out


@rule('12.19', 'The ledger is not empty and not stale', WARNING)
def r_12_19(c):
    rows = _ledger(c)
    if not rows:
        return [Finding('12.19', WARNING, 'history/ledger.jsonl', 0,
                        'no rows — either nothing has been edited since the folder was '
                        'created, or edits are not being recorded')]
    return []


@rule('12.20', 'Every handoff is recorded')
def r_12_20(c):
    """A package on disk and a package in the ledger name each other.

    The ledger is what the next package reads to mark what changed since this one, so a
    handoff missing from it silently widens that window: statements the client has
    already seen come back unmarked.
    """
    out = []
    d = os.path.join(c.root, 'history', 'handoffs')
    on_disk = sorted(f for f in os.listdir(d)) if os.path.isdir(d) else []
    rows = [r for r in _ledger(c) if r.get('kind') == 'handoff']
    named = ' '.join(str(r.get('now', '')) + ' ' + str(r.get('source', '')) for r in rows)
    for f in on_disk:
        if f.startswith('.'):
            continue
        stem = f.rsplit('.', 1)[0]
        if stem not in named and f not in named:
            out.append(Finding('12.20', ERROR, 'history/handoffs/' + f, 0,
                               'sits in handoffs/ and no handoff row in the ledger names '
                               'it — the next package cannot tell what the client has '
                               'already seen'))
    for r in rows:
        m = re.search(r'`?(handoffs/[^`\s]+)`?', str(r.get('now') or ''))
        if m and not os.path.exists(os.path.join(c.root, 'history', m.group(1))):
            out.append(Finding('12.20', ERROR, 'history/ledger.jsonl', 0,
                               'a handoff row names %s, which does not exist' % m.group(1)))
    return out


@rule('12.26', 'A finished task left a trace')
def r_12_26(c):
    """Every task at done is named by a `work` row in the ledger.

    Without it the closing half of the loop is unenforced: a task can be marked done,
    the documents never re-checked, and every staleness rule stays quiet because
    nothing recorded that anything happened.

    Reads the entity's own span rather than a fixed window after its heading. The first
    version took 600 characters, and the LAST task in the file ran past the end of its
    section into «## Вехи», picked up a milestone's `Статус: done` and reported a
    backlog task as finished — a false positive produced by looking at the neighbours.
    """
    out = []
    doc = c.docs.get('tasks')
    if doc is None:
        return out
    work = ' '.join(str(r.get('now', '')) + ' ' + str(r.get('task', '')) + ' '
                    + str(r.get('item', '')) for r in _ledger(c) if r.get('kind') == 'work')
    for it in doc.items:
        if it.level < 3 or not it.id or not re.match(r'^M\d+-T\d+$', it.id):
            continue
        if str(it.get('status') or '').strip().lower() != 'done':
            continue
        if it.id not in work:
            out.append(Finding('12.26', ERROR, 'history/TASKS.md', (it.head_line or 0) + 1,
                               '%s is done and no work row in the ledger names it' % it.id))
    return out
