---
name: user-md
description: Guide for building USER.md — user profiles, preferences, roles, and communication styles. Use this skill whenever the user is setting up who will interact with the agent, mapping Telegram/Discord user IDs to names, configuring multi-user access, or defining communication preferences. Even questions like "how does the agent know who I am", "add a team member", or "set up user permissions" need this skill.
---

# USER.md Profile Building Guide

USER.md tells the agent WHO it's helping. It contains user profiles, preferences, communication styles, and context. Loaded into every session.

## Official Template Fields

```markdown
*Name:* (your name)
*What to call them:* (preferred address)
*Pronouns:* (optional)
*Timezone:* (e.g., America/New_York)
*Notes:* (anything relevant)
```

## Extended Profile Structure

For richer context, expand beyond the template:

```markdown
# USER.md

## Primary User
- Name: [Full name]
- Call me: [Preferred name/nickname]
- Pronouns: [optional]
- Timezone: America/New_York
- Role: [CEO / Developer / Lawyer / etc.]
- Language: [Ukrainian / English / bilingual]
- Communication style: [direct and brief / detailed / formal]

## Context
- Working on: [current projects, priorities]
- Cares about: [quality, speed, cost, compliance]
- Annoyed by: [long explanations, unnecessary questions, etc.]
- Expertise: [deep in X, learning Y]

## Preferences
- Response length: [brief unless asked otherwise]
- Code comments: [minimal / thorough]
- When uncertain: [ask / make best guess and flag]
- Follow-ups: [proactive / only when asked]
```

## Multi-User Setup

When multiple people interact with the agent (e.g., via Telegram group):

```markdown
## Users

### Alice (tg:USER_ID_1)
- Role: Founder, primary decision-maker
- Language: English
- Style: Direct, prefers brief responses
- Can approve: all actions

### Bob (tg:USER_ID_2)
- Role: Marketing lead
- Language: English/Spanish
- Style: Detailed, appreciates context
- Can approve: content publication, social media posts

### Charlie (tg:USER_ID_3)
- Role: Developer
- Language: English
- Style: Technical, code-first
- Can approve: deployments, code changes
```

## Mapping Telegram IDs to Users

OpenClaw identifies users by channel-prefixed IDs (e.g., `tg:USER_ID`). Map these in USER.md so the agent addresses people by name instead of ID.

Cross-reference with `openclaw.json`:
- `channels.telegram.allowFrom` — who can DM the agent
- `channels.telegram.groups[].allowFrom` — who can interact in groups

## What Data Is Needed

| Input | Source | What It Determines |
|-------|--------|-------------------|
| Names | Client team roster | How to address each person |
| Telegram user IDs | `openclaw.json` allowFrom | Map IDs to names |
| Roles | Org chart | Approval authority |
| Timezone | Client location | Time formatting, quiet hours |
| Language | User behavior | Response language |
| Communication style | User feedback | Formal vs casual, verbose vs terse |
| Domain expertise | User background | How technical to be |
| Permissions | Business rules | Who can approve what |

## Signals from Sessions That Improve USER.md

- **User corrects language** → update language preference
- **User asks to be more/less detailed** → update style
- **New team member starts messaging** → add their profile
- **User references their role** → capture and add
- **User expresses frustration** → add to "Annoyed by" section
- **User has recurring requests** → add to "Working on" context

## Philosophical Note

The template says: "The more you know, the better you can help. But remember — you're learning about a person, not building a dossier. Respect the difference."

Keep USER.md focused on what helps the agent serve better. Don't collect information that isn't relevant to the agent's function.

## Best Practices

1. Start with essential fields only (name, timezone, language, role)
2. Build up the profile organically from interactions
3. Let the agent suggest USER.md updates during memory curation
4. For multi-user setups, include Telegram/Discord IDs for mapping
5. Update when team composition changes
6. Keep total content under 3,000 characters for fast loading
