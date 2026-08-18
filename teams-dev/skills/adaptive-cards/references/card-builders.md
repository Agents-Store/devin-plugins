# Adaptive Card builders — reference

Every builder in `@microsoft/teams.cards` follows the same conventions:

- `new ClassName(positionalRequired, …)` for the small set of required values (id, text, url).
- `.withFoo(value)` chainable mutators for optional properties.
- `.addBar(child)` chainable mutators for child elements.
- `.toJSON()` returns the raw Adaptive Card JSON the schema expects.

The shapes below mirror the Adaptive Card 1.5+ schema; see the [Adaptive Cards schema](https://adaptivecards.io/explorer/) for the underlying contract.

## Root

| Builder | Constructor |
|---|---|
| `AdaptiveCard` | `new AdaptiveCard()` |
| `AdaptiveCard.fromJSON(json)` | wrap a hand-written or designer-exported card |

Common mutators: `.addBody(child)`, `.addActions(action, …)`, `.withVersion('1.5')`, `.withSpeak(text)`, `.withRefresh({ action, userIds })`, `.withSelectAction(action)`.

## Display elements

| Builder | Constructor | Common mutators |
|---|---|---|
| `TextBlock` | `new TextBlock(text)` | `.withWeight('Default'\|'Lighter'\|'Bolder')`, `.withSize('Small'\|'Default'\|'Medium'\|'Large'\|'ExtraLarge')`, `.withColor('Default'\|'Accent'\|'Good'\|'Warning'\|'Attention')`, `.withWrap()`, `.withMaxLines(n)` |
| `RichTextBlock` | `new RichTextBlock()` | `.addInline(TextRun)` |
| `TextRun` | `new TextRun(text)` | `.withWeight(...)`, `.withColor(...)`, `.withItalic()`, `.withStrikethrough()` |
| `Image` | `new Image(url)` | `.withSize('Auto'\|'Small'\|'Medium'\|'Large')`, `.withStyle('Default'\|'Person')`, `.withSelectAction(action)` |
| `Media` | `new Media()` | `.addSource(url, mimeType)`, `.withPoster(url)` |
| `FactSet` | `new FactSet()` | `.addFact(new Fact(title, value))` |

## Inputs (always require an `id`)

| Builder | Constructor | Key mutators |
|---|---|---|
| `TextInput` | `new TextInput(id)` | `.withPlaceholder(...)`, `.withIsMultiline()`, `.withIsRequired()`, `.withMaxLength(n)`, `.withValue(default)` |
| `NumberInput` | `new NumberInput(id)` | `.withMin(n)`, `.withMax(n)`, `.withValue(n)` |
| `DateInput` | `new DateInput(id)` | `.withMin(date)`, `.withMax(date)`, `.withValue(date)` |
| `TimeInput` | `new TimeInput(id)` | `.withMin(t)`, `.withMax(t)`, `.withValue(t)` |
| `ToggleInput` | `new ToggleInput(id, title)` | `.withValueOn('yes')`, `.withValueOff('no')` |
| `ChoiceSetInput` | `new ChoiceSetInput(id)` | `.withChoices([Choice, …])`, `.withStyle('compact'\|'expanded')`, `.withIsMultiSelect()` |
| `Choice` | `new Choice(title, value)` | — |

## Actions

| Builder | Constructor | Notes |
|---|---|---|
| `SubmitAction` | `new SubmitAction()` | Generic submit; fires `card.action` if you set a verb, else falls back to legacy invoke |
| `ExecuteAction` | `new ExecuteAction(verb)` | Adaptive Cards 1.4+; fires `card.action.<verb>` |
| `OpenUrlAction` | `new OpenUrlAction(url)` | Browser open |
| `ToggleVisibilityAction` | `new ToggleVisibilityAction()` | `.withTargetElements([id])` |
| `ShowCardAction` | `new ShowCardAction(card)` | Inline expansion |

All actions support `.withTitle(label)`, `.withIconUrl(url)`, `.withStyle('default'\|'positive'\|'destructive')`, `.withData(obj)`.

## Containers

| Builder | Constructor | Key mutators |
|---|---|---|
| `Container` | `new Container()` | `.addItem(child)`, `.withStyle('default'\|'emphasis'\|'accent'\|'good'\|'warning'\|'attention')` |
| `ColumnSet` | `new ColumnSet()` | `.addColumn(Column)` |
| `Column` | `new Column()` | `.addItem(child)`, `.withWidth('auto'\|'stretch'\|number)` |
| `ActionSet` | `new ActionSet()` | `.addAction(action)` |

## Best practices

- Always set an `id` on inputs; the value will not appear in the submission without one.
- Use `ExecuteAction` over `SubmitAction` for new cards — it interoperates cleanly with `app.on('card.action.<verb>', …)`.
- For long forms, group inputs in `Container.withStyle('emphasis')` to break up the visual flow.
- Mix designer-authored JSON with builder calls via `AdaptiveCard.fromJSON(...)` followed by `.addActions(...)` — best of both worlds.
- Wrap user-provided text in `TextBlock` with `.withWrap()` — without it, long strings clip.

## Sending

```ts
import { cardAttachment } from '@microsoft/teams.api';
import { MessageActivity } from '@microsoft/teams.api';

await send(new MessageActivity().addAttachment(cardAttachment('adaptive', card)));
```

For a text + card combo: `new MessageActivity('Here is your form:').addAttachment(...)`.
