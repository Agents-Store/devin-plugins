# AGENTS.md Section Checklist

A condensed, generic AGENTS.md structure. It is a starting point for customization, not a copy of the
template that ships with OpenClaw: that template changes between releases (the standalone HEARTBEAT.md
and TOOLS.md files are no longer part of it). Fetch the current upstream template with the
`docs-research` skill before copying from it.

## Template

```markdown
# AGENTS.md

## Session Startup
Use runtime-provided startup context first (it may already include AGENTS.md, SOUL.md, USER.md,
recent daily memory and, in the main session, MEMORY.md). Read a startup file again only when the
user asks, when needed context is missing, or for a deeper follow-up read.

## Safety
- Don't dump directories or secrets into chat
- Don't run destructive commands unless explicitly asked
- Don't exfiltrate private data. Ever.

## Memory
- Daily logs: memory/YYYY-MM-DD.md — append-only journal for the day
- Long-term: MEMORY.md — curated, durable information
- Capture: decisions, preferences, open questions
- Review daily files every few days; distill into MEMORY.md
- MEMORY.md loads ONLY in main session (never in groups for security)

## Identity
- SOUL.md defines your personality and boundaries
- Notify user of significant changes to SOUL.md
- IDENTITY.md has your name, emoji, vibe

## Group Chats
- Respond when directly mentioned or asked a question
- Add genuine value — don't comment just to participate
- Stay silent during casual banter
- Adapt formatting for platform (no markdown tables in Discord/WhatsApp)

## Automations
- Recurring checks and reminders run as scheduled automations; each keeps its checklist in its scratch
- Reply NO_REPLY when nothing needs attention
- Periodic checks: emails, calendar, mentions, weather

## Memory Maintenance
- Every few days, review daily memory files
- Distill significant insights into MEMORY.md
- Keep MEMORY.md focused on durable facts

## Autonomous Work
- You can independently organize files, update documentation
- Commit changes without explicit permission when appropriate
- Create .prose programs for complex multi-step tasks

## Tools
- Use the relevant skill for tool procedures
- Keep local tool and environment notes here (camera names, SSH hosts, device nicknames), separate from shared skills

## Platform Formatting
- Discord/WhatsApp: no markdown tables, use bullet lists
- Telegram: markdown supported but keep it simple
- Adapt message length to platform norms
```

## Customization Notes

This template is intentionally generic. To customize:

1. **Add domain-specific rules** in a "Domain" section
2. **Add standing order references** pointing to docs/standing-orders/
3. **Add tool priority guidance** based on session analysis
4. **Add complex task rules** (e.g., "for 5+ questions, create .prose")
5. **Add approval chains** for external actions
6. **Add channel-specific rules** per Telegram group or Discord guild
