# Scenario: AI Enrichment Pipeline

When an article is created or its text is edited in Directus, enrich it with an AI summary and tags in a background task, write the result back, and show it on the page. The scenario exercises the whole seam: Directus Flow, Next.js receiver, Trigger.dev task, Directus write-back, fresh page. The rules behind each step are in `directus-to-trigger` and `background-tasks`; this file fills them in for one use case.

## Flow

```
editor creates an article or edits its body
  -> Directus Flow (action; condition: body is in the payload) -> POST /api/directus-webhook/articles
  -> receiver checks the secret and starts enrich-article for each key (debounced, 15 s)
  -> task: read the article, skip if the source is unchanged, call the model, write the result
  -> the revalidation Flow expires the `articles` tag -> the next visitor sees the summary
```

## Directus Collection: `articles`

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `status` | String | draft / published / archived (a new Directus 12 collection has a boolean `archived` instead; adapt the filters and the type) |
| `title` | String | |
| `slug` | String (unique) | URL identifier |
| `body` | Text | The source the editors write |
| `ai_summary` | Text | Written by the task |
| `ai_tags` | JSON (array of strings) | Written by the task |
| `ai_source_hash` | String | Hash of title and body the result was made from; lets the task skip unchanged work |
| `ai_enriched_at` | Datetime | Last successful enrichment |
| `processing_status` | String | `pending` / `processing` / `done` / `failed` |
| `last_run_id` | String | Trigger.dev run id, for the admin to find the run |
| `date_created`, `date_updated` | Timestamp (auto) | System fields |

Two Directus users are involved, with different policies. The **Next.js server's** user reads `articles`. The **task's** user reads `articles` and updates only `ai_summary`, `ai_tags`, `ai_source_hash`, `ai_enriched_at`, `processing_status` and `last_run_id` (field-level update permission). A task that cannot write `body` cannot restart its own Flow through the field the Flow watches, whatever the code does.

```typescript
// types/directus.ts
export interface Article {
  id: string;
  status: 'draft' | 'published' | 'archived';
  title: string;
  slug: string;
  body: string | null;
  ai_summary: string | null;
  ai_tags: string[] | null;
  ai_source_hash: string | null;
  ai_enriched_at: string | null;
  processing_status: 'pending' | 'processing' | 'done' | 'failed' | null;
  last_run_id: string | null;
  date_created: string;
  date_updated: string | null;
}

export interface Schema {
  articles: Article[];
}
```

## The Directus Flow

Settings → Flows, or the MCP `flows` and `operations` tools. The settings are explained in `directus-dev` → `flow-automation` → `references/send-items-to-a-worker.md`:

- **Trigger:** event hook, type **action**, scope `items.create` and `items.update`, collection `articles`
- **Condition operation** (filter rules): `{ "$trigger": { "payload": { "body": { "_nnull": true } } } }`. It passes for a new article and for an edit of `body`, and it fails for the task's own write-back, which never contains `body`
- **Request operation**, connected to the condition's resolve path: `POST https://<app>/api/directus-webhook/articles`, headers `Content-Type: application/json` and `x-webhook-secret: {{ $env.DIRECTUS_WEBHOOK_SECRET }}`, body `{"event":"{{ $trigger.event }}","collection":"{{ $trigger.collection }}","keys":{{ $trigger.keys }}}` (as a string)
- **Directus container:** `DIRECTUS_WEBHOOK_SECRET` and `FLOWS_ENV_ALLOW_LIST=DIRECTUS_WEBHOOK_SECRET` (plus `REVALIDATION_SECRET` for the revalidation Flow)

An edit of `title` alone does not start the task with this condition; add `title` to the condition with `_or` if it should.

Also list `articles` in the revalidation Flow and in `COLLECTION_TAGS` of `/api/revalidate` (`deployment`), so the task's write refreshes the page.

## The Receiver

The `articles` case of the receiver in `directus-to-trigger` starts `enrich-article` with `{ itemId }` and a debounce on the item id. Nothing else is needed here.

## The Task

