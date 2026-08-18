# Workspace Subfolders — On-Demand Reference Files

## How It Works

Only 7 core files are auto-injected into every session (AGENTS.md, SOUL.md, USER.md, IDENTITY.md, TOOLS.md, HEARTBEAT.md, MEMORY.md). BOOTSTRAP.md is also auto-injected when present on new workspaces (deleted after bootstrap completes). Everything else — including BOOT.md, agent-created files, and subfolders — lives in workspace/ but is NOT loaded into context automatically. The agent reads them when needed via the `read` tool. This saves tokens — files are loaded only when relevant.

## Structure

```
workspace/
├── AGENTS.md              ← references docs/ below
├── SOUL.md
├── USER.md
├── ...
├── docs/
│   ├── rules/             ← extended rules that don't fit in AGENTS.md
│   ├── procedures/        ← how to do specific tasks
│   ├── clients/           ← client context and background
│   └── standing-orders/   ← recurring automated tasks
├── workflows/
│   └── *.prose            ← prose workflow files
├── canvas/                ← canvas UI files (optional)
├── skills/                ← instance-specific skills
│   └── */SKILL.md
└── memory/
    └── YYYY-MM-DD.md      ← daily logs (auto-created)
```

## What Goes WHERE

| Content | Put in | Why |
|---------|--------|-----|
| Core identity, tone, hard limits | SOUL.md | Needed every message |
| Memory rules, task routing, session startup | AGENTS.md | Needed every message |
| Tool commands, search priority | TOOLS.md | Needed every message |
| User profiles, timezone, language | USER.md | Needed every message |
| Extended security rules | docs/rules/security.md | Only when relevant |
| Data classification policy | docs/rules/data-classification.md | Only when handling sensitive data |
| Group chat policy details | docs/rules/group-chat-policy.md | Only in group contexts |
| How to do a specific task type | docs/procedures/task-name.md | Only for that task |
| Client background, contracts | docs/clients/client-name.md | Only for that client |
| Weekly report instructions | docs/standing-orders/weekly-report.md | Only on report day |
| Complex multi-step workflow | workflows/workflow-name.prose | Only when triggered |

## The 50% Rule

- If content is needed in **>= 50% of sessions** → keep it in auto-injected files (AGENTS.md, SOUL.md, etc.)
- If content is needed in **< 50% of sessions** → move it to docs/
- If content is **critical for safety** → keep it in AGENTS.md or SOUL.md regardless

## How to Reference from AGENTS.md

Add a section like this to AGENTS.md:

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

## How the Agent Uses It

1. User asks: "Prepare analysis for ClientX"
2. Agent sees "docs/clients/" in AGENTS.md
3. Agent runs: `read docs/clients/clientx.md`
4. Agent gets full context, then works

No extra tokens burned in sessions where this topic is not mentioned.

## File Naming Rules

- Lowercase letters, hyphens for spaces
- Descriptive names (not abbreviations): `contract-review.md` not `CR.md`
- One topic per file — agent reads the whole file when referenced
- Keep individual files under 10,000 characters for fast loading

## Template: docs/procedures/

```markdown
# [Procedure Name]

## When to Use
[Describe when this procedure applies]

## Steps
1. [First step]
2. [Second step]
3. [Third step]

## Output Format
[What the result should look like]

## Common Mistakes
- [Mistake to avoid]
- [Another mistake]

## Related Docs
- docs/rules/[relevant-rule].md
```

## Template: docs/clients/

```markdown
# [Client Name]

## Profile
- Industry: ...
- Key services: ...
- Main contacts: ...

## Current Projects
- Project A: status, deadlines, notes
- Project B: status, deadlines, notes

## Preferences
- Communication language: ...
- Report format: ...
- Escalation rules: ...

## Key Facts
- [Important context the agent should know]
```

## Template: docs/rules/

```markdown
# [Rule Name]

## Scope
[When this rule applies]

## Rules
1. [Rule statement]
2. [Rule statement]
3. [Rule statement]

## Exceptions
- [When this rule does NOT apply]

## Escalation
- [What to do if rule conflicts with user request]
```

## Template: docs/standing-orders/

See the **standing-orders** skill for detailed standing order templates and patterns.

## Adding a New Doc

1. Create file: `docs/<folder>/<name>.md`
2. Add reference to AGENTS.md (one line in the relevant section)
3. Done — agent reads it when needed

## Removing a Doc

1. Delete the file
2. Remove the reference from AGENTS.md
3. Done — agent stops looking for it
