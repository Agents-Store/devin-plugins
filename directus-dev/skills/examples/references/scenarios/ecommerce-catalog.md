# Scenario: E-Commerce Catalog

Complete schema build for an e-commerce catalog with products, variants, categories, brands, and orders.

## Collections

| Collection | Purpose | Type |
|-----------|---------|------|
| `brands` | Product brands | Independent |
| `categories` | Product categories (hierarchical) | Independent (self-referencing) |
| `products` | Main product entries | Dependent |
| `variants` | Product variants (size, color) | Dependent |
| `product_categories` | Junction: products ↔ categories | Junction (M2M) |
| `orders` | Customer orders | Independent |
| `order_items` | Items within orders | Dependent |

## Step 1: Create Independent Collections

```json
Tool: collections
Input: {
  "action": "create",
  "data": [
    {
      "collection": "brands",
      "schema": {},
      "meta": { "icon": "store", "display_template": "{{name}}" }
    },
    {
      "collection": "categories",
      "schema": {},
      "meta": { "icon": "category", "display_template": "{{name}}" }
    },
    {
      "collection": "orders",
      "schema": {},
      "meta": { "icon": "receipt_long", "display_template": "Order #{{order_number}}" }
    }
  ]
}
```

## Step 2: Add Fields to Brands

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "brands",
  "data": [
    { "field": "name", "type": "string", "meta": { "interface": "input" }, "schema": { "is_nullable": false } },
    { "field": "slug", "type": "string", "meta": { "interface": "input" }, "schema": { "is_unique": true } },
    { "field": "logo", "type": "uuid", "meta": { "interface": "file-image", "special": ["file"], "display": "image" } },
    { "field": "description", "type": "text", "meta": { "interface": "input-multiline" } },
    { "field": "website", "type": "string", "meta": { "interface": "input" } }
  ]
}
```

## Step 3: Add Fields to Categories (with self-referencing parent)

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "categories",
  "data": [
    { "field": "name", "type": "string", "meta": { "interface": "input" }, "schema": { "is_nullable": false } },
    { "field": "slug", "type": "string", "meta": { "interface": "input" }, "schema": { "is_unique": true } },
    { "field": "description", "type": "text", "meta": { "interface": "input-multiline" } },
    { "field": "image", "type": "uuid", "meta": { "interface": "file-image", "special": ["file"], "display": "image" } },
    { "field": "parent", "type": "uuid", "meta": { "interface": "select-dropdown-m2o", "special": ["m2o"], "display": "related-values" } },
    { "field": "children", "type": "alias", "meta": { "interface": "list-o2m", "special": ["o2m"], "display": "related-values" } },
    { "field": "sort", "type": "integer", "meta": { "interface": "input", "hidden": true } }
  ]
}
```

Self-referencing relation:

```json
Tool: relations
Input: {
  "action": "create",
  "collection": "categories",
  "field": "parent",
  "data": {
    "collection": "categories",
    "field": "parent",
    "related_collection": "categories",
    "schema": { "on_delete": "SET NULL" },
    "meta": { "one_field": "children" }
  }
}
```

## Step 4: Create Products Collection

```json
Tool: collections
Input: {
  "action": "create",
  "data": [{
    "collection": "products",
    "schema": {},
    "meta": {
      "icon": "inventory_2",
      "display_template": "{{name}} — ${{base_price}}",
      "sort_field": "sort",
      "archive_field": "status",
      "archive_value": "discontinued",
      "unarchive_value": "draft"
    }
  }]
}
```