```typescript
// trigger/enrich-article.ts
import { createHash } from 'node:crypto';
import { logger, task } from '@trigger.dev/sdk';
import { readItem, updateItem } from '@directus/sdk';
import OpenAI from 'openai';
import { getDirectus, requireEnv } from './lib/directus';

let client: OpenAI | undefined;
// Created on first use: no API key exists while the image is built
const openai = () => (client ??= new OpenAI({ apiKey: requireEnv('OPENAI_API_KEY') }));

async function summarize(title: string, body: string): Promise<{ summary: string; tags: string[] }> {
  const completion = await openai().chat.completions.create({
    model: requireEnv('ENRICH_MODEL'),
    response_format: { type: 'json_object' },
    messages: [
      {
        role: 'system',
        content: 'You enrich articles. Answer with JSON: { "summary": "one or two sentences", "tags": ["three short tags"] }.',
      },
      { role: 'user', content: `Title: ${title}\n\nBody:\n${body}` },
    ],
  });
  const parsed: unknown = JSON.parse(completion.choices[0]?.message?.content ?? '{}');
  const { summary, tags } = (parsed ?? {}) as { summary?: unknown; tags?: unknown };
  if (typeof summary !== 'string' || !Array.isArray(tags)) throw new Error('model answer has the wrong shape');
  return { summary, tags: tags.filter((tag): tag is string => typeof tag === 'string') };
}

export const enrichArticle = task({
  id: 'enrich-article',
  maxDuration: 300,
  retry: { maxAttempts: 2 }, // every retry of a model call is paid
  run: async (payload: { itemId: string; requestedBy?: string; force?: boolean }, { ctx }) => {
    // A missing variable is not fixed by a retry: fail before the item is touched
    requireEnv('OPENAI_API_KEY');
    requireEnv('ENRICH_MODEL');

    const directus = getDirectus();
    const article = await directus.request(
      readItem('articles', payload.itemId, { fields: ['id', 'title', 'body', 'ai_source_hash'] }),
    );

    // Skip unchanged work: a second delivery, a replay, or a write-back that slipped past the Flow's condition
    const hash = createHash('sha256').update(`${article.title}\n${article.body ?? ''}`).digest('hex');
    if (!payload.force && article.ai_source_hash === hash) return { itemId: article.id, skipped: 'unchanged' };

    if (!article.body || article.body.length < 50) {
      logger.warn('body too short to enrich', { itemId: article.id });
      await directus.request(updateItem('articles', article.id, { processing_status: 'done', ai_source_hash: hash }));
      return { itemId: article.id, skipped: 'too short' };
    }
    await directus.request(updateItem('articles', article.id, { processing_status: 'processing', last_run_id: ctx.run.id }));

    const { summary, tags } = await summarize(article.title, article.body);

    await directus.request(
      updateItem('articles', article.id, {
        ai_summary: summary,
        ai_tags: tags,
        ai_source_hash: hash,
        ai_enriched_at: new Date().toISOString(),
        processing_status: 'done',
      }),
    );
    logger.info('article enriched', { itemId: article.id, requestedBy: payload.requestedBy ?? null });
    return { itemId: article.id, tags: tags.length };
  },
  // Runs once, after the last retry has failed. Keep it below `run`: TypeScript takes the payload type from there
  onFailure: async ({ payload }) => {
    await getDirectus().request(updateItem('articles', payload.itemId, { processing_status: 'failed' }));
  },
});
```

- The task never writes `body` or `title`, so its updates never satisfy the Flow's condition.
- `onFailure` writes `failed` once, after the last attempt; the page and editors see the state.
- The model name is an environment variable (`ENRICH_MODEL`), not a literal, so changing it needs no deploy.
- The model's answer is untrusted text: it is stored as is, validated for shape, and rendered as text below.

### Environment of the task (Trigger.dev project, per environment)

| Variable | Value |
|----------|-------|
| `DIRECTUS_URL` | Directus address, reachable from the Trigger.dev workers |
| `DIRECTUS_TOKEN` | Static token of the **task** user (read `articles`; update the six result fields) |
| `OPENAI_API_KEY`, `ENRICH_MODEL` | Provider key and the model to use |

For `trigger dev` the same names go in `.env.trigger.local` with literal values.

## The Article Page

The page reads through a tagged read, like every other read of the stack (`directus-to-nextjs` → "Cache"):

```typescript
// lib/articles.ts
import 'server-only';
import { cache } from 'react';
import { readItems } from '@directus/sdk';
import { requestTagged } from '@/lib/directus-tagged';

const ONE_HOUR = 3600; // safety net: a missed webhook heals itself within the hour

export const getArticleBySlug = cache(async (slug: string) => {
  const [article] = await requestTagged(
    readItems('articles', {
      filter: { slug: { _eq: slug }, status: { _eq: 'published' } },
      fields: ['id', 'title', 'body', 'ai_summary', 'ai_tags'],
      limit: 1,
    }),
    ['articles'],
    ONE_HOUR,
  );
  return article ?? null;
});
```

```tsx
// app/articles/[slug]/page.tsx
import { notFound } from 'next/navigation';
import { getArticleBySlug } from '@/lib/articles';

export default async function ArticlePage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const article = await getArticleBySlug(slug);
  if (!article) notFound();

  return (
    <article>
      <h1>{article.title}</h1>
      {article.ai_summary && (
        <aside>
          <strong>Summary:</strong> {article.ai_summary}
        </aside>
      )}
      {/* body is HTML written by editors: sanitize it first if anyone less trusted can write it */}
      <div dangerouslySetInnerHTML={{ __html: article.body ?? '' }} />
      {article.ai_tags && article.ai_tags.length > 0 && (
        <footer>{article.ai_tags.map((tag) => <span key={tag}>#{tag} </span>)}</footer>
      )}
    </article>
  );
}
```

## Regenerate Button and Live Status (optional)

A "regenerate" button is the Server Action `regenerateSummary` of `background-tasks`, which authorizes with the user's token, starts the task with `force: true` and returns the run's handle. A Client Component then subscribes to the run with `useRealtimeRun` (`trigger-dev` → `realtime` → "From a Next.js App with Self-Hosted Trigger.dev": `baseURL`, the run-scoped token, `refreshAccessToken`).

## Verification

- [ ] Create an article in Directus with a body longer than 50 characters: the Flow runs, the receiver answers `200` with `{ started: 1 }`
- [ ] The Trigger.dev dashboard shows `enrich-article` starting about 15 seconds later, not once per keystroke-sized save
- [ ] The task ends: the article has `ai_summary`, `ai_tags`, `ai_source_hash`, `processing_status: 'done'`
- [ ] The Flow does **not** fire again for the task's own write (check the Flow's log: one run per editor save)
- [ ] `/articles/<slug>` shows the summary within seconds, without a rebuild
- [ ] Saving the article again without changing `body` starts no run (the condition fails); saving a changed `body` runs the task once
- [ ] A second run for an unchanged article returns `skipped: 'unchanged'`
- [ ] Remove `OPENAI_API_KEY` from the Trigger.dev environment: the run fails at once, without retries, naming the variable, and `onFailure` sets `processing_status` to `failed`
- [ ] A wrong `x-webhook-secret` gets `401`; an unknown collection gets `400`
