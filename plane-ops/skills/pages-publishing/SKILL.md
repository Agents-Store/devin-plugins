---
name: pages-publishing
description: Create and publish Plane pages — sprint reports, retro notes, release notes, roadmap, meeting notes, decision logs (ADRs), specs, runbooks, and any general-purpose page as formatted HTML. Use when the user wants to publish a report, write a sprint summary, create a retro page, generate release notes, share a roadmap, document a decision, write a spec, capture meeting notes, or create any Plane page. Includes reusable HTML templates and Plane editor compatibility rules.
---

# Pages Publishing

Plane pages are rich HTML documents attached to a project or the workspace. Use them to publish durable artifacts: sprint reports, retros, release notes, roadmaps, ADRs, and stakeholder updates.

## Tool Name Resolution

Plane MCP exposes one `page` tool and the operation goes into the `action` parameter. Resolve the real tool name (`mcp__<server>__page`) through the `connector-bootstrap` skill - never assume a server prefix. An omitted `project_id` means a workspace page.

## Available Calls

| Call | Purpose |
|------|---------|
| `page(action=create, name, description_html)` | Create a page at the workspace level |
| `page(action=create, project_id, name, description_html)` | Create a page inside a project |
| `page(action=retrieve, page_id)` / `page(action=retrieve, project_id, page_id)` | Get a workspace / project page |
| `page(action=list)` / `page(action=list, project_id)` | List workspace / project pages (paginated) |
| `page(action=update\|archive\|delete\|set_collection\|attach_to_workitem\|detach_from_workitem)` | Edit and manage existing pages (see "Updating, Archiving and Deleting Pages") |
| `release(action=list\|retrieve\|get_changelog\|update_changelog\|list_workitems)` | Source data and a home for release notes (see "Release Notes from Plane Releases") |

## HTML Formatting Rules

Plane pages accept a restricted HTML subset in `description_html`. The Plane editor parses HTML through a Tiptap/ProseMirror schema — anything outside the schema is **silently transformed or stripped**. What you send is not always what you get.

**Safe tags:**
- Structure: `<h1>`, `<h2>`, `<h3>`, `<p>`, `<hr>`
- Lists: `<ul>`, `<ol>`, `<li>` (see List Rendering Gotchas below)
- Ordered list start offset: `<ol start="5">` is preserved
- Emphasis: `<strong>`, `<em>`, `<code>`, `<pre>`
- Tables: `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`, `<td>`
- Links: `<a href="…">`
- Hard break inside text: `<br>` (becomes a `hardBreak` node inside the surrounding paragraph)

**Avoid:** inline `<style>`, `<script>`, `<iframe>`, raw markdown, any custom `data-*` attributes (see gotchas below).

## List Rendering Gotchas — Critical

Plane's editor is strict about list structure. Several "valid HTML" patterns silently produce broken, disjointed, or empty-bullet output. These were verified by roundtrip testing (submit HTML → retrieve stored ProseMirror doc → compare). Follow these rules or your published page will look wrong.

### Gotcha 1 — `<li>` must start with text, not a nested list

**Broken:** a `<li>` whose first child is `<ul>` or `<ol>` (no own text).

```html
<!-- BROKEN: produces three disjointed top-level lists -->
<ul>
  <li><ul><li>Orphan child</li></ul></li>
  <li>Normal sibling</li>
</ul>
```

Stored result: **three separate top-level `bulletList` nodes** — one empty, one with the "Orphan child", one with the "Normal sibling". The outer list is torn apart at every child-first `<li>`.

**Correct:** always put at least one text character in the parent `<li>` before the nested list.

```html
<!-- OK: one structured list with proper nesting -->
<ul>
  <li>Topic<ul><li>Sub-point</li></ul></li>
  <li>Normal sibling</li>
</ul>
```

This is the root cause of "broken lists with gaps" that most users see.

### Gotcha 2 — Task lists / checkboxes via `data-checked` are silently stripped

