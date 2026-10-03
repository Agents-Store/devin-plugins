---
name: message-extensions
description: Use this skill when the user is building Microsoft Teams message extensions on Teams SDK 2.1 — search commands (`message.ext.query`), action commands (`message.ext.submit`, `message.ext.open`), link unfurling (`message.ext.query-link`), item selection, settings pages. Triggers on "Teams message extension", "compose extension", "link unfurling", "message.ext.query", "search command Teams", "action command".
---

# Message extensions

A message extension lets users call the bot from the compose box or from a message's menu. Each kind is a route:

| Kind | Route | Purpose |
|---|---|---|
| Search command | `message.ext.query` | The user typed a search in the compose-box menu |
| Item selection | `message.ext.select-item` | The user tapped a result that carried a `tap` action |
| Action command | `message.ext.submit` | The user submitted an action command's form |
| Action command with a dynamic form | `message.ext.open` | The command has `fetchTask: true`; the bot returns the dialog |
| Link unfurling | `message.ext.query-link` | The user pasted a URL on a registered domain |
| Settings | `message.ext.query-settings-url`, `message.ext.setting` | Settings page link and its result |

Commands are declared in the app manifest. The scaffolded project keeps no manifest file; edit it through the CLI (`teams app manifest download <teamsAppId> manifest.json`, edit, `teams app manifest upload manifest.json <teamsAppId>`) or one field at a time with `teams app manifest update`. See `cli-recipes`.

## 1. Search command

Manifest fragment (the `botId` of a downloaded manifest is already the real bot id; in a manifest template it is `${{BOT_ID}}`):

```jsonc
{
  "composeExtensions": [{
    "botId": "${{BOT_ID}}",
    "commands": [{
      "id": "searchQuery",
      "type": "query",
      "title": "Search issues",
      "context": ["compose", "commandBox"],
      "parameters": [{ "name": "q", "title": "Query", "inputType": "text" }]
    }]
  }]
}
```

Handler. Each result is an Adaptive Card (shown when picked) plus a `preview` card (shown in the result list):

```ts
import { ThumbnailCard, cardAttachment } from '@microsoft/teams.api';
import { AdaptiveCard, FactSet, Fact, TextBlock } from '@microsoft/teams.cards';

app.on('message.ext.query', async ({ activity }) => {
  const { commandId } = activity.value;
  const q = String(activity.value.parameters?.[0]?.value ?? '');
  if (commandId !== 'searchQuery') return { status: 400 };

  const issues = await searchIssues(q);
  const attachments = issues.map((issue) => {
    const card = new AdaptiveCard(
      new TextBlock(`${issue.id}: ${issue.title}`, { weight: 'Bolder', wrap: true }),
      new FactSet(new Fact('Status', issue.status), new Fact('Assignee', issue.assignee)),
    );
    const preview = { title: `${issue.id}: ${issue.title}`, text: issue.status } satisfies ThumbnailCard;
    return { ...cardAttachment('adaptive', card), preview: cardAttachment('thumbnail', preview) };
  });

  return {
    composeExtension: { type: 'result', attachmentLayout: 'list', attachments },
  } as const;
});
```

Response types: `result` (normal), `auth` (ask the user to sign in), `config` (send to a settings page). Without a `tap` on the preview, tapping a result inserts its card into the compose box. With a `tap` of type `invoke`, Teams calls `message.ext.select-item` instead:

```ts
app.on('message.ext.select-item', async ({ activity, send }) => {
  const { option } = activity.value;       // the value you put in the tap action
  await send(`Selected item: ${String(option)}`);
  return { status: 200 };
});
```

## 2. Action commands

```jsonc
{
  "composeExtensions": [{
    "commands": [
      { "id": "createCard", "type": "action", "title": "Create card", "context": ["compose", "commandBox"],
        "fetchTask": false,
        "parameters": [{ "name": "title", "title": "Title", "inputType": "text" }] },
      { "id": "fetchConversationMembers", "type": "action", "title": "List members", "context": ["compose"],
        "fetchTask": true }
    ]
  }]
}
```

