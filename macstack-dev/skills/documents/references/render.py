#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render the three GENERATED documents of a macstack/ folder. Three documents,
three different sources:

    generated/ARCHITECTURE.md   <- macstack.json                 how it is built
    generated/INDEX.md          <- client/*.md + TEST-CASES.md    the folder's own index
    README.md                   <- doc-contracts.json             the folder's own contract

Deterministic BY DESIGN. Lint rule 12.18 re-renders and compares, so a renderer whose
output varies between runs would make that rule permanently red. Everything here is a
pure function of its source: no timestamps in the body, no dict iteration that depends
on hash order (every grouping key is sorted explicitly before it is walked), no prose
invented at render time.

The ONE exception is the journal: those rows are human history and must survive a
rebuild. They are read back out of the existing file and carried forward. A new row is
appended only when the rendered body actually changed, which is what keeps a second run
byte-identical to the first.

Usage:  render.py <macstack-dir> [--date YYYY-MM-DD] [--check] [--only architecture|index|readme]
        --check   render into memory and report differences without writing (12.18)
"""
import sys, os, io, re, json, datetime, difflib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Only the section/doc anchors are still mdblocks' — every entity below is v3's now.
from mdblocks import anchor, doc_header
from i18n import doc_lang, msg, out
import v3                                            # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CONTRACT_PATH = os.path.join(HERE, 'doc-contracts.json')


def load_contract():
    with io.open(CONTRACT_PATH, encoding='utf-8') as f:
        return json.load(f)


def load_spec(root):
    try:
        with io.open(os.path.join(root, 'macstack.json'), encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def esc(s):
    return str(s).replace('|', '\\|').replace('\n', ' ').strip() if s is not None else ''


def L(table, lang):
    return table.get(lang) or table['en']


# ---------------------------------------------------------------- prose catalogue
# Headings, one-line explanations and grouping labels, per document. Anchors and
# YAML keys never appear here — only what docs.language governs.
TITLE = {
    'ru': dict(architecture="Архитектура — как здесь строят",
               index="Индекс — кейсы, экраны, триггеры, покрытие",
               readme="Карта папки macstack/"),
    'en': dict(architecture="Architecture — how this is built",
               index="Index — cases, screens, triggers, coverage",
               readme="Map of the macstack/ folder"),
}

HEAD = {
    'ru': dict(howto="Как читать этот документ", stack="Чем собрано",
               entities="Сущности и где они лежат", workflows="Что исполняется",
               integrations="Интеграции и контекст", journal="Журнал документа",
               cases="Кейсы", screens="Экраны", triggers="Триггеры", coverage="Покрытие",
               map="Карта", ownership="Кто чем владеет", idspaces="Пространства id",
               loop="Цикл работы",
        processes='Процессы',
        roles='Роли',
        tasks='Задачи',
        invariants='Правила, которые не нарушаются',
        prohibitions='Запреты',
        glossary='Словарь',
        open_questions='Открытые вопросы',
    ),
    'en': dict(howto="How to read this", stack="What it is made of",
               entities="Entities and where they live", workflows="What runs",
               integrations="Integrations and context", journal="Document journal",
               cases="Cases", screens="Screens", triggers="Triggers", coverage="Coverage",
               map="Map", ownership="Who owns what", idspaces="ID spaces",
               loop="Working loop",
        processes='Processes',
        roles='Roles',
        tasks='Tasks',
        invariants='Invariants',
        prohibitions='Prohibitions',
        glossary='Glossary',
        open_questions='Open questions',
    ),
}

MISC = {
    'ru': dict(
        banner_note="Собран из `{src}`. Правки руками теряются при следующей сборке — правьте источник.",
        rebuilt="пересобран из `{src}`", created="создан",
        col_date="дата", col_what="что изменилось",
        arch_howto=(
            "Машинная половина спецификации, разложенная для человека и для агента, которому предстоит\n"
            "здесь строить: чем собрано, что хранится и где, что исполняется и в каком файле."),
        patterns="паттерны", no_software="В спецификации нет ни одного software.",
        no_entities="В спецификации нет ни одной сущности.",
        single_master="**master для всех сущностей этого раздела:** `{master}`.",
        master_label="master", status_label="статус",
        no_workflows="В спецификации нет ни одного workflow.",
        mcp_label="MCP-соединения", interfaces_label="Интерфейсы", plugins_label="Плагины",
        no_cases="Пока нет `client/USER-CASES.md` — кейсов нет.",
        no_screens="Пока нет `client/UX-UI.md` — экранов нет.",
        no_triggers="Пока нет `client/AUTOMATION.md` — триггеров нет.",
        no_coverage="Нет кейсов, покрывать нечего.",
        role_col="роль", cases_col="кейсов", acc_col="пунктов приёмки", tests_col="тестов",
        tests_cell="{n} (авто {auto} / вручную {manual}, без теста {open})",
        coverage_line="кейсов: {cases} · пунктов приёмки: {acc} · тестов: {tests} (авто {auto} / вручную {manual}, без теста {open})",
        owned_generated="генерируется из `{source}`",
        owned_derived="сеется из {sources}, дальше ведётся руками",
        owned_authored="авторский документ, аудитория: {audience}",
        loop_lines=[
            "Материал клиента ложится в `inbox/` и получает запись в `history/log.md`.",
            "Анализ становится дельтой в `history/deltas/` — что противоречит, что добавляется.",
            "Дельта разрешается решениями в `history/decisions/` — что принято и почему.",
            "Принятое применяется к `client/*.md`, откуда `render.py` пересобирает генерируемые документы.",
        ],
        value_prose={
            'interface': "Обеспечивает интерфейс — то, через что человек или агент видит систему.",
            'workflows': "Исполняет процессы — то, что двигает данные и запускает действия.",
            'data': "Держит данные — источник фактов для остального стека.",
            'storage': "Хранит и раздаёт — инфраструктурный слой под данными и процессами.",
        },
    
        nothing_found='В %s не нашлось ни одной сущности — либо документ пуст, либо его формат не разбирается',
        requirements_lead='Каждое проверяемое утверждение клиентских документов, с его постоянным адресом. Ничего руками: правьте client/.',
        tests_lead="Кейс проверен, когда есть сценарный тест, проходящий его целиком. Связь — в названии теста: `test('... (CC-04)')`. Инженерные тесты показаны отдельно: они поддержка, а не доказательство.",
        no_acceptance='нет пунктов приёмки',
        no_scenario='сценарного теста нет',
        supported_by='есть инженерные: %d',
        not_covered='не покрыт',
    ),
    'en': dict(
        banner_note="Generated from `{src}`. Hand edits are lost on the next render — edit the source.",
        rebuilt="rebuilt from `{src}`", created="created",
        col_date="date", col_what="what changed",
        arch_howto=(
            "The machine half of the spec laid out for a human and for the agent that has to build here:\n"
            "what it is made of, what is stored and where, what runs and in which file."),
        patterns="patterns", no_software="The spec declares no software.",
        no_entities="The spec declares no entities.",
        single_master="**master for every entity in this section:** `{master}`.",
        master_label="master", status_label="status",
        no_workflows="The spec declares no workflows.",
        mcp_label="MCP connections", interfaces_label="Interfaces", plugins_label="Plugins",
        no_cases="No `client/USER-CASES.md` yet — no cases.",
        no_screens="No `client/UX-UI.md` yet — no screens.",
        no_triggers="No `client/AUTOMATION.md` yet — no triggers.",
        no_coverage="No cases, nothing to cover.",
        role_col="role", cases_col="cases", acc_col="acceptance bullets", tests_col="tests",
        tests_cell="{n} (auto {auto} / manual {manual}, {open} without a test)",
        coverage_line="cases: {cases} · acceptance bullets: {acc} · tests: {tests} (auto {auto} / manual {manual}, {open} without a test)",
        owned_generated="generated from `{source}`",
        owned_derived="seeded from {sources}, maintained by hand from there",
        owned_authored="authored document, audience: {audience}",
        loop_lines=[
            "Client material lands in `inbox/` and gets an entry in `history/log.md`.",
            "Analysis becomes a delta in `history/deltas/` — what contradicts, what is added.",
            "The delta is resolved by decisions in `history/decisions/` — what was ruled, and why.",
            "What was accepted is applied to `client/*.md`, from which `render.py` rebuilds the generated documents.",
        ],
        value_prose={
            'interface': "Provides the interface — what a person or an agent sees the system through.",
            'workflows': "Runs the processes — what moves data and fires actions.",
            'data': "Holds the data — the source of facts for the rest of the stack.",
            'storage': "Stores and serves — the infrastructure layer under the data and the processes.",
        },
    
        nothing_found='No entities were found in %s — the document is either empty or its format does not parse',
        requirements_lead='Every checkable statement of the client documents, at its permanent address. Nothing by hand: edit client/.',
        tests_lead="A case is verified when a scenario test covers it end to end. The link is in the test title: `test('... (CC-04)')`. Engineering tests are shown separately: they are support, not proof.",
        no_acceptance='no acceptance bullets',
        no_scenario='no scenario test',
        supported_by='engineering tests: %d',
        not_covered='not covered',
    ),
}


# ---------------------------------------------------------------- ARCHITECTURE.md
# form='slug' on every entity here, never form='id'. v3 takes the id from the
# HEADING, not from the pointer, and _split_heading's id-first branch only
# accepts a spoken id — CC-04, QA5, M3-T1, CZ-03. software/entities/workflows are
# technical slugs (payload, coach, wf-entry-capture), so '### payload · Payload'
# parses as a titled heading with NO id: 39 pointers, 39 headings, 0 entities,
# and not one error. The em-dash form '### Payload — `payload`' is what
# format-rules §3 declares for a slug, and it is the only one v3 can read back.
def _bullet(key, value, lang):
    """'- **key:** value'.

    The key is the literal ASCII macstack.json field name, never translated —
    doc-contracts.format.yaml_rule already made that promise for the fenced yaml
    block this line replaces, and a bullet label is that same key wearing v3's
    punctuation instead of a colon inside a fence. Only the VALUE goes through
    v3's own rules (v3.value_text): booleans become words, bare identifiers get
    backticked, an empty value leaves no trailing space rather than a dash.
    """
    text = v3.value_text(value, lang)
    return '- **%s:**%s' % (key, (' ' + text) if text else '')


def _agentic_text(agentic, lang):
    """'mcp да, api да, cli да, rating `full`' — macstack.json nests this one field;
    everything else in a software entity is already flat. The old dump_yaml path
    pre-stringified True/False here because a nested Python bool round-tripped as
    the WORD 'True'; v3.value_text has no such bug, so mcp/api/cli/partial go
    through it exactly like any other bullet value, in the one order the schema
    declares them (never dict order, which agentic dicts don't reliably keep).

    A key present but empty is DROPPED rather than rendered as a bare word: it
    would leave '- **agentic:** rating ' with a hanging space, which is the same
    defect v3.emit_field guards against and which put 41 such lines into a live
    HANDBOOK.md. False is not empty — it renders as 'нет' and stays."""
    parts = []
    for k in ('mcp', 'api', 'cli', 'rating'):
        text = v3.value_text(agentic[k], lang) if k in agentic else ''
        if text:
            parts.append('%s %s' % (k, text))
    return ', '.join(parts)


def render_architecture(spec, lang):
    h, m = L(HEAD, lang), L(MISC, lang)
    out_lines = ['# ' + L(TITLE, lang)['architecture'], '',
                 anchor('section', 'howto'), '## ' + h['howto'], '', m['arch_howto'], '']

    # ---- stack ----
    out_lines += [anchor('section', 'stack'), '## ' + h['stack'], '']
    patterns = ((spec.get('profile') or {}).get('architecture_patterns')) or []
    if patterns:
        out_lines += ['**%s:** %s' % (m['patterns'], ' · '.join('`%s`' % p for p in patterns)), '']
    software = spec.get('software') or []
    if not software:
        out_lines += ['_%s_' % m['no_software'], '']
    for s in software:
        bullets = [
            _bullet('category', s.get('category'), lang),
            _bullet('type', s.get('type'), lang),
            _bullet('layers', s.get('layers') or [], lang),
            _bullet('license', s.get('license'), lang),
            _bullet('hosting', s.get('hosting'), lang),
            _bullet('agentic', _agentic_text(s.get('agentic') or {}, lang), lang),
            _bullet('role', s.get('role'), lang),
        ]
        prose = [(None, bullets)]
        if s.get('value'):
            prose.append((None, [m['value_prose'].get(s['value'], s['value'])]))
        out_lines += v3.emit_entity('software', s['id'], s.get('name', s['id']),
                                     prose=prose, pointer='software[id=%s]' % s['id'],
                                     lang=lang, level=3, form='slug')
        out_lines.append('')

    # ---- entities ----
    out_lines += [anchor('section', 'entities'), '## ' + h['entities'], '']
    ents = spec.get('entities') or []
    if not ents:
        out_lines += ['_%s_' % m['no_entities'], '']
    else:
        masters = sorted(set(e.get('master') for e in ents))
        single_master = masters[0] if len(masters) == 1 else None
        if single_master:
            out_lines += [m['single_master'].format(master=single_master), '']
            for e in ents:
                bullets = [
                    _bullet('stores', [st.get('software') for st in (e.get('stores') or [])], lang),
                    _bullet('volume', e.get('volume'), lang),
                ]
                out_lines += v3.emit_entity('entity', e['id'], e.get('name', e['id']),
                                             prose=[(None, bullets)],
                                             pointer='entities[id=%s]' % e['id'],
                                             lang=lang, level=3, form='slug')
                out_lines.append('')
        else:
            by_master = {}
            for e in ents:
                by_master.setdefault(e.get('master') or '', []).append(e)
            for master in sorted(by_master):
                out_lines += ['**%s:** `%s`' % (m['master_label'], master or '—'), '']
                for e in by_master[master]:
                    bullets = [
                        _bullet('master', e.get('master'), lang),
                        _bullet('stores', [st.get('software') for st in (e.get('stores') or [])], lang),
                        _bullet('volume', e.get('volume'), lang),
                    ]
                    out_lines += v3.emit_entity('entity', e['id'], e.get('name', e['id']),
                                                 prose=[(None, bullets)],
                                                 pointer='entities[id=%s]' % e['id'],
                                                 lang=lang, level=3, form='slug')
                    out_lines.append('')

    # ---- workflows ----
    out_lines += [anchor('section', 'workflows'), '## ' + h['workflows'], '']
    wfs = spec.get('workflows') or []
    if not wfs:
        out_lines += ['_%s_' % m['no_workflows'], '']
    else:
        by_status = {}
        for w in wfs:
            by_status.setdefault(w.get('status') or '', []).append(w)
        for status in sorted(by_status):
            out_lines += ['**%s:** `%s`' % (m['status_label'], status or '—'), '']
            for w in by_status[status]:
                bullets = [
                    _bullet('engine', w.get('engine'), lang),
                    _bullet('triggers', w.get('triggers') or [], lang),
                    _bullet('invocation', w.get('invocation') or [], lang),
                    _bullet('implements', w.get('implements'), lang),
                    _bullet('location', w.get('location'), lang),
                ]
                out_lines += v3.emit_entity('workflow', w['id'], w.get('name', w['id']),
                                             prose=[(None, bullets)],
                                             pointer='workflows[id=%s]' % w['id'],
                                             lang=lang, level=3, form='slug')
                out_lines.append('')

    # ---- integrations ----
    out_lines += [anchor('section', 'integrations'), '## ' + h['integrations'], '']
    mcp = ((spec.get('connections') or {}).get('mcp')) or []
    if mcp:
        out_lines += ['**%s**' % m['mcp_label'], '']
        for c in mcp:
            out_lines.append('- `%s`' % esc(c.get('software') or c.get('id')))
        out_lines.append('')
    ifs = spec.get('interfaces') or []
    if ifs:
        out_lines += ['**%s**' % m['interfaces_label'], '']
        for i in ifs:
            out_lines.append('- `%s` — %s' % (esc(i['id']), esc(i.get('type') or '—')))
        out_lines.append('')
    plugins = ((spec.get('context') or {}).get('plugins')) or {}
    flat = []
    if isinstance(plugins, dict):
        for host in sorted(plugins):
            lst = plugins[host]
            if isinstance(lst, list):
                for p in lst:
                    flat.append((host, p))
    if flat:
        out_lines += ['**%s**' % m['plugins_label'], '']
        for host, p in flat:
            name = p.get('name') if isinstance(p, dict) else str(p)
            covers = ' · '.join(p.get('covers') or []) if isinstance(p, dict) else ''
            out_lines.append('- `%s` (%s) — %s' % (esc(name), esc(host), esc(covers or '—')))
        out_lines.append('')

    return '\n'.join(out_lines).rstrip('\n') + '\n'


# ---------------------------------------------------------------- INDEX.md
def render_index(root, lang):
    """Оглавление: все кейсы, экраны и триггеры плюс счёт покрытия.

    Читает КЛИЕНТСКИЕ документы в формате v3 — заголовки и списки. v2-читатель искал
    здесь якоря сущностей и, когда их убрали, молча отдал пустой указатель: пять
    разделов по нулю пунктов, и ни одной ошибки. Отсюда правило: генератор, не нашедший
    ни одного элемента там, где документ не пуст, обязан сказать об этом вслух.
    """
    h, m = L(HEAD, lang), L(MISC, lang)
    out_lines = ['# ' + L(TITLE, lang)['index'], '']

    cases = [i for i in v3.load(os.path.join(root, 'client', 'USER-CASES.md'), lang) if i.id]
    screens = [i for i in v3.load(os.path.join(root, 'client', 'UX-UI.md'), lang)
               if i.id and (i.ref or '').startswith('interfaces[')]
    triggers = [i for i in v3.load(os.path.join(root, 'client', 'AUTOMATION.md'), lang)
                if i.id and (i.ref or '').startswith('triggers[id=')]
    tests = [i for i in v3.load(os.path.join(root, 'generated', 'TEST-CASES.md'), lang) if i.id]

    # ---- кейсы, сгруппированные по разделу документа ----
    out_lines += ['## ' + h['cases'], '']
    if not cases:
        out_lines += ['_%s_' % m['no_cases'], '']
    else:
        by_sec = []
        for c in cases:
            key = c.section or '—'
            if not by_sec or by_sec[-1][0] != key:
                by_sec.append((key, []))
            by_sec[-1][1].append(c)
        for sec, items in by_sec:
            out_lines += ['**%s**' % esc(sec), '']
            for c in items:
                prio = c.get('priority')
                out_lines.append('- **%s** · %s%s' % (
                    c.id, esc(c.title or ''), (' — `%s`' % esc(prio)) if prio else ''))
            out_lines.append('')

    # ---- экраны ----
    out_lines += ['## ' + h['screens'], '']
    if not screens:
        out_lines += ['_%s_' % m['no_screens'], '']
    else:
        for sc in sorted(screens, key=lambda b: b.id):
            path = sc.get('path')
            roles = sc.get('roles')
            roles_s = ', '.join(roles) if isinstance(roles, list) else (roles or '')
            out_lines.append('- **%s** · %s%s%s' % (
                sc.id, esc(sc.title or ''),
                (' — `%s`' % esc(str(path))) if path else '',
                (' (%s)' % esc(str(roles_s))) if roles_s else ''))
        out_lines.append('')

    # ---- триггеры ----
    out_lines += ['## ' + h['triggers'], '']
    if not triggers:
        out_lines += ['_%s_' % m['no_triggers'], '']
    else:
        for tg in sorted(triggers, key=lambda b: b.id):
            bits = [x for x in (tg.get('type'), tg.get('source')) if x]
            raises = tg.get('raises')
            out_lines.append('- **%s** · %s%s%s' % (
                tg.id, esc(tg.title or ''),
                (' — %s' % esc(' / '.join(str(b) for b in bits))) if bits else '',
                (' — %s' % esc(str(raises))) if raises else ''))
        out_lines.append('')

    # ---- покрытие ----
    out_lines += ['## ' + h['coverage'], '']
    if not cases:
        out_lines += ['_%s_' % m['no_coverage'], '']
    else:
        out_lines += _coverage_v3(cases, tests, lang)

    return '\n'.join(out_lines).rstrip('\n') + '\n'


def _coverage_v3(cases, tests, lang):
    """Счёт покрытия списком: пунктов приёмки против тестов, по разделам документа."""
    m = L(MISC, lang)
    covered = set()
    for t in tests:
        cov = t.get('covers')
        for aid in (cov if isinstance(cov, list) else ([cov] if cov else [])):
            covered.add(str(aid))
    per = []
    for c in cases:
        key = c.section or '—'
        bullets = 0
        for label, body in c.sections.items():
            if any(w in label.lower() for w in ('готово', 'done when', 'acceptance')):
                bullets = sum(1 for ln in body if ln.strip().startswith('-'))
        ids = ['%s.a%d' % (c.id, i + 1) for i in range(bullets)]
        if not per or per[-1][0] != key:
            per.append([key, 0, 0, 0])
        per[-1][1] += 1
        per[-1][2] += len(ids)
        per[-1][3] += sum(1 for a in ids if a in covered)
    lines = []
    for key, n_cases, n_acc, n_cov in per:
        gap = n_acc - n_cov
        lines.append('- **%s** — кейсов %d, пунктов приёмки %d, покрыто тестами %d%s'
                     % (esc(key), n_cases, n_acc, n_cov,
                        (', без теста %d' % gap) if gap else ''))
    lines.append('')
    return lines


# ---------------------------------------------------------------- README.md
def _first_sentence(text):
    text = (text or '').strip()
    if not text:
        return ''
    idx = text.find('. ')
    return text[:idx + 1] if idx != -1 else text.split('\n')[0]


TEST_TITLE = re.compile(r"""^\s*(?:it|test)\s*\(\s*(['"`])(.*?)\1""", re.M)
COVERS = re.compile(r'\b(C?[A-Z]-\d{2})(\.a\d+)?\b')
# Каталоги, в которые сканер тестов не заходит. Помимо очевидного мусора здесь
# `.claude` и `.codex`: оба держат worktree'ы, а worktree — это второй экземпляр
# того же дерева. Соседняя проверка на вложенный `.git` ловит остальные случаи,
# включая чекаут, положенный внутрь проекта руками.
SKIP_DIRS = ('node_modules', '.git', '.next', 'dist', 'build', 'coverage',
             '.turbo', '.claude', '.codex', '.venv', '__pycache__')

TEST_EXT = ('.spec.ts', '.test.ts', '.spec.tsx', '.test.tsx', '.spec.js', '.test.js',
            '_test.py', '_spec.rb')


def scan_tests(project_root):
    """-> {covered_id: [(file, title)]} — что тесты САМИ про себя говорят.

    Связь живёт в названии теста, а не в отдельной таблице соответствия. Таблица
    — это второй документ, который надо держать в согласии с первым, и она врёт
    ровно с того дня, как тест удалили: покрытие остаётся зелёным, а проверки
    нет. Название теста удаляется вместе с тестом.

    Соглашение уже существовало здесь неформально: в живом наборе 36 файлов
    называют кейс прямо в заголовке — `(C-10)`, `(C-07/Z-03)`. Это его
    продолжение, только точнее: до пункта приёмки, а не до кейса.
    """
    hits = {}
    for base, dirs, files in os.walk(project_root):
        # `.claude` и `.codex` держат worktree'ы агентов — это ПОЛНЫЕ чекауты
        # того же репозитория, и без этой строки покрытие считается по чужой
        # ветке, а в TEST-CASES.md уезжают пути вида
        # `.claude/worktrees/agent-…/tests/e2e/…`. Документ читает заказчик.
        dirs[:] = [d for d in dirs
                   if d not in SKIP_DIRS
                   and not os.path.exists(os.path.join(base, d, '.git'))]
        for f in files:
            if not f.endswith(TEST_EXT):
                continue
            p = os.path.join(base, f)
            try:
                text = io.open(p, encoding='utf-8', errors='replace').read()
            except IOError:
                continue
            rel = os.path.relpath(p, project_root)
            for m in TEST_TITLE.finditer(text):
                title = m.group(2)
                for c in COVERS.finditer(title):
                    key = c.group(1) + (c.group(2) or '')
                    hits.setdefault(key, []).append((rel, title))
    return hits


def render_test_cases(root, lang):
    """Покрытие считается ПО КЕЙСАМ, а не по пунктам приёмки.

    Первая версия считала по пунктам: 384 обещания — 384 связи. Это неверная
    единица. Пункт приёмки не тест, а строка чек-листа ВНУТРИ кейса: «кнопка
    видна», «геолокация проверяется», «отказ называет расстояние» — человек
    проходит это одним сценарием, а не пятью.

    Поэтому здесь два разных слоя, и путать их нельзя:

    - СЦЕНАРНЫЙ тест проходит кейс целиком, как человек. Он и есть доказательство
      обещания. В этом проекте такие живут в tests/e2e/.
    - ИНЖЕНЕРНЫЙ тест проверяет функцию или кусок кода. Их 2315, они нужны, и
      размечать их не надо: они отвечают на вопрос «код не сломался», а не на
      вопрос «обещание выполнено».

    Инженерный тест, называющий кейс, показывается как поддержка, но за
    доказательство не считается: «эта функция работает» и «человек может это
    сделать» — разные утверждения.
    """
    h, m = L(HEAD, lang), L(MISC, lang)
    spec = load_spec(root)
    project = os.path.normpath(os.path.join(root, '..'))
    hits = scan_tests(project)

    def is_scenario(path):
        p = path.replace(os.sep, '/')
        return '/e2e/' in p or 'scenario' in p or p.endswith('.e2e.spec.ts')

    out_lines = ['# ' + L(TITLE, lang).get('test_cases', 'Test cases'), '']
    out_lines += [m['tests_lead'], '']

    rows = []
    for c in (spec.get('cases') or []):
        rows.append((c['id'], c.get('name') or '', len(c.get('acceptance') or [])))
    for pr in (spec.get('prohibitions') or []):
        rows.append((pr['id'], pr.get('name') or '', 0))

    proven = supported = 0
    body = []
    for cid, name, n_acc in rows:
        found = hits.get(cid) or []
        scen = [f for f, _ in found if is_scenario(f)]
        eng = sorted({f for f, _ in found if not is_scenario(f)})
        if scen:
            proven += 1
            mark = '`%s`' % sorted(set(scen))[0]
        elif eng:
            supported += 1
            mark = '%s · %s' % (m.get('no_scenario', 'сценарного теста нет'),
                                m.get('supported_by', 'есть инженерные: %d') % len(eng))
        else:
            mark = m.get('not_covered', 'не покрыт')
        body.append('- `%s` %s — %s' % (cid, name[:52], mark))

    total = len(rows)
    pct = (100 * proven // total) if total else 0
    out_lines += ['**Проверено сценарием: %d из %d · %d%%.** Ещё %d имеют только '
                  'инженерные тесты.' % (proven, total, pct, supported), '']
    out_lines += body
    return '\n'.join(out_lines).rstrip('\n') + '\n'


def render_requirements(root, lang):
    """Всё, что утверждают клиентские документы, в машинном виде и на одном экране.

    Это тот файл, по которому агент — Claude Code, Codex, любой другой — сверяет код с
    договорённостью. INDEX.md перечисляет ЧТО существует; здесь написано, ЧТО ОБЕЩАНО:
    каждый пункт приёмки с его постоянным адресом, каждый экранный запрет, каждый
    инвариант, каждый открытый вопрос.

    Полнота проверяется, а не обещается: правило 12.35 сверяет множество id здесь с
    множеством id в client/, и расхождение — ошибка. «Абсолютно вся информация»
    становится проверкой.
    """
    h, m = L(HEAD, lang), L(MISC, lang)
    spec = load_spec(root)
    cl = os.path.join(root, 'client')
    cases = [i for i in v3.load(os.path.join(cl, 'USER-CASES.md'), lang) if i.id]
    screens = [i for i in v3.load(os.path.join(cl, 'UX-UI.md'), lang)
               if i.id and (i.ref or '').startswith('interfaces[')]
    trig = [i for i in v3.load(os.path.join(cl, 'AUTOMATION.md'), lang)
            if i.id and (i.ref or '').startswith('triggers[id=')]
    tasks = [i for i in v3.load(os.path.join(cl, 'AUTOMATION.md'), lang)
             if i.id and '.tasks[' in (i.ref or '')]
    opens = [i for i in v3.load(os.path.join(cl, 'OPEN-QUESTIONS.md'), lang) if i.id]

    def prose(it, name):
        for k, v in it.sections.items():
            if k.rstrip(':.').strip() == name:
                return [x for x in v if x.strip().startswith('-')]
        return []

    acc_label = _prose_label('acceptance', lang)
    forb_label = _prose_label('forbidden', lang)
    shows_label = _prose_label('content', lang)
    does_label = _prose_label('actions', lang)

    out_lines = ['# ' + L(TITLE, lang).get('requirements', 'Requirements'), '']
    out_lines += [m['requirements_lead'], '']

    out_lines += ['## ' + h.get('cases', 'Cases'), '']
    if not cases:
        out_lines += ['**' + m['nothing_found'] % 'client/USER-CASES.md' + '**', '']
    for it in cases:
        bits = []
        for k in ('priority', 'screens', 'triggers', 'workflow'):
            v = it.get(k)
            if v:
                bits.append('%s=%s' % (k, ','.join(v) if isinstance(v, list) else v))
        role = ''
        mm = re.findall(r'roles\[id=([^\]]+)\]', it.ref or '')
        if mm:
            role = 'role=%s ' % mm[0]
        out_lines.append('### %s · %s' % (it.id, it.title))
        out_lines.append('')
        if role or bits:
            out_lines += ['- ' + role + ' '.join(bits), '']
        acc = prose(it, acc_label)
        for n, a in enumerate(acc, 1):
            out_lines.append('- `%s.a%d` %s' % (it.id, n, a.lstrip('- ').rstrip(';')))
        if not acc:
            out_lines.append('- ' + m.get('no_acceptance', 'нет пунктов приёмки'))
        out_lines.append('')

    out_lines += ['## ' + h.get('screens', 'Screens'), '']
    for it in screens:
        out_lines += ['### %s · %s' % (it.id, it.title), '']
        p_ = it.get('path')
        r_ = it.get('roles')
        out_lines += ['- path=%s roles=%s' % (p_ or '—',
                                              ','.join(r_) if isinstance(r_, list) else (r_ or '—')), '']
        for lbl, tag in ((shows_label, 'c'), (does_label, 'd'), (forb_label, 'f')):
            items = prose(it, lbl)
            for n, x in enumerate(items, 1):
                out_lines.append('- `%s.%s%d` %s' % (it.id, tag, n, x.lstrip('- ').rstrip(';')))
        out_lines.append('')

    procs = [i for i in v3.load(os.path.join(cl, 'AUTOMATION.md'), lang)
             if i.id and (i.ref or '').startswith('processes[id=')]
    roles = [i for i in v3.load(os.path.join(cl, 'AUTOMATION.md'), lang)
             if i.id and (i.ref or '').startswith('roles[id=')]
    out_lines += ['## ' + h.get('processes', 'Processes'), '']
    for it in procs:
        out_lines.append('- `%s` %s' % (it.id, it.title))
    out_lines.append('')
    out_lines += ['## ' + h.get('roles', 'Roles'), '']
    for it in roles:
        out_lines.append('- `%s` %s' % (it.id, it.title))
    out_lines.append('')
    # цели, результаты и интеграции документ называет в OVERVIEW.md, и без них
    # «всё, что обещано» неполно ровно на десять записей
    for key in ('goals', 'results', 'integrations'):
        rows = [i for i in v3.load(os.path.join(cl, 'OVERVIEW.md'), lang)
                if i.id and (i.ref or '').startswith(key + '[id=')]
        if not rows:
            continue
        out_lines += ['## ' + h.get(key, key.title()), '']
        for it in rows:
            extra = ' '.join('%s=%s' % (k, v) for k, v in sorted(it.fields.items()))
            out_lines.append('- `%s` %s%s' % (it.id, it.title, (' · ' + extra) if extra else ''))
        out_lines.append('')

    out_lines += ['## ' + h.get('triggers', 'Triggers'), '']
    for it in trig:
        out_lines += ['- `%s` type=%s source=%s raises=%s' %
                      (it.id, it.get('type') or '—', it.get('source') or '—',
                       it.get('raises') or '—')]
    out_lines.append('')

    out_lines += ['## ' + h.get('tasks', 'Tasks'), '']
    for it in tasks:
        out_lines.append('- `%s` role=%s gate=%s' %
                         (it.id, it.get('role') or '—', it.get('gate') or '—'))
    out_lines.append('')

    for key, label in (('invariants', h.get('invariants', 'Invariants')),
                       ('prohibitions', h.get('prohibitions', 'Prohibitions')),
                       ('glossary', h.get('glossary', 'Glossary'))):
        rows = spec.get(key) or []
        out_lines += ['## ' + label, '']
        for r in rows:
            out_lines.append('- `%s` %s' % (r.get('id'), r.get('name') or r.get('term') or ''))
        out_lines.append('')

    out_lines += ['## ' + h.get('open_questions', 'Open questions'), '']
    for it in opens:
        out_lines.append('- `%s` %s' % (it.id, it.title))
    return '\n'.join(out_lines).rstrip('\n') + '\n'


def _prose_label(key, lang):
    pr = (load_contract().get('prose') or {}).get(key) or {}
    return (pr.get('label') or {}).get(lang, key)


def render_readme(contract, lang):
    h, m = L(HEAD, lang), L(MISC, lang)
    docs = contract.get('documents') or {}
    dirs = contract.get('dirs') or {}
    id_spaces = contract.get('id_spaces') or {}

    out_lines = ['# ' + L(TITLE, lang)['readme'], '']

    # ---- map ----
    out_lines += [anchor('section', 'map'), '## ' + h['map'], '']
    root_docs = [(k, d) for k, d in docs.items() if '/' not in d.get('path', '')]
    for key, d in sorted(root_docs, key=lambda kv: kv[1]['path']):
        out_lines.append('- **%s** — %s' % (d['path'], esc(_first_sentence(d.get('note')))))
    for dirname in sorted(dirs):
        if dirname.startswith('_'):
            continue
        out_lines.append('- **%s/** — %s' % (dirname, esc(_first_sentence(dirs[dirname]))))
        entries = [(k, d) for k, d in docs.items() if d.get('path', '').startswith(dirname + '/')]
        for key, d in sorted(entries, key=lambda kv: kv[1]['path']):
            out_lines.append('  - `%s` — %s' % (d['path'], esc(_first_sentence(d.get('note')))))
    out_lines.append('')

    # ---- ownership ----
    out_lines += [anchor('section', 'ownership'), '## ' + h['ownership'], '']
    for key, d in sorted(docs.items(), key=lambda kv: kv[1]['path']):
        if d.get('generated'):
            line = m['owned_generated'].format(source=d['generated'])
        elif d.get('derived_from'):
            line = m['owned_derived'].format(sources=', '.join(d['derived_from']))
        else:
            line = m['owned_authored'].format(audience=d.get('audience', '—'))
        out_lines.append('- **%s** — %s' % (d['path'], line))
    out_lines.append('')

    # ---- idspaces ----
    out_lines += [anchor('section', 'idspaces'), '## ' + h['idspaces'], '']
    for space in sorted(id_spaces):
        info = id_spaces[space]
        out_lines.append('- **%s** — `%s` — %s' % (space, info.get('pattern', ''), info.get('owner', '')))
    out_lines.append('')

    # ---- loop ----
    out_lines += [anchor('section', 'loop'), '## ' + h['loop'], '']
    for i, line in enumerate(m['loop_lines'], 1):
        out_lines.append('%d. %s' % (i, line))
    out_lines.append('')

    return '\n'.join(out_lines).rstrip('\n') + '\n'


# ---------------------------------------------------------------- journal
# Журнал — список, а не таблица. Строка v2-формата ещё читается, чтобы история,
# написанная до перехода, не пропала при первой же пересборке.
JOURNAL_ROW = re.compile(r'^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(.+?)\s*\|\s*$')
JOURNAL_ITEM = re.compile(r'^-\s+\*\*(\d{4}-\d{2}-\d{2})\*\*\s+—\s+(.+?)\s*$')


def split_journal(text):
    """Тело документа и строки журнала: (date, what)."""
    head = None
    for cand in ('## ' + L(HEAD, 'ru')['journal'], '## ' + L(HEAD, 'en')['journal'],
                 anchor('section', 'journal')):
        if cand in text:
            head = cand
            break
    if head is None:
        return text, []
    body, _, jr = text.partition(head)
    rows = []
    for ln in jr.split('\n'):
        m = JOURNAL_ROW.match(ln) or JOURNAL_ITEM.match(ln)
        if m:
            item = (m.group(1), m.group(2).strip())
            # «пересобран из client/*.md» пять раз подряд — это не история,
            # это шум от пяти прогонов. Подряд идущие одинаковые схлопываются.
            if rows and rows[-1][1] == item[1]:
                rows[-1] = item
                continue
            rows.append(item)
    return body, rows


def with_journal(body, rows, lang, date, changed, seed_text):
    m = L(MISC, lang)
    if changed:
        # одна и та же запись подряд ничего не сообщает: пять «пересобран из
        # client/*.md» в живом документе появились ровно так
        if not rows or rows[-1][1] != seed_text:
            rows = rows + [(date, seed_text)]
        else:
            rows = rows[:-1] + [(date, seed_text)]
    if not rows:
        rows = [(date, m['created'])]
    j = ['## ' + L(HEAD, lang)['journal'], '']
    j += ['- **%s** — %s' % (d, w) for d, w in rows]
    return body.rstrip('\n') + '\n\n' + '\n'.join(j) + '\n'


def build_full(doc_key, lang, src, body):
    header = doc_header(doc_key, lang, 1)
    banner = '<!-- macstack:generated from=%s -->' % src
    note = '> ' + L(MISC, lang)['banner_note'].format(src=src)
    return '%s\n%s\n\n%s\n\n%s' % (header, banner, note, body)


# ---------------------------------------------------------------- main
USAGE = '''Использование: render.py [КАТАЛОГ] [--check] [--date ГГГГ-ММ-ДД] [--only ИМЯ]

  КАТАЛОГ   папка macstack (по умолчанию: macstack)
  --check   не писать, а сказать, разошлись ли файлы со спекой (код 1 при расхождении)
  --date    дата для строк журнала вместо сегодняшней
  --only    собрать один документ: architecture | index | requirements | test-cases | readme'''


def main():
    argv = sys.argv[1:]
    check = '--check' in argv
    date, only = None, None
    positional = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--date' and i + 1 < len(argv):
            date = argv[i + 1]; i += 2; continue
        if a == '--only' and i + 1 < len(argv):
            only = argv[i + 1]; i += 2; continue
        if a == '--check':
            i += 1; continue
        if a in ('-h', '--help'):
            print(USAGE); return 0
        # Иначе `--help` попадал в positional и становился КОРНЕМ ПРОЕКТА:
        # скрипт создавал каталог с именем `--help` и писал в него пять
        # документов. Любой флаг, которого мы не знаем, — это опечатка, и
        # молча принимать её за путь дороже, чем отказать.
        if a.startswith('-'):
            sys.stderr.write('render.py: неизвестный флаг %s\n\n%s\n' % (a, USAGE))
            return 2
        positional.append(a); i += 1
    root = positional[0] if positional else 'macstack'
    date = date or datetime.date.today().isoformat()

    lang = doc_lang(root)
    contract = load_contract()
    spec = load_spec(root)
    if not spec and only in (None, 'architecture'):
        out(lang, 'no_spec', dir=root)

    jobs = []
    if only in (None, 'architecture'):
        jobs.append(('architecture', os.path.join('generated', 'ARCHITECTURE.md'), 'macstack.json',
                      render_architecture(spec, lang)))
    if only in (None, 'index'):
        jobs.append(('index', os.path.join('generated', 'INDEX.md'), 'client/*.md',
                      render_index(root, lang)))
    if only in (None, 'requirements'):
        jobs.append(('requirements', os.path.join('generated', 'REQUIREMENTS.md'),
                     'client/*.md', render_requirements(root, lang)))
    if only in (None, 'test_cases'):
        jobs.append(('test_cases', os.path.join('generated', 'TEST-CASES.md'),
                     'client/USER-CASES.md + tests/', render_test_cases(root, lang)))
    if only in (None, 'readme'):
        jobs.append(('readme', 'README.md', 'doc-contracts.json', render_readme(contract, lang)))

    rc = 0
    for key, relpath, src, body in jobs:
        path = os.path.join(root, relpath)
        full = build_full(key, lang, src, body)

        old = ''
        if os.path.exists(path):
            with io.open(path, encoding='utf-8') as f:
                old = f.read()
        old_body, old_rows = split_journal(old)
        changed = old_body.rstrip('\n') != full.rstrip('\n')
        seed_text = L(MISC, lang)['rebuilt'].format(src=src)
        new = with_journal(full, old_rows, lang, date, changed or not old, seed_text)

        if check:
            if old != new:
                rc = 1
                out(lang, 'drift', path=path)
                print('  ' + msg(lang, 'drift_hint'))
                for ln in list(difflib.unified_diff(old.split('\n'), new.split('\n'),
                                                      'disk', 'spec', lineterm=''))[:12]:
                    print('   ' + ln)
            else:
                out(lang, 'in_sync', path=path)
        else:
            os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
            if old != new:
                with io.open(path, 'w', encoding='utf-8') as f:
                    f.write(new)
                out(lang, 'wrote', path=path)
            else:
                out(lang, 'unchanged', path=path)
    return rc


if __name__ == '__main__':
    sys.exit(main())
