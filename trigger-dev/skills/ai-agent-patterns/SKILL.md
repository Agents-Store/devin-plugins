---
name: ai-agent-patterns
description: Build AI agent workflows on Trigger.dev — prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer, and human-in-the-loop. Use when the user asks to "build an AI agent with trigger.dev", "chain LLM calls", "parallelize AI tasks", "create an orchestrator", "add human approval to workflow", or needs patterns for LLM-powered durable execution.
---

# AI Agent Patterns

Build production-ready AI agents using Trigger.dev's durable execution.

## Pattern Selection

```
Need to...                              → Use
─────────────────────────────────────────────────────
Process items in parallel               → Parallelization
Route to different models/handlers      → Routing
Chain steps with validation gates       → Prompt Chaining
Coordinate multiple specialized tasks   → Orchestrator-Workers
Self-improve until quality threshold    → Evaluator-Optimizer
Pause for human approval                → Human-in-the-Loop
Stream progress to frontend             → Realtime Streams
Let LLM call your tasks as tools        → ai.tool
```

## 1. Prompt Chaining (Sequential with Gates)

```ts
import { task } from "@trigger.dev/sdk";
import { generateText } from "ai";
import { openai } from "@ai-sdk/openai";

export const translateCopy = task({
  id: "translate-copy",
  run: async ({ text, targetLanguage, maxWords }) => {
    const draft = await generateText({
      model: openai("gpt-4o"),
      prompt: `Write marketing copy about: ${text}`,
    });

    // Gate: validate before continuing
    const wordCount = draft.text.split(/\s+/).length;
    if (wordCount > maxWords) {
      throw new Error(`Draft too long: ${wordCount} > ${maxWords}`);
    }

    const translated = await generateText({
      model: openai("gpt-4o"),
      prompt: `Translate to ${targetLanguage}: ${draft.text}`,
    });

    return { draft: draft.text, translated: translated.text };
  },
});
```

## 2. Routing (Classify then Dispatch)

```ts
export const routeQuestion = task({
  id: "route-question",
  run: async ({ question }) => {
    const routing = await generateText({
      model: openai("gpt-4o-mini"),
      messages: [{
        role: "system",
        content: `Classify complexity. Return JSON: {"model": "gpt-4o" | "o1-mini"}
          - gpt-4o: simple factual questions
          - o1-mini: complex reasoning, math, code`,
      }, { role: "user", content: question }],
    });

    const { model } = JSON.parse(routing.text);
    const answer = await generateText({ model: openai(model), prompt: question });
    return { answer: answer.text, routedTo: model };
  },
});
```

## 3. Parallelization

```ts
import { batch, task } from "@trigger.dev/sdk";

export const analyzeContent = task({
  id: "analyze-content",
  run: async ({ text }) => {
    const { runs: [sentiment, summary, moderation] } =
      await batch.triggerByTaskAndWait([
        { task: analyzeSentiment, payload: { text } },
        { task: summarizeText, payload: { text } },
        { task: moderateContent, payload: { text } },
      ]);

    if (moderation.ok && moderation.output.flagged) {
      return { error: "Content flagged", reason: moderation.output.reason };
    }

    return {
      sentiment: sentiment.ok ? sentiment.output : null,
      summary: summary.ok ? summary.output : null,
    };
  },
});
```

## 4. Orchestrator-Workers (Fan-out/Fan-in)

```ts
export const factChecker = task({
  id: "fact-checker",
  run: async ({ article }) => {
    const { runs: [extractResult] } = await batch.triggerByTaskAndWait([
      { task: extractClaims, payload: { article } },
    ]);
    if (!extractResult.ok) throw new Error("Failed to extract claims");

    const { runs } = await batch.triggerByTaskAndWait(
      extractResult.output.map(claim => ({ task: verifyClaim, payload: claim }))
    );

    const verified = runs
      .filter((r): r is typeof r & { ok: true } => r.ok)
      .map(r => r.output);

    return { claims: extractResult.output, verifications: verified };
  },
});
```

## 5. Evaluator-Optimizer (Self-Refining)

```ts
export const refineTranslation = task({
  id: "refine-translation",
  run: async ({ text, targetLanguage, feedback, attempt = 0 }) => {
    if (attempt >= 5) return { text, status: "MAX_ATTEMPTS", attempts: attempt };

    const prompt = feedback
      ? `Improve based on feedback:\n${feedback}\n\nOriginal: ${text}`
      : `Translate to ${targetLanguage}: ${text}`;

    const translation = await generateText({ model: openai("gpt-4o"), prompt });

    const evaluation = await generateText({
      model: openai("gpt-4o"),
      prompt: `Evaluate translation. Reply APPROVED or provide feedback:\n${translation.text}`,
    });

    if (evaluation.text.includes("APPROVED")) {
      return { text: translation.text, status: "APPROVED", attempts: attempt + 1 };
    }

    return refineTranslation.triggerAndWait({
      text, targetLanguage, feedback: evaluation.text, attempt: attempt + 1,
    }).unwrap();
  },
});
```

## Error Handling for Batch Results

```ts
const { runs } = await batch.triggerByTaskAndWait([...]);

for (const run of runs) {
  if (run.ok) {
    console.log(run.output);
  } else {
    console.error(run.error, run.taskIdentifier);
  }
}
```

## Deeper Reference

- @references/orchestration.md — advanced orchestration patterns
- @references/ai-tool.md — letting LLMs call tasks as tools
- @references/waitpoints.md — human-in-the-loop patterns
- @references/streaming.md — realtime AI streaming
