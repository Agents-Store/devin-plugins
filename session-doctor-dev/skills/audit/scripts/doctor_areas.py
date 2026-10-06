"""Audit areas. Each block registers one collector, its checks and its digest lines.

Append new blocks at the end. Collectors run in file order and get the shared
Context from session_doctor.py: ctx.t is the parsed transcript, ctx.layers the
settings files, ctx.flags the claude command-line flags, ctx.launch_env the
environment claude started with (None off Linux), ctx.plugins the enabled plugins.
"""
import glob
import os
import re
from collections import Counter

from doctor_common import (QUERY, TESTED_ON, TOKEN_VALUE, USERINFO, check, clean, collector, details, family,
                           finding, fmt_duration, fmt_k, frontmatter, glob_to_regex, iso_seconds, read_json, scrub,
                           secret_name, section, short, top, walk_strings)
from doctor_sources import (SETTINGS_PRECEDENCE, claude_json_path, effective, git, git_info, git_root,
                            is_claude_process, managed_dirs, settings_env, tracked)
from doctor_transcript import file_stat, parse_subagents


# ═══ area: session ═══════════════════════════════════════════════════════════

@collector("session")
def collect_session(ctx):
    t, live = ctx.t, ctx.live
    seconds = 0
    if t.first_ts and t.last_ts:
        start, end = iso_seconds(t.first_ts), iso_seconds(t.last_ts)
        seconds = int(end - start) if start and end else 0
    versions = [v for v, _ in t.versions.most_common()]
    if not versions and live.get("version"):
        versions = [str(live["version"])]
    match = re.search(r"/versions/(\d+\.\d+\.\d+)", (ctx.argv or [""])[0])
    if not versions and match:
        versions = [match.group(1)]
    modes = dict(t.modes)
    if not modes:
        default_mode, _ = effective(ctx.layers, lambda d: (d.get("permissions") or {}).get("defaultMode"))
        chosen = (ctx.flags.get("--permission-mode") or [default_mode])[-1]
        modes = {chosen: 0} if chosen else {}
    return {
        "id": (os.path.basename(t.path)[: -len(".jsonl")] if t.path
               else ctx.env.get("CLAUDE_CODE_SESSION_ID") or live.get("sessionId")),
        "versions": versions,
        "entrypoint": (t.entrypoints.most_common(1)[0][0] if t.entrypoints
                       else live.get("entrypoint") or ctx.env.get("CLAUDE_CODE_ENTRYPOINT")),
        "permission_modes": modes,
        "plan_mode_used": t.plan_mode,
        "seconds": seconds,
        "prompts": t.prompt_count,
        "cost_usd": t.cost_usd,
        "transcript": {"found": bool(t.path), "path": t.path, "bytes": t.size, "records": t.records,
                       "recognized": t.known, "unreadable": t.bad_records, "note": ctx.transcript_note},
    }


@collector("workspace")
def collect_workspace(ctx):
    snapshot = ctx.t.env_last if isinstance(ctx.t.env_last, dict) else {}
    current = snapshot.get("workingDirectory") if isinstance(snapshot.get("workingDirectory"), str) else ctx.start_dir
    repo = git_info(current)
    own_id = (os.path.basename(ctx.t.path)[: -len(".jsonl")] if ctx.t.path
              else ctx.env.get("CLAUDE_CODE_SESSION_ID"))
    others = []
    for path in glob.glob(os.path.join(ctx.cfg, "sessions", "*.json")):
        data, _ = read_json(path)
        if not isinstance(data, dict) or data.get("sessionId") == own_id:
            continue
        where = str(data.get("cwd") or "")
        if not is_claude_process(data.get("pid"), ctx.env):
            continue
        if repo.get("root"):  # a worktree is its own checkout, even when it lives inside this one
            same = os.path.isdir(where) and git_root(where) == repo["root"]
        else:
            same = where in (current, ctx.start_dir)
        if same:
            others.append({"session": str(data.get("sessionId") or "?")[:8],
                           "status": str(data.get("status") or "?"), "cwd": where})
    home = os.path.realpath(os.path.expanduser("~"))
    return {"start_dir": ctx.start_dir, "current_dir": current, "git": repo, "other_sessions": others,
            "too_broad": os.path.realpath(ctx.start_dir) in (home, "/"),
            "config_dir": ctx.cfg, "custom_config_dir": bool(ctx.env.get("CLAUDE_CONFIG_DIR"))}


@check
def check_core(r):
    out = []
    session = r.get("session") or {}
    tr = session.get("transcript") or {}
    if not tr.get("found"):
        out.append(finding("info", "TRANSCRIPT_MISSING", "No transcript yet — configuration-only audit",
                           tr.get("note") or "no *.jsonl for this session or directory",
                           "Normal on the first turn: take runtime lists (skills, MCP status, agents) from "
                           "your own context, or run /session-doctor-dev:audit again after one more turn"))
    elif tr.get("records") and not tr.get("recognized"):
        out.append(finding("medium", "TRANSCRIPT_FORMAT", "Transcript format not recognised",
                           "Claude Code %s; parsers checked on %s" % (
                               ", ".join(session.get("versions") or ["?"]), TESTED_ON),
                           "Update doctor_transcript.py for this Claude Code version"))
    for layer in r.get("settings_files") or []:
        if layer.get("error"):
            out.append(finding("high", "SETTINGS_INVALID", "Settings file is broken and ignored",
                               "%s: %s" % (layer["path"], layer["error"]),
                               "Fix the JSON (python3 -m json.tool <file>) and restart"))
    if r.get("errors"):
        out.append(finding("low", "DOCTOR_PARTIAL", "Some sources could not be read",
                           "; ".join(r["errors"][:2]), "Report it; the rest of the audit is valid"))
    return out


@check
def check_workspace(r):
    ws, out = r.get("workspace") or {}, []
    if ws.get("too_broad"):
        out.append(finding("medium", "CWD_TOO_BROAD", "Session started in the home or root directory",
                           ws.get("start_dir"), "Start Claude inside the project directory"))
    others = ws.get("other_sessions") or []
    if others:
        out.append(finding("medium", "SHARED_CHECKOUT", "Other live Claude sessions work in this checkout",
                           ", ".join("%s (%s)" % (o["session"], o["status"]) for o in others[:3]),
                           "Give each session its own git worktree so edits do not collide"))
    git = ws.get("git") or {}
    default = git.get("default_branch") or ("main" if git.get("branch") in ("main", "master") else None)
    if git.get("repo") and git.get("branch") == default and git.get("dirty"):
        out.append(finding("low", "DEFAULT_BRANCH_DIRTY", "Uncommitted changes on the default branch",
                           "%s: %d changed files" % (git["branch"], git["dirty"]),
                           "Work on a feature branch or worktree and commit small steps"))
    return out


