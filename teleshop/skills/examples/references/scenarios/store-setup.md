# Store Setup Scenario

Complete scenario for setting up a new Teleshop store from scratch using MCP tools.

## Scenario: Clothing Store Setup

A merchant wants to set up an online clothing store with categories, attributes, and initial product catalog.

### Phase 1: Category Structure

```
1. Create top-level categories:
   batch_create_categories(categories=[
     { title: "Men" },
     { title: "Women" },
     { title: "Kids" },
     { title: "Accessories" }
   ])
   -> Men(1), Women(2), Kids(3), Accessories(4)

2. Create subcategories:
   batch_create_categories(categories=[
     { title: "T-Shirts", parentId: 1, orderBy: "popular" },
     { title: "Jeans", parentId: 1, orderBy: "cheap" },
     { title: "Jackets", parentId: 1, orderBy: "novelty" },
     { title: "Dresses", parentId: 2, orderBy: "popular" },
     { title: "Tops", parentId: 2, orderBy: "popular" },
     { title: "Shoes", parentId: 2, orderBy: "cheap" }
   ])

3. Verify:
   list_categories(sortBy="position", sortOrder="ASC")
```

### Phase 2: Product Attributes

```
1. Create Size attribute (variant):
   create_attribute(name="Size", type="select", isVariant=true)
   add_attribute_values(id=sizeId, values=["XS","S","M","L","XL","XXL"])

2. Create Color attribute (variant):
   create_attribute(name="Color", type="color", isVariant=true)
   add_attribute_values(id=colorId, values=["Black","White","Red","Blue","Green","Navy"])

3. Create Material attribute (info):
   create_attribute(name="Material", type="select", isVariant=false)
   add_attribute_values(id=materialId, values=["Cotton","Polyester","Wool","Silk","Denim","Leather"])

4. Create Brand attribute (info):
   create_attribute(name="Brand", type="select", isVariant=false)
   add_attribute_values(id=brandId, values=["Nike","Adidas","Zara","H&M","Uniqlo"])

5. Verify:
   list_attributes()
```

### Phase 3: Initial Products

```
Option A — Individual creation:
  create_product(
    sku="MTS-BLK-M",
    title="Classic Black T-Shirt",
    description="Comfortable cotton t-shirt for everyday wear",
    price=29.99,
    quantity=100,
    categoryId=5,  // Men > T-Shirts
    sellStatus="available",
    stockControl=true,
    isActive=true,
    rawAttributes=[
      ["Color","Black","color"],
      ["Size","M","text"],
      ["Material","Cotton","text"]
    ]
  )

Option B — Catalog import (recommended for many products):
  import_catalog(
    options={ mode: "merge", stockControl: true },
    categories=[
      { externalId: "men", title: "Men" },
      { externalId: "men-tshirts", title: "T-Shirts", parentExternalId: "men" },
      ...
    ],
    products=[
      {
        sku: "MTS-BLK-M",
        title: "Classic Black T-Shirt",
        price: 29.99,
        description: "Comfortable cotton t-shirt",
        quantity: 100,
        categoryExternalId: "men-tshirts",
        imageUrls: ["https://cdn.example.com/tshirt-black.jpg"],
        attributes: [
          { name: "Color", value: "Black,#000000", type: "color" },
          { name: "Size", value: "M", type: "string" },
          { name: "Material", value: "Cotton", type: "string" }
        ],
        isActive: true,
        stockControl: true
      },
      ... (more products)
    ]
  )
```

### Phase 4: Webhook Integration

```
1. Discover events:
   get_webhook_events()

2. Create order webhook:
   create_webhook(
     url="https://merchant-crm.com/api/teleshop-orders",
     events=["order.created", "order.updated"]
   )

3. Save secret:
   get_webhook_secret(id=webhookId)
   -> Merchant saves this for payload verification

4. Test:
   test_webhook(id=webhookId)
   -> 200 OK
```

### Phase 5: Addons Configuration

```
1. List available addons:
   list_workflows()

2. Configure data sync (if supplier feed available):
   get_workflow_variables(id=syncId)
   set_workflow_variables(id=syncId, variables={
     source_url: "https://supplier.com/catalog.xml",
     auto_publish: "true"
   })
   set_workflow_schedule(id=syncId, schedule="0 6 * * *")  // Daily at 6 AM
   toggle_workflow(id=syncId)  // Enable

3. Test sync:
   execute_workflow(id=syncId)
   list_products(sortBy="updatedAt", sortOrder="DESC", limit=5)
```

### Verification Checklist

```
1. list_categories() -> Verify hierarchy (4 top + subcategories)
2. list_attributes() -> Verify 4 attributes with values
3. list_products() -> Verify products in correct categories
4. list_webhooks() -> Verify webhooks active
5. list_workflows() -> Verify addons configured
```
