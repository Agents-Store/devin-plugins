# Activity types

The route string passed to `app.on(...)` determines the activity type the handler receives. Bind specific handlers to the most precise route possible; use bare prefixes only when you want to catch everything below them.

## Routing table

| Route string | Activity class | Use |
|---|---|---|
| `message` | `MessageActivity` | Chat message in 1:1 / group / channel |
| `message.reaction` | `MessageReactionActivity` | Reaction added/removed on a previous message |
| `message.update` | `MessageUpdateActivity` | Existing message edited |
| `message.delete` | `MessageDeleteActivity` | Existing message deleted |
| `install.add` | `InstallActivity` | First install of the bot in a scope |
| `install.remove` | `InstallActivity` | Uninstall |
| `conversation.update` | `ConversationUpdateActivity` | Members added/removed, team renamed |
| `members.added` | shortcut | Subset of `conversation.update` |
| `members.removed` | shortcut | Subset of `conversation.update` |
| `config.open` | `ConfigOpenActivity` | Tab configuration page opens |
| `config.submit` | `ConfigSubmitActivity` | Tab configuration submitted |
| `dialog.open.<id>` | `DialogOpenActivity` | Specific dialog id opening |
| `dialog.open` | `DialogOpenActivity` | Any dialog opening |
| `dialog.submit.<id>` | `DialogSubmitActivity` | Specific dialog id submitted |
| `dialog.submit` | `DialogSubmitActivity` | Any dialog submitted |
| `card.action.<id>` | `CardActionActivity` | `Action.Execute` on an Adaptive Card |
| `card.action` | `CardActionActivity` | Any card execute action |
| `message.ext.query` | `MessageExtQueryActivity` | Search command typed in compose |
| `message.ext.submit` | `MessageExtSubmitActivity` | Action command submitted |
| `message.ext.select-item` | `MessageExtSelectItemActivity` | User clicked a search result |
| `message.ext.query-link` | `MessageExtQueryLinkActivity` | URL pasted in compose triggers preview |
| `message.ext.fetch-task` | `MessageExtFetchTaskActivity` | Action command needs `fetchTask: true` form |
| `signin.token-exchange` | `SigninTokenExchangeActivity` | SSO token-exchange callback |
| `signin.verify-state` | `SigninVerifyStateActivity` | SSO verify-state callback |
| `task.complete` | `TaskCompleteActivity` | Long-running task finished (callback style) |

## Routing precedence

Handlers are matched longest-prefix first, then in registration order. Two handlers on the same route both run unless one short-circuits without calling `next()`.

```ts
app.on('dialog.submit', async ({ next }) => {
  // Pre-validation for every dialog submit
  await next();
});

app.on('dialog.submit.signup_form', async ({ activity, send }) => {
  // Specific to signup_form
});
```

## Common payload fields

```ts
activity.id               // GUID
activity.type             // 'message' | 'invoke' | 'event' | …
activity.from             // { id, name, aadObjectId }
activity.recipient        // bot identity
activity.conversation     // { id, conversationType: 'personal' | 'groupChat' | 'channel', tenantId }
activity.channelId        // 'msteams'
activity.replyToId        // root activity id when this is a reply
activity.text             // user text (message-like)
activity.attachments      // [{ contentType, content, … }]
activity.value            // payload for invoke activities (card actions, dialog submits, …)
activity.channelData      // Teams-specific extra fields (channel, team, tenant)
```

## Type narrowing

The handler's `activity` is narrowed automatically based on the route string. Example:

```ts
app.on('dialog.submit.signup_form', async ({ activity }) => {
  // activity is DialogSubmitActivity — has .value.data
  const data = activity.value.data;
});

app.on('message.ext.query', async ({ activity }) => {
  // activity is MessageExtQueryActivity — has .value.commandId, .value.parameters
});
```

Avoid storing the activity in a generic variable before reading id-bound fields — narrowing is lost once you assign to `Activity`.
