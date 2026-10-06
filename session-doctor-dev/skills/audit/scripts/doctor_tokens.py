"""API tokens the session used, and what the session itself shows about each: accepted or not.

Read-only and offline. A token's status is derived from the HTTP codes already in the transcript —
the status the same curl/wget command printed. Nothing is replayed, no socket is opened.

Tokens come from Bash curl/wget commands only: an Authorization / x-api-key / X-...-Token / Cookie
header, `-u user:pass`, URL userinfo, a secret-named query parameter, a Telegram `/bot<id>:<token>/`
path. WebFetch, WebSearch and MCP calls carry no literal token, so they never make a row.

SECRET SAFETY: a value is never stored in the report. Every value found — literal or resolved from a
$VAR — is handed to remember_secrets(), so the final scrub() of the whole output (including the raw
tool input that --json dumps) erases it. The report keeps only a kind label, the variable name, and an
8-hex sha256 fingerprint. A $VAR that cannot be resolved stays a row with its name and no fingerprint.
No .env file is ever opened. Missing keys never raise.
"""
import difflib
import hashlib
import json
import re
import shlex

from doctor_common import (CURL_USER, FLAG, QUERY, TOKEN_VALUE, USERINFO, check, collector, details,
                           finding, remember_secrets, section, short, walk_strings)
from doctor_events import events as session_events
from doctor_http import (ASSIGN, _command_tokens, _parse_wget, _split_commands, _split_heredocs, _tokens,
                         parse_curl, requests_from_event, split_url)
from doctor_sources import settings_env

MIN_LEN = 8            # same floor remember_secrets() uses; a shorter literal is not a credential
MAX_ROWS = 100
MAX_SWEEP = 500        # distinct values scrubbed without a row (tool input is dumped raw by --json)
HEADER_NAME = re.compile(r"(?i)(token|key|secret|auth)")
SCHEME_WORD = re.compile(r"(?i)^(bearer|basic|token)\s+")
# A candidate is a variable ONLY when it is exactly $NAME or ${NAME} (doctor_common.PLACEHOLDER, plus
# digits in the name). Anything else — even with a `$` inside — is a literal credential.
PURE_REF = re.compile(r"^\$(?:\{([A-Za-z_][A-Za-z0-9_]*)\}|([A-Za-z_][A-Za-z0-9_]*))$")
ANSI_C = re.compile(r"\$'((?:[^'\\]|\\.)*)'")
MAX_FRAGMENT_SCAN = 5000
USERINFO_PASS = re.compile(r"(?i)^[a-z][a-z0-9+.\-]*://[^\s/:@]*:([^\s@/]+)@")
TELEGRAM = re.compile(r"/bot(\d{5,}:[A-Za-z0-9_\-]{30,})")
GITHUB_SHAPE = re.compile(r"^(?:gh[pousr]_|github_pat_)")
WGET_PASSWORD = ("--password", "--http-password", "--ftp-password", "--proxy-password")
RANK = {"❌": 0, "⚠": 1, "✅": 2}


# ── candidates ───────────────────────────────────────────────────────────────

def _cand(kind_hint, raw, scheme=""):
    raw = (raw or "").strip().strip("'\"")
    return {"hint": kind_hint, "raw": raw, "scheme": scheme} if raw else None


def _header_candidate(name, value):
    name, value = (name or "").strip().lower(), (value or "").strip()
    if not value:
        return None
    if name == "cookie":
        return _cand("cookie", value)
    if name == "authorization":
        found = SCHEME_WORD.match(value)
        return _cand("auth", value[found.end():] if found else value, found.group(1).lower() if found else "")
    if HEADER_NAME.search(name):
        return _cand("header", value)
    return None


def _url_candidates(url):
    out = []
    url = str(url or "")
    found = USERINFO_PASS.match(url)
    if found:
        out.append(_cand("userinfo", found.group(1)))
    out += [_cand("query", m.group(2)) for m in QUERY.finditer(url)]
    out += [_cand("telegram", m.group(1)) for m in TELEGRAM.finditer(url)]
    return out


def _curl_candidates(parsed):
    out = [_header_candidate(n, v) for n, v in (parsed.get("headers") or {}).items()]
    user = parsed.get("user")
    if isinstance(user, str) and ":" in user:
        out.append(_cand("user", user.partition(":")[2]))
    return out + _url_candidates(parsed.get("url"))


