#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reconcile the BUSINESS half of macstack.json against the client's authored v3 documents.

client/AUTOMATION.md and client/UX-UI.md are written by a human and corrected by the
client; this reads their entities (roles, role tasks, triggers, screens) and reports
exactly where the spec disagrees. v1 read two tables by column POSITION and applied
value changes by regex substitution over the raw JSON text; v2 moved the machine
fields into a per-entity YAML block. Both are gone here — v3 keeps only a heading and
one `macstack:ref=<path-into-macstack.json>` pointer above it (`v3.py`), and the spec
is edited as TEXT (`jsonedit.py`), never reparsed and reserialized, so formatting and
key order survive the round trip: `json.dump(indent=2)` on this project's live spec
turned 959 lines into 4119.

WILL change — values of entities matched unambiguously BY ID: a role_task's gate, a
trigger's schedule, a screen's path/roles, and any entity's name (its heading title).
Will NOT change anything else this script also compares (a role's cases/isolation, a
role_task's workflow, a trigger's type or its non-schedule config keys) — those are
REPORTED as `changed` but never applied. A wider "changed" report than "applied" is
deliberate: it says what differs, not just what is safe to write back automatically.

Will NOT create or delete anything, ever. A new entity needs an id, and an id is a
decision: workflows, tests and prose reference it, so a machine that invents one is a
machine that silently orphans a reference on the next rename. New and missing entities
are reported as `add` / `gone` for a human to resolve.

v1 -> v2 -> v3: the document entity has carried an id in its heading since v2, so
unlike v1 (where a task was matched by normalizing its NAME text, because no id
existed anywhere) an entity is matched by id alone. That makes a TITLE rename
detectable and applicable — it shows up as a `changed` `name`. Changing the ID itself
still looks like one `add` plus one `gone`, and this script reports that rather than
guessing a rename.

Screens are the one place id-matching does not hold. UX-UI.md writes one heading per
SCREEN (37 on the corpus this was measured against) but macstack.json keeps one record
per interface AREA (9) — the pointer above a screen heading names the area, not the
screen. `compare_screens` matches on the pointer's target, and only the screen whose
own id equals that target (the area's entry screen, a convention every area in the
corpus follows) stands for the area's name/path/roles; the other screens count only
toward whether the area is described at all.

