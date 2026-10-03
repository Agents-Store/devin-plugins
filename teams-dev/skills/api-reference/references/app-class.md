# `App` class reference (`@microsoft/teams.apps` 2.1)

`App` is the entry point. Construct it, register routes, `start()`.

```ts
import { App } from '@microsoft/teams.apps';

const app = new App(/* options? */);
```

## `AppOptions`

| Field | Type | Notes |
|---|---|---|
| `clientId` | `string` | Bot's Entra app id. Falls back to `CLIENT_ID` |
| `clientSecret` | `string` | Falls back to `CLIENT_SECRET`; unset means managed identity |
| `tenantId` | `string` | Falls back to `TENANT_ID` |
| `managedIdentityClientId` | `'system' \| string` | Falls back to `MANAGED_IDENTITY_CLIENT_ID`; same as `clientId` means user-assigned managed identity, `system` or another id means a federated credential |
| `applicationIdUri` | `string` | The Entra application id URI used for user auth; matches `webApplicationInfo.resource` |
| `token` | `TokenProvider` | Fetch tokens yourself instead of the SDK: a function `(scope, tenantId?) => string`, or an object when the app acts with an agentic identity |
| `cloud` | `CloudEnvironment` | `PUBLIC` (default), `US_GOV`, `US_GOV_DOD`, `CHINA` from `@microsoft/teams.api`; falls back to `CLOUD` (`Public`, `USGov`, `USGovDoD`, `China`); a value in code wins |
| `serviceUrl` | `string` | Falls back to `SERVICE_URL`; default is the public bot service |
| `messagingEndpoint` | `` `/${string}` `` | Route for activities; default `/api/messages` |
| `httpServerAdapter` | `IHttpServerAdapter` | Server integration; `ExpressAdapter` or your own (`sdk-patterns`) |
| `plugins` | `IPlugin[]` | Plugins; `app.plugin(p)` adds one later |
| `state` | `boolean \| { storage?, keyPrefix? }` | Per-turn conversation and user state. Off by default; `addOAuthFlow` turns it on |
| `oauthFlows` | `string[]` | OAuth connections to register at construction (`authentication`) |
| `logger` | `ILogger` | Replaces the default `ConsoleLogger` |
| `client` | `HttpClient \| options \| factory` | Shared HTTP client for outbound calls |
| `activity` | `{ mentions: { stripText } }` | Strip the bot's `<at>` mention from inbound `text` |
| `apiClientSettings` | `{ oauthUrl }` | Regional token service |
| `telemetry` | `{ agent365 }` | Agent 365 baggage options, or `false` |
| `dangerouslyAllowUnauthenticatedRequests` | `boolean` | Local testing only. Falls back to `DANGEROUSLY_ALLOW_UNAUTHENTICATED_REQUESTS` |

Deprecated: `storage` (use `state.storage`), `skipAuth` (alias of the unauthenticated flag), `oauth` (`{ defaultConnectionName }`, replaced by `addOAuthFlow`; cannot be combined with registered flows).

## Properties

| Property | Meaning |
|---|---|
| `app.api` | Teams REST clients (`conversations`, `users`, `teams`, `meetings`, …) |
| `app.graph` | Graph client with the app's identity |
| `app.graphBaseUrl` | Graph root of the configured cloud, for clients you build yourself |
| `app.log` | Logger |
| `app.id` | The bot's client id |
| `app.cloud` | The resolved cloud |
| `app.tokenProvider` | The app's token source |

## Methods

| Method | Purpose |
|---|---|
| `app.on(route, handler)` | Register an activity handler |
| `app.message(pattern, handler)` | Message handler filtered by string or RegExp |
| `app.event(name, handler)` | App events: `start`, `signin`, `error`, `activity`, `activity.response`, `activity.sent` |
| `app.use(handler)` | Middleware; one context argument that carries `next` |
| `app.plugin(plugin)`, `app.getPlugin(name)` | Plugins |
| `app.addOAuthFlow(name, options?)`, `app.getOAuthFlow(name)` | OAuth connections |
| `app.function(name, handler)` | REST function at `/api/functions/<name>`, Entra-token validated |
| `app.tab(name, dir)` | Static tab at `/tabs/<name>` |
| `app.initialize()` | Register routes; no server started |
| `app.start(port?)` | `initialize()` plus start the server |
| `app.stop()` | Stop the server |
| `app.send(conversationId, activity, options?)` | Proactive send |
| `app.reply(conversationId, messageId, activity)` | Proactive threaded reply |
| `app.getAgenticIdentity(options?)` | Agent 365 identity for scoped sends |
| `app.hasMatchingRoute(activity)` | Whether a handler exists for an inbound activity |

`toThreadedConversationId(conversationId, messageId)` is a separate export for building thread ids.

## Lifecycle

`initialize()` creates the HTTP route and runs every plugin's `onInit`. `start()` calls `initialize()` and then each plugin's `onStart` and opens the listener. A custom server calls only `initialize()`.

## Example

```ts
import { App } from '@microsoft/teams.apps';
import { ConsoleLogger } from '@microsoft/teams.common';

const app = new App({
  logger: new ConsoleLogger('my-bot', { level: 'info' }),
  state: true,
});

app.use(async ({ log, next }) => {
  log.debug('inbound');
  await next();
});

app.on('message', async ({ send, activity }) => {
  await send(`Echo: ${activity.text}`);
});

app.start(process.env.PORT || 3978).catch(console.error);
```