@section(100)
def section_session(r):
    s, ws = r.get("session") or {}, r.get("workspace") or {}
    tr, git = s.get("transcript") or {}, ws.get("git") or {}
    cost = (" · cost ≈$%.2f" % s["cost_usd"]) if isinstance(s.get("cost_usd"), (int, float)) else ""
    lines = ["SESSION    %s · Claude Code %s · %s · mode %s · %s · prompts %d%s" % (
        (s.get("id") or "?")[:8], "/".join(s.get("versions") or ["?"]), s.get("entrypoint") or "?",
        "/".join(sorted(s.get("permission_modes") or {})) or "?", fmt_duration(s.get("seconds")),
        s.get("prompts") or 0, cost)]
    lines.append("TRANSCRIPT %s (%.1f MB, %d records%s)%s" % (
        tr.get("path") or "not found", (tr.get("bytes") or 0) / 1e6, tr.get("records") or 0,
        ", %d unreadable" % tr["unreadable"] if tr.get("unreadable") else "",
        "; " + tr["note"] if tr.get("note") else ""))
    where = ws.get("start_dir") or "?"
    if ws.get("current_dir") and ws.get("current_dir") != ws.get("start_dir"):
        where += " · now " + ws["current_dir"]
    lines.append("WORKSPACE  " + where)
    if git.get("repo"):
        lines.append("           git %s%s · %d uncommitted · default %s" % (
            git.get("branch"), " (worktree)" if git.get("worktree") else "", git.get("dirty") or 0,
            git.get("default_branch") or "?"))
    else:
        lines.append("           not a git repository")
    others = ws.get("other_sessions") or []
    lines.append("           other live sessions here: %s" % (
        ", ".join("%s %s" % (o["session"], o["status"]) for o in others) if others else "none"))
    lines.append("PROFILE    config %s%s · settings: %s" % (
        ws.get("config_dir") or "?", " (CLAUDE_CONFIG_DIR)" if ws.get("custom_config_dir") else "",
        ", ".join(sorted({f["scope"] for f in r.get("settings_files") or []})) or "none"))
    return lines


# ═══ area: models ════════════════════════════════════════════════════════════

MODEL_ENV = ("ANTHROPIC_MODEL", "ANTHROPIC_DEFAULT_MODEL", "ANTHROPIC_DEFAULT_OPUS_MODEL",
             "ANTHROPIC_DEFAULT_SONNET_MODEL", "ANTHROPIC_DEFAULT_HAIKU_MODEL", "ANTHROPIC_DEFAULT_FABLE_MODEL",
             "CLAUDE_CODE_EFFORT_LEVEL", "CLAUDE_CODE_SUBAGENT_MODEL", "CLAUDE_CODE_SUBAGENT_MODEL_FORCE",
             "MAX_THINKING_TOKENS")


def model_env(launch_env, layers, own_env):
    """Values of model and effort variables: model names and levels, never secrets."""
    from_settings = settings_env(layers)
    result = {}
    for name in MODEL_ENV:
        if launch_env is not None and name in launch_env:
            result[name] = {"value": launch_env[name], "source": "launch env"}
        elif name in from_settings:
            result[name] = {"value": from_settings[name][0], "source": "settings:" + from_settings[name][1]}
        elif launch_env is None and name in own_env:
            result[name] = {"value": own_env[name], "source": "env"}
    return result


def agent_files(ctx):
    found = []
    for scope, base in (("project", os.path.join(ctx.start_dir, ".claude", "agents")),
                        ("user", os.path.join(ctx.cfg, "agents"))):
        for path in sorted(glob.glob(os.path.join(base, "*.md"))):
            fields = frontmatter(path)
            found.append({"scope": scope, "name": fields.get("name") or os.path.basename(path)[:-3],
                          "model": fields.get("model") or "inherit", "effort": fields.get("effort")})
    return found


@collector("models")
def collect_models(ctx):
    t, flags = ctx.t, ctx.flags
    menv = model_env(ctx.launch_env, ctx.layers, ctx.env)
    main = [{"model": m, "effort": e, "turns": n} for (m, e), n in t.turns.most_common()]
    settings_model, model_scope = effective(ctx.layers, lambda d: d.get("model"))
    current = main[0]["model"] if main else (t.model_identity or {}).get("modelId")
    asked = (current or (flags.get("--model") or [None])[-1]
             or (menv.get("ANTHROPIC_MODEL") or {}).get("value") or settings_model)
    fam = family("sonnet" if asked == "opusplan" else asked)
    if t.slash_commands.get("model"):
        model_source = "/model in session"
    elif flags.get("--model"):
        model_source = "--model flag (%s)" % flags["--model"][-1]
    elif "ANTHROPIC_MODEL" in menv:
        model_source = "ANTHROPIC_MODEL (%s)" % menv["ANTHROPIC_MODEL"]["source"]
    elif settings_model:
        model_source = "settings model=%s (%s)" % (settings_model, model_scope)
    elif "ANTHROPIC_DEFAULT_MODEL" in menv:
        model_source = "ANTHROPIC_DEFAULT_MODEL"
    else:
        model_source = "built-in default"

    def per_model(d):
        block = d.get("modelSettings") or {}
        return (block.get(fam) or block.get(asked) or {}).get("effortLevel")

    level, level_scope = effective(ctx.layers, per_model)
    version = re.search(r"opus-(\d+)-(\d+)", str(asked or ""))
    new_opus = fam == "opus" and (not version or (int(version.group(1)), int(version.group(2))) >= (5, 5))
    top_scopes = ("managed", "local", "project") if new_opus else SETTINGS_PRECEDENCE
    top_level, top_scope = effective(ctx.layers, lambda d: d.get("effortLevel"), top_scopes)
    cap, cap_scope = effective(ctx.layers, lambda d: ((d.get("modelSettings") or {}).get(fam) or {}).get("maxEffortLevel"))
    if "CLAUDE_CODE_EFFORT_LEVEL" in menv:
        effort_source = "CLAUDE_CODE_EFFORT_LEVEL (%s)" % menv["CLAUDE_CODE_EFFORT_LEVEL"]["source"]
    elif t.slash_commands.get("effort"):
        effort_source = "/effort in session"
    elif flags.get("--effort"):
        effort_source = "--effort flag (%s)" % flags["--effort"][-1]
    elif level:
        effort_source = "settings modelSettings.%s.effortLevel=%s (%s)" % (fam, level, level_scope)
    elif top_level:
        effort_source = "settings effortLevel=%s (%s)" % (top_level, top_scope)
    else:
        effort_source = "model default"
    model_settings = {layer["scope"]: layer["data"]["modelSettings"] for layer in ctx.layers
                      if isinstance(layer["data"].get("modelSettings"), dict)}
    subagents = parse_subagents(ctx.transcript_path) if ctx.transcript_path else []
    if not subagents and t.sidechain_turns:
        subagents = [{"id": "legacy", "type": "?", "description": "sidechain records in the main transcript",
                      "requested": None, "turns": sum(t.sidechain_turns.values()), "seconds": 0,
                      "stopped_by_user": False,
                      "used": [{"model": m, "effort": e, "turns": n} for (m, e), n in t.sidechain_turns.items()]}]
    return {
        "main": main, "current": current or asked, "identity": t.model_identity,
        "effort_now": ctx.env.get("CLAUDE_EFFORT"),
        "model_source": model_source, "effort_source": effort_source,
        "effort_cap": {"level": cap, "scope": cap_scope} if cap else None,
        "settings_model": {"value": settings_model, "scope": model_scope} if settings_model else None,
        "model_settings": model_settings,
        "flags": {k: flags[k][-1] for k in ("--model", "--effort", "--permission-mode", "--fallback-model")
                  if flags.get(k)},
        "env": menv,
        "by_mode": [{"mode": md, "model": m, "turns": n} for (md, m), n in t.mode_turns.most_common()],
        "subagents": subagents,
        "custom_agents": agent_files(ctx),
    }


