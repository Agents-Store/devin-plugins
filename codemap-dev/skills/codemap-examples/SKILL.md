---
name: codemap-examples
description: >
  This skill should be used when the user asks for "codemap examples", "how to use codemap",
  "show me what codemap can do", "codemap walkthrough", or wants to see end-to-end usage
  scenarios for the codemap plugin.
disable-model-invocation: true
---

# Codemap Usage Examples

End-to-end scenarios showing how codemap-dev commands and skills work together.

## Scenario 1: Onboarding to a Flask Project

A junior developer joins a team with an existing Flask + SQLAlchemy application.

### Step 1: Full onboarding

```
/codemap:onboard
```

**What happens:**
1. Scans the project — finds Flask app factory, blueprints, SQLAlchemy models
2. Generates `docs/codemap/ONBOARDING.md` with stack summary, directory roles, how to run locally
3. Generates `docs/codemap/ARCHITECTURE.md` with layer descriptions
4. Creates 3 diagrams:
   - `docs/codemap/diagrams/architecture.drawio` — C4 container diagram (Flask app, PostgreSQL, external APIs)
   - `docs/codemap/diagrams/main-flow.drawio` — primary user flow as a flowchart
   - `docs/codemap/diagrams/erd.drawio` — all database tables with relationships

### Step 2: Understand a specific module

```
/codemap:explain routes/deals.py
```

**What happens:**
1. Applies 4-layer model: Context (what the file does) → Data Flow (request lifecycle) → Details (each route handler) → Pitfalls (common mistakes)
2. If 3+ components interact, auto-generates a mini-diagram

### Step 3: Review your first PR

```
/codemap:review #15
```

**What happens:**
1. Fetches PR diff via `gh pr diff 15`
2. Reviews across 5 dimensions: Security, Correctness, Readability, Patterns, Beginner Pitfalls
3. Each finding explains **why** it matters, not just what to fix

## Scenario 2: Understanding a Database Schema

A developer needs to understand the data model before making changes.

### Step 1: Generate ERD and documentation

```
/codemap:db
```

**What happens:**
1. Auto-detects ORM (SQLAlchemy, Prisma, TypeORM, Django, raw SQL migrations)
2. Parses all model definitions — tables, columns, types, foreign keys, relationships
3. Reviews schema quality (missing indexes, naming inconsistencies, missing constraints)
4. Generates `docs/codemap/diagrams/erd.drawio` with color-coded tables
5. Generates `docs/codemap/DB.md` with table details and relationship descriptions

### Step 2: Explore a specific relationship

```
/codemap:explain models/deal.py
```

**What happens:**
1. Explains the Deal model — what it represents, its columns, relationships to other models
2. Shows data flow: how deals are created, updated, queried
3. Notes pitfalls: cascade deletes, missing constraints, N+1 query risks

## Scenario 3: Visualizing Architecture for a Team Presentation

A developer needs to create architecture diagrams for a team knowledge-sharing session.

### Step 1: System overview

```
/codemap:diagram architecture
```

**What happens:**
1. Scans root configs, entry points, all top-level directories
2. Generates C4 container diagram showing all services, databases, external APIs
3. Saves to `docs/codemap/diagrams/architecture.drawio` and opens interactive preview

### Step 2: Specific feature flow

```
/codemap:diagram sequence POST /api/deals
```

**What happens:**
1. Traces the request from route handler through service layer to database
2. Generates sequence diagram with lifelines for each component
3. Labels arrows with data being passed at each step

### Step 3: Discover all user flows

```
/codemap:flows
```

**What happens:**
1. Finds all route definitions and groups them into logical flows
2. Generates a flowchart for each major flow (auth, CRUD, key features)
3. Writes `docs/codemap/FLOWS.md` with descriptions and diagram links
