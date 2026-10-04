# -*- coding: utf-8 -*-
"""Заготовка AUTOMATION.md проходит собственный линтер плагина.

Запуск: python3 skills/documents/references/tests/test_seed_lint.py

`seed.py` пишет первую версию client/AUTOMATION.md из macstack.json, и эта версия —
первое, что видит человек после `start`. Если линтер плагина красен на свежей
заготовке, красен он на каждом новом проекте с первой минуты, и ни одной правки
человека за этим нет. Измерено на схемно-валидной спецификации:

  * триггеры `email` и `queue` — два из семи значений `triggers[].type` в схеме —
    не имели записи в `SOURCE_BY_TYPE`; `source` выходил пустым и отбрасывался, а
    контракт требует его у каждого триггера (12.21);
  * задача без блока `human` (чисто машинная, `workflow` без человека) писалась в
    документ с `gate: none`. Такого значения нет в `human.gate` схемы — там
    `approve | input | review | execute`, — а правило 12.22 прямо говорит, что
    машинная половина документу не принадлежит. Итог: «task … is in the document,
    but the spec has no human gate for it» и «a role_task must declare role».

Схема — канон, поэтому ожидание берётся из неё, а не пишется списком в тесте: добавят
в схему восьмой тип триггера — тест покраснеет, пока заготовка его не научится
называть.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.dirname(HERE)
SKILLS = os.path.dirname(os.path.dirname(DOCS))
LINT = os.path.join(SKILLS, 'lint', 'references')
SEED = os.path.join(DOCS, 'seed.py')
LINT_FOLDER = os.path.join(LINT, 'lint_folder.py')
SCHEMA = os.path.join(LINT, 'macstack.schema.json')
CONTRACT = os.path.join(DOCS, 'doc-contracts.json')

sys.path.insert(0, DOCS)
import seed                                                    # noqa: E402


def load(path):
    with io.open(path, encoding='utf-8') as fh:
        return json.load(fh)


def trigger_types():
    """Все значения `triggers[].type`, как их называет схема."""
    return load(SCHEMA)['properties']['triggers']['items']['properties']['type']['enum']


def spec(lang, with_machine_task=True):
    """Схемно-валидная спецификация: все семь типов триггеров и одна машинная задача."""
    triggers = [
        {'id': 'trg-%s' % t.replace('_', '-'), 'name': 'Trigger %s' % t, 'type': t}
        for t in trigger_types()]
    # конфиг, который схема допускает и документ показывает, — расписание и путь
    for t in triggers:
        if t['type'] == 'schedule':
            t['config'] = {'schedule': '0 3 * * *'}
        if t['type'] == 'webhook':
            t['config'] = {'path': '/hooks/x'}
        if t['type'] == 'queue':
            t['config'] = {'queue': 'digest'}
    tasks = [{'id': 'approve-refund', 'name': 'Approve a refund',
              'human': {'role': 'ops', 'gate': 'approve'}}]
    if with_machine_task:
        tasks.append({'id': 'send-digest', 'name': 'Send the digest',
                      'workflow': 'wf-send-digest'})
    return {
        'macstack': '1.0', 'name': 'seed-fixture', 'version': '0.1.0',
        'description': 'A spec carrying every trigger type the schema allows.',
        'docs': {'language': lang},
        'roles': [{'id': 'ops', 'name': 'Operations'}],
        'workflows': [{'id': 'wf-send-digest', 'name': 'Send the digest',
                       'engine': 'script', 'triggers': ['trg-email', 'trg-queue']}],
        'processes': [{'id': 'support', 'name': 'Support', 'type': 'operations',
                       'tasks': tasks}],
        'triggers': triggers,
    }


class SeedAgainstOwnLint(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='macstack-seed-')

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def seeded(self, data):
        with io.open(os.path.join(self.root, 'macstack.json'), 'w', encoding='utf-8') as fh:
            json.dump(data, fh, ensure_ascii=False)
        subprocess.check_output([sys.executable, SEED, self.root, '--only', 'automation'],
                                stderr=subprocess.STDOUT)
        with io.open(os.path.join(self.root, 'client', 'AUTOMATION.md'),
                     encoding='utf-8') as fh:
            return fh.read()

    def lint(self, *rules):
        argv = [sys.executable, LINT_FOLDER, self.root, '--json']
        for r in rules:
            argv += ['--rule', r]
        proc = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertIn(proc.returncode, (0, 1), proc.stderr.decode('utf-8'))
        return json.loads(proc.stdout.decode('utf-8'))

    def test_the_fixture_is_schema_valid(self):
        # Без этого тест доказывал бы «заготовка проходит линтер на мусоре».
        try:
            import jsonschema
        except ImportError:
            self.skipTest('jsonschema is not installed')
        schema = load(SCHEMA)
        cls = jsonschema.validators.validator_for(schema)
        for lang in ('en', 'ru'):
            errors = sorted(cls(schema).iter_errors(spec(lang)), key=str)
            self.assertEqual(errors, [], [e.message for e in errors])

    def test_every_trigger_type_the_schema_allows_gets_a_source(self):
        allowed = load(CONTRACT)['fields']['source']['enum']
        for t in trigger_types():
            got = seed.trigger_source({'type': t})
            self.assertIn(got, allowed,
                          'seed.py не называет `source` для триггера типа %r' % t)

    def test_the_seeded_automation_has_no_automation_findings(self):
        for lang in ('en', 'ru'):
            shutil.rmtree(self.root)
            self.root = tempfile.mkdtemp(prefix='macstack-seed-')
            self.seeded(spec(lang))
            found = self.lint('12.0', '12.21', '12.22')
            self.assertEqual(
                found, [],
                '%s: свежая заготовка красна на собственном линтере:\n%s'
                % (lang, '\n'.join('%s %s:%s %s' % (f['rule'], f['path'], f['line'],
                                                    f['message']) for f in found)))

    def test_a_machine_only_task_is_not_written_into_the_client_document(self):
        text = self.seeded(spec('en'))
        self.assertIn('`approve-refund`', text)
        self.assertNotIn('`send-digest`', text,
                         'машинная задача — не дело AUTOMATION.md (правило 12.22)')

    def test_no_seeded_task_carries_a_gate_the_schema_does_not_know(self):
        allowed = set(load(SCHEMA)['properties']['processes']['items']['properties']
                      ['tasks']['items']['properties']['human']['properties']
                      ['gate']['enum'])
        text = self.seeded(spec('en'))
        label = load(CONTRACT)['fields']['gate']['label']['en']
        values = [line.split(':**', 1)[1].strip().strip('`')
                  for line in text.splitlines() if line.startswith('- **%s:**' % label)]
        self.assertTrue(values, 'в заготовке нет ни одного гейта — тест ничего не проверил')
        self.assertTrue(set(values) <= allowed, values)

    def test_a_spec_with_machine_tasks_only_says_so(self):
        data = spec('en')
        data['processes'][0]['tasks'] = [
            {'id': 'send-digest', 'name': 'Send the digest', 'workflow': 'wf-send-digest'}]
        text = self.seeded(data)
        self.assertNotIn('`send-digest`', text)
        self.assertIn(seed.MISC['en']['no_human_tasks'], text)
        # Правило 12.0 здесь молчать не обязано: оно читает «ни одной сущности вида»
        # как сломанный фильтр, а у проекта без человеческих задач их и нет — то же,
        # что у спецификации без триггеров. Это его собственная граница, не заготовки.
        self.assertEqual(self.lint('12.21', '12.22'), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
