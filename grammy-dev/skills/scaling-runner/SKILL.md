---
name: scaling-runner
description: This skill should be used when the user asks about "grammY runner", "@grammyjs/runner", "concurrent updates in grammY", "rate limit grammY", "transformer-throttler", "auto-retry", "sequentialize", "high-throughput Telegram bot", or needs to scale a grammY bot beyond default sequential polling.
---

# grammY — Scaling & Runner

By default `bot.start()` processes updates one at a time. For high-throughput bots you want concurrency, proactive rate-limit shaping, and automatic retries on 429.

## When you actually need scaling

You probably don't. grammY's default polling handles most bots fine. Reach for the runner only when:

- Single handler latency >2 seconds AND you have many users.
- You see Telegram returning 429 (Too Many Requests).
- Updates back up faster than you process them (`bot.start` log shows growing batches).

## @grammyjs/runner — concurrent updates

```bash
npm install @grammyjs/runner
```

Replace `bot.start()` with `run(bot)`:

```typescript
import { run } from "@grammyjs/runner";

const handle = run(bot);

process.once("SIGINT",  () => handle.stop());
process.once("SIGTERM", () => handle.stop());
```

The runner fetches updates concurrently and dispatches handlers in parallel — your middleware needs to be safe to run for multiple updates at once.

## sequentialize — concurrency safety per chat

If two updates from the same chat run in parallel, you can get race conditions (e.g. both increment a session counter to the same value). `sequentialize` serializes updates that share a key:

```typescript
import { run, sequentialize } from "@grammyjs/runner";

function getSessionKey(ctx: Context): string | undefined {
  return ctx.chat?.id.toString();
}

bot.use(sequentialize(getSessionKey));   // install BEFORE session/handlers
bot.use(session({ initial: () => ({ counter: 0 }), getSessionKey }));
// … rest of handlers

run(bot);
```

The key function must match your `session({ getSessionKey })`. Updates from different chats run in parallel; updates from the same chat queue up.

For multi-sessions, return an array of keys:

```typescript
function getMultiKeys(ctx: Context): string[] | undefined {
  const chat = ctx.chat?.id.toString();
  const user = ctx.from?.id.toString();
  return chat && user ? [chat, user] : undefined;
}
bot.use(sequentialize(getMultiKeys));
```

## auto-retry — handle 429 transparently

Telegram returns `Too Many Requests: retry after N` when you exceed limits. The `@grammyjs/auto-retry` transformer waits the requested time and retries:

```bash
npm install @grammyjs/auto-retry
```

```typescript
import { autoRetry } from "@grammyjs/auto-retry";

bot.api.config.use(autoRetry({
  maxAttempts: 3,         // up to 3 retries
  maxDelaySeconds: 10,    // never wait longer than 10s — fail fast otherwise
  retryOnInternalServerErrors: true,
}));
```

Without auto-retry you'd see `GrammyError: 429 Too Many Requests` bubbling into your handlers — your bot just stops talking until the user retries.

## transformer-throttler — proactive shaping

Auto-retry is reactive. `@grammyjs/transformer-throttler` *prevents* hitting the limit by enqueueing outgoing calls via Bottleneck:

```bash
npm install @grammyjs/transformer-throttler
```

```typescript
import { apiThrottler } from "@grammyjs/transformer-throttler";

bot.api.config.use(apiThrottler({
  // Global limit (across all chats)
  global: { reservoir: 30, reservoirRefreshAmount: 30, reservoirRefreshInterval: 1000 },
  // Per-group limit
  group:  { reservoir: 20, reservoirRefreshAmount: 20, reservoirRefreshInterval: 60_000 },
  // Per-out-chat limit
  out:    { reservoir: 1, reservoirRefreshAmount: 1, reservoirRefreshInterval: 1000 },
}));
```

Recommended pairing: **install BOTH** — throttler proactively, auto-retry as the safety net.

```typescript
bot.api.config.use(apiThrottler());     // first
bot.api.config.use(autoRetry());        // second (executes if throttler missed)
```

## Bot API rate limits — what you're shaping against

Documented Telegram limits (subject to change):

| Action | Limit |
|---|---|
| Outgoing messages to the same user | ~1 / second |
| Outgoing messages to the same group | ~20 / minute |
| Global outgoing | ~30 / second |
| Broadcasts | Use `sendMessage` in chunks of ≤30/s |

The throttler defaults approximate these. Telegram also enforces *undocumented* anti-spam limits — there's no way to know exactly where the line is, so always include auto-retry.

## Bot.api.config — transformer order matters

Transformers are applied in the order you `use()` them, outermost first. The recommended order:

```typescript
bot.api.config.use(apiThrottler());     // 1. shape outbound rate
bot.api.config.use(autoRetry());        // 2. retry on 429 / 5xx
// (your custom transformers if any)
```

Reverse this and auto-retry happens *before* throttling — wasted requests when you're already past the limit.

## High-throughput pattern (canonical)

```typescript
import { Bot } from "grammy";
import { run, sequentialize } from "@grammyjs/runner";
import { apiThrottler } from "@grammyjs/transformer-throttler";
import { autoRetry } from "@grammyjs/auto-retry";

const bot = new Bot<MyContext>(process.env.BOT_TOKEN!);

// Outbound shaping
bot.api.config.use(apiThrottler());
bot.api.config.use(autoRetry());

// Inbound safety
bot.use(sequentialize((ctx) => ctx.chat?.id.toString()));
bot.use(session({ initial: () => ({}), getSessionKey: (ctx) => ctx.chat?.id.toString() }));

// … handlers …

bot.catch(/* … */);

const handle = run(bot);
process.once("SIGINT",  () => handle.stop());
process.once("SIGTERM", () => handle.stop());
```

This stack handles thousands of concurrent users without races and without 429s.

## When to use webhooks instead

Long polling + runner scales vertically — single process, single host. For horizontal scaling, switch to webhooks (`webhookCallback`) behind a load balancer. See `deployment-hosting` for hosting options.

Note: **`run()` is for long polling only.** With webhooks the platform's HTTP runtime handles concurrency for you; throttler + auto-retry still apply.
