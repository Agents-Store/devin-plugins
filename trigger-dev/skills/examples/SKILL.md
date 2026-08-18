---
name: examples
description: Trigger.dev code examples, end-to-end workflow templates, MCP tool usage patterns, and scenario walkthroughs. Use when the user asks for "trigger.dev examples", "task templates", "MCP tool patterns", "trigger.dev workflow examples", or needs reference implementations.
---

# Examples & Patterns

Ready-to-use examples and complete workflow scenarios.

## MCP Tool Examples

| File | Description |
|------|-------------|
| @references/mcp/tool-patterns.md | Common MCP tool call patterns and workflows |

## Scenario Walkthroughs

| File | Description |
|------|-------------|
| @references/scenarios/webhook-processor.md | Complete webhook processing task with queue and retry |
| @references/scenarios/ai-pipeline.md | AI agent pipeline with chaining, tools, and streaming |
| @references/scenarios/cron-data-sync.md | Scheduled data sync with batch processing |

## Quick Reference Patterns

### Initialize New Project

```
1. list_orgs() → pick org
2. initialize_project(orgParam, projectName, cwd)
3. get_current_worker(environment="dev") → verify
```

### Trigger and Monitor

```
1. get_current_worker() → find task + schema
2. trigger_task(taskId, payload) → get run ID
3. wait_for_run_to_complete(runId) → get result
```

### Debug Failures

```
1. list_runs(status="FAILED", period="1d")
2. get_run_details(runId) → read trace + span IDs
3. get_span_details(runId, spanId) → AI enrichment (model, tokens, cost) if GenAI span
4. Fix code, redeploy
5. trigger_task(taskId, payload) → retry
```

### Deploy to Production

```
1. deploy(environment="staging") → test first
2. trigger_task(environment="staging") → verify
3. deploy(environment="prod") → ship it
4. list_deploys(environment="prod", limit=1) → confirm
```

### Run Dev Server from an Agent

```
1. start_dev_server(configPath?)             → launches `trigger dev` in background
2. dev_server_status(lines=50)               → poll until status="ready"
3. get_current_worker(environment="dev")     → task list
4. trigger_task(...)                         → test task
5. stop_dev_server()                         → tear down
```

### Analyze Failures with TRQL

```
1. get_query_schema(table="runs")
2. query({
     query: "SELECT task_identifier, count() AS n
             FROM runs
             WHERE status = 'Failed'
             GROUP BY task_identifier
             ORDER BY n DESC LIMIT 10",
     period: "7d"
   })
```

### LLM Cost Breakdown

```
1. get_query_schema(table="llm_metrics")
2. query({
     query: "SELECT model, sum(cost_usd) AS usd
             FROM llm_metrics
             GROUP BY model
             ORDER BY usd DESC",
     period: "30d"
   })
```

### Switch Profile Mid-Session

```
1. whoami()                           → current profile + API URL
2. list_profiles()                    → available profiles
3. switch_profile("self-hosted-prod") → subsequent tool calls use new profile
```

### Prompt Override Hotfix

```
1. list_prompts(environment="prod")                              → find slug
2. get_prompt_versions(slug, environment="prod")                 → see current/override state
3. create_prompt_override(slug, textContent, commitMessage)      → apply hotfix
4. (iterate) update_prompt_override(slug, textContent)
5. remove_prompt_override(slug)                                  → revert after code fix deploys
```
