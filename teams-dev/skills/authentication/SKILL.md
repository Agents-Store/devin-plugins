---
name: authentication
description: Use this skill when the user is wiring authentication into a Microsoft Teams app on Teams SDK 2.1 — app credentials (`CLIENT_ID`/`CLIENT_SECRET`/`TENANT_ID`, managed identity), user sign-in with `app.addOAuthFlow()` (SSO or third-party OAuth), several connections, sign-in callbacks, Nested App Authentication for tabs. Triggers on "Teams SSO", "addOAuthFlow", "OAuth Teams bot", "signIn", "onSignInComplete", "NAA Teams", "managed identity Teams bot".
---

# Authentication

Three questions, three answers:

| Who calls what | Mode | Where |
|---|---|---|
| The bot talks to Teams and Graph **as itself** | App auth: client secret, managed identity or federated credential | `new App()` and the environment |
| The bot acts **for a signed-in user** | User auth: an OAuth flow on an Azure Bot connection (SSO for Entra ID, plain OAuth for other providers) | `app.addOAuthFlow(name)` |
| A tab calls Graph or the agent **as the user**, no popup | Nested App Authentication (NAA) | `@microsoft/teams.client` or MSAL in the page; see `tabs` |

The Azure-side setup — migrating the bot to Azure, the Entra app, the OAuth connection, `webApplicationInfo`, verification with `teams app doctor` — is a CLI-driven walkthrough in the vendored official guide: `teams-sdk-teams-dev` → `references/guide-setup-sso.md`. This skill is the code side.

## 1. App auth

`App` reads its credentials from the environment. `teams app create --env .env` writes the first three.

| Variable | Meaning |
|---|---|
| `CLIENT_ID` | Application (client) id of the bot's Entra app |
| `CLIENT_SECRET` | Client secret; leave it unset for managed identity |
| `TENANT_ID` | Tenant of the app registration (leave unset only for legacy multitenant apps) |
| `MANAGED_IDENTITY_CLIENT_ID` | Federated credential: the managed identity's client id, or `system` for a system-assigned identity |
| `CLOUD` | `Public`, `USGov`, `USGovDoD`, `China` (see `deployment`) |
| `SERVICE_URL`, `PORT` | Overrides |

| Mode | Set |
|---|---|
| Client secret | `CLIENT_ID` + `CLIENT_SECRET` (+ `TENANT_ID`) |
| User-assigned managed identity | `CLIENT_ID` (+ `TENANT_ID`), **no** `CLIENT_SECRET` |
| Federated credential | `CLIENT_ID` + `MANAGED_IDENTITY_CLIENT_ID` (+ `TENANT_ID`), no secret |

The same values exist as options (`clientId`, `clientSecret`, `tenantId`, `managedIdentityClientId`); an option wins over the environment. `BOT_ID` survives only as a substitution variable inside manifest templates (`"botId": "${{BOT_ID}}"`); the SDK does not read it.

A custom route on the same server is not covered by the SDK's inbound validation. Gate it yourself, for example with a shared secret in a header.

## 2. User sign-in with an OAuth flow (2.1)

A flow owns one OAuth connection of the Azure Bot. Register it once and keep the returned object:

```ts
import { App } from '@microsoft/teams.apps';

const app = new App();                       // or new App({ oauthFlows: ['graph'] }) and app.getOAuthFlow('graph') later

const graph = app.addOAuthFlow('graph', {
  oauthCardText: 'Sign in to your account',
  signInButtonText: 'Sign in',
});
```

The name must equal the connection name configured on the Azure Bot. Registering a flow turns turn-state on (`sdk-patterns`) so a sign-in callback can be traced back to the flow that started it. A Teams-managed bot has no OAuth connections: migrate it first (`teams app bot migrate`).

### Sign in and use the token

```ts
import { Client as GraphClient } from '@microsoft/teams.graph';
import * as endpoints from '@microsoft/teams.graph-endpoints';

app.message('/whoami', async (ctx) => {
  const token = await graph.signIn(ctx);      // cached token, or undefined after an OAuth card was sent
  if (!token) return;                         // the flow resumes in onSignInComplete

  const client = new GraphClient({ token: () => token }, { baseUrlRoot: app.graphBaseUrl });
  const me = await client.call(endpoints.me.get);
  await ctx.send(`you are signed in as "${me.displayName}" (${me.mail || me.userPrincipalName})`);
});
```

`signIn` only sends the card; it does not wait for the user. Anything that must happen after consent goes into the callback.

### Callbacks

```ts
graph.onSignInComplete(async (ctx, token) => {
  await ctx.send(`Signed in on ${token.connectionName}. Type **/whoami** or **/signout**.`);
});

graph.onSignInFailure(async (ctx, failure) => {
  ctx.log.error(`Graph sign-in failed: ${failure?.code} - ${failure?.message}`);
  await ctx.send('Graph sign-in failed.');
});
```

