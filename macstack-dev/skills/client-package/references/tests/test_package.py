#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Пакет — единственный артефакт этого плагина, который ИСПОЛНЯЕТСЯ у читателя.

Запуск: python3 skills/client-package/references/tests/test_package.py

Почему эти тесты появились только 2026-08-27. До них проверок у `client-package`
не было ни одной, и кнопка «Собрать мои ответы» не работала НИ В ОДНОМ пакете за
всё время жизни плагина: скрипт читал `PKG_DATE` и `COUNTED`, которых сборщик
никогда не выводил, и `save()` умирал на `ReferenceError` первой же строкой —
до того, как что-либо попадало в поле. Элемента `#cnt`, куда пишется число
собранных ответов, в разметке не существовало вовсе.

Не заметили потому, что исключение в обработчике клика невидимо нажавшему: поле
просто остаётся пустым. В журнале это выглядело как «клиент не отвечает» —
тринадцать выданных пакетов и ноль ответов, — и было записано именно так.

**Отсюда правило, которое держат эти тесты: страница, содержащая скрипт,
проверяется исполнением, а не чтением.** Всё, что проверялось раньше, работало с
текстом страницы: считало пункты, искало утечки, сверяло разметку. Ни одна
проверка не спросила, запустится ли скрипт.

Зависимостей нет — плагин ими не пользуется намеренно. Класс дефекта («скрипт
читает то, чего страница не объявляет») ловится статически и полностью. Прогон в
настоящем браузере есть в `test_button_browser.py`; он пропускается там, где
Playwright не установлен, поэтому не может стать зависимостью.
"""
import io, json, os, re, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.dirname(HERE)
sys.path.insert(0, REF)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(REF)),
                                'documents', 'references'))
import package as pk                                              # noqa: E402

CORPUS = os.path.join(os.path.dirname(os.path.dirname(REF)),
                      'documents', 'references', 'tests', 'corpus')

# Идентификаторы, которые скрипт вправе читать, не объявляя: их даёт браузер.
BROWSER = {
    'JSON', 'Math', 'Date', 'Object', 'Array', 'String', 'Number', 'Boolean',
    'RegExp', 'Promise', 'Error', 'NaN', 'Infinity',
}


def build_root():
    """Минимальный `macstack/` из общего корпуса документов.

    Корпус один на весь плагин — второй набор примерных документов разошёлся бы
    с первым, и разошёлся бы молча.
    """
    root = tempfile.mkdtemp(prefix='macstack-pkg-')
    os.makedirs(os.path.join(root, 'client'))
    os.makedirs(os.path.join(root, 'history', 'handoffs'))
    for f in os.listdir(CORPUS):
        if f.endswith('.md') and f != 'README.md':
            shutil.copy(os.path.join(CORPUS, f), os.path.join(root, 'client', f))
    io.open(os.path.join(root, 'macstack.json'), 'w', encoding='utf-8').write(
        json.dumps({'name': 'bike-rental',
                    'identity': {'title': 'Прокат велосипедов'},
                    'docs': {'language': 'ru', 'files': {
                        'user_cases': {'version': '1.0'},
                        'open_questions': {'version': '1.0'},
                        'ux_ui': {'version': '1.0'},
                        'automation': {'version': '1.0'},
                        'overview': {'version': '1.0'},
                        'handbook': {'version': '1.0'}}}},
                   ensure_ascii=False, indent=2))
    io.open(os.path.join(root, 'history', 'ledger.jsonl'), 'w',
            encoding='utf-8').write('')
    return root


class PageScript(unittest.TestCase):
    """Скрипт страницы должен ЗАПУСКАТЬСЯ, а не просто присутствовать."""

    @classmethod
    def setUpClass(cls):
        cls.root = build_root()
        cls.page, _, cls.counted, _ = pk.build(cls.root, '2026-01-02', 'x')
        cls.art, _, _, _ = pk.build(cls.root, '2026-01-02', 'x', artifact=True)
        cls.js = re.search(r'<script>(.*?)</script>', cls.page, re.S).group(1)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def test_every_constant_the_script_reads_is_declared(self):
        """ЭТО тот самый дефект: `PKG_DATE` читалась и никогда не объявлялась.

        Соглашение плагина — вставляемая константа пишется ЗАГЛАВНЫМИ. Проверяем
        каждую такую, а не список известных: список пришлось бы помнить, и
        следующая забытая константа прошла бы молча, ровно как эта.
        """
        used = set(re.findall(r'\b([A-Z][A-Z0-9_]{2,})\b', self.js)) - BROWSER
        declared = set(re.findall(r'\bvar\s+([A-Z][A-Z0-9_]{2,})\s*=', self.js))
        declared |= set(re.findall(r',\s*([A-Z][A-Z0-9_]{2,})\s*=', self.js))
        self.assertEqual(used - declared, set(),
                         'скрипт читает необъявленное — нажатие упадёт на '
                         'ReferenceError и не покажет ничего')

    def test_every_element_the_script_looks_up_exists(self):
        """`#cnt` искался, а его в разметке не было. Молча: поиск вернул null."""
        want = set(re.findall(r"getElementById\('([^']+)'\)", self.js))
        want |= set(re.findall(r"querySelector\('#([^']+)'\)", self.js))
        self.assertTrue(want, 'скрипт не ищет ни одного элемента — проверка мертва')
        for i in sorted(want):
            self.assertIn('id="%s"' % i, self.page,
                          'скрипт ищет #%s, а страница его не содержит' % i)

    def test_button_is_bound_from_script_not_by_attribute(self):
        """Инлайновый `onclick` запрещён политикой безопасности строже той, при
        которой сам скрипт ещё выполняется, — и кнопка молчит без сообщения."""
        self.assertIn("addEventListener('click'", self.js)
        markup = re.sub(r'<script>.*?</script>', '', self.page, flags=re.S)
        self.assertNotIn('onclick=', markup)

    def test_collect_reads_the_sections_the_page_actually_writes(self):
        """Селектор скрипта и разметка — два описания одного, и они расходятся.

        Прошлый раз разошлись при переходе на карточки: скрипт продолжал
        спрашивать `tr[data-id]` и собирал ноль ответов, потому что пустой
        список — тоже список.
        """
        sel = re.search(r"querySelectorAll\('([^']+)'\)", self.js).group(1)
        tag = sel.split('.')[0] or 'section'
        cls = re.search(r'\.([a-z-]+)', sel).group(1)
        self.assertRegex(self.page, r'<%s class="%s[^"]*"[^>]*data-id=' % (tag, cls),
                         'скрипт ищет «%s», а страница пишет другое' % sel)

    def test_script_is_valid_javascript(self):
        """Синтаксическая ошибка ломает скрипт целиком и так же молча.

        Пропускается там, где нет `node`: это единственная проверка, которой
        нужен посторонний исполнитель, и делать его зависимостью плагина ради
        неё нельзя. Всё остальное в этом файле — чистый Python.
        """
        node = shutil.which('node')
        if not node:
            self.skipTest('node не установлен')
        d = tempfile.mkdtemp()
        try:
            f = os.path.join(d, 's.js')
            io.open(f, 'w', encoding='utf-8').write(self.js)
            r = subprocess.run([node, '--check', f], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_artifact_is_a_body_and_the_file_is_a_page(self):
        """Тело артефакта нельзя открыть в браузере и нельзя отдать клиенту."""
        for t in ('<!doctype', '<html', '<body>'):
            self.assertNotIn(t, self.art.lower(), 'в теле артефакта есть %s' % t)
        self.assertIn('<!doctype html>', self.page.lower())
        self.assertIn('<title>', self.art, 'без <title> артефакт безымянный')
        # Скрипт и кнопка обязаны быть в ОБОИХ: клиент отвечает и на странице.
        for doc, what in ((self.page, 'файл'), (self.art, 'артефакт')):
            self.assertIn('id="go"', doc, '%s без кнопки' % what)
            self.assertIn('<script>', doc, '%s без скрипта' % what)


class Selection(unittest.TestCase):
    """`--only` / `--skip` делят пакет, ничего не теряя и не задваивая."""

    @classmethod
    def setUpClass(cls):
        cls.root = build_root()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def test_split_partitions_the_package(self):
        _, _, whole, _ = pk.build(self.root, '2026-01-02', 'x')
        _, _, without, _ = pk.build(self.root, '2026-01-02', 'x', skip='questions')
        _, _, only, _ = pk.build(self.root, '2026-01-02', 'x', only='questions')
        self.assertEqual(whole, without + only,
                         'раздел потерян или посчитан дважды')

    def test_one_section_package_names_itself_after_that_section(self):
        doc, _, _, _ = pk.build(self.root, '2026-01-02', 'x', artifact=True,
                                only='questions')
        title = re.search(r'<title>(.*?)</title>', doc).group(1)
        h1 = re.search(r'<h1>(.*?)</h1>', doc).group(1)
        self.assertIn('Вопросы', title)
        self.assertEqual(h1, 'Вопросы к вам')
        self.assertEqual(doc.count('<h2>'), 0, 'заголовок раздела задвоен с <h1>')

    def test_questions_are_what_the_client_owes_not_what_we_deferred(self):
        """§B выпадал лишь потому, что его заголовки набраны через тире."""
        doc, _, _, _ = pk.build(self.root, '2026-01-02', 'x', artifact=True,
                                only='questions')
        ids = re.findall(r'data-id="([^"]+)"', doc)
        self.assertTrue(ids, 'раздел вопросов пуст — проверка ничего не значит')
        self.assertEqual([i for i in ids if i.startswith('B')], [],
                         'наша отложенная работа ушла клиенту вопросом')

    def test_unknown_section_is_refused(self):
        for bad in ('question', 'screens,nonsense'):
            with self.assertRaises(SystemExit):
                pk.build(self.root, '2026-01-02', 'x', only=bad)

    def test_scaffolder_prompt_is_not_content(self):
        """Незаполненный HANDBOOK — заголовки с просьбой, обращённой к НАМ."""
        doc, _, _, data = pk.build(self.root, '2026-01-02', 'x')
        self.assertNotIn('Опишите шаги', doc)
        self.assertNotIn('handbook', [k for k, v in data if v])


class Cli(unittest.TestCase):
    def test_unknown_flag_is_refused_not_ignored(self):
        """Оболочка склеила аргументы в один — ни один ключ не узнался, и пакет
        собрался по умолчанию, записав себя в журнал состоявшимся кругом."""
        root = build_root()
        try:
            for argv in (['--slugg', 'x'], ['--slug x --only questions']):
                r = subprocess.run([sys.executable, os.path.join(REF, 'package.py'),
                                    root] + argv, capture_output=True, text=True)
                self.assertEqual(r.returncode, 2, argv)
                self.assertIn('неизвестн', r.stdout + r.stderr)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_record_url_writes_the_ledger_row(self):
        """URL артефакта вписывается командой, а не правкой JSONL руками."""
        root = build_root()
        try:
            subprocess.run([sys.executable, os.path.join(REF, 'package.py'), root,
                            '--slug', 'p', '--artifact'], capture_output=True)
            r = subprocess.run([sys.executable, os.path.join(REF, 'package.py'), root,
                                '--record-url', 'https://example.invalid/a',
                                '--handoff', '%s-p-artifact.html' % pk._today(root)],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            rows = [json.loads(l) for l in
                    io.open(os.path.join(root, 'history', 'ledger.jsonl'),
                            encoding='utf-8').read().splitlines() if l.strip()]
            urls = [x.get('url') for x in rows if x.get('kind') == 'handoff']
            self.assertIn('https://example.invalid/a', urls)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_answers_from_the_button_are_readable_back(self):
        """Обе половины петли, одной проверкой: формат, который печатает кнопка,
        должен разбираться `--read`. Раньше их связывало только намерение."""
        root = build_root()
        try:
            payload = {'package': 'x', 'date': '2026-01-02', 'answers': [
                {'id': 'A1', 'answer': 'ok', 'comment': ''},
                {'id': 'A2', 'answer': 'no', 'comment': 'не так'},
                {'id': 'A3', 'answer': '', 'comment': 'ответим позже'}]}
            p = os.path.join(root, 'answers.json')
            io.open(p, 'w', encoding='utf-8').write(
                json.dumps(payload, ensure_ascii=False))
            rows = pk.read_answers(root, p)
            self.assertEqual(len(rows), 3)
            self.assertEqual([r['verdict'] for r in rows], ['ok', 'no', ''])
            self.assertEqual(rows[2]['why'], 'ответим позже')
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
