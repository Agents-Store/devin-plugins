---
name: field-relations
description: Field types, relationship configuration — M2O, O2M, M2M, M2A, translations, files. This skill should be used when the user asks to add fields, configure field types, set up relations, create relationships between Directus collections, or design M2O/O2M/M2M/M2A structures.
---

# Fields & Relations

Complete reference for the `fields` and `relations` MCP tools — field types, interfaces, and relationship workflows.

## Fields Tool

### Creating Fields

**Critical: `data` is ALWAYS an array**, even for a single field.

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "posts",
  "data": [{
    "field": "title",
    "type": "string",
    "meta": {
      "interface": "input",
      "note": "Post title",
      "required": true
    },
    "schema": {
      "is_nullable": false
    }
  }]
}
```

### Reading Fields

```json
Tool: fields
Input: { "action": "read", "collection": "posts" }
```

Or read a specific field:

```json
Tool: fields
Input: { "action": "read", "collection": "posts", "field": "title" }
```

### Deleting Fields

```json
Tool: fields
Input: { "action": "delete", "collection": "posts", "field": "deprecated_field" }
```

## Field Types Reference

| Type | Description | Typical Interface |
|------|-------------|-------------------|
| `string` | Short text (max 255) | `input` |
| `text` | Long text (unlimited) | `input-multiline`, `input-rich-text-md`, `input-rich-text-html` |
| `uuid` | UUID identifier | `input` (auto-generated for PKs) |
| `hash` | Hashed value | `input-hash` |
| `integer` | Whole number | `input` |
| `bigInteger` | Large whole number | `input` |
| `float` | Floating point | `input` |
| `decimal` | Exact decimal | `input` |
| `timestamp` | Date + time (with timezone) | `datetime` |
| `datetime` | Date + time (no timezone) | `datetime` |
| `date` | Date only | `datetime` |
| `time` | Time only | `datetime` |
| `boolean` | True/false | `boolean`, `toggle` |
| `json` | JSON data | `input-code`, `select-multiple-dropdown` |
| `csv` | Comma-separated values | `tags` |
| `alias` | Virtual field (no column) | Used for O2M, M2M, M2A |

## Common Interface Mappings

| Use Case | Type | Interface | Meta Options |
|----------|------|-----------|--------------|
| Short text | `string` | `input` | — |
| Rich text | `text` | `input-rich-text-md` | — |
| Dropdown | `string` | `select-dropdown` | `options.choices: [{text, value}]` |
| Tags | `json` | `tags` | — |
| Toggle | `boolean` | `boolean` | — |
| Number | `integer` | `input` | — |
| Currency | `decimal` | `input` | `options.prefix: "$"` |
| Date picker | `datetime` | `datetime` | — |
| Color picker | `string` | `select-color` | — |
| Slug | `string` | `input` | `options.slug: true` |
| Image (single) | `uuid` | `file-image` | `special: ["file"]` |
| File (single) | `uuid` | `file` | `special: ["file"]` |

## Relationship Types

### M2O (Many-to-One)

Example: Many posts belong to one author.

**Step 1: Create the M2O field** (uuid type in the "many" collection):

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "posts",
  "data": [{
    "field": "author",
    "type": "uuid",
    "meta": {
      "interface": "select-dropdown-m2o",
      "special": ["m2o"],
      "display": "related-values",
      "display_options": { "template": "{{first_name}} {{last_name}}" }
    },
    "schema": {}
  }]
}
```

**Step 2: Create the relation:**

```json
Tool: relations
Input: {
  "action": "create",
  "collection": "posts",
  "field": "author",
  "data": {
    "collection": "posts",
    "field": "author",
    "related_collection": "authors",
    "schema": { "on_delete": "SET NULL" },
    "meta": {}
  }
}
```

### O2M (One-to-Many)

Example: One author has many posts. This is the reverse side of M2O — an alias field on the "one" collection.

**The M2O side must exist first.** Then add an alias field to the "one" collection:

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "authors",
  "data": [{
    "field": "posts",
    "type": "alias",
    "meta": {
      "interface": "list-o2m",
      "special": ["o2m"],
      "display": "related-values"
    }
  }]
}
```

Then create the relation from the O2M side:

```json
Tool: relations
Input: {
  "action": "create",
  "collection": "posts",
  "field": "author",
  "data": {
    "collection": "posts",
    "field": "author",
    "related_collection": "authors",
    "schema": { "on_delete": "SET NULL" },
    "meta": { "one_field": "posts" }
  }
}
```

### M2M (Many-to-Many)

Example: Posts can have many tags, tags can belong to many posts.

**Step 1: Create junction collection:**

```json
Tool: collections
Input: {
  "action": "create",
  "data": [{
    "collection": "posts_tags",
    "schema": {},
    "meta": { "hidden": true, "icon": "import_export" }
  }]
}
```

**Step 2: Create M2O fields in junction:**

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "posts_tags",
  "data": [
    {
      "field": "posts_id",
      "type": "uuid",
      "meta": { "hidden": true }
    },
    {
      "field": "tags_id",
      "type": "uuid",
      "meta": { "hidden": true }
    }
  ]
}
```

