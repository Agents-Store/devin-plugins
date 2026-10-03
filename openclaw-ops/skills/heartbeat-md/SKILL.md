---
name: heartbeat-md
description: Guide for OpenClaw heartbeats — the periodic background turn that surfaces anything needing attention. Current releases keep heartbeat instructions in the heartbeat monitor's scratch (a database row, managed with `openclaw automations scratch`) and the cadence in `agents.defaults.heartbeat`; the HEARTBEAT.md workspace file is retired and never read at runtime, but older workspaces still carry one. Use this skill whenever the user needs background monitoring, periodic checks, standing orders integration, quiet hours configuration, a leftover HEARTBEAT.md, or wants to understand heartbeat mechanics and token costs. Even questions like "how do I make the agent check something periodically", "set up monitoring", or "reduce heartbeat token costs" need this skill.
---

# Heartbeat Configuration Guide

A heartbeat is a periodic main-session agent turn that runs without a user message. It is a
system-owned automation: the gateway keeps one monitor job per heartbeat-enabled agent (visible as
`Heartbeat (<agent-id>)` in `openclaw automations list --all`; `openclaw cron` is an alias of the same
commands). Every heartbeat is a full agent turn, so keep what it has to do SHORT.

## HEARTBEAT.md is retired

The workspace file `HEARTBEAT.md` is no longer created in new workspaces and **the runtime never
reads it**. What it used to hold now lives in two places:

| What | Where it lives now |
|---|---|
| Cadence, target, quiet hours, model, context weight | `agents.defaults.heartbeat` (per agent: `agents.entries.<id>.heartbeat`) in `openclaw.json` |
| The checklist the heartbeat follows | the monitor's **scratch**, stored in the shared state database |

Read and change the scratch with the monitor job id from `openclaw automations list --all`:

```bash
openclaw automations scratch <jobId>
openclaw automations scratch <jobId> --set "<checklist>"
openclaw automations scratch <jobId> --file <notes.md>
openclaw automations scratch <jobId> --unset
```

Setting the scratch changes agent behaviour from the next tick, so it is an R2 change: show the old and
the new text first, and keep the old text in the plan's ROLLBACK as an executable `--set`/`--file` line.

### A workspace that still has HEARTBEAT.md

The file is dead weight on a current release. The doctor's repair mode imports it into the monitor
scratch, converts valid legacy `tasks:` entries into automation jobs, archives the original under the
state directory and removes the file. That mode rewrites what it does not understand, so in this plugin
it is an R4 plan with a typed confirmation (backup first, eight blocks, no `--yes` in the turn the plan
is shown) — never a routine step after an edit. The alternative is to copy the checklist into the
scratch by hand and leave the file for the plan that retires it. Confirm current behaviour with the
`docs-research` skill before acting; the upstream page is the "Retired HEARTBEAT.md workspace file"
template page.

## Config Mechanics

```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "30m",
        "model": "<provider>/<model-id>",
        "lightContext": true,
        "isolatedSession": true
      }
    }
  }
}
```

- `every` — cadence; `"0m"` disables only the recurring tick (event-driven wakes still work). Unset, the
  default is `30m`, or `1h` when Anthropic OAuth/token auth is in use.
- `model` — an exact model reference for heartbeat turns. Take it from the instance's own model
  catalogue, never from memory; a model id typed from memory is `fleet.config.model-id-unverified`.
- `lightContext: true` — skip workspace bootstrap files for heartbeat runs; the monitor scratch is
  injected either way.
- `isolatedSession: true` — a fresh session per run, with no conversation history. This is the single
  biggest token saver.
- `activeHours` (`start`, `end`, local time) — quiet hours: outside the window the tick is skipped.
- `target` — where alerts go: `owner` (default, the operator DM), `last`, `none`, or a channel id.
- The heartbeat object is **strict**: an unknown field refuses the config. Check the field list against
  the running build (`openclaw config schema`) before adding anything.
- Scheduled heartbeats need automations: with `cron.enabled` false, nothing ticks.

Config changes go through the `config-surgery` procedure (snapshot, patch with base hash, validate,
verify from the runtime) — never a plain file write against a running gateway.

## Response Contract

If nothing needs attention, the heartbeat replies `NO_REPLY` (or calls `heartbeat_respond` with
`notify: false`). An alert is the alert text only, with no silent acknowledgment attached.

## Example Scratch Checklist

```markdown
# Periodic Checks
- Check the inbox for urgent messages only
- Check Telegram mentions in monitored groups
- Calendar: events in the next 2 hours
```

Quiet hours belong in `activeHours`, not in the checklist text.

## Heartbeat or Automation?

The default heartbeat prompt tells the agent not to infer or repeat old tasks from earlier chats and
that recurring tasks are automations. Use the scratch for a small awareness checklist; create a
separate **automation** (`openclaw automations create …`) for anything with its own schedule, its own
delivery, or its own approval rules.

## Standing Orders Integration

Standing orders live in `docs/standing-orders/` and are referenced from AGENTS.md. Trigger them from
an automation, not from the heartbeat scratch, so each program keeps its own cadence and run history.
See the **standing-orders** skill for design patterns.

## Token-Efficient Heartbeats

Every heartbeat costs tokens. Minimise cost:

1. **Isolate the session** — `isolatedSession: true`
2. **Use a cheap model** — set `heartbeat.model` to a small model from the instance's catalogue
3. **Keep the checklist short** — 3-5 items max
4. **Use `lightContext: true`** — loads minimal context
5. **Set an appropriate cadence** — do not tick every minute unless needed
6. **Define quiet hours** — `activeHours`

## What Data Is Needed

| Input | Source | What It Determines |
|-------|--------|-------------------|
| Business hours | Client timezone + schedule | `activeHours` |
| Monitoring needs | Client requirements | What the scratch checks |
| News/legal sources | Domain-specific | Sites/feeds to monitor |
| Standing orders | docs/standing-orders/ | Scheduled tasks (as automations) |
| Channel activity | openclaw.json channels | Which platforms to monitor |
| Alert recipient | `commands.ownerAllowFrom` or channel `allowFrom` | Where heartbeat alerts go |

## Signals That Improve the Heartbeat

- **User asks "did anything happen?"** → add relevant monitoring to the scratch
- **User wants periodic reports** → create an automation
- **Agent burns tokens on useless checks** → remove from the scratch, isolate the session
- **Missed important event** → add monitoring for that event type
- **Too many notifications** → refine filters, add `activeHours`

## Best Practices

1. Start with an empty scratch — add only what's needed
2. Keep to 3-5 checklist items
3. Always define quiet hours
4. Use the cheapest model that can handle the tasks
5. Do not create a separate state file for "already checked" bookkeeping
6. Review token costs weekly — remove low-value checks
