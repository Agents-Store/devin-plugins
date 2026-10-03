# Task-Backed AI Tools — Let LLMs Call Tasks

Wrap Trigger.dev tasks as tools that an LLM can call through the Vercel AI SDK. Each tool call runs as a separate durable subtask with its own retries, logging and observability.

**AI SDK version.** `@trigger.dev/sdk` 4.5.0 and later require `ai` `^5`, `^6` or `>=7` (peer dependency). AI SDK v4 is not supported: the v4 tool-schema key is now `inputSchema`, and the v4 step-count option is replaced by `stopWhen: stepCountIs(n)`.

The older `ai.tool(task)` helper is deprecated (it may be removed in a future major). Build the tool with the AI SDK's own `tool()` and pass `execute: ai.toolExecute(task)`. `ai` here is the Trigger.dev helper, imported from `@trigger.dev/sdk/ai`, not the AI SDK package.

## Basic Usage

```ts
import { schemaTask } from "@trigger.dev/sdk";
import { ai } from "@trigger.dev/sdk/ai";
import { generateText, stepCountIs, tool } from "ai";
import { openai } from "@ai-sdk/openai";
import { z } from "zod";

// The subtask that does the work
export const searchTask = schemaTask({
  id: "search-web",
  description: "Search the web for information",
  schema: z.object({ query: z.string() }),
  run: async ({ query }) => {
    return { results: await runSearch(query) };
  },
});

const searchTool = tool({
  description: searchTask.description ?? "",
  inputSchema: searchTask.schema!,
  execute: ai.toolExecute(searchTask),
});

export const agentTask = schemaTask({
  id: "agent-with-tools",
  schema: z.object({ goal: z.string() }),
  machine: "medium-1x",
  maxDuration: 300,
  run: async ({ goal }) => {
    const result = await generateText({
      model: openai("gpt-4o"),
      tools: { search: searchTool },
      stopWhen: stepCountIs(10),
      prompt: goal,
    });
    return { answer: result.text };
  },
});
```

## Multi-Tool Agent

```ts
const tools = {
  search: tool({
    description: "Search the web",
    inputSchema: z.object({ query: z.string() }),
    execute: ai.toolExecute(searchTask),
  }),
  calculate: tool({
    description: "Evaluate a math expression",
    inputSchema: z.object({ expression: z.string() }),
    execute: ai.toolExecute(calcTask),
  }),
  database: tool({
    description: "Query the database",
    inputSchema: z.object({ sql: z.string() }),
    execute: ai.toolExecute(dbTask),
  }),
};
```

`ai.toolExecute` works with `schemaTask` (Zod, ArkType or any schema that exposes JSON Schema). Tool-level AI SDK options such as `toModelOutput` go on `tool({ ... })`, not on `ai.toolExecute`.

Inside the subtask, `ai.toolCallId()` returns the current tool call id, and `ai.chatContext<typeof myChat>()` returns the chat context (`chatId`, `clientData`) when the parent is a `chat.agent`. See the **ai-chat-agents** skill.
