# Workflow Examples — Multi-Step MCP Patterns

## Workflow 1: Explore and Understand a Directus Instance

### Step 1: Get System Context

```json
Tool: system-prompt
Input: {}
```

### Step 2: Discover All Collections

```json
Tool: schema
Input: {}
```

### Step 3: Inspect Specific Collection

```json
Tool: schema
Input: { "keys": ["posts"] }
```

### Step 4: Read Sample Data

```json
Tool: items
Input: {
  "action": "read",
  "collection": "posts",
  "query": { "fields": ["*"], "limit": 5 }
}
```

### Step 5: Check Relations

```json
Tool: relations
Input: { "action": "read", "collection": "posts" }
```

---

## Workflow 2: Build a Collection with Fields and Relations

### Step 1: Create the Collection

```json
Tool: collections
Input: {
  "action": "create",
  "data": [{
    "collection": "products",
    "schema": {},
    "meta": {
      "icon": "inventory_2",
      "display_template": "{{name}} — ${{price}}",
      "sort_field": "sort"
    }
  }]
}
```

### Step 2: Add Basic Fields

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "products",
  "data": [
    { "field": "name", "type": "string", "meta": { "interface": "input" }, "schema": { "is_nullable": false } },
    { "field": "description", "type": "text", "meta": { "interface": "input-rich-text-md" } },
    { "field": "price", "type": "decimal", "meta": { "interface": "input", "options": { "prefix": "$" } } },
    { "field": "sku", "type": "string", "meta": { "interface": "input" }, "schema": { "is_unique": true } },
    { "field": "status", "type": "string", "meta": { "interface": "select-dropdown", "options": { "choices": [{"text": "Draft", "value": "draft"}, {"text": "Active", "value": "active"}, {"text": "Discontinued", "value": "discontinued"}] } }, "schema": { "default_value": "draft" } },
    { "field": "sort", "type": "integer", "meta": { "interface": "input", "hidden": true } }
  ]
}
```

### Step 3: Add M2O Relation to Brand

First, ensure the `brands` collection exists. Then:

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "products",
  "data": [{
    "field": "brand",
    "type": "uuid",
    "meta": { "interface": "select-dropdown-m2o", "special": ["m2o"], "display": "related-values" }
  }]
}
```

```json
Tool: relations
Input: {
  "action": "create",
  "collection": "products",
  "field": "brand",
  "data": {
    "collection": "products",
    "field": "brand",
    "related_collection": "brands",
    "schema": { "on_delete": "SET NULL" },
    "meta": {}
  }
}
```

### Step 4: Add Featured Image (File Relation)

```json
Tool: fields
Input: {
  "action": "create",
  "collection": "products",
  "data": [{
    "field": "image",
    "type": "uuid",
    "meta": { "interface": "file-image", "special": ["file"], "display": "image" }
  }]
}
```

```json
Tool: relations
Input: {
  "action": "create",
  "collection": "products",
  "field": "image",
  "data": {
    "collection": "products",
    "field": "image",
    "related_collection": "directus_files",
    "schema": { "on_delete": "SET NULL" },
    "meta": {}
  }
}
```

### Step 5: Verify Schema

```json
Tool: schema
Input: { "keys": ["products"] }
```

### Step 6: Create Sample Data

```json
Tool: items
Input: {
  "action": "create",
  "collection": "products",
  "data": [
    { "name": "Widget Pro", "description": "Professional-grade widget", "price": 49.99, "sku": "WDG-PRO-001", "status": "active" },
    { "name": "Widget Basic", "description": "Entry-level widget", "price": 19.99, "sku": "WDG-BAS-001", "status": "active" }
  ]
}
```

---

## Workflow 3: Import Batch Data

### Step 1: Check Target Collection Schema

```json
Tool: schema
Input: { "keys": ["contacts"] }
```

### Step 2: Create Items in Batches

```json
Tool: items
Input: {
  "action": "create",
  "collection": "contacts",
  "data": [
    { "first_name": "Alice", "last_name": "Smith", "email": "alice@example.com", "company": "Acme Inc" },
    { "first_name": "Bob", "last_name": "Jones", "email": "bob@example.com", "company": "Tech Corp" },
    { "first_name": "Carol", "last_name": "Williams", "email": "carol@example.com", "company": "Design Co" }
  ]
}
```

Repeat with next batch (10-25 items per call).

### Step 3: Verify Import

```json
Tool: items
Input: {
  "action": "read",
  "collection": "contacts",
  "query": {
    "aggregate": { "count": ["*"] }
  }
}
```

---

## Workflow 4: Set Up Automation Flow

### Step 1: Create the Flow

```json
Tool: flows
Input: {
  "action": "create",
  "data": {
    "name": "Welcome Email on User Create",
    "trigger": "event",
    "status": "active",
    "icon": "mail",
    "options": {
      "type": "action",
      "scope": ["items.create"],
      "collections": ["contacts"]
    }
  }
}
```

### Step 2: Create Log Operation

```json
Tool: operations
Input: {
  "action": "create",
  "data": {
    "flow": "FLOW_UUID",
    "key": "log_new_contact",
    "type": "log",
    "name": "Log New Contact",
    "options": { "message": "New contact: {{ $trigger.payload.email }}" },
    "position_x": 20,
    "position_y": 1
  }
}
```

### Step 3: Create Email Operation

```json
Tool: operations
Input: {
  "action": "create",
  "data": {
    "flow": "FLOW_UUID",
    "key": "send_welcome",
    "type": "mail",
    "name": "Send Welcome Email",
    "options": {
      "to": "{{ $trigger.payload.email }}",
      "subject": "Welcome, {{ $trigger.payload.first_name }}!",
      "body": "Thank you for joining us."
    },
    "position_x": 40,
    "position_y": 1
  }
}
```

### Step 4: Connect Operations

```json
Tool: operations
Input: {
  "action": "update",
  "key": "log_new_contact",
  "data": { "resolve": "SEND_WELCOME_UUID" }
}
```

### Step 5: Set Flow Entry Point

```json
Tool: flows
Input: {
  "action": "update",
  "key": "FLOW_UUID",
  "data": { "operation": "LOG_NEW_CONTACT_UUID" }
}
```

---

## Workflow 5: File Organization

### Step 1: Create Folder Structure

```json
Tool: folders
Input: {
  "action": "create",
  "data": [
    { "name": "Blog" },
    { "name": "Products" },
    { "name": "Team" }
  ]
}
```

### Step 2: Import Images

```json
Tool: files
Input: {
  "action": "import",
  "data": [
    { "url": "https://example.com/hero.jpg", "file": { "title": "Blog Hero", "folder": "BLOG_FOLDER_UUID" } },
    { "url": "https://example.com/product1.jpg", "file": { "title": "Product 1", "folder": "PRODUCTS_FOLDER_UUID" } }
  ]
}
```

### Step 3: Verify Files

```json
Tool: files
Input: {
  "action": "read",
  "query": {
    "fields": ["id", "title", "folder.name", "type"],
    "sort": ["-uploaded_on"],
    "limit": 10
  }
}
```
