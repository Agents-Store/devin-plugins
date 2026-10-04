# -*- coding: utf-8 -*-
"""Правило 12.1 и ключи `docs.files` схемы rev 18.

Запуск: python3 skills/lint/references/tests/test_docs_files_keys.py

12.1 строит перечень ключей `docs.files`, которые обязан называть проект, из
ВСТРОЕННОЙ копии схемы: «ключ есть в схеме и есть файл на диске — значит, запись
обязательна». Схема rev 18 добавила в `docs.files` четыре ключа, которые контракт
документов знал и раньше — `ledger`, `requirements`, `review`, `inbox_manifest`, — и
пометила `log` устаревшим псевдонимом `ledger`. Копия обновилась, и правило, не
менявшееся ни на строку, потребовало эти записи у каждого v3-проекта: живой проект
получил три новых ошибки на исправной папке (`ledger`, `requirements`,
`inbox_manifest`), хотя схема их не требует — объект `files` открыт, а `required` пуст.

Ошибка на исправном файле — та находка, из-за которой линтер перестают читать, поэтому:

  * ключ, который схема объявила только в rev 18, у проекта, не знавшего о нём, — это
    ПРЕДУПРЕЖДЕНИЕ с исправлением, а не ошибка;
  * `log` — псевдоним `ledger`: запись под любым из двух имён закрывает вопрос
    (и предупреждение называет устаревшее имя и его замену);
  * ключи, которые схема знала и до rev 18, остаются ошибкой — иначе правило
    разучилось бы ловить то, ради чего написано.

Отдельно: правило не вправе читать ключ документа, которого нет в контракте. В
`rules_process.py` жила функция, читавшая `c.text.get('log')`; такого документа в
контракте нет с тех пор, как журнал стал `ledger`, поэтому она всегда возвращала
пустой список, и ничто этого не замечало.
"""
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
LINT = os.path.dirname(HERE)
DOCS = os.path.normpath(os.path.join(LINT, '..', '..', 'documents', 'references'))
sys.path.insert(0, LINT)
import lint_folder as lf                                       # noqa: E402

REV18_KEYS = ('ledger', 'requirements', 'review', 'inbox_manifest')


def load(path):
    with io.open(path, encoding='utf-8') as fh:
        return json.load(fh)


CONTRACT = load(os.path.join(DOCS, 'doc-contracts.json'))
SCHEMA = load(os.path.join(LINT, 'macstack.schema.json'))


def write(path, text=u''):
    d = os.path.dirname(path)
    if not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, 'w', encoding='utf-8') as fh:
        fh.write(text)


def fixed_documents():
    """{contract key: path} для документов с фиксированным путём."""
    return dict((k, d['path']) for k, d in CONTRACT['documents'].items()
                if d.get('path') and '<' not in d['path'])


def schema_file_keys():
    return set(SCHEMA['properties']['docs']['properties']['files']['properties'])


class Folder(unittest.TestCase):
    """Папка `macstack/` v3: каждый документ контракта на месте, спека называет часть."""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='macstack-files-')
        for rel in fixed_documents().values():
            write(os.path.join(self.root, rel))
        # папки обязаны быть, даже если в них нет документа с фиксированным путём
        for d in ('client', 'generated', 'inbox', 'history'):
            if not os.path.isdir(os.path.join(self.root, d)):
                os.makedirs(os.path.join(self.root, d))

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def spec(self, keys):
        files = dict((k, {'path': fixed_documents()[k]}) for k in keys)
        write(os.path.join(self.root, 'macstack.json'),
              json.dumps({'docs': {'language': 'en', 'files': files}}))

    def lint(self):
        found, _ = lf.run(self.root, only=['12.1'], warnings=True)
        self.assertIsNotNone(found, 'линтер не смог загрузить папку')
        return found

    def named_in(self, found, key):
        return [f for f in found if re.search(r'\b%s\b' % key, f.message)]


def pre_rev18_keys():
    """Что называл проект до rev 18: всё, что схема знает, кроме четырёх новых."""
    return sorted(k for k in fixed_documents()
                  if k in schema_file_keys() and k not in REV18_KEYS)


