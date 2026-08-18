---
name: plugins-catalog
description: This skill should be used when the user asks about "grammY plugins", "what plugins are available for grammY", "@grammyjs", "hydrate plugin", "parse-mode plugin", "i18n", "ratelimiter", "router", "emoji", "chat-members", "stateless-question", "media-group", "fluent", "entity-parser", "autoquote", "console-time", "files plugin", or needs an overview of the official grammY plugin ecosystem.
---

# grammY — Official Plugins Catalog

The grammY ecosystem ships ~25 first-party plugins under the `@grammyjs/*` npm scope. Each is small, focused, and composable. Install only what you need.

## Install pattern

Every plugin follows the same shape:

```bash
npm install @grammyjs/<plugin-name>
```

```typescript
import { somePlugin } from "@grammyjs/<plugin-name>";
bot.use(somePlugin(options));
```

A few plugins are transformers (modify outgoing API calls) instead of middleware — install them differently:

```typescript
import { someTransformer } from "@grammyjs/<plugin-name>";
bot.api.config.use(someTransformer(options));
```

## State & flow plugins

| Plugin | Use case | Notes |
|---|---|---|
| `@grammyjs/conversations` | Multi-message dialogs with `await wait()` | See dedicated `conversations` skill |
| Built-in `session` | Per-chat persistent data | See dedicated `sessions` skill |
| `@grammyjs/menu` | Stateful inline menus with submenus | Replaces hand-rolled `editMessageReplyMarkup` |
| `@grammyjs/router` | Route updates by string key from session | Useful for multi-step wizards without conversations |
| `@grammyjs/stateless-question` | One-off question/answer without sessions | Stateless via callback data |

### Menu plugin

```typescript
import { Menu } from "@grammyjs/menu";

const menu = new Menu<MyContext>("main")
  .text("A", (ctx) => ctx.reply("clicked A"))
  .text("B", (ctx) => ctx.reply("clicked B")).row()
  .submenu("Open child", "child");

const child = new Menu<MyContext>("child")
  .text("X", (ctx) => ctx.reply("X"))
  .back("Back");

menu.register(child);
bot.use(menu);
bot.command("menu", (ctx) => ctx.reply("Menu:", { reply_markup: menu }));
```

### Router plugin

```typescript
import { Router } from "@grammyjs/router";

const router = new Router<MyContext>((ctx) => ctx.session.step);

router.route("name",  async (ctx) => { ctx.session.name = ctx.msg.text; ctx.session.step = "email"; });
router.route("email", async (ctx) => { /* … */ });

bot.use(router);
```

## Context augmentation

| Plugin | Adds |
|---|---|
| `@grammyjs/hydrate` | `ctx.message.delete()`, `msg.editText()`, `msg.forward()` — methods on returned message objects |
| `@grammyjs/parse-mode` | `ctx.replyWithHTML()`, `ctx.replyWithMarkdownV2()` + safe builders (`bold`, `italic`, `code`, …) |
| `@grammyjs/files` | `file.download()`, `file.getUrl()` |
| `@grammyjs/emoji` | Type-safe emoji literals: `${emoji.fire} hot` |
| `@grammyjs/entity-parser` | Convert message entities to HTML/Markdown/Plain text |

### Hydrate

```typescript
import { hydrate, HydrateFlavor } from "@grammyjs/hydrate";

type MyContext = HydrateFlavor<Context>;
bot.use(hydrate());

bot.on(":photo", async (ctx) => {
  const status = await ctx.reply("Processing…");
  await processImage(ctx.msg.photo);
  await status.editText("Done!");
  setTimeout(() => status.delete().catch(() => {}), 3000);
});
```

### parse-mode

```typescript
import { hydrateReply, parseMode } from "@grammyjs/parse-mode";
import type { ParseModeFlavor } from "@grammyjs/parse-mode";

type MyContext = ParseModeFlavor<Context>;
bot.api.config.use(parseMode("MarkdownV2"));   // default for ctx.reply
bot.use(hydrateReply);

bot.command("start", (ctx) => ctx.replyWithMarkdownV2("*Hello* _world_"));
```

## Localization

| Plugin | Engine |
|---|---|
| `@grammyjs/i18n` | Built on `gettext` |
| `@grammyjs/fluent` | Project Fluent (Mozilla) |

