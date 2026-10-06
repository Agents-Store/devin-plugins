"""HTTP requests the session made: Bash curl/wget/httpie/gh, python/node snippets, WebFetch, WebSearch,
MCP tool calls and Claude's own API errors, with method, host, path and status codes.

Reads the typed event list from doctor_events (memoized on ctx); read-only, no network. Every host
and path passes through redact() before it is stored, so a userinfo or query secret never lands in a
line. A request whose status the transcript does not show gets the code "?" — about four curls in
five print no status, so "?" is expected, not a failure. Missing keys never raise.

parse_curl() and requests_from_event() are reused by the token-leak section.
"""
import json
import re
import shlex
from datetime import datetime
from urllib.parse import urlsplit

from doctor_common import collector, details, redact, section, short, top
from doctor_events import events as session_events

REQUEST_COMMANDS = ("curl", "wget", "http", "https", "gh")
SCRIPT_COMMANDS = ("python", "python3", "node", "deno", "bun")
EXCLUDED_COMMANDS = ("git", "npm", "npx", "pip", "pip3", "yarn", "pnpm", "docker", "apt", "apt-get")
SKIP_WORDS = ("sudo", "time", "nohup", "exec", "command", "env", "then", "do", "else", "elif", "if",
              "while", "until", "!", "{", "xargs")
NETWORK_ERRORS = re.compile(r"ECONNRESET|ENOTFOUND|ETIMEDOUT|ECONNREFUSED|EAI_AGAIN|socket hang up", re.I)
HTTP_METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS")
MAX_REQUESTS = 500      # per-request rows kept for the full view

CURL_SHORT_ARG = frozenset("XHudoeAbcwmTFKrxEyYzCQUPt")
CURL_LONG_ARG = frozenset((
    "request", "header", "user", "data", "data-raw", "data-binary", "data-urlencode", "data-ascii", "json",
    "form", "form-string", "output", "upload-file", "url", "user-agent", "referer", "cookie", "cookie-jar",
    "write-out", "max-time", "connect-timeout", "retry", "retry-delay", "retry-max-time", "cacert", "cert",
    "key", "proxy", "proxy-user", "resolve", "connect-to", "limit-rate", "range", "oauth2-bearer",
    "aws-sigv4", "config", "dump-header", "trace", "trace-ascii", "interface", "unix-socket", "cert-type",
    "capath", "ciphers", "expect100-timeout", "time-cond", "continue-at", "quote", "pass", "proxy-header",
    "variable", "next-after", "stderr", "etag-save", "etag-compare", "output-dir", "hsts", "alt-svc"))
CURL_DATA_FLAGS = frozenset(("d", "F", "data", "data-raw", "data-binary", "data-urlencode", "data-ascii",
                             "json", "form", "form-string"))
WGET_ARG = frozenset(("-O", "-o", "-P", "-t", "-T", "-w", "-e", "-U", "-a", "-i", "-B", "-l", "-Q",
                      "--header", "--user-agent", "--post-data", "--post-file", "--timeout", "--tries",
                      "--output-document", "--output-file", "--directory-prefix", "--user", "--password",
                      "--referer", "--wait", "--limit-rate", "--certificate", "--ca-certificate"))
HTTPIE_ARG = frozenset(("-a", "--auth", "-A", "--auth-type", "--timeout", "--session", "--session-read-only",
                        "-o", "--output", "--proxy", "--verify", "--cert", "--cert-key", "--max-redirects",
                        "--pretty", "-s", "--style", "--print", "-p", "--default-scheme"))

URLISH = re.compile(r"^(?:[A-Za-z][A-Za-z0-9+.\-]*://|\$\{?[A-Za-z_][A-Za-z0-9_]*\}?(?:/|:|$)"
                    r"|localhost(?::\d+)?(?:/|$)|(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?(?:/|$)"
                    r"|[A-Za-z0-9][A-Za-z0-9.\-]*\.[A-Za-z]{2,}(?::\d+)?(?:/|$))")
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.\-]*://")
UUIDISH = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
HEXLONG = re.compile(r"^[0-9a-fA-F]{16,}$")
OPAQUE = re.compile(r"^[A-Za-z0-9_\-]{24,}$")
HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
PY_CALL = re.compile(r"""\b(?:requests|httpx|aiohttp|axios|got|session|client|http|https|s|r)\.(get|post|put|patch|delete|head)"""
                     r"""\s*\(\s*[fFrb]?['"`](https?://[^'"`\s)]+)""")
