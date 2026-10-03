---
name: plugins-catalog
description: This skill should be used when the user asks about "grammY plugins", "what plugins are available for grammY", "@grammyjs", "hydrate plugin", "parse-mode plugin", "i18n", "ratelimiter", "router", "emoji", "chat-members", "stateless-question", "fluent", "commands plugin", "stream plugin", "files plugin", or needs an overview of the official grammY plugin ecosystem.
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

Plugins track the core package through `peerDependencies`: `@grammyjs/menu` 1.5 needs `grammy ^1.46.0` and `@grammyjs/commands` 1.4 needs `^1.45.1`. Keep `grammy` at `^1.46.0` (Bot API 10.3) — a project pinned to an older 1.4x release gets peer-dependency conflicts when it installs the current plugin versions.

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

router.route("name",  async (ctx) => { ctx.session.name = ctx.message?.text ?? ""; ctx.session.step = "email"; });
router.route("email", async (ctx) => { /* … */ });

bot.use(router);
```

## Context augmentation

| Plugin | Adds |
|---|---|
| `@grammyjs/hydrate` | `ctx.message.delete()`, `msg.editText()`, `msg.forward()` — methods on returned message objects |
| `@grammyjs/parse-mode` | `fmt` tagged templates and `FormattedString` — build text plus `entities`, no escaping needed (≥ 2.0) |
| `@grammyjs/files` | `file.download()`, `file.getUrl()` on the result of `ctx.getFile()` (needs `hydrateFiles` + `FileFlavor`) |
| `@grammyjs/emoji` | Type-safe emoji literals: `${emoji.fire} hot` |

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

### parse-mode (≥ 2.0)

Version 2 is a formatting library, not a middleware: there is nothing to install on the bot and no context flavor. You compose a `FormattedString` with `fmt` and send its text plus entities:

```typescript
import { b, fmt, i, u } from "@grammyjs/parse-mode";

bot.command("start", async (ctx) => {
  const name = ctx.from?.first_name ?? "friend";
  const msg = fmt`${b}Hello${b}, ${i}${name}${i}!`;   // interpolated text needs no escaping
  await ctx.reply(msg.text, { entities: msg.entities });
});

// Captions use caption / caption_entities
bot.on(":photo", async (ctx) => {
  const cap = fmt`${u}Nice photo${u}`;
  await ctx.replyWithPhoto(ctx.msg.photo.at(-1)!.file_id, {
    caption: cap.caption,
    caption_entities: cap.caption_entities,
  });
});
```

`FormattedString` also has a chaining form: `FormattedString.b("bold").plain(" and plain").u(" underlined")`. The 1.x API (a transformer that set a default parse mode, a `replyWith*` context flavor, ad-hoc `bold()` escapers) was removed in 2.0 — migrate old code to `fmt`. If you only need static formatting, plain `parse_mode: "HTML"` on `ctx.reply` still works.

## Localization

| Plugin | Engine |
|---|---|
| `@grammyjs/i18n` | Built on Project Fluent (Mozilla) — `.ftl` files |
| `@grammyjs/fluent` | The older standalone Fluent package; prefer `@grammyjs/i18n` |

```typescript
import { I18n, type I18nFlavor } from "@grammyjs/i18n";

type MyContext = Context & I18nFlavor;

const i18n = new I18n<MyContext>({
  defaultLocale: "en",
  directory: "locales",      // locales/en.ftl, locales/es.ftl, …
});

