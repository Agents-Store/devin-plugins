# n8n-dev (Devin plugin)

n8n workflow automation dev plugin for Agents Store. MCP tools guide (external + native), workflow patterns, expression syntax, validation, node configuration, Code node patterns, REST API reference, CLI recipes, and troubleshooting for developers building n8n workflows.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (13)

- `n8n-api-reference` — n8n REST API reference with all endpoints, authentication, and curl examples. Use when making direct API calls, writing scripts that interact with n8n API, or when MCP tools are unavailable. Reference-only skill.
- `n8n-cli-recipes` — n8n CLI commands for self-hosted instances. Use when executing workflows from command line, exporting/importing workflows and credentials, managing licenses, resetting user accounts, running security audits via CLI, or managing community nodes. Also use when asking about "n8n CLI", "command line", "n8n execute", "export workflow".
- `n8n-examples` — End-to-end n8n workflow development scenarios with step-by-step walkthroughs. Use when starting a new workflow, looking for real-world examples, wanting to see complete workflow creation from start to finish, or asking about "n8n example", "workflow example", "show me how to build", "sample workflow".
- `n8n-code-javascript` — Write JavaScript code in n8n Code nodes. Use when writing JavaScript in n8n, using $input/$json/$node syntax, making HTTP requests with $helpers, working with dates using DateTime, troubleshooting Code node errors, or choosing between Code node modes.
- `n8n-code-python` — Write Python code in n8n Code nodes. Use when writing Python in n8n, using _input/_json/_node syntax, working with standard library, or need to understand Python limitations in n8n Code nodes.
- `n8n-expression-syntax` — Validate n8n expression syntax and fix common errors. Use when writing n8n expressions, using {{}} syntax, accessing $json/$node variables, troubleshooting expression errors, or working with webhook data in workflows.
- `n8n-mcp-tools-expert` — Expert guide for using n8n-mcp MCP tools effectively. Use when searching for nodes, validating configurations, accessing templates, managing workflows, managing credentials, auditing instance security, or using any n8n-mcp tool. Provides tool selection guidance, parameter formats, and common patterns.
- `n8n-native-mcp` — Guide for using n8n native MCP server tools. Use when creating workflows from SDK code, executing workflows, publishing/unpublishing, getting node type definitions, using get_sdk_reference, or working with the official n8n MCP server. Also use when asking about "native MCP", "n8n SDK", "workflow from code", "execute workflow".
- `n8n-node-configuration` — Operation-aware node configuration guidance. Use when configuring nodes, understanding property dependencies, determining required fields, choosing between get_node detail levels, or learning common configuration patterns by node type.
- `n8n-validation-expert` — Interpret validation errors and guide fixing them. Use when encountering validation errors, validation warnings, false positives, operator structure issues, or need help understanding validation results. Also use when asking about validation profiles, error types, or the validation loop process.
- `n8n-workflow-patterns` — Proven workflow architectural patterns from real n8n workflows. Use when building new workflows, designing workflow structure, choosing workflow patterns, planning workflow architecture, or asking about webhook processing, HTTP API integration, database operations, AI agent workflows, or scheduled tasks.
- `n8n-setup` — Verify n8n MCP connection and configure n8n MCP servers. Use when the user asks to "verify n8n connection", "check n8n MCP", "test n8n setup", "configure n8n", "set up n8n MCP", or needs to confirm that n8n MCP integration is operational.
- `n8n-troubleshoot` — Troubleshoot n8n workflow development issues. Use when encountering MCP connection errors, API authentication failures, workflow execution problems, expression errors, node configuration issues, or any n8n-related error. Also use when asking about "n8n error", "n8n not working", "debug n8n", "fix n8n".

## Not carried over

- 1 agent(s) — Devin plugins do not support agents

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/n8n-dev
