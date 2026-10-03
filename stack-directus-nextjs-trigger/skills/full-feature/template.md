# Feature Template: {{FEATURE_NAME}}

Placeholders: `{{collection_name}}` (Directus collection, also the cache tag), `{{TypeName}}`, `{{route}}`, `{{PageName}}`, `{{DetailPageName}}`, and for a task `{{feature_name}}` (kebab-case task id) and `{{featureName}}` (the exported constant).

## Step 1: Data Model (Directus)

Create the collection and fields in Directus:

**Collection:** `{{collection_name}}`

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID (auto) | Primary key |
| `status` | String (dropdown: draft/published/archived) | Content workflow, see the note below |
| `sort` | Integer | Optional ordering |
| `date_created` | Timestamp (auto) | System field |
| `date_updated` | Timestamp (auto) | System field |
| `title` | String | |
| `slug` | String (unique) | URL-friendly identifier |
| _Add feature-specific fields below_ | | |
| _Add these if step 5 applies:_ | | |
| `processing_status` | String (`pending` / `processing` / `done` / `failed`) | State of the task's work, for the UI |
| `last_run_id` | String | Trigger.dev run id, for the admin to find the run |
| `source_hash` | String | Hash of the source fields the result was made from; lets the task skip unchanged work |

Directus 12 gives a new collection a boolean `archived` field instead of a `status` dropdown. Both work. Pick one, and keep the type in Step 2 and the filters in Step 3 in line with it (`{ archived: { _eq: false } }` instead of `{ status: { _eq: 'published' } }`).

**Relations (if any):**
- M2O: `{{collection_name}}.author` → `authors` (a collection of your own; the SDK does not read `directus_users` through `readItems`)
- M2M: `{{collection_name}}` ↔ `categories` (junction: `{{collection_name}}_categories`, which belongs in `Schema`)

**Permissions:** Give the policy of the server token's user read access to the new collection and to every collection it expands. Writes (Step 4) are given to the policy of the *users who sign in* on the NextAuth path, because they write with their own token; keep the server token read-only. On the Better Auth path the server token's policy needs create and update, and your code decides who may call. A task (Step 5) has its **own** Directus user: give it read on the source fields and update on the result fields only (`processing_status`, `last_run_id`, `source_hash` and the output fields), never on the field the revalidation or job Flow watches. Give the Public policy nothing unless the browser reads the collection directly.

**Sample data:** Create 3-5 sample items that pass the published filter, for testing.

## Step 2: TypeScript Types

Add to `types/directus.ts`:

```typescript
// types/directus.ts
export interface {{TypeName}} {
  id: string;
  status: 'draft' | 'published' | 'archived';
  sort: number | null;
  date_created: string;
  date_updated: string;
  title: string;
  slug: string;
  // Add feature-specific fields
  // If step 5 applies:
  // processing_status: 'pending' | 'processing' | 'done' | 'failed' | null;
  // last_run_id: string | null;
  // source_hash: string | null;
}

// Update the Schema interface:
export interface Schema {
  // ... existing collections
  {{collection_name}}: {{TypeName}}[];
}
```

## Step 3: Reads and Pages

### Read functions

One module per collection. Every read carries the tag of each collection it reads, and sits inside `cache()` so `generateMetadata` and the page share one request (the `requestTagged` helper is described in `directus-to-nextjs`):

```typescript
// lib/content/{{collection_name}}.ts
import 'server-only';
import { cache } from 'react';
import { readItems } from '@directus/sdk';
import { requestTagged } from '@/lib/directus-tagged';

const TAGS = ['{{collection_name}}'];
const ONE_HOUR = 3600;

export const get{{TypeName}}List = cache(async () =>
  requestTagged(
    readItems('{{collection_name}}', {
      filter: { status: { _eq: 'published' } },
      sort: ['-date_created'],
      fields: ['id', 'title', 'slug', 'date_created'],
    }),
    TAGS,
    ONE_HOUR,
  ),
);

export const get{{TypeName}}Slugs = cache(async () => {
  const items = await requestTagged(
    readItems('{{collection_name}}', { filter: { status: { _eq: 'published' } }, fields: ['slug'], limit: -1 }),
    TAGS,
    ONE_HOUR,
  );
  return items.map((item) => item.slug);
});

export const get{{TypeName}}BySlug = cache(async (slug: string) => {
  const [item] = await requestTagged(
    readItems('{{collection_name}}', {
      filter: { slug: { _eq: slug }, status: { _eq: 'published' } },
      fields: ['*'],
      limit: 1,
    }),
    TAGS,
    ONE_HOUR,
  );
  return item ?? null;
});
```

