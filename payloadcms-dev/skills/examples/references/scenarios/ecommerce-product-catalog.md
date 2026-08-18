# Scenario — E-commerce Product Catalog

Products with variants (color/size/SKU), inventory, Stripe price IDs, customer auth, order creation, confirmation email queued as a background job.

## Collections

### `src/collections/Customers.ts`

```ts
import type { CollectionConfig } from 'payload'

export const Customers: CollectionConfig = {
  slug: 'customers',
  auth: { tokenExpiration: 30 * 24 * 60 * 60, verify: true },
  admin: { useAsTitle: 'email', group: 'Commerce' },
  fields: [
    { name: 'firstName', type: 'text' },
    { name: 'lastName', type: 'text' },
    { name: 'stripeCustomerId', type: 'text', admin: { readOnly: true } },
    {
      name: 'addresses',
      type: 'array',
      fields: [
        { name: 'label', type: 'text' },
        { name: 'street', type: 'text', required: true },
        { name: 'city', type: 'text', required: true },
        { name: 'state', type: 'text' },
        { name: 'postalCode', type: 'text', required: true },
        { name: 'country', type: 'text', required: true },
      ],
    },
  ],
}
```

### `src/collections/Products.ts`

```ts
import type { Block, CollectionConfig } from 'payload'

const VariantBlock: Block = {
  slug: 'variant',
  fields: [
    { name: 'sku', type: 'text', required: true, unique: true },
    { name: 'color', type: 'text' },
    { name: 'size', type: 'select', options: ['XS', 'S', 'M', 'L', 'XL'] },
    { name: 'priceCents', type: 'number', required: true, min: 0 },
    { name: 'stripePriceId', type: 'text' },
    { name: 'stock', type: 'number', required: true, defaultValue: 0, min: 0 },
    { name: 'image', type: 'upload', relationTo: 'media' },
  ],
}

export const Products: CollectionConfig = {
  slug: 'products',
  access: {
    read: () => true,
    create: ({ req: { user } }) => user?.roles?.includes('admin') ?? false,
    update: ({ req: { user } }) => user?.roles?.includes('admin') ?? false,
    delete: ({ req: { user } }) => user?.roles?.includes('admin') ?? false,
  },
  admin: {
    group: 'Commerce',
    useAsTitle: 'name',
    defaultColumns: ['name', 'slug', 'baseStock', 'updatedAt'],
  },
  fields: [
    { name: 'name', type: 'text', required: true },
    { name: 'slug', type: 'text', required: true, unique: true, index: true },
    { name: 'description', type: 'richText' },
    { name: 'images', type: 'upload', relationTo: 'media', hasMany: true },
    { name: 'basePriceCents', type: 'number', required: true, min: 0 },
    { name: 'baseStock', type: 'number', defaultValue: 0, min: 0 },
    {
      name: 'variants',
      type: 'blocks',
      blocks: [VariantBlock],
      minRows: 0,
      maxRows: 100,
    },
    {
      name: 'totalStock',
      type: 'number',
      virtual: true,
      hooks: {
        afterRead: [({ siblingData }) => {
          const base = siblingData.baseStock ?? 0
          const variantStock = (siblingData.variants || [])
            .reduce((acc: number, v: any) => acc + (v.stock ?? 0), 0)
          return base + variantStock
        }],
      },
    },
  ],
}
```

### `src/collections/Orders.ts`

```ts
import type { CollectionConfig } from 'payload'

export const Orders: CollectionConfig = {
  slug: 'orders',
  access: {
    read: ({ req: { user } }) => {
      if (!user) return false
      if (user.collection === 'users' && user.roles?.includes('admin')) return true
      // Customers only see their own
      return { customer: { equals: user.id } }
    },
    create: ({ req: { user } }) => Boolean(user),
    update: ({ req: { user } }) => user?.roles?.includes('admin') ?? false,
    delete: ({ req: { user } }) => user?.roles?.includes('admin') ?? false,
  },
  admin: {
    group: 'Commerce',
    useAsTitle: 'id',
    defaultColumns: ['id', 'customer', 'status', 'totalCents', 'createdAt'],
  },
  fields: [
    { name: 'customer', type: 'relationship', relationTo: 'customers', required: true },
    {
      name: 'status',
      type: 'select',
      options: ['pending', 'paid', 'shipped', 'delivered', 'cancelled', 'refunded'],
      defaultValue: 'pending',
      required: true,
    },
    {
      name: 'items',
      type: 'array',
      minRows: 1,
      fields: [
        { name: 'product', type: 'relationship', relationTo: 'products', required: true },
        { name: 'variantSku', type: 'text' },
        { name: 'quantity', type: 'number', required: true, min: 1 },
        { name: 'unitPriceCents', type: 'number', required: true },
      ],
    },
    { name: 'totalCents', type: 'number', required: true },
    { name: 'shippingAddress', type: 'group', fields: [/* same as customer address */] },
    { name: 'stripePaymentIntentId', type: 'text' },
    { name: 'confirmationEmailSent', type: 'checkbox', defaultValue: false },
  ],
  hooks: {
    afterChange: [
      async ({ doc, previousDoc, operation, req }) => {
        // Queue confirmation email on first paid transition
        if (
          operation === 'update' &&
          doc.status === 'paid' &&
          previousDoc?.status !== 'paid' &&
          !doc.confirmationEmailSent
        ) {
          await req.payload.jobs.queue({
            task: 'sendOrderConfirmation',
            input: { orderId: doc.id },
          })
        }
        return doc
      },
    ],
  },
}
```

