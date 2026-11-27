---
name: heartbeat-md
description: OpenClaw heartbeats, the periodic background check, now an ordinary automation job (schedule, quiet hours, model, session, delivery per job; checklist in its scratch); `agents.defaults.heartbeat` and HEARTBEAT.md are retired and migrated by Doctor. Use for periodic checks, quiet hours, heartbeat costs, standing orders the heartbeat checks, or a leftover HEARTBEAT.md. Not for writing standing orders (standing-orders), BOOT.md (bootstrap-boot) or automation diagnostics (fleet-diagnostics).
---

# Heartbeat Configuration Guide

A heartbeat is a periodic agent turn that runs without a user message. On current releases it is no
longer a special monitor: it is an **ordinary automation job** with its own schedule, prompt, scratch,
model, session target and delivery (`openclaw automations …`; `openclaw cron` is an alias of the same
commands). Every run is a full agent turn, so keep what it has to do SHORT.

## Where heartbeat settings live now

| What | Where it lives now |
|---|---|
| Cadence, quiet hours, model, session, light context, delivery | flags of the automation job (`openclaw automations edit <job-id> …`) — per job, not a global setting |
| The checklist the check follows | the job's **scratch**, stored in the shared state database |
| Whether anything scheduled runs at all | `cron.enabled` in `openclaw.json` (false, or `OPENCLAW_SKIP_CRON=1`, stops scheduled runs; manual runs still work) |

The old keys `agents.defaults.heartbeat` and `agents.entries.<id>.heartbeat` are **retired: a config
that still carries them is invalid** and the Gateway will not start on it. Never add them to a config.

### First setup

A fresh setup creates one job named **Proactive check** for the owner agent, **disabled**. Defaults once
enabled: every 30 minutes, the agent's main conversation, waits for idle, delivers to the owner DM.
Other agents get a heartbeat only by creating a job for them. Startup and config reload never recreate
a deleted job — deleting it is a lasting choice.

```bash
openclaw automations list --all          # find the job id (disabled jobs included)
openclaw automations show <job-id>
openclaw automations enable <job-id>
```

### Editing the job

<!-- example-only -->
```bash
openclaw automations edit <job-id> --every 30m                       # or --cron "<expr>" --tz <iana-zone>
openclaw automations edit <job-id> --active-hours-start 08:00 --active-hours-end 22:00 \
  --active-hours-timezone user                                       # --clear-active-hours removes the window
openclaw automations edit <job-id> --idle-only --skip-if-scratch-empty
openclaw automations edit <job-id> --session isolated --light-context
openclaw automations edit <job-id> --model <provider>/<model-id>     # --clear-model returns to the default
openclaw automations edit <job-id> --delivery-target owner           # or --announce --channel <ch> --to <id>, or --no-deliver
openclaw automations edit <job-id> --message "Check the scratch. Report only what needs attention; otherwise reply NO_REPLY."
```
<!-- /example-only -->

- `--session` takes `main`, `isolated`, `current` or `session:<id>`; `isolated` gives a fresh
  transcript per run and is the biggest token saver.
- `--light-context` applies to isolated agent-turn jobs only: the run starts without the workspace
  bootstrap files.
- `--model` must be an exact reference from the instance's own model catalogue **and** inside the
  agent's `modelPolicy.allow`; a model id typed from memory is `fleet.config.model-id-unverified`.
- `--skip-if-scratch-empty` skips a run whose scratch is explicitly empty; a missing scratch still runs.
- `disable`, `enable` and `remove` work as for any automation.

Each edit changes agent behaviour from the next run, so it is an R2 change: show the current job
(`automations show`) and the intended flags first, and keep the reverse `edit` as an executable line in
the plan's ROLLBACK.

### The scratch (the checklist)

```bash
openclaw automations scratch <job-id>
openclaw automations scratch <job-id> --set "<checklist>"
openclaw automations scratch <job-id> --file <notes.md>
openclaw automations scratch <job-id> --unset
```

Setting the scratch is also R2: keep the old text in ROLLBACK as an executable `--set`/`--file` line
(`--expected-revision` guards against a concurrent edit).

## Upgrading an instance that still has the old heartbeat

