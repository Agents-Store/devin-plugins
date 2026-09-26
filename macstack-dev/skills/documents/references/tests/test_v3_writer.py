#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The three properties that define the v3 writer, plus the two regressions
the cardinality census exists to hold.

Run: python3 skills/documents/references/tests/test_v3_writer.py

Why unittest and not pytest: this plugin ships with no dependencies, and a test
suite that cannot run on the machine it validates is not a test suite.

P1  identity          — load_doc(p).text() is the file, byte for byte.
P2  idempotent write  — writing a field its current value changes nothing.
P3  emit determinism  — same arguments, same bytes.

P1 is nearly free and only guards the reader. P2 is the one that can break, and
it is the property that makes `sync --write` safe: 75% of a live client document
is prose no model represents, so a writer that re-renders destroys it. The
comparison is on the PARSED value, never on bytes — 'критично' and 'Критично.'
are the same priority, and a cron the human wrote bare must not gain backticks.
"""
import glob, io, os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import v3

# Корпус, на котором прогоняются тесты: СВОЙ, лежит рядом с ними.
#
# Здесь стоял абсолютный путь к чужому рабочему проекту — с именем пользователя
# и названием клиента, в публичном репозитории. Он ломал тест двумя способами
# сразу, и оба замерены 2026-08-27:
#
#   на той машине     15 тестов, один красный — числа переписи сняты с ЖИВЫХ
#                     документов, а они законно растут (триггеров стало 61
#                     против 57, вопросов 28 против 26, экранов 39 против 37).
#                     Тест, который краснеет от нормальной работы, перестают
#                     читать;
#   на любой другой   каталога нет, glob пуст, DOCS пуст — и двенадцать тестов
#                     из пятнадцати ПРОСТО НЕ СОЗДАЮТСЯ, потому что они
#                     порождаются по документам. Прогон печатает
#                     `Ran 3 tests ... OK`. Зелено, и не проверено ничего.
#
# Второе хуже первого: тест не падал у чужого, он молча переставал существовать.
# Ровно тот класс, о котором предупреждает LEARNINGS.md этого плагина — пустой
# результат принят за «там ничего нет» вместо «я не смог это прочитать».
#
# `corpus/` — выдуманный прокат велосипедов, шесть документов, минимальные, но
# настоящей формы: в них есть все ТРИ вида привязки указателя, ради которых
# перепись и существует (тождество, контейнер, отсутствие). MACSTACK_FIXTURE
# по-прежнему работает — так тесты можно прогнать против настоящего проекта, —
# но по умолчанию плагин проверяет себя на своём.
CORPUS = os.path.join(HERE, 'corpus')
CLIENT = os.environ.get('MACSTACK_FIXTURE') or CORPUS

# README.md рядом с корпусом — объяснение для человека, а не документ v3, и
# `*.md` его подхватывает. Поймано `assert`-ом ниже в ту же минуту, в которую
# README был написан: ради этого assert и стоит.
DOCS = sorted(d for d in glob.glob(os.path.join(CLIENT, '*.md'))
              if os.path.basename(d) != 'README.md')

if not DOCS:
    raise SystemExit('нет документов в %s — прогон остановлен.\n'
                     'Пустой корпус даёт три зелёных теста вместо пятнадцати, '
                     'и это выглядит как успех.' % CLIENT)

# Перепись снята с corpus/. Изменение здесь — никогда не повод ослабить тест:
# оно означает, что сдвинулась связь указателя, а тихо это происходит ровно
# одним способом — кто-то придумал запись в спеке, чтобы удовлетворить правило
# линта.
#
#   тождество   AUTOMATION, OVERVIEW, USER-CASES   id заголовка == id указателя
#   контейнер   UX-UI                              3 экрана -> 2 области
#   отсутствие  OPEN-QUESTIONS                     1 зачёркнутый пункт без указателя
CENSUS = {
    'AUTOMATION.md':     dict(headings=4, pointers=4, targets=4, same=4, none=0),
    'HANDBOOK.md':       dict(headings=0, pointers=0, targets=0, same=0, none=0),
    'OPEN-QUESTIONS.md': dict(headings=3, pointers=2, targets=2, same=2, none=1),
    'OVERVIEW.md':       dict(headings=2, pointers=2, targets=2, same=2, none=0),
    'USER-CASES.md':     dict(headings=3, pointers=3, targets=3, same=3, none=0),
    'UX-UI.md':          dict(headings=3, pointers=3, targets=2, same=0, none=0),
}

# Корпус должен ОСТАВАТЬСЯ полным: если чья-то правка выбросит из него документ,
# соответствующие тесты исчезнут так же тихо, как исчезали при пустом пути.
assert sorted(os.path.basename(d) for d in glob.glob(os.path.join(CORPUS, '*.md'))
              if os.path.basename(d) != 'README.md') == sorted(CENSUS), \
    'corpus/ и CENSUS разошлись по составу документов'


def read(p):
    return io.open(p, encoding='utf-8').read()


class P1Identity(unittest.TestCase):
    """The document is its lines. Reading then writing changes nothing."""


class P2IdempotentWrite(unittest.TestCase):
    """Writing a field the value it already holds must not touch the file."""


class P3EmitDeterminism(unittest.TestCase):
    def test_emit_entity_is_deterministic(self):
        a = v3.emit_entity('case', 'C-16', u'Проверка',
                           fields={'priority': 'important', 'screens': ['a', 'b']},
                           lang='ru')
        b = v3.emit_entity('case', 'C-16', u'Проверка',
                           fields={'priority': 'important', 'screens': ['a', 'b']},
                           lang='ru')
        self.assertEqual(a, b)


class LabelsDeclared(unittest.TestCase):
    """Every bullet label in the corpus reverses to a field key.

    Measured before the fix: 103 of 430 labels did not — 66 in AUTOMATION.md
    alone, where the table said 'что требуется от человека' and all 33 live
    bullets say 'что от человека требуется'. Each one became a raw Cyrillic
    dict key that no consumer reads, and nothing reported it.
    """

    def test_no_unmapped_labels(self):
        bad = []
        for p in DOCS:
            txt = read(p)
            lang = v3.header(txt).get('lang', 'ru')
            tbl = v3.LABELS.get(lang) or v3.LABELS['en']
            for n, line in enumerate(txt.splitlines(), 1):
                m = v3.BULLET.match(line)
                if m and m.group(1).strip().lower() not in tbl:
                    bad.append('%s:%d %s' % (os.path.basename(p), n, m.group(1)))
        self.assertEqual(bad, [], '%d unmapped labels\n%s'
                         % (len(bad), '\n'.join(bad[:12])))


class CardinalityCensus(unittest.TestCase):
    """Pointer binding is not one relation, and this is the proof.

    identity  AUTOMATION, OVERVIEW, USER-CASES   heading id == pointer id
    container UX-UI                              37 headings -> 9 interfaces[]
    none      4 closed open items                struck through, no longer owed

    Schema rev 13 changed two of these on purpose. Before it there was no cases[] to
    point at, so a case pointed at the ROLE that owned it — membership in the glob
    'C-*' — and the 27 cross-cutting cases and prohibitions, which belong to no role,
    carried no pointer at all. Now every case names its own record, and the member
    binding has no user left in this corpus. It stays in the contract because the
    relation is real; a project whose documents predate rev 13 will still use it.

    The eight processes that OVERVIEW.md used to head are now a list: the heading and
    the id were duplicated verbatim in two documents, which is one rename away from a
    disagreement nobody would notice.
    """

    def test_census_unchanged(self):
        import re
        # Перепись описывает СВОЙ корпус. Направив тесты на чужой через
        # MACSTACK_FIXTURE, её нужно пропустить, а не красить: остальные
        # четырнадцать проверяют читатель и писатель и осмысленны на любых
        # документах, а эта одна — нет.
        if CLIENT != CORPUS:
            self.skipTest('перепись снята с corpus/; запущено на %s' % CLIENT)
        for p in DOCS:
            name = os.path.basename(p)
            if name not in CENSUS:
                continue
            items = v3.load(p)
            ids = [i.id for i in items if i.id]
            ptr = [(i.id, i.ref) for i in items if i.id and i.ref]
            last = []
            for _id, q in ptr:
                m = re.findall(r'\[id=([^\]]+)\]', q or '')
                last.append(m[-1] if m else None)
            got = dict(headings=len(ids), pointers=len(ptr),
                       targets=len(set(x for x in last if x)),
                       same=sum(1 for (i, _), l in zip(ptr, last) if i == l),
                       none=len(ids) - len(ptr))
            self.assertEqual(got, CENSUS[name], name)


def _bind(cls, name, fn):
    setattr(cls, name, fn)


for _p in DOCS:
    _n = os.path.basename(_p).replace('.', '_').replace('-', '_').lower()

    def _p1(self, p=_p):
        self.assertEqual(v3.load_doc(p).text(), read(p))
    _bind(P1Identity, 'test_identity_' + _n, _p1)

    def _p2(self, p=_p):
        doc = v3.load_doc(p)
        for it in doc.items:
            for k, v in list(it.fields.items()):
                self.assertIs(v3.set_field(doc, it, k, v), False,
                              '%s %s.%s rewrote an unchanged value' %
                              (os.path.basename(p), it.id, k))
        self.assertFalse(doc.dirty)
        self.assertEqual(doc.text(), read(p))
    _bind(P2IdempotentWrite, 'test_idempotent_' + _n, _p2)


class ValueSplitting(unittest.TestCase):
    """Когда запятая делит значение на список, а когда остаётся запятой.

    Правило `_value`: список получается, только если КАЖДАЯ часть похожа на
    идентификатор — наивное деление резало cron `0 6 1,16 * *` пополам. Поле
    `docs` (3.1.0) несёт ПУТИ, а `IDENT` не знает `/`, поэтому два документа
    склеивались в одну строку с обратными кавычками внутри, пока `screens`
    рядом честно становился списком. Обе половины закреплены здесь: и то, что
    путь теперь делится, и то, что cron по-прежнему нет.
    """

    def _field(self, bullet, lang='ru'):
        doc = ('<!-- macstack:doc=tasks lang=%s version=1.5 -->\n# T\n\n'
               '### M1-T1 · X\n\n%s\n' % (lang, bullet))
        return dict([i for i in v3.read(doc, lang=lang) if i.id][0].fields)

    def test_several_paths_become_a_clean_list(self):
        self.assertEqual(
            self._field('- **Документы:** `a/b.md`, `c/d.pdf`'),
            {'docs': ['a/b.md', 'c/d.pdf']})

    def test_one_path_stays_scalar(self):
        # Соглашение всего документа: одно значение — скаляр, несколько — список;
        # потребители приводят к списку у себя (`ARRAY_FIELDS`, `_as_list`).
        self.assertEqual(
            self._field('- **Документы:** `docs/plans/m16.md`'),
            {'docs': 'docs/plans/m16.md'})

    def test_ids_still_split(self):
        self.assertEqual(
            self._field('- **Экраны:** `kalender`, `coach-portal`'),
            {'screens': ['kalender', 'coach-portal']})

    def test_cron_with_a_comma_is_not_a_list(self):
        # Регрессия, ради которой предикат вообще существует.
        self.assertEqual(
            self._field('- **Как часто:** 0 6 1,16 * *'),
            {'frequency': '0 6 1,16 * *'})

    def test_plan_label_is_read_as_docs(self):
        # Псевдоним читается, но не пишется: уже написанное «- **План:**»
        # обязано разбираться как поле, иначе оно молча становится прозой.
        self.assertEqual(
            self._field('- **План:** `docs/plans/m16.md`'),
            {'docs': 'docs/plans/m16.md'})

    def test_writer_emits_the_canonical_label(self):
        self.assertEqual(v3.emit_field('docs', ['a/b.md', 'c/d.pdf'], 'ru'),
                         '- **Документы:** `a/b.md`, `c/d.pdf`')


if __name__ == '__main__':
    unittest.main(verbosity=2)
