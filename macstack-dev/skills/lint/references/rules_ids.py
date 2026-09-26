# -*- coding: utf-8 -*-
"""Group 12.3-12.6, 12.34 - ids, cross-references, checked copies, pointer identity.

12.3/12.4 read id tokens straight off the document TEXT rather than trusting
`v3.Item.id` everywhere, on purpose. `v3._split_heading` only recognises an id when
it sits before a middle dot (`### A1 · Title`); the live corpus's own §B section
writes `### B7 — Title` (an em dash), which the parser silently fails to split, so
`it.id` comes back `None` and the item vanishes from every kind-filtered lookup with
no error anywhere. A rule that trusts `it.id` for these headings would be exactly as
blind as the parser. Scanning the raw line for "the token right after the hashes"
sidesteps that: it does not care which separator character follows.

The same raw-text approach is what makes the homoglyph check possible at all: a
Cyrillic capital KA (U+041A) in `### К-1 · ...` LOOKS like `K-1` to a human and to
`grep 'K-1'`, but `re.match(r'^K-\\d+$', tok)` correctly says no. Folding the classic
Cyrillic/Greek confusables back to ASCII and re-testing is what turns "silently not
an id" into "an id, spelled wrong" - the finding this rule exists to produce.
"""
import re, io, os, glob
import v3
import mdblocks
from lint_folder import rule, Finding, ERROR, WARNING, _binding_for, _glob

# ---------------------------------------------------------------- confusables
# Only the letters that actually occur as the FIRST character of an id token in
# this project's spaces (A B C D K M N O R S T X Z, plus their lowercase kin for
# the slug spaces). Widening this table further would start folding ordinary
# Cyrillic prose into false id-shapes; see the safety argument at each call site.
_CONFUSABLE = {
    u'А': 'A', u'В': 'B', u'Е': 'E', u'К': 'K', u'М': 'M',
    u'Н': 'H', u'О': 'O', u'Р': 'P', u'С': 'C', u'Т': 'T',
    u'У': 'Y', u'Х': 'X', u'Β': 'B', u'Ν': 'N', u'Ρ': 'P',
    u'а': 'a', u'е': 'e', u'о': 'o', u'р': 'p', u'с': 'c',
    u'у': 'y', u'х': 'x',
}


def _fold(token):
    return ''.join(_CONFUSABLE.get(ch, ch) for ch in token)


# ---------------------------------------------------------------- raw-line extraction
# "The first token after the hashes" - works for every heading-based id space this
# project has (`### A1 · ...`, `### К-1 · ...`, `## M11 · ...`, `### BL-3 · ...`)
# because in every one of them the id is the first thing on the line, regardless of
# which separator or which script follows it.
_HEAD_TOKEN = re.compile(r'^#{2,6}\s+~*([^\s~]+)~*(?:\s|$)')
# The slug spaces (role/role_task/trigger/screen) put the id LAST instead, in
# backticks: "<title> — `<slug>`". Greedy .* finds the trailing pair even when the
# title itself quotes something in backticks.
_SLUG_TOKEN = re.compile(r'^#{2,6}\s+.*`([^`]+)`\s*$')
# Decisions are not headings at all - one registry bullet per decision.
_BULLET_TOKEN = re.compile(r'^\s*-\s+\*\*([^*]+)\*\*')
# A slug is an id only under an ENTITY heading, and an entity heading is the line
# right below its pointer. Without that gate `_SLUG_TOKEN` reads any heading whose
# title happens to end in a backticked term, and two howto headings quoting the same
# file name become a duplicate-id error against a document that has none.
_POINTER = re.compile(r'^\s*<!--\s*macstack:ref=')
_FENCE = re.compile(r'^\s*```')


def _unfenced(lines):
    """The same lines, every fenced region blanked, every position kept.

    Everything else in this codebase strips fences before reading text - v3,
    mdblocks, 12.24, 12.25 - and these three scanners did not. A ```markdown block
    in DECISIONS.md's own "how to use this" section, showing a specimen registry
    row `- **D99** ...`, registered D99 as a real decision and turned the gap check
    into fifty-four invented findings. Quoted text is not an assignment. Blanking
    rather than dropping is what keeps the line number a finding quotes truthful.
    """
    out, inside = [], False
    for line in lines:
        if _FENCE.match(line):
            inside = not inside
            out.append('')
            continue
        out.append('' if inside else line)
    return out


