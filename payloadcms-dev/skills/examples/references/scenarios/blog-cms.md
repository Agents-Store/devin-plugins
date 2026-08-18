# Scenario — Blog CMS with Drafts, Live Preview, ISR

A production-grade Payload blog. Posts with Lexical content, tags, categories, drafts + autosave, live preview, public frontend with ISR + on-save revalidation.

## Collections

### `src/collections/Users.ts`

```ts
import type { CollectionConfig } from 'payload'

export const Users: CollectionConfig = {
  slug: 'users',
  auth: { tokenExpiration: 7200, cookies: { secure: true, sameSite: 'Strict' } },
  admin: { useAsTitle: 'email' },
  fields: [
    {
      name: 'roles',
      type: 'select',
      hasMany: true,
      saveToJWT: true,
      options: [
        { label: 'Admin', value: 'admin' },
        { label: 'Author', value: 'author' },
      ],
      defaultValue: ['author'],
      required: true,
    },
    { name: 'name', type: 'text' },
  ],
}
```

### `src/collections/Media.ts`

```ts
import type { CollectionConfig } from 'payload'

export const Media: CollectionConfig = {
  slug: 'media',
  access: { read: () => true },
  upload: {
    mimeTypes: ['image/*'],
    imageSizes: [
      { name: 'thumbnail', width: 400, height: 300, position: 'centre' },
      { name: 'card', width: 768 },
      { name: 'hero', width: 1920 },
    ],
    adminThumbnail: 'thumbnail',
  },
  fields: [
    { name: 'alt', type: 'text', required: true },
    { name: 'caption', type: 'text' },
  ],
}
```

### `src/collections/Tags.ts`

```ts
import type { CollectionConfig } from 'payload'

export const Tags: CollectionConfig = {
  slug: 'tags',
  access: { read: () => true },
  admin: { useAsTitle: 'label' },
  fields: [
    { name: 'label', type: 'text', required: true, unique: true },
    { name: 'slug', type: 'text', unique: true, index: true },
  ],
}
```

### `src/collections/Categories.ts`

```ts
import type { CollectionConfig } from 'payload'

export const Categories: CollectionConfig = {
  slug: 'categories',
  access: { read: () => true },
  admin: { useAsTitle: 'name' },
  fields: [
    { name: 'name', type: 'text', required: true, unique: true },
    { name: 'slug', type: 'text', unique: true, index: true },
    { name: 'description', type: 'textarea' },
  ],
}
```

### `src/collections/Posts.ts`

```ts
import type { CollectionConfig } from 'payload'
import { revalidatePath, revalidateTag } from 'next/cache'
import slugify from 'slugify'

const isAdminOrAuthor: any = ({ req: { user } }: any) => {
  if (!user) return false
  if (user.roles?.includes('admin')) return true
  return { author: { equals: user.id } }
}

export const Posts: CollectionConfig = {
  slug: 'posts',
  admin: {
    useAsTitle: 'title',
    defaultColumns: ['title', 'author', '_status', 'publishedAt', 'updatedAt'],
    livePreview: {
      url: ({ data }) =>
        `${process.env.NEXT_PUBLIC_SITE_URL}/posts/${data.slug}?live-preview=true`,
      breakpoints: [
        { name: 'mobile', width: 375, height: 667, label: 'Mobile' },
        { name: 'desktop', width: 1440, height: 900, label: 'Desktop' },
      ],
    },
    preview: (doc) =>
      `${process.env.NEXT_PUBLIC_SITE_URL}/api/preview?slug=${doc.slug}&secret=${process.env.PREVIEW_SECRET}&path=/posts/${doc.slug}`,
  },
  access: {
    read: ({ req: { user } }) =>
      user ? true : { _status: { equals: 'published' } },
    create: ({ req: { user } }) => Boolean(user),
    update: isAdminOrAuthor,
    delete: isAdminOrAuthor,
  },
  versions: {
    drafts: { autosave: { interval: 800 }, schedulePublish: true },
    maxPerDoc: 50,
  },
  fields: [
    { name: 'title', type: 'text', required: true },
    { name: 'slug', type: 'text', unique: true, index: true },
    { name: 'excerpt', type: 'textarea' },
    { name: 'heroImage', type: 'upload', relationTo: 'media' },
    { name: 'content', type: 'richText', required: true },
    {
      name: 'author',
      type: 'relationship',
      relationTo: 'users',
      required: true,
      defaultValue: ({ user }) => user?.id,
    },
    { name: 'categories', type: 'relationship', relationTo: 'categories', hasMany: true },
    { name: 'tags', type: 'relationship', relationTo: 'tags', hasMany: true },
    { name: 'publishedAt', type: 'date' },
    {
      name: 'seo',
      type: 'group',
      fields: [
        { name: 'metaTitle', type: 'text' },
        { name: 'metaDescription', type: 'textarea' },
        { name: 'ogImage', type: 'upload', relationTo: 'media' },
      ],
    },
  ],
  hooks: {
    beforeChange: [
      ({ data, operation }) => {
        if (operation === 'create' && data.title && !data.slug) {
          data.slug = slugify(data.title, { lower: true, strict: true })
        }
        if (data._status === 'published' && !data.publishedAt) {
          data.publishedAt = new Date().toISOString()
        }
        return data
      },
    ],
    afterChange: [
      ({ doc, previousDoc, req: { context } }) => {
        if (context?.disableRevalidate) return doc
        if (doc._status === 'published') {
          revalidatePath(`/posts/${doc.slug}`)
          revalidateTag('posts')
        }
        if (previousDoc?.slug && previousDoc.slug !== doc.slug) {
          revalidatePath(`/posts/${previousDoc.slug}`)
        }
        return doc
      },
    ],
    afterDelete: [
      ({ doc }) => {
        revalidatePath(`/posts/${doc.slug}`)
        revalidateTag('posts')
      },
    ],
  },
}
```

