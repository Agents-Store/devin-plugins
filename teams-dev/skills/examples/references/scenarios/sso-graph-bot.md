# Scenario — SSO + Microsoft Graph bot

A bot that signs the user in with SSO, then lists the next five calendar events from Microsoft Graph.

## 1. Prerequisites

- Node 22.12 or newer, `teams login` done, Azure CLI (`az`) installed and signed in with the **same** account.
- An **Azure-managed** bot: a Teams-managed bot cannot do OAuth or SSO. Create it as Azure from the start, or migrate it:

```bash
teams app create --name "Graph Bot" --azure --subscription <subscription-id> --resource-group <resource-group> \
  --endpoint "https://<tunnel-host>/api/messages" --env .env --json
# existing Teams-managed bot instead:
# teams app bot migrate <teamsAppId> --resource-group <resource-group>
```

## 2. Configure SSO (Azure side)

Follow the official CLI-driven guide, which this scenario deliberately does not repeat: `teams-sdk-teams-dev` → `references/guide-setup-sso.md`. It ends with an OAuth connection named **`graph`** on the Azure Bot, an Entra app exposing `access_as_user`, the Teams clients pre-authorised, `webApplicationInfo` on the app, and `teams app doctor <teamsAppId>` green. Give the connection the scopes `User.Read Calendars.Read`.

## 3. The bot

```bash
teams project new typescript graph-bot -t echo --yes
cd graph-bot
npm install @microsoft/teams.graph @microsoft/teams.graph-endpoints
```

Bring the `.env` written by `teams app create` into the project. Replace `src/index.ts`:

```ts
import { App } from '@microsoft/teams.apps';
import { Client as GraphClient } from '@microsoft/teams.graph';
import * as endpoints from '@microsoft/teams.graph-endpoints';

const app = new App();
const graph = app.addOAuthFlow('graph', { oauthCardText: 'Sign in to view your calendar', signInButtonText: 'Sign in' });

async function sendEvents(ctx: { send: (text: string) => Promise<unknown> }, token: string) {
  const client = new GraphClient({ token: () => token }, { baseUrlRoot: app.graphBaseUrl });
  const events = await client.call(endpoints.me.events.list, {
    $top: 5,
    $orderby: ['start/dateTime'],
    $select: ['subject', 'start'],
  });
  const lines = (events.value ?? []).map((e) => `• ${e.start?.dateTime} — ${e.subject}`);
  await ctx.send(lines.length ? `Next ${lines.length} events:\n${lines.join('\n')}` : 'No upcoming events.');
}

app.on('message', async (ctx) => {
  const token = await graph.signIn(ctx);        // cached token, or undefined after an OAuth card was sent
  if (!token) return;
  await sendEvents(ctx, token);
});

graph.onSignInComplete(async (ctx, token) => {
  await ctx.send('Signed in. Here is your calendar:');
  await sendEvents(ctx, token.token);
});

graph.onSignInFailure(async (ctx, failure) => {
  ctx.log.error(`sign-in failed: ${failure?.code} ${failure?.message}`);
  await ctx.send('Sign-in failed. Ask your admin to check consent for this app.');
});

app.message('/signout', async (ctx) => {
  await graph.signOut(ctx);
  await ctx.send('You have been signed out.');
});

app.start(process.env.PORT || 3978).catch(console.error);
```

## 4. Run and verify

```bash
npm run dev          # tunnel running, endpoint registered, unauthenticated flag OFF
```

1. Install the app in Teams and open the 1:1 chat. SSO does not run in the Agents Playground.
2. Send any message. First time: an OAuth card, then a consent prompt for `Calendars.Read`.
3. After consent the callback sends the calendar. A second message answers directly from the cached token.
4. `/signout` clears the token; the next message asks again.

`teams app doctor <teamsAppId>` shows the SSO checks (identifier URI, `access_as_user`, pre-authorised clients, redirect URI, OAuth connection) if the card never appears.

## Common tweaks

- A durable store for anything you keep per user; pending sign-ins live in turn state, so give `state.storage` a shared store before scaling out (`sdk-patterns`).
- Add a function tool to an AI agent that wraps the calendar call, so the model can answer "what is on my calendar" (`ai-agents`).
- Several providers: one `addOAuthFlow` per connection (`authentication`).
- Sovereign clouds: the client already follows `app.graphBaseUrl`; set `CLOUD` (`deployment`).
