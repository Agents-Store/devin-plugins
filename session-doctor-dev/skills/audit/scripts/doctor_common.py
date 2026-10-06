"""Shared helpers for session-doctor: redaction, formatting, readers and the registry.

Nothing here prints or writes, and every helper tolerates bad input: the audit
must survive any file it reads.
"""
import json
import os
import re
import subprocess
from datetime import datetime

TESTED_ON = "2.1.289"
SEVERITY_RANK = {"high": 0, "medium": 1, "low": 2, "info": 3}
PLACEHOLDER = re.compile(r"^\$\{?[A-Za-z_]+\}?$")
SECRET_NAME = re.compile(
    r"(TOKEN|SECRET|PASSW|PASS$|_PASS_|API[_-]?KEY|PRIVATE[_-]?KEY|ACCESS[_-]?KEY|CREDENTIAL|_PAT$|_PAT_|AUTH"
    r"|[_-]KEY$|_KEY_|DSN$)", re.I)
NOT_SECRET_NAME = re.compile(
    r"(URL|URI|HOST|HOSTNAME|DOMAIN|EMAIL|USERNAME|USER|REGION|PORT|ENDPOINT|SLUG|NAME|PATH|DIR)$", re.I)
TOKEN_VALUE = (
    re.compile(r"\b(?:sk|pk|rk)-[A-Za-z0-9_\-]{16,}"),
    re.compile(r"\b(?:sk|pk|rk)_(?:live|test)_[A-Za-z0-9]{16,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"\bglpat-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"\bnpm_[A-Za-z0-9]{36}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b"),
    re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}"),
    re.compile(r"(?<!\d)\d{8,10}:[A-Za-z0-9_\-]{35}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{4,}"),
    re.compile(r"\b[A-Fa-f0-9]{32,}\b"),
)
USERINFO = re.compile(r"(?i)\b([a-z][a-z0-9+.\-]*://[^\s/:@]*:)([^\s@/]+)(@)")
QUERY = re.compile(r"(?i)([?&][a-z0-9_\-]*?(?:token|key|secret|passw(?:or)?d|auth|sig|signature|code)=)([^&\s#\"']+)")
FLAG = re.compile(r"(?i)((?<!\S)--?(?:password|passwd|token|secret|api[-_]?key|access[-_]?key|auth[-_]?token"
                  r"|client[-_]?secret)(?:=|\s+))([^\s\"']+)")
CURL_USER = re.compile(r"((?<!\S)(?:-u|--user)(?:=|\s+)[^\s:]+:)(\S+)")
# A key is an identifier whose segment ENDS in a secret word (GITHUB_TOKEN, PGPASSWORD, accessToken,
# x-api-key, STRIPE_KEY, SENTRY_DSN, Authorization) — never a word that merely contains one
# (Unauthorized, authenticate, oauth, authz, "primary key").
KEY = (r"(?<![A-Za-z0-9])(?:[A-Za-z0-9]+[_.\-]){0,6}"
       r"(?:[A-Za-z0-9]*?(?:token|secret|passw(?:or)?d|pwd)|api[_\-]?key|access[_\-]?key|private[_\-]?key"
       r"|authorization|auth|credentials?|dsn|(?<=[_.\-])key)"
       r"(?![A-Za-z0-9])(?:[_.\-][A-Za-z0-9]+){0,6}")
ASSIGNMENT = re.compile(r"(?i)(" + KEY + r"[\"']?\s*[=:]\s*(?:(?:bearer|basic|token)\s+)?)"
                        r"(\"[^\"\n]*\"|'[^'\n]*'|[^\s\"'&,;}]{4,})")
BEARER = re.compile(r"(?i)\b((?:bearer|basic)\s+)([A-Za-z0-9._~+/=\-]{12,})")

_KNOWN_SECRETS = []


# ── redaction ────────────────────────────────────────────────────────────────

def secret_name(name):
    return bool(SECRET_NAME.search(name)) and not NOT_SECRET_NAME.search(name)


def remember_secrets(*sources):
    """Learn secret values — by variable name, or by a value that looks like a credential.

    Additive: a later call (a collector that found a literal token in a command) never forgets what
    an earlier one learned, so the final scrub() of the whole output erases them all."""
    values = set(_KNOWN_SECRETS)
    for source in sources:
        for name, value in (source or {}).items():
            value = value[0] if isinstance(value, tuple) else value
            if not isinstance(value, str) or len(value) < 8:
                continue
            if (secret_name(str(name)) or USERINFO.search(value)
                    or any(rx.search(value) for rx in TOKEN_VALUE)):
                values.add(value)
    _KNOWN_SECRETS[:] = sorted(values, key=len, reverse=True)


def scrub(text):
    for value in _KNOWN_SECRETS:
        if value in text:
            text = text.replace(value, "***")
    return text


def _masked(value):
    return value[0] + "***" + value[0] if value[:1] in ("'", '"') else "***"


