---
name: catalog-import
description: Full catalog import with categories and products from JSON. Use when importing a complete catalog, migrating from another platform, or bulk-loading products.
---

# Catalog Import

This skill covers the catalog import tool — importing a full catalog of categories and products from structured JSON data in a single operation.

## Available Tools

| Tool | Description |
|------|-------------|
| `import_catalog` | Import full catalog (categories + products) from JSON |

## Import Catalog

```
Tool: import_catalog
Input: {
  "options": {
    "mode": "merge",
    "stockControl": true
  },
  "categories": [
    {
      "externalId": "cat-electronics",
      "title": "Electronics",
      "parentExternalId": null,
      "imageUrl": "https://example.com/electronics.jpg"
    },
    {
      "externalId": "cat-phones",
      "title": "Smartphones",
      "parentExternalId": "cat-electronics",
      "imageUrl": "https://example.com/phones.jpg"
    }
  ],
  "products": [
    {
      "sku": "IPHONE-15-PRO",
      "title": "iPhone 15 Pro",
      "price": 999.99,
      "description": "Latest iPhone with titanium design",
      "discountPrice": 899.99,
      "quantity": 50,
      "categoryExternalId": "cat-phones",
      "imageUrls": [
        "https://example.com/iphone1.jpg",
        "https://example.com/iphone2.jpg"
      ],
      "attributes": [
        { "name": "Storage", "value": "256GB", "type": "string" },
        { "name": "Color", "value": "Space Black,#1d1d1f", "type": "color" }
      ],
      "brand": "Apple",
      "isActive": true,
      "stockControl": true
    }
  ]
}
```

**Max request size: 10 MB**

## Import Options

| Field | Type | Required | Values | Description |
|-------|------|----------|--------|-------------|
| mode | string | YES | merge, replace | How to handle existing data |
| stockControl | boolean | no | true/false | Enable stock control for imported products |

**Import modes:**
- `merge` — Add new items, update existing (matched by SKU for products, externalId for categories). Existing items not in the import are preserved.
- `replace` — Remove all existing data and replace with imported data. **Use with caution!**

## Category Import Format

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| externalId | string | YES | Your unique ID for the category (used for linking) |
| title | string | YES | Category display name |
| parentExternalId | string | no | Parent category's externalId (for hierarchy) |
| imageUrl | string | no | URL to category image (will be downloaded) |

Categories are linked via `externalId` / `parentExternalId` — build hierarchy within a single import.

## Product Import Format

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| sku | string | YES | Unique product SKU |
| title | string | YES | Product title |
| price | number | YES | Product price |
| description | string | no | Product description |
| discountPrice | number | no | Discounted price |
| quantity | number | no | Available quantity |
| categoryExternalId | string | no | Category externalId to assign |
| imageUrls | array[string] | no | URLs to product images (downloaded automatically) |
| attributes | array | no | Product attributes |
| brand | string | no | Brand name |
| variantGroupId | string | no | Group ID for variant products |
| isActive | boolean | no | Whether product is active |
| stockControl | boolean | no | Per-product stock control override |

### Attribute Format in Import

```json
{ "name": "Size", "value": "XL", "type": "string" }
{ "name": "Color", "value": "Red,#FF0000", "type": "color" }
```

**Attribute types:**
- `string` — plain text value
- `color` — format: `"ColorName,#HexCode"` (comma-separated name and hex)

### Variant Grouping

Products with the same `variantGroupId` are linked as variants:
```json
[
  { "sku": "TSHIRT-S", "title": "T-Shirt S", "price": 29, "variantGroupId": "tshirt-group" },
  { "sku": "TSHIRT-M", "title": "T-Shirt M", "price": 29, "variantGroupId": "tshirt-group" },
  { "sku": "TSHIRT-L", "title": "T-Shirt L", "price": 29, "variantGroupId": "tshirt-group" }
]
```

## Common Workflows

### Initial Store Setup from Spreadsheet Data
```
1. Prepare JSON with categories and products from spreadsheet
2. import_catalog(mode="merge", categories=[...], products=[...]) -> Import all
3. list_categories() -> Verify categories created
4. list_products() -> Verify products created
```

### Sync with External System
```
1. Get updated data from external system
2. import_catalog(mode="merge", products=[updated products]) -> Merge changes
   (SKU matching: existing products updated, new products added)
```

### Full Catalog Replace
```
1. import_catalog(mode="replace", categories=[...], products=[...])
   WARNING: This deletes ALL existing products and categories first!
```

## Best Practices

1. **Use "merge" mode** for most imports — safer and preserves existing data
2. **Use "replace" mode only** for full catalog resets
3. **Always set externalId** on categories for proper hierarchy linking
4. **Use SKU as the unique identifier** — merge mode matches by SKU
5. **Keep import under 10 MB** — split large catalogs into multiple imports
6. **Use imageUrls** — the platform downloads and stores images automatically
7. **Test with a small batch first** before importing the full catalog
8. **Use variantGroupId** to link product variants within the import
