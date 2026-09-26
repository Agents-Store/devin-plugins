#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reader for the v3 client-document format: headings and lists, nothing else.

v2 put the machine fields in a fenced yaml block under each heading. That made the
parser trivial and the document unreadable — the owner's verdict on the first real one
was that markdown, yaml and tables had been stirred into porridge, and that a client
cannot tell what is safe to edit.

v3 has none of it. A client document is headings and bullet lists, plus ONE comment line
above the document and one above each entity naming where the same data sits in
macstack.json:

    <!-- macstack:ref=triggers[id=trg-week-close] -->
    ### Закрытие полумесячного периода — `trg-week-close`

    - **Что это за событие:** расписание
    - **Кто его создаёт:** часы, по расписанию

    **Что происходит.** 1-го и 16-го платформа собирает период…

So the reader matches bullet labels through a per-language table. That is the price of
a document a human will actually correct, and it is the right price: the labels are
few, they are declared here, and a project writing in German gets German labels rather
than a document nobody edits.
"""
import io, json, os, re, sys

DOC_HEADER = re.compile(r'^<!--\s*macstack:doc=(\S+)\s+lang=(\S+)\s+version=(\S+)\s*-->')
REF = re.compile(r'^<!--\s*macstack:ref=(.+?)\s*-->\s*$')
HEADING = re.compile(r'^(#{1,6})\s+(.*?)\s*$')
BULLET = re.compile(r'^\s*[-*]\s+\*\*(.+?):\*\*\s*(.*)$')
PROSE = re.compile(r'^\*\*(.+?)[.:]?\*\*\s*(.*)$')

# ---------------------------------------------------------------- labels
# Ярлыки живут в doc-contracts.json и строятся отсюда инверсией. Здесь их
# больше нет: два места, объявляющие одно и то же, расходятся — и разошлись.
# Контракт объявил ASCII-псевдонимы для сгенерированных документов, а таблица
# в этом файле о них не знала, поэтому линтер считал ARCHITECTURE.md разобранным,
# а читатель находил в нём ноль полей и 149 неизвестных ярлыков.
#
# READ многие-к-одному: у поля бывает больше одного имени. Цели говорят «Чем
# измеряем», результаты — «Что измеряем», и это одно поле; задачи говорят «Кто
# делает», процедуры — «Кто». Единственное имя на поле молча теряло 103 пункта
# из 430.
#
# EMIT один-к-одному и по видам: писатель никогда не выводит псевдоним.
_CONTRACT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              'doc-contracts.json')


def _tables(contract):
    read_, emit, by_kind, values = {}, {}, {}, {}
    for key, f in (contract.get('fields') or {}).items():
        for lang, lab in (f.get('label') or {}).items():
            emit.setdefault(lang, {})[key] = lab
            read_.setdefault(lang, {})[lab.strip().lower()] = key
        for kind, per in (f.get('label_by_kind') or {}).items():
            for lang, lab in per.items():
                by_kind.setdefault(lang, {}).setdefault(kind, {})[key] = lab
                read_.setdefault(lang, {})[lab.strip().lower()] = key
        for lang, aliases in (f.get('label_aliases') or {}).items():
            for lab in aliases:
                read_.setdefault(lang, {})[lab.strip().lower()] = key
        for lang, vmap in (f.get('value_label') or {}).items():
            for canon, word in vmap.items():
                values.setdefault(lang, {})[word.strip().lower()] = canon
    # значения, не привязанные к enum: да/нет и автоматически/руками
    for lang, extra in ((u'ru', {u'да': True, u'нет': False,
                                 u'автоматически': 'auto', u'руками': 'manual'}),
                        ('en', {'yes': True, 'no': False})):
        values.setdefault(lang, {}).update(extra)
    read_.setdefault('en', {})
    emit.setdefault('en', {})
    return read_, emit, by_kind, values


try:
    with io.open(_CONTRACT_PATH, encoding='utf-8') as _fh:
        READ, EMIT, EMIT_BY_KIND, VALUES = _tables(json.load(_fh))
except (IOError, ValueError) as _e:          # контракт рядом не лежит — читаем как умеем
    sys.stderr.write('v3: doc-contracts.json не прочитан (%s); '
                     'ярлыки недоступны, поля разбираться не будут\n' % _e)
    READ, EMIT, EMIT_BY_KIND, VALUES = {'en': {}}, {'en': {}}, {}, {'en': {}}

LABELS = READ          # имя сохранено: его импортируют пять модулей


class Item(object):
    __slots__ = ('id', 'title', 'level', 'ref', 'fields', 'sections', 'body', 'section',
                 'span', 'head_line', 'ref_line', 'field_lines', 'kind')

    def __init__(self):
        self.id = self.title = self.ref = self.section = self.kind = None
        self.level = 0
        self.fields, self.sections, self.body = {}, {}, []
        # Позиции — то, что делает писателя патчером, а не рендерером.
        # 75 % живого клиентского документа это проза, которой в модели нет;
        # инструмент, пересобирающий файл из модели, уничтожает три четверти.
        self.span = (0, 0)
        self.head_line = self.ref_line = None
        self.field_lines = {}          # key -> (lineno, label, raw_value)

    def get(self, key, default=None):
        return self.fields.get(key, default)

    def __repr__(self):
        return '<v3 %s %r>' % (self.id, (self.title or '')[:28])


def _split_heading(text):
    """«C-04 · Название» или «Название — `slug`» -> (id, title)."""
    m = re.match(r'^~*(C?[A-Z]-\d{2}|Q?[AB]\d+|M\d+(?:-T\d+)?)~*\s*·\s*(.+)$', text)
    if m:
        return m.group(1), m.group(2).strip()
    m = re.search(r'^(.*?)\s+—\s+`([A-Za-z0-9][A-Za-z0-9._-]*)`\s*$', text)
    if m:
        return m.group(2), m.group(1).strip()
    return None, text.strip()


IDENT = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._*-]*$')
# Путь тоже делится по запятой. IDENT не знает `/`, поэтому «- **Документы:**
# `a/b.md`, `c/d.pdf`» возвращался ОДНОЙ строкой с кавычками внутри, а `screens`
# рядом честно становился списком. Требование «без пробелов и есть `/`» узкое
# нарочно: cron `0 6 1,16 * *` содержит пробелы и остаётся текстом, а
# `einsaetze.rate_unit` в «Куда пойдёт» не содержит слэша и остаётся скаляром.
PATHISH = re.compile(r'^[A-Za-z0-9._-]+(?:/[A-Za-z0-9._#-]+)+$')


def _value(raw, lang):
    """Список — только когда КАЖДАЯ часть выглядит идентификатором.

    Наивное деление по запятой резало cron `0 6 1,16 * *` пополам и превращало
    «часы, по расписанию» в два значения. Запятая в тексте — это запятая, а не
    разделитель списка."""
    v = raw.strip().rstrip('.')
    tbl = VALUES.get(lang, {})

    def one(x):
        x = x.strip()
        # обратные кавычки снимаем только если в них ВСЁ значение: иначе
        # «workflow `wf-x`» теряет закрывающую и перестаёт быть кодом
        if len(x) > 1 and x[0] == '`' and x[-1] == '`' and x.count('`') == 2:
            x = x[1:-1].strip()
        return tbl.get(x.lower(), x)

    if ',' in v:
        parts = [p.strip().strip('`').strip() for p in v.split(',')]  # список — только из id
        if len(parts) > 1 and all(IDENT.match(p) or PATHISH.match(p)
                                  for p in parts if p):
            return [one(p) for p in parts if p]
    return one(v)


def header(text):
    m = DOC_HEADER.match(text.lstrip().splitlines()[0] if text.strip() else '')
    return dict(doc=m.group(1), lang=m.group(2), version=m.group(3)) if m else {}


def read(text, lang=None, undeclared=None):
    """Every heading of the document as an Item, in order.

    A bullet becomes a FIELD only when its label is declared. An undeclared
    label is prose that happens to be bold — `- **По-прежнему блокирует:** …`
    sits in a plain list beside two ordinary sentences — and inventing a field
    from it puts a raw Cyrillic key into the model that no consumer reads.
    Undeclared labels are collected for lint rather than swallowed or guessed.
    """
    h = header(text)
    lang = lang or h.get('lang') or 'ru'
    labels = READ.get(lang) or READ['en']
    lines = text.splitlines()
    items, cur, pending_ref, pending_ref_line, section = [], None, None, None, None
    for n, line in enumerate(lines):
        m = REF.match(line.strip())
        if m:
            pending_ref, pending_ref_line = m.group(1), n
            continue
        if line.lstrip().startswith('<!--'):
            continue
        hm = HEADING.match(line)
        if hm:
            lvl, txt = len(hm.group(1)), hm.group(2)
            if lvl == 2:
                section = txt
            if cur is not None:
                cur.span = (cur.span[0], pending_ref_line if pending_ref_line is not None
                            and pending_ref_line < n else n)
            it = Item()
            it.level, it.ref, it.section = lvl, pending_ref, section
            it.ref_line, it.head_line = pending_ref_line, n
            it.span = (pending_ref_line if pending_ref is not None else n, len(lines))
            it.id, it.title = _split_heading(txt)
            items.append(it)
            cur, pending_ref, pending_ref_line = it, None, None
            continue
        if cur is None:
            continue
        bm = BULLET.match(line)
        if bm:
            raw_label = bm.group(1).strip()
            key = labels.get(raw_label.lower())
            if key is not None:
                cur.fields[key] = _value(bm.group(2), lang)
                cur.field_lines[key] = (n, raw_label, bm.group(2))
                continue
            if undeclared is not None:
                undeclared.append((n + 1, raw_label))
            # не поле — значит проза, и она остаётся прозой
        pm = PROSE.match(line.strip())
        if pm:
            cur.sections[pm.group(1).strip()] = [pm.group(2)] if pm.group(2).strip() else []
            cur.body.append(line)
            continue
        if cur.sections:
            last = list(cur.sections)[-1]
            cur.sections[last].append(line)
        cur.body.append(line)
    return items


def entities(items, kind=None, level=None):
    """Only headings that carry an id, optionally filtered by the ref's collection."""
    out = []
    for it in items:
        if it.id is None:
            continue
        if level and it.level != level:
            continue
        if kind and not (it.ref or '').startswith(kind):
            continue
        out.append(it)
    return out


