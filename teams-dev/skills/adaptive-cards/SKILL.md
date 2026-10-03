---
name: adaptive-cards
description: Use this skill when the user is building or sending Adaptive Cards from a Microsoft Teams bot on `@microsoft/teams.cards` 2.1 — `AdaptiveCard`, `TextBlock`, inputs with `.withId()`, `ExecuteAction` with `SubmitData`, routing `card.action.<action>`, input validation, pasting Designer JSON, search-as-you-type choice sets. Triggers on "Teams card", "Adaptive Card", "Action.Execute", "card form", "card.action", "Adaptive Card Designer".
---

# Adaptive Cards in Teams (TypeScript)

`@microsoft/teams.cards` has a typed builder for every element of the Adaptive Card schema. The 2.x shape: **children go into the constructor**, optional properties go into an options object or a `with*` call, and the id of an input is set with `.withId()`. The full catalogue is in `references/card-builders.md`.

## A minimal card

```ts
import { AdaptiveCard, TextBlock } from '@microsoft/teams.cards';

app.on('message', async ({ send }) => {
  const card = new AdaptiveCard(
    new TextBlock('Hello from Teams', { weight: 'Bolder', size: 'Large', wrap: true }),
  );
  await send(card);
});
```

`send(card)` wraps the card in the attachment envelope. To combine text and a card, or to send several attachments, use the message builder: `new MessageActivityInput('Heads up:').addCard('adaptive', card)` (see `messaging`).

## Inputs and actions

```ts
import {
  AdaptiveCard, TextBlock, TextInput, NumberInput, DateInput, ChoiceSetInput,
  ActionSet, ExecuteAction, OpenUrlAction, SubmitData,
} from '@microsoft/teams.cards';

const signupCard = new AdaptiveCard(
  new TextBlock('Sign up', { weight: 'Bolder', size: 'Large' }),
  new TextInput().withId('email').withLabel('Email').withPlaceholder('you@example.com').withIsRequired(),
  new NumberInput({ id: 'age', label: 'Age' }).withMin(0).withMax(120),
  new DateInput({ id: 'start_date', label: 'Start date' }),
  new ChoiceSetInput(
    { title: 'Engineer', value: 'eng' },
    { title: 'Designer', value: 'design' },
  ).withId('role').withLabel('Role').withValue('eng'),
  new ActionSet(
    new ExecuteAction({ title: 'Save' })
      .withData(new SubmitData('save_signup', { source: 'welcome-card' }))
      .withAssociatedInputs('auto')
      .withStyle('positive'),
    new OpenUrlAction('https://example.com/help').withTitle('Learn more'),
  ),
);
```

- Every input needs an **id** — without it the value is not validated and not sent. Set it in the options object (`new TextInput({ id: 'email' })`) or with `.withId('email')`.
- `ChoiceSetInput` takes its choices as arguments (`{ title, value }` objects). `value` is the wire value, `title` the label.
- `.withAssociatedInputs('auto')` makes the action collect and validate every input of the card. Without it no input values travel with the action.
- Actions go into an `ActionSet` inside the body, or into `card.withActions(...)` for the card's action bar.
- `SubmitData(action, extra?)` sets the reserved `action` key that the router reads, plus any static data that should come back with the submission.

## Handle the submission

The router dispatches `card.action.<action>` using the name passed to `SubmitData`; `card.action` is the catch-all.

```ts
app.on('card.action.save_signup', async ({ activity, send }) => {
  const data = activity.value.action.data;       // inputs + extra data, all values untyped; checkbox values arrive as strings
  await send(`Saved: ${String(data.email)} (${String(data.role)})`);
  return {
    statusCode: 200,
    type: 'application/vnd.microsoft.activity.message',
    value: 'Saved',
  } as const;
});
```

The handler **must return** a response for the invoke: a message (as above), an error (`application/vnd.microsoft.error` with `statusCode` 400 and a `code`/`message` body), or a replacement card:

```ts
import { AdaptiveCard, TextBlock } from '@microsoft/teams.cards';

app.on('card.action.approve', async () => ({
  statusCode: 200,
  type: 'application/vnd.microsoft.card.adaptive',
  value: new AdaptiveCard(new TextBlock('Approved', { weight: 'Bolder', color: 'Good' })),
} as const));
```

