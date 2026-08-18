---
name: search-filter
description: |
  NocoDB filter syntax reference for searching, filtering, and sorting records. Use when:
  - "filter records"
  - "search for records where"
  - "NocoDB where clause"
  - "how to filter by date"
  - "sort results"
  - "query syntax"
  - "find records matching"
  - "filter by status"
  - "records created this week"
  - "combine multiple filters"
---

# Search and Filter Reference

## Basic Filter Syntax

Every filter follows this pattern:

```
(FieldName,operator,value)
```

- Wrap each condition in parentheses.
- Separate field name, operator, and value with commas.
- Field names are case-sensitive -- use the exact name from the table schema.

Example: find all records where Status equals "Active":

```
(Status,eq,Active)
```

## Text and General Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `eq` | Equals | `(Status,eq,Active)` |
| `neq` | Does not equal | `(Status,neq,Closed)` |
| `like` | Contains text | `(Name,like,John)` |
| `nlike` | Does not contain text | `(Name,nlike,Test)` |
| `in` | Matches any value in a list | `(Status,in,Active,Pending)` |

Notes:
- `like` matches anywhere in the text. `(Name,like,oh)` matches "John" and "Mohit."
- `in` takes a comma-separated list of values after the operator.

## Numeric Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `gt` | Greater than | `(Amount,gt,100)` |
| `lt` | Less than | `(Amount,lt,50)` |
| `gte` | Greater than or equal | `(Amount,gte,100)` |
| `lte` | Less than or equal | `(Amount,lte,500)` |
| `btw` | Between two values | `(Amount,btw,100,500)` |
| `nbtw` | Not between two values | `(Amount,nbtw,100,500)` |

**Important:** The `btw` operator may not work correctly with Currency fields. For Currency fields, combine `gte` and `lte` instead:

```
(Price,gte,10)~and(Price,lte,100)
```

## Null and Empty Operators

| Operator | Meaning | What It Catches |
|----------|---------|-----------------|
| `blank` | Field has no value at all | Null or empty string |
| `notblank` | Field has some value | Any non-null, non-empty value |
| `null` | Field is null | Only null (not empty string) |
| `notnull` | Field is not null | Includes empty strings |
| `empty` | Field is empty string | Only empty string (not null) |
| `notempty` | Field is not empty string | Includes null values |

These operators take no value -- just the field and operator:

```
(Email,notblank)
(Notes,blank)
(Phone,notnull)
```

Use `blank` / `notblank` when you want "has any value" or "has no value" without worrying about null vs. empty distinctions.

## Boolean (Checkbox) Operators

| Operator | Meaning |
|----------|---------|
| `checked` | Checkbox is checked (true) |
| `notchecked` | Checkbox is not checked (false) |

No value needed:

```
(IsActive,checked)
(Archived,notchecked)
```

## Multi-Select Operators

For fields that allow multiple selections:

| Operator | Meaning | Example |
|----------|---------|---------|
| `allof` | Has all of these values | `(Tags,allof,Urgent,High)` |
| `anyof` | Has any of these values | `(Tags,anyof,Urgent,High)` |
| `nallof` | Does not have all of these | `(Tags,nallof,Urgent,High)` |
| `nanyof` | Does not have any of these | `(Tags,nanyof,Spam,Test)` |

## Date and Time Filtering

Date filters use a different structure with sub-operators.

### Relative Date Ranges (isWithin)

Find records within a relative time window:

```
(CreatedAt,isWithin,pastWeek)
(CreatedAt,isWithin,pastMonth)
(CreatedAt,isWithin,pastYear)
(CreatedAt,isWithin,pastNumberOfDays,30)
(CreatedAt,isWithin,nextWeek)
(CreatedAt,isWithin,nextMonth)
(CreatedAt,isWithin,nextYear)
(CreatedAt,isWithin,nextNumberOfDays,14)
```

### Relative Date Comparisons

Compare a date field to a relative reference point:

```
(DueDate,eq,today)
(DueDate,eq,yesterday)
(DueDate,eq,tomorrow)
(DueDate,gt,daysAgo,7)
(DueDate,lt,daysFromNow,30)
(DueDate,gte,daysAgo,14)
```

### Exact Date Comparisons

Compare to a specific calendar date:

```
(DueDate,eq,exactDate,2024-12-31)
(DueDate,lt,exactDate,2025-01-01)
(DueDate,gte,exactDate,2024-06-01)
(DueDate,btw,exactDate,2024-01-01,exactDate,2024-12-31)
```

### Common Date Filter Patterns

| Need | Filter |
|------|--------|
| Created today | `(CreatedAt,eq,today)` |
| Due this week | `(DueDate,isWithin,pastWeek)` |
| Overdue items | `(DueDate,lt,today)` |
| Created in last 30 days | `(CreatedAt,isWithin,pastNumberOfDays,30)` |
| Due before end of year | `(DueDate,lt,exactDate,2025-12-31)` |
| Updated in the past 7 days | `(UpdatedAt,gt,daysAgo,7)` |

