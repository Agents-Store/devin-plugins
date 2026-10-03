# Where Filter Syntax

Complete `where` clause syntax for REST and MCP record queries, aligned with the live NocoDB MCP server (2026.09). The official `nocodb.sh` script prints its own copy with `where:help`.

The MCP record tools also take a **structured `filter`** (preferred over `where`; pass only one of the two): a single condition `{ "field", "operator", "value", "sub_operator"? }` or a group `{ "group_operator": "AND" | "OR", "filters": [...] }`. Names and values are quoted for you. Everything below -- operators, date sub-operators, the two-bound range rule -- applies to both forms. REST has only the `where` query parameter.

## Basic Syntax

```
(field,operator,value)            Basic filter
(field,operator)                  No-value operators (blank, null, checked, etc.)
(field,op,sub_op)                 Date with sub-operator
(field,op,sub_op,value)           Date with sub-operator and value
(field,operator,val1,val2,val3)   Multiple values
```

## Operators

### Text / General

| Operator | Description | Example |
|----------|-------------|---------|
| eq | Equal | `(name,eq,John)` |
| neq | Not equal | `(status,neq,archived)` |
| like | Contains (% wildcard) | `(name,like,%john%)` |
| nlike | Does not contain | `(name,nlike,%test%)` |
| in | In list | `(status,in,active,pending,review)` |

### Numeric

| Operator | Description | Example |
|----------|-------------|---------|
| gt | Greater than (>) | `(price,gt,100)` |
| lt | Less than (<) | `(stock,lt,10)` |
| gte | Greater than or equal (>=) | `(rating,gte,4)` |
| lte | Less than or equal (<=) | `(age,lte,65)` |

### Range

`btw` / `nbtw` are **rejected** on Number, Decimal, Currency, Percent, Rating, Duration, Date / DateTime and Checkbox fields with `Operation btw is not supported for type <T>`; only Time and text fields accept them. Two bounds work on every type, so always express a range that way:

| Need | Filter |
|------|--------|
| Between (inclusive) | `(price,gte,10)~and(price,lte,100)` |
| Not between | `(score,lt,0)~or(score,gt,50)` |

### Null / Empty (no value needed)

| Operator | Description | Example |
|----------|-------------|---------|
| blank | Is blank (null or empty) | `(notes,blank)` |
| notblank | Is not blank | `(email,notblank)` |
| null | Is null | `(deleted_at,null)` |
| notnull | Is not null | `(created_by,notnull)` |
| empty | Is empty string | `(description,empty)` |
| notempty | Is not empty string | `(title,notempty)` |

### Boolean / Checkbox (no value needed)

| Operator | Description | Example |
|----------|-------------|---------|
| checked | Is checked/true | `(is_active,checked)` |
| notchecked | Is not checked/false | `(is_archived,notchecked)` |

### Multi-Select / Tags

| Operator | Description | Example |
|----------|-------------|---------|
| allof | Contains all of | `(tags,allof,urgent,important)` |
| anyof | Contains any of | `(tags,anyof,bug,feature)` |
| nallof | Does not contain all of | `(tags,nallof,spam,junk)` |
| nanyof | Does not contain any of | `(categories,nanyof,draft,deleted)` |

## Date / Time Filtering

Date fields require a sub-operator on **every** comparison. In the structured `filter` it is the `sub_operator` key; in `where` it follows the operator. A bare date after the operator is read as the sub-operator and rejected (`'<date>' is not supported`).

### isWithin — date falls within a time range

Sub-operators (no value): pastWeek, pastMonth, pastYear, nextWeek, nextMonth, nextYear
Sub-operators (value = days): pastNumberOfDays, nextNumberOfDays

```bash
(created_at,isWithin,pastWeek)                        # Last 7 days
(created_at,isWithin,pastMonth)                       # Last 30 days
(due_date,isWithin,pastNumberOfDays,14)               # Last 14 days
(due_date,isWithin,nextNumberOfDays,30)               # Next 30 days
```

### eq, neq, gt, lt, gte, lte — date comparisons

gt = after, lt = before, gte = on or after, lte = on or before

Sub-operators (no value): today, tomorrow, yesterday, oneWeekAgo, oneWeekFromNow, oneMonthAgo, oneMonthFromNow
Sub-operators (value = days): daysAgo, daysFromNow
Sub-operator (value = YYYY-MM-DD): exactDate

```bash
(created_at,eq,today)                                 # Created today
(due_date,lt,today)                                   # Overdue (before today)
(updated_at,gt,oneWeekAgo)                            # Updated after one week ago
(event_date,eq,exactDate,2024-06-15)                  # On exact date
(deadline,lt,exactDate,2024-12-31)                    # Before Dec 31, 2024
(created_at,gte,daysAgo,7)                            # Created within last 7 days
```

### Date range — two bounds (`btw` / `nbtw` are not supported on dates)

```bash
(event_date,gte,exactDate,2024-01-01)~and(event_date,lte,exactDate,2024-12-31)    # Events in year 2024
```

### in — any of several exact dates

```bash
(due_date,in,exactDate,2024-06-15,2024-07-01)
```

### Null checks for dates (no sub-operator)

```bash
(due_date,blank)                                      # Date is not set
(due_date,notblank)                                   # Date is set
```

## Logical Operations

**IMPORTANT:** Use `~and`, `~or`, `~not` (with tilde prefix). Plain "and"/"or" will error.

```bash
# AND
(filter1)~and(filter2)
(name,eq,John)~and(age,gte,18)

# OR
(filter1)~or(filter2)
(status,eq,active)~or(status,eq,pending)

# NOT
~not(filter)
~not(is_deleted,checked)
```

Lowercase only: `~AND` / `~OR` error. **Never put whitespace after `~and` / `~or` / `~not`** -- `(a,eq,1)~and (b,eq,2)` is a parse error (a space *before* is fine). `~not` only starts an expression or a group; to negate a later term wrap it: `(a,eq,1)~and(~not(b,checked))`.

**Tip:** Use `in` operator instead of nested OR conditions:
```bash
# Instead of: ((status,eq,active)~or(status,eq,pending))~and(country,eq,USA)
# Use:
(status,in,active,pending)~and(country,eq,USA)
```

## Special Values

```
NULL value:         (field,eq,null)
Empty string:       (field,eq,'') or (field,eq,"")
Value with comma:   (field,eq,"hello, world")
Value with quotes:  (field,eq,"it's here") or (field,eq,'say "hello"')
Field with spaces:  (Full Name,eq,John)    # Do NOT use quotes around field names
```

A field name must not carry a trailing space (`(name ,eq,John)` reports `field 'name ' not found`); a trailing space in a value is kept and silently matches nothing. Field names in `where` are case-sensitive (`Column alias '<name>' not found` on a case mismatch); the structured `filter` matches field titles case-insensitively.

## Complex Examples

```bash
# Active users created this month
(status,eq,active)~and(created_at,isWithin,pastMonth)

# Overdue high-priority tasks
(due_date,lt,today)~and(priority,eq,high)~and(completed,notchecked)

# Orders $100-$500 in pending/processing
(amount,gte,100)~and(amount,lte,500)~and(status,in,pending,processing)

# Updated recently, not archived
(updated_at,isWithin,pastNumberOfDays,14)~and(~not(is_archived,checked))

# Multiple segments and countries
(Segment,in,Government,Enterprise)~and(Country,in,Germany,France)
```
