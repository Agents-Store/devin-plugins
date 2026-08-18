---
name: message-extensions
description: Use this skill when the user is building Microsoft Teams message extensions — search-based "compose extension" commands, action commands, link unfurling, or item selection from a search list. Triggers on "Teams message extension", "compose extension", "link unfurling", "message.ext.query", "search command Teams".
---

# Message extensions (compose extensions)

A message extension lets users invoke the bot from the compose box of any chat. The four activity verbs cover the full surface:

| Verb | Handler route | Purpose |
|---|---|---|
| Search query | `message.ext.query` | User typed a search term in the compose-box menu |
| Action submit | `message.ext.submit` | User submitted an action command form |
| Item selection | `message.ext.select-item` | User clicked a search result |
| Link unfurling | `message.ext.query-link` | Teams previews a pasted URL |

## 1. Search command

Manifest fragment in `appPackage/manifest.json`:

```jsonc
{
  "composeExtensions": [{
    "botId": "${BOT_ID}",
    "commands": [{
      "id": "searchIssues",
      "type": "query",
      "title": "Search issues",
      "context": ["compose", "commandBox"],
      "parameters": [{ "name": "q", "title": "Query", "inputType": "text" }]
    }]
  }]
}
```

Handler:

```ts
import { cardAttachment } from '@microsoft/teams.api';
import { AdaptiveCard, TextBlock } from '@microsoft/teams.cards';

app.on('message.ext.query', async ({ activity }) => {
  const commandId = activity.value.commandId;            // 'searchIssues'
  const param = activity.value.parameters?.find(p => p.name === 'q');
  const q = String(param?.value ?? '');

  const results = await searchIssues(q);

  return {
    composeExtension: {
      type: 'result',
      attachmentLayout: 'list',
      attachments: results.map(r =>
        cardAttachment(
          'adaptive',
          new AdaptiveCard().addBody(new TextBlock(r.title).withWeight('Bolder')),
        ),
      ),
    },
  };
});
```

Return shape:
- `type: 'result'` for normal returns.
- `type: 'auth'` to request sign-in (see `authentication`).
- `type: 'config'` to direct the user to a settings page.

## 2. Action command

Manifest:

```jsonc
{
  "composeExtensions": [{
    "commands": [{
      "id": "createTask",
      "type": "action",
      "title": "Create task",
      "context": ["compose", "commandBox", "message"],
      "fetchTask": true
    }]
  }]
}
```

`fetchTask: true` means Teams calls `dialog.open.createTask` to build the form on the fly:

```ts
app.on('dialog.open.createTask', async () => ({
  task: { type: 'continue', value: { title: 'New task', card: { contentType: '…', content: form.toJSON() } } },
}));

app.on('message.ext.submit', async ({ activity }) => {
  const data = activity.value.data;
  const created = await createTask(data);
  return {
    composeExtension: {
      type: 'result',
      attachmentLayout: 'list',
      attachments: [cardAttachment('adaptive', renderTaskCard(created))],
    },
  };
});
```

## 3. Item selection

```ts
app.on('message.ext.select-item', async ({ activity }) => {
  const selected = activity.value as { id: string };
  const item = await loadItem(selected.id);
  return {
    composeExtension: {
      type: 'result',
      attachmentLayout: 'list',
      attachments: [cardAttachment('adaptive', renderItemCard(item))],
    },
  };
});
```

Trigger by attaching a `Action.Invoke` with a payload that includes the id you want back.

## 4. Link unfurling

Manifest:

```jsonc
{
  "composeExtensions": [{
    "messageHandlers": [{
      "type": "link",
      "value": { "domains": ["yourapp.example.com"] }
    }]
  }]
}
```

Handler:

```ts
app.on('message.ext.query-link', async ({ activity }) => {
  const url = activity.value.url;
  const meta = await fetchPreview(url);
  return {
    composeExtension: {
      type: 'result',
      attachmentLayout: 'list',
      attachments: [cardAttachment('adaptive', renderPreviewCard(meta))],
    },
  };
});
```

When a user pastes a `https://yourapp.example.com/...` link in compose, Teams calls this handler and shows the returned card as a preview.

## Context values

`commandId`, `parameters`, and `messagePayload` (for `context: ['message']` commands) all live on `activity.value`. Type-narrow by `commandId` before reading.

## Common pitfalls

- **Search command never fires** — the command is missing from the manifest's `composeExtensions.commands` array, or the manifest's `botId` does not match `BOT_ID` in `.env`.
- **Link unfurling silently does nothing** — the domain is not listed in `messageHandlers[].value.domains` or in `validDomains`.
- **`message.ext.submit` returns 400** — your handler returned the wrong envelope shape; the response must have a `composeExtension` root key.
- **No results visible** — `attachmentLayout` defaults to `list`. For thumbnails, set `attachmentLayout: 'grid'`.
