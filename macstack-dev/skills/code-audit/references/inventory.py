#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Перечислить, что есть в коде — по конвенциям, которые объявила спека.

Это НЕ парсер Payload и не парсер Next.js. Плагин технологический: он не имеет
права знать один стек лучше другого. Что он знает — это `software[].category` из
`macstack.json` и таблицу конвенций для категорий. Спека называет стек, таблица
говорит, где у такого стека лежат сущности, экраны, задания и права.

И он ничего не решает. Каждая строка на выходе — КАНДИДАТ: файл, вид, имя, путь.
Сопоставляет их с документами агент, потому что «коллекция Sessions — это entity
session или часть entity einsatz» — вопрос предметный, а не файловый.

Правило, которое здесь дороже остальных: **выдуманный id хуже пустого поля.**
Пустое поле видно и его спросят. Выдуманный id пройдёт вниз по течению, и каждая
проверка на нём отчитается зелёным.

Использование:
    inventory.py <project-dir> [--json] [--kind entity] [--macstack macstack]

Выход: 0 — перечислено; 2 — не удалось запуститься.
"""
import glob as _glob
import io
import json
import os
import re
import sys

# ------------------------------------------------------------------ конвенции
# Ключ — 'category' или 'category:software-id'. Более точный побеждает.
# `glob` — от корня проекта. `id_from` — как получить имя кандидата:
#   stem  — имя файла без расширения
#   slug  — поле slug: '...' внутри файла, иначе stem
#   route — путь как URL: src/app/(group)/coach/today/page.tsx -> /coach/today
PROBES = {
    'cms:payload': [
        ('entity',      'src/collections/*.ts',        'slug'),
        ('entity',      'src/globals/*.ts',            'slug'),
        ('job',         'src/jobs/*.ts',               'stem'),
        ('workflow',    'src/workflows/*.ts',          'stem'),
        ('access',      'src/access/*.ts',             'stem'),
        ('hook',        'src/hooks/**/*.ts',           'stem'),
        ('endpoint',    'src/endpoints/**/*.ts',       'stem'),
    ],
    'cms': [
        ('entity',      'src/collections/*.*',         'slug'),
    ],
    'frontend-frameworks:nextjs': [
        ('interface',   'src/app/**/page.tsx',         'route'),
        ('endpoint',    'src/app/**/route.ts',         'route'),
        ('action',      'src/actions/**/*.ts',         'stem'),
    ],
    'frontend-frameworks': [
        ('interface',   'src/pages/**/*.vue',          'stem'),
        ('interface',   'src/routes/**/+page.svelte',  'route'),
    ],
    'databases': [
        ('migration',   'src/migrations/*.*',          'stem'),
        ('migration',   'migrations/*.*',              'stem'),
    ],
    'communication': [
        ('notification', 'src/notifications/**/*.*',   'stem'),
        ('notification', 'src/email/**/*.*',           'stem'),
    ],
    'automation': [
        ('workflow',    'src/workflows/**/*.*',        'stem'),
    ],
}

SLUG = re.compile(r"""^\s*slug\s*:\s*(['"])(.+?)\1""", re.M)
SKIP_DIRS = ('node_modules', '.next', 'dist', 'build', '.git', 'coverage')


def _probes_for(software):
    """Пробы, применимые к этому стеку. Точная вытесняет общую.

    'cms:payload' описывает Payload точнее, чем 'cms'. Если есть точная, общую
    для того же софта брать НЕ надо: она ничего не добавит, зато её пустые пробы
    напечатают три предупреждения о том, что в Next.js-проекте нет файлов Vue.
    Предупреждение, которое всегда ложно, учит не читать предупреждения.
    """
    keys, seen = [], set()
    for s in software:
        cat, sid = s.get('category') or '', s.get('id') or ''
        exact = '%s:%s' % (cat, sid)
        for k in ((exact,) if exact in PROBES else (cat,)):
            if k in PROBES and k not in seen:
                seen.add(k)
                keys.append((k, sid))
    return keys


def _route_of(path):
    """src/app/(payload)/api/health/route.ts -> /api/health

    Скобочные сегменты — группировка Next.js, в URL их нет. Динамические
    сегменты остаются как есть: `[id]` в маршруте — часть его имени, и
    подставлять туда что-нибудь значило бы выдумать.
    """
    p = path.replace(os.sep, '/')
    for root in ('src/app/', 'app/', 'src/routes/', 'routes/'):
        if p.startswith(root):
            p = p[len(root):]
            break
    p = re.sub(r'/(page|route|\+page)\.[a-z]+$', '', p)
    parts = [x for x in p.split('/') if x and not (x.startswith('(') and x.endswith(')'))]
    return '/' + '/'.join(parts) if parts else '/'


def _name_of(path, how, root):
    full = os.path.join(root, path)
    if how == 'route':
        return _route_of(path)
    if how == 'slug':
        try:
            m = SLUG.search(io.open(full, encoding='utf-8', errors='replace').read(200000))
            if m:
                return m.group(2)
        except IOError:
            pass
    return os.path.splitext(os.path.basename(path))[0]


def _iglob(root, pattern):
    out = []
    for p in _glob.glob(os.path.join(root, pattern), recursive=True):
        rel = os.path.relpath(p, root).replace(os.sep, '/')
        if any(('/' + d + '/') in ('/' + rel) for d in SKIP_DIRS):
            continue
        if os.path.isfile(p):
            out.append(rel)
    return sorted(set(out))


def collect(root, mac='macstack'):
    specp = os.path.join(root, mac, 'macstack.json')
    if not os.path.exists(specp):
        return None, ['нет %s — перечислять не по чему: конвенции берутся из '
                      'software[].category, а не угадываются по дереву файлов' % specp]
    spec = json.load(io.open(specp, encoding='utf-8'))
    software = spec.get('software') or []
    if not software:
        return None, ['macstack.json не объявляет ни одного software[] — '
                      'какие конвенции применять, сказать нечем']

    keys = _probes_for(software)
    notes, cands, seen = [], [], set()
    empty = {}          # (key, kind) -> список шаблонов, не давших ничего
    filled = set()      # (key, kind), где хоть один шаблон сработал
    for key, sid in keys:
        for kind, pattern, how in PROBES[key]:
            hits = _iglob(root, pattern)
            if not hits:
                empty.setdefault((key, kind, sid), []).append(pattern)
                continue
            filled.add((key, kind))
            for rel in hits:
                if rel in seen:
                    continue
                seen.add(rel)
                cands.append({'kind': kind, 'name': _name_of(rel, how, root),
                              'path': rel, 'by': key})
    # Громко — но только когда пусты ВСЕ шаблоны этого вида. Один и тот же вид
    # часто лежит в одном из нескольких мест (`migrations/` или `src/migrations/`),
    # и жаловаться на невыбранное место значит печатать шум.
    #
    # Когда пусто действительно всё — это либо конвенция мимо, либо кода нет, и
    # молчать нельзя: молчаливый ноль неотличим от «проверили, всё на месте».
    # Тот самый дефект, ради которого в линтере живёт правило 12.0.
    for (key, kind, sid), pats in sorted(empty.items()):
        if (key, kind) in filled:
            continue
        notes.append('ничего не найдено: %s (стек объявляет %s) — искали в %s'
                     % (kind, sid or key, ', '.join(pats)))
    if not keys:
        notes.append('ни одна конвенция не подошла к объявленному стеку: %s. '
                     'Добавьте пробу в PROBES или назовите категорию точнее.'
                     % ', '.join('%s/%s' % (s.get('id'), s.get('category'))
                                 for s in software))
    return {'root': os.path.abspath(root), 'software': [s.get('id') for s in software],
            'candidates': cands, 'notes': notes}, []


def main():
    argv = sys.argv[1:]
    flags = {a[2:].split('=')[0]: (a.split('=', 1)[1] if '=' in a else True)
             for a in argv if a.startswith('--')}
    args = [a for a in argv if not a.startswith('--')]
    root = args[0] if args else '.'
    if not os.path.isdir(root):
        sys.stderr.write('нет папки %s\n' % root)
        return 2
    data, errs = collect(root, flags.get('macstack') or 'macstack')
    if errs:
        for e in errs:
            sys.stderr.write(e + '\n')
        return 2
    if flags.get('kind'):
        data['candidates'] = [c for c in data['candidates'] if c['kind'] == flags['kind']]
    if flags.get('json'):
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    by = {}
    for c in data['candidates']:
        by.setdefault(c['kind'], []).append(c)
    print('%s  ·  стек: %s' % (data['root'], ', '.join(data['software'])))
    print('')
    for kind in sorted(by, key=lambda k: -len(by[k])):
        items = by[kind]
        print('%-12s %3d' % (kind, len(items)))
        for c in items[:8]:
            print('    %-28s %s' % (c['name'][:28], c['path']))
        if len(items) > 8:
            print('    … ещё %d' % (len(items) - 8))
        print('')
    for n in data['notes']:
        print('  ! ' + n)
    print('всего кандидатов: %d' % len(data['candidates']))
    print('')
    print('Это кандидаты, не выводы. Сопоставьте их с документами:')
    print('  нет в документах · нет в коде · противоречит')
    return 0


if __name__ == '__main__':
    sys.exit(main())
