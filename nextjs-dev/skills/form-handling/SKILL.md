---
name: form-handling
description: >
  Next.js form handling with Server Actions and validation. Use when the user asks about
  "forms in Next.js", "Server Action forms", "useActionState", "form validation",
  "Zod validation", "useFormStatus", "optimistic updates", "useOptimistic",
  "progressive enhancement", "file uploads", or needs guidance on building forms in App Router.
---

# Form Handling

Next.js forms use Server Actions for mutations with progressive enhancement — forms work even without JavaScript.

## Basic Server Action Form

The simplest pattern — a form that calls a Server Action directly:

```tsx
// app/actions.ts
'use server'

import { redirect } from 'next/navigation'
import { revalidatePath } from 'next/cache'

export async function createInvoice(formData: FormData) {
  const rawFormData = {
    customerId: formData.get('customerId') as string,
    amount: Number(formData.get('amount')),
    status: formData.get('status') as string,
  }

  // Insert into database...
  await db.invoice.create({ data: rawFormData })

  revalidatePath('/invoices')
  redirect('/invoices')
}
```

```tsx
// app/invoices/create/page.tsx
import { createInvoice } from '@/app/actions'

export default function CreateInvoicePage() {
  return (
    <form action={createInvoice}>
      <input name="customerId" type="text" required />
      <input name="amount" type="number" required />
      <select name="status">
        <option value="pending">Pending</option>
        <option value="paid">Paid</option>
      </select>
      <button type="submit">Create Invoice</button>
    </form>
  )
}
```

This form works **without JavaScript** (progressive enhancement). The `action` attribute submits directly to the server.

## Form State with `useActionState`

For showing validation errors and pending state:

```tsx
// app/actions.ts
'use server'

export type FormState = {
  message: string
  errors?: { [key: string]: string[] }
}

export async function createUser(prevState: FormState, formData: FormData) {
  const name = formData.get('name') as string
  const email = formData.get('email') as string

  // Validate
  const errors: { [key: string]: string[] } = {}
  if (!name || name.length < 2) {
    errors.name = ['Name must be at least 2 characters']
  }
  if (!email || !email.includes('@')) {
    errors.email = ['Please enter a valid email']
  }

  if (Object.keys(errors).length > 0) {
    return { message: 'Validation failed', errors }
  }

  // Create user...
  await db.user.create({ data: { name, email } })

  return { message: 'User created successfully' }
}
```

```tsx
// app/ui/signup-form.tsx
'use client'

import { useActionState } from 'react'
import { createUser, type FormState } from '@/app/actions'

const initialState: FormState = { message: '' }

export function SignupForm() {
  const [state, formAction, pending] = useActionState(createUser, initialState)

  return (
    <form action={formAction}>
      <div>
        <label htmlFor="name">Name</label>
        <input id="name" name="name" type="text" required />
        {state.errors?.name && (
          <p className="text-red-500 text-sm">{state.errors.name[0]}</p>
        )}
      </div>

      <div>
        <label htmlFor="email">Email</label>
        <input id="email" name="email" type="email" required />
        {state.errors?.email && (
          <p className="text-red-500 text-sm">{state.errors.email[0]}</p>
        )}
      </div>

      <button type="submit" disabled={pending}>
        {pending ? 'Creating...' : 'Sign Up'}
      </button>

      {state.message && <p aria-live="polite">{state.message}</p>}
    </form>
  )
}
```

## Submit Button with `useFormStatus`

Extract the submit button for reusable pending state:

```tsx
// app/ui/submit-button.tsx
'use client'

import { useFormStatus } from 'react-dom'

export function SubmitButton({ children }: { children: React.ReactNode }) {
  const { pending } = useFormStatus()

  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Submitting...' : children}
    </button>
  )
}
```

**Important:** `useFormStatus` must be used in a component that is a **child** of the `<form>`. It does not work in the same component that renders the form.

## Zod Validation

Use Zod for type-safe schema validation in Server Actions. Note for zod v4 (current): `z.string().email()` is deprecated in favor of `z.email()`, and the `errorMap` option is replaced by `error`:

```typescript
// app/lib/schemas.ts
import { z } from 'zod'

export const CreatePostSchema = z.object({
  title: z.string().min(1, 'Title is required').max(100, 'Title too long'),
  content: z.string().min(10, 'Content must be at least 10 characters'),
  published: z.coerce.boolean().default(false),
})

export type CreatePostInput = z.infer<typeof CreatePostSchema>
```

