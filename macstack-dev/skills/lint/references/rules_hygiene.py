# -*- coding: utf-8 -*-
"""Group 12, "content and truth" half: hygiene, staleness, language. 12.7, 12.8,
12.9, 12.10, 12.17, 12.18, 12.25 — the checks that ask not "does this parse" but
"is this still true, and is it still safe to hand to a client."

Everything here reads files under macstack/ or shells out to render.py; nothing
here edits lint_folder.py, another rules_*.py, the contract or the schema.
"""
import datetime, glob, io, json, os, re, subprocess, sys

from lint_folder import rule, Finding, ERROR, WARNING

import lint_folder as _lf                 # only to reach _lf.DOCS, _lf.HERE
import mdblocks                           # v2 parser + the language-ratio regexes
import i18n                               # render.py's own output catalogue
import macstack_freshness                 # 12.17: shared with both hooks


# ---------------------------------------------------------------- shared walk
_MAX_SCAN_BYTES = 8 * 1024 * 1024        # past this it is an asset, not a document


def _walk_files(root, exts=None):
    """Every file under `root`; `exts` narrows it to those extensions.

    Dot-DIRECTORIES are skipped (.git is the tool's storage, not the folder's
    content, and walking it would be both wrong and enormous). Dot-FILES are NOT:
    12.9 says "no secrets anywhere under macstack/", and `.env` is the first place
    anyone looks for one. Excluding it because .DS_Store is litter would have made
    the rule blind to exactly the file it exists for — the extension allowlist this
    replaced already was, and let an AWS key in client/leaked.txt, a token in a
    handoff .html and a password in history/ledger.jsonl through untouched.

    Binaries drop out by themselves: `_read` returns None when the bytes are not
    UTF-8, which is what every PDF in inbox/ does.
    """
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for fn in sorted(filenames):
            if exts is not None and os.path.splitext(fn)[1] not in exts:
                continue
            yield os.path.join(dirpath, fn)


def _read(path):
    """The file as text, or None when it is not text.

    The size cap lives HERE and not in the walk. Putting it in the walk made every
    caller inherit it, and 12.7 — which only needs a file's NAME and its size — then
    stopped seeing the corpus's own 9.5 MB `client-portal-spec-2026-08-24.pdf`
    entirely: no name check, no manifest check, no immutability check, and the intake
    size warning silently green on the one file in the folder that trips it.
    """
    try:
        if os.path.getsize(path) > _MAX_SCAN_BYTES:
            return None
        text = io.open(path, encoding='utf-8').read()
    except (IOError, OSError, UnicodeDecodeError, ValueError):
        return None
    return None if '\x00' in text else text     # decoded, but still not text


# ================================================================== 12.7
# The contract declares the shape itself (`inbox.filename`) rather than leaving it at
# "ASCII-only": a space, a leading underscore or a bracket are all pure ASCII and all
# break the manifest, because mdblocks.ANCHOR reads an intake id as `\S+` and stops at
# the first space. `client spec (2).pdf` therefore CANNOT be given a manifest entry at
# all — checking only for non-ASCII bytes passed it and then blamed the manifest.
_ASCII_FALLBACK = r'^[A-Za-z0-9][A-Za-z0-9._-]*$'


def _inbox_rules(c):
    inb = (c.contract.get('inbox') or {})
    pat = inb.get('filename') or _ASCII_FALLBACK
    try:
        rx = re.compile(pat)
    except re.error:
        rx = re.compile(_ASCII_FALLBACK)
        pat = _ASCII_FALLBACK
    warn_mb = inb.get('size_warn_mb')
    return rx, pat, (warn_mb if isinstance(warn_mb, (int, float)) else None)


