---
name: ai-agents
description: Use this skill when the user is adding LLM-powered behavior to a Microsoft Teams bot — building a `ChatPrompt`, attaching `OpenAIChatModel` (OpenAI or Azure OpenAI), registering function tools, streaming responses, or composing multi-agent flows with `A2AClientPlugin`. Triggers on "AI Teams bot", "ChatPrompt", "OpenAI Teams", "function calling Teams", "streaming Teams response", "A2A agent".
---

# AI agents in Teams (TypeScript)

`@microsoft/teams.ai` provides the prompt and tool primitives; `@microsoft/teams.openai` plugs in OpenAI and Azure OpenAI as the model backend. Full details in `references/prompts-and-models.md`.

## 1. Minimal AI bot

```ts
import { App } from '@microsoft/teams.apps';
import { ChatPrompt } from '@microsoft/teams.ai';
import { OpenAIChatModel } from '@microsoft/teams.openai';

const prompt = new ChatPrompt({
  instructions: 'You are a quote bot. Reply with a fitting quote.',
  model: new OpenAIChatModel({ model: 'gpt-4o' }),
});

const app = new App({});

app.on('message', async ({ send, activity }) => {
  const { content } = await prompt.send(activity.text ?? '');
  await send(content);
});

await app.start();
```

Env: set `OPENAI_API_KEY`. For Azure: set `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_API_VERSION`, and pass `endpoint`/`apiVersion`/`model` to `OpenAIChatModel`.

## 2. Streaming responses (1:1 only)

```ts
app.on('message', async ({ send, stream, activity }) => {
  const isDirect = activity.conversation.conversationType === 'personal';
  if (isDirect) {
    await prompt.send(activity.text ?? '', { onChunk: (chunk) => stream.emit(chunk) });
  } else {
    const { content } = await prompt.send(activity.text ?? '');
    await send(content);
  }
});
```

`stream.emit` only renders progressively in 1:1 chats. In channels/group chats, the Teams client shows the final concatenated text only.

## 3. Function calling

```ts
const prompt = new ChatPrompt({
  instructions: 'You are a meeting assistant.',
  model: new OpenAIChatModel({ model: 'gpt-4o' }),
});

prompt.function({
  name: 'create_event',
  description: 'Create a calendar event',
  parameters: {
    type: 'object',
    properties: {
      title: { type: 'string' },
      start: { type: 'string', description: 'ISO 8601 timestamp' },
      durationMinutes: { type: 'integer' },
    },
    required: ['title', 'start', 'durationMinutes'],
  },
  handler: async (args) => {
    const event = await calendar.create(args);
    return { eventId: event.id };
  },
});
```

The model invokes the function when its arguments are inferable from the user message. The handler return value flows back into the prompt as a tool message and the model produces the final assistant reply.

## 4. State and memory

`ChatPrompt` is stateless by default. Persist conversation history per user/thread to keep context:

```ts
const memory = new Map<string, { role: string; content: string }[]>();

app.on('message', async ({ send, activity }) => {
  const key = activity.conversation.id;
  const history = memory.get(key) ?? [];
  history.push({ role: 'user', content: activity.text ?? '' });

  const { content } = await prompt.send(history);
  history.push({ role: 'assistant', content });
  memory.set(key, history.slice(-20));

  await send(content);
});
```

For production, replace the in-memory map with a durable store keyed on conversation id.

## 5. Calling remote A2A agents

`A2AClientPlugin` lets your bot delegate to other A2A-compatible agents:

```ts
import { A2AClientPlugin } from '@microsoft/teams.mcp';

const app = new App({
  plugins: [
    new A2AClientPlugin({
      agents: [
        { name: 'docs', url: 'https://docs-agent.example.com/a2a' },
        { name: 'crm', url: 'https://crm-agent.example.com/a2a' },
      ],
    }),
  ],
});
```

When the prompt decides to call `docs` or `crm`, the plugin routes the JSON-RPC call to the remote agent and merges the response back into the conversation.

## 6. Exposing your bot as an MCP server

```ts
import { McpPlugin } from '@microsoft/teams.mcp';

const app = new App({ plugins: [new McpPlugin({ port: 4000 })] });
```

Other LLM hosts can connect to `http://localhost:4000/mcp` and call your tools. See `mcp-plugin`.

## 7. Best practices

- **System message lives in `instructions`** — keep it stable; vary user input through `prompt.send(...)`.
- **Stream by default in 1:1** — users prefer progressive output. Fall back to a single send in channels.
- **Guard against unbounded history** — slice the last N turns (10–20) or summarise older context.
- **Validate tool args** — the model can hallucinate fields. Re-validate in the handler before side effects.
- **Always log token usage** — the model object exposes per-call usage in the response.

## Common pitfalls

- **`401 Unauthorized` from OpenAI** — wrong `OPENAI_API_KEY` or `AZURE_OPENAI_API_KEY`.
- **Streaming flushes nothing in a channel** — expected; switch to non-streaming for non-1:1.
- **Tool fires twice** — the prompt was given the same history with the tool message duplicated. Add and slice once per turn.
- **Latency above 15s** — Teams may drop the activity. Emit a `typing` indicator first, then send the final response with `app.send(...)`.