With `cacheComponents: true` use `'use cache'`, `cacheTag('{{collection_name}}')` and `cacheLife('hours')` inside each function instead (see "Cache" in `directus-to-nextjs`).

### Listing Page

Create `app/{{route}}/page.tsx`:

```typescript
// app/{{route}}/page.tsx
import Link from 'next/link';
import { get{{TypeName}}List } from '@/lib/content/{{collection_name}}';

export default async function {{PageName}}Page() {
  const items = await get{{TypeName}}List();

  return (
    <main>
      <h1>{{Feature Name}}</h1>
      <ul>
        {items.map((item) => (
          <li key={item.id}>
            <Link href={`/{{route}}/${item.slug}`}>{item.title}</Link>
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
// app/{{route}}/[slug]/page.tsx
import { notFound } from 'next/navigation';
import { get{{TypeName}}BySlug, get{{TypeName}}Slugs } from '@/lib/content/{{collection_name}}';

export async function generateStaticParams() {
  const slugs = await get{{TypeName}}Slugs();
  return slugs.map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const item = await get{{TypeName}}BySlug(slug);
  return item ? { title: item.title } : {};
}

export default async function {{DetailPageName}}({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const item = await get{{TypeName}}BySlug(slug);
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

A Server Action is a public endpoint and anyone can call it with any id, so authenticate **and** authorize. On the NextAuth path the write carries the signed-in user's own token (`withToken`), and Directus applies that user's policies: a user without update permission on the item gets `403`. On the Better Auth path there is no user token: write with the server token, and check role or ownership in code first (`if (session.user.role !== 'editor') throw new Error('Forbidden')`), never skip it. Validate `formData` (Zod, see `form-handling` in `nextjs-dev`) before writing, then expire the tag.

Create `app/{{route}}/actions.ts`:

```typescript
// app/{{route}}/actions.ts
'use server';
import { createItem, updateItem, withToken } from '@directus/sdk';
import { updateTag } from 'next/cache';
import directus from '@/lib/directus';
import { requireUser } from '@/lib/session';

export async function create{{TypeName}}(formData: FormData) {
  const session = await requireUser(); // authenticate
  await directus.request(
    withToken( // authorize: Directus checks the user's own policies
      session.accessToken,
      createItem('{{collection_name}}', {
        title: String(formData.get('title') ?? ''),
        slug: String(formData.get('slug') ?? ''),
        status: 'draft',
        // Add feature-specific fields
      }),
    ),
  );
  updateTag('{{collection_name}}');
}

export async function update{{TypeName}}(id: string, formData: FormData) {
  const session = await requireUser();
  await directus.request(
    withToken(
      session.accessToken,
      updateItem('{{collection_name}}', id, {
        title: String(formData.get('title') ?? ''),
        // Add feature-specific fields
      }),
    ),
  );
  updateTag('{{collection_name}}');
}
```

## Step 5: Background Work (if needed)

Skip this step unless `SKILL.md` ("Decide: Does This Feature Need a Task?") said yes. A task is started in one of three ways: by a Server Action (below), by a Directus Flow through the receiver (`directus-to-trigger`), or by a schedule (`trigger-dev` → `scheduled-tasks`).

### Start it from a Server Action

Add to `app/{{route}}/actions.ts`. The action authenticates and authorizes first, exactly as in Step 4, then starts the task with **ids**, never a token or a copy of the item:

```typescript
// app/{{route}}/actions.ts (continued)
import { tasks } from '@trigger.dev/sdk';
import type { {{featureName}} } from '@/trigger/{{feature_name}}'; // a type import: no task code in the Next.js bundle