```typescript
// app/actions.ts
'use server'

import { CreatePostSchema } from '@/app/lib/schemas'
import { revalidatePath } from 'next/cache'

export type PostFormState = {
  message: string
  errors?: Record<string, string[]>
  success?: boolean
}

export async function createPost(
  prevState: PostFormState,
  formData: FormData
): Promise<PostFormState> {
  const parsed = CreatePostSchema.safeParse({
    title: formData.get('title'),
    content: formData.get('content'),
    published: formData.get('published'),
  })

  if (!parsed.success) {
    return {
      message: 'Validation failed',
      errors: parsed.error.flatten().fieldErrors,
    }
  }

  try {
    await db.post.create({ data: parsed.data })
    revalidatePath('/posts')
    return { message: 'Post created', success: true }
  } catch (e) {
    return { message: 'Database error. Failed to create post.' }
  }
}
```

## Optimistic Updates with `useOptimistic`

Show optimistic UI while the Server Action is pending:

```tsx
// app/ui/messages.tsx
'use client'

import { useOptimistic } from 'react'
import { sendMessage } from '@/app/actions'

type Message = { id: string; text: string; sending?: boolean }

export function Messages({ messages }: { messages: Message[] }) {
  const [optimisticMessages, addOptimisticMessage] = useOptimistic(
    messages,
    (state, newMessage: string) => [
      ...state,
      { id: crypto.randomUUID(), text: newMessage, sending: true },
    ]
  )

  async function formAction(formData: FormData) {
    const text = formData.get('text') as string
    addOptimisticMessage(text)
    await sendMessage(text)
  }

  return (
    <>
      <ul>
        {optimisticMessages.map((msg) => (
          <li key={msg.id} className={msg.sending ? 'opacity-50' : ''}>
            {msg.text}
            {msg.sending && <span className="ml-2 text-sm">(Sending...)</span>}
          </li>
        ))}
      </ul>
      <form action={formAction}>
        <input name="text" type="text" required />
        <button type="submit">Send</button>
      </form>
    </>
  )
}
```

## File Uploads

Handle file uploads via FormData in Server Actions:

```typescript
// app/actions.ts
'use server'

export async function uploadFile(formData: FormData) {
  const file = formData.get('file') as File

  if (!file || file.size === 0) {
    return { error: 'No file selected' }
  }

  // Validate file type and size
  const MAX_SIZE = 5 * 1024 * 1024 // 5MB
  const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp']

  if (file.size > MAX_SIZE) {
    return { error: 'File too large (max 5MB)' }
  }

  if (!ALLOWED_TYPES.includes(file.type)) {
    return { error: 'Invalid file type' }
  }

  const bytes = await file.arrayBuffer()
  const buffer = Buffer.from(bytes)

  // Save to disk or upload to S3/R2/etc.
  await writeFile(`/uploads/${file.name}`, buffer)

  return { success: true, filename: file.name }
}
```

```tsx
// app/ui/upload-form.tsx
'use client'

import { useActionState } from 'react'
import { uploadFile } from '@/app/actions'

export function UploadForm() {
  const [state, formAction, pending] = useActionState(uploadFile, null)

  return (
    <form action={formAction}>
      <input type="file" name="file" accept="image/*" required />
      <button type="submit" disabled={pending}>
        {pending ? 'Uploading...' : 'Upload'}
      </button>
      {state?.error && <p className="text-red-500">{state.error}</p>}
      {state?.success && <p className="text-green-500">Uploaded!</p>}
    </form>
  )
}
```

## Next.js `<Form>` Component

Next.js provides a `<Form>` component that extends `<form>` with prefetching, client-side navigation, and progressive enhancement:

```tsx
import Form from 'next/form'

export function SearchForm() {
  return (
    <Form action="/search">
      <input name="q" type="text" placeholder="Search..." />
      <button type="submit">Search</button>
    </Form>
  )
}
```

When JavaScript is loaded, `<Form>` navigates client-side on submit. For GET forms (search, filters), it prefetches the target route's loading UI.

## Common Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| Form doesn't reset after submit | State not cleared | Return new initial state or use `key` prop on form |
| `useFormStatus` always shows `pending: false` | Component not inside `<form>` | Move `useFormStatus` to a child component of the form |
| Stale data after mutation | Missing revalidation | Call `revalidatePath()` or `revalidateTag()` in Server Action |
| Redirect after action fails silently | `redirect()` thrown inside try/catch | Call `redirect()` outside the try/catch block |
| Type error on `formData.get()` | Returns `FormDataEntryValue | null` | Cast with `as string` or use Zod to parse |

## What This Skill Does NOT Cover

- Third-party form libraries (React Hook Form, Formik) — use their docs
- Client-only forms without Server Actions — standard React patterns
- Complex multi-step wizard flows — combine patterns above with URL state
- Real-time validation (debounced API calls) — use `useTransition` + fetch
