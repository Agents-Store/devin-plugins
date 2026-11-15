"""Create the ads workspace in a project, copy the toolkit into it, and hand the keys to Claude Code."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from . import __version__
from .core import DEFAULT_CONFIG, Refused, TOOLKIT_DIR, WORKSPACE_DIRS, parse_env_text
from .keys import all_keys

ASSETS = TOOLKIT_DIR / "assets"
GITIGNORE = "# written by stack-ads: keep keys, the copied toolkit and raw research dumps out of git\n.env\n.google-adc.json\ntools/\nresearch/raw/\nreports/raw/\n*.dry-run.txt\n"


def guides_source():
    """Key guides live next to the toolkit in the workspace, or in the skill's references in the plugin."""
    for candidate in (TOOLKIT_DIR / "guides", TOOLKIT_DIR.parent / "references"):
        if candidate.is_dir():
            return candidate
    return None


def init(target, update=False):
    ws = Path(target).expanduser().resolve()
    created = []
    fresh = not (ws / "config.json").is_file()
    if update and fresh:
        raise Refused("%s holds no ads workspace yet" % ws, "run init without --update first")
    ws.mkdir(parents=True, exist_ok=True)
    if not update:
        for name in WORKSPACE_DIRS:
            (ws / name).mkdir(parents=True, exist_ok=True)
        if fresh:
            (ws / "config.json").write_text(json.dumps(DEFAULT_CONFIG, indent=2) + "\n", encoding="utf-8")
            created.append("config.json")
        env_file = ws / ".env"
        if not env_file.exists():
            shutil.copyfile(ASSETS / "env.example", env_file)
            os.chmod(env_file, 0o600)
            created.append(".env")
        ignore = ws / ".gitignore"
        if not ignore.exists():
            ignore.write_text(GITIGNORE, encoding="utf-8")
            created.append(".gitignore")
        readme = ws / "README.md"
        if not readme.exists():
            shutil.copyfile(ASSETS / "workspace-readme.md", readme)
            created.append("README.md")
    tools = ws / "tools"
    if tools.resolve() != TOOLKIT_DIR:
        if tools.exists():
            shutil.rmtree(tools)
        tools.mkdir(parents=True)
        shutil.copyfile(TOOLKIT_DIR / "ads.py", tools / "ads.py")
        shutil.copytree(TOOLKIT_DIR / "adskit", tools / "adskit", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        shutil.copytree(ASSETS, tools / "assets")
        source = guides_source()
        if source:
            (tools / "guides").mkdir()
            for guide in sorted(source.glob("*.md")):
                shutil.copyfile(guide, tools / "guides" / guide.name)
        (tools / "VERSION").write_text(__version__ + "\n", encoding="utf-8")
        created.append("tools/ (toolkit %s)" % __version__)
    return {"workspace": str(ws), "created": created, "toolkit": __version__,
            "next": "fill ads/.env, then run: python3 ads/tools/ads.py doctor --live"}


def git_ignored(path):
    """True or False inside a git repository, None outside one."""
    path = Path(path).resolve()
    folder = path.parent
    while not folder.is_dir():
        folder = folder.parent
    try:
        inside = subprocess.run(["git", "-C", str(folder), "rev-parse", "--is-inside-work-tree"],
                                capture_output=True, text=True)
        if inside.returncode != 0:
            return None
        done = subprocess.run(["git", "-C", str(folder), "check-ignore", "-q", str(path)], capture_output=True, text=True)
    except OSError:
        return None
    return done.returncode == 0


def sync_claude(ctx, settings=None):
    """Merge the keys of ads/.env into the env block of .claude/settings.local.json."""
    env_file = ctx.ws / ".env"
    if not env_file.is_file():
        raise Refused("%s does not exist" % env_file, "run init first")
    target = Path(settings) if settings else ctx.ws.parent / ".claude" / "settings.local.json"
    for path in (env_file, target):
        if git_ignored(path) is False:
            raise Refused("%s is not ignored by git, so the keys could be committed" % path,
                          "add it to .gitignore, then run this command again")
    known = set(all_keys())
    values = {k: v for k, v in parse_env_text(env_file.read_text(encoding="utf-8")).items() if v and k in known}
    data = {}
    if target.is_file():
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
        except ValueError as exc:
            raise Refused("%s is not valid JSON: %s" % (target, exc))
    block = data.setdefault("env", {})
    changed = sorted(k for k, v in values.items() if block.get(k) != v)
    block.update(values)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    try:
        os.chmod(target, 0o600)
    except OSError:
        pass
    return {"settings": str(target), "variables_written": changed, "variables_total": len(values),
            "next": "restart the Claude Code session: MCP servers read these variables at start"}