Usage: sync-spec.py <macstack-dir> [--apply]
"""
import sys, os, io, re, json, collections

sys.path.insert(0, os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', 'documents', 'references')))
import v3                                              # noqa: E402
import jsonedit as J  # noqa: E402
from i18n import doc_lang, msg  # noqa: E402

CONFIG_KEYS = ('schedule', 'entity', 'event', 'condition', 'path')

ROLE_FIELDS = ('name', 'sees', 'can', 'cases', 'isolation')
SCREEN_FIELDS = ('name', 'path', 'roles')

# The rule, rather than a list somebody has to keep in step with the contract:
# APPLY any value the client document OWNS; refuse anything that would create an id or
# point at one that does not exist. The document owns the business half — roles, their
# tasks and gates, triggers and what they raise, screens and their addresses. It does
# not own what the contract's feeds.not names, and that list is short and stable.
ROLE_APPLIABLE = {'name', 'sees', 'can', 'cases', 'isolation'}
TASK_APPLIABLE = {'name', 'gate', 'role', 'workflow'}
TRIGGER_APPLIABLE = {'name', 'type', 'source', 'schedule', 'entity', 'event', 'condition', 'path'}
SCREEN_APPLIABLE = {'name', 'path', 'roles'}
# Кейс: документ владеет тем, ЧТО человек должен получить и насколько это важно.
# `acceptance` сюда не входит намеренно — список пунктов приёмки выделяется
# рендером и живёт в generated/, а не переписывается из прозы.
CASE_APPLIABLE = {'name', 'priority', 'role', 'screens', 'triggers', 'workflow'}

# Never written from a client document, whatever it says. These are the architect's,
# measured against the code; generating them from a client's words would be a promise
# the format cannot keep, and the failure would be silent.
NEVER = {'location', 'engine', 'software', 'entities', 'status', 'instances'}

# An interface a person does not open cannot appear in UX-UI.md, so its absence there is
# not a disagreement. v1 carried this whitelist and v2 lost it, which made every API and
# channel interface report as `gone` forever.
SCREENISH = ('web', 'admin_ui', 'dashboard', 'approval_center', 'form')


def is_screen(iface):
    if (iface.get('type') or '') not in SCREENISH:
        return False
    if (iface.get('mode') or 'ui') not in ('ui', ''):
        return False
    return (iface.get('audience') or 'human') in ('human', 'both', '')


# v3 fields the schema declares an ARRAY: v3._value() returns a bare string when the
# document names exactly one id and a list only for several (comma is a list
# separator, not a marker of arrayness), so a screen naming one role would otherwise
# hand jsonedit a string where interfaces[].roles wants ["coach"]. Coercing at the
# read boundary means every caller downstream — comparison and apply alike — already
# sees the shape the schema expects.
ARRAY_FIELDS = frozenset((
    'roles', 'screens', 'triggers', 'entities', 'cases', 'languages', 'views'))


def field(item, key):
    v = item.get(key)
    if key in ARRAY_FIELDS and v is not None and not isinstance(v, (list, tuple)):
        return [v]
    return v


def title_of(item):
    return item.title or ''


# ------------------------------------------------------------------- documents
def doc_role(it):
    return {
        'id': it.id,
        'name': title_of(it),
        'cases': field(it, 'cases'),
        'isolation': field(it, 'isolation'),
        'sees': field(it, 'sees'),
        'can': field(it, 'can'),
    }


def doc_task(it):
    return {
        'id': it.id,
        'name': title_of(it),
        'role': field(it, 'role'),
        'gate': field(it, 'gate'),
        'workflow': field(it, 'workflow'),
    }


def doc_trigger(it):
    config = dict((k, field(it, k)) for k in CONFIG_KEYS if field(it, k) is not None)
    return {
        'id': it.id,
        'name': title_of(it),
        'type': field(it, 'type'),
        'config': config,
    }


REF_ID = re.compile(r'\[id=([^\]]+)\]')


def doc_case(it):
    """Кейс из USER-CASES.md.

    Роль читается из УКАЗАТЕЛЯ, а не из пункта: на живом корпусе у кейса нет
    пункта «Кто» — принадлежность роли несёт `roles[id=coach].cases`, и до схемы
    rev 13 это был единственный её адрес. Сквозные `X-`, сценарии `S-` и запреты
    `Z-` не принадлежат роли по существу и указателя не несут вовсе.
    """
    m = re.search(r'roles\[id=([^\]]+)\]', it.ref or '')
    return {
        'id': it.id,
        'name': title_of(it),
        'role': m.group(1) if m else field(it, 'role'),
        'priority': field(it, 'priority'),
        'screens': field(it, 'screens'),
        'triggers': field(it, 'triggers'),
        'workflow': field(it, 'workflow'),
    }


def screen_target(it):
    """The interface AREA the pointer names — `interfaces[id=coach-portal]` ->
    'coach-portal'. NOT it.id: UX-UI.md writes one heading per screen, macstack.json
    keeps one record per area, and matching on the screen's own heading id would
    report every non-entry screen `add` forever, since no screen slug is ever an
    interfaces[].id.

    A pointer that names the collection and no member — `interfaces[]` over a heading
    that does carry a slug — leaves that slug as the only address the document
    offers, so it stands in. Returning None instead reached the report as
    `add screen None`: an id no human can look up and `path_of` can never resolve."""
    m = REF_ID.search(it.ref or '')
    return m.group(1) if m else it.id


def doc_screen(it):
    return {
        'id': it.id,
        'target': screen_target(it),
        'name': title_of(it),
        'path': field(it, 'path'),
        'roles': field(it, 'roles'),
    }


# --------------------------------------------------------------------- diffing
# Not "non-ASCII" — that would refuse Träger, Auswertung and every other proper noun a
# German or French project legitimately carries in an English sentence. The rule is
# SCRIPT: macstack.json is written in the Latin script.
NON_LATIN = re.compile(
    u'[\u0370-\u03FF\u0400-\u052F\u0590-\u05FF\u0600-\u06FF\u0900-\u097F'
    u'\u0E00-\u0E7F\u1100-\u11FF\u2E80-\u9FFF\uAC00-\uD7AF\uF900-\uFAFF]')


def is_english(v):
    """macstack.json is ALWAYS English — the standard says so and every downstream
    consumer assumes it.

    The client documents are not: docs.language is exactly the field that says so. So a
    value can only cross from a Russian, German or Ukrainian document into the spec if it
    carries no non-ASCII letter. That admits everything structural — a path, a cron
    expression, a gate, a role id, an enum member — and refuses everything that is prose
    in the document's own language.

    Caught by running --apply on the live project: applying screen names from the
    migrated Russian document rewrote thirteen English `interfaces[].name` values into
    Cyrillic. Nothing failed; the spec simply stopped being what the standard promises.

    The test is the SCRIPT, not the byte range. A first cut refused every non-ASCII
    character and would have blocked `Träger` and `Auswertung` — words that were already
    in the spec, in English sentences, because they are the client's own proper nouns."""
    if isinstance(v, (list, tuple)):
        return all(is_english(x) for x in v)
    if isinstance(v, dict):
        return all(is_english(x) for x in v.values())
    return not NON_LATIN.search(str(v or ''))


