# Prompts and models — deeper reference

`ChatPrompt` (from `@microsoft/teams.ai`) wraps an LLM with conversation orchestration: system instructions, tools, memory, streaming. `OpenAIChatModel` (from `@microsoft/teams.openai`) is the most common backend.

## `ChatPrompt`

```ts
import { ChatPrompt } from '@microsoft/teams.ai';
import { OpenAIChatModel } from '@microsoft/teams.openai';

const prompt = new ChatPrompt({
  instructions: 'You are a precise, friendly research assistant.',
  model: new OpenAIChatModel({ model: 'gpt-4o' }),
});
```

Options:

| Key | Type | Notes |
|---|---|---|
| `instructions` | `string` | System message, kept stable across turns |
| `model` | `Model` | `OpenAIChatModel` or any other adapter |
| `memory` | `Memory` | Pluggable history backing store (optional) |
| `temperature`, `topP`, `maxTokens` | numbers | Generation knobs (optional, depend on model) |

## Sending a turn

```ts
const { content, usage } = await prompt.send('What is RAG?');
// content: string | structured content
// usage: { promptTokens, completionTokens, totalTokens }
```

Passing an array sends a full message history:

```ts
const { content } = await prompt.send([
  { role: 'user', content: 'Quote Marcus Aurelius' },
  { role: 'assistant', content: 'Waste no more time arguing about what a good man should be. Be one.' },
  { role: 'user', content: 'Another?' },
]);
```

## Streaming

```ts
await prompt.send('Give me a long answer.', {
  onChunk: (chunk: string) => stream.emit(chunk),
});
```

`stream` is the per-handler streaming emitter (see `messaging`). Stream chunks render progressively only in 1:1 chats.

## Function calling

```ts
prompt.function({
  name: 'get_weather',
  description: 'Returns the current weather for a city',
  parameters: {
    type: 'object',
    properties: { city: { type: 'string' } },
    required: ['city'],
  },
  handler: async ({ city }) => {
    const w = await fetchWeather(city);
    return { tempC: w.tempC, conditions: w.conditions };
  },
});
```

The model decides when to call the tool. The handler return value flows back into the conversation as a tool message and the model produces the final assistant reply automatically.

## `OpenAIChatModel`

```ts
new OpenAIChatModel({
  apiKey: process.env.OPENAI_API_KEY,
  model: 'gpt-4o',
});

new OpenAIChatModel({
  apiKey: process.env.AZURE_OPENAI_API_KEY,
  endpoint: process.env.AZURE_OPENAI_ENDPOINT,
  apiVersion: process.env.AZURE_OPENAI_API_VERSION,
  model: 'my-gpt-4o-deployment',          // Azure: the deployment name
});
```

Env defaults: if `apiKey` is omitted, the constructor reads `OPENAI_API_KEY` (or `AZURE_OPENAI_API_KEY` when `endpoint` is set).

## Memory

```ts
import { Memory } from '@microsoft/teams.ai';

class InMemory implements Memory {
  private store = new Map<string, ChatMessage[]>();
  async load(key: string) { return this.store.get(key) ?? []; }
  async save(key: string, msgs: ChatMessage[]) { this.store.set(key, msgs.slice(-20)); }
}

const prompt = new ChatPrompt({
  instructions: '…',
  model: new OpenAIChatModel({ model: 'gpt-4o' }),
  memory: new InMemory(),
});

const { content } = await prompt.send(input, { conversationKey: activity.conversation.id });
```

A real store: Postgres, Redis, Cosmos DB, or any KV.

## Cost control

- Pin the model name; do not let it drift to a more expensive default.
- Cap `maxTokens` for short-answer use cases.
- Cap history length in your `Memory.save` implementation.
- Log `usage` per call to detect runaway costs.

## Mixed-model setups

`A2AClientPlugin` lets your local prompt delegate to remote agents, which can be backed by entirely different models. The local prompt can use a small, cheap model for routing and call out to a larger remote agent for hard turns.

## Pitfalls

- **`401`** — wrong key or endpoint.
- **Tool fires twice** — the same function name is registered in both `prompt.function` and an MCP plugin; pick one host per tool.
- **Hallucinated args** — re-validate arguments inside the handler before any side effect.
- **Slow first token** — Azure deployments often have higher cold latency; warm with a small request at startup.
