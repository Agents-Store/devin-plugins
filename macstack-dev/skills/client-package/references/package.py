#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the client review package: one self-contained artifact a client can answer.

The inbound half of the client loop always worked. This is the outbound half. Nobody
sends a client an 88 KB markdown file and expects edits back, so in practice the client
writes a fresh document of their own and somebody transcribes it by hand — which is
where a hundred small changes go missing.

Reads the FIVE client documents — OVERVIEW, USER-CASES, UX-UI, AUTOMATION, HANDBOOK —
and gives every checkable claim a place to answer: confirm, correct, or ask. v1 promised
four documents and read two, which is the same failure with a smaller number.

IDS ARE STABLE. Every acceptance bullet carries `C-04.a3`, every screen prohibition
`coach-today.f2`, allocated from the document's own order and unchanged by a rebuild. v1
numbered bullets positionally per package, which only worked because handoffs/ is
immutable and broke the moment a bullet was inserted above another. A client's comment
has to survive the next round.

Output goes to handoffs/<date>-<slug>.html and is IMMUTABLE from that moment: the
client's comments come back against that exact file.

Usage: package.py <macstack-dir> [--date YYYY-MM-DD] [--slug user-cases] [--lang xx]
"""
import sys, os, io, re, json, html

sys.path.insert(0, os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', 'documents', 'references')))
import v3                                             # noqa: E402
import ledger                                         # noqa: E402
from i18n import doc_lang                             # noqa: E402

TODO = '_TODO —'


# ---------------------------------------------------------------- reading
PROSE_LABEL = {}


def _label(contract, key, lang):
    pr = (contract.get('prose') or {}).get(key) or {}
    return (pr.get('label') or {}).get(lang, key)


def _block(item, label):
    """Содержимое прозаического блока сущности, по его ярлыку.

    Блок бывает и списком, и абзацем: экран перечисляет, что на нём, списком, а
    роль описывает, что она видит, одним предложением. Первая версия брала
    только списки и молча теряла все три роли целиком.
    """
    for k, v in item.sections.items():
        if k.rstrip(':.').strip() != label:
            continue
        bullets = [x.lstrip('- ').rstrip(';').strip() for x in v
                   if x.strip().startswith('-')]
        if bullets:
            return bullets
        para = ' '.join(x.strip() for x in v if x.strip()).strip()
        return [para] if para else []
    return []


ENTITY_MD = re.compile(r'^#{1,6}\s')


def _entity_md(doc_lines, item, drop_labels):
    """Сущность целиком, как её читает человек — без машинных пунктов.

    Клиенту показывают ЛОГИКУ, а не чек-лист. Пункты приёмки — это тест-кейсы,
    они для машины; в документе они живут внутри кейса и читаются как его часть,
    а не как отдельные вопросы. Первая версия расплющила их в 611 отдельных
    строк по 400 символов, и получился длинный опросник вместо документа.

    Машинные пункты (`- **Насколько важно:** критично`) убираются: клиенту они
    ничего не говорят, а приоритет показывается отдельной пометкой.
    """
    a, b = item.span
    out, seen_head = [], False
    for raw in doc_lines[a:b]:
        s = raw.rstrip()
        if s.lstrip().startswith('<!--'):
            continue
        if ENTITY_MD.match(s):
            if seen_head:
                break
            seen_head = True
            continue                      # заголовок печатаем отдельно
        m = re.match(r'^\s*-\s+\*\*(.+?):\*\*', s)
        if m and m.group(1).strip() in drop_labels:
            continue
        out.append(s)
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return out


def _machine_labels(contract, lang):
    """Ярлыки машинных полей на языке документа — их клиенту не показывают."""
    out = set()
    for f in (contract.get('fields') or {}).values():
        lab = (f.get('label') or {}).get(lang)
        if lab:
            out.add(lab)
        for per in (f.get('label_by_kind') or {}).values():
            if per.get(lang):
                out.add(per[lang])
    return out


_HINT = re.compile(r'_[^_\n][^_]*_|<em>.*?</em>', re.S)


def _is_stub(body):
    """Сущность, в которой нет ничего, кроме подсказки генератора.

    `seed.py` пишет заготовку строкой курсива — `_Опишите шаги от начала до конца
    этой процедуры._` — и рядом жирную подпись раздела. Пока никто не заполнил
    процедуру, это ВСЁ её содержимое, и в пакет уходит заголовок с просьбой,
    обращённой к нам, а не к клиенту. Измерено 2026-08-27 на живом проекте: раздел
    «Как этим пользоваться» — 41 такая заготовка, ни одной отвечаемой, и поля,
    куда клиент мог бы написать ответ, под ними нет. Раздел обещал пошаговые
    инструкции и отдавал 41 бланк.

    Условие намеренно узкое: «кроме подсказки НИЧЕГО нет». Курсивная строка
    среди настоящего текста — это выделение автора, и она остаётся; молча
    выбрасывать слова, которые клиент написал сам, было бы хуже показанной
    заготовки. Вызывается только там, где у сущности нет id (`want_id=False`),
    поэтому ни один кейс, экран или вопрос через него не проходит.

    Ничего не нужно помнить и включать обратно: `collect` уже отбрасывает раздел,
    в котором не осталось сущностей, так что раздел вернётся сам — в тот день,
    когда в документе появится первая написанная процедура.
    """
    if not body:
        return True
    # `_entity_md` отдаёт СТРОКИ ИСХОДНИКА, а не готовый html — их ещё пройдёт md().
    # Первая версия этой проверки звала re.sub прямо по body и падала TypeError на
    # списке; тихо она бы не упала, поэтому проверка есть в тесте ниже по файлу.
    t = '\n'.join(body) if isinstance(body, (list, tuple)) else body
    t = re.sub(r'\*\*.*?\*\*|<strong>.*?</strong>', ' ', t, flags=re.S)  # подписи заготовки
    t = _HINT.sub(' ', t)
    t = re.sub(r'<[^>]+>', ' ', t)
    return not t.strip()


def collect(root, contract, lang):
    """Семь разделов, и в каждом — сущности ЦЕЛИКОМ.

    Единица, на которую отвечает клиент, — кейс, экран, триггер, вопрос. Не
    строка внутри него. Клиент читает связный текст и говорит про него одно из
    трёх; разбивать документ на шестьсот отдельных вопросов значит превращать
    его в опросник, который никто не дочитает. Пункты приёмки — тест-кейсы, они
    для машины и живут внутри кейса как его часть.
    """
    cl = os.path.join(root, 'client')
    drop = _machine_labels(contract, lang)

    def load(name):
        p_ = os.path.join(cl, name)
        return v3.load_doc(p_) if os.path.exists(p_) else None

    docs = dict((n, load(n)) for n in ('OVERVIEW.md', 'USER-CASES.md', 'UX-UI.md',
                                       'AUTOMATION.md', 'HANDBOOK.md',
                                       'OPEN-QUESTIONS.md'))

    def ents(name, pref=None, level=3, want_id=True):
        d = docs.get(name)
        if d is None:
            return []
        out = []
        for it in d.items:
            if it.level != level:
                continue
            if want_id and not it.id:
                continue
            if pref is not None and not (it.ref or '').startswith(pref):
                continue
            body = _entity_md(d.lines, it, drop)
            if not it.id and (not body or _is_stub(body)):
                continue
            out.append(dict(id=it.id or '', title=it.title or '', section=it.section,
                            meta=_meta(it, lang), body=body))
        return out

    def prose(name, heads):
        d = docs.get(name)
        if d is None:
            return []
        out = []
        for it in d.items:
            if it.level != 2 or (it.title or '') not in heads:
                continue
            body = _entity_md(d.lines, it, drop)
            if body:
                out.append(dict(id='', title=it.title, section=None, meta='', body=body))
        return out

    tasks = [e for e in ents('AUTOMATION.md', None, level=4) if e['id']]
    sections = [
        ('product', prose('OVERVIEW.md',
                          (u'О продукте', u'Как это работает', u'Для кого',
                           u'Правила, которые не нарушаются',
                           u'Что платформа отказывается делать',
                           'About the product', 'How it works', 'Who it is for'))),
        ('goals', ents('OVERVIEW.md', 'goals[') + ents('OVERVIEW.md', 'results[')),
        ('roles', ents('AUTOMATION.md', 'roles[')),
        ('automation', ents('AUTOMATION.md', 'processes[')
                       + ents('AUTOMATION.md', 'triggers[') + tasks),
        ('cases', ents('USER-CASES.md')),
        # Клиенту уходит §A — то, что должен ОН, — и различается это по указателю
        # `lifecycle.needs_from_client`, которым §A связан со спекой, а §B нет.
        # Раньше фильтром было «есть id», и §B выпадал лишь потому, что его
        # заголовки написаны через тире (`B1 — …`), а §A через точку (`A1 · …`):
        # разбор id не узнавал тире, id получался пустым. Работало, но случайно —
        # первый же пункт §B, набранный по образцу соседнего раздела, ушёл бы
        # клиенту вопросом про нашу отложенную работу. Зачёркнутое отсеивается
        # отдельно: указатель говорит «должен заказчик», зачёркивание — «уже
        # закрыто», и это два разных условия.
        ('questions', [e for e in ents('OPEN-QUESTIONS.md', 'lifecycle.needs_from_client')
                       if '~~' not in (e['title'] or '')]),
        ('screens', ents('UX-UI.md', 'interfaces[')),
        ('handbook', ents('HANDBOOK.md', None, level=3, want_id=False)),
    ]
    return [(k, v) for k, v in sections if v]


def _meta(item, lang):
    PRI = {'critical': {'ru': u'критично', 'en': 'critical'},
           'important': {'ru': u'важно', 'en': 'important'},
           'nice-to-have': {'ru': u'желательно', 'en': 'nice to have'}}
    bits = []
    p_ = item.get('priority')
    if p_:
        bits.append((PRI.get(p_) or {}).get(lang, p_))
    for k in ('path', 'horizon', 'metric_target'):
        v = item.get(k)
        if v:
            bits.append(str(v))
    return ' · '.join(bits)


def _spec(root):
    try:
        return json.load(io.open(os.path.join(root, 'macstack.json'), encoding='utf-8'))
    except (IOError, ValueError):
        return {}


def md(s):
    s = html.escape(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'`(.+?)`', r'<code>\1</code>', s)
    s = re.sub(r'(?<![A-Za-z0-9_])\*(.+?)\*(?![A-Za-z0-9_])', r'<em>\1</em>', s)
    return s


# Ни одной внешней загрузки. Пакет обещан самодостаточным: его открывают из
# почтового вложения, с флешки и в самолёте, и страница, которой для вида нужен
# чужой сервер, этого обещания не держит. Вторая причина весомее первой: запрос за
# шрифтом сообщает стороннему CDN IP клиента и момент, когда тот открыл документ со
# своей же коммерческой спецификацией. Платить этим за начертание нельзя.
#
# IBM Plex остаётся первым в каждом стеке — у кого он установлен, тот его и увидит.
# Дальше идут гарнитуры, которые есть в системе и НЕСУТ КИРИЛЛИЦУ: документ русский,
# и стек, подобранный по латинице, отвалился бы на первом же слове.
FONTS = ''

CSS = """
/* IBM Plex: сделано для технических документов и несёт полную кириллицу.
   Документ русский, и половина фамильных гарнитур отпала бы на первом же слове.
   Не загружается со стороны — см. комментарий у FONTS. */
