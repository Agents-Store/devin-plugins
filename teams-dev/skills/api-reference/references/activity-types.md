# Activity routes (`app.on`) — Teams SDK 2.1

The route string passed to `app.on(...)` selects the activity type of the handler and the response type it must return. An unknown route is a compile error, so the route list below is also the source of truth for what exists. Invoke activities are routed from their wire name (`task/fetch`, `composeExtension/query`, …) to the dotted names here.

## Chat activities

| Route | Fires | Useful fields |
|---|---|---|
| `message` | A chat message | `text`, `attachments`, `entities`, `from`, `conversation`, `stripMentionsText()`, `getQuotedMessages()` |
| `messageReaction` | A reaction added or removed | `reactionsAdded`, `reactionsRemoved` |
| `messageUpdate`, `messageDelete` | A message edited, restored or deleted | `channelData.eventType` |
| `editMessage`, `undeleteMessage`, `softDeleteMessage` | The same events, split by `eventType` | |
| `typing` | The user is typing | |
| `mention` | The bot was mentioned | |
| `activity` | Every activity (catch-all) | |
| `install.add`, `install.remove` | The app was installed or removed in a scope | `conversation.id`, `from` |
| `conversationUpdate` | Any conversation update | `channelData.eventType` |
| `channelCreated`, `channelDeleted`, `channelRenamed`, `channelRestored`, `channelShared`, `channelUnshared`, `channelMemberAdded`, `channelMemberRemoved`, `teamArchived`, `teamDeleted`, `teamHardDeleted`, `teamRenamed`, `teamRestored`, `teamUnarchived`, `teamMemberAdded`, `teamMemberRemoved` | The `eventType` values of `conversationUpdate`, each as its own route | `membersAdded`, `membersRemoved`, `channelData.channel`, `channelData.team` |

## Event activities

| Route | Fires |
|---|---|
| `meetingStart`, `meetingEnd` | A meeting started or ended; `value` has the title and times (`StartTime`, `EndTime`, `Title`, `JoinUrl`) |
| `meetingParticipantJoin`, `meetingParticipantLeave` | A participant joined or left; `value.members[]` |
| `readReceipt` | A read receipt |
| `agentLifecycle`, `agenticUserIdentityCreated`, `agenticUserIdentityUpdated`, `agenticUserManagerUpdated`, `agenticUserEnabled`, `agenticUserDisabled`, `agenticUserDeleted`, `agenticUserUndeleted`, `agenticUserWorkloadOnboardingUpdated` | Agent 365 lifecycle events |

## Invoke activities

| Route | Wire name | Typical `value` and response |
|---|---|---|
| `card.action`, `card.action.<action>` | `adaptiveCard/action` | `value.action.data`; respond with a message, an error or a card (`adaptive-cards`) |
| `card.search` | `application/search` | `value.queryText`, `value.dataset`; respond with search results |
| `dialog.open`, `dialog.open.<id>` | `task/fetch` | return `{ task: { type: 'continue', value } }` (`dialogs`) |
| `dialog.submit`, `dialog.submit.<action>` | `task/submit` | `value.data`; return a `task` response or `{ status: 200 }` |
| `message.ext.query` | `composeExtension/query` | `value.commandId`, `value.parameters[]`; return `{ composeExtension }` |
| `message.ext.select-item` | `composeExtension/selectItem` | the `tap` value of the chosen result |
| `message.ext.submit` | `composeExtension/submitAction` | `value.commandId`, `value.data`, `value.messagePayload` |
| `message.ext.edit`, `message.ext.send` | `composeExtension/submitAction` with `value.botMessagePreviewAction` | the user edited or sent a bot message preview |
| `message.ext.open` | `composeExtension/fetchTask` | the action command's dynamic form |
| `message.ext.query-link` | `composeExtension/queryLink` | `value.url` |
| `message.ext.anon-query-link` | `composeExtension/anonymousQueryLink` | `value.url`, for users who have not signed in |
| `message.ext.query-settings-url` | `composeExtension/querySettingUrl` | return a `config` response |
| `message.ext.setting` | `composeExtension/setting` | `value.state` |
| `message.ext.card-button-clicked` | `composeExtension/onCardButtonClicked` | a button on a result card |
| `message.fetch-task`, `message.submit`, `message.submit.<actionName>` | `message/fetchTask`, `message/submitAction` | message actions; `message.submit.feedback` (thumbs on an AI message) carries `value.actionValue.reaction` and `.feedback` |
| `message.execute` | `actionableMessage/executeAction` | legacy actionable messages |
| `tab.open`, `tab.submit` | `tab/fetch`, `tab/submit` | tab content requests |
| `config.open`, `config.submit` | `config/fetch`, `config/submit` | configuration page requests |
| `file.consent`, `file.consent.accept`, `file.consent.decline` | `fileConsent/invoke` | file upload consent; the sub-routes follow `value.action` |
| `signin.token-exchange`, `signin.verify-state`, `signin.failure` | `signin/tokenExchange`, `signin/verifyState`, `signin/failure` | handled by OAuth flows (`authentication`) |
| `handoff.action` | `handoff/action` | hand-off between agents |
| `suggested-action.submit` | `suggestedActions/submit` | a suggested action was chosen |
| `widget.callTool` | `htmlwidget/calltool` | an HTML widget calls a tool |

## Routing order

Every handler whose route matches the activity is a candidate, in registration order; a handler passes control on by calling `next()`, one that answers does not. `app.use(handler)` wraps every activity. There is no prefix or longest-match logic — a route either equals the name derived from the activity or it does not.

How the dotted sub-routes are derived from the payload:

| Route | Matches when |
|---|---|
| `dialog.open.<id>` | the `task/fetch` payload has `value.data.dialog_id === <id>` (what `OpenDialogData(<id>)` writes) |
| `dialog.submit.<action>` | the `task/submit` payload has `value.data.action === <action>` (what `SubmitData(<action>)` writes) |
| `card.action.<action>` | the card action payload has `value.action.data.action === <action>` (the same `SubmitData` key) |
| `message.submit.<actionName>` | `value.actionName` of `message/submitAction` |
| `install.<action>` | `action` of the installation update (`add`, `remove`) |
| conversation and message events | `channelData.eventType` |

A payload without that key reaches only the bare route (`dialog.submit`, `card.action`, …), so a catch-all is the place for submissions that do not come from `SubmitData`.

## Common payload fields

```ts
app.on('message', async ({ activity }) => {
  activity.id;             // activity id
  activity.type;           // 'message'
  activity.from;           // { id, name, aadObjectId }
  activity.recipient;      // the bot's account
  activity.conversation;   // { id, conversationType: 'personal' | 'groupChat' | 'channel', tenantId }
  activity.channelId;      // 'msteams'
  activity.replyToId;      // parent activity id for replies
  activity.text;
  activity.attachments;
  activity.channelData;    // Teams extras: team, channel, tenant, eventType
});
```

## Type narrowing

The route name narrows `activity` for you. Do not widen it into a generic `Activity` variable before reading route-specific fields — the narrowing is lost.
