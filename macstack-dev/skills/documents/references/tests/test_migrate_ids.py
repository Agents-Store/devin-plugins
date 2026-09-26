# -*- coding: utf-8 -*-
"""Перевод id на новую форму переименовывает объявленное и НИЧЕГО больше.

Два способа сделать эту миграцию неправильно, и оба измерены на живом проекте:

1. **Слепой regex.** `^[A-Z]-\\d{2}$` совпадает не только с нашими кейсами. На
   живом проекте по той же форме записаны id ЧУЖОГО документа — немецкого
   технического задания заказчика (`E-05`, `A-08`, `NF-07`). Переименовав их, мы
   порвали бы ссылку на бумагу, которой не владеем, и молча.

2. **Забыть про неизменяемое.** Первая версия скрипта сравнивала путь с началом
   строки, а `inbox/` и `history/handoffs/` лежат ВНУТРИ `macstack/` — проверка
   не срабатывала ни разу. Разница измерена: 9041 замена против 2964. Две трети
   всех совпадений сидели в пакетах, уже отправленных заказчику, где id — это то,
   что он прочитал, и переписывать их задним числом значит рассинхронить его
   копию с нашей без единого следа.
"""
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), 'migrate_ids.py')


def write(path, text):
    d = os.path.dirname(path)
    if not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def read(path):
    return io.open(path, encoding='utf-8').read()


