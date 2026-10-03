# The `openai` SDK in a Teams agent — deeper reference

The Teams SDK does not wrap a model. The `openai` package is the model client, `runTools()` is the agent loop, and the Teams handler is the glue. This file covers the parts the main skill only names.

## Clients

```ts
import { AzureOpenAI, OpenAI } from 'openai';

const azure = new AzureOpenAI({
  endpoint: process.env.AZURE_OPENAI_ENDPOINT!,
  apiKey: process.env.AZURE_OPENAI_API_KEY!,
  deployment: process.env.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME!,
  apiVersion: process.env.AZURE_OPENAI_API_VERSION || '2024-10-21',
  maxRetries: 2,
  timeout: 60_000,
});

const plain = new OpenAI({ maxRetries: 2, timeout: 60_000 });   // reads OPENAI_API_KEY
void azure; void plain;
```

| Environment variable | Used by |
|---|---|
| `OPENAI_API_KEY` | `OpenAI` |
| `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_MODEL_DEPLOYMENT_NAME`, `AZURE_OPENAI_API_VERSION` | `AzureOpenAI`; the deployment name is also the `model` value you pass to calls |

For Azure, `model` is the **deployment name**, not the base model name. A gateway that speaks the same wire protocol works with `new OpenAI({ baseURL })`.

## One-shot calls

```ts
import type { ChatCompletionMessageParam } from 'openai/resources/chat/completions';
import { azure as client, MODEL } from './model.js';

export async function summarise(history: ChatCompletionMessageParam[]): Promise<string> {
  const completion = await client.chat.completions.create({
    model: MODEL,
    messages: [...history, { role: 'user', content: 'Summarise our conversation in two sentences.' }],
    max_completion_tokens: 200,
  });
  return completion.choices[0]?.message?.content ?? '';
}
```

Use a one-shot call wherever you need a result rather than a conversation turn: follow-up prompts, routing, summaries of old history.

## Structured output

For machine-readable answers ask for a JSON schema and parse the content:

```ts
import type { ChatCompletionMessageParam } from 'openai/resources/chat/completions';
import { azure as client, MODEL } from './model.js';

const FOLLOW_UPS_SCHEMA = {
  type: 'object',
  properties: { prompt1: { type: 'string' }, prompt2: { type: 'string' } },
  required: ['prompt1', 'prompt2'],
  additionalProperties: false,
} as const;

export async function followUps(history: ChatCompletionMessageParam[]): Promise<string[]> {
  try {
    const completion = await client.chat.completions.create({
      model: MODEL,
      messages: [...history, { role: 'system', content: 'Produce 2 specific prompts the user might ask next, first person, under 8 words each.' }],
      response_format: { type: 'json_schema', json_schema: { name: 'follow_ups', strict: true, schema: FOLLOW_UPS_SCHEMA } },
    });
    const parsed = JSON.parse(completion.choices[0]?.message?.content ?? '{}');
    return [parsed.prompt1, parsed.prompt2].filter((s): s is string => typeof s === 'string' && s.length > 0);
  } catch {
    return [];                       // degrade silently; the main answer has shipped
  }
}
```

## The runner

`runTools()` returns a runner. Events worth knowing:

| Event | Fires |
|---|---|
| `content` | each text delta (streaming) |
| `functionToolCall`, `functionToolCallResult` | before and after each tool callback |
| `message` | each message added to the transcript, tool messages included |
| `error`, `abort` | the loop failed or was aborted |

Awaiting `runner.done()` waits for the end of the loop; `runner.messages` is the transcript, `await runner.totalUsage()` the token count.

```ts
import type { RunnableToolFunction } from 'openai/lib/RunnableFunction';
import type { ChatCompletionMessageParam } from 'openai/resources/chat/completions';
import { azure as client, MODEL } from './model.js';

export async function runTurn(
  history: ChatCompletionMessageParam[],
  tools: RunnableToolFunction<any>[],
  emit: (delta: string) => void,
  log: (line: string) => void,
) {
  const runner = client.chat.completions.runTools(
    { model: MODEL, messages: history, tools, stream: true },
    { maxChatCompletions: 8 },                    // at most 8 model rounds per turn
  );
  runner.on('content', emit);
  runner.on('functionToolCall', (call) => log(`tool ${call.name}`));
  await runner.done();
  const usage = await runner.totalUsage();
  log(`tokens: ${usage.total_tokens}`);
  return runner.messages as ChatCompletionMessageParam[];
}
```

## History

```ts
import type { ChatCompletionMessageParam } from 'openai/resources/chat/completions';

// Keep the system prompt and the last `max` messages, never starting on an orphaned tool result.
export function trim(history: ChatCompletionMessageParam[], max = 30): ChatCompletionMessageParam[] {
  const [system, ...rest] = history;
  let tail = rest.slice(-max);
  while (tail.length > 0 && tail[0].role === 'tool') tail = tail.slice(1);
  return [system, ...tail];
}
```

Store the result in `ctx.state.conversation` (`new App({ state: true })`). The history is JSON, which is what turn state persists. An assistant message with tool calls must stay together with the tool messages that answer it; trimming from the front can split them, hence the loop above.

## Errors

```ts
import { APIError } from 'openai';

app.on('message', async ({ send, log }) => {
  try {
    await send('…run the agent…');
  } catch (err) {
    if (err instanceof APIError) {
      log.error(`model API ${err.status}: ${err.message}`);
      await send(err.status === 429 ? 'The model is busy, try again in a minute.' : 'The model call failed.');
      return;
    }
    throw err;
  }
});
```

Register `app.event('error', …)` for everything that escapes a handler (`sdk-patterns`).

## Cost and latency

- Pin the model or deployment through an environment variable; do not let a default drift.
- Cap output with `max_completion_tokens` for short-answer bots and the tool rounds with `maxChatCompletions`.
- Log `totalUsage()` per turn to spot runaway loops.
- Azure deployments can be slow on the first token after idle time; a cheap request at startup warms them.
- A tool that does slow I/O should answer fast with a placeholder and report later with `app.send`, so the turn stays inside the platform's time limits.

## Pitfalls

- **A tool fires twice** — the same tool is registered both as a local function and through an MCP wrapper; keep one host per tool name.
- **`400` about tool messages** — history was trimmed between a tool call and its result.
- **`parse` throws** — the model sent invalid JSON for the arguments; catch it and return an error string the model can react to.
- **`model` not found on Azure** — the deployment name is wrong, or the API version predates the model.