@check
def check_models(r):
    models, out = r.get("models") or {}, []
    wanted = models.get("settings_model") or {}
    if wanted and not str(models.get("model_source") or "").startswith("settings"):
        out.append(finding("info", "MODEL_OVERRIDDEN", "Settings model is not the one running",
                           "settings: model=%s (%s); running %s via %s" % (
                               wanted.get("value"), wanted.get("scope"), models.get("current"),
                               models.get("model_source")),
                           "Expected if you chose it; otherwise drop the flag or env, or run /model"))
    main = models.get("main") or []
    total = sum(m["turns"] for m in main)
    heavy = sum(m["turns"] for m in main if m["effort"] in ("max", "xhigh"))
    if total >= 5 and heavy * 5 >= total * 4:
        out.append(finding("low", "EFFORT_ALWAYS_MAX", "Almost every turn runs at max/xhigh effort",
                           "%d of %d main turns" % (heavy, total),
                           "Keep a lower default (/effort high or medium) and raise it for hard steps "
                           "(/effort max, or ultrathink in one prompt)"))
    force = ((models.get("env") or {}).get("CLAUDE_CODE_SUBAGENT_MODEL_FORCE") or {}).get("value")
    ignored = []
    for agent in models.get("subagents") or []:
        asked, used = family(agent.get("requested")), {family(u["model"]) for u in agent.get("used") or []}
        if asked and used and asked not in used:
            ignored.append("%s asked %s → ran %s" % (agent["type"], agent["requested"],
                                                     "/".join(sorted(u["model"] for u in agent["used"]))))
    if ignored:
        out.append(finding("low", "SUBAGENT_MODEL_IGNORED", "Requested subagent model was not used",
                           "; ".join(ignored[:3]) + (" (CLAUDE_CODE_SUBAGENT_MODEL_FORCE=%s)" % force if force else ""),
                           "Decide which wins: drop FORCE so per-call and frontmatter models apply, "
                           "or stop requesting models, and make your rules say the same"))
    stopped = [a for a in models.get("subagents") or [] if a.get("stopped_by_user")]
    if stopped:
        out.append(finding("low", "SUBAGENT_STOPPED", "Subagents stopped by hand",
                           ", ".join(a["description"] or a["type"] for a in stopped[:3]),
                           "Brief subagents with a narrower task and a clear done-condition"))
    return out


def _usage(used):
    return ", ".join("%s @ %s ×%d" % (u["model"], u["effort"], u["turns"]) for u in used) or "no turns"


@section(200)
def section_models(r):
    m = r.get("models") or {}
    lines = ["MODELS", "  main       %s" % _usage(m.get("main") or [])]
    lines.append("             model ← %s · effort ← %s%s%s" % (
        m.get("model_source") or "?", m.get("effort_source") or "?",
        " · effort now %s (CLAUDE_EFFORT)" % m["effort_now"] if m.get("effort_now") else "",
        " · cap %s (%s)" % (m["effort_cap"]["level"], m["effort_cap"]["scope"]) if m.get("effort_cap") else ""))
    configured = []
    if m.get("settings_model"):
        configured.append("model=%s (%s)" % (m["settings_model"]["value"], m["settings_model"]["scope"]))
    for scope, block in sorted((m.get("model_settings") or {}).items()):
        for fam, values in sorted(block.items()):
            if isinstance(values, dict):
                configured.append("%s %s (%s)" % (fam, " ".join("%s=%s" % kv for kv in sorted(values.items())), scope))
    lines.append("  settings   %s" % (" · ".join(configured) or "no model settings"))
    if m.get("env"):
        lines.append("  env        %s" % " · ".join("%s=%s (%s)" % (k, v["value"], v["source"])
                                                   for k, v in sorted(m["env"].items())))
    subs = m.get("subagents") or []
    groups = Counter()
    for a in subs:
        groups[(a["type"], str(a.get("requested") or "none"),
                ", ".join("%s @ %s" % (u["model"], u["effort"]) for u in a.get("used") or []) or "no turns")] += 1
    lines.append("  subagents  %d run%s" % (len(subs), "" if subs else " in this session"))
    for (kind, asked, used), n in groups.most_common(6):
        lines.append("             %s ×%d → %s (asked: %s)" % (kind, n, used, asked))
    custom = m.get("custom_agents") or []
    if custom:
        lines.append("  custom     %s" % ", ".join("%s (%s, model %s)" % (a["name"], a["scope"], a["model"])
                                               for a in custom[:6]))
    return lines


@details(200)
def details_models(r):
    return ["  subagent %s %-18s asked %-8s → %s · %d turns · %s%s · %s" % (
        a["id"][:8], a["type"], a.get("requested") or "none", _usage(a.get("used") or []), a.get("turns") or 0,
        fmt_duration(a.get("seconds")), " · stopped" if a.get("stopped_by_user") else "", a.get("description") or "")
        for a in (r.get("models") or {}).get("subagents") or []]


