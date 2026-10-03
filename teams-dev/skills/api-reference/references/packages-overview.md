# `@microsoft/teams.*` packages — what to install and what each exports

All packages below are at 2.1.0 on the `latest` dist-tag and need Node 22.12 or newer. The CLI is versioned separately (3.x).

## `@microsoft/teams.apps`

The framework. Every Teams app installs it.

- `App`, `AppOptions` — the entry point and its options.
- `ExpressAdapter`, `IHttpServerAdapter`, `HttpMethod`, `HttpRouteHandler` — HTTP integration. `ExpressAdapter` is exported from the package root.
- `OAuthFlow`, `OAuthSignInCompleteHandler`, `OAuthSignInFailureHandler`, `OAuthSignInOptions` — user sign-in.
- State: `TurnState` and the turn-state container types.
- Files: `FileError`, `FileAccessError`, `FileCredentialError`, `FileScopeNotSupportedError`, `FileUrlExpiredError`.
- `toThreadedConversationId` — build a channel-thread conversation id.
- Diagnostics: `createAgent365Scope`, `withAgent365Baggage`, `TeamsBotApplicationTelemetry`.
- Plugin types (`IPlugin`) for custom plugins.

The cloud presets are **not** exported here; they come from `@microsoft/teams.api`.

## `@microsoft/teams.api`

Activities, attachments and REST clients.

- `MessageActivityInput` (and `TypingActivityInput`) — build outgoing activities.
- `cardAttachment(type, content)` — wrap a card (`'adaptive'`, `'thumbnail'`, …) as an attachment.
- Types: `Account`, `ThumbnailCard`, `Message`, the invoke response types (`AdaptiveCardActionMessageResponse`, `AdaptiveCardActionErrorResponse`, `AdaptiveCardActionCardResponse`).
- Clients: `Client` with `bots`, `users` (incl. `users.token`), `conversations`, `teams`, `meetings`, `reactions` — reachable as `app.api` or `ctx.api`.
- Cloud presets and helpers: `PUBLIC`, `US_GOV`, `US_GOV_DOD`, `CHINA`, `withOverrides`.
- Agent 365: `AgenticIdentity`.

## `@microsoft/teams.cards`

Adaptive Card builders. Constructors take children as arguments; options go in an object or `with*` calls.

- Root and containers: `AdaptiveCard`, `Container`, `ColumnSet`, `Column`, `ActionSet`.
- Display: `TextBlock`, `RichTextBlock`, `TextRun`, `Image`, `Media`, `FactSet`/`Fact`, `CodeBlock`, `Table`.
- Inputs: `TextInput`, `NumberInput`, `DateInput`, `TimeInput`, `ToggleInput`, `ChoiceSetInput`, `Choice`.
- Actions: `ExecuteAction`, `SubmitAction`, `OpenUrlAction`, `ToggleVisibilityAction`, `ShowCardAction`.
- Helpers: `SubmitData(action, extra?)`, `OpenDialogData(dialogId, extra?)`.
- Raw schema types: `IAdaptiveCard`, `IExecuteAction`, …

## `@microsoft/teams.graph`, `@microsoft/teams.graph-endpoints`, `@microsoft/teams.graph-endpoints-beta`

`Client` (`call(endpoint, params)`, `http`), `EndpointRequest` for custom requests; the endpoints packages hold typed builders grouped by Graph resource (`me`, `users`, `teams`, `chats`, …). Install the endpoints packages explicitly.

## `@microsoft/teams.client`

Browser-side `App(clientId, options)` for tabs: `start()`, `graph`, `exec(name, data)`, `hasConsentForScopes`, `ensureConsentForScopes`. Context, pages, dialogs and the host API are in `@microsoft/teams-js`.

## `@microsoft/teams.common`

`ConsoleLogger`, `ILogger`, `IStorage`, `LocalStorage`, the HTTP `Client`.

## `@microsoft/teams.m365extensions`

`useTeamsSdk(agentApp, connectionManager)` and `isTeamsChannel` — run a Teams SDK app inside a Microsoft 365 Agents SDK `AgentApplication` (`@microsoft/agents-hosting`).

## `@microsoft/teams.botbuilder`

Bot Framework interoperability for migrations from BotBuilder.

## `@microsoft/teams.cli`

The `teams` command. Install it globally without a tag: `npm install -g @microsoft/teams.cli` (`cli-recipes`). Never imported in app code.

## Not Teams SDK packages

| Need | Install |
|---|---|
| A model client and tool loop | `openai` (`ai-agents`) |
| MCP client or server | `@modelcontextprotocol/sdk`, `zod` (`mcp-a2a`) |
| Agent2Agent | `@a2a-js/sdk` (`mcp-a2a`) |
| Local testing | `@microsoft/m365agentsplayground`, installed globally (`agents-playground`) |
| Browser host API | `@microsoft/teams-js` |
| Browser sign-in | `@azure/msal-browser` |

## Install matrix

| Goal | Install |
|---|---|
| Echo bot | `@microsoft/teams.apps` |
| Bot with outgoing activity builders and invoke types | + `@microsoft/teams.api` |
| Bot with cards | + `@microsoft/teams.cards` |
| Bot that calls Graph | + `@microsoft/teams.graph`, `@microsoft/teams.graph-endpoints` |
| AI bot | + `openai` |
| Bot that serves or consumes MCP | + `@modelcontextprotocol/sdk`, `zod`, `express` |
| Tab | server: `@microsoft/teams.apps`; browser: `@microsoft/teams.client`, `@microsoft/teams-js` |
| Existing Express server | `@microsoft/teams.apps`, `express` |

`@microsoft/teams.api`, `@microsoft/teams.graph`, `@microsoft/teams.common` and `express` come in as dependencies of `@microsoft/teams.apps`, but list a package in your own `package.json` when your code imports it.
