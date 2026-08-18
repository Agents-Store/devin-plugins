# atlassian-ops (Devin plugin)

Atlassian Jira + Confluence Cloud ops plugin. Drive the full Jira Cloud REST API v3 and Confluence Cloud REST API v2 by curl — Jira: issues (create/edit/transition/assign, ADF bodies), JQL search, comments & worklogs, attachments & links, projects/versions/components, fields & screens, workflows/types/statuses, users & groups (accountId), permission/notification/security schemes, dashboards & filters, plans & teams; Confluence: pages & blog posts (versioned, storage/ADF bodies), spaces & permissions, comments & attachments, labels & content properties. Authenticates with Atlassian Cloud Basic auth (ATLASSIAN_EMAIL + ATLASSIAN_API_TOKEN) against ATLASSIAN_SITE_URL.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (6)

- `api-reference` — This skill should be used when the user asks for "Jira API endpoints", "Confluence API endpoints", "Jira/Confluence REST API", "Atlassian curl examples", "the exact method/parameters" for any Jira or Confluence resource, or needs HTTP details for issues, JQL search, comments, worklogs, attachments, links, projects, versions, components, fields, screens, workflows, statuses, users, groups, permissions, schemes, dashboards, filters, plans; or Confluence pages, blog posts, spaces, comments, attachments, labels, content properties. Indexes the full per-domain endpoint catalog plus the bundled OpenAPI specs.
- `confluence-operations` — This skill should be used when the user wants to do Confluence work — "create a Confluence page", "update a page", "edit a wiki page", "create a child page", "create a space", "list spaces", "comment on a page", "add a label", "attach a file in Confluence", or any everyday Confluence operation. Provides plain-language playbooks that drive the Confluence Cloud REST API v2.
- `examples` — This skill should be used when the user wants a worked end-to-end Jira/Confluence example or walkthrough — "show me a full Jira workflow", "example of planning an epic with stories", "issue lifecycle example", "build a Confluence space via the API", "generate release notes in Confluence from Jira", or wants to see several Atlassian API calls chained together for a real scenario.
- `jira-operations` — This skill should be used when the user wants to do Jira work — "create a Jira issue", "search Jira", "run a JQL query", "transition an issue", "move an issue to Done", "assign an issue", "comment on an issue", "log work / log time", "create a Jira project", "create a version/release", "add an attachment", or any everyday Jira operation. Provides plain-language playbooks that drive the Jira Cloud REST API v3.
- `setup` — This skill should be used when the user wants to "connect to Jira", "connect to Confluence", "authenticate with Atlassian", "set up Jira/Confluence access", "use my Atlassian API token", or before running any Jira or Confluence REST API call. Establishes Atlassian Cloud Basic auth (email + API token) and the global conventions both APIs share (base paths, headers, Jira startAt/maxResults vs Confluence cursor pagination, ADF/storage body formats, accountId).
- `troubleshoot` — This skill should be used when a Jira or Confluence REST API call fails or behaves unexpectedly — "Jira/Confluence returns 401 / 403 / 404 / 400 / 409 / 429", "Atlassian API token not working", "ADF error / body must be ADF", "page won't update / version conflict", "can't find the page/issue", "wrong base URL", "CQL not working in v2", "boards/sprints endpoint not found", or any Atlassian error response. Maps symptoms to causes and fixes.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/atlassian-ops
