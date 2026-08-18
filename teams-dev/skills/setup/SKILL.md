---
name: setup
description: Use this skill when the user is preparing a development environment for Microsoft Teams app development — installing the Teams Developer CLI, verifying Node version, confirming a Teams sideloading-enabled tenant, or troubleshooting "command not found" / "teams CLI not installed" / "no Microsoft 365 dev tenant" errors before any other Teams work begins.
---

# Setup — Microsoft Teams SDK (TypeScript)

Verify the developer machine is ready for Teams SDK work. Run these checks before scaffolding a project or invoking any other skill.

## Prerequisites

1. **Node 18 or newer.** Node 20+ recommended for the AI skill.
   ```bash
   node --version    # expect v18.x.x or higher
   ```
2. **npm 9+** (ships with modern Node).
3. **A Microsoft 365 tenant with sideloading enabled.** The fastest path is a free [Microsoft 365 Developer Program](https://developer.microsoft.com/microsoft-365/dev-program) tenant — it grants admin rights and sideloading.
4. **A devtunnel or ngrok account.** Teams must reach an HTTPS callback URL; localhost is not addressable.

## Install the Teams Developer CLI

```bash
npm install -g @microsoft/teams.cli@preview
teams --version
```

If `teams --version` prints nothing or errors with `command not found`:

- Verify the global npm bin is on `PATH`: `npm config get prefix` + `$PATH`.
- macOS/Linux: ensure `~/.npm-global/bin` or `/usr/local/bin` is in `PATH`.
- Windows: re-open the shell after install so the user `PATH` reload picks up the new global.

To upgrade later:

```bash
teams self-update
```

## Authenticate the CLI

```bash
teams auth login
teams status
```

`teams status` shows the signed-in account and target tenant. If it shows "Not signed in", re-run `teams auth login` and complete the device-code flow in the browser tab it opens.

If the account is signed in but `teams app list` returns empty even though apps exist in Teams Admin Center, the account is missing the required role — sign in with the developer-tenant admin instead of an end-user account.

## Required env vars

A scaffolded project ships with `.env` placeholders. Common keys:

| Variable | Purpose | Required for |
|---|---|---|
| `BOT_ID` | App registration / bot client ID | Any bot |
| `BOT_PASSWORD` | Bot client secret | Bots without Teams-managed identity |
| `TEAMS_APP_ID` | Sideloaded Teams app id | Sideload + `teams app update` |
| `OPENAI_API_KEY` | OpenAI key | `ai-agents` skill |
| `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_API_VERSION` | Azure OpenAI | `ai-agents` skill (Azure) |
| `AAD_APP_CLIENT_ID`, `AAD_APP_CLIENT_SECRET`, `AAD_APP_TENANT_ID` | AAD app for SSO/Graph | `authentication` + `graph-integration` |

Add real values only to `.env` (gitignored). Never commit secrets.

## Verify

```bash
node --version
npm --version
teams --version
teams status
```

All four should return non-empty output before proceeding.

## Next

- New project: see `getting-started`.
- Existing repo: see `troubleshoot` (run the integration audit in its `references/integrate-existing-server.md`).
- Sideloading the manifest: see `deployment`.

## Common setup errors

- **`EACCES: permission denied` on `npm i -g`** — use a Node version manager (nvm, fnm, volta) instead of fighting `sudo`; this avoids the prefix being owned by root.
- **`teams: command not found` after install** — global bin is not on `PATH`; print `npm config get prefix` and add `<prefix>/bin` to `PATH`.
- **`teams auth login` opens browser but times out** — corporate proxy is blocking the device-code endpoint; retry on a network that allows `login.microsoftonline.com`.
- **`teams status` shows the wrong tenant** — `teams auth logout`, then `teams auth login` and pick the developer tenant in the consent screen.
