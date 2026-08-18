---
name: node-configuration
description: Node configuration — HTTP Request, Code, IF, Switch, Merge, Split In Batches, error handling. This skill should be used when the user asks to configure a specific node type, set up authentication, write conditions, or add error handling.
---

# Node Configuration

Detailed configuration guide for commonly used n8n nodes — HTTP Request, Code, IF, Switch, Merge, Split In Batches, and error handling.

## HTTP Request Node

### Basic Configuration
```json
{
  "method": "GET",
  "url": "https://api.example.com/data",
  "authentication": "none",
  "options": {}
}
```

### Authentication Types
| Type | Configuration |
|------|--------------|
| None | No auth headers |
| Generic Credential | Predefined credential with header/query auth |
| Predefined Credential | Service-specific (OAuth2, API Key, etc.) |

### Headers
```json
{
  "method": "POST",
  "url": "https://api.example.com/data",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      { "name": "Content-Type", "value": "application/json" },
      { "name": "X-API-Key", "value": "{{ $env.API_KEY }}" }
    ]
  }
}
```

### Request Body
```json
{
  "method": "POST",
  "url": "https://api.example.com/data",
  "sendBody": true,
  "bodyContentType": "json",
  "jsonBody": "={{ JSON.stringify({ name: $json.name, email: $json.email }) }}"
}
```

### Pagination
```json
{
  "options": {
    "pagination": {
      "paginationMode": "offset",
      "limitParameter": "limit",
      "offsetParameter": "offset",
      "pageSize": 100,
      "maxPages": 10
    }
  }
}
```

### Retry on Failure
```json
{
  "options": {
    "retry": {
      "enabled": true,
      "maxRetries": 3,
      "waitBetweenRetries": 1000
    }
  }
}
```

### Response Handling
```json
{
  "options": {
    "response": {
      "fullResponse": false,
      "responseFormat": "json"
    }
  }
}
```

## Code Node

### JavaScript Mode
```javascript
// Access all input items
const items = $input.all();

// Process each item
for (const item of items) {
  item.json.processed = true;
  item.json.timestamp = new Date().toISOString();
}

return items;
```

### Python Mode
```python
# Access all input items
items = _input.all()

# Process each item
for item in items:
    item.json["processed"] = True
    item.json["timestamp"] = "2024-01-01"

return items
```

### Return Format
Code node must return an array of items:
```javascript
// Create new items
return [
  { json: { name: "Item 1", value: 100 } },
  { json: { name: "Item 2", value: 200 } }
];
```

### Access Previous Node Data
```javascript
// Get data from a specific node
const userData = $("HTTP Request").first().json;
const allRecords = $("Database Query").all();

// Access environment variables
const apiKey = $env.API_KEY;
```

## IF Node

### Basic Condition
```json
{
  "conditions": {
    "string": [
      {
        "value1": "={{ $json.status }}",
        "operation": "equals",
        "value2": "active"
      }
    ]
  }
}
```

### Condition Types
| Type | Operations |
|------|-----------|
| String | equals, notEquals, contains, notContains, startsWith, endsWith, regex, isEmpty, isNotEmpty |
| Number | equals, notEquals, larger, smaller, largerEqual, smallerEqual, isEmpty, isNotEmpty |
| Boolean | true, false |
| DateTime | after, before, equals |

### Multiple Conditions
```json
{
  "conditions": {
    "string": [
      { "value1": "={{ $json.status }}", "operation": "equals", "value2": "active" }
    ],
    "number": [
      { "value1": "={{ $json.age }}", "operation": "larger", "value2": 18 }
    ]
  },
  "combineConditions": "AND"
}
```

Combine modes: `AND` (all must match), `OR` (any must match).

### Outputs
- **true** branch: conditions match
- **false** branch: conditions don't match

## Switch Node

### Rules Mode
```json
{
  "mode": "rules",
  "rules": [
    { "value": "={{ $json.type }}", "operation": "equals", "value2": "order", "output": 0 },
    { "value": "={{ $json.type }}", "operation": "equals", "value2": "refund", "output": 1 },
    { "value": "={{ $json.type }}", "operation": "equals", "value2": "inquiry", "output": 2 }
  ],
  "fallbackOutput": 3
}
```

### Expression Mode
```json
{
  "mode": "expression",
  "expression": "={{ $json.type }}",
  "outputs": ["order", "refund", "inquiry"]
}
```

## Merge Node

### Modes
| Mode | Description | Use Case |
|------|-------------|----------|
| Append | Combine all items | Merge two lists |
| Combine by Position | Pair items by index | Zip two lists |
| Combine by Fields | Match on field values | Join on ID |
| Multiplex | Cross-product of inputs | All combinations |
| Choose Branch | Pick one input | After IF node |

### Combine by Fields (Join)
```json
{
  "mode": "combineMerge",
  "mergeByFields": {
    "values": [
      { "field1": "id", "field2": "userId" }
    ]
  },
  "joinMode": "inner",
  "options": {
    "clashHandling": "preferInput1"
  }
}
```

Join modes: `inner` (matching only), `left` (all from input 1), `right` (all from input 2), `outer` (all from both).

## Split In Batches Node

Process items in batches (for API rate limiting, memory management).

```json
{
  "batchSize": 10,
  "options": {
    "reset": false
  }
}
```

### Loop Pattern
```
Split In Batches → Process → [loop back to Split In Batches]
```

The node outputs items in groups of `batchSize`. Connect the "loop" output back to itself to process next batch.

## Error Handling

### Error Trigger Node
Catches errors from any node in the workflow.

```
Main workflow: Node A → Node B → Node C
Error workflow: Error Trigger → Send Notification
```

### Stop and Error Node
Deliberately stop execution with an error message.

```json
{
  "errorMessage": "Validation failed: missing required field '{{ $json.field }}'"
}
```

### Try/Catch Pattern
```
Node A → Node B (may fail)
         ↓ error output
         Error Handler → Continue or Notify
```

Enable "Continue On Fail" on a node to catch its errors:
- Node setting: `continueOnFail: true`
- Error data available in `$json._error`

### Retry Pattern
```
Split In Batches → HTTP Request (with retry options) → [loop back]
```

## Node Positioning Guidelines

When creating workflows via MCP:
```
X spacing: 200px between nodes
Y spacing: 150px between parallel branches
Starting position: x=250, y=300
```

## Common Node Combinations

### API Call with Error Handling
```
HTTP Request → IF (status check) → true: Process / false: Error Handler
```

### Batch Processing
```
Get All Items → Split In Batches → Process → [loop] → Done
```

### Data Transformation Pipeline
```
Input → Code (transform) → IF (filter) → Set (format) → Output
```

### Webhook with Validation
```
Webhook → IF (validate) → true: Process → Respond / false: Respond with Error
```