def _prev_nonblank(lines, i):
    """The line above index `i`, skipping blanks. '' when there is none."""
    j = i - 1
    while j >= 0 and not lines[j].strip():
        j -= 1
    return lines[j] if j >= 0 else ''


def _heading_tokens(lines):
    lines = _unfenced(lines)
    out = []
    for n, line in enumerate(lines, 1):
        m = _HEAD_TOKEN.match(line)
        if m:
            out.append((n, m.group(1), line))
    return out


def _slug_tokens(lines):
    lines = _unfenced(lines)
    out = []
    for n, line in enumerate(lines, 1):
        m = _SLUG_TOKEN.match(line)
        if m and _POINTER.match(_prev_nonblank(lines, n - 1)):
            out.append((n, m.group(1), line))
    return out


def _bullet_tokens(lines):
    lines = _unfenced(lines)
    out = []
    for n, line in enumerate(lines, 1):
        m = _BULLET_TOKEN.match(line)
        if m:
            out.append((n, m.group(1), line))
    return out


def _check_space(out, seen, path, occurrences, strict, space):
    """Classify every candidate token against one id space.

    A token that matches `strict` outright is a normal id and goes into `seen` for
    the uniqueness pass below. A token that only matches AFTER folding confusables
    is the homoglyph itself - reported here, immediately, because 12.4 and 12.6
    would otherwise just report the id as "missing" with no clue why. Anything that
    matches neither is not id-shaped for this space at all (ordinary heading prose,
    e.g. "## Как читать этот документ") and is silently skipped, on
    purpose: folding a handful of letters never turns real prose into a valid id
    shape, since the shape still demands the digits/hyphens land in the right spots.
    """
    strict_re = re.compile(strict)
    for lineno, raw, line in occurrences:
        if strict_re.match(raw):
            seen.setdefault((space, raw), []).append((path, lineno, line))
            continue
        folded = _fold(raw)
        if folded != raw and strict_re.match(folded):
            bad = ['position %d: %r (U+%04X)' % (i, ch, ord(ch))
                   for i, ch in enumerate(raw) if ord(ch) > 127]
            out.append(Finding('12.3', ERROR, path, lineno,
                                '%s reads as a %s id but is not ASCII - %s. It greps as '
                                'absent and drops silently out of every %s cross-reference.'
                                % (raw, space, '; '.join(bad), space)))
            # still register it under the id it was clearly TRYING to be, so a
            # second, genuine A1 elsewhere in the document is still caught as a
            # reuse rather than swallowed by this token's own ASCII finding.
            seen.setdefault((space, folded), []).append((path, lineno, line))


@rule('12.3', 'ID integrity - unique per space, ASCII-only, D has no gaps, '
      'A/B numbers are never reused after a strike')
