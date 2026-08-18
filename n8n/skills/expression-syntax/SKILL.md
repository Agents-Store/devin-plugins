---
name: expression-syntax
description: Expression syntax — variables, methods, JMESPath, data references. This skill should be used when the user asks to write expressions, reference data between nodes, use JMESPath, or debug expression errors.
---

# Expression Syntax

Complete reference for n8n expression syntax — variables, data references, built-in methods, and common patterns.

## Expression Basics

Expressions use double curly braces: `{{ expression }}`. They can reference data from previous nodes, environment variables, and built-in functions.

```
{{ $json.fieldName }}
{{ $json["field with spaces"] }}
{{ $json.nested.field }}
```

## Built-in Variables

### Current Item Data
| Variable | Description |
|----------|-------------|
| `$json` | Current item's JSON data (alias for `$input.item.json`) |
| `$binary` | Current item's binary data |
| `$input.item.json` | Full form of current item |
| `$input.all()` | All items from previous node (array) |
| `$input.first()` | First item from previous node |
| `$input.last()` | Last item from previous node |

### Node References
| Variable | Description |
|----------|-------------|
| `$node["Node Name"].json` | Data from a specific named node |
| `$("Node Name").item.json` | Same as above (shorthand) |
| `$("Node Name").all()` | All items from a specific node |
| `$("Node Name").first()` | First item from a specific node |

### Workflow & Execution
| Variable | Description |
|----------|-------------|
| `$workflow.id` | Current workflow ID |
| `$workflow.name` | Current workflow name |
| `$workflow.active` | Whether workflow is active |
| `$execution.id` | Current execution ID |
| `$execution.mode` | Execution mode (manual, trigger, webhook) |
| `$execution.resumeUrl` | URL to resume a waiting execution |

### Environment & Parameters
| Variable | Description |
|----------|-------------|
| `$env.VARIABLE_NAME` | Environment variable |
| `$vars.variableName` | n8n workflow variable |
| `$parameter.fieldName` | Current node parameter value |
| `$itemIndex` | Index of current item in the array |
| `$runIndex` | Current run index (for loops) |
| `$now` | Current DateTime |
| `$today` | Today's date at midnight |

### Trigger Data
| Variable | Description |
|----------|-------------|
| `$webhookData` | Data from webhook trigger |
| `$execution.customData` | Custom data set during execution |

## String Methods

```
{{ $json.name.toUpperCase() }}
{{ $json.name.toLowerCase() }}
{{ $json.email.includes("@gmail.com") }}
{{ $json.text.replace("old", "new") }}
{{ $json.text.replaceAll("old", "new") }}
{{ $json.name.trim() }}
{{ $json.name.length }}
{{ $json.text.slice(0, 100) }}
{{ $json.text.split(",") }}
{{ $json.name.startsWith("Mr") }}
{{ $json.name.endsWith("Jr") }}
```

## Number Methods

```
{{ $json.price.toFixed(2) }}
{{ Math.round($json.value) }}
{{ Math.floor($json.value) }}
{{ Math.ceil($json.value) }}
{{ Math.max($json.a, $json.b) }}
{{ Math.min($json.a, $json.b) }}
{{ parseInt($json.stringNumber) }}
{{ parseFloat($json.stringDecimal) }}
```

## Array Methods

```
{{ $json.items.length }}
{{ $json.items.filter(item => item.status === "active") }}
{{ $json.items.map(item => item.name) }}
{{ $json.items.find(item => item.id === 123) }}
{{ $json.items.some(item => item.price > 100) }}
{{ $json.items.every(item => item.active) }}
{{ $json.tags.join(", ") }}
{{ $json.items.sort((a, b) => a.price - b.price) }}
{{ $json.items.reduce((sum, item) => sum + item.price, 0) }}
{{ $json.items.includes("value") }}
```

## Date and Time

