#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""`history/ledger.jsonl` — every edit and every client comment, keyed by item id.

Why a ledger at all. Until now history lived in two places and served neither: a
per-document journal at the bottom of every client document, and `history/log.md`
for the session. The journal made the client's document longer every week with
rows that mostly recorded the plugin's own migrations — "seeded from macstack.json",
"converted to the v2 block format" — which mean nothing to the person being asked
to correct the text. And neither place recorded WHICH STATEMENT changed, so when a
review package went out there was no way to show the client "this sentence is not
what you read last time, and here is what you said about it."

So: one append-only stream, one line per event, keyed by the id of the thing that
changed. The client documents lose their journals entirely (lint 12.33). The review
package reads this file to mark what moved and to replay a client's own comments
beside the statement they were about.

Why JSON Lines rather than markdown. It is appended, never edited, so two sessions
writing at once cannot conflict on a line. It is queried by item id far more often
than it is read start to finish. And the one consumer that must not misread it — the
package generator — gets a parsed object instead of a regex over prose.

A record:

    {"date": "2026-08-26", "doc": "client/USER-CASES.md", "item": "C-04",
     "kind": "changed", "was": "…", "now": "…",
     "why": "client comment in the 2026-08-25 package",
     "source": "handoff:2026-08-25-user-cases-rev2",
     "task": "M15-T2", "decision": "D42", "by": "claude"}

`kind` is closed:

    added     the statement did not exist before
    changed   it existed and now says something else
    removed   it is gone; `was` carries what it said
    comment   the client said something ABOUT it
    answer    we replied to that comment
    audit     a conformance run reached a verdict on it
    handoff   a review package went to the client
    release   something reached the people who use it
    work      a task was finished

One stream on purpose: the package needs them interleaved in time for a single item,
and a client's comment and the edit it caused are the same story.

The last three carry an `item` of `project` or `doc:<key>` rather than a statement id,
because a package and a release are events about the whole thing. They replace the five
entry kinds of the old `history/log.md`, minus two: `intake` and `merge` get no kind of
their own, because their trace is the EDITS they produced. A row saying "material was
merged" beside rows saying what the merge changed is a summary of its own neighbours,
and it is the row that goes stale first.
"""
import collections, io, json, os, re, sys

KINDS = ('added', 'changed', 'removed', 'comment', 'answer', 'audit',
         'handoff', 'release', 'work')
NAME = 'ledger.jsonl'

Record = dict


def path_of(root):
    return os.path.join(root, 'history', NAME)


def _check(rec):
    if not rec.get('item'):
        raise ValueError('a ledger row without an item id is a row nothing can find: %r'
                         % (rec,))
    if rec.get('kind') not in KINDS:
        raise ValueError('kind %r is not one of %s' % (rec.get('kind'), ', '.join(KINDS)))
    if not rec.get('date'):
        raise ValueError('a ledger row without a date cannot be ordered')
    return rec


def append(root, records, dry=False):
    """Append one record or many. Returns how many were written."""
    if isinstance(records, dict):
        records = [records]
    rows = [_check(dict(r)) for r in records]
    if dry:
        return len(rows)
    p = path_of(root)
    d = os.path.dirname(p)
    if not os.path.isdir(d):
        os.makedirs(d)
    with io.open(p, 'a', encoding='utf-8') as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n')
    return len(rows)


def read(root):
    """Every record, in file order. A malformed line is reported, never skipped silently."""
    p = path_of(root)
    if not os.path.exists(p):
        return []
    out = []
    for n, line in enumerate(io.open(p, encoding='utf-8'), 1):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except ValueError as e:
            sys.stderr.write('%s:%d is not a record: %s\n' % (NAME, n, e))
    return out


def by_item(root, item, kinds=None):
    """One statement's whole story, oldest first — what the package prints beside it."""
    rows = [r for r in read(root) if r.get('item') == item]
    if kinds:
        rows = [r for r in rows if r.get('kind') in kinds]
    return sorted(rows, key=lambda r: (r.get('date') or '', r.get('kind') or ''))


def index(root):
    """item id -> its records, for a package that needs all of them at once."""
    out = collections.defaultdict(list)
    for r in read(root):
        out[r.get('item')].append(r)
    for k in out:
        out[k].sort(key=lambda r: (r.get('date') or '', r.get('kind') or ''))
    return dict(out)


def since(root, date, kinds=None):
    rows = [r for r in read(root) if (r.get('date') or '') > date]
    if kinds:
        rows = [r for r in rows if r.get('kind') in kinds]
    return rows


HANDOFF = re.compile(r'^handoff:(\d{4}-\d{2}-\d{2})')


def last_handoff(root):
    """The date of the newest package the client actually answered against, or None.

    This is what "changed since you last read this" is measured from, so it must be
    the date of the PACKAGE, not of anything we did afterwards. The date comes out of
    the source slug (`handoff:2026-08-25-user-cases-rev2`) rather than out of the row's
    own `date`: a comment carries the day the client wrote it and an answer the day we
    replied, and either would move the mark forward past statements the client has in
    fact never seen — marking them unchanged in the next package.
    """
    dates = []
    for r in read(root):
        m = HANDOFF.match(str(r.get('source') or ''))
        if m:
            dates.append(m.group(1))
    return max(dates) if dates else None


def changed_since(root, date):
    """{item: [records]} for everything that moved after `date` — the CHANGED marks."""
    out = collections.defaultdict(list)
    for r in read(root):
        if (r.get('date') or '') > date and r.get('kind') in ('added', 'changed', 'removed'):
            out[r['item']].append(r)
    return dict(out)


# ---------------------------------------------------------------- CLI
def main():
    argv = sys.argv[1:]
    if not argv:
        print(__doc__.split('\n\n')[0])
        print('\nusage: ledger.py <macstack-dir> [--item C-04] [--since 2026-08-01] '
              '[--kind changed] [--stats]')
        return 0
    root = argv[0]
    def opt(name):
        return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else None
    item, since_, kind = opt('--item'), opt('--since'), opt('--kind')
    rows = read(root)
    if '--stats' in argv:
        by_kind = collections.Counter(r.get('kind') for r in rows)
        by_doc = collections.Counter(r.get('doc') for r in rows)
        items = len({r.get('item') for r in rows})
        print('записей: %d · предметов: %d' % (len(rows), items))
        print('по виду : %s' % ', '.join('%s×%d' % kv for kv in by_kind.most_common()))
        print('по файлу: %s' % ', '.join('%s×%d' % (os.path.basename(k or '—'), v)
                                         for k, v in by_doc.most_common(6)))
        h = last_handoff(root)
        print('последний пакет клиенту: %s' % (h or 'не было'))
        return 0
    if item:
        rows = by_item(root, item)
    if since_:
        rows = [r for r in rows if (r.get('date') or '') > since_]
    if kind:
        rows = [r for r in rows if r.get('kind') == kind]
    for r in rows:
        line = '%s  %-8s %-12s %s' % (r.get('date'), r.get('kind'), r.get('item'),
                                      (r.get('why') or r.get('now') or '')[:80])
        print(line)
        if r.get('was') and r.get('kind') == 'changed':
            print('%s было: %s' % (' ' * 12, str(r['was'])[:80]))
    if not rows:
        print('ничего не найдено')
    return 0


if __name__ == '__main__':
    sys.exit(main())