:root{
  --paper:#fcfcfd; --ink:#15181e; --dim:#5c6270; --line:#e4e6eb; --soft:#f4f5f7;
  --accent:#0f5f61; --accent-ink:#ffffff;
  --mark:#8a5a00; --mark-bg:#fdf6e7; --mark-line:#dbb96a;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --paper:#101318; --ink:#e8eaee; --dim:#98a0ad; --line:#272c35; --soft:#171b22;
  --accent:#4fd0cf; --accent-ink:#0a1416;
  --mark:#e0b866; --mark-bg:#201c10; --mark-line:#6b5423;
}}
:root[data-theme="dark"]{
  --paper:#101318; --ink:#e8eaee; --dim:#98a0ad; --line:#272c35; --soft:#171b22;
  --accent:#4fd0cf; --accent-ink:#0a1416;
  --mark:#e0b866; --mark-bg:#201c10; --mark-line:#6b5423;
}
*{box-sizing:border-box}
body{background:var(--paper);color:var(--ink);margin:0 auto;max-width:44rem;
 padding:2.5rem 1.15rem 6rem;
 font:400 16.5px/1.6 "IBM Plex Sans","Inter","Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
 -webkit-text-size-adjust:100%}
h1{font:600 1.75rem/1.2 "IBM Plex Serif","Charter","Times New Roman",Georgia,serif;margin:0 0 .35rem;
 text-wrap:balance;letter-spacing:-.01em}
