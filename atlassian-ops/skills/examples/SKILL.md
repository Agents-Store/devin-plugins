---
name: examples
description: This skill should be used when the user wants a worked end-to-end Jira/Confluence example or walkthrough — "show me a full Jira workflow", "example of planning an epic with stories", "issue lifecycle example", "build a Confluence space via the API", "generate release notes in Confluence from Jira", or wants to see several Atlassian API calls chained together for a real scenario.
---

# Atlassian Worked Examples

End-to-end scenarios that chain real Jira and Confluence REST calls. Each scenario lives in `references/scenarios/`. They assume the `setup` skill has run (so `ATLASSIAN_SITE_URL`, `ATLASSIAN_EMAIL`, `ATLASSIAN_API_TOKEN` are set) and reuse the conventions from `jira-operations` / `confluence-operations` (real verbs, ADF for Jira, version bump for Confluence, resolve names → ids, confirm destructive actions).

## Scenarios

| Scenario | File | What it demonstrates |
|----------|------|----------------------|
| Plan an epic with stories | `references/scenarios/plan-epic-and-stories.md` | Create an Epic → create child Stories linked to it → JQL report of the epic's children |
| Issue lifecycle | `references/scenarios/issue-lifecycle.md` | Create issue → add ADF comment → discover transitions → move In Progress → Done |
| Publish a Confluence space | `references/scenarios/publish-confluence-space.md` | Create space → parent + child pages (storage body) → update a page (version bump) → label → list |
| Release notes from Jira | `references/scenarios/release-notes-from-jira.md` | Cross-product: JQL on a fixVersion → format done issues → build a Confluence release-notes page |

## How to use

Pick the scenario closest to the user's goal, open its file, and adapt the names/keys/ids (project, issue, space, page) to the live site. When an exact method or field is unclear, open the matching `api-reference` `references/jira/*.md` or `references/confluence/*.md` file. When a call fails, switch to `troubleshoot`.

<example>
User: "Walk me through creating an epic and a few stories under it in Jira."
→ Open `references/scenarios/plan-epic-and-stories.md` and run it, substituting the project key and story summaries.
</example>

<example>
User: "Show me the full lifecycle of a Jira issue from creation to Done."
→ Open `references/scenarios/issue-lifecycle.md`; it chains create → comment → transitions → Done.
</example>

<example>
User: "Generate release notes in Confluence from the issues we shipped in 1.2.0."
→ Open `references/scenarios/release-notes-from-jira.md`; it runs a JQL on `fixVersion` and builds a Confluence page from the results.
</example>
