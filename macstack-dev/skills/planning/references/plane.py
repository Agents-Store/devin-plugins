#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TASKS.md <-> the team's tracker, in both directions, without picking a winner.

This script does not talk to Plane. It has no credentials and should not have any:
the session already holds an authenticated MCP connection, and a plugin that carried
its own token would be a second place for that token to leak from.

So it does the half a program can do — read both sides, decide what differs, and emit
an action list — and the `planning` skill executes it with `mcp__plane__workitem`.
Reading the tracker back in is the same shape: the caller passes what the tracker said
via `--tracker <file>`, and this compares.

The join is `external_id`: the task's own id (`M15-T2`) with `external_source`
`macstack`. Nothing stores a Plane UUID in the markdown — a uuid in a document is a
number nobody can check by eye, and it rots the first time a project is re-created.

    plane.py <macstack-dir> --plan                     what to send
    plane.py <macstack-dir> --plan --tracker t.json    what to send AND what disagrees

Status vocabulary is Plane's, deliberately: backlog · todo · in_progress · done ·
cancelled. Two vocabularies for two systems is two opinions about whether the work is
finished.
"""
import io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', '..', 'documents', 'references')))
import v3                                                          # noqa: E402

STATES = ('backlog', 'todo', 'in_progress', 'done', 'cancelled')
TASK_ID = re.compile(r'^M\d+(-T\d+)?$')
SOURCE = 'macstack'


def binding(root):
    """`.plane.json` sits in the PROJECT root, one level above macstack/."""
    for p in (os.path.join(root, '..', '.plane.json'),
              os.path.join(root, '.plane.json')):
        if os.path.exists(p):
            return json.load(io.open(p, encoding='utf-8'))
    return {}


def read_tasks(root):
    """-> [{id, title, status, closes, tracker, body}] from history/TASKS.md."""
    p = os.path.join(root, 'history', 'TASKS.md')
    if not os.path.exists(p):
        return []
    doc = v3.load_doc(p)
    out = []
    for it in doc.items:
        if it.level < 3 or not it.id or not TASK_ID.match(it.id):
            continue
        if '-T' not in it.id:
            continue                       # веха, не задача
        a, b = it.span
        out.append({
            'id': it.id, 'title': it.title,
            'status': (it.get('status') or '').strip().lower() or 'backlog',
            'closes': it.get('closes') or it.get('covers'),
            'tracker': it.get('tracker'),
            'priority': it.get('priority'),
            'body': '\n'.join(doc.lines[a:b]).strip(),
            'line': (it.head_line or 0) + 1})
    return out


def summary(task):
    """Что уезжает в трекер: суть и указатель на файл, а не весь текст задачи.

    Файл — источник правды о том, ЧТО за работа; трекер — место, где о ней идёт
    разговор. Гнать туда полное описание значит держать две копии одного текста и
    расходиться на первой же правке. Сводка выводится ДЕТЕРМИНИРОВАННО из того же
    файла, поэтому сравнение стабильно: иначе синк докладывал бы «обновить всё»
    на каждом прогоне, а правило, которое всегда красное, никто не читает.
    """
    body = task.get('body') or ''
    what = re.search(r'\*\*(?:Что сделать|What to do)\.\*\*\s*(.*?)(?=\n\n\*\*|\Z)',
                     body, re.S)
    first = ''
    if what:
        first = re.split(r'(?<=[.;])\s', re.sub(r'\s+', ' ', what.group(1)).strip())[0]
    closes = task.get('closes') or '—'
    if isinstance(closes, (list, tuple)):
        closes = ', '.join(closes)
    return ('Закрывает кейс %s. %s\n\nПолное описание — macstack/history/TASKS.md, задача %s.'
            % (closes, first[:400], task['id']))


def plan(root, tracker=None):
    """-> {'create': [...], 'update': [...], 'conflict': [...], 'binding': {...}}."""
    tasks = read_tasks(root)
    known = {}
    for w in (tracker or []):
        ext = (w.get('external_id') or '').strip()
        if ext and (w.get('external_source') or SOURCE) == SOURCE:
            known[ext] = w
    create, update, conflict = [], [], []
    for t in tasks:
        if t['status'] not in STATES:
            conflict.append({'task': t['id'], 'why': 'status %r is not one of %s'
                             % (t['status'], ', '.join(STATES))})
            continue
        w = known.get(t['id'])
        payload = {'external_id': t['id'], 'external_source': SOURCE,
                   'name': '%s · %s' % (t['id'], t['title']),
                   'description_stripped': summary(t),
                   'state': t['status']}
        if w is None:
            create.append(payload)
            continue
        theirs = (w.get('state_name') or w.get('state') or '').strip().lower().replace(' ', '_')
        if theirs and theirs != t['status']:
            # Обе стороны имеют право быть правой: файл знает, что за работа,
            # трекер — что с ней происходит. Автоматический выбор победителя
            # молча теряет одну из двух правд, поэтому здесь остановка.
            conflict.append({'task': t['id'], 'document': t['status'], 'tracker': theirs,
                             'why': 'the two disagree about whether this is done'})
            continue
        # сравниваем только имя: описание в трекере ведёт человек, и перезаписывать
        # его на каждом прогоне значит стирать разговор, ради которого трекер и есть
        if (w.get('name') or '') != payload['name']:
            update.append(dict(payload, workitem_id=w.get('id')))
    orphan = [ext for ext in known if ext not in {t['id'] for t in tasks}]
    return {'binding': binding(root), 'create': create, 'update': update,
            'conflict': conflict, 'orphan': orphan, 'tasks': len(tasks)}


def main():
    argv = sys.argv[1:]
    pos = [a for a in argv if not a.startswith('--')]
    root = pos[0] if pos else 'macstack'
    tr = None
    if '--tracker' in argv:
        i = argv.index('--tracker')
        if i + 1 < len(argv):
            tr = json.load(io.open(argv[i + 1], encoding='utf-8'))
            tr = tr.get('results', tr) if isinstance(tr, dict) else tr
    res = plan(root, tr)
    if '--json' in argv:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 1 if res['conflict'] else 0
    b = res['binding']
    print('проект: %s · %s' % (b.get('identifier') or '—', b.get('baseUrl') or 'нет .plane.json'))
    print('задач в файле: %d' % res['tasks'])
    print('  завести  : %d  %s' % (len(res['create']), ', '.join(c['external_id'] for c in res['create'][:8])))
    print('  обновить : %d  %s' % (len(res['update']), ', '.join(c['external_id'] for c in res['update'][:8])))
    print('  в трекере, но не в файле: %d  %s' % (len(res['orphan']), ', '.join(res['orphan'][:8])))
    for c in res['conflict']:
        print('  РАСХОЖДЕНИЕ %s: %s' % (c['task'], c.get('why')))
    if not (tr is not None):
        print('\nтрекер не прочитан — это только то, что файл предлагает отправить.')
        print('Передайте выгрузку `workitem list` через --tracker, чтобы увидеть расхождения.')
    return 1 if res['conflict'] else 0


if __name__ == '__main__':
    sys.exit(main())
