---
name: spec-authoring
description: This skill should be used when the user asks to "create macstack.json", "add macstack.json to this project", "init macstack", "generate macstack.json from scratch", "design a stack for…", "pick software and architecture for my need", "describe this existing project as a spec", "find plugins for this stack", "pick a prototype", "show a full macstack.json example", or describes a business need with or without an existing codebase. Owns macstack.json itself — the audit path, the design path, context discovery and the canonical examples.
---

# Authoring macstack.json

Two paths into the same file. **Audit** describes a project that already exists;
**design** builds one that does not. Both end at a spec that passes `lint`, and
neither invents a fact.

For a request spanning many domains or an ambiguous software choice, delegate to the
`macstack-architect` agent.

---

# Path A — audit an existing codebase

The file must describe reality, not aspiration: audit first, write second, ask the
user only what cannot be derived.

## A1 — Evidence, not guesses

Scan in this order and map findings to sections:

| Source | What it yields |
|---|---|
| `package.json` / `requirements.txt` / `pyproject.toml` / `composer.json` | `software[]` candidates |
| `docker-compose.yml` (services + images) | self-hosted `software[]` + `instances[]` |
| `.mcp.json` | `connections.mcp[]` — transports, `${VAR}` → `url_env` |
| `.env.example` / `.env` (key NAMES only, NEVER values) | `resources.accesses[]` |
| `.claude/settings.json` enabledPlugins | `context.plugins` |
| `.infisical.json`, `.dokploy.json`, `.plane.json` | `resources.bindings` |
| DB schemas, CMS collections, migrations | `entities[]` with attributes and master |
| `src/trigger/`, n8n exports, Flows | `workflows[]` + `triggers[]` |
| App Router pages, admin panels, bots | `interfaces[]` — `path` relative to the instance |
| README, CLAUDE.md, AGENTS.md, `docs/` | description, a goals/results draft |
| an existing `macstack/client/*.md` | goals, results and open questions already in the client's words |

**`.mcp.json` is a secret-scan surface.** A live project's file held a hardcoded
service token and a Figma API key. Any hardcoded credential found here is an open
question at high severity — rotate it and move it to `${VAR}` — not a note for later.

**Do not deep-`grep` the source tree to find entities.** In an iCloud-backed folder a
recursive grep hangs for minutes. Derive entities from schemas and generated types,
and put a timeout on any search you do run.

Layer classification: full-stack frameworks (nextjs, django) → logic + interface;
BaaS and headless CMS (directus, nocodb, supabase) → data; job runners (trigger-dev,
n8n, bullmq) → logic; Docker, CI, Terraform → infrastructure.

## A2 — Ask only the business gaps

The audit yields the technical half. Ask the rest in ONE compact message:

1. The project's **goals** — 1–3, each with a horizon.
2. The **results** it must produce, measurable, and the **problem** each one closes.
3. The **client** and **organization**; is there an organization root stack
   (→ `stacks.role: substack`)?
4. The **prototype** it was built from, if any.
5. The **language** the documents should be written in (`docs.language`).

## A3 — Write the draft

Write to `macstack/macstack.json` — the canonical location, never the bare root file
for a new project. Fill sections in the schema's order. Mark anything not confirmed by
code or by the user as `"status": "planned"`.

Every entity MUST get a `master`. If two stores exist and the master is unclear, that
is a question for the user, never a silent guess — a wrong master means data
corruption later.

Do NOT invent goals or results the user did not confirm. **A spec that lies is worse
than an incomplete one**, because the incomplete one is visibly incomplete.

---

# Path B — design from a business request

The order is NON-NEGOTIABLE: money first, software last. Never start from "which
technologies" — start from "which result makes money".

## B0 — The interview, when there is nothing to read

An empty folder has no evidence, so everything comes from the owner. Six questions, in
this order, from the Result-First framework. **The order is the method, not a style
choice**: the value chain is read right to left — Goal ← Result ← Process ← Task ←
Workflow ← Software — so an answer to question 4 given before question 1 is an answer to
a question nobody has asked yet.

