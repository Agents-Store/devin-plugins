# plane-ops (Devin plugin)

Plane Agile Ops knowledge plugin. Full coverage of the Plane MCP surface: sprint planning, task decomposition, estimation, backlog management, velocity tracking, retrospectives, standups, intake triage, modules, epics, initiatives, milestones, roadmaps, dependencies, burndown, pages (sprint reports, retros, ADRs, runbooks, specs, meeting notes), labels, workflow states, work item types, custom properties, comments, links, work logs, relations, history, bulk edits, search, members, and assignment. Tool- and instance-agnostic: works with any Plane MCP server or connector via a bootstrap skill that discovers tools across naming conventions.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (17)

- `agile-fundamentals` — Single source of truth for Agile formulas, Definition of Ready, Definition of Done, MoSCoW priority mapping, WSJF scoring, capacity and velocity formulas, WIP limits, Fibonacci story points, and sprint buffer policy. Use whenever the user asks about story points, estimation, velocity, capacity, focus factor, WSJF, DoR/DoD, MoSCoW, Fibonacci, sprint buffer, or any Agile rule — and whenever any other plane-ops skill, command, or agent needs canonical Agile definitions. Do not duplicate these rules elsewhere — link here instead.
- `backlog-management` — Backlog management — MoSCoW prioritization, WSJF scoring, value-effort analysis, backlog health monitoring, grooming workflows. Use when prioritizing backlog, grooming items, or assessing backlog health.
- `connector-bootstrap` — MUST be consulted at the start of ANY Plane-related request before answering the user or declaring tools unavailable. Discovers Plane tools across any MCP server, connector, or instance naming convention (cowork mode, remote MCP, local MCP, self-hosted, cloud). Use when the user mentions sprint, backlog, work item, cycle, epic, module, milestone, initiative, project, issue, ticket, task, standup, retro, estimate, roadmap, board, Plane, or any work-management operation — even if Plane tools are not visible yet. Also use before saying "I don't have access to Plane tools" or "tool not available".
- `daily-standup` — Daily standup support — progress summary, blocker identification, team status updates, sprint progress tracking, async standup. Use when running daily standups, checking team progress, identifying blockers, or generating async standup reports.
- `epics-initiatives-milestones` — Long-horizon planning in Plane — epics, initiatives, and milestones. Use when the user wants to create an epic, group epics under an initiative, track a release milestone, build a roadmap, or report progress on a long-running goal that spans multiple sprints or modules. Clarifies the difference between the three and when to use which.
- `estimation` — Estimation — story points, Fibonacci scale, t-shirt sizing, relative estimation, planning poker facilitation. Use when estimating work items or running estimation sessions.
- `examples` — Tool call patterns, end-to-end workflow examples, and scenario references for Plane Agile workflows. Use when needing reference implementations, complete examples, or tool call patterns.
- `intake-triage` — Plane intake inbox — triage incoming requests, bug reports, and ideas before they enter the backlog. Use when the user wants to review the intake queue, accept or reject incoming items, convert intake items into work items, or set up a triage process. Covers daily/weekly triage rituals and routing rules.
- `labels-states-properties` — Design taxonomies for Plane projects — labels, workflow states, work item types, and custom properties. Use when the user asks how to organize labels, design a state machine, set up custom fields, configure work item types, decide between label/property/type, or audit a noisy taxonomy. Covers naming conventions, recommended sets, and the difference between the four metadata mechanisms.
- `modules` — Plane modules — feature and workstream grouping that cuts across sprints. Use when the user wants to group related work items by feature area, track progress of a larger feature over multiple sprints, create or manage modules, or ask about workstream progress. Modules complement cycles (time-boxed) by organizing work around outcomes (scope-boxed).
- `pages-publishing` — Create and publish Plane pages — sprint reports, retro notes, release notes, roadmap, meeting notes, decision logs (ADRs), specs, runbooks, and any general-purpose page as formatted HTML. Use when the user wants to publish a report, write a sprint summary, create a retro page, generate release notes, share a roadmap, document a decision, write a spec, capture meeting notes, or create any Plane page. Includes reusable HTML templates and Plane editor compatibility rules.
- `project-setup` — Agile-ready project setup — states, labels, work item types, properties, and feature configuration for Agile workflows. Use when setting up a new project or configuring an existing project for Agile.
- `sprint-planning` — Sprint planning — capacity calculation, sprint goal setting, work item selection, cycle creation. Use when planning a new sprint, calculating capacity, or selecting items for a sprint.
- `sprint-review-retro` — Sprint review and retrospective — completion metrics, previous retro action review, Start-Stop-Continue retro, DAKI format, 4Ls format, action item tracking, sprint close. Use when running sprint review, retrospective, closing a sprint, or reviewing previous retro action item status.
- `task-decomposition` — Task decomposition — INVEST criteria, vertical slicing, epic-to-subtask breakdown, story splitting patterns. Use when breaking down epics, stories, or large work items into smaller pieces.
- `velocity-metrics` — Velocity and metrics — historical velocity calculation, sprint burndown analysis, WIP limits, throughput tracking, time effort analysis. Use when calculating velocity, analyzing sprint progress, reviewing team metrics, comparing estimated vs actual effort, or checking time logged per story point.
- `work-items` — Work item operations in Plane — create, read, update, delete, search, assign, label, link, comment, relate, and log time on work items (issues/tasks/tickets). Use when the user wants to create a task, update an issue, add a comment, attach a label, link a PR, set a blocker, log work time, or inspect a specific item. Covers work item types, custom properties, and multi-item batch edits.

## Not carried over

- 2 agent(s) — Devin plugins do not support agents
- 44 command(s) — Devin plugins do not support commands
- hooks — Devin plugins do not support hooks

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/plane-ops
