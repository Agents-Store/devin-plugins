#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass 3 — the `macstack/` folder. Rule group 12, as a program.

Until now this pass was prose in SKILL.md that an agent was expected to carry out
by eye. That is why rule 12.21 — "every entity carries exactly one fenced yaml
block" — never once fired against a folder that had no yaml blocks at all, and why
12.18 was structurally unsatisfiable for README.md across three releases without
anyone being able to tell whether it was passing or simply not running.

A rule nobody can run is not a rule. Each check below returns findings with a file,
a line and a verbatim excerpt, because "this table is too wide" is not actionable
and "cell 4 of row 12 is 876 characters" is.

Usage:
    lint_folder.py <macstack-dir> [--rule 12.3 ...] [--json] [--warnings]

Exit: 0 clean, 1 errors found, 2 could not run.
"""
import collections, glob, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.normpath(os.path.join(HERE, '..', '..', 'documents', 'references'))
# Свежесть считает `hooks/macstack_freshness.py` — тот же код, что у обоих хуков.
# Своя копия расчёта здесь уже была, и она разошлась с хуковой: линтер поднимал
# часы ещё и по `archive/reviews/`, а хук — нет, так что на проекте, отревьюенном
# до переезда вердиктов в журнал, линтер молчал, а хук звал сверяться. Путь
# кладётся здесь по той же причине и тем же способом, что и DOCS.
HOOKS = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'hooks'))
sys.path.insert(0, DOCS)
sys.path.insert(0, HOOKS)
import v3                                                       # noqa: E402

ERROR, WARNING, INFO = 'error', 'warning', 'info'

Finding = collections.namedtuple('Finding', 'rule severity path line message')

_RULES = []


def rule(rid, title, severity=ERROR):
    def wrap(fn):
        fn.rid, fn.title, fn.severity = rid, title, severity
        _RULES.append(fn)
        return fn
    return wrap


# ---------------------------------------------------------------- context
class Ctx(object):
    """Everything a rule may need, loaded once and shared."""

    def __init__(self, root):
        self.root = os.path.abspath(root)
        self.errors = []
        self.spec = self._json(os.path.join(self.root, 'macstack.json'))
        self.contract = self._json(os.path.join(DOCS, 'doc-contracts.json'))
        self.lang = (self.spec.get('docs') or {}).get('language') or 'ru'
        self.files = ((self.spec.get('docs') or {}).get('files') or {})
        # Какие ключи docs.files допускает СХЕМА. Правило 12.1 не имеет права
        # требовать записи для документа, которого схема туда не пустит:
        # inbox/README.md — манифест папки, а не документ проекта, и его там нет.
        sch = self._json(os.path.join(HERE, 'macstack.schema.json'))
        self.docs_files_keys = set(
            (((sch.get('properties') or {}).get('docs') or {})
             .get('properties', {}).get('files', {}).get('properties') or {}))
        self.docs = {}          # contract key -> v3.Doc
        self.text = {}          # contract key -> raw text
        for key, decl in (self.contract.get('documents') or {}).items():
            p = self.path_of(key)
            if not p or '<' in (decl.get('path') or '') or not os.path.exists(p):
                continue
            try:
                raw = io.open(p, encoding='utf-8').read()
            except IOError:
                continue
            self.text[key] = raw
            if decl.get('format') == 'v3':
                self.docs[key] = v3.read_doc(raw, path=p)

    def _json(self, p):
        try:
            return json.load(io.open(p, encoding='utf-8'))
        except Exception as e:
            self.errors.append('%s: %s' % (p, e))
            return {}

    def path_of(self, key):
        decl = (self.contract.get('documents') or {}).get(key) or {}
        rel = (self.files.get(key) or {}).get('path') or decl.get('path')
        return os.path.join(self.root, rel) if rel else None

    def rel(self, p):
        return os.path.relpath(p, self.root)

    def is_generated(self, key):
        return bool(((self.contract.get('documents') or {}).get(key) or {}).get('generated'))

    def authored_keys(self):
        """Документы, которые пишет человек. Форму сгенерированного гарантирует
        его генератор и правило 12.18 — требовать с него указателей значит
        требовать, чтобы генератор их придумывал."""
        return [k for k in self.docs if not self.is_generated(k)]

    def client_keys(self):
        """Everything the client actually reads — `client` AND `both`.

        OPEN-QUESTIONS.md is `both` on purpose: §A is owed by the client, §B is the
        team's deferred work. But it goes into the review package like the rest, and
        classifying it `both` quietly exempted it from every rule that protects the
        client's reading — no tables, no journal, the language ratio. It carried a
        journal for weeks and nothing said so.
        """
        return [k for k, d in (self.contract.get('documents') or {}).items()
                if d.get('audience') in ('client', 'both') and k in self.docs]

    def client_owned_keys(self):
        """Only what the client owns outright — for rules about authorship."""
        return [k for k, d in (self.contract.get('documents') or {}).items()
                if d.get('audience') == 'client' and k in self.docs]

    def entity_kind(self, item):
        """Which contract entity kind this heading is. None when it is not one."""
        if not item.ref:
            return 'case' if item.id and re.match(r'^[XSZ]-\d\d$', item.id) else None
        tail = item.ref.split('.')[-1] if '.' in item.ref else ''
        if tail.startswith('tasks'):
            return 'role_task'
        if tail.startswith('cases'):
            return 'case'
        return re.split(r'[\[\.]', item.ref)[0]

    def entities_of(self, key, kind):
        """(contract entity declaration, [items]) for one kind in one document."""
        decl = None
        for e in ((self.contract.get('documents') or {}).get(key) or {}).get('entities') or []:
            if e['kind'] == kind:
                decl = e
        doc = self.docs.get(key)
        if decl is None or doc is None:
            return None, []
        if decl.get('pointerless'):
            # Сущность, у которой указателя нет по существу: сессия решений — не
            # запись в macstack.json, и lifecycle.decisions указывает в обратную
            # сторону. Сопоставлять её по коллекции нечем, значит по id-шаблону.
            pat = decl.get('id_pattern')
            return decl, [i for i in doc.items
                          if i.level >= 3 and i.id
                          and (not pat or re.match(pat, i.id))]
        want = set(decl.get('collections') or [_CONTRACT_KIND.get(kind, kind)])
        return decl, [i for i in doc.items
                      if i.level >= 3 and self.entity_kind(i) in want]

    def prose_label(self, prose_key, lang=None):
        pr = (self.contract.get('prose') or {}).get(prose_key) or {}
        return (pr.get('label') or {}).get(lang or self.lang, prose_key)


# contract kind -> the collection its pointer starts with
_CONTRACT_KIND = {'screen': 'interfaces', 'trigger': 'triggers', 'role': 'roles',
                  'process': 'processes', 'goal': 'goals', 'result': 'results',
                  'integration': 'integrations', 'open_item': 'lifecycle'}

CODE = re.compile(r'`[^`]*`')
FENCE = re.compile(r'^\s*```')
TABLE = re.compile(r'^\s*\|')


# ---------------------------------------------------------------- rules
@rule('12.0', 'A declared entity kind is actually found in its document')
def r_12_0(c):
    """The guard against the failure this whole pass exists to catch.

    A rule that filters entities and matches none reports CLEAN, and clean is
    indistinguishable from correct. It happened here: schema rev 13 gave cases their
    own records, the pointers were repointed from `roles[].cases` to `cases[id=…]`,
    and the kind filter — still matching the old collection — silently returned zero.
    Thirty-five rules ran over an empty list and every one of them passed.

    So: if the contract declares an entity kind for a document and the document has
    headings, finding none of that kind is an ERROR, not silence.
    """
    out = []
    for key in sorted(c.docs):
        doc = c.docs[key]
        if not [i for i in doc.items if i.level >= 3]:
            continue
        for e in ((c.contract.get('documents') or {}).get(key) or {}).get('entities') or []:
            if e.get('status') == 'unrealised':
                continue
            _, items = c.entities_of(key, e['kind'])
            if not items:
                out.append(Finding('12.0', ERROR, c.rel(doc.path), 0,
                                   'the contract declares a %s here and not one was '
                                   'matched — the document has %d headings, so this is '
                                   'a broken filter, not an empty document'
                                   % (e['kind'], len([i for i in doc.items if i.level >= 3]))))
    return out


@rule('12.1', 'Layout — six entries in the root, and every fixed-path document exists')
def r_12_1(c):
    out = []
    if not os.path.isdir(c.root):
        return [Finding('12.1', ERROR, c.root, 0, 'docs.root does not resolve')]
    entries = sorted(e for e in os.listdir(c.root) if not e.startswith('.'))
    want = {'README.md', 'macstack.json', 'client', 'generated', 'inbox', 'history'}
    extra = [e for e in entries if e not in want]
    missing = sorted(want - set(entries))
    if extra:
        out.append(Finding('12.1', ERROR, c.rel(c.root), 0,
                           'a seventh entry in the root: %s' % ', '.join(extra)))
    if missing:
        out.append(Finding('12.1', ERROR, c.rel(c.root), 0,
                           'missing from the root: %s' % ', '.join(missing)))
    for key, decl in (c.contract.get('documents') or {}).items():
        p = decl.get('path') or ''
        if not p or '<' in p:
            continue
        if not os.path.exists(os.path.join(c.root, p)):
            out.append(Finding('12.1', ERROR, p, 0,
                               'the contract names this document; it does not exist'))
        elif key not in c.files and key in c.docs_files_keys:
            out.append(Finding('12.1', ERROR, 'macstack.json', 0,
                               'docs.files does not name %s — an authored map that '
                               'names nothing approves an empty folder' % key))
    return out


@rule('12.2', 'Headers and pointers — every entity heading carries one')
def r_12_2(c):
    """The rule that had no implementation anywhere, and it showed.

    Delete a screen's pointer and nothing in the pass said a word: 12.28 and 12.29
    only look at pointers that exist, and 12.21 only at fields. A heading with no
    pointer simply left the model — which also took it out of the uniqueness check,
    so removing one pointer could hide a duplicate id as a bonus.
    """
    out = []
    for key in sorted(c.authored_keys()):
        doc = c.docs[key]
        if not doc.header.get('doc'):
            out.append(Finding('12.2', ERROR, c.rel(doc.path), 1,
                               'no <!-- macstack:doc=… --> header'))
        # Заголовок БЕЗ указателя выпадает из фильтра сущностей раньше любой
        # проверки, поэтому искать его среди найденных сущностей бесполезно —
        # его там по определению нет. Признак: заголовок несёт идентификатор.
        reserved = set()
        pointerless = set()
        for e in ((c.contract.get('documents') or {}).get(key) or {}).get('entities') or []:
            if e.get('pointerless'):
                pointerless.add(e.get('id_pattern') or '.')
            for pref, r in ((e.get('pointer') or {}).get('by_id_prefix') or {}).items():
                if r.get('binding') == 'none':
                    reserved.add(pref)
        for it in doc.items:
            if it.level < 3 or not it.id or it.ref:
                continue
            if any(it.id.startswith(pref) for pref in reserved):
                continue
            if any(re.match(pat, it.id) for pat in pointerless):
                continue
            if '~~' in (doc.lines[it.head_line] if it.head_line is not None else ''):
                continue                      # зачёркнутый — закрыт, адреса больше нет
            out.append(Finding('12.2', ERROR, c.rel(doc.path), (it.head_line or 0) + 1,
                               '%s carries an id and no pointer — a heading outside the '
                               'model is checked by nothing below it' % it.id))
        # заголовок с id, который не попал ни в один объявленный вид
        claimed = set()
        for e in ((c.contract.get('documents') or {}).get(key) or {}).get('entities') or []:
            claimed.update(id(x) for x in c.entities_of(key, e['kind'])[1])
        for it in doc.items:
            if it.level >= 3 and it.id and id(it) not in claimed and it.ref:
                out.append(Finding('12.2', ERROR, c.rel(doc.path), (it.head_line or 0) + 1,
                                   '%s points at %s, which matches no entity kind the '
                                   'contract declares for this document'
                                   % (it.id, it.ref)))
    return out


@rule('12.28', 'Every pointer resolves into macstack.json')
def r_12_28(c):
    out = []
    for key in sorted(c.docs):
        for it in c.docs[key].items:
            if not it.ref:
                continue
            bad = _resolve(c.spec, it.ref)
            if bad:
                out.append(Finding('12.28', ERROR, c.rel(c.docs[key].path),
                                   (it.ref_line or 0) + 1,
                                   'pointer %s does not resolve: %s' % (it.ref, bad)))
    return out


def _resolve(spec, ref):
    """None when the path exists; otherwise the first segment that failed.

    `a[].b[]` is the UNION of b over every a — the contract declares that form for
    a section pointer, and a resolver that does not implement it reports a correct
    document as broken. Which is what it did: processes[].tasks[] in AUTOMATION.md.
    """
    node = spec
    for seg in ref.split('.'):
        if isinstance(node, list):
            m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\[\]$', seg)
            if not m:
                return 'segment %r follows a collection and is not a union' % seg
            name = m.group(1)
            hit = [x[name] for x in node
                   if isinstance(x, dict) and isinstance(x.get(name), list)]
            if not hit:
                return 'no %r on any member of the collection' % name
            node = [y for sub in hit for y in sub]
            continue
        m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)(\[(?:id=([^\]]+))?\])?$', seg)
        if not m:
            return 'segment %r is not a path' % seg
        name, brackets, ident = m.group(1), m.group(2), m.group(3)
        if not isinstance(node, dict) or name not in node:
            return 'no %r' % name
        node = node[name]
        if brackets and ident:
            if not isinstance(node, list):
                return '%r is not a collection' % name
            hit = [x for x in node if isinstance(x, dict) and x.get('id') == ident]
            if not hit:
                return 'no id=%s in %s' % (ident, name)
            node = hit[0]
        elif brackets:
            if not isinstance(node, list):
                return '%r is not a collection' % name
    return None


@rule('12.29', 'The pointer binds the heading the way its contract declares')
def r_12_29(c):
    out = []
    for key in sorted(c.docs):
        decls = ((c.contract.get('documents') or {}).get(key) or {}).get('entities') or []
        for e in decls:
            decl, items = c.entities_of(key, e['kind'])
            ptr = (e.get('pointer') or {})
            for it in items:
                b = _binding_for(ptr, it)
                last = re.findall(r'\[id=([^\]]+)\]', it.ref or '')
                where = (c.rel(c.docs[key].path), (it.head_line or 0) + 1)
                if b == 'none':
                    if it.ref:
                        out.append(Finding('12.29', ERROR, where[0], where[1],
                                           '%s is a reserved prefix and must carry no '
                                           'pointer; it carries %s' % (it.id, it.ref)))
                elif b == 'identity':
                    if not last or last[-1] != it.id:
                        out.append(Finding('12.29', ERROR, where[0], where[1],
                                           'identity binding: heading %s against pointer %s'
                                           % (it.id, it.ref)))
                elif b == 'member':
                    globs = _at(c.spec, it.ref) or []
                    if not any(_glob(g, it.id or '') for g in globs
                               if isinstance(g, str)):
                        out.append(Finding('12.29', ERROR, where[0], where[1],
                                           'member binding: %s satisfies none of %s at %s'
                                           % (it.id, globs, it.ref)))
    return out


def _binding_for(ptr, item):
    if not ptr:
        return None
    by = ptr.get('by_id_prefix')
    if by:
        for pref, rule_ in by.items():
            if pref != '*' and (item.id or '').startswith(pref):
                return rule_.get('binding')
        return (by.get('*') or {}).get('binding')
    return ptr.get('binding')


def _at(spec, ref):
    node = spec
    for seg in ref.split('.'):
        m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)(\[(?:id=([^\]]+))?\])?$', seg)
        if not m:
            return None
        name, ident = m.group(1), m.group(3)
        if not isinstance(node, dict) or name not in node:
            return None
        node = node[name]
        if ident:
            hit = [x for x in node if isinstance(x, dict) and x.get('id') == ident]
            if not hit:
                return None
            node = hit[0]
    return node


def _glob(pat, s):
    return re.match('^' + re.escape(pat).replace(r'\*', '.*') + '$', s) is not None


@rule('12.30', 'A client document is headings and bullets, and nothing else')
def r_12_30(c):
    out = []
    for key in [k for k in c.client_keys() if not c.is_generated(k)]:
        p = c.rel(c.docs[key].path)
        for n, line in enumerate(c.docs[key].lines, 1):
            if FENCE.match(line):
                out.append(Finding('12.30', ERROR, p, n, 'a fenced block: %s' % line.strip()[:60]))
            elif TABLE.match(line):
                out.append(Finding('12.30', ERROR, p, n, 'a table row: %s' % line.strip()[:60]))
            elif re.match(r'^#{5,}\s', line):
                out.append(Finding('12.30', ERROR, p, n, 'a heading deeper than ####'))
            elif line.lstrip().startswith('<!--') and not re.match(
                    r'^\s*<!--\s*macstack:(doc|ref)=', line):
                out.append(Finding('12.30', ERROR, p, n,
                                   'HTML that is not a macstack pointer: %s' % line.strip()[:60]))
    return out


@rule('12.31', 'Every bullet label is declared in the contract')
def r_12_31(c):
    out = []
    known = set()
    for f in (c.contract.get('fields') or {}).values():
        for lang, lab in (f.get('label') or {}).items():
            known.add((lang, lab.lower()))
        for per in (f.get('label_by_kind') or {}).values():
            for lang, lab in per.items():
                known.add((lang, lab.lower()))
        for lang, aliases in (f.get('label_aliases') or {}).items():
            for lab in aliases:
                known.add((lang, lab.lower()))
    for key in sorted(c.docs):
        doc = c.docs[key]
        lang = doc.header.get('lang') or c.lang
        for n, lab in doc.undeclared:
            if (lang, lab.lower()) not in known:
                out.append(Finding('12.31', ERROR, c.rel(doc.path), n,
                                   'undeclared bullet label %r — declare it in '
                                   'doc-contracts.json `fields`, or make the line prose'
                                   % lab))
    return out


@rule('12.33', 'A client document carries no journal')
def r_12_33(c):
    out = []
    heads = [u'история изменений', u'document journal', u'журнал документа',
             u'änderungsverlauf', u'change log', u'changelog']
    for key in [k for k in c.client_keys() if not c.is_generated(k)]:
        doc = c.docs[key]
        for it in doc.items:
            if it.level == 2 and (it.title or '').strip().lower() in heads:
                out.append(Finding('12.33', ERROR, c.rel(doc.path), (it.head_line or 0) + 1,
                                   'a journal section in a client document — history '
                                   'lives in history/, and the client sees it per item '
                                   'in the review package'))
        for n, line in enumerate(doc.lines, 1):
            if re.match(r'^-\s+\*\*(Версия|Version)\s', line):
                out.append(Finding('12.33', ERROR, c.rel(doc.path), n,
                                   'a version row inside a client document'))
    return out


@rule('12.21', 'Entities parse — required bullets and prose blocks are present')
def r_12_21(c):
    out = []
    for key in sorted(c.docs):
        decls = ((c.contract.get('documents') or {}).get(key) or {}).get('entities') or []
        lang = c.docs[key].header.get('lang') or c.lang
        for e in decls:
            decl, items = c.entities_of(key, e['kind'])
            if decl is None:
                continue
            req = list(e.get('bullets_required') or [])
            forb = set(e.get('bullets_forbidden') or [])
            cond = e.get('bullets_conditional') or {}
            allowed = set(req) | set(e.get('bullets_optional') or []) | set(cond)
            preq = list(e.get('prose_required') or [])
            pexc = e.get('prose_required_except_prefix') or {}
            pat = e.get('id_pattern')
            for it in items:
                p, ln = c.rel(c.docs[key].path), (it.head_line or 0) + 1
                if pat and it.id and not re.match(pat, it.id):
                    out.append(Finding('12.21', ERROR, p, ln,
                                       '%s does not match %s for a %s' % (it.id, pat, e['kind'])))
                for k in req:
                    if k not in it.fields:
                        out.append(Finding('12.21', ERROR, p, ln,
                                           '%s: a %s must declare %s' % (it.id, e['kind'], k)))
                for k, r in cond.items():
                    if k in it.fields:
                        continue
                    uv = r.get('unless_value')
                    if uv:
                        # «нужен, ЕСЛИ значение другого поля не такое-то»: задача в
                        # бэклоге ещё не заведена в трекере, и требовать с неё номер
                        # значит требовать выдумать его.
                        if str(it.fields.get(uv.get('field'))) in [str(x) for x in uv.get('in') or []]:
                            continue
                        out.append(Finding('12.21', ERROR, p, ln,
                                           '%s: %s is required unless %s is one of %s'
                                           % (it.id, k, uv.get('field'), ', '.join(uv.get('in') or []))))
                        continue
                    if not it.fields.get(r.get('unless')):
                        out.append(Finding('12.21', ERROR, p, ln,
                                           '%s: %s is required unless %s' % (it.id, k, r.get('unless'))))
                for k in sorted(set(it.fields) - allowed):
                    why = ('it is already the pointer' if k in forb
                           else 'the contract does not declare it for a %s' % e['kind'])
                    out.append(Finding('12.21', ERROR, p, ln,
                                       '%s: bullet %s — %s' % (it.id, k, why)))
                heads = {h.rstrip('.:').strip() for h in it.sections}
                for k in preq:
                    # Сравнение по букве ВИДА, а не по началу строки. В
                    # двухбуквенной форме id первая буква всегда `C` («case»), и
                    # `startswith('Z')` перестал бы узнавать запрет `CZ-01` —
                    # после чего правило требовало бы с запрета список приёмки,
                    # которого у запрета нет по устройству. Опущенный `C`
                    # обрабатывается тем же выражением.
                    head = (it.id or '').split('-', 1)[0]
                    kind_letter = head[-1:] if head else ''
                    if any(kind_letter == x or (it.id or '').startswith(x)
                           for x in pexc.get(k, [])):
                        continue
                    if c.prose_label(k, lang) not in heads:
                        out.append(Finding('12.21', ERROR, p, ln,
                                           '%s: a %s must carry the block "%s"'
                                           % (it.id, e['kind'], c.prose_label(k, lang))))
    return out


@rule('12.24', 'Tables stay inside the budget', WARNING)
def r_12_24(c):
    out = []
    budget = (c.contract.get('format') or {}).get('table_budget') or {}
    maxcol = budget.get('max_columns', 4)
    maxcell = budget.get('max_cell_chars', 80)
    minrow = budget.get('min_rows', 3)
    for p in sorted(glob.glob(os.path.join(c.root, '*/*.md')) +
                    glob.glob(os.path.join(c.root, '*.md'))):
        if os.sep + 'client' + os.sep in p:
            continue                                   # 12.30 owns client/
        rows, start = [], 0
        for n, line in enumerate(io.open(p, encoding='utf-8').read().split('\n'), 1):
            if TABLE.match(line):
                if not rows:
                    start = n
                rows.append((n, line))
                continue
            if rows:
                out.extend(_budget(c, p, start, rows, maxcol, maxcell, minrow))
                rows = []
        if rows:
            out.extend(_budget(c, p, start, rows, maxcol, maxcell, minrow))
    return out


def _budget(c, p, start, rows, maxcol, maxcell, minrow):
    body = [(n, l) for n, l in rows if not re.match(r'^\s*\|[\s:|-]+\|\s*$', l)]
    if not body:
        return []
    out = []
    cols = max(len([x for x in l.strip().strip('|').split('|')]) for _, l in body)
    if cols > maxcol:
        out.append(Finding('12.24', WARNING, c.rel(p), start,
                           'a table of %d columns, budget is %d' % (cols, maxcol)))
    if len(body) < minrow:
        out.append(Finding('12.24', WARNING, c.rel(p), start,
                           'a table of %d rows — under %d it is a list' % (len(body), minrow)))
    for n, l in body:
        for i, cell in enumerate(l.strip().strip('|').split('|'), 1):
            cell = cell.strip()
            if len(cell) > maxcell:
                out.append(Finding('12.24', WARNING, c.rel(p), n,
                                   'cell %d is %d characters: %s…'
                                   % (i, len(cell), cell[:60])))
            if '<br>' in cell:
                out.append(Finding('12.24', WARNING, c.rel(p), n,
                                   'cell %d carries <br> — that is a list wearing a grid' % i))
    return out


# ---------------------------------------------------------------- rule modules
def _load_rule_modules():
    """Rules live in rules_*.py beside this file and register themselves on import.

    One module per group rather than one file for everything: the groups are
    independent, and a file several people edit at once is a file that only ever
    gets edited by one.
    """
    import importlib
    # Под `python3 lint_folder.py` этот файл зовётся __main__, и `from lint_folder
    # import rule` в модуле правил импортировал бы его ВТОРОЙ раз — со своим,
    # пустым реестром. Регистрация под собственным именем закрывает это раз и
    # навсегда; без неё правила молча не подключаются, а счётчик показывает своё
    # прежнее число, то есть ровно тот молчаливый ноль, ради которого всё и затеяно.
    sys.modules.setdefault('lint_folder', sys.modules[__name__])
    for f in sorted(glob.glob(os.path.join(HERE, 'rules_*.py'))):
        name = os.path.splitext(os.path.basename(f))[0]
        try:
            importlib.import_module(name)
        except Exception as e:                                    # noqa: BLE001
            sys.stderr.write('rule module %s did not load: %s: %s\n'
                             % (name, type(e).__name__, e))


sys.path.insert(0, HERE)
_load_rule_modules()


# ---------------------------------------------------------------- driver
def run(root, only=None, warnings=False):
    c = Ctx(root)
    if c.errors:
        for e in c.errors:
            sys.stderr.write('could not load %s\n' % e)
        return None, 2
    found = []
    for fn in _RULES:
        if only and fn.rid not in only:
            continue
        try:
            found.extend(fn(c) or [])
        except Exception as e:                                    # noqa: BLE001
            found.append(Finding(fn.rid, ERROR, '<lint>', 0,
                                 'the rule itself failed: %s: %s' % (type(e).__name__, e)))
    if not warnings:
        found = [f for f in found if f.severity == ERROR]
    return found, (1 if any(f.severity == ERROR for f in found) else 0)


def main():
    argv = sys.argv[1:]
    only = [a for i, a in enumerate(argv) if i and argv[i - 1] == '--rule']
    as_json = '--json' in argv
    warn = '--warnings' in argv
    pos = [a for a in argv if not a.startswith('--') and a not in only]
    root = pos[0] if pos else 'macstack'
    found, code = run(root, only or None, warn)
    if found is None:
        return 2
    if as_json:
        print(json.dumps([f._asdict() for f in found], ensure_ascii=False, indent=1))
        return code
    if not found:
        print('чисто: %d правил, ноль находок' % len(_RULES))
        return code
    by = collections.Counter(f.rule for f in found)
    for f in sorted(found, key=lambda x: (x.severity != ERROR, x.rule, x.path, x.line)):
        print('%-8s %-7s %s:%s  %s' % (f.rule, f.severity, f.path, f.line or '-', f.message))
    print('\nнаходок: %d по %d правилам (%s)'
          % (len(found), len(by), ', '.join('%s×%d' % (k, v) for k, v in sorted(by.items()))))
    return code


if __name__ == '__main__':
    sys.exit(main())