```html
<!-- Stripped: data-checked is dropped, renders as plain bullets -->
<ul>
  <li data-checked="true">Done action</li>
  <li data-checked="false">Pending action</li>
</ul>
```

Plane's schema does not recognize `data-checked` on `<li>` at the HTML import layer — there is no `taskList` / `taskItem` node produced. The attribute is cosmetically preserved in `description_html` but the stored ProseMirror doc is plain `bulletList`.

**Correct:** use Unicode status markers as text instead. They render identically in any viewer and do not depend on editor features.

```html
<ul>
  <li>✅ Done action</li>
  <li>⏳ In progress action</li>
  <li>⬜ Not started action</li>
</ul>
```

### Gotcha 3 — Never emit empty `<li></li>`

```html
<!-- BROKEN: produces a visible empty bullet gap -->
<ul>
  <li>Before</li>
  <li></li>
  <li>After</li>
</ul>
```

An empty `<li>` is stored as a listItem with an empty paragraph and renders as an empty bulleted line. When a template placeholder like `{{NOT_DELIVERED_ITEMS}}` has no data, **do not substitute an empty string into `<ul>…</ul>`** — either emit the whole `<ul>` block conditionally or substitute `<li><em>None</em></li>`.

### Gotcha 4 — Don't mix inline text with block elements inside `<li>`

```html
<!-- Looks odd: three stacked paragraphs inside one bullet -->
<li>Text then<p>paragraph inside</p>and more text</li>
```

Each text run and each `<p>` becomes its own paragraph inside the `listItem`, stacking them vertically under one bullet marker. If you need a paragraph, put it outside the list. If you want a single bullet with multi-line text, use `<br>` inside one text run:

```html
<li>First line<br>second line of the same bullet</li>
```

### Gotcha 5 — Two `<ul>` blocks back-to-back stay separate

This is **not** a bug, but worth knowing: if you emit two adjacent `<ul>` blocks without a heading or `<hr>` between them, they stay as two separate lists (not merged). Fine for most cases, but if you want merged output, put the items in one `<ul>`.

### Quick Checklist for Template Authors

Before publishing any generated HTML:
1. No `<li>` starts with `<ul>` or `<ol>` — every parent list item has leading text
2. No empty `<li></li>` — conditional render the whole `<ul>` block for empty data
3. No `data-checked`, `data-*`, or other custom attributes — use Unicode markers
4. No mixed text + `<p>` inside a single `<li>` — use `<br>` for multi-line items
5. Nested lists use at most 3 levels (deeper works but is hard to read)
6. `<ol start="N">` is preserved if you need numbered lists starting mid-sequence

## Updating, Archiving and Deleting Pages

The `page` tool covers the whole page lifecycle, at workspace scope (omit `project_id`) or project scope (pass it):

| Need | Call |
|------|------|
| Edit a published report | `page(action=retrieve, page_id)` first, then `page(action=update, page_id, description_html, name?)` |
| Hide a page | `page(action=archive, page_id)`; `archive=false` restores it |
| Remove a page | `page(action=archive, ...)` first, then `page(action=delete, page_id)` — delete is refused for a page that is not archived, and it needs the user's confirmation |
| File a workspace page | `page(action=set_collection, page_id, collection_id)` (collections are managed with the `collection` tool) |
| Tie a page to a work item | `page(action=attach_to_workitem, project_id, workitem_id, page_id)`; undo with `detach_from_workitem` (needs the `workitem_page_id` from `page(action=list_workitem_pages)`) |

Rules to follow:
- `update` **replaces the whole body**: `description_html` overwrites everything, so retrieve the page first and send the full edited HTML, not a fragment. A locked or archived page is refused.
- A page's parent is fixed at creation (`parent_id` on `create`); nothing can reparent it later, so decide the hierarchy before publishing.
- Prefer `update` over creating a duplicate: regenerate-and-update keeps one page per report. Roadmap pages that the team refreshes weekly are a good fit.
- When testing publishing flows, still use a throwaway project: archived pages remain until deleted.
- `update` refuses a locked or archived page; unlock or restore it first (the `page` tool has no unlock action, so a locked page is unlocked in the Plane UI).

