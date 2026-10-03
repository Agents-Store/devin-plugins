# Scenario — AI quote agent

A bot that answers every message with a fitting public-domain quote. It streams in 1:1 chats, sends one message elsewhere, and remembers the conversation in turn state.

## 1. Scaffold and add the model client

The CLI has no AI template; start from `echo` and add the `openai` package.

```bash
teams project new typescript quote-agent -t echo --yes
cd quote-agent
npm install openai
```

Create the app registration as in `echo-bot.md` (`teams app create … --env .env`), then add the model settings to `.env`. Use one block:

```bash
# OpenAI
OPENAI_API_KEY=<your-key>
OPENAI_MODEL=<model-name>

# or Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_MODEL_DEPLOYMENT_NAME=<deployment-name>
AZURE_OPENAI_API_VERSION=2024-10-21
```

## 2. The agent

Replace `src/index.ts`:

```ts
import { App } from '@microsoft/teams.apps';
import { AzureOpenAI, OpenAI } from 'openai';
import type { ChatCompletionMessageParam } from 'openai/resources/chat/completions';

const useAzure = Boolean(process.env.AZURE_OPENAI_ENDPOINT);
const client = useAzure
  ? new AzureOpenAI({
      endpoint: process.env.AZURE_OPENAI_ENDPOINT!,
      apiKey: process.env.AZURE_OPENAI_API_KEY!,
      deployment: process.env.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME!,
      apiVersion: process.env.AZURE_OPENAI_API_VERSION || '2024-10-21',
    })
  : new OpenAI();
const MODEL = (useAzure ? process.env.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME : process.env.OPENAI_MODEL)!;

const SYSTEM_PROMPT =
  'You are a quote bot. Given any input, reply with a single fitting quote from a public-domain author. Format: "<quote>" — <author>.';

const app = new App({ state: true });          // conversation scope keeps the history

app.on('message', async ({ activity, stream, send, state }) => {
  const history: ChatCompletionMessageParam[] =
    state?.conversation.get<ChatCompletionMessageParam[]>('history') ?? [{ role: 'system', content: SYSTEM_PROMPT }];
  history.push({ role: 'user', content: activity.text ?? '' });

  if (activity.conversation.conversationType === 'personal') {
    const runner = client.chat.completions.runTools({ model: MODEL, messages: history, tools: [], stream: true });
    runner.on('content', (delta: string) => {
      if (stream.canceled) { runner.abort(); return; }
      stream.emit(delta);
    });
    await runner.done();
    state?.conversation.set('history', (runner.messages as ChatCompletionMessageParam[]).slice(-20));
    return;
  }

  // channels and group chats cannot stream
  const completion = await client.chat.completions.create({ model: MODEL, messages: history });
  const text = completion.choices[0]?.message?.content ?? '';
  history.push({ role: 'assistant', content: text });
  state?.conversation.set('history', history.slice(-20));
  await send(text);
});

app.start(process.env.PORT || 3978).catch(console.error);
```

## 3. Run and verify

```bash
npm run dev
```

- In the Agents Playground (`agents-playground`), send `stay calm` — a quote comes back.
- In Teams, in a 1:1 chat, the same message streams progressively.
- Add the bot to a channel and mention it: the reply arrives as one message.
- Ask `another one` — the answer differs from the first, because the history is in turn state.

## Common tweaks

- Cap cost: `max_completion_tokens: 80` on the call, and a shorter history slice.
- Add a tool: define a `RunnableToolFunction` and pass it in `tools` (`ai-agents`).
- Mark the answer as AI output with `addAiGenerated()` and feedback buttons (`ai-agents`).
- More than one instance: give `state.storage` a shared store (`sdk-patterns`).
