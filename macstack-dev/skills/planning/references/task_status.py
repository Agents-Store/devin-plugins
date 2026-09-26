#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Статус задачи против вердикта аудита — недостающее звено обратной связи.

`conformance` пишет в журнал вердикт на КЕЙС: сделано, частично, отсутствует.
`TASKS.md` держит статус на ЗАДАЧЕ. Связь между ними — буллет «Закрывает» — до сих
пор читалась ровно в одну сторону: `uncovered.py` спрашивал «у этого кейса есть
задача?», чтобы не предлагать работу дважды. Обратного вопроса — «эта задача ещё
актуальна?» — не задавал никто, и оба его следствия молчаливые:

  * задача висит `todo`, хотя код давно делает обещанное. Список работ показывает
    объём, которого нет, и человек планирует уже сделанное;
  * задача стоит `done`, хотя аудит нашёл `absent`. Это хуже первого: список работ
    выглядит короче правды, и никто не ищет то, что считается закрытым.

Отсюда обе стороны, а не одна. Закрывать по вердикту без переоткрытия — значит
построить храповик, который умеет только уменьшать список работ.

## Правило свежести: доказательство новее заявления

Вердикт применяется, только если он ДАТИРОВАН ПОЗЖЕ самой свежей собственной даты
задачи (`Заведена`/`Взята`/`Закрыта`). Иначе аудит, прогнанный до работы, каждый
следующий запуск переоткрывал бы задачу, закрытую после него, — и скрипт спорил бы
с человеком, у которого больше сведений. Это то же различение, что `reviewed` и
`updated` у документов: дата проверки и дата изменения — разные утверждения.

## Задача, закрывающая несколько кейсов

`done` — только если КАЖДЫЙ названный кейс `implemented`. Переоткрытие — если ХОТЯ
БЫ ОДИН `absent` или `partial`. Оба правила консервативны в одну и ту же сторону:
не считать сделанным то, про что это не доказано.

## Словарь статусов

Берётся из контракта (`fields.status.enum`) — того же места, по которому судит
правило линтера 12.14. Захардкоженный список разошёлся бы с ним молча, и скрипт
писал бы статус, который линтер тут же назовёт ошибкой. Карту
`documents.tasks.statuses` не читает никто, и её токены (`doing`, `blocked`)
правило 12.14 как раз отвергает — поэтому она здесь не источник.

Usage: task_status.py <macstack-dir> [--apply] [--json]
       выход 1, если есть расхождения (без --apply), 0 если применено или чисто
