# Integrate Teams into an existing server

When the codebase already has an HTTP server, do not start a second listener. Wrap the server in an adapter, give the adapter to `App`, call `app.initialize()`, and start the server yourself. The SDK registers its routes on your server and never starts or stops it.

The official guide `teams-sdk-teams-dev` → `references/guide-integrate-existing-server.md` is the short version; this file adds the checklist.

## 1. Install

```bash
npm install @microsoft/teams.apps @microsoft/teams.api
```

`ExpressAdapter` ships in `@microsoft/teams.apps` itself — there is no separate sub-path import and no separate adapter package.

## 2. Mount with `ExpressAdapter`

```ts
import http from 'node:http';
import express from 'express';
import { App, ExpressAdapter } from '@microsoft/teams.apps';

const expressApp = express();

expressApp.get('/health', (_req, res) => { res.json({ status: 'healthy' }); });

const adapter = new ExpressAdapter(expressApp);        // your Express app; the SDK adds its route to it
const app = new App({ httpServerAdapter: adapter });

app.on('message', async ({ send, activity }) => {
  await send(`You said: ${activity.text}`);
});

async function main() {
  await app.initialize();            // registers POST /api/messages on expressApp; does NOT start a server
  http.createServer(expressApp).listen(3978, () => console.log('listening on http://localhost:3978'));
}
main().catch(console.error);
```

- Pass the adapter your **Express app**. If you pass an `http.Server` instead, the adapter creates a second Express app and attaches it to that server — alongside your own app both answer every request and the second one fails with `ERR_HTTP_HEADERS_SENT`. A bare `http.Server` is for apps that have no Express app of their own; routes are then added through `adapter.get(...)`, `adapter.post(...)` and `adapter.use(...)`.
- Call `initialize()`, not `start()`. You own the lifecycle.
- Plugins that set up in `onStart` do not run after `initialize()`; either call `start()` or invoke that plugin's `onStart` yourself.
- Credentials come from `CLIENT_ID`, `CLIENT_SECRET` and `TENANT_ID` as usual, or from the `App` options if the server has its own configuration layer.

## 3. Ordering and body parsing

Teams adds its route when `initialize()` runs, so call it **before** a catch-all 404 handler and after the middleware that should wrap every route (request ids, logging):

```ts
import express from 'express';

declare const requestId: express.RequestHandler;
declare const notFound: express.RequestHandler;
declare const errorHandler: express.ErrorRequestHandler;
declare const app: import('@microsoft/teams.apps').App;
const expressApp = express();

async function wire() {
  expressApp.use(requestId);
  await app.initialize();            // Teams route registered here
  expressApp.use(notFound);
  expressApp.use(errorHandler);
}
void wire;
```

The adapter parses the activity itself. If a global body parser already ran with a small limit, raise it for card and extension payloads: `express.json({ limit: '4mb' })`.

## 4. Authentication stays with the SDK

`/api/messages` validates the Teams service token itself. Do not put your own JWT middleware in front of it; exclude the route from global auth instead. Your other routes are not protected by the SDK — a webhook or MCP route you add needs its own check (a shared secret, your identity provider).

## 5. Other frameworks

For anything other than Express implement `IHttpServerAdapter`. Only `registerRoute` is required; `serveStatic`, `start` and `stop` are optional.

```ts
import { HttpMethod, HttpRouteHandler, IHttpServerAdapter } from '@microsoft/teams.apps';

class MyFrameworkAdapter implements IHttpServerAdapter {
  constructor(private readonly server: { post(path: string, cb: (req: any, res: any) => Promise<void>): void }) {}

  registerRoute(method: HttpMethod, path: string, handler: HttpRouteHandler): void {
    if (method !== 'POST') throw new Error(`Unsupported method: ${method}`);     // Teams only POSTs to the bot endpoint
    this.server.post(path, async (req, res) => {
      const response = await handler({ body: req.body, headers: req.headers });
      res.status(response.status).send(response.body);
    });
  }
}
```

`microsoft/teams.ts` has complete `express`, `hono` and `restify` adapters under `examples/http-adapters`. There is no built-in Fastify adapter and no standalone request handler to mount by hand — write an adapter.

## 6. Tabs on the same server

```ts
import path from 'node:path';

app.tab('settings', path.resolve('dist/client'));       // served at /tabs/settings by the adapter
```

`app.tab` registers through the adapter, so an earlier `express.static` mount on the same URL shadows it.

## 7. Verify

```bash
curl -fsS http://localhost:3978/health
curl -i -X POST http://localhost:3978/api/messages -H "Content-Type: application/json" -d '{}'
```

An unsigned POST to `/api/messages` answers `401`: the route exists and authentication is enforced. A `404` means the route is not registered — `initialize()` did not run, or the adapter wraps another server than the one listening. (With `DANGEROUSLY_ALLOW_UNAUTHENTICATED_REQUESTS` on, validation is off and the answer differs; that is a local-only mode.)

Then register the bot with the port your server actually uses — the tunnel must expose that port, not 3978 if you run elsewhere (`cli-recipes`).

## Common pitfalls

- **404 on `/api/messages`** — `app.initialize()` was not awaited, or ran after the 404 handler.
- **The adapter never sees requests** — an earlier body parser or a catch-all consumed them.
- **`401` on every Teams request** — a global JWT middleware runs before the Teams route.
- **A type error on `new ExpressAdapter({ app })`** — the constructor takes the Express app (or server) itself, not an options object.
- **`ERR_HTTP_HEADERS_SENT` on every other request** — the adapter was given an `http.Server` that already runs your Express app; give it the Express app.
