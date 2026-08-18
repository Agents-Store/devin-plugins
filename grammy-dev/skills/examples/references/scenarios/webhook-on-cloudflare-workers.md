# Scenario: Webhook bot on Cloudflare Workers

Production deploy with zero servers. Cloudflare Workers gives you a free 100k requests/day on the free tier and global edge locations.

## Setup

```bash
npm create cloudflare@latest my-grammy-bot -- --type=hello-world --ts --git
cd my-grammy-bot
npm install grammy
```

## src/index.ts

```typescript
import { Bot, Context, InlineKeyboard, webhookCallback } from "grammy";

export interface Env {
  BOT_TOKEN: string;
  BOT_INFO: string;          // JSON cache of bot.getMe() — saves a round-trip
  WEBHOOK_SECRET?: string;   // optional shared secret
}

export default {
  async fetch(request: Request, env: Env, _ctx: ExecutionContext): Promise<Response> {
    // 1. Verify secret header if you set one
    if (env.WEBHOOK_SECRET) {
      const got = request.headers.get("X-Telegram-Bot-Api-Secret-Token");
      if (got !== env.WEBHOOK_SECRET) return new Response("forbidden", { status: 403 });
    }

    // 2. Construct the bot per request — cheap, no init() needed thanks to BOT_INFO
    const bot = new Bot(env.BOT_TOKEN, { botInfo: JSON.parse(env.BOT_INFO) });

    // 3. Handlers
    bot.command("start", (ctx: Context) =>
      ctx.reply("Hello from the edge ⚡", {
        reply_markup: new InlineKeyboard().url("Source", "https://grammy.dev"),
      })
    );
    bot.on("message:text", (ctx) => ctx.reply(`You said: ${ctx.message.text}`));

    bot.catch((err) => console.error("bot error", err));

    // 4. Hand off to grammY
    return webhookCallback(bot, "cloudflare-mod")(request);
  },
};
```

## wrangler.toml

```toml
name = "my-grammy-bot"
main = "src/index.ts"
compatibility_date = "2025-01-01"

# Set with: wrangler secret put BOT_TOKEN
# vars block left empty — all secrets go in `wrangler secret put`
```

## Deploy

```bash
# Set secrets
wrangler secret put BOT_TOKEN
# (paste your BotFather token)

wrangler secret put BOT_INFO
# (paste the JSON from: curl "https://api.telegram.org/bot$BOT_TOKEN/getMe" | jq .result)

# Optional: enable secret-header verification
wrangler secret put WEBHOOK_SECRET
# (paste a random 32-byte hex string)

# Ship
wrangler deploy
```

`wrangler deploy` prints something like `https://my-grammy-bot.<account>.workers.dev`.

## Register the webhook

```bash
curl "https://api.telegram.org/bot$BOT_TOKEN/setWebhook" \
  -d "url=https://my-grammy-bot.<account>.workers.dev" \
  -d "secret_token=$WEBHOOK_SECRET" \
  -d "drop_pending_updates=true"
```

Verify:

```bash
curl "https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo" | jq
```

`url` should match, `pending_update_count` should be 0, `last_error_*` empty.

Talk to the bot in Telegram — first message has a ~200 ms cold-start latency, subsequent ones ~50 ms.

## Common Cloudflare-specific gotchas

| Symptom | Cause |
|---|---|
| `Error: process is not defined` | You used `process.env`; on Workers use `env.BOT_TOKEN` instead |
| First message takes 3 s | You forgot `BOT_INFO` — every cold start does `getMe()` |
| `Error: Cannot find module 'node:crypto'` | A dependency uses Node built-ins; use `nodejs_compat` in wrangler.toml or switch the dep |
| `Worker exceeded CPU time` | Handler used >50 ms CPU (free tier); paid plan raises this to 30 s |
| Sessions don't persist | Workers have no per-worker memory across requests — use Cloudflare KV / Durable Objects / D1 with the `@grammyjs/storage-cloudflare` adapter |
