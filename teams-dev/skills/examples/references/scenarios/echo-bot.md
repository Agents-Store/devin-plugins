# Scenario — Echo bot

The minimum viable bot. Scaffolds the project, starts a tunnel, sideloads, and verifies a round-trip.

## Steps

```bash
teams project new typescript echo-bot --template echo
cd echo-bot
npm install
```

`src/index.ts` after scaffolding:

```ts
import { App } from '@microsoft/teams.apps';
import { DevtoolsPlugin } from '@microsoft/teams.dev';

const app = new App({
  plugins: [new DevtoolsPlugin()],
});

app.on('message', async ({ send, activity }) => {
  await send(`You said: ${activity.text}`);
});

(async () => {
  await app.start(+(process.env.PORT ?? 3978));
})();
```

Start a tunnel and bind it:

```bash
# in another terminal
devtunnel host -p 3978 --allow-anonymous

# in your project terminal, once the tunnel URL is shown
TEAMS_APP_ID=$(teams app list --json | jq -r '.[0].teamsAppId')
teams app update $TEAMS_APP_ID --endpoint "https://<tunnel-host>/api/messages"

# run the bot
npm run dev
```

Open `http://localhost:3979/devtools` — confirm the page loads.

## Sideload

1. Open `https://dev.teams.microsoft.com/`.
2. Find `echo-bot`. Click **Preview in Teams**.
3. Accept the manifest. A 1:1 chat with the bot opens.
4. Send "hello world".

Expected reply: **You said: hello world**

## Verify

- The DevTools Activities tab shows the inbound `message` and outbound reply.
- The handler's `log` lines (if any) appear alongside.
- Re-sending a message returns immediately (< 1s).

## Next steps

- Add a typing indicator: replace `await send(...)` with `await send({ type: 'typing' }); await send(...)`.
- Add an Adaptive Card response: see `adaptive-card-form.md`.
- Switch to an LLM-driven reply: see `ai-quote-agent.md`.
