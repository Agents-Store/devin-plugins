# n8n-provision (Devin plugin)

n8n instance provisioning plugin. Discover workflows from the official template library (12,900+ templates), GitHub repos, and community platforms, then analyze, import, and batch-deploy them to provision an n8n instance.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (9)

- `batch-provisioning` — Provision an n8n instance with multiple workflows in a single batch operation. Handles dependency ordering, credential grouping, progress tracking, rollback strategy, and post-flight verification.
Use when: "provision n8n instance", "batch import workflows", "set up n8n with workflows", "deploy multiple templates", "bootstrap n8n", "install workflow suite", "bulk deploy workflows"

- `community-source-discovery` — Find n8n workflows from GitHub repositories and third-party platforms when the official template library is insufficient. Use when asked to "find n8n workflow on github", "community n8n workflows", "search github for n8n", "n8n workflow sources", "n8n automation repository", or when official template search returns no good matches.
- `credential-planning` — Plan and prepare credentials before importing workflows to an n8n instance. Extracts credential requirements from workflow JSON, checks existing credentials, groups by service, and produces a setup checklist.
Use when: "plan credentials for import", "what credentials needed", "n8n credential setup", "prepare credentials before import", "credential requirements", "which credentials do I need", "credential checklist"

- `examples` — End-to-end scenario walkthroughs for n8n workflow provisioning. This skill should be used when the user asks for "n8n provisioning example", "how to import workflows", "n8n provision walkthrough", "batch import tutorial", "template deploy guide", "n8n setup example", "find and import n8n workflow", "deploy automation suite", or needs a complete example of discovering, analyzing, and deploying n8n workflows.

- `instance-readiness` — Assess n8n instance readiness before provisioning. Runs health checks, inventories workflows and credentials, detects conflicts, verifies community nodes, and produces a readiness report with pass/warn/fail ratings.
Use when: "check n8n instance", "is n8n ready for provisioning", "n8n health check", "verify n8n instance", "pre-provisioning check", "audit n8n before import", "instance readiness report"

- `single-workflow-import` — Import and deploy a single workflow to an n8n instance from the official template library or community JSON source. Handles validation, auto-fix, credential stripping, and post-import verification.
Use when: "import n8n workflow", "deploy n8n template", "install n8n automation", "add workflow to n8n", "import template to n8n", "deploy workflow from JSON", "install community workflow"

- `template-discovery` — Search the official n8n template library (12,900+ templates). Use when asked to "search n8n templates", "find n8n workflow", "browse n8n template library", "n8n workflow catalog", "discover n8n automation", or need to find a template by keyword, node type, task, category, or architectural pattern.
- `troubleshoot` — Diagnose and fix n8n provisioning and import issues. This skill should be used when the user encounters "n8n import error", "template deploy failed", "workflow validation error", "provisioning troubleshoot", "n8n provision problem", "community node missing", "credential not found", "workflow won't activate", "workflow won't publish", "template not found", "batch deploy failed", or needs help debugging n8n workflow import and deployment issues.

- `workflow-analysis` — Analyze an n8n workflow JSON before importing — node inventory, connection topology, credential requirements, security flags, complexity scoring, and compatibility checks. Use when asked to "analyze n8n workflow", "check workflow before import", "workflow compatibility check", "review n8n template", "assess workflow complexity", or before importing any template or community workflow.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents
- 5 command(s) — Devin plugins do not support commands

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/n8n-provision
