# `App` class reference

`App` (from `@microsoft/teams.apps`) is the entry point. Construct it, register routes, call `start()`.

## Constructor

```ts
import { App } from '@microsoft/teams.apps';

const app = new App(options?: AppOptions);
```

## `AppOptions`

| Field | Type | Required | Notes |
|---|---|---|---|
| `plugins` | `Plugin[]` | no | DevtoolsPlugin, McpPlugin, A2AClientPlugin, ExpressAdapter, custom |
| `cloud` | `PUBLIC \| US_GOV \| US_GOV_DOD \| CHINA` | no | Defaults to `PUBLIC` |
| `clientId` | `string` | no | Bot's app id; falls back to `BOT_ID` env var |
| `clientSecret` | `string` | no | Bot's secret; falls back to `BOT_PASSWORD` env var |
| `tenantId` | `string` | no | For single-tenant bots; falls back to env |
| `messagingEndpoint` | `string` | no | Override the route Teams should hit (default `/api/messages`) |
| `logger` | `Logger` | no | Replace the default console logger |

Sovereign clouds adjust login authority, bot service base URL, and JWT validation issuers automatically when `cloud` is changed.

## Methods

| Method | Purpose |
|---|---|
| `app.on(routeName, handler)` | Register an activity handler |
| `app.start(port?)` | Begin listening; resolves once the HTTP server binds |
| `app.stop()` | Graceful shutdown of all listeners |
| `app.send(conversationId, message)` | Proactive send to a known conversation |
| `app.reply(conversationId, activityId, message)` | Reply to a specific activity (thread root) |
| `app.tab(name, dir)` | Mount a static directory at `/tabs/<name>` |
| `app.use(middleware)` | Add a global middleware that runs before route handlers |

## Lifecycle hooks

Plugins can attach to lifecycle events. The most common are:

| Event | Fires when |
|---|---|
| `before-start` | Just before `start()` binds the listener |
| `after-start` | After the listener is up |
| `activity-received` | Each inbound activity, before routing |
| `activity-sent` | Each outbound activity, after the wire send |
| `before-stop` | On `app.stop()` before shutdown completes |

## The handler context

Every handler receives a context object. Common keys:

| Key | Type | Purpose |
|---|---|---|
| `activity` | typed activity (per route) | The incoming payload |
| `send` | `(text \| Activity) => Promise<SendResponse>` | Reactive reply |
| `stream` | streaming emitter | `stream.emit(chunk)` (1:1 only) |
| `log` | structured logger | Captured by DevTools |
| `api` | Graph + REST proxy | `api.graph.*`, `api.tokens.*`, `api.conversations.*` |
| `next` | `() => Promise<void>` | Continue to next handler in chain |

## Example

```ts
import { App, PUBLIC } from '@microsoft/teams.apps';
import { DevtoolsPlugin } from '@microsoft/teams.dev';

const app = new App({
  plugins: [new DevtoolsPlugin()],
  cloud: PUBLIC,
});

app.use(async (ctx, next) => {
  ctx.log.info('inbound', { route: ctx.activity.type });
  await next();
});

app.on('message', async ({ send, activity }) => {
  await send(`Echo: ${activity.text}`);
});

await app.start(+(process.env.PORT ?? 3978));
```