FETCH_CALL = re.compile(r"""\bfetch\s*\(\s*['"`](https?://[^'"`\s)]+)""")
URLOPEN_CALL = re.compile(r"""\b(?:urlopen|Request)\s*\(\s*['"`](https?://[^'"`\s)]+)""")
FETCH_METHOD = re.compile(r"""method\s*:\s*['"`]([A-Za-z]+)""")
MCP_NAME = re.compile(r"^mcp__(.+?)__(.+)$")
MCP_CODES = (re.compile(r"status code (\d{3})"), re.compile(r"\((\d{3})\)"),
             re.compile(r"HTTP (\d{3})"), re.compile(r": (\d{3}) "))
LONE_CODE = re.compile(r"(?m)^\s*([1-5]\d\d)\s*$")
HTTP_LINE = re.compile(r"HTTP/\d(?:\.\d)? (\d{3})")
RETURNED_ERROR = re.compile(r"returned error: (\d{3})")
WGET_CODE = re.compile(r"awaiting response\.\.\. (\d{3})|ERROR (\d{3})")
CURL_ERROR = re.compile(r"curl: \((\d+)\)")
GH_ERROR = re.compile(r"gh: .*\(HTTP (\d{3})\)")


# ── command splitting ────────────────────────────────────────────────────────

def _split_commands(command):
    """Split a shell line on ; && || | newline ( ) ` outside quotes -> [segment, ...]."""
    command = command.replace("\\\n", " ")
    segments, buf, quote, i, n = [], [], None, 0, len(command)
    while i < n:
        c = command[i]
        if quote:
            buf.append(c)
            if c == "\\" and quote == '"' and i + 1 < n:
                buf.append(command[i + 1])
                i += 2
                continue
            if c == quote:
                quote = None
        elif c == "\\" and i + 1 < n:
            buf.append(c)
            buf.append(command[i + 1])
            i += 2
            continue
        elif c in "'\"":
            quote = c
            buf.append(c)
        elif c in ";|\n()`" or (c == "&" and command[i + 1:i + 2] == "&"):
            segments.append("".join(buf))
            buf = []
            if c in "|&" and command[i + 1:i + 2] == c:
                i += 1
        else:
            buf.append(c)
        i += 1
    segments.append("".join(buf))
    return [s.strip() for s in segments if s.strip()]


def _split_heredocs(command):
    """-> (text without heredoc bodies, [(owner_line, body), ...])."""
    out, bodies, delim, owner, body = [], [], None, "", []
    for line in command.split("\n"):
        if delim is not None:
            if line.strip() == delim:
                bodies.append((owner, "\n".join(body)))
                delim, body = None, []
            else:
                body.append(line)
            continue
        out.append(line)
        found = HEREDOC.search(line)
        if found:
            delim, owner, body = found.group(2), line, []
    if delim is not None:
        bodies.append((owner, "\n".join(body)))
    return "\n".join(out), bodies


def _tokens(segment):
    try:
        return shlex.split(segment)
    except ValueError:
        return segment.split()


def _command_tokens(segment):
    """Tokens of a segment with leading assignments, sudo/time/env... and a path prefix removed."""
    toks = _tokens(segment)
    while toks:
        word = toks[0]
        if ASSIGN.match(word) or word in SKIP_WORDS:
            toks = toks[1:]
        elif word == "timeout" and len(toks) > 1:
            toks = toks[2:]
        else:
            break
    if toks:
        toks[0] = toks[0].rsplit("/", 1)[-1]
    return toks


# ── parsers ──────────────────────────────────────────────────────────────────

def _urlish(token):
    return bool(URLISH.match(token))


