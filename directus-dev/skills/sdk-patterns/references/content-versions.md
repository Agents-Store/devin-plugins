# Content Versions (Draft and Publish)

Moved out of `SKILL.md` to keep it short. Uses the `client` from the Client Setup section.

For collections with `meta.versioning: true`. In the Studio the published view is read-only since Directus 12 and edits go to a version that is then promoted; API writes to the item itself still work when the policy allows them, so use versions on purpose for review workflows. The reserved keys are `published` (alias `main`) and `draft`.

```typescript
import {
  readItem, readItems, createContentVersion, saveToContentVersion,
  compareContentVersion, promoteContentVersion,
} from '@directus/sdk';

// Read the draft of an item (use 'published' for the live one; 'main' still works)
const draft = await client.request(
  readItem('posts', 'item-uuid', { version: 'draft', fields: ['*', { author: ['*'] }] }),
);

// Raw relational delta of a version (single-item reads only)
const raw = await client.request(readItem('posts', 'item-uuid', { version: 'draft', versionRaw: true }));

// Create a custom version, save changes into it, review the difference, publish it
const version = await client.request(
  createContentVersion({ key: 'spring-edit', name: 'Spring edit', collection: 'posts', item: 'item-uuid' }),
);
await client.request(saveToContentVersion(version.id, { title: 'New title' }));
const { outdated, mainHash, current } = await client.request(compareContentVersion(version.id));
if (!outdated) {
  await client.request(promoteContentVersion(version.id, mainHash));
}
```

`outdated: true` means the published item changed after the version was created. Compare again and decide before promoting. Requesting a version key that does not exist answers `403 FORBIDDEN`, it does not fall back to the published item. That includes `draft` while nobody has saved a draft for the item yet, so read the published item first or handle the 403.
