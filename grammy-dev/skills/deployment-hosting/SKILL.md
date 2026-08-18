---
name: deployment-hosting
description: This skill should be used when the user asks about "deploy grammY bot", "webhookCallback", "long polling vs webhooks", "deploy to Cloudflare Workers", "deploy to Vercel", "deploy to Deno Deploy", "Fly.io grammY", "Heroku Telegram bot", "Supabase Edge Functions", "VPS bot deployment", "Firebase functions Telegram", "Zeabur", or needs to put a grammY bot into production.
---

# grammY — Deployment & Hosting

Two update-delivery modes (long polling vs webhooks) and ten official hosting recipes. Pick polling for prototypes and tiny bots, webhooks for everything else.

## Long polling vs webhooks

| | Long polling (`bot.start()`) | Webhooks (`webhookCallback(bot, …)`) |
|---|---|---|
| Setup | None — just run | Public HTTPS URL, set webhook once |
| Latency | ~0.5–2 s | ~50–200 ms |
| Process model | One persistent process | Stateless function per request |
| Best for | Development, small bots, VPS | Serverless, edge, autoscaling |
| Hosts | VPS, Docker, anywhere with outbound HTTPS | Cloudflare Workers, Vercel, Deno Deploy, Lambda, Cloud Functions, Supabase, Fly, Heroku web dyno |

You can run only **one** of them per bot token at a time. Running both gives `409 Conflict`.

## webhookCallback adapter API

```typescript
import { webhookCallback } from "grammy";

const handler = webhookCallback(bot, "<adapter>");
```

Built-in adapters (string names):

| Adapter | Framework |
|---|---|
| `"express"` | Express |
| `"fastify"` | Fastify |
| `"hono"` | Hono |
| `"koa"` | Koa |
| `"oak"` | Oak (Deno) |
| `"http"` / `"https"` | Node's `http`/`https` |
| `"std/http"` | Deno `std/http` |
| `"cloudflare-mod"` | Cloudflare Workers (modules) |
| `"cloudflare"` | Cloudflare Workers (service worker) |
| `"aws-lambda-async"` | AWS Lambda |
| `"vercel"` | Vercel functions |
| `"sveltekit"` | SvelteKit |
| `"next-js"` | Next.js |
| `"nhttp"` | nhttp |
| `"elysia"` | Elysia |
| `"bun"` | Bun.serve |
| `"worktop"` | Worktop |
| `"azure"` | Azure Functions |

If your framework isn't in the list, the `"http"` adapter works for any Node HTTP server.

## Setting the webhook URL

After deploying, tell Telegram where to call you:

```bash
curl "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://your-domain.com/<BOT_TOKEN>&drop_pending_updates=true"
```

Or from code:

```typescript
await bot.api.setWebhook("https://your-domain.com/<BOT_TOKEN>", {
  drop_pending_updates: true,
  secret_token: process.env.WEBHOOK_SECRET,
});
```

Setting `secret_token` makes Telegram send an `X-Telegram-Bot-Api-Secret-Token` header — verify it in your webhook handler.

## Recipe: VPS with Express + webhooks

```typescript
import express from "express";
import { webhookCallback } from "grammy";
import { bot } from "./bot.js";

const app = express();
app.use(express.json());

const secretPath = String(process.env.BOT_TOKEN);
app.use(`/${secretPath}`, webhookCallback(bot, "express"));

app.listen(Number(process.env.PORT) || 3000, async () => {
  await bot.api.setWebhook(`https://${process.env.DOMAIN}/${secretPath}`);
});
```

Pair with nginx for TLS termination, or use Caddy for automatic HTTPS.

## Recipe: VPS with Fastify

```typescript
import { fastify } from "fastify";
import { webhookCallback } from "grammy";
import { bot } from "./bot.js";

const server = fastify();
server.post(`/${bot.token}`, webhookCallback(bot, "fastify"));
await server.listen({ port: 3000, host: "0.0.0.0" });
```

## Recipe: Cloudflare Workers (TypeScript modules)

```typescript
import { Bot, Context, webhookCallback } from "grammy";

export interface Env {
  BOT_TOKEN: string;
  BOT_INFO: string;     // JSON.stringify(await bot.api.getMe()) cached
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const bot = new Bot(env.BOT_TOKEN, { botInfo: JSON.parse(env.BOT_INFO) });

    bot.command("start", (ctx: Context) => ctx.reply("Hello, world!"));

