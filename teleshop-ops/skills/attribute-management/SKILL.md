---
name: attribute-management
description: Attribute CRUD, adding attribute values, and variant configuration. Use when creating product attributes like color, size, or material, or managing attribute values.
---

# Attribute Management

This skill covers attribute operations — creating attributes (color, size, material, etc.), managing their values, and configuring which attributes can be used as product variants.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_attributes` | List all attributes with search and sorting |
| `get_attribute` | Get single attribute with all its values |
| `create_attribute` | Create a new attribute |
| `update_attribute` | Update attribute name or variant flag |
| `delete_attribute` | Delete an attribute |
| `add_attribute_values` | Add new values to an existing attribute |

## Listing Attributes

```
Tool: list_attributes
Input: {
  "search": "Color",
  "sortBy": "name",
  "sortOrder": "ASC"
}
```

**Parameters:**

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| search | string | any | Search by attribute name |
| sortBy | string | id, name, createdAt, updatedAt | Sort field |
| sortOrder | string | ASC, DESC | Sort direction |

## Getting an Attribute

```
Tool: get_attribute
Input: {"id": 1}

Returns: { id, name, type, isVariant, shopId, values[], createdAt, updatedAt }
```

## Creating Attributes

### Create Text Attribute
```
Tool: create_attribute
Input: {
  "name": "Material",
  "type": "select"
}
```

### Create Variant Attribute
```
Tool: create_attribute
Input: {
  "name": "Size",
  "type": "select",
  "isVariant": true
}
```

### Create Color Attribute
```
Tool: create_attribute
Input: {
  "name": "Color",
  "type": "color",
  "isVariant": true
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | YES | Attribute name (e.g., "Size", "Color") |
| type | string | YES | Attribute type: "select", "color", "text" |
| isVariant | boolean | no | Can be used to create product variants |

**Attribute types:**
- `select` — dropdown with predefined values (Size: S, M, L, XL)
- `color` — color picker with hex values and color names
- `text` — free text input

## Adding Attribute Values

```
Tool: add_attribute_values
Input: {
  "id": 1,
  "values": ["S", "M", "L", "XL", "XXL"]
}
```

Values are added to existing ones (not replaced).

## Updating Attributes

```
Tool: update_attribute
Input: {
  "id": 1,
  "name": "Clothing Size",
  "isVariant": true
}
```

**Updatable fields:**

| Field | Type | Description |
|-------|------|-------------|
| name | string | Attribute display name |
| isVariant | boolean | Enable/disable as variant selector |

## Deleting Attributes

```
Tool: delete_attribute
Input: {"id": 1}
```

Note: Deleting an attribute removes it from all products that use it.

## Variant Attributes

Attributes marked with `isVariant: true` can be used to create product variants. For example:
- **Size** (isVariant: true) → allows creating "T-Shirt S", "T-Shirt M", "T-Shirt L" as separate variants
- **Color** (isVariant: true) → allows "Blue Sneakers", "Red Sneakers" as variants
- **Material** (isVariant: false) → informational only, no variants created

## Common Workflows

### Set Up Clothing Store Attributes
```
1. create_attribute(name="Size", type="select", isVariant=true) -> Get ID
2. add_attribute_values(id, values=["XS","S","M","L","XL","XXL"]) -> Add sizes
3. create_attribute(name="Color", type="color", isVariant=true) -> Get ID
4. add_attribute_values(id, values=["Red","Blue","Black","White"]) -> Add colors
5. create_attribute(name="Material", type="select") -> Informational
6. add_attribute_values(id, values=["Cotton","Polyester","Wool","Silk"]) -> Add materials
```

### Set Up Electronics Attributes
```
1. create_attribute(name="Storage", type="select", isVariant=true)
2. add_attribute_values(id, values=["64GB","128GB","256GB","512GB","1TB"])
3. create_attribute(name="Color", type="color", isVariant=true)
4. add_attribute_values(id, values=["Black","Silver","Gold"])
5. create_attribute(name="RAM", type="select")
6. add_attribute_values(id, values=["4GB","8GB","16GB"])
```

### Extend Existing Attribute
```
1. get_attribute(id) -> Check current values
2. add_attribute_values(id, values=["NewValue1", "NewValue2"]) -> Add new values
```

## Best Practices

1. **Mark variant-capable attributes** with `isVariant: true` from the start
2. **Use "select" type** for fixed value sets (sizes, materials)
3. **Use "color" type** for color attributes to enable visual color pickers
4. **Create attributes before products** — easier to assign during product creation
5. **Add values in bulk** using add_attribute_values rather than one at a time
6. **Don't delete attributes** that are in use by products without updating those products first