Each flow holds one completion and one failure callback; registering again replaces the earlier one. `failure` is undefined for token-service and token-exchange errors. The app-wide `app.event('signin', ...)` still fires for every connection.

### Resume the original request

Remember what the user asked, ask for sign-in, then finish after the callback:

```ts
const pendingMessages = new Map<string, string>();         // use your store in production

app.on('message', async (ctx) => {
  const token = await graph.signIn(ctx, { oauthCardText: 'To help with that, I need to sign you in first.' });
  if (!token) {
    pendingMessages.set(ctx.activity.from.id, ctx.activity.text ?? '');
    return;
  }
  await processMessage(ctx.activity.text ?? '', ctx, token);
});

graph.onSignInComplete(async (ctx, token) => {
  const pending = pendingMessages.get(ctx.activity.from.id);
  if (!pending) {
    await ctx.send('You are now signed in!');
    return;
  }
  pendingMessages.delete(ctx.activity.from.id);
  await processMessage(pending, ctx, token.token);
});
```

### Sign out, several connections, status

```ts
const github = app.addOAuthFlow('github', { oauthCardText: 'Sign in with GitHub' });

app.message('/signout', async (ctx) => { await graph.signOut(ctx); await ctx.send('Signed out of Microsoft.'); });
app.message('/signout github', async (ctx) => { await github.signOut(ctx); await ctx.send('Signed out of GitHub.'); });

app.message('/status', async (ctx) => {
  const statuses = await ctx.getConnectionStatus();
  await ctx.send(statuses.map((s) => `- \`${s.connectionName}\`: ${s.hasToken ? 'signed in' : 'signed out'}`).join('\n'));
});
```

Signing out of one connection leaves the others signed in. `flow.isSignedIn(ctx)` and `flow.getToken(ctx)` read the state without sending a card. Connection names match case-insensitively and must be unique.

### What the SDK handles for you

The routes `signin.token-exchange`, `signin.verify-state` and `signin.failure` are handled by the flow. Register them yourself only for a custom protocol. The low-level token client is `ctx.api.users.token` with `get`, `getAad`, `getStatus`, `exchange` and `signOut`.

The older SDK 2.0 pattern — `new App({ oauth: { defaultConnectionName } })`, `ctx.signin()`, `ctx.signout()`, `userGraph` — still compiles but is deprecated, and it cannot be combined with registered flows.

## 3. Failures and consent

When SSO fails, Teams sends `signin/failure` with a code; the flow passes it to `onSignInFailure`:

| Code | Meaning |
|---|---|
| `installedappnotfound` | The bot is not installed for the user or group chat (most common) |
| `resourcematchfailed` | The OAuth card's token exchange resource does not match the Entra application id URI |
| `authrequestfailed` | The SSO request failed — often a cross-tenant setup without admin consent in the installing tenant |
| `tokenmissing`, `invokeerror`, `oauthcardnotvalid` | Token acquisition, generic and card-parsing errors |

A magic code in the popup (six digits) is expected when the signing-in identity differs from the Teams user. Troubleshooting steps are in `troubleshoot`.

## 4. Manifest

SSO needs `webApplicationInfo` in the manifest. The CLI sets it without a manifest round trip:

```bash
teams app update <teamsAppId> --web-app-info-id <client-id> --web-app-info-resource "api://botid-<client-id>"
teams app doctor <teamsAppId>
```

`resource` must equal the application id URI of the Entra app and the `tokenExchangeUrl` of the OAuth connection. Leave the connection's Token Exchange URL empty for plain OAuth with a non-Entra provider. The documented scope for OAuth and SSO is `personal`; group chats go through an install-and-authorise card flow (failure codes `installappfailed`, `authrequestfailed`), so test that path before promising it.

## 5. Nested App Authentication (tabs)

In a tab, `@microsoft/teams.client` (or MSAL's `createNestablePublicClientApplication`) asks the Teams host for a token silently. The Entra app needs the single-page-application platform and the nested-app redirect URI described in the Microsoft Learn NAA guide, plus the Graph scopes you request. Code is in `tabs`; consent prewarming through `prewarmScopes` avoids a prompt on first use.

## 6. Regional bots

A bot deployed to a specific Azure region needs the regional token service: the redirect URI in the Entra app becomes the regional `…/.auth/web/redirect`, `validDomains` in the manifest carries the regional host, and `OAUTH_URL` points the SDK at it (for example the Europe token endpoint).

## Common pitfalls

- **`graph.signIn(ctx)` returns undefined and nothing happens afterwards** — it sent a card; finish the flow in `onSignInComplete`.
- **The OAuth card never appears** — the flow name differs from the Azure connection name, or the bot is Teams-managed.
- **Scopes missing in Graph (403)** — add the delegated permission to the Entra app, grant consent, and add it to the connection's scopes.
- **`oauth.defaultConnectionName` throws once `addOAuthFlow` is used** — the two cannot be combined; keep flows only.
- **A second instance loses sign-in state** — pending sign-ins live in turn state; give `state.storage` a shared store before scaling out.
