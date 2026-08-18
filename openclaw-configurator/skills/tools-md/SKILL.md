---
name: tools-md
description: Guide for optimizing TOOLS.md — environment-specific tool notes, search priorities, device names, and local infrastructure details. Use this skill whenever the user is configuring which tools their agent should prefer, adding environment notes, documenting search tool priority orders, or setting up device/API references. Even questions like "which search tool should my agent use first", "how do I tell the agent about my devices", or "add tool notes" need this skill.
---

# TOOLS.md Optimization Guide

TOOLS.md contains environment-specific notes about the tools available to the agent. It does NOT control tool access (that's in `openclaw.json`) — it provides guidance on HOW to use tools effectively in this specific environment.

## Official Template

```markdown
# TOOLS.md - Local Notes
Skills define HOW tools work. This file is for YOUR specifics.
```

The docs say: "Add whatever helps you do your job. This is your cheat sheet."

## What Goes Here

| Category | Examples |
|----------|---------|
| Search tool priorities | "Use Firecrawl for Ukrainian sites, EXA for English queries" |
| Camera names/locations | "Front door camera: cam-01" |
| SSH hosts and aliases | "Production: ssh prod@10.0.1.5" |
| TTS preferences | "Use ElevenLabs voice 'Rachel' for notifications" |
| Speaker/room names | "Living room speaker: sonos-living" |
| Device nicknames | "Desk lamp = hue-light-3" |
| API endpoints | Custom internal API URLs |
| Database connections | Connection string references (not credentials!) |

## Why Separate from Skills?

"Skills are shared. Your setup is yours." This separation enables:
- Updating skills without losing environment notes
- Sharing skills without exposing infrastructure
- Different agents using same skills with different tool configs

## Search Tool Priority Template

Data-driven tool priority based on session analysis:

```markdown
## Search Tools (priority order for [domain])

1. **Firecrawl** — best for [language/region] sites. [X]% success rate.
   Use for: scraping full page content, crawling sites
   Command: `firecrawl search "query" --scrape --limit 5`

2. **Perplexity** — good for overview + synthesis.
   Use for: quick summaries, multi-source answers

3. **EXA** — best for English queries. NOTE: [X]% fail rate on [language] text.
   Workaround: translate queries to English first

4. **Deep Research** — for comprehensive analysis (combines multiple providers).
   Use for: research tasks requiring 3+ sources
```

## Optimizing TOOLS.md from Session Data

Analyze session logs to determine optimal tool configuration:

1. **Most used tools** — ensure they're documented with correct syntax
2. **Tools with high error rates** — add workarounds and alternatives
3. **Tools never used** — consider if they're needed, or if agent doesn't know about them
4. **Domain-specific tools** — add usage notes for specialized tools

## What Data Is Needed

| Input | Source | What It Determines |
|-------|--------|-------------------|
| Installed skills | `ls workspace/skills/` + extraDirs | Available tools |
| Skill SKILL.md files | Read each SKILL.md | Commands and syntax |
| API endpoints | Client infrastructure | Custom URLs |
| Search priority | Domain needs | Which tool first |
| Tool performance | Session log analysis | Success/fail rates |
| Custom scripts | workspace/scripts/ | CLI utilities |

## Signals from Sessions That Improve TOOLS.md

- **Tool call fails repeatedly** → add workaround note
- **Agent uses suboptimal tool** → add priority guidance
- **New skill installed** → add usage notes
- **Agent doesn't know about a tool** → document it
- **Tool works differently than expected** → add clarification

## Best Practices

1. Lead with the most-used tools
2. Include success rates when available (from session analysis)
3. Add workarounds for known issues
4. Keep credentials out — reference env vars instead
5. Update when skills or infrastructure change
6. Group by function (search, media, communication, home automation)
