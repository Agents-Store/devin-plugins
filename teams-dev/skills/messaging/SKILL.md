---
name: messaging
description: Use this skill when the user is sending or receiving messages in a Microsoft Teams bot on Teams SDK 2.1 — handling incoming messages, `send`/`reply`/`quote`, `MessageActivityInput`, typing indicators, mentions, targeted (private) messages, quoted replies, streaming and its limits, proactive notifications, receiving files, reactions. Triggers on "Teams bot message", "send a reply", "typing indicator", "stream a response", "proactive message", "targeted message", "quoted reply".
---

# Messaging — sending and receiving in Teams

Every handler receives `send`, `reply`, `quote`, `stream` and `activity`. Outgoing messages are built with `MessageActivityInput` from `@microsoft/teams.api`; a plain string is accepted wherever a message is.

## Receiving

```ts
app.on('message', async ({ send, activity, log }) => {
  log.info(`message from ${activity.from.id}`);
  const text = activity.stripMentionsText().text ?? '';   // text without the <at>Bot</at> prefix
  await send(`You said: ${text}`);
});
```

`activity` is typed `MessageActivity`: `.text`, `.attachments`, `.from`, `.conversation`, `.channelData`, `.entities`.

## Sending

```ts
import { MessageActivityInput } from '@microsoft/teams.api';

app.on('message', async ({ send }) => {
  await send('Plain text');
  await send(new MessageActivityInput('**Saved.**').withTextFormat('markdown'));
  await send({ type: 'typing' });          // purely informational; any later message clears it
});
```

Older signatures that pass `MessageActivity` or other raw activity objects to `send` and `app.send` still work but are marked `@deprecated`. Build outgoing messages with `MessageActivityInput` (or `TypingActivityInput`).

## `send`, `reply`, `quote`, threads

| Call | Result |
|---|---|
| `send(x)` | Message in the same conversation; in a channel, in the same thread; no quote |
| `reply(x)` | Same, with a visual quote of the inbound message |
| `quote(messageId, x)` | Same, quoting another message by id |

```ts
app.on('message', async ({ send, reply, quote }) => {
  await send('Acknowledged');
  await reply('Got it!');
  await quote('1772050244572', 'Referencing an earlier message');
});
```

For proactive threading, `toThreadedConversationId(conversationId, messageId)` builds the thread conversation id, and `app.reply(conversationId, messageId, activity)` sends into the thread:

```ts
import { toThreadedConversationId } from '@microsoft/teams.apps';

async function threadUpdate(conversationId: string, messageId: string) {
  await app.reply(conversationId, messageId, 'Thread update!');
  await app.send(toThreadedConversationId(conversationId, messageId), 'Same thing, explicit id');
}
void threadUpdate;
```

## Mentions

```ts
import { MessageActivityInput } from '@microsoft/teams.api';

app.on('message', async ({ send, activity }) => {
  await send(new MessageActivityInput('hi!').addMention(activity.from));
});
```

`addMention` takes an `Account` and writes both the visible `<at>` text and the mention entity Teams needs for the notification.

## Targeted messages (visible to one user)

A targeted message is delivered to one person in a shared conversation — useful for sign-in prompts, errors and personal reminders. Replying to an inbound targeted activity through `send` or `reply` targets automatically; otherwise name the recipient:

```ts
import { MessageActivityInput } from '@microsoft/teams.api';

app.on('message', async ({ send, activity }) => {
  await send(new MessageActivityInput('Only you can see this.').withRecipient(activity.from, true));
});
```

Proactively you must pass the account yourself, and you can tie the message to the targeted one it answers:

```ts
import { Account, MessageActivityInput } from '@microsoft/teams.api';

async function privateNotice(conversationId: string, recipient: Account, targetedMessageId: string) {
  await app.send(
    conversationId,
    new MessageActivityInput('Here is the result!')
      .addTargetedMessageInfo(targetedMessageId)
      .withRecipient(recipient, true),
  );
}
void privateNotice;
```

## Quoted replies

```ts
import { MessageActivityInput } from '@microsoft/teams.api';

app.on('message', async ({ activity, reply }) => {
  const quotes = activity.getQuotedMessages();
  if (quotes.length > 0) {
    const quote = quotes[0].quotedReply;
    await reply(`You quoted ${quote.messageId} from ${quote.senderName}: "${quote.preview}"`);
  }
});

async function digest(conversationId: string) {
  await app.send(
    conversationId,
    new MessageActivityInput('see below for previous messages')
      .addQuote('1772050244573')
      .addQuote('1772050244574', 'response to both'),
  );
}
void digest;
```

`addQuote(messageId, text?)` can be chained; a quote without text groups with the next one.

## Streaming

```ts
app.on('message', async ({ stream, activity }) => {
  for await (const chunk of generateLLMResponse(activity.text)) {
    if (stream.canceled) break;      // the user pressed Stop
    stream.emit(chunk);
  }
  // the SDK closes the stream when the handler returns
});
```

What the platform allows:

