"""Read a Claude Code session transcript and its subagent transcripts.

The format is internal to Claude Code and changes between releases, so every
key is optional and unknown records are skipped. Field names were checked on
2.1.289. Free text is kept raw here (cut to 400 characters); collectors clean
it after the secret values are known.
"""
import glob
import os
import re
from collections import Counter

from doctor_common import clean, iso_seconds, iter_jsonl, read_json, text_of

BIG_OUTPUT_CHARS = 25000
KNOWN_TYPES = {"assistant", "user", "attachment", "system", "permission-mode", "mode", "cost-state",
               "summary", "last-prompt", "queue-operation", "file-history-snapshot"}
ERROR_KINDS = (
    ("user_rejected", ("doesn't want to proceed", "tool use was rejected")),
    ("auto_mode_denied", ("auto mode classifier",)),
    ("permission_denied", ("permission settings", "Permission to use")),
    ("interrupted", ("interrupted by user",)),
    ("blocked", ("Blocked:",)),
    ("nonzero_exit", ("Exit code",)),
    ("tool_use_error", ("<tool_use_error>",)),
)


class Transcript(object):
    """Everything the audit needs from the main thread of one session."""

    def __init__(self):
        self.path = None
        self.size = 0
        self.records = 0
        self.known = 0
        self.bad_records = 0
        self.versions = Counter()
        self.entrypoints = Counter()
        self.first_ts = None
        self.last_ts = None
        self.cwd = None
        self.env_first = None
        self.env_last = None
        self.instructions = None
        self.nested_memory = {}
        self.skill_listing = None
        self.skill_names = None
        self.skill_listing_chars = 0
        self.agent_types = set()
        self.builtin_agents = set()
        self.deferred_tools = set()
        self.mcp_status = {}
        self.mcp_instructions = set()
        self.mcp_dropped = []
        self.prompt_tools = []
        self.hook_errors = []
        self.unknown_commands = []
        self.model_identity = None
        self.turns = Counter()
        self.mode_turns = Counter()
        self.modes = Counter()
        self.plan_mode = False
        self.prompts = []
        self.prompt_count = 0
        self.slash_commands = Counter()
        self.tool_calls = Counter()
        self.tool_errors = Counter()
        self.error_samples = {}
        self.failed = Counter()
        self.interrupts = 0
        self.compactions = []
        self.peak_context = 0
        self.baseline_context = 0
        self.big_outputs = Counter()
        self.cost_usd = None
        self.slowest_turn_ms = 0
        self.skills_invoked = Counter()
        self.sidechain_turns = Counter()


def classify_error(text):
    for kind, needles in ERROR_KINDS:
        if any(n in text for n in needles):
            return kind
    return "other"


def signature(name, inp):
    """What a tool call did, raw — repeated failures are grouped by it."""
    if name == "Bash":
        return "Bash: " + " ".join(str(inp.get("command") or "").split())[:300]
    for key in ("file_path", "path", "url", "pattern", "query", "skill"):
        if inp.get(key):
            return "%s: %s" % (name, str(inp[key])[:300])
    return name


def file_stat(path, kind, content):
    content = content if isinstance(content, str) else ""
    return {"path": path, "type": kind or "?", "chars": len(content),
            "lines": content.count("\n") + 1 if content else 0}


READ_ONLY_TOOLS = ("Read", "Grep", "Glob", "LS", "NotebookRead", "WebFetch", "WebSearch", "TodoWrite", "ToolSearch")


def _int(value):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _dict(value):
    return value if isinstance(value, dict) else {}


def _list(value):
    return value if isinstance(value, list) else []


def _strings(value):
    return [str(x) for x in _list(value) if isinstance(x, (str, int, float))]


def parse_transcript(path):
    t = Transcript()
    t.path = path
    try:
        t.size = os.path.getsize(path)
    except OSError:
        return t
    state = {"seen": set(), "pending": {}, "mode": None, "changes": 0, "failed_at": {}}
    for rec in iter_jsonl(path):
        t.records += 1
        try:
            _record(t, rec, state)
        except Exception:  # one odd record must not cost the whole transcript
            t.bad_records += 1
    if t.skill_names is not None:
        t.skill_listing = {"names": list(t.skill_names), "count": len(t.skill_names), "chars": t.skill_listing_chars,
                           "without_description": [n for n, shown in t.skill_names.items() if shown is False]}
    return t


