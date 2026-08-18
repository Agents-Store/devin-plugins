---
name: sdk-patterns
description: This skill should be used when the user asks about "grammY Bot class", "grammY Context object", "ctx.reply", "ctx.api", "send a message in grammY", "use grammY in code", or needs idiomatic grammY code patterns for everyday bot operations.
---

# grammY — SDK Patterns

Idiomatic code patterns for the everyday surface of grammY: creating a `Bot`, handling updates via the `Context` object, calling the Bot API, and typing context flavors.

## Create a Bot

```typescript
import { Bot } from "grammy";

const bot = new Bot(process.env.BOT_TOKEN!);
```

The single positional argument is your BotFather token. A second optional argument lets you pass `botInfo`, `client` options (timeouts, base URL), or a custom `ContextConstructor`.

## The Context object (ctx)

Every middleware receives one argument — `ctx` — which represents *the current update being processed*. It bundles:

| Property | What it is |
|---|---|
| `ctx.update` | The full Telegram `Update` object |
| `ctx.message`, `ctx.editedMessage`, `ctx.channelPost` … | Aliases for the matching update type |
| `ctx.from` | The sender's `User` |
| `ctx.chat` | The current `Chat` |
| `ctx.callbackQuery` | Present for inline-button presses |
| `ctx.api` | Direct Bot API client — `ctx.api.sendMessage(chatId, text)` |
| `ctx.me` | Info about the bot itself (filled by `bot.init()`) |

### Reply aliases — always prefer these

Instead of `ctx.api.sendMessage(ctx.chat.id, "hi")`, write `ctx.reply("hi")`. grammY provides one alias per Bot API send method, automatically using the current chat id:

```typescript
await ctx.reply("text");
await ctx.replyWithPhoto("https://example.com/img.png", { caption: "Look" });
await ctx.replyWithDocument(new InputFile("./report.pdf"));
await ctx.replyWithAudio("file_id_from_earlier");
await ctx.replyWithVideo(new InputFile("./demo.mp4"));
await ctx.replyWithSticker("CAACAgIA...");
await ctx.replyWithChatAction("typing");
await ctx.editMessageText("updated text");
await ctx.deleteMessage();
await ctx.answerCallbackQuery({ text: "noted" });
await ctx.answerInlineQuery([...]);
```

### Use ctx.api for *other* chats

`ctx.reply` only targets the chat the update came from. To send a message to a different chat (broadcast, admin notification, scheduled post):

```typescript
await ctx.api.sendMessage(adminChatId, "alert: user reported abuse");
```

## Register handlers

```typescript
bot.command("start", (ctx) => ctx.reply("Welcome"));
bot.command(["help", "h"], (ctx) => ctx.reply("Help text"));   // multiple aliases

bot.hears("ping", (ctx) => ctx.reply("pong"));                  // plain text match
bot.hears(/^echo (.+)$/i, (ctx) => ctx.reply(ctx.match[1]));    // regex with capture

bot.on("message:text", (ctx) => { /* … */ });                   // filter query
bot.on("callback_query:data", (ctx) => { /* … */ });

bot.on(":file", async (ctx) => {
  const file = await ctx.getFile();                             // returns File obj with file_path
  console.log(file.file_path);
});
```

For the full filter-query DSL, open `filter-queries`.

## TypeScript context flavors

The base `Context` type is augmented by plugins. Whenever you use a plugin that adds methods or properties to `ctx`, *combine* its flavor with `Context` and pass it as a generic to `Bot<C>`:

```typescript
import { Bot, Context, SessionFlavor, session } from "grammy";
import { ConversationFlavor, conversations } from "@grammyjs/conversations";
import { HydrateFlavor, hydrate } from "@grammyjs/hydrate";

interface SessionData { counter: number }

type MyContext = HydrateFlavor<
  ConversationFlavor<Context & SessionFlavor<SessionData>>
>;

const bot = new Bot<MyContext>(process.env.BOT_TOKEN!);

bot.use(session({ initial: () => ({ counter: 0 }) }));
bot.use(conversations());
bot.use(hydrate());
```

Order of flavors matches order of `bot.use()` installation. Forgetting a flavor is the #1 source of `Property 'session' does not exist on type 'Context'` errors.

## API options object

Send methods accept an optional `other` object with all the Bot API parameters that aren't chat_id / text / file:

```typescript
await ctx.reply("Bold *italic* `code`", {
  parse_mode: "MarkdownV2",
  disable_notification: true,
  reply_parameters: { message_id: ctx.msg.message_id },
  link_preview_options: { is_disabled: true },
});
```

## Initialization (optional, advanced)

By default `bot.start()` calls `bot.init()` internally. Call it manually only when:

- You need `ctx.me` available before the first update (e.g. serverless cold starts — see `deployment-hosting`).
- You're constructing several `Bot` instances and want to skip duplicate `getMe` calls by passing `{ botInfo }` from a cache.

```typescript
await bot.init();          // populates bot.botInfo
console.log(bot.botInfo);  // { id, username, ... }
```

## Graceful shutdown

```typescript
process.once("SIGINT", () => bot.stop());
process.once("SIGTERM", () => bot.stop());
```

`bot.stop()` waits for in-flight updates to finish before exiting.

## Bot.api — call any Bot API method

`bot.api` (and `ctx.api`) is a typed proxy for every Bot API method, plus options:

```typescript
await bot.api.setMyCommands([
  { command: "start", description: "Begin" },
  { command: "help",  description: "Show help" },
]);

await bot.api.setMyDescription("This bot helps you …");
await bot.api.getMe();
await bot.api.deleteWebhook({ drop_pending_updates: true });
```

The full method list is curated in the `api-reference` skill (manual-trigger).
