# -*- coding: utf-8 -*-
"""`reconcile.py` не объявляет сиротами кейсы `CX-`, `CS-`, `CZ-`.

Запуск: python3 skills/sync/references/tests/test_reconcile_reserved.py

Три буквы — `X` сквозное, `S` сценарий, `Z` запрет — зарезервированы и не отдаются
ролям никогда (`doc-contracts.json` -> id_spaces.case). В двухбуквенной форме id кейса
первая буква всегда `C`, а буква вида стоит перед дефисом: `CX-01`, `CS-01`, `CZ-01`.
Сверка брала `c.split('-')[0]` целиком, получала `CX` и сравнивала её с `('X', 'S', 'Z')`.
Так каждый сквозной кейс, сценарий и запрет проекта, переведённого на новую форму,
попадал в строку «кейсов не покрыто ни одним roles[].cases» — дыра, закрыть которую
нечем: ни одной роли эти кейсы принадлежать не должны.

Страж в обратную сторону — кейс роли, которую никто не объявил (`CT-01`), по-прежнему
дыра: иначе тест прошёл бы и на сверке, которая молчит обо всём.
"""
import contextlib
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
import reconcile                                               # noqa: E402


def write(path, text):
    d = os.path.dirname(path)
    if not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, 'w', encoding='utf-8') as fh:
        fh.write(text)


def cases_doc(*ids):
    out = ['<!-- macstack:doc=user_cases lang=en version=1.0 -->', '# User cases', '']
    for i in ids:
        out += ['### %s · Case %s' % (i, i), '', '- **Priority:** critical', '']
    return '\n'.join(out)


class Reconcile(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='macstack-reconcile-')

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def run_on(self, role_globs, *case_ids):
        write(os.path.join(self.root, 'macstack.json'), json.dumps({
            'docs': {'language': 'en'},
            'roles': [{'id': 'coach', 'name': 'Coach', 'cases': role_globs}],
            'lifecycle': {'needs_from_client': []}}))
        write(os.path.join(self.root, 'client', 'USER-CASES.md'), cases_doc(*case_ids))
        for name in ('AUTOMATION', 'UX-UI'):
            write(os.path.join(self.root, 'client', name + '.md'),
                  '<!-- macstack:doc=x lang=en version=1.0 -->\n# Doc\n')
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            reconcile.run(self.root)
        return buf.getvalue()

    def orphans(self, out):
        m = re.search(r'(\d+) кейсов не покрыты ни одним roles\[\]\.cases: (.*)', out)
        return [x.strip() for x in m.group(2).split(',')] if m else []

    def reserved_count(self, out):
        m = re.search(r'ничьих по определению \(X/S/Z\) — (\d+)', out)
        self.assertIsNotNone(m, out)
        return int(m.group(1))

    def test_two_letter_reserved_cases_are_nobodys_by_definition(self):
        out = self.run_on(['CC-*'], 'CC-01', 'CX-01', 'CS-01', 'CZ-01')
        self.assertEqual(self.orphans(out), [], out)
        self.assertEqual(self.reserved_count(out), 3, out)

    def test_the_legacy_one_letter_forms_are_still_reserved(self):
        out = self.run_on(['C-*'], 'C-01', 'X-01', 'S-01', 'Z-01')
        self.assertEqual(self.orphans(out), [], out)
        self.assertEqual(self.reserved_count(out), 3, out)

    def test_a_case_of_an_undeclared_role_is_still_a_hole(self):
        out = self.run_on(['CC-*'], 'CC-01', 'CX-01', 'CT-01')
        self.assertEqual(self.orphans(out), ['CT-01'], out)
        self.assertEqual(self.reserved_count(out), 1, out)

    # Роль и её кейсы мигрируют не одним шагом: roles[].cases может ещё держать `A-*`,
    # когда USER-CASES.md уже пишет `CA-01`, — и наоборот. Это одна роль, а не сирота.
    def test_a_legacy_role_glob_covers_a_migrated_case(self):
        out = self.run_on(['A-*'], 'CA-01')
        self.assertEqual(self.orphans(out), [], out)

    def test_a_migrated_role_glob_covers_a_legacy_case(self):
        out = self.run_on(['CA-*'], 'A-01')
        self.assertEqual(self.orphans(out), [], out)

    def test_mixed_forms_do_not_hide_a_different_role(self):
        out = self.run_on(['A-*'], 'CA-01', 'CB-01')
        self.assertEqual(self.orphans(out), ['CB-01'], out)


if __name__ == '__main__':
    unittest.main(verbosity=2)