def redact(text):
    """Mask known secret values and anything shaped like a credential."""
    text = USERINFO.sub(lambda m: m.group(1) + "***" + m.group(3), scrub(str(text)))
    for rx in (QUERY, FLAG, CURL_USER):
        text = rx.sub(lambda m: m.group(1) + "***", text)
    text = ASSIGNMENT.sub(lambda m: m.group(1) + _masked(m.group(2)), text)
    text = BEARER.sub(lambda m: m.group(1) + "***", text)
    for rx in TOKEN_VALUE:
        text = rx.sub("***", text)
    return text


def short(text, limit):
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def clean(text, limit):
    """Redact first, then shorten — a cut must never leave half a secret behind.

    Only the head that can show up after shortening is redacted, which keeps the
    regexes fast on huge error texts.
    """
    return short(redact(str(text)[: limit * 4 + 200]), limit)


# ── formatting ───────────────────────────────────────────────────────────────

def family(model):
    low = (model or "").lower()
    for name in ("opus", "sonnet", "haiku", "fable"):
        if name in low:
            return name
    return None


def iso_seconds(stamp):
    try:
        return datetime.strptime(str(stamp)[:19], "%Y-%m-%dT%H:%M:%S").timestamp()
    except ValueError:
        return None


def fmt_duration(seconds):
    seconds = int(seconds or 0)
    if seconds >= 3600:
        return "%dh%02dm" % (seconds // 3600, seconds % 3600 // 60)
    return "%dm%02ds" % (seconds // 60, seconds % 60)


def fmt_k(number):
    number = int(number or 0)
    if number >= 1000000:
        return "%.2fM" % (number / 1e6)
    if number >= 1000:
        return "%.1fk" % (number / 1e3)
    return str(number)


def top(counts, limit):
    items = sorted(counts.items(), key=lambda kv: -kv[1])
    text = " · ".join("%s %d" % (k, v) for k, v in items[:limit])
    return text + (" …" if len(items) > limit else "")


# ── readers ──────────────────────────────────────────────────────────────────

def read_json(path):
    """Return (data, error). Both are None when the file does not exist."""
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh), None
    except FileNotFoundError:
        return None, None
    except (OSError, ValueError) as exc:
        return None, "%s: %s" % (type(exc).__name__, short(exc, 120))


def iter_jsonl(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except ValueError:
                    continue
                if isinstance(record, dict):
                    yield record
    except OSError:
        return


def run(cmd, timeout=5):
    try:
        done = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                              universal_newlines=True, timeout=timeout)
        return done.returncode, done.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return 1, ""


def frontmatter(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read(6000)
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    fields = {}
    for line in text[3:end if end > 0 else 0].splitlines():
        match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip().strip("'\"")
    return fields


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(str(b.get("text") or "") for b in content
                        if isinstance(b, dict) and b.get("type") == "text")
    return ""


def walk_strings(obj, key=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            for item in walk_strings(v, k):
                yield item
    elif isinstance(obj, list):
        for v in obj:
            for item in walk_strings(v, key):
                yield item
    elif isinstance(obj, str):
        yield key, obj


def glob_to_regex(pattern):
    """Translate a claudeMdExcludes glob: ** crosses directories, * ? [ab] {a,b} do not; ~ is home."""
    pattern = os.path.expanduser(pattern) if pattern.startswith("~") else pattern
    out, i = "", 0
    while i < len(pattern):
        end = pattern.find("]" if pattern[i] == "[" else "}", i + 1) if pattern[i] in "[{" else -1
        if pattern.startswith("**/", i):
            out, i = out + "(?:.*/)?", i + 3
        elif pattern.startswith("**", i):
            out, i = out + ".*", i + 2
        elif pattern[i] == "*":
            out, i = out + "[^/]*", i + 1
        elif pattern[i] == "?":
            out, i = out + "[^/]", i + 1
        elif pattern[i] == "[" and end > i + 1:
            body = pattern[i + 1:end]
            out += "[" + ("^" + body[1:] if body.startswith("!") else body).replace("\\", "\\\\") + "]"
            i = end + 1
        elif pattern[i] == "{" and end > i:
            out += "(?:" + "|".join(re.escape(p) for p in pattern[i + 1:end].split(",")) + ")"
            i = end + 1
        else:
            out, i = out + re.escape(pattern[i]), i + 1
    try:
        return re.compile("^" + out + "$")
    except re.error:
        return re.compile(r"(?!)")


# ── registry ─────────────────────────────────────────────────────────────────
# doctor_areas.py fills these. Collectors run in file order; sections print by
# their order number, with a blank line whenever the hundreds digit changes.

COLLECTORS = []
CHECKS = []
SECTIONS = []
DETAILS = []


def collector(key):
    """Register fn(ctx) -> dict; the result lands in report[key]."""
    def register(fn):
        COLLECTORS.append((key, fn))
        return fn
    return register


def check(fn):
    """Register fn(report) -> [finding, ...]."""
    CHECKS.append(fn)
    return fn


def section(order):
    """Register fn(report) -> [line, ...] for the digest."""
    def register(fn):
        SECTIONS.append((order, fn))
        return fn
    return register


def details(order):
    """Register fn(report) -> [line, ...] printed only with `full`."""
    def register(fn):
        DETAILS.append((order, fn))
        return fn
    return register


def finding(severity, fid, title, evidence, fix):
    return {"severity": severity, "id": fid, "title": title, "evidence": evidence, "fix": fix}
