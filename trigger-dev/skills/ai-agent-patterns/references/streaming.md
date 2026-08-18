# Realtime Streams for AI

Stream LLM output from Trigger.dev tasks to your frontend in real time.

## Define a Stream

```ts
// trigger/streams.ts
import { streams } from "@trigger.dev/sdk";

export const aiStream = streams.define<string>({
  id: "ai-output",
});
```

## Pipe OpenAI Stream

```ts
import { task } from "@trigger.dev/sdk";
import { aiStream } from "./streams";
import OpenAI from "openai";

const openai = new OpenAI();

export const streamingAI = task({
  id: "streaming-ai",
  run: async ({ prompt }: { prompt: string }) => {
    const completion = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [{ role: "user", content: prompt }],
      stream: true,
    });

    const { waitUntilComplete } = aiStream.pipe(completion);
    await waitUntilComplete();
  },
});
```

## Pipe Vercel AI SDK Stream

```ts
import { streamText } from "ai";
import { openai } from "@ai-sdk/openai";

export const vercelStream = task({
  id: "vercel-stream",
  run: async ({ prompt }) => {
    const result = streamText({
      model: openai("gpt-4o"),
      prompt,
    });

    const { waitUntilComplete } = aiStream.pipe(result.textStream);
    await waitUntilComplete();
  },
});
```

## Read Stream in React

```tsx
"use client";
import { useRealtimeStream } from "@trigger.dev/react-hooks";
import { aiStream } from "../trigger/streams";

function AIResponse({ runId, accessToken }: Props) {
  const { parts, error } = useRealtimeStream(aiStream, runId, {
    accessToken,
    throttleInMs: 50,  // Control re-render frequency
  });

  if (error) return <div>Error: {error.message}</div>;
  if (!parts) return <div>Waiting for response...</div>;

  return <div className="whitespace-pre-wrap">{parts.join("")}</div>;
}
```

## Child-to-Parent Streaming

Stream data from a child task to the parent's stream:

```ts
export const parentTask = task({
  id: "parent-task",
  run: async ({ prompts }) => {
    for (const prompt of prompts) {
      const result = await streamingAI.triggerAndWait({ prompt });
      // Child's stream output is visible to subscribed clients
    }
  },
});
```