| # | Ask | Produces |
|---|---|---|
| 1 | Which results are needed, in money? | `goals[]`, `results[]` |
| 2 | Which processes produce those results? | `processes[]` |
| 3 | How exactly is each one done? | `workflows[]`, `triggers[]` |
| 4 | What is it done with? | `software[]`, `connections`, `entities[]` |
| 5 | Who confirms? Where must a person decide? | human gates in `processes[].tasks` |
| 6 | What does the agent need to know to do it alone? | `agents[]`, `context` |

**Ask each one through AskUserQuestion, never as plain text in a reply.** Two to four
concrete options, the recommendation first and labelled so. A free-text question at this
stage gets a free-text answer, and a spec assembled from prose is a spec assembled from
guesses.

Three rules that decide whether this produces a usable spec or a plausible one:

- **Never ask what you can derive.** If question 2 is already answered by the answer to
  question 1, say what you derived and ask for confirmation instead. Asking the owner to
  restate what they just said is how an interview turns into an interrogation and stops
  getting real answers.
- **Do not proceed past an unanswered question.** "I want a bot" is not a result. The
  result question gets asked out loud — *what measurable result must the bot produce, and
  what is it worth per month?* — and the interview stops there until it is answered.
  Everything downstream is derived from that number.
- **Write down what was not asked.** Anything the owner deferred goes into
  `lifecycle.open_questions` as a pointer and into `OPEN-QUESTIONS.md` as wording, on
  the day it was deferred. An unrecorded gap becomes an invented fact within a week.

Money before software is not a preference here. Start from "which technologies" and you
get a stack looking for a use; start from "which result makes money" and the stack is
determined by the answer.

## B1 — Goals and results

**goals[]** — 1–3 business goals with a horizon and a metric. **results[]** —
measurable assets that realize them, each with a `class`
(revenue_asset · client_revenue · pipeline_asset · cost_saving), a `metric`
{unit, target, cadence}, the `problem` it closes and a `goal` ref. Phrase results as
business outcomes, not technologies.

A vague need — "I want a bot" — gets the result question asked out loud: *what
measurable result must the bot produce, and what is it worth per month?*

## B2 — Processes → triggers → workflows

**processes[]** — which processes produce the results; `type`, `automation_mode`
(workflow · agent · hybrid), and tasks with human gates wherever a person is
mandatory. **triggers[]** — a separate collection: what starts the automation, of
which `type`, from which `source`, and in which software it lives. **workflows[]** —
deterministic implementations: engine, trigger refs, invocation, named
`[Domain] - [Action] - [Trigger]`.

## B3 — Software selection

In priority order:

1. **Prototype first.** A prototype repo that already covers the need beats assembly.
   Set `prototype` and inherit its software. Ask the user where their prototypes live
   — never guess an org, and skip this step outright when there is no answer.
2. **Open source first, agentic ready first.** Prefer MCP + API + CLI (rating full or
   good). A stack without MCP is just software.
3. **Proven bundles.** Universal workspace = postgresql + nocodb + n8n (+trigger-dev);
   web app = directus + nextjs (+trigger-dev); headless agents = postgresql + qdrant +
   n8n/trigger-dev; BPMS = nocobase.
4. **Custom code only for the unique** — `type: custom`, category `custom-scripts`.

For every software, **copy its passport from the registry first**
(`raw.githubusercontent.com/macstacks/registry/main/software/<slug>.json`) — category,
type, form, license, layers and agentic rating arrive already consistent — then add the
stack-specific half: `role`, `value`, `hosting`, `instances[]`, `cost`. No passport →
fill from the schema enums by hand and propose the new passport as a registry PR.

## B4 — The rest

`entities[]` with a mandatory master (the client's external systems are software with
`hosting: external`) · `interfaces[]` with relative paths, notifications as
`type: channel` · `connections` · `agents` (a worker at minimum; an orchestrator when a
messenger frontend is needed) · `context.plugins` from discovery · `resources.accesses`
with every env key and its `required` flag · `profile` · `commercial` with the cost of
ownership, which is where the open-source-first economics becomes explicit ·
`docs` with `language` and `files` · `lifecycle` at `stage: define`, with
`open_questions` and `needs_from_client` in **pointer form from day one** — the wording
lives in `OPEN-QUESTIONS.md`, never in the JSON.

## B5 — Validate and present

Run `lint`. Present result-first: goals and results before processes, processes before
the stack. **Get the results confirmed before any scaffolding** — the system designs
itself from the result, and changing the result after assembly is expensive.

