---
name: crm-deals-pipelines
description: CRM deals and sales pipelines — create and manage deals, configure pipeline stages, move deals between pipelines. Use when working with sales processes, deal tracking, or pipeline configuration.
---

# CRM Deals & Pipelines

This skill covers the full sales pipeline lifecycle — pipeline setup, deal management, and stage progression.

## Available Tools

| Tool | Description |
|------|-------------|
| `crm_pipelines_list` | List all sales pipelines |
| `crm_pipelines_show` | Get pipeline details |
| `crm_pipelines_create` | Create a new pipeline |
| `crm_pipelines_update` | Update pipeline settings |
| `crm_pipelines_steps_list` | List stages in a pipeline |
| `crm_pipelines_steps_create` | Add a stage to a pipeline |
| `crm_pipelines_steps_update` | Update a pipeline stage |
| `crm_pipelines_steps_delete` | Remove a pipeline stage |
| `crm_deals_list` | List deals with filters |
| `crm_deals_show` | Get deal details |
| `crm_deals_create` | Create a new deal |
| `crm_deals_update` | Update deal fields |
| `crm_deals_contacts_list` | List contacts linked to a deal |
| `crm_deals_comments_create` | Add comment to a deal |
| `crm_deals_pipelines_change` | Move deal to a different pipeline/step |

## Pipeline Management

### List Pipelines
```
Tool: crm_pipelines_list
Input: {}

Returns all pipelines with IDs, names, and configuration.
```

### Create Pipeline
```
Tool: crm_pipelines_create
Input: {"name": "Sales Pipeline", "is_default": true}

Returns new pipeline ID.
```

### Get Pipeline Details
```
Tool: crm_pipelines_show
Input: {"id": "<pipeline-id>"}

Returns pipeline with all steps/stages.
```

### Update Pipeline
```
Tool: crm_pipelines_update
Input: {"id": "<pipeline-id>", "name": "Enterprise Sales"}
```

## Pipeline Steps (Stages)

### List Steps
```
Tool: crm_pipelines_steps_list
Input: {"pipeline_id": "<pipeline-id>"}

Returns ordered list of stages with IDs and names.
```

### Create Step
```
Tool: crm_pipelines_steps_create
Input: {"pipeline_id": "<pipeline-id>", "name": "Qualification", "position": 1}

Adds a new stage to the pipeline.
```

### Update Step
```
Tool: crm_pipelines_steps_update
Input: {"id": "<step-id>", "name": "Negotiation", "position": 3}
```

### Delete Step
```
Tool: crm_pipelines_steps_delete
Input: {"id": "<step-id>"}

Removes a stage. Deals in this stage should be moved first.
```

## Deal Management

### List Deals
```
Tool: crm_deals_list
Input: {"limit": 50, "offset": 0}

Returns deals with name, amount, step, pipeline, and status.
Supports filtering and pagination.
```

### Create Deal
```
Tool: crm_deals_create
Input: {
  "name": "Enterprise License",
  "pipeline_id": "<pipeline-id>",
  "step_id": "<step-id>",
  "amount": 15000,
  "currency": "USD",
  "contact_id": "<contact-id>"
}

Returns new deal ID.
```

### Get Deal Details
```
Tool: crm_deals_show
Input: {"id": "<deal-id>"}

Returns full deal record with amount, contacts, custom fields, history.
```

### Update Deal
```
Tool: crm_deals_update
Input: {"id": "<deal-id>", "amount": 18000, "name": "Enterprise License v2"}
```

### Move Deal Between Pipelines/Steps
```
Tool: crm_deals_pipelines_change
Input: {"id": "<deal-id>", "pipeline_id": "<new-pipeline-id>", "step_id": "<new-step-id>"}

Moves the deal to a different pipeline or stage.
```

### List Deal Contacts
```
Tool: crm_deals_contacts_list
Input: {"id": "<deal-id>"}

Returns all contacts associated with the deal.
```

### Add Comment to Deal
```
Tool: crm_deals_comments_create
Input: {"id": "<deal-id>", "text": "Client approved pricing. Moving to contract."}
```

## Common Workflows

### Set Up a Complete Sales Pipeline
```
1. crm_pipelines_create(name="B2B Sales") -> Get pipeline ID
2. crm_pipelines_steps_create(pipeline_id, name="Lead", position=1)
3. crm_pipelines_steps_create(pipeline_id, name="Qualification", position=2)
4. crm_pipelines_steps_create(pipeline_id, name="Proposal", position=3)
5. crm_pipelines_steps_create(pipeline_id, name="Negotiation", position=4)
6. crm_pipelines_steps_create(pipeline_id, name="Closed Won", position=5)
```

### Create Deal and Progress Through Pipeline
```
1. crm_pipelines_list() -> Find pipeline
2. crm_pipelines_steps_list(pipeline_id) -> Find first step
3. crm_deals_create(name, pipeline_id, step_id, amount) -> Create deal
4. crm_deals_pipelines_change(deal_id, pipeline_id, next_step_id) -> Advance
5. crm_deals_comments_create(deal_id, text) -> Document progress
```

### Review Pipeline Health
```
1. crm_pipelines_list() -> Get all pipelines
2. crm_deals_list() -> List all deals
3. Group deals by step to see funnel distribution
```

## Best Practices

1. **Create pipelines with clear stages** that mirror your actual sales process
2. **Always specify pipeline and step** when creating deals
3. **Add comments** when moving deals between stages to document reasoning
4. **Link contacts to deals** for relationship tracking
5. **Use amounts and currency** on deals for revenue forecasting
6. **Review pipeline regularly** — move stale deals or close them