def _wget_candidates(ctoks, url):
    out, i = [], 1
    while i < len(ctoks):
        tok = ctoks[i]
        i += 1
        name, eq, val = tok.partition("=")
        takes_value = name == "--header" or name in WGET_PASSWORD
        if takes_value and not eq and i < len(ctoks):
            val, i = ctoks[i], i + 1
        if name == "--header":
            head, sep, body = val.partition(":")
            out.append(_header_candidate(head, body) if sep else None)
        elif name in WGET_PASSWORD:
            out.append(_cand("user", val))
    return out + _url_candidates(url)


# ── resolving $VAR ───────────────────────────────────────────────────────────

def _resolve(raw, lookup):
    """-> (value, var). A pure $NAME / ${NAME} reference: (value or None if unresolved, NAME).
    Anything else is a literal credential: (raw, None) — `var` never holds any part of a value."""
    ref = PURE_REF.match(raw)
    if not ref:
        return raw, None
    name = ref.group(1) or ref.group(2)
    return lookup(name), name


def _lookup_factory(ctx):
    env_settings = settings_env(getattr(ctx, "layers", None) or [])
    launch = getattr(ctx, "launch_env", None) or {}
    own = getattr(ctx, "env", None) or {}

    def make(inline):
        def lookup(name):
            if name in inline:
                return inline[name]
            if name in env_settings:
                return env_settings[name][0]
            if name in launch:
                return launch[name]
            return own.get(name)
        return lookup
    return make


def _kind(hint, scheme, value):
    if hint in ("cookie", "query", "telegram"):
        return hint
    if hint in ("userinfo", "user"):
        return "basic-auth"
    if value:
        if value.startswith("eyJ") and value.count(".") == 2:
            return "bearer-jwt"
        if GITHUB_SHAPE.match(value):
            return "github"
    if hint == "auth":
        return {"bearer": "bearer", "basic": "basic"}.get(scheme, "token")
    return "x-api-key"


def _fingerprint(value):
    return hashlib.sha256(value.encode("utf-8", "replace")).hexdigest()[:8]


# ── scrub bookkeeping ────────────────────────────────────────────────────────

def _forms(value):
    forms = {value}
    escaped = json.dumps(value, ensure_ascii=False)[1:-1]     # as --json would print it
    forms.add(escaped)
    return forms


class _Secrets(object):
    """Collects every value to erase from the output; flushed once into remember_secrets()."""

    def __init__(self):
        self.values = []
        self.seen = set()

    def add(self, value):
        if not isinstance(value, str) or len(value) < MIN_LEN or PURE_REF.match(value):
            return
        for form in _forms(value):
            if form not in self.seen:
                self.seen.add(form)
                self.values.append(form)

    def flush(self):
        # a key that always looks like a secret name, so remember_secrets() keeps the value
        remember_secrets({"TOKEN_%d" % i: v for i, v in enumerate(self.values)})

    def add_fragments(self, segment, value):
        """Every literal piece of the command that spelled this credential. shlex joins quote runs
        ('part1'"part2"), so the value is not a substring of the raw command and scrub() would miss
        it; add each common block of segment and value (>= MIN_LEN) and each $'...' run."""
        if not isinstance(value, str) or not value:
            return
        for match in ANSI_C.finditer(segment[:MAX_FRAGMENT_SCAN]):
            inner = match.group(1)
            self.add(inner)
            if ":" in inner:
                self.add(inner.partition(":")[2].strip())
        matcher = difflib.SequenceMatcher(None, segment[:MAX_FRAGMENT_SCAN], value[:2000], autojunk=False)
        for block in matcher.get_matching_blocks():
            if block.size >= MIN_LEN:
                self.add(value[block.b:block.b + block.size])


SWEEP = [(rx, 2) for rx in (QUERY, USERINFO, FLAG, CURL_USER)] + \
        [(rx, 0) for rx in TOKEN_VALUE if not rx.pattern.startswith(r"\b[A-Fa-f0-9]")]


def _sweep(event, secrets):
    """Scrub-only: token-shaped values anywhere in a tool call's input (WebFetch url, python -c, env
    dumps...) — these never become a row, but --json prints the raw input, so they must not survive."""
    inp = event.get("input")
    if not isinstance(inp, dict):
        return
    for _, text in walk_strings(inp):
        text = text[:20000]
        for rx, group in SWEEP:
            if len(secrets.seen) > MAX_SWEEP:
                return
            for match in rx.finditer(text):
                secrets.add(match.group(group).strip("'\""))