bot.use(i18n);
bot.command("start", (ctx) => ctx.reply(ctx.t("welcome", { name: ctx.from?.first_name ?? "friend" })));
```

## API reliability

| Plugin | Purpose |
|---|---|
| `@grammyjs/auto-retry` | Auto-retry on 429 with `retry_after` |
| `@grammyjs/transformer-throttler` | Proactive rate limit shaping via Bottleneck |
| `@grammyjs/ratelimiter` | Per-user message rate limit (drop spammers) |
| `@grammyjs/runner` | Concurrent update fetching for high-throughput bots |
| `@grammyjs/auto-chat-action` | Auto-send `typing` action during long handlers |

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

## Chat administration

| Plugin | Purpose |
|---|---|
| `@grammyjs/chat-members` | Track all members in groups; cache `getChatMember` with hydrated `is()` helper |
| `@grammyjs/commands` | `CommandGroup` builder with localization, scopes, ephemeral commands, and one-call sync to Telegram |

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

Since 1.0 the builder class is `CommandGroup` (there is no `Commands` export). Install `commands()` and add `CommandsFlavor` if you want `ctx.setMyCommands(group)` for per-chat menus:

```typescript
import { CommandGroup, commands, type CommandsFlavor } from "@grammyjs/commands";

type MyContext = CommandsFlavor<Context>;
const bot = new Bot<MyContext>(process.env.BOT_TOKEN!);
bot.use(commands());

const myCommands = new CommandGroup<MyContext>();
myCommands.command("start", "Start the bot", (ctx) => ctx.reply("Hi!"));
myCommands.command("help",  "Show help",      (ctx) => ctx.reply("Help"));
bot.use(myCommands);                      // registers the handlers
await myCommands.setCommands(bot);        // syncs the command menu with Telegram
```

`.localize(languageCode, name, description)` adds per-language translations:

```typescript
myCommands.command("start", "Start the bot", handler)
  .localize("es", "iniciar", "Empezar el bot")
  .localize("ru", "старт",  "Запустить бота");
```

Commands can also be ephemeral (Bot API 10.2+) — shown and answered only for the user who invoked them:

```typescript
myCommands.command("whisper", "Private reply inside a group", (ctx) => ctx.reply("Only you see this."))
  .ephemeral();
```

## Streaming and other helpers

| Plugin | Purpose |
|---|---|
| `@grammyjs/stream` | Stream long text — LLM output shows up as animated message drafts (`ctx.replyWithStream`, `ctx.replyWithMarkdownStream`, `ctx.replyWithHtmlStream`) |

Albums and inline-query results need no plugin: building them is core grammY (`InputMediaBuilder`, `ctx.replyWithMediaGroup`, `InlineQueryResultBuilder`; see `files-and-media`). There is no official plugin that waits for a whole album to arrive — each photo of an album is a separate update that shares a `media_group_id`.

### stream — LLM replies as message drafts

Built on `sendMessageDraft` (Bot API 9.3, open to every bot since 9.5) and rich messages (10.1+). Private chats only. Install `auto-retry` first so rate limits slow the stream down instead of crashing it:

```typescript
import { autoRetry } from "@grammyjs/auto-retry";
import { stream, type StreamFlavor } from "@grammyjs/stream";

type MyContext = StreamFlavor<Context>;
const bot = new Bot<MyContext>(process.env.BOT_TOKEN!);

bot.api.config.use(autoRetry());
bot.use(stream());

async function* tokens(): AsyncGenerator<string> {
  yield "Streaming ";
  yield "works.";
}

bot.command("stream", (ctx) => ctx.replyWithStream(tokens()));
// markdown pieces from an LLM SDK -> one rich message: ctx.replyWithMarkdownStream(textStream)
```

## Picking plugins — rules of thumb

- **Multi-message dialog?** → `@grammyjs/conversations`
- **Bot uses Bot API rate limits?** → `@grammyjs/auto-retry` + (if heavy outbound) `@grammyjs/transformer-throttler`
- **Bot must answer 10k+ updates/s?** → `@grammyjs/runner`
- **Bot spans many languages?** → `@grammyjs/i18n` (Fluent-based)
- **Bot has complex menus?** → `@grammyjs/menu`
- **Group bot needs admin checks?** → `@grammyjs/chat-members`
- **Formatting without escaping?** → `@grammyjs/parse-mode` (`fmt`)
- **Need to download files?** → `@grammyjs/files`
- **Streaming an LLM answer?** → `@grammyjs/stream` (+ `auto-retry`)

When in doubt, check https://grammy.dev/plugins/ for the full list and READMEs.