class TheMirrorIsRev18(unittest.TestCase):
    def test_schema_declares_the_four_keys_and_deprecates_log(self):
        props = SCHEMA['properties']['docs']['properties']['files']['properties']
        for k in REV18_KEYS:
            self.assertIn(k, props, 'встроенная копия схемы старше rev 18: нет %s' % k)
        self.assertTrue(props['log'].get('deprecated'),
                        '`log` в схеме должен быть помечен устаревшим')

    def test_every_fixed_path_document_of_the_contract_is_a_schema_key(self):
        # Иначе 12.1 не может спросить запись об этом документе, и дрейф между
        # контрактом и схемой снова станет невидимым.
        missing = sorted(k for k in fixed_documents() if k not in schema_file_keys())
        self.assertEqual(missing, [], 'контракт знает документы, которых нет в схеме')


class ProjectBeforeRev18(Folder):
    """Живой v3-проект: записи только о тех ключах, что были до rev 18."""

    def test_no_error_on_a_project_that_never_heard_of_the_new_keys(self):
        self.spec(pre_rev18_keys())
        errors = [f for f in self.lint() if f.severity == lf.ERROR]
        self.assertEqual(errors, [], '\n'.join(f.message for f in errors))

    def test_the_new_keys_are_asked_for_as_warnings_with_the_fix(self):
        self.spec(pre_rev18_keys())
        found = self.lint()
        for key in ('ledger', 'requirements', 'inbox_manifest'):
            hit = self.named_in(found, key)
            self.assertEqual(len(hit), 1, '%s: %r' % (key, found))
            self.assertEqual(hit[0].severity, lf.WARNING, key)
            self.assertIn('docs.files', hit[0].message)

    def test_a_key_the_schema_knew_before_rev18_is_still_an_error(self):
        keys = [k for k in pre_rev18_keys() if k != 'overview']
        self.spec(keys)
        hit = self.named_in(self.lint(), 'overview')
        self.assertEqual([f.severity for f in hit], [lf.ERROR], hit)


class ProjectOnRev18(Folder):
    def test_a_project_naming_everything_is_clean(self):
        self.spec(sorted(k for k in fixed_documents() if k in schema_file_keys()))
        self.assertEqual(self.lint(), [])

    def test_log_is_accepted_as_the_ledger_and_named_deprecated(self):
        self.spec(pre_rev18_keys() + ['requirements', 'inbox_manifest'])
        raw = load(os.path.join(self.root, 'macstack.json'))
        raw['docs']['files']['log'] = {'path': 'history/ledger.jsonl'}
        write(os.path.join(self.root, 'macstack.json'), json.dumps(raw))
        found = self.lint()
        self.assertEqual([f for f in found if f.severity == lf.ERROR], [], found)
        for f in found:
            self.assertNotIn('does not name ledger', f.message,
                             '`log` не закрыл запись о `ledger`: %s' % f.message)
        hit = self.named_in(found, 'log')
        self.assertEqual(len(hit), 1, found)
        self.assertEqual(hit[0].severity, lf.WARNING)
        self.assertIn('ledger', hit[0].message, 'предупреждение не называет замену')


class NoRuleReadsAnUnknownDocument(unittest.TestCase):
    """Ключ документа в правиле обязан быть в контракте — иначе правило слепо."""

    READS = [
        re.compile(r"""\bc\.(?:text|docs|files)(?:\.get\(|\[)\s*['"](\w+)['"]"""),
        re.compile(r"""\bc\.path_of\(\s*['"](\w+)['"]"""),
        re.compile(r"""\bc\.entities_of\(\s*['"](\w+)['"]"""),
        re.compile(r"""\b_entity_decl\(\s*c\s*,\s*['"](\w+)['"]"""),
    ]

    def test_every_document_key_a_rule_reads_exists_in_the_contract(self):
        known = set(CONTRACT['documents'])
        bad = []
        for name in sorted(os.listdir(LINT)):
            if not (name.startswith('rules_') or name == 'lint_folder.py') \
                    or not name.endswith('.py'):
                continue
            with io.open(os.path.join(LINT, name), encoding='utf-8') as fh:
                for n, line in enumerate(fh, 1):
                    if line.lstrip().startswith('#'):
                        continue
                    for rx in self.READS:
                        for m in rx.finditer(line):
                            if m.group(1) not in known:
                                bad.append('%s:%d reads %r' % (name, n, m.group(1)))
        self.assertEqual(bad, [], 'документ, которого нет в контракте:\n' + '\n'.join(bad))


if __name__ == '__main__':
    unittest.main(verbosity=2)
