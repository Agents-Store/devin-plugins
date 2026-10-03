# Scenario: Product Catalog with Directus + Next.js

Build an e-commerce catalog with products, categories, image galleries and dynamic filtering. Uses the boundary rules of `directus-to-nextjs` (tagged reads, asset URLs without a token) and the revalidation pipeline of `deployment`.

## Directus Collections

### `categories`

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `name` | String | Category name |
| `slug` | String (unique) | URL identifier |
| `description` | Text | Category description |
| `image` | File (M2O → directus_files) | Category image |
| `sort` | Integer | Display order |

### `products`

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `status` | String | draft / published / archived |
| `name` | String | Product name |
| `slug` | String (unique) | URL identifier |
| `description` | WYSIWYG | Full product description |
| `price` | Decimal | Product price. Arrives as a string (`"19.99"`) |
| `currency` | String (default: "USD") | Price currency |
| `sku` | String (unique) | Stock keeping unit |
| `featured_image` | File (M2O → directus_files) | Main product image |
| `category` | M2O → categories | Primary category |
| `date_created` | Timestamp (auto) | System field |

A new collection in Directus 12 gets a boolean `archived` field instead of a `status` dropdown. This scenario models `status`; with `archived`, filter on `{ archived: { _eq: false } }` and change the type to match.

### `product_images` (gallery)

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `product` | M2O → products | Parent product |
| `image` | File (M2O → directus_files) | Gallery image |
| `sort` | Integer | Display order |
| `alt_text` | String | Image alt text |

## TypeScript Types

```typescript
// types/directus.ts
export interface Category {
  id: string;
  name: string;
  slug: string;
  description: string;
  image: string | null;
  sort: number;
}

export interface Product {
  id: string;
  status: 'draft' | 'published' | 'archived';
  name: string;
  slug: string;
  description: string;
  price: string; // decimal fields arrive as strings; use Number(product.price) to format
  currency: string;
  sku: string;
  featured_image: string | null;
  category: string | Category;
  date_created: string;
}

export interface ProductImage {
  id: string;
  product: string | Product;
  image: string;
  sort: number;
  alt_text: string;
}

export interface Schema {
  products: Product[];
  categories: Category[];
  product_images: ProductImage[];
}
```

## Reads

One module, every read tagged with the collections it reads. A search string makes an unbounded number of distinct requests, so a search bypasses the cache; the listing without a search is cached per filter and sort:

```typescript
// lib/content/products.ts
import 'server-only';
import { cache } from 'react';
import { readItems, type QueryFilter } from '@directus/sdk';
import { requestTagged } from '@/lib/directus-tagged';
import type { Product, Schema } from '@/types/directus';

const ONE_HOUR = 3600;
const LIST_TAGS = ['products', 'categories'];

const SORTS = {
  'price-asc': 'price',
  'price-desc': '-price',
  newest: '-date_created',
} as const;
export type SortKey = keyof typeof SORTS;

// hasOwn, not `in`: a URL value such as "toString" must not pass
function sortKey(value: string | undefined): SortKey {
  return value !== undefined && Object.hasOwn(SORTS, value) ? (value as SortKey) : 'newest';
}

export interface ProductQuery {
  category?: string;
  search?: string;
  sort?: string;
}

export const getProducts = cache(async ({ category, search, sort }: ProductQuery) => {
  const published: QueryFilter<Schema, Product> = { status: { _eq: 'published' } };
  const filter: QueryFilter<Schema, Product> = category
    ? { _and: [published, { category: { slug: { _eq: category } } }] }
    : published;

  return requestTagged(
    readItems('products', {
      filter,
      search: search || undefined,
      // Only values of SORTS reach Directus: the text from the URL is never used as a sort field
      sort: [SORTS[sortKey(sort)]],
      fields: ['id', 'name', 'slug', 'price', 'currency', 'featured_image', { category: ['name', 'slug'] }],
      limit: 50,
    }),
    LIST_TAGS,
    search ? 'no-store' : ONE_HOUR, // a search is never cached
  );
});

export const getCategories = cache(async () =>
  requestTagged(readItems('categories', { sort: ['sort'], fields: ['name', 'slug'] }), ['categories'], ONE_HOUR),
);

export const getProductSlugs = cache(async () => {
  const products = await requestTagged(
    readItems('products', { filter: { status: { _eq: 'published' } }, fields: ['slug'], limit: -1 }),
    ['products'],
    ONE_HOUR,
  );
  return products.map((product) => product.slug);
});

export const getProductBySlug = cache(async (slug: string) => {
  const [product] = await requestTagged(
    readItems('products', {
      filter: { slug: { _eq: slug }, status: { _eq: 'published' } },
      fields: ['*', { category: ['name', 'slug'] }],
      limit: 1,
    }),
    ['products', 'categories'],
    ONE_HOUR,
  );
  return product ?? null;
});

export const getGallery = cache(async (productId: string) =>
  requestTagged(
    readItems('product_images', {
      filter: { product: { _eq: productId } },
      sort: ['sort'],
      fields: ['image', 'alt_text'],
    }),
    ['product_images'],
    ONE_HOUR,
  ),
);
```

## Products Listing with Filtering

