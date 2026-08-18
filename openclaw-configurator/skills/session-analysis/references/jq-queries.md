# Session Analysis jq Commands

Ready-to-use jq commands for analyzing OpenClaw session JSONL files. All paths relative to CWD (`~/.openclaw-{name}/`). Replace `SESSION_FILE.jsonl` with actual path, or use `cat ./agents/main/sessions/*.jsonl` for bulk analysis.

---

## User Behavior

### What do users ask about most?
```bash
jq -r 'select(.message.role=="user") | .message.content[]? | select(.type=="text") | .text' SESSION_FILE.jsonl \
  | head -500 | sort | uniq -c | sort -rn | head -20
```

### Which Telegram users are most active?
```bash
jq -r 'select(.type=="session") | .deliveryContext.senderId' SESSION_FILE.jsonl \
  | sort | uniq -c | sort -rn
```

### What languages do users write in?
```bash
# Extract sample messages for language detection
jq -r 'select(.message.role=="user") | .message.content[]? | select(.type=="text") | .text' SESSION_FILE.jsonl \
  | head -50
```

### User corrections (agent made a mistake)
```bash
jq -r 'select(.message.role=="user") | .message.content[]? | select(.type=="text") | .text' SESSION_FILE.jsonl \
  | grep -i "wrong\|incorrect\|no,\|that's not\|I said\|fix\|try again\|redo\|not what I\|you missed\|forgot"
```

### Sessions where user repeated a request
```bash
# Look for similar consecutive user messages
jq -r 'select(.message.role=="user") | .message.content[]? | select(.type=="text") | .text' SESSION_FILE.jsonl \
  | uniq -d
```

---

## Tool Effectiveness

### Most used tools
```bash
jq -r 'select(.message.content[]?.type=="toolCall") | .message.content[] | select(.type=="toolCall") | .name' SESSION_FILE.jsonl \
  | sort | uniq -c | sort -rn
```

### Tools that return errors
```bash
jq -r 'select(.message.role=="toolResult") | .message.content[]? | select(.type=="text") | .text' SESSION_FILE.jsonl \
  | grep -ci "error\|failed\|exception"
```

### Error details by tool
```bash
jq -r '
  select(.message.role=="toolResult") |
  select(.message.content[]?.text | test("error|failed|exception"; "i")) |
  .message.content[]? | select(.type=="text") | .text
' SESSION_FILE.jsonl | head -30
```

### Average tool calls per session
```bash
# Count toolCall entries in a session file
jq '[select(.message.content[]?.type=="toolCall")] | length' SESSION_FILE.jsonl
```

### Tool call success rate
```bash
# Total tool results
TOTAL=$(jq 'select(.message.role=="toolResult")' SESSION_FILE.jsonl | wc -l)
# Tool results with errors
ERRORS=$(jq -r 'select(.message.role=="toolResult") | .message.content[]?.text' SESSION_FILE.jsonl | grep -ci "error\|failed\|exception")
echo "Total: $TOTAL, Errors: $ERRORS, Success rate: $(( (TOTAL - ERRORS) * 100 / TOTAL ))%"
```

---

## Cost Analysis

### Total cost per session file
```bash
jq -s '[.[] | .message.usage.cost.total // 0] | add' SESSION_FILE.jsonl
```

### Token usage summary
```bash
jq -s '
  [.[] | .message.usage // empty] |
  {
    total_input: [.[].input_tokens // 0] | add,
    total_output: [.[].output_tokens // 0] | add,
    total_cost: [.[].cost.total // 0] | add
  }
' SESSION_FILE.jsonl
```

### Most expensive sessions
```bash
for f in ./agents/main/sessions/*.jsonl; do
  cost=$(jq -s '[.[] | .message.usage.cost.total // 0] | add' "$f" 2>/dev/null)
  echo "$cost $f"
done | sort -rn | head -10
```

---

## Active Hours

### When are users most active?
```bash
jq -r 'select(.message.role=="user") | .timestamp' SESSION_FILE.jsonl \
  | cut -dT -f2 | cut -d: -f1 | sort | uniq -c | sort -rn
```

### Most active days
```bash
jq -r 'select(.message.role=="user") | .timestamp' SESSION_FILE.jsonl \
  | cut -dT -f1 | sort | uniq -c | sort -rn | head -10
```

---

## Workspace Completeness Check

### Which standard files exist?
```bash
for f in AGENTS.md SOUL.md USER.md IDENTITY.md TOOLS.md HEARTBEAT.md MEMORY.md BOOT.md; do
  [ -f "./workspace/$f" ] && echo "OK $f ($(wc -c < "./workspace/$f") bytes)" || echo "MISSING $f"
done
```

### Word count of each file
```bash
wc -w ./workspace/AGENTS.md ./workspace/SOUL.md ./workspace/USER.md ./workspace/IDENTITY.md ./workspace/TOOLS.md ./workspace/HEARTBEAT.md ./workspace/MEMORY.md 2>/dev/null
```

### Docs subfolder count
```bash
find ./workspace/docs/ -name "*.md" 2>/dev/null | wc -l
```

### Skills inventory
```bash
find ./workspace/skills/ -name "SKILL.md" 2>/dev/null | while read f; do
  echo "$(dirname "$f" | xargs basename): $(head -5 "$f" | grep -i description || echo 'no description')"
done
```

---

## Bulk Analysis (across all sessions)

### Aggregate all recent sessions
```bash
ls -t ./agents/main/sessions/*.jsonl 2>/dev/null | head -50 | xargs cat
```

### Count total sessions analyzed
```bash
ls ./agents/main/sessions/*.jsonl 2>/dev/null | wc -l
```