"""
import sys, os, io, json, re, datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(_HERE, '..', '..', 'documents',
                                                 'references')))
import v3                                                      # noqa: E402
import ledger as _L                                            # noqa: E402

CONTRACT = os.path.normpath(os.path.join(_HERE, '..', '..', 'documents',
                                         'references', 'doc-contracts.json'))
TASK_ID = re.compile(r'^M\d+-T\d+$')
CASE_ID = re.compile(r'\b(C?[A-Z]-\d{2})\b')
DATE = re.compile(r'(\d{4})-(\d{2})-(\d{2})')

# Вердикт -> в какой статус он переводит задачу. Значения проверяются по enum
# контракта перед употреблением: если проект переименует статус, скрипт откажется
# писать, а не запишет несуществующий токен.
FROM_VERDICT = {
    'implemented': 'done',
    'absent': 'todo',
    'partial': 'in_progress',
    # `externally-blocked` намеренно НЕ переоткрывает: код закончен, мешает
    # внешнее — кредитив, ответ клиента, чужой аккаунт. Переоткрытая задача
    # вернула бы в очередь работу, которую взявший её не сможет доделать.
}
NEVER_TOUCH = ('cancelled', 'dropped', 'backlog')


def _contract():
    return json.load(io.open(CONTRACT, encoding='utf-8'))


def _date(value):
    m = DATE.search(str(value or ''))
    if not m:
        return None
    try:
        return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def newest_verdicts(root):
    """{case_id: (вердикт, дата, доказательство)} — по свежайшей строке `audit`."""
    out = {}
    for r in _L.read(root):
        if r.get('kind') != 'audit' or not r.get('item') or not r.get('now'):
            continue
        d = _date(r.get('date'))
        if d is None:
            continue
        prev = out.get(r['item'])
        if prev is None or d >= prev[1]:
            out[r['item']] = (str(r['now']).strip().lower(), d, r.get('why') or '')
    return out


def task_claim_date(item):
    """Самая свежая собственная дата задачи, или None.

    Это «когда про эту задачу в последний раз что-то утверждали». Вердикт старше
    её — сведения, устаревшие относительно заявления, и действовать по ним нельзя.
    """
    best = None
    for key in ('finished', 'started', 'opened'):
        d = _date(item.get(key))
        if d and (best is None or d > best):
            best = d
    return best


def cases_of(item):
    """Кейсы, которые задача закрывает. `closes` — буллет «Закрывает»."""
    raw = item.get('closes')
    if isinstance(raw, (list, tuple)):
        raw = ' '.join(str(x) for x in raw)
    return sorted(set(CASE_ID.findall(str(raw or ''))))


def decide(status, cases, verdicts, claim):
    """-> (новый_статус | None, причина, доказательство).

    None означает «не трогать», и причина объясняет почему — молчаливое
    бездействие неотличимо от «расхождений нет», а это разные вещи.
    """
    status = (status or '').strip().lower()
    if status in NEVER_TOUCH:
        return None, 'status %s is a decision, not a measurement' % status, ''
    if not cases:
        return None, 'closes no case — nothing to measure it against', ''

    seen = [(c, verdicts[c]) for c in cases if c in verdicts]
    if not seen:
        return None, 'no audit verdict for %s' % ', '.join(cases), ''

    # Доказательство должно быть новее заявления.
    fresh = [(c, v) for c, v in seen if claim is None or v[1] > claim]
    if not fresh:
        newest = max(v[1] for _, v in seen)
        return None, ('verdict %s is older than the task\'s own %s — stale evidence'
                      % (newest.isoformat(), claim.isoformat() if claim else '?')), ''

    why = '; '.join('%s=%s%s' % (c, v[0], (' (%s)' % v[2]) if v[2] else '')
                    for c, v in fresh)

    bad = [(c, v) for c, v in fresh if v[0] in ('absent', 'partial')]
    if bad and status == 'done':
        # Переоткрытие. `absent` сильнее `partial`: если хоть один кейс не
        # построен вовсе, задача не «в работе», она не начата по этому кейсу.
        want = 'todo' if any(v[0] == 'absent' for _, v in bad) else 'in_progress'
        return want, 'audit found %s' % ', '.join('%s %s' % (c, v[0]) for c, v in bad), why

    if status != 'done' and all(v[0] == 'implemented' for _, v in fresh) \
            and len(fresh) == len(cases):
        return 'done', 'every case it closes is confirmed implemented', why

    return None, 'status %s agrees with the verdicts' % (status or '—'), why


def run(root, apply=False):
    contract = _contract()
    allowed = set((contract.get('fields') or {}).get('status', {}).get('enum') or [])
    tasks_p = os.path.join(root, 'history', 'TASKS.md')
    if not os.path.exists(tasks_p):
        return {'error': 'missing: %s' % tasks_p}

    # Язык берётся из ЗАГОЛОВКА документа (`lang=` в первой строке), а не из
    # `docs.language` проекта. Схема разрешает язык на документ
    # (`docs.files.<key>.language`), поэтому проект на английском законно держит
    # русский TASKS.md — и читатель, доверившийся проектной настройке, разберёт
    # русские метки английской таблицей и увидит документ БЕЗ ЕДИНОГО ПОЛЯ. Не
    # ошибка, не исключение: ноль задач, то есть «двигать нечего».
    doc = v3.load_doc(tasks_p)
    items = [i for i in doc.items if i.id and TASK_ID.match(i.id)]
    if not items:
        # v2 (`<!-- macstack:task= -->` + блок yaml) читается `uncovered.py`, но
        # писателя у него нет. Тихо ничего не сделать здесь нельзя: отчёт «0
        # расхождений» на непрочитанном файле — это ложь, а не чистый прогон.
        return {'error': 'no v3 tasks in %s — migrate it first '
                         '(/macstack-dev:start --migrate), then re-run' % tasks_p}

    verdicts = newest_verdicts(root)
    moves, held = [], []
    for it in items:
        cases = cases_of(it)
        was = str(it.get('status') or '').strip().lower()
        want, why, evidence = decide(was, cases, verdicts, task_claim_date(it))
        if want is None:
            held.append({'task': it.id, 'status': was, 'cases': cases, 'why': why})
            continue
        if want not in allowed:
            held.append({'task': it.id, 'status': was, 'cases': cases,
                         'why': 'would need status %r, which the contract does not '
                                'allow (%s)' % (want, ', '.join(sorted(allowed)))})
            continue
        moves.append({'task': it.id, 'was': was, 'now': want, 'cases': cases,
                      'why': why, 'evidence': evidence, 'item': it})

    if apply and moves:
        today = datetime.date.today().isoformat()
        rows = []
        for m in moves:
            it = m['item']
            v3.set_field(doc, it, 'status', m['now'])
            # Дата закрытия — часть утверждения «сделано»; без неё следующий
            # прогон не сможет отличить свежее доказательство от старого.
            if m['now'] == 'done':
                v3.set_field(doc, it, 'finished', today)
            rows.append({'date': today, 'doc': 'history/TASKS.md', 'item': m['task'],
                         'kind': 'changed', 'was': m['was'], 'now': m['now'],
                         'why': '%s — %s' % (m['why'], m['evidence']) if m['evidence']
                                else m['why'],
                         'source': 'task_status', 'by': 'claude'})
        v3.save(doc)
        _L.append(root, rows)

    for m in moves:
        m.pop('item', None)
    return {'moves': moves, 'held': held, 'applied': bool(apply and moves),
            'tasks': len(items), 'verdicts': len(verdicts)}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    root = args[0] if args else 'macstack'
    apply = '--apply' in sys.argv
    res = run(root, apply)

    if '--json' in sys.argv:
        print(json.dumps(res, ensure_ascii=False, indent=1, sort_keys=True))
        return 1 if res.get('error') or (res.get('moves') and not apply) else 0

    if res.get('error'):
        print(res['error'])
        return 2
    moves, held = res['moves'], res['held']
    print('задач: %d · кейсов с вердиктом: %d' % (res['tasks'], res['verdicts']))
    if not moves:
        print('статусы согласны с вердиктами — двигать нечего')
    for m in moves:
        arrow = 'ЗАКРЫТЬ ' if m['now'] == 'done' else 'ПЕРЕОТКРЫТЬ'
        print('  %s %-10s %s -> %s   %s' % (arrow, m['task'], m['was'] or '—',
                                            m['now'], m['why']))
        if m['evidence']:
            print('              %s' % m['evidence'])
    # Причины бездействия печатаются только те, что означают недостаток сведений:
    # «согласен с вердиктом» — это норма, и в списке она была бы шумом, за
    # которым потерялось бы «вердикта нет вовсе».
    quiet = [h for h in held if 'agrees with' not in h['why']]
    if quiet:
        print('\nне двигали (%d):' % len(quiet))
        for h in quiet:
            print('  %-10s %-12s %s' % (h['task'], h['status'] or '—', h['why']))
    if res['applied']:
        print('\nприменено: %d, каждое — строкой в журнале' % len(moves))
        return 0
    if moves:
        print('\n--apply запишет их в TASKS.md и в журнал')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
