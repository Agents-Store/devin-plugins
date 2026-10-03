---
name: session-analysis
description: Techniques for analyzing OpenClaw session transcripts (listed through the CLI, exported as a trajectory bundle, then queried with jq) to understand user behavior, tool effectiveness, error patterns, token costs, and active hours. Use this skill whenever the user wants to analyze how their agent is performing, what users are asking, which tools work best, what errors occur, or how to improve the workspace based on real usage data. Also applies to questions like "what do my users ask about", "is my agent working well", or "show me session stats".
---

# Session Transcript Analysis

OpenClaw records every conversation as a transcript: user messages, assistant messages, tool calls and
tool results. Analyzing these reveals user behavior, tool effectiveness, error patterns, and
optimization opportunities for workspace files.

## Where Session Data Lives

Sessions and transcripts are rows in the **per-agent SQLite database**
(`agents/<agent-id>/agent/openclaw-agent.sqlite` under the instance's state directory), not files.
Older installs may still hold `sessions.json` and `*.jsonl` files under `agents/<agent-id>/sessions/`;
those are legacy migration inputs and archive artifacts, not live data.

Do **not** open the database to read sessions: it is a live file, it holds OAuth material next to the
transcripts, and a compressed event is invisible to a plain `SELECT`. Use the supported surfaces:

| Need | Surface |
|------|---------|
| List sessions, activity, models | `openclaw sessions --agent <id> --json` (`--all-agents`, `--active <minutes>`, `--limit all`) |
| One session's full timeline | `openclaw sessions export-trajectory --session-key "<key>" --workspace <dir> --output <name> --json` |
| Find where something was discussed | the `sessions_search` / `sessions_history` agent tools |

An instance on a fleet host is reached through `/openclaw-ops:exec <selector> -- sessions …`, never a
hand-written `docker exec`.

A trajectory export writes a bundle (`events.jsonl`, `session-branch.json`, `artifacts.json`,
`metadata.json`, …) under `.openclaw/trajectory-exports/` in the selected workspace. The bundle can
contain prompts, tool results and local paths: treat it as a credential-grade artifact — mode 0600,
outside any repository, deleted when the analysis is done. The export is an owner-level operation.

A daily session reset is opt-in (`session.reset.atHour`, default `4`); history from before a reset
stays in the store, so analyse by session key and window, not by calendar day alone.

## Shape of the Data

Transcript entries are a tree (`id` + `parentId`); the notable entry types are `message`
(user, assistant and `toolResult` messages), `compaction`, `reset` and `branch_summary`. The recipes
below assume the message shape (`message.role`, `message.content[]` with `text` and `toolCall` items,
`message.usage`). Exports differ between releases — **probe the real field names first**:

```bash
jq -c 'keys' <export-file> | sort | uniq -c | sort -rn | head
```

and adjust the paths. The trajectory events (`tool.call`, `tool.result`, `model.completed`) and
`artifacts.json` (final status, errors, usage) are the documented alternative for tool outcomes and
costs.

## Key Data Extractable

| Category | What You Learn | Informs |
|----------|---------------|---------|
| User messages | What users ask, how they phrase requests | SOUL.md tone, AGENTS.md rules |
| Tool calls | Which tools used, frequency | AGENTS.md `## Tools` priorities |
| Errors | What fails, error patterns | AGENTS.md `## Tools` workarounds, AGENTS.md rules |
| Costs | Token usage per session | heartbeat scratch and cadence optimization |
| Active hours | When users interact | Quiet hours, timezone settings |
| User corrections | When users fix the agent | SOUL.md/AGENTS.md improvements |
| Languages | What languages users write in | Language settings |

## Analysis Workflow

### Step 1: Count the sessions
```bash
openclaw sessions --agent <id> --json --limit all | jq '.sessions | length'
```

### Step 2: Export the sessions to analyse
```bash
openclaw sessions --agent <id> --json --limit 20 | jq -r '.sessions[].key'
openclaw sessions export-trajectory --session-key "<key>" --workspace <dir> --output <name> --json
```
Each export lands in its own directory; the recipes below read `<name>/events.jsonl` as
`SESSION_FILE.jsonl`.

### Step 3: Extract user messages (what users ask about)
```bash
jq -r 'select(.message.role=="user") | .message.content[]? | select(.type=="text") | .text' SESSION_FILE.jsonl
```

### Step 4: Extract tool calls (which tools are used)
```bash
jq -r 'select(.message.content[]?.type=="toolCall") | .message.content[] | select(.type=="toolCall") | .name' SESSION_FILE.jsonl
```

### Step 5: Find errors
```bash
jq -r 'select(.message.role=="toolResult") | .message.content[]? | select(.type=="text") | .text' SESSION_FILE.jsonl | grep -i "error\|failed\|exception"
```

### Step 6: Calculate costs
```bash
jq -s '[.[] | .message.usage.cost.total // 0] | add' SESSION_FILE.jsonl
```

### Step 7: Find user corrections
```bash
jq -r 'select(.message.role=="user") | .message.content[]? | select(.type=="text") | .text' SESSION_FILE.jsonl | grep -i "wrong\|incorrect\|no,\|that's not\|I said\|fix\|try again\|redo"
```

See `references/jq-queries.md` for the complete jq command reference.

## Turning Analysis into Workspace Improvements

### User messages → SOUL.md / AGENTS.md
- If users frequently ask in Ukrainian → set default language in SOUL.md
- If users ask multi-part questions → add checklist rule to AGENTS.md
- If users ask about specific domains → sharpen domain expertise in SOUL.md

### Tool calls → AGENTS.md `## Tools`
- Most-used tools → document first with correct syntax
- Rarely-used tools → check if agent knows about them, or remove
- Calculate success rates → set priority order

### Errors → AGENTS.md
- Repeated tool errors → add workaround to the `## Tools` section
- Pattern of similar failures → add preventive rule to AGENTS.md

### User corrections → SOUL.md / AGENTS.md
- Tone corrections → adjust SOUL.md vibe
- Procedure corrections → add/fix AGENTS.md rules
- Factual corrections → add verification requirements

### Costs → heartbeat scratch
- High-cost heartbeat cycles → simplify the heartbeat scratch, isolate the session
- Expensive sessions → identify token-heavy patterns

### Active hours → heartbeat `activeHours` / USER.md
- Peak usage times → optimize heartbeat schedule
- Off hours → define quiet hours
- Timezone patterns → update USER.md timezone

## Multi-Session Analysis

To analyze across multiple sessions, export each one (Step 2), then aggregate the exports:

```bash
# Aggregate across all exports in one directory
cat <export-dir>/*/events.jsonl | jq ...

# Or process the most recent N exports
ls -td <export-dir>/*/ | head -50 | while read -r d; do cat "$d/events.jsonl"; done | jq ...
```

## Generating a Workspace Audit Report

Combine multiple analyses:

1. Run all jq queries from references/jq-queries.md
2. Compile findings into categories (user behavior, tool effectiveness, errors, costs)
3. Map each finding to the workspace file it should improve
4. Generate specific recommendations with proposed changes

## Best Practices

1. Analyze at least 20-50 sessions for meaningful patterns
2. Focus on repeated patterns, not one-off events
3. Prioritize: user corrections > errors > tool usage > costs
4. Update workspace files based on findings, then re-analyze after 1-2 weeks
5. Run analysis monthly for ongoing optimization
