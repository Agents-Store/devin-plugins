# Scenario — Message-extension search command

A "compose extension" the user invokes from the message compose box to search a backing dataset and pick a result card to send.

## Steps

```bash
teams project new typescript me-search --template echo
cd me-search
npm install
```

Add the command to `appPackage/manifest.json`:

```jsonc
{
  "composeExtensions": [{
    "botId": "${BOT_ID}",
    "commands": [{
      "id": "searchIssues",
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

Edit `src/index.ts`:

```ts
import { App } from '@microsoft/teams.apps';
import { DevtoolsPlugin } from '@microsoft/teams.dev';
import { AdaptiveCard, TextBlock, FactSet, Fact } from '@microsoft/teams.cards';
import { cardAttachment } from '@microsoft/teams.api';

type Issue = { id: string; title: string; status: 'open' | 'closed'; assignee: string };

async function searchIssues(q: string): Promise<Issue[]> {
  // Replace with a real call to your issue tracker.
  const sample: Issue[] = [
    { id: 'BUG-1', title: 'Login fails on Safari', status: 'open', assignee: 'alice' },
    { id: 'BUG-2', title: 'Card renders blank', status: 'closed', assignee: 'bob' },
    { id: 'FEAT-9', title: 'Add SSO', status: 'open', assignee: 'carol' },
  ];
  const needle = q.toLowerCase();
  return sample.filter((i) => i.title.toLowerCase().includes(needle));
}

const issueCard = (i: Issue) =>
  new AdaptiveCard()
    .addBody(new TextBlock(`${i.id}: ${i.title}`).withWeight('Bolder'))
    .addBody(
      new FactSet()
        .addFact(new Fact('Status', i.status))
        .addFact(new Fact('Assignee', i.assignee)),
    );

const app = new App({
  plugins: [new DevtoolsPlugin()],
});

app.on('message.ext.query', async ({ activity }) => {
  const param = activity.value.parameters?.find((p) => p.name === 'q');
  const q = String(param?.value ?? '');

  const results = await searchIssues(q);

  return {
    composeExtension: {
      type: 'result',
      attachmentLayout: 'list',
      attachments: results.map((i) => cardAttachment('adaptive', issueCard(i))),
    },
  };
});

(async () => {
  await app.start();
})();
```

## Run

```bash
devtunnel host -p 3978 --allow-anonymous
teams app update $(teams app list --json | jq -r '.[0].teamsAppId') --endpoint "https://<tunnel-host>/api/messages"
npm run dev
```

## Verify

1. Sideload the updated manifest in Teams.
2. In any chat compose box, click the **+** icon → pick **Search issues**.
3. Type `login`. Results appear in the dropdown.
4. Click **BUG-1** — the issue card is inserted in the message draft.
5. Send the message. The card renders in the conversation.

DevTools shows the `message.ext.query` activity with `value.parameters` containing your query.

## Common tweaks

- Switch `attachmentLayout: 'list'` to `'grid'` for thumbnail previews.
- Add caching keyed on query string to keep results snappy.
- Add an `action` command (`type: 'action'`) for users to *create* an issue from a compose form — see `message-extensions` for the dialog flow.
