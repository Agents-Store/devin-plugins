# Scenario: AI Enrichment Pipeline

When a new article is created in Directus, automatically enrich it with an AI-generated summary and tags, then refresh the Next.js page that displays it. This example exercises the full integration seam: Directus Flow → Next.js webhook → Trigger.dev task → Directus SDK write → revalidate.

## Flow

```
Editor creates/updates article in Directus
    ↓  (Directus Flow: Event Hook on items.create/update)
POST /api/directus-webhook (Next.js route handler)
    ↓  (verify signature, then)
tasks.trigger<typeof enrichArticleTask>("enrich-article", { itemId })
    ↓  (Trigger.dev runs the task durably)
task.run():
  - fetch article from Directus
  - call OpenAI for summary + tags
  - updateItem() back to Directus
  - POST /api/revalidate to invalidate ISR
    ↓
Readers see enriched content on next page load
```

## Directus Collections

### `articles`

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `status` | String | draft / published / archived |
| `title` | String | |
| `slug` | String (unique) | URL identifier |
| `body` | Text | Raw article body |
| `ai_summary` | Text | Written by the enrichment task |
| `ai_tags` | JSON (array of strings) | Written by the enrichment task |
| `ai_enriched_at` | Datetime | Last successful enrichment timestamp |
| `processing_status` | String | `pending` / `processing` / `done` / `failed` |
| `last_run_id` | String | Trigger.dev run handle (for `useRealtimeRun` in admin UI) |
| `date_created` | Timestamp (auto) | System field |
| `date_updated` | Timestamp (auto) | System field |

Grant the API token role read + update access to `ai_summary`, `ai_tags`, `ai_enriched_at`, `processing_status`, `last_run_id`.

## Directus Flow

Settings → Flows → Create Flow:

- **Name**: `Articles — Enrich on Save`
- **Status**: Active
- **Trigger**: Event Hook
- **Type**: Filter (run before save) OR Action (run after save) — use **Action** (non-blocking)
- **Scope**: `items.create`, `items.update`
- **Collection**: `articles`
- **Operation**: Webhook
  - **Method**: POST
  - **URL**: `https://yourdomain.com/api/directus-webhook/articles?secret={{ $env.REVALIDATION_SECRET }}`
  - **Headers**: `Content-Type: application/json`
  - **Body**: `{ "event": "{{ $trigger.event }}", "keys": {{ $trigger.keys }}, "collection": "{{ $trigger.collection }}" }`

Set `REVALIDATION_SECRET` in Directus Settings → Environment Variables so `{{ $env.REVALIDATION_SECRET }}` interpolates.

## Next.js Webhook Receiver

```typescript
// app/api/directus-webhook/articles/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { tasks } from '@trigger.dev/sdk/v3';
import type { enrichArticleTask } from '@/trigger/enrich-article';

export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  // 1. Verify the shared secret from the Directus Flow
  const secret = request.nextUrl.searchParams.get('secret');
  if (secret !== process.env.REVALIDATION_SECRET) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  // 2. Parse the Directus event payload
  const body = await request.json();
  const keys: string[] = body.keys ?? [];

  // 3. Fan out: one task per affected article
  const handles = await Promise.all(
    keys.map((itemId) =>
      tasks.trigger<typeof enrichArticleTask>(
        'enrich-article',
        { itemId },
        { idempotencyKey: `enrich-article-${itemId}` }
      )
    )
  );

  return NextResponse.json({ triggered: handles.length, handles });
}
```

**`force-dynamic` is critical** — without it, Next.js will try to pre-render this route at build time, and `tasks.trigger()` will fail because `TRIGGER_SECRET_KEY` isn't bound during static generation.

**Idempotency keyed on item ID** — if Directus retries the webhook, Trigger.dev sees the same key and returns the existing run instead of spawning a duplicate.

## Trigger.dev Task