## Logical Operators (Combining Filters)

Combine multiple conditions with logical operators. **Always use the tilde prefix (`~`).**

| Operator | Meaning | Syntax |
|----------|---------|--------|
| `~and` | Both conditions must match | `(A,eq,1)~and(B,eq,2)` |
| `~or` | Either condition can match | `(A,eq,1)~or(B,eq,2)` |
| `~not` | Negate a condition | `~not(A,eq,1)` |

### Combining Multiple Conditions

Two conditions with AND:

```
(Status,eq,Active)~and(Priority,eq,High)
```

Three conditions:

```
(Status,eq,Active)~and(Priority,eq,High)~and(DueDate,lt,today)
```

Mixing AND and OR:

```
(Status,eq,Active)~and((Priority,eq,High)~or(Priority,eq,Urgent))
```

Using NOT:

```
(Status,eq,Active)~and~not(Category,eq,Internal)
```

## Special Values and Edge Cases

### Filtering for Null or Empty

```
(Notes,blank)           -- no value at all
(Notes,notblank)        -- has some value
```

### Field Names with Spaces

Use the field name as-is. Spaces are allowed inside the parentheses:

```
(First Name,eq,John)
(Order Total,gt,100)
```

### Values with Commas

If the value itself contains a comma, the filter may misinterpret it. Avoid values with commas in `eq` filters. Use `like` for partial matching instead:

```
(Address,like,New York)
```

### Numeric Strings

Numeric operators only work on numeric fields. For text fields that contain numbers, use `eq` or `like`:

```
(ZipCode,eq,10001)      -- text field, use eq
(Amount,gt,100)          -- numeric field, use gt
```

## Sorting

The `sort` parameter in `queryRecords` accepts an array of sort rules. Each rule has a `field` and `direction`.

```
sort: [{ "field": "CreatedAt", "direction": "desc" }]
```

Multiple sort levels (sort by Status first, then by Date within each status):

```
sort: [
  { "field": "Status", "direction": "asc" },
  { "field": "DueDate", "direction": "asc" }
]
```

Sort directions:
- `asc` -- smallest/earliest/A first
- `desc` -- largest/latest/Z first

## Practical Examples

### 1. Active high-priority tasks due this week

```
where: "(Status,eq,Active)~and(Priority,eq,High)~and(DueDate,isWithin,pastWeek)"
sort: [{ "field": "DueDate", "direction": "asc" }]
```

### 2. Orders over $500 from the past 30 days

```
where: "(Total,gt,500)~and(OrderDate,isWithin,pastNumberOfDays,30)"
sort: [{ "field": "Total", "direction": "desc" }]
```

### 3. Contacts without an email address

```
where: "(Email,blank)"
fields: ["Name", "Phone", "Company"]
```

### 4. Products in Electronics or Clothing categories

```
where: "(Category,in,Electronics,Clothing)"
sort: [{ "field": "Name", "direction": "asc" }]
```

### 5. Unresolved support tickets created more than 7 days ago

```
where: "(Resolution,blank)~and(CreatedAt,lt,daysAgo,7)"
sort: [{ "field": "CreatedAt", "direction": "asc" }]
```

### 6. Records updated today

```
where: "(UpdatedAt,eq,today)"
sort: [{ "field": "UpdatedAt", "direction": "desc" }]
```

### 7. Inventory items with low stock

```
where: "(Quantity,lte,10)~and(Quantity,gt,0)"
sort: [{ "field": "Quantity", "direction": "asc" }]
```

### 8. Invoices between $1,000 and $5,000

```
where: "(Amount,gte,1000)~and(Amount,lte,5000)"
sort: [{ "field": "Amount", "direction": "desc" }]
```

### 9. Tasks assigned to a specific person that are not completed

```
where: "(AssignedTo,eq,Jane Smith)~and(Status,neq,Completed)"
sort: [{ "field": "Priority", "direction": "desc" }, { "field": "DueDate", "direction": "asc" }]
```

### 10. Records with any tag containing "Urgent"

```
where: "(Tags,anyof,Urgent)"
```

### 11. Exclude archived and test records

```
where: "(Archived,notchecked)~and(Name,nlike,Test)"
```

### 12. Date range -- all of Q1 2025

```
where: "(Date,gte,exactDate,2025-01-01)~and(Date,lte,exactDate,2025-03-31)"
```

## Quick Reference

When building a filter:

1. Get the exact field names from `mcp__nocodb__getTableSchema`.
2. Pick the right operator for the field type (text, number, date, checkbox, multi-select).
3. Combine conditions with `~and` or `~or` (always with tilde).
4. Test with a small `pageSize` first to verify results before running large queries.
5. Add `sort` to control the order of results.
6. Use `fields` to return only the columns you need.