def parse_curl(command_str):
    """One curl command -> {method, url, headers: {lower-name: value}, user, insecure}, or None without a URL."""
    toks = _tokens(command_str or "")
    if toks and toks[0].rsplit("/", 1)[-1] == "curl":
        toks = toks[1:]
    method, url, user, insecure, head, data, get_mode, upload = None, None, None, False, False, False, False, False
    headers = {}

    def apply(flag, value):
        nonlocal method, url, user, data, upload
        if flag in ("X", "request"):
            method = (value or "").upper() or method
        elif flag in ("H", "header"):
            name, sep, val = (value or "").partition(":")
            if sep:
                headers[name.strip().lower()] = val.strip()
        elif flag in ("u", "user"):
            user = value
        elif flag == "url":
            url = url or value
        elif flag == "T":
            upload = True
        if flag in CURL_DATA_FLAGS:
            data = True

    i = 0
    while i < len(toks):
        tok = toks[i]
        i += 1
        if tok == "--":
            continue
        if tok.startswith("--"):
            name, eq, val = tok[2:].partition("=")
            if name in ("insecure",):
                insecure = True
            elif name == "head":
                head = True
            elif name == "get":
                get_mode = True
            elif name in CURL_LONG_ARG:
                if not eq and i < len(toks):
                    val, i = toks[i], i + 1
                apply(name, val)
            continue
        if tok.startswith("-") and len(tok) > 1:
            j = 1
            while j < len(tok):
                ch = tok[j]
                j += 1
                if ch == "k":
                    insecure = True
                elif ch == "I":
                    head = True
                elif ch == "G":
                    get_mode = True
                elif ch in CURL_SHORT_ARG:
                    val = tok[j:]
                    if not val and i < len(toks):
                        val, i = toks[i], i + 1
                    apply(ch, val)
                    break
            continue
        if url is None and _urlish(tok):
            url = tok
    if not url:
        return None
    if head:
        method = "HEAD"
    elif method is None:
        method = "PUT" if upload else ("POST" if data and not get_mode else "GET")
    return {"method": method, "url": url, "headers": headers, "user": user, "insecure": insecure}


def _parse_wget(toks):
    method, url, i = "GET", None, 1
    while i < len(toks):
        tok = toks[i]
        i += 1
        if tok.startswith("--method="):
            method = tok.split("=", 1)[1].upper() or method
        elif tok in ("--post-data", "--post-file") or tok.startswith(("--post-data=", "--post-file=")):
            method = "POST"
            if "=" not in tok:
                i += 1
        elif tok == "--spider":
            method = "HEAD"
        elif tok in WGET_ARG:
            i += 1
        elif not tok.startswith("-") and url is None and _urlish(tok):
            url = tok
    return {"method": method, "url": url} if url else None


def _parse_httpie(toks, scheme):
    method, url, i, data = None, None, 1, False
    while i < len(toks):
        tok = toks[i]
        i += 1
        if tok in HTTPIE_ARG:
            i += 1
        elif tok.startswith("-"):
            continue
        elif method is None and url is None and tok.upper() in HTTP_METHODS and tok.isupper():
            method = tok
        elif url is None:
            url = tok
        elif "=" in tok and "==" not in tok:
            data = True
    if not url:
        return None
    if url.startswith(":") and not SCHEME.match(url):
        url = "localhost" + url
    if not SCHEME.match(url):
        url = scheme + "://" + url
    return {"method": method or ("POST" if data else "GET"), "url": url}


def _parse_gh(toks):
    """gh api ... -> its endpoint; any other gh subcommand -> a CLI call against api.github.com."""
    words = [t for t in toks[1:] if not t.startswith("-")]
    if words[:1] == ["api"]:
        method, path, i, data = None, None, 2, False
        rest = toks[2:]
        k = 0
        while k < len(rest):
            tok = rest[k]
            k += 1
            if tok in ("-X", "--method") and k < len(rest):
                method, k = rest[k].upper(), k + 1
            elif tok.startswith("--method="):
                method = tok.split("=", 1)[1].upper()
            elif tok in ("-f", "-F", "--field", "--raw-field", "--input"):
                data, k = True, k + 1
            elif tok in ("-H", "--header", "-q", "--jq", "-t", "--template", "--hostname", "--cache"):
                k += 1
            elif not tok.startswith("-") and path is None:
                path = tok
        if path is None:
            return None
        if SCHEME.match(path):
            return {"method": method or "GET", "url": path}
        return {"method": method or ("POST" if data else "GET"),
                "url": "https://api.github.com/" + path.lstrip("/")}
    sub = " ".join(["gh"] + words[:2])
    return {"method": "CLI", "url": "https://api.github.com/" + sub.replace(" ", "/"), "label": sub}


# ── URL normalisation ────────────────────────────────────────────────────────

def _norm_segment(seg):
    if (seg.isdigit() or UUIDISH.match(seg) or HEXLONG.match(seg)
            or (OPAQUE.match(seg) and re.search(r"\d", seg))):
        return ":id"
    return seg