`searchParams` is request data, so this page renders per request; the cache lives in the reads above.

```typescript
// app/products/page.tsx
import Image from 'next/image';
import Link from 'next/link';
import { directusAsset } from '@/lib/directus-asset';
import { getCategories, getProducts } from '@/lib/content/products';

interface Props {
  searchParams: Promise<{ category?: string; search?: string; sort?: string }>;
}

export default async function ProductsPage({ searchParams }: Props) {
  const { category, search, sort } = await searchParams;
  const [products, categories] = await Promise.all([getProducts({ category, search, sort }), getCategories()]);

  return (
    <main>
      <h1>Products</h1>

      {/* Category filter */}
      <nav>
        <Link href="/products">All</Link>
        {categories.map((cat) => (
          <Link
            key={cat.slug}
            href={`/products?category=${encodeURIComponent(cat.slug)}`}
            style={{ fontWeight: category === cat.slug ? 'bold' : 'normal' }}
          >
            {cat.name}
          </Link>
        ))}
      </nav>

      {/* Sort options */}
      <div>
        <Link href={`/products?${new URLSearchParams({ category: category ?? '', sort: 'price-asc' })}`}>
          Price: Low to High
        </Link>
        <Link href={`/products?${new URLSearchParams({ category: category ?? '', sort: 'price-desc' })}`}>
          Price: High to Low
        </Link>
      </div>

      {/* Product grid */}
      <div>
        {products.map((product) => {
          const image = directusAsset(product.featured_image, { width: 400, height: 400, fit: 'cover' });
          return (
            <article key={product.id}>
              {image && <Image src={image} alt={product.name} width={400} height={400} />}
              <h2>
                <Link href={`/products/${product.slug}`}>{product.name}</Link>
              </h2>
              <p>
                {new Intl.NumberFormat('en-US', { style: 'currency', currency: product.currency }).format(
                  Number(product.price),
                )}
              </p>
            </article>
          );
        })}
      </div>
    </main>
  );
}
```

## Product Detail with Image Gallery

```typescript
// app/products/[slug]/page.tsx
import Image from 'next/image';
import { notFound } from 'next/navigation';
import { directusAsset } from '@/lib/directus-asset';
import { getGallery, getProductBySlug, getProductSlugs } from '@/lib/content/products';

const money = (amount: string, currency: string) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(Number(amount));

export async function generateStaticParams() {
  const slugs = await getProductSlugs();
  return slugs.map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const product = await getProductBySlug(slug);
  if (!product) return {};
  const image = directusAsset(product.featured_image, { width: 1200, height: 630, fit: 'cover' });
  return {
    title: product.name,
    description: `${product.name} - ${money(product.price, product.currency)}`,
    openGraph: { images: image ? [image] : [] },
  };
}

export default async function ProductPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const product = await getProductBySlug(slug);
  if (!product) notFound();

  const gallery = await getGallery(product.id);
  const category = typeof product.category === 'object' ? product.category : null;
  const mainImage = directusAsset(product.featured_image, { width: 800, height: 800, fit: 'contain' });

  return (
    <main>
      {/* Image gallery */}
      <div>
        {mainImage && <Image src={mainImage} alt={product.name} width={800} height={800} priority />}
        {gallery.map((img) => {
          const thumb = directusAsset(img.image, { width: 200, height: 200, fit: 'cover' });
          return thumb ? <Image key={img.image} src={thumb} alt={img.alt_text} width={200} height={200} /> : null;
        })}
      </div>

      {/* Product info */}
      <div>
        {category && <span>{category.name}</span>}
        <h1>{product.name}</h1>
        <p>{money(product.price, product.currency)}</p>
        {/* HTML written by Directus editors: sanitize first if anyone less trusted can write it */}
        <div dangerouslySetInnerHTML={{ __html: product.description }} />
      </div>
    </main>
  );
}
```

## Category Page

```typescript
// app/categories/[slug]/page.tsx
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getCategories, getProducts } from '@/lib/content/products';

export async function generateStaticParams() {
  const categories = await getCategories();
  return categories.map((category) => ({ slug: category.slug }));
}

export default async function CategoryPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const categories = await getCategories();
  const category = categories.find((c) => c.slug === slug);
  if (!category) notFound();

  const products = await getProducts({ category: slug });

  return (
    <main>
      <h1>{category.name}</h1>
      <ul>
        {products.map((product) => (
          <li key={product.id}>
            <Link href={`/products/${product.slug}`}>{product.name}</Link>
          </li>
        ))}
      </ul>
      {/* Render the product grid the same way as the products listing */}
    </main>
  );
}
```

## Revalidation Strategy

- Product reads are tagged `products` (and `categories` where the query expands it); the gallery is tagged `product_images`. Pages carry no `revalidate` export.
- The Directus Flow of `deployment` lists `products`, `categories` and `product_images`; so does `COLLECTION_TAGS` in `/api/revalidate`. A product edit then refreshes the listing, the detail page and the category pages that show it.
- Detail and category pages are generated at build time from `generateStaticParams`; new products and categories render on their first request.
- A search request is never cached, so the cache holds the filter-and-sort combinations visitors actually use, and one hour is its safety net.
