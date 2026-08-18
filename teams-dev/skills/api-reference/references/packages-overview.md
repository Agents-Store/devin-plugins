# `@microsoft/teams.*` packages

Reference of what every package in the Teams SDK ecosystem exports and when to install it.

## `@microsoft/teams.apps`

Core framework. Always installed.

Exports:
- `App` — main entry point class.
- `AppOptions` — constructor options type.
- Cloud constants: `PUBLIC`, `US_GOV`, `US_GOV_DOD`, `CHINA`.
- `Plugin` base class — implement to write a custom plugin.
- `ExpressAdapter` (subpath `@microsoft/teams.apps/express`) — mount the bot on an existing Express app.

## `@microsoft/teams.api`

Activity types, attachment helpers, REST client types.

Exports:
- Activity classes: `MessageActivity`, `InvokeActivity`, `DialogOpenActivity`, `DialogSubmitActivity`, `CardActionActivity`, `ConfigOpenActivity`, `ConfigSubmitActivity`, message-extension activities, sign-in activities.
- Attachment helpers: `cardAttachment(type, content)`, `OAuthCard`, `HeroCard`, `OpenDialogData`.
- Conversation primitives: `Mention`, `ChannelData`.

## `@microsoft/teams.cards`

Adaptive Card builders.

Exports (non-exhaustive):
- `AdaptiveCard` (root), `Container`, `ColumnSet`, `Column`, `ActionSet`.
- Inputs: `TextInput`, `NumberInput`, `DateInput`, `TimeInput`, `ToggleInput`, `ChoiceSetInput`, `Choice`.
- Display: `TextBlock`, `Image`, `Media`, `RichTextBlock`, `FactSet`, `Fact`.
- Actions: `SubmitAction`, `ExecuteAction`, `OpenUrlAction`, `ToggleVisibilityAction`, `ShowCardAction`.

Builders chain with `.withX(value)` and `.addY(child)` for type-safe composition. `.toJSON()` returns the raw card.

## `@microsoft/teams.ai`

LLM primitives.

Exports:
- `ChatPrompt` — orchestrates conversations with instructions, model, tools, and state.
- `Memory` — pluggable conversation history backing store.

## `@microsoft/teams.openai`

OpenAI and Azure OpenAI model adapter.

Exports:
- `OpenAIChatModel` — accepts `{ apiKey, endpoint, model, apiVersion }`. For OpenAI proper, only `model` is required (key read from env). For Azure, supply all four.

Other model adapters (Anthropic, etc.) live in sibling packages or third-party plugins.

## `@microsoft/teams.mcp`

Model Context Protocol and Agent-to-Agent.

Exports:
- `McpPlugin` — start an MCP server inside the Teams app; register tools and resources.
- `A2AClientPlugin` — call remote A2A agents from `ChatPrompt`.
- Tool/resource schema types.

## `@microsoft/teams.client`

Tab / static-page SDK.

Exports (top-level namespaces):
- `teams.initialize()` — must be called inside Teams.
- `teams.app.getContext()` — theme, user, channel.
- `teams.pages.config.setConfig/getConfig/setValidityState` — channel-tab configuration.
- `teams.authentication.getAuthToken()` — fetch the SSO token from the host.
- `teams.dialog.url.open/submit` — open or submit a URL-based dialog.

Bundle via standard bundlers (Vite, webpack). Tree-shake-safe.

## `@microsoft/teams.dev`

Local developer tools.

Exports:
- `DevtoolsPlugin` — runs the local inspector at `http://localhost:3979/devtools`.

Do not ship to production.

## `@microsoft/teams.cli`

Command-line scaffolding tool. Install globally with `npm i -g @microsoft/teams.cli@preview`. Provides `teams` binary.

Not imported in app code.

## Install matrix

| Goal | Install |
|---|---|
| Echo bot | `@microsoft/teams.apps`, `@microsoft/teams.api`, `@microsoft/teams.dev` |
| Bot with cards | + `@microsoft/teams.cards` |
| AI bot | + `@microsoft/teams.ai`, `@microsoft/teams.openai` |
| MCP-aware bot | + `@microsoft/teams.mcp` |
| Tab | `@microsoft/teams.apps` (server) + `@microsoft/teams.client` (browser) |
| Existing Express server | + `@microsoft/teams.apps` (the `express` subpath ships with the main package) |
