---
name: graph-integration
description: Use this skill when the user is calling Microsoft Graph from a Microsoft Teams app on Teams SDK 2.1 — `app.graph.call(endpoints…)` as the app, a `GraphClient` built from a user's OAuth token, `@microsoft/teams.graph-endpoints` parameters, beta endpoints, paging, permissions. Triggers on "Microsoft Graph Teams", "graph-endpoints", "app.graph", "list calendar events bot", "send mail Teams bot", "graph permissions".
---

# Microsoft Graph integration

Graph is split into three packages. There is no fluent `graph.users.list()` object on the API client.

| Package | Role |
|---|---|
| `@microsoft/teams.graph` | A small client: `new Client(options).call(endpoint, params)` |
| `@microsoft/teams.graph-endpoints` | Typed request builders for the v1.0 API (tree-shakable; install it explicitly) |
| `@microsoft/teams.graph-endpoints-beta` | The same for the beta API; can be mixed with v1.0 calls |

```bash
npm install @microsoft/teams.graph @microsoft/teams.graph-endpoints
```

The picture to keep in mind: **an endpoint builder describes the request, a client signs and sends it.** Which client you use decides whose token travels.

## 1. As the app (application permissions)

`app.graph` and, inside a handler, `appGraph` use the bot's own identity — the same `CLIENT_ID`/`CLIENT_SECRET`/`TENANT_ID`, no extra credentials:

```ts
import * as endpoints from '@microsoft/teams.graph-endpoints';

app.on('message', async ({ send, appGraph }) => {
  const users = await appGraph.call(endpoints.users.list, {
    $top: 5,
    $select: ['id', 'displayName'],
  });
  await send(`First users: ${(users.value ?? []).map((u) => u.displayName).join(', ')}`);
});
```

All arguments — path variables, query options, request body — go into one object after the endpoint. Application permissions (`User.Read.All`, `Team.ReadBasic.All`, …) need admin consent in the tenant.

## 2. As the user (delegated permissions)

Get the user's token from an OAuth flow (`authentication`), then build a client around it. The client is bound to the connection that owns the token:

```ts
import { Client as GraphClient } from '@microsoft/teams.graph';
import * as endpoints from '@microsoft/teams.graph-endpoints';

const graph = app.addOAuthFlow('graph');

app.on('message', async (ctx) => {
  const token = await graph.signIn(ctx);
  if (!token) return;                               // an OAuth card was sent

  const client = new GraphClient({ token: () => token }, { baseUrlRoot: app.graphBaseUrl });
  const events = await client.call(endpoints.me.events.list, {
    $top: 10,
    $orderby: ['start/dateTime'],
    $select: ['subject', 'start'],
  });
  await ctx.send(`Next: ${(events.value ?? []).map((e) => e.subject).join(', ')}`);
});
```

`token` can be a function so a refreshed token is picked up on each request. `baseUrlRoot: app.graphBaseUrl` routes sovereign-cloud apps to the right Graph host (it is `undefined` for the public cloud, which the client defaults to).

The SDK 2.0 object `userGraph` on the context still compiles, deprecated; new code builds the client from the flow.

## 3. Path variables, query options and bodies

```ts
import * as endpoints from '@microsoft/teams.graph-endpoints';

async function demo(client: import('@microsoft/teams.graph').Client, userId: string) {
  const user = await client.call(endpoints.users.get, { 'user-id': userId, $select: ['id', 'displayName', 'mail'] });
  const teams = await client.call(endpoints.me.joinedTeams.list);
  void user; void teams;
}
void demo;
```

- Path placeholders keep their Graph names: `'user-id'`, `'team-id'`, `'channel-id'`.
- `$select`, `$orderby`, `$expand` take arrays; `$top` takes a number; `$search` queries need `ConsistencyLevel: 'eventual'` as a parameter.
- Request bodies are strictly typed. Nested complex types carry an `'@odata.type'` discriminator:

```ts
import { Client as GraphClient } from '@microsoft/teams.graph';
import * as endpoints from '@microsoft/teams.graph-endpoints';

async function createStandup(client: GraphClient) {
  await client.call(endpoints.me.events.create, {
    '@odata.type': 'microsoft.graph.event',
    subject: 'Stand-up',
    start: { '@odata.type': 'microsoft.graph.dateTimeTimeZone', dateTime: '2026-05-19T09:00:00', timeZone: 'UTC' },
    end: { '@odata.type': 'microsoft.graph.dateTimeTimeZone', dateTime: '2026-05-19T09:15:00', timeZone: 'UTC' },
  });
}
void createStandup;
```

If the compiler rejects a body, read the expected type — it lists the required discriminators. `sendMail` takes its body under a capitalised `Message` key.

## 4. Beta endpoints and custom requests

```ts
import * as endpointsBeta from '@microsoft/teams.graph-endpoints-beta';
import type { EndpointRequest } from '@microsoft/teams.graph';

async function betaMe() {
  return app.graph.call(endpointsBeta.me.get);       // GET /beta/me
}

const getMyDisplayName = (): EndpointRequest<{ displayName: string }> => ({
  ver: 'beta',
  method: 'get',
  path: '/me',
  paramDefs: { query: ['$select'] },
  params: { $select: ['displayName'] },
});

async function customCall() {
  const { displayName } = await app.graph.call(getMyDisplayName);
  return displayName;
}
void betaMe; void customCall;
```

A hand-written `EndpointRequest` gives a narrower return type, or reaches an API the endpoints packages do not have yet.

## 5. Paging

Collections return `@odata.nextLink`. Follow it with the client's own HTTP client, which already carries the token and base URL:

```ts
import { Client as GraphClient } from '@microsoft/teams.graph';
import * as endpoints from '@microsoft/teams.graph-endpoints';

async function allMessages(client: GraphClient) {
  let page = await client.call(endpoints.me.messages.list, { $top: 50 });
  const all = [...(page.value ?? [])];
  while (page['@odata.nextLink']) {
    const res = await client.http.get<typeof page>(page['@odata.nextLink']);
    page = res.data;
    all.push(...(page.value ?? []));
  }
  return all;
}
void allMessages;
```

## 6. Throttling

Graph throttles per app and tenant. On `429`, wait for the `Retry-After` period and retry with a bounded number of attempts; do not loop in the handler — a handler that runs long should answer first and finish with `app.send`.

## 7. Permissions and consent

- Delegated permissions are consented by the user at sign-in, or by an admin in advance; the Graph scopes belong on the OAuth connection too.
- Application permissions always need admin consent; sign-in does not grant them.
- Resource-specific consent (RSC) for team or chat data is managed with `teams app rsc add|set` (`cli-recipes`).
- The `graph` CLI template shows the end-to-end sign-in; its code uses the 2.0 style, the shape here is the 2.1 one.

## Common pitfalls

- **`403 Forbidden`** — wrong identity (app token on a `me` call), a missing scope, or no admin consent. Decode the token at jwt.ms and compare `scp` (delegated) or `roles` (application).
- **`401` after a long session** — the user's token expired; call `graph.signIn(ctx)` again.
- **A type error on a request body** — a nested object lacks its `'@odata.type'`, or the key is cased differently from Graph (`Message` for `sendMail`).
- **An empty `value`** — the collection is paged; follow `@odata.nextLink`.
- **`InvalidAuthenticationToken`** — the client holds the app token where a delegated one is required, or the reverse.