```typescript
import { I18n } from "@grammyjs/i18n";

const i18n = new I18n<MyContext>({
  defaultLocale: "en",
  directory: "locales",      // locales/en.ftl, locales/es.ftl, …
});

bot.use(i18n);
bot.command("start", (ctx) => ctx.reply(ctx.t("welcome", { name: ctx.from?.first_name })));
```

## API reliability

| Plugin | Purpose |
|---|---|
| `@grammyjs/auto-retry` | Auto-retry on 429 with `retry_after` |
| `@grammyjs/transformer-throttler` | Proactive rate limit shaping via Bottleneck |
| `@grammyjs/ratelimiter` | Per-user message rate limit (drop spammers) |
| `@grammyjs/runner` | Concurrent update fetching for high-throughput bots |
| `@grammyjs/auto-chat-action` | Auto-send `typing` action during long handlers |
| `@grammyjs/autoquote` | Always reply by quoting the original message |

See the dedicated `scaling-runner` skill for runner / throttler / auto-retry details.

### ratelimiter

```typescript
import { limit } from "@grammyjs/ratelimiter";

bot.use(limit({
  timeFrame: 2000,     // 2 seconds
  limit: 3,            // max 3 messages
  onLimitExceeded: async (ctx) => {
    await ctx.reply("Slow down!");
  },
}));
```

### autoquote

```typescript
import { autoQuote } from "@grammyjs/auto-quote";
bot.use(autoQuote());     // every reply now quotes the message it answers
```

## Chat administration

| Plugin | Purpose |
|---|---|
| `@grammyjs/chat-members` | Track all members in groups; cache `getChatMember` with hydrated `is()` helper |
| `@grammyjs/commands` | Command builder with localization, scopes, and one-call sync to Telegram |

### chat-members hydration

```typescript
import { hydrateChatMember, type HydrateChatMemberFlavor, type HydrateChatMemberApiFlavor } from "@grammyjs/chat-members";

type MyContext = HydrateChatMemberFlavor<Context>;
type MyApi = HydrateChatMemberApiFlavor<Api>;

const bot = new Bot<MyContext, MyApi>(process.env.BOT_TOKEN!);
bot.api.config.use(hydrateChatMember());

bot.command("ban", async (ctx) => {
  const author = await ctx.getAuthor();
  if (!author.is("admin")) return ctx.reply("Admin only");
  await ctx.banAuthor();
});
```

### commands plugin

```typescript
import { Commands } from "@grammyjs/commands";

const myCommands = new Commands<MyContext>();
myCommands.command("start", "Start the bot", (ctx) => ctx.reply("Hi!"));
myCommands.command("help",  "Show help",      (ctx) => ctx.reply("Help"));
bot.use(myCommands);
await myCommands.setCommands(bot);
```

`.localize(languageCode, name, description)` adds per-language translations:

```typescript
myCommands.command("start", "Start the bot", handler)
  .localize("es", "iniciar", "Empezar el bot")
  .localize("ru", "старт",  "Запустить бота");
```

## Reception filters & helpers

| Plugin | Purpose |
|---|---|
| `@grammyjs/media-group` | Wait for the entire album to arrive before processing |
| `@grammyjs/inline-query` | Helpers for inline query results (`InlineQueryResultBuilder` improvements) |
| `@grammyjs/console-time` | Console.time logger for handler durations |
| `@grammyjs/stream` | Stream large API responses |
| `@grammyjs/middlewares` | Collection of small reusable middlewares (admin filter, chat filter, etc.) |

### media-group

```typescript
import { mediaGroup } from "@grammyjs/media-group";

bot.use(mediaGroup());

bot.on(":media", async (ctx) => {
  // ctx.mediaGroup is the full album (array of Message), or undefined for single media
  console.log("album size:", ctx.mediaGroup?.length ?? 1);
});
```

## Picking plugins — rules of thumb

- **Multi-message dialog?** → `@grammyjs/conversations`
- **Bot uses Bot API rate limits?** → `@grammyjs/auto-retry` + (if heavy outbound) `@grammyjs/transformer-throttler`
- **Bot must answer 10k+ updates/s?** → `@grammyjs/runner`
- **Bot spans many languages?** → `@grammyjs/i18n` or `@grammyjs/fluent`
- **Bot has complex menus?** → `@grammyjs/menu`
- **Group bot needs admin checks?** → `@grammyjs/chat-members`
- **Markdown formatting?** → `@grammyjs/parse-mode`
- **Need to download files?** → `@grammyjs/files`

When in doubt, check https://grammy.dev/plugins/ for the full list and READMEs.