def load(path, lang=None):
    try:
        return read(io.open(path, encoding='utf-8').read(), lang)
    except IOError:
        return []


# ---------------------------------------------------------------- документ
class Doc(object):
    """Документ — это его строки. Ничто другое не авторитетно.

    Замер на живом корпусе: из 3837 строк шести клиентских документов модель
    видит 955 (25 %). Остальные 2882 — проза, которой в модели нет: вступления
    к ролям, «Как читать», списки вне объёма. Поэтому писатель патчит названную
    строку, а файл целиком собирается ровно в двух случаях — seed по
    несуществующему пути и render в generated/.
    """
    __slots__ = ('lines', 'header', 'items', 'lang', 'path', 'dirty',
                 'undeclared', '_final_nl')

    def __init__(self, lines, header, items, lang, path=None,
                 undeclared=None, final_nl=True):
        self.lines, self.header, self.items = lines, header, items
        self.lang, self.path, self.dirty = lang, path, False
        self.undeclared = undeclared or []
        self._final_nl = final_nl

    def text(self):
        return '\n'.join(self.lines) + ('\n' if self._final_nl else '')

    def item(self, ident):
        for it in self.items:
            if it.id == ident:
                return it
        return None

    def by_ref(self, ref):
        return [it for it in self.items if (it.ref or '').startswith(ref)]

    def __repr__(self):
        return '<v3.Doc %s %d lines %d items>' % (
            self.header.get('doc'), len(self.lines), len(self.items))


