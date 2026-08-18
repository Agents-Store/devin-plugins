---
name: collections-design
description: Collection design patterns — collection types, naming conventions, system fields, inheritance, tree structures. This skill should be used when the user asks to design a data model, create collections, plan entity relationships, or choose collection types.
---

# Collections Design

Expert guidance on designing NocoBase collections (data models) — types, naming, system fields, inheritance, and architecture patterns.

## Collection Types

| Type | Description | Use Case |
|------|-------------|----------|
| General | Standard data collection | Contacts, Orders, Products |
| Tree | Hierarchical with parent-child | Categories, Org Structure |
| Calendar | Date-based entries | Events, Appointments |
| File | File storage collection | Documents, Attachments |
| Expression | Computed/virtual collection | Aggregated views |

## Naming Conventions

- **Collection names:** snake_case, plural (`contacts`, `order_items`, `task_comments`)
- **Field names:** camelCase (`firstName`, `orderDate`, `totalAmount`)
- **Relation fields:** describe the relationship (`company`, `assignee`, `tags`)
- **Through tables:** combine both collection names (`order_products`, `user_roles`)

## System Fields

Every collection should include:

| Field | Type | Purpose |
|-------|------|---------|
| id | bigInt (auto) | Primary key |
| createdAt | datetime | Record creation time |
| updatedAt | datetime | Last modification time |
| createdBy | belongsTo (users) | Who created the record |
| updatedBy | belongsTo (users) | Who last modified |

NocoBase adds these automatically when enabled in collection settings.

## Design Process

### Step 1: Identify Entities
List all data entities the application needs. Think in terms of:
- **Core entities:** Main business objects (Contacts, Orders, Products)
- **Supporting entities:** Reference data (Categories, Statuses, Tags)
- **Junction entities:** Many-to-many bridges (OrderItems, UserRoles)

### Step 2: Define Fields per Entity
For each entity, list fields with types:
```
contacts:
  - name: string (required)
  - email: email (unique)
  - phone: phone
  - status: singleSelect (Lead, Active, Inactive)
  - avatar: attachment
  - notes: richText
  - birthday: date
```

### Step 3: Map Relations
Draw entity relationships:
```
companies ──< contacts (one company has many contacts)
contacts ──< deals (one contact has many deals)
deals >──< products (many-to-many via deal_products)
```

### Step 4: Create in Order
```
1. Independent collections (no foreign keys): companies, products, categories
2. Dependent collections: contacts (needs companies), deals (needs contacts)
3. Junction collections: deal_products (needs deals + products)
4. Set up relations between collections
5. Add computed/formula fields
```

## Collection Architecture Patterns

### Master-Detail
```
orders (master)
  ├── order_items (detail, hasMany)
  └── order_notes (detail, hasMany)
```

### Self-Referencing (Tree)
```
categories
  └── parent (belongsTo → categories, self-reference)
  └── children (hasMany → categories)
```

### Polymorphic
```
comments
  - commentable_type: string (posts, products, orders)
  - commentable_id: bigInt
  → Can belong to different collection types
```

### Soft Delete
```
Add field: deletedAt (datetime, nullable)
Filter by default: where deletedAt IS NULL
```

## Inheritance

NocoBase supports collection inheritance:
```
base_collection: people
  - name, email, phone

child_collection: employees (inherits people)
  - department, salary, hireDate

child_collection: customers (inherits people)
  - company, tier, lastPurchase
```

Inherited collections share base fields and can add their own.

## Tools for Collection Inspection

| Tool | Purpose |
|------|---------|
| `collection_list` | List all existing collections |
| `collection_get` | Get collection details — fields, types, relations |

### Workflow: Inspect Existing Schema Before Designing

Before creating new collections, always check what already exists:

```
Step 1: collection_list → get all collections
Step 2: collection_get → for each relevant collection, get field details
Step 3: Identify gaps — what collections/fields are missing
Step 4: Design new collections considering existing relations
```

Example:
```
collection_list()
  → [{ name: "users" }, { name: "companies" }, { name: "products" }]

collection_get("companies")
  → { name: "companies", fields: [
       { name: "name", type: "string" },
       { name: "industry", type: "singleSelect" },
       { name: "contacts", type: "hasMany", target: "contacts" }
     ] }

// Now design "contacts" knowing that "companies" already has a hasMany relation
```

### Workflow: Validate Schema Design

After designing on paper, verify against the instance:

```
Step 1: collection_list → confirm no naming conflicts
Step 2: collection_get → check existing collections for relation compatibility
Step 3: Document creation order based on dependencies
```

## Best Practices

1. **Plan before building** — sketch ERD on paper or whiteboard
2. **Inspect existing schema** — always run `collection_list` and `collection_get` before adding new collections
3. **Normalize data** — avoid storing the same data in multiple places
4. **Use proper field types** — email for emails, phone for phones (enables validation)
5. **Enable system fields** — always include createdAt, updatedAt, createdBy
6. **Name consistently** — stick to naming conventions project-wide
7. **Start with core entities** — build the minimum viable data model first
8. **Use relations, not IDs** — configure proper belongsTo/hasMany instead of raw foreign keys
9. **Design for UI** — consider what blocks and views you'll need when choosing field types
