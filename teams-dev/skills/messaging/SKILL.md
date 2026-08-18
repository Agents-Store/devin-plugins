---
name: messaging
description: Use this skill when the user is sending or receiving messages in a Microsoft Teams bot — handling incoming messages, replying, sending typing indicators, mentioning users, replying in threads, streaming AI responses, or pushing proactive notifications. Triggers on "Teams bot message", "send a reply", "typing indicator", "stream a response", "proactive message".
---

# Messaging — sending and receiving in Teams

The bot pipeline is built around `MessageActivity`. The same primitives handle 1:1 chats, group chats, channel threads, and proactive notifications.

## Receiving messages

```ts
app.on('message', async ({ send, activity, log }) => {
  log.info({ text: activity.text, from: activity.from.id });
  await send(`You said: ${activity.text}`);
});
```

`activity` has typed access to `.text`, `.attachments`, `.from`, `.conversation`, `.channelData`, `.mentions`, and more.

## Sending text

```ts
await send('Plain text');
await send('Markdown is **supported** in 1:1 and group chats');
```

## Sending a typed activity

```ts
import { MessageActivity } from '@microsoft/teams.api';

await send(
  new MessageActivity('Saved.')
    .withTextFormat('markdown')
    .withImportance('normal'),
);
```

## Typing indicator

```ts
await send({ type: 'typing' });
// … do work …
await send('Result is ready');
```

A typing indicator is purely informational — it does not block the conversation. Pair it with longer-running work so the user sees the bot is thinking.

## Replying in a thread

```ts
app.on('message', async ({ send, activity }) => {
  // If the incoming message is in a channel, `send` already replies to the same thread.
  // To start a NEW thread from a proactive call:
  await app.send(activity.conversation.id, 'Starting a new thread');
  // To reply to a specific thread root:
  await app.reply(activity.conversation.id, activity.replyToId!, 'Threaded reply');
});
```

## Mentions

```ts
import { MessageActivity, Mention } from '@microsoft/teams.api';

const mention = new Mention(activity.from);
await send(new MessageActivity(`Hi ${mention.toMarkdown()}`).addMention(mention));
```

`Mention` records both the markdown text (`<at>Name</at>`) and the structured `mentioned` field that Teams uses to highlight + notify the user.

## Streaming a response (1:1 only)

```ts
app.on('message', async ({ stream, activity }) => {
  for await (const chunk of generateLLMResponse(activity.text)) {
    stream.emit(chunk);
  }
  // Closing the stream is automatic when the handler returns.
});
```

Important: **streaming only works in 1:1 chats**. In channels and group chats, the SDK falls back to a single message containing the final concatenated text. Detect the conversation type to gate the UX:

```ts
const isDirect = activity.conversation.conversationType === 'personal';
if (isDirect) {
  for await (const chunk of stream) ctx.stream.emit(chunk);
} else {
  const final = await collect(stream);
  await send(final);
}
```

## Proactive messages

Proactive = the bot starts the conversation, not the user. Persist the conversation reference when the user first interacts, then send to it later:

```ts
const refs = new Map<string, string>(); // userId -> conversationId

app.on('message', async ({ activity }) => {
  refs.set(activity.from.id, activity.conversation.id);
});

// Later, from a cron or webhook:
const conversationId = refs.get(userId);
if (conversationId) {
  await app.send(conversationId, 'Daily reminder: stand-up in 5 minutes.');
}
```

Push notifications obey the user's Teams notification settings — no special permission needed beyond the user having installed the app.

## Attachments

Most rich UI ships as an Adaptive Card attachment — see `adaptive-cards`. File and image attachments use `MessageActivity.addAttachment`:

```ts
await send(
  new MessageActivity('Here is the file:')
    .addAttachment({
      contentType: 'application/vnd.microsoft.teams.file.download.info',
      content: { uniqueId: fileId, fileType: 'pdf' },
      contentUrl: downloadUrl,
      name: 'report.pdf',
    }),
);
```

## Reactions

```ts
app.on('message.reaction', async ({ activity }) => {
  // activity.reactionsAdded / activity.reactionsRemoved
});
```

## Common pitfalls

- **`stream.emit` produces no output in a channel** — expected behaviour. Use a single `send` for non-1:1.
- **Mentions render as plain text** — you forgot to call `.addMention()` on the activity; the markdown alone is not enough.
- **Proactive send returns 403** — the user uninstalled the app or the conversation reference is from a tenant the bot can no longer reach.
- **Typing indicator never disappears** — send any non-typing message (text, card) to clear it; otherwise it expires on a timeout.