h2{font:600 1.22rem/1.3 "IBM Plex Serif","Charter","Times New Roman",Georgia,serif;margin:3.2rem 0 .25rem;
 padding-top:1.15rem;border-top:2px solid var(--ink);text-wrap:balance}
h3{font:500 1.02rem/1.35 "IBM Plex Serif","Charter","Times New Roman",Georgia,serif;margin:2rem 0 .55rem;
 display:flex;flex-wrap:wrap;align-items:baseline;gap:.55rem;text-wrap:balance}
.lead{color:var(--dim);margin:0 0 1.6rem;font-size:.96rem}
.howto{background:var(--soft);border-radius:10px;padding:1rem 1.15rem;font-size:.94rem;
 display:flex;flex-direction:column;gap:.6rem}
.howto p{margin:0}
.sec-note,.meta{color:var(--dim);font-size:.9rem;margin:.15rem 0 1.1rem}
.grp{margin-bottom:.4rem}
.code{font:400 11.5px/1 "IBM Plex Mono",ui-monospace,"SF Mono",Menlo,Consolas,monospace;color:var(--dim);
 letter-spacing:.02em}
h3 .code{font-size:12px}
.e{border:1px solid var(--line);border-radius:12px;padding:1.05rem 1.15rem;
 display:flex;flex-direction:column;gap:.55rem;margin-bottom:.75rem;background:var(--paper)}
.e.changed{border-color:var(--mark-line);background:var(--mark-bg)}
.e h3{margin:0}
.body{display:flex;flex-direction:column;gap:.55rem;max-width:64ch}
.body p{margin:0}
.body ul{margin:0;padding-left:1.15rem;display:flex;flex-direction:column;gap:.3rem}
.body li{margin:0}
.body .sub{font-weight:600;margin-top:.15rem}
.tag{font:500 10.5px/1 "IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;text-transform:uppercase;
 letter-spacing:.09em;color:var(--mark)}
.was{margin:0;font-size:.89rem;color:var(--mark);padding-left:.75rem;
 border-left:2px solid var(--mark-line)}
.said{margin:0;font-size:.89rem;color:var(--dim);padding-left:.75rem;
 border-left:2px solid var(--line)}
.prev{margin:0;font-size:.87rem;color:var(--accent);font-weight:500}
.ans{display:flex;flex-wrap:wrap;gap:.4rem}
.r{display:inline-flex;align-items:center;gap:.35rem;border:1px solid var(--line);
 border-radius:999px;padding:.32rem .85rem;font-size:.92rem;cursor:pointer;
 user-select:none;transition:background .12s,border-color .12s,color .12s}
.r:hover{border-color:var(--dim)}
.r:focus-within{outline:2px solid var(--accent);outline-offset:2px}
.r input{accent-color:var(--accent);margin:0}
.r:has(input:checked){background:var(--accent);border-color:var(--accent);
 color:var(--accent-ink)}
.r:has(input:checked) input{accent-color:var(--accent-ink)}
.c{border:1px dashed var(--line);border-radius:8px;min-height:2.2rem;
 padding:.5rem .65rem;font-size:.94rem}
.c:focus{outline:2px solid var(--accent);outline-offset:1px;border-style:solid}
.c:empty:before{content:attr(data-ph);color:var(--dim);opacity:.65}
#bar{margin-top:2.5rem;display:flex;flex-direction:column;gap:.6rem}
/* Пустой, пока не нажали: подтверждение появляется только после действия. */
.cnt{margin:0;font-size:.92rem;color:var(--accent);font-weight:500}
.cnt:empty{display:none}
button{font:500 .95rem/1 "IBM Plex Sans","Inter","Segoe UI",Roboto,Arial,sans-serif;padding:.7rem 1.2rem;
 border:1px solid var(--accent);background:var(--accent);color:var(--accent-ink);
 border-radius:8px;cursor:pointer;align-self:flex-start}
button:hover{filter:brightness(1.08)}
button:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
textarea{width:100%;min-height:11rem;border:1px solid var(--line);border-radius:8px;
 padding:.75rem;background:var(--soft);color:var(--ink);
 font:400 13px/1.55 "IBM Plex Mono",ui-monospace,"SF Mono",Menlo,Consolas,monospace}
footer{margin-top:3.5rem;padding-top:1.3rem;border-top:1px solid var(--line);
 color:var(--dim);font-size:.93rem}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
@media print{
  body{max-width:none;padding:0;font-size:11pt}
  .ans,.c,.e{-webkit-print-color-adjust:exact;print-color-adjust:exact}
  button,textarea,#bar{display:none}
  .e{break-inside:avoid;page-break-inside:avoid}
  h2{break-after:avoid}
}
"""

JS = """
/* Ищет СЕКЦИИ, а не строки таблицы. Первая версия после перехода на карточки
   продолжала спрашивать tr[data-id] и собирала ноль ответов — молча, потому что
   пустой список это тоже список. */
