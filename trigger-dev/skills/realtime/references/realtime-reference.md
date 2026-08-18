# Realtime API Reference

## Token Types

| Token Type | Purpose | Created By | Scopes |
|-----------|---------|------------|--------|
| Public Access Token | Read-only access to runs | `auth.createPublicToken()` | read: runs, tasks, tags, batches |
| Trigger Token | Trigger + read | `auth.createTriggerPublicToken()` | trigger specific task + read |

## Public Access Token — Full Options

```ts
import { auth } from "@trigger.dev/sdk";

const token = await auth.createPublicToken({
  scopes: {
    read: {
      runs: ["run_123", "run_456"],     // Specific run IDs
      tasks: ["my-task"],                // All runs of a task
      tags: ["user-123"],                // All runs with tag
      batch: ["batch_abc"],              // Batch runs
    },
  },
  expirationTime: "1h",  // "30m", "1h", "24h", etc.
});
```

## React Hooks Reference

### useRealtimeTaskTrigger

Trigger a task and subscribe to its run in one step:

```tsx
const { submit, run, isLoading, error } = useRealtimeTaskTrigger<typeof myTask>(
  "my-task",
  { accessToken }
);
```

### useRealtimeRun

Subscribe to an existing run:

```tsx
const { run, error } = useRealtimeRun<typeof myTask>(runId, {
  accessToken,
  onComplete: (run) => {},
  onError: (error) => {},
});
```

### useRealtimeRunsWithTag

Subscribe to all runs with a specific tag:

```tsx
const { runs, error } = useRealtimeRunsWithTag("user-123", { accessToken });
```

### useRealtimeStream

Subscribe to a realtime stream:

```tsx
const { parts, error } = useRealtimeStream(aiStream, runId, {
  accessToken,
  throttleInMs: 50,
});
```

### useWaitToken

Complete a wait token from the UI:

```tsx
const { complete, isCompleting } = useWaitToken(tokenId, { accessToken });
await complete({ approved: true });
```

## Backend Subscription Methods

```ts
import { runs } from "@trigger.dev/sdk";

// Subscribe to a single run
for await (const run of runs.subscribeToRun(runId)) { }

// Subscribe to all runs with a tag
for await (const run of runs.subscribeToRunsWithTag("user-123")) { }

// Subscribe to a batch
for await (const run of runs.subscribeToBatch(batchId)) { }
```

## Stream Definition

```ts
import { streams } from "@trigger.dev/sdk";

// Define typed stream
export const myStream = streams.define<string>({ id: "my-stream" });

// Pipe data in a task
const { waitUntilComplete } = myStream.pipe(readableStream);
await waitUntilComplete();
```

## Best Practices

1. Scope tokens narrowly — only grant necessary permissions
2. Set short expiration times
3. Use typed hooks — pass task types for proper inference
4. Handle errors — always check for errors in hooks
5. Throttle streams — use `throttleInMs` to control re-renders
