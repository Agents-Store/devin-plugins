---
name: middleware
description: This skill should be used when the user asks about "grammY middleware", "bot.use", "Composer", "middleware ordering", "skip handler", "compose plugins", "custom middleware", or needs to understand how grammY chains and routes update handlers.
---

# grammY — Middleware

grammY's update pipeline is a stack of middleware. `bot.use()` adds a function to the stack; each function calls `await next()` to hand off to the next one — like Koa or Express, but typed.

## The signature

```typescript
type Middleware<C extends Context> =
  (ctx: C, next: NextFunction) => unknown | Promise<unknown>;

type NextFunction = () => Promise<void>;
```

A middleware can:

1. Read or mutate `ctx`.
2. `await next()` to continue to the next middleware.
3. *Not* call `next()` — to stop the chain.

## Execution order = registration order

```typescript
bot.use(async (ctx, next) => { console.log("1 before"); await next(); console.log("1 after"); });
bot.use(async (ctx, next) => { console.log("2 before"); await next(); console.log("2 after"); });
bot.on("message", (ctx) => console.log("handler"));
```

Receiving a message logs:

```
1 before
2 before
handler
2 after
1 after
```

This is the same onion model as Express — outer middleware sees both the request *and* the response.

## Mounting handlers and other Composers

A `Composer` is a fluent middleware builder. `Bot` itself is a Composer. You can build sub-routers and mount them:

```typescript
import { Bot, Composer } from "grammy";

const adminRouter = new Composer<MyContext>();
adminRouter.command("ban", (ctx) => { /* … */ });
adminRouter.command("kick", (ctx) => { /* … */ });

const bot = new Bot<MyContext>(process.env.BOT_TOKEN!);
bot.use(async (ctx, next) => {
  if (await isAdmin(ctx.from?.id)) await next();
});
bot.use(adminRouter); // only admins reach these commands
```

## Composer methods

| Method | What it does |
|---|---|
| `bot.use(mw)` | Adds middleware to the chain |
| `bot.on(query, mw)` | Adds middleware behind a filter query (see `filter-queries`) |
| `bot.command(name, mw)` | Shortcut for `:bot_command` whose text is `/name` |
| `bot.hears(pattern, mw)` | Matches plain text or regex |
| `bot.callbackQuery(data, mw)` | Matches `callback_query:data` exactly or by regex |
| `bot.inlineQuery(pattern, mw)` | Inline query handler |
| `bot.filter(pred, mw)` | Custom predicate filter |
| `bot.route(fn, branches)` | Multi-branch routing — see `@grammyjs/router` for full router |
| `bot.fork(mw)` | Runs `mw` in parallel — does NOT delay subsequent middleware |
| `bot.errorBoundary(handler, ...mw)` | Catches errors thrown by `...mw` without affecting other branches |
| `bot.lazy(factory)` | Constructs middleware lazily per update |
| `bot.drop(pred)` | Skip remaining middleware for updates matching the predicate |

## Custom middleware example

```typescript
// Tag each ctx with a unique request id and log start/end
const requestId: Middleware<Context> = async (ctx, next) => {
  const id = crypto.randomUUID();
  console.log(`[${id}] start update=${ctx.update.update_id}`);
  const start = Date.now();
  try {
    await next();
  } finally {
    console.log(`[${id}] done in ${Date.now() - start}ms`);
  }
};
bot.use(requestId);
```

## Authorization middleware (stop the chain)

```typescript
bot.use(async (ctx, next) => {
  if (BANNED_USER_IDS.has(ctx.from?.id ?? 0)) {
    return; // do not call next() — banned users go no further
  }
  await next();
});
```

## errorBoundary — local error handling

`bot.catch` (see `error-handling`) is the catch-all *last resort*. To handle errors only in a sub-branch without bubbling up, use `errorBoundary`:

```typescript
const safe = bot.errorBoundary(
  (err) => console.error("admin branch crashed:", err),
  adminRouter,
);

// Suppress errors silently in a different branch
const suppress = (_err: BotError, next: NextFunction) => next();
bot.errorBoundary(suppress).on("edited_message", noisyMiddleware);
```

## fork — run middleware in parallel

```typescript
// Log message length without blocking the main handler chain
bot.fork(async (ctx) => {
  await metrics.record("update", { type: ctx.update });
});
bot.on("message", mainHandler); // runs alongside the fork, not after it
```

## Common plugin ordering

When stacking grammY plugins, ordering matters:

```typescript
bot.use(session({ initial: () => ({ counter: 0 }) }));   // 1. session first
bot.use(conversations());                                 // 2. conversations needs session
bot.use(hydrate());                                       // 3. hydrate attaches helpers
bot.use(i18n.middleware());                               // 4. i18n
bot.use(myAuthMiddleware);                                // 5. business middleware
bot.use(createConversation(myConvo));                     // 6. individual conversations
bot.command("start", startHandler);                       // 7. handlers
bot.catch(globalErrorHandler);                            // 8. catch-all LAST
```

Forgetting "session before conversations" gives an obscure `cannot serialize conversation` error.

## What this skill does NOT cover

- The full filter-query grammar (use `filter-queries`).
- Plugin-specific middleware patterns (use `plugins-catalog` for the catalog; `sessions`/`conversations` for those two).
- Error catching strategies beyond `errorBoundary` (use `error-handling`).