def read_doc(text, lang=None, path=None):
    h = header(text)
    und = []
    items = read(text, lang, undeclared=und)
    return Doc(text.split('\n') if not text.endswith('\n')
               else text[:-1].split('\n'),
               h, items, lang or h.get('lang') or 'ru', path, und,
               final_nl=text.endswith('\n'))


def load_doc(path, lang=None):
    return read_doc(io.open(path, encoding='utf-8').read(), lang, path)


def save(doc, path=None):
    """Пишет только если что-то менялось. Возвращает, писал ли."""
    if not doc.dirty:
        return False
    target = path or doc.path
    io.open(target, 'w', encoding='utf-8').write(doc.text())
    doc.dirty = False
    return True


# ---------------------------------------------------------------- эмиттеры
class ContractError(Exception):
    pass


def label_of(key, lang, kind=None):
    by_kind = (EMIT_BY_KIND.get(lang) or {}).get(kind or '', {})
    if key in by_kind:
        return by_kind[key]
    tbl = EMIT.get(lang) or EMIT['en']
    if key not in tbl:
        raise ContractError('no %s label for field %r' % (lang, key))
    return tbl[key]


def _invert_values(lang):
    out = {}
    for word, canon in (VALUES.get(lang) or {}).items():
        out.setdefault(canon, word)
    return out


def value_text(value, lang):
    """Значение в том виде, в каком его читает человек."""
    if value is None:
        return ''
    if isinstance(value, bool):
        return _invert_values(lang).get(value, 'yes' if value else 'no')
    if isinstance(value, (list, tuple)):
        return ', '.join('`%s`' % v for v in value)
    if isinstance(value, str):
        word = _invert_values(lang).get(value)
        if word is not None:
            return word
        if IDENT.match(value) and not value.isdigit():
            return '`%s`' % value
    return '%s' % value


