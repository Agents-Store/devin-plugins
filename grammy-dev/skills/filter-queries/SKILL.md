---
name: filter-queries
description: This skill should be used when the user asks about "grammY filter query", "bot.on syntax", "listen for specific update types", "message:text", "filter photos", "filter URLs", or needs to understand grammY's filter-query DSL — the framework's signature feature for routing updates with type narrowing.
---

# grammY — Filter Queries

The filter-query DSL is grammY's signature feature: a compact string syntax for `bot.on()` that picks the *exact* update types you want and narrows the TypeScript context type at the same time.

## The mental model

Telegram updates form a tree:

```
update
├── message
│   ├── text
│   ├── photo
│   ├── caption
│   ├── entities[]
│   └── forward_origin
├── edited_message (same shape)
├── channel_post   (same shape)
├── edited_channel_post (same shape)
├── callback_query
│   └── data
├── inline_query
└── …
```

A filter query is a colon-separated path into this tree. `bot.on("a:b:c")` fires when `update.a.b.c` exists.

## The basics

```typescript
// All kinds of message updates (message, edited, channel post, edited channel post)
bot.on("message", (ctx) => { /* … */ });

// Only direct messages with text
bot.on("message:text", (ctx) => { /* … */ });

// Only text — for both messages AND channel posts (leading colon is a wildcard for the L1 type)
bot.on(":text", (ctx) => { /* … */ });

// Photos
bot.on("message:photo", (ctx) => { /* … */ });

// Any file payload (photo | video | document | audio | voice | …)
bot.on(":file", async (ctx) => {
  const file = await ctx.getFile();
});

// Stickers
bot.on("message:sticker", (ctx) => { /* … */ });
```

## Entities and captions — the `::` form

`message::url` means *URL entity in either the text OR the caption*. The double colon is a shortcut for "in entities or caption_entities":

```typescript
// Messages whose text contains a URL
bot.on("message:entities:url", (ctx) => { /* … */ });

// Messages whose caption contains a URL
bot.on("message:caption_entities:url", (ctx) => { /* … */ });

// Either — most common form
bot.on("message::url", (ctx) => { /* … */ });

// Entities of any type (mention, hashtag, bot_command, url, email, …)
bot.on("message:entities", (ctx) => { /* … */ });
```

All standard entity types are valid: `mention`, `hashtag`, `cashtag`, `bot_command`, `url`, `email`, `phone_number`, `bold`, `italic`, `underline`, `strikethrough`, `spoiler`, `code`, `pre`, `text_link`, `text_mention`, `custom_emoji`.

## Combining queries

### Array — logical OR

```typescript
// Matches text messages OR edited text messages with a URL
bot.on(
  ["message:entities:url", "edited_message:entities:url"],
  (ctx) => { /* … */ },
);
```

### Chaining — logical AND

```typescript
// Messages or channel posts that contain a URL AND are forwards
bot.on("::url").on(":forward_origin", (ctx) => {
  // both conditions hold
});
```

### Combined with bot.command / bot.hears

```typescript
// Only photo messages sent by users (not channels) that contain a caption
bot
  .filter((ctx) => ctx.chat?.type === "private")
  .on("message:photo:caption", (ctx) => { /* … */ });
```

## Type narrowing

Filter queries are not just runtime predicates — they refine the TypeScript type of `ctx`:

```typescript
bot.on("message", async (ctx) => {
  const text: string | undefined = ctx.msg.text;       // could be photo/video/etc.
});

bot.on("message:text", async (ctx) => {
  const text: string = ctx.msg.text;                   // guaranteed present
});

bot.on("callback_query:data", async (ctx) => {
  const data: string = ctx.callbackQuery.data;         // guaranteed
});
```

This is why filter queries should always be preferred over `if (ctx.msg.text)` runtime guards.

## Generic `.filter()` for non-tree predicates

When a check is not expressible as a tree path (random sampling, custom permission, runtime flag), use `bot.filter()`:

```typescript
// Only process every second update
bot
  .filter((ctx) => ctx.update.update_id % 2 === 0)
  .on("message", (ctx) => { /* … */ });

// Type-predicate variant — narrows ctx too
function isFromAdmin(ctx: Context): ctx is Context & { from: { id: number } } {
  return ctx.from?.id === ADMIN_ID;
}
bot.filter(isFromAdmin, async (ctx) => {
  ctx.from.id; // narrowed to number, not number | undefined
});
```

## Cheat sheet

| Query | Fires on |
|---|---|
| `message` | Any direct message (text, photo, doc, …) |
| `message:text` | Text message |
| `message:photo` | Photo |
| `message:document` | File |
| `message:voice` | Voice note |
| `message:video_note` | Round video |
| `message:location` | Location share |
| `message:contact` | Contact share |
| `message:new_chat_members` | User joined |
| `message:left_chat_member` | User left |
| `:text` | Text in message OR channel post |
| `:file` | Any media attachment |
| `::url` | URL in text or caption |
| `::bot_command` | `/something` in text or caption |
| `edited_message` | User edited a message |
| `callback_query:data` | Inline-button press |
| `inline_query` | User typed `@bot ` in any chat |
| `chosen_inline_result` | User picked an inline result |
| `chat_member` | Bot's chat-member status changed |
| `my_chat_member` | Bot was added/removed/promoted |
| `pre_checkout_query` | Payment confirm step (10s deadline) |
| `successful_payment` | Payment completed |
| `business_connection` | Telegram Business connected/disconnected |
| `business_message` | Message in a Business-managed chat |

For payments and business specifics, open `payments-business-games`.
