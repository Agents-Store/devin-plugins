#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse and write v2 macstack documents: anchors, entities, YAML blocks, sections.

The v1 parser read TABLE COLUMNS BY POSITION, because a heading follows docs.language
and matching on its text would break the moment a project wrote its documents in
German. That worked, and it dragged every piece of prose into a grid to get there.

v2 keeps the language independence and drops the grid. A document is:

    <!-- macstack:doc=<type> lang=<code> version=<v> -->
    # Title

    <!-- macstack:section=<key> -->
    ## Heading in whatever language

    <!-- macstack:<space>=<id> -->
    ### <id> · Title in whatever language

    ```yaml
    key: value          <- machine fields, ASCII keys, one block per entity
    ```

    <!-- macstack:<field> -->
    **Label in whatever language**
    - prose the client reads

Everything a checker needs is an ASCII anchor or a YAML key. Nothing a checker needs
is a heading, a label or a column.

No third-party imports: the plugin promises python3 and jsonschema, nothing else, so
the YAML understood here is the flat subset the contract actually declares — scalars,
inline lists, inline maps and block lists. A document needing more than that is a
document putting prose in the machine half.
"""
import re, io, os

ANCHOR = re.compile(r'^<!--\s*macstack:([a-z_]+)(?:=(\S+))?((?:\s+\w+=\S+)*)\s*-->\s*$')
HEADING = re.compile(r'^(#{1,6})\s+(.*?)\s*$')
FENCE = re.compile(r'^\s*```+\s*(\w+)?\s*$')


# ---------------------------------------------------------------- tiny YAML
def _scalar(v):
    v = v.strip()
    if not v:
        return None
    if v[0] in '"\'' and len(v) > 1 and v[-1] == v[0]:
        return v[1:-1]
    if v.startswith('[') and v.endswith(']'):
        inner = v[1:-1].strip()
        return [_scalar(x) for x in _split_top(inner)] if inner else []
    if v.startswith('{') and v.endswith('}'):
        inner = v[1:-1].strip()
        out = {}
        for part in _split_top(inner):
            if ':' in part:
                k, _, val = part.partition(':')
                out[k.strip()] = _scalar(val)
        return out
    low = v.lower()
    if low in ('true', 'false'):
        return low == 'true'
    if low in ('null', '~', '—', '-'):
        return None
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return v


def _split_top(s):
    """Split on commas that are not inside brackets or quotes."""
    out, buf, depth, q = [], [], 0, None
    for ch in s:
        if q:
            buf.append(ch)
            if ch == q:
                q = None
            continue
        if ch in '"\'':
            q = ch; buf.append(ch); continue
        if ch in '[{':
            depth += 1
        elif ch in ']}':
            depth -= 1
        if ch == ',' and depth == 0:
            out.append(''.join(buf)); buf = []
            continue
        buf.append(ch)
    if ''.join(buf).strip():
        out.append(''.join(buf))
    return [x.strip() for x in out]


def parse_yaml(text):
    """The flat subset the document contract declares. Returns an ordered dict-ish."""
    data, pending_key = {}, None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if stripped.startswith('- ') and pending_key is not None and indent > 0:
            data.setdefault(pending_key, [])
            if isinstance(data[pending_key], list):
                data[pending_key].append(_scalar(stripped[2:]))
            continue
        if ':' in stripped:
            k, _, v = stripped.partition(':')
            k = k.strip()
            if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', k):
                continue
            if v.strip():
                data[k] = _scalar(v)
                pending_key = None
            else:
                data[k] = []
                pending_key = k
    return data


def dump_yaml(data):
    """Emit the same flat subset, deterministically, in the order given."""
    lines = []
    for k, v in data.items():
        if v is None:
            lines.append('%s: —' % k)
        elif isinstance(v, bool):
            lines.append('%s: %s' % (k, 'true' if v else 'false'))
        elif isinstance(v, (list, tuple)):
            if not v:
                lines.append('%s: []' % k)
            else:
                lines.append('%s: [%s]' % (k, ', '.join(_q(x) for x in v)))
        elif isinstance(v, dict):
            lines.append('%s: { %s }' % (k, ', '.join('%s: %s' % (a, _q(b)) for a, b in v.items())))
        else:
            lines.append('%s: %s' % (k, _q(v)))
    return '\n'.join(lines)


def _q(v):
    if isinstance(v, bool):
        # A nested map used to emit Python's True/False, which round-trips back as the
        # STRING "True" rather than a boolean. Owning the bool case at the leaf fixes it
        # everywhere instead of at each call site.
        return 'true' if v else 'false'
    if v is None:
        return '—'
    s = str(v)
    if s == '':
        return "''"
    if re.search(r'[:#\[\]{},]|^\s|\s$', s):
        return "'%s'" % s.replace("'", "''")
    return s


# ---------------------------------------------------------------- document
class Block(object):
    """One anchored region: a section, an entity, or a field inside an entity."""
    __slots__ = ('kind', 'id', 'attrs', 'heading', 'level', 'yaml', 'body', 'children',
                 'start', 'end')

    def __init__(self, kind, ident=None, attrs=None):
        self.kind = kind; self.id = ident; self.attrs = attrs or {}
        self.heading = None; self.level = 0
        self.yaml = {}; self.body = []; self.children = []
        self.start = self.end = 0

    def text(self):
        return '\n'.join(self.body).strip()

    def field(self, key):
        for c in self.children:
            if c.kind == key:
                return c
        return None

    def __repr__(self):
        return '<%s %s>' % (self.kind, self.id or '')


def parse(text):
    """Return (header_attrs, [top-level Blocks]). Entities nest their field blocks."""
    lines = text.splitlines()
    header, blocks = {}, []
    cur_section = cur_entity = None
    pending = None          # anchor seen, waiting for its heading
    in_fence = None
    fence_buf, fence_lang = None, None
    sink = None             # where plain lines go

    def close_fence(target):
        if fence_lang == 'yaml' and target is not None and not target.yaml:
            target.yaml = parse_yaml('\n'.join(fence_buf))
        elif target is not None:
            target.body.append('```%s' % (fence_lang or ''))
            target.body.extend(fence_buf)
            target.body.append('```')

    for n, raw in enumerate(lines):
        f = FENCE.match(raw)
        if in_fence is not None:
            if f and (f.group(1) is None):
                close_fence(sink if sink is not None else cur_entity)
                in_fence = None; fence_buf = None; fence_lang = None
            else:
                fence_buf.append(raw)
            continue
        if f:
            in_fence = True; fence_buf = []; fence_lang = f.group(1)
            continue

        a = ANCHOR.match(raw)
        if a:
            kind, ident, extra = a.group(1), a.group(2), a.group(3) or ''
            attrs = dict(re.findall(r'(\w+)=(\S+)', extra))
            if kind == 'doc':
                header = dict(attrs); header['doc'] = ident
                continue
            b = Block(kind, ident, attrs)
            b.start = n
            if kind == 'section':
                cur_section = b; cur_entity = None; blocks.append(b); sink = b
            elif ident is not None:
                cur_entity = b
                (cur_section.children if cur_section is not None else blocks).append(b)
                sink = b
            else:                       # a field inside the current entity
                target = cur_entity or cur_section
                if target is not None:
                    target.children.append(b)
                else:
                    blocks.append(b)
                sink = b
            pending = b
            continue

        h = HEADING.match(raw)
        if h and pending is not None and pending.heading is None:
            pending.level = len(h.group(1)); pending.heading = h.group(2)
            pending = None
            continue
        if h:
            pending = None
            if sink is not None:
                sink.body.append(raw)
            continue

        if sink is not None:
            sink.body.append(raw)

    if in_fence is not None:
        close_fence(sink if sink is not None else cur_entity)
    return header, blocks


def entities(blocks, kind=None):
    """Flatten every entity block, optionally filtered by anchor kind."""
    out = []
    for b in blocks:
        if b.kind == 'section':
            for c in b.children:
                if c.id is not None and (kind is None or c.kind == kind):
                    out.append(c)
        elif b.id is not None and (kind is None or b.kind == kind):
            out.append(b)
    return out


def sections(blocks):
    return dict((b.id, b) for b in blocks if b.kind == 'section')


# ---------------------------------------------------------------- writing
def doc_header(doc_type, lang, version):
    return '<!-- macstack:doc=%s lang=%s version=%s -->' % (doc_type, lang, version)


def anchor(kind, ident=None):
    return '<!-- macstack:%s%s -->' % (kind, ('=' + str(ident)) if ident is not None else '')


def entity(kind, ident, title, yaml_fields, fields, level=3):
    """Render one entity. `fields` is [(anchor_key, label, body_lines)]."""
    out = [anchor(kind, ident), '%s %s · %s' % ('#' * level, ident, title), '']
    if yaml_fields:
        out += ['```yaml', dump_yaml(yaml_fields), '```', '']
    for key, label, body in fields:
        out.append(anchor(key))
        if label:
            out.append('**%s**' % label)
        out.extend(body)
        out.append('')
    return '\n'.join(out).rstrip() + '\n'


# ---------------------------------------------------------------- measuring
CELL_SPLIT = re.compile(r'(?<!\\)\|')


def tables(text):
    """Every markdown table, as (start_line, header_cells, [row_cells])."""
    lines = text.splitlines()
    out, i = [], 0
    in_fence = False
    while i < len(lines):
        if FENCE.match(lines[i]):
            in_fence = not in_fence
            i += 1; continue
        if not in_fence and lines[i].lstrip().startswith('|') and i + 1 < len(lines) \
                and re.match(r'^\s*\|[\s:\-|]+\|\s*$', lines[i + 1]):
            head = _cells(lines[i]); rows = []
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith('|'):
                rows.append(_cells(lines[j])); j += 1
            out.append((i, head, rows))
            i = j; continue
        i += 1
    return out


CODESPAN = re.compile(r'`[^`]*`')


def _cells(line):
    """Split a table row. A pipe inside a code span is content, not a separator —
    `app | migrate | postgres` is one cell, and treating it as three silently truncates
    the row and everything downstream of it."""
    line = line.strip()
    spans = []

    def hide(m):
        spans.append(m.group(0))
        return '\x00%d\x00' % (len(spans) - 1)

    line = CODESPAN.sub(hide, line)
    parts = CELL_SPLIT.split(line)
    if parts and not parts[0].strip():
        parts = parts[1:]
    if parts and not parts[-1].strip():
        parts = parts[:-1]
    out = []
    for p in parts:
        for i, s in enumerate(spans):
            p = p.replace('\x00%d\x00' % i, s)
        out.append(p.strip())
    return out


BUDGET = dict(max_columns=4, max_cell_chars=80, min_rows=3,
              forbid=('<br>', '**', '```', '|'))


def table_violations(text, exempt_anchors=('journal',)):
    """Rule 12.24. Returns [(line, columns, longest_cell_len, longest_cell, reason)]."""
    lines = text.splitlines()
    bad = []
    for start, head, rows in tables(text):
        # a journal is exempt: find the nearest anchor above
        ctx = '\n'.join(lines[max(0, start - 6):start])
        if any(('macstack:section=%s' % e) in ctx or ('macstack:table=%s' % e) in ctx
               for e in exempt_anchors):
            continue
        cells = [c for row in rows for c in row] + head
        longest = max(cells, key=len) if cells else ''
        reasons = []
        if len(head) > BUDGET['max_columns']:
            reasons.append('%d columns' % len(head))
        if len(longest) > BUDGET['max_cell_chars']:
            reasons.append('cell of %d chars' % len(longest))
        for token in BUDGET['forbid']:
            if token == '|':
                continue
            # Bold on a short cell is a term in a legend, not prose in a grid. Bold
            # inside a long cell is the smell this rule exists for.
            limit = 40 if token == '**' else 0
            if any(token in c and len(c) > limit for c in cells):
                reasons.append('%s inside a cell' % token)
        if reasons:
            bad.append((start + 1, len(head), len(longest), longest, '; '.join(sorted(set(reasons)))))
    return bad


CYR = re.compile(r'[\u0400-\u04FF]')
LAT = re.compile(r'[A-Za-z]')
STRIP = re.compile(r'(```.*?```|`[^`]*`|<!--.*?-->|\[[^\]]*\]\([^)]*\))', re.S)
IDTOK = re.compile(r'\bC?[A-Z]-\d{2}(\.[aT]\d+)?\b|\bM\d+(-T\d+)?\b|\bQ?[AB]\d+\b|\bD\d+\b|\bBL-\d+\b')


def strip_fences(text):
    """Remove fenced blocks by tracking fences LINE BY LINE, not by regex pairing.

    A regex that pairs ``` with the next ``` breaks on a document that mentions the fence
    syntax in its own prose — one stray mention shifts every later pair by one, so the
    real yaml blocks stop being stripped and the prose between them starts being. Found
    on a live document whose 'how to edit this' section named ```yaml as text: the
    language check then read it as 84% foreign when it was 15%."""
    out, inside = [], False
    for line in text.splitlines():
        if FENCE.match(line):
            inside = not inside
            continue
        out.append('' if inside else line)
    return '\n'.join(out)


def foreign_ratio(text, lang):
    """Rule 12.25. Share of letters from the wrong alphabet outside code, anchors and ids."""
    body = strip_fences(text)
    body = STRIP.sub(' ', body)
    body = IDTOK.sub(' ', body)
    cyr = len(CYR.findall(body))
    lat = len(LAT.findall(body))
    total = cyr + lat
    if total < 200:
        return 0.0
    if lang in ('ru', 'uk'):
        return lat / float(total)
    return cyr / float(total)


if __name__ == '__main__':
    import sys, json
    src = io.open(sys.argv[1], encoding='utf-8').read()
    hdr, bl = parse(src)
    print('header:', hdr)
    for b in bl:
        print(' section', b.id, '->', [(c.kind, c.id, sorted(c.yaml)) for c in b.children][:6])
    print('table violations:', table_violations(src))
