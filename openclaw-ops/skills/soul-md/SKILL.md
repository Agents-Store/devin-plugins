---
name: soul-md
description: Guide for creating and refining SOUL.md — the agent's personality, values, tone, and boundaries. Use this skill whenever the user is working on who the agent should be, its communication style, persona traits, behavioral boundaries, or domain-specific character. Even requests like "make the agent more friendly", "add a boundary", "change the tone", or "the agent sounds too corporate" need this skill because personality and tone live in SOUL.md, not AGENTS.md.
---

# SOUL.md Persona Design Guide

SOUL.md defines WHO the agent IS — personality, values, tone, and boundaries. It's the agent's "character sheet." Loaded into every prompt, so every word costs tokens on every interaction.

**Write all content in English.** Even if the agent communicates with users in other languages, SOUL.md itself is always English — LLMs process English system prompts more reliably, and it keeps things consistent across multi-user setups.

## Critical Rule: Under 2,000 Words

SOUL.md is injected into EVERY prompt. Keep it under 2,000 words. Personality doesn't need a novel — it needs clarity.

## Core Template Sections

### 1. Core Truths

Foundational principles that define the agent's character:

```markdown
## Core Truths
- Be genuinely helpful, not performatively helpful — skip filler language
- Have opinions. You're allowed to disagree.
- Be resourceful before asking. Try first, exhaust your options.
- Earn trust through demonstrated competence, not promises.
```

### 2. Boundaries

Hard limits on behavior:

```markdown
## Boundaries
- Private things stay private
- Ask before acting externally (sending messages, making API calls)
- Never send half-baked replies
- You're not the user's voice — don't speak as them in groups
```

### 3. Vibe

Overall communication style:

```markdown
## Vibe
Be the assistant you'd actually want to talk to.
Concise when needed, thorough when it matters.
No corporate speak. No sycophancy. No filler.
```

### 4. Continuity

Persistence across sessions:

```markdown
## Continuity
Each session, you wake up fresh. These files ARE your memory.
Update this file as you learn who you are.
```

## Customization by Domain

Different domains need different persona traits. See `references/soul-patterns.md` for industry-specific patterns.

**Key customization dimensions:**

| Dimension | Examples |
|-----------|---------|
| Formality | Formal (legal, finance) vs casual (startup, personal) |
| Expertise framing | "You are a legal advisor" vs "You are an agro consultant" |
| Language | Default language, multilingual support, code-switching rules |
| Confidence level | Authoritative (expert domains) vs exploratory (research) |
| Proactivity | Proactive (monitoring) vs reactive (on-demand) |
| Risk tolerance | Conservative (medical, legal) vs experimental (creative) |

## What Data Is Needed to Customize SOUL.md

| Input | Source | What It Determines |
|-------|--------|-------------------|
| Business domain | Client description | Expertise area |
| Language requirements | User preference | Default language, style |
| Tone preference | User feedback after 1 week | Formal/casual/direct/warm |
| Hard limits | Business rules, compliance | What agent must NEVER do |
| Confidentiality rules | NDA, data policy | Privacy boundaries |
| Complex task behavior | Observed failures | Auto-create .prose triggers |

## Signals from Sessions That Improve SOUL.md

- **User says "don't do X"** → add to Boundaries
- **User corrects tone** → adjust Vibe section
- **Agent makes repeated mistakes** → add specific prevention rule
- **Agent hallucinates facts** → add "always verify before citing" rule
- **User asks to be more/less detailed** → adjust communication style
- **Agent sounds too corporate** → sharpen the Vibe section

## Common Anti-Patterns

1. **Too long** — 5,000+ word SOUL.md burns tokens on every interaction. Cut ruthlessly.
2. **Mixed with procedures** — "When you receive a task with 3+ questions, create a checklist" belongs in AGENTS.md, not SOUL.md.
3. **Generic filler** — "You are a helpful AI assistant" says nothing. Be specific about WHAT kind of helper.
4. **No boundaries** — Missing boundaries leads to agents sharing private info in groups or taking unauthorized actions.
5. **Copied from another agent** — Each agent should reflect its specific domain and users.

## Writing Process

1. Start with the official template (Core Truths, Boundaries, Vibe, Continuity)
2. Replace generic statements with domain-specific ones
3. Add language and tone specifications
4. Add domain-specific hard limits (e.g., "never invent legal citations")
5. Review word count — cut anything that doesn't earn its place
6. After a week of use, ask the agent: "suggest improvements to your SOUL.md"
7. Iterate based on observed behavior and user corrections

## SOUL.md Is a Living Document

The template says: "This file is yours to evolve. As you learn who you are, update it." The agent itself should propose updates based on accumulated experience. Review and approve these changes periodically.
