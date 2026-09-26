#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Edit macstack.json in place without reformatting it.

`json.load` then `json.dump(indent=2)` looks like the safe way to change one field.
Measured on a live spec: 959 lines became 4119. The file is hand-formatted with
judgment — short objects inlined as `{ "slug": "app", "status": "planned" }`, a long
goal object kept on one line because it reads better there — and no width heuristic
reproduces that. A whole-file reformat turns a three-line change into an unreviewable
diff and throws away formatting a human chose.

So: parse for the DECISION, edit the TEXT for the write. This module finds the exact
character span of any value by path and replaces it, leaving every other byte alone.

Every writer here re-parses the result and compares it to the intended structure before
returning. An edit that does not produce the object it promised is refused, not written.
"""
import json, re, collections

WS = ' \t\r\n'


class Span(object):
    __slots__ = ('start', 'end', 'key_start', 'children')

    def __init__(self, start, end, key_start=None):
        self.start, self.end, self.key_start = start, end, key_start
        self.children = collections.OrderedDict()

    def __repr__(self):
        return '<span %d:%d>' % (self.start, self.end)


def _skip(s, i):
    while i < len(s) and s[i] in WS:
        i += 1
    return i


def _string_end(s, i):
    assert s[i] == '"'
    i += 1
    while i < len(s):
        if s[i] == '\\':
            i += 2
            continue
        if s[i] == '"':
            return i + 1
        i += 1
    raise ValueError('unterminated string at %d' % i)


def _scan(s, i):
    """Return (Span, next_index) for the value starting at i."""
    i = _skip(s, i)
    start = i
    c = s[i]
    if c == '{':
        sp = Span(start, None)
        i += 1
        while True:
            i = _skip(s, i)
            if s[i] == '}':
                i += 1
                break
            key_start = i
            ke = _string_end(s, i)
            key = json.loads(s[i:ke])
            i = _skip(s, ke)
            assert s[i] == ':', 'expected : at %d' % i
            child, i = _scan(s, i + 1)
            child.key_start = key_start
            sp.children[key] = child
            i = _skip(s, i)
            if s[i] == ',':
                i += 1
                continue
            if s[i] == '}':
                i += 1
                break
            raise ValueError('expected , or } at %d' % i)
        sp.end = i
        return sp, i
    if c == '[':
        sp = Span(start, None)
        i += 1
        n = 0
        while True:
            i = _skip(s, i)
            if s[i] == ']':
                i += 1
                break
            child, i = _scan(s, i)
            sp.children[n] = child
            n += 1
            i = _skip(s, i)
            if s[i] == ',':
                i += 1
                continue
            if s[i] == ']':
                i += 1
                break
            raise ValueError('expected , or ] at %d' % i)
        sp.end = i
        return sp, i
    if c == '"':
        e = _string_end(s, i)
        return Span(start, e), e
    m = re.compile(r'-?\d+(\.\d+)?([eE][-+]?\d+)?|true|false|null').match(s, i)
    if not m:
        raise ValueError('bad value at %d: %r' % (i, s[i:i + 20]))
    return Span(start, m.end()), m.end()


def index(raw):
    sp, _ = _scan(raw, 0)
    return sp


def locate(root, path):
    """Span for a key path, or None. Path elements are dict keys or list indices."""
    sp = root
    for p in path:
        if p not in sp.children:
            return None
        sp = sp.children[p]
    return sp


def indent_at(raw, pos):
    line_start = raw.rfind('\n', 0, pos) + 1
    return raw[line_start:pos] if raw[line_start:pos].strip() == '' else ''


def render(value, pad):
    """Serialize a value the way this file would: compact when it was compact."""
    txt = json.dumps(value, ensure_ascii=False, indent=2)
    if '\n' not in txt:
        return txt
    return txt.replace('\n', '\n' + pad)


def set_value(raw, path, value, create=False):
    """Replace one value, leaving every other byte untouched.

    create=True inserts the key when it is absent — needed because docs.files entries are
    hand-written and half of them carry no `version` at all, which is exactly the state
    rule 12.5 exists to end."""
    sp = locate(index(raw), path)
    if sp is None:
        if create and len(path) > 1 and locate(index(raw), path[:-1]) is not None:
            return insert_key(raw, path[:-1], path[-1], value)
        raise KeyError('/'.join(str(p) for p in path))
    pad = indent_at(raw, sp.key_start if sp.key_start is not None else sp.start)
    out = raw[:sp.start] + render(value, pad) + raw[sp.end:]
    return _verify(raw, out, path, value)


def rename_key(raw, parent_path, old, new):
    sp = locate(index(raw), list(parent_path) + [old])
    if sp is None:
        raise KeyError(old)
    ks = sp.key_start
    ke = _string_end(raw, ks)
    return raw[:ks] + json.dumps(new, ensure_ascii=False) + raw[ke:]


def insert_key(raw, parent_path, key, value):
    """Append a key to an object, matching the indentation of its last member."""
    parent = locate(index(raw), parent_path)
    if parent is None:
        raise KeyError('/'.join(str(p) for p in parent_path))
    if not parent.children:
        raise ValueError('cannot infer indentation of an empty object')
    last = list(parent.children.values())[-1]
    pad = indent_at(raw, last.key_start)
    if not pad:
        # The object is written on one line — `{ "path": "...", "version": "1.8" }`.
        # Expanding it would reformat a file whose formatting is the thing we are
        # protecting, so the key goes in beside its siblings, inline, same as they are.
        inline = json.dumps(value, ensure_ascii=False)
        if '\n' in inline:
            raise ValueError('refusing to inline a multi-line value into a one-line object')
        text = ', %s: %s' % (json.dumps(key, ensure_ascii=False), inline)
        return raw[:last.end] + text + raw[last.end:]
    text = ',\n%s%s: %s' % (pad, json.dumps(key, ensure_ascii=False), render(value, pad))
    return raw[:last.end] + text + raw[last.end:]


def _verify(before, after, path, value):
    """An edit that does not produce what it promised is refused, not written."""
    try:
        got = json.loads(after)
    except ValueError as e:
        raise ValueError('edit produced invalid JSON: %s' % e)
    node = got
    for p in path:
        node = node[p]
    if node != value:
        raise ValueError('edit did not take at %s' % '/'.join(str(p) for p in path))
    old = json.loads(before)
    if _shape(old) != _shape(got):
        raise ValueError('edit changed the document shape')
    return after


def _shape(o, depth=0):
    if depth > 2:
        return type(o).__name__
    if isinstance(o, dict):
        return ('d', tuple((k, _shape(v, depth + 1)) for k, v in o.items()))
    if isinstance(o, list):
        return ('l', len(o))
    return type(o).__name__