def _record(t, rec, state):
    kind = rec.get("type")
    if kind in KNOWN_TYPES:
        t.known += 1
    stamp = rec.get("timestamp")
    if isinstance(stamp, str):
        t.first_ts = t.first_ts or stamp
        t.last_ts = max(t.last_ts or stamp, stamp)
    if isinstance(rec.get("version"), str):
        t.versions[rec["version"]] += 1
    if isinstance(rec.get("entrypoint"), str):
        t.entrypoints[rec["entrypoint"]] += 1
    if isinstance(rec.get("cwd"), str) and not t.cwd:
        t.cwd = rec["cwd"]
    if rec.get("isSidechain"):
        _sidechain(t, rec, state["seen"])
        return
    if kind == "assistant":
        _assistant(t, rec, state)
    elif kind == "user":
        if isinstance(rec.get("permissionMode"), str):
            state["mode"] = rec["permissionMode"]
            t.modes[state["mode"]] += 1
        _user(t, rec, state)
    elif kind == "attachment":
        _attachment(t, _dict(rec.get("attachment")))
    elif kind == "system":
        _system(t, rec)
    elif kind == "permission-mode" and isinstance(rec.get("permissionMode"), str):
        state["mode"] = rec["permissionMode"]
    elif kind == "cost-state" and isinstance(rec.get("totalCostUSD"), (int, float)):
        t.cost_usd = rec["totalCostUSD"]
    if state["mode"] == "plan":
        t.plan_mode = True


def _sidechain(t, rec, seen):
    """Old transcripts kept subagent turns in the main file, marked isSidechain."""
    msg = _dict(rec.get("message"))
    key = str(msg.get("id") or rec.get("uuid"))
    if rec.get("type") == "assistant" and isinstance(msg.get("model"), str) and key not in seen:
        seen.add(key)
        t.sidechain_turns[(msg["model"], str(rec.get("effort") or "-"))] += 1


