# -*- coding: utf-8 -*-
"""Ветка `blocked_by` правила 12.4 читает TASKS.md в форме v3.

Запуск: python3 skills/lint/references/tests/test_blocked_by_v3.py

Ветка читала `history/TASKS.md` через `mdblocks` и видела только записи с якорем
`<!-- macstack:task= -->` и блоком yaml — форму v2. Контракт же давно требует v3:
заголовки и пункты-метки без единого якоря. На v3-файле ветка не находила ни одной
задачи и молчала — как когда-то молчало правило 12.0 на пустом фильтре, и по той же
причине: «ничего не проверено» выглядело как «всё в порядке». Висячий `blocked_by`
(задача, которой нет, вопрос, которого нет) проходил линтер.

Решение владельца (2026-10-04): сначала предупреждения, ошибки потом. Поэтому ветка
теперь читает v3 — и сообщает о находках ПРЕДУПРЕЖДЕНИЯМИ, говоря об этом в тексте:
на проектах, где `blocked_by` уже заведён, она начнёт срабатывать, и красить их сразу
значило бы красить файлы, которые никто не проверял. Форма v2 по-прежнему читается.
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


LABELS = {
    'en': {'status': 'Status', 'opened': 'Opened', 'closes': 'Closes',
           'tracker': 'Tracker', 'blocked_by': 'Blocked by'},
    'ru': {'status': u'Состояние', 'opened': u'Заведена', 'closes': u'Закрывает',
           'tracker': 'Plane', 'blocked_by': u'Чем заблокирована'},
}


class Folder(unittest.TestCase):
    lang = 'en'

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='macstack-blocked-')
        write(os.path.join(self.root, 'macstack.json'),
              json.dumps({'docs': {'language': self.lang}}))
        write(os.path.join(self.root, 'client', 'OPEN-QUESTIONS.md'), u'\n'.join([
            '<!-- macstack:doc=open_questions lang=%s version=1.0 -->' % self.lang,
            '# Open questions', '', '## Client inputs', '',
            '### QA1 · Still open', '', '### ~~QA5~~ · CLOSED D1, 2026-09-02', '']))

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def tasks(self, blocked_by):
        """TASKS.md v3. blocked_by = {task number: value as written in the bullet | None}."""
        lb = LABELS[self.lang]
        lines = ['<!-- macstack:doc=tasks lang=%s version=1.0 -->' % self.lang,
                 '# Tasks', '', '## Tasks', '']
        for n in sorted(blocked_by):
            lines += ['<!-- macstack:ref=cases[id=C-01] -->',
                      '### M1-T%d · Task %d' % (n, n), '',
                      '- **%s:** todo' % lb['status'], '- **%s:** 2026-10-01' % lb['opened'],
                      '- **%s:** `C-01`' % lb['closes'], '- **%s:** TRK-%d' % (lb['tracker'], n)]
            if blocked_by[n] is not None:
                lines.append('- **%s:** %s' % (lb['blocked_by'], blocked_by[n]))
            lines += ['', '**Acceptance:**', '- a named test reddens', '']
        write(os.path.join(self.root, 'history', 'TASKS.md'), u'\n'.join(lines))

    def lint(self, warnings=True):
        found, _ = lf.run(self.root, only=['12.4'], warnings=warnings)
        self.assertIsNotNone(found, 'линтер не смог загрузить папку')
        return [f for f in found if 'blocked_by' in f.message]


class V3Tasks(Folder):
    def test_a_dangling_task_is_reported(self):
        self.tasks({1: '`M1-T9`', 2: None})
        got = self.lint()
        self.assertEqual(len(got), 1, got)
        self.assertIn('M1-T1', got[0].message)
        self.assertIn('M1-T9', got[0].message)

    def test_a_dangling_open_item_is_reported(self):
        self.tasks({1: '`QA7`'})
        got = self.lint()
        self.assertEqual(len(got), 1, got)
        self.assertIn('QA7', got[0].message)

    def test_a_live_task_and_a_live_or_closed_open_item_resolve(self):
        self.tasks({1: '`M1-T2`', 2: '`QA1`', 3: '`QA5`'})
        self.assertEqual(self.lint(), [])

    def test_a_list_reports_only_the_member_that_does_not_resolve(self):
        self.tasks({1: '`M1-T2`, `M1-T9`', 2: None})
        got = self.lint()
        self.assertEqual(len(got), 1, got)
        self.assertIn('M1-T9', got[0].message)
        self.assertNotIn("'M1-T2'", got[0].message)

    def test_a_task_without_the_bullet_is_silent(self):
        self.tasks({1: None})
        self.assertEqual(self.lint(), [])

    def test_the_finding_points_at_the_bullet(self):
        self.tasks({1: '`M1-T9`'})
        got = self.lint()[0]
        lines = io.open(os.path.join(self.root, 'history', 'TASKS.md'),
                        encoding='utf-8').read().split('\n')
        self.assertIn('Blocked by', lines[got.line - 1])


class WarningsFirst(Folder):
    def test_the_finding_is_a_warning_and_says_it_will_become_an_error(self):
        self.tasks({1: '`M1-T9`'})
        got = self.lint()
        self.assertEqual([f.severity for f in got], [lf.WARNING], got)
        self.assertIn('warning for now', got[0].message)
        self.assertIn('error', got[0].message)

    def test_no_error_is_produced(self):
        self.tasks({1: '`M1-T9`', 2: '`QA7`'})
        found, _ = lf.run(self.root, only=['12.4'], warnings=False)
        self.assertEqual(found, [], 'ветка blocked_by не должна давать ошибок')

    def test_the_rule_text_says_warnings_first(self):
        here = os.path.join(os.path.dirname(HERE), 'rules-group-12.md')
        text = io.open(here, encoding='utf-8').read()
        i = text.index('12.4 **Cross-file refs**')
        self.assertIn('warning', text[i:i + 1600].lower())


class RussianLabel(Folder):
    lang = 'ru'

    def test_the_declared_russian_label_is_read(self):
        self.tasks({1: '`M1-T9`'})
        got = self.lint()
        self.assertEqual(len(got), 1, got)
        self.assertIn('M1-T9', got[0].message)


class LegacyAnchoredForm(Folder):
    def test_the_v2_form_is_still_read_and_is_a_warning_now(self):
        write(os.path.join(self.root, 'history', 'TASKS.md'), u'\n'.join([
            '<!-- macstack:doc=tasks lang=en version=1.0 -->', '# Tasks', '',
            '## Tasks', '',
            '<!-- macstack:task=M1-T1 -->', '### M1-T1 · Do the thing', '',
            '```yaml', 'status: todo', 'blocked_by: [M1-T9]', '```', '']))
        got = self.lint()
        self.assertEqual([f.severity for f in got], [lf.WARNING], got)
        self.assertIn('M1-T9', got[0].message)


if __name__ == '__main__':
    unittest.main(verbosity=2)
