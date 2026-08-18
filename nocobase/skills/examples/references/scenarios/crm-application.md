# Scenario: CRM Application

Complete CRM application design for NocoBase — collections, relations, workflows, and UI.

## Entity Model

```
companies ──< contacts ──< activities
    │              │
    └──< deals >──┘
         │
    deals >──< products (via deal_products)
```

## Collections

### companies
| Field | Type | Config |
|-------|------|--------|
| name | string | required, primary display |
| industry | singleSelect | Tech, Finance, Healthcare, Retail, Other |
| website | url | |
| size | singleSelect | 1-10, 11-50, 51-200, 201-1000, 1000+ |
| revenue | decimal | precision: 2 |
| contacts | hasMany | → contacts |
| deals | hasMany | → deals |

### contacts
| Field | Type | Config |
|-------|------|--------|
| name | string | required, primary display |
| email | email | unique |
| phone | phone | |
| title | string | Job title |
| company | belongsTo | → companies |
| status | singleSelect | Lead, Qualified, Active, Inactive |
| source | singleSelect | Website, Referral, LinkedIn, Cold Call |
| deals | hasMany | → deals |
| activities | hasMany | → activities |

### deals
| Field | Type | Config |
|-------|------|--------|
| title | string | required, primary display |
| amount | decimal | precision: 2 |
| stage | singleSelect | Discovery, Proposal, Negotiation, Closed Won, Closed Lost |
| contact | belongsTo | → contacts |
| company | belongsTo | → companies |
| closeDate | date | Expected close |
| probability | integer | 0-100 |
| products | belongsToMany | → products (via deal_products) |
| weightedValue | formula | `{{amount}} * {{probability}} / 100` |

### products
| Field | Type | Config |
|-------|------|--------|
| name | string | required, primary display |
| sku | string | unique |
| price | decimal | precision: 2 |
| category | singleSelect | Software, Hardware, Service, Support |
| active | boolean | default: true |

### deal_products (through table)
| Field | Type | Config |
|-------|------|--------|
| deal | belongsTo | → deals |
| product | belongsTo | → products |
| quantity | integer | default: 1 |
| unitPrice | decimal | |
| lineTotal | formula | `{{quantity}} * {{unitPrice}}` |

### activities
| Field | Type | Config |
|-------|------|--------|
| subject | string | required, primary display |
| type | singleSelect | Call, Email, Meeting, Note |
| date | datetime | |
| contact | belongsTo | → contacts |
| deal | belongsTo | → deals |
| notes | richText | |

## Workflows

### New Deal Notification
```
Trigger: deals.afterCreate
1. Query: Get deal creator details
2. Condition: amount > 10000?
   Yes → Request: Send Slack alert to #big-deals
   No → (skip)
3. Request: Send email to assigned contact
```

### Deal Won → Revenue Log
```
Trigger: deals.afterUpdate
Condition: stage changed to "Closed Won"
1. Create: Add entry to revenue_log
2. Update: Set all related activities as "Completed"
3. Request: Notify team via webhook
```

### Weekly Pipeline Report
```
Trigger: Schedule (Monday 9:00 AM)
1. Query: All deals with stage NOT IN (Closed Won, Closed Lost)
2. Calculation: Sum amounts by stage
3. Request: Send report to Slack/email
```

## UI Design

### Menu Structure
```
CRM
  ├── Dashboard (Charts)
  ├── Contacts (Table + Form)
  ├── Companies (Table)
  ├── Deals (Kanban + Table)
  ├── Activities (Calendar + Table)
  └── Products (Table)
```

### Dashboard Page
```
Blocks:
  - Chart: Revenue by Month (bar chart, deals.amount grouped by closeDate)
  - Chart: Deals by Stage (pie chart, count by stage)
  - Chart: New Contacts This Month (counter)
  - Table: Recent Deals (top 10 by createdAt DESC)
```

### Deals Page
```
Tab 1: Pipeline (Kanban block)
  - Group by: stage
  - Card: title, amount, contact.name, closeDate
  - Drag-drop to change stage

Tab 2: All Deals (Table block)
  - Columns: title, amount, stage, contact, company, closeDate
  - Filters: stage, date range, amount range
  - Sort: -createdAt
  - Actions: Create, Edit, Delete, Export
```

### Contacts Page
```
Table block:
  - Columns: name, email, phone, company.name, status
  - Quick filter: status
  - Actions: Create (modal form), Edit, View (drawer), Delete
  - Sub-table: activities (in drawer/details view)
```
