# dokploy-dev (Devin plugin)

Dokploy self-hosted PaaS development plugin (aligned with Dokploy v0.30.x). Deploy applications, provision 6 database types (Postgres, MySQL, MariaDB, MongoDB, Redis, LibSQL), manage domains and Docker Compose stacks, AND debug failed deployments end-to-end — reads runtime logs of every container (including each container in a Docker Compose stack) over the API/MCP with tail/since/search, plus AI-powered log analysis (ai-analyzeLogs), Docker container and host introspection (server health, events, disk usage, images, volumes), Traefik diagnosis, and a guided recovery chain. Complete MCP/REST coverage: all 604 operations across 57 categories indexed with params — covers per-service Docker network management, vault (external secrets) providers, DNS providers, forward-auth SSO domain protection, SCIM provisioning, build concurrency, and the auto-generated @dokploy/cli (604 commands incl. read-logs). Uses the official @dokploy/mcp server (secret fields are redacted by default since 0.30.0) plus debugging-focused slash commands including /compose-logs.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (9)

- `ai-assist` — This skill should be used when the user wants AI-powered deployment debugging on Dokploy — wiring up an LLM provider (OpenAI, Anthropic, Gemini, Ollama, OpenRouter, etc.), summarising build logs with AI, or asking Dokploy for a next-step suggestion. Triggers: "analyze my failed deploy with AI", "ai analyze logs dokploy", "set up dokploy ai", "configure ai provider in dokploy", "why is dokploy not suggesting fixes", "dokploy ai-analyzeLogs", "dokploy ai-suggest".
- `api-reference` — This skill should be used when making direct HTTP/curl calls to the Dokploy API, looking up endpoint parameters, or building integrations that bypass the MCP server. Triggers: "dokploy API", "curl dokploy", "REST endpoint", "HTTP request to dokploy".
- `cli-recipes` — This skill should be used when running Dokploy operations from the terminal with the @dokploy/cli — authenticating, creating projects/apps, deploying, managing environment variables, provisioning databases, or reading logs via command line. Triggers: "dokploy cli", "dokploy command", "dokploy auth", "dokploy application deploy", "dokploy read-logs from terminal", "deploy dokploy from terminal".
- `debug-deploy` — End-to-end recovery of a failed or misbehaving Dokploy deployment, covering failed or errored builds, deployments stuck in running or queued, a redeploy marked done while the old version is still served, crash-looping containers, 502 and 504 after a deploy, safe rollback, and verifying the fix. Use it for any Dokploy deploy that is not working, in any language. For one known symptom use troubleshoot; for reading logs only use read-logs.
- `examples` — This skill should be used when learning how to deploy apps, provision databases, set up Docker Compose stacks, or debug a failed deployment on Dokploy. Provides end-to-end workflow walkthroughs. Triggers: "dokploy example", "how to deploy on dokploy", "dokploy tutorial", "dokploy walkthrough", "show me how to use dokploy", "dokploy debug example".
- `mcp-patterns` — This skill should be used when deploying applications, managing projects, provisioning databases, configuring domains, working with Docker Compose, or performing any Dokploy operation via MCP tools. Triggers: "deploy app", "create project", "add domain", "provision database", "dokploy compose", "manage dokploy".
- `read-logs` — This skill should be used whenever the user wants to read, tail, stream, or search Dokploy logs — application runtime logs, Docker Compose stack logs (every container), database logs, or deployment build logs — and especially to diagnose why something failed. Triggers: "read the logs", "show me the dokploy logs", "tail the logs", "compose logs", "all containers' logs", "container logs", "why is my app crashing", "why did my deploy fail — check the logs", "grep the logs for an error", "runtime logs", "build logs". Use it instead of telling the user logs aren't available over the API — since Dokploy v0.29.0 they are.
- `setup` — This skill should be used when verifying Dokploy MCP connection, CLI installation, and API access. Use when user says "set up dokploy", "verify dokploy connection", "check dokploy", "test dokploy access", or enables the dokploy-dev plugin for the first time.
- `troubleshoot` — Symptom-to-cause lookup for an app, domain, database or proxy on Dokploy - a domain that does not open or resolve, an SSL certificate error on a new domain, 502 or 404 from Traefik while the container runs (Traefik dashboard), connection refused between containers (internal hostname), a known deploy or compose error such as a registry pull or port conflict, Dokploy MCP or API errors such as missing tools or 401. Not for a full failed-deploy walkthrough (debug-deploy) or reading logs (read-logs).

## Not carried over

- 1 agent(s) — Devin plugins do not support agents
- 14 command(s) — Devin plugins do not support commands
- MCP servers — Devin plugins do not support MCP server declarations

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/dokploy-dev
