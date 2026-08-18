---
name: examples
description: Complete end-to-end workspace customization examples for different industries — legal firms, dev teams, marketing agencies, customer support, personal assistants, and content creators. Use this skill whenever the user wants to see a reference implementation, asks "how would you set up OpenClaw for X", wants to see what a complete workspace looks like, or needs a starting template for their industry. Even vague requests like "show me an example" or "what does a good workspace look like" should trigger this skill.
---

# Workspace Customization Examples

Complete end-to-end examples of OpenClaw workspace configurations for different industries and use cases. Each scenario shows all workspace files working together.

## Available Scenarios

| Scenario | Use Case | Key Features |
|----------|----------|-------------|
| [Legal Firm](references/scenarios/legal-firm.md) | Law firm with legal research, compliance, client management | Strict accuracy rules, citation requirements, confidentiality |
| [Dev Team](references/scenarios/dev-team.md) | Software development team with CI/CD, code review, deployments | Technical precision, deployment safety, code-first communication |
| [Personal Assistant](references/scenarios/personal-assistant.md) | Individual productivity, scheduling, research, communications | Proactive, warm tone, broad capability, privacy-focused |
| [Marketing Agency](references/scenarios/marketing-agency.md) | Content creation, social media, client brand management | Creative + analytical, brand voice matching, approval workflows |
| [Customer Support](references/scenarios/customer-support.md) | Support team handling tickets, FAQs, escalations | Empathetic, resolution-focused, escalation rules, SLA tracking |
| [Content Creator](references/scenarios/content-creator.md) | Individual content creator, writing, research, publishing | Creative partner, voice matching, workflow support |

## How to Use These Scenarios

1. **Pick the closest scenario** to your use case
2. **Read the full scenario** from references/scenarios/
3. **Adapt** — replace placeholders with your specific details
4. **Combine elements** — take the SOUL.md from one scenario and AGENTS.md from another if your use case is hybrid
5. **Start minimal** — don't copy everything; begin with SOUL.md + AGENTS.md + USER.md, add others as needed

## Common Patterns Across All Scenarios

### SOUL.md Pattern
Every good SOUL.md has:
- Domain-specific expertise statement
- 3-5 core values relevant to the domain
- Clear boundaries (what NOT to do)
- Communication style guidance
- Under 2,000 words

### AGENTS.md Pattern
Every good AGENTS.md has:
- Session startup checklist
- Memory management rules
- Red lines / safety rules
- Group chat behavior (if applicable)
- Tool usage priorities
- Complex task handling rules

### USER.md Pattern
Every good USER.md has:
- Primary user profile (name, timezone, language)
- Communication preferences
- Domain expertise level
- Approval authority

### Workspace Structure Pattern
Every well-organized workspace has:
```
workspace/
├── Core files (AGENTS, SOUL, USER, IDENTITY, TOOLS)
├── HEARTBEAT.md (if periodic tasks needed)
├── MEMORY.md (curated long-term memory)
├── docs/
│   ├── procedures/    (domain-specific workflows)
│   ├── standing-orders/ (autonomous programs)
│   └── [domain]/      (domain-specific reference docs)
└── memory/            (daily logs, auto-managed)
```

## Quick Start: Minimal Viable Workspace

For any use case, start with these three files:

### 1. SOUL.md (under 500 words to start)
```markdown
## Core Truths
- [2-3 domain-specific values]
- Be resourceful before asking

## Boundaries
- [2-3 hard limits specific to your domain]

## Vibe
[One sentence describing communication style]
```

### 2. AGENTS.md (under 1,000 words to start)
```markdown
## Session Startup
1. Read SOUL.md, USER.md
2. Read today's memory file

## Safety
- Don't run destructive commands without confirmation
- Keep private data private

## Memory
- Daily logs in memory/YYYY-MM-DD.md
- Long-term facts in MEMORY.md (main session only)
```

### 3. USER.md (minimal profile)
```markdown
- Name: [your name]
- Timezone: [your timezone]
- Language: [preferred language]
- Style: [brief/detailed, formal/casual]
```

Then iterate: add IDENTITY.md, TOOLS.md, HEARTBEAT.md, and docs/ as needs arise.
