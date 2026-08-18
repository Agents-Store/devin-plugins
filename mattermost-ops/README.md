# mattermost-ops (Devin plugin)

Mattermost collaboration ops plugin. Drive the full Mattermost REST API v4 by curl — users, teams, channels (public/private/DM/group), posts & threads, reactions, files, custom emoji, webhooks, slash commands, bots, OAuth apps, plus system administration: config, RBAC roles & schemes, LDAP/SAML groups, compliance, data retention, plugins, jobs, and analytics. Authenticates with MATTERMOST_ADMIN_USERNAME + MATTERMOST_ADMIN_PASSWORD to obtain a session token against MATTERMOST_API_URL.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (5)

- `api-reference` — This skill should be used when the user asks for "Mattermost API endpoints", "Mattermost REST API", "Mattermost curl examples", "Mattermost API documentation", the exact path/method for any Mattermost resource, or needs HTTP details for users, teams, channels, posts, reactions, files, emoji, webhooks, slash commands, bots, OAuth apps, system config, roles, schemes, groups, LDAP/SAML, compliance, or data retention. Index into the full per-domain endpoint catalog.
- `common-operations` — This skill should be used when the user wants to do collaboration work in Mattermost — "post a message to a channel", "send a DM in Mattermost", "create a channel", "add users to a team/channel", "deactivate a user", "create a team", "set up a webhook", "react to a post", or any everyday Mattermost operation. Provides plain-language workflows that drive the REST API and route to the exact endpoints.
- `examples` — This skill should be used when the user wants a worked end-to-end Mattermost example or walkthrough — "show me a full Mattermost workflow", "example of onboarding a team in Mattermost", "how do I broadcast a message to several channels via the API", "end-to-end channel management example", or wants to see several Mattermost API calls chained together for a real scenario.
- `setup` — This skill should be used when the user wants to "connect to Mattermost", "log into Mattermost", "authenticate with Mattermost", "get a Mattermost token", "set up Mattermost access", or before running any Mattermost REST API call. Establishes the session token (read from the login Token response header) and the global request conventions (base path, headers, pagination, rate limits).
- `troubleshoot` — This skill should be used when a Mattermost REST API call fails or behaves unexpectedly — "Mattermost returns 401 / 403 / 404 / 429", "Mattermost login fails", "I got no token after login", "can't find the channel/user", "pagination missing results", "permission denied", or any Mattermost error response. Maps symptoms to causes and fixes.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/mattermost-ops
