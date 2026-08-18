# Scenario — Adaptive Card form

A bot that posts a sign-up card. The user fills the fields, clicks **Save**, and the bot acknowledges the submission.

## Steps

```bash
teams project new typescript card-form --template echo
cd card-form
npm install
```

Edit `src/index.ts`:

```ts
import { App } from '@microsoft/teams.apps';
import { DevtoolsPlugin } from '@microsoft/teams.dev';
import {
  AdaptiveCard,
  TextBlock,
  TextInput,
  ChoiceSetInput,
  Choice,
  ExecuteAction,
} from '@microsoft/teams.cards';
import { MessageActivity, cardAttachment } from '@microsoft/teams.api';

const buildForm = () =>
  new AdaptiveCard()
    .addBody(new TextBlock('Sign up').withWeight('Bolder').withSize('Large'))
    .addBody(
      new TextInput('email')
        .withPlaceholder('you@example.com')
        .withIsRequired(),
    )
    .addBody(
      new ChoiceSetInput('role')
        .withChoices([
          new Choice('Engineer', 'eng'),
          new Choice('Designer', 'design'),
          new Choice('Product', 'pm'),
        ])
        .withStyle('compact')
        .withValue('eng'),
    )
    .addActions(
      new ExecuteAction('save').withTitle('Save').withStyle('positive'),
    );

const app = new App({
  plugins: [new DevtoolsPlugin()],
});

app.on('message', async ({ send }) => {
  await send(
    new MessageActivity('Please fill the form:').addAttachment(
      cardAttachment('adaptive', buildForm()),
    ),
  );
});

app.on('card.action.save', async ({ activity, send }) => {
  const data = activity.value as { email: string; role: string };
  await send(`Saved: ${data.email} (${data.role})`);
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

1. Send any message to the bot.
2. The bot posts a card with email + role inputs and a Save button.
3. Fill the email, leave the role default, click **Save**.
4. The bot replies with `Saved: <email> (eng)`.

DevTools shows three activities: inbound message, outbound card, inbound `card.action.save`.

## Common tweaks

- Validate the email in the handler with a regex before saving.
- Re-render the card on save with `Action.Execute({ data: { kind: 'refresh' } })` to give visual feedback.
- Convert the form into a dialog modal — see `dialogs` for the `dialog.open.<id>` + `dialog.submit.<id>` shape.
