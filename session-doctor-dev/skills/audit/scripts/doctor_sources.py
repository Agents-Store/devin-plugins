"""Where session-doctor looks: arguments, Claude Code files, the claude process, settings, git.

Test overrides: SESSION_DOCTOR_PROC replaces /proc, SESSION_DOCTOR_MANAGED_DIR
replaces the managed-settings directory.
"""
import glob
import os
import re
import sys
from functools import lru_cache

from doctor_common import PLACEHOLDER, read_json, run

SETTINGS_PRECEDENCE = ("managed", "local", "project", "user")


# ── arguments and Claude Code files ──────────────────────────────────────────

def parse_args(argv):
    """--session/--cwd/--json/--full, plus --args with the raw text the user typed after the command."""
    opts = {"session": None, "arg_session": None, "cwd": None, "json": False, "full": False}
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("--session", "--cwd", "--args") and i + 1 < len(argv):
            value = argv[i + 1]
            i += 2
            if arg != "--args":
                opts[arg[2:]] = None if PLACEHOLDER.match(value) else value
                continue
            for token in value.split():
                low = token.lower().lstrip("-")
                if low in ("full", "json"):
                    opts[low] = True
                elif not PLACEHOLDER.match(token) and re.match(r"^([0-9a-fA-F-]{6,}|.+\.jsonl)$", token):
                    opts["arg_session"] = token
            continue
        if arg in ("--json", "--full"):
            opts[arg[2:]] = True
        i += 1
    return opts


def config_dir(env):
    return env.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")


def claude_json_path(env, cfg):
    """A custom CLAUDE_CONFIG_DIR keeps its own .claude.json; never read another profile's."""
    if env.get("CLAUDE_CONFIG_DIR"):
        return os.path.join(cfg, ".claude.json")
    return os.path.join(os.path.expanduser("~"), ".claude.json")


def slugify(path):
    return re.sub(r"[^A-Za-z0-9]", "-", path)


def find_transcript(cfg, session, cwd):
    """Return (path, note): the session's transcript, else the newest one for cwd."""
    root = os.path.join(cfg, "projects")
    if session:
        if os.path.isfile(session):
            return session, None
        hits = (glob.glob(os.path.join(root, "*", session + ".jsonl"))
                or glob.glob(os.path.join(root, "*", session + "*.jsonl")))
        if hits:
            return max(hits, key=os.path.getmtime), None
        return None, "no transcript for session %s yet (first turn?)" % session[:8]
    candidates = [p for p in glob.glob(os.path.join(root, slugify(cwd), "*.jsonl")) if os.path.getsize(p) > 0]
    if not candidates:
        return None, None
    return max(candidates, key=os.path.getmtime), None


def session_record(cfg, pid):
    """Claude Code's registry entry for a live session: $CLAUDE_CONFIG_DIR/sessions/<pid>.json."""
    data, _ = read_json(os.path.join(cfg, "sessions", "%s.json" % pid)) if pid else (None, None)
    return data if isinstance(data, dict) else {}


def looks_like_claude(argv):
    """The program is claude: its own path says so, or node/bun runs a claude script."""
    if not argv:
        return False
    program = argv[0].lower()
    runner = os.path.basename(program) in ("node", "bun", "deno")
    return "claude" in program or (runner and len(argv) > 1 and "claude" in argv[1].lower())


def is_claude_process(pid, env):
    """A live pid whose program is claude — a stale registry entry's pid may be reused."""
    argv = read_argv(pid, env)
    if argv is None:
        return pid_alive(pid)
    return looks_like_claude(argv)


def pid_alive(pid):
    try:
        os.kill(int(pid), 0)
    except (ProcessLookupError, ValueError, TypeError):
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


# ── the claude process ───────────────────────────────────────────────────────

def proc_root(env):
    return env.get("SESSION_DOCTOR_PROC") or "/proc"


def read_argv(pid, env):
    try:
        with open(os.path.join(proc_root(env), str(pid), "cmdline"), "rb") as fh:
            return [a.decode("utf-8", "replace") for a in fh.read().split(b"\0") if a]
    except OSError:
        pass
    if env.get("SESSION_DOCTOR_PROC") or sys.platform.startswith("linux"):
        return None
    code, out = run(["ps", "-o", "args=", "-p", str(pid)])
    return out.split() if code == 0 and out else None


def read_launch_env(pid, env):
    """The environment the claude process started with (Linux only; None elsewhere)."""
    try:
        with open(os.path.join(proc_root(env), str(pid), "environ"), "rb") as fh:
            raw = fh.read()
    except OSError:
        return None
    result = {}
    for item in raw.split(b"\0"):
        if b"=" in item:
            key, value = item.split(b"=", 1)
            result[key.decode("utf-8", "replace")] = value.decode("utf-8", "replace")
    return result


def parent_pid(pid, env):
    try:
        with open(os.path.join(proc_root(env), str(pid), "stat")) as fh:
            return int(fh.read().rsplit(")", 1)[1].split()[1])
    except (OSError, ValueError, IndexError):
        pass
    if env.get("SESSION_DOCTOR_PROC"):
        return None
    code, out = run(["ps", "-o", "ppid=", "-p", str(pid)])
    try:
        return int(out) if code == 0 else None
    except ValueError:
        return None


def find_claude_pid(env):
    """CLAUDE_PID when Claude Code sets it, else the nearest ancestor whose command line says claude."""
    pid = env.get("CLAUDE_PID", "")
    if pid.isdigit():
        return int(pid)
    current = os.getppid()
    for _ in range(6):
        if not current or current <= 1:
            return None
        if looks_like_claude(read_argv(current, env)):
            return current
        current = parent_pid(current, env)
    return None


