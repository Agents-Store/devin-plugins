---
name: session-analysis
description: Techniques for analyzing OpenClaw session JSONL logs to understand user behavior, tool effectiveness, error patterns, token costs, and active hours. Use this skill whenever the user wants to analyze how their agent is performing, what users are asking, which tools work best, what errors occur, or how to improve the workspace based on real usage data. Also applies to questions like "what do my users ask about", "is my agent working well", or "show me session stats".
---

# Session JSONL Analysis

OpenClaw stores session data as JSONL files. Analyzing these reveals user behavior, tool effectiveness, error patterns, and optimization opportunities for workspace files.

## Session File Location

All paths relative to CWD (standard: `~/.openclaw/`, Docker multi-instance: `~/.openclaw-{name}/`):

```
./agents/main/sessions/sessions.json   # Session index
./agents/main/sessions/*.jsonl         # Session transcripts
```

Each JSONL line is a JSON object representing a message, tool call, or system event. Sessions reset daily at **4 AM local time** by default.

## Key Data Extractable

| Category | What You Learn | Informs |
|----------|---------------|---------|
| User messages | What users ask, how they phrase requests | SOUL.md tone, AGENTS.md rules |
| Tool calls | Which tools used, frequency | TOOLS.md priorities |
| Errors | What fails, error patterns | TOOLS.md workarounds, AGENTS.md rules |
| Costs | Token usage per session | HEARTBEAT.md optimization |
| Active hours | When users interact | Quiet hours, timezone settings |
| User corrections | When users fix the agent | SOUL.md/AGENTS.md improvements |
| Languages | What languages users write in | Language settings |

## Analysis Workflow

### Step 1: Check session index
```bash
cat ./agents/main/sessions/sessions.json 2>/dev/null | jq length
```

### Step 2: Locate session files
```bash
ls -t ./agents/main/sessions/*.jsonl 2>/dev/null | head -20
```

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

### Tool calls → TOOLS.md
- Most-used tools → document first with correct syntax
- Rarely-used tools → check if agent knows about them, or remove
- Calculate success rates → set priority order

### Errors → TOOLS.md / AGENTS.md
- Repeated tool errors → add workaround to TOOLS.md
- Pattern of similar failures → add preventive rule to AGENTS.md

### User corrections → SOUL.md / AGENTS.md
- Tone corrections → adjust SOUL.md vibe
- Procedure corrections → add/fix AGENTS.md rules
- Factual corrections → add verification requirements

### Costs → HEARTBEAT.md
- High-cost heartbeat cycles → simplify HEARTBEAT.md
- Expensive sessions → identify token-heavy patterns

### Active hours → HEARTBEAT.md / USER.md
- Peak usage times → optimize heartbeat schedule
- Off hours → define quiet hours
- Timezone patterns → update USER.md timezone

## Multi-Session Analysis

To analyze across multiple sessions:

```bash
# Aggregate across all recent session files
cat ./agents/main/sessions/*.jsonl | jq ...

# Or process the most recent N files
ls -t ./agents/main/sessions/*.jsonl | head -50 | xargs cat | jq ...
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
