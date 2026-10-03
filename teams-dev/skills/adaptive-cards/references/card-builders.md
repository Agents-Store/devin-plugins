# Adaptive Card builders — reference (`@microsoft/teams.cards` 2.1)

Conventions shared by every element and action:

- Children are **constructor arguments** where the element holds a list: `new AdaptiveCard(...body)`, `new Container(...items)`, `new Column(...items)`, `new ActionSet(...actions)`, `new FactSet(...facts)`, `new ChoiceSetInput(...choices)`.
- Scalar content comes first, options second: `new TextBlock(text, options?)`, `new Image(url, options?)`, `new OpenUrlAction(url, options?)`, `new ToggleInput(title, options?)`, `new Fact(title, value)`.
- Elements without a mandatory scalar take only an options object: `new TextInput({ id, label, placeholder, … })`, `new NumberInput(options)`, `new ExecuteAction({ title })`, `new SubmitAction(options)`.
- Every option also has a chainable setter: `.withId()`, `.withLabel()`, `.withIsRequired()`, `.withStyle()`, … Setters return the element.
- Types are strict: an invalid enum value (`size: 'huge'`) is a compile error.
- The raw schema types are exported as `IAdaptiveCard`, `IExecuteAction`, `IOpenUrlAction`, … for hand-written JSON (`as const satisfies IOpenUrlAction`).

The shapes follow the Adaptive Cards 1.5+ schema; the [schema explorer](https://adaptivecards.io/explorer/) is the contract.

## Root

| Builder | Notes |
|---|---|
| `new AdaptiveCard(...body)` | The version is set for you. Setters: `.withBody(...elements)`, `.withActions(...actions)`, `.withVersion('1.5')`, `.withSpeak(text)`, `.withRefresh({ … })`, `.withSelectAction(action)`, `.withMinHeight()`, `.withBackgroundImage()`, `.withFallbackText()` |

## Display elements

| Builder | Constructor | Common setters |
|---|---|---|
| `TextBlock` | `(text, options?)` | `weight` (`Lighter`/`Default`/`Bolder`), `size` (`Small`…`ExtraLarge`), `color` (`Default`, `Accent`, `Good`, `Warning`, `Attention`, …), `wrap`, `maxLines`, `style` (`heading`), `spacing` |
| `RichTextBlock` | `(options?)` | `.withInlines(new TextRun(text, { italic: true }), …)` |
| `TextRun` | `(text, options?)` | `weight`, `color`, `italic`, `strikethrough`, `underline` |
| `Image` | `(url, options?)` | `size` (`Auto`, `Small`, `Medium`, `Large`), `style` (`Person`), `altText`, `.withSelectAction()` |
| `Media` | `(options?)` | `sources`, `poster` |
| `FactSet` | `(...facts)` | children are `new Fact('Status', 'open')` |
| `CodeBlock` | `(options?)` | `codeSnippet`, `language` |
| `Table` | `(options?)` | rows and columns per the schema |

## Inputs (each needs an id)

| Builder | Constructor | Common setters |
|---|---|---|
| `TextInput` | `(options?)` | `.withId()`, `.withLabel()`, `.withPlaceholder()`, `.withIsMultiline()`, `.withMaxLength()`, `.withValue()`, `.withIsRequired()`, `.withErrorMessage()` |
| `NumberInput` | `(options?)` | `.withMin()`, `.withMax()`, `.withValue()` |
| `DateInput` | `(options?)` | `.withMin()`, `.withMax()`, `.withValue('YYYY-MM-DD')` |
| `TimeInput` | `(options?)` | `.withMin()`, `.withMax()`, `.withValue('HH:mm')` |
| `ToggleInput` | `(title, options?)` | `.withValueOn()`, `.withValueOff()`, `.withValue()`; the submitted value is a string |
| `ChoiceSetInput` | `(...choices)` | choices are `{ title, value }` objects; `.withStyle('compact'\|'expanded'\|'filtered')`, `.withIsMultiSelect()`, `.withPlaceholder()` |

## Actions

| Builder | Constructor | Notes |
|---|---|---|
| `ExecuteAction` | `(options?)` | `Action.Execute`; routes to `card.action.<action>` through `.withData(new SubmitData('<action>'))`; `.withAssociatedInputs('auto')`; `.withVerb()` for universal-action verbs |
| `SubmitAction` | `(options?)` | `Action.Submit`; the one dialogs use: `.withData(new OpenDialogData('<id>'))` opens a dialog, `.withData(new SubmitData('<action>'))` submits one |
| `OpenUrlAction` | `(url, options?)` | opens in the browser |
| `ToggleVisibilityAction` | `(options?)` | `.withTargetElements([...])` |
| `ShowCardAction` | `(options?)` | `.withCard(card)` expands inline |

Shared setters: `.withTitle()`, `.withIconUrl()`, `.withStyle('default'|'positive'|'destructive')`, `.withMode()`, `.withTooltip()`, `.withIsEnabled()`.

`SubmitData` and `OpenDialogData` come from `@microsoft/teams.cards`. Both take the routing name first and optional static data second.

## Containers

| Builder | Constructor | Notes |
|---|---|---|
| `Container` | `(...items)` | `.withStyle('default'\|'emphasis'\|'accent'\|'good'\|'warning'\|'attention')`, `.withItems(...)`, `.withSelectAction()` |
| `ColumnSet` | `(options?)` | `.withColumns(...columns)` |
| `Column` | `(...items)` | `.withWidth('auto'\|'stretch'\|number)`, `.withItems(...)` |
| `ActionSet` | `(...actions)` | an inline row of actions inside the body |

## Practices

- Prefer `ExecuteAction` for new cards; it fits the `card.action.<action>` router and universal actions.
- Group long forms in `Container(...).withStyle('emphasis')` sections.
- Give user-provided text `wrap: true`; without it a long string clips.
- Keep one `SubmitData` name per action and one `card.action.<name>` handler per name.

## Sending

```ts
import { MessageActivityInput } from '@microsoft/teams.api';
import { AdaptiveCard, TextBlock } from '@microsoft/teams.cards';

app.on('message', async ({ send }) => {
  const card = new AdaptiveCard(new TextBlock('Your form:'));
  await send(card);                                                      // card only
  await send(new MessageActivityInput('Here is your form:').addCard('adaptive', card));   // text + card
});
```