def parse_flags(argv):
    flags = {}
    takes_value = ("--model", "--effort", "--permission-mode", "--fallback-model", "--mcp-config",
                   "--settings", "--agents", "--add-dir", "--resume", "--session-id")
    i = 0
    while i < len(argv):
        name, has_eq, value = argv[i].partition("=")
        if name in takes_value:
            if not has_eq:
                value = argv[i + 1] if i + 1 < len(argv) else ""
                i += 1
            flags.setdefault(name, []).append(value)
        elif name in ("--dangerously-skip-permissions", "--print", "-p", "--continue", "-c"):
            flags.setdefault(name, []).append(True)
        i += 1
    return flags


# ── settings, git, plugins ───────────────────────────────────────────────────

def managed_dirs(env):
    if env.get("SESSION_DOCTOR_MANAGED_DIR"):
        return [env["SESSION_DOCTOR_MANAGED_DIR"]]
    if sys.platform == "darwin":
        return ["/Library/Application Support/ClaudeCode"]
    return ["/etc/claude-code"]


def load_settings(cfg, project_dir, env):
    """Every settings file that exists, as {scope, path, data, error}."""
    paths = []
    for base in managed_dirs(env):
        paths.append(("managed", os.path.join(base, "managed-settings.json")))
        paths.extend(("managed", p) for p in sorted(glob.glob(os.path.join(base, "managed-settings.d", "*.json"))))
    paths.append(("user", os.path.join(cfg, "settings.json")))
    paths.append(("project", os.path.join(project_dir, ".claude", "settings.json")))
    paths.append(("local", os.path.join(project_dir, ".claude", "settings.local.json")))
    layers = []
    for scope, path in paths:
        data, error = read_json(path)
        if data is None and error is None:
            continue
        layers.append({"scope": scope, "path": path, "data": data if isinstance(data, dict) else {},
                       "error": error})
    return layers


def effective(layers, getter, scopes=SETTINGS_PRECEDENCE):
    """The value from the highest-precedence settings file that sets it, and that file's scope."""
    for scope in scopes:
        for layer in layers:
            if layer["scope"] != scope:
                continue
            try:
                value = getter(layer["data"])
            except (AttributeError, TypeError):
                value = None
            if value not in (None, "", [], {}):
                return value, scope
    return None, None


def settings_env(layers):
    """{name: (value, scope)} from every settings `env` block, highest precedence first."""
    merged = {}
    for scope in SETTINGS_PRECEDENCE:
        for layer in layers:
            block = layer["data"].get("env") if layer["scope"] == scope else None
            if isinstance(block, dict):
                for name, value in block.items():
                    merged.setdefault(name, (str(value), scope))
    return merged


def git(path, *args):
    """Read-only git: --no-optional-locks keeps `status` from rewriting a shared checkout's index."""
    return run(["git", "--no-optional-locks", "-C", path] + list(args))


def git_root(path):
    code, top = git(path, "rev-parse", "--show-toplevel")
    return top if code == 0 and top else None


def git_info(path):
    code, top = git(path, "rev-parse", "--show-toplevel")
    if code != 0 or not top:
        return {"repo": False}
    _, branch = git(path, "rev-parse", "--abbrev-ref", "HEAD")
    _, status = git(path, "status", "--porcelain")
    _, head = git(path, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    default = head.split("/", 1)[1] if "/" in head else None
    for candidate in ("main", "master"):
        if not default and git(path, "rev-parse", "--verify", "--quiet", "refs/remotes/origin/" + candidate)[0] == 0:
            default = candidate
    return {"repo": True, "root": top, "branch": branch or "?",
            "worktree": os.path.isfile(os.path.join(top, ".git")),
            "dirty": len([line for line in status.splitlines() if line.strip()]),
            "default_branch": default}


@lru_cache(maxsize=None)
def tracked(path):
    if not path or not os.path.exists(path):
        return False
    code, _ = git(os.path.dirname(path) or ".", "ls-files", "--error-unmatch", os.path.basename(path))
    return code == 0


def plugins_state(layers, cfg, env, project_dir):
    """enabledPlugins merged by precedence, joined with installed_plugins.json."""
    enabled = {}
    for scope in reversed(SETTINGS_PRECEDENCE):
        for layer in layers:
            block = layer["data"].get("enabledPlugins") if layer["scope"] == scope else None
            if isinstance(block, dict):
                for plugin_id, on in block.items():
                    enabled[plugin_id] = (bool(on), scope)
    root = env.get("CLAUDE_CODE_PLUGIN_CACHE_DIR") or os.path.join(cfg, "plugins")
    data, _ = read_json(os.path.join(root, "installed_plugins.json"))
    installed = data.get("plugins") if isinstance(data, dict) else None
    plugins = []
    for plugin_id, (on, scope) in sorted(enabled.items()):
        raw = (installed or {}).get(plugin_id)
        entries = [e for e in (raw if isinstance(raw, list) else [raw]) if isinstance(e, dict)]
        chosen = next((e for e in entries if e.get("projectPath") in (project_dir, None)), None)
        chosen = chosen or (entries[0] if entries else {})
        plugins.append({"id": plugin_id, "name": plugin_id.split("@", 1)[0], "enabled": on,
                        "scope": scope, "installed": bool(entries),
                        "path": chosen.get("installPath"), "version": chosen.get("version")})
    return plugins
