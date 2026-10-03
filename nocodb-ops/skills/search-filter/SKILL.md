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

NocoDB MCP tools take a filter in one of two forms. **Pass only one of the two** in a call:

| Form | Parameter | Use it for |
|------|-----------|------------|
| **Structured** (preferred) | `filter` | Everything -- names and values are quoted for you, so commas, parentheses and quotes in values are safe |
| **String** (fallback) | `where` | Short one-liners, and the REST `where=` query parameter |

Both forms work on `queryRecords`, `countRecords`, `groupByRecords`, `updateRecordsByCondition` and on each `aggregate.filterGroups[]` entry (`{ "alias": "...", "filter": ... }` or `{ "alias": "...", "where": "..." }`).

## Structured `filter`

A single condition:

```
filter: { "field": "Status", "operator": "eq", "value": "Active" }
```

A group -- `group_operator` is `AND` or `OR`, members may be conditions or nested groups:

```
filter: { "group_operator": "AND", "filters": [
  { "field": "Status", "operator": "eq", "value": "Active" },
  { "group_operator": "OR", "filters": [
    { "field": "Priority", "operator": "eq", "value": "High" },
    { "field": "Priority", "operator": "eq", "value": "Urgent" } ] } ] }
```

- `value` is a scalar for most operators, an **array** for `in`, `allof`, `anyof`, `nallof`, `nanyof`, and omitted for `blank`, `notblank`, `null`, `notnull`, `empty`, `notempty`, `checked`, `notchecked`.
- Date and DateTime fields add a `sub_operator` (see "Date and Time Filtering" below).
- Field titles are case-insensitive in `filter`.

## Basic `where` Syntax

Every `where` condition follows this pattern:

```
(FieldName,operator,value)
```

- Wrap each condition in parentheses.
- Separate field name, operator, and value with commas.
- Field names are case-sensitive in `where` -- use the exact name from the table schema (a wrong case fails with `Column alias '<name>' not found`).

Example: find all records where Status equals "Active":

```
(Status,eq,Active)
```

The rest of this page shows the `where` strings; every one has a `filter` equivalent.

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

### Ranges: always two bounds

`btw` / `nbtw` are **rejected** on Number, Decimal, Currency, Percent, Rating, Duration, Date / DateTime and Checkbox fields (`Operation btw is not supported for type <T>`); only Time and text fields accept them. Two bounds work on every type, so write every range that way:

| Need | Filter |
|------|--------|
| Between 10 and 100 (inclusive) | `(Price,gte,10)~and(Price,lte,100)` |
| Not between 0 and 50 | `(Score,lt,0)~or(Score,gt,50)` |

As a structured filter:

```
filter: { "group_operator": "AND", "filters": [
  { "field": "Price", "operator": "gte", "value": 10 },
  { "field": "Price", "operator": "lte", "value": 100 } ] }
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

Date and DateTime fields (and CreatedTime / LastModifiedTime) need a **sub-operator** on every comparison. The `where` form is `(field,operator,sub_operator)` or `(field,operator,sub_operator,value)`; the structured form adds a `sub_operator` key next to `operator`:

```
filter: { "field": "DueDate", "operator": "lt", "sub_operator": "today" }
filter: { "field": "DueDate", "operator": "gte", "sub_operator": "exactDate", "value": "2026-06-01" }
```

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

Compare to a specific calendar date. The date goes in the **value slot after `exactDate`** -- never directly after the operator:

```
(DueDate,eq,exactDate,2024-12-31)      CORRECT
(DueDate,lt,exactDate,2025-01-01)      CORRECT
(DueDate,gte,exactDate,2024-06-01)     CORRECT
(DueDate,eq,YYYY-MM-DD)                WRONG -- a bare date is read as the sub-operator
                                       and rejected: '<date>' is not supported
```

A date **range** is two bounds -- `btw` / `nbtw` are not supported on date fields:

```
(DueDate,gte,exactDate,2024-01-01)~and(DueDate,lte,exactDate,2024-12-31)
```

Match any of several exact dates with `in`:

```
(DueDate,in,exactDate,2024-06-15,2024-07-01)
```

Date fields without a value (`blank`, `notblank`) take no sub-operator: `(DueDate,blank)`.

### Common Date Filter Patterns

| Need | Filter |
|------|--------|
| Created today | `(CreatedAt,eq,today)` |
| Due in the next 7 days | `(DueDate,isWithin,nextWeek)` |
| Overdue items | `(DueDate,lt,today)` |
| Created in last 30 days | `(CreatedAt,isWithin,pastNumberOfDays,30)` |
| Due before the end of 2025 | `(DueDate,lte,exactDate,2025-12-31)` |
| Due in 2025 | `(DueDate,gte,exactDate,2025-01-01)~and(DueDate,lte,exactDate,2025-12-31)` |
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
(Status,eq,Active)~and(~not(Category,eq,Internal))
```

`~not` only starts an expression or a group -- wrap it in parentheses when it follows `~and` / `~or`. Never put whitespace after `~and`, `~or` or `~not` (`(A,eq,1)~and (B,eq,2)` is a parse error), and write the operators in lowercase.

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

### Values with Commas, Quotes, Parentheses

In a `where` string, wrap such a value in quotes:

```
(Address,eq,"12 Main St, Springfield")
(Note,eq,"it's here")
```

The structured `filter` needs no quoting at all -- `{ "field": "Address", "operator": "eq", "value": "12 Main St, Springfield" }` is safe as is. Do not leave a trailing space inside a field name (`(Name ,eq,John)` reports `field 'Name ' not found`); a trailing space inside a value is kept and silently matches nothing.

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

### 1. Active high-priority tasks due in the next 7 days

```
where: "(Status,eq,Active)~and(Priority,eq,High)~and(DueDate,isWithin,nextWeek)"
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

1. Get the exact field names from `mcp__plugin_nocodb-ops_nocodb__getTableSchema`.
2. Pick the right operator for the field type (text, number, date, checkbox, multi-select) -- ranges are two bounds, dates carry a sub-operator.
3. Prefer the structured `filter`; with `where`, combine conditions with `~and` or `~or` (always with tilde).
4. Test with a small `pageSize` first to verify results before running large queries.
5. Add `sort` to control the order of results.
6. Use `fields` to return only the columns you need.
