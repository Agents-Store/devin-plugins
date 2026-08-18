---
name: conversations
description: This skill should be used when the user asks about "grammY conversations plugin", "@grammyjs/conversations", "multi-step wizard", "ask user for input", "conversation.wait", "conversation.form", "checkpoint and rewind", "conversation menu", or needs to model multi-message dialog flows in a grammY bot.
---

# grammY — Conversations

The `@grammyjs/conversations` plugin turns multi-message dialog flows from a state machine into linear, awaitable async code. You write your conversation as a function with `await conversation.wait()` calls — the plugin handles persistence and resumption across messages.

## Install

```bash
npm install @grammyjs/conversations
```

The plugin **requires** the session plugin underneath — it stores conversation state in the session.

## Set up

```typescript
import { Bot, Context, session } from "grammy";
import {
  conversations,
  createConversation,
  type Conversation,
  type ConversationFlavor,
} from "@grammyjs/conversations";

type MyContext = ConversationFlavor<Context>;
type MyConversation = Conversation<MyContext>;

const bot = new Bot<MyContext>(process.env.BOT_TOKEN!);

// 1. Session (required)
bot.use(session({ initial: () => ({}) }));
// 2. Conversations plugin
bot.use(conversations());
// 3. Register each conversation by name
bot.use(createConversation(greet, "greet"));

// 4. Enter the conversation from a command
bot.command("greet", (ctx) => ctx.conversation.enter("greet"));

bot.start();
```

## Write a conversation

```typescript
async function greet(conversation: MyConversation, ctx: MyContext) {
  await ctx.reply("What's your name?");
  const { msg: { text: name } } = await conversation.waitFor("message:text");

  await ctx.reply(`Nice to meet you, ${name}. How old are you?`);
  const age = await conversation.form.number();

  await ctx.reply(`OK, ${name}, you're ${age} years old.`);
}
```

The function looks synchronous but spans multiple messages — `await conversation.wait*()` suspends the conversation until the next matching update arrives.

## `conversation.wait` family

| Call | Returns when |
|---|---|
| `conversation.wait()` | Any update arrives |
| `conversation.waitFor("message:text")` | Filter-query match (see `filter-queries`) |
| `conversation.waitForCommand("cancel")` | Specific slash command |
| `conversation.waitForCallbackQuery(/^vote:/)` | Callback query matching string or regex |
| `conversation.waitFrom(userId)` | Next update from a specific user |
| `conversation.waitUntil(pred)` | Custom predicate |
| `conversation.waitUnless(pred)` | Predicate-negated |

The return value is always a fresh `Context` for the new update — destructure what you need.

## `conversation.form` — typed input helpers

The `form` object collects validated input and re-prompts on mismatch:

```typescript
const text     = await conversation.form.text();         // any text message
const number   = await conversation.form.number();       // re-asks if not a number
const int      = await conversation.form.int();
const url      = await conversation.form.url();
const email    = await conversation.form.email();
const select   = await conversation.form.select(["red", "green", "blue"]);
const phone    = await conversation.form.phone();
const photo    = await conversation.form.photo();
const file     = await conversation.form.file();
```

Each accepts an `otherwise` callback to customize the rejection message:

```typescript
const age = await conversation.form.int({
  otherwise: (ctx) => ctx.reply("Please send a whole number."),
});
```

## Conditional branching

```typescript
async function order(conversation: MyConversation, ctx: MyContext) {
  await ctx.reply("Buy now? yes / no");
  const { msg: { text } } = await conversation.waitFor("message:text");
  if (text.toLowerCase() === "no") {
    await ctx.reply("Maybe next time.");
    return;   // ends the conversation
  }
  await ctx.reply("Great — what's your address?");
  const address = await conversation.form.text();
  // …
}
```

## Loops

```typescript
async function addItems(conversation: MyConversation, ctx: MyContext) {
  const items: string[] = [];
  while (true) {
    await ctx.reply("Item? (send /done to finish)");
    const ev = await conversation.waitFor("message:text");
    if (ev.msg.text === "/done") break;
    items.push(ev.msg.text);
  }
  await ctx.reply(`Saved ${items.length} items.`);
}
```

## Checkpoints and rewind — undo support

Snapshot the conversation state at any point and jump back later:

```typescript
async function game(conversation: MyConversation, ctx: MyContext) {
  await ctx.reply("Pick a door: 1, 2, or 3");
  const checkpoint = conversation.checkpoint();

  const { msg: { text } } = await conversation.waitFor("message:text");
  await ctx.reply(`You picked door ${text}. Want to retry? yes/no`);

  const { msg: { text: again } } = await conversation.waitFor("message:text");
  if (again === "yes") {
    await conversation.rewind(checkpoint);   // jumps back, never returns
  }
}
```

`rewind` never returns — execution resumes from the line *after* `conversation.checkpoint()`.

## Conversational menus

Build inline menus that live inside a conversation:

```typescript
async function settings(conversation: MyConversation, ctx: MyContext) {
  const menu = conversation.menu()
    .text("Toggle notifications", async (ctx) => {
      await ctx.editMessageText("Notifications toggled");
    })
    .text("Close", (ctx) => ctx.menu.close());

  await ctx.reply("Settings", { reply_markup: menu });
}
```

For multi-level submenus, name them and reference the parent:

```typescript
const root = conversation.menu("root")
  .submenu("Open submenu", (ctx) => ctx.editMessageText("submenu"))
  .text("Close", (ctx) => ctx.menu.close());

conversation.menu("child", { parent: "root" })
  .back("Go back", (ctx) => ctx.editMessageText("Root menu"));

await ctx.reply("Root menu", { reply_markup: root });
```

## Calling external APIs — wrap with `conversation.external`

Anything non-deterministic (HTTP request, random number, current time) must run inside `conversation.external` so the plugin can replay your function deterministically:

```typescript
const weather = await conversation.external(() =>
  fetch("https://api.weather.com/now").then((r) => r.json())
);

const id = await conversation.external(() => crypto.randomUUID());
const now = await conversation.external(() => Date.now());
```

If you skip `conversation.external`, you'll see "deterministic execution" errors when the conversation resumes.

## Using other plugins inside a conversation

By default a conversation has a *fresh* context with only the base `Context` type — none of the plugins installed on the bot are active inside it. Pass them explicitly:

```typescript
import { hydrate } from "@grammyjs/hydrate";

bot.use(createConversation(myConvo, { plugins: [hydrate()] }));
```

Then inside `myConvo`, the context has `ctx.message.delete()` (hydrate) helpers.

## Exit a conversation early

- `return` from the function — clean exit.
- `await conversation.halt()` — exits even if called from deeply nested logic; subsequent `wait()` calls would never resolve.

The plugin also exposes `ctx.conversation.exit(name?)` outside the conversation to cancel it from a different handler.

## Common pitfalls

1. **Forgetting the session plugin** — conversations needs it. Mount session first.
2. **Mutating `conversation` between waits without `external`** — non-deterministic, breaks replay.
3. **Catching errors and continuing** — if a handler throws inside a wait, the conversation aborts. Use `try/catch` only for known-recoverable cases.
4. **Long-lived blocking calls inside a wait** — keep them under a few seconds. For long jobs, store a job id in session and exit the conversation; resume in a separate handler.
