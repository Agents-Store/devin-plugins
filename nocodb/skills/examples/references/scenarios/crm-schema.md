# Scenario: CRM Schema Design

Build a complete CRM schema in NocoDB with Contacts, Companies, Deals, and Activities.

## Entity Relationship

```
Companies ──< Contacts ──< Activities
    │              │
    └──< Deals >──┘
         │
    Deals >──< Products (M2M)
```

## Tables

### Companies
| Field | Type | Notes |
|-------|------|-------|
| Name | SingleLineText | Primary display |
| Industry | SingleSelect | Tech, Finance, Healthcare, Retail, Other |
| Website | URL | |
| Size | SingleSelect | 1-10, 11-50, 51-200, 201-1000, 1000+ |
| Revenue | Currency | Annual revenue |
| Notes | LongText | |

### Contacts
| Field | Type | Notes |
|-------|------|-------|
| Name | SingleLineText | Primary display |
| Email | Email | |
| Phone | PhoneNumber | |
| Title | SingleLineText | Job title |
| Company | Link (hm) | → Companies |
| Status | SingleSelect | Lead, Active, Inactive |
| Source | SingleSelect | Website, Referral, LinkedIn, Cold Call |

### Deals
| Field | Type | Notes |
|-------|------|-------|
| Title | SingleLineText | Primary display |
| Amount | Currency | Deal value |
| Stage | SingleSelect | Discovery, Proposal, Negotiation, Closed Won, Closed Lost |
| Contact | Link (hm) | → Contacts |
| Company | Link (hm) | → Companies |
| CloseDate | Date | Expected close |
| Probability | Percent | Win likelihood |

### Products
| Field | Type | Notes |
|-------|------|-------|
| Name | SingleLineText | Primary display |
| Price | Currency | Unit price |
| Category | SingleSelect | Software, Hardware, Service, Support |
| Active | Checkbox | Currently offered |

### Activities
| Field | Type | Notes |
|-------|------|-------|
| Subject | SingleLineText | Primary display |
| Type | SingleSelect | Call, Email, Meeting, Note |
| Date | DateTime | When it happened |
| Contact | Link (hm) | → Contacts |
| Deal | Link (hm) | → Deals |
| Notes | LongText | Activity details |

## Build Order

```
1. create_table("Companies", columns)
2. create_table("Contacts", columns)
3. create_table("Products", columns)
4. create_table("Deals", columns)
5. create_table("Activities", columns)
6. create_column(Contacts, Link → Companies, hm)
7. create_column(Deals, Link → Contacts, hm)
8. create_column(Deals, Link → Companies, hm)
9. create_column(Deals, Link → Products, mm)  ← Many-to-Many
10. create_column(Activities, Link → Contacts, hm)
11. create_column(Activities, Link → Deals, hm)
```

## Lookups and Rollups

```
// In Companies: total deal value
create_column(Companies, Rollup "Total Deal Value", deals_link, amount, sum)

// In Companies: deal count
create_column(Companies, Rollup "Deal Count", deals_link, id, count)

// In Companies: contact count
create_column(Companies, Rollup "Contact Count", contacts_link, id, count)

// In Contacts: company name lookup
create_column(Contacts, Lookup "Company Name", company_link, name)

// In Deals: contact email lookup
create_column(Deals, Lookup "Contact Email", contact_link, email)
```

## Formulas

```
// In Deals: weighted value
create_column(Deals, Formula "Weighted Value", "({Amount} * {Probability}) / 100")

// In Deals: deal age
create_column(Deals, Formula "Days Open", "DATETIME_DIFF(NOW(), {Created}, 'days')")

// In Companies: segment
create_column(Companies, Formula "Segment", "IF({Revenue} > 1000000, 'Enterprise', IF({Revenue} > 100000, 'Mid-Market', 'SMB'))")
```

## Views

```
// Deals: Pipeline Kanban
create_view(Deals, "Pipeline", Kanban, group_by="Stage")

// Contacts: All contacts grid
create_view(Contacts, "All Contacts", Grid, sort=Name ASC)

// Contacts: Lead capture form
create_view(Contacts, "New Lead", Form)

// Activities: Calendar
create_view(Activities, "Activity Calendar", Calendar, date_field="Date")

// Companies: Gallery with logos
create_view(Companies, "Company Directory", Gallery)

// Deals: Active deals only
create_view(Deals, "Active Deals", Grid, filter: Stage not in [Closed Won, Closed Lost])
```

## Result

A complete CRM with:
- 5 interconnected tables
- HasMany and ManyToMany relations
- Lookups for cross-table data access
- Rollups for aggregated metrics
- Formulas for calculated fields
- Kanban pipeline, calendar, form, and filtered views
