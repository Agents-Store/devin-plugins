---
name: api-reference
description: Use this skill on explicit request when the user asks for the Teams SDK 2.1 API reference — the `@microsoft/teams.*` packages and what each exports, `App` options, the handler context, activity routes, the `app.api` clients. Reference-only — does not auto-load.
disable-model-invocation: true
---

# Microsoft Teams SDK 2.1 — API reference (TypeScript)

Curated reference for the `@microsoft/teams.*` packages at **2.1.0** (all need Node 22.12 or newer; the CLI is a separate 3.x line). The official LLM-optimised documentation is the authority when something here looks stale:

- `https://microsoft.github.io/teams-sdk/llms_docs/llms_typescript.txt` — index
- `https://microsoft.github.io/teams-sdk/llms_docs/llms_typescript_full.txt` — everything in one file

This plugin does not cache a copy; the files change faster than the plugin does.

## Packages

| Package | Purpose |
|---|---|
| `@microsoft/teams.apps` | `App`, routing, plugins, HTTP adapters, OAuth flows, turn state |
| `@microsoft/teams.api` | Activity types and builders, `MessageActivityInput`, API clients, cloud presets, attachments |
| `@microsoft/teams.cards` | Adaptive Card builders, `SubmitData`, `OpenDialogData` |
| `@microsoft/teams.graph` | Graph client (`call(endpoint, params)`) |
| `@microsoft/teams.graph-endpoints`, `-beta` | Typed Graph request builders, v1.0 and beta |
| `@microsoft/teams.client` | Browser `App` for tabs: MSAL, Graph, `exec` of server functions |
| `@microsoft/teams.common` | Logger, storage interface, HTTP client |
| `@microsoft/teams.m365extensions` | Embed the Teams SDK in a Microsoft 365 Agents SDK `AgentApplication` |
| `@microsoft/teams.botbuilder` | Bot Framework interoperability, for migrations |
| `@microsoft/teams.cli` | The `teams` command (`cli-recipes`) |

There are no SDK packages for prompts, models, MCP or A2A: use `openai`, `@modelcontextprotocol/sdk` and `@a2a-js/sdk` directly (`ai-agents`, `mcp-a2a`). For local testing there is no plugin either: use the Agents Playground (`agents-playground`).

See `references/packages-overview.md` for exports and the install matrix.

## Bootstrapping

```ts
import { App } from '@microsoft/teams.apps';

const app = new App();                       // CLIENT_ID, CLIENT_SECRET, TENANT_ID from the environment

app.on('message', async ({ send, activity }) => {
  await send(`you said "${activity.text}"`);
});

app.start(process.env.PORT || 3978).catch(console.error);
```

The options table and the lifecycle are in `references/app-class.md`.

## Activity routing

`app.on(route, handler)`; the route string selects the activity type and the handler's return type. The authoritative name list is the `IRoutes` type of `@microsoft/teams.apps`; `references/activity-types.md` has the table. `app.message(pattern, handler)` matches message text, `app.event(name, handler)` observes app events (`start`, `signin`, `error`, `activity`, `activity.response`, `activity.sent`), `app.use(handler)` is middleware.

## Handler context

| Key | Purpose |
|---|---|
| `activity` | The typed inbound activity |
| `send(x)`, `reply(x)`, `quote(id, x)` | Reply in the conversation; `reply` and `quote` add a visual quote |
| `stream` | `emit(text \| activity)`, `update(text)`, `clearText()`, `close()`, `canceled`, `closed` |
| `state` | Conversation and user scopes when `new App({ state })` is on |
| `files` | Uploaded files on the inbound activity: `list()`, `first()`, `download()` |
| `api` | Teams REST clients: `conversations`, `users` (incl. `users.token`), `teams`, `meetings`, `reactions`, `bots` |
| `appGraph` | Graph client for the app's identity (same as `app.graph`) |
| `log` | Scoped logger |
| `next()` | Pass control to the next handler |
| `getConnectionStatus()` | Token status of every registered OAuth connection |
| `ref`, `appId` | Conversation reference and the bot's id |

Deprecated and kept for compatibility: `userGraph`, `isSignedIn`, `userToken`, `signin()`, `signout()`, `storage`. Their replacements are an OAuth flow (`authentication`) and turn state.

## Sending

```ts
import { MessageActivityInput } from '@microsoft/teams.api';

app.on('message', async ({ send, reply, quote, activity }) => {
  await send('text');
  await send(new MessageActivityInput('hello').addMention(activity.from));
  await send({ type: 'typing' });
  await reply('quoted reply');
  await quote('1772050244572', 'quote an earlier message');
});

async function proactive(conversationId: string) {
  await app.send(conversationId, new MessageActivityInput('hello'));
  await app.reply(conversationId, '1772050244572', new MessageActivityInput('thread reply'));
}
void proactive;
```

`MessageActivityInput` builders: `addCard`, `addAttachments`, `withAttachmentLayout('list' | 'carousel')`, `addMention`, `withTextFormat`, `withRecipient(account, isTargeted)`, `addQuote`, `addTargetedMessageInfo`, `withId`, `addAiGenerated`, `addFeedback`, `addCitation`, `withSuggestedActions`, `addStreamFinal`. See `messaging`.

## Adaptive Cards

```ts
import { AdaptiveCard, TextBlock, TextInput, ActionSet, ExecuteAction, SubmitData } from '@microsoft/teams.cards';

const card = new AdaptiveCard(
  new TextBlock('Hi', { weight: 'Bolder' }),
  new TextInput().withId('email').withPlaceholder('you@example.com'),
  new ActionSet(new ExecuteAction({ title: 'Save' }).withData(new SubmitData('save')).withAssociatedInputs('auto')),
);
void card;
```

The builder catalogue is in `adaptive-cards` → `references/card-builders.md`.

## Reference files

- `references/packages-overview.md` — exports of each package and the install matrix
- `references/app-class.md` — `AppOptions`, methods, events
- `references/activity-types.md` — route names with their payloads
