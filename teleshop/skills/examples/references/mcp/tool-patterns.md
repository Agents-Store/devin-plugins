# MCP Tool Call Patterns

Reference patterns for all 50 Teleshop MCP tools with exact parameter formats.

## Products

### list_products
```json
{
  "search": "iPhone",
  "page": 1,
  "limit": 20,
  "sortBy": "createdAt",
  "sortOrder": "DESC",
  "category": "Electronics",
  "visibility": "catalog",
  "sellStatus": "available",
  "stockControl": true,
  "isActive": true,
  "lonely": false
}
```

### get_product
```json
{ "id": 123 }
```

### create_product
```json
{
  "sku": "SKU-001",
  "title": "Product Title",
  "description": "Product description",
  "price": 99.99,
  "discountPrice": 79.99,
  "quantity": 50,
  "categoryId": 1,
  "visibility": "catalog",
  "sellStatus": "available",
  "stockControl": true,
  "isActive": true,
  "rawAttributes": [["Color", "Red", "color"], ["Size", "L", "text"]],
  "imageIds": [1, 2, 3],
  "variantIds": [10, 11],
  "isHaveVariants": false
}
```

### batch_create_products
```json
{
  "products": [
    { "sku": "SKU-001", "title": "Product 1", "description": "...", "price": 10, "quantity": 5 },
    { "sku": "SKU-002", "title": "Product 2", "description": "...", "price": 20, "quantity": 10 }
  ]
}
```

### update_product
```json
{
  "id": 123,
  "title": "Updated Title",
  "price": 109.99,
  "quantity": 100,
  "sellStatus": "preorder"
}
```

### delete_product
```json
{ "id": 123 }
```

### batch_delete_products
```json
{ "productIds": [1, 2, 3, 4, 5] }
```

### update_product_images
```json
{ "id": 123, "imageIds": [1, 2, 3] }
```

### update_product_attributes
```json
{
  "id": 123,
  "attributes": [
    { "field": "Color", "value": "#FF0000", "type": "color", "colorName": "Red" },
    { "field": "Size", "value": "XL", "type": "text" },
    { "field": "Material", "value": "Cotton", "type": "text" }
  ]
}
```

## Orders

### list_orders
```json
{
  "search": "John",
  "sortBy": "createdAt",
  "sortOrder": "DESC",
  "status": "processing",
  "paymentType": "onlinePayment",
  "deliveryType": "novaPoshtaCourier",
  "isPayed": true,
  "customerId": 1,
  "isArchived": false
}
```

### get_order
```json
{ "id": 456 }
```

### update_order
```json
{
  "id": 456,
  "ttn": "20450123456789",
  "comment": "Express delivery requested",
  "email": "john@example.com",
  "fullName": "John Smith",
  "phoneNumber": "+380991234567",
  "skipConfirmationCall": true
}
```

### update_order_status
```json
{ "id": 456, "status": "shipped" }
```

### update_order_payment
```json
{ "id": 456, "isPayed": true }
```

## Categories

### list_categories
```json
{ "search": "Electronics", "sortBy": "position", "sortOrder": "ASC" }
```

### get_category
```json
{ "id": 5 }
```

### create_category
```json
{ "title": "Smartphones", "parentId": 5, "orderBy": "popular", "imageId": 10 }
```

### batch_create_categories
```json
{
  "categories": [
    { "title": "Clothing" },
    { "title": "T-Shirts", "parentId": 1 },
    { "title": "Shoes" }
  ]
}
```

### update_category
```json
{ "id": 5, "title": "Consumer Electronics", "orderBy": "novelty" }
```

### delete_category
```json
{ "id": 5 }
```

### batch_delete_categories
```json
{ "categoryIds": [10, 11, 12] }
```

## Attributes

### list_attributes
```json
{ "search": "Color", "sortBy": "name", "sortOrder": "ASC" }
```

### get_attribute
```json
{ "id": 1 }
```

### create_attribute
```json
{ "name": "Size", "type": "select", "isVariant": true }
```

### update_attribute
```json
{ "id": 1, "name": "Clothing Size", "isVariant": true }
```

### delete_attribute
```json
{ "id": 1 }
```

### add_attribute_values
```json
{ "id": 1, "values": ["S", "M", "L", "XL", "XXL"] }
```

## Customers

### list_customers
```json
{ "search": "John", "sortBy": "createdAt", "sortOrder": "DESC" }
```

### get_customer
```json
{ "id": 789 }
```

## Catalog Import

### import_catalog
```json
{
  "options": { "mode": "merge", "stockControl": true },
  "categories": [
    { "externalId": "cat-1", "title": "Electronics", "parentExternalId": null },
    { "externalId": "cat-2", "title": "Phones", "parentExternalId": "cat-1" }
  ],
  "products": [
    {
      "sku": "PHONE-001",
      "title": "Smartphone",
      "price": 599,
      "description": "Modern smartphone",
      "quantity": 30,
      "categoryExternalId": "cat-2",
      "imageUrls": ["https://example.com/img.jpg"],
      "attributes": [{ "name": "Storage", "value": "128GB", "type": "string" }],
      "isActive": true,
      "stockControl": true
    }
  ]
}
```

## Webhooks

### list_webhooks
```json
{}
```

### get_webhook_events
```json
{}
```

### get_webhook
```json
{ "id": 1 }
```

### create_webhook
```json
{ "url": "https://my-server.com/webhooks", "events": ["order.created", "order.updated"] }
```

### update_webhook
```json
{ "id": 1, "url": "https://new-server.com/webhooks", "events": ["order.created"] }
```

### delete_webhook
```json
{ "id": 1 }
```

### test_webhook
```json
{ "id": 1 }
```

### get_webhook_sample_payload
```json
{ "event": "order.created" }
```

### get_webhook_logs
```json
{ "id": 1 }
```

### get_webhook_secret
```json
{ "id": 1 }
```

### get_webhook_stats
```json
{ "id": 1 }
```

### toggle_webhook
```json
{ "id": 1 }
```

## Addons (Workflows)

### list_workflows
```json
{}
```

### toggle_workflow
```json
{ "id": "addon-123" }
```

### get_workflow_variables
```json
{ "id": "addon-123" }
```

### set_workflow_variables
```json
{ "id": "addon-123", "variables": { "key": "value" } }
```

### execute_workflow
```json
{ "id": "addon-123" }
```

### get_workflow_schedule
```json
{ "id": "addon-123" }
```

### set_workflow_schedule
```json
{ "id": "addon-123", "schedule": "0 */6 * * *" }
```

### clear_workflow_schedule
```json
{ "id": "addon-123" }
```
