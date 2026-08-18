# Integrate Teams into an existing server

When the codebase already has an HTTP server (Express, Fastify, NestJS, Koa, raw Node), do not start a second listener — plug the Teams `App` into the existing one. This guide covers the Express variant; sibling adapters exist for other frameworks and the approach is identical.

## 1. Install

```bash
npm install @microsoft/teams.apps @microsoft/teams.api @microsoft/teams.dev
```

## 2. Mount via `ExpressAdapter`

```ts
import express from 'express';
import { App } from '@microsoft/teams.apps';
import { ExpressAdapter } from '@microsoft/teams.apps/express';

const server = express();
server.use(express.json());

server.get('/health', (_, res) => res.send('ok'));

const app = new App({
  plugins: [new ExpressAdapter({ app: server })],
});

app.on('message', async ({ send, activity }) => {
  await send(`You said: ${activity.text}`);
});

server.listen(3978, () => {
  console.log('listening on http://localhost:3978');
});
```

The adapter registers a `POST /api/messages` route on the existing Express server, parses the activity, and routes it through `app.on(...)` handlers.

## 3. Body parsing

If the server has body-size limits, raise them to handle Adaptive Card payloads and message-extension responses:

```ts
server.use(express.json({ limit: '4mb' }));
```

## 4. Auth and middleware ordering

Place Teams adapter mounting **after** any global middleware you want to apply (logging, request ids) and **before** any catch-all `404` handler.

```ts
server.use(requestId());
server.use(logger);

// register Teams here

server.use(notFound);
server.use(errorHandler);
```

The activity route handles its own authentication — do not put your AAD JWT middleware in front of `/api/messages`.

## 5. Other frameworks

For Fastify:

```ts
import Fastify from 'fastify';
import { App } from '@microsoft/teams.apps';
import { FastifyAdapter } from '@microsoft/teams.apps/fastify';

const fastify = Fastify();
const app = new App({ plugins: [new FastifyAdapter({ app: fastify })] });

await fastify.listen({ port: 3978 });
```

The same pattern applies — replace `ExpressAdapter` with the framework's adapter.

For a framework without an adapter, you can mount a custom handler:

```ts
import { App, BotHandler } from '@microsoft/teams.apps';

const app = new App({});
const handler: BotHandler = app.handler;   // (req, res) => Promise<void>

myFramework.post('/api/messages', handler);
```

`app.handler` is a plain `(req, res) => Promise<void>` — compatible with any Node HTTP framework that exposes those.

## 6. Sharing config

Reuse the existing server's config layer:

```ts
const app = new App({
  clientId: config.bot.id,
  clientSecret: config.bot.secret,
  cloud: config.cloud,
});
```

Do not duplicate `.env` parsing.

## 7. Tabs on the same server

```ts
import path from 'node:path';

app.tab('settings', path.join(__dirname, '../public/settings'));
```

The static directory is mounted on the same Express instance — no extra port.

## 8. Verifying

After mounting, confirm:

```bash
curl -fsS http://localhost:3978/health
# ok

curl -X POST http://localhost:3978/api/messages \
  -H "Content-Type: application/json" \
  -d '{}'
# expected: 401 Unauthorized (Teams normally signs requests; unsigned ones are rejected)
```

A `401` from `/api/messages` is the **healthy** response from an unsigned request — it proves the route is reachable and auth is enforced.

## Common pitfalls

- **`Cannot find module '@microsoft/teams.apps/express'`** — version too old; upgrade to a release that includes the subpath export.
- **Adapter never sees requests** — body-parser middleware consumed the request before the adapter. Mount the adapter before any custom body parsers for `/api/messages`.
- **Adapter conflicts with existing JWT middleware** — exclude `/api/messages` from the middleware: `server.use(/^(?!\/api\/messages).*/, requireJwt)`.
- **Tabs return 404** — `app.tab` runs after `server.use(express.static(...))` and is shadowed. Order matters.
