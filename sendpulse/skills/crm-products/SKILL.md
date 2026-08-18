---
name: crm-products
description: CRM product catalog and deal-product associations. Use when managing product listings, adding products to deals, or viewing product-deal relationships.
---

# CRM Products

This skill covers product catalog management and linking products to deals.

## Available Tools

| Tool | Description |
|------|-------------|
| `crm_products_list` | List products with filtering and sorting |
| `crm_products_deals_list` | List products attached to a specific deal |
| `crm_products_deals_add` | Add a product to a deal |

## Product Catalog

### List Products
```
Tool: crm_products_list
Input: {"limit": 50, "offset": 0}

Returns products with name, price, description, and metadata.
```

## Deal-Product Relationships

### List Products in a Deal
```
Tool: crm_products_deals_list
Input: {"deal_id": "<deal-id>"}

Returns all products attached to the deal with quantities and prices.
```

### Add Product to Deal
```
Tool: crm_products_deals_add
Input: {"deal_id": "<deal-id>", "product_id": "<product-id>", "quantity": 2, "price": 99.99}

Links a product to a deal with specified quantity and price.
```

## Common Workflows

### Create Deal with Products
```
1. crm_products_list() -> Find product IDs
2. crm_deals_create(name, pipeline_id, step_id) -> Create deal
3. crm_products_deals_add(deal_id, product_id, quantity, price) -> Attach products
```

### Review Deal Value
```
1. crm_products_deals_list(deal_id) -> List all products
2. Calculate total from quantities and prices
```

## Best Practices

1. **List products first** to confirm IDs and current prices
2. **Specify accurate prices** — they may differ from catalog for custom deals
3. **Set quantity correctly** for accurate deal value calculation
