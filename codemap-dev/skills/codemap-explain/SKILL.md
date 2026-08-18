---
name: codemap-explain
description: >
  This skill should be used when the user asks to "explain this code", "what does this file do", "how does this work",
  "walk me through this function", "explain this module", "what is this for",
  "help me understand this", "break down this code for me", "give me a tour of this codebase",
  or needs a beginner-friendly step-by-step explanation of code, files, functions, or modules.
  Also triggers when the user points at code and asks "why" or "how" questions, or says
  "I don't understand this", "what's happening here", "trace this flow for me".
---

# Code Explanation for Beginners

## Step 0: Execution Mode (MANDATORY)

Before doing ANY work, ask the user:

> "Want me to delegate this to the **architect-explainer** agent (guided explanation with diagrams), or proceed inline in this chat?"

- If user chooses agent → launch the **architect-explainer** agent with the target and context. STOP here — do not continue with the steps below.
- If user chooses inline → proceed with the methodology below.
- If user doesn't respond clearly → default to agent.

---

## Step 1: Clarify Scope and Depth (MANDATORY)

Before explaining anything, ask the user these questions (skip any already answered in their request):

1. **What to explain?** — specific file, function, module/directory, or full project?
2. **How deep?**
   - **Overview** — high-level summary, architecture, purpose (2-3 minutes read)
   - **Moderate** — key logic explained, data flows traced, patterns identified (5-7 minutes read)
   - **Deep dive** — line-by-line for key logic, edge cases, framework internals (10+ minutes read)
3. **What aspect interests you most?**
   - How it works (mechanics)
   - Why it's built this way (design decisions)
   - How data flows through it (inputs → outputs)
   - How to modify or extend it (practical next steps)
4. **Your experience level with this stack?** — helps calibrate terminology and analogies

If the user gives a vague request like "explain this", default to: the file/module they're looking at, moderate depth, "how it works" aspect. Confirm before proceeding.

<example>
User: "Explain the auth system"
Agent: "I'll explain the auth system. A few quick questions:
- Should I cover the whole auth module or a specific file (e.g., login handler, middleware)?
- Do you want a high-level overview or a deep dive into the internals?
- Are you more interested in how it works, or how to modify it?
- How familiar are you with [detected framework, e.g., Express/Passport]?"
</example>

---

## Step 2: Read and Analyze Code (before explaining)

Follow this reading strategy based on scope:

### For a function
1. Read the function and its docstring/comments
2. Read the file it's in — understand surrounding context
3. Grep for callers: who calls this function and with what arguments?
4. Check imports: what dependencies does it use?

### For a file
1. Read the full file
2. Read the project's entry point or config to understand where this file fits
3. Check imports to map dependencies
4. Grep for references to this file from other files

### For a module/directory
1. List all files in the directory
2. Read the module's index/init file if it exists
3. Read 2-3 key files (entry points, models, main logic)
4. Read the project root (package.json, requirements.txt, README) for stack context
5. Map internal file dependencies via imports

### For full project
1. Read root files: README, CLAUDE.md, main config (package.json / requirements.txt / go.mod)
2. List top-level directories and identify their roles
3. Find entry points: main app file, route definitions, CLI commands
4. Trace one complete request path through the system

