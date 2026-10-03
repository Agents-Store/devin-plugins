---
name: sdk-patterns
description: Use this skill when the user is writing the core wiring of a Microsoft Teams app on Teams SDK 2.1 — booting `App`, credentials from the environment, per-turn state (`state`), activity routing (`app.on`, `app.message`, `app.event`), middleware (`app.use`, `next`), plugins, logging, or running the app on an existing HTTP server with an adapter. Triggers on "Teams App class", "Teams middleware", "register a plugin", "activity routing", "turn state", "httpServerAdapter".
---

# SDK patterns — App, state, routing, middleware, plugins

`@microsoft/teams.apps` is one class, `App`, plus a router. Everything else — messages, cards, dialogs, OAuth — hangs off handlers registered on it. Teams SDK 2.1 needs Node 22.12 or newer.

## 1. Boot the App

```ts
import { App } from '@microsoft/teams.apps';

const app = new App();

app.on('message', async ({ send, activity }) => {
  await send(`you said "${activity.text}"`);
});

app.start(process.env.PORT || 3978).catch(console.error);
```

- With no options, `App` reads `CLIENT_ID`, `CLIENT_SECRET` and `TENANT_ID` from the environment. `teams app create --env .env` writes them. `MANAGED_IDENTITY_CLIENT_ID`, `CLOUD`, `SERVICE_URL` and `PORT` are read the same way.
- `start()` initializes the app, opens the HTTP server and listens. It resolves when the server is up.
- Without credentials the SDK rejects every inbound request and logs a warning. For local work against the Agents Playground, see `agents-playground`; never enable that in production.
- Authentication modes: client secret (`CLIENT_ID` + `CLIENT_SECRET`), user-assigned managed identity (`CLIENT_ID` only), federated credential (`CLIENT_ID` + `MANAGED_IDENTITY_CLIENT_ID`, the value `system` for a system-assigned identity). See `deployment`.

## 2. Per-turn state

`state` gives every handler a conversation scope and a user scope, loaded before the handler runs and saved after it. It replaces module-level `Map`s for histories, counters and conversation references.

```ts
import { App } from '@microsoft/teams.apps';

const app = new App({ state: true });

app.on('message', async (ctx) => {
  if (!ctx.state) throw new Error('Turn state is not enabled.');

  const count = (ctx.state.conversation.get<number>('messageCount') ?? 0) + 1;
  ctx.state.conversation.set('messageCount', count);

  if (ctx.state.user && ctx.activity.text?.startsWith('my name is ')) {
    ctx.state.user.set('name', ctx.activity.text.slice('my name is '.length).trim());
  }

  const name = ctx.state.user?.get<string>('name') ?? 'there';
  await ctx.reply(`Hello, ${name}. Message #${count}.`);
});
```

- Scopes expose `get`, `set`, `has`, `delete` and `clear`. After mutating an object or array returned by `get`, call `set` again so the scope is marked for saving.
- `ctx.state` is undefined when state is off or the activity has no conversation. Do not keep it after the handler returns — the scopes are sealed.
- Default storage is process-local. For more than one instance pass a durable store that implements `IStorage<string, string>`:

```ts
import { App } from '@microsoft/teams.apps';
import type { IStorage } from '@microsoft/teams.common';

function createApp(durable: IStorage<string, string>): App {
  return new App({ state: { storage: durable, keyPrefix: 'my-app' } });
}
```

- Scopes are saved as whole JSON strings, so concurrent turns are last-writer-wins.
- `app.addOAuthFlow(...)` switches state on by itself (see `authentication`). `storage` on `new App({ ... })` and `app.storage` are deprecated; use `state.storage`.

## 3. Activity routing

`app.on(route, handler)` takes a route name; the handler's `activity` type follows the name.

| Route | Fires when |
|---|---|
| `message` | A chat message (1:1, group, channel) |
| `messageReaction` | A reaction added or removed |
| `install.add`, `install.remove` | The app is installed or removed |
| `conversationUpdate`, `messageUpdate`, `messageDelete` | Membership and edit events, further split by `channelData.eventType` |
| `meetingStart`, `meetingEnd`, `meetingParticipantJoin`, `meetingParticipantLeave` | Meeting events |
| `card.action`, `card.action.<action>` | `Action.Execute` / `Action.Submit` on a card |
| `card.search` | Dynamic search on a choice set |
| `dialog.open`, `dialog.open.<id>`, `dialog.submit`, `dialog.submit.<action>` | Dialogs |
| `message.ext.query`, `.submit`, `.select-item`, `.query-link`, `.open`, `.setting`, `.query-settings-url` | Message extensions |
| `message.submit.feedback` | Thumbs up/down on an AI message |
| `tab.open`, `tab.submit` | Tab fetch and submit |
| `signin.failure`, `signin.token-exchange`, `signin.verify-state` | Sign-in; prefer the OAuth flow callbacks |
| `file.consent`, `handoff.action`, `suggested-action.submit`, `widget.callTool` | Specialised invokes |

Two more registration helpers:

```ts
app.message('/help', async ({ send }) => {       // text matches a string or RegExp
  await send('Commands: /help, /signin');
});