Types for the three response shapes are exported from `@microsoft/teams.api` (`AdaptiveCardActionMessageResponse`, `AdaptiveCardActionErrorResponse`, `AdaptiveCardActionCardResponse`) — use them with `satisfies`.

## Validation

```ts
import { AdaptiveCard, ActionSet, ExecuteAction, NumberInput, SubmitData, TextInput } from '@microsoft/teams.cards';

const profileCard = new AdaptiveCard(
  new TextInput({ id: 'name' }).withLabel('Name').withIsRequired().withErrorMessage('Name is required!'),
  new NumberInput({ id: 'age' }).withLabel('Age').withIsRequired(true).withMin(0).withMax(120),
  new ActionSet(
    new ExecuteAction({ title: 'Save' })
      .withData(new SubmitData('save_profile'))
      .withAssociatedInputs('auto'),     // the client blocks the submit until all inputs validate
  ),
);
```

## Containers and layout

```ts
import { AdaptiveCard, Column, ColumnSet, Container, Image, TextBlock } from '@microsoft/teams.cards';

const row = new AdaptiveCard(
  new Container(
    new ColumnSet().withColumns(
      new Column(new Image('https://example.com/avatar.png', { size: 'Small' })).withWidth('auto'),
      new Column(new TextBlock('Ada Lovelace', { weight: 'Bolder' })),
    ),
  ).withStyle('emphasis'),
);
```

`Container`, `Column` and `ActionSet` take their children as arguments; `ColumnSet` takes columns through `withColumns(...)`.

## Cards from the Designer

Paste Designer JSON as typed data and, if needed, attach more with the builder:

```ts
import { AdaptiveCard, IAdaptiveCard } from '@microsoft/teams.cards';

const designerJson: IAdaptiveCard = {
  type: 'AdaptiveCard',
  version: '1.5',
  body: [{ type: 'TextBlock', text: 'Imported card', wrap: true }],
};

const card = new AdaptiveCard().withBody(...(designerJson.body ?? []));
```

`withBody` takes the elements; the card has no JSON-parsing factory. When a card is serialised, default-valued properties are no longer written (2.1), so tests that compare the raw JSON against a snapshot must expect a smaller payload.

## Dynamic search in a choice set

A choice set can search as the user types. The card declares the dataset, and the `card.search` route answers:

```ts
import { IAdaptiveCard } from '@microsoft/teams.cards';

const searchCard: IAdaptiveCard = {
  type: 'AdaptiveCard',
  version: '1.5',
  body: [{
    type: 'Input.ChoiceSet',
    id: 'game',
    label: 'Game',
    style: 'filtered',
    choices: [],
    'choices.data': { type: 'Data.Query', dataset: 'games' },
  }],
  actions: [{ type: 'Action.Execute', title: 'Submit', data: { action: 'submit_game' } }],
};

const GAMES = ['Super Mario Odyssey', 'Metroid Dread', 'Splatoon 3'];

app.on('card.search', async ({ activity }) => {
  const query = activity.value.queryText?.toLowerCase() ?? '';
  const results = GAMES.filter((g) => g.toLowerCase().includes(query)).map((g) => ({ title: g, value: g }));
  return {
    statusCode: 200,
    type: 'application/vnd.microsoft.search.searchResponse',
    value: { results },
  } as const;
});
void searchCard;
```

## Common pitfalls

- **Builder code from early-preview samples fails to compile** — chained `add*` calls for children, a JSON-parsing factory and an id as the first constructor argument are gone in 2.x. Put children in the constructor, use `withBody`/`withActions`, and `withId`.
- **The action does nothing** — no `SubmitData` name, so no `card.action.<action>` route matches; or the handler returned nothing and Teams shows an error.
- **Inputs missing from the submission** — no id on the input, or `withAssociatedInputs('auto')` is missing on the action.
- **Card renders blank in Teams** — an element newer than the client supports; check the card schema version against the Teams client you test on.
- **Checkbox shows `"true"`** — toggle values come back as strings; compare against `'true'`.
