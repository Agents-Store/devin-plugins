---
name: examples
description: This skill should be used when the user wants a worked end-to-end Outline example or walkthrough — "show me a full Outline workflow", "example of building a knowledge base in Outline", "how do I publish and share a doc via the API", "document lifecycle example", "onboard users to Outline", or wants to see several Outline API calls chained together for a real scenario.
---

# Outline Worked Examples

End-to-end scenarios that chain real Outline REST calls. Each scenario lives in `references/scenarios/`. They assume the `setup` skill has run (so `OUTLINE_API_URL` and `OUTLINE_API_KEY` are set) and reuse the conventions from `common-operations` (POST to `${OUT}/<method>`, read `.data`, resolve titles → ids, confirm destructive actions).

## Scenarios

| Scenario | File | What it demonstrates |
|----------|------|----------------------|
| Publish a knowledge base | `references/scenarios/publish-knowledge-base.md` | Create a collection → create nested docs → publish → share publicly → star |
| Document lifecycle | `references/scenarios/document-lifecycle.md` | Draft → update (append/patch) → move → archive → restore → trash → restore from trash |
| Search & report | `references/scenarios/search-and-report.md` | Full-text & title search → list by collection → view counts → insights → audit-log events |
| Onboard users & permissions | `references/scenarios/onboard-users-permissions.md` | Invite users → create a group → add members → grant collection & document access |

## How to use

Pick the scenario closest to the user's goal, open its file, and adapt the names/ids (collection, document, user, group) to the live workspace. When an exact method or field is unclear, open the matching `api-reference` `references/*.md` file. When a call fails, switch to `troubleshoot`.

<example>
User: "Walk me through standing up a new knowledge base in Outline and sharing the homepage."
→ Open `references/scenarios/publish-knowledge-base.md` and run it, substituting the collection name, document titles, and bodies.
</example>

<example>
User: "Show me the full lifecycle of a document — draft, edit, archive, restore."
→ Open `references/scenarios/document-lifecycle.md`; it chains create → update → move → archive → restore → delete.
</example>

<example>
User: "Give me a usage report of our most active docs this month."
→ Open `references/scenarios/search-and-report.md`; it chains search, list, views, insights, and events into a report.
</example>
