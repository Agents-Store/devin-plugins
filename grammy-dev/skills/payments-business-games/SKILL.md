---
name: payments-business-games
description: This skill should be used when the user asks about "Telegram Stars in grammY", "sendInvoice", "pre_checkout_query", "successful_payment", "XTR currency", "Telegram payments", "Business connection", "business_message", "Telegram games", "createInvoiceLink", or needs to integrate Telegram payments, Business mode, or games into a grammY bot.
---

# grammY — Payments, Business, Games

Three advanced Bot API surfaces grouped here because each spans multiple update types and has a tight handshake protocol you must follow exactly.

## Telegram Stars and payments

Telegram supports two payment systems:

| System | Currency | Use case |
|---|---|---|
| **Telegram Stars (XTR)** | `XTR` | Digital goods, in-app upgrades, tips — no external provider needed |
| **External providers** | Real currency (USD, EUR, …) | Physical goods, real money — requires a provider token from BotFather |

### Send an invoice

```typescript
await ctx.replyWithInvoice(
  "Pro upgrade",          // title
  "Unlimited everything", // description
  "pro_v1",               // payload — your internal product id, returned later
  "XTR",                  // currency code (XTR = Stars)
  [
    { label: "Pro plan", amount: 100 }, // amount in the smallest unit; for XTR it's whole Stars
  ],
);
```

For real currencies you must include `provider_token` (issued by BotFather via `/mybots → Payments`) and amounts are in the smallest currency unit (cents for USD, etc.).

### Or generate an invoice link

For non-bot share contexts (a button in a Web App, an external page):

```typescript
const link = await bot.api.createInvoiceLink(
  "Pro upgrade", "Unlimited everything", "pro_v1", "XTR",
  [{ label: "Pro plan", amount: 100 }],
);
// → "https://t.me/$..."
```

### The handshake — three handlers

When the user taps Pay:

1. Telegram sends `pre_checkout_query` — your bot must answer within **10 seconds** with approval or rejection.
2. If approved, Telegram processes the payment.
3. On success Telegram sends a `successful_payment` service message.

```typescript
// Step 1 — verify and approve
bot.on("pre_checkout_query", async (ctx) => {
  const payload = ctx.preCheckoutQuery.invoice_payload;
  const inStock = await checkStock(payload);
  if (!inStock) {
    return ctx.answerPreCheckoutQuery(false, { error_message: "Out of stock." });
  }
  await ctx.answerPreCheckoutQuery(true);
});

// Step 2 — fulfil
bot.on(":successful_payment", async (ctx) => {
  const pay = ctx.message.successful_payment;
  await grantEntitlement(ctx.from.id, pay.invoice_payload);
  await ctx.reply("Payment received — thanks!");
});
```

**Always answer `pre_checkout_query` within 10 s.** If you miss the deadline Telegram cancels the transaction.

### Star balance & refunds

```typescript
// Check the bot's Star balance
const balance = await bot.api.getMyStarBalance();

// Refund a Star payment
await bot.api.refundStarPayment(userId, telegramPaymentChargeId);
```

### Pay button

The Pay button must be the **first button in the first row** of an inline keyboard, and only inside an invoice message:

```typescript
const keyboard = new InlineKeyboard()
  .pay("⭐ 100 — Buy Pro")        // grammY swaps ⭐ XTR for the Star icon automatically
  .row()
  .text("Cancel", "cancel");
```

## Telegram Business

Telegram Business lets a paid Business user delegate their account to a bot — the bot reads and replies to that user's regular DMs.

### Subscribe to a Business account

The user adds your bot in Telegram Settings → Business → Chatbots. Telegram then sends a `business_connection` update:

```typescript
bot.on("business_connection", async (ctx) => {
  const conn = ctx.businessConnection;
  // Persist conn.id → conn.user.id mapping
  await saveBusinessConnection(conn.id, conn.user.id, conn.can_reply);
});
```

### Send and react to Business messages

Updates use the `business_message` / `edited_business_message` / `deleted_business_messages` types:

```typescript
bot.on("business_message", async (ctx) => {
  // ctx.businessMessage = the message in the Business user's chat
  if (ctx.businessMessage.text?.toLowerCase().includes("hello")) {
    await ctx.api.sendMessage(ctx.businessMessage.chat.id, "Hi! Owner is away — I'll relay your message.", {
      business_connection_id: ctx.businessMessage.business_connection_id,
    });
  }
});
```

Always include `business_connection_id` when calling `sendMessage` / `sendPhoto` / etc. on behalf of the Business account. Without it Telegram treats the call as coming from your bot, not the Business user.

### Limitations

- Only Business-tier users can connect a bot.
- The connection can be revoked at any time — handle `business_connection.is_enabled === false`.
- You cannot start a conversation; you can only reply within existing chats unless `conn.can_reply` is true and the contact is a Business contact.

## Telegram Games

Games let your bot host an HTML5 game inside Telegram and post scores.

### Set up a game in BotFather

`/newgame` in BotFather → upload a 640×360 preview image → set the short name (e.g. `space_invaders`) and game URL.

### Send a game

```typescript
await ctx.replyWithGame("space_invaders");
```

The game appears as a special message with a Play button.

### Handle the Play callback

When the user taps Play, Telegram sends a `callback_query` with `game_short_name` (no `data`):

```typescript
bot.on("callback_query:game_short_name", async (ctx) => {
  const game = ctx.callbackQuery.game_short_name;
  // Return the URL of your game (with the user id signed into a token)
  await ctx.answerCallbackQuery({
    url: `https://yourgame.com/play?u=${signUser(ctx.from.id)}`,
  });
});
```

### Submit a score

From your game's backend (when the user finishes):

```typescript
await bot.api.setGameScore(
  userId,
  score,
  { chat_id: chatId, message_id: messageId, force: false },
);
```

`force: true` allows decreasing scores.

```typescript
const high = await bot.api.getGameHighScores(userId, { chat_id, message_id });
```

## Quick decision tree

| You want to … | Use |
|---|---|
| Charge in-app Stars for a digital upgrade | `sendInvoice` with `currency: "XTR"`, handle `pre_checkout_query` + `:successful_payment` |
| Sell a physical good | `sendInvoice` with real `currency` and `provider_token` from BotFather |
| Respond to a Business user's incoming DMs | Subscribe to `business_connection`, handle `business_message`, include `business_connection_id` in replies |
| Host an HTML5 game inside Telegram | Register via BotFather, `replyWithGame`, handle `callback_query:game_short_name`, `setGameScore` |
| Refund a Stars payment | `bot.api.refundStarPayment(userId, charge_id)` |
