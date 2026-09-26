# -*- coding: utf-8 -*-
"""Форма записи внутри сущности — то, что не покрыто ядром."""
from lint_folder import rule, Finding, ERROR, WARNING


@rule('12.37', 'The first bullet of an entity does not restate its heading')
def r_12_37(c):
    import re
    out = []
    for key in c.client_keys():
        doc = c.docs[key]
        for it in doc.items:
            if it.level < 3 or not it.title:
                continue
            core = re.sub(r'[`*~]', '', it.title).strip().lower()[:36]
            if len(core) < 12:
                continue
            for n in range(it.head_line + 1, min(it.span[1], it.head_line + 6)):
                line = doc.lines[n] if n < len(doc.lines) else ''
                if not line.strip().startswith('-'):
                    continue
                if core in re.sub(r'[`*~]', '', line).strip().lower():
                    out.append(Finding('12.37', ERROR, c.rel(doc.path), n + 1,
                                       '%s: the first bullet repeats the heading — the '
                                       'client reads the same sentence twice'
                                       % (it.id or it.title[:24])))
                    break
    return out
