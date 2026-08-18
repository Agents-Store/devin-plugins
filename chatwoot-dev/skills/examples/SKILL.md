---
name: examples
description: This skill should be used when the user wants a worked, end-to-end Chatwoot example — "show me a full Chatwoot integration", "seed a conversation via the API", "build a Chatwoot bot example", "bulk import contacts", or "triage Chatwoot from the terminal" — combining setup, the REST API, the CLI, and webhooks into a complete scenario.
---

# Chatwoot Worked Examples

End-to-end scenarios that combine the other skills (`setup`, `api-reference`, `cli-recipes`,
`webhooks-automation`). Each scenario is a self-contained walkthrough in `references/scenarios/`.
Read the one that matches the task; all commands assume the env vars from the `setup` skill.

| Scenario | File | Skills exercised |
|----------|------|------------------|
| Seed a conversation through the **Public/Client API** (contact → conversation → message), the way a custom widget would | `references/scenarios/seed-conversation-via-api.md` | setup, api-reference (client) |
| Build an **agent bot** that listens to a webhook and replies via the Application API | `references/scenarios/agent-bot-webhook.md` | setup, webhooks-automation, api-reference |
| **Bulk import contacts** with custom attributes and search them back | `references/scenarios/bulk-contact-import.md` | api-reference (application), pagination |
| **Triage conversations from the terminal** with the `chatwoot` CLI | `references/scenarios/triage-from-terminal.md` | cli-recipes, safety |

## How to use these

1. Confirm credentials with the `setup` skill (`CHATWOOT_BASE_URL`, `CHATWOOT_API_KEY`,
   `CHATWOOT_ACCOUNT_ID`).
2. Pick the scenario closest to the goal and adapt the IDs/payloads.
3. For any customer-visible write (replies, status, labels), show the exact request and
   confirm before running — see the safety guidance in `cli-recipes`.