# ═══ area: instructions ══════════════════════════════════════════════════════

@collector("instructions")
def collect_instructions(ctx):
    t = ctx.t
    if t.instructions is not None:
        loaded, source = list(t.instructions), "transcript"
    else:
        loaded, source = [], "filesystem"
    known = {f["path"] for f in loaded}
    loaded.extend(v for k, v in sorted(t.nested_memory.items()) if k not in known)
    candidates = [os.path.join(managed_dirs(ctx.env)[0], "CLAUDE.md"), os.path.join(ctx.cfg, "CLAUDE.md")]
    directory, chain = os.path.abspath(ctx.start_dir), []
    while True:
        chain.append(directory)
        parent = os.path.dirname(directory)
        if parent == directory:
            break
        directory = parent
    for directory in reversed(chain):
        for name in ("CLAUDE.md", os.path.join(".claude", "CLAUDE.md"), "CLAUDE.local.md"):
            candidates.append(os.path.join(directory, name))
    loaded_real = {os.path.realpath(f["path"]) for f in loaded if f.get("path")}
    excludes = [(str(p), layer["scope"]) for layer in ctx.layers for p in layer["data"].get("claudeMdExcludes") or []]
    missing = []
    for path in candidates:
        if not os.path.isfile(path):
            continue
        if source == "filesystem":
            with open(path, encoding="utf-8", errors="replace") as fh:
                loaded.append(file_stat(path, "?", fh.read()))
            continue
        if os.path.realpath(path) in loaded_real:
            continue
        hit = next(((p, s) for p, s in excludes if glob_to_regex(p).match(path)), None)
        missing.append({"path": path, "excluded_by": hit[0] if hit else None, "exclude_scope": hit[1] if hit else None})
    return {"source": source, "files": loaded, "not_loaded": missing,
            "total_chars": sum(f.get("chars") or 0 for f in loaded)}


@check
def check_instructions(r):
    ins, out = r.get("instructions") or {}, []
    loaded_paths = {f.get("path") for f in ins.get("files") or []}
    for item in ins.get("not_loaded") or []:
        why = ("matches claudeMdExcludes \"%s\" (%s)" % (item["excluded_by"], item["exclude_scope"])
               if item.get("excluded_by") else "not in the loaded set")
        if os.path.join(os.path.dirname(item["path"]), "AGENTS.md") in loaded_paths:
            why += "; AGENTS.md from the same directory was loaded instead"
        out.append(finding("medium", "MEMORY_NOT_LOADED", "A CLAUDE.md on disk is not loaded",
                           "%s — %s" % (item["path"], why),
                           "Narrow the claudeMdExcludes glob, or move the file where Claude Code reads it"))
    long_files = [f for f in ins.get("files") or [] if (f.get("lines") or 0) > 200]
    if long_files:
        out.append(finding("low", "MEMORY_LONG", "Instruction files over the 200-line guideline",
                           ", ".join("%s (%d lines)" % (os.path.basename(f["path"] or "?"), f["lines"])
                                     for f in long_files[:3]),
                           "Trim them: move procedures into skills and path-scoped rules"))
    return out


