---
name: ui-configuration
description: UI blocks, pages, actions, and field components. This skill should be used when the user asks to create a page, add a table or form block, build a dashboard, set up a kanban board, or configure menu structure.
---

# UI Configuration

Expert guidance on NocoBase UI configuration — blocks, pages, actions, field components, and layout design.

## Block Types

| Block | Description | Best For |
|-------|-------------|----------|
| Table | Data grid with columns | Data listing, CRUD |
| Form | Input form | Record creation, editing |
| Details | Read-only record view | Record display |
| Kanban | Board view by status | Pipeline tracking |
| Calendar | Date-based calendar | Scheduling, events |
| Gantt | Timeline chart | Project planning |
| List | Simple list layout | Simple data display |
| Grid Card | Card layout in grid | Visual catalogs |
| Chart | Data visualization | Reports, dashboards |
| Markdown | Static content | Instructions, documentation |
| Iframe | Embedded external content | External tools |

## Table Block

### Configuration
```
Collection: contacts
Fields visible: [name, email, phone, company, status, createdAt]
Default sort: createdAt DESC
Page size: 20
Actions:
  - Create (opens form)
  - Edit (inline or modal)
  - Delete (with confirmation)
  - Filter
  - Export
  - Bulk actions
```

### Column Configuration
```
Column: name
  - Width: 200px
  - Fixed: left
  - Sortable: true
  - Filterable: true

Column: status
  - Component: Tag (colored)
  - Width: 120px
  - Filterable: true

Column: email
  - Component: Link (mailto)
  - Width: 250px

Column: createdAt
  - Format: YYYY-MM-DD HH:mm
  - Width: 180px
  - Sortable: true
```

## Form Block

### Configuration
```
Collection: contacts
Mode: create / edit
Layout: vertical / horizontal
Fields:
  - name (required, text input)
  - email (required, email input)
  - phone (phone input)
  - company (relation picker → companies)
  - status (select dropdown)
  - notes (rich text editor)
  - avatar (image upload)

Actions:
  - Submit
  - Cancel
  - Save as Draft
```

### Field Layout
```
Grid layout example:
Row 1: [name (50%), email (50%)]
Row 2: [phone (50%), company (50%)]
Row 3: [status (30%), birthday (30%), source (40%)]
Row 4: [notes (100%)]
Row 5: [Submit] [Cancel]
```

## Kanban Block

### Configuration
```
Collection: deals
Group by: stage (SingleSelect)
Columns: [Discovery, Proposal, Negotiation, Closed Won, Closed Lost]
Card fields: [title, amount, contact.name, closeDate]
Sort within column: -amount (highest first)
```

### Card Template
```
Card displays:
  - Title: deal title (bold)
  - Subtitle: contact name
  - Badge: amount (formatted as currency)
  - Footer: close date
```

## Calendar Block

### Configuration
```
Collection: events
Date field: startDate
End date field: endDate (optional, for multi-day events)
Title field: title
Color field: category (color by type)
```

## Chart Block

### Configuration
```
Collection: orders
Type: bar / line / pie / doughnut / area
X axis: month (date field, grouped by month)
Y axis: total (sum of amount)
Group by: status
```

## Actions

### Standard CRUD Actions
| Action | Description | Config |
|--------|-------------|--------|
| Create | Open create form | Form block, modal/drawer/page |
| Edit | Open edit form | Form block, modal/drawer/inline |
| View | Open details | Details block, modal/drawer/page |
| Delete | Delete record | Confirmation dialog |
| Duplicate | Copy record | Pre-fill form |
| Print | Print record | Print template |
| Export | Export to Excel/CSV | Field selection |

### Bulk Actions
```
Available for Table block:
  - Bulk delete
  - Bulk update (specific fields)
  - Bulk export
```

### Custom Actions
```
Action: Submit for Approval
Type: Workflow trigger
Workflow: approval_flow
Condition: status == "Draft"
Confirmation: "Are you sure you want to submit?"
```

## Page & Menu Structure

### Page Layout
```
Page: Contacts
  └── Tabs:
      ├── All Contacts (Table block)
      ├── By Company (Table block, grouped)
      └── New Contact (Form block)
```

### Menu Structure
```
Menu:
  ├── Dashboard (Chart blocks)
  ├── CRM
  │   ├── Contacts (Table + Kanban tabs)
  │   ├── Companies (Table)
  │   └── Deals (Kanban + Table tabs)
  ├── Operations
  │   ├── Orders (Table)
  │   └── Products (Grid Card)
  └── Settings
      ├── Users (Table)
      └── Roles (Table)
```

