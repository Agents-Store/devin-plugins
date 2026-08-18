---
name: api-reference
description: Use this skill on explicit request when the user asks for "Teams SDK API reference", "@microsoft/teams.* packages", "Teams App class options", "TS activity types", or needs precise signatures for `App`, `ChatPrompt`, `AdaptiveCard`, or other SDK types. Reference-only — does not auto-load.
disable-model-invocation: true
---

# Microsoft Teams SDK — API Reference (TypeScript)

Curated reference for the `@microsoft/teams.*` npm packages. Full documentation lives at `https://microsoft.github.io/teams-sdk/typescript/`. A trimmed copy of the SDK's LLM doc is at `references/llms-typescript-full.md` for offline grep.

## Packages

| Package | Purpose |
|---|---|
| `@microsoft/teams.apps` | Core `App` framework, plugin system, activity routing |
| `@microsoft/teams.api` | Activity types, API contracts, REST clients |
| `@microsoft/teams.cards` | Adaptive Card builders (`AdaptiveCard`, `TextBlock`, `TextInput`, `ActionSet`, …) |
| `@microsoft/teams.ai` | `ChatPrompt`, function calling, streaming |
| `@microsoft/teams.openai` | `OpenAIChatModel` for OpenAI + Azure OpenAI |
| `@microsoft/teams.mcp` | MCP server plugin and MCP client plugin (`McpPlugin`, `A2AClientPlugin`) |
| `@microsoft/teams.client` | Client-side SDK for static tabs |
| `@microsoft/teams.dev` | `DevtoolsPlugin` — local activity inspector |
| `@microsoft/teams.cli` | `teams` CLI binary (global install) |

See `references/packages-overview.md` for what each one exports.

## Bootstrapping

```ts
import { App, PUBLIC, US_GOV, US_GOV_DOD, CHINA } from '@microsoft/teams.apps';

const app = new App({
  plugins: [],            // DevtoolsPlugin, McpPlugin, ExpressAdapter, etc.
  cloud: PUBLIC,          // default; override for sovereign clouds
  clientId: '...',        // optional — derived from env if omitted
  clientSecret: '...',    // optional — derived from env if omitted
});

await app.start(3978);
```

See `references/app-class.md` for the full `AppOptions` shape.

## Activity routing

```ts
app.on('message', async (ctx) => { /* MessageActivity */ });
app.on('install.add', async (ctx) => { /* InstallActivity */ });
app.on('config.open', async (ctx) => { /* ConfigOpenActivity */ });
app.on('dialog.open.<id>', async (ctx) => { /* DialogOpenActivity */ });
app.on('dialog.submit.<id>', async (ctx) => { /* DialogSubmitActivity */ });
app.on('card.action.<id>', async (ctx) => { /* CardActionActivity */ });
app.on('message.ext.query', async (ctx) => { /* MessageExtQueryActivity */ });
app.on('message.ext.submit', async (ctx) => { /* MessageExtSubmitActivity */ });
app.on('message.ext.select-item', async (ctx) => { /* MessageExtSelectItemActivity */ });
app.on('message.ext.query-link', async (ctx) => { /* MessageExtQueryLinkActivity */ });
app.on('signin.token-exchange', async (ctx) => { /* token exchange for SSO */ });
app.on('signin.verify-state', async (ctx) => { /* verify state after sign-in */ });
```

Route-name string drives the activity-type inference. See `references/activity-types.md`.

## Handler context

Every handler receives an object with:

| Key | Type | Purpose |
|---|---|---|
| `send` | `(text \| Activity) => Promise<SendResponse>` | Reactive reply to the originating conversation |
| `activity` | typed activity (per route) | Incoming request payload |
| `log` | logger | Structured logging — visible in DevTools |
| `stream` | streaming emitter | `stream.emit(chunk)` — 1:1 chats only |
| `api` | api proxy | `api.graph.*`, `api.users.*`, etc. |
| `next` | `() => Promise<void>` | Pass to the next middleware in the chain |

## Sending messages

```ts
await send('Hello');                                   // text
await send(new MessageActivity('Hello'));              // explicit activity
await send({ type: 'typing' });                        // typing indicator
await app.send(conversationId, 'Hello');               // proactive send
await app.reply(conversationId, threadId, 'Hello');    // thread reply
```

## Adaptive Cards

```ts
import { AdaptiveCard, TextBlock, TextInput, ActionSet, ExecuteAction } from '@microsoft/teams.cards';
import { cardAttachment } from '@microsoft/teams.api';

const card = new AdaptiveCard()
  .addBody(new TextBlock('Hi').withWeight('Bolder'))
  .addBody(new TextInput('email').withPlaceholder('you@example.com'))
  .addActions(new ExecuteAction('save').withTitle('Save'));

await send(new MessageActivity().addAttachment(cardAttachment('adaptive', card)));
```

See `adaptive-cards` skill for the full builder catalogue.

## AI

```ts
import { ChatPrompt } from '@microsoft/teams.ai';
import { OpenAIChatModel } from '@microsoft/teams.openai';

const prompt = new ChatPrompt({
  instructions: 'You are a helpful assistant.',
  model: new OpenAIChatModel({ model: 'gpt-4o' }),
});

const { content } = await prompt.send('Quote me Marcus Aurelius');
```

See `ai-agents` skill + `references/prompts-and-models.md`.

## Plugins

```ts
new App({ plugins: [new DevtoolsPlugin(), new McpPlugin(), new A2AClientPlugin(...)] });
```

Plugins intercept the activity pipeline. See `mcp-plugin` for MCP-specific patterns.

## Reference files

- `references/packages-overview.md` — what each `@microsoft/teams.*` package exports
- `references/app-class.md` — `AppOptions`, `cloud` enum, lifecycle hooks
- `references/activity-types.md` — exhaustive activity-name → type table
- `references/llms-typescript-full.md` — trimmed offline copy of the SDK's own LLM reference
