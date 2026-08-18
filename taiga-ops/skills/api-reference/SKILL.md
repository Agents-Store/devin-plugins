---
name: api-reference
description: This skill should be used when the user asks for "Taiga API endpoints", "Taiga REST API", "Taiga curl examples", "Taiga API documentation", the exact path/method for any Taiga resource, or needs HTTP details for projects, epics, user stories, tasks, issues, milestones, wiki, webhooks, custom attributes, search, or import/export. Index into the full per-domain endpoint catalog.
disable-model-invocation: true
---

# Taiga REST API Reference

Complete endpoint catalog for the Taiga REST API, split by domain. Official docs: https://docs.taiga.io/api.html

Load the `setup` skill first for authentication and the global conventions (auth header, base path, pagination, `version` locking, the resolver) — those rules apply to every endpoint here and are not repeated in each file.

## Global conventions (recap)

- Base: `${TAIGA_API_URL%/}/api/v1/...` — header `Authorization: Bearer ${TAIGA_AUTH_TOKEN}`.
- Edits (`PATCH`/`PUT`) require the object's current `version` (GET first). `PATCH` = partial, `PUT` = full.
- Lists paginate (`x-pagination-*` headers; `?page=`, or header `x-disable-pagination: True`) and accept `?project=`, `?milestone=`, `?status=`, `?assigned_to=` filters.
- Use `/api/v1/resolver` to turn project slugs and item refs into numeric IDs.

## Domain index

Open the file matching the resource you need:

| Domain | File | Covers |
|--------|------|--------|
| Auth & users | `references/auth-users.md` | auth (login/register/refresh), applications & application-tokens, users, user-storage, locales, feedback, contact |
| Projects & access | `references/projects.md` | projects (+ tags, like/watch, modules, stats, duplicate, logo), project-templates, memberships, invitations, roles, permissions |
| Epics | `references/epics.md` | epics, related user stories, epic-statuses, epic custom-attributes (+ values), epic attachments |
| User stories | `references/user-stories.md` | userstories (+ bulk order/backlog/sprint/kanban), userstory-statuses, points, US custom-attributes (+ values), attachments |
| Tasks | `references/tasks.md` | tasks (+ bulk), task-statuses, task custom-attributes (+ values), attachments |
| Issues | `references/issues.md` | issues, issue-statuses, issue-types, priorities, severities, issue custom-attributes (+ values), attachments |
| Milestones & wiki | `references/milestones-wiki.md` | milestones (sprints) + stats, wiki pages, wiki links, wiki attachments |
| History & webhooks | `references/history-webhooks.md` | history & comments, attachments overview, webhooks, webhook-logs, notify-policies |
| Search & import | `references/search-import.md` | search, resolver, stats, export/import, importers (Trello/GitHub/Jira) |

## How to use a reference file

Each file lists endpoints as `METHOD /api/v1/<path>` with purpose and key fields. To run one, wrap it with auth and `jq`:

```bash
curl -s -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" \
  "${TAIGA_API_URL%/}/api/v1/<path>" | jq .
```

For writes, add `-X POST|PATCH|PUT|DELETE`, `-H "Content-Type: application/json"`, and `-d '<json>'` — and include `version` on edits.

## Examples

<example>
User: "What's the endpoint to move a user story to another sprint?"
→ Open `references/user-stories.md`. Single story: `PATCH /api/v1/userstories/{id}` with `{"milestone": <id>, "version": <v>}`. Many at once: `POST /api/v1/userstories/bulk_update_milestone`.
</example>

<example>
User: "How do I list all issues assigned to me that are still open?"
→ Open `references/issues.md`. `GET /api/v1/issues?project=<id>&assigned_to=<userId>&status=<openStatusId>`. Use `GET /api/v1/issues/filters_data?project=<id>` to discover status IDs.
</example>

<example>
User: "Give me the curl to create a webhook on project 7."
→ Open `references/history-webhooks.md`. `POST /api/v1/webhooks` with `{"project":7,"name":"CI","url":"https://...","key":"<secret>"}`.
</example>
