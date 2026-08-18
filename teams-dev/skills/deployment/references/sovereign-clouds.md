# Sovereign clouds

The `cloud` option on `new App({ cloud })` reconfigures every endpoint the SDK talks to. Match it to the tenant where the bot is deployed.

| Cloud | `cloud` value | Tenant suffix | Notes |
|---|---|---|---|
| Public (default) | `PUBLIC` | `*.onmicrosoft.com` | Default; do not set explicitly unless overriding env-based logic |
| US Government (GCC High) | `US_GOV` | `*.onmicrosoft.us` | GCC and GCC High both use this |
| US Government DoD | `US_GOV_DOD` | `*.onmicrosoft.us` | DoD-specific routing |
| China (operated by 21Vianet) | `CHINA` | `*.partner.onmschina.cn` | Separate identity stack |

## Code

```ts
import { App, PUBLIC, US_GOV, US_GOV_DOD, CHINA } from '@microsoft/teams.apps';

const cloud = ((): typeof PUBLIC | typeof US_GOV | typeof US_GOV_DOD | typeof CHINA => {
  switch (process.env.CLOUD) {
    case 'USGov':    return US_GOV;
    case 'USGovDoD': return US_GOV_DOD;
    case 'China':    return CHINA;
    default:         return PUBLIC;
  }
})();

const app = new App({ cloud });
```

What changes under the hood:

- **Login authority** — `login.microsoftonline.us`, `login.partner.microsoftonline.cn`, etc.
- **Bot service base URL** — service endpoint for `/v3/conversations/...` calls.
- **JWT issuer validation** — accepted `iss` claims on inbound activity tokens.

## Per-cloud caveats

| Cloud | Caveat |
|---|---|
| US Government | Bot must be registered in an Azure US Government subscription. The Azure Bot Service in commercial Azure cannot serve a GCC High tenant. |
| US Government DoD | Some Graph endpoints lag commercial parity by 1–2 releases. |
| China | Operated independently of Microsoft global services. `@microsoft/teams.openai` does not work without a region-specific deployment; Azure OpenAI is the only viable backend. |

## Manifest

The manifest schema is identical across clouds, but the **app store / Teams Admin Center** is per-cloud. Sideload via the Developer Portal that matches the tenant (`https://dev.teams.microsoft.us/` for US Gov, `https://dev.teams.microsoft.cn/` for China).

## Env example

```
CLOUD=USGov
BOT_ID=...
BOT_PASSWORD=...
AAD_APP_TENANT_ID=...
```

## Verification

After deploy, hit `/api/messages` from the bot service and check the logs:

```
inbound activity from https://smba.infra.gov.teams.microsoft.us/...
```

The base URL must match the cloud. If you see `smba.infra.teams.microsoft.com` against a `USGov` configuration, the bot is mis-routed — confirm the Azure Bot resource is in the right cloud.