@section(300)
def section_instructions(r):
    ins = r.get("instructions") or {}
    files = ins.get("files") or []
    biggest = max(files, key=lambda f: f.get("lines") or 0) if files else None
    lines = ["INSTRUCTIONS %d files · %s chars ≈ %s tokens%s%s" % (
        len(files), fmt_k(ins.get("total_chars")), fmt_k((ins.get("total_chars") or 0) // 4),
        " · biggest %s %d lines" % (os.path.basename(biggest["path"] or "?"), biggest["lines"]) if biggest else "",
        " (from the filesystem: the transcript has no list)" if ins.get("source") == "filesystem" else "")]
    for item in ins.get("not_loaded") or []:
        lines.append("             not loaded: %s%s" % (item["path"], " — matches claudeMdExcludes \"%s\" (%s)" % (
            item["excluded_by"], item["exclude_scope"]) if item.get("excluded_by") else ""))
    return lines


@details(300)
def details_instructions(r):
    return ["  instruction %-8s %4d lines %7d chars  %s" % (f["type"], f["lines"], f["chars"], f["path"])
            for f in (r.get("instructions") or {}).get("files") or []]


# ═══ area: skills ════════════════════════════════════════════════════════════

@collector("skills")
def collect_skills(ctx):
    listing = ctx.t.skill_listing or {}
    names = listing.get("names") or []
    dirs, directory = [], os.path.abspath(ctx.start_dir)
    stop = os.path.abspath(ctx.git_root) if ctx.git_root else directory
    while True:
        dirs.append(directory)
        if directory == stop or os.path.dirname(directory) == directory:
            break
        directory = os.path.dirname(directory)
    synced = {os.path.basename(os.path.dirname(p))
              for p in glob.glob(os.path.join(ctx.cfg, "skills", "synced", "*", "*", "SKILL.md"))}
    by_source, plugins, detail = Counter(), Counter(), {}

    def has(base, name):
        return (os.path.isfile(os.path.join(base, ".claude", "skills", name, "SKILL.md"))
                or os.path.isfile(os.path.join(base, ".claude", "commands", name + ".md")))

    for name in names:
        if ":" in name:
            space, bare = name.split(":", 1)
            if "/" in space:
                source = "nested"
            elif space == "anthropic-skills" or bare in synced:
                source = "claude.ai"
            else:
                source = "plugin"
                plugins[space] += 1
        elif any(has(d, name) for d in dirs):
            source = "project"
        elif (os.path.isfile(os.path.join(ctx.cfg, "skills", name, "SKILL.md"))
              or os.path.isfile(os.path.join(ctx.cfg, "commands", name + ".md"))):
            source = "user"
        else:
            source = "built-in"
        by_source[source] += 1
        detail.setdefault(source, []).append(name)
    return {"listed": len(names), "by_source": dict(by_source), "plugins": dict(plugins.most_common()),
            "without_description": listing.get("without_description") or [],
            "listing_chars": listing.get("chars"), "names": detail,
            "invoked": dict(ctx.t.skills_invoked), "slash_commands": dict(ctx.t.slash_commands),
            "unknown_commands": [short(scrub(c), 80) for c in ctx.t.unknown_commands]}


@collector("agents")
def collect_agents(ctx):
    return {"types": sorted(ctx.t.agent_types), "built_in": sorted(ctx.t.builtin_agents),
            "custom": agent_files(ctx)}


@check
def check_skills(r):
    sk, out = r.get("skills") or {}, []
    dropped = sk.get("without_description") or []
    if dropped:
        out.append(finding("medium", "SKILLS_DESC_DROPPED", "Skills listed without a description",
                           "%d of %d skills; e.g. %s" % (len(dropped), sk.get("listed") or 0, ", ".join(dropped[:3])),
                           "Claude cannot pick those by description: disable plugins this project does not use, "
                           "mark manual-only skills `disable-model-invocation: true`, or raise skillListingBudgetFraction"))
    for name in sorted(set(sk.get("unknown_commands") or [])):
        out.append(finding("medium", "UNKNOWN_COMMAND", "Unknown slash command typed", "/" + name,
                           "Install the plugin that provides it (/plugin) or use an existing command"))
    return out


@section(310)
def section_skills(r):
    sk, ag = r.get("skills") or {}, r.get("agents") or {}
    parts = []
    for source, count in sorted((sk.get("by_source") or {}).items(), key=lambda kv: -kv[1]):
        extra = " (%s)" % top(sk["plugins"], 4) if source == "plugin" and sk.get("plugins") else ""
        parts.append("%s %d%s" % (source, count, extra))
    lines = ["SKILLS       %d listed · %s · %d without description" % (
        sk.get("listed") or 0, " · ".join(parts) or "none", len(sk.get("without_description") or []))]
    used = dict(sk.get("invoked") or {})
    for name, count in (sk.get("slash_commands") or {}).items():
        used[name] = used.get(name, 0) + count
    unknown = set(sk.get("unknown_commands") or [])
    lines.append("             used: %s" % (", ".join("%s%s" % (k, " (unknown)" if k in unknown else "")
                                                     for k in sorted(set(used) | unknown)) or "none"))
    lines.append("AGENTS       %d types (%d built-in)" % (len(ag.get("types") or []), len(ag.get("built_in") or [])))
    return lines


@details(310)
def details_skills(r):
    sk = r.get("skills") or {}
    lines = ["  skills %-9s %s" % (source, ", ".join(names)) for source, names in sorted((sk.get("names") or {}).items())]
    if sk.get("without_description"):
        lines.append("  skills w/o description: %s" % ", ".join(sk["without_description"]))
    return lines


# ═══ area: plugins and hooks ═════════════════════════════════════════════════

@collector("plugins")
def collect_plugins(ctx):
    return ctx.plugins


@collector("hooks")
def collect_hooks(ctx):
    configured = []

    def take(source, hooks):
        if not isinstance(hooks, dict):
            return
        for event, groups in hooks.items():
            for group in groups if isinstance(groups, list) else []:
                for hook in (group.get("hooks") or []) if isinstance(group, dict) else []:
                    kind = hook.get("type") if isinstance(hook, dict) else None
                    configured.append({"source": source, "event": event, "type": kind,
                                       "invalid": event in ("SessionStart", "Setup")
                                       and kind in ("prompt", "agent", "http")})

    for layer in ctx.layers:
        take(layer["scope"], layer["data"].get("hooks"))
    for plugin in ctx.plugins:
        if plugin["enabled"] and plugin["path"]:
            data, _ = read_json(os.path.join(plugin["path"], "hooks", "hooks.json"))
            if isinstance(data, dict):
                take("plugin:" + plugin["name"], data.get("hooks", data))
    errors = [dict(e, hook=short(scrub(str(e.get("hook") or "?")), 60), stderr=clean(e.get("stderr") or "", 140))
              for e in ctx.t.hook_errors]
    return {"configured": configured, "errors": errors}


@check
def check_plugins(r):
    missing = [p["id"] for p in r.get("plugins") or [] if p.get("enabled") and not p.get("installed")]
    if not missing:
        return []
    return [finding("medium", "PLUGIN_NOT_INSTALLED", "Enabled plugins are not installed in this profile",
                    "%d: %s" % (len(missing), ", ".join(missing[:4]) + (" …" if len(missing) > 4 else "")),
                    "Their skills, agents and MCP servers are missing: /plugin install <id>, "
                    "or remove them from enabledPlugins")]


@check
def check_hooks(r):
    hooks, out = r.get("hooks") or {}, []
    invalid = [h for h in hooks.get("configured") or [] if h.get("invalid")]
    for hook in invalid[:3]:
        out.append(finding("medium", "HOOK_INVALID", "Hook type not supported on %s" % hook["event"],
                           "%s defines a %s hook on %s" % (hook["source"], hook["type"], hook["event"]),
                           "Only command and mcp_tool hooks run on SessionStart/Setup: fix or disable it"))
    invalid_events, seen = {h["event"] for h in invalid}, set()
    for err in hooks.get("errors") or []:
        if err.get("event") in invalid_events and "not supported" in (err.get("stderr") or ""):
            continue
        key = (err.get("hook"), err.get("stderr"))
        if key in seen:
            continue
        seen.add(key)
        out.append(finding("medium", "HOOK_ERROR", "Hook %s failed" % err.get("hook"), err.get("stderr") or "?",
                           "Fix the hook command or remove it (/hooks shows where it is defined)"))
        if len(seen) >= 3:
            break
    return out


@section(330)
def section_plugins_hooks(r):
    on = [p for p in r.get("plugins") or [] if p.get("enabled")]
    hooks = r.get("hooks") or {}
    configured = hooks.get("configured") or []
    by_source = Counter(h["source"] for h in configured)
    return ["PLUGINS      %d enabled (%s) · %d not installed" % (
                len(on), top(dict(Counter(p["scope"] for p in on)), 4) or "none",
                len([p for p in on if not p.get("installed")])),
            "HOOKS        %d configured%s · %d invalid · %d runtime errors" % (
                len(configured), " (%s)" % top(dict(by_source), 4) if by_source else "",
                len([h for h in configured if h.get("invalid")]), len(hooks.get("errors") or []))]


@details(330)
def details_plugins_hooks(r):
    lines = ["  plugin %-45s %s %s%s" % (p["id"], p["scope"], p.get("version") or "-",
                                         "" if p.get("installed") else " NOT INSTALLED")
             for p in r.get("plugins") or [] if p.get("enabled")]
    lines += ["  hook %-22s %-16s %s%s" % (h["source"], h["event"], h["type"], " INVALID" if h["invalid"] else "")
              for h in (r.get("hooks") or {}).get("configured") or []]
    return lines


# ═══ area: mcp ═══════════════════════════════════════════════════════════════

VAR_REF = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(:-[^}]*)?\}")