```typescript
// trigger/enrich-article.ts
import { task, logger } from '@trigger.dev/sdk/v3';
import { createDirectus, rest, staticToken, readItem, updateItem } from '@directus/sdk';
import OpenAI from 'openai';
import type { Schema } from '@/types/directus';

export const enrichArticleTask = task({
  id: 'enrich-article',
  maxDuration: 300, // 5 minutes
  retry: {
    maxAttempts: 3,
    factor: 2,
    minTimeoutInMs: 1000,
    maxTimeoutInMs: 30000,
  },
  run: async (payload: { itemId: string }) => {
    // 1. Build server-side Directus client inside the task
    const directus = createDirectus<Schema>(process.env.NEXT_PUBLIC_DIRECTUS_URL!)
      .with(staticToken(process.env.DIRECTUS_ADMIN_TOKEN!))
      .with(rest({ cache: 'no-store' }));

    // 2. Mark as processing
    await directus.request(
      updateItem('articles', payload.itemId, { processing_status: 'processing' })
    );

    // 3. Fetch the article
    const article = await directus.request(
      readItem('articles', payload.itemId, { fields: ['id', 'title', 'body'] })
    );

    if (!article.body || article.body.length < 50) {
      logger.warn('Article body too short to enrich', { itemId: payload.itemId });
      await directus.request(
        updateItem('articles', payload.itemId, { processing_status: 'done' })
      );
      return { itemId: payload.itemId, skipped: true };
    }

    // 4. Call OpenAI
    const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      response_format: { type: 'json_object' },
      messages: [
        {
          role: 'system',
          content:
            'You enrich articles. Return JSON: { "summary": "1-2 sentence summary", "tags": ["tag1", "tag2", "tag3"] }.',
        },
        { role: 'user', content: `Title: ${article.title}\n\nBody:\n${article.body}` },
      ],
    });

    const raw = completion.choices[0]?.message?.content ?? '{}';
    const { summary, tags } = JSON.parse(raw) as { summary: string; tags: string[] };

    // 5. Write enriched fields back to Directus
    await directus.request(
      updateItem('articles', payload.itemId, {
        ai_summary: summary,
        ai_tags: tags,
        ai_enriched_at: new Date().toISOString(),
        processing_status: 'done',
      })
    );

    // 6. Close the loop — revalidate Next.js ISR cache
    await fetch(
      `${process.env.NEXT_PUBLIC_SITE_URL}/api/revalidate?secret=${process.env.REVALIDATION_SECRET}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ collection: 'articles' }),
      }
    );

    return { itemId: payload.itemId, summary, tags };
  },
  catchError: async ({ payload, error, retry }) => {
    // Final failure handling
    if (retry.attempt >= 3) {
      const directus = createDirectus<Schema>(process.env.NEXT_PUBLIC_DIRECTUS_URL!)
        .with(staticToken(process.env.DIRECTUS_ADMIN_TOKEN!))
        .with(rest({ cache: 'no-store' }));
      await directus.request(
        updateItem('articles', (payload as { itemId: string }).itemId, {
          processing_status: 'failed',
        })
      );
    }
    throw error;
  },
});
```

## Environment Variables Required in the Task

Set these in the Trigger.dev dashboard → Environment Variables (per environment):

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_DIRECTUS_URL` | Production Directus URL |
| `DIRECTUS_ADMIN_TOKEN` | Task-scoped static token (read + update on `articles`) |
| `OPENAI_API_KEY` | OpenAI API key |
| `NEXT_PUBLIC_SITE_URL` | Production Next.js URL |
| `REVALIDATION_SECRET` | Same secret used by the `/api/revalidate` route |

## Next.js Article Page

```typescript
// app/articles/[slug]/page.tsx
import directus from '@/lib/directus';
import { readItems } from '@directus/sdk';
import { notFound } from 'next/navigation';

export const revalidate = 300; // 5 min default, overridden by on-demand revalidation

export default async function ArticlePage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const [article] = await directus.request(
    readItems('articles', {
      filter: { slug: { _eq: slug }, status: { _eq: 'published' } },
      fields: ['*'],
      limit: 1,
    })
  );
  if (!article) notFound();

  return (
    <article>
      <h1>{article.title}</h1>
      {article.ai_summary && (
        <aside className="ai-summary">
          <strong>AI Summary:</strong> {article.ai_summary}
        </aside>
      )}
      <div>{article.body}</div>
      {article.ai_tags?.length > 0 && (
        <footer>
          Tags: {article.ai_tags.map((tag) => <span key={tag}>#{tag}</span>)}
        </footer>
      )}
    </article>
  );
}
```

## Realtime Progress in Directus Admin (Optional)

If you run a Next.js page inside the Directus admin as an iframe extension, show live task status:

```typescript
'use client';
import { useRealtimeRun } from '@trigger.dev/react-hooks';

export function EnrichmentStatus({ runId }: { runId: string }) {
  const { run, error } = useRealtimeRun(runId);
  if (error) return <span>Error: {error.message}</span>;
  if (!run) return <span>Loading…</span>;
  return <span>Status: {run.status}</span>;
}
```

## Verification

- [ ] Create an article in Directus with a long body
- [ ] Directus Flow fires, POSTs to `/api/directus-webhook/articles`
- [ ] Webhook route returns 200 with a run handle in the body
- [ ] Trigger dashboard shows the `enrich-article` task running
- [ ] Task completes; article in Directus has `ai_summary`, `ai_tags`, `ai_enriched_at`, `processing_status: 'done'`
- [ ] Next.js `/articles/[slug]` page shows the enriched content within seconds (revalidation fired)
- [ ] Creating the same article twice in quick succession reuses the same run (idempotency key works)
- [ ] Deliberately break `OPENAI_API_KEY` — task retries 3x then marks `processing_status: 'failed'`