def r_12_3(c):
    out = []
    seen = {}          # (space, id) -> [(path, line, raw_line)]

    def scan(lines, path, extractor, strict, space):
        if lines is None:
            return
        _check_space(out, seen, path, extractor(lines), strict, space)

    # case - X-01..Z-15 &c, headings in USER-CASES.md
    if 'user_cases' in c.docs:
        doc = c.docs['user_cases']
        scan(doc.lines, c.rel(doc.path), _heading_tokens, r'^C?[A-Z]-[0-9]{2}$', 'case')

    # open_item - A<n>/B<n>, headings in OPEN-QUESTIONS.md (see module docstring
    # for why this reads raw lines instead of it.id)
    if 'open_questions' in c.docs:
        doc = c.docs['open_questions']
        scan(doc.lines, c.rel(doc.path), _heading_tokens, r'^[AB][0-9]+$', 'open_item')

    # decision - D<n>, registry bullets in DECISIONS.md
    dtext = c.text.get('decisions')
    dpath = c.path_of('decisions')
    if dtext is not None:
        scan(dtext.splitlines(), c.rel(dpath), _bullet_tokens, r'^D[0-9]+$', 'decision')

    # contradiction/addition - K-<n>/N-<n>, headings inside every dated delta.
    # Deltas are dated instances (path carries <slug>), so Ctx never loads them -
    # this is the one place in the group that has to glob for itself.
    for p in sorted(glob.glob(os.path.join(c.root, 'history', 'deltas', '*.md'))):
        try:
            lines = io.open(p, encoding='utf-8').read().splitlines()
        except IOError:
            continue
        scan(lines, c.rel(p), _heading_tokens, r'^K-[0-9]+$', 'contradiction')
        scan(lines, c.rel(p), _heading_tokens, r'^N-[0-9]+$', 'addition')

    # milestone/task/backlog - headings in TASKS.md
    ttext = c.text.get('tasks')
    tpath = c.path_of('tasks')
    if ttext is not None:
        tlines = ttext.splitlines()
        scan(tlines, c.rel(tpath), _heading_tokens, r'^M[0-9]+$', 'milestone')
        scan(tlines, c.rel(tpath), _heading_tokens, r'^M[0-9]+-T[0-9]+$', 'task')
        scan(tlines, c.rel(tpath), _heading_tokens, r'^BL-[0-9]+$', 'backlog')

    # release - R-YYYY-MM-DD, headings in CHANGELOG.md
    ctext = c.text.get('changelog')
    cpath = c.path_of('changelog')
    if ctext is not None:
        scan(ctext.splitlines(), c.rel(cpath), _heading_tokens,
             r'^R-[0-9]{4}-[0-9]{2}-[0-9]{2}$', 'release')

    # role / role_task / trigger (all three share one document and one heading
    # shape) and screen - the id sits in backticks at the END of the heading.
    # Kept as one 'slug' space per document rather than one per contract kind:
    # splitting further would need section-aware parsing this scan does not do,
    # and the live corpus carries no role/trigger/task naming collision to miss
    # (checked directly against the v3-parsed ids before writing this).
    for key in ('automation', 'ux_ui'):
        if key in c.docs:
            doc = c.docs[key]
            scan(doc.lines, c.rel(doc.path), _slug_tokens,
                 r'^[a-z0-9]+([-.][a-z0-9]+)*$', 'slug:%s' % key)

    # -------- unique per space (this also covers "never reused after a strike":
    # a struck id and a fresh one written under the same number are, structurally,
    # two definitions of the same id, which is exactly what this catches) --------
    for (space, ident), occ in sorted(seen.items()):
        if len(occ) < 2:
            continue
        first_path, first_line, _ = occ[0]
        struck = any(('~~%s~~' % ident) in raw or 'CLOSED' in raw for _, _, raw in occ)
        for path, lineno, raw in occ[1:]:
            why = (' - A/B numbers are never reused after a strike-through'
                   if space == 'open_item' and struck else '')
            out.append(Finding('12.3', ERROR, path, lineno,
                                '%s %s reused: already assigned at %s:%d%s'
                                % (space, ident, first_path, first_line, why)))

    # -------- D-numbering has no gaps --------
    dnums = sorted(int(i[1:]) for (sp, i) in seen if sp == 'decision')
    if dnums:
        missing = [n for n in range(1, dnums[-1] + 1) if n not in dnums]
        if missing:
            out.append(Finding('12.3', ERROR, c.rel(dpath), 0,
                                'D-numbering has a gap: D%s never assigned, between D1 '
                                'and D%d' % (', D'.join(str(n) for n in missing), dnums[-1])))

    return out


# ---------------------------------------------------------------- 12.4 shared lookups
def _open_item_ids(c):
    """{id: (line, closed)} for every A/B heading in OPEN-QUESTIONS.md.

    Raw scan, not it.id - see the module docstring. `closed` follows the rule text
    verbatim: struck (`~~A6~~`) and/or the word CLOSED in the heading line.
    """
    doc = c.docs.get('open_questions')
    if doc is None:
        return None
    out = {}
    for n, tok, line in _heading_tokens(doc.lines):
        if re.match(r'^[AB][0-9]+$', tok):
            closed = (('~~%s~~' % tok) in line) or ('CLOSED' in line)
            out[tok] = (n, closed)
    return out