function collect(){
  var els=document.querySelectorAll('section.e[data-id]'),out=[];
  for(var i=0;i<els.length;i++){
    var e=els[i],id=e.getAttribute('data-id');
    var picked=e.querySelector('input[type=radio]:checked');
    var note=(e.querySelector('.c')||{}).innerText||'';
    note=note.replace(/\\s+/g,' ').trim();
    var was=e.getAttribute('data-was')||'';
    if(!picked&&!note)continue;
    var v=picked?picked.value:'';
    if(v===was&&!note)continue;            /* прошлый ответ без правки — не шлём */
    out.push({id:id,answer:v,comment:note});
  }
  return out;
}
function save(){
  var d=document.getElementById('dump'),n=document.getElementById('cnt'),a=collect();
  d.value=JSON.stringify({package:(document.title||''),date:PKG_DATE,answers:a},null,2);
  d.style.display='block';d.focus();d.select();
  /* Копирование в буфер может быть запрещено (песочница, отказ в разрешении) —
     тогда текст всё равно виден и выделен, и его копируют руками. Поэтому
     сообщение НЕ обещает, что уже скопировано, пока это не подтвердилось. */
  var done=false;
  try{done=document.execCommand('copy')}catch(e){}
  if(n)n.textContent=(a.length?COUNTED.replace('%d',a.length):EMPTY)+(done?COPIED:'');
  if(!done&&navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(d.value).then(function(){
      if(n)n.textContent=(a.length?COUNTED.replace('%d',a.length):EMPTY)+COPIED;
    },function(){});
  }
}
/* Обработчик вешается ИЗ СКРИПТА, а не атрибутом onclick: инлайновый атрибут
   запрещён политикой безопасности строже той, при которой сам этот блок ещё
   выполняется, и кнопка тогда молчит без единого сообщения. */
