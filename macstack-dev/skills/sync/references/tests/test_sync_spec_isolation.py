# -*- coding: utf-8 -*-
"""`sync-spec.py` не пишет в `roles[].isolation` ничего, кроме строки, которую знает схема.

Запуск: python3 skills/sync/references/tests/test_sync_spec_isolation.py

Контракт документа объявлял поле `isolation` булевым («Чужого не видит: да/нет»), а схема
(`roles[].isolation`) — СТРОКА: «Tenant isolation (e.g.: by the company field)». Живая
спецификация несёт строки («own records only (entries via own Einsätze)»), заготовка
(`seed.py`) пишет эту строку в документ как есть — а читатель, встретив в документе
`да`, возвращает `True`. `--apply` записывал бы `True` как JSON `true` в поле, где схема
требует строку: файл записан, ошибки нет, схема отвергает его при следующем чтении.

Правило, как для гейта: показать расхождение можно всегда, записать — только значение,
допустимое схеме. Булево «да/нет» описания изоляции не несёт, поэтому:

  * `да` и в спеке непустая строка — согласие, расхождения нет;
  * `да`, а в спеке изоляции нет — расхождение в отчёте, записывать нечего;
  * `нет`, а в спеке описана изоляция — расхождение в отчёте, не записывается;
  * строка в документе (на латинице) — записывается как есть, как и раньше.

Допустимое читается из схемы, а не списком в тесте.
"""
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.dirname(HERE)
SKILLS = os.path.dirname(os.path.dirname(REF))
SCHEMA = os.path.join(SKILLS, 'lint', 'references', 'macstack.schema.json')
CONTRACT = os.path.join(SKILLS, 'documents', 'references', 'doc-contracts.json')


def load_sync_spec():
    spec = importlib.util.spec_from_file_location('sync_spec', os.path.join(REF, 'sync-spec.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ss = load_sync_spec()


def load(path):
    with io.open(path, encoding='utf-8') as fh:
        return json.load(fh)


def schema_isolation():
    return load(SCHEMA)['properties']['roles']['items']['properties']['isolation']


def doc_role(isolation):
    return {'id': 'ops', 'name': 'Operations', 'cases': None, 'sees': None, 'can': None,
            'isolation': isolation}


def changes(doc_isolation, spec_isolation):
    role = {'id': 'ops', 'name': 'Operations'}
    if spec_isolation is not None:
        role['isolation'] = spec_isolation
    _add, _gone, changed = ss.compare_roles([doc_role(doc_isolation)], [role])
    return [c for c in changed if c['field'] == 'isolation'], role


class BooleanAnswers(unittest.TestCase):
    def test_the_schema_wants_a_string(self):
        # опорный факт: без него «пишем только строку» было бы чьим-то мнением
        self.assertEqual(schema_isolation()['type'], 'string')

    def test_yes_agrees_with_a_described_isolation(self):
        got, _ = changes(True, 'own records only')
        self.assertEqual(got, [], 'да + описанная изоляция — не расхождение')

    def test_yes_over_no_isolation_is_reported_and_not_applied(self):
        got, _ = changes(True, None)
        self.assertEqual(len(got), 1)
        self.assertFalse(got[0]['appliable'], '`true` записался бы в строковое поле')
        self.assertIsNone(got[0]['apply'])

    def test_no_over_a_described_isolation_is_reported_and_not_applied(self):
        got, _ = changes(False, 'own records only')
        self.assertEqual(len(got), 1)
        self.assertFalse(got[0]['appliable'])

    def test_no_over_no_isolation_agrees(self):
        got, _ = changes(False, None)
        self.assertEqual(got, [])


class StringAnswers(unittest.TestCase):
    def test_a_latin_string_is_applied_as_a_string(self):
        got, role = changes('own records only', 'by company')
        self.assertEqual(len(got), 1)
        self.assertTrue(got[0]['appliable'])
        got[0]['apply']()
        self.assertEqual(role['isolation'], 'own records only')
        self.assertIsInstance(role['isolation'], str)

    def test_a_string_in_the_documents_own_script_is_not_applied(self):
        got, _ = changes(u'только свои записи', 'by company')
        self.assertEqual(len(got), 1)
        self.assertFalse(got[0]['appliable'], 'macstack.json всегда латиница')

    def test_a_list_is_not_a_string(self):
        got, _ = changes(['own', 'records'], 'by company')
        self.assertEqual(len(got), 1)
        self.assertFalse(got[0]['appliable'])

    def test_an_appliable_isolation_is_always_what_the_schema_allows(self):
        # общий замок: что бы ни пришло из документа, записываемое — строка схемы
        allowed = {'string': str}[schema_isolation()['type']]
        for dv in (True, False, 'x', u'ы', ['a', 'b'], '', None, 3):
            got, _ = changes(dv, 'by company')
            for c in got:
                if c['appliable']:
                    self.assertIsInstance(c['want'], allowed, repr(dv))


class ContractAgreesWithTheSchema(unittest.TestCase):
    def test_the_contract_does_not_call_isolation_a_boolean(self):
        kind = {'string': 'text'}[schema_isolation()['type']]
        self.assertEqual(load(CONTRACT)['fields']['isolation']['type'], kind)


SPEC = {
    'macstack': '1.0', 'name': 'iso', 'version': '0.1.0', 'description': 'x',
    'docs': {'language': 'en'},
    'roles': [{'id': 'ops', 'name': 'Operations', 'isolation': 'by company'}],
    'processes': [], 'triggers': [],
}

AUTOMATION = u"""<!-- macstack:doc=automation lang=en version=1.0 -->
# Automation

## Roles

<!-- macstack:ref=roles[id=ops] -->
### Operations — `ops`

- **Sees nothing else:** {value}

## Tasks

## Triggers
"""


class EndToEnd(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='macstack-iso-')

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def run_apply(self, spec, written):
        sp = os.path.join(self.root, 'macstack.json')
        with io.open(sp, 'w', encoding='utf-8') as fh:
            json.dump(spec, fh, indent=2)
        os.makedirs(os.path.join(self.root, 'client'))
        with io.open(os.path.join(self.root, 'client', 'AUTOMATION.md'), 'w',
                     encoding='utf-8') as fh:
            fh.write(AUTOMATION.format(value=written))
        subprocess.check_output([sys.executable, os.path.join(REF, 'sync-spec.py'),
                                 self.root, '--apply'], stderr=subprocess.STDOUT)
        return load(sp)

    def test_apply_never_turns_isolation_into_a_boolean(self):
        for written in ('yes', 'no'):
            shutil.rmtree(self.root)
            self.root = tempfile.mkdtemp(prefix='macstack-iso-')
            out = self.run_apply(dict(SPEC), written)
            iso = out['roles'][0].get('isolation')
            self.assertIsInstance(iso, str, '%s -> %r' % (written, iso))

    def test_the_spec_stays_schema_valid(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest('jsonschema is not installed')
        schema = load(SCHEMA)
        cls = jsonschema.validators.validator_for(schema)
        for written in ('yes', 'own records only'):
            shutil.rmtree(self.root)
            self.root = tempfile.mkdtemp(prefix='macstack-iso-')
            out = self.run_apply(dict(SPEC), written)
            errors = [e.message for e in cls(schema).iter_errors(out)]
            self.assertEqual(errors, [], written)


if __name__ == '__main__':
    unittest.main(verbosity=2)
