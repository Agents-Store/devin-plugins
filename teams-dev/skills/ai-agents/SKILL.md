---
name: ai-agents
description: Use this skill when the user is adding LLM behaviour to a Microsoft Teams bot on Teams SDK 2.1 — calling OpenAI or Azure OpenAI directly with the `openai` SDK and `runTools()`, streaming into Teams, tools as `RunnableToolFunction`, conversation history in turn state, clarification cards, AI labels, feedback buttons, citations, suggested prompts. Triggers on "AI Teams bot", "OpenAI Teams", "function calling Teams", "streaming Teams response", "runTools", "Azure OpenAI Teams".
---

# AI agents in Teams (TypeScript)

The Teams SDK stays out of the intelligence layer: it has **no prompt, model or memory classes**. The model client and the tool loop are yours — the `openai` package — and the SDK provides routing, streaming, cards, state and Teams-native affordances (AI label, feedback, citations). The old SDK AI packages (a prompt class, an OpenAI model wrapper, and MCP/A2A plugins) are deprecated on npm; do not install them.

The guide below is bound to the OpenAI chat-completions wire protocol: OpenAI and Azure OpenAI work, other providers need their own client and loop. The official walkthrough is "Build an agent in Teams"; its source is `examples/ai-mcp` in `microsoft/teams.ts`. MCP servers and clients and A2A are in `mcp-a2a`.

## 1. Setup

```bash
npm install openai
```

```ts
// src/model.ts
import { AzureOpenAI, OpenAI } from 'openai';

// Azure OpenAI
export const azure = new AzureOpenAI({
  endpoint: process.env.AZURE_OPENAI_ENDPOINT!,
  apiKey: process.env.AZURE_OPENAI_API_KEY!,
  deployment: process.env.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME!,
  apiVersion: process.env.AZURE_OPENAI_API_VERSION || '2024-10-21',
});

// OpenAI itself: reads OPENAI_API_KEY from the environment
export const openai = new OpenAI();

export const MODEL = process.env.OPENAI_MODEL ?? process.env.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME!;
export const SYSTEM_PROMPT = 'You are a helpful Teams assistant. Keep answers short.';
```

Keep keys in `.env`; pass the model or deployment name through the environment so it can change without a release.

## 2. A streaming agent with history

`runTools()` sends your tool definitions, runs each tool the model calls, feeds the result back and repeats until the model produces text. `content` events carry the text deltas — forward them to the Teams stream.

```ts
import type { ChatCompletionMessageParam } from 'openai/resources/chat/completions';
import { App } from '@microsoft/teams.apps';
import { azure as client, MODEL, SYSTEM_PROMPT } from './model.js';

const app = new App({ state: true });          // conversation scope holds the history

app.on('message', async (ctx) => {
  const { activity, stream, send, state } = ctx;
  const history: ChatCompletionMessageParam[] = state?.conversation.get<ChatCompletionMessageParam[]>('history')
    ?? [{ role: 'system', content: SYSTEM_PROMPT }];
  history.push({ role: 'user', content: activity.text ?? '' });

  if (activity.conversation.conversationType !== 'personal') {
    // channels and group chats cannot stream: run to completion, then send
    const completion = await client.chat.completions.create({ model: MODEL, messages: history });
    const text = completion.choices[0]?.message?.content ?? '';
    history.push({ role: 'assistant', content: text });
    state?.conversation.set('history', history.slice(-40));
    await send(text);
    return;
  }

  const runner = client.chat.completions.runTools({ model: MODEL, messages: history, tools: [], stream: true });
  runner.on('content', (delta: string) => {
    if (stream.canceled) { runner.abort(); return; }     // the user pressed Stop
    stream.emit(delta);
  });
  await runner.done();

  // runner.messages holds the whole turn: system, user, tool calls, tool results, assistant
  state?.conversation.set('history', (runner.messages as ChatCompletionMessageParam[]).slice(-40));
});

app.start(process.env.PORT || 3978).catch(console.error);
```

- Keep one `ChatCompletionMessageParam[]` per conversation. Turn state (`new App({ state: true })`) stores it as JSON; configure `state.storage` with a shared store before running more than one instance (`sdk-patterns`).
- Cap the history (last 20–40 messages) or summarise old turns. Trim at a message boundary — a tool result without its tool call is rejected by the API.
- Streaming in Teams is 1:1 only, one streamed message per chat, two minutes from the first chunk. Details and the hand-off to message updates are in `messaging`.
- When the user presses Stop, `stream.canceled` turns true; abort the runner so no more tokens are spent.

## 3. Tools

A tool is a `RunnableToolFunction`: a JSON schema for the arguments, a `parse` function and the callback `runTools()` executes.

```ts
import type { RunnableToolFunction } from 'openai/lib/RunnableFunction';

type WeatherArgs = { city: string };

export const weatherTool: RunnableToolFunction<WeatherArgs> = {
  type: 'function',
  function: {
    name: 'get_weather',
    description: 'Current weather for a city',
    parameters: {
      type: 'object',
      properties: { city: { type: 'string' } },
      required: ['city'],
      additionalProperties: false,
    },
    function: async ({ city }: WeatherArgs) => `Sunny in ${city}`,    // return a string; JSON.stringify objects
    parse: (raw: string) => JSON.parse(raw) as WeatherArgs,
  },
};
```