def mcp_key(name):
    """A server's display name as it appears inside tool names (mcp__<key>__tool)."""
    return re.sub(r"[^A-Za-z0-9_-]", "_", str(name))


def mcp_servers_from(mapping, scope, source, ctx, from_settings):
    servers = []
    for name, spec in (mapping.items() if isinstance(mapping, dict) else []):
        if not isinstance(spec, dict):
            continue
        refs, secrets = [], set()
        for key, value in walk_strings(spec):
            for match in VAR_REF.finditer(value):
                var = match.group(1)
                if match.group(2) is not None:
                    state = "default"
                elif ctx.launch_env is not None:
                    state = ("launch-env" if var in ctx.launch_env
                             else "settings-env-only" if var in from_settings else "missing")
                else:
                    state = "unverified" if var in ctx.env else "missing"
                refs.append({"var": var, "field": key, "state": state})
            is_url = re.match(r"^[a-z][a-z0-9+.\-]*://", value, re.I)
            if "${" not in value and (any(rx.search(value) for rx in TOKEN_VALUE) or USERINFO.search(value)
                                      or QUERY.search(value) or (secret_name(key) and len(value) >= 12 and not is_url)):
                secrets.add(key)
        servers.append({"name": name, "scope": scope, "source": source,
                        "transport": spec.get("type") or ("stdio" if spec.get("command") else "?"),
                        "vars": refs, "literal_secrets": sorted(secrets)})
    return servers


@collector("mcp")
def collect_mcp(ctx):
    t, from_settings, configured = ctx.t, settings_env(ctx.layers), []
    cj_path = claude_json_path(ctx.env, ctx.cfg)
    cj, _ = read_json(cj_path)
    cj = cj if isinstance(cj, dict) else {}
    configured += mcp_servers_from(cj.get("mcpServers"), "user", cj_path, ctx, from_settings)
    projects = cj.get("projects") if isinstance(cj.get("projects"), dict) else {}
    for key in sorted({ctx.start_dir, ctx.git_root} - {None}):
        entry = projects.get(key) if isinstance(projects.get(key), dict) else {}
        configured += mcp_servers_from(entry.get("mcpServers"), "local", cj_path, ctx, from_settings)
    seen_files = set()
    for base in (ctx.start_dir, ctx.git_root):
        path = os.path.join(base, ".mcp.json") if base else ""
        if not os.path.isfile(path) or os.path.realpath(path) in seen_files:
            continue
        seen_files.add(os.path.realpath(path))
        data, _ = read_json(path)
        for server in mcp_servers_from((data or {}).get("mcpServers") if isinstance(data, dict) else None,
                                       "project", path, ctx, from_settings):
            server["tracked"] = tracked(path)
            configured.append(server)
    for path in ctx.flags.get("--mcp-config") or []:
        data, _ = read_json(path)
        if isinstance(data, dict):
            configured += mcp_servers_from(data.get("mcpServers"), "flag", path, ctx, from_settings)
    for plugin in ctx.plugins:
        if not (plugin["enabled"] and plugin["path"]):
            continue
        data, _ = read_json(os.path.join(plugin["path"], ".mcp.json"))
        mapping = data.get("mcpServers", data) if isinstance(data, dict) else None
        for server in mcp_servers_from(mapping, "plugin", plugin["id"], ctx, from_settings):
            server["name"] = "plugin:%s:%s" % (plugin["name"], server["name"])
            configured.append(server)
    entry = projects.get(ctx.start_dir) if isinstance(projects.get(ctx.start_dir), dict) else {}
    enabled, disabled, enable_all = set(), set(), False  # approvals from every file add up
    for data in [layer["data"] for layer in ctx.layers] + [entry]:
        enabled.update(x for x in data.get("enabledMcpjsonServers") or [] if isinstance(x, str))
        disabled.update(x for x in data.get("disabledMcpjsonServers") or [] if isinstance(x, str))
        enable_all = enable_all or data.get("enableAllProjectMcpServers") is True
    entry = ((t.entrypoints.most_common(1)[0][0] if t.entrypoints else None) or ctx.live.get("entrypoint")
             or ctx.env.get("CLAUDE_CODE_ENTRYPOINT") or "")
    headless = bool(ctx.flags.get("--print") or ctx.flags.get("-p")) or str(entry).startswith("sdk")
    for server in configured:
        server["loads"] = True
        if server["scope"] == "project":
            server["approval"] = ("disabled" if server["name"] in disabled
                                  else "approved" if enable_all or server["name"] in enabled
                                  else "not approved")
            server["loads"] = server["approval"] == "approved" or (headless and server["approval"] != "disabled")
    tools = Counter()
    for name in set(t.deferred_tools) | set(t.prompt_tools):
        parts = str(name).split("__")
        if len(parts) >= 3 and parts[0] == "mcp":
            tools[parts[1]] += 1
    failed = []
    for item in t.mcp_status.get("failedMcpServers") or []:
        name = short(scrub(str(item.get("name"))), 80) if isinstance(item, dict) else None
        if name and name not in {f["name"] for f in failed}:  # names stay raw: they are keys, not prose
            failed.append({"name": name, "code": short(scrub(str(item.get("errorCode") or "")), 40),
                           "error": clean(item.get("error") or "", 140)})
    needs_auth = [short(scrub(str(n)), 80) for n in t.mcp_status.get("needsAuthMcpServers") or []]
    pending = [short(scrub(str(n)), 80) for n in t.mcp_status.get("pendingMcpServers") or []]
    down = {mcp_key(n) for n in needs_auth + pending + [f["name"] for f in failed]}
    return {"connected": sorted((set(tools) | {mcp_key(n) for n in t.mcp_instructions}) - down),
            "tools_by_server": dict(tools.most_common()), "tools_total": sum(tools.values()),
            "tools_upfront": len([n for n in t.prompt_tools if str(n).startswith("mcp__")]),
            "failed": failed, "needs_auth": needs_auth, "pending": pending,
            "dropped_tools": [clean(e, 160) for e in t.mcp_dropped], "configured": configured}