- `fetchTask: false` with parameters: Teams renders the form from the manifest and posts it to `message.ext.submit`.
- `fetchTask: true`: Teams first asks the bot for the form (`message.ext.open`), then posts the result to `message.ext.submit`.

```ts
import { cardAttachment } from '@microsoft/teams.api';
import { AdaptiveCard, TextBlock } from '@microsoft/teams.cards';

app.on('message.ext.submit', async ({ activity }) => {
  const { commandId } = activity.value;
  if (commandId !== 'createCard') throw new Error(`Unknown commandId: ${commandId}`);

  const created = await createTask(activity.value.data);          // form values keyed by parameter name
  return {
    composeExtension: {
      type: 'result',
      attachmentLayout: 'list',
      attachments: [cardAttachment('adaptive', new AdaptiveCard(new TextBlock(created.title, { weight: 'Bolder' })))],
    },
  } as const;
});

app.on('message.ext.open', async ({ activity, api }) => {
  const members = await api.conversations.getMembers(activity.conversation.id);
  const card = new AdaptiveCard(new TextBlock(members.map((m) => m.name).join(', '), { wrap: true }));
  return {
    task: {
      type: 'continue',
      value: { title: 'Conversation members', height: 'small', width: 'small', card: cardAttachment('adaptive', card) },
    },
  } as const;
});
```

A command with `context: ["message"]` receives the selected message as `activity.value.messagePayload` (`body.content`, `attachments`, `createdDateTime`, `linkToMessage`).

## 3. Link unfurling

```jsonc
{
  "composeExtensions": [{
    "messageHandlers": [{ "type": "link", "value": { "domains": ["links.example.com"] } }]
  }]
}
```

```ts
import { ThumbnailCard, cardAttachment } from '@microsoft/teams.api';
import { AdaptiveCard, TextBlock } from '@microsoft/teams.cards';

app.on('message.ext.query-link', async ({ activity }) => {
  const { url } = activity.value;
  if (!url) return { status: 400 };

  const meta = await fetchPreview(url);
  const card = new AdaptiveCard(new TextBlock(meta.title, { weight: 'Bolder', size: 'Large' }), new TextBlock(url, { size: 'Small' }));
  const thumbnail = { title: meta.title, text: url } satisfies ThumbnailCard;
  return {
    composeExtension: {
      type: 'result',
      attachmentLayout: 'list',
      attachments: [{ ...cardAttachment('adaptive', card), preview: cardAttachment('thumbnail', thumbnail) }],
    },
  } as const;
});
```

The domain must be in `messageHandlers[].value.domains`, and the host of the link page in `validDomains`.

## 4. Settings

The settings page is a web page served by the bot (`app.tab('settings', dir)`) that calls `microsoftTeams.authentication.notifySuccess(value)` when saved.

```ts
app.on('message.ext.query-settings-url', async () => ({
  composeExtension: {
    type: 'config',
    suggestedActions: {
      actions: [{ type: 'openUrl', title: 'Settings', value: `${process.env['BOT_ENDPOINT']}/tabs/settings` }],
    },
  },
} as const));

app.on('message.ext.setting', async ({ activity, send }) => {
  const { state } = activity.value;
  if (state === 'CancelledByUser') return { status: 400 };
  await send(`Selected option: ${String(state)}`);
  return { status: 200 };
});
```

Store the setting in your own storage keyed by `activity.from.id` (the app-level `storage` is deprecated).

## Common pitfalls

- **The command never fires** — it is missing from `composeExtensions[].commands`, or the extension's `botId` is not the bot's client id.
- **The action command's form never opens** — `fetchTask: true` needs `message.ext.open`; `dialog.open.*` handlers do not receive it.
- **Link unfurling does nothing** — the domain is missing from `messageHandlers[].value.domains` or `validDomains`.
- **A 400 or empty result** — the handler returned something other than `{ composeExtension: … }`, `{ task: … }` or `{ status }`.
- **`attachmentLayout`** — `list` is the default; use `grid` for thumbnails.
