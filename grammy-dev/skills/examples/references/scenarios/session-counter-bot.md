# Scenario: Session counter bot

Per-chat counter that survives across messages. Uses in-memory storage for the demo — swap for Redis / MongoDB / Postgres in production (see `sessions` skill).

## Install

```bash
npm install grammy dotenv
```

## src/bot.ts

```typescript
import "dotenv/config";
import {
  Bot,
  Context,
  GrammyError,
  HttpError,
  type SessionFlavor,
  session,
} from "grammy";

interface SessionData {
  counter: number;
  lastSeen: string | null;
}

type MyContext = Context & SessionFlavor<SessionData>;

const bot = new Bot<MyContext>(process.env.BOT_TOKEN!);

bot.use(session({
  initial: (): SessionData => ({ counter: 0, lastSeen: null }),
  // For production:
  // storage: new RedisAdapter({ instance: new IORedis(process.env.REDIS_URL!) }),
}));

bot.command("start", (ctx) =>
  ctx.reply("Send me any message — I'll count and remember.")
);

bot.command("count", (ctx) =>
  ctx.reply(`You've sent ${ctx.session.counter} messages.`)
);

bot.command("reset", async (ctx) => {
  ctx.session.counter = 0;
  await ctx.reply("Counter reset.");
});

bot.on("message", (ctx) => {
  ctx.session.counter += 1;
  ctx.session.lastSeen = new Date().toISOString();
  return ctx.reply(`Got it. That's #${ctx.session.counter}.`);
});

bot.catch((err) => {
  const e = err.error;
  if (e instanceof GrammyError)    console.error("Bot API:", e.description);
  else if (e instanceof HttpError) console.error("Network:", e);
  else                             console.error("Unknown:", e);
});

bot.start();
```

## Run

```bash
BOT_TOKEN=... npx tsx src/bot.ts
```

Send some messages → `/count` shows the running total → `/reset` zeroes it.

## Production upgrade — Redis

Swap `storage` for the Redis adapter:

```bash
npm install @grammyjs/storage-redis ioredis
```

```typescript
import { RedisAdapter } from "@grammyjs/storage-redis";
import IORedis from "ioredis";

const redis = new IORedis(process.env.REDIS_URL!);

bot.use(session({
  initial: (): SessionData => ({ counter: 0, lastSeen: null }),
  storage: new RedisAdapter({ instance: redis }),
}));
```

## Production upgrade — per user instead of per chat

In groups the default key is the chat id (everyone shares one counter). For a per-user counter:

```typescript
bot.use(session({
  initial: (): SessionData => ({ counter: 0, lastSeen: null }),
  getSessionKey: (ctx) => ctx.from?.id.toString(),
}));
```

## Production upgrade — concurrency safety

If you use `@grammyjs/runner` (see `scaling-runner`), two updates from the same chat could increment the counter to the same value. Add `sequentialize`:

```typescript
import { run, sequentialize } from "@grammyjs/runner";

bot.use(sequentialize((ctx) => ctx.chat?.id.toString()));   // BEFORE session
bot.use(session({ /* … */ }));

run(bot);   // replaces bot.start()
```
