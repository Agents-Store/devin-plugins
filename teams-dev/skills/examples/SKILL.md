---
name: examples
description: Use this skill when the user wants a worked, end-to-end scenario for a Microsoft Teams app — a full walkthrough for an echo bot, an AI quote agent, an Adaptive Card form, a message-extension search command, or an SSO + Microsoft Graph bot. Triggers on "Teams bot example", "full example Teams", "end-to-end Teams scenario", "echo bot example", "Teams SSO example".
---

# Examples — end-to-end scenarios

Each scenario is a complete walkthrough: CLI commands, files to create or edit, code, manifest changes, and sideload steps. Pick the closest match and adapt.

| Scenario | What it demonstrates | File |
|---|---|---|
| Echo bot | Minimum viable bot | `references/scenarios/echo-bot.md` |
| AI quote agent | `ChatPrompt` + streaming in 1:1 | `references/scenarios/ai-quote-agent.md` |
| Adaptive Card form | Card with inputs + `card.action.<id>` | `references/scenarios/adaptive-card-form.md` |
| Message-extension search | `message.ext.query` + results list | `references/scenarios/message-extension-search.md` |
| SSO + Graph bot | OAuth → on-behalf-of → `api.graph.me.events.list` | `references/scenarios/sso-graph-bot.md` |

## How to use a scenario

1. Read it top-to-bottom once.
2. Run the listed `teams project new …` (or `teams project new + add-feature` if extending an existing project).
3. Apply each diff in order — they are written to compile after every step, not only at the end.
4. Run `npm run dev` and follow the verification block.
5. Sideload via the Teams Developer Portal.

Scenarios are intentionally short. Cross-link to the deep-dive skills (`messaging`, `adaptive-cards`, `ai-agents`, `authentication`, `graph-integration`) when you need more depth on a step.