def _walk_strings(node, path):
    """Every string leaf of a JSON value, paired with its dotted/indexed path."""
    if isinstance(node, dict):
        for k, v in node.items():
            for x in _walk_strings(v, path + '.' + k):
                yield x
    elif isinstance(node, list):
        for i, v in enumerate(node):
            for x in _walk_strings(v, '%s[%d]' % (path, i)):
                yield x
    elif isinstance(node, str):
        yield (path, node)


def _as_list(v):
    if v is None or v == '':
        return []
    return v if isinstance(v, list) else [v]


def _v3_style_field(body_lines, field_key, lang):
    """Fall back to a v3 "- **Label:** value" bullet when a plain doc carries one.

    TEST-CASES.md and TASKS.md are still v2 (fenced yaml) everywhere they have been
    measured - see the module this rule reads from, `doc-contracts.json`, which
    marks them without `format: v3`. But their `covers`/`blocked_by` sections are
    currently empty, so which shape the FIRST real entry will use is not yet
    decided; trying both means the rule keeps working either way instead of
    silently going blind the day someone writes the first one by hand.

    What "both" reaches is bounded by the contract, and the bound is worth stating
    because it was measured rather than assumed: `covers` carries a declared label
    (`Проверяет`) and so reads from a bullet in any language the contract knows;
    `blocked_by` carries none, so only its yaml form and a literal `**blocked_by:**`
    bullet read. Give it a label in `doc-contracts.json` and the rest follows.
    """
    labels = v3.READ.get(lang) or v3.READ['en']
    bullet = re.compile(r'^\s*[-*]\s+\*\*(.+?):\*\*\s*(.*)$')
    for line in body_lines:
        m = bullet.match(line)
        if not m:
            continue
        lab = m.group(1).strip().lower()
        # The ASCII key itself counts as a label. `blocked_by` is declared nowhere in
        # `doc-contracts.json` `fields`, so `v3.READ` has no translation to look up and
        # this fallback was structurally dead for it - measured, by writing the bullet
        # form and watching the rule stay silent on a dangling id. Accepting the key is
        # not an invented translation; it is the key. Anything else must be declared in
        # the contract first, and until it is, the yaml form is the only shape that reads.
        if labels.get(lab) == field_key or lab == field_key:
            return v3._value(m.group(2), lang)
    return None


def _entity_value(entity, field_key, lang):
    if entity.yaml and field_key in entity.yaml:
        return entity.yaml[field_key]
    return _v3_style_field(entity.body, field_key, lang)


def _acceptance_counts(c):
    """{case id: number of acceptance bullets} - the valid range for `<case>.a<n>`."""
    doc = c.docs.get('user_cases')
    if doc is None:
        return {}
    lang = doc.header.get('lang') or c.lang
    label = c.prose_label('acceptance', lang)
    decl, items = c.entities_of('user_cases', 'case')
    out = {}
    for it in items:
        body = it.sections.get(label) or []
        out[it.id] = sum(1 for l in body if l.lstrip().startswith('-'))
    return out


def _ids_of(c, key, kind):
    decl, items = c.entities_of(key, kind)
    return set(it.id for it in items if it.id)


D_CITE = re.compile(r'(?<![A-Za-z0-9_-])D([0-9]+)(?![A-Za-z0-9_-])')
AB_CITE = re.compile(r'(?<![A-Za-z0-9_-])([AB][0-9]+)(?![A-Za-z0-9_-])')


