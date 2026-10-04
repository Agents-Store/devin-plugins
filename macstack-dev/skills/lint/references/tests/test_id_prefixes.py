# -*- coding: utf-8 -*-
"""Префиксы `Q` и `C` в идентификаторах — линтер читает их так же, как legacy-форму.

Запуск: python3 skills/lint/references/tests/test_id_prefixes.py

Контракт (`doc-contracts.json` -> `id_spaces`) принимает две формы одного и того же
номера: `A27` / `QA27` для вопроса и `CZ-14` / `Z-14` для кейса. Миграция
(`migrate_ids.py`) переписывает первую форму во вторую, v3-парсер и схема обе формы
принимают, а правила 12.3, 12.4 и 12.6 читали только legacy: сканировали заголовки по
`^[AB][0-9]+$` и искали открытые пункты через `startswith('A')`.

Следствие молчаливое, и поэтому тесты сравнивают, а не просто ищут находку. После
миграции:

  * `QA5` и ещё один `QA5` (или `~~QA5~~` и новый `QA5`) не считались повтором — а
    «номера не переиспользуются никогда» держится именно на этой проверке;
  * закрытый `~~QA9~~` в `needs_from_client` не давал 12.6 «витрина устарела», а
    открытый `QA1`, которого в витрине нет, не давал «клиента не спросят»;
  * `blocked_by: QA5` на существующий пункт давал ЛОЖНОЕ 12.4 — вымышленную ошибку на
    исправном файле, ровно та шумная находка, из-за которой линтер перестают читать.

Эталон — один и тот же проект в двух написаниях. Он обязан давать те же находки с
точностью до префикса, и непустые: проект, на котором ничего не находится ни в одной
форме, сравнение «одинаково» прошёл бы тоже.
"""
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import lint_folder as lf                                       # noqa: E402


def write(path, text):
    d = os.path.dirname(path)
    if not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, 'w', encoding='utf-8') as fh:
        fh.write(text)


class Folder(unittest.TestCase):
    """Минимальная папка `macstack/`: ровно то, что читают 12.3, 12.4 и 12.6."""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='macstack-ids-')

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def spec(self, lifecycle):
        write(os.path.join(self.root, 'macstack.json'),
              json.dumps({'docs': {'language': 'en'}, 'lifecycle': lifecycle}))

    def questions(self, *headings):
        body = ['<!-- macstack:doc=open_questions lang=en version=1.0 -->',
                '# Open questions', '', '## Client inputs', '']
        for h in headings:
            body += ['### %s' % h, '']
        write(os.path.join(self.root, 'client', 'OPEN-QUESTIONS.md'),
              '\n'.join(body))

    def tasks_v2(self, blocked_by):
        """TASKS.md в форме, которую читает ветка `blocked_by` правила 12.4.

        Ветка идёт через `mdblocks`, то есть видит только записи с якорем
        `<!-- macstack:task= -->` и yaml-блоком; про v3-заголовки без якоря см.
        LEARNINGS.md — там это записано как отдельная находка.
        """
        write(os.path.join(self.root, 'history', 'TASKS.md'),
              '\n'.join([
                  '<!-- macstack:doc=tasks lang=en version=1.0 -->',
                  '# Tasks', '', '## Tasks', '',
                  '<!-- macstack:task=M1-T1 -->',
                  '### M1-T1 · Do the thing', '',
                  '```yaml', 'status: todo', 'blocked_by: [%s]' % blocked_by,
                  '```', '']))

    def lint(self, *rules):
        found, _ = lf.run(self.root, only=list(rules))
        self.assertIsNotNone(found, 'линтер не смог загрузить папку')
        return found

    def messages(self, *rules):
        return sorted((f.rule, f.message) for f in self.lint(*rules))


def unprefixed(text):
    """`QA5` -> `A5`: приводит находку новой формы к виду legacy."""
    return re.sub(r'\bQ([AB][0-9]+)', r'\1', text)


