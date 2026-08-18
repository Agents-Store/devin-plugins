# PayloadCMS — Custom Component Slot Catalog

Every slot below takes a **string path** (`'/components/Foo#Named'` or `'/components/Foo'` for a default export), an **array of paths** (for `before*`/`after*` multi-slots), or a **config object** `{ path, exportName?, clientProps?, serverProps? }`. After adding any component, register it in the import map — run `payload generate:importmap` (see the `setup` / `cli-recipes` skills). Components are **Server Components by default**; add `'use client'` to make them Client Components.

All components receive `payload` (the Payload instance) and `i18n` as default props. Server Components can run Local API queries directly; Client Components use hooks (see `references/react-hooks.md`).

---

## Root-Level Slots — `config.admin.components`

| Slot | Config key | Renders | Type |
| --- | --- | --- | --- |
| Nav | `Nav` | The entire sidebar / mobile menu | single |
| Logo | `graphics.Logo` | Full logo on the Login view | single |
| Icon | `graphics.Icon` | Simplified logo used in the `Nav` | single |
| Logout button | `logout.Button` | The sidebar logout button | single |
| Avatar | `config.admin.avatar` | Account avatar (`'gravatar'`, `'default'`, or `{ Component }`) | single |
| Header | `header` | Banner above the Payload header (announcements, notices) | array |
| Actions | `actions` | Buttons rendered inside the Admin Panel header | array |
| Before dashboard | `beforeDashboard` | Components before the default dashboard content | array |
| After dashboard | `afterDashboard` | Components after the default dashboard content | array |
| Dashboard widgets | `config.admin.dashboard.widgets` | Modular dashboard widget cards (`{ Component }[]`); built-in collections widget auto-included when no `defaultLayout` is defined | array |
| Before login | `beforeLogin` | Components above the login form | array |
| After login | `afterLogin` | Components below the login form | array |
| Before nav links | `beforeNavLinks` | Components above the nav links | array |
| After nav links | `afterNavLinks` | Components below the nav links (great for custom-view links) | array |
| Settings menu | `settingsMenu` | Items in the gear-icon popup above logout | array |
| Providers | `providers` | React Context providers wrapping the whole Admin Panel | array |
| Views | `views` | Override built-in views or register new root views | object |

```ts
// payload.config.ts
admin: {
  avatar: { Component: '@/components/Avatar' },
  components: {
    graphics: { Logo: '@/components/Logo', Icon: '@/components/Icon' },
    Nav: '@/components/Nav',
    logout: { Button: '@/components/LogoutButton' },
    actions: ['@/components/PublishAll'],
    header: ['@/components/EnvBanner'],
    beforeDashboard: ['@/components/WelcomeWidget'],
    afterNavLinks: ['@/components/ReportsNavLink'],
    providers: ['@/providers/MyContext'],
  },
}
```

Custom Context providers wrap the panel and must render `children`:

```tsx
// src/providers/MyContext.tsx
'use client'
import React, { createContext, useContext } from 'react'

const Ctx = createContext({ tenant: 'default' })
export const useTenant = () => useContext(Ctx)

export default function MyContext({ children }: { children: React.ReactNode }) {
  return <Ctx.Provider value={{ tenant: 'acme' }}>{children}</Ctx.Provider>
}
```

---

## Custom Views — `config.admin.components.views`

A new key adds a brand-new root view with its own route. Add a nav link via `afterNavLinks`.

| Property | Purpose |
| --- | --- |
| `Component` | Path to the view component (required) |
| `path` | URL route, must start with `/` (required for new views) |
| `exact` | Match the exact path only |
| `strict` | Require trailing-slash matching |
| `sensitive` | Case-sensitive matching |
| `meta` | Per-view metadata override (title, description) |

```ts
admin: {
  components: {
    views: {
      reports: {
        Component: '@/views/Reports',
        path: '/reports',
        exact: true,
        meta: { title: 'Reports' },
      },
    },
  },
}
```

Root views receive **`AdminViewServerProps`** (`req`, `payload`, `permissions`, `initPageResult`, `params`, `searchParams`, etc.).

---

## Collection Edit-View Slots — `collection.admin.components.edit`

