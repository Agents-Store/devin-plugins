# -*- coding: utf-8 -*-
"""`scan_tests` считает покрытие по ОДНОМУ дереву, а не по всем, что лежат внутри.

Дефект, ради которого написан файл (измерен 2026-08-27 на живом проекте): в
`.claude/worktrees/` лежали четыре worktree'а агентов — полные чекауты того же
репозитория. Сканер обошёл их наравне с рабочим деревом, и в `TEST-CASES.md`
уехали строки вида

    - `X-01` Task feed … — `.claude/worktrees/agent-a52f8dda…/tests/e2e/panels.e2e.spec.ts`

Это документ, который читает заказчик как отчёт о готовности. Хуже, чем
некрасивый путь: кейс мог оказаться «проверенным» тестом с ЧУЖОЙ ветки, которая
не слита и, возможно, никогда не будет.

Второй случай тот же по природе и не ловится списком имён: чекаут, положенный
внутрь проекта руками. Поэтому проверок две — по имени каталога и по наличию
вложенного `.git`.
"""
import io
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import render  # noqa: E402


def _spec(path, body):
    os.makedirs(os.path.dirname(path))
    with io.open(path, 'w', encoding='utf-8') as f:
        f.write(body)


class ScanTestsSkipsNestedCheckouts(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='macstack-scan-')
        _spec(os.path.join(self.root, 'tests', 'a.spec.ts'),
              u"it('the real tree proves this (C-01)', () => {})\n")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_the_working_tree_is_counted(self):
        hits = render.scan_tests(self.root)
        self.assertIn('C-01', hits)

    def test_a_worktree_under_dot_claude_is_not(self):
        _spec(os.path.join(self.root, '.claude', 'worktrees', 'agent-x', 'tests', 'b.spec.ts'),
              u"it('a branch nobody merged (C-02)', () => {})\n")
        hits = render.scan_tests(self.root)
        self.assertIn('C-01', hits)
        self.assertNotIn('C-02', hits, u'тест из worktree агента попал в покрытие')

    def test_a_worktree_under_dot_codex_is_not(self):
        _spec(os.path.join(self.root, '.codex', 'worktrees', '1543', 'tests', 'c.spec.ts'),
              u"it('another tool branch (C-03)', () => {})\n")
        self.assertNotIn('C-03', render.scan_tests(self.root))

    def test_any_nested_checkout_is_not_however_it_is_named(self):
        # Ни `.claude`, ни `.codex` — обычное имя. Ловит только вложенный `.git`.
        nested = os.path.join(self.root, 'vendor', 'copy-of-the-repo')
        _spec(os.path.join(nested, 'tests', 'd.spec.ts'),
              u"it('a checkout somebody dropped in (C-04)', () => {})\n")
        os.makedirs(os.path.join(nested, '.git'))
        self.assertNotIn('C-04', render.scan_tests(self.root))

    def test_an_ordinary_vendor_directory_is_still_counted(self):
        # Обратная сторона: исключаем чекауты, а не всё подряд. Без этого случая
        # предыдущие три зелены на сканере, который не считает ничего.
        _spec(os.path.join(self.root, 'packages', 'ui', 'tests', 'e.spec.ts'),
              u"it('an ordinary workspace package (C-05)', () => {})\n")
        self.assertIn('C-05', render.scan_tests(self.root))


if __name__ == '__main__':
    unittest.main(verbosity=2)
