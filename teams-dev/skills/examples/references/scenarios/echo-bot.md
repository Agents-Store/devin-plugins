# Scenario — Echo bot

The minimum viable bot: scaffold, register, tunnel, test locally, test in Teams.

## 1. Scaffold

```bash
teams login                                    # once
teams project new typescript echo-bot -t echo --yes
cd echo-bot
npm install
```

`src/index.ts` as scaffolded:

```ts
import { App } from '@microsoft/teams.apps';

const app = new App();

app.on('message', async ({ send, activity }) => {
  await send({ type: 'typing' });
  await send(`you said "${activity.text}"`);
});

app.start(process.env.PORT || 3978).catch(console.error);
```

There is no plugin and no second port. With no credentials the app rejects all inbound requests — the next two steps deal with that.

## 2. Test locally, no registration

Allow unauthenticated requests for this shell only and use the Agents Playground (`agents-playground`):

```bash
# terminal 1
DANGEROUSLY_ALLOW_UNAUTHENTICATED_REQUESTS=true npm run dev

# terminal 2
npm install -g @microsoft/m365agentsplayground
agentsplayground -e http://localhost:3978/api/messages -c emulator
```

Open `http://localhost:56150`, send `hello world`, and expect `you said "hello world"`. Stop the dev server before the next step.

## 3. Register the bot and test in Teams

A tunnel gives Teams a public HTTPS address for the local port (Dev Tunnels shown; ngrok or Cloudflare work the same):

```bash
devtunnel create my-echo-bot --allow-anonymous
devtunnel port create my-echo-bot -p 3978
devtunnel host my-echo-bot                      # prints https://<tunnel-host>
```

Create the Entra app and bot with that endpoint; the command writes `CLIENT_ID`, `CLIENT_SECRET` and `TENANT_ID` to `.env`:

```bash
teams app create --name "Echo Bot" --endpoint "https://<tunnel-host>/api/messages" --env .env --json
```

Take `teamsAppId` from the JSON, start the bot without the unauthenticated flag, and open the install link:

```bash
npm run dev
teams app get <teamsAppId> --install-link
```

Install the app in Teams, open the 1:1 chat and send `hello world`. The reply arrives as `you said "hello world"`.

The official walkthrough with every prerequisite check is `teams-sdk-teams-dev` → `references/guide-create-bot-infra.md`.

## 4. Verify

- `teams app doctor <teamsAppId>` reports the bot, the Entra app, the manifest and the endpoint as healthy.
- The dev server logs one inbound activity per message; with `LOG_LEVEL=debug` it logs the payload.
- A restarted tunnel keeps its hostname (persistent Dev Tunnels). With ngrok's free tier run `teams app update <teamsAppId> --endpoint "https://<new-host>/api/messages"` after every restart.

## Next steps

- Reply with a quote: swap `send` for `reply` (`messaging`).
- Respond with a card: `adaptive-card-form.md`.
- Switch to an LLM-driven reply: `ai-quote-agent.md`.