| Slot | Purpose |
| --- | --- |
| `SaveButton` | Save the current document |
| `SaveDraftButton` | Save as draft |
| `PublishButton` | Publish |
| `UnpublishButton` | Unpublish |
| `PreviewButton` | Open the preview |
| `Description` | Collection description (shared with the List View) |
| `Upload` | Custom file-upload UI (upload collections only) |
| `beforeDocumentControls` | Array — components rendered before the default document controls |
| `editMenuItems` | Array — items injected into the 3-dot edit menu (use `PopupList.Button` from `@payloadcms/ui`) |

```ts
// Posts collection
admin: {
  components: {
    edit: {
      SaveButton: '@/components/MySaveButton',
      beforeDocumentControls: ['@/components/StatusBadge'],
    },
  },
}
```

Globals use **`admin.components.elements`** with the same slots (no `Upload`).

Each slot receives a typed prop pair, e.g. `SaveButtonServerProps` / `SaveButtonClientProps`. Reuse `@payloadcms/ui` exports (`SaveButton`, `PublishButton`, `Upload`) to keep default styling.

### Full edit-view override — `collection.admin.components.views.edit`

```ts
admin: {
  components: {
    views: {
      edit: {
        default: { Component: '@/views/CustomEdit' },        // replaces the form area
        // versions, version, api are also overridable here
        myTab: {                                             // custom document tab
          Component: '@/views/AuditTab',
          path: '/audit',
          tab: { label: 'Audit', href: '/audit' },
        },
      },
    },
  },
}
```

Document views receive **`DocumentViewServerProps`** / `DocumentViewClientProps` (`doc`, `collectionConfig`, `docPermissions`, `initPageResult`, etc.).

---

## Collection List-View Slots — `collection.admin.components`

| Slot | Purpose |
| --- | --- |
| `beforeList` | Array — before the documents list |
| `beforeListTable` | Array — before the table |
| `afterList` | Array — after the documents list |
| `afterListTable` | Array — after the table |
| `Description` | Collection description (shared with the Edit View) |

### Full list-view override — `views.list`

```ts
admin: { components: { views: { list: { Component: '@/views/CustomList' } } } }
```

List views render inside a `ListQueryProvider`. Wrap `DefaultListView` from `@payloadcms/ui` to keep the built-in table:

```tsx
'use client'
import { DefaultListView } from '@payloadcms/ui'
import type { ListViewClientProps } from 'payload'

export default function CustomList(props: ListViewClientProps) {
  return (<div><h1>My Header</h1><DefaultListView {...props} /></div>)
}
```

**`ListViewServerProps`**: `collectionConfig`, `data`, `limit`, `listPreferences`, `listSearchableFields`, `i18n`, `locale`, `params`, `payload`, `permissions`, `searchParams`, `user`.
**`ListViewClientProps`**: `collectionSlug`, `columnState`, `enableRowSelections`, `hasCreatePermission`, `hasDeletePermission`, `Table`, `BeforeList`, `AfterList`, etc.

---

## Field-Level Slots — `field.admin.components`

| Slot | Renders | Type |
| --- | --- | --- |
| `Field` | The form field in the Edit View | single |
| `Cell` | The List View table cell for this field | single |
| `Label` | Wherever the field's label appears | single |
| `Description` | The field's helper text | single |
| `Error` | Shown when validation fails | single |
| `Filter` | Input in the List View "Filter By" dropdown | single |
| `beforeInput` | Components before the input element | array |
| `afterInput` | Components after the input element | array |
| `RowLabel` | (array field only) custom label per row | single |

**Field component props** (`field`, `path`, `schemaPath`, `indexPath`, `readOnly`, `locale`, `user`, `validate`, `docPreferences`). Server-only additions: `clientField`, `data`, `i18n`, `payload`, `permissions`, `siblingData`, `value`.

**Cell component props** (`DefaultCellComponentProps`): `cellData`, `rowData`, `field`, `collectionSlug`, `columnIndex`, `link`, `linkURL`, `onClick`, `customCellProps`, `viewType`, `className`.

```ts
// On a field definition
{
  name: 'price',
  type: 'number',
  admin: {
    components: {
      Field: '@/fields/PriceField',
      Cell: '@/fields/PriceCell',
      afterInput: ['@/fields/CurrencyHint'],
    },
  },
}
```
