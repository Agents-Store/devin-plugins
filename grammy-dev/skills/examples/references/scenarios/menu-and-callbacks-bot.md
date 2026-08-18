# Scenario: Menu + callbacks bot

Inline keyboard with vote buttons. The bot edits its own message in place when a user votes — no chat clutter.

## src/bot.ts

```typescript
import "dotenv/config";
import { Bot, InlineKeyboard, GrammyError, HttpError } from "grammy";

const bot = new Bot(process.env.BOT_TOKEN!);

function voteKeyboard(yes = 0, no = 0): InlineKeyboard {
  return new InlineKeyboard()
    .text(`👍 ${yes}`, "vote:yes")
    .text(`👎 ${no}`,  "vote:no")
    .row()
    .text("Show results", "vote:show");
}

const tallies = new Map<number, { yes: number; no: number }>();

bot.command("poll", async (ctx) => {
  const msg = await ctx.reply("Do you like grammY?", { reply_markup: voteKeyboard() });
  tallies.set(msg.message_id, { yes: 0, no: 0 });
});

bot.callbackQuery(/^vote:(yes|no)$/, async (ctx) => {
  const choice = ctx.match![1] as "yes" | "no";
  const messageId = ctx.callbackQuery.message?.message_id;
  if (!messageId) return ctx.answerCallbackQuery("Lost the poll");

  const t = tallies.get(messageId);
  if (!t) return ctx.answerCallbackQuery("Poll expired");

  t[choice] += 1;
  await ctx.answerCallbackQuery({ text: `Counted: ${choice}` });
  await ctx.editMessageReplyMarkup({ reply_markup: voteKeyboard(t.yes, t.no) });
});

bot.callbackQuery("vote:show", async (ctx) => {
  const messageId = ctx.callbackQuery.message?.message_id;
  const t = messageId ? tallies.get(messageId) : undefined;
  if (!t) return ctx.answerCallbackQuery("No data");
  await ctx.answerCallbackQuery({ text: `👍 ${t.yes}  •  👎 ${t.no}`, show_alert: true });
});

bot.catch((err) => {
  const e = err.error;
  if (e instanceof GrammyError)    console.error("Bot API:", e.description);
  else if (e instanceof HttpError) console.error("Network:", e);
  else                             console.error("Unknown:", e);
});

bot.start();
```

## Try it

```bash
npm install grammy dotenv
BOT_TOKEN=... npx tsx src/bot.ts
```

In Telegram:

1. `/poll` — bot posts the question with two buttons.
2. Tap 👍 a couple of times — the count next to the button updates in place.
3. Tap "Show results" — gets the count as a popup alert.

## Why this shape

- **In-memory `Map` for tallies** — fine for a demo. For production swap it with the `session` plugin keyed by `message_id` or a real DB.
- **`editMessageReplyMarkup`** is cheaper than `editMessageText` because only the markup changes.
- **`answerCallbackQuery`** must always be called within ~15 minutes, or the button shows a spinner forever.
- **`show_alert: true`** makes a callback answer pop a dialog instead of a tooltip.
