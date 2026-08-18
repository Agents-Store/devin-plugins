---
name: agents-md
description: Guide for creating and customizing AGENTS.md — the operating rules, procedures, and behavioral guardrails for an OpenClaw agent. Use this skill whenever the user is working on agent behavior, operating procedures, session startup sequences, memory management policies, group chat rules, safety red lines, tool usage priorities, or standing order references. Even if they just say "the agent should do X differently" or "add a rule for Y", this skill applies because operational rules belong in AGENTS.md. Also use when deciding what belongs in AGENTS.md versus SOUL.md — this skill clarifies the boundary.
---

# AGENTS.md Customization Guide

AGENTS.md is the "employee handbook" for an OpenClaw agent. It defines HOW the agent operates — procedures, rules, memory management, group chat behavior, and standing orders. Loaded into every session.

**Write all content in English.** Users may communicate in any language, but workspace files are always English — this ensures consistency across multi-user setups and better model compatibility (LLMs process English instructions more reliably).

## Key Distinction

- **SOUL.md** = WHO the agent is (persona, values, tone)
- **AGENTS.md** = WHAT the agent does and HOW (procedures, rules, checklists)

Never mix them. If it describes personality, it goes in SOUL.md. If it describes a procedure, it goes in AGENTS.md.

## Core Sections

### 1. Session Startup

Define what the agent reads before responding:

```markdown
## Session Startup
1. Read SOUL.md (your identity)
2. Read USER.md (who you're helping)
3. Read today's memory: memory/YYYY-MM-DD.md
4. Read yesterday's memory if relevant
5. Check MEMORY.md for long-term context
```

### 2. Memory Management

Two-layer memory system:

```markdown
## Memory
- Daily logs: memory/YYYY-MM-DD.md (append-only journal)
- Long-term: MEMORY.md (curated facts, decisions, preferences)
- Capture: decisions, user preferences, open questions, project status
- Review daily files every few days; distill into MEMORY.md
- MEMORY.md loads ONLY in main session (never groups)
```

### 3. Red Lines

Non-negotiable safety rules:

```markdown
## Red Lines
- Don't dump directories or secrets into chat
- Don't run destructive commands unless explicitly asked
- Don't exfiltrate private data. Ever.
- Don't speak as the user in group contexts
- Ask before taking external actions (sending messages, making calls)
```

### 4. Group Chat Behavior

Rules for shared spaces:

```markdown
## Group Chats
- Respond when directly mentioned or asked a question
- Add genuine value — don't comment just to participate
- Stay silent during casual banter
- Never share MEMORY.md content in groups
- Adapt formatting: no markdown tables in Discord/WhatsApp, use bullet lists
```

### 5. Tools Guidance

Point to TOOLS.md and add usage priorities:

```markdown
## Tools
- See TOOLS.md for environment-specific notes
- Prefer [tool A] for [domain] queries
- Use [tool B] as fallback when [tool A] fails
- For complex tasks (3+ steps): create a .prose program
```

### 6. Reference Documents (Subfolder Pattern)

AGENTS.md should reference on-demand docs that the agent reads when needed:

```markdown
## Reference Documents
Before starting a task, check if a relevant doc exists.
Read it with: read docs/<folder>/<file>.md

Available docs:
- docs/rules/         — security rules, data classification, group chat policy
- docs/procedures/    — step-by-step guides for specific task types
- docs/clients/       — client profiles, contracts, key facts
- docs/standing-orders/ — recurring tasks and schedules

Always read the relevant doc BEFORE starting work. Do not guess.
```

This saves tokens — files in docs/ are loaded only when relevant, unlike AGENTS.md which loads every session. Use the 50% rule: if content is needed in < 50% of sessions, move it to docs/.

### 7. Heartbeat Configuration

Background task triggers:

```markdown
## Heartbeats
- Check HEARTBEAT.md for periodic tasks
- Track state via memory/heartbeat-state.json
- Don't repeat checks already done this cycle
- Respect quiet hours: [time range]
```

### 8. Standing Orders References

Point to docs/standing-orders/ for autonomous programs:

```markdown
## Standing Orders
See docs/standing-orders/ for authorized autonomous programs:
- docs/standing-orders/weekly-report.md
- docs/standing-orders/monitoring.md
Each defines: scope, triggers, approval gates, escalation rules
```

## Customization Inputs

To customize AGENTS.md effectively, gather:

| Input | Source | What It Determines |
|-------|--------|-------------------|
| Available skills | `openclaw.json` skills + extraDirs | Tool usage instructions |
| Enabled plugins | `openclaw.json` plugins | Plugin-specific behavior |
| Telegram group IDs | `openclaw.json` channels.telegram.groups | Group-specific rules |
| User roles | Client org chart | Approval chains, permissions |
| Complex task threshold | Observed quality issues | When to trigger .prose |
| Error patterns | Session logs | Specific preventive rules |

## Signals from Sessions That Improve AGENTS.md

- **Agent skips steps** → add explicit checklist
- **Agent uses wrong tool** → add tool priority guidance
- **Agent forgets context** → improve memory instructions
- **Task too complex** → add prose auto-trigger rule ("for 5+ questions, create .prose")
- **Agent shares private info in group** → tighten group chat rules
- **User repeats requests** → add numbered checklist requirement

## Default Template

See `references/default-agents-template.md` for the official default AGENTS.md that ships with OpenClaw.

## Best Practices

1. Start minimal, add rules only when you see problems
2. Every rule should earn its place — if you can't explain why, remove it
3. Use numbered checklists for multi-step procedures
4. Reference docs/ subfolders rather than embedding long content
5. Keep total AGENTS.md under 15,000 characters to leave room for other bootstrap files
6. After a week, ask the agent: "suggest improvements to your AGENTS.md"
7. All content in English — even if users communicate in other languages