(function(){
  function bind(){
    var b=document.getElementById('go');
    if(b)b.addEventListener('click',save);
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bind);
  else bind();
})();
"""

STR = {
 'ru': dict(title='Что платформа должна делать — на согласование',
            short='{n} — на согласование',
            lead='{n}. Версия {v} · {d}',
            howto=('<p><strong>Как этим пользоваться.</strong> Каждый блок — одно утверждение '
                   'о платформе. Отметьте «верно», «не так» или «вопрос» и допишите комментарий, '
                   'если есть что сказать.</p>'
                   '<p>Можно отвечать прямо в браузере, потом «Печать» → «Сохранить как PDF». '
                   'Можно распечатать и писать от руки. Можно нажать кнопку внизу и прислать нам '
                   'текст ответов.</p>'
                   '<p>Код над утверждением — например <code>C-04.a3</code> — это его постоянный '
                   'адрес. Он не меняется между версиями, на него можно сослаться и через год.</p>'),
            since='Жёлтым помечено то, что изменилось после прошлого пакета от %s. '
                  'Под таким утверждением написано, как было.',
            s_product='О продукте', s_goals='Цели', s_roles='Кто чем занимается',
            s_automation='Что запускает работу и кто её делает', s_cases='Что должно быть сделано',
            s_questions='Вопросы к вам', s_screens='Экраны',
            n_product='Правила, которые платформа держит всегда, без исключений.',
            n_questions='На эти вопросы можем ответить только вы. Пока ответа нет, работа по ним стоит.',
            n_cases='Главное в пакете. Каждый пункт — то, что человек должен смочь сделать.',
            c_c='комментарий, если есть',
            c_c_questions='ваш ответ',
            howto_questions=(
                '<p><strong>Как этим пользоваться.</strong> Ниже — вопросы, ответить на '
                'которые можем только мы вместе: всё это либо ваши данные, либо ваши '
                'решения. Под каждым вопросом написано, что будет, если ответа не будет.</p>'
                '<p>Пишите ответ прямо в поле под вопросом. Отметка рядом — про сам вопрос: '
                '«верно» — написанное верно, добавить нечего; «не так» — мы что-то поняли '
                'неправильно; «вопрос» — непонятно, что именно от вас нужно.</p>'
                '<p>Можно отвечать прямо в браузере, потом «Печать» → «Сохранить как PDF». '
                'Можно распечатать и писать от руки. Можно нажать кнопку внизу и прислать '
                'нам текст ответов.</p>'
                '<p>Код у вопроса — например <code>A1</code> — это его постоянный адрес. Он '
                'не меняется между версиями, на него можно сослаться письмом и через год.</p>'),
            s_handbook='Как этим пользоваться',
            n_handbook='Пошагово, для того, кто сядет работать в платформе.',
            ok='верно', no='не так', q='вопрос',
            changed='изменилось', was='было:', you='вы', us='мы',
            answered='Вы отвечали %s: «%s». Ответ подставлен — можно оставить или изменить.',
            counted='Собрано ответов: %d.',
            empty='Пока ничего не отмечено — отметьте хотя бы один пункт или напишите комментарий.',
            copied=' Текст скопирован — вставьте его в письмо.',
            btn='Собрать мои ответы', dump='Скопируйте этот текст и пришлите нам',
            foot=('Верните этот файл — с ответами в браузере, сканом от руки или текстом из '
                  'кнопки выше. Мы разберём каждый пункт и вернёмся с решением по каждому.')),
 'en': dict(title='What the platform must do — for review',
            short='{n} — for review',
            lead='{n}. Version {v} · {d}',
            howto=('<p><strong>How to use this.</strong> Each block is one claim about the '
                   'platform. Mark it "right", "not so" or "question", and add a comment if you '
                   'have one.</p>'
                   '<p>Answer straight in the browser and Print → Save as PDF, print it and write '
                   'by hand, or press the button at the bottom and send us the text.</p>'
                   '<p>The code above a claim — <code>C-04.a3</code> — is its permanent address. '
                   'It does not change between versions and is still quotable a year from now.</p>'),
            since='Marked yellow: changed since the last package of %s. What it said before is '
                  'written underneath.',
            s_product='About the product', s_goals='Goals', s_roles='Who does what',
            s_automation='What starts work, and who does it', s_cases='What must be delivered',
            s_questions='Questions for you', s_screens='Screens',
            n_product='Rules the platform keeps always, without exception.',
            n_questions='Only you can answer these. Work on them is stopped until you do.',
            n_cases='The heart of the package. Each item is something a person must be able to do.',
            c_c='a comment, if you have one',
            c_c_questions='your answer',
            howto_questions=(
                '<p><strong>How to use this.</strong> Below are the questions only you can '
                'answer: each is either your data or your decision. Under each one is what '
                'happens if the answer does not come.</p>'
                '<p>Write your answer in the field under the question. The mark beside it is '
                'about the question itself: "right" — it is correct and there is nothing to '
                'add; "not so" — we got something wrong; "question" — it is unclear what is '
                'being asked of you.</p>'
                '<p>Answer straight in the browser and Print → Save as PDF, print it and '
                'write by hand, or press the button at the bottom and send us the text.</p>'
                '<p>The code on a question — <code>A1</code> — is its permanent address. It '
                'does not change between versions and is still quotable a year from now.</p>'),
            s_handbook='How to use it',
            n_handbook='Step by step, for the person who will work in it.',
            ok='right', no='not so', q='question',
            changed='changed', was='was:', you='you', us='we',
            answered='You answered on %s: \u201c%s\u201d. It is pre-filled — keep it or change it.',
            counted='Answers collected: %d.',
            empty='Nothing marked yet — mark at least one item or write a comment.',
            copied=' Copied — paste it into your reply.',
            btn='Collect my answers', dump='Copy this text and send it to us',
            foot=('Send this file back — answered in the browser, scanned from paper, or as the '
                  'text from the button above. We will work through every item and come back '
                  'with a decision on each.')),
}


def rows(T, group, hist, since):
    """Сущность как кусок документа, и ОДИН ответ на неё."""
    ident = group['id']
    rec = hist.get(ident, []) if ident else []
    # Сравнение НЕ строгое, и это разница между «жёлтым помечено 18 пунктов» и
    # «жёлтым не помечено ничего». Журнал датирован днём, а пакет пересобирают в
    # тот же день, в который правили документы: `since` — дата ПРОШЛОГО пакета,
    # и при `>` каждая правка того же дня отбрасывается. Измерено 2026-08-27 на
    # На живом проекте: 16 сущностей реально сдвинулись (8 новых, 8 с новым текстом), `>`
    # пометил 0 из 209, а страница при этом продолжала обещать клиенту «жёлтым
    # помечено то, что изменилось после прошлого пакета от 2026-08-27».
    # День — это вся точность, какая есть, поэтому ошибка неизбежна; выбрана
    # ошибка в сторону лишней пометки. Лишняя стоит клиенту второго взгляда на
    # пункт, который он уже видел (на том же замере — 2 пункта из 18);
    # пропущенная стоит правки, которую клиент не прочитает никогда, а ради неё
    # эта пометка и существует.
    moved = [r for r in rec if r.get('kind') in ('added', 'changed')
             and (r.get('date') or '') >= (since or '')]
    said = [r for r in rec if r.get('kind') in ('comment', 'answer')]
    # Последний ответ клиента по этому куску: он подставляется галочкой и
    # остаётся изменяемым. Клиент не должен отвечать заново на то, что уже
    # прошёл, — но и запирать его в прошлом ответе нельзя: документ поменялся,
    # и «верно» полугодовой давности может перестать быть верным.
    prev = None
    for r in rec:
        if r.get('kind') == 'comment' and r.get('verdict'):
            prev = r

    attrs = ' data-id="%s"' % html.escape(ident) if ident else ''
    if prev:
        attrs += ' data-was="%s"' % html.escape(prev.get('verdict') or '')
    out = ['<section class="e%s"%s>' % (' changed' if moved else '', attrs)]
    head = md(group['title'] or '')
    if ident:
        head += ' <span class="code">%s</span>' % html.escape(ident)
    out.append('<h3>%s</h3>' % head)
    if group.get('meta'):
        out.append('<p class="meta">%s</p>' % md(str(group['meta'])))
    if moved:
        out.append('<p class="tag">%s</p>' % T['changed'])
    out.append('<div class="body">%s</div>' % _md_block(group['body']))
    for r in moved:
        if r.get('was'):
            out.append('<p class="was">%s %s</p>' % (T['was'], md(str(r['was'])[:400])))
    for r in said:
        who = T['you'] if r.get('by') == 'client' else T['us']
        out.append('<p class="said"><strong>%s, %s:</strong> %s</p>'
                   % (who, html.escape(r.get('date') or ''),
                      md(str(r.get('why') or r.get('now') or '')[:400])))
    if ident:
        if prev:
            out.append('<p class="prev">%s</p>'
                       % (T['answered'] % (html.escape(prev.get('date') or ''),
                                           T.get(prev.get('verdict'), prev.get('verdict')))))
        radios = ''.join(
            '<label class="r"><input type="radio" name="%s" value="%s"%s>%s</label>'
            % (html.escape(ident), val,
               ' checked' if prev and prev.get('verdict') == val else '', T[key])
            for val, key in (('ok', 'ok'), ('no', 'no'), ('q', 'q')))
        out.append('<div class="ans">%s</div>' % radios)
        out.append('<div class="c" contenteditable="true" data-ph="%s"></div>' % T['c_c'])
    out.append('</section>')
    return out


def _md_block(lines):
    """Абзацы, списки и жирные подзаголовки — как в самом документе.

    Строки абзаца склеиваются ДО преобразования. В документе жирный текст
    свободно переносится на следующую строку, и построчное преобразование
    оставляло от него половину: «**центр» на одной строке и «подтверждает
    часы**» на другой — ни одна не пара сама себе.
    """
    out, ul, para = [], False, []

    def flush():
        if not para:
            return
        s = ' '.join(x.strip() for x in para).strip()
        del para[:]
        if not s:
            return
        if re.match(r'^\*\*[^*]+[.:]?\*\*$', s):
            out.append('<p class="sub">%s</p>' % md(s))
        else:
            out.append('<p>%s</p>' % md(s))

    for raw in lines:
        s = raw.strip()
        if not s:
            flush()
            if ul:
                out.append('</ul>')
                ul = False
            continue
        if s.startswith('- '):
            flush()
            if not ul:
                out.append('<ul>')
                ul = True
            out.append('<li>%s</li>' % md(s[2:].rstrip(';')))
            continue
        if ul:
            out.append('</ul>')
            ul = False
        para.append(s)
    flush()
    if ul:
        out.append('</ul>')
    return '\n'.join(out)


SECTION_KEYS = ('product', 'goals', 'roles', 'automation', 'cases',
                'questions', 'screens', 'handbook')


def _select(sections, only, skip):
    """Разделить пакет на несколько, не потеряв ни одного раздела молча.

    Открытые вопросы — единственная часть, которую заказчик читает НЕ так, как
    остальное: там он не подтверждает наше описание, а отдаёт то, чего у нас нет,
    и до его ответа работа стоит. Отсюда просьба владельца (2026-08-27) разложить
    пакет надвое — документы отдельно, вопросы отдельно.

    Ошибка в имени раздела — отказ, а не пустой пакет: `--only question` (без «s»)
    иначе собрал бы файл из нуля пунктов, записал бы его в журнал как состоявшийся
    круг и сдвинул бы точку отсчёта «что изменилось» для СЛЕДУЮЩЕГО пакета. Дороже
    всего здесь именно последнее — про сам файл видно, что он пуст, а про сдвинутую
    отметку не видно ничего.
    """
    def parse(v):
        if v in (None, True, False):
            return None
        got = [x.strip() for x in str(v).replace(',', ' ').split() if x.strip()]
        bad = [x for x in got if x not in SECTION_KEYS]
        if bad:
            raise SystemExit('неизвестный раздел: %s\nизвестные: %s'
                             % (', '.join(bad), ', '.join(SECTION_KEYS)))
        return got

    only, skip = parse(only), parse(skip)
    out = sections
    if only:
        out = [(k, v) for k, v in out if k in only]
    if skip:
        out = [(k, v) for k, v in out if k not in skip]
    if not out:
        raise SystemExit('выбор не оставил ни одного раздела — пакет не собран')
    return out


def build(root, date, slug, lang=None, artifact=False,
          only=None, skip=None):
    spec = _spec(root)
    lang = lang or doc_lang(root)
    T = STR.get(lang, STR['en'])
    name = (spec.get('identity') or {}).get('title') or spec.get('name', '')
    contract = _contract()
    sections = _select(collect(root, contract, lang), only, skip)

    # История по пункту и точка отсчёта «что изменилось». Дата берётся из имени
    # ПРОШЛОГО пакета, а не из даты записи: комментарий несёт день, когда его
    # написал клиент, и он сдвинул бы отметку за утверждения, которых клиент не
    # видел, пометив их неизменными.
    hist = ledger.index(root)
    since = ledger.last_handoff(root)

    # Пакет из ОДНОГО раздела называет себя этим разделом. Иначе два пакета,
    # собранные в один день, уходят клиенту под одним и тем же именем и в галерее
    # артефактов различаются только ссылкой — а выбирать из них будет человек.
    solo = sections[0][0] if len(sections) == 1 else None
    head = T.get('s_' + solo, T['title']) if solo else T['title']

    # Пакет из одного раздела показывает версию СВОЕГО документа. Иначе на пакете
    # вопросов стоит версия USER-CASES.md — чужая, и она не сдвинется, когда
    # перепишут сами вопросы: клиент увидит ту же цифру над новым текстом.
    DOC_OF = {'questions': 'open_questions', 'cases': 'user_cases', 'screens': 'ux_ui',
              'automation': 'automation', 'roles': 'automation', 'handbook': 'handbook',
              'product': 'overview', 'goals': 'overview'}
    files = ((spec.get('docs') or {}).get('files') or {})
    version = files.get(DOC_OF.get(solo, 'user_cases') if solo else 'user_cases',
                        {}).get('version', '?')

    # Вопросы читают не так, как остальное: там не подтверждают наше описание, а
    # отдают то, чего у нас нет. Общая инструкция зовёт отметить «верно» — для «дайте
    # реквизиты компании» это бессмыслица, и она стоит первой строкой, которую человек
    # читает. Своя инструкция и своя подпись поля есть только у этого раздела.
    if solo and T.get('howto_' + solo):
        T = dict(T)
        T['howto'] = T['howto_' + solo]
        if T.get('c_c_' + solo):
            T['c_c'] = T['c_c_' + solo]

    if artifact:
        # Полный пакет держит короткую форму, какой была: менять имя круга,
        # который клиент уже видел, значит терять его в галерее.
        tab = (('%s — %s' % (name, head)) if solo else T['short'].format(n=name)) \
            if name else head
        P = ['<title>%s</title>' % html.escape(tab), FONTS,
             '<style>%s</style>' % CSS]
    else:
        P = ['<!doctype html><html lang="%s"><head><meta charset="utf-8">' % lang,
             '<meta name="viewport" content="width=device-width,initial-scale=1">',
             FONTS,
             '<title>%s — %s</title><style>%s</style></head><body>'
             % (html.escape(name), html.escape(head), CSS)]
    P += ['<h1>%s</h1>' % html.escape(head),
          '<p class="lead">%s</p>' % html.escape(T['lead'].format(n=name, v=version, d=date)),
          '<div class="howto">%s</div>' % T['howto']]
    if since:
        P.append('<p class="sec-note">%s</p>' % html.escape(T['since'] % since))

    counted = 0
    for key, groups in sections:
        if not groups:
            continue
        if key != solo:                      # у пакета из одного раздела это <h1>
            P.append('<h2>%s</h2>' % html.escape(T.get('s_' + key, key)))
        note = T.get('n_' + key)
        if note:
            P.append('<p class="sec-note">%s</p>' % html.escape(note))
        for g in groups:
            P.extend(rows(T, g, hist, since))
            counted += 1 if g['id'] else 0

    # `id="go"` вместо `onclick`, и `id="cnt"` — элемент, в который скрипт пишет,
    # сколько ответов собрано. Раньше скрипт искал `cnt`, а такого элемента в
    # странице не было вовсе, так что подтверждения не появлялось никогда.
    P.append('<div id="bar"><button id="go" type="button">%s</button>'
             '<p id="cnt" class="cnt"></p>'
             '<textarea id="dump" placeholder="%s"></textarea></div>'
             % (html.escape(T['btn']), html.escape(T['dump'])))
    P.append('<footer>%s</footer>' % html.escape(T['foot']))
    # Константы, которые скрипт ЧИТАЕТ. Их не было ни одной: `save()` падал на
    # `PKG_DATE` первой же строкой — до того, как что-либо попадало в поле, — и
    # кнопка «Собрать мои ответы» не работала ни в одном пакете, который этот
    # сборщик когда-либо выпустил. Тихо: исключение в обработчике никак не видно
    # тому, кто нажал. Это же объясняет, почему в журнале живого проекта тринадцать строк
    # `handoff` и ноль строк `comment`: возвращать ответы было нечем.
    P.append('<script>var PKG_DATE=%s,COUNTED=%s,EMPTY=%s,COPIED=%s;%s</script>%s'
             % (json.dumps(date, ensure_ascii=False),
                json.dumps(T['counted'], ensure_ascii=False),
                json.dumps(T['empty'], ensure_ascii=False),
                json.dumps(T['copied'], ensure_ascii=False),
                JS, '' if artifact else '</body></html>'))
    return '\n'.join(P), version, counted, sections


def _contract():
    p = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      '..', '..', 'documents', 'references',
                                      'doc-contracts.json'))
    try:
        return json.load(io.open(p, encoding='utf-8'))
    except (IOError, ValueError):
        return {}


VERDICT = {'ok': 'ok', 'no': 'no', 'q': 'q',
           'верно': 'ok', 'не так': 'no', 'вопрос': 'q',
           'right': 'ok', 'not so': 'no', 'question': 'q'}


def read_answers(root, src, date=None):
    """Ответы клиента -> строки журнала. Один путь, оба канала.

    Клиент возвращает JSON из кнопки внизу страницы — неважно, скопировал он
    его из HTML-файла или из опубликованной страницы. Второго пути для
    вернувшихся пакетов строить нельзя: он уже однажды оказался местом, где
    правки теряются.

    Строка пишется на КАЖДЫЙ ответ, включая «верно». Молчаливое согласие и
    отсутствие ответа выглядят одинаково, а это разные вещи: первое означает,
    что человек прочёл и согласился.
    """
    raw = io.open(src, encoding='utf-8').read().strip()
    try:
        data = json.loads(raw)
    except ValueError as e:
        raise SystemExit('не разбирается как JSON: %s' % e)
    answers = data.get('answers') if isinstance(data, dict) else data
    if not isinstance(answers, list):
        raise SystemExit('в файле нет списка ответов')
    pkg = (data.get('package') or '') if isinstance(data, dict) else ''
    when = date or (data.get('date') if isinstance(data, dict) else None) or _today(root)
    rows_ = []
    for a in answers:
        ident = (a.get('id') or '').strip()
        if not ident:
            continue
        v = VERDICT.get(str(a.get('answer') or '').strip().lower())
        note = (a.get('comment') or '').strip()
        if not v and not note:
            continue
        rows_.append({'date': when, 'doc': 'client/', 'item': ident, 'kind': 'comment',
                      'verdict': v or '', 'why': note or _VERDICT_WORD.get(v, v or ''),
                      'source': 'handoff:%s' % (data.get('handoff') or pkg or 'unknown'),
                      'by': 'client'})
    return rows_


_VERDICT_WORD = {'ok': 'верно', 'no': 'не так', 'q': 'вопрос'}


# Что печатается после сборки. Отдельно от STR, потому что STR — это текст
# ДОКУМЕНТА для заказчика, а это текст ДЛЯ ТОГО, кто собрал: их читают разные
# люди в разных местах, и смешивать их в одном словаре значит переводить их
# вместе, когда переводить надо порознь.
OUT = {
 'ru': dict(
    items='%s к ответу',        # число + слово согласует plural_ru()
    is_file='ФАЙЛ ДЛЯ КЛИЕНТА. Открывается в любом браузере, печатается в PDF, '
            'внизу кнопка «Собрать мои ответы».',
    is_artifact='ЭТО НЕ ФАЙЛ ДЛЯ КЛИЕНТА — это тело артефакта. В браузере оно не '
                'откроется: в нём нет ни <html>, ни <body>, их дописывает издатель.',
    next='Дальше:',
    f1='отдайте файл клиенту;',
    f2='клиент жмёт «Собрать мои ответы» и присылает текст;',
    a1='опубликуйте инструментом Artifact:',
    a2='впишите полученный URL в журнал — командой, а не руками по JSON:',
    a3='отдайте клиенту ссылку;',
    back='ответы вернутся так: /macstack-dev:review --read <файл> — они лягут в '
         'журнал, и следующий пакет подставит их под теми же пунктами.'),
 'en': dict(
    items='%s',                 # 'N answerable item(s)' — согласует plural_en()
    is_file='THE FILE FOR THE CLIENT. Opens in any browser, prints to PDF, and '
            'carries the "collect my answers" button at the bottom.',
    is_artifact='NOT THE FILE FOR THE CLIENT — this is an artifact body. A browser '
                'will not render it: it has no <html> and no <body>; the publisher '
                'adds them.',
    next='Next:',
    f1='give the file to the client;',
    f2='the client presses "collect my answers" and sends you the text;',
    a1='publish it with the Artifact tool:',
    a2='record the URL it returns — with the command, not by hand-editing JSON:',
    a3='give the client the link;',
    back='answers come back this way: /macstack-dev:review --read <file> — they land '
         'in the ledger, and the next package pre-fills them under the same items.'),
}


def plural_ru(n, one, few, many):
    """«24 пунктов» — это не опечатка машины, это машина, которая не умеет
    согласовывать. Строка, которую человек читает после каждой сборки, читается
    десятки раз, и небрежность в ней читается как небрежность во всём остальном."""
    n = abs(int(n))
    if n % 10 == 1 and n % 100 != 11:
        return '%d %s' % (n, one)
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return '%d %s' % (n, few)
    return '%d %s' % (n, many)


def plural_en(n, one, many):
    return '%d %s' % (n, one if abs(int(n)) == 1 else many)


def counted_words(lang, n):
    if lang == 'ru':
        return plural_ru(n, 'пункт', 'пункта', 'пунктов')
    return plural_en(n, 'answerable item', 'answerable items')


def lang_of(root):
    try:
        return doc_lang(root)
    except Exception:                                             # noqa: BLE001
        return 'en'


def record_url(root, handoff, url):
    """Вписать URL опубликованного артефакта в его строку журнала.

    Руками это правка JSONL в 200 строк, и делать её приходится каждый раз после
    публикации. Трижды за одну сессию (живой проект, 2026-08-27) она делалась одноразовым
    скриптом на месте — то есть кодом, который никто не проверял и который негде
    исправить, когда он ошибётся.

    Строка ищется по ИМЕНИ ФАЙЛА, а не по дате: за день собирают несколько
    пакетов, и дата их не различает.
    """
    p_ = os.path.join(root, 'history', 'ledger.jsonl')
    if not os.path.exists(p_):
        raise SystemExit('нет %s' % p_)
    lines, hit = [], 0
    for ln in io.open(p_, encoding='utf-8').read().splitlines():
        if ln.strip():
            r = json.loads(ln)
            if r.get('kind') == 'handoff' and os.path.basename(r.get('doc') or '') == handoff:
                r['url'] = url
                hit += 1
                ln = json.dumps(r, ensure_ascii=False, sort_keys=True)
        lines.append(ln)
    if hit != 1:
        raise SystemExit('строк handoff с именем %s: %d — ожидалась ровно одна'
                         % (handoff, hit))
    io.open(p_, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    return hit


# Имена флагов, которые эта команда понимает. Неизвестный флаг — ОТКАЗ, а не
# молчание: `--slug` без значения (и весь набор, склеенный оболочкой в одну
# строку) раньше просто не узнавался, команда собирала пакет по умолчанию под
# именем по умолчанию и записывала его в журнал как состоявшийся круг. Про
# опечатку не говорилось ничего.
FLAGS = ('date', 'slug', 'artifact', 'lang', 'only', 'skip',
         'read', 'dry', 'record-url', 'handoff')


def main():
    argv = sys.argv[1:]
    args, flags, i = [], {}, 0
    while i < len(argv):
        a = argv[i]
        if a.startswith('--'):
            if '=' in a:
                k, _, v = a[2:].partition('='); flags[k] = v
            elif i + 1 < len(argv) and not argv[i + 1].startswith('--'):
                flags[a[2:]] = argv[i + 1]; i += 1
            else:
                flags[a[2:]] = True
        else:
            args.append(a)
        i += 1
    root = args[0] if args else 'macstack'
    bad = [k for k in flags if k not in FLAGS]
    if bad:
        print('неизвестный ключ: %s' % ', '.join('--' + b for b in bad))
        print('известные: %s' % ' '.join('--' + f for f in FLAGS))
        return 2
    if not os.path.isdir(root):
        print('no macstack/ folder at %s' % root)
        return 1
    if flags.get('record-url'):
        h = flags.get('handoff')
        if not h or h is True:
            print('--record-url требует --handoff <имя файла в history/handoffs/>')
            return 2
        record_url(root, h, flags['record-url'])
        print('URL записан в строку handoff: %s' % h)
        return 0
    if flags.get('read'):
        rows_ = read_answers(root, flags['read'], flags.get('date'))
        import collections as _c
        by = _c.Counter(r['verdict'] or '—' for r in rows_)
        print('ответов: %d  %s' % (len(rows_), dict(by)))
        if flags.get('dry'):
            for r in rows_[:12]:
                print('   %-14s %-5s %s' % (r['item'], r['verdict'], r['why'][:60]))
            print('сухой прогон — в журнал не записано')
            return 0
        ledger.append(root, rows_)
        print('записано в history/ledger.jsonl — следующий пакет подставит эти ответы')
        return 0
    date = flags.get('date') or _today(root)
    slug = flags.get('slug') or 'user-cases'
    artifact = flags.get('artifact') is True or flags.get('artifact') == 'true'
    doc, version, counted, data = build(root, date, slug, flags.get('lang'), artifact,
                                       flags.get('only'), flags.get('skip'))

    outdir = os.path.join(root, 'history', 'handoffs')
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, '%s-%s%s.html' % (date, slug, '-artifact' if artifact else ''))
    if os.path.exists(out):
        print('refusing to overwrite an immutable handoff: %s' % out)
        print('a new round writes a new dated file — pass --date or --slug')
        return 2
    io.open(out, 'w', encoding='utf-8').write(doc)

    # Пакет записывает себя в журнал сам. Без этой строки СЛЕДУЮЩИЙ пакет не знает,
    # от чего считать «что изменилось с прошлого раза», и пометит либо всё, либо
    # ничего. Дата берётся из имени файла — по ней и считает ledger.last_handoff.
    try:
        stem = os.path.basename(out).rsplit('.', 1)[0]
        ledger.append(root, {'date': date, 'doc': 'history/handoffs/' + os.path.basename(out),
                             'item': 'project', 'kind': 'handoff',
                             'now': 'пакет на согласование: %d пунктов, версия %s'
                                    % (counted, version),
                             'source': 'handoff:' + stem, 'by': 'claude'})
    except Exception as e:                                        # noqa: BLE001
        sys.stderr.write('ledger не записан: %s\n' % e)

    # Вывод — на языке документов, и говорит РАЗНОЕ про два разных файла.
    # Прежняя версия печатала два подряд идущих `if artifact:` с одной и той же
    # инструкцией на английском и на русском, а «Дальше» было русским всегда,
    # при английской же первой строке. Читателю это не сообщало главного: что
    # `-artifact.html` НЕЛЬЗЯ отдать клиенту и нельзя открыть в браузере — в нём
    # нет ни <html>, ни <body>, их дописывает издатель.
    W = OUT.get(lang_of(root), OUT['en'])
    print('')
    print(out)
    print('  %s  ·  %s' % (W['items'] % counted_words(lang_of(root), counted),
                           ' · '.join('%s %d' % (k, len(gs)) for k, gs in data if gs)))
    print('')
    if artifact:
        print('  ' + W['is_artifact'])
        print('')
        print('  ' + W['next'])
        print('    1. ' + W['a1'])
        print('       file_path: %s' % out)
        print('    2. ' + W['a2'])
        print('       python3 <package.py> %s --record-url <URL> --handoff %s'
              % (root, os.path.basename(out)))
        print('    3. ' + W['a3'])
        print('    4. ' + W['back'])
    else:
        print('  ' + W['is_file'])
        print('')
        print('  ' + W['next'])
        print('    1. ' + W['f1'])
        print('    2. ' + W['f2'])
        print('    3. ' + W['back'])
    print('')
    return 0


def _today(root):
    """No clock in the body of a rendered document, but a handoff IS dated. Take the
    date from the caller when given; otherwise from the filesystem, once."""
    import datetime
    return datetime.date.today().isoformat()


if __name__ == '__main__':
    sys.exit(main())
