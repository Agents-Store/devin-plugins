---
name: cli-recipes
description: Use this skill when the user is driving the Microsoft Teams Developer CLI 3.x (`teams`) from a script, a CI job or an agent — `teams login`, `teams project new typescript`, `teams app create|get|update|doctor`, manifest and RSC edits, `--json` output with jq, non-interactive flags. Triggers on "teams CLI", "teams app update", "teams app create", "teams app doctor", "teams manifest", "teams self-update", "teams status".
---

# Teams Developer CLI 3.x — recipes

`@microsoft/teams.cli` provides the `teams` binary: sign in, scaffold a project, create the Entra app and bot registration, change the endpoint, edit the manifest. The official guide `teams-sdk-teams-dev` walks the standard flows step by step (scaffold, bot registration, SSO, troubleshooting) — start there for a first run. This skill holds the command tree and the scripting recipes around it.

## Install and update

Needs **Node 22.12 or newer**.

```bash
npm install -g @microsoft/teams.cli
teams --version        # 3.x
teams self-update      # the CLI also checks once a day; --disable-auto-update turns that off
```

The `latest` dist-tag is the stable 3.x line. Install it without a tag.

## Command tree

```text
teams
├── login [--device-code]            logout            status [--json]
├── self-update [--force]
├── config get [key] | set <key> [value]
├── project new typescript|csharp|python [name] -t <template>
└── app
    ├── list | get [appId] | create | update [appId] | doctor [appId]
    ├── manifest download|upload|update
    ├── package download
    ├── bot get|migrate
    ├── rsc list|add|remove|set <teamsAppId>
    └── auth secret create [appId]
```

Global flags: `-y, --yes` (auto-confirm, for agents and CI), `-v` (verbose), `--help --json` (command tree as JSON — `teams app --help --json` scopes it to a subtree). `TEAMS_NO_INTERACTIVE=1` disables every prompt.

## Sign in

```bash
teams login            # opens a browser on a local desktop session
teams login --device-code   # URL + code to enter elsewhere; the default over SSH, in CI and with TEAMS_NO_INTERACTIVE=1
teams status --json    # login, Developer Portal access, sideloading policy (tenant and user), az CLI state
```

`teams status` is the first diagnostic: it shows whether the tenant and the user policy allow custom app upload.

## Scaffold a project

```bash
teams project new typescript my-bot -t echo --yes
cd my-bot && npm install && npm run dev
```

| Template | What you get |
|---|---|
| `echo` (default) | `new App()` with an echo handler, `src/index.ts`, `tsup`, `tsx watch` |
| `graph` | Bot that signs the user in and calls Microsoft Graph with `@microsoft/teams.graph-endpoints`; written in the SDK 2.0 style (`oauth.defaultConnectionName`) — the `authentication` skill shows the 2.1 `addOAuthFlow` form |
| `tab` | Bot plus a Vite/React tab built with `@microsoft/teams.client` and an `app.function()` |

Which templates exist depends on the installed CLI: it lists whatever sits in its `templates/typescript` folder. Run `teams project new typescript --help` and trust that list. The AI, MCP and A2A agents are not scaffolded — start from `echo` and add them with the `ai-agents` and `mcp-a2a` skills.

Credentials: pass `--client-id` and `--client-secret` to write them into `.env`, or create the app afterwards (next section). With `--json` or `--yes` the command prints the follow-up `teams app create ... --env .env` line instead of asking.

## Create the app and the bot

```bash
teams app create --name "My Bot" --endpoint "https://<tunnel-host>/api/messages" --env .env --json
```

One command creates the Entra app, a client secret, the manifest, the Teams app and the bot registration, and writes `CLIENT_ID`, `CLIENT_SECRET` and `TENANT_ID` to `.env`.

| Flag | Use |
|---|---|
| `--no-secret` | Managed identity or federated credentials: only `CLIENT_ID` and `TENANT_ID` are produced |
| `--azure --subscription <id> --resource-group <rg>` | Azure Bot instead of the default Teams-managed bot — needed for OAuth and SSO |
| `--sign-in-audience myOrg\|multipleOrgs` | Single-tenant or multitenant Entra app |
| `--service-management-reference <id>` | Tenants that demand service attribution on new Entra apps |
| `--env appsettings.json` | C# projects |

