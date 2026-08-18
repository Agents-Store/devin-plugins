---
name: full-feature
description: This skill should be used when the user wants to "build a complete feature", "create end-to-end functionality", "implement a full feature across all layers", "build feature with data model and automation", or needs a step-by-step recipe for building features that span the Data, Logic, and Interface layers of the Composable Stack.
---

# Full Feature Recipe

Step-by-step process for building features that span all layers of the Composable Stack: Data (PostgreSQL/NocoDB), Logic (n8n/Trigger.dev), and Interface (NocoBase/NocoDB).

## Feature Development Process

Follow these steps in order for every new feature.

### Step 1: Design Data Model (Data Layer)

1. Define tables in PostgreSQL using `snake_case` naming
2. Include standard fields: `id`, `created_at`, `updated_at`
3. Define relations (foreign keys, junction tables)
4. Create the tables using the `postgresql-external-dev` plugin skills
5. Alternatively, create tables directly using PostgreSQL MCP:

```
Tool: mcp__postgresql-mcp__execute_sql
Input: { "sql": "CREATE TABLE orders (id SERIAL PRIMARY KEY, title TEXT NOT NULL, status TEXT DEFAULT 'pending', created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now())" }
```

6. Verify schema with PostgreSQL MCP:

```
Tool: mcp__postgresql-mcp__list_tables
Input: { "table_names": "orders" }
```

Verify the tables also appear in NocoDB:

```
Tool: mcp__nocodb__getTablesList
```

### Step 2: Set Up NocoDB Views (Data Layer)

1. Create appropriate NocoDB views (Grid, Form, Gallery, Kanban)
2. Configure field visibility and ordering
3. Set up filters for common queries
4. Create shared views if external access is needed

### Step 3: Build NocoBase Interface (Interface Layer)

**Always build on the NocoBase dev instance first** (`${NOCOBASE_DEV_URL}` / `${NOCOBASE_DEV_API_KEY}`, also exposed through the `nocobase-dev` MCP server). The dev instance is a sandbox for new tables, fields, menus, pages, blocks, and UX — safe to break, fast to iterate.

1. Create or sync NocoBase collections from the PostgreSQL tables on the **dev** instance
2. Design form blocks for data entry
3. Design table blocks for data display
4. Add action buttons for triggering workflows
5. Configure field permissions and validation rules
6. Once validated, promote the schema and UI to the **prod** instance (`${NOCOBASE_URL}`) via export/import or migration

### Step 4: Create Automation Logic (Logic Layer)

Choose the appropriate service:

**For n8n workflows (visual, short-running):**
1. Create webhook trigger or schedule trigger
2. Build data transformation nodes
3. Add NocoDB read/write operations
4. Configure error handling
5. Name: `[Domain] - [Action] - [Trigger]`

**For Trigger.dev tasks (durable, long-running):**
1. Create task file in `src/trigger/`
2. Define payload type and retry config
3. Implement business logic
4. Add NocoDB status updates
5. Deploy with `npx trigger.dev deploy`

### Step 5: Connect the Layers

Wire up the integration points:

1. **Data → Logic**: NocoDB webhook → n8n/Trigger.dev
2. **Interface → Logic**: NocoBase button/workflow → n8n webhook
3. **Logic → Data**: n8n/Trigger.dev → NocoDB MCP (read/write records)
4. **Logic → Data (direct)**: n8n HTTP Request → PostgREST API (REST CRUD)
5. **Logic → Data (SQL)**: Trigger.dev/n8n → PostgreSQL MCP `execute_sql` (complex queries)
6. **Logic → Interface**: n8n → NocoBase API (update UI state)

### Step 6: Verify End-to-End

1. Create a test record through NocoBase UI or NocoDB
2. Verify the automation triggers
3. Check the result in NocoDB
4. Verify status updates in the interface

## Feature Template

Use `full-feature/template.md` as a structured checklist for each new feature. Copy and fill in the placeholders.

## Example: Order Processing Feature

| Step | Action | Service |
|------|--------|---------|
| 1 | Create `orders` table with fields | PostgreSQL |
| 2 | Set up Grid + Kanban views | NocoDB |
| 3 | Build order form and dashboard | NocoBase |
| 4 | Create payment processing workflow | n8n |
| 5 | Create PDF generation background task | Trigger.dev |
| 6 | Wire: new order → process payment → generate PDF → update status | All |

## Best Practices

- Start with the data model — it's the foundation for everything
- Use NocoDB views for operational data access, NocoBase for admin UI
- Keep n8n workflows focused — one workflow per business process
- Use Trigger.dev for anything that needs retries or takes >30 seconds
- Document webhook URLs and task IDs in the project config
- Test each layer independently before wiring them together
- Include a `status` field on records that participate in workflows
