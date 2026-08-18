---
name: deployment
description: Use this skill when the user is deploying a Microsoft Teams bot — sideloading the manifest, registering bot infrastructure with the Teams CLI, switching between localhost / devtunnel / production hosts, configuring sovereign clouds (US Gov, GCC High, China), or planning a Teams app release. Triggers on "deploy Teams bot", "sideload Teams app", "Teams app production", "Teams sovereign cloud", "Teams bot endpoint".
---

# Deployment

The deployment surface has three steps: bot infrastructure (identity), endpoint URL (where Teams sends activities), and sideloading (how users get the app). Sovereign-cloud tenants add one extra configuration.

For the detailed bot-infra walk-through, see `references/bot-infra-setup.md`. For sovereign clouds, see `references/sovereign-clouds.md`.

## 1. Bot infrastructure

The bot needs a registered identity Teams trusts. Two options:

- **Teams-managed bot** (recommended for new apps): the Teams Developer Portal allocates `BOT_ID` + secret and you do not host an AAD app for the bot identity.
- **Custom AAD app** (single-tenant or multi-tenant): you own and rotate the secret yourself, useful when the same AAD app is shared with another workload.

Set up via the CLI:

```bash
teams app create my-bot                          # creates the app + bot registration
teams app get <teamsAppId> --json | jq .         # see BOT_ID, password, etc.
```

Pipe the secret into `.env`:

```
BOT_ID=...
BOT_PASSWORD=...
TEAMS_APP_ID=...
```

The full setup walkthrough is at `references/bot-infra-setup.md`.

## 2. Endpoint URL

Teams delivers each activity to `https://<host>/api/messages`. The host changes between environments:

- **Local dev** — `https://<id>.devtunnels.ms/api/messages` or `https://<id>.ngrok.io/api/messages`.
- **Staging** — your staging host (Azure App Service, AWS, Vercel, Render, etc.).
- **Production** — production host with a stable DNS name.

Update Teams after every host change:

```bash
teams app update <teamsAppId> --endpoint "https://<host>/api/messages"
```

`<teamsAppId>` is the Teams-side app id; do not confuse with the AAD client id.

## 3. Sideloading

After the endpoint is set:

1. Open the [Teams Developer Portal](https://dev.teams.microsoft.com/).
2. Find the app — the CLI auto-registers on `teams project new`.
3. Click **Preview in Teams**, accept the manifest, then send the bot a message.

For organisation-wide rollout, an admin uploads the manifest in the Teams Admin Center → Manage apps → Upload.

For an external app store listing, submit through Partner Center / AppSource. The manifest must pass automated validation: schema version, icon sizes, valid domains, and required `webApplicationInfo` for SSO.

## 4. Production hosting

The bot is a regular Node HTTP server. Any host that supports long-lived HTTPS works:

- **Azure App Service** — easiest fit; ships with App Service Authentication if you want managed AAD.
- **AWS Fargate / Lambda + API Gateway** — Lambda works only if you wrap activities in synchronous responses < 15s.
- **Container hosts** (Cloud Run, Fly, Render) — package the bot in a Docker image.
- **Self-hosted Node** behind nginx — standard reverse proxy + LE certs.

Required at runtime:

| Var | Source |
|---|---|
| `BOT_ID`, `BOT_PASSWORD` | `teams app get` |
| `TEAMS_APP_ID` | `teams app list` |
| `PORT` | host-provided |
| `OPENAI_API_KEY` / `AZURE_OPENAI_*` | if AI is enabled |
| `AAD_*` | if SSO/Graph is enabled |

Ensure logs are durable; the DevTools plugin is for local only — disable it in production:

```ts
const plugins = process.env.NODE_ENV === 'production' ? [] : [new DevtoolsPlugin()];
const app = new App({ plugins });
```

## 5. Sovereign clouds

```ts
import { App, US_GOV, US_GOV_DOD, CHINA, PUBLIC } from '@microsoft/teams.apps';

const cloud = process.env.CLOUD === 'USGov'    ? US_GOV
            : process.env.CLOUD === 'USGovDoD' ? US_GOV_DOD
            : process.env.CLOUD === 'China'    ? CHINA
            : PUBLIC;

const app = new App({ cloud });
```

The `cloud` value swaps the login authority, bot service URL, and JWT issuer. See `references/sovereign-clouds.md` for the full table and per-cloud caveats.

## 6. CI/CD checklist

- `npm run build` (or `tsc`) emits to `dist/`.
- Container image runs `node dist/index.js` with `PORT` from env.
- `.env` is supplied as runtime secrets, not committed.
- Health probe: add `app.tab('health', '/health')` or a separate Express route returning 200.
- On deploy, re-run `teams app update --endpoint` only if the URL changes.

## Common pitfalls

- **Sideload fails with "manifest invalid"** — the manifest JSON schema version is older than the icons / features used; bump `manifestVersion` to the latest.
- **`401` from Teams** — bot password rotated but the running server still has the old one; restart with new `.env`.
- **Activities arrive in dev but not in prod** — endpoint not updated for the production host.
- **Sovereign cloud tokens rejected** — `cloud: PUBLIC` against a USGov tenant; switch the enum value.