def split_url(url):
    """url -> (host, path): redacted, userinfo/query dropped, numeric and opaque ids -> :id."""
    text = redact(str(url or "").strip().strip("'\"<>,;)"))
    host, path = "", ""
    try:
        if SCHEME.match(text):
            parts = urlsplit(text)
            host, path = parts.netloc, parts.path
        else:
            raise ValueError("no scheme")
    except ValueError:
        body = SCHEME.sub("", text)
        auth, sep, rest = re.split(r"[?#]", body, 1)[0].partition("/")
        host, path = auth, (sep + rest) if sep else ""
    host = host.rpartition("@")[2].lower()
    path = "/".join(_norm_segment(s) for s in path.split("/"))
    return redact(host), short(redact(path), 90)


# ── requests from an event ───────────────────────────────────────────────────

def _req(ev, source, method, url, code, label=None):
    host, path = split_url(url)
    return {"ts": ev.get("ts"), "actor": ev.get("actor") or "main", "source": source,
            "method": method, "host": host, "path": label or path, "code": str(code)}


def _bash_code(source, text, segment):
    """The status the command's output shows: an HTTP code, curl:N for a network error, or '?'."""
    text = text or ""
    if source == "curl" and re.search(r"(?:^|\s)(?:-[A-Za-z]*w|--write-out)\b", segment):
        lone = LONE_CODE.findall(text)
        if lone:
            return lone[-1]
    for rx in (HTTP_LINE, RETURNED_ERROR):
        found = rx.findall(text)
        if found:
            return found[-1]
    if source == "wget":
        found = [a or b for a, b in WGET_CODE.findall(text)]
        if found:
            return found[-1]
    found = CURL_ERROR.findall(text)
    if found and source in ("curl", "httpie"):
        return "curl:" + found[-1]
    if source == "gh":
        found = GH_ERROR.findall(text)
        if found:
            return found[-1]
    return "?"


def _script_requests(ev, source, code_text):
    found, seen = [], set()
    for match in PY_CALL.finditer(code_text):
        key = (match.group(1).upper(), match.group(2))
        if key not in seen:
            seen.add(key)
            found.append(key)
    for match in FETCH_CALL.finditer(code_text):
        near = FETCH_METHOD.search(code_text[match.end():match.end() + 200])
        key = ((near.group(1).upper() if near else "GET"), match.group(1))
        if key not in seen:
            seen.add(key)
            found.append(key)
    for match in URLOPEN_CALL.finditer(code_text):
        key = ("GET", match.group(1))
        if key not in seen:
            seen.add(key)
            found.append(key)
    return [_req(ev, source, method, url, "?") for method, url in found]


def _bash_requests(ev):
    command = (ev.get("input") or {}).get("command")
    if not isinstance(command, str) or not command.strip():
        return []
    text = ev.get("result_text") or ""
    stripped, bodies = _split_heredocs(command)
    found = []   # (source, parsed, segment)
    for segment in _split_commands(stripped):
        toks = _command_tokens(segment)
        if not toks:
            continue
        head = toks[0]
        if head in EXCLUDED_COMMANDS:
            continue
        if head == "curl":
            parsed = parse_curl(segment)
            if parsed:
                found.append(("curl", parsed, segment))
        elif head == "wget":
            parsed = _parse_wget(toks)
            if parsed:
                found.append(("wget", parsed, segment))
        elif head in ("http", "https"):
            parsed = _parse_httpie(toks, head)
            if parsed:
                found.append(("httpie", parsed, segment))
        elif head == "gh":
            parsed = _parse_gh(toks)
            if parsed:
                found.append(("gh", parsed, segment))
        elif head in SCRIPT_COMMANDS:
            source = "node" if head in ("node", "deno", "bun") else "python"
            code = segment + "\n" + "\n".join(b for owner, b in bodies if head in owner)
            found.extend(("script", source, r) for r in _script_requests(ev, source, code))
    if not any(item[0] == "script" for item in found):   # `python - <<EOF` leaves the owner line alone
        for owner, body in bodies:
            toks = _command_tokens(owner)
            if toks and toks[0] in SCRIPT_COMMANDS:
                source = "node" if toks[0] in ("node", "deno", "bun") else "python"
                found.extend(("script", source, r) for r in _script_requests(ev, source, body))
    commands = [item for item in found if item[0] != "script"]
    out = [item[2] for item in found if item[0] == "script"]
    for source, parsed, segment in commands:
        # Several requests in one command share one output: the status cannot be told apart.
        code = _bash_code(source, text, segment) if len(commands) == 1 else "?"
        out.append(_req(ev, source, parsed["method"], parsed["url"], code, parsed.get("label")))
    return out


