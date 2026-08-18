---
name: release-migration
description: Reconcile an OpenClaw instance's configuration against a new release — read the changelog/release notes between two tags, recommend newly available features, flag and migrate deprecated/legacy settings, then run openclaw doctor. Use after updating OpenClaw (invoked by /instance-update), when the user says "I just updated OpenClaw — check my config", "what new features should I enable", "fix legacy/deprecated settings", or "migrate my config to the new version".
---

# Release Migration

Turn a code update into a config update. After OpenClaw's code is bumped from `OLD_TAG` to `NEW_TAG`, this workflow reads what changed, recommends new features, removes/migrates legacy settings, and verifies with `openclaw doctor`. It is invoked as the final phase of `/instance-update` and is also runnable standalone via `/config-validate --upgrade-from <tag>` on an already-updated instance.

## Inputs

- `OLD_TAG` — the version before the update (e.g. `$PRE_UPDATE_TAG`).
- `NEW_TAG` — the version after the update (e.g. `$TARGET_TAG`).
- **Project git dir** = `$OPENCLAW_PROJECT_DIR` — holds the git checkout + `CHANGELOG.md`.
- **Instance dir** = `${OPENCLAW_INSTANCE_DIR:-${OPENCLAW_PROJECT_DIR:-$(pwd)}}` — holds `openclaw.json` (config to reconcile). Config lives in the **instance** dir, not the git project dir.

## Step A — Gather change data

From the project git dir:

```bash
PROJECT_DIR="${OPENCLAW_PROJECT_DIR:-$(pwd)}"
git -C "$PROJECT_DIR" show "$NEW_TAG:CHANGELOG.md" 2>/dev/null | sed -n '1,120p'   # read the OLD..NEW section
git -C "$PROJECT_DIR" log --oneline "$OLD_TAG..$NEW_TAG" 2>/dev/null               # commit-level changes
```

Then load **docs-research** to fetch:
- GitHub release notes for each tag in range: `https://github.com/openclaw/openclaw/releases`
- Any new-feature pages on `https://docs.openclaw.ai/` referenced by the changelog.

If `CHANGELOG.md` is absent, rely on `git log` + release notes + docs.

## Step B — Categorize changes

Sort what you found into three buckets:

1. **New features** — config fields, channels, tool profiles, memory/compaction strategies, hooks, or models that are newly available. Candidates to **recommend enabling**.
2. **Deprecated / legacy** — settings that still parse but are obsolete. Common examples:
   - Legacy model refs: `openai-codex/*` and `codex-cli/*` → `openai/*`; `claude-cli/*` → canonical `anthropic/*` + runtime; `google-gemini-cli/*` → canonical `google/*` + runtime.
   - Renamed/moved fields; removed options; old auth-profile shapes.
3. **Breaking changes** — settings that will stop the gateway or change behavior and **must** be edited.

Cross-reference the **config-validation** skill's field-level checklist for current valid values, and **provider-auth** for auth-method migrations (a frequent upgrade surface).

## Step C — Apply migrations

Edit `openclaw.json` in the instance dir using the **openclaw-config** safeguards, one change at a time:

1. Show the proposed diff and ask for explicit confirmation.
2. Back up once: `cp ./openclaw.json ./openclaw.json.bak`
3. Validate JSON syntax before writing.
4. **Never delete sections** — only add or modify fields.
5. For new features: present them as opt-in recommendations (don't enable silently).

Prefer `openclaw config set/unset` over hand-editing when a CLI path exists.

## Step D — Run doctor

```bash
# Standard:
openclaw doctor --fix
# Docker multi-instance (run in the project dir where docker-compose.yaml lives):
cd "$PROJECT_DIR" && docker compose exec openclaw-gateway-<name> openclaw doctor --fix
```

`openclaw doctor --fix` auto-rewrites known legacy refs (e.g. `openai-codex/* → openai/*`). Capture its output and report exactly what it changed. Re-run without `--fix` to confirm a clean result. Note: `unresolved SecretRef` warnings outside gateway runtime are safe to ignore.

If `openclaw.json` was edited from the host in a Docker deployment, fix permissions (chown + doctor) as in `/workspace-optimize` step 9.

## Step E — Migration report

```markdown
# OpenClaw Release Migration Report — OLD_TAG → NEW_TAG

## New features available (opt-in)
- [ ] <feature> — <what it does> — recommend: enable / skip — <doc link>

## Deprecated / legacy found
| Setting | Status | Action taken |
|---------|--------|--------------|
| openai-codex/gpt-5.5 | legacy ref | rewritten to openai/gpt-5.5 by doctor |

## Migrations applied
- <field>: <old> → <new> (backed up to openclaw.json.bak)

## doctor result
- <pass / N fixes applied / remaining issues>

## Follow-ups
1. <most important next action>
```

## Cross-links

- **docs-research** — all changelog/release/doc fetching.
- **config-validation** — field-level validity checklist.
- **provider-auth** — auth-method changes between releases.
- **openclaw-config** — editing safeguards.
