---
name: conversations
description: This skill should be used when the user asks about "grammY conversations plugin", "@grammyjs/conversations", "multi-step wizard", "ask user for input", "conversation.wait", "conversation.form", "checkpoint and rewind", "conversation menu", "wait timeout", "persist conversations", or needs to model multi-message dialog flows in a grammY bot.
---

# grammY — Conversations

The `@grammyjs/conversations` plugin turns multi-message dialog flows from a state machine into linear, awaitable async code. You write your conversation as a function with `await conversation.wait()` calls — the plugin stores the state and replays your function on every new update. This skill targets **2.x** (2.1 at the time of writing).

## Install

```bash
npm install @grammyjs/conversations
```

The plugin does **not** need the session plugin. `bot.use(conversations())` keeps conversation state itself — in an in-memory `Map` by default, or in the storage you pass (see "Persisting conversations"). Sessions are only needed if your own code also reads session data.

## Set up

```typescript
import { Bot, Context } from "grammy";
import {
  conversations,
  createConversation,
  type Conversation,
  type ConversationFlavor,
} from "@grammyjs/conversations";

// Outside (middleware) context: carries ConversationFlavor.
type MyContext = ConversationFlavor<Context>;
// Inside a conversation: a separate context type, WITHOUT ConversationFlavor.
type MyConversationContext = Context;
type MyConversation = Conversation<MyContext, MyConversationContext>;

const bot = new Bot<MyContext>(process.env.BOT_TOKEN!);

// 1. Conversations plugin (no session needed)
bot.use(conversations());
// 2. Register each conversation; the id defaults to the function name
bot.use(createConversation(greet, "greet"));

// 3. Enter the conversation from a handler that comes AFTER the registration
bot.command("greet", (ctx) => ctx.conversation.enter("greet"));

bot.start();
```

`Conversation` takes two context types: the outside one (it needs `ConversationFlavor`) and the one used inside the conversation (it must never have `ConversationFlavor`). The two types must differ.

## Write a conversation

```typescript
async function greet(conversation: MyConversation, ctx: MyConversationContext) {
  await ctx.reply("What's your name?");
  const { msg: { text: name } } = await conversation.waitFor("message:text");

  await ctx.reply(`Nice to meet you, ${name}. How old are you?`);
  const age = await conversation.form.number();

  await ctx.reply(`OK, ${name}, you're ${age} years old.`);
}
```

The function looks synchronous but spans multiple messages — `await conversation.wait*()` suspends the conversation until the next matching update arrives. Arguments passed to `ctx.conversation.enter("name", a, b)` arrive as extra parameters after `ctx` (they must be JSON-serializable).

## Persisting conversations

Without a storage, all conversations are gone when the process restarts. Pass any storage adapter (the storage adapter packages listed in the `sessions` skill work) and a **version** that you bump whenever the conversation code changes shape:

```typescript
bot.use(conversations({
  storage: {
    type: "key",
    version: 1,                // number or string; defaults to 0
    prefix: "convo-",          // optional namespace, handy when sharing a database with sessions
    adapter: storageAdapter,   // read/write/delete by string key — default key is ctx.chatId
  },
}));
```

The plugin detects a version mismatch and handles the stored data itself instead of replaying it against changed code, so a code change cannot corrupt a running dialog. Upgrading from 1.x discards all stored conversation data — everybody restarts.

## `conversation.wait` family

| Call | Returns when |
|---|---|
| `conversation.wait()` | Any update arrives |
| `conversation.waitFor("message:text")` | Filter-query match (see `filter-queries`) |
| `conversation.waitForHears(/yes\|no/i)` | Text matching a string or regex |
| `conversation.waitForCommand("cancel")` | Specific slash command |
| `conversation.waitForCallbackQuery(/^vote:/)` | Callback query matching string or regex |
| `conversation.waitForReaction("👍")` | Message reaction |
| `conversation.waitForReplyTo(messageId)` | Reply to a given message |
| `conversation.waitFrom(userId)` | Next update from a specific user |
| `conversation.waitUntil(pred)` | Custom predicate |
| `conversation.waitUnless(pred)` | Predicate-negated |

The return value is always a fresh `Context` for the new update — destructure what you need. Every wait call takes `otherwise` (runs for non-matching updates) and `maxMilliseconds`.

### Timeouts

```typescript
// Give up after an hour: the conversation is halted, the update goes on to later handlers
const ctx2 = await conversation.wait({ maxMilliseconds: 60 * 60 * 1000 });