class SameProjectTwoSpellings(Folder):
    """Один проект, записанный с префиксом и без: находки те же, непустые."""

    def build(self, p):
        self.questions('%sA1 · An open question' % p,
                       '~~%sA9~~ · CLOSED D1, 2026-09-02' % p)
        self.spec({
            # закрытый A9 в витрине — «витрина устарела»; открытого A1 в ней нет —
            # «клиента не спросят»; A7 не существует вовсе — 12.4
            'needs_from_client': [{'id': '%sA9' % p}],
            'open_questions': [{'id': '%sA7' % p}],
        })

    def test_the_legacy_form_produces_the_expected_three(self):
        # Опорный случай: без него «те же находки» могли бы оказаться «никаких».
        self.build('')
        got = self.messages('12.4', '12.6')
        self.assertEqual([r for r, _ in got], ['12.4', '12.6', '12.6'], got)

    def test_the_q_form_produces_the_same_findings(self):
        self.build('')
        legacy = [(r, m) for r, m in self.messages('12.4', '12.6')]
        shutil.rmtree(self.root)
        self.root = tempfile.mkdtemp(prefix='macstack-ids-')
        self.build('Q')
        got = [(r, unprefixed(m)) for r, m in self.messages('12.4', '12.6')]
        self.assertEqual(got, legacy,
                         'после миграции A->QA проект перестал давать находки 12.4/12.6')


class NeverReuseANumber(Folder):
    """12.3: номер вопроса не переиспользуется, в какой бы форме он ни был записан."""

    def reused(self):
        return [f for f in self.lint('12.3') if 'reused' in f.message]

    def test_two_headings_with_the_same_q_id(self):
        self.questions('QA5 · First', '~~QA5~~ · CLOSED D1, 2026-09-02')
        self.spec({})
        self.assertEqual(len(self.reused()), 1, self.lint('12.3'))

    def test_a_number_reused_across_forms(self):
        # `A5` и `QA5` — один пункт до и после миграции; оба в одном файле — это
        # два определения одного номера.
        self.questions('A5 · Legacy spelling', 'QA5 · Migrated spelling')
        self.spec({})
        self.assertEqual(len(self.reused()), 1, self.lint('12.3'))

    def test_a_struck_q_id_reused_says_why(self):
        self.questions('~~QB3~~ · CLOSED D2, 2026-09-02', 'QB3 · A fresh one')
        self.spec({})
        got = self.reused()
        self.assertEqual(len(got), 1, self.lint('12.3'))
        self.assertIn('never reused after a strike', got[0].message)

    def test_the_legacy_duplicate_is_still_caught(self):
        self.questions('A5 · First', 'A5 · Second')
        self.spec({})
        self.assertEqual(len(self.reused()), 1, self.lint('12.3'))

    def test_different_letters_are_different_numbers(self):
        # Обратная сторона: нормализация не должна склеить QA5 с QB5 или A5 с B5.
        self.questions('QA5 · Owed by the client', 'QB5 · Deferred by the team',
                       'A6 · Legacy client', 'B6 · Legacy team')
        self.spec({})
        self.assertEqual(self.reused(), [], self.lint('12.3'))


class BlockedByAnOpenItem(Folder):
    """12.4: `blocked_by` на вопрос в префиксной форме разрешается так же, как в legacy."""

    def setUp(self):
        super(BlockedByAnOpenItem, self).setUp()
        self.questions('QA1 · Still open', '~~QA5~~ · CLOSED D1, 2026-09-02')
        self.spec({'needs_from_client': [{'id': 'QA1'}]})

    def test_an_existing_closed_q_item_is_not_an_error(self):
        self.tasks_v2('QA5')
        self.assertEqual(self.lint('12.4'), [])

    def test_an_existing_open_q_item_is_not_an_error(self):
        self.tasks_v2('QA1')
        self.assertEqual(self.lint('12.4'), [])

    def test_a_missing_q_item_is_still_an_error(self):
        # Починка не должна превратиться в «принимать любое QA…».
        self.tasks_v2('QA7')
        got = self.lint('12.4')
        self.assertEqual(len(got), 1, got)
        self.assertIn('QA7', got[0].message)

    def test_the_legacy_form_is_unchanged(self):
        self.questions('A1 · Still open', '~~A5~~ · CLOSED D1, 2026-09-02')
        self.spec({'needs_from_client': [{'id': 'A1'}]})
        self.tasks_v2('A5')
        self.assertEqual(self.lint('12.4'), [])
        self.tasks_v2('A7')
        self.assertEqual(len(self.lint('12.4')), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