export async function start{{TypeName}}Job(id: string) {
  const session = await requireUser(); // authenticate
  await directus.request(
    withToken( // authorize: the user's own token must be allowed this small write
      session.accessToken,
      updateItem('{{collection_name}}', id, { processing_status: 'pending' }),
    ),
  );

  const handle = await tasks.trigger<typeof {{featureName}}>(
    '{{feature_name}}',
    { itemId: id, requestedBy: session.user.id },
    { tags: [`user-${session.user.id}`] },
  );
  return { runId: handle.id, publicAccessToken: handle.publicAccessToken }; // for a live status in the browser
}
```

### The task

Create `trigger/{{feature_name}}.ts`. It builds its client from its own environment (`getDirectus()` from `directus-to-trigger`), reads the record, skips what is done and writes only result fields:

```typescript
// trigger/{{feature_name}}.ts
import { createHash } from 'node:crypto';
import { task } from '@trigger.dev/sdk';
import { readItem, updateItem } from '@directus/sdk';
import { getDirectus } from './lib/directus';

export const {{featureName}} = task({
  id: '{{feature_name}}',
  maxDuration: 600, // seconds
  retry: { maxAttempts: 3, factor: 2, minTimeoutInMs: 1_000, maxTimeoutInMs: 30_000 },
  run: async (payload: { itemId: string; requestedBy?: string }, { ctx }) => {
    const directus = getDirectus();
    const item = await directus.request(readItem('{{collection_name}}', payload.itemId));

    // Skip unchanged work: a second delivery, or a replay from the dashboard
    const hash = createHash('sha256').update(JSON.stringify([item.title /* , other source fields */])).digest('hex');
    if (item.source_hash === hash) return { itemId: item.id, skipped: true };

    await directus.request(
      updateItem('{{collection_name}}', item.id, { processing_status: 'processing', last_run_id: ctx.run.id }),
    );

    // Do the slow or flaky work here: an AI call, an external API, an image transformation.
    // Create third-party clients inside run() or lazily, never at module level.
    const result = {};

    await directus.request(
      updateItem('{{collection_name}}', item.id, {
        ...result, // result fields only: never the source fields a Flow watches
        source_hash: hash,
        processing_status: 'done',
      }),
    );
    return { itemId: item.id };
  },
  // Runs once, after the last retry has failed. Keep it below `run`: TypeScript takes the payload type from there
  onFailure: async ({ payload }) => {
    await getDirectus().request(updateItem('{{collection_name}}', payload.itemId, { processing_status: 'failed' }));
  },
});
```

- **Never write the source fields** from the task. A Flow that starts the task watches them; writing them restarts it.
- **Environment:** the task reads `DIRECTUS_URL` and `DIRECTUS_TOKEN` (the task user's token) from the Trigger.dev environment, plus any third-party key (`deployment`).
- **Paid work:** keep `maxAttempts` low for AI calls and set `maxDuration` (`trigger-dev` → `task-development`).
- **Triggered by a Flow instead of a user:** add a `case` for the collection to the receiver in `directus-to-trigger` and use `debounce` on the item id.

## Step 6: Register the Collection for Revalidation

Content edited in Directus reaches the site only through the pipeline from `deployment`. A collection that is missing from either list never refreshes:

- [ ] Add `{{collection_name}}` to the `collections` of the Directus Flow that calls `/api/revalidate`
- [ ] Add `{{collection_name}}` to `COLLECTION_TAGS` in `app/api/revalidate/route.ts`
- [ ] If a read of another collection expands `{{collection_name}}`, add its tag to that read's `TAGS`
- [ ] This also refreshes the page after a task's write: the Flow fires for every `items.update`, whoever made it

## Step 7: Verify

- [ ] `npx tsc --noEmit` passes
- [ ] Listing page at `/{{route}}` renders the published items from Directus
- [ ] Detail page at `/{{route}}/[slug]` loads with all fields
- [ ] Images render through `next/image` without a token in the URL (view the page source)
- [ ] SEO metadata appears in the page source (`generateMetadata`)
- [ ] Create and update forms work, fail for a visitor who is not signed in, and fail with `403` for a signed-in user whose policy does not allow the write (if mutations were added)
- [ ] Edit an item in Directus: the page changes within seconds, without a rebuild
- [ ] Non-existent slugs show 404 (`notFound()`)
- [ ] A task was started (step 5): the Trigger.dev dashboard shows the run, `processing_status` goes `pending`, `processing`, `done`, and the page shows the result without a manual refresh
- [ ] The task started twice for an unchanged item returns `skipped`; with a broken third-party key it retries, then `onFailure` sets `failed`
- [ ] The task's Directus user cannot write the source fields (try it with the user's token)
