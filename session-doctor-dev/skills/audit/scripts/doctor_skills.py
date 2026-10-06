"""Skills actually invoked in the session: by the user (slash), by the model (Skill tool), by a subagent.

Reads the typed event list from doctor_events; read-only, no network. Prints skill names
and counts only. Missing keys never raise: a gap in the transcript is an empty row set.
"""
from datetime import datetime

from doctor_common import collector, section, short
from doctor_events import events as session_events

# Events the transcript may interleave between a slash command and its skill body.
TRANSPARENT_KINDS = ("listing", "invoked_skills", "unknown_command")
OUTCOME_RANK = {"ok": 0, "forked": 1, "error": 2, "unknown": 3, "after-compact": 4}


def _caller_rank(caller):
    return 0 if caller == "user" else (2 if caller == "model" else 1)


def _tool_outcome(ev):
    res = ev.get("tool_result")
    res = res if isinstance(res, dict) else {}
    if res.get("status") == "forked":
        return "forked"
    if ev.get("is_error"):
        return "error"
    if res.get("success") is True:
        return "ok"
    return "unknown"


def _listed_names(events):
    names = set()
    for ev in events:
        if ev.get("kind") == "listing":
            names.update(n for n in ev.get("names") or [] if isinstance(n, str))
    return names


def _body_follows(events, idx):
    actor = events[idx].get("actor")
    for nxt in events[idx + 1:]:
        if nxt.get("actor") != actor:
            continue
        if nxt.get("kind") in TRANSPARENT_KINDS:
            continue
        return nxt.get("kind") == "skill_body"
    return False


def build_skills(events):
    """[{name, caller, count, first_ts, outcome}, ...] from a typed event list."""
    listed = _listed_names(events)
    calls = []   # (name, caller, ts, outcome)
    for idx, ev in enumerate(events):
        kind = ev.get("kind")
        if kind == "slash":
            name = str(ev.get("command") or "").lstrip("/")
            if name and (ev.get("is_meta_body_follows") or _body_follows(events, idx) or name in listed):
                calls.append((name, "user", ev.get("ts"), "ok"))
        elif kind == "tool" and ev.get("name") == "Skill":
            inp = ev.get("input") if isinstance(ev.get("input"), dict) else {}
            name = str(inp.get("skill") or "").lstrip("/")
            if name:
                actor = ev.get("actor") or "main"
                calls.append((name, "model" if actor == "main" else actor, ev.get("ts"), _tool_outcome(ev)))
    seen = {c[0] for c in calls}
    for ev in events:
        if ev.get("kind") != "invoked_skills":
            continue
        for skill in ev.get("skills") or []:
            name = str(skill.get("name") or "") if isinstance(skill, dict) else ""
            if name and name not in seen:
                seen.add(name)
                calls.append((name, "model", ev.get("ts"), "after-compact"))

    grouped = {}
    for name, caller, ts, outcome in calls:
        row = grouped.get(name)
        if row is None:
            grouped[name] = {"name": name, "caller": caller, "count": 1, "first_ts": ts, "outcome": outcome}
            continue
        row["count"] += 1
        if ts is not None and (row["first_ts"] is None or ts < row["first_ts"]):
            row["first_ts"] = ts
        if _caller_rank(caller) < _caller_rank(row["caller"]):
            row["caller"] = caller
        if OUTCOME_RANK.get(outcome, 9) < OUTCOME_RANK.get(row["outcome"], 9):
            row["outcome"] = outcome
    return sorted(grouped.values(), key=lambda r: (r["first_ts"] is None, r["first_ts"] or 0, r["name"]))


@collector("skills_invoked_v2")
def collect_skills_invoked(ctx):
    # Collectors receive ctx only, not the report; events() is memoized on ctx (one parse per run).
    return {"skills": build_skills((session_events(ctx) or {}).get("events") or [])}


def _clock(ts):
    try:
        return datetime.fromtimestamp(ts).strftime("%H:%M:%S")
    except (TypeError, ValueError, OverflowError, OSError):
        return "?"


@section(320)
def section_skills_invoked(r):
    rows = ((r.get("skills_invoked_v2") or {}).get("skills")) or []
    if not rows:
        return ["SKILLS INVOKED none"]
    lines = ["SKILLS INVOKED %d" % len(rows)]
    for row in rows:
        lines.append("  %-34s %-10s ×%-3d %-13s %s" % (
            short(row["name"], 34), short(str(row["caller"]), 10), row["count"], row["outcome"],
            _clock(row["first_ts"])))
    return lines
