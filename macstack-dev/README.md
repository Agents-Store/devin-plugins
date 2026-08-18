# macstack-dev (Devin plugin)

MACSTACK dev plugin for Agents Store. Creates and maintains macstack.json — the standardized business + technical stack specification for Claude projects: init in existing projects, generate from scratch (result-first), discover context plugins and prototypes, scaffold project files in the prototype → stack plugins → dev plugins order, wire Infisical env, install best-practice rules and commands.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (11)

- `best-practices` — This skill should be used when the user asks to "install best practice rules", "set up project rules", "add project rules and commands", "set up project conventions", or scaffold-project reaches the rules step. Installs the proven MACSTACK rule set (.claude/rules) and core commands into a project.
- `discover-context` — This skill should be used when the user asks to "find plugins for this stack", "discover context for the project", "which plugins should I install", "find a prototype", "pick a stack prototype", or when init-project/generate-stack need context.plugins and prototype candidates. Searches Agents Store plugins and stackmakers-ai prototypes on GitHub.
- `examples` — This skill should be used when the user asks for "macstack examples", "show a full macstack.json example", "how does a complete macstack.json look", "walk me through a macstack scenario", or needs an end-to-end scenario walkthrough for this plugin's skills.
- `feedback` — This skill should be used when the user reports a problem with macstack-dev or the MACSTACK standard — "this skill did the wrong thing", "the schema is missing a field", "the passport for X is wrong", "send macstack feedback", "improve the schema based on my edit", "fix the macstack plugin" — and the fix must land in the right source (plugin, schema repo, or registry repo).
- `generate-stack` — This skill should be used when the user asks to "generate macstack.json from scratch", "design a stack for…", "pick software and architecture for my need", "create a stack spec from my request", or describes a business need without an existing codebase. Designs goals, results, processes, workflows, software and architecture result-first and produces a validated macstack.json.
- `infisical-env` — This skill should be used when the user asks to "set up Infisical for this project", "create .infisical.json", "pull the env keys", "wire the env", "sync secrets", or scaffold-project reaches the env step. Creates .infisical.json, pulls .env.prod/.env.dev, ensures every key from macstack.json resources.accesses exists, and installs the mandatory secrets scripts and commands.
- `init-project` — This skill should be used when the user asks to "create macstack.json in this project", "add macstack.json", "init macstack", "describe this existing project as macstack.json", or an existing codebase has no macstack.json. Audits the existing project and produces a validated macstack.json draft.
- `lint` — This skill should be used when the user asks to "validate macstack.json", "lint macstack", "check the stack spec", "verify macstack.json integrity", or after any skill of this plugin writes/edits macstack.json. Validates against the bundled JSON Schema and the referential-integrity rules.
- `scaffold-project` — This skill should be used when the user asks to "scaffold the project from macstack.json", "create the project working files", "generate project files from the spec", "build the project from macstack.json", or after a macstack.json is validated and the working tree must be built. Creates project files strictly in the prototype → stack plugins → dev plugins order.
- `setup` — This skill should be used when the user asks "what is macstack.json", "set up macstack", "check macstack setup", "verify macstack.json", "explain the macstack standard", or before any other macstack-dev skill runs in a project for the first time. Explains the standard, locates the schema and category registry, and verifies tooling.
- `troubleshoot` — This skill should be used when the user reports "macstack lint fails", "prototype does not resolve", "env keys missing", "scaffold broke my files", "cross-stack reference does not work", or any macstack-dev skill errors out. Diagnoses the common failure modes of the macstack.json toolchain.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents
- 6 command(s) — Devin plugins do not support commands

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/macstack-dev
