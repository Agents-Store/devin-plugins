# NocoBase MCP Workflow Examples

Complete multi-step workflows combining multiple MCP tools.

## Workflow 1: Build a CRUD Page from Scratch

Build a complete contacts management page with table, actions, and columns.

### Steps

```
1. health_check()
   → Verify server is running

2. collection_get("contacts")
   → { fields: [name, email, phone, company, status, createdAt] }

3. page_create({ title: "Contacts", icon: "UserOutlined" })
   → { id: "page_1" }

4. table_add({ pageId: "page_1", collection: "contacts", type: "table" })
   → { blockId: "block_1" }

5. column_add({ blockId: "block_1", fieldName: "name" })
   column_add({ blockId: "block_1", fieldName: "email" })
   column_add({ blockId: "block_1", fieldName: "phone" })
   column_add({ blockId: "block_1", fieldName: "status" })
   column_add({ blockId: "block_1", fieldName: "createdAt" })
   → All columns added

6. action_add({ blockId: "block_1", type: "create" })
   action_add({ blockId: "block_1", type: "edit" })
   action_add({ blockId: "block_1", type: "delete" })
   action_add({ blockId: "block_1", type: "filter" })
   action_add({ blockId: "block_1", type: "export" })
   → All actions added

7. page_inspect("page_1")
   → Verify complete structure
```

## Workflow 2: Build Complete CRM Application

Create a full CRM with multiple pages organized under a menu group.

### Steps

```
1. collection_list()
   → [contacts, companies, deals, products]

2. menu_create_group({ title: "CRM", icon: "TeamOutlined" })
   → { id: "crm_group" }

3. // Contacts page — table view
   page_create({ title: "Contacts", parent: "CRM" })
   → { id: "page_contacts" }
   table_add({ pageId: "page_contacts", collection: "contacts", type: "table" })
   → { blockId: "block_contacts" }
   column_add({ blockId: "block_contacts", fieldName: "name" })
   column_add({ blockId: "block_contacts", fieldName: "email" })
   column_add({ blockId: "block_contacts", fieldName: "company" })
   column_add({ blockId: "block_contacts", fieldName: "status" })
   action_add({ blockId: "block_contacts", type: "create" })
   action_add({ blockId: "block_contacts", type: "edit" })
   action_add({ blockId: "block_contacts", type: "delete" })
   action_add({ blockId: "block_contacts", type: "filter" })

4. // Deals page — kanban view
   page_create({ title: "Deals", parent: "CRM" })
   → { id: "page_deals" }
   table_add({ pageId: "page_deals", collection: "deals", type: "kanban", groupField: "stage" })
   → { blockId: "block_deals" }
   column_add({ blockId: "block_deals", fieldName: "title" })
   column_add({ blockId: "block_deals", fieldName: "amount" })
   column_add({ blockId: "block_deals", fieldName: "contact" })
   column_add({ blockId: "block_deals", fieldName: "closeDate" })

5. // Companies page — table view
   page_create({ title: "Companies", parent: "CRM" })
   → { id: "page_companies" }
   table_add({ pageId: "page_companies", collection: "companies", type: "table" })
   → { blockId: "block_companies" }
   column_add({ blockId: "block_companies", fieldName: "name" })
   column_add({ blockId: "block_companies", fieldName: "industry" })
   column_add({ blockId: "block_companies", fieldName: "website" })
   action_add({ blockId: "block_companies", type: "create" })
   action_add({ blockId: "block_companies", type: "edit" })

6. page_list()
   → Verify all pages created under CRM group
```

## Workflow 3: Seed Data into a Collection

Import sample data into a collection for testing.

### Steps

```
1. collection_get("products")
   → { fields: [name, price, category, stock, description] }

2. data_create("products", { name: "Widget A", price: 29.99, category: "Widgets", stock: 100 })
   data_create("products", { name: "Widget B", price: 49.99, category: "Widgets", stock: 50 })
   data_create("products", { name: "Gadget X", price: 199.99, category: "Gadgets", stock: 25 })
   data_create("products", { name: "Tool Pro", price: 89.99, category: "Tools", stock: 75 })
   → 4 records created

3. data_list("products", { sort: ["-price"] })
   → Verify all records, sorted by price descending
```

## Workflow 4: Audit and Clean Up Application

Review existing pages and remove empty or unused ones.

### Steps

```
1. page_list()
   → [page_1: "Contacts", page_2: "Old Test", page_3: "Dashboard", page_4: "Untitled"]

2. page_inspect("page_2")
   → { blocks: [] }  // empty page

3. page_inspect("page_4")
   → { blocks: [] }  // empty page

4. page_delete("page_2")
   page_delete("page_4")
   → Removed empty pages

5. page_list()
   → [page_1: "Contacts", page_3: "Dashboard"]  // Clean
```
