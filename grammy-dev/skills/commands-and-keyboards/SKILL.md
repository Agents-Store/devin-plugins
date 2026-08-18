---
name: commands-and-keyboards
description: This skill should be used when the user asks about "slash commands in grammY", "bot.command", "setMyCommands", "inline keyboard", "reply keyboard", "callback query", "buttons in Telegram bot", or needs to add interactive commands and keyboards to a grammY bot.
---

# grammY — Commands & Keyboards

Slash commands (`/start`, `/help`) and keyboards (inline buttons, reply buttons) are the two main ways users interact with a Telegram bot beyond plain text. grammY has first-class APIs for both.

## Slash commands

### Register handlers

```typescript
bot.command("start", (ctx) => ctx.reply("Welcome!"));
bot.command("help",  (ctx) => ctx.reply("Available: /start /help /settings"));

// Multiple aliases
bot.command(["faq", "support"], (ctx) => ctx.reply("FAQ: …"));

// Read the argument string (everything after `/cmd `)
bot.command("echo", (ctx) => {
  const arg = ctx.match;          // string after the command, "" if absent
  return ctx.reply(arg || "send: /echo <text>");
});
```

`bot.command("foo")` matches:

- `/foo` at the start of a message.
- `/foo@your_bot` (used in group chats to disambiguate).
- `/foo arg1 arg2` (args available as `ctx.match`).

### Tell Telegram which commands you have (`setMyCommands`)

Tell Telegram about your commands so they show up in the chat-input autocomplete menu:

```typescript
await bot.api.setMyCommands([
  { command: "start",    description: "Begin" },
  { command: "help",     description: "Show help" },
  { command: "settings", description: "Adjust your preferences" },
]);
```

Run this once at startup or whenever the command list changes — Telegram caches it.

### Scopes and localization

`setMyCommands` accepts a scope so different chats see different menus:

```typescript
await bot.api.setMyCommands(
  [{ command: "admin", description: "Admin panel" }],
  { scope: { type: "chat", chat_id: ADMIN_CHAT_ID } },
);

// Per-language
await bot.api.setMyCommands(
  [{ command: "start", description: "Empezar" }],
  { language_code: "es" },
);
```

Available scope types: `default`, `all_private_chats`, `all_group_chats`, `all_chat_administrators`, `chat`, `chat_administrators`, `chat_member`.

For larger setups with localization, use the `@grammyjs/commands` plugin (see `plugins-catalog`) — it provides a `Commands` builder, `.localize()`, and one-call sync.

## Inline keyboards (buttons under a message)

Inline keyboards live under a single message. When the user taps a button, Telegram sends a `callback_query` update to your bot.

### Build and send

```typescript
import { InlineKeyboard } from "grammy";

const keyboard = new InlineKeyboard()
  .text("Yes", "vote:yes").text("No", "vote:no").row()
  .text("Maybe", "vote:maybe").row()
  .url("Source", "https://example.com");

await ctx.reply("Vote:", { reply_markup: keyboard });
```

Builder methods:

| Method | Button type |
|---|---|
| `.text(label, callback_data?)` | Callback button (default callback_data = label) |
| `.url(label, url)` | Open URL |
| `.webApp(label, url)` | Launch a Telegram Web App |
| `.login(label, url)` | LoginUrl button (OAuth-style) |
| `.switchInline(label, query?)` | Switch to inline mode in another chat |
| `.switchInlineCurrent(label, query?)` | … in the current chat |
| `.game(label)` | Game button |
| `.pay(label)` | Payment button (only inside an invoice message) |
| `.row()` | Start a new row |
| `.add(...buttons)` | Append raw button objects |

### Handle callback_query

```typescript
// Match exact callback_data
bot.callbackQuery("vote:yes", async (ctx) => {
  await ctx.answerCallbackQuery({ text: "Counted!" });   // dismisses the loading spinner
  await ctx.editMessageText("Thanks — you voted YES");
});

// Match by regex
bot.callbackQuery(/^vote:(yes|no|maybe)$/, async (ctx) => {
  const choice = ctx.match![1];
  await ctx.answerCallbackQuery({ text: `Got ${choice}` });
});

// Generic — read ctx.callbackQuery.data yourself
bot.on("callback_query:data", async (ctx) => {
  console.log("callback", ctx.callbackQuery.data);
  await ctx.answerCallbackQuery();
});
```

**Always call `answerCallbackQuery()`** within ~15 minutes, or Telegram shows a loading spinner on the user's button forever.

### Edit a message in place

```typescript
await ctx.editMessageText("Updated text");
await ctx.editMessageReplyMarkup({ reply_markup: newKeyboard });
await ctx.editMessageCaption({ caption: "new caption" });
```

If you only change the markup (not the text), `editMessageReplyMarkup` is cheaper.

## Reply keyboards (custom keyboard under the input field)

Reply keyboards replace the user's keyboard with predefined buttons. Tapping a button sends its label as a regular message.

```typescript
import { Keyboard } from "grammy";

const keyboard = new Keyboard()
  .text("Settings").text("Help").row()
  .text("Contact").row()
  .resized()        // shrink to button size
  .oneTime()        // hide after one press
  .placeholder("Choose…");

await ctx.reply("Pick one:", { reply_markup: keyboard });
```

Special button types:

```typescript
new Keyboard()
  .requestContact("Share contact")
  .requestLocation("Share location")
  .requestPoll("Create poll", "regular")
  .requestUsers("Choose user", 1, { user_is_bot: false })
  .requestChat("Choose chat", 2, { chat_is_channel: true })
  .webApp("Open Web App", "https://my.webapp/");
```

### Remove the keyboard

```typescript
import { ReplyKeyboardRemove } from "grammy/types";

await ctx.reply("Bye keyboard", {
  reply_markup: { remove_keyboard: true } satisfies ReplyKeyboardRemove,
});
```

## Inline keyboards vs reply keyboards — when to use which

| Use case | Choose |
|---|---|
| Yes/No/Cancel under a specific message | Inline |
| Persistent menu while in conversation | Reply |
| Linking to a URL or Web App | Inline |
| Need to know which message the button belonged to | Inline (`ctx.callbackQuery.message`) |
| Want to collect free-form text *after* the choice | Reply (the label becomes the next message text) |

## Dynamic, stateful menus — use the menu plugin

For menus with multiple pages, dynamic labels, or shared state, hand-rolling `editMessageReplyMarkup` becomes painful. Install `@grammyjs/menu`:

```bash
npm install @grammyjs/menu
```

```typescript
import { Menu } from "@grammyjs/menu";

const main = new Menu<MyContext>("main")
  .text("Settings", (ctx) => ctx.editMessageText("Settings"))
  .text("Help",     (ctx) => ctx.editMessageText("Help text"))
  .row()
  .submenu("Admin", "admin");

const admin = new Menu<MyContext>("admin")
  .text("Stats", (ctx) => ctx.editMessageText("Stats: …"))
  .back("Back");

main.register(admin);
bot.use(main);

bot.command("menu", (ctx) => ctx.reply("Main menu", { reply_markup: main }));
```

Full menu patterns live in `plugins-catalog`.
