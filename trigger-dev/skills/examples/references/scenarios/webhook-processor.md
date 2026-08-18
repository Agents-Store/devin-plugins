# Scenario: Webhook Processor

Complete example of a webhook processing task with queue, retry, and monitoring.

## Task Definition

```ts
// src/trigger/webhook-processor.ts
import { task, queue } from "@trigger.dev/sdk";
import { z } from "zod";

const webhookQueue = queue({
  name: "webhook-processing",
  concurrencyLimit: 10,
});

const WebhookPayload = z.object({
  event: z.string(),
  data: z.record(z.unknown()),
  timestamp: z.string().datetime(),
  source: z.string(),
});

export const processWebhook = task({
  id: "process-webhook",
  queue: webhookQueue,
  retry: {
    maxAttempts: 5,
    factor: 2,
    minTimeoutInMs: 1000,
    maxTimeoutInMs: 30000,
  },
  run: async (payload: z.infer<typeof WebhookPayload>) => {
    const validated = WebhookPayload.parse(payload);

    console.log(`Processing ${validated.event} from ${validated.source}`);

    switch (validated.event) {
      case "order.created":
        return await handleOrderCreated(validated.data);
      case "payment.completed":
        return await handlePaymentCompleted(validated.data);
      case "user.registered":
        return await handleUserRegistered(validated.data);
      default:
        console.warn(`Unknown event: ${validated.event}`);
        return { skipped: true, event: validated.event };
    }
  },
});

async function handleOrderCreated(data: Record<string, unknown>) {
  // Process order, create invoice, send notification
  return { processed: true, type: "order.created" };
}

async function handlePaymentCompleted(data: Record<string, unknown>) {
  return { processed: true, type: "payment.completed" };
}

async function handleUserRegistered(data: Record<string, unknown>) {
  return { processed: true, type: "user.registered" };
}
```

## Triggering from API Route

```ts
// app/api/webhook/route.ts (Next.js)
import { tasks } from "@trigger.dev/sdk";
import type { processWebhook } from "@/trigger/webhook-processor";

export async function POST(req: Request) {
  const body = await req.json();

  const handle = await tasks.trigger<typeof processWebhook>("process-webhook", {
    event: body.event,
    data: body.data,
    timestamp: new Date().toISOString(),
    source: req.headers.get("x-webhook-source") || "unknown",
  });

  return Response.json({ runId: handle.id });
}
```

## MCP Monitoring

```
1. list_runs(taskIdentifier="process-webhook", period="1h")
2. list_runs(status="FAILED", taskIdentifier="process-webhook", period="1d")
3. get_run_details(runId="run_xxx") → check error trace
```
