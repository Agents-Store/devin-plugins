# -*- coding: utf-8 -*-
"""Словарь статусов задач и вех: одна каноническая пятёрка, три устаревших токена.

Запуск: python3 skills/lint/references/tests/test_status_vocabulary.py

Решение владельца (2026-10-04). Каноническая пятёрка — трекерная:
`backlog · todo · in_progress · done · cancelled`. Три старых токена остаются ДОПУСТИМЫМИ
(иначе рухнет каждый существующий файл), но линтер предупреждает о каждом и называет
замену:

    doing   -> in_progress
    dropped -> cancelled
    blocked -> не статус: оставить настоящий (`todo` или `in_progress`), а препятствие
               записать в `blocked_by`

До решения словарей было три, и ни один не совпадал с другим:

  * контракт (`fields.status.enum`, по нему судит 12.14) знал пятёрку, `dropped` и три
    токена `planned · building · live`, которые не пишет и не читает ни один скрипт, —
    но не знал `doing` и `blocked`, и правило называло их ОШИБКОЙ;
  * схема rev 18 (`$defs/taskRef.status`, `$defs/milestoneRef.status`) знает пятёрку
    и `doing · blocked · dropped`, а `planned · building · live` не знает вовсе — задача
    с `status: live` проходила линтер и не проходила схему при зеркалировании;
  * у вех словаря в линтере не было совсем.

Схема — канон, поэтому контракт сверяется с ней, а не со списком в тесте.
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
LINT = os.path.dirname(HERE)
SKILLS = os.path.dirname(os.path.dirname(LINT))
DOCS = os.path.join(SKILLS, 'documents', 'references')
PLANNING = os.path.join(SKILLS, 'planning', 'references')
sys.path.insert(0, LINT)
sys.path.insert(0, PLANNING)
import lint_folder as lf                                       # noqa: E402

CANONICAL = ('backlog', 'todo', 'in_progress', 'done', 'cancelled')


def load(path):
    with io.open(path, encoding='utf-8') as fh:
        return json.load(fh)


CONTRACT = load(os.path.join(DOCS, 'doc-contracts.json'))
SCHEMA = load(os.path.join(LINT, 'macstack.schema.json'))


def write(path, text):
    d = os.path.dirname(path)
    if not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, 'w', encoding='utf-8') as fh:
        fh.write(text)


class Folder(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='macstack-status-')
        write(os.path.join(self.root, 'macstack.json'),
              json.dumps({'docs': {'language': 'en'}}))

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def tasks(self, task_statuses=(), milestone_statuses=()):
        lines = ['<!-- macstack:doc=tasks lang=en version=1.0 -->', '# Tasks', '',
                 '## Milestones', '']
        for i, st in enumerate(milestone_statuses, 1):
            lines += ['### M%d · Milestone %d' % (i, i), '', '- **Status:** %s' % st, '',
                      '**Done when:**', '- a file exists', '']
        lines += ['## Tasks', '']
        for i, st in enumerate(task_statuses, 1):
            lines += ['<!-- macstack:ref=cases[id=C-01] -->',
                      '### M1-T%d · Task %d' % (i, i), '',
                      '- **Status:** %s' % st, '- **Opened:** 2026-10-01',
                      '- **Closes:** `C-01`', '- **Tracker:** TRK-%d' % i, '',
                      '**Acceptance:**', '- a test named so reddens', '']
        write(os.path.join(self.root, 'history', 'TASKS.md'), '\n'.join(lines))

    def lint(self):
        found, _ = lf.run(self.root, only=['12.14'], warnings=True)
        self.assertIsNotNone(found, 'линтер не смог загрузить папку')
        return found


class TaskStatuses(Folder):
    def test_the_canonical_five_give_nothing(self):
        self.tasks(CANONICAL)
        self.assertEqual(self.lint(), [])

    def test_doing_is_a_warning_naming_in_progress(self):
        self.tasks(['doing'])
        found = self.lint()
        self.assertEqual([(f.rule, f.severity) for f in found], [('12.14', lf.WARNING)],
                         found)
        self.assertIn('in_progress', found[0].message)
        self.assertIn('M1-T1', found[0].message)

    def test_dropped_is_a_warning_naming_cancelled(self):
        self.tasks(['dropped'])
        found = self.lint()
        self.assertEqual([f.severity for f in found], [lf.WARNING], found)
        self.assertIn('cancelled', found[0].message)

    def test_blocked_is_a_warning_pointing_at_blocked_by(self):
        self.tasks(['blocked'])
        found = self.lint()
        self.assertEqual([f.severity for f in found], [lf.WARNING], found)
        self.assertIn('blocked_by', found[0].message)
        self.assertIn('todo', found[0].message)

    def test_a_token_no_vocabulary_knows_is_still_an_error(self):
        for tok in ('planned', 'building', 'live', 'whatever'):
            self.tasks([tok])
            found = self.lint()
            self.assertEqual([f.severity for f in found], [lf.ERROR],
                             '%s: %r' % (tok, found))

    def test_a_deprecated_task_is_not_also_an_error(self):
        # Три токена «допустимы»: ни ошибки «не из списка», ни ошибки про трекер,
        # которого у задачи нет по причине статуса, а не по небрежности.
        self.tasks(['doing', 'dropped', 'blocked'])
        found = self.lint()
        self.assertEqual([f.severity for f in found], [lf.WARNING] * 3, found)


class MilestoneStatuses(Folder):
    def test_canonical_milestones_give_nothing(self):
        self.tasks(milestone_statuses=CANONICAL)
        self.assertEqual(self.lint(), [])

    def test_deprecated_milestone_statuses_warn_with_the_replacement(self):
        self.tasks(milestone_statuses=['doing', 'dropped', 'blocked'])
        found = self.lint()
        self.assertEqual([f.severity for f in found], [lf.WARNING] * 3, found)
        text = ' '.join(f.message for f in found)
        self.assertIn('in_progress', text)
        self.assertIn('cancelled', text)
        self.assertIn('blocked_by', text)

    def test_a_milestone_status_the_schema_does_not_know_is_a_warning(self):
        # Раньше словаря у вех не было вообще; ошибкой это не становится — только
        # предупреждением, чтобы новая проверка не покраснила существующий проект.
        self.tasks(milestone_statuses=['live'])
        found = self.lint()
        self.assertEqual([f.severity for f in found], [lf.WARNING], found)


class ContractAgreesWithTheSchema(unittest.TestCase):
    def schema_enum(self, ref):
        return set(SCHEMA['$defs'][ref]['properties']['status']['enum'])

    def test_the_contract_vocabulary_is_the_schema_vocabulary(self):
        enum = set(CONTRACT['fields']['status']['enum'])
        self.assertEqual(enum, self.schema_enum('taskRef'),
                         'контракт и taskRef.status расходятся: %s'
                         % sorted(enum ^ self.schema_enum('taskRef')))
        self.assertEqual(enum, self.schema_enum('milestoneRef'))

    def test_the_two_schema_vocabularies_agree_with_each_other(self):
        self.assertEqual(self.schema_enum('taskRef'), self.schema_enum('milestoneRef'))

    def test_the_deprecated_tokens_carry_a_fix(self):
        dep = CONTRACT['fields']['status'].get('deprecated') or {}
        self.assertEqual(sorted(dep), ['blocked', 'doing', 'dropped'])
        self.assertEqual(dep['doing'].get('replace_with'), 'in_progress')
        self.assertEqual(dep['dropped'].get('replace_with'), 'cancelled')
        self.assertIn('blocked_by', dep['blocked'].get('fix', ''))
        enum = set(CONTRACT['fields']['status']['enum'])
        for tok, d in dep.items():
            self.assertIn(tok, enum, '%s устарел, но не допустим' % tok)
            if 'replace_with' in d:
                self.assertIn(d['replace_with'], CANONICAL)

    def test_the_canonical_five_are_what_is_left_after_deprecation(self):
        enum = CONTRACT['fields']['status']['enum']
        dep = CONTRACT['fields']['status'].get('deprecated') or {}
        self.assertEqual(sorted(t for t in enum if t not in dep), sorted(CANONICAL))


class NoWriterEmitsADeprecatedToken(unittest.TestCase):
    def test_task_status_may_only_write_the_canonical_five(self):
        import task_status                                      # noqa: PLC0415
        allowed = task_status.writable_statuses(CONTRACT)
        self.assertEqual(sorted(allowed), sorted(CANONICAL))

    def test_the_plane_reconcile_names_the_replacement(self):
        import plane                                            # noqa: PLC0415
        root = tempfile.mkdtemp(prefix='macstack-plane-')
        try:
            write(os.path.join(root, 'macstack.json'), json.dumps({}))
            write(os.path.join(root, 'history', 'TASKS.md'), '\n'.join([
                '<!-- macstack:doc=tasks lang=en version=1.0 -->', '# Tasks', '',
                '## Tasks', '', '### M1-T1 · Old word', '',
                '- **Status:** doing', '- **Tracker:** TRK-1', '']))
            plan = plane.plan(root)
            self.assertEqual(len(plan['conflict']), 1, plan)
            self.assertIn('deprecated', plan['conflict'][0]['why'])
            self.assertIn("use 'in_progress'", plan['conflict'][0]['why'])
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
