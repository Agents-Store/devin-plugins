# Feature Template: {{FEATURE_NAME}}

## Step 1: Data Model (Directus)

Create the collection and fields in Directus:

**Collection:** `{{collection_name}}`

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID (auto) | Primary key |
| `status` | String (dropdown: draft/published/archived) | Content workflow |
| `sort` | Integer | Optional ordering |
| `date_created` | Timestamp (auto) | System field |
| `date_updated` | Timestamp (auto) | System field |
| `title` | String | |
| `slug` | String (unique) | URL-friendly identifier |
| _Add feature-specific fields below_ | | |

**Relations (if any):**
- M2O: `{{collection_name}}.author` → `directus_users`
- M2M: `{{collection_name}}` ↔ `categories` (junction: `{{collection_name}}_categories`)

**Permissions:** Grant the API token role read access to the new collection. Grant write access if mutations are needed.

**Sample data:** Create 3-5 sample items with status "published" for testing.

## Step 2: TypeScript Types

Add to `types/directus.ts`:

```typescript
export interface {{TypeName}} {
  id: string;
  status: 'draft' | 'published' | 'archived';
  sort: number | null;
  date_created: string;
  date_updated: string;
  title: string;
  slug: string;
  // Add feature-specific fields
}

// Update the Schema interface:
export interface Schema {
  // ... existing collections
  {{collection_name}}: {{TypeName}}[];
}
```

## Step 3: Next.js Pages

### Listing Page

Create `app/{{route}}/page.tsx`:

```typescript
import directus from '@/lib/directus';
import { readItems } from '@directus/sdk';

export const revalidate = 60;

export default async function {{PageName}}Page() {
  const items = await directus.request(
    readItems('{{collection_name}}', {
      filter: { status: { _eq: 'published' } },
      sort: ['-date_created'],
      fields: ['id', 'title', 'slug', 'date_created'],
    })
  );

  return (
    <main>
      <h1>{{Feature Name}}</h1>
      <ul>
        {items.map((item) => (
          <li key={item.id}>
            <a href={`/{{route}}/${item.slug}`}>{item.title}</a>
          </li>
        ))}
      </ul>
    </main>
  );
}
```

### Detail Page

Create `app/{{route}}/[slug]/page.tsx`:

```typescript
import directus from '@/lib/directus';
import { readItems } from '@directus/sdk';
import { notFound } from 'next/navigation';

export async function generateStaticParams() {
  const items = await directus.request(
    readItems('{{collection_name}}', {
      filter: { status: { _eq: 'published' } },
      fields: ['slug'],
    })
  );
  return items.map((item) => ({ slug: item.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const [item] = await directus.request(
    readItems('{{collection_name}}', {
      filter: { slug: { _eq: slug } },
      fields: ['title'],
      limit: 1,
    })
  );
  if (!item) return {};
  return { title: item.title };
}

export default async function {{DetailPageName}}({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const [item] = await directus.request(
    readItems('{{collection_name}}', {
      filter: { slug: { _eq: slug } },
      fields: ['*'],
      limit: 1,
    })
  );

  if (!item) notFound();

  return (
    <main>
      <h1>{item.title}</h1>
      {/* Render feature-specific content */}
    </main>
  );
}
```

## Step 4: Mutations (if needed)

Create `app/{{route}}/actions.ts`:

```typescript
'use server';
import directus from '@/lib/directus';
import { createItem, updateItem } from '@directus/sdk';
import { revalidatePath } from 'next/cache';

export async function create{{TypeName}}(formData: FormData) {
  await directus.request(
    createItem('{{collection_name}}', {
      title: formData.get('title') as string,
      slug: formData.get('slug') as string,
      status: 'draft',
      // Add feature-specific fields
    })
  );
  revalidatePath('/{{route}}');
}

export async function update{{TypeName}}(id: string, formData: FormData) {
  await directus.request(
    updateItem('{{collection_name}}', id, {
      title: formData.get('title') as string,
      // Add feature-specific fields
    })
  );
  revalidatePath('/{{route}}');
}
```

## Step 5: Verify

- [ ] Listing page at `/{{route}}` renders published items from Directus
- [ ] Detail page at `/{{route}}/[slug]` loads with all fields
- [ ] Images render correctly via `next/image` (if applicable)
- [ ] SEO metadata appears in page source (`generateMetadata`)
- [ ] Create/update forms work (if mutations added)
- [ ] Cache revalidation triggers after mutations
- [ ] Non-existent slugs show 404 (`notFound()`)