## `payload.config.ts`

```ts
import { buildConfig } from 'payload'
import { postgresAdapter } from '@payloadcms/db-postgres'
import { lexicalEditor, FixedToolbarFeature, HeadingFeature, LinkFeature, UploadFeature } from '@payloadcms/richtext-lexical'
import { s3Storage } from '@payloadcms/storage-s3'
import { resendAdapter } from '@payloadcms/email-resend'
import path from 'path'
import { fileURLToPath } from 'url'
import { Users } from './collections/Users'
import { Media } from './collections/Media'
import { Tags } from './collections/Tags'
import { Categories } from './collections/Categories'
import { Posts } from './collections/Posts'

const filename = fileURLToPath(import.meta.url)
const dirname = path.dirname(filename)

export default buildConfig({
  admin: { user: 'users', importMap: { baseDir: path.resolve(dirname) } },
  collections: [Users, Media, Categories, Tags, Posts],
  editor: lexicalEditor({
    features: ({ defaultFeatures }) => [
      ...defaultFeatures,
      FixedToolbarFeature(),
      HeadingFeature({ enabledHeadingSizes: ['h2', 'h3', 'h4'] }),
      LinkFeature({ enabledCollections: ['posts'] }),
      UploadFeature({ collections: { media: { fields: [{ name: 'caption', type: 'textarea' }] } } }),
    ],
  }),
  db: postgresAdapter({ pool: { connectionString: process.env.DATABASE_URI } }),
  secret: process.env.PAYLOAD_SECRET || '',
  typescript: { outputFile: path.resolve(dirname, 'payload-types.ts') },
  plugins: [
    s3Storage({
      collections: { media: true },
      bucket: process.env.S3_BUCKET || '',
      config: {
        endpoint: process.env.S3_ENDPOINT,
        region: 'auto',
        credentials: {
          accessKeyId: process.env.S3_ACCESS_KEY_ID || '',
          secretAccessKey: process.env.S3_SECRET_ACCESS_KEY || '',
        },
        forcePathStyle: true,
      },
    }),
  ],
  email: resendAdapter({
    defaultFromAddress: 'no-reply@example.com',
    defaultFromName: 'Blog',
    apiKey: process.env.RESEND_API_KEY || '',
  }),
})
```

## Frontend Pages

### `src/app/(frontend)/posts/page.tsx`

```tsx
import { getPayload } from 'payload'
import config from '@payload-config'
import Link from 'next/link'

export const revalidate = 60

export default async function PostsList() {
  const payload = await getPayload({ config })
  const { docs } = await payload.find({
    collection: 'posts',
    where: { _status: { equals: 'published' } },
    sort: '-publishedAt',
    limit: 20,
    depth: 1,
    select: { title: true, slug: true, excerpt: true, heroImage: true, publishedAt: true, author: true },
  })

  return (
    <ul>
      {docs.map((p) => (
        <li key={p.id}>
          <Link href={`/posts/${p.slug}`}>
            <h2>{p.title}</h2>
            <p>{p.excerpt}</p>
          </Link>
        </li>
      ))}
    </ul>
  )
}
```

### `src/app/(frontend)/posts/[slug]/page.tsx`

```tsx
import { getPayload } from 'payload'
import config from '@payload-config'
import { notFound } from 'next/navigation'
import { draftMode } from 'next/headers'
import { RichText } from '@payloadcms/richtext-lexical/react'

export const revalidate = 3600

export async function generateStaticParams() {
  const payload = await getPayload({ config })
  const { docs } = await payload.find({
    collection: 'posts',
    where: { _status: { equals: 'published' } },
    limit: 1000,
    select: { slug: true },
  })
  return docs.map((p) => ({ slug: p.slug }))
}

export default async function PostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const { isEnabled: isDraft } = await draftMode()
  const payload = await getPayload({ config })

  const { docs } = await payload.find({
    collection: 'posts',
    where: { slug: { equals: slug } },
    draft: isDraft,
    limit: 1,
    depth: 2,
  })

  const post = docs[0]
  if (!post) return notFound()

  return (
    <article>
      <h1>{post.title}</h1>
      <p>{post.excerpt}</p>
      {/* @ts-expect-error — Lexical generic */}
      <RichText data={post.content} />
    </article>
  )
}
```

### `src/app/(frontend)/api/preview/route.ts`

```ts
import { draftMode } from 'next/headers'
import { redirect } from 'next/navigation'

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url)
  if (searchParams.get('secret') !== process.env.PREVIEW_SECRET) {
    return new Response('Invalid token', { status: 401 })
  }
  ;(await draftMode()).enable()
  redirect(searchParams.get('path') || '/')
}
```

## What This Demonstrates

- Drafts + autosave + live preview wired end-to-end.
- ISR with on-save revalidation hook (handles slug change and delete).
- Public-vs-authored access pattern (`isAdminOrAuthor` row-level rule).
- Lexical with custom features (toolbar, headings, links, upload-with-caption).
- S3-compatible storage, Resend email, Postgres adapter.
- Type-safe Server Component fetches with `select`.

## Next Steps to Extend

- Add `categories` and `tags` index pages (`/categories/[slug]`, `/tags/[slug]`).
- Replace generic `seo` group with `@payloadcms/plugin-seo` for sitemap/robots integration.
- Add a `comments` collection (auth-only create, public read).
- Use `@payloadcms/plugin-search` for full-text search.
