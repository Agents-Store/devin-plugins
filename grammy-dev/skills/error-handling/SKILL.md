---
name: error-handling
description: This skill should be used when the user asks about "grammY error handling", "bot.catch", "GrammyError", "HttpError", "BotError", "errorBoundary", "bot crashed", "unhandled promise rejection in bot", or needs to understand the three error types grammY throws and how to catch them.
---

# grammY — Error Handling

grammY wraps every middleware error into a `BotError` and routes it to `bot.catch`. There are exactly three error classes you ever need to know.

## The three error types

| Type | Thrown when | How to inspect |
|---|---|---|
| `GrammyError` | Bot API responded with `ok: false`. Your request reached Telegram but Telegram rejected it (bad parameter, no permission, blocked by user, etc.) | `err.description`, `err.error_code`, `err.parameters` |
| `HttpError` | Could not reach Telegram at all — DNS, TLS, timeout, network down | `err.error` (the underlying network error) |
| `BotError<C>` | Wraps any error thrown from middleware. Contains both the original error AND the update context that triggered it | `err.error`, `err.ctx` |

`BotError` is always what reaches `bot.catch`. Its `.error` property holds the real cause (a `GrammyError`, `HttpError`, or any other thrown value).

## The canonical bot.catch handler

```typescript
import { Bot, GrammyError, HttpError } from "grammy";

const bot = new Bot(process.env.BOT_TOKEN!);

// … register handlers …

bot.catch((err) => {
  const ctx = err.ctx;
  console.error(`Error while handling update ${ctx.update.update_id}:`);
  const e = err.error;
  if (e instanceof GrammyError) {
    console.error("Error in request:", e.description);
  } else if (e instanceof HttpError) {
    console.error("Could not contact Telegram:", e);
  } else {
    console.error("Unknown error:", e);
  }
});
```

**Always install `bot.catch`.** Without it, grammY logs to stderr and may crash the process on unhandled promise rejections in some Node versions.

## Frequent GrammyError descriptions

| `description` | Meaning | Fix |
|---|---|---|
| `Unauthorized` | Token wrong or revoked | Re-issue with BotFather, update env var |
| `Forbidden: bot was blocked by the user` | User blocked your bot | Mark user as opted-out in your DB; don't send |
| `Forbidden: bot is not a member of the channel chat` | You tried to post in a channel where the bot isn't admin | Add bot as admin |
| `Bad Request: message is too long` | Text >4096 chars | Chunk into 4000-char slices |
| `Bad Request: message text is empty` | Sent empty string | Validate before sending |
| `Bad Request: chat not found` | Chat id wrong or bot never met that chat | Verify id |
| `Too Many Requests: retry after N` | Hit Telegram's rate limit | Install `@grammyjs/auto-retry` and/or `@grammyjs/transformer-throttler` (see `scaling-runner`) |
| `Bad Request: query is too old` | Replied to a callback query >15 min after it arrived | Answer faster |

`err.parameters` may include `retry_after` (seconds to wait) or `migrate_to_chat_id` (group → supergroup migration).

## errorBoundary — scoped catching

`bot.catch` is the global last resort. To catch errors only in a sub-tree of middleware without affecting siblings, wrap it in `errorBoundary`:

```typescript
import { type BotError, type NextFunction } from "grammy";

function logAndContinue(err: BotError) {
  console.error("Admin branch crashed:", err);
  // not re-thrown → other branches keep running
}

const safe = bot.errorBoundary(logAndContinue);
safe.command("admin-stats", adminStatsHandler);
safe.command("admin-broadcast", broadcastHandler);

// To swallow errors silently and let processing continue:
const suppress = (_err: BotError, next: NextFunction) => next();
bot.errorBoundary(suppress).on("edited_message", noisyHandler);
```

## Retrying API calls

Don't write retry loops by hand — install the official transformer:

```bash
npm install @grammyjs/auto-retry
```

```typescript
import { autoRetry } from "@grammyjs/auto-retry";

bot.api.config.use(autoRetry({
  maxAttempts: 3,
  maxDelaySeconds: 10,
}));
```

It transparently waits `retry_after` seconds when Telegram returns 429.

For full rate-limit shaping (proactive throttling, not just reactive retry), combine with `@grammyjs/transformer-throttler` — see `scaling-runner`.

## Sending users a friendly error message

```typescript
bot.catch(async (err) => {
  const e = err.error;
  console.error("update", err.ctx.update.update_id, e);

  if (e instanceof GrammyError && e.description.includes("blocked by the user")) {
    return; // can't reach them, nothing to do
  }
  try {
    await err.ctx.reply("Something went wrong on my side. Try again in a moment.");
  } catch (_) { /* user may have blocked us — give up */ }
});
```

Always wrap the user-facing reply in its own try/catch — sending the apology can itself throw if the chat is no longer reachable.

## Sentry / observability hook

```typescript
import * as Sentry from "@sentry/node";

bot.catch((err) => {
  Sentry.withScope((scope) => {
    scope.setContext("update", err.ctx.update);
    scope.setUser({ id: String(err.ctx.from?.id) });
    Sentry.captureException(err.error);
  });
});
```

## Webhook vs polling — error behavior differs

- **Long polling (`bot.start()`)**: errors caught by `bot.catch` are logged; the process keeps polling.
- **Webhooks (`webhookCallback(bot, ...)`)**: if you do *not* install `bot.catch`, the wrapper rejects with the error, which the underlying HTTP framework typically returns as 500 — Telegram will retry the update, causing duplicates. **Always install `bot.catch` for webhook bots.**