## Step 5: Add Product Fields

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "products",
  "data": [
    { "field": "name", "type": "string", "meta": { "interface": "input" }, "schema": { "is_nullable": false } },
    { "field": "slug", "type": "string", "meta": { "interface": "input" }, "schema": { "is_unique": true } },
    { "field": "description", "type": "text", "meta": { "interface": "input-rich-text-md" } },
    { "field": "short_description", "type": "text", "meta": { "interface": "input-multiline" } },
    { "field": "sku", "type": "string", "meta": { "interface": "input" }, "schema": { "is_unique": true } },
    { "field": "base_price", "type": "decimal", "meta": { "interface": "input", "options": { "prefix": "$" }, "width": "half" } },
    { "field": "compare_price", "type": "decimal", "meta": { "interface": "input", "options": { "prefix": "$" }, "width": "half", "note": "Original price for sale display" } },
    { "field": "featured_image", "type": "uuid", "meta": { "interface": "file-image", "special": ["file"], "display": "image" } },
    { "field": "status", "type": "string", "meta": { "interface": "select-dropdown", "options": { "choices": [{"text": "Draft", "value": "draft"}, {"text": "Active", "value": "active"}, {"text": "Discontinued", "value": "discontinued"}] } }, "schema": { "default_value": "draft" } },
    { "field": "featured", "type": "boolean", "meta": { "interface": "boolean", "width": "half" }, "schema": { "default_value": false } },
    { "field": "sort", "type": "integer", "meta": { "interface": "input", "hidden": true } },
    { "field": "brand", "type": "uuid", "meta": { "interface": "select-dropdown-m2o", "special": ["m2o"], "display": "related-values" } },
    { "field": "date_created", "type": "timestamp", "meta": { "special": ["date-created"], "interface": "datetime", "readonly": true, "hidden": true } },
    { "field": "date_updated", "type": "timestamp", "meta": { "special": ["date-updated"], "interface": "datetime", "readonly": true, "hidden": true } }
  ]
}
```

Brand relation:

```json
Tool: relations
Input: {
  "action": "create",
  "collection": "products",
  "field": "brand",
  "data": { "collection": "products", "field": "brand", "related_collection": "brands", "schema": { "on_delete": "SET NULL" }, "meta": {} }
}
```

Featured image relation:

```json
Tool: relations
Input: {
  "action": "create",
  "collection": "products",
  "field": "featured_image",
  "data": { "collection": "products", "field": "featured_image", "related_collection": "directus_files", "schema": { "on_delete": "SET NULL" }, "meta": {} }
}
```

## Step 6: Create Variants Collection

```json
Tool: collections
Input: {
  "action": "create",
  "data": [{
    "collection": "variants",
    "schema": {},
    "meta": { "icon": "style", "display_template": "{{sku}} — {{name}}" }
  }]
}
```

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "variants",
  "data": [
    { "field": "name", "type": "string", "meta": { "interface": "input", "note": "e.g. Red / Large" } },
    { "field": "sku", "type": "string", "meta": { "interface": "input" }, "schema": { "is_unique": true, "is_nullable": false } },
    { "field": "price", "type": "decimal", "meta": { "interface": "input", "options": { "prefix": "$" }, "width": "half" } },
    { "field": "stock", "type": "integer", "meta": { "interface": "input", "width": "half" }, "schema": { "default_value": 0 } },
    { "field": "attributes", "type": "json", "meta": { "interface": "input-code", "note": "e.g. {\"color\": \"red\", \"size\": \"L\"}" } },
    { "field": "product", "type": "uuid", "meta": { "interface": "select-dropdown-m2o", "special": ["m2o"] } },
    { "field": "sort", "type": "integer", "meta": { "interface": "input", "hidden": true } }
  ]
}
```

Product → Variants relation:

```json
Tool: relations
Input: {
  "action": "create",
  "collection": "variants",
  "field": "product",
  "data": { "collection": "variants", "field": "product", "related_collection": "products", "schema": { "on_delete": "CASCADE" }, "meta": {} }
}
```

