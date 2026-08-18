# Orchestration Patterns

## batch.triggerByTaskAndWait

The primary tool for typed parallel execution of different tasks:

```ts
import { batch } from "@trigger.dev/sdk";

const { runs } = await batch.triggerByTaskAndWait([
  { task: taskA, payload: { foo: 1 } },
  { task: taskB, payload: { bar: "x" } },
  { task: taskC, payload: { baz: true } },
]);

// Each run is typed according to its task
const [resultA, resultB, resultC] = runs;
if (resultA.ok) console.log(resultA.output); // Typed as taskA output
```

## Fan-Out / Fan-In

Distribute work across many workers, collect results:

```ts
export const mapReduce = task({
  id: "map-reduce",
  run: async (payload: { documents: string[] }) => {
    // Fan-out: process each document in parallel
    const summaries = await summarizeDoc.batchTriggerAndWait(
      payload.documents.map(doc => ({ payload: { doc } }))
    );

    // Fan-in: combine all summaries
    const validSummaries = summaries
      .filter(r => r.ok)
      .map(r => r.output);

    const combined = await combineSummaries.triggerAndWait({
      summaries: validSummaries,
    }).unwrap();

    return combined;
  },
});
```

## Pipeline Pattern

Sequential processing with typed handoffs:

```ts
export const pipeline = task({
  id: "content-pipeline",
  run: async ({ rawData }) => {
    const cleaned = await cleanData.triggerAndWait({ data: rawData }).unwrap();
    const enriched = await enrichData.triggerAndWait({ data: cleaned }).unwrap();
    const indexed = await indexData.triggerAndWait({ data: enriched }).unwrap();
    return indexed;
  },
});
```

## Self-Recursive Pattern

Task calls itself with updated state:

```ts
export const crawler = task({
  id: "web-crawler",
  run: async ({ urls, depth = 0, maxDepth = 3 }) => {
    if (depth >= maxDepth) return { urls, depth };

    const newLinks = await extractLinks(urls);
    if (newLinks.length === 0) return { urls, depth };

    return crawler.triggerAndWait({
      urls: newLinks,
      depth: depth + 1,
      maxDepth,
    }).unwrap();
  },
});
```
