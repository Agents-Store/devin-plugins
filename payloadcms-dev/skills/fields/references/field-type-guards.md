# Field Type Guards

Type narrowing utilities for runtime field inspection — useful inside hooks, custom components, and plugin code that iterates over `config.collections[*].fields[*]`.

## Why You Need Them

`Field` in Payload is a discriminated union across ~20 field types. To safely access `field.relationTo` or `field.fields`, narrow first:

```ts
import type { Field } from 'payload'

function processField(field: Field) {
  // Without narrowing, TS complains because not every Field has `.relationTo`
  // field.relationTo  // ❌ TS error
}
```

## Type Guard Functions

Payload exposes guards via `payload/shared`:

```ts
import {
  fieldHasSubFields,
  fieldIsArrayType,
  fieldIsBlockType,
  fieldIsGroupType,
  fieldIsLocalized,
  fieldIsPresentationalOnly,
  fieldIsVirtual,
  fieldAffectsData,
  tabHasName,
} from 'payload/shared'
```

| Guard | Narrows to | True when |
| --- | --- | --- |
| `fieldHasSubFields(field)` | `field.fields` exists | `array`, `blocks`, `group`, `collapsible`, `row`, `tabs` w/o name |
| `fieldIsArrayType(field)` | `ArrayField` | `type === 'array'` |
| `fieldIsBlockType(field)` | `BlocksField` | `type === 'blocks'` |
| `fieldIsGroupType(field)` | `GroupField` | `type === 'group'` |
| `fieldIsLocalized(field)` | `field.localized === true` | localization on |
| `fieldIsPresentationalOnly(field)` | `ui` / `row` / `collapsible` | No data |
| `fieldIsVirtual(field)` | `field.virtual === true` | virtual field |
| `fieldAffectsData(field)` | field has a `name` and stores data | not `row`/`collapsible`/`tabs` w/o name/`ui` |
| `tabHasName(tab)` | `tab.name` defined | tab nests data under a key |

## Common Patterns

### Recursive field walker

```ts
import type { Field } from 'payload'
import { fieldHasSubFields, fieldAffectsData } from 'payload/shared'

function walkFields(fields: Field[], fn: (field: Field, path: string[]) => void, path: string[] = []) {
  for (const field of fields) {
    const nextPath = fieldAffectsData(field) && 'name' in field
      ? [...path, field.name]
      : path

    fn(field, nextPath)

    if (fieldHasSubFields(field)) {
      walkFields(field.fields, fn, nextPath)
    }

    if (field.type === 'blocks') {
      for (const block of field.blocks) {
        walkFields(block.fields, fn, [...nextPath, block.slug])
      }
    }

    if (field.type === 'tabs') {
      for (const tab of field.tabs) {
        const tabPath = 'name' in tab && tab.name ? [...nextPath, tab.name] : nextPath
        walkFields(tab.fields, fn, tabPath)
      }
    }
  }
}
```

### Find all relationship fields

```ts
import type { Field, RelationshipField } from 'payload'

function getRelationshipFields(fields: Field[]): RelationshipField[] {
  const found: RelationshipField[] = []
  walkFields(fields, (f) => {
    if (f.type === 'relationship') found.push(f)
  })
  return found
}
```

### Narrow inside a hook

```ts
hooks: {
  beforeChange: [
    async ({ data, collection }) => {
      for (const field of collection.fields) {
        if (field.type === 'text' && field.required && !data?.[field.name]) {
          throw new Error(`Missing required text field: ${field.name}`)
        }
      }
      return data
    },
  ],
}
```

### Detect localized fields at runtime

```ts
import { fieldIsLocalized, fieldAffectsData } from 'payload/shared'

function getLocalizedFieldNames(fields: Field[]): string[] {
  return fields
    .filter((f) => fieldAffectsData(f) && fieldIsLocalized(f) && 'name' in f)
    .map((f) => (f as any).name)
}
```

### Type-safe block rendering (frontend)

```ts
type LayoutBlock = NonNullable<Page['layout']>[number]

function renderBlock(block: LayoutBlock) {
  switch (block.blockType) {
    case 'hero':
      return <Hero {...block} />          // TS knows shape
    case 'content':
      return <Content {...block} />
    case 'media':
      return <Media {...block} />
    default: {
      const _exhaustive: never = block    // Compile-time guard
      return null
    }
  }
}
```

## Where This Matters

- **Plugin development** — iterating over user collections to inject behavior.
- **Custom admin views** — rendering field-aware UI.
- **Migration scripts** — transforming data based on field shape.
- **Validation helpers** — generating runtime validators from config.

When working at this level always import from `payload/shared` (universal) — not `payload` (server-only) — so guards work in client components too.
