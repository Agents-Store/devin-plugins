# Scenario — Message-extension search command

A "compose extension" the user opens from the compose box to search a dataset and pick a card to send.

## 1. Scaffold and register

```bash
teams project new typescript me-search -t echo --yes
cd me-search
npm install @microsoft/teams.cards @microsoft/teams.api
```

Register the app as in `echo-bot.md` (`teams app create … --env .env`) — the extension is tested in Teams, the Playground does not render compose-box menus.

## 2. Add the command to the manifest

The scaffolded project keeps no manifest file; the manifest lives in the Developer Portal. Download it, add the command, upload it:

```bash
teams app manifest download <teamsAppId> manifest.json
```

Add this under the manifest root, keeping the bot's real id in `botId`:

```jsonc
{
  "composeExtensions": [{
    "botId": "<existing bot id from the manifest>",
    "commands": [{
      "id": "searchQuery",
      "type": "query",
      "title": "Search issues",
      "description": "Search the issue tracker and insert a card",
      "context": ["compose", "commandBox"],
      "parameters": [
        { "name": "q", "title": "Query", "description": "Search text", "inputType": "text" }
      ]
    }]
  }]
}
```

```bash
teams app manifest upload manifest.json <teamsAppId>
```

The upload bumps the patch version when the content changed; reinstall the app in Teams so the client picks the command up.

## 3. The handler

Replace `src/index.ts`:

```ts
import { ThumbnailCard, cardAttachment } from '@microsoft/teams.api';
import { App } from '@microsoft/teams.apps';
import { AdaptiveCard, Fact, FactSet, TextBlock } from '@microsoft/teams.cards';

type Issue = { id: string; title: string; status: 'open' | 'closed'; assignee: string };

const SAMPLE: Issue[] = [
  { id: 'BUG-1', title: 'Login fails on Safari', status: 'open', assignee: 'alice' },
  { id: 'BUG-2', title: 'Card renders blank', status: 'closed', assignee: 'bob' },
  { id: 'FEAT-9', title: 'Add SSO', status: 'open', assignee: 'carol' },
];

async function findIssues(q: string): Promise<Issue[]> {
  // Replace with a call to your issue tracker.
  const needle = q.toLowerCase();
  return SAMPLE.filter((i) => i.title.toLowerCase().includes(needle));
}

const issueCard = (i: Issue) =>
  new AdaptiveCard(
    new TextBlock(`${i.id}: ${i.title}`, { weight: 'Bolder', wrap: true }),
    new FactSet(new Fact('Status', i.status), new Fact('Assignee', i.assignee)),
  );

const app = new App();

app.on('message.ext.query', async ({ activity }) => {
  const { commandId } = activity.value;
  if (commandId !== 'searchQuery') return { status: 400 };

  const q = String(activity.value.parameters?.[0]?.value ?? '');
  const attachments = (await findIssues(q)).map((issue) => {
    const preview = { title: `${issue.id}: ${issue.title}`, text: `${issue.status}, ${issue.assignee}` } satisfies ThumbnailCard;
    return { ...cardAttachment('adaptive', issueCard(issue)), preview: cardAttachment('thumbnail', preview) };
  });

  return {
    composeExtension: { type: 'result', attachmentLayout: 'list', attachments },
  } as const;
});

app.start(process.env.PORT || 3978).catch(console.error);
```

## 4. Run and verify

```bash
npm run dev          # with the tunnel from echo-bot.md running and the endpoint registered
```

1. In any chat's compose box, open the **+** menu and pick **Search issues**.
2. Type `login`. The result list shows `BUG-1: Login fails on Safari`.
3. Pick it: the issue card is inserted into the draft. Send the message; the card renders in the conversation.

With `LOG_LEVEL=debug` the server logs the `composeExtension/query` invoke and its `value.parameters`.

## Common tweaks

- `attachmentLayout: 'grid'` for thumbnail results.
- Cache results by query string to keep the list snappy.
- Open a detail view on tap: give the preview a `tap` of type `invoke`, then handle `message.ext.select-item` (`message-extensions`).
- Add an action command that creates an issue from a form (`message.ext.submit`, with `fetchTask: true` for a dynamic form handled by `message.ext.open`).
