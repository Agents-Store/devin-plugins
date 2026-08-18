---
name: sdk-patterns
description: Use this skill when the user is writing the core wiring of a Microsoft Teams app — booting the `App`, registering plugins, structuring activity routes, chaining middleware with `next()`, or organising the project layout for a TypeScript Teams bot or app. Triggers on phrases like "Teams App class", "Teams middleware", "register a plugin", "activity routing".
---

# SDK patterns — App, plugins, routing, middleware

The `@microsoft/teams.apps` package is built around one class (`App`) and a plugin pipeline. Mastering four patterns — boot, plugin registration, routing, and middleware — covers ~80% of day-to-day work.

## 1. Boot the App

```ts
import { App, PUBLIC } from '@microsoft/teams.apps';
import { DevtoolsPlugin } from '@microsoft/teams.dev';

const app = new App({
  plugins: [new DevtoolsPlugin()],
  cloud: PUBLIC,
});

(async () => {
  await app.start(+(process.env.PORT ?? 3978));
})();
```

- `app.start(port?)` returns once the HTTP server is listening.
- The HTTP listener handles `/api/messages` (bot activities) and any routes plugins register.
- The default `cloud` is `PUBLIC`. For US Gov / GCC High / China, pass `US_GOV`, `US_GOV_DOD`, or `CHINA` — see `deployment/references/sovereign-clouds.md`.

## 2. Register plugins

Plugins are passed to the constructor:

```ts
new App({
  plugins: [
    new DevtoolsPlugin(),                          // local inspector
    new McpPlugin({ port: 4000 }),                 // expose tools as MCP server
    new A2AClientPlugin({ agents: [{ ... }] }),    // call remote A2A agents
    new ExpressAdapter({ app: express() }),        // run on an existing Express server
  ],
});
```

Plugin order matters: earlier plugins wrap later ones. Place adapter-level plugins (e.g. `ExpressAdapter`) last so they observe the final, fully-decorated pipeline.

## 3. Activity routing

The `app.on(name, handler)` API attaches a handler to a route. The route name is dotted:

| Pattern | Activity type | Example |
|---|---|---|
| `message` | `MessageActivity` | `app.on('message', ...)` |
| `install.add` / `install.remove` | `InstallActivity` | First time the app is added |
| `config.open` / `config.submit` | `ConfigActivity` | Tab configuration page |
| `dialog.open.<id>` | `DialogOpenActivity` | Task module opens |
| `dialog.submit.<id>` | `DialogSubmitActivity` | Task module submitted |
| `card.action.<id>` | `CardActionActivity` | Adaptive Card `Action.Execute` |
| `message.ext.<verb>` | message-extension activities | Search / submit / select-item / query-link |
| `signin.token-exchange` / `signin.verify-state` | sign-in activities | SSO flow |

Use a concrete `<id>` to scope a handler. Use the bare verb (`dialog.open`) to catch every id.

## 4. Middleware via `next()`

Each handler receives `next`. Call it to pass control to the next matching handler:

```ts
app.on('message', async (ctx) => {
  if (ctx.activity.text?.startsWith('/admin')) {
    if (!isAdmin(ctx.activity.from)) {
      await ctx.send('Not authorised.');
      return;
    }
  }
  await ctx.next();
});

app.on('message', async ({ send, activity }) => {
  await send(`You said: ${activity.text}`);
});
```

The first handler short-circuits non-admin `/admin` requests; the second runs only when `next()` is called.

## 5. Project layout

```
src/
├── index.ts          # App boot, plugin list, route registration
├── handlers/
│   ├── message.ts    # app.on('message', …)
│   ├── dialog.ts     # app.on('dialog.*', …)
│   └── extension.ts  # app.on('message.ext.*', …)
├── cards/            # Adaptive Card builders
├── prompts/          # AI ChatPrompt definitions
└── lib/              # Domain code
```

Keep `index.ts` short — registration only. Put handler bodies in `handlers/*` modules and import them. This keeps the route map readable.

## 6. Integrating with an existing server

If the app is not greenfield, plug into the existing Express/Fastify server via `ExpressAdapter`:

```ts
import express from 'express';
import { App } from '@microsoft/teams.apps';
import { ExpressAdapter } from '@microsoft/teams.apps/express';

const server = express();
const app = new App({ plugins: [new ExpressAdapter({ app: server })] });

server.get('/health', (_, res) => res.send('ok'));
app.on('message', async ({ send }) => { await send('hi'); });

server.listen(3978);
```

See `troubleshoot/references/integrate-existing-server.md` for the full migration checklist.

## 7. Common pitfalls

- **Forgetting `await app.start()`** — without the await, the HTTP server never binds.
- **Plugins after `start()`** — plugins must be passed at construction; calling `app.use(plugin)` post-start is not supported.
- **Logging via `console.log`** — use `ctx.log` so DevTools captures the entry alongside the activity.
- **Long-running handlers** — Teams expects a response within ~15 seconds. Use `stream.emit()` (1:1) or send a typing indicator + proactive follow-up for longer work.