A Teams-managed bot cannot do OAuth or SSO. `teams app bot migrate <appId> --resource-group <rg>` moves it to Azure without changing `CLIENT_ID`, the secret or the tenant. `teams config set default-bot-location azure` makes Azure the default for `app create`.

## Everyday app commands

```bash
teams app list --json                                    # [{ appId, appName, version, teamsAppId, bots: [{ botId, messagingEndpoint }] }]
teams app get <teamsAppId> --json appId,name,endpoint    # pick fields
teams app get <teamsAppId> --install-link                # just the install link, pipe-friendly
teams app update <teamsAppId> --endpoint "https://<host>/api/messages"
teams app update <teamsAppId> --scopes personal,team,groupChat,copilot
teams app update <teamsAppId> --web-app-info-id <client-id> --web-app-info-resource "api://botid-<client-id>"
teams app doctor <teamsAppId>                            # bot, Entra app, manifest and SSO checks
teams app auth secret create <teamsAppId> --env .env     # new client secret (rotation)
teams app package download <teamsAppId> -o app.zip       # sideload-ready zip with icons
```

`teams app update --endpoint` also adds the endpoint's domain to `validDomains` in the manifest; after a domain change the user reinstalls the app in Teams.

## Edit the manifest

Scaffolded projects have no manifest file — the manifest lives in the Developer Portal. Work on it through the CLI:

```bash
teams app manifest download <teamsAppId> manifest.json
teams app manifest upload manifest.json <teamsAppId>      # bumps the patch version when content changed; --no-bump-version disables it
teams app manifest update <teamsAppId> --set-json 'name.short="Contoso Bot"' --dry-run
teams app manifest update <teamsAppId> --set-json validDomains='["bot.example.com"]'
teams app manifest update <teamsAppId> --remove webApplicationInfo
```

`manifest update` validates against the manifest schema and asks before uploading; `--yes` skips the question. Values passed to `--set-json` are JSON, so strings need their own quotes.

Resource-specific consent (RSC) has its own subtree:

```bash
teams app rsc list <teamsAppId>
teams app rsc add <teamsAppId> ChannelMessage.Read.Group --type Application
teams app rsc set <teamsAppId> --permissions TeamSettings.ReadWrite.Group,ChannelMessage.Read.Group
```

## Scripting

Every data command takes `--json`.

```bash
APP_ID=$(teams app list --json | jq -r '.[] | select(.appName=="my-bot") | .teamsAppId')
teams app update "$APP_ID" --endpoint "https://${TUNNEL_HOST}/api/messages" --yes
```

A `package.json` script that re-points the endpoint after a tunnel restart:

```jsonc
{
  "scripts": {
    "tunnel": "devtunnel host my-teams-bot",
    "endpoint": "teams app update \"$TEAMS_APP_ID\" --endpoint \"https://$TUNNEL_HOST/api/messages\" --yes"
  }
}
```

Keep `TEAMS_APP_ID` and `TUNNEL_HOST` in the shell or an untracked env file, never in the repository.

## Common pitfalls

- **`teams: command not found`** — the global npm bin directory is not on `PATH`: `npm config get prefix`, then add `<prefix>/bin`. A Node version manager avoids `EACCES` on global installs.
- **`AUTH_REQUIRED` or `AUTH_TOKEN_FAILED`** — run `teams login` again, then `teams status`.
- **`Unknown template`** — the installed CLI does not ship it; `teams project new typescript --help` prints the real list.
- **`app update` hits the wrong app** — `teamsAppId` is not the bot's client id; copy it from `teams app list --json`.
- **A prompt blocks a script** — add `--yes` or set `TEAMS_NO_INTERACTIVE=1`.
- **Anything unexplained** — `teams app doctor <teamsAppId>` first, then the `troubleshoot` skill.