@check
def check_mcp(r):
    mcp, out = r.get("mcp") or {}, []
    by_name = {}
    for server in mcp.get("configured") or []:
        by_name.setdefault(server["name"], server)
    for failed in (mcp.get("failed") or [])[:4]:
        bad = [v for v in (by_name.get(failed["name"]) or {}).get("vars") or []
               if v["state"] in ("settings-env-only", "missing")]
        evidence = "%s: %s" % (failed.get("code") or "error", failed.get("error") or "?")
        if bad:
            where = ("defined only in settings env, not in Claude's launch environment"
                     if bad[0]["state"] == "settings-env-only" else "not defined anywhere")
            evidence += "; %s uses ${%s} — %s" % (bad[0]["field"] or "config", bad[0]["var"], where)
            fix = ("Export %s in the environment that launches Claude (or give the server a literal value "
                   "with `claude mcp add -s local`), then restart" % bad[0]["var"])
        elif failed["name"].startswith("claude.ai "):
            fix = "Check the connector at claude.ai → Settings → Connectors, or disconnect it"
        else:
            fix = "Run `claude mcp list` or /mcp to see the error and fix the server config"
        out.append(finding("high", "MCP_FAILED", "MCP server %s failed to start" % failed["name"], evidence, fix))
    reported = {f["name"] for f in mcp.get("failed") or []}
    for server in mcp.get("configured") or []:
        bad = [v for v in server["vars"] if v["state"] in ("settings-env-only", "missing")]
        if bad and server.get("loads", True) and server["name"] not in reported:
            reported.add(server["name"])
            out.append(finding("low" if server["scope"] == "plugin" else "medium", "MCP_VAR_UNSET",
                               "MCP server %s gets unexpanded variables" % server["name"],
                               ", ".join("${%s} (%s)" % (v["var"], v["state"]) for v in bad[:3])
                               + " — the server starts without them (expect auth or URL errors)",
                               "Export them in the environment that launches Claude, or use ${VAR:-default}"))
        if server.get("literal_secrets") and server.get("tracked"):
            out.append(finding("high", "MCP_SECRET_COMMITTED", "Literal secret in a git-tracked .mcp.json",
                               "server %s, keys: %s" % (server["name"], ", ".join(server["literal_secrets"])),
                               "Replace the value with ${VAR}, keep it in local env, rotate the key"))
    needs = mcp.get("needs_auth") or []
    if needs:
        out.append(finding("medium" if len(needs) >= 5 else "low", "MCP_NEEDS_AUTH",
                           "MCP servers waiting for authentication",
                           "%d: %s" % (len(needs), ", ".join(needs[:4]) + (" …" if len(needs) > 4 else "")),
                           "Authenticate the ones you need in /mcp; disconnect the rest "
                           "(claude.ai connectors: claude.ai → Settings → Connectors)"))
    if mcp.get("dropped_tools"):
        out.append(finding("low", "MCP_TOOLS_DROPPED", "MCP tools dropped for invalid schemas",
                           "%d, e.g. %s" % (len(mcp["dropped_tools"]), short(mcp["dropped_tools"][0], 100)),
                           "A server bug: update that server; nothing to change in the session"))
    if (mcp.get("tools_upfront") or 0) > 40:
        out.append(finding("low", "MCP_TOOLS_UPFRONT", "Many MCP tools loaded into every request",
                           "%d tool definitions up front" % mcp["tools_upfront"],
                           "Keep tool search on (ENABLE_TOOL_SEARCH unset or auto) and disable unused servers"))
    return out


@section(350)
def section_mcp(r):
    mcp = r.get("mcp") or {}
    lines = ["MCP          connected %d · failed %d · needs auth %d · pending %d · tools %d (%d up front) · dropped %d" % (
        len(mcp.get("connected") or []), len(mcp.get("failed") or []), len(mcp.get("needs_auth") or []),
        len(mcp.get("pending") or []), mcp.get("tools_total") or 0, mcp.get("tools_upfront") or 0,
        len(mcp.get("dropped_tools") or []))]
    scopes = Counter(server["scope"] for server in mcp.get("configured") or [])
    if scopes:
        lines.append("             configured: %s" % top(dict(scopes), 6))
    if mcp.get("failed"):
        lines.append("             failed: %s" % ", ".join(f["name"] for f in mcp["failed"]))
    return lines


@details(350)
def details_mcp(r):
    mcp = r.get("mcp") or {}
    lines = ["  mcp ok      %-40s %d tools" % (n, (mcp.get("tools_by_server") or {}).get(n, 0))
             for n in mcp.get("connected") or []]
    for server in mcp.get("configured") or []:
        lines.append("  mcp config  %-40s %s %s%s%s" % (
            server["name"], server["scope"], server["transport"],
            " " + server["approval"] if server.get("approval") else "",
            " vars: " + ", ".join("%s=%s" % (v["var"], v["state"]) for v in server["vars"]) if server["vars"] else ""))
    lines += ["  mcp auth    %s" % n for n in mcp.get("needs_auth") or []]
    return lines


# ═══ area: env ═══════════════════════════════════════════════════════════════

AUTH_ENV = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_BASE_URL",
            "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY")


@collector("env")
def collect_env(ctx):
    by_scope = {}
    for layer in ctx.layers:
        if isinstance(layer["data"].get("env"), dict):
            by_scope.setdefault(layer["scope"], set()).update(str(n) for n in layer["data"]["env"])
    from_settings = settings_env(ctx.layers)
    auth = {}
    for name in AUTH_ENV:
        where = (["launch env"] if ctx.launch_env and ctx.launch_env.get(name) else []) + \
                (["settings:" + from_settings[name][1]] if from_settings.get(name, ("", ""))[0] else [])
        if where:
            auth[name] = where
    _, helper_scope = effective(ctx.layers, lambda d: d.get("apiKeyHelper"))
    committed = []
    for layer in ctx.layers:
        if layer["scope"] == "project" and tracked(layer["path"]):
            leaked = sorted(n for n in (layer["data"].get("env") or {}) if secret_name(str(n)))
            if leaked:
                committed.append({"file": layer["path"], "names": leaked})
        if layer["scope"] == "local" and tracked(layer["path"]):
            committed.append({"file": layer["path"], "names": ["<the whole file is tracked by git>"]})
    code, out = git(ctx.start_dir, "ls-files", "--", ".env", ".env.*", "*/.env", "*/.env.*")
    for path in out.splitlines() if code == 0 else []:
        if not path.endswith((".example", ".sample", ".template", ".dist")):
            committed.append({"file": os.path.join(ctx.start_dir, path), "names": ["<env file tracked by git>"]})
    return {
        "settings": {scope: {"count": len(names), "secret_like": len([n for n in names if secret_name(n)]),
                             "names": sorted(names)} for scope, names in by_scope.items()},
        "launch_env_available": ctx.launch_env is not None,
        "launch_env_count": len(ctx.launch_env or {}),
        "launch_secret_like": sorted(n for n in (ctx.launch_env or {}) if secret_name(n)),
        "auth": auth, "api_key_helper": helper_scope,
        "subscription_login": os.path.isfile(os.path.join(ctx.cfg, ".credentials.json")),
        "committed": committed,
    }