@rule('12.7', 'Inbox hygiene')
def r_12_7(c):
    inbox = os.path.join(c.root, 'inbox')
    if not os.path.isdir(inbox):
        return []                         # a fresh folder legitimately lacks intake
    out = []
    rx, pat, warn_mb = _inbox_rules(c)

    # Recursive on purpose. A flat os.listdir made `inbox/round-2/секрет.pdf` invisible
    # to all three legs at once — no name check, no manifest check, no immutability
    # check — and no other rule in the pass looks below the folder's root either.
    files = []
    for p in _walk_files(inbox):
        rel = os.path.relpath(p, inbox)
        if rel == 'README.md':
            continue                      # the manifest itself, and the one writable file
        files.append(rel)
    files.sort()

    for f in files:
        name = os.path.basename(f)
        if not rx.match(name):
            try:
                name.encode('ascii')
                why = 'does not match the contract\'s inbox.filename %s' % pat
            except UnicodeEncodeError:
                # A non-ASCII byte greps as absent the same way a homoglyph id does
                # (12.3's argument, extended to the filesystem).
                why = 'is not ASCII, so it greps as absent'
            out.append(Finding('12.7', ERROR, c.rel(os.path.join(inbox, f)), 0,
                               'inbox filename %r %s' % (name, why)))
        if os.sep in f:
            out.append(Finding('12.7', ERROR, c.rel(os.path.join(inbox, f)), 0,
                               'inbox/ has no sub-folders: %s sits under %r, where the '
                               'manifest cannot name it' % (name, os.path.dirname(f))))

    # ---- every file has a manifest entry. inbox/README.md is v2-format (no
    # `format: v3` in the contract), so it is read with mdblocks, not v3.
    manifest_raw = _read(os.path.join(inbox, 'README.md'))
    if manifest_raw is not None:
        _, blocks = mdblocks.parse(manifest_raw)
        named = {e.id for e in mdblocks.entities(blocks, kind='intake') if e.id}
        for f in files:
            if f not in named and os.path.basename(f) not in named:
                out.append(Finding('12.7', ERROR, c.rel(os.path.join(inbox, f)), 0,
                                   '%s has no entry in inbox/README.md — the manifest '
                                   'is silent about a file that exists' % f))
    elif files:
        out.append(Finding('12.7', ERROR, c.rel(os.path.join(inbox, 'README.md')), 0,
                           'inbox/ holds %d file(s) but README.md does not exist or '
                           'could not be read — nothing says what they are' % len(files)))

    # ---- size. A WARNING by SKILL.md's own warnings list ("an inbox/ file heavier
    # than 5 MB") and by the contract's size_warn_mb; no other rule in the pass owns
    # it, so an unenforced number in the contract is what it stayed until now.
    if warn_mb:
        for f in files:
            p = os.path.join(inbox, f)
            try:
                mb = os.path.getsize(p) / (1024.0 * 1024.0)
            except OSError:
                continue
            if mb > warn_mb:
                out.append(Finding('12.7', WARNING, c.rel(p), 0,
                                   '%.1f MB — over the %g MB intake budget; ask for the '
                                   'source in a lighter form rather than committing this'
                                   % (mb, warn_mb)))

    # ---- content-modifying commits after the add commit. README.md is exempt:
    # it is "the ONLY writable file under inbox/" by the contract's own words, so
    # it is SUPPOSED to gain modifying commits as the manifest grows.
    if files:
        out.extend(_r_12_7_git(c, inbox, files))
    return out