def emit_field(key, value, lang, kind=None):
    """'- **Насколько важно:** критично'.

    Пустое значение не даёт висящего пробела: seed.py писал '- **Кто:** ' и
    оставил 41 такую строку в HANDBOOK.md живого проекта.
    """
    text = value_text(value, lang)
    label = label_of(key, lang, kind)
    return '- **%s:**%s' % (label, (' ' + text) if text else '')


def emit_pointer(path):
    return '<!-- macstack:ref=%s -->' % path


def emit_heading(level, ident, title, form='id'):
    if ident and form == 'id':
        return '%s %s · %s' % ('#' * level, ident, title)
    if ident and form == 'slug':
        return '%s %s — `%s`' % ('#' * level, title, ident)
    return '%s %s' % ('#' * level, title)


def emit_entity(kind, ident, title, fields=None, prose=(), pointer=None,
                lang='ru', level=3, form='id', order=None):
    """Строки ОДНОЙ сущности: без ведущей и без хвостовой пустой строки."""
    out = []
    if pointer:
        out.append(emit_pointer(pointer))
    out.append(emit_heading(level, ident, title, form))
    fields = fields or {}
    keys = [k for k in (order or sorted(fields)) if k in fields]
    if keys:
        out.append('')
        out.extend(emit_field(k, fields[k], lang, kind) for k in keys)
    for label, lines in prose:
        out.append('')
        if label:
            out.append('**%s:**' % label)
        out.extend(lines)
    return out


# ---------------------------------------------------------------- патчеры
def set_field(doc, item, key, value):
    """Переписать ровно одну строку-пункт. Возвращает, менялось ли что-нибудь.

    ПРАВИЛО ХОЛОСТОГО ХОДА: если поле уже есть и разобранное значение совпадает
    — не трогать ничего. Сравнение по РАЗОБРАННОМУ значению, не по байтам:
    «коуч.» остаётся «коуч.», cron `0 6 1,16 * *`, написанный без обратных
    кавычек, их не получает, а пункт, переставленный человеком, остаётся там,
    куда его поставили. Это то свойство, которое делает `sync --write`
    безопасным.
    """
    if key in item.field_lines:
        n, label, raw = item.field_lines[key]
        if _value(raw, doc.lang) == value:
            return False
        text = value_text(value, doc.lang)
        doc.lines[n] = '- **%s:**%s' % (label, (' ' + text) if text else '')
        item.fields[key] = value
        item.field_lines[key] = (n, label, text)
        doc.dirty = True
        return True
    # нового поля ещё нет — вставляем после последнего существующего
    if item.field_lines:
        after = max(n for n, _, _ in item.field_lines.values())
    else:
        after = item.head_line + 1
        doc.lines.insert(after, '')
        _shift(doc, after, 1)
    line = emit_field(key, value, doc.lang, item.kind)
    doc.lines.insert(after + 1, line)
    _shift(doc, after + 1, 1)
    item.fields[key] = value
    item.field_lines[key] = (after + 1, label_of(key, doc.lang, item.kind),
                             value_text(value, doc.lang))
    doc.dirty = True
    return True


def _shift(doc, at, by):
    """Сдвинуть все запомненные позиции ниже точки вставки."""
    for it in doc.items:
        if it.head_line is not None and it.head_line >= at:
            it.head_line += by
        if it.ref_line is not None and it.ref_line >= at:
            it.ref_line += by
        it.span = (it.span[0] + by if it.span[0] >= at else it.span[0],
                   it.span[1] + by if it.span[1] >= at else it.span[1])
        for k, (n, lab, raw) in list(it.field_lines.items()):
            if n >= at:
                it.field_lines[k] = (n + by, lab, raw)


def set_pointer(doc, item, path):
    line = emit_pointer(path)
    if item.ref_line is not None:
        if doc.lines[item.ref_line] == line:
            return False
        doc.lines[item.ref_line] = line
    else:
        doc.lines.insert(item.head_line, line)
        _shift(doc, item.head_line, 1)
        item.ref_line = item.head_line - 1
    item.ref = path
    doc.dirty = True
    return True


def remove_entity(doc, item):
    """Убрать сущность целиком. Возвращает удалённые строки — для переписи."""
    a, b = item.span
    gone = doc.lines[a:b]
    del doc.lines[a:b]
    _shift(doc, b, -(b - a))
    doc.items.remove(item)
    doc.dirty = True
    return gone


def insert_entity(doc, lines, after=None):
    at = (after.span[1] if after is not None else len(doc.lines))
    doc.lines[at:at] = [''] + lines
    _shift(doc, at, len(lines) + 1)
    doc.dirty = True
    return at
