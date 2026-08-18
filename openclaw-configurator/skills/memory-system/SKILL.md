---
name: memory-system
description: Guide for OpenClaw's memory system — MEMORY.md curation, daily logs, memory flush, and vector search. Use this skill whenever the user asks about how the agent remembers things between sessions, wants to configure memory management, needs to understand daily logs versus long-term memory, or is setting up memory curation processes. Also applies to questions about vector search, memory security in groups, or "how does the agent remember".
---

# Memory System Guide

OpenClaw's memory is built on plain Markdown files in the workspace. The agent doesn't retain information in RAM between sessions — all persistent data must be written to disk.

## Two-Layer Architecture

### Layer 1: Daily Logs (`memory/YYYY-MM-DD.md`)
- Append-only journal for the day
- Today's and yesterday's entries loaded at session start
- Captures running notes, decisions, observations
- Format: freeform markdown, chronological entries
- Auto-created by the agent during sessions

### Layer 2: Long-Term Memory (`MEMORY.md`)
- Curated, durable information
- Loaded ONLY in main private sessions (never in groups — security)
- Contains: key facts, user preferences, project decisions, recurring patterns
- Maintained by the agent during heartbeats or explicitly

## Memory Tools

Two agent-facing tools for memory operations:

| Tool | Purpose |
|------|---------|
| `memory_search` | Semantic retrieval across indexed Markdown snippets |
| `memory_get` | Targeted file/line-range reading (returns empty gracefully if file doesn't exist) |

## Memory Flush Mechanism

Before context compaction (when session tokens approach the limit), OpenClaw triggers a silent agentic turn:

- Agent is reminded to preserve durable memories to disk
- Activates when: `contextWindow - reserveTokensFloor - softThresholdTokens` is reached
- Uses `NO_REPLY` so users aren't interrupted
- Runs once per compaction cycle
- Requires writable workspace access (skipped in read-only sandbox)

Configure in `openclaw.json`:
```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "memoryFlush": true,
        "reserveTokensFloor": 8000
      }
    }
  }
}
```

## Vector Search (Optional)

OpenClaw supports semantic memory search via vector indexing:

- Indexes both MEMORY.md and daily logs
- Supports multiple embedding providers: OpenAI, Gemini, Voyage, Mistral, Ollama, local GGUF
- Features: hybrid BM25+vector search, MMR re-ranking, temporal decay
- Useful for agents with large memory histories

## MEMORY.md Structure

Recommended format for curated long-term memory:

```markdown
# MEMORY.md

## User Preferences
- User prefers brief responses unless complexity requires detail
- Concise answers for simple questions, thorough for complex ones
- Prefers code examples over long explanations

## Key Decisions
- 2025-03-15: Chose PostgreSQL over MongoDB for the main project
- 2025-03-10: Agreed on 2-week sprints with Monday planning

## Active Projects
- OpenClaw workspace optimization — in progress
- API migration from v2 to v3 — blocked on auth design

## Recurring Patterns
- User asks about legal compliance every Monday
- Weekly report needed by Friday 17:00
- Deploy window: Tuesday-Thursday only

## Important Context
- Company uses Jira for project management
- CI/CD via GitHub Actions
- Production on AWS eu-central-1
```

## Memory Curation Process

The agent should periodically (every few days) review daily logs and distill:

1. Read last 3-5 daily logs
2. Identify durable facts, decisions, preferences
3. Check if they're already in MEMORY.md
4. Add new items, update changed items, remove outdated ones
5. Keep MEMORY.md focused — remove ephemeral details

## Security: MEMORY.md in Groups

MEMORY.md is **never loaded in group chats**. This is a security feature — prevents leaking private user information to shared contexts. The agent should follow this rule in AGENTS.md:

```markdown
## Memory
- MEMORY.md loads ONLY in main session
- Never reference MEMORY.md content in group chats
- Daily logs are session-private as well
```

## Configuring Memory in AGENTS.md

Add memory management instructions:

```markdown
## Memory Management
1. On session start: read memory/YYYY-MM-DD.md (today + yesterday)
2. During work: append notes to today's memory file
3. Every 3 days: review daily files, distill into MEMORY.md
4. Before answering questions about past decisions: check MEMORY.md first
5. Never share MEMORY.md content in group chats
```

## Best Practices

1. Keep MEMORY.md under 5,000 characters — it's loaded every main session
2. Use categories (Preferences, Decisions, Projects, Patterns)
3. Include dates for time-sensitive items
4. Remove outdated entries regularly
5. Let the agent suggest memory updates during curation
6. Don't duplicate what's in AGENTS.md or SOUL.md
