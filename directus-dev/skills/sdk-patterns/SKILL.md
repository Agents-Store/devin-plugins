---
name: sdk-patterns
description: "@directus/sdk patterns \u2014 composable client, TypeScript types, CRUD operations, authentication, real-time subscriptions. This skill should be used when the user asks about \"Directus SDK\", \"@directus/sdk\", \"Directus client library\", \"Directus TypeScript\", or needs code patterns for integrating Directus into a JavaScript/TypeScript project."
---

# @directus/sdk Patterns

The official Directus SDK uses a composable architecture. Install:

```bash
npm install @directus/sdk
```

## Client Setup

### Basic Client (Static Token)

```typescript
import { createDirectus, rest, staticToken } from '@directus/sdk';

const client = createDirectus('https://your-instance.com')
  .with(staticToken('your-static-token'))
  .with(rest());
```

### Client with Login

```typescript
import { createDirectus, rest, authentication } from '@directus/sdk';

const client = createDirectus('https://your-instance.com')
  .with(authentication())
  .with(rest());

// Login
await client.login('user@example.com', 'password');

// Token is managed automatically (refresh handled internally)
```

## Type-Safe Schema

Define your schema for TypeScript autocompletion:

```typescript
interface Post {
  id: string;
  title: string;
  content: string;
  status: 'draft' | 'published' | 'archived';
  author: string | Author;
  categories: string[] | PostCategory[];
  date_created: string;
}

interface Author {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
}

interface Category {
  id: string;
  name: string;
  slug: string;
}

interface PostCategory {
  id: string;
  posts_id: string | Post;
  categories_id: string | Category;
}

interface MySchema {
  posts: Post[];
  authors: Author[];
  categories: Category[];
  posts_categories: PostCategory[];
}

const client = createDirectus<MySchema>('https://your-instance.com')
  .with(staticToken('token'))
  .with(rest());
```

## CRUD Operations

### Read Items

```typescript
import { readItems } from '@directus/sdk';

// List with filter and sort
const posts = await client.request(
  readItems('posts', {
    fields: ['id', 'title', 'status', { author: ['first_name', 'last_name'] }],
    filter: { status: { _eq: 'published' } },
    sort: ['-date_created'],
    limit: 25,
  })
);
```

### Read Single Item

```typescript
import { readItem } from '@directus/sdk';

const post = await client.request(
  readItem('posts', 'item-uuid', {
    fields: ['*', { author: ['*'] }],
  })
);
```

### Create Item

```typescript
import { createItem } from '@directus/sdk';

const newPost = await client.request(
  createItem('posts', {
    title: 'New Post',
    content: 'Post content...',
    status: 'draft',
    author: 'author-uuid',
  })
);
```

### Create Multiple Items

```typescript
import { createItems } from '@directus/sdk';

const newPosts = await client.request(
  createItems('posts', [
    { title: 'Post 1', status: 'draft' },
    { title: 'Post 2', status: 'draft' },
  ])
);
```

### Update Item

```typescript
import { updateItem } from '@directus/sdk';

const updated = await client.request(
  updateItem('posts', 'item-uuid', {
    status: 'published',
  })
);
```

### Update Multiple Items

```typescript
import { updateItems } from '@directus/sdk';

const updated = await client.request(
  updateItems('posts', ['uuid-1', 'uuid-2'], {
    status: 'archived',
  })
);
```

### Delete Item

```typescript
import { deleteItem, deleteItems } from '@directus/sdk';

// Single
await client.request(deleteItem('posts', 'item-uuid'));

// Multiple
await client.request(deleteItems('posts', ['uuid-1', 'uuid-2']));
```

## Filtering

```typescript
const results = await client.request(
  readItems('products', {
    filter: {
      _and: [
        { status: { _eq: 'active' } },
        {
          _or: [
            { price: { _lt: 50 } },
            { featured: { _eq: true } },
          ],
        },
      ],
    },
  })
);
```

## Aggregation

```typescript
import { aggregate } from '@directus/sdk';

const stats = await client.request(
  aggregate('orders', {
    aggregate: { count: '*', sum: 'total', avg: 'total' },
    groupBy: ['status'],
  })
);
```

## Search

```typescript
const results = await client.request(
  readItems('articles', {
    search: 'machine learning',
    fields: ['id', 'title', 'excerpt'],
    limit: 20,
  })
);
```

## Deep Queries

```typescript
const posts = await client.request(
  readItems('posts', {
    fields: ['title', { comments: ['text', { author: ['name'] }] }],
    deep: {
      comments: {
        _filter: { status: { _eq: 'approved' } },
        _sort: ['-date_created'],
        _limit: 5,
      },
    },
  })
);
```

## File Operations

```typescript
import { uploadFiles, importFile } from '@directus/sdk';

// Upload from form data
const formData = new FormData();
formData.append('file', fileBlob);
formData.append('title', 'My Image');

const uploaded = await client.request(uploadFiles(formData));

// Import from URL
const imported = await client.request(
  importFile('https://example.com/image.jpg', {
    title: 'Imported Image',
    folder: 'folder-uuid',
  })
);
```

## Schema Operations

```typescript
import {
  readCollections, createCollection,
  readFields, createField,
  readRelations, createRelation,
  schemaSnapshot, schemaDiff, schemaApply,
} from '@directus/sdk';

// Read all collections
const collections = await client.request(readCollections());

// Get schema snapshot for migration
const snapshot = await client.request(schemaSnapshot());

// Apply schema diff
const diff = await client.request(schemaDiff(snapshotFromStaging));
if (diff) {
  await client.request(schemaApply(diff));
}
```

## Real-Time (WebSocket)

```typescript
import { createDirectus, realtime, staticToken } from '@directus/sdk';

const client = createDirectus('https://your-instance.com')
  .with(staticToken('token'))
  .with(realtime());

// Connect
await client.connect();

// Subscribe to collection changes
const { subscription } = await client.subscribe('posts', {
  event: 'create',
  query: { fields: ['id', 'title', 'status'] },
});

for await (const event of subscription) {
  console.log('New post:', event.data);
}
```

## Error Handling

```typescript
try {
  const result = await client.request(readItem('posts', 'nonexistent'));
} catch (error) {
  if (error.errors) {
    for (const err of error.errors) {
      console.error(`[${err.extensions?.code}] ${err.message}`);
    }
  }
}
```

Common error codes: `FORBIDDEN`, `RECORD_NOT_UNIQUE`, `FAILED_VALIDATION`, `INVALID_PAYLOAD`, `ROUTE_NOT_FOUND`.

## Environment Variables

Always use env vars for configuration:

```typescript
const client = createDirectus(process.env.DIRECTUS_URL!)
  .with(staticToken(process.env.DIRECTUS_TOKEN!))
  .with(rest());
```

```bash
# .env
DIRECTUS_URL=https://your-instance.com
DIRECTUS_TOKEN=your-static-token
```
