# Scenario: E-Commerce Storefront

Build a public product catalog with ISR, search, product detail pages, image optimization, and a client-side cart.

## Project Structure

```
app/
├── layout.tsx                 # Root layout (fonts, cart provider)
├── page.tsx                   # Home page (featured products)
├── products/
│   ├── page.tsx               # Product catalog with filters
│   ├── loading.tsx            # Product grid skeleton
│   └── [slug]/
│       ├── page.tsx           # Product detail (ISR)
│       └── loading.tsx        # Detail skeleton
├── cart/
│   └── page.tsx               # Cart page (client state)
├── checkout/
│   ├── page.tsx               # Checkout form
│   └── success/
│       └── page.tsx           # Order confirmation
├── api/
│   └── checkout/
│       └── route.ts           # Stripe/payment API
├── components/
│   ├── product-card.tsx       # Server Component
│   ├── product-grid.tsx       # Server Component
│   ├── add-to-cart-button.tsx # Client Component
│   ├── cart-icon.tsx          # Client Component
│   ├── search-filters.tsx     # Client Component
│   └── image-gallery.tsx      # Client Component
├── lib/
│   ├── products.ts            # Product data functions
│   ├── cart-store.ts          # Zustand cart store
│   └── stripe.ts              # Stripe config
└── providers.tsx              # Cart context provider
```

## Step 1: Root Layout with Cart Provider

```tsx
// app/layout.tsx
import { Inter } from 'next/font/google'
import { CartProvider } from './providers'
import { CartIcon } from '@/components/cart-icon'
import Link from 'next/link'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: { default: 'Store', template: '%s | Store' },
  description: 'Modern e-commerce storefront',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.className}>
      <body>
        <CartProvider>
          <header className="border-b">
            <nav className="container mx-auto flex items-center justify-between p-4">
              <Link href="/" className="text-xl font-bold">Store</Link>
              <div className="flex items-center gap-4">
                <Link href="/products">Products</Link>
                <CartIcon />
              </div>
            </nav>
          </header>
          <main>{children}</main>
        </CartProvider>
      </body>
    </html>
  )
}
```

```tsx
// app/providers.tsx
'use client'

import { createContext, useContext, useReducer, type ReactNode } from 'react'

type CartItem = { id: string; name: string; price: number; image: string; quantity: number }
type CartState = { items: CartItem[] }
type CartAction =
  | { type: 'ADD'; item: Omit<CartItem, 'quantity'> }
  | { type: 'REMOVE'; id: string }
  | { type: 'UPDATE_QUANTITY'; id: string; quantity: number }
  | { type: 'CLEAR' }

const CartContext = createContext<{
  state: CartState
  dispatch: React.Dispatch<CartAction>
} | null>(null)

function cartReducer(state: CartState, action: CartAction): CartState {
  switch (action.type) {
    case 'ADD': {
      const existing = state.items.find(i => i.id === action.item.id)
      if (existing) {
        return { items: state.items.map(i => i.id === action.item.id ? { ...i, quantity: i.quantity + 1 } : i) }
      }
      return { items: [...state.items, { ...action.item, quantity: 1 }] }
    }
    case 'REMOVE':
      return { items: state.items.filter(i => i.id !== action.id) }
    case 'UPDATE_QUANTITY':
      return { items: state.items.map(i => i.id === action.id ? { ...i, quantity: action.quantity } : i) }
    case 'CLEAR':
      return { items: [] }
    default:
      return state
  }
}

export function CartProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(cartReducer, { items: [] })
  return <CartContext.Provider value={{ state, dispatch }}>{children}</CartContext.Provider>
}

export function useCart() {
  const context = useContext(CartContext)
  if (!context) throw new Error('useCart must be used within CartProvider')
  return context
}
```

## Step 2: Product Catalog with ISR and Search

```tsx
// app/products/page.tsx
import { Suspense } from 'react'
import { ProductGrid } from '@/components/product-grid'
import { SearchFilters } from '@/components/search-filters'
import { GridSkeleton } from '@/components/skeletons'

export const metadata = { title: 'Products' }
export const revalidate = 60  // ISR: revalidate every 60 seconds

export default async function ProductsPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; category?: string; sort?: string; page?: string }>
}) {
  const params = await searchParams

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Products</h1>
      <SearchFilters currentParams={params} />
      <Suspense key={JSON.stringify(params)} fallback={<GridSkeleton />}>
        <ProductGrid
          query={params.q}
          category={params.category}
          sort={params.sort}
          page={Number(params.page) || 1}
        />
      </Suspense>
    </div>
  )
}
```

```tsx
// components/product-grid.tsx — Server Component
import { getProducts } from '@/lib/products'
import { ProductCard } from './product-card'

export async function ProductGrid({
  query, category, sort, page,
}: {
  query?: string; category?: string; sort?: string; page: number
}) {
  const { products, totalPages } = await getProducts({ query, category, sort, page })

  if (products.length === 0) {
    return <p className="text-gray-500 mt-8">No products found.</p>
  }

  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mt-6">
        {products.map(product => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
      {/* Pagination component */}
    </>
  )
}
```

## Step 3: Product Card with Image Optimization

