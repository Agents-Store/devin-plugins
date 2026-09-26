---
name: product-management
description: Product CRUD, batch operations, image and attribute management, variants, filtering and sorting. Use when creating, updating, deleting, or listing products in a Teleshop store.
---

# Product Management

This skill covers all product operations in a Teleshop store — creating, reading, updating, deleting products individually or in batches, managing product images and attributes.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_products` | List products with pagination, search, and filters |
| `get_product` | Get single product details by ID |
| `create_product` | Create a new product |
| `batch_create_products` | Create multiple products at once |
| `update_product` | Update an existing product |
| `delete_product` | Delete a product |
| `batch_delete_products` | Delete multiple products at once |
| `update_product_images` | Update product images by image IDs |
| `update_product_attributes` | Update product attributes (color, size, etc.) |

## Listing Products

### List with Filters
```
Tool: list_products
Input: {
  "search": "iPhone",
  "page": 1,
  "limit": 20,
  "sortBy": "createdAt",
  "sortOrder": "DESC",
  "category": "Electronics",
  "sellStatus": "available",
  "isActive": true
}
```

**Filter Parameters:**

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| search | string | any | Search by product title |
| page | number | 1+ | Page number |
| limit | number | 1-100 | Items per page |
| sortBy | string | id, title, price, quantity, createdAt, updatedAt, category | Sort field |
| sortOrder | string | ASC, DESC | Sort direction |
| category | string | any | Filter by category name |
| visibility | string | catalog, parent | Product visibility type |
| sellStatus | string | available, unavailable, preorder | Product sell status |
| stockControl | boolean | true/false | Filter by stock control enabled |
| isActive | boolean | true/false | Filter active/inactive products |
| lonely | boolean | true/false | Filter products without variants |

**Response:** `{ items: ProductDto[], meta: { currentPage, itemCount, itemsPerPage, totalItems, totalPages } }`

## Getting a Single Product

```
Tool: get_product
Input: {"id": 123}

Returns full ProductDto with: id, sku, title, description, price, discountPrice,
sellStatus, visibility, quantity, stockControl, isActive, categoryId,
images[], attributes[], priceRules[], variants info.
```

## Creating Products

### Create Single Product
```
Tool: create_product
Input: {
  "sku": "SKU-001",
  "title": "iPhone 15 Pro",
  "description": "Latest iPhone with titanium design",
  "price": 999.99,
  "discountPrice": 899.99,
  "quantity": 50,
  "categoryId": 1,
  "sellStatus": "available",
  "visibility": "catalog",
  "stockControl": true,
  "isActive": true
}
```

**Required fields:** sku, title, description, price, quantity

**Optional fields:**

| Field | Type | Description |
|-------|------|-------------|
| discountPrice | number | Discounted price (must be < price) |
| visibility | string | "catalog" (default) or "parent" |
| sellStatus | string | "available", "unavailable", "preorder" |
| categoryId | number | Category ID to assign |
| stockControl | boolean | Enable stock tracking |
| enableFormatTitle | boolean | Auto-format title |
| isActive | boolean | Active in store |
| rawAttributes | array | Attributes as [name, value, type] tuples |
| imageIds | array | Image IDs to attach |
| variantIds | array | Variant product IDs |
| isHaveVariants | boolean | Mark as parent with variants |

### Create with Attributes (rawAttributes format)
```
Tool: create_product
Input: {
  "sku": "TSHIRT-RED-XL",
  "title": "Red T-Shirt XL",
  "description": "Cotton t-shirt",
  "price": 29.99,
  "quantity": 100,
  "rawAttributes": [
    ["Color", "Red", "color"],
    ["Size", "XL", "text"],
    ["Material", "Cotton", "text"]
  ]
}
```

### Batch Create Products
```
Tool: batch_create_products
Input: {
  "products": [
    { "sku": "SKU-001", "title": "Product 1", "description": "...", "price": 10, "quantity": 5 },
    { "sku": "SKU-002", "title": "Product 2", "description": "...", "price": 20, "quantity": 10 }
  ]
}

Response: { createdIds: string[], count: number }
```

## Updating Products

### Update Product Fields
```
Tool: update_product
Input: {
  "id": 123,
  "title": "iPhone 15 Pro Max",
  "price": 1099.99,
  "discountPrice": 999.99,
  "quantity": 200,
  "sellStatus": "available"
}
```
All fields are optional — only send what you want to change.

### Update Product Images
```
Tool: update_product_images
Input: {
  "id": 123,
  "imageIds": [1, 2, 3]
}
```
Replaces all current images with the provided image IDs.

### Update Product Attributes
```
Tool: update_product_attributes
Input: {
  "id": 123,
  "attributes": [
    { "field": "Color", "value": "#FF0000", "type": "color", "colorName": "Red" },
    { "field": "Size", "value": "XL", "type": "text" },
    { "field": "Material", "value": "Cotton", "type": "text" }
  ]
}
```

**Attribute types:**
- `text` — plain text value
- `color` — hex color value with optional colorName
- `select` — value from predefined list

## Deleting Products

### Delete Single Product
```
Tool: delete_product
Input: {"id": 123}
```

### Batch Delete Products
```
Tool: batch_delete_products
Input: {"productIds": [1, 2, 3, 4, 5]}
```

## Common Workflows

### Add Product with Category and Attributes
```
1. list_categories() -> Find or create target category
2. create_product(sku, title, description, price, quantity, categoryId, rawAttributes) -> Create product
3. update_product_images(id, imageIds) -> Attach images if needed
```

### Bulk Price Update
```
1. list_products(category="Sale Items") -> Get products to update
2. For each product: update_product(id, price, discountPrice) -> Update prices
```

### Product Variant Setup
```
1. create_product(visibility="parent", isHaveVariants=true) -> Create parent
2. batch_create_products(products with variantIds) -> Create variants
3. update_product(parentId, variantIds=[...]) -> Link variants to parent
```

## Enums Reference

**sellStatus:** `available` | `unavailable` | `preorder`
**visibility:** `catalog` (visible in store) | `parent` (variant parent, not directly visible)
**sortBy:** `id` | `title` | `price` | `quantity` | `createdAt` | `updatedAt` | `category`

## Best Practices

1. **Always set SKU** — SKU must be unique across the store
2. **Enable stockControl** for physical goods to prevent overselling
3. **Use batch operations** for bulk imports (more efficient than individual creates)
4. **Set discountPrice < price** — the API will reject if discount >= regular price
5. **Use rawAttributes** on create, **update_product_attributes** for updates
6. **Check category exists** before assigning categoryId
