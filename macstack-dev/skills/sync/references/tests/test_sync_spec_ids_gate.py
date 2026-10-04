# -*- coding: utf-8 -*-
"""`sync-spec.py` не пишет в macstack.json то, чего схема не знает, и читает `CZ-`.

Запуск: python3 skills/sync/references/tests/test_sync_spec_ids_gate.py

Два места, оба найдены при разборе дрейфа заготовки и линтера.

1. **Гейт.** `--apply` переносит гейт задачи из документа в `processes[].tasks[].human.gate`
   как есть. Контракт документа допускает `none` («ничей»), а схема — только
   `approve | input | review | execute`, поэтому документ, в который когда-то попало
   `gate: none` (старый `seed.py` писал его машинным задачам), при следующем `--apply`
   превращал валидный macstack.json в невалидный: файл записан, ошибки нет, схема
   отвергает его при следующем чтении. Различие между «показать расхождение» и «записать
   его» уже есть в `mk_change`: расхождение остаётся в отчёте, но `appliable` False.

2. **Запреты.** `compare_cases` отсекает запреты — они живут в `prohibitions[]`, а не в
   `cases[]` — по `startswith('Z-')`. Двухбуквенная форма `CZ-14` под это не попадала, и
   каждый запрет проекта на новой форме id выходил строкой `add case`.

Схема — канон, поэтому допустимые значения гейта читаются из неё, а не списком в тесте.
"""
import importlib.util
import io
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.dirname(HERE)
SCHEMA = os.path.join(os.path.dirname(os.path.dirname(REF)), 'lint', 'references',
                      'macstack.schema.json')


def load_sync_spec():
    # имя файла с дефисом — обычным `import` не взять
    spec = importlib.util.spec_from_file_location('sync_spec', os.path.join(REF, 'sync-spec.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ss = load_sync_spec()


def schema_gates():
    with io.open(SCHEMA, encoding='utf-8') as fh:
        s = json.load(fh)
    human = (s['properties']['processes']['items']['properties']['tasks']['items']
             ['properties']['human'])
    return list(human['properties']['gate']['enum'])


def spec_with_gate(gate):
    human = {'role': 'ops'}
    if gate:
        human['gate'] = gate
    return {'processes': [{'id': 'p', 'tasks': [
        {'id': 'approve-refund', 'name': 'Approve a refund', 'human': human}]}]}


def doc_task(gate):
    return {'id': 'approve-refund', 'name': 'Approve a refund', 'role': 'ops',
            'gate': gate, 'workflow': None}


def gate_change(spec, gate):
    ss.SPEC = spec
    _add, _gone, changed = ss.compare_tasks([doc_task(gate)], spec)
    got = [c for c in changed if c['field'] == 'gate']
    return got[0] if got else None


class GateIsOnlyWrittenWhenTheSchemaKnowsIt(unittest.TestCase):
    def test_a_gate_the_schema_does_not_know_is_reported_not_applied(self):
        spec = spec_with_gate('approve')
        ch = gate_change(spec, 'none')
        self.assertIsNotNone(ch, 'расхождение пропало из отчёта')
        self.assertFalse(ch['appliable'], '`none` записался бы в human.gate')
        self.assertIsNone(ch['apply'])

    def test_it_stays_unapplied_when_the_spec_has_no_gate_yet(self):
        ch = gate_change(spec_with_gate(None), 'none')
        self.assertIsNotNone(ch)
        self.assertFalse(ch['appliable'])

    def test_every_gate_the_schema_knows_is_applied(self):
        gates = schema_gates()
        self.assertEqual(len(gates), 4, gates)         # схема сменила словарь — перечитай тест
        for g in gates:
            spec = spec_with_gate(next(x for x in gates if x != g))
            ch = gate_change(spec, g)
            self.assertIsNotNone(ch, g)
            self.assertTrue(ch['appliable'], g)
            ch['apply']()
            self.assertEqual(spec['processes'][0]['tasks'][0]['human']['gate'], g)

    def test_the_applied_value_is_always_in_the_schema(self):
        allowed = set(schema_gates())
        for g in ('none', 'approve', 'выполнить', '', 'review'):
            spec = spec_with_gate('input')
            ch = gate_change(spec, g or None)
            if ch and ch['appliable']:
                ch['apply']()
            self.assertIn(spec['processes'][0]['tasks'][0]['human']['gate'], allowed, g)


class ProhibitionsAreNotCases(unittest.TestCase):
    def added(self, doc_ids, spec_ids=()):
        doc = [{'id': i, 'name': 'Case %s' % i} for i in doc_ids]
        spec = [{'id': i, 'name': 'Case %s' % i} for i in spec_ids]
        add, _gone, _changed = ss.compare_cases(doc, spec)
        return sorted(a[1] for a in add)

    def test_the_legacy_prohibition_is_skipped(self):
        self.assertEqual(self.added(['Z-14', 'C-01']), ['C-01'])

    def test_the_two_letter_prohibition_is_skipped_too(self):
        self.assertEqual(self.added(['CZ-14', 'CC-01']), ['CC-01'])

    def test_cross_cutting_cases_and_scenarios_are_still_cases(self):
        # `CX` и `CS` — настоящие кейсы (сквозной, сценарий), они живут в cases[];
        # отсекается только запрет.
        self.assertEqual(self.added(['CX-01', 'CS-01', 'CZ-01']), ['CS-01', 'CX-01'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
