# ai.tool — Let LLMs Call Tasks

Use `ai.tool` to wrap Trigger.dev tasks as tools that LLMs can call via the Vercel AI SDK.

## Basic Usage

```ts
import { task } from "@trigger.dev/sdk";
import { generateText, tool } from "ai";
import { openai } from "@ai-sdk/openai";

const searchTool = tool({
  description: "Search the web for information",
  parameters: z.object({ query: z.string() }),
  execute: async ({ query }) => {
    return searchTask.triggerAndWait({ query }).unwrap();
  },
});

export const agentTask = task({
  id: "agent-with-tools",
  machine: { preset: "medium-1x" },
  maxDuration: 300,
  run: async ({ goal }) => {
    const result = await generateText({
      model: openai("gpt-4o"),
      tools: { search: searchTool },
      maxSteps: 10,
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
    parameters: z.object({ query: z.string() }),
    execute: async ({ query }) => searchTask.triggerAndWait({ query }).unwrap(),
  }),
  calculate: tool({
    description: "Evaluate a math expression",
    parameters: z.object({ expression: z.string() }),
    execute: async ({ expression }) => calcTask.triggerAndWait({ expression }).unwrap(),
  }),
  database: tool({
    description: "Query the database",
    parameters: z.object({ sql: z.string() }),
    execute: async ({ sql }) => dbTask.triggerAndWait({ sql }).unwrap(),
  }),
};
```

Each tool call runs as a separate durable task with its own retries, logging, and observability.
