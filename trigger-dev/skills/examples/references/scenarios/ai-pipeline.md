# Scenario: AI Pipeline

Multi-step AI agent pipeline with chaining, parallelization, and streaming.

## Task Definitions

```ts
// src/trigger/ai-pipeline.ts
import { task, batch, metadata } from "@trigger.dev/sdk";
import { generateText, streamText } from "ai";
import { openai } from "@ai-sdk/openai";
import { streams } from "@trigger.dev/sdk";

// Define stream for live output
export const pipelineStream = streams.define<string>({ id: "pipeline-output" });

// Step 1: Research
export const researchTopic = task({
  id: "research-topic",
  machine: { preset: "medium-1x" },
  retry: { maxAttempts: 3 },
  run: async ({ topic }: { topic: string }) => {
    const result = await generateText({
      model: openai("gpt-4o"),
      prompt: `Research the topic "${topic}". Provide key facts, statistics, and insights.`,
    });
    return { research: result.text };
  },
});

// Step 2: Generate outline (depends on research)
export const generateOutline = task({
  id: "generate-outline",
  machine: { preset: "small-1x" },
  run: async ({ research }: { research: string }) => {
    const result = await generateText({
      model: openai("gpt-4o-mini"),
      prompt: `Create an article outline from this research:\n${research}`,
    });
    return { outline: result.text };
  },
});

// Step 3: Write article with streaming
export const writeArticle = task({
  id: "write-article",
  machine: { preset: "medium-1x" },
  maxDuration: 120,
  run: async ({ outline, research }: { outline: string; research: string }) => {
    const result = streamText({
      model: openai("gpt-4o"),
      prompt: `Write a detailed article from this outline:\n${outline}\n\nUsing this research:\n${research}`,
    });

    const { waitUntilComplete } = pipelineStream.pipe(result.textStream);
    await waitUntilComplete();

    return { article: await result.text };
  },
});

// Orchestrator: chains all steps
export const contentPipeline = task({
  id: "content-pipeline",
  machine: { preset: "medium-1x" },
  maxDuration: 300,
  run: async ({ topic }: { topic: string }) => {
    metadata.set("status", "researching");

    // Step 1: Research (parallel — multiple sources)
    const { runs: [result1, result2] } = await batch.triggerByTaskAndWait([
      { task: researchTopic, payload: { topic } },
      { task: researchTopic, payload: { topic: `${topic} latest developments` } },
    ]);

    const research = [
      result1.ok ? result1.output.research : "",
      result2.ok ? result2.output.research : "",
    ].join("\n\n");

    metadata.set("status", "outlining");

    // Step 2: Outline
    const outline = await generateOutline.triggerAndWait({ research }).unwrap();

    metadata.set("status", "writing");

    // Step 3: Write with streaming
    const article = await writeArticle.triggerAndWait({
      outline: outline.outline,
      research,
    }).unwrap();

    metadata.set("status", "completed");

    return { topic, article: article.article };
  },
});
```

## Frontend Integration

```tsx
"use client";
import { useRealtimeTaskTrigger, useRealtimeStream } from "@trigger.dev/react-hooks";
import { pipelineStream } from "../trigger/ai-pipeline";
import type { contentPipeline } from "../trigger/ai-pipeline";

function ContentGenerator({ accessToken }: { accessToken: string }) {
  const { submit, run } = useRealtimeTaskTrigger<typeof contentPipeline>(
    "content-pipeline",
    { accessToken }
  );

  return (
    <div>
      <button onClick={() => submit({ topic: "AI in healthcare" })}>
        Generate Article
      </button>
      {run && (
        <div>
          <p>Status: {run.metadata?.status}</p>
          <StreamOutput runId={run.id} accessToken={accessToken} />
        </div>
      )}
    </div>
  );
}

function StreamOutput({ runId, accessToken }: { runId: string; accessToken: string }) {
  const { parts } = useRealtimeStream(pipelineStream, runId, {
    accessToken, throttleInMs: 50,
  });
  return <div className="prose">{parts?.join("") || "Waiting..."}</div>;
}
```