```tsx
// components/product-card.tsx — Server Component
import Image from 'next/image'
import Link from 'next/link'
import { AddToCartButton } from './add-to-cart-button'

type Product = { id: string; slug: string; name: string; price: number; image: string }

export function ProductCard({ product }: { product: Product }) {
  return (
    <div className="group rounded-lg border overflow-hidden">
      <Link href={`/products/${product.slug}`}>
        <div className="relative aspect-square">
          <Image
            src={product.image}
            alt={product.name}
            fill
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw"
            className="object-cover group-hover:scale-105 transition-transform"
          />
        </div>
      </Link>
      <div className="p-4">
        <Link href={`/products/${product.slug}`}>
          <h3 className="font-medium">{product.name}</h3>
        </Link>
        <p className="text-lg font-bold mt-1">${product.price.toFixed(2)}</p>
        <AddToCartButton
          item={{ id: product.id, name: product.name, price: product.price, image: product.image }}
        />
      </div>
    </div>
  )
}
```

```tsx
// components/add-to-cart-button.tsx — Client Component
'use client'

import { useCart } from '@/app/providers'

type CartItem = { id: string; name: string; price: number; image: string }

export function AddToCartButton({ item }: { item: CartItem }) {
  const { dispatch } = useCart()

  return (
    <button
      onClick={() => dispatch({ type: 'ADD', item })}
      className="w-full mt-2 bg-black text-white py-2 rounded hover:bg-gray-800"
    >
      Add to Cart
    </button>
  )
}
```

## Step 4: Product Detail Page with ISR

```tsx
// app/products/[slug]/page.tsx
import { notFound } from 'next/navigation'
import Image from 'next/image'
import { getProduct, getProducts } from '@/lib/products'
import { AddToCartButton } from '@/components/add-to-cart-button'
import type { Metadata } from 'next'

// Generate static pages for all products at build time
export async function generateStaticParams() {
  const { products } = await getProducts({ page: 1, pageSize: 100 })
  return products.map((p) => ({ slug: p.slug }))
}

// ISR: revalidate product pages every 60 seconds
export const revalidate = 60

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>
}): Promise<Metadata> {
  const { slug } = await params
  const product = await getProduct(slug)
  if (!product) return { title: 'Product Not Found' }
  return {
    title: product.name,
    description: product.description,
    openGraph: { images: [product.image] },
  }
}

export default async function ProductPage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const product = await getProduct(slug)
  if (!product) notFound()

  return (
    <div className="container mx-auto p-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="relative aspect-square">
          <Image
            src={product.image}
            alt={product.name}
            fill
            sizes="(max-width: 768px) 100vw, 50vw"
            priority
            className="object-cover rounded-lg"
          />
        </div>
        <div>
          <h1 className="text-3xl font-bold">{product.name}</h1>
          <p className="text-2xl font-bold mt-2">${product.price.toFixed(2)}</p>
          <p className="text-gray-600 mt-4">{product.description}</p>
          <div className="mt-6">
            <AddToCartButton
              item={{ id: product.id, name: product.name, price: product.price, image: product.image }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
```

## Step 5: Cart Page (Client State)

```tsx
// app/cart/page.tsx
import { CartContents } from '@/components/cart-contents'

export const metadata = { title: 'Cart' }

export default function CartPage() {
  return (
    <div className="container mx-auto p-4 max-w-2xl">
      <h1 className="text-3xl font-bold mb-6">Your Cart</h1>
      <CartContents />
    </div>
  )
}
```

```tsx
// components/cart-contents.tsx
'use client'

import Image from 'next/image'
import Link from 'next/link'
import { useCart } from '@/app/providers'

export function CartContents() {
  const { state, dispatch } = useCart()
  const total = state.items.reduce((sum, item) => sum + item.price * item.quantity, 0)

  if (state.items.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Your cart is empty.</p>
        <Link href="/products" className="text-blue-600 mt-2 inline-block">Browse products</Link>
      </div>
    )
  }

  return (
    <div>
      {state.items.map(item => (
        <div key={item.id} className="flex items-center gap-4 py-4 border-b">
          <Image src={item.image} alt={item.name} width={80} height={80} className="rounded" />
          <div className="flex-1">
            <p className="font-medium">{item.name}</p>
            <p className="text-gray-600">${item.price.toFixed(2)}</p>
          </div>
          <select
            value={item.quantity}
            onChange={(e) => dispatch({ type: 'UPDATE_QUANTITY', id: item.id, quantity: Number(e.target.value) })}
          >
            {[1, 2, 3, 4, 5].map(n => <option key={n} value={n}>{n}</option>)}
          </select>
          <button onClick={() => dispatch({ type: 'REMOVE', id: item.id })} className="text-red-600">
            Remove
          </button>
        </div>
      ))}

      <div className="mt-6 flex justify-between items-center">
        <p className="text-xl font-bold">Total: ${total.toFixed(2)}</p>
        <Link href="/checkout" className="bg-black text-white px-6 py-3 rounded">
          Checkout
        </Link>
      </div>
    </div>
  )
}
```

## Key Patterns Used

1. **ISR** — Product catalog and detail pages revalidate every 60 seconds
2. **`generateStaticParams`** — Pre-render all product pages at build time
3. **Image optimization** — `next/image` with `fill`, `sizes`, `priority` for LCP image
4. **URL state** — Search and filter params in searchParams (shareable URLs)
5. **Client state** — Cart managed with `useReducer` + Context (no server persistence needed for browsing)
6. **Server/Client split** — Product grid and cards are Server Components; cart button and cart page are Client Components
7. **Metadata** — Dynamic `generateMetadata` for product SEO with OpenGraph images