**Step 3: Create alias fields on both parent collections:**

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "posts",
  "data": [{
    "field": "tags",
    "type": "alias",
    "meta": {
      "interface": "list-m2m",
      "special": ["m2m"],
      "display": "related-values",
      "display_options": { "template": "{{tags_id.name}}" }
    }
  }]
}
```

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "tags",
  "data": [{
    "field": "posts",
    "type": "alias",
    "meta": {
      "interface": "list-m2m",
      "special": ["m2m"],
      "display": "related-values"
    }
  }]
}
```

**Step 4: Create relations:**

```json
Tool: relations
Input: {
  "action": "create",
  "collection": "posts_tags",
  "field": "posts_id",
  "data": {
    "collection": "posts_tags",
    "field": "posts_id",
    "related_collection": "posts",
    "schema": { "on_delete": "CASCADE" },
    "meta": { "one_field": "tags", "junction_field": "tags_id" }
  }
}
```

```json
Tool: relations
Input: {
  "action": "create",
  "collection": "posts_tags",
  "field": "tags_id",
  "data": {
    "collection": "posts_tags",
    "field": "tags_id",
    "related_collection": "tags",
    "schema": { "on_delete": "CASCADE" },
    "meta": { "one_field": "posts", "junction_field": "posts_id" }
  }
}
```

### M2A (Many-to-Any)

Polymorphic relation — items can relate to different collection types. Used for page builders, flexible content blocks.

**Step 1: Create junction collection** with `item` (uuid) and `collection` (string) fields:

```json
Tool: collections
Input: {
  "action": "create",
  "data": [{
    "collection": "page_sections",
    "schema": {},
    "meta": { "hidden": true }
  }]
}
```

**Step 2: Add junction fields:**

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "page_sections",
  "data": [
    { "field": "pages_id", "type": "uuid" },
    { "field": "item", "type": "uuid", "meta": { "hidden": true } },
    { "field": "collection", "type": "string", "meta": { "hidden": true } },
    { "field": "sort", "type": "integer", "meta": { "hidden": true } }
  ]
}
```

**Step 3: Add M2A alias on parent:**

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "pages",
  "data": [{
    "field": "sections",
    "type": "alias",
    "meta": {
      "interface": "list-m2a",
      "special": ["m2a"],
      "options": {
        "allowedCollections": ["headings", "paragraphs", "images", "cta_blocks"]
      }
    }
  }]
}
```

### File Relation (Single File)

Relate a field to `directus_files`:

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "posts",
  "data": [{
    "field": "featured_image",
    "type": "uuid",
    "meta": {
      "interface": "file-image",
      "special": ["file"],
      "display": "image"
    }
  }]
}
```

Then create the relation to `directus_files`:

```json
Tool: relations
Input: {
  "action": "create",
  "collection": "posts",
  "field": "featured_image",
  "data": {
    "collection": "posts",
    "field": "featured_image",
    "related_collection": "directus_files",
    "schema": { "on_delete": "SET NULL" },
    "meta": {}
  }
}
```

## on_delete Options

| Value | Behavior |
|-------|----------|
| `SET NULL` | Set foreign key to null (default, safe) |
| `CASCADE` | Delete related items (use for junction tables) |
| `NO ACTION` | Prevent deletion if related items exist |
| `SET DEFAULT` | Reset to default value |

## Common Mistakes

1. **Wrong type for relation fields** — M2O fields must be `uuid`, O2M/M2M/M2A fields must be `alias`
2. **Missing `meta.special`** — M2O needs `["m2o"]`, O2M needs `["o2m"]`, M2M needs `["m2m"]`, M2A needs `["m2a"]`, files need `["file"]`
3. **Forgetting junction collection** — M2M requires a dedicated junction collection with two M2O fields
4. **Wrong schema for alias fields** — Alias fields (O2M, M2M, M2A) should NOT have a `schema` property (or set `schema: null`)
5. **Creating relations before fields** — The field must exist before the relation is created
6. **Missing `one_field` in M2M meta** — The `meta.one_field` tells Directus which alias field on the related collection to populate
7. **Forgetting `junction_field` in M2M meta** — Required for M2M relations to know which field in the junction points to the other collection