# ── extraction ───────────────────────────────────────────────────────────────

def _leading_assignments(toks):
    assigns, i = {}, 0
    while i < len(toks):
        tok = toks[i]
        if tok == "export":
            i += 1
        elif ASSIGN.match(tok):
            name, _, val = tok.partition("=")
            assigns[name] = val
            i += 1
        else:
            break
    return assigns, toks[i:]


def _segment_requests(segment):
    """-> (source, method, url, candidates) for a curl/wget segment, else None."""
    ctoks = _command_tokens(segment)
    if not ctoks:
        return None
    if ctoks[0] == "curl":
        parsed = parse_curl(" ".join(shlex.quote(t) for t in ctoks))
        if parsed:
            return "curl", parsed["method"], parsed["url"], _curl_candidates(parsed)
    elif ctoks[0] == "wget":
        parsed = _parse_wget(ctoks)
        if parsed:
            return "wget", parsed["method"], parsed["url"], _wget_candidates(ctoks, parsed["url"])
    return None


def _bash_tokens(event, make_lookup, secrets):
    """One Bash event -> [(token, hosts, codes)] where token = {kind, var, value|None}."""
    command = (event.get("input") or {}).get("command")
    if not isinstance(command, str) or not command.strip():
        return []
    reqs = requests_from_event(event)
    used, found, inline = set(), [], {}
    for segment in _split_commands(_split_heredocs(command)[0]):
        assigns, rest = _leading_assignments(_tokens(segment))
        if not rest:                    # `export X=...` / `X=...` on its own line: stays set
            inline.update(assigns)
            continue
        local = dict(inline)
        local.update(assigns)           # `X=... curl ...`: only for this command
        got = _segment_requests(segment)
        if not got:
            continue
        source, method, url, cands = got
        host, path = split_url(url)
        codes, matched = [], False
        for idx, req in enumerate(reqs):
            if idx not in used and (req["source"], req["method"], req["host"], req["path"]) == (
                    source, method, host, path):
                used.add(idx)
                codes.append(req["code"])
                matched = True
                break
        lookup = make_lookup(local)
        per_segment = {}
        for cand in cands:
            if not cand:
                continue
            value, var = _resolve(cand["raw"], lookup)
            if value is not None:
                secrets.add(value)                    # as resolved, before any scheme is stripped
                if cand["hint"] == "auth":
                    value = SCHEME_WORD.sub("", value)
                if not value or (var is None and len(value) < MIN_LEN):
                    continue
                secrets.add(value)
                secrets.add(cand["raw"])
                secrets.add_fragments(segment, cand["raw"])    # quote-concatenated / unquoted pieces
                secrets.add_fragments(segment, value)
                token = {"kind": _kind(cand["hint"], cand["scheme"], value), "var": var, "value": value}
                key = ("f", _fingerprint(value))
            else:
                token = {"kind": _kind(cand["hint"], cand["scheme"], None), "var": var, "value": None}
                key = ("v", var)
            per_segment.setdefault(key, token)
        for key, token in per_segment.items():
            found.append((key, token, host, codes, matched))
    return found


# ── verdict ──────────────────────────────────────────────────────────────────

def _is_2xx(code):
    return code.isdigit() and (200 <= int(code) < 300 or code == "304")


def _is_down(code):
    return (code.isdigit() and int(code) >= 500) or code.startswith("curl:") or code in ("err", "error")


def verdict(codes, matched, resolved):
    decided = [c for c in (codes or {}) if c != "?"]
    if "401" in decided:
        return "❌ rejected"
    if "403" in decided:
        return "⚠️ no access"
    if decided and all(_is_2xx(c) for c in decided):
        return "✅ accepted"
    if decided and all(_is_down(c) for c in decided):
        return "⚠️ service was down"
    if decided or (matched and resolved):
        return "— no code for this token"
    return "— not checkable from the session"


# ── collector ────────────────────────────────────────────────────────────────

