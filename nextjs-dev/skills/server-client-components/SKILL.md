---
name: server-client-components
description: Server and Client Component patterns in Next.js App Router. This skill should be used when the user asks about "Server Components", "Client Components", "'use client' directive", "when to use Server vs Client components", "component boundaries", "interleaving components", "context providers in Next.js", or needs guidance on the server/client rendering split.
---

# Server and Client Components

In the App Router, all components are Server Components by default. Client Components are opted into with the `'use client'` directive. Understanding when to use each and how to compose them is essential for building performant Next.js apps.

## Decision Matrix

Use **Server Components** when you need to:
- Fetch data from databases or APIs close to the source
- Use API keys, tokens, and secrets without exposing them to the client
- Reduce the amount of JavaScript sent to the browser
- Improve First Contentful Paint and stream content progressively

Use **Client Components** when you need to:
- Interactivity — `onClick`, `onChange`, form state
- React state — `useState`, `useReducer`
- Lifecycle effects — `useEffect`
- Browser APIs — `localStorage`, `window`, `navigator.geolocation`
- Custom hooks that use state or effects

## The `'use client'` Boundary

Add `'use client'` at the top of a file to mark it as a Client Component:

```tsx
'use client'

import { useState } from 'react'

export default function Counter() {
  const [count, setCount] = useState(0)
  return <button onClick={() => setCount(count + 1)}>{count}</button>
}
```

`'use client'` declares a boundary between Server and Client module graphs. Once a file has `'use client'`, all its imports and child components become part of the client bundle. Do not add the directive to every interactive component — add it at the highest boundary needed.

## Minimize Client Boundaries

Push `'use client'` as far down the component tree as possible. Keep layouts and data-fetching components as Server Components:

```tsx
// app/layout.tsx — Server Component (no 'use client')
import Search from './search'
import Logo from './logo'

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <nav>
        <Logo />       {/* Server Component — no JS sent */}
        <Search />     {/* Client Component — interactive */}
      </nav>
      <main>{children}</main>
    </>
  )
}
```

```tsx
// app/search.tsx
'use client'

export default function Search() {
  // Uses state, event handlers — needs client
  return <input type="search" onChange={/* ... */} />
}
```

This pattern keeps the majority of the layout server-rendered and only ships JavaScript for the interactive search bar.

## Passing Data: Server to Client

Pass data from Server Components to Client Components via props. Props must be serializable (no functions, classes, or Dates without conversion):

```tsx
// app/[id]/page.tsx — Server Component
import LikeButton from './like-button'
import { getPost } from '@/lib/data'

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const post = await getPost(id)
  // Pass only the serializable data the Client Component needs
  return <LikeButton postId={post.id} initialLikes={post.likes} />
}
```

```tsx
// app/[id]/like-button.tsx — Client Component
'use client'

import { useState } from 'react'

export default function LikeButton({ postId, initialLikes }: { postId: string; initialLikes: number }) {
  const [count, setCount] = useState(initialLikes)
  return <button onClick={() => setCount(c => c + 1)}>{count} likes</button>
}
```

Be explicit about what crosses the boundary — pass specific primitive props (strings, numbers) rather than entire objects when possible. This makes the serialization contract clear and keeps the Client Component lightweight.

## Interleaving: Server Components Inside Client Components

Pass Server Components as `children` or other props to Client Components:

```tsx
// app/ui/modal.tsx — Client Component
'use client'

import { useState } from 'react'

export default function Modal({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false)
  return (
    <>
      <button onClick={() => setIsOpen(true)}>Open</button>
      {isOpen && <div className="modal">{children}</div>}
    </>
  )
}
```

```tsx
// app/page.tsx — Server Component
import Modal from './ui/modal'
import Cart from './ui/cart'  // Server Component that fetches data

export default function Page() {
  return (
    <Modal>
      <Cart />  {/* Rendered on server, passed as children */}
    </Modal>
  )
}
```

The `<Cart />` Server Component renders on the server. The `<Modal>` Client Component receives its rendered output as `children`. This pattern avoids pulling data-fetching logic into the client bundle.

## Context Providers

React context requires `'use client'`. Create a wrapper Client Component and use it in a Server Component layout:

```tsx
// app/providers.tsx
'use client'

import { ThemeProvider } from 'next-themes'
import { SessionProvider } from 'next-auth/react'

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider>
      <ThemeProvider attribute="class" defaultTheme="system">
        {children}
      </ThemeProvider>
    </SessionProvider>
  )
}
```

```tsx
// app/layout.tsx — Server Component
import Providers from './providers'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
```

Render providers as deep as possible in the tree. Wrap only `{children}`, not the entire `<html>` document, so Next.js can optimize the static parts.

## Third-Party Component Wrapping

Third-party components that use client features but lack `'use client'` must be wrapped:

```tsx
// app/carousel.tsx
'use client'

import { Carousel } from 'acme-carousel'

export default Carousel
```

Now `<Carousel />` can be used inside Server Components:

```tsx
// app/page.tsx — Server Component
import Carousel from './carousel'

export default function Page() {
  return <Carousel />
}
```

## Environment Poisoning Prevention

Every data-access module that touches databases, API keys, or secrets should start with `import 'server-only'`. This causes a build-time error if the module is accidentally imported in a Client Component — catching the leak before it reaches production:

```tsx
// lib/data.ts
import 'server-only'  // Build fails if any Client Component imports this file

export async function getData() {
  const res = await fetch('https://api.example.com/data', {
    headers: { authorization: process.env.API_KEY! },
  })
  return res.json()
}
```

```tsx
// lib/products.ts
import 'server-only'

export async function getProduct(slug: string) { /* ... */ }
export async function getAllProducts() { /* ... */ }
```

Install both guard packages:

```bash
npm install server-only client-only
```

Use `import 'client-only'` in modules that depend on browser APIs (`localStorage`, `window`) to prevent accidental server-side usage.

Only env vars prefixed with `NEXT_PUBLIC_` are included in the client bundle. Unprefixed variables are replaced with empty strings on the client. Never put secrets in `NEXT_PUBLIC_*` variables.

## Shared Types Across Server/Client Boundary

When Server and Client Components share types, extract them into a standalone types file. Type-only files have no runtime code, so they don't affect bundling:

```tsx
// types/product.ts — shared between server and client
export interface Product {
  id: string
  name: string
  slug: string
  price: number
  image: string
}

export interface CartItem {
  product: Product
  quantity: number
}
```

```tsx
// lib/products.ts — Server-only data layer
import 'server-only'
import type { Product } from '@/types/product'

export async function getProduct(slug: string): Promise<Product | null> { /* ... */ }
```

```tsx
// components/add-to-cart.tsx — Client Component
'use client'
import type { Product } from '@/types/product'

export function AddToCartButton({ product }: { product: Product }) { /* ... */ }
```

The `import type` syntax ensures types are stripped at build time and never affect bundle size.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Adding `'use client'` to the root layout | Move interactive parts to child Client Components |
| Importing a Server Component into a Client Component file | Pass as `children` prop instead |
| Using `useEffect` for data fetching | Fetch in Server Components or use Server Actions |
| Passing non-serializable props (functions, Date objects) to Client Components | Serialize data before passing; move callbacks to Client Components |
| Adding `'use client'` to every component | Only add at the boundary — child components inherit client status |
