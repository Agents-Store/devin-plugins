---
name: codemap-diagram
description: >
  This skill should be used when the user asks to "draw a diagram", "visualize architecture", "show me the database schema",
  "create an ERD", "sequence diagram", "flow diagram", "dependency graph", "architecture diagram",
  "C4 diagram", or needs any visual representation of code structure, data flow, or system architecture.
  All diagrams are generated as native mxGraph XML and rendered via drawio-mcp. Also triggers when
  a code explanation would benefit from a visual aid.
---

# Diagram Generation via drawio-mcp

## Step 0: Execution Mode (MANDATORY)

Before doing ANY work, ask the user:

> "Want me to delegate this to the **diagrammer** agent (specialized diagram generation), or proceed inline in this chat?"

- If user chooses agent → launch the **diagrammer** agent with the diagram type, scope, and context. STOP here — do not continue with the steps below.
- If user chooses inline → proceed with the methodology below.
- If user doesn't respond clearly → default to agent.

---

**CRITICAL RULES:**
- **ALL diagrams MUST be native mxGraph XML saved as `.drawio` files.** Never generate Mermaid (`.mmd`), PlantUML, or text-based diagrams — this is a hard requirement, not a preference.
- If drawio-mcp is unavailable, report the error. Do NOT fall back to any other format.

Generate all diagrams as native mxGraph XML. Save as `.drawio` files and render via drawio-mcp `create_diagram` tool.

Available drawio-mcp tools: `create_diagram` (render XML), `search_shape` (find shapes).

## Diagram Type Selection

Use this decision tree to choose the right diagram type:

| Question | Diagram Type |
|----------|-------------|
| Overview of the entire system? | **C4 Container** — boxes for each service/component, arrows for communication |
| How a user action flows through the system? | **Flowchart** — steps, decisions, outcomes |
| How an API request moves between components? | **Sequence** — lifelines with arrows showing call order |
| What tables exist and how they relate? | **ERD** — tables with columns, FK relationships |
| Which modules depend on which? | **Dependency Graph** — directed graph of imports/calls |
| How components within one service connect? | **C4 Component** — internal structure of one container |

See `${CLAUDE_PLUGIN_ROOT}/skills/codemap-diagram/references/diagram-types.md` for detailed guidance on each type.

## Generation Process

For every diagram, follow these steps:

### Step 1: Analyze the Code
- Read relevant source files (models, routes, configs, imports)
- Identify the entities/components to include
- Determine relationships/connections between them
- Decide what to include and what to omit (keep diagrams focused)

### Step 2: Generate mxGraph XML
- Use templates from `${CLAUDE_PLUGIN_ROOT}/skills/codemap-diagram/references/mxgraph-templates.md`
- Apply color coding from `${CLAUDE_PLUGIN_ROOT}/skills/codemap-diagram/references/color-legend.md`
- Follow naming rules: use actual names from code, not generic labels
- Keep diagrams readable: max 15 nodes per diagram, split if more

### Step 3: Save as .drawio File
- Save to `docs/codemap/diagrams/{type}-{scope}.drawio`
- Create `docs/codemap/diagrams/` directory if it doesn't exist
- File naming: `architecture.drawio`, `erd.drawio`, `flow-login.drawio`, `sequence-create-deal.drawio`, `deps-routes.drawio`

### Step 4: Render via drawio-mcp
- Call the `create_diagram` MCP tool with the generated XML
- Present the interactive URL to the user
- If drawio-mcp is unavailable, report the error — do NOT fall back to Mermaid or text diagrams

### Step 5: Report to User
- Show the file path where `.drawio` was saved
- Show the interactive preview URL from drawio-mcp
- Brief description of what the diagram shows

## mxGraph XML Rules

- Always wrap in `<mxGraphModel>` root element
- Use `<root>` with cell id="0" (root) and cell id="1" (default parent)
- Node cells: `vertex="1"` with `<mxGeometry>` for position/size
- Edge cells: `edge="1"` with `source` and `target` attributes
- NO XML comments (`<!-- -->`) — drawio-mcp forbids them
- Use `style` attribute for colors, shapes, fonts
- Position nodes with adequate spacing (min 40px gap between nodes)

## Color Legend

Apply consistent colors across all diagrams:

| Layer | Fill Color | Hex | When to use |
|-------|-----------|-----|-------------|
| Data | Light Blue | `#dae8fc` | Models, database tables, migrations, ORM |
| Logic | Light Green | `#d5e8d4` | Routes, services, business logic, controllers |
| Interface | Light Yellow | `#fff2cc` | Templates, static files, API endpoints, forms |
| External | Light Red | `#f8cecc` | Third-party APIs, MCP servers, external services |
| Auth | Light Purple | `#e1d5e7` | Authentication, authorization, security components |
| Infra | Light Gray | `#f5f5f5` | Docker, config files, CI/CD, environment |

## Diagram Quality Rules

- **Use real names from code** — not "Service A" but "deals_bp" or "User model"
- **Show direction** — arrows indicate data flow or dependency direction
- **Include cardinality on ERD** — 1:N, N:M relationships marked
- **Label edges** — "imports", "calls", "FK: user_id", "HTTP POST"
- **Keep it focused** — one diagram per concept, don't mix architecture with DB schema
- **Add a title** — every diagram has a text label at top describing what it shows

## Error Handling

- **drawio-mcp unavailable** → inform the user, suggest retry. Do NOT fall back to Mermaid.
- **File path doesn't exist** → ask the user to verify the path
- **Too many entities (>15 nodes)** → split into multiple diagrams, explain the split
- **ORM not detected** → ask the user to specify the ORM type or point to model files