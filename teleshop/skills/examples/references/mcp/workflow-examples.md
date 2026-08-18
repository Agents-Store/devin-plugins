# Multi-Step Workflow Examples

End-to-end workflow examples combining multiple Teleshop MCP tools.

## 1. Complete Product Lifecycle

### Add Product from Scratch
```
Step 1: Create category
  create_category(title="Electronics", orderBy="popular")
  -> categoryId: 5

Step 2: Create attribute
  create_attribute(name="Storage", type="select", isVariant=true)
  -> attributeId: 1

Step 3: Add attribute values
  add_attribute_values(id=1, values=["64GB", "128GB", "256GB", "512GB"])

Step 4: Create parent product
  create_product(
    sku="PHONE-001",
    title="Smartphone X",
    description="Flagship smartphone",
    price=799,
    quantity=0,
    categoryId=5,
    visibility="parent",
    isHaveVariants=true,
    isActive=true
  )
  -> parentId: 100

Step 5: Create variant products
  batch_create_products(products=[
    { sku="PHONE-001-64", title="Smartphone X 64GB", description="...", price=699, quantity=20, categoryId=5, rawAttributes=[["Storage","64GB","text"]] },
    { sku="PHONE-001-128", title="Smartphone X 128GB", description="...", price=799, quantity=30, rawAttributes=[["Storage","128GB","text"]] },
    { sku="PHONE-001-256", title="Smartphone X 256GB", description="...", price=899, quantity=15, rawAttributes=[["Storage","256GB","text"]] }
  ])

Step 6: Link variants to parent
  update_product(id=100, variantIds=[101, 102, 103])
```

### Update Pricing Across Category
```
Step 1: List products in category
  list_products(category="Electronics", limit=100)
  -> [list of products]

Step 2: Apply 10% discount to each
  For each product:
    update_product(id=<id>, discountPrice=<price * 0.9>)
```

## 2. Order Processing Pipeline

### Process New Orders
```
Step 1: Get new orders
  list_orders(status="created", sortBy="createdAt", sortOrder="ASC")
  -> [orders]

Step 2: Review first order
  get_order(id=456)
  -> Order #1234, John Smith, 3 items, $299.97

Step 3: Start processing
  update_order_status(id=456, status="processing")
  update_order(id=456, comment="Started preparing package")

Step 4: Prepare and ship
  update_order(id=456, ttn="20450123456789")
  update_order_status(id=456, status="shipped")

Step 5: Confirm payment (if offline)
  update_order_payment(id=456, isPayed=true)

Step 6: Complete
  update_order_status(id=456, status="completed")
```

### Handle Returns / Cancellations
```
Step 1: Find the order
  list_orders(search="John Smith")
  -> Order #1234

Step 2: Get full details
  get_order(id=456)

Step 3: Cancel the order
  update_order_status(id=456, status="canceled")
  update_order(id=456, comment="Canceled per customer request - refund issued")

Step 4: If payment was received, mark as unpaid (refund processed externally)
  update_order_payment(id=456, isPayed=false)
```

## 3. Full Store Setup from Scratch

```
Step 1: Create category structure
  batch_create_categories(categories=[
    { title: "Clothing" },
    { title: "Electronics" },
    { title: "Accessories" }
  ])
  -> IDs: 1, 2, 3

  batch_create_categories(categories=[
    { title: "T-Shirts", parentId: 1 },
    { title: "Jeans", parentId: 1 },
    { title: "Phones", parentId: 2 },
    { title: "Laptops", parentId: 2 }
  ])

Step 2: Create attributes
  create_attribute(name="Size", type="select", isVariant=true)
  add_attribute_values(id=sizeId, values=["XS","S","M","L","XL","XXL"])

  create_attribute(name="Color", type="color", isVariant=true)
  add_attribute_values(id=colorId, values=["Black","White","Red","Blue"])

  create_attribute(name="Material", type="select")
  add_attribute_values(id=materialId, values=["Cotton","Polyester","Leather"])

Step 3: Import products
  import_catalog(
    options={ mode: "merge", stockControl: true },
    products=[
      { sku: "TS-001", title: "Basic Tee", price: 19.99, quantity: 200, categoryExternalId: "tshirts", ... },
      ... (more products)
    ]
  )

Step 4: Set up webhooks
  get_webhook_events() -> available events
  create_webhook(url="https://my-crm.com/webhooks", events=["order.created", "order.updated"])
  get_webhook_secret(id=webhookId) -> save secret
  test_webhook(id=webhookId) -> verify delivery

Step 5: Configure addons
  list_workflows() -> see available addons
  set_workflow_variables(id=syncAddonId, variables={ source_url: "..." })
  set_workflow_schedule(id=syncAddonId, schedule="0 0 * * *")
  toggle_workflow(id=syncAddonId) -> enable
```

## 4. Webhook Monitoring

### Set Up and Monitor Webhooks
```
Step 1: Discover available events
  get_webhook_events()
  -> ["order.created", "order.updated", "payment.completed", ...]

Step 2: Create webhook
  create_webhook(url="https://api.example.com/hooks", events=["order.created"])
  -> webhookId: 7

Step 3: Get security secret
  get_webhook_secret(id=7)
  -> "whsec_abc123..."

Step 4: Preview payload format
  get_webhook_sample_payload(event="order.created")
  -> { orderNumber, status, customer, items, ... }

Step 5: Test delivery
  test_webhook(id=7)
  -> 200 OK

Step 6: Monitor over time
  get_webhook_stats(id=7)
  -> { total: 150, success: 148, failed: 2, avgResponseTime: 230ms }

  get_webhook_logs(id=7)
  -> [delivery history with timestamps and status codes]
```

## 5. Addon Automation

### Configure Data Sync Addon
```
Step 1: Find the addon
  list_workflows()
  -> [{ id: "sync-addon", name: "Auto Data Sync", enabled: false }]

Step 2: Check configuration
  get_workflow_variables(id="sync-addon")
  -> { source_url: "", sync_interval: "60", auto_publish: "false" }

Step 3: Configure
  set_workflow_variables(id="sync-addon", variables={
    source_url: "https://supplier.com/feed.xml",
    sync_interval: "30",
    auto_publish: "true"
  })

Step 4: Set schedule
  set_workflow_schedule(id="sync-addon", schedule="0 */6 * * *")

Step 5: Enable
  toggle_workflow(id="sync-addon")

Step 6: Test run
  execute_workflow(id="sync-addon")
  -> Check results

Step 7: Verify
  list_products(sortBy="updatedAt", sortOrder="DESC", limit=5)
  -> Recently updated products from sync
```
