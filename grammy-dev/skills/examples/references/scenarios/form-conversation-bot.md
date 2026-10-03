# Scenario: Form conversation bot

Asks the user for name, age, and email across multiple messages using `@grammyjs/conversations` 2.x (no session plugin needed).

## Install

```bash
npm install grammy @grammyjs/conversations dotenv
```

## src/bot.ts

```typescript
import "dotenv/config";
import { Bot, Context, GrammyError, HttpError } from "grammy";
import {
  conversations,
  createConversation,
  type Conversation,
  type ConversationFlavor,
} from "@grammyjs/conversations";

// Outside (middleware) context carries the flavor; the context INSIDE a conversation must not.
type MyContext = ConversationFlavor<Context>;
type MyConversationContext = Context;
type MyConversation = Conversation<MyContext, MyConversationContext>;

const bot = new Bot<MyContext>(process.env.BOT_TOKEN!);

// Conversations 2.x keeps its own state (in memory by default) — no session needed.
// To survive restarts: conversations({ storage: { type: "key", version: 1, adapter } })
bot.use(conversations());

// Registered BEFORE the conversation, otherwise "/cancel" would be swallowed as an answer
bot.command("cancel", async (ctx) => {
  await ctx.conversation.exitAll();
  await ctx.reply("Cancelled.");
});

async function signup(conversation: MyConversation, ctx: MyConversationContext) {
  await ctx.reply("Welcome! What's your name?");
  const { msg: { text: name } } = await conversation.waitFor("message:text");

  await ctx.reply(`Nice to meet you, ${name}. How old are you?`);
  const age = await conversation.form.int({
    otherwise: (c) => c.reply("Please send a whole number."),
  });

  await ctx.reply("Last one — what's your email?");
  // There is no email field; Telegram marks addresses as "email" entities, so ask for one of those
  const email = await conversation.form.entity("email", {
    otherwise: (c) => c.reply("That doesn't look like an email. Try again."),
  });

  // Anything non-deterministic must run in `external`
  const id = await conversation.external(() => crypto.randomUUID());

  // Persist somewhere (mock here)
  await conversation.external(() =>
    saveUser({ id, name, age, email: email.text, telegramId: ctx.from!.id })
  );

  await ctx.reply(`Done! Your id is <code>${id}</code>.`, { parse_mode: "HTML" });
}

bot.use(createConversation(signup, "signup"));

bot.command("signup", (ctx) => ctx.conversation.enter("signup"));

bot.command("start", (ctx) =>
  ctx.reply("Send /signup to begin, /cancel to abort.")
);

bot.catch((err) => {
  const e = err.error;
  if (e instanceof GrammyError)    console.error("Bot API:", e.description);
  else if (e instanceof HttpError) console.error("Network:", e);
  else                             console.error("Unknown:", e);
});

bot.start();

// ----- mock storage -----
async function saveUser(u: { id: string; name: string; age: number; email: string; telegramId: number }) {
  console.log("[saveUser]", u);
}
```

## Try it

```bash
BOT_TOKEN=... npx tsx src/bot.ts
```

Then in Telegram:

```
/signup
> What's your name?
Alice
> Nice to meet you, Alice. How old are you?
not-a-number
> Please send a whole number.
33
> Last one — what's your email?
alice@example.com
> Done! Your id is `c5d1c…`
```

## Notes

- **No session plugin** — conversations 2.x stores its state itself. Install `session` only if you also want `ctx.session`; inside a conversation read it with `conversation.external((ctx) => ctx.session)`.
- **Two context types** — `ConversationFlavor<Context>` outside, a plain `Context` inside the conversation function.
- **`conversation.form.*` re-prompts on validation failure** — no manual loop needed. The real fields are `text`, `number`, `int`, `select`, `entity`, `photo`, `contact`, … (see the `conversations` skill).
- **`conversation.external` for `crypto.randomUUID()`, `Date.now()`, DB writes** — keeps the conversation deterministic so it can be replayed.
- **`/cancel` works because it is registered before the conversation** and calls `ctx.conversation.exitAll()` (or `exit("signup")` for one conversation).
- **HTML for the final message** — MarkdownV2 would need every `!` and `.` escaped.
