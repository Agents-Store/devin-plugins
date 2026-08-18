---
name: graph-integration
description: Use this skill when the user is calling Microsoft Graph from a Microsoft Teams bot — listing or creating users / events / messages / files via `api.graph`, switching between app-only and on-behalf-of user tokens, or designing a Graph-driven feature. Triggers on "Microsoft Graph Teams", "api.graph", "list calendar events bot", "send mail Teams bot", "graph permissions".
---

# Microsoft Graph integration

The `api.graph` proxy in the handler context is a typed Graph SDK pre-bound to the current activity's identity. Picking the right token (app vs. user) is the single most important decision.

## 1. App-only vs. user (on-behalf-of)

| Token | When | Permission type |
|---|---|---|
| App-only | Bot acts as itself — internal automations, tenant-wide reads | Application permissions |
| User (OBO) | Bot acts on behalf of the signed-in user | Delegated permissions |

Set both up in the AAD app registration ("API permissions" → add Graph permissions for each type you need, admin-consent the application ones).

## 2. App-only call

```ts
app.on('message', async ({ send, api }) => {
  // api.graph uses the app's own token by default
  const teams = await api.graph.teams.list();
  await send(`This tenant has ${teams.value.length} teams.`);
});
```

App permissions like `Team.ReadBasic.All` typically require admin consent. The token is acquired lazily on the first call.

## 3. User (on-behalf-of) call

Trigger SSO first (see `authentication`) to obtain a user token, then bind it:

```ts
const userToken = await store.get(userId);          // saved during signin.token-exchange
const events = await api.graph.withToken(userToken).me.events.list({
  $top: 10,
  $orderby: 'start/dateTime',
});
```

`withToken(...)` returns a Graph proxy that uses the supplied token for this call chain only.

## 4. Common Graph patterns

```ts
// Send mail as the user
await api.graph.withToken(userToken).me.sendMail.post({
  message: {
    subject: 'Daily summary',
    body: { contentType: 'Text', content: 'Today you closed 3 tickets.' },
    toRecipients: [{ emailAddress: { address: 'lead@example.com' } }],
  },
});

// Create a calendar event
await api.graph.withToken(userToken).me.events.post({
  subject: 'Stand-up',
  start: { dateTime: '2026-05-19T09:00:00', timeZone: 'UTC' },
  end: { dateTime: '2026-05-19T09:15:00', timeZone: 'UTC' },
});

// Read OneDrive file content
const file = await api.graph.withToken(userToken).me.drive.items.byId(fileId).content.get();

// Channel message (Teams API)
await api.graph.teams.byId(teamId).channels.byId(channelId).messages.post({
  body: { content: 'Deploy starting.' },
});
```

## 5. Paging

```ts
let page = await api.graph.withToken(userToken).me.messages.list({ $top: 50 });
const all = [...page.value];
while (page.nextLink) {
  page = await api.graph.follow(page.nextLink);
  all.push(...page.value);
}
```

`follow(nextLink)` re-uses the same token + auth context.

## 6. Throttling

Graph throttles by app + tenant. On 429, honour the `Retry-After` header:

```ts
import pRetry from 'p-retry';

const events = await pRetry(
  () => api.graph.withToken(userToken).me.events.list(),
  { retries: 3, onFailedAttempt: e => console.warn('retry', e.attemptNumber, e.message) },
);
```

## 7. Granting consent

For delegated permissions: user grants on first sign-in (or admin grants in advance via "Grant admin consent for tenant" in the AAD portal).

For app permissions: an admin must consent explicitly — the `signin.token-exchange` flow does not cover application permissions.

## 8. Useful Graph endpoints in Teams bots

| Endpoint | Use |
|---|---|
| `me`, `users.byId(...)` | Profile / directory lookups |
| `me.events`, `me.calendar` | Calendar workflows |
| `me.messages`, `me.sendMail` | Mail summaries / notifications |
| `me.drive.items` | OneDrive file access |
| `teams`, `teams.byId(...).channels` | Team / channel directory |
| `users.byId(...).chats` | List user chats |
| `applications`, `servicePrincipals` | App registration management |

## Common pitfalls

- **`403 Forbidden`** — wrong token type (app token for a `me.*` call) or missing permission scope. Inspect the JWT at jwt.ms to confirm `aud`, `scp` / `roles`.
- **`401` after a long-running session** — user token expired; refresh by re-issuing the OAuthCard, the SDK handles silent renewal where possible.
- **Empty `value` array** — paging not exhausted; follow `nextLink`.
- **`InvalidAuthenticationToken`** — `withToken` was called with the app token instead of the user token; tokens are not interchangeable.