After reading, identify: **the main abstraction** (what concept does this code represent?), **the key decision** (what's the most important choice made here?), and **the surprise** (what would a newcomer not expect?).

---

## Step 3: Explain Using the 4-Layer Model

Adjust depth based on the user's answer in Step 1. Skip or compress layers that don't match the requested aspect.

### Layer 1: Context (always start here)

Answer: **What problem does this solve? Where does it fit in the project?**

- One sentence: what this code does in plain language
- Where it sits in the architecture (data layer? route handler? utility?)
- Who calls it / what triggers it (incoming request, cron job, user action, another module)
- What would break if this didn't exist

For beginners, use an analogy: relate the code's role to something familiar. See `${CLAUDE_PLUGIN_ROOT}/skills/codemap-explain/references/explanation-patterns.md` for common analogies per pattern.

### Layer 2: Data Flow

Answer: **What goes in, what comes out, what happens in between?**

- Inputs: what data this code receives (parameters, request data, database queries)
- Processing: the main transformations, validations, or decisions
- Outputs: what it returns or produces (response, database write, side effect)
- Dependencies: what external services or modules it relies on

Show concrete values flowing through — not abstract descriptions. Use a mini-trace:

```
Form data {email, password}
  → validate(email) → check DB for user
  → bcrypt.compare(password, hash)
  → if match: create session → redirect /dashboard
  → if no match: flash error → redirect /login
```

### Layer 3: Details

Answer: **How does each part work?**

- Walk through key sections of the code (not every line — focus on logic, not boilerplate)
- Explain non-obvious patterns or framework-specific conventions
- Define technical terms on first use: "Blueprint (Flask's way of organizing related routes into a module)"
- Show connections: "this function is called by X on line Y in file Z"

Adjust depth to user's request:
- **Overview** → skip this layer or give 1-2 sentences per section
- **Moderate** → explain key functions/blocks, skip boilerplate
- **Deep dive** → line-by-line for important logic, annotate decisions

### Layer 4: Pitfalls

Answer: **What can go wrong? What's non-obvious?**

- Edge cases the code handles (or doesn't)
- Common mistakes when modifying this code
- Framework gotchas relevant to this code
- Performance considerations if applicable
- Security implications if applicable

Only include pitfalls proportional to depth requested. Overview = 1-2 biggest risks. Deep dive = comprehensive.

---

## Step 4: Verify Your Explanation

Before presenting the explanation, cross-check:

1. **Every claim references real code** — don't say "this function calls X" without confirming it in the source
2. **Names match the code** — use actual variable names, function names, file paths from the codebase
3. **Flow matches reality** — if you described a data flow, trace it one more time in the code to confirm
4. **No hallucinated features** — don't attribute behavior that isn't in the code

If you discover something contradicts your initial analysis during verification, correct the explanation before presenting it.

---

## Step 5: Suggest Next Steps

End every explanation with actionable next steps tailored to the user's interest:

- **"How it works"** → "Want me to explain [related module] next?" or "Want a diagram of this flow?"
- **"Design decisions"** → "Want me to review alternative approaches?" or "Want to understand the tradeoffs?"
- **"Data flow"** → "Want me to trace [another endpoint/feature]?" or "Want an ERD of the data models?"
- **"How to modify"** → "Want me to walk through adding [specific feature]?" or "Want a review of your changes after?"

Always suggest 2-3 specific next steps, not generic ones.

---

## Output Format

Structure explanations consistently:

```
## [Target Name] — [one-line summary]

**Scope:** [function / file / module] · **Depth:** [overview / moderate / deep dive]
**Stack:** [detected framework, language, key libraries]

### Context
[Layer 1 content — 1-3 paragraphs depending on depth]

### Data Flow
[Layer 2 content — trace with concrete values, mini-diagram if helpful]

### How It Works
[Layer 3 content — adjusted to requested depth]

### Pitfalls
[Layer 4 content — proportional to depth]

### Next Steps
- [Suggestion 1]
- [Suggestion 2]
- [Suggestion 3]
```

For **overview** depth: Context + Data Flow + Next Steps (skip Details and Pitfalls).
For **moderate** depth: all sections, Details compressed.
For **deep dive** depth: all sections expanded, line-by-line annotations in Details.

---

## Mini-Diagram Decision

Generate a mini-diagram (via `codemap-diagram` skill at `${CLAUDE_PLUGIN_ROOT}/skills/codemap-diagram/SKILL.md`) when:
- 3+ components interact in the explanation
- Data flows through multiple files/services
- The user is confused about how pieces connect
- A visual would save 200+ words of text

Do NOT generate a diagram for:
- Single-function explanations
- Simple CRUD with obvious flow
- When the user just wants a quick answer

---

## Scope-Specific Adjustments

### For a single function
- **Context:** 1-2 sentences — what it does, who calls it
- **Data Flow:** parameter → processing → return value trace with concrete values
- **Details:** line-by-line for key logic, skip boilerplate (imports, type declarations)
- **Pitfalls:** edge cases and error paths — what inputs break it?
- **Format:** inline explanation, no headers needed for overview depth

### For a file
- **Context:** file's role in the project, what module it belongs to
- **Data Flow:** list public API (exports, route handlers, model definitions) with one-line descriptions
- **Details:** explain each key function/class — skip helpers unless non-obvious
- **Pitfalls:** common modification mistakes, implicit dependencies
- **Format:** use headers per function/class for moderate+ depth

### For a module/directory
- **Context:** module's purpose, boundaries, what it owns
- **Data Flow:** file listing with one-line role descriptions, dependency map
- **Details:** key files explained in depth, others summarized
- **Pitfalls:** architectural decisions and their tradeoffs, coupling risks
- **Format:** start with file map, then drill into key files

### For full project
- **Context:** what the project does, who it's for, deployment model
- **Data Flow:** one complete request traced end-to-end
- **Details:** layer-by-layer architecture overview (routes → services → data)
- **Pitfalls:** key architectural decisions, tech debt, scaling concerns
- **Format:** start with architecture overview, then offer to drill into any layer

---

## Tone Rules

- **Define terms on first use** — "Blueprint (Flask's way of organizing related routes into a module)"
- **Use concrete examples** — show actual values flowing through, not abstract descriptions
- **Relate to familiar concepts** — see `${CLAUDE_PLUGIN_ROOT}/skills/codemap-explain/references/explanation-patterns.md` for analogies
- **Progressive complexity** — start simple, add nuance layer by layer
- **Honest about complexity** — "this part is genuinely tricky because..." is better than oversimplifying
- **Match the user's level** — use framework jargon only if user confirmed familiarity; otherwise define everything

Do NOT:
- Use filler phrases ("Let's dive in!", "Great question!")
- Explain obvious things (what a for-loop is, what imports do) unless user is a complete beginner
- Hedge excessively ("it seems like", "it appears to") — be direct about what the code does
- Skip to code without context — always start with Layer 1

---

## Error Handling

- **File not found** → ask the user to verify the path. Suggest: "Want me to search for similar filenames with Glob?"
- **Symbol not found** → grep broader patterns (partial name, related terms). Ask for clarification if still not found
- **Module too large (>20 files)** → explain top-level structure first, then ask: "Which part should I drill into?"
- **Minified/generated code** → warn the user this is generated code, offer to find the source instead
- **Binary/non-text files** → explain what the file type is and where it's likely configured or generated from
