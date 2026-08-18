# Scenario: Product Catalog with Directus + Next.js

Build an e-commerce catalog with products, categories, image galleries, and dynamic filtering.

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
| `price` | Decimal | Product price |
| `currency` | String (default: "USD") | Price currency |
| `sku` | String (unique) | Stock keeping unit |
| `featured_image` | File (M2O → directus_files) | Main product image |
| `category` | M2O → categories | Primary category |
| `date_created` | Timestamp (auto) | System field |

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
  price: number;
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

## Products Listing with Filtering

```typescript
// app/products/page.tsx
import directus from '@/lib/directus';
import { readItems } from '@directus/sdk';
import Image from 'next/image';
import Link from 'next/link';
import { directusAsset } from '@/lib/directus-asset';

export const revalidate = 60;

interface Props {
  searchParams: Promise<{ category?: string; search?: string; sort?: string }>;
}

export default async function ProductsPage({ searchParams }: Props) {
  const { category, search, sort } = await searchParams;

  // Build Directus filter from search params
  const filter: Record<string, unknown> = { status: { _eq: 'published' } };
  if (category) {
    filter['category'] = { slug: { _eq: category } };
  }

  const products = await directus.request(
    readItems('products', {
      filter,
      search: search || undefined,
      sort: [sort === 'price-asc' ? 'price' : sort === 'price-desc' ? '-price' : '-date_created'],
      fields: ['id', 'name', 'slug', 'price', 'currency', 'featured_image', 'category.name', 'category.slug'],
      limit: 50,
    })
  );

  const categories = await directus.request(
    readItems('categories', {
      sort: ['sort'],
      fields: ['name', 'slug'],
    })
  );

  return (
    <main>
      <h1>Products</h1>

      {/* Category filter */}
      <nav>
        <Link href="/products">All</Link>
        {categories.map((cat) => (
          <Link
            key={cat.slug}
            href={`/products?category=${cat.slug}`}
            style={{ fontWeight: category === cat.slug ? 'bold' : 'normal' }}
          >
            {cat.name}
          </Link>
        ))}
      </nav>

      {/* Sort options */}
      <div>
        <Link href={`/products?${new URLSearchParams({ ...{ category: category || '' }, sort: 'price-asc' })}`}>
          Price: Low to High
        </Link>
        <Link href={`/products?${new URLSearchParams({ ...{ category: category || '' }, sort: 'price-desc' })}`}>
          Price: High to Low
        </Link>
      </div>

      {/* Product grid */}
      <div>
        {products.map((product) => (
          <article key={product.id}>
            {product.featured_image && (
              <Image
                src={directusAsset(product.featured_image, { width: 400, height: 400, fit: 'cover' })!}
                alt={product.name}
                width={400}
                height={400}
              />
            )}
            <h2>
              <Link href={`/products/${product.slug}`}>{product.name}</Link>
            </h2>
            <p>
              {new Intl.NumberFormat('en-US', { style: 'currency', currency: product.currency }).format(product.price)}
            </p>
          </article>
        ))}
      </div>
    </main>
  );
}
```

## Product Detail with Image Gallery

```typescript
// app/products/[slug]/page.tsx
import directus from '@/lib/directus';
import { readItems } from '@directus/sdk';
import Image from 'next/image';
import { notFound } from 'next/navigation';
import { directusAsset } from '@/lib/directus-asset';

export async function generateStaticParams() {
  const products = await directus.request(
    readItems('products', {
      filter: { status: { _eq: 'published' } },
      fields: ['slug'],
    })
  );
  return products.map((p) => ({ slug: p.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const [product] = await directus.request(
    readItems('products', {
      filter: { slug: { _eq: slug } },
      fields: ['name', 'description', 'price', 'currency', 'featured_image'],
      limit: 1,
    })
  );
  if (!product) return {};
  return {
    title: product.name,
    description: `${product.name} - ${new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: product.currency,
    }).format(product.price)}`,
    openGraph: {
      images: product.featured_image
        ? [directusAsset(product.featured_image, { width: 1200, height: 630, fit: 'cover' })!]
        : [],
    },
  };
}

export default async function ProductPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;

  const [product] = await directus.request(
    readItems('products', {
      filter: { slug: { _eq: slug }, status: { _eq: 'published' } },
      fields: ['*', 'category.*'],
      limit: 1,
    })
  );

  if (!product) notFound();

  // Fetch gallery images
  const gallery = await directus.request(
    readItems('product_images', {
      filter: { product: { _eq: product.id } },
      sort: ['sort'],
      fields: ['image', 'alt_text'],
    })
  );

  const category = typeof product.category === 'object' ? product.category : null;

  return (
    <main>
      {/* Image gallery */}
      <div>
        {product.featured_image && (
          <Image
            src={directusAsset(product.featured_image, { width: 800, height: 800, fit: 'contain' })!}
            alt={product.name}
            width={800}
            height={800}
            priority
          />
        )}
        {gallery.map((img) => (
          <Image
            key={img.image}
            src={directusAsset(img.image, { width: 200, height: 200, fit: 'cover' })!}
            alt={img.alt_text}
            width={200}
            height={200}
          />
        ))}
      </div>

      {/* Product info */}
      <div>
        {category && <span>{category.name}</span>}
        <h1>{product.name}</h1>
        <p>
          {new Intl.NumberFormat('en-US', { style: 'currency', currency: product.currency }).format(product.price)}
        </p>
        <div dangerouslySetInnerHTML={{ __html: product.description }} />
      </div>
    </main>
  );
}
```

## Category Page

```typescript
// app/categories/[slug]/page.tsx
import directus from '@/lib/directus';
import { readItems } from '@directus/sdk';
import Link from 'next/link';
import { notFound } from 'next/navigation';

export async function generateStaticParams() {
  const categories = await directus.request(readItems('categories', { fields: ['slug'] }));
  return categories.map((c) => ({ slug: c.slug }));
}

export default async function CategoryPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;

  const [category] = await directus.request(
    readItems('categories', { filter: { slug: { _eq: slug } }, fields: ['*'], limit: 1 })
  );
  if (!category) notFound();

  const products = await directus.request(
    readItems('products', {
      filter: { status: { _eq: 'published' }, category: { slug: { _eq: slug } } },
      fields: ['name', 'slug', 'price', 'currency', 'featured_image'],
    })
  );

  return (
    <main>
      <h1>{category.name}</h1>
      <p>{category.description}</p>
      {/* Render product grid same as products listing */}
    </main>
  );
}
```

## Revalidation Strategy

- Product listing: `revalidate = 60` (ISR every 60 seconds)
- Product detail: Static at build via `generateStaticParams`, revalidated on-demand
- Category pages: Static at build, revalidated when products change
- Directus Automate: Webhook to `/api/revalidate?secret=...&tag=products` on item.create/update in `products` collection