def is_blank(v):
    """A value a converter or a seed left unfilled."""
    if v is None:
        return True
    if isinstance(v, (list, tuple, dict)):
        return len(v) == 0
    s = str(v).strip()
    return s in ('', '—', '-', '~') or s.startswith('_TODO')


def would_erase(doc_value, spec_value):
    """A blank in the document over a populated spec value is not a correction.

    Seen live: the migrator could not turn the prose cell "все без входа" into role ids,
    so the screen came out with `roles: []`. Applying that would have deleted a correct
    list from the spec on the authority of a cell nobody had rewritten yet. A blank is a
    gap in the document, and a gap is reported, never propagated."""
    return is_blank(doc_value) and not is_blank(spec_value)


def id_exists(spec, coll, ident):
    if not ident:
        return True
    if coll == 'workflows':
        return any(w.get('id') == ident for w in (spec.get('workflows') or []))
    if coll == 'roles':
        return any(r.get('id') == ident for r in (spec.get('roles') or []))
    return True


def mk_change(kind, id_, field, have, want, appliable, apply_fn):
    if would_erase(want, have) or not is_english(want):
        appliable, apply_fn = False, None
    return {'kind': kind, 'id': id_, 'field': field, 'have': have, 'want': want,
            'appliable': appliable, 'apply': apply_fn}


CONFIG_FIELDS = ('schedule', 'entity', 'event', 'condition', 'path')


def path_of(spec, rec):
    """The JSON path of a change, so it can be written as TEXT rather than by
    reserializing the file.

    json.dump(indent=2) on a live spec turned 959 lines into 4119 — the file is
    hand-formatted, short objects inlined, and a whole-file reformat makes a one-value
    change unreviewable. The parse decides WHAT to change; the path says WHERE."""
    kind, ident, field = rec['kind'], rec['id'], rec['field']
    if kind == 'role':
        for i, r in enumerate(spec.get('roles') or []):
            if r.get('id') == ident:
                return ['roles', i, field]
    elif kind == 'role_task':
        for pi, pr in enumerate(spec.get('processes') or []):
            for ti, tk in enumerate(pr.get('tasks') or []):
                if tk.get('id') == ident:
                    base = ['processes', pi, 'tasks', ti]
                    if field in ('gate', 'role'):
                        return base + ['human', field]
                    return base + [field]
    elif kind == 'trigger':
        for i, x in enumerate(spec.get('triggers') or []):
            if x.get('id') == ident:
                if field in CONFIG_FIELDS:
                    return ['triggers', i, 'config', field]
                return ['triggers', i, field]
    elif kind == 'screen':
        for i, x in enumerate(spec.get('interfaces') or []):
            if x.get('id') == ident:
                return ['interfaces', i, field]
    return None


SPEC = {}


def compare_roles(doc_roles, spec_roles):
    add, gone, changed = [], [], []
    spec_by_id = dict((r.get('id'), r) for r in spec_roles)
    doc_by_id = dict((r['id'], r) for r in doc_roles)
    for rid, d in doc_by_id.items():
        if rid not in spec_by_id:
            add.append(('role', rid, d['name']))
            continue
        s = spec_by_id[rid]
        for f in ROLE_FIELDS:
            dv, sv = d.get(f), s.get(f)
            if dv is not None and dv != sv:
                appliable = f in ROLE_APPLIABLE
                fn = (lambda s=s, f=f, dv=dv: s.__setitem__(f, dv)) if appliable else None
                changed.append(mk_change('role', rid, f, sv, dv, appliable, fn))
    for rid, s in spec_by_id.items():
        if rid not in doc_by_id:
            gone.append(('role', rid, s.get('name')))
    return add, gone, changed


