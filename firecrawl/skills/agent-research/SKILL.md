---
name: agent-research
description: Autonomous research agent — start complex web research tasks, get structured results. This skill should be used when the user asks for multi-site exploration, open-ended web research, or deep-dive analysis across multiple sources.
---

# Research Agent

The autonomous research agent browses, searches, and extracts information based on a natural language prompt. Use it for complex multi-site research that would be tedious to do manually.

## Tools

| Tool | Description |
|------|-------------|
| `agent` | Start an autonomous web research agent |
| `agent_status` | Check agent results |

## Start Research Agent

```
Tool: agent
Input: {
  "prompt": "Find the pricing plans for the top 5 project management tools and compare their features",
  "urls": ["https://asana.com/pricing", "https://monday.com/pricing"]
}

Returns: { "agent_id": "agent_xxx", "status": "running" }
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `prompt` | string | Research task description (required, max 10,000 chars) |
| `urls` | string[] | Starting URLs to guide the agent (optional) |
| `schema` | object | JSON schema for structured output (optional) |

## Check Agent Results

```
Tool: agent_status
Input: { "id": "agent_xxx" }

Returns: {
  "status": "completed" | "running" | "failed",
  "result": { ... }
}
```

## Workflows

### Research with Structured Output
```
1. agent({
     prompt: "Research the top 5 CRM tools, find their pricing and key features",
     schema: {
       "type": "object",
       "properties": {
         "tools": {
           "type": "array",
           "items": {
             "type": "object",
             "properties": {
               "name": { "type": "string" },
               "pricing": { "type": "string" },
               "features": { "type": "array", "items": { "type": "string" } }
             }
           }
         }
       }
     }
   }) → Start agent
2. agent_status(agent_id) → Poll until complete
3. Process structured results
```

### Research Starting from Known URLs
```
1. agent({
     prompt: "Compare the API documentation quality of these services",
     urls: ["https://docs.stripe.com", "https://docs.paypal.com"]
   }) → Start with specific URLs
2. agent_status(agent_id) → Get comparison results
```

## When to Use Agent vs Manual Tools

| Use Case | Approach | Why |
|----------|----------|-----|
| Simple page scrape | `scrape_url` | Faster, more predictable |
| Known data extraction | `extract_data` | Direct, schema-based |
| Complex multi-site research | `agent` | Autonomous navigation |
| Open-ended exploration | `agent` | Agent decides what to search/scrape |
| Comparison across many sources | `agent` | Agent handles discovery |

## Best Practices

1. **Be specific in prompts** — clear task description gives better results
2. **Provide starting URLs** — guides the agent to relevant sources
3. **Use schemas** — structured output is more reliable than free-form
4. **Keep prompts under 10k chars** — respect the limit
5. **Poll for results** — agents take time for complex research

## Error Handling

- **Agent fails** → simplify prompt or provide more specific URLs
- **Incomplete results** → break research into smaller, focused prompts
- **Schema mismatch** → ensure schema properties match what can be found on the web
- **Timeout** → reduce scope of research task