def _assistant(t, rec, state):
    msg = _dict(rec.get("message"))
    key = str(msg.get("id") or rec.get("uuid"))
    model = msg.get("model")
    if key not in state["seen"] and isinstance(model, str) and model != "<synthetic>":
        state["seen"].add(key)
        t.turns[(model, str(rec.get("effort") or rec.get("perTurnEffort") or "-"))] += 1
        t.mode_turns[(state["mode"] or "?", model)] += 1
        usage = _dict(msg.get("usage"))
        context = sum(_int(usage.get(k)) for k in
                      ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
        t.peak_context = max(t.peak_context, context)
        t.baseline_context = t.baseline_context or context
    for block in _list(msg.get("content")):
        if not isinstance(block, dict) or block.get("type") != "tool_use":
            continue
        name = str(block.get("name") or "?")
        inp = _dict(block.get("input"))
        t.tool_calls[name] += 1
        state["pending"][str(block.get("id"))] = (name, signature(name, inp), state["changes"])
        if name not in READ_ONLY_TOOLS:  # anything that may change files or state counts as a change
            state["changes"] += 1
        if name == "Skill":
            t.skills_invoked[str(inp.get("skill") or "?")] += 1


def _user(t, rec, state):
    content = _dict(rec.get("message")).get("content")
    has_result = False
    for block in _list(content):
        if isinstance(block, dict) and block.get("type") == "tool_result":
            has_result = True
            _tool_result(t, block, state)
    text = text_of(content)
    if not text:
        return
    if "[Request interrupted by user" in text:
        t.interrupts += 1
        return
    for match in re.finditer(r"<command-name>/?([^<]+)</command-name>", text):
        t.slash_commands[match.group(1).strip()] += 1
    origin = _dict(rec.get("origin"))
    human = origin.get("kind") in (None, "human") and not rec.get("isMeta") and not has_result
    if human and not text.lstrip().startswith("<"):
        t.prompt_count += 1
        t.prompts.append(text[:400])
        del t.prompts[:-8]


def _tool_result(t, block, state):
    name, sig, before = state["pending"].pop(str(block.get("tool_use_id")), ("?", None, None))
    content = block.get("content")
    text = content if isinstance(content, str) else text_of(content)
    if len(text) > BIG_OUTPUT_CHARS:
        t.big_outputs[name] += 1
    if not block.get("is_error"):
        return
    kind = classify_error(text)
    t.tool_errors[kind] += 1
    t.error_samples.setdefault(kind, ("%s: %s" % (name, text))[:400])
    if sig and before is not None and kind in ("nonzero_exit", "tool_use_error", "other"):
        if state["failed_at"].get(sig) == before:
            t.failed[sig] += 1  # the same failing call again, with nothing changed in between
        state["failed_at"][sig] = before + (0 if name in READ_ONLY_TOOLS else 1)


def _attachment(t, att):
    kind = att.get("type")
    if kind == "instructions":
        t.instructions = [file_stat(f.get("path"), f.get("type"), f.get("content"))
                          for f in _list(att.get("files")) if isinstance(f, dict)]
    elif kind == "nested_memory":
        inner = _dict(att.get("content"))
        path = att.get("path") or inner.get("path")
        if isinstance(path, str):
            t.nested_memory[path] = file_stat(path, inner.get("type"), inner.get("content"))
    elif kind == "skill_listing":  # the first listing is full; later ones add or re-describe skills
        content = att.get("content") if isinstance(att.get("content"), str) else ""
        if att.get("isInitial") or t.skill_names is None:
            t.skill_names = {}
        for name in _strings(att.get("names")):
            t.skill_names.setdefault(name, None)
        for line in content.splitlines():
            if line.startswith("- "):
                body = line[2:].strip()
                t.skill_names[body.split(": ", 1)[0] if ": " in body else body] = ": " in body
        t.skill_listing_chars = len(content)
    elif kind == "agent_listing_delta":
        t.agent_types.update(_strings(att.get("addedTypes")))
        t.agent_types.difference_update(_strings(att.get("removedTypes")))
        t.builtin_agents.update(_strings(att.get("builtInTypes")))
    elif kind == "deferred_tools_delta":
        t.deferred_tools.update(_strings(att.get("addedNames")))
        t.deferred_tools.difference_update(_strings(att.get("removedNames")))
        for key in ("needsAuthMcpServers", "failedMcpServers", "pendingMcpServers"):
            if key in att:
                t.mcp_status[key] = _list(att.get(key))
    elif kind == "mcp_instructions_delta":
        t.mcp_instructions.update(_strings(att.get("addedNames")))
        t.mcp_instructions.difference_update(_strings(att.get("removedNames")))
    elif kind == "mcp_dropped_tools_delta":
        t.mcp_dropped.extend(_strings(att.get("addedEntries")))
    elif kind == "unknown_command_fallback" and isinstance(att.get("commandName"), str):
        t.unknown_commands.append(att["commandName"])
    elif kind == "environment" and isinstance(att.get("snapshot"), dict):
        t.env_first = t.env_first or att["snapshot"]
        t.env_last = att["snapshot"]
    elif kind == "model" and isinstance(att.get("identity"), dict):
        t.model_identity = att["identity"]
    elif kind in ("plan_mode", "plan_mode_exit"):
        t.plan_mode = True
    elif kind == "prompt_snapshot" and isinstance(att.get("tools"), list):
        t.prompt_tools = [str(x.get("name")) for x in att["tools"] if isinstance(x, dict)]
    elif isinstance(kind, str) and "hook" in kind and "error" in kind:
        stderr = att.get("stderr")
        stderr = stderr if isinstance(stderr, str) else " ".join(_strings(stderr))
        t.hook_errors.append({"hook": str(att.get("hookName") or att.get("hookEvent") or "?"),
                              "event": att.get("hookEvent") if isinstance(att.get("hookEvent"), str) else None,
                              "stderr": stderr.strip().split("\n")[0][:400]})


def _system(t, rec):
    sub = rec.get("subtype")
    if sub == "compact_boundary":
        meta = _dict(rec.get("compactMetadata"))
        t.compactions.append((str(meta.get("trigger") or "?"), _int(meta.get("preTokens"))))
    elif sub == "turn_duration":
        t.slowest_turn_ms = max(t.slowest_turn_ms, _int(rec.get("durationMs")))
    elif sub == "stop_hook_summary":
        for err in _list(rec.get("hookErrors")):
            t.hook_errors.append({"hook": "Stop", "event": "Stop", "stderr": str(err)[:400]})


def parse_subagents(transcript_path):
    """One entry per <session>/subagents/agent-*.jsonl with its meta.json."""
    base = transcript_path[: -len(".jsonl")]
    agents = []
    for path in sorted(glob.glob(os.path.join(base, "subagents", "agent-*.jsonl"))):
        meta, _ = read_json(path[: -len(".jsonl")] + ".meta.json")
        meta = meta if isinstance(meta, dict) else {}
        used, seen, first, last = Counter(), set(), None, None
        for rec in iter_jsonl(path):
            stamp = iso_seconds(rec.get("timestamp")) if isinstance(rec.get("timestamp"), str) else None
            if stamp:
                first = first or stamp
                last = stamp
            msg = _dict(rec.get("message"))
            key = str(msg.get("id") or rec.get("uuid"))
            model = msg.get("model")
            if rec.get("type") != "assistant" or key in seen or not isinstance(model, str) or model == "<synthetic>":
                continue
            seen.add(key)
            used[(model, str(rec.get("effort") or rec.get("perTurnEffort") or "-"))] += 1
        agents.append({
            "id": os.path.basename(path)[len("agent-"): -len(".jsonl")],
            "type": str(meta.get("agentType") or "?"),
            "description": clean(meta.get("description") or "", 60),
            "requested": meta.get("model") if isinstance(meta.get("model"), str) else None,
            "used": [{"model": m, "effort": e, "turns": n} for (m, e), n in used.most_common()],
            "turns": sum(used.values()),
            "seconds": int(last - first) if first and last else 0,
            "stopped_by_user": bool(meta.get("stoppedByUser")),
        })
    return agents
