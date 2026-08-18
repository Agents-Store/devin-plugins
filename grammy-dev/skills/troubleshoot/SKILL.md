---
name: troubleshoot
description: This skill should be used when the user reports that "grammY bot is broken", "401 Unauthorized", "409 Conflict", "bot not responding", "double replies", "TypeScript error in grammY", "ctx.session is undefined", "conversations not working", "bot only responds once then stops", or any other grammY runtime / type / deployment failure.
---

# grammY — Troubleshooting

Symptoms first, root causes next. Grouped by the layer where the bug actually lives — your token, Telegram, your code, your TypeScript, your deploy.

## 401 Unauthorized

**Cause**: bot token is wrong, missing, or revoked.

**Fix**:

```bash
echo $BOT_TOKEN          # confirm the env var is set
curl "https://api.telegram.org/bot$BOT_TOKEN/getMe"
# Should return {"ok":true,"result":{"id":...,"username":"..."}}
```

If `getMe` fails too, regenerate the token via `/token` in BotFather.

## 409 Conflict: terminated by other getUpdates request

**Cause**: two processes are simultaneously fetching updates for the same bot.

**Common scenarios**:

- Local `npm run dev` + deployed bot both polling.
- Deployed with both `bot.start()` AND `webhookCallback()` registered.
- A previous deploy is still running on the host.

**Fix**: stop the duplicate process. To verify nothing else is polling:

```bash
curl "https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo"
```

If `url` is non-empty you have a webhook set — `bot.start()` will fight it. Either delete the webhook (`deleteWebhook`) or remove `bot.start()`.

## 429 Too Many Requests: retry after N

**Cause**: hit Telegram's rate limits.

**Fix**: install both rate-limit plugins (see `scaling-runner`):

```typescript
bot.api.config.use(apiThrottler());
bot.api.config.use(autoRetry({ maxAttempts: 3, maxDelaySeconds: 10 }));
```

## Bot replies twice to every message

**Cause**: long polling + webhook *both* active in the same process.

**Fix**: pick one. If using webhooks, remove `bot.start()`. If using polling, call `bot.api.deleteWebhook({ drop_pending_updates: true })` on startup.

## Bot doesn't respond at all

Checklist in order:

1. `curl …/getMe` → token works.
2. `curl …/getWebhookInfo` → either webhook URL is correct **or** url is empty (then you must be polling).
3. Process log shows `[grammY] You can stop me by pressing Ctrl+C` (polling) or your HTTP server log shows incoming requests (webhook).
4. `bot.start()` or `webhookCallback()` is actually called (check for missing `await` or unreachable code).
5. Filter query matches what you're sending (`bot.on("message:text", …)` doesn't match a photo).
6. No middleware before the handler is `return`ing without `next()`.

## TypeScript: Property 'session' does not exist on type 'Context'

**Cause**: you installed `session()` but didn't add `SessionFlavor` to your context type.

**Fix**:

```typescript
type MyContext = Context & SessionFlavor<MyData>;
const bot = new Bot<MyContext>(token);
```

Same applies to every plugin that augments context: `ConversationFlavor`, `HydrateFlavor`, `ParseModeFlavor`, `ChatMembersFlavor`, etc. Combine them:

```typescript
type MyContext = HydrateFlavor<ConversationFlavor<Context & SessionFlavor<MyData>>>;
```

## conversation.wait never resolves

Checklist:

1. Did you mount the session plugin *before* `conversations()`? Without session, conversation state isn't persisted.
2. Did you call `bot.use(createConversation(myConvo, "name"))` AND `ctx.conversation.enter("name")`?
3. Inside the conversation, do you call `await conversation.wait*()` — never plain `await new Promise(...)`?
4. Inside the conversation, do you wrap non-deterministic calls (fetch, randomUUID, Date.now) in `conversation.external(() => …)`?

## "Cannot serialize conversation"

You stored something non-serializable in `conversation.session` (a function, class instance, Map, Set). Conversations must only hold JSON-compatible values. Wrap non-serializable computation in `conversation.external`.

## ctx.reply works but ctx.api.sendMessage(otherChatId, …) fails with "chat not found"

**Cause**: your bot has never met that chat, OR you used a username instead of an id.

**Fix**:

- For private chats: the user must `/start` your bot at least once.
- For groups/channels: your bot must be a member (and admin for channels).
- Use chat *id* (number), not @username, except for public channels.

## Webhook errors

`getWebhookInfo` returns last_error_date / last_error_message. Common ones:

| `last_error_message` | Cause |
|---|---|
| `Wrong response from the webhook: 401 Unauthorized` | You're checking `secret_token` and the header doesn't match |
| `Wrong response from the webhook: 500 Internal Server Error` | Your handler threw — install `bot.catch` |
| `Connection timed out` | Handler took >30 s; offload long work |
| `SSL error: certificate verify failed` | Your TLS chain is incomplete; check Let's Encrypt fullchain |

## Message is too long

Telegram caps text at 4096 chars. Split before sending:

```typescript
function chunk(text: string, size = 4000): string[] {
  const out: string[] = [];
  for (let i = 0; i < text.length; i += size) out.push(text.slice(i, i + size));
  return out;
}
for (const part of chunk(longText)) await ctx.reply(part);
```

## Markdown / HTML formatting errors

`Bad Request: can't parse entities` means your text breaks the chosen parse_mode.

- For `MarkdownV2`: every literal `_ * [ ] ( ) ~ ` `` ` `` `> # + - = | { } . !` must be escaped with `\\` (in TS source).
- Easier: install `@grammyjs/parse-mode` and use the `bold(text)`, `italic(text)` builders which escape for you.

## "Cannot find module 'grammy'" or similar import failure

```bash
npm ls grammy           # is it installed?
node -e "console.log(require.resolve('grammy'))"
```

If using ESM with `"type": "module"`, import as `import { Bot } from "grammy"` (no `.js`). If using TypeScript with `"moduleResolution": "node16"`, you may need `.js` suffixes on relative imports — see your tsconfig.

## Long polling stops after one update

**Cause**: handler threw synchronously and you didn't install `bot.catch`. The polling loop crashes.

**Fix**: install `bot.catch` (see `error-handling`).

## Deno: "Uncaught (in promise) Forbidden: bot was blocked by the user"

Same as everywhere — the user blocked your bot, but the error reached top-level. Install `bot.catch` and ignore or log this case.

## When all else fails

1. Enable debug logs: `DEBUG=grammy* node ./src/bot.js`.
2. Inspect raw updates: `bot.use((ctx) => { console.log(JSON.stringify(ctx.update, null, 2)); })`.
3. Check `getWebhookInfo` (webhook) or `getMe` (polling).
4. Search https://github.com/grammyjs/grammY/issues for the exact error.
5. Open https://t.me/grammyjs — the official chat.
