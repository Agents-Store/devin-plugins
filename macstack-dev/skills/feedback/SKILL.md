---
name: feedback
description: This skill should be used when the user reports a problem with macstack-dev or the MACSTACK standard — "this skill did the wrong thing", "the schema is missing a field", "the passport for X is wrong", "send macstack feedback", "improve the schema based on my edit", "fix the macstack plugin" — and the fix must land in the right source (plugin, schema repo, or registry repo).
disable-model-invocation: true
---

# Send Feedback: Plugin, Schema, or Registry

Record a problem found while using macstack-dev and apply the fix at the SOURCE.
The ecosystem has three sources of truth — route the feedback to the right one; a
fix applied to a mirror gets silently overwritten later.

## Step 1 — Identify and route

Ask (skip what the conversation already answers): what happened, what was expected,
severity (critical / major / minor). Then route by WHAT is wrong:

| The problem is about… | Target | Repo |
|---|---|---|
| A skill/command/agent of this plugin behaved wrongly | **Plugin** | `claude-public-plugins/plugins/macstack-dev` (via `$PLUGINS_PUBLIC_SOURCE_DIR`) |
| The schema: a missing/wrong property, enum value, required rule; a lint rule; an example | **Standard** | `github.com/macstacks/macstack` |
| A software passport, category, entity/trigger/agent template | **Registry** | `github.com/macstacks/registry` |

One report may touch several targets (a new schema field usually needs: schema +
examples + the plugin's bundled copy + a skill mention) — fix all of them in one
pass, never partially.

## Step 2 — Fix at the source

### Plugin feedback

Edit the skill in `$PLUGINS_PUBLIC_SOURCE_DIR/macstack-dev/skills/<skill>/SKILL.md`:
minimal targeted change, generalize beyond the reported case, positive framing with
a one-sentence WHY for restrictive rules. Bump the **patch** version in
`.claude-plugin/plugin.json` AND `../.claude-plugin/marketplace.json` (must match).

### Standard (schema) feedback

```bash
git clone --depth 1 git@github.com:macstacks/macstack.git "$TMP/macstack"   # maintainer
# contributors: gh repo fork macstacks/macstack --clone
```

1. Edit `schema/macstack.schema.json` — keep enums/ids stable unless the change is
   the point; breaking changes bump the format (`"macstack": "1.x"`) and get a
   migration note in the README.
2. Update `examples/*.macstack.json` to exercise the change, run
   `python3 scripts/lint.py examples/*.macstack.json` — all must pass.
3. Commit + push (maintainer) or open a PR (`gh pr create`). CI re-validates.
4. **Sync the mirrors in the same session** — this is the step people forget:
   - the plugin's bundled copy `skills/lint/references/macstack.schema.json`
     (then bump the plugin patch version);
   - any project mirrors the user maintains (e.g. vk-ops `docs/macstack/`).

### Registry feedback

Same flow against `github.com/macstacks/registry`: edit the passport/template or
`software-categories.json`, run `python3 scripts/validate.py` (filenames = ids,
ratings consistent), push or PR. If the fix changes a category set, re-check the
plugin's bundled `software-categories.json` copy too.

## Step 3 — Record the learning

Append to the plugin's `LEARNINGS.md` (this file travels with the plugin):

```markdown
## [YYYY-MM-DD] <plugin|schema|registry> feedback — <short title>
- Problem: …
- Fix: … (commits/PRs: …)
- Root cause: …
- Severity: critical | major | minor
```

Schema/registry learnings that change authoring behavior also belong in the
affected skill's text (one line), so future runs don't repeat the mistake.

## Step 4 — Verify

- Plugin fix: re-read the edited skill; versions in plugin.json ⇄ marketplace.json
  match.
- Schema fix: `scripts/lint.py` green on all examples; bundled copy byte-identical
  to the hosted one (`curl -fsSL <raw-url> | diff - <bundled>`).
- Registry fix: `scripts/validate.py` green.

<example>
user: "The schema is missing an sla field on processes — I added it by hand in my macstack.json"
→ route: Standard. Clone macstacks/macstack, add `processes[].sla` to the schema,
  extend one example, lint.py green, push. Sync the bundled copy in macstack-dev
  (patch bump), note the mirror rule in LEARNINGS. Report commits.
</example>
