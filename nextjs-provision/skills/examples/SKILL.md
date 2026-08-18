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

For simple forms, the newer `field` component (`npx shadcn@latest add field`) is the modern alternative — it works with Server Actions, React Hook Form, and TanStack Form. The RHF + Zod pattern below remains fully valid:

```bash
# 1. Install form components
npx shadcn@latest add form input button label select

# 2. Create schema
```

```typescript
// lib/validations.ts
import { z } from "zod"

export const contactSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Invalid email address"),
  message: z.string().min(10, "Message must be at least 10 characters"),
})
```

```typescript
// 3. Build the form component
// components/forms/contact-form.tsx
"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { contactSchema } from "@/lib/validations"
import { Button } from "@/components/ui/button"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import type { z } from "zod"

export function ContactForm() {
  const form = useForm<z.infer<typeof contactSchema>>({
    resolver: zodResolver(contactSchema),
    defaultValues: { name: "", email: "", message: "" },
  })

  function onSubmit(values: z.infer<typeof contactSchema>) {
    console.log(values)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField control={form.control} name="name" render={({ field }) => (
          <FormItem>
            <FormLabel>Name</FormLabel>
            <FormControl><Input {...field} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <FormField control={form.control} name="email" render={({ field }) => (
          <FormItem>
            <FormLabel>Email</FormLabel>
            <FormControl><Input type="email" {...field} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <Button type="submit">Submit</Button>
      </form>
    </Form>
  )
}
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
- New York style variant (cleaner borders and shadows)
- CSS variables enabled for theming
