#!/usr/bin/env python3
"""session-doctor — read-only audit of the current Claude Code session.

Prints a compact digest (or JSON with --json) of where the session runs, what
context it loaded, which env variable names it can see, which model and effort
the main session and every subagent used and why, and findings with fixes.

Never prints a secret value, never writes a file, always exits 0: the skill that
runs it is aborted by a non-zero exit, and a partial audit beats none.

Usage: session_doctor.py [--session ID|PATH] [--cwd DIR] [--json] [--full] [--args "RAW"]
"""
import json
import os
import sys

sys.dont_write_bytecode = True  # read-only: no __pycache__ next to the skill
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from doctor_common import (CHECKS, COLLECTORS, DETAILS, SECTIONS, SEVERITY_RANK,  # noqa: E402
                           clean, remember_secrets, scrub)
from doctor_sources import (config_dir, find_claude_pid, find_transcript, git_info,  # noqa: E402
                            load_settings, parse_args, parse_flags, plugins_state, read_argv,
                            read_launch_env, session_record, settings_env)
from doctor_transcript import Transcript, parse_transcript  # noqa: E402
import doctor_areas  # noqa: E402,F401  (registers every collector, check and section)
import doctor_events  # noqa: E402,F401
import doctor_skills  # noqa: E402,F401
import doctor_http  # noqa: E402,F401
import doctor_tokens  # noqa: E402,F401


def _cwd():
    try:
        return os.getcwd()
    except OSError:  # the shell's directory was deleted under it
        return "/"


class Context(object):
    """Inputs shared by every collector, loaded once; a broken source becomes an error line."""

    def __init__(self, opts, env):
        self.opts, self.env, self.errors = opts, env, []
        self.cfg = config_dir(env)
        guess = opts.get("cwd") or _cwd()
        session = opts.get("arg_session") or opts.get("session") or env.get("CLAUDE_CODE_SESSION_ID")
        self.transcript_path, self.transcript_note = self._step(
            "transcript", lambda: find_transcript(self.cfg, session, guess), (None, None))
        self.t = self._step("transcript", lambda: parse_transcript(self.transcript_path), None) \
            if self.transcript_path else None
        self.t = self.t or Transcript()
        snapshot = self.t.env_first if isinstance(self.t.env_first, dict) else {}
        start = opts.get("cwd") or snapshot.get("workingDirectory") or self.t.cwd or guess
        self.start_dir = start if isinstance(start, str) else guess
        self.pid = self._step("process", lambda: find_claude_pid(env), None)
        self.argv = self._step("process", lambda: read_argv(self.pid, env), None) if self.pid else None
        self.flags = parse_flags(self.argv or [])
        self.launch_env = self._step("process", lambda: read_launch_env(self.pid, env), None) if self.pid else None
        self.live = self._step("process", lambda: session_record(self.cfg, self.pid), {})
        self.layers = self._step("settings", lambda: load_settings(self.cfg, self.start_dir, env), [])
        self.git_root = self._step("git", lambda: git_info(self.start_dir).get("root"), None)
        self.plugins = self._step("plugins", lambda: plugins_state(self.layers, self.cfg, env, self.start_dir), [])
        self._step("secrets", lambda: remember_secrets(settings_env(self.layers), self.launch_env, env), None)

    def _step(self, label, fn, default):
        try:
            return fn()
        except Exception as exc:  # keep going: a partial audit beats none
            self.errors.append("%s: %s: %s" % (label, type(exc).__name__, clean(exc, 160)))
            return default


def build_report(opts, env):
    ctx = Context(opts, env)
    report = {"tool": "session-doctor", "format": 1, "errors": list(ctx.errors),
              "settings_files": [{"scope": layer["scope"], "path": layer["path"], "error": layer["error"]}
                                 for layer in ctx.layers],
              "process": {"pid": ctx.pid, "argv_known": ctx.argv is not None,
                          "launch_env_known": ctx.launch_env is not None}}
    for key, fn in COLLECTORS:
        try:
            report[key] = fn(ctx)
        except Exception as exc:  # one broken source must not stop the audit
            report[key] = None
            report["errors"].append("%s: %s: %s" % (key, type(exc).__name__, clean(exc, 160)))
    report["findings"] = run_checks(report)
    return report


def run_checks(report):
    findings = []
    for fn in CHECKS:
        try:
            findings.extend(fn(report))
        except Exception as exc:  # one broken check must not hide the others
            report["errors"].append("%s: %s: %s" % (fn.__name__, type(exc).__name__, clean(exc, 120)))
    findings.sort(key=lambda f: SEVERITY_RANK.get(f["severity"], 9))
    return findings


def _lines(registry, report):
    out, group = [], None
    for order, fn in sorted(registry, key=lambda item: item[0]):
        try:
            block = fn(report)
        except Exception as exc:  # show the gap instead of losing the digest
            block = ["  (%s failed: %s)" % (fn.__name__, clean(exc, 100))]
        if group is not None and order // 100 != group:
            out.append("")
        group = order // 100
        out.extend(block)
    return out


def render(report, full=False):
    lines = ["session-doctor · audit data (read-only; secret values are never shown)", ""]
    lines += _lines(SECTIONS, report)
    lines += ["", "FINDINGS (high → info)"]
    for item in report.get("findings") or []:
        lines.append("  [%s] %s — %s" % (item["severity"], item["id"], item["title"]))
        lines.append("      evidence: %s" % item["evidence"])
        lines.append("      fix: %s" % item["fix"])
    if not report.get("findings"):
        lines.append("  none")
    if report.get("errors"):
        lines += ["", "DOCTOR ERRORS"] + ["  " + e for e in report["errors"]]
    if full:
        lines += ["", "DETAILS"] + _lines(DETAILS, report)
    return "\n".join(lines)


def main(argv):
    try:
        sys.stdout.reconfigure(errors="replace")
    except AttributeError:
        pass
    try:
        opts = parse_args(argv)
        report = build_report(opts, dict(os.environ))
        if opts["json"]:
            output = json.dumps(report, indent=1, ensure_ascii=False, default=str)
        else:
            output = render(report, opts["full"])
        print(scrub(output))
    except Exception as exc:  # last resort: still exit 0 so the skill keeps going
        print(scrub("session-doctor: internal error: %s: %s" % (type(exc).__name__, clean(exc, 200))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
