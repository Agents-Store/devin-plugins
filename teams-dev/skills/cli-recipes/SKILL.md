---
name: cli-recipes
description: Use this skill when the user is invoking the Microsoft Teams Developer CLI (`teams`) — scaffolding projects with `teams project new`, listing or updating apps with `teams app list/get/update`, checking auth status, or upgrading the CLI itself. Triggers on "teams CLI", "teams project new", "teams app update", "teams self-update", "teams status".
---

# Teams Developer CLI recipes

The `teams` CLI bundles project scaffolding, app management, and auth helpers. Install once globally; upgrade with `teams self-update`.

## Installation and auth

```bash
npm install -g @microsoft/teams.cli@preview
teams --version
teams auth login         # device-code flow
teams status             # which account/tenant is signed in
teams auth logout        # if you need to switch tenants
```

## Project scaffolding

```bash
teams project new typescript <name> --template <echo|ai|graph|tab>
```

| Template | What it scaffolds |
|---|---|
| `echo` (default) | Echo bot |
| `ai` | Bot using `ChatPrompt` + `OpenAIChatModel` |
| `graph` | Bot using `api.graph` with SSO |
| `tab` | Static-hosted tab |

Other useful flags:

- `--package-manager npm|pnpm|yarn` — pick a different manager.
- `--directory ./apps/<name>` — scaffold into a subdirectory.

## App management

```bash
teams app list
# → JSON list of apps with teamsAppId, name, bot endpoint

teams app get <teamsAppId> --json
# → full app metadata, useful for piping into jq

teams app update <teamsAppId> --endpoint "https://<host>/api/messages"
# → most common chore — run after every devtunnel restart

teams app create <name>
# → create a new app + bot identity (alternative to scaffold flow)

teams app delete <teamsAppId>
# → unregister
```

## Auth status

```bash
teams status
# Account: you@contoso.com
# Tenant: contoso.onmicrosoft.com (xxxx-xxxx)
```

## Self-update

```bash
teams self-update
```

The CLI is on the `@preview` npm dist-tag — re-run periodically.

## Diagnostic commands

```bash
teams doctor             # checks Node version, ports, devtunnel reachability
teams logs <teamsAppId>  # tails recent bot activity from the cloud side (where supported)
```

If `teams doctor` reports an issue you cannot resolve, jump to `troubleshoot`.

## CLI inside scripts

Most commands accept `--json` for machine-readable output:

```bash
APP_ID=$(teams app list --json | jq -r '.[] | select(.name=="demo-bot") | .teamsAppId')
teams app update "$APP_ID" --endpoint "https://$DEVTUNNEL/api/messages"
```

Combine with `package.json` scripts for one-shot dev loops:

```jsonc
{
  "scripts": {
    "tunnel": "devtunnel host -p 3978 --allow-anonymous",
    "tunnel:url": "devtunnel show host --json | jq -r '.tunnel.host_url'",
    "endpoint": "TEAMS_APP_ID=$(teams app list --json | jq -r '.[0].teamsAppId') && URL=$(npm run -s tunnel:url) && teams app update $TEAMS_APP_ID --endpoint \"$URL/api/messages\""
  }
}
```

## Common pitfalls

- **`teams: command not found`** — global npm bin is not on `PATH`. Run `npm config get prefix` and add `<prefix>/bin` to your shell config.
- **`teams app update` returns 404** — wrong `teamsAppId`. Use `teams app list` to confirm.
- **`teams status` shows the wrong tenant** — log out, log back in, and pick the developer tenant.
- **CLI hangs on `teams project new`** — npm registry unreachable; check proxy / mirror config.