@rule('12.4', 'Cross-file refs - every id an ERROR resolves to a live target')
def r_12_4(c):
    out = []

    # -------- every D<n> cited anywhere resolves in DECISIONS.md --------
    known_d = set(tok for _, tok, _ in _bullet_tokens((c.text.get('decisions') or '').splitlines())
                  if re.match(r'^D[0-9]+$', tok))
    if c.text.get('decisions') is not None:
        for p in sorted(glob.glob(os.path.join(c.root, '**', '*.md'), recursive=True)):
            try:
                text = io.open(p, encoding='utf-8').read()
            except IOError:
                continue
            # `_unfenced`, not `splitlines`: a howto that shows how a citation is
            # written ("следующий номер - D45") is quoting a form, not naming a
            # decision, and reporting it as dangling is how a linter gets muted.
            for n, line in enumerate(_unfenced(text.splitlines()), 1):
                for m in D_CITE.finditer(line):
                    tok = m.group(0)
                    if tok not in known_d:
                        out.append(Finding('12.4', ERROR, c.rel(p), n,
                                            '%s cited here does not resolve in '
                                            'DECISIONS.md' % tok))
        for path, text in _walk_strings(c.spec, 'macstack.json'):
            for m in D_CITE.finditer(text):
                tok = m.group(0)
                if tok not in known_d:
                    out.append(Finding('12.4', ERROR, 'macstack.json', 0,
                                        '%s at %s does not resolve in DECISIONS.md'
                                        % (tok, path)))

    # -------- every A<n>/B<n> in spec.lifecycle.* resolves to a live item --------
    open_items = _open_item_ids(c)
    if open_items is not None:
        cited = {}
        for path, text in _walk_strings(c.spec.get('lifecycle') or {}, 'lifecycle'):
            for m in AB_CITE.finditer(text):
                cited.setdefault(m.group(1), []).append(path)
        for tok, paths in sorted(cited.items()):
            if tok not in open_items:
                out.append(Finding('12.4', ERROR, 'macstack.json', 0,
                                    '%s at %s does not resolve to any heading in '
                                    'OPEN-QUESTIONS.md' % (tok, paths[0])))

    # -------- roles[].cases prefix yields >=1 case heading; letter -> one role --------
    case_ids = _ids_of(c, 'user_cases', 'case')
    if 'user_cases' in c.docs:
        roles = c.spec.get('roles') or []
        for r in roles:
            for g in (r.get('cases') or []):
                if isinstance(g, str) and not any(_glob(g, cid) for cid in case_ids):
                    out.append(Finding('12.4', ERROR, 'macstack.json', 0,
                                        "roles[id=%s].cases glob %r matches no case "
                                        "heading in USER-CASES.md" % (r.get('id'), g)))
        # Буква РОЛИ — та, что стоит непосредственно перед дефисом, а не первая
        # в строке. В двухбуквенной форме первая буква всегда `C` («case»), и
        # `cid[0]` сложил бы все кейсы всех ролей в одну корзину `C`, после чего
        # правило 12.4 сообщало бы, что кейсы заявлены более чем одной ролью —
        # на совершенно исправном файле.
        by_letter = {}
        for cid in case_ids:
            head = cid.split('-', 1)[0]
            by_letter.setdefault(head[-1], set()).add(cid)
        reserved = set('XSZ')          # never assigned to a role - id_spaces.case
        upath = c.rel(c.docs['user_cases'].path)
        for letter, ids in sorted(by_letter.items()):
            if letter in reserved:
                continue
            owners = sorted(set(r.get('id') for r in roles
                                 if any(_glob(g, cid) for g in (r.get('cases') or [])
                                        for cid in ids)))
            if not owners:
                out.append(Finding('12.4', ERROR, upath, 0,
                                    'cases %s-* have no owning role - no roles[].cases '
                                    'glob matches them' % letter))
            elif len(owners) > 1:
                out.append(Finding('12.4', ERROR, upath, 0,
                                    'cases %s-* are claimed by more than one role: %s'
                                    % (letter, ', '.join(owners))))

    # -------- generated/TEST-CASES.md: <case>.T<n> names a live case; covers
    # names a live acceptance bullet. Both legs walk the same entity list, found
    # by ID SHAPE rather than a guessed anchor-kind literal, because the section
    # is currently empty and the shape the first real entry takes is not fixed
    # by anything this rule can read (see _v3_style_field). --------
    tc_path = c.path_of('test_cases')
    if tc_path and os.path.exists(tc_path):
        try:
            tc_text = io.open(tc_path, encoding='utf-8').read()
        except IOError:
            tc_text = None
        if tc_text is not None:
            _header, blocks = mdblocks.parse(tc_text)
            counts = _acceptance_counts(c)
            for e in mdblocks.entities(blocks):
                m = re.match(r'^(C?[A-Z]-[0-9]{2})\.T[0-9]+$', e.id or '')
                if not m:
                    continue
                line = (e.start or 0) + 2
                if m.group(1) not in case_ids:
                    out.append(Finding('12.4', ERROR, c.rel(tc_path), line,
                                        '%s covers case %s, which no longer exists in '
                                        'USER-CASES.md' % (e.id, m.group(1))))
                for token in _as_list(_entity_value(e, 'covers', c.lang)):
                    cm = re.match(r'^(C?[A-Z]-[0-9]{2})\.a([0-9]+)$', str(token))
                    if not cm or int(cm.group(2)) > counts.get(cm.group(1), 0) \
                            or int(cm.group(2)) < 1:
                        out.append(Finding('12.4', ERROR, c.rel(tc_path), line,
                                            '%s: covers %r names no acceptance bullet '
                                            'that exists' % (e.id, token)))

    # -------- history/TASKS.md: blocked_by resolves to a live task or open item --------
    tasks_path = c.path_of('tasks')
    if tasks_path and os.path.exists(tasks_path):
        try:
            tasks_text = io.open(tasks_path, encoding='utf-8').read()
        except IOError:
            tasks_text = None
        if tasks_text is not None:
            _header, blocks = mdblocks.parse(tasks_text)
            task_ids = set(e.id for e in mdblocks.entities(blocks)
                            if re.match(r'^M[0-9]+-T[0-9]+$', e.id or ''))
            item_ids = set(open_items) if open_items is not None else set()
            for e in mdblocks.entities(blocks):
                if e.id not in task_ids:
                    continue
                for token in _as_list(_entity_value(e, 'blocked_by', c.lang)):
                    token = str(token)
                    if token not in task_ids and token not in item_ids:
                        out.append(Finding('12.4', ERROR, c.rel(tasks_path),
                                            (e.start or 0) + 2,
                                            '%s: blocked_by %r resolves to no live task '
                                            'or open item' % (e.id, token)))

    # -------- a case's screens/triggers resolve into UX-UI.md / AUTOMATION.md --------
    # NOTE (measured): no case currently carries either field, so this leg finds
    # nothing on the live corpus today - the link is restored later. Implemented
    # anyway per instructions, and its fire-test is in a scratch copy.
    if 'user_cases' in c.docs:
        screen_ids = _ids_of(c, 'ux_ui', 'screen')
        trigger_ids = _ids_of(c, 'automation', 'trigger')
        decl, items = c.entities_of('user_cases', 'case')
        upath = c.rel(c.docs['user_cases'].path)
        for it in items:
            sline = it.field_lines.get('screens')
            for token in _as_list(it.fields.get('screens')):
                if token not in screen_ids:
                    out.append(Finding('12.4', ERROR, upath,
                                        (sline[0] + 1) if sline else (it.head_line or 0) + 1,
                                        '%s: screens names %r, which is not a screen in '
                                        'UX-UI.md' % (it.id, token)))
            tline = it.field_lines.get('triggers')
            for token in _as_list(it.fields.get('triggers')):
                if token not in trigger_ids:
                    out.append(Finding('12.4', ERROR, upath,
                                        (tline[0] + 1) if tline else (it.head_line or 0) + 1,
                                        '%s: triggers names %r, which is not a trigger in '
                                        'AUTOMATION.md' % (it.id, token)))

    return out


