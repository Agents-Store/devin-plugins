# -*- coding: utf-8 -*-
"""Правило 12.0 молчит, когда в самой спецификации сущностей этого вида нет.

Запуск: python3 skills/lint/references/tests/test_rule_12_0_empty_kinds.py

12.0 читает «в документе есть заголовки, а ни одной сущности объявленного вида не
нашлось» как СЛОМАННЫЙ ФИЛЬТР — и это его работа: фильтр, который ничего не находит,
выглядит как чистый документ. Но AUTOMATION.md проекта вообще без человеческих задач
(одни машинные, у которых в документе нет места) или без триггеров не содержит их
законно, и правило объявляло такой документ сломанным. Находка, которой нечем
подтвердить «сломан», — шум, по которому линтер перестают читать.

Различение простое: сколько сущностей вида ждёт СПЕЦИФИКАЦИЯ. Нет ни одной — документ
пуст по праву. Есть, а в документе ни одной — фильтр действительно может быть сломан, и
правило обязано сработать (охранные тесты ниже).
"""
import io
import json
import os
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


MACHINE_TASK = {'id': 'send-digest', 'name': 'Send the digest', 'workflow': 'wf-x'}
HUMAN_TASK = {'id': 'approve-refund', 'name': 'Approve a refund',
              'human': {'role': 'ops', 'gate': 'approve'}}
TRIGGER = {'id': 'trg-nightly', 'name': 'Nightly', 'type': 'schedule',
           'config': {'schedule': '0 3 * * *'}}


class Folder(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='macstack-12-0-')

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def project(self, tasks, triggers, doc_tasks=(), doc_triggers=()):
        spec = {'docs': {'language': 'en'},
                'roles': [{'id': 'ops', 'name': 'Operations'}],
                'workflows': [{'id': 'wf-x', 'name': 'X', 'engine': 'script'}],
                'processes': [{'id': 'support', 'name': 'Support', 'type': 'operations',
                               'tasks': list(tasks)}],
                'triggers': list(triggers)}
        write(os.path.join(self.root, 'macstack.json'), json.dumps(spec))
        lines = ['<!-- macstack:doc=automation lang=en version=1.0 -->', '# Automation', '',
                 '## Roles', '', '<!-- macstack:ref=roles[id=ops] -->',
                 '### Operations — `ops`', '', '## Tasks', '',
                 '<!-- macstack:ref=processes[id=support] -->', '### Support — `support`', '']
        for tid in doc_tasks:
            lines += ['<!-- macstack:ref=processes[id=support].tasks[id=%s] -->' % tid,
                      '#### Task %s — `%s`' % (tid, tid), '', '- **Who does it:** `ops`',
                      '- **What the person must do:** `approve`', '']
        lines += ['## Triggers', '']
        for tid in doc_triggers:
            lines += ['<!-- macstack:ref=triggers[id=%s] -->' % tid,
                      '### Trigger %s — `%s`' % (tid, tid), '',
                      '- **Kind of event:** `schedule`', '']
        write(os.path.join(self.root, 'client', 'AUTOMATION.md'), u'\n'.join(lines))

    def broken_filters(self):
        found, _ = lf.run(self.root, only=['12.0'])
        self.assertIsNotNone(found)
        return found


class SpecHasNoneOfTheKind(Folder):
    def test_a_document_without_human_tasks_when_the_spec_has_none(self):
        self.project([MACHINE_TASK], [TRIGGER], doc_triggers=['trg-nightly'])
        self.assertEqual(self.broken_filters(), [])

    def test_a_document_without_triggers_when_the_spec_has_none(self):
        self.project([HUMAN_TASK], [], doc_tasks=['approve-refund'])
        self.assertEqual(self.broken_filters(), [])

    def test_a_document_with_neither_when_the_spec_has_neither(self):
        self.project([MACHINE_TASK], [])
        self.assertEqual(self.broken_filters(), [])

    def test_a_spec_with_no_tasks_at_all(self):
        self.project([], [TRIGGER], doc_triggers=['trg-nightly'])
        self.assertEqual(self.broken_filters(), [])


class SpecExpectsTheKind(Folder):
    """Охрана: ради этого правило и написано, и оно должно продолжать срабатывать."""

    def test_human_tasks_in_the_spec_and_none_matched_in_the_document(self):
        self.project([HUMAN_TASK], [TRIGGER], doc_triggers=['trg-nightly'])
        found = self.broken_filters()
        self.assertEqual(len(found), 1, found)
        self.assertIn('role_task', found[0].message)

    def test_triggers_in_the_spec_and_none_matched_in_the_document(self):
        self.project([HUMAN_TASK], [TRIGGER], doc_tasks=['approve-refund'])
        found = self.broken_filters()
        self.assertEqual(len(found), 1, found)
        self.assertIn('trigger', found[0].message)

    def test_a_complete_document_is_clean(self):
        self.project([HUMAN_TASK], [TRIGGER], doc_tasks=['approve-refund'],
                     doc_triggers=['trg-nightly'])
        self.assertEqual(self.broken_filters(), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