def _r_12_7_git(c, inbox, files):
    try:
        probe = subprocess.run(['git', '-C', c.root, 'rev-parse', '--is-inside-work-tree'],
                               capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return []                         # no git binary — this leg cannot run, skip it
    if probe.returncode != 0 or probe.stdout.strip() != 'true':
        return []                         # not a git repo — legitimate, e.g. a scratch copy
    out = []
    for f in files:
        rel = os.path.join('inbox', f)
        try:
            r = subprocess.run(['git', '-C', c.root, 'log', '--follow',
                                '--diff-filter=M', '--format=%H %ad', '--date=short',
                                '--', rel],
                               capture_output=True, text=True, timeout=20)
        except (OSError, subprocess.SubprocessError):
            continue                      # this one file's history is unreadable; move on
        rows = [ln for ln in r.stdout.splitlines() if ln.strip()]
        if rows:
            out.append(Finding('12.7', ERROR, c.rel(os.path.join(inbox, f)), 0,
                               'modified after it was added (%s) — inbox/ is immutable; '
                               'the edit belongs in README.md\'s manifest, never in the '
                               'file itself' % rows[0]))
    return out


# ================================================================== 12.8
# `[A-Za-z0-9_./-]+\.[a-z]{2,4}:[0-9]+` is the contract's own `line-pointers`
# prohibition (doc-contracts.json). It also matches a URL:port — "api.host.com:3000"
# parses identically to "src/foo.py:42" — so both guards below exist to keep this at
# zero false positives without excluding a real citation like `config.yaml:118`.
LINE_POINTER = re.compile(r'([A-Za-z0-9_./-]+)\.([a-z]{2,4}):([0-9]+)')
_SCHEME_BEFORE = re.compile(r'[A-Za-z][A-Za-z0-9+.-]*:$')
_HOST_LIKE_TLD = frozenset(('com', 'org', 'net', 'io', 'co', 'ai', 'dev', 'app',
                           'gov', 'edu', 'info', 'biz', 'me', 'tv'))
LINK = re.compile(r'\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)')


@rule('12.8', 'No rotting pointers')
def r_12_8(c):
    out = []
    # "anywhere under macstack/" is the rule's own wording, so every readable text
    # file, not an .md/.json allowlist that silently exempted history/ledger.jsonl
    # and the handoff .html twins.
    for path in _walk_files(c.root):
        text = _read(path)
        if text is None:
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for m in LINE_POINTER.finditer(line):
                stem, ext, _num = m.group(1), m.group(2), m.group(3)
                if _SCHEME_BEFORE.search(line[:m.start()]) and line[m.start():].startswith('//'):
                    continue               # scheme://host:port — not a citation
                if ext in _HOST_LIKE_TLD and '/' not in stem:
                    continue               # bare host.tld:port — not a citation
                out.append(Finding('12.8', ERROR, c.rel(path), n,
                                   'a line-number citation that will rot on the next '
                                   'edit: %s — name a symbol or a title instead'
                                   % m.group(0)))
    out.extend(_r_12_8_links(c))
    return out


def _r_12_8_links(c):
    try:
        top = subprocess.run(['git', '-C', c.root, 'rev-parse', '--show-toplevel'],
                             capture_output=True, text=True, timeout=10)
        repo_root = top.stdout.strip() if top.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        repo_root = None
    if not repo_root:
        return []                         # cannot say what "outside the repo" means here
    repo_root = os.path.realpath(repo_root)
    out = []
    for path in _walk_files(c.root, ('.md',)):
        text = _read(path)
        if text is None:
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for m in LINK.finditer(line):
                target = m.group(1)
                if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'):
                    continue               # a scheme (http:, mailto:) or an in-page anchor
                frag = target.split('#', 1)[0]
                if not frag:
                    continue
                base = c.root if frag.startswith('/') else os.path.dirname(path)
                resolved = os.path.realpath(os.path.join(base, frag.lstrip('/')))
                if resolved != repo_root and not resolved.startswith(repo_root + os.sep):
                    out.append(Finding('12.8', ERROR, c.rel(path), n,
                                       'link target resolves outside the repository: %s'
                                       % target))
    return out


# ================================================================== 12.9
# Names of env keys are the spec's business on purpose (they are what a deploy needs
# to set) — only VALUES that look like real credentials are the violation. The named
# patterns (AWS, GitHub, sk-, PEM, user:pass@) are specific enough to stand alone and
# measure zero across every readable file in the live corpus. The two SHAPE patterns
# are not: on their own, `_HEX_RUN` reports every 40-character commit hash in
# history/ as a credential. They are therefore gated behind a key that names a
# secret, because a rule that reddens on an ordinary journal line gets switched off
# and then catches nothing at all.
_AWS_KEY = re.compile(r'\bAKIA[0-9A-Z]{16}\b')
_GH_TOKEN = re.compile(r'\bgh[pousr]_[A-Za-z0-9]{20,}\b')
_SK_KEY = re.compile(r'\bsk-[A-Za-z0-9_-]{20,}\b')
_PEM = re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----')
_URL_CRED = re.compile(r'[a-zA-Z][a-zA-Z0-9+.-]*://[^\s/:@]+:[^\s/:@]+@')
_HEX_RUN = re.compile(r'\b[0-9a-fA-F]{32,}\b')
# base64 candidate: no '/' (a path separator in every false positive measured — see
# the report), and either padded with '=' or mixing case AND a digit, because a
# naturalistic lowercase word run never does both at once.
_B64_RUN = re.compile(
    r'\b[A-Za-z0-9+]{16,}={1,2}(?!\w)'
    r'|\b(?=[A-Za-z0-9+]{32,}\b)(?=[A-Za-z0-9+]*[a-z])(?=[A-Za-z0-9+]*[A-Z])'
    r'(?=[A-Za-z0-9+]*[0-9])[A-Za-z0-9+]{32,}\b')
_ENV_ASSIGN = re.compile(r'^[ \t]*([A-Z][A-Z0-9_]{2,})\s*=\s*(\S.*)$')
_PLACEHOLDER_RHS = re.compile(
    r'^(["\']?)(<.*>|\.\.\.|x{3,}|\*{3,}|-|—|change[_-]?me|your[_-].*|'
    r'replace[_-]?me|todo|tbd|example.*|placeholder.*)\1$', re.I)
# A key that NAMES a credential. The generic shape heuristics below fire only as the
# value of one of these: a bare 40-hex run in prose is a commit hash, which every
# history/ file cites and which is not a secret in any sense — reporting it as one was
# a blocking ERROR on the most ordinary line a journal can contain.
# The prefix is optional on purpose: `api_key: …` is the commonest form there is, and
# requiring one leading character made the pattern match `X_API_KEY` but never `api_key`.
_CRED_KEY = re.compile(
    r'(?i)([A-Za-z0-9_.\-]*'
    r'(?:secret|token|password|passwd|pwd|api[_-]?key|apikey|access[_-]?key|'
    r'private[_-]?key|credential|bearer|signature|salt)'
    r'[A-Za-z0-9_.\-]*)["\']?\s*[:=]\s*["\']?([^\s"\',;]+)')
_BEARER = re.compile(r'(?i)\bbearer\s+([A-Za-z0-9+/=._\-]{16,})')
_LATIN_WORD_ONLY = re.compile(r'^[A-Za-z]+$')
_NUMBER_ONLY = re.compile(r'^[0-9]+([.,][0-9]+)?$')
_URL_VALUE = re.compile(r'^[a-zA-Z][a-zA-Z0-9+.-]*://')


def _env_value_is_credential_shaped(v):
    """A value that could BE a credential, as opposed to prose that happens to sit
    after an equals sign. Four exclusions, each one a measured false positive:

      `FIO = Иванов Иван`   — whitespace, and letters outside the Latin alphabet;
                              this is a Russian sentence, not a shell assignment.
      `MAX_ITEMS = 50`      — a bare number is a count.
      `BASE_URL=https://…`  — a URL with no user:pass in it; _URL_CRED owns the
                              credentialed form and a public endpoint is not a secret.
      `NODE_ENV=production` — one plain dictionary word, no digit and no separator.
                              No credential in the world looks like that, and the rule
                              is titled "no SECRETS", not "no assignments".

    Everything else stays a finding, because the contract's wording is flat: "names of
    env keys only, never values".
    """
    v = v.strip().strip('"\'')
    if not v or re.search(r'\s', v):
        return False
    if _NUMBER_ONLY.match(v) or len(v) < 8:
        return False
    if re.search(r'[^\x00-\x7f]', v):
        return False                      # a non-ASCII value is prose, never a token
    if _URL_VALUE.match(v):
        return False
    if _LATIN_WORD_ONLY.match(v):
        return False
    return bool(re.search(r'[A-Za-z0-9]', v))


def _secret_findings(path, text, rel):
    # The matched VALUE is never put into the message — a finding that quotes the
    # secret it caught just relocates the leak into the lint output (and from there
    # into CI logs, terminal scrollback, this very report). Kind, line and length
    # are enough to act on; the payload is not reproduced.
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        for pat, why in ((_AWS_KEY, 'an AWS access key id'),
                         (_GH_TOKEN, 'a GitHub token'),
                         (_SK_KEY, 'an sk- style API key'),
                         (_PEM, 'a PEM private key block'),
                         (_URL_CRED, 'a URL carrying user:password@')):
            m = pat.search(line)
            if m:
                out.append(Finding('12.9', ERROR, rel, n,
                                   '%s (%d characters) — value withheld from this '
                                   'finding on purpose' % (why, len(m.group(0)))))
        for cand, whose in _credential_values(line):
            for pat, why in ((_HEX_RUN, 'a long hex run'),
                             (_B64_RUN, 'a long base64-shaped run')):
                if pat.search(cand):
                    out.append(Finding('12.9', ERROR, rel, n,
                                       '%s assigned to %s (%d characters) — value '
                                       'withheld from this finding on purpose'
                                       % (why, whose, len(cand))))
                    break
        m = _ENV_ASSIGN.match(line)
        if (m and not _PLACEHOLDER_RHS.match(m.group(2).strip())
                and _env_value_is_credential_shaped(m.group(2))):
            out.append(Finding('12.9', ERROR, rel, n,
                               '%s carries a value (%d characters), and the contract '
                               'allows the NAME of an env key only — value withheld '
                               'from this finding on purpose'
                               % (m.group(1), len(m.group(2).strip()))))
    return out


def _credential_values(line):
    """(value, what named it) for every value on this line a credential key claims."""
    for m in _CRED_KEY.finditer(line):
        yield m.group(2), '`%s`' % m.group(1)
    for m in _BEARER.finditer(line):
        yield m.group(1), 'a Bearer header'


@rule('12.9', 'No secrets anywhere under macstack/')
def r_12_9(c):
    out = []
    # Every readable file, dot-files included. The .md/.json allowlist this replaced
    # left `macstack/.env`, `client/leaked.txt`, `history/ledger.jsonl` and the handoff
    # .html files unopened — a secrets rule that cannot see .env is not a secrets rule.
    for path in _walk_files(c.root):
        text = _read(path)
        if text is None:
            continue
        out.extend(_secret_findings(path, text, c.rel(path)))
    return out


# ================================================================== 12.10
_APPLIED = re.compile(r'<!--\s*macstack:applied\s*-->')
_SUPERSEDED = re.compile(
    r'(?i)supersed|за[м]ен[её]н|устаре[лвш]|ersetzt|застаріл|заміне[нн]')


def _delta_settled(text):
    m = _APPLIED.search(text)
    if m:
        for line in text[m.end():].strip().splitlines()[:5]:
            line = line.strip()
            if not line:
                continue
            return not line.startswith('_TODO')      # the seed/migration placeholder marker
        return False                                  # anchor present, body still empty
    return bool(_SUPERSEDED.search(text))


@rule('12.10', 'No parallel spec')
def r_12_10(c):
    """Two bands, and the contract names both.

    `delta.age_budget_days` is `{warn: 14, error: 30}`, and SKILL.md says the same
    thing in two places: 12.10 sits unmarked in the Pass-3 list (so, an ERROR, like
    every rule there that is not tagged "(warning)"), and its warnings list carries
    "a delta aged 14–30 days with no applied banner" separately. Shipping one band at
    WARNING collapsed the two: a year-old parallel specification never blocked, and
    the warn band never fired at all.
    """
    deltas = os.path.join(c.root, 'history', 'deltas')
    if not os.path.isdir(deltas):
        return []
    budget = ((c.contract.get('documents') or {}).get('delta') or {}).get('age_budget_days') or {}
    warn_at = budget.get('warn') if isinstance(budget.get('warn'), int) else 14
    error_at = budget.get('error') if isinstance(budget.get('error'), int) else 30
    out = []
    today = datetime.date.today()
    for name in sorted(os.listdir(deltas)):
        m = re.match(r'^(\d{4})-(\d{2})-(\d{2})-', name)
        if not name.endswith('.md') or not m:
            continue                      # not this rule's business — 12.3/naming owns that
        try:
            age = (today - datetime.date(int(m.group(1)), int(m.group(2)),
                                         int(m.group(3)))).days
        except ValueError:
            continue
        if age <= warn_at:
            continue
        text = _read(os.path.join(deltas, name))
        if text is None or _delta_settled(text):
            continue
        sev = ERROR if age > error_at else WARNING
        out.append(Finding('12.10', sev, c.rel(os.path.join(deltas, name)), 0,
                           'a %d-day-old delta with neither an applied banner nor a '
                           'superseded note (budget: warn %d, error %d) — it is read as '
                           'a second specification, not a settled proposal'
                           % (age, warn_at, error_at)))
    return out


# ================================================================== 12.17
# Дата последней сверки и срок годности считаются в `hooks/macstack_freshness.py`
# — том же модуле, которым живут оба хука. Здесь была своя копия, и она разошлась:
# копия линтера поднимала часы ещё и по `archive/reviews/`, хуковая — нет, так что
# на проекте, отревьюенном до переезда вердиктов в журнал, правило молчало, а хук
# на старте сессии заявлял «ни разу не сверяли». Расхождение двух копий одного
# порога и должно было всплыть именно так — спором инструментов о свежести.
_latest_conformance_date = macstack_freshness.last_audit


@rule('12.17', 'Documents have a shelf life')
def r_12_17(c):
    if not c.files:
        return []
    out = []
    # Сгенерированный документ не сверяют с кодом: его пересобирают, и это
    # проверяет правило 12.18. Требовать с него дату «когда сверяли» значит
    # требовать проверку, которой для него не существует.

    today = datetime.date.today()
    docs = c.spec.get('docs') or {}
    # A spec that fails pass 1 still reaches pass 3 — the live corpus does exactly that
    # today, with three schema errors standing — so every value read here is treated as
    # untrusted. `freshness_days: "thirty"` and `reviewed: 20260101` (an unquoted date)
    # each killed this rule outright, and a rule that dies reports nothing at all.
    #
    # The budget is per document (`docs.files.<key>.freshness_days`, which is where the
    # schema defines it) and falls back to the folder-wide `docs.freshness_days`, then
    # to 30. Only the folder-wide one used to be read, so the per-document setting the
    # schema documents did nothing at all — the quietest kind of wrong: the file says
    # ninety days, the linter measures thirty, and neither ever mentions the other.
    for where, value in macstack_freshness.bad_budget_values(docs):
        out.append(Finding('12.17', ERROR, 'macstack.json', 0,
                           '%s is not a positive whole number of days: %r — the shelf '
                           'life is measured against %d instead'
                           % (where, value, macstack_freshness.DEFAULT_DAYS)))
    latest_review = _latest_conformance_date(c.root)
    for key in sorted(c.files):

        if ((c.contract.get('documents') or {}).get(key) or {}).get('generated'):
            continue
        meta = c.files.get(key)
        if not isinstance(meta, dict):
            out.append(Finding('12.17', ERROR, 'macstack.json', 0,
                               'docs.files.%s is not an object (%s) — nothing can carry '
                               'a `reviewed` date' % (key, type(meta).__name__)))
            continue
        path = c.path_of(key)
        rel = c.rel(path) if path else 'macstack.json'
        reviewed = meta.get('reviewed')
        if not reviewed:
            out.append(Finding('12.17', ERROR, rel, 0,
                               'docs.files.%s carries no `reviewed` date — nobody has '
                               'ever recorded checking it against the code, which is '
                               'worse than being stale' % key))
            continue
        try:
            d = datetime.date(*(int(x) for x in str(reviewed).split('-')))
        except (ValueError, TypeError, AttributeError):
            out.append(Finding('12.17', ERROR, rel, 0,
                               'docs.files.%s.reviewed is not a YYYY-MM-DD date: %r'
                               % (key, reviewed)))
            continue
        if latest_review and latest_review > d:
            d = latest_review
        age = (today - d).days
        fresh_days = macstack_freshness.budget(docs, meta)
        if age <= fresh_days:
            continue
        sev = ERROR if age > fresh_days * 2 else WARNING
        out.append(Finding('12.17', sev, rel, 0,
                           '%s was last checked against the code %d days ago '
                           '(budget %d) — reviewed=%s' % (key, age, fresh_days,
                                                          d.isoformat())))
    return out


# ================================================================== 12.18
def _render_jobs():
    """Работы рендера читаются ИЗ render.py, а не перечисляются здесь.

    Список жил копией в этом правиле и разошёлся с оригиналом ровно тогда, когда
    появились REQUIREMENTS.md и TEST-CASES.md: генераторы есть, а правило
    докладывало, что их нет. Ровно тот же класс, что и README.md, из-за которого
    12.18 три релиза было невыполнимо.
    """
    try:
        src = io.open(os.path.join(_lf.DOCS, 'render.py'), encoding='utf-8').read()
    except IOError:
        return set()
    return set(re.findall(r"only in \(None, '([a-z_]+)'\)", src))


@rule('12.18', "A generated document equals its source")
def r_12_18(c):
    docs = c.contract.get('documents') or {}
    gen_keys = sorted(k for k, d in docs.items() if d.get('generated'))
    if not gen_keys:
        return []
    out = []
    uncovered = [k for k in gen_keys if k not in _render_jobs()]
    for k in uncovered:
        # This is exactly the historical README.md failure: a contract entry says
        # `generated` and no generator exists for it, so the rule was unsatisfiable
        # and silently reported nothing for three releases. The gap itself is the
        # finding now, not a green rule that never actually looked.
        out.append(Finding('12.18', ERROR, docs[k].get('path') or k, 0,
                           'the contract marks `%s` generated but render.py has no '
                           '--only job for it — this rule cannot verify it' % k))
    checked = [k for k in gen_keys if k in _render_jobs()]
    if not checked:
        return out
    render_py = os.path.join(_lf.DOCS, 'render.py')
    if not os.path.exists(render_py):
        out.append(Finding('12.18', ERROR, 'render.py', 0,
                           'the renderer is missing at %s — cannot verify %s'
                           % (render_py, ', '.join(checked))))
        return out
    try:
        proc = subprocess.run([sys.executable, render_py, c.root, '--check'],
                              capture_output=True, text=True, timeout=90)
    except (OSError, subprocess.SubprocessError) as e:
        out.append(Finding('12.18', ERROR, 'render.py', 0,
                           'could not run the renderer: %s: %s' % (type(e).__name__, e)))
        return out
    lines = set((proc.stdout or '').splitlines())
    # render.py picks its output language with i18n.doc_lang, NOT with the raw
    # docs.language string: it lowercases, drops a BCP-47 region and falls back to 'en'
    # for anything unsupported. Reading its verdict through `c.lang` (raw, defaulting to
    # 'ru') therefore matched nothing whenever the two disagreed — `"language": "ru-RU"`,
    # which the schema explicitly invites, produced three "cannot confirm it is in sync"
    # ERRORs against files render.py had just called byte-identical to their source.
    out_lang = i18n.doc_lang(c.root)
    for k in checked:
        path = os.path.join(c.root, (c.contract.get('documents') or {}).get(k, {}).get('path', k))
        drift = i18n.msg(out_lang, 'drift', path=path)
        insync = i18n.msg(out_lang, 'in_sync', path=path)
        if drift in lines:
            if not os.path.exists(path):
                # A first run has no generated/ yet, and render.py calls a missing file
                # a difference. Saying "either it was hand-edited or the source moved"
                # about a file nobody has ever rendered sends the reader looking for an
                # edit that does not exist.
                out.append(Finding('12.18', ERROR, c.rel(path), 0,
                                   '%s has never been rendered from `%s` — run render.py '
                                   'rather than writing it' % ((c.contract.get('documents') or {}).get(k, {}).get('path', k),
                                                               docs[k].get('generated'))))
            else:
                out.append(Finding('12.18', ERROR, c.rel(path), 0,
                                   '%s no longer matches a fresh render of `%s` — either '
                                   'it was hand-edited or the source moved and nobody '
                                   're-rendered; re-render it, never hand-fix it'
                                   % ((c.contract.get('documents') or {}).get(k, {}).get('path', k), docs[k].get('generated'))))
        elif insync not in lines:
            out.append(Finding('12.18', ERROR, c.rel(path), 0,
                               'render.py --check gave no verdict for %s — cannot '
                               'confirm it is in sync (stderr: %s)'
                               % ((c.contract.get('documents') or {}).get(k, {}).get('path', k), (proc.stderr or '').strip()[:200])))
    return out


# ================================================================== 12.25
# mdblocks.CYR / LAT / IDTOK are reused as-is — simple character classes and token
# patterns, no pairing risk. mdblocks.STRIP is NOT reused: it is compiled with
# re.S and applied to the WHOLE document in one `sub`, so its single-backtick
# alternative `` `[^`]*` `` pairs across line breaks exactly the way strip_fences'
# own docstring warns triple-backtick pairing does. Measured on the live corpus:
# history/TASKS.md carries one stray unmatched backtick (153 in the file, an odd
# count), and mdblocks.STRIP's cross-line pairing then swallows several headings
# and a table as one giant "code span" — mostly Cyrillic, so the ratio it leaves
# behind reads as 27% foreign. A per-line stripper on the same file (never letting
# a backtick pair reach past its own line, since a code span in this format is
# never written to span one) gives 5.3%. render.py never calls foreign_ratio, but
# migrate.py does, so this is not a hypothetical — it is a live bug upstream in
# mdblocks.py, out of scope here to fix (not this module), and worked around
# locally by never crossing a newline while stripping.
_INLINE_CODE = re.compile(r'`[^`\n]*`')
_ANCHOR_LINE = re.compile(r'<!--[^\n]*-->')
_MD_LINK_LINE = re.compile(r'\[[^\]\n]*\]\([^)\n]*\)')
_MIN_LETTERS = 200          # mdblocks.foreign_ratio's own floor: too short to mean anything
_MIN_LINE_LETTERS = 8       # a worst LINE below this is one stray word, not a finding


def _strip_for_language(text):
    """The same exclusions mdblocks.STRIP names — code spans, anchors, links —
    applied per line so a stray or odd-numbered backtick can never pair across a
    line break and eat unrelated prose."""
    body = mdblocks.strip_fences(text)
    out = []
    for line in body.splitlines():
        line = _ANCHOR_LINE.sub(' ', line)
        line = _MD_LINK_LINE.sub(' ', line)
        line = _INLINE_CODE.sub(' ', line)
        out.append(line)
    return '\n'.join(out)


# Which script a language is written in. The rule is a two-way split — one alphabet is
# the document's, the other is foreign — so it needs the language NORMALISED first.
# `docs.language` is a BCP-47 code by the schema's own description, and comparing it
# raw against the literals 'ru'/'uk' inverted the whole measurement for "RU" and
# "ru-RU": every correctly-Russian document in the corpus was reported at 97–99%
# foreign, ten blocking ERRORs on a folder with nothing wrong with it.
_CYRILLIC_LANGS = frozenset(('ru', 'uk', 'be', 'bg', 'sr', 'mk', 'kk', 'ky', 'mn', 'tg'))


def _norm_lang(lang):
    """i18n.doc_lang's own normalisation, applied to a code from anywhere."""
    if not lang:
        return None
    return str(lang).strip().split('-')[0].split('_')[0].lower() or None


def _foreign_ratio(text, lang):
    body = mdblocks.IDTOK.sub(' ', _strip_for_language(text))
    cyr, lat = len(mdblocks.CYR.findall(body)), len(mdblocks.LAT.findall(body))
    total = cyr + lat
    if total < _MIN_LETTERS:
        return None
    wrong = lat if lang in _CYRILLIC_LANGS else cyr
    return wrong / float(total)


def _worst_line(text, lang):
    stripped_lines = _strip_for_language(text).splitlines()
    raw_lines = text.splitlines()
    best_n, best_ratio = 0, -1.0
    for n, sline in enumerate(stripped_lines, 1):
        body = mdblocks.IDTOK.sub(' ', sline)
        cyr, lat = len(mdblocks.CYR.findall(body)), len(mdblocks.LAT.findall(body))
        total = cyr + lat
        if total < _MIN_LINE_LETTERS:
            continue
        ratio = (lat if lang in _CYRILLIC_LANGS else cyr) / float(total)
        if ratio > best_ratio:
            best_ratio, best_n = ratio, n
    if best_n and best_n <= len(raw_lines):
        return best_n, raw_lines[best_n - 1].strip()[:80]
    return 0, ''


def _lang_for(c, key, decl, text):
    meta = c.files.get(key)
    override = _norm_lang(meta.get('language')) if isinstance(meta, dict) else None
    if override:
        return override
    if not decl.get('format') == 'v3':
        # A dated instance (delta/rulings/review) has no docs.files entry of its own;
        # its v2 header can carry its own `lang=`, and a document that says so
        # honestly should not be measured against a default it never claimed.
        header, _ = mdblocks.parse(text)
        if _norm_lang(header.get('lang')):
            return _norm_lang(header['lang'])
    # The project default, read raw and normalised here rather than taken from
    # c.lang: the schema says "Absent = en" and every other tool in the plugin
    # resolves it through i18n.doc_lang, while Ctx.lang falls back to 'ru'. Guessing
    # Russian for a folder that never said so measures an English document against
    # the wrong alphabet and reports it at ~99% foreign.
    declared = _norm_lang((c.spec.get('docs') or {}).get('language'))
    return declared or i18n.doc_lang(c.root)


@rule('12.25', 'The document is written in its declared language')
def r_12_25(c):
    out = []
    docs = c.contract.get('documents') or {}
    seen_paths = set()
    for key, decl in sorted(docs.items()):
        if decl.get('generated'):
            continue                      # the standard that forbids translating ids
        p = decl.get('path') or ''
        if not p or '<' in p:
            continue                      # a dated-instance pattern, walked separately below
        text = c.text.get(key)
        path = c.path_of(key)
        if text is None:
            if not path or not os.path.exists(path):
                continue
            text = _read(path)
            if text is None:
                continue
        seen_paths.add(os.path.realpath(path))
        out.extend(_r_12_25_one(c, key, decl, path, text))

    # dated instances: real files behind a `<placeholder>` path in the contract.
    # None of the three (delta, rulings, review) is `generated`, so all are in scope.
    for subdir, key in (('deltas', 'delta'), (os.path.join('decisions'), 'rulings'),
                        ('reviews', 'review')):
        decl = docs.get(key) or {}
        for path in sorted(glob.glob(os.path.join(c.root, 'history', subdir, '*.md'))):
            if os.path.realpath(path) in seen_paths:
                continue
            text = _read(path)
            if text is None:
                continue
            out.extend(_r_12_25_one(c, key, decl, path, text))
    return out


def _r_12_25_one(c, key, decl, path, text):
    lang = _lang_for(c, key, decl, text)
    ratio = _foreign_ratio(text, lang)
    if ratio is None or ratio <= 0.15:
        return []
    n, snippet = _worst_line(text, lang)
    sev = ERROR if decl.get('audience') in ('client', 'both') else WARNING
    return [Finding('12.25', sev, c.rel(path), n,
                    '%.0f%% of its letters are outside the %s alphabet (budget 15%%) — '
                    'worst line: %s' % (ratio * 100, lang, snippet or '(no single line '
                    'carries enough letters to blame)'))]

@rule('12.36', 'A document that moved has a ledger row saying what moved')
def r_12_36(c):
    """Правка без строки в журнале — дефект, и это не бюрократия.

    Клиентский пакет показывает КАЖДОЕ утверждение с его собственной историей:
    что было, что стало, почему. Строка, называющая только файл, к утверждению не
    цепляется, а значит клиент увидит документ без следа изменения — ровно то,
    ради чего журнал и заводился.

    Проверка дешёвая и не требует git: версия в шапке документа против самой
    свежей строки журнала, которая этот документ называет. Версию поднимают, когда
    документ меняют; если журнал об этой версии не знает, правка прошла мимо него.
    """
    led = _ledger_rows(c)
    if led is None:
        return []                     # журнала ещё нет — это ловит 12.13, не мы
    seen = {}
    for r in led:
        d = str(r.get('doc') or '')
        if d:
            seen[d] = max(seen.get(d, ''), str(r.get('date') or ''))
    out = []
    # Только авторские. Сгенерированный документ переписывает его генератор, и за
    # его свежесть отвечает 12.18; требовать от рендера строку в журнале о самом
    # себе — значит завести шум, в котором утонет правка, сделанная человеком.
    for key in sorted(k for k in c.client_keys() if not c.is_generated(k)):
        doc = c.docs[key]
        rel = c.rel(doc.path)
        ver = (doc.header or {}).get('version')
        if not ver:
            continue
        rows = [r for r in led if str(r.get('doc') or '') == rel]
        if not rows:
            out.append(Finding('12.36', ERROR, rel, 1,
                               'документ версии %s, а в history/ledger.jsonl о нём '
                               'нет ни одной строки — значит правки не записаны'
                               % ver))
    return out


def _ledger_rows(c):
    p = os.path.join(c.root, 'history', 'ledger.jsonl')
    if not os.path.exists(p):
        return None
    rows = []
    for n, line in enumerate(io.open(p, encoding='utf-8')):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except ValueError:
            # Битая строка — это не «журнала нет». Молчаливый пропуск здесь
            # означал бы, что правило проходит тем увереннее, чем хуже журнал.
            c.errors.append('history/ledger.jsonl:%d не разбирается' % (n + 1))
    return rows


@rule('12.38', 'client/ holds documents, and nothing else')
def r_12_38(c):
    """Файл, который не является одним из шести документов, — входящий материал.

    Клиент пришлёт правки как умеет: положит .docx рядом с документами, скинет
    скриншот, сохранит свой вариант под другим именем. Оставить это в `client/`
    значит завести седьмой документ, которого не знает ни рендер, ни пакет, ни
    спека, — и через месяц никто не скажет, он источник правды или чей-то черновик.

    Место такому файлу — `inbox/`, где он неизменяем и имеет строку в манифесте.
    """
    want = set()
    for key, decl in (c.contract.get('documents') or {}).items():
        rel = (c.files.get(key) or {}).get('path') or decl.get('path') or ''
        if rel.startswith('client/'):
            want.add(os.path.basename(rel))
    d = os.path.join(c.root, 'client')
    if not os.path.isdir(d) or not want:
        return []
    out = []
    for name in sorted(os.listdir(d)):
        if name.startswith('.') or name in want:
            continue
        out.append(Finding('12.38', ERROR, 'client/' + name, 0,
                           'не один из документов — входящий материал: перенесите '
                           'в inbox/ и разберите через /macstack-dev:intake'))
    return out


@rule('12.39', 'Every workflow source path still exists')
def r_12_39(c):
    """`workflows[].source` говорит, где workflow живёт в коде. Файл переименуют
    или удалят — поле останется, и следующий аудит отчитается зелёным по пути,
    которого нет.

    Поле появилось потому, что имена две стороны не связывают: на живом проекте
    код зовёт workflow по предметной области, спека — по шагу, и сходятся 3 из
    17. Связь, которую нельзя вывести, приходится хранить; хранимую связь надо
    проверять, иначе она хуже отсутствующей — ей верят.

    Пустое `source` здесь не ошибка: workflow может быть ещё не написан. Ошибка
    — заполненное и неверное.
    """
    root = os.path.normpath(os.path.join(c.root, '..'))
    out = []
    for w in (c.spec.get('workflows') or []):
        src = w.get('source')
        if not src:
            continue
        if not os.path.exists(os.path.join(root, src)):
            out.append(Finding('12.39', ERROR, 'macstack.json', 0,
                               '%s: source указывает на %s — файла нет'
                               % (w.get('id'), src)))
    return out


# Команды, без которых папка перестаёт обновляться. Не весь список из семи: правило
# требует того, что держит документы в согласии с кодом, а не полноты перечисления.
_KEEPERS = ('/macstack-dev:update', '/macstack-dev:intake')


@rule('12.40', 'The project tells its agents when to update the folder')
def r_12_40(c):
    """`CLAUDE.md` и `AGENTS.md` должны называть команды, которыми папку
    поддерживают, а не только путь к ней.

    Блок, который говорит «читай macstack.json первым» и молчит о том, что делать
    после работы, даёт агента, который по папке сверяется и оставляет её стареть.
    Указание «поддерживай документы в актуальном состоянии» без названного повода
    и команды — пожелание, а не инструкция.

    Требуются два имени, а не таблица целиком: формулировку перепишут, и правило,
    придирающееся к словам, будут обходить. `update` и `intake` — то, без чего
    папка перестаёт обновляться вообще; остальные команды её не ведут.

    Оба файла, а не один: документы читает тот агент, которого запустила команда,
    и спецификация, которую находит только Claude Code, — это спецификация,
    которой половина команды пользоваться не может.
    """
    root = os.path.normpath(os.path.join(c.root, '..'))
    out = []
    for name in ('CLAUDE.md', 'AGENTS.md'):
        p = os.path.join(root, name)
        if not os.path.exists(p):
            out.append(Finding('12.40', ERROR, '../' + name, 0,
                               'файла нет — агент, работающий в этом проекте, не '
                               'узнает ни про macstack/, ни про то, когда её '
                               'обновлять. Заводит /macstack-dev:start'))
            continue
        try:
            body = io.open(p, encoding='utf-8').read()
        except IOError as e:
            out.append(Finding('12.40', ERROR, '../' + name, 0,
                               'не читается: %s' % e))
            continue
        missing = [k for k in _KEEPERS if k not in body]
        if missing:
            out.append(Finding('12.40', ERROR, '../' + name, 0,
                               'не называет %s — сказано, ГДЕ лежит спецификация, '
                               'и не сказано, КОГДА её обновлять'
                               % ' и '.join(missing)))
    return out
