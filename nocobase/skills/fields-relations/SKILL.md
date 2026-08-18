---
name: fields-relations
description: Field types and relation configuration — basic, advanced, relation fields, foreign keys, through tables. This skill should be used when the user asks to configure fields, set up relations between collections, or manage foreign keys and through tables.
---

# Fields & Relations

Expert guidance on NocoBase field types and relation configuration.

## Basic Field Types

| Type | Description | Config |
|------|-------------|--------|
| string | Short text (255 chars) | maxLength, pattern |
| text | Long text | - |
| richText | Rich text with formatting | - |
| integer | Whole number | min, max |
| float | Decimal number | precision |
| decimal | Precise decimal | precision, scale |
| boolean | True/false | defaultValue |
| date | Date only | format |
| datetime | Date + time | format, timezone |
| time | Time only | format |
| email | Email address | validation built-in |
| phone | Phone number | validation built-in |
| url | Web URL | validation built-in |
| password | Masked input | - |
| color | Color picker | - |
| icon | Icon selector | - |
| json | JSON data | - |
| array | Array of values | - |

## Selection Fields

### Single Select
```json
{
  "type": "string",
  "interface": "select",
  "uiSchema": {
    "enum": [
      { "value": "lead", "label": "Lead" },
      { "value": "active", "label": "Active" },
      { "value": "inactive", "label": "Inactive" }
    ]
  }
}
```

### Multi Select
```json
{
  "type": "array",
  "interface": "multipleSelect",
  "uiSchema": {
    "enum": [
      { "value": "feature", "label": "Feature" },
      { "value": "bug", "label": "Bug" },
      { "value": "urgent", "label": "Urgent" }
    ]
  }
}
```

### Checkbox Group
```json
{
  "type": "array",
  "interface": "checkboxGroup",
  "uiSchema": {
    "enum": [...]
  }
}
```

## Advanced Fields

| Type | Description | Use Case |
|------|-------------|----------|
| formula | Calculated field | `{{price}} * {{quantity}}` |
| sequence | Auto-incrementing | `ORD-{YYYYMMDD}-{0000}` |
| snapshot | Point-in-time copy | Order snapshot of product |
| nanoid | Short unique ID | Public-facing IDs |
| uuid | Universal unique ID | API identifiers |
| sort | Drag-and-drop ordering | List ordering |
| attachment | File upload | Documents, images |

### Formula Field
```json
{
  "type": "formula",
  "expression": "{{price}} * {{quantity}} * (1 - {{discount}} / 100)"
}
```

### Sequence Field
```json
{
  "type": "sequence",
  "patterns": [
    { "type": "string", "options": { "value": "ORD-" } },
    { "type": "date", "options": { "format": "YYYYMMDD" } },
    { "type": "string", "options": { "value": "-" } },
    { "type": "integer", "options": { "digits": 4, "start": 1, "key": "order_seq" } }
  ]
}
```

## Relation Types

### belongsTo (Many-to-One)
Child record belongs to one parent.
```
contacts.company → companies (each contact has one company)

Config:
  - Source collection: contacts
  - Target collection: companies
  - Foreign key: companyId (in contacts table)
```

### hasMany (One-to-Many)
Parent has many children. Reverse of belongsTo.
```
companies.contacts → contacts[] (company has many contacts)

Config:
  - Source collection: companies
  - Target collection: contacts
  - Foreign key: companyId (in contacts table)
```

### hasOne (One-to-One)
Exclusive one-to-one relationship.
```
users.profile → profiles (each user has one profile)

Config:
  - Source collection: users
  - Target collection: profiles
  - Foreign key: userId (in profiles table)
```

### belongsToMany (Many-to-Many)
Both sides have many. Requires a through/junction table.
```
deals ↔ products (via deal_products)

Config:
  - Source: deals
  - Target: products
  - Through: deal_products
  - Source key: dealId (in deal_products)
  - Target key: productId (in deal_products)
```

## Relation Design Patterns

### Simple belongsTo
```
Collection: contacts
  company: belongsTo → companies
  └── Foreign key: companyId
  └── Display field: companies.name
```

### hasMany with Nested Display
```
Collection: companies
  contacts: hasMany → contacts
  └── Show in table block as sub-table
  └── Allow inline creation
```

### Many-to-Many with Through Data
```
Collections:
  orders: hasMany → order_items
  products: hasMany → order_items

  order_items (through table):
    - order: belongsTo → orders
    - product: belongsTo → products
    - quantity: integer
    - unitPrice: decimal
    - lineTotal: formula (quantity * unitPrice)
```

### Polymorphic Relation
```
Collection: comments
  - commentableType: string (distinguishes target collection)
  - commentableId: bigInt (target record ID)

Can reference: posts, products, orders
```

## Field Validation

| Validation | Description | Example |
|-----------|-------------|---------|
| required | Must have value | Name field |
| unique | No duplicates | Email, SKU |
| min/max | Number range | Age: 0-150 |
| minLength/maxLength | Text length | Title: 1-200 |
| pattern | Regex match | SKU format |
| enum | From predefined list | Status values |

## Best Practices

1. **Choose the right relation type** — belongsTo for "this record has one parent", hasMany for "this record has many children"
2. **Use through tables for M2M** — store additional data on the relationship (quantity, price)
3. **Set display fields on relations** — configure which field from related collection to show
4. **Enable cascading** — delete children when parent is deleted (where appropriate)
5. **Use formula over duplication** — calculate values instead of copying from related records
6. **Validate at field level** — required, unique, min/max save data integrity issues later
7. **Plan foreign keys** — understand which table holds the foreign key in each relation