Pass `tools: [weatherTool]` to `runTools`. Validate the arguments in `parse` or the callback before any side effect — the model can invent fields. The same wrapper turns MCP tools into runnable tools (`mcp-a2a`).

## 4. Clarification cards

A tool can ask the user a question with a card instead of guessing. The callback parks the card in a per-turn list and returns a short placeholder; the handler sends the card after the run.

```ts
import type { RunnableToolFunction } from 'openai/lib/RunnableFunction';
import { AdaptiveCard, ChoiceSetInput, ExecuteAction, SubmitData, TextBlock } from '@microsoft/teams.cards';

export const CLARIFICATION_VERB = 'clarification';
export const CLARIFICATION_INPUT_ID = 'clarificationChoice';

type ClarificationArgs = { question: string; options: string[] };

export function clarificationTool(pendingCards: AdaptiveCard[]): RunnableToolFunction<ClarificationArgs> {
  return {
    type: 'function',
    function: {
      name: 'request_clarification',
      description: 'Ask the user to pick between 2-4 interpretations when the request is ambiguous.',
      parameters: {
        type: 'object',
        properties: { question: { type: 'string' }, options: { type: 'array', items: { type: 'string' } } },
        required: ['question', 'options'],
        additionalProperties: false,
      },
      function: async (args: ClarificationArgs) => {
        pendingCards.push(
          new AdaptiveCard(
            new TextBlock(args.question, { weight: 'Bolder', wrap: true }),
            new ChoiceSetInput(...args.options.map((o) => ({ title: o, value: o })))
              .withId(CLARIFICATION_INPUT_ID)
              .withIsRequired(true),
          ).withActions(
            new ExecuteAction({ title: 'Submit' })
              .withData(new SubmitData(CLARIFICATION_VERB))
              .withAssociatedInputs('auto'),
          ),
        );
        return 'Clarification card attached.';
      },
      parse: (raw: string) => JSON.parse(raw) as ClarificationArgs,
    },
  };
}
```

After the run: if `pendingCards` is not empty, call `stream.clearText()` to drop streamed text and `stream.emit(new MessageActivityInput().addCard('adaptive', card).addAiGenerated())`. The user's choice returns through `card.action.clarification`, which feeds it back to the agent as the next user turn:

```ts
app.on('card.action.clarification', async ({ activity, send }) => {
  const data = (activity.value.action.data ?? {}) as Record<string, unknown>;
  const choice = typeof data['clarificationChoice'] === 'string' ? data['clarificationChoice'] : '';
  if (choice) await send(`You picked: ${choice}`);       // here: run the agent again with `choice`
  return { statusCode: 200, type: 'application/vnd.microsoft.activity.message', value: 'OK' } as const;
});
```

## 5. Teams affordances on AI output

Emit a closing marker activity to attach everything to the final streamed message:

```ts
import { MessageActivityInput } from '@microsoft/teams.api';

app.on('message', async ({ stream, activity }) => {
  for await (const delta of runAgent(activity.text)) stream.emit(delta);

  const finalMarker = new MessageActivityInput()
    .addAiGenerated()                 // the "AI generated" label
    .addFeedback('custom')            // thumbs up/down with a feedback form
    .addCitation(1, { name: 'Teams SDK docs', abstract: 'Where the answer came from', url: 'https://microsoft.github.io/teams-sdk/' })
    .withSuggestedActions({
      to: [activity.from.id],
      actions: [{ type: 'imBack', title: 'Show an example', value: 'Show an example' }],
    });
  stream.emit(finalMarker);
});

app.on('message.submit.feedback', async ({ activity, log }) => {
  const { reaction, feedback } = activity.value.actionValue;      // 'like' | 'dislike', and the form text as JSON
  log.info(`feedback on ${activity.replyToId}: ${reaction} ${feedback}`);
});
```

- Citations are numbered. Put `[1]`, `[2]` markers in the answer, and `addCitation(position, { name, abstract, url })` for each marker that has a source.
- Suggested prompts: ask the model for two short follow-ups with structured output (`response_format: { type: 'json_schema', … }`) and attach them with `withSuggestedActions`. If that call fails, skip it; the main answer has already shipped.
- Store feedback keyed by the sent message id (`const { id } = await send(…)`).

## 6. Where more is

- `references/openai-runtools.md` — client options, error handling, structured output, cost control.
- `mcp-a2a` — MCP tools for the agent, exposing the bot as an MCP server, bot-to-bot hand-off.
- `messaging` — the streaming window and updates.

## Common pitfalls

- **Streaming flashes nothing in a channel** — expected; gate on `conversationType === 'personal'`.
- **`401` from the model API** — wrong key, endpoint or deployment name for the client you built (`OpenAI` and `AzureOpenAI` are different).
- **The tool loop never ends** — a tool throws every time or keeps asking for the same call; cap tool rounds with `maxChatCompletions` on the runner options and return error text instead of throwing.
- **Tool messages duplicated** — the history already contains what `runner.messages` returns; overwrite the stored history, do not append to it.
- **A handler that runs for minutes** — Teams may drop the request; stream, or acknowledge and finish with `app.send`.
