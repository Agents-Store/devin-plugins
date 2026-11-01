# codemap-dev (Devin plugin)

Code understanding plugin for developers. Helps onboard to unfamiliar projects through beginner-friendly code review, step-by-step explanations, visual diagrams (architecture, ERD, flows) via drawio-mcp, and frontend testing via Playwright MCP.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (5)

- `codemap-diagram` — This skill should be used when the user asks to "draw a diagram", "visualize architecture", "show me the database schema", "create an ERD", "sequence diagram", "flow diagram", "dependency graph", "architecture diagram", "C4 diagram", or needs any visual representation of code structure, data flow, or system architecture. All diagrams are generated as native mxGraph XML and rendered via drawio-mcp. Also triggers when a code explanation would benefit from a visual aid.

- `codemap-examples` — This skill should be used when the user asks for "codemap examples", "how to use codemap", "show me what codemap can do", "codemap walkthrough", or wants to see end-to-end usage scenarios for the codemap plugin.

- `codemap-explain` — Use when the user wants existing code explained as a learner - what a file, function or module does, how a request or data flows through the project, why it was built that way, or a tour of a codebase. Gives a structured step-by-step explanation (context, data flow, details, pitfalls) pitched at the user's level, preferred to an ad-hoc answer when the user is learning the code. Not for code review (codemap-review) or diagrams (codemap-diagram).
- `codemap-review` — Use when a developer asks for feedback on code they wrote - to review it, check their work, say what is wrong with it or what to improve - whether it is a pasted snippet, a file, a diff or a pull request. Returns findings ranked by severity, each with why it matters and a fix, plus what is done well, pitched for learners. Not for explaining how code works (codemap-explain) or testing a running app (frontend-test).
- `frontend-test` — This skill should be used when the user asks to "test the frontend", "check the UI", "explore the app in a browser", "test my admin panel", "find frontend bugs", "check for console errors", "verify the app works in a browser", "test user flows", "check the website", or wants a comprehensive frontend health report for a running application. Also triggers when the user says "open my app and test it", "browse my app", "check if the UI is working", or "give me a frontend report". Uses Playwright MCP to navigate, interact, and diagnose.


## Not carried over

- 4 agent(s) — Devin plugins do not support agents
- 7 command(s) — Devin plugins do not support commands
- MCP servers — Devin plugins do not support MCP server declarations

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/codemap-dev