app.event('error', ({ error }) => {              // app-level events: start, signin, error, activity, activity.response, activity.sent
  app.log.error(error);
});
```

The full list with payload fields is in `api-reference` → `references/activity-types.md`.

## 4. Middleware

Handlers for the same route run in registration order; a handler passes control on by calling `next()`.

```ts
app.on('message', async ({ activity, send, next }) => {
  if (activity.text?.startsWith('/admin') && !isAdmin(activity.from)) {
    await send('Not authorised.');
    return;
  }
  await next();
});

app.on('message', async ({ send, activity }) => {
  await send(`You said: ${activity.text}`);
});
```

`app.use` registers middleware for every activity. It takes one context argument that carries `next`:

```ts
app.use(async ({ log, next }) => {
  const startedAt = Date.now();
  await next();
  log.debug(`turn took ${Date.now() - startedAt} ms`);
});
```

## 5. Plugins and the HTTP server

A plugin hooks into the app lifecycle (init, start, stop) and into activity events. Add one with `plugins: [...]` in the options or `app.plugin(p)`; `app.use` is middleware, not a plugin.

The HTTP layer is an adapter. Express is the default. To mount the Teams endpoint on a server you already own, wrap that server and hand the adapter to `App`:

```ts
import http from 'node:http';
import express from 'express';
import { App, ExpressAdapter } from '@microsoft/teams.apps';

const expressApp = express();
expressApp.get('/health', (_req, res) => { res.json({ status: 'healthy' }); });

const app = new App({ httpServerAdapter: new ExpressAdapter(expressApp) });   // your Express app, not a server wrapping it
app.on('message', async ({ send, activity }) => { await send(`Echo: ${activity.text}`); });

async function main() {
  await app.initialize();   // registers /api/messages on expressApp, does not start a server
  http.createServer(expressApp).listen(3978);
}
main().catch(console.error);
```

Pass `ExpressAdapter` your **Express app**. Handing it an `http.Server` instead makes the adapter create its own Express app and attach it to that server; if your own Express app is attached too, both handle every request and responses collide (`ERR_HTTP_HEADERS_SENT`). With a bare `http.Server`, add routes through the adapter (`adapter.get(...)`, `adapter.use(...)`).

`app.initialize()` runs each plugin's `onInit` but not `onStart`. A plugin that does its setup in `onStart` needs `app.start()` or a manual call. Another framework needs a small `IHttpServerAdapter` with a `registerRoute` method. The migration checklist is in `troubleshoot` → `references/integrate-existing-server.md`; the official guide `teams-sdk-teams-dev` covers the adapter choice.

## 6. Logging

The default logger is a `ConsoleLogger` named `@teams/app`. `LOG_LEVEL=debug` raises verbosity; `LOG` is a name filter (a pattern that does not match `@teams/app` silences the default logger — unset it when in doubt). Handlers get `log`; `log.child('scope')` derives a scoped logger.

```ts
import { App } from '@microsoft/teams.apps';
import { ConsoleLogger } from '@microsoft/teams.common';

const app = new App({ logger: new ConsoleLogger('echo', { level: 'debug' }) });
```

## 7. Agent 365 identity and telemetry (2.1)

For apps that run as an Agent 365 agent, 2.1 adds an agentic identity and OpenTelemetry signals. The SDK does not configure an exporter — wire your own and filter on the tracer and meter name `Microsoft.Teams.Apps`.

```ts
import { App } from '@microsoft/teams.apps';

const app = new App({
  telemetry: { agent365: { include: [], operationSource: 'my-agent' } }, // identifier-only baggage; add 'senderName' etc. only on purpose
});

async function notify(conversationId: string) {
  const identity = app.getAgenticIdentity();                   // blueprint and tenant from the app configuration
  await app.send(conversationId, 'Heads up', { agenticIdentity: identity });
}
void notify;
```

`app.tokenProvider` hands out the app's token for something the SDK does not call itself, such as a telemetry exporter. The surface is new in 2.1 — read the release notes of the version you pin before building on it.

## 8. Project layout

```text
src/
├── index.ts          # App options, registration only
├── handlers/         # message.ts, dialog.ts, extension.ts — one module per surface
├── cards/            # Adaptive Card builders
└── lib/              # domain code, model clients, storage
```

Keep `index.ts` short and import handler modules for their side effect or pass `app` in.

## Common pitfalls

- **`app.use((ctx, next) => …)`** — `use` takes one argument; `next` is inside it.
- **`plugins` and `app.use` mixed up** — middleware goes in `app.use`, plugins in `plugins` or `app.plugin`.
- **No reply and a warning about credentials** — set `CLIENT_ID`, `CLIENT_SECRET` and `TENANT_ID`, or enable unauthenticated requests for local testing only.
- **A start-up failure is silent** — `app.start()` stops the app and reports the error through the `error` event instead of rejecting, so register `app.event('error', …)` before starting.
- **`state` is undefined** — `state` was never enabled, or the activity has no conversation (some invokes).
- **A long handler** — Teams expects an answer within about 15 seconds. Stream (`stream.emit`) or send a typing activity and follow up with `app.send`.