@check
def check_env(r):
    env, out = r.get("env") or {}, []
    if "ANTHROPIC_API_KEY" in (env.get("auth") or {}):
        out.append(finding("high" if env.get("subscription_login") else "medium", "API_KEY_BILLING",
                           "ANTHROPIC_API_KEY is set",
                           "set in %s; it is used instead of a subscription login even when logged in"
                           % ", ".join(env["auth"]["ANTHROPIC_API_KEY"]),
                           "unset ANTHROPIC_API_KEY unless you mean to bill the API"))
    for item in env.get("committed") or []:
        out.append(finding("high", "SECRET_COMMITTED", "Secrets in a git-tracked file",
                           "%s: %s" % (item["file"], ", ".join(item["names"][:5])),
                           "Move them to .claude/settings.local.json or a secret manager, untrack the file, "
                           "rotate the keys"))
    return out


@section(360)
def section_env(r):
    env = r.get("env") or {}
    settings = env.get("settings") or {}
    auth = env.get("auth") or {}
    return ["ENV          settings: %s · launch env: %s" % (
                " · ".join("%s %d (%d secret-like)" % (k, v["count"], v["secret_like"])
                           for k, v in sorted(settings.items())) or "none",
                "%d vars (%d secret-like)" % (env.get("launch_env_count") or 0, len(env.get("launch_secret_like") or []))
                if env.get("launch_env_available") else "unavailable on this OS"),
            "             auth: %s" % (", ".join("%s (%s)" % (k, "/".join(v)) for k, v in sorted(auth.items()))
                                       or ("subscription login" if env.get("subscription_login")
                                           else "no API key variables"))]


@details(360)
def details_env(r):
    env = r.get("env") or {}
    lines = ["  env %-8s %s" % (scope, ", ".join(block["names"])) for scope, block in sorted((env.get("settings") or {}).items())]
    if env.get("launch_secret_like"):
        lines.append("  env launch secret-like: %s" % ", ".join(env["launch_secret_like"]))
    return lines


# ═══ area: activity ══════════════════════════════════════════════════════════

@collector("activity")
def collect_activity(ctx):
    t = ctx.t
    return {
        "tool_calls": dict(t.tool_calls.most_common()),
        "tool_errors": dict(t.tool_errors),
        "error_samples": {k: clean(v, 120) for k, v in t.error_samples.items()},
        "repeated_failures": [{"call": clean(sig, 100), "retries": n} for sig, n in t.failed.most_common()][:5],
        "interrupts": t.interrupts,
        "compactions": [{"trigger": trig, "pre_tokens": pre} for trig, pre in t.compactions],
        "peak_context": t.peak_context, "baseline_context": t.baseline_context,
        "big_outputs": dict(t.big_outputs),
        "slowest_turn_seconds": t.slowest_turn_ms // 1000,
        "recent_prompts": [clean(p, 100) for p in t.prompts],
    }


@check
def check_activity(r):
    act, out = r.get("activity") or {}, []
    repeated = act.get("repeated_failures") or []
    if repeated:
        out.append(finding("medium" if repeated[0]["retries"] >= 2 else "low", "REPEATED_FAILURES",
                           "A failing call was retried without changing anything",
                           "; ".join("%d× %s" % (x["retries"], x["call"]) for x in repeated[:2])
                           + " (no edits in between)",
                           "Read the error and change approach; after two failed fixes, /clear and restate the task"))
    errors = act.get("tool_errors") or {}
    denied = {k: v for k, v in errors.items() if k in ("user_rejected", "permission_denied", "auto_mode_denied")}
    if sum(denied.values()) >= 3:
        out.append(finding("medium", "PERMISSION_FRICTION", "Many tool calls were denied",
                           ", ".join("%s %d" % kv for kv in sorted(denied.items())),
                           "Allow what you always approve (/permissions) or redirect Claude earlier"))
    if (act.get("interrupts") or 0) >= 3:
        out.append(finding("low", "INTERRUPTIONS", "Claude was interrupted often", "%d interruptions" % act["interrupts"],
                           "Agree on a plan first (plan mode) and state acceptance criteria up front"))
    if (act.get("baseline_context") or 0) >= 60000:
        out.append(finding("medium", "CONTEXT_BASELINE", "Heavy context before any work",
                           "the first request already carried %s tokens" % fmt_k(act["baseline_context"]),
                           "Every request re-sends it: disable unused plugins and MCP servers, trim CLAUDE.md "
                           "and rules; /context shows the biggest items"))
    compactions = act.get("compactions") or []
    peak = max([act.get("peak_context") or 0] + [c["pre_tokens"] for c in compactions])
    if compactions or peak >= 300000:
        out.append(finding("medium" if compactions else "low", "CONTEXT_HEAVY", "Context grew very large",
                           "peak %s tokens; %d compaction(s)" % (fmt_k(peak), len(compactions)),
                           "/clear between unrelated tasks, delegate verbose work (tests, logs, research) "
                           "to subagents, /compact <focus> before it auto-compacts"))
    if sum((act.get("big_outputs") or {}).values()) >= 5:
        out.append(finding("low", "BIG_OUTPUTS", "Many oversized tool outputs",
                           top(act["big_outputs"], 3) + " outputs over ~6k tokens",
                           "Filter output (head, grep, --quiet) or run noisy commands in a subagent"))
    return out


@section(400)
def section_activity(r):
    act, s = r.get("activity") or {}, r.get("session") or {}
    errors = act.get("tool_errors") or {}
    lines = ["ACTIVITY",
             "  tools      %s" % (top(act.get("tool_calls") or {}, 8) or "none"),
             "  errors     %d failed tool calls%s · %d interrupts" % (
                 sum(errors.values()), " (%s)" % top(errors, 6) if errors else "", act.get("interrupts") or 0),
             "  context    first request %s tokens · peak %s · %d compactions · %d big outputs%s" % (
                 fmt_k(act.get("baseline_context")), fmt_k(act.get("peak_context")),
                 len(act.get("compactions") or []), sum((act.get("big_outputs") or {}).values()),
                 " · slowest turn %ds" % act["slowest_turn_seconds"] if act.get("slowest_turn_seconds") else ""),
             "  plan mode  %s" % ("used" if s.get("plan_mode_used") else "not used")]
    lines += ["  prompt     \"%s\"" % p for p in act.get("recent_prompts") or []]
    return lines
