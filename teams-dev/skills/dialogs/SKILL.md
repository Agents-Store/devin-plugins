---
name: dialogs
description: Use this skill when the user is building task module dialogs in Microsoft Teams — opening a modal from an Adaptive Card button, handling `dialog.open.<id>` and `dialog.submit.<id>`, returning a card or a web page as the dialog body, or chaining a multi-step dialog flow. Triggers on "Teams dialog", "task module", "modal in Teams", "dialog.open", "dialog.submit".
---

# Dialogs (Task Modules)

A dialog is a modal pop-up the Teams client opens on top of a chat. It receives input, then closes and returns control. The Teams SDK supports two body types: an Adaptive Card or a static web page.

## 1. Trigger a dialog from a card

```ts
import { AdaptiveCard, TextBlock, ExecuteAction } from '@microsoft/teams.cards';
import { OpenDialogData } from '@microsoft/teams.api';

const card = new AdaptiveCard()
  .addBody(new TextBlock('Need details? Open the form.'))
  .addActions(
    new ExecuteAction('open_form')
      .withTitle('Open form')
      .withData(new OpenDialogData('signup_form')),
  );
```

`OpenDialogData('<id>')` is the magic key. When the user clicks, Teams invokes `dialog.open.signup_form` on the bot.

## 2. Handle `dialog.open.<id>` — return a card-based dialog

```ts
import { AdaptiveCard, TextBlock, TextInput, SubmitAction } from '@microsoft/teams.cards';

app.on('dialog.open.signup_form', async ({ activity }) => {
  const card = new AdaptiveCard()
    .addBody(new TextBlock('Sign up').withWeight('Bolder'))
    .addBody(new TextInput('email').withIsRequired())
    .addActions(new SubmitAction().withTitle('Submit'));

  return {
    task: {
      type: 'continue',
      value: {
        title: 'Sign up',
        height: 200,
        width: 400,
        card: { contentType: 'application/vnd.microsoft.card.adaptive', content: card.toJSON() },
      },
    },
  };
});
```

Returning the task envelope is what tells Teams to render the dialog. `type: 'continue'` keeps the dialog open; `type: 'message'` closes it and posts a final message.

## 3. Handle `dialog.submit.<id>` — collect the result

```ts
app.on('dialog.submit.signup_form', async ({ activity, send }) => {
  const data = activity.value.data as { email: string };
  await persist(data);
  await send(`Signed up: ${data.email}`);
  return { task: { type: 'message', value: 'Thanks!' } };
});
```

The submission carries the input values keyed by their `id`. Return:
- `type: 'message'` to close the dialog with a final toast.
- `type: 'continue'` to swap the dialog body (multi-step wizards).

## 4. Web-page dialogs

For richer UIs (your own React/Vue page), serve a static URL and reference it instead of a card:

```ts
app.on('dialog.open.profile_editor', async () => ({
  task: {
    type: 'continue',
    value: {
      title: 'Edit profile',
      height: 600,
      width: 800,
      url: 'https://yourapp.example.com/profile',
      fallbackUrl: 'https://yourapp.example.com/profile',
    },
  },
}));
```

The page uses `@microsoft/teams.client` to call `microsoftTeams.dialog.url.submit({ ... })` from the browser, which fires `dialog.submit.<id>` on the bot. See `tabs` for client-side SDK details.

## 5. Multi-step dialogs

Return another `continue` from `dialog.submit.<id>` to swap the body without closing:

```ts
app.on('dialog.submit.signup_form', async ({ activity }) => {
  if (!isComplete(activity.value.data)) {
    return {
      task: {
        type: 'continue',
        value: { title: 'One more thing', card: { contentType: '…', content: nextStepCard.toJSON() } },
      },
    };
  }
  return { task: { type: 'message', value: 'Done!' } };
});
```

## Manifest

The bot must declare the dialog domain in `appPackage/manifest.json`:

```jsonc
{
  "validDomains": ["yourapp.example.com"],
  "webApplicationInfo": {
    "id": "<AAD app id>",
    "resource": "api://yourapp.example.com/<AAD app id>"
  }
}
```

Web-page dialogs without a `validDomains` entry are rejected by the Teams client.

## Common pitfalls

- **Dialog never opens** — `OpenDialogData` was attached to the wrong action type, or the action button was sent without `cardAttachment('adaptive', card)`.
- **Submit hits nothing** — handler is `dialog.submit.<id>` (with the same id as `OpenDialogData(<id>)`). A bare `dialog.submit` matches every id but won't run before a specific handler.
- **Webpage dialog 404s** — the URL is missing from `validDomains`.
- **Dialog body is blank** — the returned task envelope is missing `task.value.card.content` or `task.value.url`.
