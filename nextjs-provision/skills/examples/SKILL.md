---
name: examples
description: >
  End-to-end scenario walkthroughs for setting up Next.js projects with shadcn/ui and shadcn studio. This
  skill should be used when the user asks for "shadcn setup walkthrough", "how to set up a project with
  shadcn from scratch", "add shadcn to existing project example", "full shadcn setup guide", "shadcn studio
  tutorial", "step-by-step shadcn setup", or needs a complete example of provisioning a Next.js project
  with shadcn components.
---

## Available Scenarios

| Scenario | Description | Reference |
|----------|-------------|-----------|
| New project with shadcn studio | Full setup from `create-next-app` through theme + components + MCP | `references/scenarios/new-project-shadcn-studio.md` |
| Add components to existing project | Audit, install shadcn, migrate existing UI, add studio blocks | `references/scenarios/add-components-to-existing.md` |

## Quick Reference Patterns

### Minimum Viable shadcn Setup (5 steps)

```bash
# 1. Create project
npx create-next-app@latest my-app --typescript --tailwind --eslint --app --src-dir

# 2. Enter project
cd my-app

# 3. Init shadcn (default preset base-nova: Base UI + Nova style; -b radix for Radix)
npx shadcn@latest init

# 4. Install first components
npx shadcn@latest add button card input

# 5. Use in a page
```

```typescript
// src/app/page.tsx
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"

export default function Home() {
  return (
    <main className="flex min-h-screen items-center justify-center p-8">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Welcome</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input placeholder="Enter your email" type="email" />
          <Button className="w-full">Get Started</Button>
        </CardContent>
      </Card>
    </main>
  )
}
```

### Add a Form with Validation (3 steps)

Forms are built from the `field` component plus a form library — there is no working `form` item in the registry (the old `Form` / `FormField` / `FormItem` wrappers are gone). React Hook Form + Zod:

```bash
# 1. Install the field component, inputs and the form libraries
npx shadcn@latest add field input textarea button
npm install react-hook-form @hookform/resolvers zod

# 2. Create the schema
```

```typescript
// lib/validations.ts
import * as z from "zod"

export const contactSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters."),
  email: z.string().email("Invalid email address."),
  message: z.string().min(10, "Message must be at least 10 characters."),
})

export type ContactValues = z.infer<typeof contactSchema>
```

```typescript
// 3. Build the form component
// components/forms/contact-form.tsx
"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { Controller, useForm } from "react-hook-form"

import { Button } from "@/components/ui/button"
import { Field, FieldError, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { contactSchema, type ContactValues } from "@/lib/validations"

export function ContactForm() {
  const form = useForm<ContactValues>({
    resolver: zodResolver(contactSchema),
    defaultValues: { name: "", email: "", message: "" },
  })

  function onSubmit(values: ContactValues) {
    console.log(values)
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <FieldGroup>
        <Controller
          name="name"
          control={form.control}
          render={({ field, fieldState }) => (
            <Field data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor={field.name}>Name</FieldLabel>
              <Input {...field} id={field.name} aria-invalid={fieldState.invalid} autoComplete="name" />
              {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
            </Field>
          )}
        />
        <Controller
          name="email"
          control={form.control}
          render={({ field, fieldState }) => (
            <Field data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor={field.name}>Email</FieldLabel>
              <Input {...field} id={field.name} type="email" aria-invalid={fieldState.invalid} autoComplete="email" />
              {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
            </Field>
          )}
        />
        <Controller
          name="message"
          control={form.control}
          render={({ field, fieldState }) => (
            <Field data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor={field.name}>Message</FieldLabel>
              <Textarea {...field} id={field.name} aria-invalid={fieldState.invalid} />
              {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
            </Field>
          )}
        />
        <Button type="submit">Submit</Button>
      </FieldGroup>
    </form>
  )
}
```

TanStack Form and Formisch variants: https://ui.shadcn.com/docs/forms.

### Add a Date Picker (2 steps)

A date picker is a composition of `Popover` and `Calendar` — there is no `date-picker` item:

```bash
# 1. Install the parts
npx shadcn@latest add popover calendar

# 2. Compose them — full component in the `component-registry` skill ("Date Picker")
```

### Add a Data Table (3 steps)

```bash
# 1. Install dependencies
npx shadcn@latest add table
npm install @tanstack/react-table

# 2. Define columns
# 3. Build the table component
```

See `references/scenarios/new-project-shadcn-studio.md` for a complete data table implementation.

## Convention Notes

- All examples use the `src/` directory structure with `@/` path aliases
- TypeScript is used throughout
- Server Components by default; `'use client'` only when needed
- `base-nova` style (Base UI, the `init` default; `-b radix` gives `radix-nova`)
- CSS variables enabled for theming