## Release Notes from Plane Releases

When the team tracks releases in Plane (the `release`, `release_tag` and `release_label` tools), build the release notes from the release itself instead of asking the user to list what shipped:

```
1. release(action=list)
   → Find the release by name; status is unreleased | released | cancelled
   (release_tag(action=list) maps a version string such as "v2.0.0" to the tag a release points at)

2. release(action=retrieve, release_id=<id>)
   → name, status, release_date, tag

3. release(action=list_workitems, release_id=<id>)
   → The work items shipped in the release (follow next_cursor);
     group them by type or label into New Features / Improvements / Bug Fixes

4. release(action=get_changelog, release_id=<id>)
   → The stored changelog (every release has one, created empty with the release);
     read it first so a rewrite does not drop hand-written notes

5. Render the Release Notes template with the grouped items.

6. Publish and store:
   page(action=create, project_id=<id>, name="Release v2.0 — YYYY-MM-DD", description_html="<…>")
   release(action=update_changelog, release_id=<id>, description_html="<…>")
   → the page is the stakeholder-facing copy, the changelog keeps the notes with the release
```

Other release calls: `release(action=create, name, status, release_date, tag_id, lead_id, is_prerelease)`, `release(action=update, ...)`, `release(action=manage_workitems, release_id, add_ids|remove_ids)` and `release_label(action=attach|detach, release_id, label_ids)`. `release_date` is what the Plane UI labels "Target date" (`YYYY-MM-DD`). `description_html` of the changelog follows the same HTML rules as any page.

## HTML Templates

Reusable templates live as separate files — load only the one you need:

| Type | File |
|------|------|
| Sprint report | [references/templates/sprint-report.html](references/templates/sprint-report.html) |
| Retrospective | [references/templates/retro.html](references/templates/retro.html) |
| Release notes | [references/templates/release-notes.html](references/templates/release-notes.html) |
| Roadmap | [references/templates/roadmap.html](references/templates/roadmap.html) |
| Milestone update | [references/templates/milestone-update.html](references/templates/milestone-update.html) |

Each template uses `{{PLACEHOLDER}}` tokens. Render by replacing tokens with concrete values gathered from Plane. Inlined previews follow for quick reference.

## Sprint Report Template

```html
<h1>Sprint 14 Report — Billing v2</h1>
<p><strong>Dates:</strong> 2026-03-24 → 2026-04-04 &middot; <strong>Goal:</strong> Users can see their Stripe invoices in-app</p>

<h2>Summary</h2>
<ul>
  <li>Completed: <strong>34 / 40 points</strong> (85%)</li>
  <li>Velocity vs last 3 sprints avg: 34 vs 32 (+6%)</li>
  <li>Goal achieved: <strong>Yes</strong></li>
</ul>

<h2>Delivered</h2>
<table>
  <thead><tr><th>ID</th><th>Title</th><th>Points</th><th>Owner</th></tr></thead>
  <tbody>
    <tr><td>PROJ-148</td><td>Stripe webhook receiver</td><td>5</td><td>@alice</td></tr>
  </tbody>
</table>

<h2>Not Delivered</h2>
<ul>
  <li>PROJ-152 — PDF export (3 pts) — blocked by vendor API, transferred to Sprint 15</li>
</ul>

<h2>Metrics</h2>
<ul>
  <li>Cycle time: 2.4 days avg</li>
  <li>WIP peak: 6 (limit 7)</li>
  <li>Blockers encountered: 2</li>
</ul>

<h2>Next Sprint</h2>
<p>Goal: …</p>
```

## Retrospective Template