def _mcp_code(ev, text):
    err_body = False
    if text.lstrip().startswith("{"):
        try:
            body = json.loads(text)
            err_body = isinstance(body, dict) and bool(body.get("error"))
        except ValueError:
            err_body = bool(re.match(r'^\s*\{\s*"error"\s*:\s*(?!null\b)', text))
    if ev.get("is_error") or err_body:
        for rx in MCP_CODES:
            found = rx.search(text)
            if found:
                return found.group(1)
        return "error"
    found = MCP_CODES[0].search(text[:300])    # a server that forgot isError but says so in words
    return found.group(1) if found else "ok"


def requests_from_event(event):
    """One tool / api_error event -> [request, ...]; each request is
    {ts, actor, source, method, host, path, code} with host and path redacted; code is a string
    (HTTP status, 'ok', 'error', 'err', 'curl:N' or '?'). Other event kinds and odd shapes -> []."""
    try:
        if not isinstance(event, dict):
            return []
        kind = event.get("kind")
        if kind == "api_error":
            status = event.get("status")
            match = re.search(r"https?://([^/\s\"']+)", str(event.get("error") or ""))
            req = {"ts": event.get("ts"), "actor": event.get("actor") or "main", "source": "api",
                   "method": "POST", "host": redact(match.group(1)) if match else "<api>",
                   "path": "", "code": str(status) if isinstance(status, int) else "?"}
            if isinstance(event.get("retry_attempt"), int):
                req["retry"] = event["retry_attempt"]
            return [req]
        if kind != "tool":
            return []
        name = str(event.get("name") or "")
        inp = event.get("input") if isinstance(event.get("input"), dict) else {}
        text = event.get("result_text") or ""
        res = event.get("tool_result") if isinstance(event.get("tool_result"), dict) else {}
        if name == "Bash":
            return _bash_requests(event)
        if name == "WebFetch":
            url = inp.get("url") or res.get("url")
            if not isinstance(url, str) or not url:
                return []
            code = res.get("code")
            if isinstance(code, int) and not isinstance(code, bool):
                code = str(code)
            elif NETWORK_ERRORS.search(text):
                code = "err"
            else:
                code = "error" if event.get("is_error") else "?"
            return [_req(event, "WebFetch", "GET", url, code)]
        if name == "WebSearch":
            return [{"ts": event.get("ts"), "actor": event.get("actor") or "main", "source": "WebSearch",
                     "method": "SEARCH", "host": "", "path": "",
                     "code": "error" if event.get("is_error") else "ok"}]
        mcp = MCP_NAME.match(name)
        if mcp:
            return [{"ts": event.get("ts"), "actor": event.get("actor") or "main", "source": "mcp",
                     "method": "CALL", "host": redact(mcp.group(1)), "path": redact(mcp.group(2)),
                     "code": _mcp_code(event, text)}]
    except Exception:   # an odd event is a missing row, never a crash
        return []
    return []


# ── collector and sections ───────────────────────────────────────────────────

def _is_error(code, source):
    code = str(code)
    return (source in ("api", "mcp-connect") or code in ("err", "error") or code.startswith("curl:")
            or (code.isdigit() and int(code) >= 400))


def _collapse_api(reqs):
    """Retries of one API call arrive as several api_error events with a rising retry_attempt; keep one."""
    out, prev = [], None
    for req in reqs:
        if req["source"] != "api":
            out.append(req)
            continue
        retry, last = req.get("retry"), prev.get("retry") if prev else None
        same = (prev is not None and req["code"] == prev["code"] and last is not None
                and (retry is None or retry > last))
        if same:
            prev["retry"] = max(retry if retry is not None else last, last)
            continue
        prev = dict(req)
        out.append(prev)
    return out


def build_lines(events):
    """-> (lines grouped by source/method/host/path, every request in time order)."""
    reqs = []
    for ev in events or []:
        reqs.extend(requests_from_event(ev))
    reqs = _collapse_api(reqs)
    grouped = {}
    for req in reqs:
        key = (req["source"], req["method"], req["host"], req["path"])
        line = grouped.get(key)
        if line is None:
            line = grouped[key] = {"source": key[0], "method": key[1], "host": key[2], "path": key[3],
                                   "count": 0, "codes": {}, "has_error": False}
        line["count"] += 1
        line["codes"][req["code"]] = line["codes"].get(req["code"], 0) + 1
        line["has_error"] = line["has_error"] or _is_error(req["code"], req["source"])
        if req.get("retry"):
            line["retries"] = max(line.get("retries", 0), req["retry"])
    return list(grouped.values()), reqs


