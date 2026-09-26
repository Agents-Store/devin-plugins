# -*- coding: utf-8 -*-
"""Перевод проекта со старой формы id на новую: `C-14` → `CC-14`, `A27` → `QA27`.

## Зачем

Старая форма не говорила, в каком файле искать запись, и переиспользовала буквы:
`T-19` был кейсом тренинг-центра, а `T` в `M15-T11` — задачей. Владелец проекта
читал код и не мог по нему понять ни файла, ни вида записи.

Новая форма ставит букву файла впереди: `C` — case (`client/USER-CASES.md`),
`Q` — question (`client/OPEN-QUESTIONS.md`). Вторая буква остаётся прежней и
означает то же, что раньше: роль у кейса, адресата у вопроса.

## Почему слепой regex здесь НЕЛЬЗЯ

`^[A-Z]-\\d{2}$` matches не только наши кейсы. В живом проекте по этой же форме
записаны id ЧУЖОГО документа — немецкого технического задания заказчика
(`E-05`, `A-08`, `NF-07`). Переименовав их, мы бы порвали ссылку на бумагу,
которой не владеем, и сделали это молча.

Поэтому скрипт **сначала читает объявления** — заголовки в `USER-CASES.md` и
`OPEN-QUESTIONS.md`, — и переименовывает ровно те id, которые там объявлены.
Всё остальное, даже совпадающее по форме, не трогается.

## Что не трогается никогда

`inbox/` и `history/handoffs/` — материал заказчика и уже отправленные ему
пакеты. Оба неизменяемы по устройству macstack: пакет, отданный клиенту, несёт
те id, которые клиент прочитал, и переписать их задним числом значит рассинхронить
его копию с нашей без единого следа.

## Как запускать

    python3 migrate_ids.py <корень проекта>            # показать, ничего не менять
    python3 migrate_ids.py <корень проекта> --apply     # переписать

Второй запуск идемпотентен: `CC-14` под старый шаблон уже не подходит.
"""
from __future__ import print_function

import io
import os
import re
import sys

MACSTACK = 'macstack'
# Имена КАТАЛОГОВ, в которые не заходим. Сравниваются как компоненты пути на
# любой глубине, а не как префикс от корня: неизменяемое лежит внутри
# `macstack/`, и сравнение с началом пути молча пропускало бы его.
NEVER_DIRS = ('inbox', 'handoffs', 'node_modules', '.git', '.next', 'dist',
              'build', 'coverage', '.turbo', '.claude', '.codex', '.venv',
              '__pycache__')
EXT = ('.md', '.json', '.jsonl', '.ts', '.tsx', '.js', '.jsx', '.html')

CASE_HEADING = re.compile(r'^#{2,6}\s+~*([A-Z]-[0-9]{2})~*\s*[·.]', re.M)
OPEN_HEADING = re.compile(r'^#{2,6}\s+~*([AB][0-9]+)~*\s*[·.—-]', re.M)
# Те же заголовки, уже переведённые. Нужны для ДОГОНЯЮЩЕГО прохода по папкам,
# которые обычный прогон не трогает: к этому моменту client/ уже в новой форме,
# и старую форму больше неоткуда прочитать.
CASE_DONE = re.compile(r'^#{2,6}\s+~*C([A-Z]-[0-9]{2})~*\s*[·.]', re.M)
OPEN_DONE = re.compile(r'^#{2,6}\s+~*Q([AB][0-9]+)~*\s*[·.—-]', re.M)


def declared(root):
    """-> (кейсы, открытые вопросы) — ровно те id, что ОБЪЯВЛЕНЫ заголовками."""
    def read(rel):
        p = os.path.join(root, MACSTACK, rel)
        if not os.path.exists(p):
            return ''
        return io.open(p, encoding='utf-8', errors='replace').read()

    uc = read(os.path.join('client', 'USER-CASES.md'))
    oq = read(os.path.join('client', 'OPEN-QUESTIONS.md'))
    cases = set(CASE_HEADING.findall(uc)) or set(CASE_DONE.findall(uc))
    opens = set(OPEN_HEADING.findall(oq)) or set(OPEN_DONE.findall(oq))
    return cases, opens


def rename_map(cases, opens):
    """-> (везде, только-в-macstack) — два набора, и разделение НЕ косметическое.

    Кейс несёт дефис (`C-14`, `T-19`). Форма достаточно своеобразная, чтобы
    встречаться только там, где её и написали, поэтому кейсы переименовываются во
    всём дереве — включая названия тестов и комментарии в коде, которые обязаны
    остаться ссылками на существующую запись.

    Открытый пункт — голая буква с цифрами (`A4`, `B3`), и вот это вне `macstack/`
    значит совсем другое. Измерено на живом проекте:

        src/pdf/InvoiceDocument.tsx:441   <Page size="A4" …>
        tests/int/helpers/pdf-text.ts:189 export const A4 = { width: 595.28, … }

    Первое — размер страницы выпущенного счёта, второе — экспортируемая
    константа, на которую ссылаются четыре теста. Переименование любого из них
    ломает генерацию PDF молча: тип не возражает, строка просто перестаёт быть
    известным Playwright'у форматом. Поэтому открытые пункты правятся только
    внутри `macstack/`, где `A4` не значит ничего, кроме вопроса заказчику.
    """
    everywhere = dict((cid, 'C' + cid) for cid in cases)
    macstack_only = dict((oid, 'Q' + oid) for oid in opens)
    return everywhere, macstack_only


