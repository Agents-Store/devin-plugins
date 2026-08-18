# Diagram Types Guide

## 1. C4 Container (Architecture Overview)

**When**: Showing the entire system — what services exist and how they communicate.

**Include**:
- Each deployable unit as a box (web app, database, external API, queue)
- Communication arrows with protocol labels (HTTP, SQL, WebSocket)
- User/actor boxes at the top
- System boundary box grouping internal components

**Omit**:
- Internal file structure of each component
- Individual routes or functions
- Configuration details

**Style**:
- Rounded rectangles for internal components
- Dashed border for system boundary
- Cloud shape for external services
- Person shape for users/actors

**Example scope**: "Show me the architecture of this app" → web server, database, external APIs, background workers

---

## 2. Flowchart (User/Feature Flow)

**When**: Showing step-by-step progression of a user action or feature.

**Include**:
- Start/end nodes (rounded rectangles)
- Action steps (rectangles)
- Decision points (diamonds) with Yes/No branches
- Key data transformations at each step

**Omit**:
- Error handling paths (unless specifically asked)
- Logging/monitoring steps
- Framework internals

**Style**:
- Top-to-bottom flow (preferred) or left-to-right for wide flows
- Green for happy path, red for error/rejection paths
- Diamond for decisions, rectangle for actions

**Example scope**: "Show the deal creation flow" → form → validation → save to DB → redirect

---

## 3. Sequence Diagram

**When**: Showing how a single request moves between components over time.

**Include**:
- Lifeline for each component (browser, route handler, service, database)
- Arrows with method/action labels in order
- Return values on dashed arrows
- Activation bars showing processing time

**Omit**:
- Parallel requests (unless essential)
- Middleware chains (group as single step)
- Logging calls

**Style**:
- Lifelines as vertical dashed lines with component box at top
- Solid arrows for calls, dashed arrows for returns
- Left-to-right ordering matches call depth

**Example scope**: "Show the login sequence" → browser → /login route → check password → create session → redirect

---

## 4. ERD (Entity-Relationship Diagram)

**When**: Showing database tables, their columns, and relationships.

**Include**:
- Every table as a box with: table name, column names, column types
- Primary keys marked (PK)
- Foreign keys marked (FK) with relationship lines
- Cardinality labels: 1, N, or M on relationship lines

**Omit**:
- Index definitions
- Migration history
- Default values (unless critical)

**Style**:
- Table boxes with header row (table name) and detail rows (columns)
- Solid lines for FK relationships
- Diamond labels for M:N junction tables
- Crow's foot notation for cardinality (or simple 1:N text labels)

**Example scope**: "Show the database schema" → all tables with relationships

---

## 5. Dependency Graph

**When**: Showing which modules/files import or depend on which.

**Include**:
- Each module/file as a node
- Import/dependency arrows pointing from dependent to dependency
- Group by layer or directory (cluster boxes)

**Omit**:
- Standard library imports
- Third-party package imports (unless critical)
- Circular dependency details (just mark the cycle)

**Style**:
- Directed arrows from importer to imported
- Cluster boxes for directories/layers
- Red arrows for circular dependencies
- Node size proportional to number of dependents (optional)

**Example scope**: "Show module dependencies in routes/" → which route files import which models/utilities

---

## 6. C4 Component (Internal Structure)

**When**: Showing the internal structure of a single service/container.

**Include**:
- Major classes/modules as components
- Internal communication patterns
- Data stores accessed
- External interfaces exposed

**Omit**:
- Individual functions (unless they are the key abstraction)
- Configuration/utility code
- Test files

**Style**:
- Component boxes inside a container boundary
- Interface symbols for exposed APIs
- Directed arrows for internal calls
- Database cylinder for data stores

**Example scope**: "Show the internal structure of the Flask app" → blueprints, models, extensions, templates