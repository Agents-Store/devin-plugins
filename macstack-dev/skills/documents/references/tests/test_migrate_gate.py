# -*- coding: utf-8 -*-
"""`migrate.py` не пишет `gate: none` никогда.

Запуск: python3 skills/documents/references/tests/test_migrate_gate.py

Решение владельца (2026-10-04). Пустая ячейка гейта в таблице v1 означала «человека
тут нет» — машинную задачу; такая задача не получает пункта «что от человека
требуется» вовсе. В схеме нет `human.gate: none` и не будет: задача, которая только
запускает workflow, не имеет блока `human`. Сам же `none` читался как «ничей», то есть
как противоположность тому, что говорила строка, — и конвертер, не знавший слова из
ячейки, молча писал его на каждую такую задачу (33 штуки на живом проекте).
"""
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.dirname(HERE)
sys.path.insert(0, DOCS)
import migrate                                                 # noqa: E402

TASKS = u"""### Coach — `coach`

| Task | Starts | Gate | Workflow |
|---|---|---|---|
| Approve | — | approve | wf-a |
| Cleanup nightly | — | — | wf-b |
| Cleanup weekly | — | | wf-c |
| Odd | — | whatever | — |
"""



class GateNone(unittest.TestCase):
    def convert(self):
        _roles, tasks, _trig = migrate.convert_roles_tasks(TASKS, 'en', {})
        return dict((re.search(r'role_task=(\S+)', t).group(1), t) for t in tasks)

    def test_a_human_gate_is_written(self):
        tasks = self.convert()
        self.assertRegex(tasks['approve'], r'(?m)^gate: approve$')

    def test_a_task_without_a_human_gate_gets_no_gate_line(self):
        tasks = self.convert()
        for ident in ('cleanup-nightly', 'cleanup-weekly'):
            self.assertNotRegex(tasks[ident], r'(?m)^gate:', ident)

    def test_none_is_never_written(self):
        for text in self.convert().values():
            self.assertNotRegex(text, r'(?m)^gate:\s*none\b')

    def test_the_rest_of_the_row_survives(self):
        tasks = self.convert()
        self.assertRegex(tasks['cleanup-nightly'], r'(?m)^workflow: wf-b$')
        self.assertRegex(tasks['cleanup-nightly'], r'(?m)^role: coach$')

    def test_an_unrecognised_gate_word_is_not_guessed(self):
        # «whatever» — не гейт и не пустота: не `none`, не любое другое слово.
        self.assertNotRegex(self.convert()['odd'], r'(?m)^gate:')

    def test_the_gate_table_has_no_none_in_it(self):
        self.assertNotIn('none', set(migrate.GATES.values()))


if __name__ == '__main__':
    unittest.main(verbosity=2)
