---
name: generate-stack
description: This skill should be used when the user asks to "generate macstack.json from scratch", "design a stack for…", "pick software and architecture for my need", "create a stack spec from my request", or describes a business need without an existing codebase. Designs goals, results, processes, workflows, software and architecture result-first and produces a validated macstack.json.
---

# Generate macstack.json From Scratch (Result-First)

Design a complete stack from a user request. The order is NON-NEGOTIABLE: money first,
software last. Never start from "which technologies to pick" — start from "which
result makes money".

## Step 1 — Goals & Results (the money)

From the user's request extract and confirm:

1. **goals[]** — 1–3 business goals with a horizon and a metric ("$20k MRR by Q2",
   "cut the contract-approval cycle 5×").
2. **results[]** — measurable assets that realize the goals. Each: `class`
   (revenue_asset | client_revenue | pipeline_asset | cost_saving), `metric`
   {unit, target, cadence}, `problem` (which problem it closes), `goal` ref.
   Phrase results as business outcomes, not technologies.

If the user gave only a vague need ("I want a bot"), ask the result question
explicitly: "What measurable result must the bot produce, and what is it worth per
month?"

## Step 2 — Processes → Triggers → Workflows

3. **processes[]** — which business processes produce the results; `type`
   (development | operations | provisioning), `automation_mode`
   (workflow — deterministic | agent — the agent decides | hybrid), tasks with
   HITL gates (`human {role, gate}`) wherever a person is mandatory.
4. **triggers[]** — a separate collection: what starts the automation
   (schedule / webhook / db_event / form / manual) and in which software it lives.
5. **workflows[]** — deterministic implementations: engine, `triggers` refs,
   invocation (mcp/api/cli/webhook/trigger), naming `[Domain] - [Action] - [Trigger]`.

## Step 3 — Software selection

Select software per layer using these rules, in priority order:

1. **Prototype first**: check `discover-context` for a stackmakers-ai prototype that
   already covers the need (composable workspace, directus-nextjs website, agents
   stack…). Reuse beats assembly: set `prototype` and inherit its software.
2. **Open Source first, Agentic Ready first**: prefer tools with MCP + API + CLI
   (rating full/good): postgresql, nocodb, nocobase, n8n, trigger-dev, directus,
   qdrant, minio. A stack without MCP is "just software".
3. **Proven bundles**: universal workspace = postgresql + nocodb + n8n (+trigger-dev);
   web app = directus + nextjs (+trigger-dev); headless agents stack = postgresql +
   qdrant + n8n/trigger-dev; BPMS = nocobase.
4. **Custom code — only for the unique**: only what has no ready-made equivalent;
   `type: "custom"`, category `custom-scripts`.

For every software: **copy its passport from the registry first**
(`https://raw.githubusercontent.com/macstacks/registry/main/software/<slug>.json` —
category, type, form, license, layers, agentic already consistent), then add the
stack-specific half: `role`, `value` (why it is in the stack — one of the 4 values),
`hosting`, `instances[]`, `cost`. No passport in the registry → fill the taxonomy by
hand from the schema enums and propose the new passport as a registry PR.

## Step 4 — The rest of the file

- **entities[]** — entities with attributes, stores and a MANDATORY master; the
  client's external systems = software with `hosting: "external"`.
- **interfaces[]** — human and agent-facing; `path` is relative (full URL = instance
  url + path); notifications = `type: "channel"`.
- **connections** — MCP/API/CLI wiring (later `.mcp.json` is generated from it).
- **agents** — stack_agents (a worker at minimum; an orchestrator if a messenger
  frontend is needed) + managed_agents (model + instructions + tools + invocations).
- **context.plugins** — from `discover-context`: technology `{tool}-{dev|ops|provision}`
  + the architecture's stack plugin.
- **resources.accesses** — ALL env keys with the `required` flag (the source for
  `infisical-env`).
- **profile** — type (composable | application | agents), stack_level, patterns.
- **commercial** — the offer and the Cost of Ownership (make the open-source-first
  economics explicit).
- **lifecycle** — `stage: "define"`, open_questions, needs_from_client.

## Step 5 — Validate & present

Run `lint`. Present the file result-first: goals/results as a table first, then
processes, then the stack. Ask the user to confirm the RESULTS before any
scaffolding — "the system designs itself from the result" means changing the result
after assembly is expensive.

Use the `macstack-architect` agent for the design when the request spans many
domains or the software choice is ambiguous.

<example>
user: "I need a stack for an agency: intake website leads, manage clients, send reports"
→ goals: inbound channel; results: qualified-leads (pipeline_asset, 30/mo), weekly-report (cost_saving)
→ processes: lead-capture (workflow), reporting (workflow), crm-upkeep (hybrid)
→ prototype: github:stackmakers-ai/project-composable-stack-v1 (workspace) — the website as a separate substack
→ software: postgresql+nocodb+n8n+trigger-dev; entities: client (master postgresql), lead, report
→ lint → show the results → confirm → scaffold-project
</example>
