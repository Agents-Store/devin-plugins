## Feature: {{FEATURE_NAME}}

### Description
{{Brief description of what this feature does}}

### Step 1: Data Model (PostgreSQL + NocoDB)

**Tables to create:**

| Table | Fields | Relations |
|-------|--------|-----------|
| `{{table_name}}` | `id`, `created_at`, `updated_at`, {{fields}} | {{FK relations}} |

**NocoDB views:**
- [ ] Grid view: `{{view_name}}`
- [ ] Form view: `{{form_name}}` (if data entry needed)
- [ ] Kanban view: `{{kanban_name}}` (if status-based workflow)

### Step 2: Interface (NocoBase)

- [ ] Create/sync collection `{{collection_name}}`
- [ ] Build form block for data entry
- [ ] Build table block for data display
- [ ] Add action buttons: {{button_actions}}
- [ ] Configure field permissions

### Step 3: Business Logic

**n8n workflows:**
- [ ] `{{Domain}} - {{Action}} - {{Trigger}}`: {{description}}

**Trigger.dev tasks:**
- [ ] `{{task-id}}`: {{description}}

### Step 4: Connect Layers

- [ ] NocoDB webhook → n8n: `{{webhook_event}}` triggers `{{workflow_name}}`
- [ ] n8n → NocoDB: workflow reads/writes `{{table_name}}`
- [ ] NocoBase button → n8n: `{{button_action}}` triggers `{{workflow_name}}`
- [ ] Trigger.dev → NocoDB: task updates `{{status_field}}`

### Step 5: Verify

- [ ] Create test record via NocoBase UI
- [ ] Verify automation triggers correctly
- [ ] Check NocoDB data is updated
- [ ] Verify status field progression: `{{status_flow}}`
- [ ] Test error handling: disconnect a service and verify graceful failure

### Resource IDs

| Resource | ID | Service |
|----------|----|---------|
| Table | `tbl_xxx` | NocoDB |
| Table (PostgreSQL) | `{{table_name}}` | PostgreSQL MCP |
| Workflow | `wf_xxx` | n8n |
| Task | `{{task-id}}` | Trigger.dev |
| Webhook | `{{webhook_url}}` | n8n |
| PostgREST endpoint | `${POSTGRESQL_API_URL}/{{table_name}}` | PostgREST |
