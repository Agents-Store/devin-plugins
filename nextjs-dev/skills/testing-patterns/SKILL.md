---
name: testing-patterns
description: >
  Next.js testing patterns with Vitest and Playwright. Use when the user asks about
  "testing Next.js", "unit tests", "integration tests", "E2E tests", "Vitest with Next.js",
  "Playwright", "testing Server Components", "testing Server Actions", "testing Route Handlers",
  "mocking next/navigation", "mocking next/headers", or needs guidance on test setup and
  patterns for App Router applications.
---

# Testing Patterns

## Types of Tests

| Type | Tool | What it tests |
|------|------|---------------|
| Unit / Component | **Vitest** + React Testing Library | Individual components, hooks, utils |
| End-to-End | **Playwright** | Full user flows in a real browser |
| Snapshot | **Vitest** | Component rendered output stability |

> **Note:** `async` Server Components are not fully supported in unit test frameworks yet. Use E2E testing for `async` Server Components.

## Vitest Setup

### Installation

```bash
npm install -D vitest @vitejs/plugin-react jsdom @testing-library/react @testing-library/dom @testing-library/jest-dom
```

### Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest.setup.ts'],
    css: true,
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

```typescript
// vitest.setup.ts
import '@testing-library/jest-dom/vitest'
```

### Add test script

```json
// package.json
{
  "scripts": {
    "test": "vitest",
    "test:run": "vitest run",
    "test:coverage": "vitest run --coverage"
  }
}
```

## Testing Client Components

```tsx
// src/components/counter.tsx
'use client'

import { useState } from 'react'

export function Counter() {
  const [count, setCount] = useState(0)
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  )
}
```

```tsx
// src/components/__tests__/counter.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { Counter } from '../counter'

describe('Counter', () => {
  it('renders initial count of 0', () => {
    render(<Counter />)
    expect(screen.getByText('Count: 0')).toBeInTheDocument()
  })

  it('increments count on click', () => {
    render(<Counter />)
    fireEvent.click(screen.getByRole('button', { name: /increment/i }))
    expect(screen.getByText('Count: 1')).toBeInTheDocument()
  })
})
```

## Mocking `next/navigation`

```tsx
// src/components/__tests__/nav-component.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock next/navigation
const pushMock = vi.fn()
const replaceMock = vi.fn()

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: pushMock,
    replace: replaceMock,
    back: vi.fn(),
    forward: vi.fn(),
    refresh: vi.fn(),
    prefetch: vi.fn(),
  }),
  usePathname: () => '/current-path',
  useSearchParams: () => new URLSearchParams('q=test'),
  useParams: () => ({ id: '123' }),
}))

import { SearchForm } from '../search-form'

describe('SearchForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('navigates on submit', () => {
    render(<SearchForm />)
    const input = screen.getByRole('textbox')
    fireEvent.change(input, { target: { value: 'nextjs' } })
    fireEvent.submit(screen.getByRole('form'))
    expect(pushMock).toHaveBeenCalledWith('/search?q=nextjs')
  })
})
```

## Mocking `next/headers`

For testing code that uses `cookies()` or `headers()`:

```typescript
// src/lib/__tests__/session.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'

const mockCookies = {
  get: vi.fn(),
  set: vi.fn(),
  delete: vi.fn(),
}

vi.mock('next/headers', () => ({
  cookies: vi.fn(async () => mockCookies),
  headers: vi.fn(async () => new Headers({ 'x-custom': 'value' })),
}))

import { getSession, deleteSession } from '../session'

describe('Session', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('returns null when no session cookie', async () => {
    mockCookies.get.mockReturnValue(undefined)
    const session = await getSession()
    expect(session).toBeNull()
  })

  it('deletes session cookie', async () => {
    await deleteSession()
    expect(mockCookies.delete).toHaveBeenCalledWith('session')
  })
})
```

## Testing Server Actions

Mock the dependencies, test the logic:

```typescript
// src/app/actions/__tests__/post-actions.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock dependencies
vi.mock('next/cache', () => ({
  revalidatePath: vi.fn(),
  revalidateTag: vi.fn(),
}))

vi.mock('next/navigation', () => ({
  redirect: vi.fn(),
}))

vi.mock('@/lib/db', () => ({
  db: {
    post: {
      create: vi.fn(),
      delete: vi.fn(),
    },
  },
}))

import { createPost } from '../post-actions'
import { revalidatePath } from 'next/cache'
import { db } from '@/lib/db'

describe('createPost', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('creates a post with valid data', async () => {
    const formData = new FormData()
    formData.set('title', 'Test Post')
    formData.set('content', 'Test content that is long enough')

    vi.mocked(db.post.create).mockResolvedValue({ id: '1', title: 'Test Post' })

    const result = await createPost({ message: '' }, formData)

    expect(db.post.create).toHaveBeenCalled()
    expect(revalidatePath).toHaveBeenCalledWith('/posts')
    expect(result.success).toBe(true)
  })

  it('returns validation errors for invalid data', async () => {
    const formData = new FormData()
    formData.set('title', '')
    formData.set('content', 'short')

    const result = await createPost({ message: '' }, formData)

    expect(result.errors).toBeDefined()
    expect(db.post.create).not.toHaveBeenCalled()
  })
})
```

## Testing Route Handlers

