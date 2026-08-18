---
name: realtime
description: Subscribe to Trigger.dev task runs in real-time from frontend and backend. Use when the user asks to "show task progress in UI", "stream AI responses", "use trigger.dev React hooks", "subscribe to runs", "build a progress indicator", "use useRealtimeRun", or needs live task status in a React application.
---

# Trigger.dev Realtime

Subscribe to task runs and stream data in real-time from frontend and backend.

## When to Use

- Building progress indicators for long-running tasks
- Creating live dashboards showing task status
- Streaming AI/LLM responses to the UI
- React components that trigger and monitor tasks
- Waiting for user approval in tasks (human-in-the-loop)

## Authentication

### Create Public Access Token (Backend)

```ts
import { auth } from "@trigger.dev/sdk";

const publicToken = await auth.createPublicToken({
  scopes: {
    read: {
      runs: ["run_123"],
      tasks: ["my-task"],
    },
  },
  expirationTime: "1h",
});
```

### Create Trigger Token (for frontend triggering)

```ts
const triggerToken = await auth.createTriggerPublicToken("my-task", {
  expirationTime: "30m",
});
```

## React Hooks

### Installation

```bash
npm add @trigger.dev/react-hooks
```

### Trigger Task from React

```tsx
"use client";
import { useRealtimeTaskTrigger } from "@trigger.dev/react-hooks";
import type { myTask } from "../trigger/tasks";

function TaskTrigger({ accessToken }: { accessToken: string }) {
  const { submit, run, isLoading } = useRealtimeTaskTrigger<typeof myTask>(
    "my-task",
    { accessToken }
  );

  return (
    <div>
      <button onClick={() => submit({ data: "value" })} disabled={isLoading}>
        Start Task
      </button>
      {run && (
        <div>
          <p>Status: {run.status}</p>
          <p>Progress: {run.metadata?.progress}%</p>
          {run.output && <p>Result: {JSON.stringify(run.output)}</p>}
        </div>
      )}
    </div>
  );
}
```

### Subscribe to Existing Run

```tsx
import { useRealtimeRun } from "@trigger.dev/react-hooks";

function RunStatus({ runId, accessToken }: { runId: string; accessToken: string }) {
  const { run, error } = useRealtimeRun<typeof myTask>(runId, {
    accessToken,
    onComplete: (run) => console.log("Completed:", run.output),
  });

  if (error) return <div>Error: {error.message}</div>;
  if (!run) return <div>Loading...</div>;

  return <p>Status: {run.status} — Progress: {run.metadata?.progress || 0}%</p>;
}
```

### Subscribe to Tagged Runs

```tsx
import { useRealtimeRunsWithTag } from "@trigger.dev/react-hooks";

function UserTasks({ userId, accessToken }: Props) {
  const { runs } = useRealtimeRunsWithTag(`user-${userId}`, { accessToken });
  return (
    <ul>{runs.map(run => <li key={run.id}>{run.id}: {run.status}</li>)}</ul>
  );
}
```

## Realtime Streams (AI/LLM)

### Define Stream

```ts
// trigger/streams.ts
import { streams } from "@trigger.dev/sdk";
export const aiStream = streams.define<string>({ id: "ai-output" });
```

### Pipe Stream in Task

```ts
import { task } from "@trigger.dev/sdk";
import { aiStream } from "./streams";

export const streamingTask = task({
  id: "streaming-task",
  run: async (payload: { prompt: string }) => {
    const completion = await openai.chat.completions.create({
      model: "gpt-4", messages: [{ role: "user", content: payload.prompt }], stream: true,
    });
    const { waitUntilComplete } = aiStream.pipe(completion);
    await waitUntilComplete();
  },
});
```

### Read Stream in React

```tsx
import { useRealtimeStream } from "@trigger.dev/react-hooks";
import { aiStream } from "../trigger/streams";

function AIResponse({ runId, accessToken }: Props) {
  const { parts, error } = useRealtimeStream(aiStream, runId, {
    accessToken, throttleInMs: 50,
  });
  if (!parts) return <div>Waiting...</div>;
  return <div>{parts.join("")}</div>;
}
```

## Wait Tokens (Human-in-the-loop)

### Complete Token from React

```tsx
import { useWaitToken } from "@trigger.dev/react-hooks";

function ApprovalButton({ tokenId, accessToken }: Props) {
  const { complete } = useWaitToken(tokenId, { accessToken });
  return (
    <div>
      <button onClick={() => complete({ approved: true })}>Approve</button>
      <button onClick={() => complete({ approved: false })}>Reject</button>
    </div>
  );
}
```

## Backend Subscriptions

```ts
import { runs, tasks } from "@trigger.dev/sdk";

const handle = await tasks.trigger("my-task", { data: "value" });

for await (const run of runs.subscribeToRun(handle.id)) {
  console.log(`Status: ${run.status}`);
  if (run.status === "COMPLETED") break;
}
```

## Run Object Properties

| Property | Description |
|----------|-------------|
| `id` | Unique run identifier |
| `status` | QUEUED, EXECUTING, COMPLETED, FAILED, CANCELED |
| `payload` | Task input (typed) |
| `output` | Task result (typed, when completed) |
| `metadata` | Real-time updatable data |
| `createdAt` | Start timestamp |

## Deeper Reference

- @references/realtime-reference.md — complete Realtime API
