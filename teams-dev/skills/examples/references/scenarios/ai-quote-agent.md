# Scenario — AI quote agent

A bot that responds to any message with a relevant quote, streaming the answer in 1:1 chats.

## Steps

```bash
teams project new typescript quote-agent --template ai
cd quote-agent
npm install
```

Set the OpenAI key in `.env`:

```
OPENAI_API_KEY=sk-...
```

Edit `src/index.ts`:

```ts
import { App } from '@microsoft/teams.apps';
import { DevtoolsPlugin } from '@microsoft/teams.dev';
import { ChatPrompt } from '@microsoft/teams.ai';
import { OpenAIChatModel } from '@microsoft/teams.openai';

const prompt = new ChatPrompt({
  instructions:
    'You are a quote bot. Given any input, reply with a single fitting quote from a public-domain author. Format: "<quote>" — <author>.',
  model: new OpenAIChatModel({ model: 'gpt-4o' }),
});

const app = new App({
  plugins: [new DevtoolsPlugin()],
});

app.on('message', async ({ send, stream, activity }) => {
  const isDirect = activity.conversation.conversationType === 'personal';

  if (isDirect) {
    await prompt.send(activity.text ?? '', {
      onChunk: (chunk) => stream.emit(chunk),
    });
  } else {
    const { content } = await prompt.send(activity.text ?? '');
    await send(content);
  }
});

(async () => {
  await app.start();
})();
```

## Run

```bash
devtunnel host -p 3978 --allow-anonymous           # in another shell
teams app update $(teams app list --json | jq -r '.[0].teamsAppId') --endpoint "https://<tunnel-host>/api/messages"
npm run dev
```

Sideload via the Developer Portal and start a 1:1 chat.

## Verify

- Send "stay calm" — the bot streams a quote progressively in a 1:1 chat.
- Add the bot to a channel and @mention it — the reply arrives as a single message (no streaming).
- DevTools Activities tab shows one inbound `message` and one outbound stream of chunks.

## Common tweaks

- Cap cost: pass `maxTokens: 60` to `ChatPrompt`.
- Add memory: keep the last 5 turns per conversation.
- Add a tool: register `prompt.function({ name: 'random_author', … })` to bias the model toward a tool-driven path.

See `ai-agents` and `references/prompts-and-models.md` for details.