Create mock `NextRequest` objects:

```typescript
// src/app/api/__tests__/posts.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { NextRequest } from 'next/server'

vi.mock('@/lib/db', () => ({
  db: {
    post: {
      findMany: vi.fn(),
      create: vi.fn(),
    },
  },
}))

import { GET, POST } from '../posts/route'
import { db } from '@/lib/db'

describe('GET /api/posts', () => {
  it('returns posts as JSON', async () => {
    const mockPosts = [{ id: '1', title: 'Test' }]
    vi.mocked(db.post.findMany).mockResolvedValue(mockPosts)

    const request = new NextRequest('http://localhost:3000/api/posts')
    const response = await GET(request)
    const data = await response.json()

    expect(response.status).toBe(200)
    expect(data).toEqual(mockPosts)
  })

  it('handles query params', async () => {
    vi.mocked(db.post.findMany).mockResolvedValue([])

    const request = new NextRequest('http://localhost:3000/api/posts?page=2&limit=5')
    await GET(request)

    expect(db.post.findMany).toHaveBeenCalledWith(
      expect.objectContaining({ skip: 5, take: 5 })
    )
  })
})

describe('POST /api/posts', () => {
  it('creates a post and returns 201', async () => {
    const newPost = { id: '1', title: 'New Post', content: 'Content' }
    vi.mocked(db.post.create).mockResolvedValue(newPost)

    const request = new NextRequest('http://localhost:3000/api/posts', {
      method: 'POST',
      body: JSON.stringify({ title: 'New Post', content: 'Content' }),
      headers: { 'Content-Type': 'application/json' },
    })

    const response = await POST(request)
    const data = await response.json()

    expect(response.status).toBe(201)
    expect(data.title).toBe('New Post')
  })

  it('returns 422 for invalid body', async () => {
    const request = new NextRequest('http://localhost:3000/api/posts', {
      method: 'POST',
      body: JSON.stringify({ title: '' }),
      headers: { 'Content-Type': 'application/json' },
    })

    const response = await POST(request)
    expect(response.status).toBe(422)
  })
})
```

## Playwright E2E Setup

### Installation

```bash
npm install -D @playwright/test
npx playwright install
```

### Configuration

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

### Writing E2E Tests

```typescript
// e2e/home.spec.ts
import { test, expect } from '@playwright/test'

test('homepage has correct title', async ({ page }) => {
  await page.goto('/')
  await expect(page).toHaveTitle(/My App/)
})

test('navigation works', async ({ page }) => {
  await page.goto('/')
  await page.click('text=About')
  await expect(page).toHaveURL('/about')
  await expect(page.locator('h1')).toContainText('About')
})
```

### Auth State Reuse

Save auth state once and reuse across tests:

```typescript
// e2e/auth.setup.ts
import { test as setup, expect } from '@playwright/test'

const authFile = 'e2e/.auth/user.json'

setup('authenticate', async ({ page }) => {
  await page.goto('/login')
  await page.fill('input[name="email"]', 'test@example.com')
  await page.fill('input[name="password"]', 'password123')
  await page.click('button[type="submit"]')
  await expect(page).toHaveURL('/dashboard')

  // Save auth state
  await page.context().storageState({ path: authFile })
})
```

```typescript
// playwright.config.ts — add setup project
export default defineConfig({
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: 'e2e/.auth/user.json',
      },
      dependencies: ['setup'],
    },
  ],
})
```

### Testing Forms E2E

```typescript
// e2e/create-post.spec.ts
import { test, expect } from '@playwright/test'

test('creates a new post', async ({ page }) => {
  await page.goto('/posts/create')

  await page.fill('input[name="title"]', 'E2E Test Post')
  await page.fill('textarea[name="content"]', 'This is test content')
  await page.click('button[type="submit"]')

  // Should redirect to posts list
  await expect(page).toHaveURL('/posts')
  await expect(page.locator('text=E2E Test Post')).toBeVisible()
})

test('shows validation errors', async ({ page }) => {
  await page.goto('/posts/create')

  // Submit empty form
  await page.click('button[type="submit"]')

  // Should show validation messages
  await expect(page.locator('text=Title is required')).toBeVisible()
})
```

### Instant Navigation Regression Tests (Next.js 16.3)

With Cache Components + Partial Prefetching enabled, `@next/playwright` provides an `instant()` helper to assert that content is visible instantly during navigation (no loading gap):

```typescript
import { test, expect } from '@playwright/test'
import { instant } from '@next/playwright'

test('product page navigates instantly', async ({ page }) => {
  await page.goto('/')
  await instant(page, async () => {
    await page.click('a[href="/products/1"]')
    await expect(page.locator('h1')).toBeVisible()
  })
})
```

See [/docs/app/guides/instant-navigation#prevent-regressions-with-e2e-tests](https://nextjs.org/docs/app/guides/instant-navigation#prevent-regressions-with-e2e-tests).

## CI Integration & File Organization

For GitHub Actions workflows and test file organization conventions, see `references/ci-and-organization.md`.

## What This Skill Does NOT Cover

- Visual regression testing (Chromatic, Percy)
- Load testing and performance benchmarks
- Specific assertion library APIs beyond basics
- Database seeding and test fixtures (ORM-specific)
- Testing third-party integrations (mock them)
