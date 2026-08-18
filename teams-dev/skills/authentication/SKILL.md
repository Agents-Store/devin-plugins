---
name: authentication
description: Use this skill when the user is wiring authentication into a Microsoft Teams app — app-only bot auth, user OAuth/SSO via `signin.token-exchange` and `signin.verify-state`, Nested App Authentication (NAA) for tabs, or MSAL token acquisition for calling Microsoft Graph. Triggers on "Teams SSO", "signin.token-exchange", "AAD app Teams", "NAA Teams", "OAuth Teams bot".
---

# Authentication

Three modes — pick the one that matches the surface:

| Surface | Mode | Token path |
|---|---|---|
| Bot calling its own backend / Graph as itself | **App auth** | Automatic — bot identity issued by Teams |
| Bot calling Graph on behalf of the signed-in user | **User auth (OAuth/SSO)** | `signin.token-exchange` → on-behalf-of |
| Tab calling Graph as the signed-in user, no popup | **Nested App Authentication (NAA)** | MSAL silent token in the iframe |

For the step-by-step SSO migration (AAD app, OAuth connection, manifest changes) see `references/sso-setup.md`.

## 1. App auth

App auth is automatic. After `app.start()`, the bot has its own credentials and can hit any API that accepts an app-only token, including `api.graph` calls scoped to app permissions:

```ts
app.on('message', async ({ send, api }) => {
  const me = await api.graph.applications.get(); // app-only context
  await send(`Running as app: ${me.displayName}`);
});
```

Required env vars: `BOT_ID`, `BOT_PASSWORD` (or `BOT_TYPE=ManagedIdentity` for Teams-managed bots).

## 2. User auth (SSO) — the token-exchange flow

The flow:

1. User triggers a feature that needs their identity.
2. Bot sends an OAuth card prompting sign-in.
3. Teams handles the sign-in popup against the configured OAuth connection.
4. On success, Teams sends `signin.token-exchange` to the bot.
5. The bot calls `api.tokens.exchange()` to get an on-behalf-of access token.
6. Use that token to call Graph.

### Send the OAuth card

```ts
import { MessageActivity, OAuthCard, cardAttachment } from '@microsoft/teams.api';

app.on('message', async ({ send, activity, api }) => {
  const tokenResponse = await api.tokens.get('GRAPH_CONNECTION', activity.from.id).catch(() => null);
  if (tokenResponse?.token) {
    return handleAuthenticated(tokenResponse.token);
  }

  await send(new MessageActivity().addAttachment(
    cardAttachment('oauth', new OAuthCard({ connectionName: 'GRAPH_CONNECTION', text: 'Sign in to continue' })),
  ));
});
```

`GRAPH_CONNECTION` is the name of the OAuth connection configured in Azure Bot Service.

### Handle the token-exchange callback

```ts
app.on('signin.token-exchange', async ({ activity, api, send }) => {
  const token = await api.tokens.exchange({
    connectionName: 'GRAPH_CONNECTION',
    userTokenExchangeRequest: activity.value,
  });
  await store.put(activity.from.id, token.token);
  await send('Signed in. Try your command again.');
});

app.on('signin.verify-state', async ({ activity, api }) => {
  await api.tokens.verify({ state: activity.value.state });
});
```

### Use the user token

```ts
const userToken = await store.get(userId);
const events = await api.graph.withToken(userToken).me.events.list();
```

## 3. Nested App Authentication (NAA) for tabs

NAA lets a tab acquire a token silently without popping a sign-in window. Inside the tab:

```ts
import { PublicClientApplication } from '@azure/msal-browser';
import * as teams from '@microsoft/teams.client';

await teams.initialize();
const msal = new PublicClientApplication({
  auth: { clientId: 'AAD_CLIENT_ID', authority: 'https://login.microsoftonline.com/common', supportsNestedAppAuth: true },
});

const account = msal.getAllAccounts()[0];
const { accessToken } = await msal.acquireTokenSilent({ scopes: ['User.Read'], account });
```

The `supportsNestedAppAuth: true` flag makes MSAL talk to the Teams host instead of starting its own iframe. The host has already signed the user in.

## 4. Manifest changes

```jsonc
{
  "webApplicationInfo": {
    "id": "<AAD app client id>",
    "resource": "api://<host>/<AAD app client id>"
  },
  "validDomains": ["<host>"]
}
```

The `resource` URI is required for the SSO token-exchange to succeed.

## 5. Scopes

Set the AAD app's API permissions to match what you call:
- `User.Read` — sign-in only.
- `Mail.Read`, `Calendars.ReadWrite`, etc. — pick the minimum.
- Admin-consent the tenant for permissions that require it.

The exchanged user token has only the scopes you requested at consent time; the bot cannot widen them later.

## Common pitfalls

- **`signin.token-exchange` never fires** — OAuth connection name in the OAuthCard does not match the one configured in Azure Bot Service.
- **Exchanged token is for the wrong audience** — the AAD app exposes the API at a different `audience` (`api://...`); align `webApplicationInfo.resource` and the AAD app's "Expose an API" tab.
- **Graph call returns 403** — required Graph scope is missing from AAD app permissions, or admin consent was not granted.
- **NAA returns `interaction_required`** — fall back to a popup or send the user to a separate sign-in page; common on older Teams clients.

See `references/sso-setup.md` for the full Azure-side checklist.