@rule('12.5', "Checked copies - a fact written twice must still say the same thing")
def r_12_5(c):
    out = []

    # -------- lifecycle.{open_questions,needs_from_client}[].summary --------
    doc = c.docs.get('open_questions')
    if doc is not None:
        titles = dict((it.id, it.title) for it in doc.items if it.id)
        norm = lambda s: re.sub(r'\s+', ' ', s or '').strip()
        lc = c.spec.get('lifecycle') or {}
        for field in ('open_questions', 'needs_from_client'):
            for entry in (lc.get(field) or []):
                if not isinstance(entry, dict):
                    continue                       # legacy free-text form - nothing to check
                summary = entry.get('summary')
                if not summary:
                    continue                       # optional; absent everywhere today
                ident = entry.get('id')
                title = titles.get(ident)
                if title is None:
                    continue                       # unresolved id is 12.4's finding
                if norm(summary) != norm(title):
                    out.append(Finding('12.5', ERROR, 'macstack.json', 0,
                                        'lifecycle.%s: %s.summary %r does not match its '
                                        'heading in OPEN-QUESTIONS.md: %r'
                                        % (field, ident, summary, title)))

    # -------- docs.files.<key>.version vs the <!-- macstack:doc= --> header, and
    # vs the version the document shows a human near its own top, when it shows
    # one at all (a handful of documents carry a "**Версия X.Y · ...**" byline
    # left over from before the journal moved to history/; it is exactly the kind
    # of copy this rule exists to keep from rotting silently) --------
    for key, entry in sorted((c.files or {}).items()):
        want = entry.get('version') if isinstance(entry, dict) else None
        if not want:
            continue
        text = c.text.get(key)
        path = c.path_of(key)
        if text is None or path is None:
            continue
        got = v3.header(text).get('version')
        if got and got != want:
            out.append(Finding('12.5', ERROR, c.rel(path), 1,
                                'header says version=%s, docs.files.%s.version says %s'
                                % (got, key, want)))
        for n, line in enumerate(text.splitlines()[:15], 1):
            m = re.match(u'^\\*\\*(?:Версия|Version)\\s+([^\\s*·—]+)', line)
            if m and m.group(1) != want:
                out.append(Finding('12.5', ERROR, c.rel(path), n,
                                    "the document's own byline claims version %s, but "
                                    "docs.files.%s.version says %s - whoever reads the "
                                    "byline is reading the wrong one"
                                    % (m.group(1), key, want)))
                break

    return out