def all_spec_tasks(spec):
    """Only tasks with a human touchpoint. AUTOMATION.md's task section is titled
    "Что делают люди" — what PEOPLE do — and structurally never mentions a
    workflow-only task, so comparing one against the document reported it `gone`
    unconditionally. Measured on the live corpus: 17 of 50 spec tasks carry no
    `human` at all, and dropping them is exactly what brings `gone` to zero against a
    document that in fact describes every role task it has.

    The test is `human`, not `human.role`. A task whose human block exists but has
    lost its role is the ONE case where the document's `Кто делает` bullet is the
    repair — and requiring the role here hid that task from the comparison entirely,
    so it surfaced as `add` for an id macstack.json already holds: a false report,
    and an unappliable one, since `add` is never written back."""
    for p in (spec.get('processes') or []):
        for t in (p.get('tasks') or []):
            if t.get('id') and t.get('human'):
                yield t


def compare_tasks(doc_tasks, spec):
    add, gone, changed = [], [], []
    spec_by_id = dict((t['id'], t) for t in all_spec_tasks(spec))
    doc_by_id = dict((t['id'], t) for t in doc_tasks)
    for tid, d in doc_by_id.items():
        if tid not in spec_by_id:
            add.append(('role_task', tid, d['name']))
            continue
        t = spec_by_id[tid]
        human = t.get('human') or {}
        if d.get('name') is not None and d['name'] != t.get('name'):
            changed.append(mk_change('role_task', tid, 'name', t.get('name'), d['name'], True,
                                      lambda t=t, dv=d['name']: t.__setitem__('name', dv)))
        if d.get('gate') is not None and d['gate'] != human.get('gate'):
            def apply_gate(t=t, dv=d['gate']):
                h = t.get('human')
                if h is None:
                    h = type(t)()
                    t['human'] = h
                h['gate'] = dv
            changed.append(mk_change('role_task', tid, 'gate', human.get('gate'), d['gate'], True, apply_gate))
        if d.get('role') is not None and d['role'] != human.get('role'):
            def apply_role(t=t, dv=d['role']):
                h = t.get('human')
                if h is None:
                    h = type(t)()
                    t['human'] = h
                h['role'] = dv
            changed.append(mk_change('role_task', tid, 'role', human.get('role'), d['role'],
                                     'role' in TASK_APPLIABLE, apply_role))
        if d.get('workflow') is not None and d['workflow'] != t.get('workflow'):
            # a workflow id the spec does not declare is a dangling reference, not a value
            ok = 'workflow' in TASK_APPLIABLE and id_exists(SPEC, 'workflows', d['workflow'])
            changed.append(mk_change('role_task', tid, 'workflow', t.get('workflow'), d['workflow'],
                                     ok, (lambda t=t, dv=d['workflow']: t.__setitem__('workflow', dv)) if ok else None))
    for tid, t in spec_by_id.items():
        if tid not in doc_by_id:
            gone.append(('role_task', tid, t.get('name')))
    return add, gone, changed


def compare_triggers(doc_triggers, spec_triggers):
    add, gone, changed = [], [], []
    spec_by_id = dict((t.get('id'), t) for t in spec_triggers)
    doc_by_id = dict((t['id'], t) for t in doc_triggers)
    for tid, d in doc_by_id.items():
        if tid not in spec_by_id:
            add.append(('trigger', tid, d['name']))
            continue
        s = spec_by_id[tid]
        if d.get('name') is not None and d['name'] != s.get('name'):
            changed.append(mk_change('trigger', tid, 'name', s.get('name'), d['name'], True,
                                      lambda s=s, dv=d['name']: s.__setitem__('name', dv)))
        if d.get('type') is not None and d['type'] != s.get('type'):
            changed.append(mk_change('trigger', tid, 'type', s.get('type'), d['type'],
                                     'type' in TRIGGER_APPLIABLE,
                                     lambda s=s, dv=d['type']: s.__setitem__('type', dv)))
        s_config = s.get('config') or {}
        for k in CONFIG_KEYS:
            dv = d['config'].get(k)
            sv = s_config.get(k)
            if dv is not None and dv != sv:
                appliable = k in TRIGGER_APPLIABLE

                def apply_cfg(s=s, k=k, dv=dv):
                    cfg = s.get('config')
                    if cfg is None:
                        cfg = type(s)()
                        s['config'] = cfg
                    cfg[k] = dv
                changed.append(mk_change('trigger', tid, k, sv, dv, appliable, apply_cfg if appliable else None))
    for tid, s in spec_by_id.items():
        if tid not in doc_by_id:
            gone.append(('trigger', tid, s.get('name')))
    return add, gone, changed


