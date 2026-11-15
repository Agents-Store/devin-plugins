"""Workspace, keys, configuration, HTTP and ledger helpers shared by every command.

Nothing here prints a key: values read from the environment are remembered and
masked in every message that leaves the process.
"""
from __future__ import annotations

import base64
import copy
import csv
import datetime
import http.client
import io
import json
import mimetypes
import os
import re
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

from . import __version__

EXIT_OK, EXIT_SERVICE, EXIT_USAGE, EXIT_MISSING_KEY = 0, 1, 2, 3
USER_AGENT = "stack-ads-toolkit/%s" % __version__
TOOLKIT_DIR = Path(__file__).resolve().parent.parent


class AdsError(Exception):
    """An error meant for the person at the keyboard: a message, a hint and an exit code."""

    code = EXIT_SERVICE

    def __init__(self, message, hint="", code=None):
        super().__init__(message)
        self.message = message
        self.hint = hint
        if code is not None:
            self.code = code


class Refused(AdsError):
    """A guard rail said no, or the command was called the wrong way."""

    code = EXIT_USAGE


class MissingKey(AdsError):
    code = EXIT_MISSING_KEY


class HttpError(AdsError):
    def __init__(self, status, body, url, headers=None):
        self.status = status
        self.body = body or ""
        self.url = url
        self.headers = headers or {}
        super().__init__("HTTP %s from %s: %s" % (status, _host(url), redact(self.body.strip())[:600]))

    def json(self):
        try:
            return json.loads(self.body)
        except ValueError:
            return None


def _host(url):
    return urllib.parse.urlsplit(url).netloc or url


# ── workspace ────────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "version": 1,
    "project": {"name": "", "url": "", "markets": [], "languages": [], "currency": "USD"},
    "guardrails": {"max_daily_budget": 50, "max_research_usd_per_call": 1.0, "max_total_budget": 0},
    "api": {"google_ads": "v26", "meta_graph": "v27.0", "tiktok": "v1.3", "gemini_revision": "2026-05-20"},
    "models": {},
}
WORKSPACE_DIRS = ("brand", "research/raw", "plan/copy", "creatives/inputs", "launch", "reports/raw")


def find_workspace(explicit=None):
    """--dir, then ADS_DIR, then the folder this toolkit was copied into, then ./ads."""
    if explicit:
        return Path(explicit).expanduser().resolve()
    if os.environ.get("ADS_DIR"):
        return Path(os.environ["ADS_DIR"]).expanduser().resolve()
    if TOOLKIT_DIR.name == "tools" and (TOOLKIT_DIR.parent / "config.json").is_file():
        return TOOLKIT_DIR.parent
    return (Path.cwd() / "ads").resolve()


