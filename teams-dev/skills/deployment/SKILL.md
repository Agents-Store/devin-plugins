---
name: deployment
description: Use this skill when the user is deploying a Microsoft Teams bot built on Teams SDK 2.1 — runtime environment variables (`CLIENT_ID`, `CLIENT_SECRET`, `TENANT_ID`, `MANAGED_IDENTITY_CLIENT_ID`), managed identity and federated credentials, the messaging endpoint, install and sideloading, organisation rollout, production hosting, secret rotation, sovereign clouds (`CLOUD`, US Gov, China). Triggers on "deploy Teams bot", "sideload Teams app", "Teams app production", "Teams sovereign cloud", "Teams bot endpoint", "managed identity Teams bot".
---

# Deployment

Three pieces have to line up: the bot's **identity** (Entra app plus bot registration), the **endpoint** Teams posts activities to, and the **install** path users take. The SDK adds one more switch for sovereign clouds.

Creating the identity — `teams app create`, tunnels for local development, Azure bots, SSO — is the vendored official walkthrough: `teams-sdk-teams-dev` → `references/guide-create-bot-infra.md`. The official skill states that it does **not** cover hosting or deployment; that is this skill.

## 1. Runtime configuration

| Variable | Source | Notes |
|---|---|---|
| `CLIENT_ID` | `teams app create` output | Required |
| `CLIENT_SECRET` | `teams app create`, or `teams app auth secret create <teamsAppId>` | Omit with managed identity |
| `TENANT_ID` | `teams app create` output | |
| `MANAGED_IDENTITY_CLIENT_ID` | Azure | Federated credential: managed identity id, or `system` |
| `CLOUD` | You | `Public` (default), `USGov`, `USGovDoD`, `China` |
| `PORT` | The host | `app.start(process.env.PORT || 3978)` |
| `SERVICE_URL` | You | Override of the bot service URL; rarely needed |
| `OPENAI_API_KEY`, `AZURE_OPENAI_*` | You | Only for AI agents (`ai-agents`) |

Authentication mode follows from what is set:

- **Client secret** — `CLIENT_ID` and `CLIENT_SECRET`.
- **User-assigned managed identity** — `CLIENT_ID` and no secret. Create the bot with `teams app create --no-secret`.
- **Federated credential** — `CLIENT_ID` plus `MANAGED_IDENTITY_CLIENT_ID` (a managed identity id, or `system`), no secret.

Values come from the host's secret store or environment, never from the repository. `.env` is for local development and stays untracked. Do not set `DANGEROUSLY_ALLOW_UNAUTHENTICATED_REQUESTS` anywhere that is not a developer machine (`agents-playground`).

## 2. Endpoint

Teams delivers activities to `https://<host>/api/messages` (the path is configurable with `messagingEndpoint` on `App`). Register the host once per environment:

```bash
teams app update <teamsAppId> --endpoint "https://<host>/api/messages"
```

For a Teams-managed bot this updates the registration in the Developer Portal; for an Azure bot the CLI also updates the Azure Bot resource through `az`. A change of domain updates `validDomains` and needs a reinstall of the app in Teams. `teamsAppId` is the Teams-side app id, not the Entra client id — copy it from `teams app list --json`.

A Teams-managed bot is enough until the app needs OAuth or SSO; then migrate it (`teams app bot migrate <teamsAppId> --resource-group <rg>`). Client id, secret and tenant do not change.

## 3. Install and rollout

1. **Developer install.** `teams status` shows whether the tenant and the user policy allow custom apps; `teams app get <teamsAppId> --install-link` prints the link. A "custom apps are blocked" message means an admin has to enable custom app upload.
2. **Zip upload.** `teams app package download <teamsAppId> -o app.zip` yields manifest plus icons for upload in Teams ("Manage your apps → Upload an app").
3. **Organisation rollout.** An admin uploads the package in the Teams admin center (Manage apps), or you publish through the org's app catalog or Partner Center for the public store. Validation checks the manifest schema, icons, `validDomains` and, for SSO, `webApplicationInfo`.

The app was created in one tenant; install it in the same one while testing, or the link answers "this app cannot be found".

## 4. Hosting

The bot is a Node 22.12+ HTTP server. Anything that gives it a stable HTTPS URL and long-lived processes works: Azure App Service or Container Apps, a container platform, a VM behind a reverse proxy.

- Build with the template's `npm run build` (`tsup`) and start with `node .`; the host injects `PORT`.
- Terminate TLS in front of the app; Teams needs HTTPS.
- Give the process durable logs; set `LOG_LEVEL` for the level you want.
- Add a health route on the underlying server if the platform needs one — the SDK's adapter owns `/api/messages` only (`sdk-patterns` shows the adapter form for custom routes).
- Serverless functions fit only when each activity is answered well inside the platform's time limit; streaming needs a long-lived process.
- Run more than one instance only with a shared `state.storage` (`sdk-patterns`) and shared pending-sign-in state (`authentication`).

## 5. Secret rotation

```bash
teams app auth secret create <teamsAppId> --env .env     # writes the new CLIENT_SECRET
```

Update the host's secret store, redeploy, then remove the old secret in the Entra app. Managed identity and federated credentials have no secret to rotate — the reason to prefer them on Azure.

## 6. Sovereign clouds

`CLOUD=USGov` (GCC High), `USGovDoD` or `China` in the environment selects a preset; the same presets exist in code as `US_GOV`, `US_GOV_DOD`, `CHINA`, exported by **`@microsoft/teams.api`**:

```ts
import { App } from '@microsoft/teams.apps';
import { CHINA, US_GOV, withOverrides } from '@microsoft/teams.api';

const gov = new App({ cloud: US_GOV });
const china = new App({ cloud: withOverrides(CHINA, { loginTenant: 'your-tenant-id' }) });   // single-tenant bot in China
void gov; void china;
```

A `cloud` passed in code wins over the `CLOUD` variable. Per-cloud caveats and the override fields are in `references/sovereign-clouds.md`.

## 7. CI/CD checklist

- `npm ci && npm run build`; the artifact runs with `node .`.
- Secrets arrive as runtime environment, not baked into the image.
- A deploy needs `teams app update --endpoint` only when the URL changes, and a manifest upload only when the manifest changes (`teams app manifest upload`, `cli-recipes`).
- Smoke test: `curl -i https://<host>/api/messages` — any answer (including 401 or 404) proves the route is reachable; a timeout or 502 does not.
- `teams app doctor <teamsAppId>` after each infrastructure change.

## Common pitfalls

- **Activities arrive in dev, not in production** — the endpoint still points at the tunnel; run `teams app update --endpoint` for the production host.
- **`401` on every inbound request** — the secret rotated but the host still has the old one, or `TENANT_ID` is wrong for a single-tenant app.
- **Sovereign tokens rejected** — the public preset against a government tenant; set `CLOUD` or pass the preset.
- **A manifest that validates locally fails on upload** — `validDomains` misses a host used by a tab, dialog or link handler.