```html
<h1>Sprint 14 Retrospective</h1>
<p><strong>Date:</strong> 2026-04-04 &middot; <strong>Attendees:</strong> @alice, @bob, @carol</p>

<h2>Previous Action Items</h2>
<ul>
  <li>✅ Enable daily standup async thread</li>
  <li>⏳ Document Stripe webhook schema — carried over</li>
</ul>

<h2>What Went Well</h2>
<ul><li>…</li></ul>

<h2>What Didn't</h2>
<ul><li>…</li></ul>

<h2>Action Items</h2>
<table>
  <thead><tr><th>Action</th><th>Owner</th><th>Due</th></tr></thead>
  <tbody>
    <tr><td>Add Stripe mock to local dev</td><td>@alice</td><td>Sprint 15</td></tr>
  </tbody>
</table>
```

## Release Notes Template

```html
<h1>Release v2.0 — 2026-04-08</h1>

<h2>Highlights</h2>
<ul>
  <li>Multi-tenant support</li>
  <li>New billing portal powered by Stripe</li>
</ul>

<h2>New Features</h2>
<ul><li>…</li></ul>

<h2>Improvements</h2>
<ul><li>…</li></ul>

<h2>Bug Fixes</h2>
<ul><li>…</li></ul>

<h2>Breaking Changes</h2>
<ul><li>…</li></ul>

<h2>Upgrade Notes</h2>
<p>…</p>
```

## Roadmap Page Template

```html
<h1>Roadmap — Q2 2026</h1>

<h2>Now (this sprint)</h2>
<ul><li><strong>Billing v2</strong> — Stripe migration, 65% complete</li></ul>

<h2>Next (next sprint)</h2>
<ul><li><strong>Multi-tenant support</strong> — design done, implementation starts Sprint 16</li></ul>

<h2>Later (this quarter)</h2>
<ul><li><strong>Enterprise SSO</strong> — scoping</li></ul>

<h2>Parked</h2>
<ul><li><strong>Mobile app</strong> — revisit Q3</li></ul>
```

## Publishing Workflow

```
1. connector-bootstrap → resolve tools
2. project(action=list) → pick project_id
3. Gather data from Plane (cycle data, work items, metrics; counts with workitem(action=count, pql=..., group_by=...))
4. Render HTML using a template above
5. page(action=create,
        project_id=<id>,
        name="Sprint 14 Report",
        description_html="<...>")
6. Share the page URL with stakeholders
```

## General-Purpose Page Templates

The templates above are tied to specific reporting workflows. The `/page` command also supports general-purpose templates for everyday documentation needs. Use these when the user wants any Plane page that is not a sprint/retro/release/roadmap/milestone report.

### Meeting Notes

```html
<h1>{{MEETING_TITLE}}</h1>
<p><strong>Date:</strong> {{DATE}} &middot; <strong>Attendees:</strong> {{ATTENDEES}}</p>

<h2>Agenda</h2>
<ol>
  <li>{{AGENDA_ITEM_1}}</li>
</ol>

<h2>Discussion</h2>
<p>{{NOTES}}</p>

<h2>Decisions</h2>
<ul>
  <li>{{DECISION_1}}</li>
</ul>

<h2>Action Items</h2>
<table>
  <thead><tr><th>Action</th><th>Owner</th><th>Due</th></tr></thead>
  <tbody>
    <tr><td>{{ACTION_1}}</td><td>{{OWNER_1}}</td><td>{{DUE_1}}</td></tr>
  </tbody>
</table>
```

### Decision Log (ADR)

```html
<h1>ADR-{{NUMBER}} — {{TITLE}}</h1>
<p><strong>Status:</strong> {{STATUS}} &middot; <strong>Date:</strong> {{DATE}} &middot; <strong>Deciders:</strong> {{DECIDERS}}</p>

<h2>Context</h2>
<p>{{CONTEXT}}</p>

<h2>Decision</h2>
<p>{{DECISION}}</p>

<h2>Alternatives Considered</h2>
<ul>
  <li><strong>{{ALT_1}}</strong> — {{ALT_1_REASON}}</li>
</ul>

<h2>Consequences</h2>
<p><strong>Positive:</strong> {{POSITIVE}}</p>
<p><strong>Negative:</strong> {{NEGATIVE}}</p>
<p><strong>Risks:</strong> {{RISKS}}</p>
```

