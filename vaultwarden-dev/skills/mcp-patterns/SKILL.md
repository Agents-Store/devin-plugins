---
name: mcp-patterns
description: This skill should be used when the user asks for "a Vaultwarden MCP server", "connect Claude to my Vaultwarden", "use the Bitwarden MCP server with Vaultwarden", "warden-mcp", or wants an agent to query a self-hosted vault through MCP tools instead of shell commands.
---

# MCP Servers for Vaultwarden

This plugin ships **no** MCP server: a vault MCP needs the user's own server URL and unlock credentials, which a shared plugin cannot carry. The user wires one up in their own Claude Code configuration. Two servers are worth considering; both drive the official `bw` CLI underneath, so the version rules in `vaultwarden-dev:troubleshoot` apply.

| | `@icoretech/warden-mcp` | `@bitwarden/mcp-server` (official) |
|---|---|---|
| Target | Vaultwarden first (CI-tested against it) | Bitwarden cloud / self-hosted Bitwarden |
| Version (2026-10) | 0.2.50, MIT | 2026.7.0, GPL-3.0 |
| Unlock | from env (`BW_PASSWORD` + API key or `BW_USER`) | a pre-made `BW_SESSION`, or its `unlock` tool (opens a native OS dialog — fails on headless machines) |
| Secret output | **redacted by default**; `NOREVEAL=true` forces it | returns secrets in tool results |
| Read-only switch | `READONLY=true` | — |
| Org tools on Vaultwarden | none (no member management) | collections/members/groups/policies/events use the Bitwarden Public API — **404 on Vaultwarden**; only vault-side tools work |
| Transport | stdio, or Streamable HTTP without auth (keep to stdio) | stdio only; "must never be hosted publicly" |

Recommendation: `warden-mcp` in stdio mode with `NOREVEAL=true` (and `READONLY=true` unless the agent must write). Member and server administration stays with the client API, `python-vaultwarden` or the admin panel — no MCP server covers it on Vaultwarden.

## Configure warden-mcp (stdio)

Put credentials in the environment Claude Code starts with (for a project: the `env` block of the gitignored `.claude/settings.local.json`; or the user's own shell profile fed from an OS keychain) and reference them from a project `.mcp.json` that never holds a literal value:

```json
{
  "mcpServers": {
    "warden": {
      "command": "npx",
      "args": ["-y", "@icoretech/warden-mcp@0.2.50", "--stdio"],
      "env": {
        "BW_HOST": "${VW_URL}",
        "BW_CLIENTID": "${BW_CLIENTID}",
        "BW_CLIENTSECRET": "${BW_CLIENTSECRET}",
        "BW_PASSWORD": "${BW_PASSWORD}",
        "NOREVEAL": "true",
        "READONLY": "true"
      }
    }
  }
}
```

The tools then appear as `mcp__warden__keychain_<tool>` (prefix configurable with `TOOL_PREFIX`), e.g. `keychain_status`, `keychain_sync`, `keychain_search_items`, `keychain_get_item`, `keychain_list_folders`, `keychain_list_org_collections`, `keychain_generate`, and — without `READONLY` — `keychain_create_login`, `keychain_update_item`, `keychain_delete_item`, `keychain_move_item_to_organization`. Export/import are intentionally not exposed. The version is pinned on purpose: this process holds the unlocked vault, so a new upstream release should be read and tested before it runs — bump the pin deliberately.

## Configure the official Bitwarden MCP server

Point the CLI at Vaultwarden first — the server inherits that config — then hand it a session:

```bash
bw config server "$VW_URL" && bw login --apikey
read -r -s -p "master password: " BW_PASSWORD && export BW_PASSWORD && echo   # typed by the user, never pasted into chat
export BW_SESSION="$(bw unlock --passwordenv BW_PASSWORD --raw)"; unset BW_PASSWORD
```

```json
{
  "mcpServers": {
    "bitwarden": {
      "command": "npx",
      "args": ["-y", "@bitwarden/mcp-server@2026.7.0"],
      "env": {
        "BW_SESSION": "${BW_SESSION}"
      }
    }
  }
}
```

Leave `BW_CLIENT_ID` / `BW_CLIENT_SECRET` (organization key) unset against Vaultwarden: they only enable the Public-API organization tools, which Vaultwarden does not serve. `BW_ALLOWED_DIRECTORIES` must be set before file tools (file Sends, attachments) work. Requires Node.js 22+.

## Using vault MCP tools safely

- Search and list first; fetch a single item only when its secret is needed for the next step, and pass it on without repeating it in the reply. Results of MCP tools are in the transcript exactly like Bash output.
- The plugin's guard hook watches Bash only — MCP tool results are not intercepted. Prefer the redacting server, and follow `vaultwarden-dev:secret-hygiene`.
- Writes through MCP happen with the unlocked user's full rights. Show the target item (id, name, collection) and get confirmation before update, delete or move.

<example>
User: "Find which collection holds the staging Redis credentials."
Call `mcp__warden__keychain_search_items` with the text "redis staging", report `id`, `name`, `collectionIds`, and resolve the collection names with `mcp__warden__keychain_list_org_collections`. No password is requested or shown.
</example>

<example>
User: "Use the Bitwarden MCP to invite alice to our org."
Explain that the official server's member tools call the Bitwarden Public API, which Vaultwarden does not implement, so the call would return 404. Invite through `POST /api/organizations/<org-uuid>/users/invite` ([client API routes](../api-reference/references/client-api.md)) or `python-vaultwarden` instead.
</example>
