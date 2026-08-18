# Scenario — SSO + Microsoft Graph bot

A bot that signs the user in, then lists their next five calendar events from Microsoft Graph.

## Steps

```bash
teams project new typescript graph-bot --template graph
cd graph-bot
npm install
```

The `graph` template scaffolds an OAuth-aware bot. Complete the Azure-side setup first — follow `skills/authentication/references/sso-setup.md` end-to-end. You should end up with:

- An AAD app exposing `api://<host>/<APP_ID>/access_as_user`.
- An OAuth connection on the Bot Service named `GRAPH_CONNECTION` with scopes `access_as_user Calendars.Read`.
- The manifest's `webApplicationInfo.resource` set to `api://<host>/<APP_ID>`.

Edit `src/index.ts`:

```ts
import { App } from '@microsoft/teams.apps';
import { DevtoolsPlugin } from '@microsoft/teams.dev';
import { MessageActivity, OAuthCard, cardAttachment } from '@microsoft/teams.api';

const tokens = new Map<string, string>();   // replace with a durable store in prod

const app = new App({
  plugins: [new DevtoolsPlugin()],
});

app.on('message', async ({ send, activity, api }) => {
  const cached = tokens.get(activity.from.id);

  if (!cached) {
    await send(
      new MessageActivity().addAttachment(
        cardAttachment(
          'oauth',
          new OAuthCard({
            connectionName: 'GRAPH_CONNECTION',
            text: 'Sign in to view your calendar',
          }),
        ),
      ),
    );
    return;
  }

  const events = await api.graph
    .withToken(cached)
    .me.events.list({ $top: 5, $orderby: 'start/dateTime' });

  if (!events.value.length) {
    await send('No upcoming events.');
    return;
  }

  const lines = events.value.map(
    (e) => `• ${e.start?.dateTime} — ${e.subject}`,
  );
  await send(`Next ${events.value.length} events:\n${lines.join('\n')}`);
});

app.on('signin.token-exchange', async ({ activity, api, send }) => {
  const token = await api.tokens.exchange({
    connectionName: 'GRAPH_CONNECTION',
    userTokenExchangeRequest: activity.value,
  });
  tokens.set(activity.from.id, token.token);
  await send('Signed in. Ask me again to see your calendar.');
});

app.on('signin.verify-state', async ({ activity, api }) => {
  await api.tokens.verify({ state: activity.value.state });
});

(async () => {
  await app.start();
})();
```

## Run

```bash
devtunnel host -p 3978 --allow-anonymous
teams app update $(teams app list --json | jq -r '.[0].teamsAppId') --endpoint "https://<tunnel-host>/api/messages"
npm run dev
```

## Verify

1. Sideload the updated manifest with the SSO-enabled `webApplicationInfo`.
2. Send any message to the bot.
3. The bot replies with an OAuth card. Click **Sign in** and consent.
4. The bot replies with "Signed in. Ask me again to see your calendar."
5. Send another message. The bot replies with up to five upcoming events.

DevTools shows: inbound `message` → outbound OAuth card → inbound `signin.token-exchange` → outbound text → inbound `message` → outbound calendar list.

## Common tweaks

- Replace the `Map` with Redis / Postgres for durable token storage keyed on `activity.from.id`.
- Refresh expired tokens by re-issuing the OAuthCard on a Graph `401`.
- Add a function tool to a `ChatPrompt` that wraps `api.graph.withToken(...).me.events.list(...)` so an LLM can call it via natural language.
- For multi-tenant deployments, switch `webApplicationInfo` and the AAD app's `signInAudience` to multi-tenant and use `authority: 'https://login.microsoftonline.com/common'`.