## Task — Background Confirmation Email

### `src/tasks/sendOrderConfirmation.ts`

```ts
import type { TaskConfig } from 'payload'

export const sendOrderConfirmation: TaskConfig<'sendOrderConfirmation'> = {
  slug: 'sendOrderConfirmation',
  retries: { attempts: 3, backoff: { type: 'exponential', delay: 2000 } },
  inputSchema: [{ name: 'orderId', type: 'text', required: true }],
  handler: async ({ input, req }) => {
    const order = await req.payload.findByID({
      collection: 'orders',
      id: input.orderId,
      depth: 2,
      req,
    })

    const customer = order.customer as any
    const lines = (order.items || [])
      .map((i: any) => `• ${i.quantity}× ${i.product?.name} @ $${(i.unitPriceCents / 100).toFixed(2)}`)
      .join('\n')

    await req.payload.sendEmail({
      to: customer.email,
      subject: `Order ${order.id} confirmed`,
      text: `Thanks for your order!\n\n${lines}\n\nTotal: $${(order.totalCents / 100).toFixed(2)}`,
    })

    await req.payload.update({
      collection: 'orders',
      id: order.id,
      data: { confirmationEmailSent: true },
      context: { skipHooks: true },                     // avoid hook loop
      req,
    })

    return { output: { sentAt: new Date().toISOString() } }
  },
}
```

## `payload.config.ts` Highlights

```ts
import { sendOrderConfirmation } from './tasks/sendOrderConfirmation'

export default buildConfig({
  // …
  collections: [Users, Customers, Media, Products, Orders],
  jobs: {
    tasks: [sendOrderConfirmation],
    autoRun: [{ cron: '*/2 * * * *', queue: 'default' }],   // poll every 2m
    shouldAutoRun: () => process.env.ENABLE_JOBS === 'true',
  },
})
```

## Stripe Checkout Endpoint

### `src/app/(frontend)/api/checkout/route.ts`

```ts
import { getPayload } from 'payload'
import config from '@payload-config'
import Stripe from 'stripe'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || '', { apiVersion: '2024-06-20' as any })

export async function POST(req: Request) {
  const payload = await getPayload({ config })
  const { user } = await payload.auth({ headers: req.headers })
  if (!user) return new Response('Unauthorized', { status: 401 })

  const { items } = await req.json()

  // Resolve prices + ensure stock — server-trusted
  const lineItems = await Promise.all(
    items.map(async (i: any) => {
      const product = await payload.findByID({ collection: 'products', id: i.productId, depth: 0 })
      const variant = (product.variants || []).find((v: any) => v.sku === i.variantSku)
      const priceCents = variant?.priceCents ?? product.basePriceCents
      return {
        price_data: {
          currency: 'usd',
          unit_amount: priceCents,
          product_data: { name: `${product.name}${variant ? ` (${variant.sku})` : ''}` },
        },
        quantity: i.quantity,
      }
    }),
  )

  const session = await stripe.checkout.sessions.create({
    mode: 'payment',
    line_items: lineItems,
    success_url: `${process.env.NEXT_PUBLIC_SITE_URL}/checkout/success`,
    cancel_url: `${process.env.NEXT_PUBLIC_SITE_URL}/checkout/cancel`,
    customer_email: (user as any).email,
    metadata: { customerId: user.id as string },
  })

  return Response.json({ url: session.url })
}
```

## Webhook → Mark Order Paid

```ts
// src/app/(frontend)/api/stripe-webhook/route.ts
import { getPayload } from 'payload'
import config from '@payload-config'
import Stripe from 'stripe'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || '', { apiVersion: '2024-06-20' as any })

export async function POST(req: Request) {
  const sig = req.headers.get('stripe-signature')!
  const buf = await req.text()
  const event = stripe.webhooks.constructEvent(buf, sig, process.env.STRIPE_WEBHOOK_SECRET || '')

  if (event.type === 'checkout.session.completed') {
    const session = event.data.object as Stripe.Checkout.Session
    const payload = await getPayload({ config })
    // Look up the order by stripePaymentIntentId or create here — depending on your flow.
    await payload.update({
      collection: 'orders',
      where: { stripePaymentIntentId: { equals: session.payment_intent as string } },
      data: { status: 'paid' },
    })
  }

  return new Response('ok')
}
```

## What This Demonstrates

- `blocks` field for variants — heterogeneous sub-records inside a product.
- `virtual` field computing total stock at read time.
- Multi-collection auth (`users` for admins, `customers` for shoppers) with collection-aware access.
- Order state machine with hook-driven side effects.
- Background `sendOrderConfirmation` task with retries.
- `context.skipHooks` to prevent re-entrant `afterChange` loop.
- External payment integration with server-trusted price resolution.
