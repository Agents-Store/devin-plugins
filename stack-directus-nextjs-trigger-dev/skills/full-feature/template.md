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
| _Add background-task-output fields if step 5 applies:_ | | |
| `processing_status` | String (pending/processing/done/failed) | Mirrors the Trigger run state for UI display |
| `last_run_id` | String | Trigger.dev run handle ID for realtime subscription |

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
  processing_status?: 'pending' | 'processing' | 'done' | 'failed';
  last_run_id?: string | null;
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
      fields: ['id', 'title', 'slug', 'date_created', 'processing_status'],
    })
  );

  return (
    <main>
      <h1>{{Feature Name}}</h1>
      <ul>
        {items.map((item) => (
          <li key={item.id}>
            <a href={`/{{route}}/${item.slug}`}>{item.title}</a>
            {item.processing_status === 'processing' && <span> (processing...)</span>}
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
import { tasks } from '@trigger.dev/sdk/v3';
import type { {{featureName}}Task } from '@/trigger/{{feature_name}}';

export async function create{{TypeName}}(formData: FormData) {
  // 1. Create the item in Directus
  const item = await directus.request(
    createItem('{{collection_name}}', {
      title: formData.get('title') as string,
      slug: formData.get('slug') as string,
      status: 'draft',
      processing_status: 'pending',
    })
  );

  // 2. If the feature needs background work, kick off the task (step 5)
  const handle = await tasks.trigger<typeof {{featureName}}Task>(
    '{{feature_name}}',
    { itemId: item.id }
  );

  // 3. Store the run handle for realtime UI
  await directus.request(
    updateItem('{{collection_name}}', item.id, {
      last_run_id: handle.id,
      processing_status: 'processing',
    })
  );

  revalidatePath('/{{route}}');
  return { itemId: item.id, runId: handle.id };
}
```

## Step 5: Background Work (if step 4 triggered a task)

Create `trigger/{{feature_name}}.ts`:

```typescript
import { task } from '@trigger.dev/sdk/v3';
import { createDirectus, rest, staticToken, readItem, updateItem } from '@directus/sdk';
import type { Schema } from '@/types/directus';

export const {{featureName}}Task = task({
  id: '{{feature_name}}',
  maxDuration: 600, // 10 minutes max
  retry: {
    maxAttempts: 3,
    factor: 2,
    minTimeoutInMs: 1000,
    maxTimeoutInMs: 30000,
  },
  run: async (payload: { itemId: string }, { ctx }) => {
    // Build a server-side Directus client inside the task
    const directus = createDirectus<Schema>(process.env.NEXT_PUBLIC_DIRECTUS_URL!)
      .with(staticToken(process.env.DIRECTUS_ADMIN_TOKEN!))
      .with(rest({ cache: 'no-store' }));

    // 1. Fetch the item
    const item = await directus.request(readItem('{{collection_name}}', payload.itemId));

    // 2. Do the slow/flaky work
    // ... call an LLM, external API, image transformer, email service, etc.
    const result = await doTheSlowThing(item);

    // 3. Write results back to Directus
    await directus.request(
      updateItem('{{collection_name}}', payload.itemId, {
        // feature-specific result fields
        processing_status: 'done',
      })
    );

    // 4. Close the loop — revalidate the Next.js cache
    await fetch(`${process.env.NEXT_PUBLIC_SITE_URL}/api/revalidate?secret=${process.env.REVALIDATION_SECRET}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ collection: '{{collection_name}}' }),
    });

    return { itemId: payload.itemId, ok: true };
  },
});

async function doTheSlowThing(item: unknown): Promise<unknown> {
  // Replace with the actual work
  return {};
}
```

**Error handling:** if the task throws, Trigger retries per the `retry` config. On final failure, add a `catchError` hook to mark `processing_status: 'failed'` in Directus so the UI can show the error state.

**Idempotency:** if the Server Action can be called twice for the same item, pass `idempotencyKey: 'feature-${item.id}'` to `tasks.trigger()` in step 4.

## Step 6: Verify

- [ ] Listing page at `/{{route}}` renders published items from Directus
- [ ] Detail page at `/{{route}}/[slug]` loads with all fields
- [ ] Images render correctly via `next/image` (if applicable)
- [ ] SEO metadata appears in page source (`generateMetadata`)
- [ ] Create/update forms work (if mutations added)
- [ ] Server Action returns immediately — UI is not blocked on the slow work
- [ ] Trigger.dev dashboard shows the task run with `processing` → `done` transitions
- [ ] `processing_status` in Directus transitions through `pending` → `processing` → `done`
- [ ] Next.js page reflects the updated Directus data without manual refresh (revalidation fires)
- [ ] Cache revalidation triggers after mutations AND after task completion
- [ ] Non-existent slugs show 404 (`notFound()`)
- [ ] Failing tasks retry the configured number of times, then mark the item failed
