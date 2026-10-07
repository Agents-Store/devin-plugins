# vaultwarden-dev (Devin plugin)

Vaultwarden dev plugin for Agents Store. Script and integrate a self-hosted Vaultwarden (Bitwarden-compatible) server: what the client API can and cannot do under end-to-end encryption, the identity token flows, organization member management, the /admin panel API, the Bitwarden CLI (bw, bw serve), python-vaultwarden and Terraform, client/server version compatibility, troubleshooting, and a guard hook that asks before a command prints decrypted secrets into the chat. File-based knowledge, no MCP, no stored credentials.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (9)

- `admin-panel` — This skill should be used when the user asks to "use the Vaultwarden admin API", "script the /admin panel", "disable or delete a Vaultwarden user", "reset a user's 2FA", "change Vaultwarden config", or mentions ADMIN_TOKEN or the VW_ADMIN cookie.
- `api-reference` — Manual reference (invoke /vaultwarden-dev:api-reference) for "Vaultwarden API endpoints", "Vaultwarden REST API routes", "Vaultwarden token grants", "Vaultwarden curl examples" — exact HTTP routes, payloads and auth of a Vaultwarden server.
- `cli-recipes` — This skill should be used when the user asks to "use bw with Vaultwarden", "get a password from Vaultwarden in a script", "create a Vaultwarden item from the CLI", "confirm org members with bw", "run bw serve", or needs Bitwarden CLI recipes for a self-hosted Vaultwarden.
- `examples` — This skill should be used when the user asks "how do I onboard/offboard someone in Vaultwarden", "show a Vaultwarden CI pipeline example", "back up and upgrade Vaultwarden", or wants an end-to-end walkthrough combining the admin panel, client API and bw CLI.
- `mcp-patterns` — This skill should be used when the user asks for "a Vaultwarden MCP server", "connect Claude to my Vaultwarden", "use the Bitwarden MCP server with Vaultwarden", "warden-mcp", or wants an agent to query a self-hosted vault through MCP tools instead of shell commands.
- `sdk-patterns` — This skill should be used when the user asks for a "Vaultwarden SDK" or "Bitwarden SDK for Vaultwarden", to "automate Vaultwarden from Python", "use python-vaultwarden", "manage Vaultwarden with Terraform", or wants a library rather than curl/bw for a self-hosted Vaultwarden.
- `secret-hygiene` — This skill should be used when a Vaultwarden or bw task could print, log or store a secret — "store BW_SESSION", "show me the password from Vaultwarden", "export the vault in plain text", "put the master password in a script" — to keep secrets out of chat, logs, git and argv.
- `setup` — This skill should be used when the user asks to "connect to Vaultwarden", "point bw at my Vaultwarden server", "check Vaultwarden is reachable", "get a Vaultwarden API token", "call the Vaultwarden REST API", "manage org members via the API", or "sync users from LDAP into Vaultwarden".
- `troubleshoot` — This skill should be used when the user reports Vaultwarden errors — "Username or password is incorrect" with the right password, "404 on user-key-id", "Vaultwarden 401 or 429", "invites not arriving", "bw sync hangs" — or needs to diagnose a self-hosted Vaultwarden or bw failure.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents
- 1 command(s) — Devin plugins do not support commands
- hooks — Devin plugins do not support hooks

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/vaultwarden-dev