- **1:1 chats only.** In channels and group chats the user sees the final text, so gate the experience on `activity.conversation.conversationType === 'personal'` and `send` the full text elsewhere.
- **One streamed message per chat at a time.** Handlers can run concurrently; serialise turns per conversation or finalise the running stream first.
- **Two minutes from the first chunk.** After that Teams rejects chunks with `403 ContentStreamNotAllowed`. The SDK keeps buffering, and `stream.close()` replaces the message with the full text. A status line (`stream.update('Thinking…')`) counts as a chunk, so do slow preparation before the first update or emit.
- **No manual throttling.** `emit` is fire-and-forget; chunks are coalesced to roughly two sends per second, each carrying the accumulated text, and failed sends are retried with backoff.
- `stream.clearText()` drops buffered text (useful when a tool call turns the answer into a card); `stream.close()` finalises early and returns the sent message.

To outlast the two minutes, stream first, then `close()` and keep editing the same message with plain updates — a message with an id goes through the update path:

```ts
import { MessageActivityInput } from '@microsoft/teams.api';

app.on('message', async ({ activity, send, stream }) => {
  let opened: number | undefined;
  let text = '';
  let messageId: string | undefined;
  let editing = false;
  let lastEdit = 0;

  for await (const chunk of runAgent(activity.text)) {
    text += chunk;
    if (!editing && (opened === undefined || Date.now() - opened < 110_000)) {
      opened ??= Date.now();
      stream.emit(chunk);
      continue;
    }
    if (!editing) {
      messageId = (await stream.close())?.id;
      editing = true;
    }
    if (messageId && Date.now() - lastEdit > 3_000) {
      await send(new MessageActivityInput(text).withId(messageId));
      lastEdit = Date.now();
    }
  }

  if (!editing) await stream.close();
  else await send(new MessageActivityInput(text).withId(messageId ?? ''));
});
```

Marking AI output (label, feedback buttons, citations, suggested prompts) is covered in `ai-agents`.

## Proactive messages

The bot starts the conversation. Keep the conversation id from any earlier activity — `install.add` is a natural place, every activity carries `conversation.id` — in turn state or your own store, then send to it later:

```ts
import { MessageActivityInput } from '@microsoft/teams.api';

app.on('install.add', async ({ activity, send }) => {
  await saveConversation(activity.from.aadObjectId!, activity.conversation.id);
  await send('Hi! I will remind you soon.');
});

async function remind(userId: string) {
  const conversationId = await loadConversation(userId);
  if (!conversationId) return;
  await app.send(conversationId, new MessageActivityInput('Stand-up in 5 minutes.'));
}

declare function saveConversation(userId: string, conversationId: string): Promise<void>;
declare function loadConversation(userId: string): Promise<string | undefined>;
void remind;
```

Turn state (`new App({ state: true })`) only exists inside a handler; a cron job or webhook needs a store of its own. To reach a user who never wrote to the bot, create the 1:1 first with `app.api.conversations.create({ members: [{ id: aadObjectId, role: 'user', name }], tenantId })`. Proactive sends follow the user's notification settings and fail with `403` after an uninstall.

## Cards and attachments

```ts
import { MessageActivityInput, cardAttachment } from '@microsoft/teams.api';
import { AdaptiveCard, TextBlock } from '@microsoft/teams.cards';

app.on('message', async ({ send }) => {
  const card = new AdaptiveCard(new TextBlock('Hello from Teams', { weight: 'Bolder' }));
  await send(card);                                                         // a card alone
  await send(new MessageActivityInput('Heads up:').addCard('adaptive', card));   // text plus card
  await send(new MessageActivityInput().addAttachments(cardAttachment('adaptive', card)));  // variadic, any attachment
});
```

Card building is in `adaptive-cards`.

## Receiving files

`files` lists the uploads on the inbound activity. `contentUrl` (formerly `webUrl`) is a browsable link, not a download URL — use `download()`.

```ts
app.on('message', async ({ files, send }) => {
  const file = await files.first();
  if (!file) {
    await send('Send me a file and I will read it.');
    return;
  }
  const downloaded = await file.download();
  await send(`Got ${downloaded.filename}: ${downloaded.bytes.length} bytes, ${downloaded.contentType}`);
});
```

When `download()` fails it throws a `FileError` subclass — `FileAccessError`, `FileCredentialError`, `FileScopeNotSupportedError` or `FileUrlExpiredError` — all exported from `@microsoft/teams.apps`.

## Reactions

```ts
app.on('messageReaction', async ({ activity }) => {
  for (const reaction of activity.reactionsAdded ?? []) console.log(`added ${reaction.type}`);
  for (const reaction of activity.reactionsRemoved ?? []) console.log(`removed ${reaction.type}`);
});

app.on('message', async ({ activity, api }) => {
  await api.conversations.addReaction(activity.conversation.id, activity.id, 'like');
});
```

Reaction names: `like`, `heart`, `1f440_eyes`, `2705_whiteheavycheckmark`, `launch`, `1f4cc_pushpin`.

## Common pitfalls

- **Mentions render as plain text** — use `addMention`; the markup alone does not notify.
- **Streaming shows nothing in a channel** — expected; send the final text.
- **A stream dies after two minutes** — hand off to message updates as above.
- **`addAttachment` is not a function** — it is `addAttachments(...)` (variadic) or `addCard(type, card)`.
- **Proactive `send` returns 403** — the user uninstalled the app, or the stored conversation id is stale.
- **Typing indicator stays** — it clears on the next message or a timeout.