// Default for every wait inside one conversation
bot.use(createConversation(greet, { id: "greet", maxMillisecondsToWait: 60 * 60 * 1000 }));
```

The check runs when the next update arrives — no code runs at the exact moment of expiry.

### Enter and exit hooks

```typescript
bot.use(conversations({
  onEnter: (id, ctx) => console.log("entered", id),
  onExit:  (id, ctx) => console.log("left", id),   // also fires on halt() and on timeout
}));
```

## `conversation.form` — typed input helpers

The `form` object collects validated input and re-prompts on mismatch:

```typescript
const text    = await conversation.form.text();                        // any text message
const number  = await conversation.form.number();                      // re-asks if not a number
const int     = await conversation.form.int();
const colour  = await conversation.form.select(["red", "green", "blue"]);
const photo   = await conversation.form.photo();                       // PhotoSize[]
const contact = await conversation.form.contact();                     // shared contact (phone number)
const file    = await conversation.form.file();
```

There are no dedicated URL, e-mail or phone-number fields in 2.x. The real fields are `text`, `number`, `int`, `select`, `entity`, `animation`, `audio`, `document`, `paidMedia`, `photo`, `sticker`, `story`, `video`, `video_note`, `voice`, `contact`, `dice`, `game`, `poll`, `venue`, `location`, `media`, `file` and `build`. URLs and e-mail addresses are message entities:

```typescript
const link  = await conversation.form.entity("url");     // MessageEntity & { text: string }
const email = await conversation.form.entity("email");
await ctx.reply(`Got ${link.text} and ${email.text}`);
```

For a phone number typed as text, use `form.text()` and validate it, or build a custom field:

```typescript
const phone = await conversation.form.build({
  validate: (c) => {
    const t = c.message?.text ?? "";
    return /^\+?[0-9][0-9 -]{6,14}$/.test(t) ? { ok: true, value: t } : { ok: false };
  },
  otherwise: (c) => c.reply("Send a number like +1 555 0100."),
});
```

Each field accepts `otherwise` (reject message), `action` (runs when the field is filled) and `maxMilliseconds`:

```typescript
const age = await conversation.form.int({
  otherwise: (ctx) => ctx.reply("Please send a whole number."),
});
```

## Conditional branching

```typescript
async function order(conversation: MyConversation, ctx: MyConversationContext) {
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
async function addItems(conversation: MyConversation, ctx: MyConversationContext) {
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
async function game(conversation: MyConversation, ctx: MyConversationContext) {
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

Build inline menus that live inside a conversation. Their button handlers may `await conversation.wait*()`:

```typescript
async function settings(conversation: MyConversation, ctx: MyConversationContext) {
  let email = "";
  const emailMenu = conversation.menu()
    .text("Show email", (c) => c.reply(email || "empty"))
    .text(() => (email ? "Change email" : "Set email"), async (c) => {
      await c.reply("What is your email?");
      const response = await conversation.waitFor(":text");
      email = response.msg.text;
      c.menu.update();
    })
    .row()
    .url("About", "https://grammy.dev");

  await ctx.reply("Here is your menu", { reply_markup: emailMenu });

  // Menus only work while the conversation is alive — keep it waiting.
  await conversation.waitUntil(() => false, {
    otherwise: (c) => c.reply("Please use the menu above!"),
  });
}
```

For submenus, pass the target menu (or its id) to `submenu` and use `back` inside the child:

```typescript
const child = conversation.menu("child", { parent: "root" })
  .back("Go back");
const root = conversation.menu("root")
  .submenu("Open submenu", child)
  .text("Close", (c) => c.menu.close());
await ctx.reply("Root menu", { reply_markup: root });
```

Call `ctx.menu.close()` for every menu before the conversation ends — menus stop working as soon as it exits. A menu from the `@grammyjs/menu` plugin can take over inside a conversation if both use the same id and have the same shape and labels.

## Calling external APIs — wrap with `conversation.external`

Anything non-deterministic (HTTP request, database, random number, current time) must run inside `conversation.external` so the plugin can replay your function deterministically. The convenience helpers cover the common cases:

```typescript
const weather = await conversation.external(() =>
  fetch("https://api.example.com/now").then((r) => r.json())
);

const now = await conversation.now();        // = external(() => Date.now())
const rnd = await conversation.random();     // = external(() => Math.random())
await conversation.log("reached step 3");    // console.log that is silent during replays
const id = await conversation.external(() => crypto.randomUUID());
```

Do **not** wrap `ctx.reply(...)` or other `ctx.api.*` calls — those are replay-safe by design; wrap calls on `bot.api` or any other independent `Api` instance. Whatever `external` returns is stored, so it must survive `JSON.stringify` — pass `{ task, beforeStore, afterLoad }` for values such as `bigint`.

If you skip `conversation.external`, you'll see "deterministic execution" errors when the conversation resumes.

## Accessing sessions inside a conversation

Session plugin data is not available on the context inside a conversation (`ctx.session` is undefined there, and the 1.x session accessor on the conversation handle was removed). Reach the outside context through `external`:

```typescript
const session = await conversation.external((ctx) => ctx.session);    // read
await conversation.external((ctx) => { ctx.session.count += 1; });    // write
```

This needs the session middleware to be installed before `conversations()` on the outside — only if you use sessions at all.

## Using other plugins inside a conversation

A conversation has *fresh* context objects: none of the plugins installed on the bot are active inside it. Pass them explicitly, and add their flavor to the **inside** context type:

```typescript
import { hydrate, type HydrateFlavor } from "@grammyjs/hydrate";

type HydratedContext = HydrateFlavor<Context>;
type HydratedConversation = Conversation<MyContext, HydratedContext>;

async function myConvo(conversation: HydratedConversation, ctx: HydratedContext) {
  const status = await ctx.reply("Working…");
  await status.editText("Done");          // hydrate helper
}

bot.use(createConversation(myConvo, { plugins: [hydrate()] }));
```

For plugins every conversation needs, set defaults once: `conversations<MyContext, HydratedContext>({ plugins: [hydrate()] })`. API transformers (`bot.api.config.use(…)`) are installed from inside a small middleware in `plugins`: `async (ctx, next) => { ctx.api.config.use(autoRetry()); await next(); }`.

## Parallel conversations

By default a chat has at most one active conversation; `enter` throws if one is running. Opt in with `{ parallel: true }` to run several at once (updates a conversation does not accept are then passed on to the next handler). Pair it with `andFrom` so each instance listens to one user:

```typescript
bot.use(createConversation(captcha, { parallel: true }));

async function captcha(conversation: MyConversation, ctx: MyConversationContext) {
  const user = ctx.from!.id;
  await ctx.reply("What is the best bot framework?");
  const answer = await conversation.waitFor(":text").andFrom(user);
  if (answer.msg.text !== "grammY") await ctx.reply("Try again later.");
}
```

`ctx.conversation.active()` tells you which conversations are running and how many instances of each.

## Exit a conversation early

- `return` from the function — clean exit. Throwing an error also ends it.
- `await conversation.halt()` — exits from anywhere, never returns; calls `onExit`.
- `await ctx.conversation.exit("name")` — cancels one conversation from a handler outside; `exitAll()` cancels every one in the chat.

## Common pitfalls

1. **Giving the conversation the flavored context type** — inside the function use a plain `Context` (or a plugin flavor), never `ConversationFlavor`.
2. **Non-deterministic code outside `conversation.external`** — breaks replay (`Date.now()`, `Math.random()`, `fetch`, database access, session access).
3. **Entering a conversation before it is registered** — `bot.use(createConversation(…))` must come before the handler that calls `enter`.
4. **Forgetting to bump `version`** when you change a persisted conversation's code.
5. **Catching errors and continuing** — if a handler throws inside a wait, the conversation aborts. Use `try/catch` only for known-recoverable cases.
6. **Long-lived blocking calls inside a wait** — keep them short. For long jobs, store a job id and exit the conversation; resume in a separate handler.
