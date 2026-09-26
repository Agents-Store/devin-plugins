#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Seed the three AUTHORED client documents once, from macstack.json.

client/AUTOMATION.md, client/UX-UI.md and client/HANDBOOK.md are written by a human
and read by the client — they are a SOURCE of the spec's business half, not its
output (invariant 9). But a blank page is a bad start when the spec already knows the
roles, the tasks, the triggers and the interfaces, so this seeds a FIRST v3-format
version of each — headings and bullet lists, a `macstack:ref` pointer above every
entity naming where the same fact lives in macstack.json — and then never touches it
again.

Pointer binding is not one relation (v3.py's own docstring has the census): a role or
a trigger points at itself (identity), a screen points at the interface it belongs to
even before it has siblings there (container), and a procedure seeded from a critical
user case points at the role's case glob, because a procedure has no entry of its own
in macstack.json — container too, since `coach-c-04` is not a member of the glob `C-*`
that lives there; it is one of many procedures filed under it, exactly as many screens
are filed under one interface. Where the id a pointer needs is missing, this writes
`TODO reason=...` rather than a pointer that merely LOOKS resolved — every downstream
check trusts a `macstack:ref` line, and a wrong one is invisible until it is acted on.

REFUSES to overwrite. If the file exists, say so and stop: overwriting an authored
document with a machine guess is how a client's correction disappears. `--force`
replaces it anyway with a fresh seed (used to reseed, never as the normal path).

Usage: seed.py <macstack-dir> [--force] [--only automation|ux-ui|handbook]
"""
import sys, os, io, json, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from i18n import doc_lang, msg, out                  # noqa: E402
import v3                                             # noqa: E402

CASE_ROLE_REF = re.compile(r'^roles\[id=([^\]]+)\]')


def case_role(c):
    """The role a USER-CASES.md case belongs to. On the live corpus a case has no
    'role' bullet of its own — role is carried entirely by the case's own pointer,
    `roles[id=coach].cases` — so that is read first; a bare `role` field is only a
    fallback for a document that happens to declare one anyway. A cross-cutting case
    (X-/S-/Z-) has neither and comes back ''."""
    m = CASE_ROLE_REF.match(c.ref or '')
    return m.group(1) if m else (c.get('role') or '')


def known(fields, lang):
    """Only the fields the spec actually has a value for.

    v2 put the rest in the yaml block as `screens: []` / `workflow: —`, where a machine
    read them as empty-AND-known. A bullet has no such notation: `- **Экраны:**` reads
    back as the string '', which asserts the screens ARE empty rather than unknown. The
    migrator drops them — the live AUTOMATION.md carries 123 bullets and not one empty
    — and a reseed must not put 227 of them back.
    """
    return {k: v for k, v in fields.items() if v3.value_text(v, lang)}


def load_spec(root):
    try:
        with io.open(os.path.join(root, 'macstack.json'), encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def L(table, lang):
    return table.get(lang) or table['en']


def doc_header(doc_type, lang, version):
    """Same line in every format version — v3.py reads it but has no writer for it,
    since a header is not an entity and emit_entity's job stops at entities."""
    return '<!-- macstack:doc=%s lang=%s version=%s -->' % (doc_type, lang, version)


# ---------------------------------------------------------------- prose catalogue
TITLE = {
    'ru': dict(automation="Автоматизация — роли, задачи, триггеры",
               ux_ui="Интерфейс — что видно и чего быть не должно",
               handbook="Справочник — как работать с платформой"),
    'en': dict(automation="Automation — roles, tasks, triggers",
               ux_ui="Interface — what is visible and what must not be",
               handbook="Handbook — how to work with the platform"),
}

HEAD = {
    'ru': dict(howto="Как читать и как править", roles="Роли", tasks="Задачи",
               triggers="Триггеры",
               principles="Принципы", navigation="Навигация", states="Пустое, загрузка, ошибка",
               responsive="Адаптивность", accessibility="Доступность", tone="Тон",
               screens="Экраны", start="С чего начать", procedures="Процедуры",
               problems="Частые проблемы", glossary="Термины"),
    'en': dict(howto="How to read and how to edit", roles="Roles", tasks="Tasks",
               triggers="Triggers",
               principles="Principles", navigation="Navigation", states="Empty, loading, error",
               responsive="Responsive", accessibility="Accessibility", tone="Tone",
               screens="Screens", start="Where to start", procedures="Procedures",
               problems="Common problems", glossary="Terms"),
}

MISC = {
    'ru': dict(
        automation_howto=(
            "**Этот документ пишете вы, а не платформа.** Из него собирается бизнес-половина\n"
            "спецификации: какие есть роли, какие у них задачи, что эти задачи запускает и какой\n"
            "процесс на это отвечает. Заготовка ниже собрана из `macstack.json`; правьте её как свой\n"
            "текст — она больше не пересобирается."),
        no_roles="В спецификации нет ни одной роли.", no_tasks="В спецификации нет ни одной задачи.",
        driven_by='Приводится в движение: %s.',
        no_triggers="В спецификации нет ни одного триггера.",
        sees_label="Что видит", can_label="Что может",
        # v2 found a prose block by the anchor above it, so the wording was free. v3 has
        # no anchors: the LABEL is the key, and it has to be the word doc-contracts.json
        # `prose` declares for that block, or nothing can find it. `happens` reads
        # «Что происходит» for a task and for a trigger alike — one block, one word, two
        # hints, because what a person should write under it differs.
        happens_label="Что происходит",
        flow_hint="_Опишите шаги: кто и что делает от начала до конца этой задачи._",
        what_happens_hint="_Опишите, что видит роль, чья задача сдвигается, когда этот триггер срабатывает._",
        ux_howto=(
            "**Этот документ пишете вы.** Сквозные разделы ниже применяются к каждому экрану и\n"
            "пишутся один раз. Последняя секция каждого экрана — самая важная: там написано, чего на\n"
            "этом экране быть НЕ должно."),
        principles_hint="_Опишите 3-5 принципов интерфейса этого продукта._",
        navigation_hint="_Опишите, как человек попадает с экрана на экран._",
        states_hint="_Опишите пустое, загрузочное и ошибочное состояние — что видно и что делать._",
        responsive_hint="_Опишите поведение на узком и широком экране._",
        accessibility_hint="_Опишите требования доступности: контраст, клавиатура, читалки экрана._",
        tone_hint="_Опишите тон текста интерфейса: формальность, обращение, длина сообщений._",
        no_screens="Подходящих интерфейсов в спецификации нет.",
        content_label="Что на экране", content_hint="_Опишите, что видно на этом экране._",
        actions_label="Что можно сделать", actions_hint="_Опишите доступные действия._",
        forbidden_label="Чего здесь быть не должно", forbidden_hint="_Опишите, что запрещено показывать здесь._",
        handbook_howto=(
            "**Этот документ пишете вы**, для человека, который будет работать с платформой изо дня\n"
            "в день — не для того, кто её заказал. Заготовки процедур ниже собраны из критичных\n"
            "кейсов `client/USER-CASES.md`, если он уже существует."),
        start_hint="_Опишите первый вход: что человек видит и делает в первые пять минут._",
        see_automation="определение роли — в `AUTOMATION.md`",
        no_procedures="Нет `client/USER-CASES.md`, либо в нём нет критичных кейсов — заготовок нет.",
        steps_label="Шаги", steps_hint="_Опишите шаги от начала до конца этой процедуры._",
        problems_hint="_Опишите частые проблемы и что с ними делать._",
        glossary_hint="_Соберите термины, которые встречаются в интерфейсе, в одном месте._",
    ),
    'en': dict(
        automation_howto=(
            "**You write this document, not the platform.** It builds the business half of the\n"
            "specification: which roles exist, what their tasks are, what starts each one, and which\n"
            "process answers. The seed below is built from `macstack.json`; edit it as your own text —\n"
            "it is never regenerated again."),
        no_roles="The spec declares no roles.", no_tasks="The spec declares no tasks.",
        driven_by='Driven by: %s.',
        no_triggers="The spec declares no triggers.",
        sees_label="What it sees", can_label="What it can do",
        happens_label="What happens",
        flow_hint="_Describe the steps: who does what, start to finish, for this task._",
        what_happens_hint="_Describe what the role whose task moves sees when this trigger fires._",
        ux_howto=(
            "**You write this document.** The cross-cutting sections below apply to every screen and\n"
            "are written once. The last section of each screen is the important one: it says what must\n"
            "NOT be visible there."),
        principles_hint="_Describe 3-5 interface principles for this product._",
        navigation_hint="_Describe how a person moves from screen to screen._",
        states_hint="_Describe the empty, loading and error state — what is visible and what to do._",
        responsive_hint="_Describe behaviour at a narrow and a wide viewport._",
        accessibility_hint="_Describe accessibility requirements: contrast, keyboard, screen readers._",
        tone_hint="_Describe the tone of the interface text: formality, address, message length._",
        no_screens="No matching interfaces in the spec.",
        content_label="What is on it", content_hint="_Describe what is visible here._",
        actions_label="What can be done", actions_hint="_Describe the actions available._",
        forbidden_label="What must not be here", forbidden_hint="_Describe what is forbidden here._",
        handbook_howto=(
            "**You write this document**, for the person who will use the platform day to day — not\n"
            "for the person who commissioned it. The procedure seeds below are built from the critical\n"
            "cases in `client/USER-CASES.md`, if it already exists."),
        start_hint="_Describe the first login: what a person sees and does in the first five minutes._",
        see_automation="role definition lives in `AUTOMATION.md`",
        no_procedures="No `client/USER-CASES.md`, or it has no critical cases — nothing seeded.",
        steps_label="Steps", steps_hint="_Describe the steps, start to finish, for this procedure._",
        problems_hint="_Describe common problems and what to do about them._",
        glossary_hint="_Collect the terms that appear in the interface, in one place._",
    ),
}

SOURCE_BY_TYPE = {'schedule': 'schedule', 'form': 'interface', 'webhook': 'integration',
                   'db_event': 'backend', 'manual': 'manual'}
CFG_PRIORITY = ('schedule', 'entity', 'event', 'condition', 'path', 'form', 'queue')
SCREENISH = {'web', 'admin_ui', 'dashboard', 'approval_center', 'form'}


def trigger_source(trg):
    return SOURCE_BY_TYPE.get(trg.get('type'))


def trigger_cfg(trg):
    cfg = trg.get('config') or {}
    for key in CFG_PRIORITY:
        if cfg.get(key) is not None:
            return key, cfg[key]
    return None, None


def raises_of(trigger_id, workflows):
    return [w['id'] for w in workflows if trigger_id in (w.get('triggers') or [])]


# ---------------------------------------------------------------- client/AUTOMATION.md
def seed_automation(spec, lang):
    h, m = L(HEAD, lang), L(MISC, lang)
    emit_labels = L(v3.EMIT, lang)
    out_lines = ['## ' + h['howto'], '', m['automation_howto'], '']

    out_lines += ['## ' + h['roles'], '']
    roles = spec.get('roles') or []
    if not roles:
        out_lines += ['_%s_' % m['no_roles'], '']
    for r in roles:
        # roles[].cases живёт в спеке — документ несёт про роль то, что человек
        # ВИДИТ и МОЖЕТ, прозой. Второй список кейсов пришлось бы держать руками.
        fields = {'isolation': r.get('isolation')}
        prose = []
        if r.get('sees'):
            prose.append((m['sees_label'], [r['sees']]))
        if r.get('can'):
            prose.append((m['can_label'], [r['can']]))
        fields = known(fields, lang)
        out_lines += v3.emit_entity('role', r['id'], r.get('name', r['id']),
                                     fields=fields, prose=prose,
                                     pointer='roles[id=%s]' % r['id'],
                                     lang=lang, form='slug', order=list(fields))
        out_lines.append('')

    out_lines += ['## ' + h['tasks'], '']
    procs = spec.get('processes') or []
    wfs = {w['id']: w for w in (spec.get('workflows') or [])}
    trigs = {x['id']: x for x in (spec.get('triggers') or [])}
    any_task = False
    for p in procs:
        pid = p.get('id')
        # Процесс — заголовок, его задачи — под ним. Парадигма плагина это
        # trigger -> task -> process, и заготовка, которая печатает один
        # плоский список задач, учит неверной форме с первого дня. Контракт
        # объявляет здесь сущность `process`, а сеятель её не писал: правило
        # 12.0 поймало это на первой же чистой папке.
        if pid:
            driven = []
            for task in (p.get('tasks') or []):
                wf = wfs.get(task.get('workflow'))
                for tid in ((wf.get('triggers') or []) if wf else []):
                    tg = trigs.get(tid)
                    label = '%s (`%s`)' % (tg.get('name', tid), tid) if tg else '`%s`' % tid
                    if label not in driven:
                        driven.append(label)
            prose = [(None, [m['driven_by'] % ', '.join(driven)])] if driven else []
            out_lines += v3.emit_entity('process', pid, p.get('name', pid),
                                        prose=prose,
                                        pointer='processes[id=%s]' % pid,
                                        lang=lang, level=3, form='slug')
            out_lines.append('')
        for task in (p.get('tasks') or []):
            any_task = True
            human = task.get('human') or {}
            wf = wfs.get(task.get('workflow'))
            trig = (wf.get('triggers') or []) if wf else []
            fields = {
                'role': human.get('role'),
                'gate': human.get('gate') or ('none' if task.get('workflow') else None),
                # связь «триггер → задача» записана ОДИН раз, на самом триггере
                # («Чьи задачи двигает»). Здесь она была бы вторым экземпляром,
                # который расходится с первым при первой же правке.
                'workflow': task.get('workflow'),
                # процесс — это указатель сущности, а не её поле
            }
            prose = [(m['happens_label'], [m['flow_hint']])]
            # identity binding is two levels deep here: a task lives at
            # processes[id=].tasks[id=], never at a top-level tasks[].
            pointer = ('processes[id=%s].tasks[id=%s]' % (pid, task['id']) if pid
                       else 'TODO reason=no-process')
            fields = known(fields, lang)
            out_lines += v3.emit_entity('role_task', task['id'], task.get('name', task['id']),
                                         fields=fields, prose=prose, pointer=pointer,
                                         lang=lang, level=4 if pid else 3,
                                         form='slug', order=list(fields))
            out_lines.append('')
    if not any_task:
        out_lines += ['_%s_' % m['no_tasks'], '']

    out_lines += ['## ' + h['triggers'], '']
    trgs = spec.get('triggers') or []
    workflows = spec.get('workflows') or []
    if not trgs:
        out_lines += ['_%s_' % m['no_triggers'], '']
    for g in trgs:
        cfg_key, cfg_val = trigger_cfg(g)
        fields = {'type': g.get('type'), 'source': trigger_source(g)}
        # v3.EMIT does not declare a label for every macstack.json config key a
        # trigger can carry (a form trigger's own `config.form`, for one) — dropping
        # the bullet beats crashing on emit_field or inventing a label nobody
        # declared; the pointer below still leads a reader to the real value.
        if cfg_key and cfg_key in emit_labels:
            fields[cfg_key] = cfg_val
        fields['raises'] = raises_of(g['id'], workflows)
        prose = [(m['happens_label'], [m['what_happens_hint']])]
        fields = known(fields, lang)
        out_lines += v3.emit_entity('trigger', g['id'], g.get('name', g['id']),
                                     fields=fields, prose=prose,
                                     pointer='triggers[id=%s]' % g['id'],
                                     lang=lang, form='slug', order=list(fields))
        out_lines.append('')

    return '\n'.join(out_lines).rstrip('\n') + '\n'


# ---------------------------------------------------------------- client/UX-UI.md
def seed_ux_ui(spec, lang):
    h, m = L(HEAD, lang), L(MISC, lang)
    out_lines = ['## ' + h['howto'], '', m['ux_howto'], '']
    for key in ('principles', 'navigation', 'states', 'responsive', 'accessibility', 'tone'):
        out_lines += ['## ' + h[key], '', m['%s_hint' % key], '']

    out_lines += ['## ' + h['screens'], '']
    ifs = spec.get('interfaces') or []
    screens = [i for i in ifs if i.get('type') in SCREENISH
               and (not i.get('mode') or i.get('mode') == 'ui')
               and (i.get('audience') in (None, 'human'))]
    if not screens:
        out_lines += ['_%s_' % m['no_screens'], '']
    for i in screens:
        fields = {'path': i.get('path'), 'roles': i.get('roles') or []}
        prose = [
            (m['content_label'], [m['content_hint']]),
            (m['actions_label'], [m['actions_hint']]),
            (m['forbidden_label'], [m['forbidden_hint']]),
        ]
        # container binding: a seeded screen starts as one heading per interface,
        # but nothing stops a later edit from splitting one interface into several
        # screen headings — they all keep pointing at the same container.
        area = i.get('id')
        pointer = 'interfaces[id=%s]' % area if area else 'TODO reason=no-container'
        fields = known(fields, lang)
        out_lines += v3.emit_entity('screen', i['id'], i.get('name', i['id']),
                                     fields=fields, prose=prose, pointer=pointer,
                                     lang=lang, form='slug', order=list(fields))
        out_lines.append('')

    return '\n'.join(out_lines).rstrip('\n') + '\n'


# ---------------------------------------------------------------- client/HANDBOOK.md
def seed_handbook(spec, root, lang):
    h, m = L(HEAD, lang), L(MISC, lang)
    out_lines = ['## ' + h['howto'], '', m['handbook_howto'], '']
    out_lines += ['## ' + h['start'], '', m['start_hint'], '']

    roles = spec.get('roles') or []
    out_lines += ['## ' + h['roles'], '']
    if not roles:
        out_lines += ['_%s_' % m['no_roles'], '']
    for r in roles:
        out_lines.append('- **%s** — %s' % (r['id'], m['see_automation']))
    out_lines.append('')

    out_lines += ['## ' + h['procedures'], '']
    uc_path = os.path.join(root, 'client', 'USER-CASES.md')
    critical_by_role = {}
    if os.path.exists(uc_path):
        # USER-CASES.md is a v3 document now. Reading it with the v2 parser did not
        # error, it returned nothing — every "no critical cases" here would have been a
        # lie, not an absence. Read it in the language IT declares, never in the
        # project's: v3 matches bullet labels per language, so handing a ru document the
        # project's `en` misses every label and lands in the same silent zero by a new
        # route. `v3.load` with no lang takes it from the document's own header.
        for c in v3.load(uc_path):
            if c.id and (c.get('priority') or '') == 'critical':
                critical_by_role.setdefault(case_role(c), []).append(c)
    if not critical_by_role:
        out_lines += ['_%s_' % m['no_procedures'], '']
    else:
        for role in sorted(critical_by_role):
            for c in sorted(critical_by_role[role], key=lambda it: it.id):
                # A leading hyphen (role='' -> '-x-01') is not a v3 heading id at
                # all — form='slug' would write it, v3.load() would never read it
                # back, and the procedure becomes invisible to every later check.
                slug = ('%s-%s' % (role, c.id.lower())) if role else c.id.lower()
                fields = {'role': role, 'screens': c.get('screens') or [],
                          'cases': [c.id], 'frequency': None}
                prose = [(m['steps_label'], [m['steps_hint']])]
                # container binding, not member: a procedure has no entry of its
                # own in macstack.json, so it points at the case glob on its role — the
                # same target the source case uses. The case `C-04` IS a member of that
                # glob; the procedure `coach-c-04` is not, it is one of many filed under
                # it. Calling this member is what would make a later binding check fail.
                pointer = ('roles[id=%s].cases' % role if role
                           else 'TODO reason=no-role')
                fields = known(fields, lang)
                out_lines += v3.emit_entity('procedure', slug, c.title,
                                             fields=fields, prose=prose, pointer=pointer,
                                             lang=lang, form='slug', order=list(fields))
                out_lines.append('')

    out_lines += ['## ' + h['problems'], '', m['problems_hint'], '']
    out_lines += ['## ' + h['glossary'], '', m['glossary_hint'], '']

    return '\n'.join(out_lines).rstrip('\n') + '\n'


# ---------------------------------------------------------------- assembly
def build_full(doc_key, lang, body):
    """Header + title + body. No journal: a seeded document has no history yet, and
    once it does, that history lives in history/ — never inside the client document
    itself, and never as a table (rule 12.24)."""
    header = doc_header(doc_key, lang, '1.0')
    title = '# ' + L(TITLE, lang)[doc_key]
    return header + '\n' + title + '\n\n' + body.rstrip('\n') + '\n'


# ---------------------------------------------------------------- main
def main():
    argv = sys.argv[1:]
    force = '--force' in argv
    only = None
    positional = []
    i = 0
    while i < len(argv):
        a = argv[i]
        # --date is still accepted and consumed for CLI compatibility, even though
        # nothing below reads it any more: it only ever fed the journal row, and a
        # seeded document carries no journal (see build_full).
        if a == '--date' and i + 1 < len(argv):
            i += 2; continue
        if a == '--only' and i + 1 < len(argv):
            only = argv[i + 1]; i += 2; continue
        if a == '--force':
            i += 1; continue
        positional.append(a); i += 1
    root = positional[0] if positional else 'macstack'

    spec = load_spec(root)
    lang = doc_lang(root)
    os.makedirs(os.path.join(root, 'client'), exist_ok=True)

    jobs = []
    if only in (None, 'automation'):
        jobs.append(('automation', 'AUTOMATION.md', lambda: seed_automation(spec, lang)))
    if only in (None, 'ux-ui'):
        jobs.append(('ux_ui', 'UX-UI.md', lambda: seed_ux_ui(spec, lang)))
    if only in (None, 'handbook'):
        jobs.append(('handbook', 'HANDBOOK.md', lambda: seed_handbook(spec, root, lang)))

    rc = 0
    for doc_key, filename, fn in jobs:
        path = os.path.join(root, 'client', filename)
        if os.path.exists(path) and not force:
            out(lang, 'refuse_exists', path=path)
            rc = 1
            continue
        body = build_full(doc_key, lang, fn())
        with io.open(path, 'w', encoding='utf-8') as f:
            f.write(body)
        out(lang, 'wrote', path=path)
    return rc


if __name__ == '__main__':
    sys.exit(main())