## Field Components

| Field Type | Available Components |
|------------|---------------------|
| string | Input, TextArea, Tag |
| select | Select, Radio, Tag |
| boolean | Switch, Checkbox |
| date | DatePicker, RangePicker |
| number | InputNumber, Slider, Progress |
| relation | RecordPicker, SubForm, SubTable |
| attachment | Upload, ImageUpload |
| richText | RichText editor |
| json | JSON editor, Code editor |

## Tools for UI Configuration

| Tool | Purpose |
|------|---------|
| `page_create` | Create a new page |
| `page_list` | List all pages |
| `page_inspect` | Inspect page structure (blocks, columns, actions) |
| `page_delete` | Delete a page |
| `table_add` | Add a block (table, form, etc.) to a page |
| `column_add` | Add a column/field to a block |
| `action_add` | Add an action button to a block |
| `menu_create_group` | Create a menu group |
| `collection_get` | Get collection fields (to know what columns to add) |

## Executable Workflows

### Workflow: Create a Page with Table Block

```
Step 1: collection_get("contacts")
  → Understand available fields: name, email, phone, company, status, createdAt

Step 2: page_create("Contacts")
  → Page created with ID

Step 3: table_add(page, { collection: "contacts", type: "table" })
  → Table block added

Step 4: column_add(block, "name")
         column_add(block, "email")
         column_add(block, "phone")
         column_add(block, "status")
         column_add(block, "createdAt")
  → Columns added to table

Step 5: action_add(block, "create")
         action_add(block, "edit")
         action_add(block, "delete")
         action_add(block, "filter")
  → Actions added
```

### Workflow: Create a Page with Form Block

```
Step 1: collection_get("orders")
  → Fields: customer, product, quantity, total, status, notes

Step 2: page_create("New Order")
  → Page created

Step 3: table_add(page, { collection: "orders", type: "form" })
  → Form block added

Step 4: column_add(block, "customer")    // relation picker
         column_add(block, "product")     // relation picker
         column_add(block, "quantity")    // number input
         column_add(block, "notes")      // text area
  → Form fields added

Step 5: action_add(block, "submit")
         action_add(block, "cancel")
  → Form actions added
```

### Workflow: Create a Kanban Board Page

```
Step 1: collection_get("deals")
  → Fields: title, amount, stage, contact, closeDate

Step 2: page_create("Deal Pipeline")
  → Page created

Step 3: table_add(page, { collection: "deals", type: "kanban", groupField: "stage" })
  → Kanban block added, grouped by stage field

Step 4: column_add(block, "title")
         column_add(block, "amount")
         column_add(block, "contact")
         column_add(block, "closeDate")
  → Card fields configured
```

### Workflow: Inspect and Extend Existing Page

```
Step 1: page_list()
  → Find target page

Step 2: page_inspect(pageId)
  → See current blocks, columns, actions

Step 3: column_add(block, "newField")
  → Add missing columns

Step 4: action_add(block, "export")
  → Add missing actions

Step 5: page_inspect(pageId)
  → Verify changes
```

### Workflow: Build Complete Application UI

```
Step 1: collection_list()
  → Understand all available collections

Step 2: menu_create_group("CRM")
         menu_create_group("Operations")
  → Create navigation groups

Step 3: For each collection, create a page with appropriate block type:
  page_create("Contacts", { parent: "CRM" })  → table_add → column_add → action_add
  page_create("Deals", { parent: "CRM" })     → table_add (kanban) → column_add
  page_create("Orders", { parent: "Operations" }) → table_add → column_add → action_add

Step 4: page_create("Dashboard")
  → Add chart blocks for overview

Step 5: page_list() → Verify complete navigation
```

## Best Practices

1. **Design for the user** — different blocks for different roles
2. **Inspect before building** — always run `collection_get` to know available fields before adding columns
3. **Use tabs** — group related views in tabs on the same page
4. **Configure filters** — add commonly-used filters to table blocks
5. **Hide system fields** — don't show createdAt/updatedBy in forms
6. **Use modal for quick edits** — drawer for detailed forms, page for complex ones
7. **Default sort matters** — newest first (-createdAt) is usually best
8. **Show related data** — use sub-tables for hasMany relations
9. **Use Kanban for pipelines** — status-based workflows are perfect for boards
10. **Dashboard first** — create a dashboard page with chart blocks for overview
11. **Verify with page_inspect** — always inspect the page after modifications to confirm structure
