---
name: code-patterns
description: Code node patterns — JavaScript and Python data transformation, API processing, date handling, binary data. This skill should be used when the user asks to write code in Code nodes, transform data with JavaScript or Python, or process binary data.
---

# Code Node Patterns

JavaScript and Python patterns for n8n Code nodes — data transformation, API response processing, date handling, and binary data.

## JavaScript Patterns

### Data Transformation

#### Flatten Nested Objects
```javascript
const items = $input.all();

return items.map(item => ({
  json: {
    id: item.json.id,
    name: item.json.user.name,
    email: item.json.user.email,
    city: item.json.user.address.city
  }
}));
```

#### Group Items by Field
```javascript
const items = $input.all();
const grouped = {};

for (const item of items) {
  const key = item.json.category;
  if (!grouped[key]) grouped[key] = [];
  grouped[key].push(item.json);
}

return Object.entries(grouped).map(([category, items]) => ({
  json: { category, items, count: items.length }
}));
```

#### Deduplicate Items
```javascript
const items = $input.all();
const seen = new Set();
const unique = [];

for (const item of items) {
  const key = item.json.email;
  if (!seen.has(key)) {
    seen.add(key);
    unique.push(item);
  }
}

return unique;
```

#### Filter and Transform
```javascript
const items = $input.all();

return items
  .filter(item => item.json.status === "active" && item.json.age >= 18)
  .map(item => ({
    json: {
      fullName: `${item.json.firstName} ${item.json.lastName}`,
      email: item.json.email.toLowerCase(),
      tier: item.json.spending > 1000 ? "premium" : "standard"
    }
  }));
```

### API Response Processing

#### Extract Paginated API Data
```javascript
const response = $input.first().json;
const results = response.data || response.results || [];

return results.map(record => ({
  json: record
}));
```

#### Handle API Error Responses
```javascript
const response = $input.first().json;

if (response.error || response.statusCode >= 400) {
  return [{
    json: {
      success: false,
      error: response.error || response.message || "Unknown error",
      statusCode: response.statusCode
    }
  }];
}

return [{ json: { success: true, data: response.data } }];
```

#### Merge Data from Multiple API Calls
```javascript
const users = $("Get Users").all().map(i => i.json);
const orders = $("Get Orders").all().map(i => i.json);

return users.map(user => ({
  json: {
    ...user,
    orders: orders.filter(o => o.userId === user.id),
    totalOrders: orders.filter(o => o.userId === user.id).length
  }
}));
```

### Date Handling

#### Format Dates
```javascript
const items = $input.all();

return items.map(item => ({
  json: {
    ...item.json,
    formattedDate: new Date(item.json.createdAt).toLocaleDateString("en-US"),
    isoDate: new Date(item.json.createdAt).toISOString(),
    timestamp: new Date(item.json.createdAt).getTime()
  }
}));
```

#### Calculate Date Differences
```javascript
const items = $input.all();
const now = new Date();

return items.map(item => {
  const created = new Date(item.json.createdAt);
  const diffMs = now - created;
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  return {
    json: {
      ...item.json,
      daysAgo: diffDays,
      isRecent: diffDays <= 7
    }
  };
});
```

#### Generate Date Ranges
```javascript
const startDate = new Date($json.startDate);
const endDate = new Date($json.endDate);
const dates = [];

for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
  dates.push(new Date(d).toISOString().split("T")[0]);
}

return dates.map(date => ({ json: { date } }));
```

### Aggregation

#### Sum, Average, Count
```javascript
const items = $input.all();
const values = items.map(i => i.json.amount);

return [{
  json: {
    count: values.length,
    sum: values.reduce((a, b) => a + b, 0),
    average: values.reduce((a, b) => a + b, 0) / values.length,
    min: Math.min(...values),
    max: Math.max(...values)
  }
}];
```

#### Pivot Table
```javascript
const items = $input.all();
const pivot = {};

for (const item of items) {
  const row = item.json.month;
  const col = item.json.category;
  if (!pivot[row]) pivot[row] = {};
  pivot[row][col] = (pivot[row][col] || 0) + item.json.amount;
}

return Object.entries(pivot).map(([month, categories]) => ({
  json: { month, ...categories }
}));
```

### Working with Binary Data

#### Create CSV from Items
```javascript
const items = $input.all();
const headers = Object.keys(items[0].json);
const csv = [
  headers.join(","),
  ...items.map(item => headers.map(h => `"${item.json[h] ?? ""}"`).join(","))
].join("\n");

return [{
  json: { filename: "export.csv" },
  binary: {
    data: {
      data: Buffer.from(csv).toString("base64"),
      mimeType: "text/csv",
      fileName: "export.csv"
    }
  }
}];
```

#### Parse CSV Content
```javascript
const csvContent = $input.first().json.content;
const lines = csvContent.split("\n");
const headers = lines[0].split(",").map(h => h.trim().replace(/"/g, ""));

return lines.slice(1).filter(l => l.trim()).map(line => {
  const values = line.split(",").map(v => v.trim().replace(/"/g, ""));
  const obj = {};
  headers.forEach((h, i) => obj[h] = values[i]);
  return { json: obj };
});
```

---

## Python Patterns

### Basic Data Transformation
```python
items = _input.all()

result = []
for item in items:
    result.append({
        "json": {
            "name": item.json["firstName"] + " " + item.json["lastName"],
            "email": item.json["email"].lower(),
            "active": item.json["status"] == "active"
        }
    })

return result
```

### Filter Items
```python
items = _input.all()
return [item for item in items if item.json.get("status") == "active"]
```

### Aggregate Data
```python
items = _input.all()
values = [item.json["amount"] for item in items]

return [{
    "json": {
        "count": len(values),
        "total": sum(values),
        "average": sum(values) / len(values) if values else 0,
        "min": min(values) if values else 0,
        "max": max(values) if values else 0
    }
}]
```

### Date Operations
```python
from datetime import datetime, timedelta

items = _input.all()
now = datetime.now()

result = []
for item in items:
    created = datetime.fromisoformat(item.json["createdAt"].replace("Z", "+00:00"))
    days_ago = (now - created.replace(tzinfo=None)).days

    result.append({
        "json": {
            **item.json,
            "daysAgo": days_ago,
            "isRecent": days_ago <= 7
        }
    })

return result
```

### JSON Processing
```python
import json

items = _input.all()
raw = items[0].json.get("rawData", "{}")
parsed = json.loads(raw) if isinstance(raw, str) else raw

return [{"json": parsed}]
```

## Best Practices

1. **Always return an array of items** — `[{ json: { ... } }]`
2. **Handle empty inputs** — check `$input.all().length` before processing
3. **Use `$()` to reference nodes** — safer than `$node["Name"]`
4. **Avoid side effects** — don't make API calls from Code nodes, use HTTP Request
5. **Keep code simple** — complex logic is hard to debug in n8n
6. **Use try/catch** — wrap risky operations to prevent node failures
7. **Log for debugging** — use `console.log()` in test mode
8. **Prefer JavaScript** — broader community support and examples