@rule('12.6', "`needs_from_client` is a view - no closed item, no missing open one")
def r_12_6(c):
    out = []
    items = _open_item_ids(c)
    if items is None:
        return out
    a_open = sorted(i for i, (n, closed) in items.items()
                     if i.startswith('A') and not closed)
    view = (c.spec.get('lifecycle') or {}).get('needs_from_client') or []
    view_ids = set()
    for entry in view:
        ident = entry.get('id') if isinstance(entry, dict) else entry
        if ident:
            view_ids.add(ident)
    for ident in sorted(view_ids):
        info = items.get(ident)
        if info is not None and info[1]:
            out.append(Finding('12.6', ERROR, 'macstack.json', 0,
                                'lifecycle.needs_from_client names %s, which '
                                'OPEN-QUESTIONS.md marks closed - the view is stale'
                                % ident))
    for ident in a_open:
        if ident not in view_ids:
            out.append(Finding('12.6', ERROR, 'macstack.json', 0,
                                '%s is an open §A item in OPEN-QUESTIONS.md but '
                                'lifecycle.needs_from_client omits it - the client will '
                                'not be asked' % ident))
    return out


@rule('12.34', 'Pointer uniqueness - no two headings claim the same identity target')
def r_12_34(c):
    out = []
    seen = {}           # resolved target -> [(doc key, item)]
    for key in sorted(c.docs):
        decls = ((c.contract.get('documents') or {}).get(key) or {}).get('entities') or []
        for e in decls:
            decl, items = c.entities_of(key, e['kind'])
            ptr = e.get('pointer') or {}
            for it in items:
                if not it.ref:
                    continue                        # 12.29's finding, not this one
                if _binding_for(ptr, it) != 'identity':
                    continue                         # container may repeat, by design
                seen.setdefault(it.ref, []).append((key, it))
    for target, occ in sorted(seen.items()):
        if len(occ) < 2:
            continue
        first_key, first_it = occ[0]
        first_path = c.rel(c.docs[first_key].path)
        first_line = (first_it.head_line or 0) + 1
        for key, it in occ[1:]:
            out.append(Finding('12.34', ERROR, c.rel(c.docs[key].path),
                                (it.head_line or 0) + 1,
                                'heading %s claims %s, already claimed by %s at %s:%d'
                                % (it.id, target, first_it.id, first_path, first_line)))
    return out