def walkable(root, sent=False):
    for base, dirs, files in os.walk(root):
        parts = os.path.relpath(base, root).split(os.sep)
        blocked = NEVER_DIRS if not sent else tuple(
            d for d in NEVER_DIRS if d not in ('inbox', 'handoffs'))
        if any(part in blocked for part in parts):
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs
                   if d not in blocked
                   and not os.path.exists(os.path.join(base, d, '.git'))]
        for f in files:
            if f.endswith(EXT):
                yield os.path.join(base, f)


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith('-')]
    apply_ = '--apply' in sys.argv[1:]
    # `history/handoffs/` и `inbox/` по умолчанию неприкосновенны: первое — копии
    # того, что заказчик УЖЕ прочитал, второе — его собственные слова. Переписать
    # их значит утверждать, что мы отправили не то, что отправили. Открывается
    # только явным флагом и только решением владельца — у него могут быть свои
    # причины предпочесть единый код по всему дереву расхождению с архивом.
    sent = '--include-sent' in sys.argv[1:]
    if any(a in ('-h', '--help') for a in sys.argv[1:]) or not argv:
        print(__doc__)
        return 0
    root = argv[0]

    docs = [os.path.join(root, MACSTACK, 'client', n)
            for n in ('USER-CASES.md', 'OPEN-QUESTIONS.md')]
    if not any(os.path.exists(d) for d in docs):
        print('в %s нет ни USER-CASES.md, ни OPEN-QUESTIONS.md — это не проект macstack' % root)
        return 1

    cases, opens = declared(root)
    if not cases and not opens:
        # Документы на месте, но ни одного id СТАРОЙ формы в заголовках. Это
        # нормальный исход второго запуска, а не отказ: код возврата 1 здесь
        # выглядел бы в скрипте вызывающего как сломанная миграция.
        print('старой формы id в заголовках нет — проект уже переведён, делать нечего')
        return 0
    everywhere, macstack_only = rename_map(cases, opens)

    def build(mapping):
        if not mapping:
            return None
        # Длинные сначала — защита сверх `\b`, а не вместо неё.
        keys = sorted(mapping, key=len, reverse=True)
        return re.compile(r'\b(' + '|'.join(re.escape(k) for k in keys) + r')\b')

    re_all = build(everywhere)
    re_ms = build(dict(everywhere, **macstack_only))

    # `roles[].cases` в macstack.json — это ШАБЛОНЫ (`C-*`), а не id, и под
    # регулярку по id они не подпадают. Без этой правки линт после миграции
    # сообщает «кейсы C-* не принадлежат ни одной роли» и «glob 'C-*' не
    # совпадает ни с одним заголовком» — то есть роль теряет свои кейсы.
    letters = sorted({cid.split('-', 1)[0][-1] for cid in cases})
    re_glob = (re.compile(r'\b(' + '|'.join(letters) + r')-\*')
               if letters else None)

    print('объявлено кейсов: %d, вопросов: %d' % (len(cases), len(opens)))
    print('кейсы правятся везде; вопросы — только внутри %s/ (вне её A4 это размер страницы)'
          % MACSTACK)
    ms_root = os.path.join(os.path.abspath(root), MACSTACK)
    touched, total = 0, 0
    for path in walkable(root, sent):
        inside = os.path.abspath(path).startswith(ms_root + os.sep)
        rx = re_ms if inside else re_all
        mapping = dict(everywhere, **macstack_only) if inside else everywhere
        if rx is None:
            continue
        try:
            text = io.open(path, encoding='utf-8', errors='replace').read()
        except IOError:
            continue
        new, n = rx.subn(lambda m: mapping[m.group(1)], text)
        if inside and re_glob is not None:
            new, g = re_glob.subn(lambda m: 'C' + m.group(1) + '-*', new)
            n += g
        if n:
            touched += 1
            total += n
            print('%5d  %s' % (n, os.path.relpath(path, root)))
            if apply_:
                with io.open(path, 'w', encoding='utf-8') as f:
                    f.write(new)

    print('\nфайлов: %d, замен: %d' % (touched, total))
    if total == 0:
        # Ноль замен при НЕПУСТОЙ карте — нормальный исход повторного запуска, а
        # не отказ. Раньше это ловилось пустой картой, но карта теперь строится и
        # из новой формы (для догоняющего прохода), поэтому сигналом стал нуль.
        print('старой формы не осталось — проект уже переведён, делать нечего')
        return 0
    if not apply_:
        print('это показ. чтобы переписать — добавьте --apply')
    else:
        print('переписано. дальше: пересобрать generated/ и прогнать линт')
    return 0


if __name__ == '__main__':
    sys.exit(main())
