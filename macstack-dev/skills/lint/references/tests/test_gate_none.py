# -*- coding: utf-8 -*-
"""`gate: none` не пишется никогда; написанный — предупреждение с исправлением.

Запуск: python3 skills/lint/references/tests/test_gate_none.py

Решение владельца (2026-10-04). В схеме `human.gate` — `approve | input | review |
execute`, и `none` там нет и не будет: задача, которая только запускает workflow, не
имеет блока `human` вовсе, а блок `human` означает, что в цепочке есть человек. Контракт
документа при этом допускал `none` («ничей»), `migrate.py` писал его на каждую задачу с
пустой ячейкой гейта, а правило 12.22 за такой документ ставило ОШИБКУ — хотя ошибся не
автор документа, а инструмент, который документ создал.

Теперь:

  * `none` убран из `fields.gate.enum` контракта; перечень гейтов контракта совпадает с
    `human.gate` схемы (схема — канон, поэтому тест читает её, а не список);
  * документ, в котором `gate: none` уже стоит, получает ПРЕДУПРЕЖДЕНИЕ 12.22 с
    исправлением — не ошибку: ломать существующие файлы из-за чужой ошибки нельзя;
  * расхождение гейта настоящим значением — по-прежнему ошибка (охранный тест), как и
    задача, которая есть в спеке и не названа в документе.
"""
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
LINT = os.path.dirname(HERE)
DOCS = os.path.normpath(os.path.join(LINT, '..', '..', 'documents', 'references'))
sys.path.insert(0, LINT)
import lint_folder as lf                                       # noqa: E402


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


SPEC = {
    'docs': {'language': 'en'},
    'roles': [{'id': 'ops', 'name': 'Operations'}],
    'workflows': [{'id': 'wf-x', 'name': 'X', 'engine': 'script'}],
    'processes': [{'id': 'support', 'name': 'Support', 'type': 'operations', 'tasks': [
        {'id': 'approve-refund', 'name': 'Approve a refund',
         'human': {'role': 'ops', 'gate': 'approve'}},
        {'id': 'send-digest', 'name': 'Send the digest', 'workflow': 'wf-x'}]}],
    'triggers': [],
}


def automation(tasks):
    """AUTOMATION.md v3: роль, процесс и перечисленные задачи. tasks = [(id, role, gate)]."""
    out = ['<!-- macstack:doc=automation lang=en version=1.0 -->', '# Automation', '',
           '## Roles', '',
           '<!-- macstack:ref=roles[id=ops] -->', '### Operations — `ops`', '',
           '## Tasks', '',
           '<!-- macstack:ref=processes[id=support] -->', '### Support — `support`', '']
    for tid, role, gate in tasks:
        out += ['<!-- macstack:ref=processes[id=support].tasks[id=%s] -->' % tid,
                '#### Task %s — `%s`' % (tid, tid), '',
                '- **Who does it:** `%s`' % role,
                '- **What the person must do:** %s' % gate, '',
                '**What happens:**', 'Something.', '']
    out += ['## Triggers', '']
    return '\n'.join(out)


class Folder(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='macstack-gate-')
        write(os.path.join(self.root, 'macstack.json'), json.dumps(SPEC))

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def doc(self, tasks):
        write(os.path.join(self.root, 'client', 'AUTOMATION.md'), automation(tasks))

    def lint(self):
        found, _ = lf.run(self.root, only=['12.22'], warnings=True)
        self.assertIsNotNone(found, 'линтер не смог загрузить папку')
        return found


class GateNoneInADocument(Folder):
    def test_the_baseline_is_clean(self):
        self.doc([('approve-refund', 'ops', '`approve`')])
        self.assertEqual(self.lint(), [])

    def test_none_in_the_spec_too_does_not_advise_copying_none(self):
        # Spec `human.gate: none` is itself schema-invalid; "set it to 'none'" would
        # never clear the warning. The fix must point at the spec.
        spec = json.loads(json.dumps(SPEC))
        spec['processes'][0]['tasks'][0]['human']['gate'] = 'none'
        write(os.path.join(self.root, 'macstack.json'), json.dumps(spec))
        self.doc([('approve-refund', 'ops', '`none`')])
        found = self.lint()
        self.assertEqual([(f.rule, f.severity) for f in found], [('12.22', lf.WARNING)], found)
        self.assertNotIn("set it to 'none'", found[0].message)
        self.assertIn('macstack.json', found[0].message)

    def test_none_where_the_spec_has_a_real_gate_is_a_warning_naming_the_real_one(self):
        self.doc([('approve-refund', 'ops', '`none`')])
        found = self.lint()
        self.assertEqual([(f.rule, f.severity) for f in found], [('12.22', lf.WARNING)],
                         found)
        self.assertIn('approve', found[0].message)
        self.assertIn('approve-refund', found[0].message)

    def test_none_on_a_machine_task_is_a_warning_telling_to_remove_the_entry(self):
        # то, что писал старый seed: машинная задача с гейтом none и ролью
        self.doc([('approve-refund', 'ops', '`approve`'), ('send-digest', 'ops', '`none`')])
        found = self.lint()
        self.assertEqual([f.severity for f in found], [lf.WARNING], found)
        msg = found[0].message
        self.assertIn('send-digest', msg)
        self.assertIn('gate: none', msg)
        self.assertIn('remove', msg)
        self.assertIn('macstack.json', msg)

    def test_none_is_not_also_reported_as_an_error(self):
        self.doc([('approve-refund', 'ops', '`none`'), ('send-digest', 'ops', '`none`')])
        self.assertEqual([f.severity for f in self.lint()], [lf.WARNING] * 2)


class GuardsThatMustKeepFiring(Folder):
    def test_a_different_real_gate_is_still_an_error(self):
        self.doc([('approve-refund', 'ops', '`review`')])
        found = self.lint()
        self.assertEqual([f.severity for f in found], [lf.ERROR], found)
        self.assertIn('review', found[0].message)

    def test_a_machine_task_with_a_real_gate_is_still_an_error(self):
        self.doc([('approve-refund', 'ops', '`approve`'), ('send-digest', 'ops', '`input`')])
        found = self.lint()
        self.assertEqual([f.severity for f in found], [lf.ERROR], found)

    def test_a_human_task_missing_from_the_document_is_still_an_error(self):
        self.doc([])
        found = self.lint()
        self.assertEqual([f.severity for f in found], [lf.ERROR], found)
        self.assertIn('approve-refund', found[0].message)


class ContractAndSchemaAgree(unittest.TestCase):
    def test_none_is_not_a_gate(self):
        self.assertNotIn('none', CONTRACT['fields']['gate']['enum'])

    def test_the_contract_gates_are_the_schema_gates(self):
        human = (SCHEMA['properties']['processes']['items']['properties']['tasks']['items']
                 ['properties']['human'])
        schema_gates = set(human['properties']['gate']['enum'])
        self.assertNotIn('none', schema_gates)
        self.assertEqual(set(CONTRACT['fields']['gate']['enum']), schema_gates)

    def test_the_value_labels_name_no_none(self):
        labels = CONTRACT['fields']['gate'].get('value_label') or {}
        for lang, table in labels.items():
            self.assertNotIn('none', table, lang)


if __name__ == '__main__':
    unittest.main(verbosity=2)