def compare_cases(doc_cases, spec_cases):
    """Запреты `Z-` живут в prohibitions[], а не в cases[] — сверять их здесь
    значило бы объявлять пятнадцать штук `add` при каждом прогоне."""
    add, gone, changed = [], [], []
    spec_by_id = dict((c.get('id'), c) for c in spec_cases)
    doc_by_id = dict((c['id'], c) for c in doc_cases if not (c['id'] or '').startswith('Z-'))
    for cid, d in doc_by_id.items():
        if cid not in spec_by_id:
            add.append(('case', cid, d['name']))
            continue
        s = spec_by_id[cid]
        for key in ('name', 'priority', 'role', 'screens', 'triggers', 'workflow'):
            dv, sv = d.get(key), s.get(key)
            if dv is None or dv == sv:
                continue
            changed.append(mk_change(
                'case', cid, key, sv, dv, key in CASE_APPLIABLE,
                (lambda s=s, k=key, v=dv: s.__setitem__(k, v))
                if key in CASE_APPLIABLE else None))
    for cid, s in spec_by_id.items():
        if cid not in doc_by_id:
            gone.append(('case', cid, s.get('name')))
    return add, gone, changed


def compare_screens(doc_screens, spec_interfaces):
    """Existence is checked at the AREA the pointer names, never at the screen's own
    heading id — see `screen_target`. Field values (name/path/roles) come only from
    the group's ENTRY screen, the one whose id equals the area id: a sub-screen's own
    path is its own address, not the area's, and comparing it would report `changed`
    forever, since it structurally never equals the one value the area actually has.

    SCREENISH narrows `gone` and only `gone` — that is what its comment claims and
    the one direction it reasons about. Narrowing the existence index with it as well
    made a documented API or channel interface report `add` for an id macstack.json
    already holds, and told a human to create a second one."""
    add, gone, changed = [], [], []
    spec_by_id = dict((i.get('id'), i) for i in spec_interfaces)

    by_target = collections.OrderedDict()
    for d in doc_screens:
        by_target.setdefault(d['target'], []).append(d)

    for target, group in by_target.items():
        if target not in spec_by_id:
            home = next((g for g in group if g['id'] == target), group[0])
            add.append(('screen', target, home['name']))
            continue
        s = spec_by_id[target]
        home = next((g for g in group if g['id'] == target), None)
        if home is None:
            continue
        for f in SCREEN_FIELDS:
            dv, sv = home.get(f), s.get(f)
            if dv is not None and dv != sv:
                appliable = f in SCREEN_APPLIABLE
                fn = (lambda s=s, f=f, dv=dv: s.__setitem__(f, dv)) if appliable else None
                changed.append(mk_change('screen', target, f, sv, dv, appliable, fn))
    for s in spec_interfaces:
        if is_screen(s) and s.get('id') not in by_target:
            gone.append(('screen', s.get('id'), s.get('name')))
    return add, gone, changed


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    root = args[0] if args else 'macstack'
    apply_ = '--apply' in sys.argv
    lang = doc_lang(root)

    spec_p = os.path.join(root, 'macstack.json')
    if not os.path.exists(spec_p):
        print(msg(lang, 'no_spec', dir=root))
        return 1
    with io.open(spec_p, encoding='utf-8') as f:
        spec = json.load(f, object_pairs_hook=collections.OrderedDict)
    global SPEC
    SPEC = spec

    auto_p = os.path.join(root, 'client', 'AUTOMATION.md')
    if not os.path.exists(auto_p):
        print('missing: %s' % auto_p)
        return 1
    auto_items = v3.load(auto_p)
    doc_roles = [doc_role(it) for it in v3.entities(auto_items, 'roles')]
    # 'processes' matches BOTH the process heading and its tasks. The assumption
    # that a process heading carries no id was true when this was written and is not
    # any more: seeded and live documents both give the process its own id and
    # pointer. Without the `.tasks[` filter the eight processes of a live project
    # were reported as eight new role_tasks on every run — a wrong list, printed
    # confidently, that somebody would eventually act on.
    doc_tasks = [doc_task(it) for it in v3.entities(auto_items, 'processes')
                 if '.tasks[' in (it.ref or '')]
    doc_triggers = [doc_trigger(it) for it in v3.entities(auto_items, 'triggers')]

    doc_cases = []
    uc_p = os.path.join(root, 'client', 'USER-CASES.md')
    if os.path.exists(uc_p):
        doc_cases = [doc_case(it) for it in v3.entities(v3.load(uc_p), 'cases')]

    doc_screens = []
    ux_p = os.path.join(root, 'client', 'UX-UI.md')
    if os.path.exists(ux_p):
        doc_screens = [doc_screen(it) for it in v3.entities(v3.load(ux_p), 'interfaces')]

    add, gone, changed = [], [], []
    for a, g, c in (
        compare_roles(doc_roles, spec.get('roles') or []),
        compare_tasks(doc_tasks, spec),
        compare_triggers(doc_triggers, spec.get('triggers') or []),
        compare_screens(doc_screens, spec.get('interfaces') or []),
        compare_cases(doc_cases, spec.get('cases') or []),
    ):
        add += a
        gone += g
        changed += c

    print('=== add (%d) — in the document, not in the spec ===' % len(add))
    for kind, id_, name in add:
        print('  + %-10s %-20s %s' % (kind, id_, name or ''))
    print('\n=== gone (%d) — in the spec, not in the document ===' % len(gone))
    for kind, id_, name in gone:
        print('  - %-10s %-20s %s' % (kind, id_, name or ''))
    # Расхождение имени, отклонённое ЗАЩИТОЙ ПИСЬМЕННОСТИ, — это не новость, а
    # постоянное состояние по замыслу: macstack.json всегда латиница, документ
    # написан на языке проекта. На живом проекте таких 79 из 90, и печатать их
    # каждый прогон значит топить одиннадцать настоящих в шуме, который всегда
    # одинаковый. Одна строка вместо семидесяти девяти — и она честно называет
    # число, а не скрывает его.
    script_only = [r for r in changed
                   if not r['appliable'] and not is_english(r['want'])]
    rest = [r for r in changed if r not in script_only]
    print('\n=== changed (%d) — id matched, values differ ===' % len(changed))
    for rec in rest:
        if rec['appliable']:
            tag = ''
        elif would_erase(rec['want'], rec['have']):
            tag = '  [not applied — a blank in the document would erase the spec]'
        else:
            tag = '  [report only, not applied]'
        print('  ~ %-10s %-16s %-10s spec=%r  doc=%r%s' %
              (rec['kind'], rec['id'], rec['field'], rec['have'], rec['want'], tag))
    if script_only:
        kinds = {}
        for r in script_only:
            kinds[r['kind']] = kinds.get(r['kind'], 0) + 1
        print('  · ещё %d — имя на языке проекта против латиницы в спеке, '
              'так и задумано (%s). Показать: --script'
              % (len(script_only), ', '.join('%s %d' % kv for kv in sorted(kinds.items()))))
        if '--script' in sys.argv:
            for rec in script_only:
                print('    ~ %-10s %-16s %-10s spec=%r  doc=%r'
                      % (rec['kind'], rec['id'], rec['field'], rec['have'], rec['want']))

    if apply_:
        raw = io.open(spec_p, encoding='utf-8').read()
        before = len(raw.splitlines())
        applied, skipped = 0, []
        for r in changed:
            if not r['appliable']:
                continue
            path = path_of(spec, r)
            if path is None:
                skipped.append('%s %s.%s — could not locate it in the spec' % (r['kind'], r['id'], r['field']))
                continue
            try:
                raw = J.set_value(raw, path, r['want'])
                applied += 1
            except Exception as e:
                # a refused edit is reported, never forced: the alternative is a spec
                # that parses and says something nobody asked for
                skipped.append('%s %s.%s — %s' % (r['kind'], r['id'], r['field'], e))
        if applied:
            io.open(spec_p, 'w', encoding='utf-8').write(raw)
            print('\n  %d lines before, %d after — formatting preserved' % (before, len(raw.splitlines())))
        for s in skipped:
            print('  not written: %s' % s)
        print('\n%s: %d' % (msg(lang, 'applied'), applied))
    elif changed:
        print('\n' + msg(lang, 'dry_run'))

    if add or gone:
        print('\nadd/gone are never applied automatically — a new id is a decision for a human.')

    return 0


if __name__ == '__main__':
    sys.exit(main())