An instance upgraded from a release before the change still carries the retired keys, a persisted
monitor or a `HEARTBEAT.md` file. Doctor's repair mode converts each of them into an ordinary job — it
keeps the job identity, run history, scratch, disabled state, quiet hours and delivery target, imports
supported `HEARTBEAT.md` content, archives the file under the state directory
(`backups/heartbeat-migration/`), and only then removes the old keys.

What to know before planning it:

- Non-interactive repair (`doctor --fix --yes`, unattended updates) does **not** migrate when a cron
  partition must be chosen; it keeps the old keys and asks for an interactive `doctor --fix`. Until then
  the config is invalid and the Gateway will not start — plan the interactive run as part of the upgrade.
- The shared-state database moves to a newer schema with no downgrade: a rollback means restoring the
  pre-upgrade backup into a separate state directory. Take and verify that backup first.
- Migrated jobs use standard automation delivery: heartbeat-only duplicate suppression and no-route
  skipping are gone, so review each migrated job's delivery settings afterwards.
- A heartbeat model outside the agent's `modelPolicy.allow` is dropped from the job, and Doctor reports it.
- If the existing scratch differs from `HEARTBEAT.md`, Doctor keeps both and reports it; compare before
  copying anything into the job.

In this plugin that repair rewrites what it does not understand, so it is an R4 plan with a typed
confirmation (backup first, eight blocks, no `--yes` in the turn the plan is shown) — never a routine
step after an edit. Confirm current behaviour with the `docs-research` skill before acting; the
upstream page is "Heartbeat migration" (`gateway/heartbeat`).

## Response Contract

If nothing needs attention, the run replies `NO_REPLY`, or records the outcome with the automations
tool's self-scoped `record_result` action (`no_change` suppresses delivery). The old
`heartbeat_respond` tool no longer exists. An alert is the alert text only, with no silent
acknowledgment attached.

## Example Scratch Checklist

```markdown
# Periodic Checks
- Check the inbox for urgent messages only
- Check Telegram mentions in monitored groups
- Calendar: events in the next 2 hours
```

Quiet hours belong in the job's active hours, not in the checklist text.

## One heartbeat job or several automations?

Keep the heartbeat job for a small awareness checklist. Create a separate **automation**
(`openclaw automations create …`) for anything with its own schedule, its own delivery, or its own
approval rules.

## Standing Orders Integration

Standing orders live in `docs/standing-orders/` and are referenced from AGENTS.md. Trigger them from
their own automation, not from the heartbeat scratch, so each program keeps its own cadence and run
history. See the **standing-orders** skill for design patterns.

## Token-Efficient Heartbeats

Every run costs tokens. Minimise cost:

1. **Isolate the session** — `--session isolated`
2. **Use a cheap model** — `--model` with a small model from the instance's catalogue, allowed by the agent's model policy
3. **Keep the checklist short** — 3-5 items max
4. **Use `--light-context`** — skips the workspace bootstrap files (isolated jobs only)
5. **Set an appropriate cadence** — do not run every minute unless needed
6. **Define quiet hours** — `--active-hours-start` / `--active-hours-end`
7. **Skip empty checklists** — `--skip-if-scratch-empty`

## What Data Is Needed

| Input | Source | What It Determines |
|-------|--------|-------------------|
| Business hours | Client timezone + schedule | the job's active hours |
| Monitoring needs | Client requirements | What the scratch checks |
| News/legal sources | Domain-specific | Sites/feeds to monitor |
| Standing orders | docs/standing-orders/ | Scheduled tasks (as automations) |
| Channel activity | openclaw.json channels | Which platforms to monitor |
| Alert recipient | `commands.ownerAllowFrom` or channel `allowFrom` | The job's delivery target |

## Signals That Improve the Heartbeat

- **User asks "did anything happen?"** → add relevant monitoring to the scratch
- **User wants periodic reports** → create an automation
- **Agent burns tokens on useless checks** → remove from the scratch, isolate the session
- **Missed important event** → add monitoring for that event type
- **Too many notifications** → refine filters, narrow the active hours, review the delivery target

## Best Practices

1. Start with an empty scratch — add only what's needed
2. Keep to 3-5 checklist items
3. Always define quiet hours
4. Use the cheapest allowed model that can handle the tasks
5. Do not create a separate state file for "already checked" bookkeeping
6. Review token costs weekly — remove low-value checks