### Using Luxon (built-in)
```
{{ $now.toISO() }}                          // 2024-01-15T10:30:00.000Z
{{ $now.toFormat("yyyy-MM-dd") }}           // 2024-01-15
{{ $now.toFormat("dd/MM/yyyy HH:mm") }}     // 15/01/2024 10:30
{{ $now.plus({ days: 7 }).toISO() }}        // 7 days from now
{{ $now.minus({ hours: 2 }).toISO() }}      // 2 hours ago
{{ $now.startOf("day").toISO() }}           // Start of today
{{ $now.endOf("month").toISO() }}           // End of current month
{{ $now.weekday }}                           // Day of week (1=Mon, 7=Sun)
{{ $now.year }}                              // Current year
{{ $now.month }}                             // Current month (1-12)
{{ $now.day }}                               // Current day of month
```

### Parsing Dates
```
{{ DateTime.fromISO($json.date) }}
{{ DateTime.fromFormat($json.date, "dd/MM/yyyy") }}
{{ DateTime.fromMillis($json.timestamp) }}
{{ DateTime.fromSeconds($json.unixTimestamp) }}
```

### Date Comparisons
```
{{ DateTime.fromISO($json.dueDate) < $now }}     // Is past due?
{{ DateTime.fromISO($json.dueDate).diff($now, "days").days }}  // Days until due
```

## JMESPath Expressions

n8n supports JMESPath for complex data queries in the JMESPath expression mode:

```
// Select nested field
people[*].name

// Filter array
people[?age > `30`]

// Sort
sort_by(people, &name)

// Select multiple fields
people[*].{name: name, email: email}

// Flatten nested arrays
orders[*].items[]

// Conditions
people[?status == 'active'].name
```

## Common Patterns

### Conditional Values (Ternary)
```
{{ $json.status === "active" ? "Yes" : "No" }}
{{ $json.price > 100 ? "Premium" : "Standard" }}
{{ $json.email ? $json.email : "no-email@example.com" }}
```

### Null/Undefined Handling
```
{{ $json.field ?? "default value" }}          // Nullish coalescing
{{ $json.nested?.field ?? "missing" }}        // Optional chaining
{{ $json.items?.length ?? 0 }}               // Safe array length
```

### String Templates
```
{{ `Hello ${$json.firstName} ${$json.lastName}` }}
{{ `Order #${$json.id} - Total: $${$json.total.toFixed(2)}` }}
```

### Object Manipulation
```
{{ Object.keys($json) }}                     // Get all field names
{{ Object.values($json) }}                   // Get all values
{{ Object.entries($json) }}                  // Get key-value pairs
{{ JSON.stringify($json.data) }}             // Serialize to string
{{ JSON.parse($json.jsonString) }}           // Parse JSON string
```

### Combine Data from Multiple Nodes
```
{{ $("HTTP Request").first().json.apiData }}
{{ $("Customers DB").all().map(i => i.json.email) }}
{{ $("Config").first().json.setting ?? "default" }}
```

## Common Mistakes and Fixes

| Mistake | Fix |
|---------|-----|
| `{{ $json.field name }}` | `{{ $json["field name"] }}` — use brackets for spaces |
| `{{ $json.items[0] }}` in empty array | `{{ $json.items?.[0] ?? null }}` — check for empty |
| `{{ $node.NodeName.json }}` | `{{ $("Node Name").item.json }}` — use function syntax |
| `{{ $json.date + 1 }}` for adding days | `{{ DateTime.fromISO($json.date).plus({days:1}).toISO() }}` |
| `{{ $json.price * 1.1 }}` returns string | `{{ Number($json.price) * 1.1 }}` — ensure numeric |
| Accessing data from parallel branch | Use `$("Node Name")` to reference specific node by name |

## Expression Modes

n8n supports two expression modes in different contexts:
1. **JavaScript** — default for most fields, uses `{{ }}` syntax
2. **JMESPath** — available in specific nodes, for complex data querying
