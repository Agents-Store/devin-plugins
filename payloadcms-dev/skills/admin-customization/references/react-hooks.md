# PayloadCMS — Admin React Hooks

All hooks import from `@payloadcms/ui` and run **only in Client Components** (`'use client'`). They give custom components access to form state, the active document, config, auth, and UI context — without prop-drilling.

```tsx
import { useField, useFormFields, useDocumentInfo } from '@payloadcms/ui'
```

## Form & Field State

| Hook | Returns | Use for |
| --- | --- | --- |
| `useField({ path })` | `{ value, setValue, errorMessage, showError, formProcessing, readOnly, ... }` | Building a custom `Field` component — read/write a single field's value |
| `useFormFields(selector)` | The slice you select; only re-renders when it changes | Reading one or a few other fields reactively |
| `useAllFormFields()` | `[fields, dispatchFields]` — all form state + dispatcher | Reading/updating many fields at once |
| `useForm()` | `{ submit, validateForm, getFields, getData, getSiblingData, reset, setModified, dispatchFields }` | Programmatic submit / validation / reset |
| `useDocumentForm()` | Same as `useForm` but the **top-level** document form | Reaching the doc form from inside a nested block/array |
| `useFormModified()` | `boolean` | Showing unsaved-changes UI |

```tsx
// A custom Field component
'use client'
import { useField } from '@payloadcms/ui'

export default function SlugField({ path }: { path: string }) {
  const { value, setValue, errorMessage, showError } = useField<string>({ path })
  return (
    <div>
      <input value={value ?? ''} onChange={(e) => setValue(e.target.value)} />
      {showError && <span className="error">{errorMessage}</span>}
    </div>
  )
}
```

```tsx
// Reacting to another field with a selector (efficient — re-renders only on change)
const title = useFormFields(([fields]) => fields.title?.value)

// Updating a sibling field via dispatch
const dispatch = useFormFields(([, dispatch]) => dispatch)
dispatch({ type: 'UPDATE', path: 'slug', value: slugify(title) })
```

## Document & List Context

| Hook | Returns | Use for |
| --- | --- | --- |
| `useDocumentInfo()` | `{ id, collectionSlug, globalSlug, apiURL, docPermissions, initialData, title, isEditing, savedDocumentData, ... }` | Knowing which doc/collection you're editing |
| `useDocumentEvents()` | `{ mostRecentUpdate, reportUpdate }` | Cross-document update notifications |
| `useListQuery()` | `{ data, query, handlePageChange, handleSearchChange, handleSortChange, refineListData, modified }` | Custom List View controls |
| `useSelection()` | `{ count, selected, toggleAll, selectAll, totalDocs }` | Bulk-selection UI in the List View |
| `useTableColumns()` | `{ columns, toggleColumn, moveColumn, setActiveColumns, resetColumnsState }` | Custom column management |

## Config, Auth & Locale

| Hook | Returns | Use for |
| --- | --- | --- |
| `useConfig()` | `{ config, getEntityConfig }` | Reading sanitized client config; `getEntityConfig({ collectionSlug })` |
| `useAuth()` | `{ user, token, permissions, logOut, refreshPermissions, refreshCookie }` | Reading the logged-in user / permissions |
| `useLocale()` | `{ code, label, rtl }` | Localized custom components |
| `useTranslation()` | `{ t, i18n }` | Translating custom UI strings |
| `useTheme()` | `{ theme, setTheme, autoMode }` | Light/dark-aware components |

```tsx
'use client'
import { useAuth, useConfig } from '@payloadcms/ui'

export default function AdminBadge() {
  const { user } = useAuth()
  const { config } = useConfig()
  return <span>{user?.email} @ {config.serverURL}</span>
}
```

## UI / Navigation Context

| Hook | Returns | Use for |
| --- | --- | --- |
| `useCollapsible()` | `{ isCollapsed, toggle, isVisible, isWithinCollapsible }` | Components inside a collapsible/array row |
| `useEditDepth()` | `number` (nesting depth, 0 at top level) | Detecting whether you're inside a document drawer |
| `useStepNav()` | `{ stepNav, setStepNav }` | Setting the breadcrumb trail of a custom view |
| `usePayloadAPI(url, options)` | `[{ data, isLoading, isError }, { setParams }]` | Fetching arbitrary REST data |
| `useRouteTransition()` | `{ startRouteTransition }` | Programmatic navigation with the loading indicator |

```tsx
// Fetch via the REST API inside a custom view
'use client'
import { usePayloadAPI } from '@payloadcms/ui'

export default function PopularPosts() {
  const [{ data, isLoading }] = usePayloadAPI('/api/posts', { initialParams: { sort: '-views', limit: 5 } })
  if (isLoading) return <p>Loading…</p>
  return <ul>{data?.docs?.map((d: any) => <li key={d.id}>{d.title}</li>)}</ul>
}
```

> Hooks are client-only. In a **Server Component** you have `payload` as a prop instead — call the Local API directly (e.g. `await payload.find({ collection: 'posts' })`) and pass results down.