---

# Discovery — plugins, prototypes and reusable blocks

## The registry — reusable blocks

Before writing any `software[]`, `entities[]` or `triggers[]` entry by hand, check
`github.com/macstacks/registry`. Copying a maintained block beats retyping: fewer
taxonomy mistakes, ratings already consistent.

```bash
curl -fsSL https://raw.githubusercontent.com/macstacks/registry/main/software/directus.json
curl -fsSL https://raw.githubusercontent.com/macstacks/registry/main/entities/client.json
gh api repos/macstacks/registry/contents/software -q '.[].name'
```

## Agents Store plugins

```bash
curl -s https://raw.githubusercontent.com/agents-store/claude-plugins/main/.claude-plugin/marketplace.json \
  | jq -r '.plugins[] | "\(.name)\t\(.description)"'
```

Derive names from `software[]`: `{tool}-dev` · `{tool}-ops` · `{tool}-provision`, plus a
`stack-{name}-{process}` bundle for the layer combination — that one carries `.mcp.json`,
`.env.example` and the integration skills.

Declare what each plugin **covers**, not just that it exists. A bare slug makes the
plugin list decoration; `covers[]` makes it a routing table an agent can use to pick
which plugin to open instead of loading all of them.

Plugin not found → a `§B` item in `OPEN-QUESTIONS.md` with the trigger that makes the
gap urgent, and a pointer from `lifecycle.open_questions`. **Never invent a name inside
`context.plugins`** — a plugin that does not exist routes an agent into nothing.

## Prototypes

A prototype is a repo the user already owns; this plugin ships no catalogue of them
and must not invent one. Ask which org or folder holds them, then list it:

```bash
gh api "orgs/<org>/repos?per_page=100" -q '.[] | .name + "\t" + (.description // "")'
```

No answer means no prototype step — say so and assemble from the bundles instead. A
guessed org lists nothing and reads as "no prototype exists", which is a different and
wrong conclusion.

Where the convention holds: `project-template` is the universal base; `project-{stack}`
a stack template; `demo-{stack}` a demo with seed data; `{client}-{stack}` a real
assembly. Prefer `project-*` over a client repo. Set
`"prototype": "github:<owner>/<repo>"` — a local absolute path works too.

Check whether the prototype has its own `macstack.json` and inherit by merge-by-id. If
it only has a legacy `stack.json`, it is a scaffold source and nothing more — open a
`§B` item saying so.

---

# Wiring up

1. `lint` — fix every error.
2. `documents` — create and seed `macstack/`. An existing populated `docs/` goes
   through migration mode rather than being seeded fresh beside it.
3. The `## Stack Specification` block into **both** `CLAUDE.md` and `AGENTS.md`.
4. Offer `infisical-env` if accesses exist, then `best-practices`.

---

# Canonical examples

Full files live in `github.com/macstacks/macstack/tree/main/examples`:

- **nova-root** — an organization's root workspace: the substacks registry, the
  openclaw → claude-code agent hierarchy, the organization's master `client` entity.
- **nova-website** — an application substack: a cross-stack lead master
  (`master: "nova-root:postgresql"`), five trigger types, a managed agent invoked via
  workflow.
- **nova-support-bot** — a headless agents stack: no prototype, RAG with a Postgres
  master and a Qdrant cache.
- **meg-bpms** — a client BPMS: field-level ACL, status fields driving processes, an
  external master.

## Scenarios

**An existing project with no spec** — `/macstack-dev:start` → audit → questions →
lint → documents → the spec block in CLAUDE.md and AGENTS.md → infisical-env →
best-practices.

**A new stack from scratch** — `/macstack-dev:start "<business request>"` → design →
discovery → lint → **the owner confirms the results** → scaffold in the mandatory
source order → infisical-env → best-practices → lint → commit.

**An organization** — design the root first (`stacks.role: root`), then each substack
with a `root` ref and cross-stack masters (`"<root-id>:postgresql"`); scaffold each and
register it in the root's `substacks[]`.

**Growing a live stack** — add the software, its instances, its MCP connection, its env
keys, its workflows and triggers → lint → scaffold (idempotent, it grows) → add the key
in Infisical → commit the spec **in the same commit** as the code.

**The client drops a PDF** — that is `/macstack-dev:intake`, not this skill.