@collector("tokens")
def collect_tokens(ctx):
    events = (session_events(ctx) or {}).get("events") or []
    make_lookup = _lookup_factory(ctx)
    secrets, rows, order = _Secrets(), {}, []
    try:
        for event in events:
            if not isinstance(event, dict) or event.get("kind") != "tool":
                continue
            try:
                _sweep(event, secrets)
                if event.get("name") != "Bash":      # WebFetch / WebSearch / MCP: no literal token, no row
                    continue
                for key, token, host, codes, matched in _bash_tokens(event, make_lookup, secrets):
                    row = rows.get(key)
                    if row is None:
                        value = token["value"]
                        row = rows[key] = {"kind": token["kind"], "var": token["var"],
                                           "fp": (_fingerprint(value) if value is not None and len(value) >= MIN_LEN
                                                  else None),     # a short value's fingerprint is brute-forceable
                                           "hosts": [], "codes": {}, "_matched": False,
                                           "_resolved": value is not None}
                        order.append(key)
                    row["var"] = row["var"] or token["var"]
                    if host and host not in row["hosts"]:
                        row["hosts"].append(host)
                    for code in codes:
                        row["codes"][code] = row["codes"].get(code, 0) + 1
                    row["_matched"] = row["_matched"] or matched
            except Exception:                          # an odd event is a missing row, never a crash
                continue
    finally:
        secrets.flush()
    out = []
    for key in order:
        row = rows[key]
        row["hosts"] = row["hosts"][:5]
        row["verdict"] = verdict(row["codes"], row.pop("_matched"), row.pop("_resolved"))
        out.append(row)
    out.sort(key=lambda r: RANK.get(r["verdict"][:1], 3))      # stable: ❌ ⚠ ✅ then the rest
    return {"tokens": out[:MAX_ROWS]}


# ── checks ───────────────────────────────────────────────────────────────────

def _codes(codes):
    items = sorted((codes or {}).items(), key=lambda kv: (-kv[1], kv[0]))
    return " ".join("%s×%d" % (k, v) for k, v in items[:5])


def _who(token):
    parts = [token.get("kind") or "?"]
    if token.get("var"):
        parts.append("$" + token["var"])
    if token.get("fp"):
        parts.append("fp " + token["fp"])
    return " ".join(parts)


def _rows(report):
    return (report.get("tokens") or {}).get("tokens") or []


@check
def token_rejected(report):
    bad = [t for t in _rows(report)
           if "401" in (t.get("codes") or {})
           or ("403" in (t.get("codes") or {}) and not any(_is_2xx(c) for c in t["codes"]))]
    if not bad:
        return []
    evidence = "; ".join("%s -> %s @ %s" % (_who(t), _codes(t.get("codes")), ",".join(t.get("hosts") or ["?"]))
                         for t in bad[:5])
    return [finding("high", "TOKEN_REJECTED", "%d API token(s) refused by the server in this session" % len(bad),
                    short(evidence, 400),
                    "Renew or replace the token and update where it is stored (settings env, .env, vault). "
                    "401 = the server did not accept it; 403 = accepted but not allowed.")]


@check
def token_unverified(report):
    open_ = [t for t in _rows(report) if str(t.get("verdict") or "").startswith("—")]
    if not open_:
        return []
    evidence = "; ".join("%s @ %s" % (_who(t), ",".join(t.get("hosts") or ["?"])) for t in open_[:5])
    return [finding("info", "TOKEN_UNVERIFIED", "%d API token(s) with no status code in the session" % len(open_),
                    short(evidence, 400),
                    "Nothing in the transcript shows whether these were accepted (curl without -i / -w "
                    "'%{http_code}' prints no status). Check them where they are issued.")]


# ── sections ─────────────────────────────────────────────────────────────────

def _row_text(t):
    return "  %-10s %-18s %-8s %-28s %-12s %s" % (
        short(t.get("kind"), 10), short("$" + t["var"] if t.get("var") else "-", 18), t.get("fp") or "-",
        short(",".join(t.get("hosts") or []) or "-", 28), short(_codes(t.get("codes")) or "-", 12),
        t.get("verdict") or "")


@section(360)
def section_tokens(report):
    rows = _rows(report)
    if not rows:
        return ["TOKENS none in Bash curl/wget"]
    bad = sum(1 for t in rows if str(t.get("verdict") or "").startswith("❌"))
    out = ["TOKENS %d in Bash curl/wget · %d rejected · values never shown, status from codes in the session"
           % (len(rows), bad)]
    out += [_row_text(t) for t in rows[:15]]
    if len(rows) > 15:
        out.append("  … %d more — full" % (len(rows) - 15))
    return out


@details(365)
def details_tokens(report):
    rows = _rows(report)
    if len(rows) <= 15:
        return []
    return ["TOKENS rest"] + [_row_text(t) for t in rows[15:]]
