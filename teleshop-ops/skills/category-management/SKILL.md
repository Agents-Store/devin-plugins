---
name: category-management
description: Category CRUD, batch operations, and hierarchy management. Use when creating, updating, deleting, or listing categories in a Teleshop store.
---

# Category Management

This skill covers category operations — creating category hierarchies, listing, updating, and deleting categories individually or in batches.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_categories` | List categories with search and sorting |
| `get_category` | Get single category details |
| `create_category` | Create a new category |
| `batch_create_categories` | Create multiple categories at once |
| `update_category` | Update an existing category |
| `delete_category` | Delete a category |
| `batch_delete_categories` | Delete multiple categories at once |

## Listing Categories

```
Tool: list_categories
Input: {
  "search": "Electronics",
  "sortBy": "position",
  "sortOrder": "ASC"
}
```

**Parameters:**

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| search | string | any | Search by category title |
| sortBy | string | id, title, createdAt, updatedAt, position | Sort field |
| sortOrder | string | ASC, DESC | Sort direction |

**Response:** `{ items: CategoryDto[], meta: PaginationMetaDto }`

**CategoryDto fields:** id, title, parentId, categoryNumber, position, orderBy, shopId, createdAt, updatedAt, image, parent

## Getting a Category

```
Tool: get_category
Input: {"id": 5}

Returns category with parent info and image.
```

## Creating Categories

### Create Simple Category
```
Tool: create_category
Input: {
  "title": "Electronics"
}
```

### Create Subcategory
```
Tool: create_category
Input: {
  "title": "Smartphones",
  "parentId": 5,
  "orderBy": "popular"
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | YES | Category name |
| orderBy | string | no | Default product sort: cheap, expensive, novelty, popular |
| parentId | number | no | Parent category ID (for subcategories) |
| imageId | number | no | Image ID for category thumbnail |

### Batch Create Categories
```
Tool: batch_create_categories
Input: {
  "categories": [
    { "title": "Clothing" },
    { "title": "T-Shirts", "parentId": 10 },
    { "title": "Jeans", "parentId": 10 },
    { "title": "Shoes" }
  ]
}
```

## Updating Categories

```
Tool: update_category
Input: {
  "id": 5,
  "title": "Consumer Electronics",
  "orderBy": "novelty"
}
```

All fields are optional — only send what you want to change.

## Deleting Categories

### Delete Single Category
```
Tool: delete_category
Input: {"id": 5}
```
Note: Default categories cannot be deleted. Products in deleted categories may need reassignment.

### Batch Delete Categories
```
Tool: batch_delete_categories
Input: {"categoryIds": [10, 11, 12]}
```

## Product Ordering in Categories

The `orderBy` field controls how products are sorted by default within a category:

| Value | Description |
|-------|-------------|
| `cheap` | Cheapest first (price ASC) |
| `expensive` | Most expensive first (price DESC) |
| `novelty` | Newest first (createdAt DESC) |
| `popular` | Most popular first |

## Common Workflows

### Build Category Hierarchy
```
1. create_category(title="Clothing") -> Get parent ID
2. create_category(title="Men", parentId=parentId) -> Subcategory
3. create_category(title="Women", parentId=parentId) -> Subcategory
4. create_category(title="T-Shirts", parentId=menId) -> Sub-subcategory
```

### Reorganize Categories
```
1. list_categories() -> View current structure
2. update_category(id, parentId=newParentId) -> Move to new parent
3. update_category(id, title="New Name") -> Rename
```

### Clean Up Empty Categories
```
1. list_categories() -> Get all categories
2. For each: list_products(category=title) -> Check if empty
3. batch_delete_categories(categoryIds=[empty ones]) -> Remove empties
```

## Best Practices

1. **Plan hierarchy first** before creating categories
2. **Use batch_create_categories** for initial store setup
3. **Set orderBy** based on category type (novelty for new arrivals, cheap for budget categories)
4. **Use parentId** to create up to 3 levels of nesting
5. **Don't delete categories with products** — reassign products first
