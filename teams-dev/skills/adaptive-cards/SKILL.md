---
name: adaptive-cards
description: Use this skill when the user is building or sending Adaptive Cards from a Microsoft Teams bot in TypeScript — using `AdaptiveCard`, `TextBlock`, `TextInput`, `ActionSet`, `Action.Submit`, `Action.Execute`, attaching cards via `cardAttachment`, or pasting JSON from the Adaptive Card Designer into TS builders. Triggers on "Teams card", "Adaptive Card", "Action.Submit", "card form".
---

# Adaptive Cards in Teams (TypeScript)

`@microsoft/teams.cards` exposes a builder API mirroring the Adaptive Card schema, with TypeScript types that catch invalid combinations at compile time. The full builder catalogue lives at `references/card-builders.md`.

## A minimal card

```ts
import { AdaptiveCard, TextBlock } from '@microsoft/teams.cards';
import { cardAttachment } from '@microsoft/teams.api';

const card = new AdaptiveCard()
  .addBody(new TextBlock('Hello from Teams').withWeight('Bolder').withSize('Large'));

await send(new MessageActivity().addAttachment(cardAttachment('adaptive', card)));
```

`cardAttachment('adaptive', card)` wraps the builder output in the attachment envelope the activity payload expects.

## Inputs

```ts
import { AdaptiveCard, TextBlock, TextInput, NumberInput, DateInput, ChoiceSetInput, Choice } from '@microsoft/teams.cards';

const card = new AdaptiveCard()
  .addBody(new TextBlock('Sign up').withWeight('Bolder'))
  .addBody(new TextInput('email').withPlaceholder('you@example.com').withIsRequired())
  .addBody(new NumberInput('age').withMin(0).withMax(120))
  .addBody(new DateInput('start_date'))
  .addBody(
    new ChoiceSetInput('role')
      .withChoices([new Choice('Engineer', 'eng'), new Choice('Designer', 'design')])
      .withStyle('compact'),
  );
```

Every input has an `id` (first constructor argument) — that becomes the key on the submission payload.

## Actions

```ts
import { ActionSet, ExecuteAction, SubmitAction, OpenUrlAction } from '@microsoft/teams.cards';

card.addActions(
  new ExecuteAction('save').withTitle('Save').withVerb('save'),
  new SubmitAction().withTitle('Submit').withData({ kind: 'signup' }),
  new OpenUrlAction('https://example.com').withTitle('Learn more'),
);
```

- `Action.Submit` posts back to the bot as a `card.action.<id>` activity if the card was sent via `cardAttachment('adaptive', card)`.
- `Action.Execute` (preferred for Adaptive Cards 1.4+) supports universal actions and refresh.
- `Action.OpenUrl` opens in the user's browser.

Handle the submission:

```ts
app.on('card.action.save', async ({ activity, send }) => {
  const data = activity.value; // typed as Record<string, unknown>
  await send(`Saved: ${JSON.stringify(data)}`);
});
```

## Containers and layout

```ts
import { Container, ColumnSet, Column, Image } from '@microsoft/teams.cards';

card.addBody(
  new Container()
    .addItem(
      new ColumnSet()
        .addColumn(new Column().addItem(new Image('https://.../avatar.png').withSize('Small')).withWidth('auto'))
        .addColumn(new Column().addItem(new TextBlock('Name').withWeight('Bolder'))),
    ),
);
```

`Container`, `ColumnSet`, and `Column` accept any other element type. They map 1:1 to the schema.

## Mixing JSON from the Designer

Authoring complex cards visually in the [Adaptive Card Designer](https://adaptivecards.io/designer/) is often faster. Paste the JSON in and wrap it:

```ts
const designerJson = { type: 'AdaptiveCard', version: '1.5', body: [/* … */] };
const card = AdaptiveCard.fromJSON(designerJson);
card.addActions(new ExecuteAction('save').withTitle('Save'));
```

`fromJSON` validates against the schema. Combine with builder calls to add type-safe inputs and actions on top.

## Refreshing a card

```ts
import { ExecuteAction } from '@microsoft/teams.cards';

card.withRefresh({
  action: new ExecuteAction('refresh').withVerb('refresh'),
  userIds: [user.id],
});
```

A refresh action runs automatically when the addressed user opens a stale card.

## Sending a card-only message

```ts
await send(new MessageActivity().addAttachment(cardAttachment('adaptive', card)));
```

Leave `text` empty so the card is the only content. To combine text and a card, pass text to the constructor: `new MessageActivity('Heads up:')`.

## Common pitfalls

- **`Action.Submit` does not fire a `card.action.*` handler** — make sure you sent the card with `cardAttachment('adaptive', card)`, not as raw JSON.
- **Inputs missing from the submission** — every input needs an `id`. Without it, the value is dropped.
- **Card renders blank** — the schema requires `version`; the builder sets it automatically, but `fromJSON` from a hand-written object may omit it.
- **`ChoiceSetInput` shows the wrong default** — pass `.withValue('eng')` to preselect; `Choice.value` is the wire value, not the label.
