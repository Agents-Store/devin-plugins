---
name: lexical-editor
description: This skill should be used when the user asks about "Payload rich text", "Lexical editor in Payload", "custom Lexical feature", "richText blocks", "richText link/upload/relationship", "custom Lexical node", "render Payload Lexical to JSX", "convert Lexical to HTML", or needs to customize the editor inside `richText` fields.
---

# PayloadCMS — Lexical Editor

`richText` fields in Payload v3 are backed by **Lexical** (Facebook/Meta's editor framework). The editor is configured per field, ships dozens of default features, and is fully extensible with custom features, blocks, and nodes.

## Defaults

```ts
import { lexicalEditor } from '@payloadcms/richtext-lexical'

// In payload.config.ts — sets the default for ALL richText fields
editor: lexicalEditor(),

// Or per field
{
  name: 'content',
  type: 'richText',
  editor: lexicalEditor(),
}
```

Default features include: paragraph, heading (H1–H6), bold, italic, underline, strikethrough, code, link, list (unordered/ordered/check), block-quote, horizontal-rule, upload, indent, alignment, superscript, subscript.

## Configuring Features

`features` is a function that receives the default feature list — return a new array:

```ts
import {
  lexicalEditor,
  HeadingFeature,
  LinkFeature,
  BlocksFeature,
  UploadFeature,
  FixedToolbarFeature,
  InlineToolbarFeature,
  HorizontalRuleFeature,
  TreeViewFeature,
} from '@payloadcms/richtext-lexical'

editor: lexicalEditor({
  features: ({ defaultFeatures, rootFeatures }) => [
    ...defaultFeatures,
    FixedToolbarFeature(),                       // Toolbar sticks to the top
    InlineToolbarFeature(),                      // Floating contextual toolbar
    HorizontalRuleFeature(),
    HeadingFeature({ enabledHeadingSizes: ['h2', 'h3', 'h4'] }),
    LinkFeature({
      enabledCollections: ['posts', 'pages'],    // Internal link targets
      fields: ({ defaultFields }) => [
        ...defaultFields,
        { name: 'rel', type: 'select', options: ['nofollow', 'noopener'], hasMany: true },
      ],
    }),
    UploadFeature({
      collections: {
        media: {
          fields: [
            { name: 'caption', type: 'textarea' },
          ],
        },
      },
    }),
    BlocksFeature({
      blocks: [HeroBlock, CalloutBlock, EmbedBlock],
    }),
    TreeViewFeature(),                           // Debug view of the JSON tree
  ],
})
```

## Blocks Inside RichText

`BlocksFeature` lets editors drop any reusable `Block` definition inline:

```ts
import type { Block } from 'payload'

export const CalloutBlock: Block = {
  slug: 'callout',
  labels: { singular: 'Callout', plural: 'Callouts' },
  fields: [
    { name: 'kind', type: 'select', options: ['info', 'warning', 'success'], defaultValue: 'info' },
    { name: 'title', type: 'text' },
    { name: 'body', type: 'richText' },          // Nested richText is fine
  ],
}
```

Reference the block from the field's editor:
```ts
{
  name: 'content',
  type: 'richText',
  editor: lexicalEditor({
    features: ({ defaultFeatures }) => [
      ...defaultFeatures,
      BlocksFeature({ blocks: [CalloutBlock] }),
    ],
  }),
}
```

In the saved JSON, each block appears as a `{ type: 'block', fields: { blockType: 'callout', kind, title, body } }` node.

## Rendering Lexical to JSX (Frontend)

Use the official renderer:

```bash
pnpm add @payloadcms/richtext-lexical
```

```tsx
// app/posts/[slug]/page.tsx
import { RichText } from '@payloadcms/richtext-lexical/react'
import type { SerializedEditorState } from '@payloadcms/richtext-lexical/lexical'

export default async function PostPage({ params }) {
  const post = await fetchPost(params.slug)
  return (
    <article>
      <h1>{post.title}</h1>
      <RichText data={post.content as SerializedEditorState} />
    </article>
  )
}
```

Custom render for specific node types:
```tsx
<RichText
  data={post.content}
  converters={({ defaultConverters }) => ({
    ...defaultConverters,
    blocks: {
      callout: ({ node }) => (
        <div className={`callout callout-${node.fields.kind}`}>
          <h4>{node.fields.title}</h4>
          <RichText data={node.fields.body} />
        </div>
      ),
    },
    upload: ({ node }) => (
      <img src={node.value.url} alt={node.value.alt} />
    ),
    link: ({ node, nodesToJSX }) => {
      const url = node.fields.linkType === 'custom'
        ? node.fields.url
        : `/${node.fields.doc?.relationTo}/${node.fields.doc?.value?.slug ?? ''}`
      return <a href={url}>{nodesToJSX({ nodes: node.children })}</a>
    },
  })}
/>
```

## Converting to HTML (Server-Side)

For RSS feeds, email, or static rendering:

```ts
// Sync — data already fully populated (sufficient depth at query time)
import { convertLexicalToHTML } from '@payloadcms/richtext-lexical/html'

const html = convertLexicalToHTML({ data: post.content })
```

```ts
// Async — dynamically populate uploads/links during conversion
import { convertLexicalToHTMLAsync } from '@payloadcms/richtext-lexical/html-async'
import { getPayloadPopulateFn } from '@payloadcms/richtext-lexical'

const html = await convertLexicalToHTMLAsync({
  data: post.content,
  populate: await getPayloadPopulateFn({ currentDepth: 0, depth: 2, payload }),
})
```

Notes:

- Client-side population uses `getRestPopulateFn` from `@payloadcms/richtext-lexical/client` instead of `getPayloadPopulateFn`.
- Custom block converters go in the `converters` option — an `HTMLConvertersFunction` keying `blocks` / `inlineBlocks` by block slug (same shape as the JSX `converters` above).
- `lexicalHTMLField()` exists to store auto-converted HTML on the document via an `afterRead` hook, but the docs call it "generally not recommended" — convert at render time instead.

Source: https://payloadcms.com/docs/rich-text/converting-html

## Custom Features

A feature is a function that registers nodes, toolbar buttons, slash commands, and converters:

```ts
import { createServerFeature } from '@payloadcms/richtext-lexical'

export const CustomFeature = createServerFeature({
  feature: () => ({
    ClientFeature: '@/lexical/CustomFeature.client',  // import path
    nodes: [/* node configs */],
    sanitizedClientFeatureProps: null,
  }),
  key: 'custom',
})
```

Match it on the client:
```tsx
// src/lexical/CustomFeature.client.tsx
'use client'
import { createClientFeature } from '@payloadcms/richtext-lexical/client'

export const CustomFeatureClient = createClientFeature({
  // toolbarFixed: ..., toolbarInline: ..., slashMenu: ...
})

export default CustomFeatureClient
```

Run `pnpm payload generate:importmap` after adding any string-path component.

## Disabling Default Features

Filter `defaultFeatures` before returning:

```ts
features: ({ defaultFeatures }) =>
  defaultFeatures.filter((f) => f.key !== 'horizontalrule'),
```

## Working With Saved Data

A `richText` field stores a JSON tree:
```json
{
  "root": {
    "type": "root",
    "children": [
      { "type": "heading", "tag": "h2", "children": [{ "type": "text", "text": "Hello" }] }
    ]
  }
}
```

Walk it for analysis (word count, table-of-contents extraction):
```ts
import type { SerializedEditorState, SerializedLexicalNode } from 'lexical'

function walk(node: SerializedLexicalNode, fn: (n: SerializedLexicalNode) => void) {
  fn(node)
  if ('children' in node && Array.isArray((node as any).children)) {
    for (const c of (node as any).children) walk(c, fn)
  }
}

function textOf(data: SerializedEditorState): string {
  let out = ''
  walk(data.root, (n) => {
    if (n.type === 'text') out += (n as any).text
  })
  return out
}
```

## Common Pitfalls

| Symptom | Cause | Fix |
| --- | --- | --- |
| `RichText` shows raw JSON | Wrong import — used `data` as a string | Pass the parsed object, not stringified JSON |
| Custom feature missing in admin | `generate:importmap` not run | `pnpm payload generate:importmap` and commit |
| Block fields lose values on save | Block slug collision with another collection | Rename the block slug; slugs are global |
| Migration writes plain text into `richText` | Plain strings aren't valid Lexical state | Wrap them as `{ root: { type: 'root', children: [{ type: 'paragraph', children: [{ type: 'text', text: '…' }] }] } }` |

## See Also

- The `fields` skill — `richText` field config.
- The `cms-migration` skill — converting WordPress / Contentful rich text into Lexical state.
- The `nextjs-integration` skill — rendering richText in server components.