class MigrateIds(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='macstack-migrate-')
        ms = os.path.join(self.root, 'macstack')
        write(os.path.join(ms, 'client', 'USER-CASES.md'),
              u'### C-14 · Сообщить о проблеме\n\n### T-19 · Табель\n')
        write(os.path.join(ms, 'client', 'OPEN-QUESTIONS.md'),
              u'### A27 · Роли на смене\n\n### A2 · Реквизиты\n\n### B1 · Отложенное\n')
        write(os.path.join(ms, 'history', 'TASKS.md'),
              u'Закрывает `C-14`. Заблокирована `A27`. Задача M15-T11.\n')
        write(os.path.join(self.root, 'tests', 'a.spec.ts'),
              u"it('делает своё дело (C-14)', () => {})\n")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def run_script(self, *args):
        return subprocess.check_output(
            [sys.executable, SCRIPT, self.root] + list(args),
            stderr=subprocess.STDOUT).decode('utf-8')

    def test_declared_ids_are_renamed_everywhere_they_are_cited(self):
        self.run_script('--apply')
        tasks = read(os.path.join(self.root, 'macstack', 'history', 'TASKS.md'))
        self.assertIn('CC-14', tasks)
        self.assertIn('QA27', tasks)
        self.assertIn('M15-T11', tasks, u'задача не должна меняться — M это веха')
        self.assertIn('(CC-14)', read(os.path.join(self.root, 'tests', 'a.spec.ts')))

    def test_both_a_short_and_a_long_id_sharing_a_prefix_survive(self):
        # `A2` и `A27` объявлены оба. Опасность — что короткий съест префикс
        # длинного. Проверяется на тексте, где стоят ОБА: если бы съел, вместо
        # `QA2` и `QA27` вышло бы `QA2` и `QA2` с висящей семёркой.
        p = os.path.join(self.root, 'macstack', 'history', 'DECISIONS.md')
        write(p, u'Вопрос A2 про реквизиты и вопрос A27 про роли.\n')
        self.run_script('--apply')
        got = read(p)
        self.assertIn(u'Вопрос QA2 про реквизиты', got)
        self.assertIn(u'вопрос QA27 про роли', got)

    def test_a_lookalike_from_someone_elses_document_is_left_alone(self):
        # Ровно та форма, но НЕ объявлено заголовком в USER-CASES.md.
        p = os.path.join(self.root, 'macstack', 'history', 'DECISIONS.md')
        write(p, u'По §14 UStG, требования `E-05`, `A-08` и `NF-07` из ТЗ заказчика.\n')
        self.run_script('--apply')
        kept = read(p)
        for foreign in (u'E-05', u'A-08', u'NF-07'):
            self.assertIn(foreign, kept)
        self.assertNotIn(u'CE-05', kept)
        self.assertNotIn(u'CA-08', kept)

    def test_material_already_sent_to_the_client_is_never_rewritten(self):
        sent = os.path.join(self.root, 'macstack', 'history', 'handoffs', 'p.html')
        raw = os.path.join(self.root, 'macstack', 'inbox', 'brief.md')
        write(sent, u'<p>Кейс C-14, вопрос A27</p>\n')
        write(raw, u'Кейс C-14 из письма клиента\n')
        self.run_script('--apply')
        self.assertIn(u'C-14', read(sent))
        self.assertNotIn(u'CC-14', read(sent))
        self.assertIn(u'C-14', read(raw))
        self.assertNotIn(u'CC-14', read(raw))

    def test_an_open_item_id_is_left_alone_outside_macstack(self):
        """`A4` вне macstack/ — это размер страницы, а не вопрос заказчику.

        Измерено на живом проекте: `<Page size="A4">` в генераторе счёта и
        `export const A4 = {width: 595.28, …}` в тестовом хелпере. Переименовав
        любое из них, мы бы сломали выпуск PDF молча — тип не возражает, строка
        просто перестаёт быть известным форматом бумаги.
        """
        pdf = os.path.join(self.root, 'src', 'InvoiceDocument.tsx')
        write(pdf, u'export const A4 = { width: 595.28 }\n<Page size="A4" />\n// см. вопрос A2\n')
        self.run_script('--apply')
        got = read(pdf)
        self.assertIn(u'size="A4"', got)
        self.assertIn(u'const A4 =', got)
        self.assertNotIn(u'QA4', got)
        self.assertNotIn(u'QA2', got, u'вне macstack/ вопросы не трогаются вовсе')

    def test_a_case_id_is_renamed_even_outside_macstack(self):
        """Кейс несёт дефис — форма своеобразная, коллизий не даёт.

        Обратная сторона предыдущего случая: без неё «не трогать вне macstack»
        зелено на скрипте, который не трогает ничего.
        """
        src = os.path.join(self.root, 'src', 'notes.ts')
        write(src, u"// закрывает C-14\nconst msg = 'Beleg unverändert (T-19).'\n")
        self.run_script('--apply')
        got = read(src)
        self.assertIn(u'CC-14', got)
        self.assertIn(u'CT-19', got)

    def test_role_globs_in_the_spec_follow_the_cases(self):
        """`roles[].cases` — шаблон `C-*`, а не id, и регулярка по id его не видит.

        Без этой правки линт после миграции сообщает «кейсы C-* не принадлежат
        ни одной роли» и «glob 'C-*' не совпадает ни с одним заголовком»: роль
        молча теряет свои кейсы, а документы выглядят исправными.
        """
        spec = os.path.join(self.root, 'macstack', 'macstack.json')
        write(spec, u'{"roles": [{"id": "coach", "cases": ["C-*"]},'
                    u' {"id": "centre", "cases": ["T-*"]}]}\n')
        self.run_script('--apply')
        got = read(spec)
        self.assertIn(u'"CC-*"', got)
        self.assertIn(u'"CT-*"', got)

    def test_showing_changes_nothing(self):
        before = read(os.path.join(self.root, 'macstack', 'history', 'TASKS.md'))
        out = self.run_script()
        self.assertIn(u'--apply', out)
        self.assertEqual(before, read(os.path.join(self.root, 'macstack', 'history', 'TASKS.md')))

    def test_running_twice_does_not_double_the_prefix(self):
        self.run_script('--apply')
        again = self.run_script('--apply')
        self.assertIn(u'уже переведён', again)  # ноль замен при непустой карте
        tasks = read(os.path.join(self.root, 'macstack', 'history', 'TASKS.md'))
        self.assertIn('CC-14', tasks)
        self.assertNotIn('CCC-14', tasks)
        self.assertNotIn('QQA27', tasks)


if __name__ == '__main__':
    unittest.main(verbosity=2)