def merge(base, extra):
    out = copy.deepcopy(base)
    for key, value in (extra or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = merge(out[key], value)
        else:
            out[key] = value
    return out


def load_config(ws):
    path = Path(ws) / "config.json"
    if not path.is_file():
        return copy.deepcopy(DEFAULT_CONFIG)
    try:
        return merge(DEFAULT_CONFIG, json.loads(path.read_text(encoding="utf-8")))
    except ValueError as exc:
        raise Refused("%s is not valid JSON: %s" % (path, exc))


def save_config(ws, config):
    path = Path(ws) / "config.json"
    path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# ── keys ─────────────────────────────────────────────────────────────────

RE_ENV_LINE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$")
_SECRETS = set()


def parse_env_text(text):
    values = {}
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            continue
        m = RE_ENV_LINE.match(line)
        if not m:
            continue
        value = m.group(2).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        elif " #" in value:
            value = value.split(" #", 1)[0].rstrip()
        values[m.group(1)] = value
    return values


def load_env(ws):
    """Project .env, then the workspace .env, then the process environment: later wins."""
    values = {}
    ws = Path(ws)
    for path in (ws.parent / ".env", ws / ".env"):
        if path.is_file():
            values.update({k: v for k, v in parse_env_text(path.read_text(encoding="utf-8")).items() if v})
    values.update({k: v for k, v in os.environ.items() if v})
    for name, value in values.items():
        if len(value) >= 8 and re.search(r"KEY|TOKEN|SECRET|PASSWORD", name):
            _SECRETS.add(value)
    return values


def set_env_value(ws, name, value):
    """Write one variable into the workspace .env, keeping every other line as it is."""
    path = Path(ws) / ".env"
    lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
    done = False
    for i, line in enumerate(lines):
        m = RE_ENV_LINE.match(line)
        if m and m.group(1) == name and not line.lstrip().startswith("#"):
            lines[i] = "%s=%s" % (name, value)
            done = True
            break
    if not done:
        lines.append("%s=%s" % (name, value))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    _SECRETS.add(value)


def redact(text):
    """Mask every key value this process has seen."""
    text = str(text)
    for secret in sorted(_SECRETS, key=len, reverse=True):
        text = text.replace(secret, "***")
    return text


class Context:
    """What a command needs: the workspace, its configuration and the keys."""

    def __init__(self, ws):
        self.ws = Path(ws)
        self.config = load_config(self.ws)
        self.env = load_env(self.ws)

    def key(self, name, required=True):
        value = self.env.get(name, "")
        if not value and required:
            from .keys import hint_for  # late import: keys imports core
            raise MissingKey("%s is not set" % name, hint_for(name))
        return value

    def api(self, name):
        return self.config["api"][name]

    def path(self, *parts):
        target = self.ws.joinpath(*parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        return target


# ── HTTP ─────────────────────────────────────────────────────────────────

class Response:
    def __init__(self, status, headers, raw, url):
        self.status, self.headers, self.raw, self.url = status, headers, raw, url

    @property
    def text(self):
        return self.raw.decode("utf-8", "replace")

    def json(self):
        try:
            return json.loads(self.raw)
        except ValueError:
            error = AdsError("%s answered with something that is not JSON: %s" % (_host(self.url), redact(self.text[:300])))
            error.uncertain = True      # the request was accepted, so a write may have landed
            raise error


def join_url(base, *parts):
    return "/".join([base.rstrip("/")] + [str(p).strip("/") for p in parts if str(p) != ""])


def request(method, url, headers=None, params=None, json_body=None, data=None, timeout=60, retries=None):
    """One HTTP call. A read is retried on 429 and 5xx; a write is never repeated blindly."""
    method = method.upper()
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params, doseq=True)
    sent = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    body = None
    if json_body is not None:
        body = json.dumps(json_body).encode("utf-8")
        sent["Content-Type"] = "application/json"
    elif isinstance(data, dict):
        body = urllib.parse.urlencode(data, doseq=True).encode("utf-8")
        sent["Content-Type"] = "application/x-www-form-urlencoded"
    elif data is not None:
        body = data
    sent.update(headers or {})
    if retries is None:
        retries = 2 if method == "GET" else 0
    attempt = 0
    while True:
        req = urllib.request.Request(url, data=body, method=method, headers=sent)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return Response(resp.status, resp.headers, resp.read(), url)
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", "replace")
            if exc.code in (429, 500, 502, 503, 504) and attempt < retries:
                wait = exc.headers.get("Retry-After", "")
                time.sleep(min(float(wait), 30.0) if wait.replace(".", "", 1).isdigit() else 2.0 * (attempt + 1))
                attempt += 1
                continue
            raise HttpError(exc.code, raw, url, exc.headers)
        except (urllib.error.URLError, http.client.HTTPException, OSError) as exc:
            # OSError covers timeouts, resets, broken pipes and TLS failures, also while the answer is being read.
            if attempt < retries:
                time.sleep(2.0 * (attempt + 1))
                attempt += 1
                continue
            reason = getattr(exc, "reason", None) or exc
            error = AdsError("cannot reach %s: %s" % (_host(url), redact(str(reason) or type(reason).__name__)))
            # Only a failure to connect proves that nothing was sent; anything later leaves a write in doubt.
            error.uncertain = not isinstance(reason, (ConnectionRefusedError, socket.gaierror))
            raise error


def multipart(fields, files):
    """Encode a multipart/form-data body. files: (field, filename, bytes, content type)."""
    boundary = "adskit" + uuid.uuid4().hex
    out = io.BytesIO()
    for name, value in (fields or {}).items():
        out.write(("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (boundary, name, value)).encode("utf-8"))
    for name, filename, content, ctype in files or []:
        out.write(("--%s\r\nContent-Disposition: form-data; name=\"%s\"; filename=\"%s\"\r\nContent-Type: %s\r\n\r\n"
                   % (boundary, name, filename, ctype)).encode("utf-8"))
        out.write(content)
        out.write(b"\r\n")
    out.write(("--%s--\r\n" % boundary).encode("utf-8"))
    return "multipart/form-data; boundary=%s" % boundary, out.getvalue()


def guess_type(path):
    return mimetypes.guess_type(str(path))[0] or "application/octet-stream"


def read_file(path):
    path = Path(path)
    if not path.is_file():
        raise Refused("file not found: %s" % path)
    return path.read_bytes()


def b64_file(path):
    return base64.b64encode(read_file(path)).decode("ascii")


def download(url, dest, headers=None, timeout=300):
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    resp = request("GET", url, headers=headers, timeout=timeout)
    dest.write_bytes(resp.raw)
    return dest


# ── input and output ─────────────────────────────────────────────────────

def load_json_arg(value):
    """`@file.json` reads a file, anything else is parsed as JSON text."""
    if value is None:
        return None
    text = Path(value[1:]).read_text(encoding="utf-8") if value.startswith("@") else value
    try:
        return json.loads(text)
    except ValueError as exc:
        raise Refused("not valid JSON (%s): %s" % (value if value.startswith("@") else "inline", exc))


def parse_pairs(pairs):
    out = {}
    for item in pairs or []:
        if "=" not in item:
            raise Refused("expected KEY=VALUE, got %r" % item)
        key, value = item.split("=", 1)
        out[key] = value
    return out


def flatten(row, prefix=""):
    flat = {}
    for key, value in row.items():
        name = "%s.%s" % (prefix, key) if prefix else str(key)
        if isinstance(value, dict):
            flat.update(flatten(value, name))
        elif isinstance(value, list):
            flat[name] = json.dumps(value, ensure_ascii=False)
        else:
            flat[name] = value
    return flat


def to_csv(rows):
    rows = [flatten(r) if isinstance(r, dict) else {"value": r} for r in rows]
    columns = []
    for row in rows:
        for name in row:
            if name not in columns:
                columns.append(name)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def emit(data, fmt="json", out=None):
    """Print a result, or save it and print where it went."""
    if fmt == "csv":
        rows = data if isinstance(data, list) else [data]
        text = to_csv(rows)
    elif isinstance(data, str):
        text = data if data.endswith("\n") else data + "\n"
    else:
        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    text = redact(text)
    if out:
        path = Path(out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        size = len(data) if isinstance(data, list) else 1
        print("saved %s (%d %s)" % (path, size, "rows" if isinstance(data, list) else "document"))
    else:
        print(text, end="")


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slug(text, limit=48):
    text = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return text[:limit].strip("-") or "item"


def append_jsonl(path, entry):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read_jsonl(path):
    path = Path(path)
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows
