"""`migrate.py` пишет статусы вех только из пятёрки трекера.

Запуск: python3 skills/documents/references/tests/test_migrate_vocabulary.py

Решение владельца (2026-10-04): каноническая лексика статусов — пятёрка трекера
(`backlog · todo · in_progress · done · cancelled`). Таблица вех v1 несёт глифы
`✓ ▶ ⏸ ⊘`; `convert_milestones` переводил их в `done · doing · blocked · dropped` — то
есть в токены, о которых линтер теперь предупреждает. `doing` -> `in_progress`,
`dropped` -> `cancelled`. `blocked` — не статус: настоящий (`todo`) остаётся, а о
препятствии миграция говорит вслух, потому что у вехи нет поля `blocked_by`, и молча
потерять «⏸» значило бы стереть сведение, которое в документе было.
"""
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.dirname(HERE)
sys.path.insert(0, DOCS)
import migrate                                                 # noqa: E402

MILESTONES = u"""| ID | Name | Status | Done when |
|---|---|---|---|
| M1 | A | ✓ | x |
| M2 | B | ▶ | y |
| M3 | C | ⏸ | z |
| M4 | D | ⊘ | w |
| M5 | E | todo | v |
| M6 | F | in_progress | u |
| M7 | G | cancelled | t |
| M8 | H | backlog | s |
"""

def status_of(entities):
    out = {}
    for e in entities:
        ident = re.search(r'macstack:milestone=(\S+)', e).group(1)
        out[ident] = re.search(r'^status:\s*(\S+)', e, re.M).group(1)
    return out


class MilestoneStatuses(unittest.TestCase):
    def test_every_status_written_is_in_the_tracker_five(self):
        ents, n = migrate.convert_milestones(MILESTONES)
        self.assertEqual(n, 8)
        got = status_of(ents)
        self.assertEqual(
            got, {'M1': 'done', 'M2': 'in_progress', 'M3': 'todo', 'M4': 'cancelled',
                  'M5': 'todo', 'M6': 'in_progress', 'M7': 'cancelled', 'M8': 'backlog'})

    def test_no_deprecated_token_is_written(self):
        ents, _ = migrate.convert_milestones(MILESTONES)
        for tok in ('doing', 'blocked', 'dropped'):
            self.assertFalse(any(re.search(r'^status:\s*%s\b' % tok, e, re.M) for e in ents),
                             tok)

    def test_the_deprecated_words_in_a_cell_map_like_their_glyphs(self):
        # A v1 table may carry the word instead of the glyph; the mapping must be the
        # same, or a cell's spelling would decide the migrated status.
        words = (u"| ID | Name | Status | Done when |\n|---|---|---|---|\n"
                 u"| M1 | A | doing | x |\n| M2 | B | blocked | y |\n| M3 | C | dropped | z |\n")
        migrate.MILESTONE_NOTES[:] = []
        ents, n = migrate.convert_milestones(words)
        self.assertEqual(n, 3)
        self.assertEqual(status_of(ents), {'M1': 'in_progress', 'M2': 'todo', 'M3': 'cancelled'})
        self.assertEqual([m for m, _ in migrate.MILESTONE_NOTES], ['M2'])

    def test_a_blocked_milestone_is_reported_not_silently_flattened(self):
        migrate.MILESTONE_NOTES[:] = []
        migrate.convert_milestones(MILESTONES)
        self.assertEqual([m for m, _ in migrate.MILESTONE_NOTES], ['M3'])
        self.assertIn('blocker', migrate.MILESTONE_NOTES[0][1])


if __name__ == '__main__':
    unittest.main(verbosity=2)
