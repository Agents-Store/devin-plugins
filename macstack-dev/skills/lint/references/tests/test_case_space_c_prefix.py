# -*- coding: utf-8 -*-
"""Пространство кейсов: `CX-01` и `X-01` — один номер, один и тот же вид сущности.

Запуск: python3 skills/lint/references/tests/test_case_space_c_prefix.py

Волна 1 научила читателей id двухбуквенной форме кейса (`CX-01`, `CS-02`, `CZ-14`),
но два места остались на старой грамматике:

  * `Ctx.entity_kind` узнавал кейс без указателя по `^[XSZ]-\\d\\d$`. `CX-01` без
    указателя в этот список не попадал, заголовок выпадал из фильтра сущностей, а на
    документе, где все такие кейсы записаны новой формой, к этому добавлялось 12.0
    «сломанный фильтр»;
  * правило 12.3 сводило к одному номеру `A5` и `QA5`, но не `X-01` и `CX-01`:
    повтор одного кейса в двух написаниях не ловился — а «номера не переиспользуются»
    держится именно на этой проверке.

Обратная сторона: нормализация не должна склеить разные номера. `CA-01` и `A-02` —
разные, `CX-01` и `CS-01` — разные, а `C-01` (одна буква: наследие, где `C` — роль) и
`CC-01` (две: `C` как «case» и `C` как роль) — один номер в двух написаниях, как
сказано в `id_spaces.case`.
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


class Folder(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='macstack-cases-')
        write(os.path.join(self.root, 'macstack.json'),
              json.dumps({'docs': {'language': 'en'}}))

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def cases(self, headings, pointer=False):
        lines = ['<!-- macstack:doc=user_cases lang=en version=1.0 -->', '# Cases', '']
        for h in headings:
            if pointer:
                lines.append('<!-- macstack:ref=cases[id=%s] -->' % h.split(' ')[0])
            lines += ['### %s' % h, '', '- **Priority:** must', '']
        write(os.path.join(self.root, 'client', 'USER-CASES.md'), u'\n'.join(lines))

    def ctx(self):
        return lf.Ctx(self.root)

    def reused(self):
        found, _ = lf.run(self.root, only=['12.3'])
        return [f for f in found if 'reused' in f.message]


class EntityKindOfAPointerlessCase(Folder):
    def kind_of(self, heading):
        self.cases([heading])
        c = self.ctx()
        items = [i for i in c.docs['user_cases'].items if i.level >= 3]
        self.assertEqual(len(items), 1, items)
        return c.entity_kind(items[0])

    def test_the_legacy_one_letter_form_is_a_case(self):
        for h in ('X-01 · Cross-cutting', 'S-02 · Scenario', 'Z-14 · Prohibition'):
            self.assertEqual(self.kind_of(h), 'case', h)

    def test_the_two_letter_form_is_a_case_too(self):
        for h in ('CX-01 · Cross-cutting', 'CS-02 · Scenario', 'CZ-14 · Prohibition'):
            self.assertEqual(self.kind_of(h), 'case', h)

    def test_a_role_case_without_a_pointer_is_still_not_one(self):
        # Кейс роли обязан нести указатель на себя; безуказательной формы у него нет.
        for h in ('CA-01 · Role case', 'A-01 · Legacy role case'):
            self.assertIsNone(self.kind_of(h), h)


class TwelveThree(Folder):
    def test_x_and_cx_are_one_number(self):
        self.cases(['X-01 · Legacy spelling', 'CX-01 · Migrated spelling'], pointer=True)
        got = self.reused()
        self.assertEqual(len(got), 1, got)
        self.assertIn('CX-01', got[0].message)
        self.assertIn('as X-01', got[0].message)

    def test_the_same_holds_for_s_and_z(self):
        self.cases(['S-02 · a', 'CS-02 · b', 'Z-14 · c', 'CZ-14 · d'], pointer=True)
        self.assertEqual(len(self.reused()), 2, self.reused())

    def test_one_letter_c_and_two_letter_cc_are_one_number(self):
        self.cases(['C-01 · Legacy', 'CC-01 · Migrated'], pointer=True)
        self.assertEqual(len(self.reused()), 1, self.reused())

    def test_different_numbers_are_not_glued_together(self):
        self.cases(['CA-01 · a', 'A-02 · b', 'CX-01 · c', 'CS-01 · d', 'CZ-01 · e',
                    'CA-03 · f'], pointer=True)
        self.assertEqual(self.reused(), [], self.reused())

    def test_a_plain_duplicate_is_still_caught(self):
        self.cases(['CX-01 · a', 'CX-01 · b'], pointer=True)
        self.assertEqual(len(self.reused()), 1, self.reused())


if __name__ == '__main__':
    unittest.main(verbosity=2)