    return webhookCallback(bot, "cloudflare-mod")(request);
  },
};
```

`BOT_INFO` skips a `getMe()` round-trip on every cold start. Generate it once:

```bash
curl "https://api.telegram.org/bot$BOT_TOKEN/getMe"
# paste the .result object as the BOT_INFO env var
```

Set the env vars with `wrangler secret put BOT_TOKEN` and `wrangler secret put BOT_INFO`.

## Recipe: Cloudflare Workers (Deno)

```typescript
import { Bot, webhookCallback } from "https://deno.land/x/grammy/mod.ts";
import type { UserFromGetMe } from "https://deno.land/x/grammy/types.ts";

interface Env { BOT_TOKEN: string }

let botInfo: UserFromGetMe | undefined;

export default {
  async fetch(request: Request, env: Env) {
    const bot = new Bot(env.BOT_TOKEN, { botInfo });
    if (botInfo === undefined) { await bot.init(); botInfo = bot.botInfo; }

    bot.command("start", (ctx) => ctx.reply("Up and running."));
    bot.on("message",    (ctx) => ctx.reply("Got it."));

    return webhookCallback(bot, "cloudflare-mod")(request);
  },
};
```

## Recipe: Vercel (Node.js)

`/api/bot.ts`:

```typescript
import { Bot, webhookCallback } from "grammy";

const bot = new Bot(process.env.BOT_TOKEN!);
bot.command("start", (ctx) => ctx.reply("Hello from Vercel"));

export default webhookCallback(bot, "vercel");
```

After `vercel deploy`, set the webhook:

```text
https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://<your-app>.vercel.app/api/bot
```

## Recipe: Deno Deploy

```typescript
// main.ts
import { Bot, webhookCallback } from "https://deno.land/x/grammy/mod.ts";

const bot = new Bot(Deno.env.get("BOT_TOKEN")!);
bot.command("start", (ctx) => ctx.reply("Hi from Deno Deploy"));

const handler = webhookCallback(bot, "std/http");
Deno.serve(handler);
```

## Recipe: Supabase Edge Functions

```typescript
// supabase/functions/bot/index.ts
import { Bot, webhookCallback } from "https://deno.land/x/grammy/mod.ts";

const bot = new Bot(Deno.env.get("BOT_TOKEN")!);
bot.command("start", (ctx) => ctx.reply("Hi from Supabase"));

Deno.serve(webhookCallback(bot, "std/http"));
```

Deploy with `supabase functions deploy bot --no-verify-jwt`, then point Telegram to `https://<project-ref>.functions.supabase.co/bot`.

## Recipe: Fly.io (Docker + long polling or webhooks)

A `Dockerfile` for a polling bot:

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .
CMD ["node", "src/bot.js"]
```

Then `fly launch`. Fly auto-scales horizontally — switch to webhooks once you have more than one machine.

## Recipe: Heroku (Express + webhooks)

`web` dyno in `Procfile`:

```text
web: node src/server.js
```

`src/server.js`:

```typescript
import express from "express";
import { webhookCallback } from "grammy";
import { bot } from "./bot.js";

const app = express();
app.use(express.json());
app.use(`/${process.env.BOT_TOKEN}`, webhookCallback(bot, "express"));

app.listen(process.env.PORT, async () => {
  await bot.api.setWebhook(`https://${process.env.HEROKU_APP_NAME}.herokuapp.com/${process.env.BOT_TOKEN}`);
});
```

## Recipe: Firebase Functions

```typescript
import { onRequest } from "firebase-functions/v2/https";
import { Bot, webhookCallback } from "grammy";

const bot = new Bot(process.env.BOT_TOKEN!);
bot.command("start", (ctx) => ctx.reply("Hi from Firebase"));

export const telegram = onRequest(webhookCallback(bot, "express"));
```

## Recipe: Zeabur

`Dockerfile` or `package.json` start script — Zeabur autodetects Node/Deno. Use polling for simplicity; switch to webhooks when you need multi-region.

## Choosing a platform

| Constraint | Pick |
|---|---|
| Lowest cost, single-region, instant cold starts | Cloudflare Workers |
| Always-on, paid plan, autoscaling | Fly.io |
| Already on Vercel for the rest of your stack | Vercel |
| Native Deno, Web standard APIs | Deno Deploy or Supabase |
| Self-hosted, full control | VPS + Docker + nginx |
| Mobile / startup, free tier ok | Cloudflare Workers (free 100k req/day) |

## Bundled helper

This plugin ships a script that emits the right webhook adapter for your platform:

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/generate-webhook-adapter.sh <framework> <out-file>
# framework ∈ {express, fastify, hono, cloudflare, vercel}
```

## Debug a deploy

After setting the webhook, query Telegram for status:

```bash
curl "https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo" | jq
```

Fields to watch:

- `last_error_date` / `last_error_message` — Telegram's view of *why* your endpoint failed
- `pending_update_count` — backlog (should be 0)
- `url` — what Telegram thinks your URL is

If you see `409 Conflict`, you're running `bot.start()` somewhere else. Stop it.