Add O2M alias on products:

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "products",
  "data": [{ "field": "variants", "type": "alias", "meta": { "interface": "list-o2m", "special": ["o2m"], "display": "related-values" } }]
}
```

## Step 7: Create M2M Product ↔ Categories

```json
Tool: collections
Input: {
  "action": "create",
  "data": [{ "collection": "product_categories", "schema": {}, "meta": { "hidden": true } }]
}
```

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "product_categories",
  "data": [
    { "field": "products_id", "type": "uuid", "meta": { "hidden": true } },
    { "field": "categories_id", "type": "uuid", "meta": { "hidden": true } }
  ]
}
```

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "products",
  "data": [{ "field": "categories", "type": "alias", "meta": { "interface": "list-m2m", "special": ["m2m"], "display": "related-values" } }]
}
```

```json
Tool: relations
Input: {
  "action": "create",
  "collection": "product_categories",
  "field": "products_id",
  "data": { "collection": "product_categories", "field": "products_id", "related_collection": "products", "schema": { "on_delete": "CASCADE" }, "meta": { "one_field": "categories", "junction_field": "categories_id" } }
}
```

```json
Tool: relations
Input: {
  "action": "create",
  "collection": "product_categories",
  "field": "categories_id",
  "data": { "collection": "product_categories", "field": "categories_id", "related_collection": "categories", "schema": { "on_delete": "CASCADE" }, "meta": { "junction_field": "products_id" } }
}
```

## Step 8: Create Orders and Order Items

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "orders",
  "data": [
    { "field": "order_number", "type": "string", "meta": { "interface": "input" }, "schema": { "is_unique": true, "is_nullable": false } },
    { "field": "customer_email", "type": "string", "meta": { "interface": "input", "width": "half" } },
    { "field": "customer_name", "type": "string", "meta": { "interface": "input", "width": "half" } },
    { "field": "total", "type": "decimal", "meta": { "interface": "input", "options": { "prefix": "$" }, "width": "half" } },
    { "field": "status", "type": "string", "meta": { "interface": "select-dropdown", "options": { "choices": [{"text": "Pending", "value": "pending"}, {"text": "Processing", "value": "processing"}, {"text": "Shipped", "value": "shipped"}, {"text": "Delivered", "value": "delivered"}, {"text": "Cancelled", "value": "cancelled"}] } }, "schema": { "default_value": "pending" } },
    { "field": "date_created", "type": "timestamp", "meta": { "special": ["date-created"], "interface": "datetime", "readonly": true } }
  ]
}
```

```json
Tool: collections
Input: {
  "action": "create",
  "data": [{ "collection": "order_items", "schema": {}, "meta": { "icon": "shopping_cart", "hidden": true } }]
}
```

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "order_items",
  "data": [
    { "field": "order", "type": "uuid", "meta": { "interface": "select-dropdown-m2o", "special": ["m2o"] } },
    { "field": "variant", "type": "uuid", "meta": { "interface": "select-dropdown-m2o", "special": ["m2o"] } },
    { "field": "quantity", "type": "integer", "meta": { "interface": "input", "width": "half" }, "schema": { "default_value": 1 } },
    { "field": "unit_price", "type": "decimal", "meta": { "interface": "input", "options": { "prefix": "$" }, "width": "half" } }
  ]
}
```

Relations:

```json
Tool: relations
Input: {
  "action": "create",
  "collection": "order_items",
  "field": "order",
  "data": { "collection": "order_items", "field": "order", "related_collection": "orders", "schema": { "on_delete": "CASCADE" }, "meta": {} }
}
```

```json
Tool: relations
Input: {
  "action": "create",
  "collection": "order_items",
  "field": "variant",
  "data": { "collection": "order_items", "field": "variant", "related_collection": "variants", "schema": { "on_delete": "SET NULL" }, "meta": {} }
}
```

O2M alias on orders:

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "orders",
  "data": [{ "field": "items", "type": "alias", "meta": { "interface": "list-o2m", "special": ["o2m"], "display": "related-values" } }]
}
```

## Sample Queries

### Products with Brand and Categories

```json
Tool: items
Input: {
  "action": "read",
  "collection": "products",
  "query": {
    "fields": ["name", "base_price", "status", "brand.name", "categories.categories_id.name", "variants.sku", "variants.price", "variants.stock"],
    "filter": { "status": { "_eq": "active" } },
    "sort": ["-date_created"],
    "limit": 25
  }
}
```

### Order Summary with Items

```json
Tool: items
Input: {
  "action": "read",
  "collection": "orders",
  "query": {
    "fields": ["order_number", "customer_name", "total", "status", "items.quantity", "items.unit_price", "items.variant.name", "items.variant.sku"],
    "filter": { "status": { "_in": ["pending", "processing"] } },
    "sort": ["-date_created"]
  }
}
```

### Sales Report

```json
Tool: items
Input: {
  "action": "read",
  "collection": "orders",
  "query": {
    "aggregate": { "count": ["*"], "sum": ["total"], "avg": ["total"] },
    "groupBy": ["status"]
  }
}
```

### Low Stock Variants

```json
Tool: items
Input: {
  "action": "read",
  "collection": "variants",
  "query": {
    "fields": ["sku", "name", "stock", "product.name"],
    "filter": { "stock": { "_lt": 5 } },
    "sort": ["stock"]
  }
}
```
