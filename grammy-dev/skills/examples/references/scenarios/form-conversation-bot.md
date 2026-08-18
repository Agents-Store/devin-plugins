# Scenario: Form conversation bot

Asks the user for name, age, and email across multiple messages using `@grammyjs/conversations`.

## Install

```bash
npm install grammy @grammyjs/conversations dotenv
```

## src/bot.ts

```typescript
import "dotenv/config";
import { Bot, Context, GrammyError, HttpError, session } from "grammy";
import {
  conversations,
  createConversation,
  type Conversation,
  type ConversationFlavor,
} from "@grammyjs/conversations";

type MyContext = ConversationFlavor<Context>;
type MyConversation = Conversation<MyContext>;

const bot = new Bot<MyContext>(process.env.BOT_TOKEN!);

// Sessions are required by the conversations plugin
bot.use(session({ initial: () => ({}) }));
bot.use(conversations());

async function signup(conversation: MyConversation, ctx: MyContext) {
  await ctx.reply("Welcome! What's your name?");
  const { msg: { text: name } } = await conversation.waitFor("message:text");

  await ctx.reply(`Nice to meet you, ${name}. How old are you?`);
  const age = await conversation.form.int({
    otherwise: (c) => c.reply("Please send a whole number."),
  });

  await ctx.reply("Last one — what's your email?");
  const email = await conversation.form.email({
    otherwise: (c) => c.reply("That doesn't look like an email. Try again."),
  });

  // Anything non-deterministic must run in `external`
  const id = await conversation.external(() => crypto.randomUUID());

  // Persist somewhere (mock here)
  await conversation.external(() =>
    saveUser({ id, name, age, email, telegramId: ctx.from!.id })
  );

  await ctx.reply(`Done! Your id is \`${id}\`.`, { parse_mode: "MarkdownV2" });
}

bot.use(createConversation(signup, "signup"));

bot.command("signup", (ctx) => ctx.conversation.enter("signup"));
bot.command("cancel", async (ctx) => {
  await ctx.conversation.exit();
  await ctx.reply("Cancelled.");
});

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

- **Session plugin before conversations plugin** — required.
- **`conversation.form.*` re-prompts on validation failure** — no manual loop needed.
- **`conversation.external` for `crypto.randomUUID()`, `Date.now()`, DB writes** — keeps the conversation deterministic so it can be replayed.
- **`/cancel` works thanks to `ctx.conversation.exit()`** — call from any handler to abort the active conversation.
