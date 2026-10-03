# Scenario — Adaptive Card form

A bot that posts a sign-up card. The user fills in the fields and clicks **Save**; the bot validates on the client, receives the values and acknowledges.

## 1. Scaffold

```bash
teams project new typescript card-form -t echo --yes
cd card-form
npm install @microsoft/teams.cards @microsoft/teams.api
```

Register the app as in `echo-bot.md` when you want to test in Teams.

## 2. The bot

Replace `src/index.ts`:

```ts
import { App } from '@microsoft/teams.apps';
import {
  ActionSet,
  AdaptiveCard,
  ChoiceSetInput,
  ExecuteAction,
  SubmitData,
  TextBlock,
  TextInput,
} from '@microsoft/teams.cards';

const buildForm = () =>
  new AdaptiveCard(
    new TextBlock('Sign up', { weight: 'Bolder', size: 'Large' }),
    new TextInput({ id: 'email', label: 'Email', placeholder: 'you@example.com' })
      .withIsRequired()
      .withErrorMessage('An email is required'),
    new ChoiceSetInput(
      { title: 'Engineer', value: 'eng' },
      { title: 'Designer', value: 'design' },
      { title: 'Product', value: 'pm' },
    )
      .withId('role')
      .withLabel('Role')
      .withStyle('compact')
      .withValue('eng'),
    new ActionSet(
      new ExecuteAction({ title: 'Save' })
        .withData(new SubmitData('save_signup'))
        .withAssociatedInputs('auto')      // collect and validate every input of the card
        .withStyle('positive'),
    ),
  );

const app = new App();

app.on('message', async ({ send }) => {
  await send(buildForm());
});

app.on('card.action.save_signup', async ({ activity, send }) => {
  const data = activity.value.action.data as { email: string; role: string };
  await send(`Saved: ${data.email} (${data.role})`);
  return {
    statusCode: 200,
    type: 'application/vnd.microsoft.activity.message',
    value: 'Saved',
  } as const;
});

app.start(process.env.PORT || 3978).catch(console.error);
```

## 3. Run and verify

```bash
DANGEROUSLY_ALLOW_UNAUTHENTICATED_REQUESTS=true npm run dev
agentsplayground -e http://localhost:3978/api/messages -c emulator
```

1. Send any message; the bot answers with the card.
2. Click **Save** with an empty email: the client blocks it and shows the error message.
3. Fill the email, keep the role default, click **Save**: the bot replies `Saved: <email> (eng)`.

The Playground shows the raw card JSON and the invoke the click produces; render fidelity is best judged in Teams.

## Common tweaks

- Re-render the card instead of sending a message: return `{ statusCode: 200, type: 'application/vnd.microsoft.card.adaptive', value: <card> }` from the handler.
- Turn the form into a dialog: put the same card into `dialog.open.<id>` (`dialogs`).
- Validate the email on the server too — client validation is a convenience, not a guarantee.
- Several actions on one card: one `SubmitData` name each, one `card.action.<name>` handler each (`adaptive-cards`).