def mcp_connect_requests(events):
    """One request per distinct (server, errorCode). failedMcpServers repeats in every deferred_tools_delta,
    so the same broken server arrives many times; the first occurrence (its ts and actor) is kept."""
    seen = {}
    for ev in events or []:
        if not isinstance(ev, dict) or ev.get("kind") != "mcp_connect":
            continue
        name = short(redact(str(ev.get("name") or "")[:200]), 60) or "?"
        code = short(redact(str(ev.get("error_code") or "")[:200]), 60) or "?"
        if (name, code) not in seen:
            seen[(name, code)] = {"ts": ev.get("ts"), "actor": ev.get("actor") or "main", "source": "mcp-connect",
                                  "method": "", "host": name, "path": "", "code": code}
    return list(seen.values())


@collector("http")
def collect_http(ctx):
    events = (session_events(ctx) or {}).get("events") or []
    lines, reqs = build_lines(events)
    connects = mcp_connect_requests(events)
    for req in connects:
        lines.append({"source": "mcp-connect", "method": "", "host": req["host"], "path": "", "count": 1,
                      "codes": {req["code"]: 1}, "has_error": True})
    reqs = sorted(reqs + connects, key=lambda r: r["ts"] if isinstance(r.get("ts"), (int, float)) else 0)
    rows = [{"ts": r["ts"], "actor": r["actor"], "source": r["source"], "method": r["method"],
             "host": r["host"], "path": r["path"], "code": r["code"]} for r in reqs[:MAX_REQUESTS]]
    return {"lines": lines, "requests": rows, "total": len(reqs)}


def _target(line):
    sep = "·" if line.get("source") == "mcp" else ""   # server·tool, not host/path
    return short(sep.join((line.get("host") or "", line.get("path") or "")) or "-", 60)


def _codes(codes):
    items = sorted((codes or {}).items(), key=lambda kv: (-kv[1], kv[0]))
    return " ".join("%s×%d" % (k, v) for k, v in items[:5]) + (" …" if len(items) > 5 else "")


def _line_text(line):
    text = "  %s %-9s %-6s %-60s %s" % ("✗" if line.get("has_error") else " ", short(line.get("source"), 9),
                                       short(line.get("method"), 6), _target(line), _codes(line.get("codes")))
    if line.get("retries"):
        text += " (retries %d)" % line["retries"]
    return text


@section(340)
def section_http(r):
    data = r.get("http") or {}
    lines = data.get("lines") or []
    total = data.get("total") or sum(l.get("count", 0) for l in lines)
    if not lines:
        return ["HTTP REQUESTS none"]
    by_source = {}
    for line in lines:
        by_source[line["source"]] = by_source.get(line["source"], 0) + line.get("count", 0)
    errors = [l for l in lines if l.get("has_error")]
    out = ["HTTP REQUESTS %d in %d lines, %d with errors · %s" % (total, len(lines), len(errors), top(by_source, 6))]
    shown = list(errors)
    rest = sorted((l for l in lines if not l.get("has_error")), key=lambda l: -l.get("count", 0))
    shown += rest[:10]
    out += [_line_text(l) for l in shown]
    if len(lines) > len(shown):
        out.append("  … %d more — full" % (len(lines) - len(shown)))
    return out


def _clock(ts):
    try:
        return datetime.fromtimestamp(ts).strftime("%H:%M:%S")
    except (TypeError, ValueError, OverflowError, OSError):
        return "?"


@details(345)
def details_http(r):
    data = r.get("http") or {}
    rows = data.get("requests") or []
    if not rows:
        return ["HTTP REQUESTS none"]
    out = ["HTTP REQUESTS by time"]
    for row in rows:
        out.append("  %s %-9s %-6s %-60s %s" % (_clock(row.get("ts")), short(row.get("source"), 9),
                                               short(row.get("method"), 6), _target(row), row.get("code")))
    if (data.get("total") or 0) > len(rows):
        out.append("  … %d more not kept" % (data["total"] - len(rows)))
    return out
