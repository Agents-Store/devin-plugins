# Sovereign clouds

A cloud preset reconfigures every endpoint the SDK talks to: login authority, bot service and token service URLs, Graph scope, OpenID metadata and token issuer. Match it to the cloud where the tenant lives.

| Cloud | `CLOUD` value | Preset | Tenant suffix | Notes |
|---|---|---|---|---|
| Public (default) | `Public` | `PUBLIC` | `*.onmicrosoft.com` | Nothing to set |
| US Government (GCC High) | `USGov` | `US_GOV` | `*.onmicrosoft.us` | |
| US Government DoD | `USGovDoD` | `US_GOV_DOD` | `*.onmicrosoft.us` | DoD routing |
| China (operated by 21Vianet) | `China` | `CHINA` | `*.partner.onmschina.cn` | Separate identity stack |

## Configuration

Environment, next to whichever authentication mode is in use (client secret, managed identity, federated):

```bash
CLOUD=USGov
CLIENT_ID=<client-id>
CLIENT_SECRET=<client-secret>
TENANT_ID=<tenant-id>
```

In code — the presets come from `@microsoft/teams.api`, not from `@microsoft/teams.apps`:

```ts
import { App } from '@microsoft/teams.apps';
import { US_GOV } from '@microsoft/teams.api';

const app = new App({ cloud: US_GOV });
void app;
```

A `cloud` passed in code **takes precedence** over the `CLOUD` variable. If the variable seems ignored, check that it is exported into the process (not only the shell) and that no `cloud:` option overrides it.

## Per-endpoint overrides

`withOverrides(preset, { … })` changes single endpoints, for example the tenant-specific login URL a single-tenant bot in China needs:

```ts
import { App } from '@microsoft/teams.apps';
import { CHINA, withOverrides } from '@microsoft/teams.api';

const app = new App({
  cloud: withOverrides(CHINA, { loginTenant: 'your-tenant-id' }),
});
void app;
```

Override fields: `LoginEndpoint`, `LoginTenant`, `BotScope`, `TokenServiceUrl`, `OpenIdMetadataUrl`, `TokenIssuer`, `GraphScope`.

Graph clients built from the app (`app.graph`, `app.graphBaseUrl`) follow the preset's Graph scope, so sovereign tenants reach the right Graph host. Build user clients with `{ baseUrlRoot: app.graphBaseUrl }` (`graph-integration`).

## Per-cloud caveats

| Cloud | Caveat |
|---|---|
| US Government | Register the bot in an Azure US Government subscription; the commercial Azure Bot Service cannot serve a GCC High tenant |
| US Government DoD | Some Graph endpoints lag the commercial cloud by a release or two |
| China | Operated independently of the global services; check that the model service you call (Azure OpenAI region and deployment) exists there |

## Manifest and portal

The manifest schema is the same in every cloud, but the app catalog, admin center and Developer Portal are per cloud. Use the portal that matches the tenant when you upload or manage the app.

## Verify

After deploying, send a message and read the log of the inbound request: the service URL must belong to the cloud (a government bot service host, not the commercial one). A commercial host against a `USGov` setup means the Azure Bot resource sits in the wrong cloud.
