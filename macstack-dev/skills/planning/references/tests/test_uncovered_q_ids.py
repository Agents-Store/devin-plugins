# -*- coding: utf-8 -*-
"""`uncovered.py` узнаёт открытый вопрос в форме `QA5`, а не только `A5`.

Запуск: python3 skills/planning/references/tests/test_uncovered_q_ids.py

Отчёт делит кейсы без плана на «работа» и «ждёт ответа клиента». Вторая группа — это
кейсы, в тексте которых названо ещё не закрытое `A<n>` из OPEN-QUESTIONS.md: задачу под
них не заводят, пока ответ не пришёл (решение владельца от 2026-08-27).

Шаблон `\\b([AB]\\d+)\\b` не видит `QA5`: между `Q` и `A` нет границы слова, а сам
заголовок `### QA5 · …` не проходил `OPEN_ID.match`. После `migrate_ids.py` — а он
переписывает `A5` в `QA5` — ни один кейс больше не считался ждущим, и весь список
«ждут клиента» уезжал в «работу»: отчёт ровно тем же языком предлагал завести задачи,
которые писать нельзя.

Тут же обратный случай — закрытый (зачёркнутый) вопрос в новой форме не блокирует
ничего, как и в старой.
"""
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), 'uncovered.py')


def write(path, text):
    d = os.path.dirname(path)
    if not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, 'w', encoding='utf-8') as fh:
        fh.write(text)


CASES = u'''<!-- macstack:doc=user_cases lang=en version=1.0 -->
# User cases

## Roles

<!-- macstack:ref=cases[id=CA-01] -->
### CA-01 · Pay an invoice

- **Priority:** critical

**Done if:**
- The invoice is paid once {waits} is answered.

<!-- macstack:ref=cases[id=CA-02] -->
### CA-02 · A plain case

- **Priority:** critical

**Done if:**
- Something works.
'''

QUESTIONS = u'''<!-- macstack:doc=open_questions lang=en version=1.0 -->
# Open questions

## Client inputs

### {heading}

- **Asked on:** 2026-09-01
- **Goes to:** client
'''

TASKS = u'''<!-- macstack:doc=tasks lang=en version=1.0 -->
# Tasks

## Tasks
'''


class Uncovered(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='macstack-uncovered-')
        self.ms = os.path.join(self.root, 'macstack')
        write(os.path.join(self.ms, 'macstack.json'), u'{"docs": {"language": "en"}}')
        write(os.path.join(self.ms, 'history', 'TASKS.md'), TASKS)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def report(self, waits, heading):
        write(os.path.join(self.ms, 'client', 'USER-CASES.md'),
              CASES.format(waits=waits))
        write(os.path.join(self.ms, 'client', 'OPEN-QUESTIONS.md'),
              QUESTIONS.format(heading=heading))
        return subprocess.check_output(
            [sys.executable, SCRIPT, self.ms], stderr=subprocess.STDOUT).decode('utf-8')

    def awaiting(self, out):
        m = re.search(r'awaiting the client, NOT a task: (\d+)', out)
        self.assertIsNotNone(m, out)
        return int(m.group(1))

    def test_the_legacy_form_blocks_the_case(self):
        # Опорный случай: без него «и в новой форме нуль» могло бы значить «нуль везде».
        out = self.report('A5', 'A5 · Which provider')
        self.assertEqual(self.awaiting(out), 1, out)

    def test_the_q_form_blocks_the_case_too(self):
        out = self.report('QA5', 'QA5 · Which provider')
        self.assertEqual(self.awaiting(out), 1, out)
        self.assertRegex(out, r'CA-01.*QA5')

    def test_a_struck_q_question_blocks_nothing(self):
        out = self.report('QA5', '~~QA5~~ · CLOSED D1, 2026-09-02')
        self.assertEqual(self.awaiting(out), 0, out)

    def test_a_question_nobody_cites_blocks_nothing(self):
        out = self.report('QA9', 'QA5 · Which provider')
        self.assertEqual(self.awaiting(out), 0, out)


if __name__ == '__main__':
    unittest.main(verbosity=2)