Use ADR status values: `Proposed`, `Accepted`, `Deprecated`, `Superseded by ADR-N`.

### Spec / Design Doc

```html
<h1>{{FEATURE_NAME}} — Design Doc</h1>
<p><strong>Author:</strong> {{AUTHOR}} &middot; <strong>Status:</strong> {{STATUS}} &middot; <strong>Last updated:</strong> {{DATE}}</p>

<h2>Problem</h2>
<p>{{PROBLEM_STATEMENT}}</p>

<h2>Goals</h2>
<ul><li>{{GOAL_1}}</li></ul>

<h2>Non-goals</h2>
<ul><li>{{NON_GOAL_1}}</li></ul>

<h2>Proposed Solution</h2>
<p>{{SOLUTION}}</p>

<h2>API Changes</h2>
<pre><code>{{API_SAMPLE}}</code></pre>

<h2>Rollout Plan</h2>
<ol>
  <li>{{ROLLOUT_STEP_1}}</li>
</ol>

<h2>Open Questions</h2>
<ul><li>{{QUESTION_1}}</li></ul>

<h2>Linked Work</h2>
<ul>
  <li>Epic: {{EPIC_LINK}}</li>
  <li>Tracking issues: {{ISSUE_LINKS}}</li>
</ul>
```

### Runbook

```html
<h1>Runbook — {{SCENARIO}}</h1>
<p><strong>Owner:</strong> {{OWNER}} &middot; <strong>Severity:</strong> {{SEVERITY}} &middot; <strong>Last verified:</strong> {{DATE}}</p>

<h2>Symptoms</h2>
<ul><li>{{SYMPTOM_1}}</li></ul>

<h2>Diagnosis</h2>
<ol>
  <li>{{DIAGNOSIS_STEP_1}}</li>
</ol>

<h2>Mitigation</h2>
<ol>
  <li>{{MITIGATION_STEP_1}}</li>
</ol>

<h2>Recovery</h2>
<ol>
  <li>{{RECOVERY_STEP_1}}</li>
</ol>

<h2>Postmortem Trigger</h2>
<p>{{WHEN_TO_FILE_POSTMORTEM}}</p>

<h2>Related Dashboards</h2>
<ul><li><a href="{{DASHBOARD_URL}}">{{DASHBOARD_NAME}}</a></li></ul>
```

Runbook discipline: every action in Mitigation/Recovery is a single, copy-paste-runnable command — no "configure the thing" sentences.

### Blank

```html
<h1>{{TITLE}}</h1>
<p><em>Last updated: {{DATE}}</em></p>

<p>{{BODY}}</p>
```

The `blank` template is for when the user wants control of the body. Always include the "Last updated" line at the top — Plane does not surface page freshness in the sidebar.

## Template Selection Map

`/page create ... --from-template <name>` resolves these template names:

| Name | Template | Best for |
|---|---|---|
| `sprint-report` | Sprint Report | end-of-cycle summary |
| `retro` | Retrospective | sprint retro notes |
| `release-notes` | Release Notes | version release |
| `roadmap` | Roadmap | quarterly planning |
| `milestone-update` | Milestone Update | release tracking |
| `meeting-notes` | Meeting Notes | any meeting |
| `decision-log` | Decision Log (ADR) | architectural decisions |
| `spec` | Spec / Design Doc | feature design before build |
| `runbook` | Runbook | incident response |
| `blank` | Blank | freeform content |

## Best Practices

1. Publish the sprint report within 24 hours of sprint close — memory fades fast.
2. Link the report from the cycle's description for easy discovery.
3. Keep release notes audience-appropriate: customer-facing pages omit internal work items.
4. Roadmap pages should be updated weekly, not created from scratch.
5. Never publish PII or secrets on workspace pages — they may be broadly visible.
6. Always include a "Last updated" line — Plane does not show page freshness in the sidebar.
7. For ADRs, use a numbered prefix (`ADR-001`, `ADR-002`) so they sort naturally.
