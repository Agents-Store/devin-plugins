# Explanation Patterns Reference

Common analogies, framework-specific tips, and anti-patterns for code explanations.

## Analogies for Common Patterns

Use these when the user is unfamiliar with a concept. Pick the analogy that fits their background.

### Architectural Patterns

| Pattern | Analogy | When to use |
|---------|---------|-------------|
| **MVC** | Restaurant: Model = kitchen (data/recipes), View = dining room (what guest sees), Controller = waiter (takes orders, delivers food) | First-time web devs |
| **Middleware** | Airport security checkpoints — every request passes through each check in order before reaching the gate | Explaining Express/Koa/Django middleware |
| **Event-driven** | Pub/sub = radio station: publishers broadcast, subscribers tune in to channels they care about | Explaining message queues, EventEmitter, webhooks |
| **ORM** | Translator between your code's language (objects) and the database's language (SQL tables) | When user asks "why not just write SQL?" |
| **Dependency injection** | Power outlets: your device doesn't generate electricity, it accepts whatever power source is plugged in | Explaining DI containers, testing mocks |
| **Decorator pattern** | Gift wrapping: the gift (original function) stays the same, each wrapper adds something (logging, auth, caching) | Python decorators, TypeScript decorators |
| **State machine** | Vending machine: insert coin → select item → dispense. Each action only works in certain states | Explaining auth flows, order status, workflows |
| **Microservices** | Department store vs. strip mall: monolith = one building, many departments; microservices = separate shops that talk to each other | Architecture overview for monolith-to-micro migrations |

### Data Patterns

| Pattern | Analogy | When to use |
|---------|---------|-------------|
| **Cache** | Sticky note on your monitor with frequently used phone numbers — faster than looking up the phone book every time | Redis, memoization, HTTP caching |
| **Queue** | Line at a coffee shop: first in, first out. The barista (worker) processes one order at a time | Message queues, job processing, Celery/Bull |
| **Database index** | Book index at the back: instead of reading every page to find "authentication", jump to page 47 | Explaining slow queries, indexing strategy |
| **Migration** | Moving to a new apartment: you plan the move (migration file), execute it (migrate up), and can undo it (migrate down) | Database migrations, schema changes |
| **Transaction** | Bank transfer: either both accounts update or neither does. No halfway state | Explaining database transactions, ACID |
| **Connection pool** | Hotel room keys: the hotel (pool) has 10 keys (connections). Guests check out keys, use them, return them. If all 10 are taken, you wait | Database connection pools |

### Auth Patterns

| Pattern | Analogy | When to use |
|---------|---------|-------------|
| **JWT** | Concert wristband: proves you paid (authenticated), shows your tier (claims/roles), has an expiry time, can be verified without calling the box office | Token-based auth, stateless sessions |
| **OAuth** | Valet parking: you give the valet a special key (token) that can only drive (specific scope), not open your trunk (full access) | OAuth flows, third-party integrations |
| **Session** | Coat check ticket: you give the server a small ticket (session ID), they look up your full coat (session data) in the back | Server-side sessions, cookie-based auth |
| **RBAC** | Movie theater: your ticket (role) determines which screens (resources) you can enter | Role-based access control |

## Framework-Specific Explanation Tips

When explaining code in a specific framework, lead with these framework conventions to avoid confusion.

### React / Next.js
- **Lead with:** component tree mental model — parent passes data down (props), child signals up (callbacks)
- **Common confusion:** "Why does the component re-render?" → explain React's reconciliation: state change → re-render → diff → DOM update
- **Define early:** hooks, props, state, effects, JSX (it's not HTML — it compiles to function calls)
- **Key gotcha to highlight:** useEffect dependency arrays — missing deps = stale closures, extra deps = infinite loops

### Express / Koa / Fastify
- **Lead with:** request lifecycle — `request → middleware chain → route handler → response`
- **Common confusion:** middleware order matters — auth before route handlers, error handler last
- **Define early:** req/res objects, next(), middleware, router
- **Key gotcha:** async error handling — Express doesn't catch async errors by default (need express-async-errors or try/catch)

### Flask / Django
- **Lead with:** request-response cycle — `URL → view/route → template/JSON → response`
- **Flask:** explain blueprints as "mini-apps you plug together"
- **Django:** explain the MTV pattern (Model-Template-View, where View = controller in MVC)
- **Define early:** decorators (@app.route), context (g, request), ORM model
- **Key gotcha:** circular imports in Flask, Django's implicit magic (auto-discovery, signal handlers)

### Spring Boot / Java
- **Lead with:** annotation-driven configuration — `@RestController`, `@Service`, `@Repository` define the layer
- **Common confusion:** dependency injection via constructor — Spring creates and wires objects automatically
- **Define early:** beans, annotations, application context, profiles
- **Key gotcha:** the "magic" of auto-configuration — things work until they don't, and debugging requires understanding classpath scanning

### Go
- **Lead with:** explicit over implicit — no hidden magic, errors are values, interfaces are implicit
- **Common confusion:** goroutines vs threads, channels vs mutexes
- **Define early:** structs (not classes), interfaces (duck typing), error handling (if err != nil)
- **Key gotcha:** goroutine leaks, nil pointer on uninitialized interface, defer execution order (LIFO)

## Anti-Patterns in Explanations

Things to AVOID when explaining code:

| Anti-pattern | Why it's bad | Do this instead |
|-------------|-------------|-----------------|
| **"It's simple"** | Dismisses the learner's experience | "Here's how it works:" (neutral) |
| **Abstract-only** | "The service layer mediates between controllers and repositories" — meaningless without concrete flow | Show actual data: "When you POST /login with {email, password}, the AuthService calls UserRepo.findByEmail()..." |
| **Jargon dump** | "The HOC wraps the connected component with the Redux store's dispatch mapper" | Define each term on first use, build up incrementally |
| **Explaining the obvious** | "The import statement imports the module" | Skip trivial code, focus on logic and decisions |
| **Wall of text** | 10 paragraphs with no structure | Use the 4-layer model, headers, code traces |
| **Code-only** | Pasting code with "see here" | Always explain the WHY before showing the WHAT |
| **Top-down dump** | Starting from line 1 and going sequentially | Start with Context (what problem), then trace the interesting path |
| **Missing "why"** | "This uses bcrypt" — but why not SHA256? | "This uses bcrypt because it's intentionally slow — making brute-force attacks impractical, unlike fast hashes like SHA256" |
