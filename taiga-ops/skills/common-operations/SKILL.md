---
name: common-operations
description: This skill should be used when the user wants to do project-management work in Taiga — "create a user story / task / issue / epic in Taiga", "start a new sprint", "move a story to In Progress", "assign a task", "comment on an issue", "add members to a Taiga project", "build a sprint report", or any everyday Taiga operation. Provides plain-language workflows that drive the REST API and route to the exact endpoints.
---

# Taiga Common Operations

Plain-language playbooks for everyday Taiga work. Each one drives the REST API. For exact endpoint signatures and every field, open the `api-reference` skill's matching `references/*.md` file (named in each workflow).

## Before anything: ensure a token

If `TAIGA_AUTH_TOKEN` is not already set this session, run the `setup` skill's login first. Every call below assumes `TAIGA_AUTH_TOKEN` and `TAIGA_API_URL` are set and uses `Authorization: Bearer ${TAIGA_AUTH_TOKEN}`.

## The golden rules (why workflows look the way they do)

1. **Resolve names to IDs once.** Users say "project apollo, story #42"; the API wants numbers. Hit `/resolver` first and keep the IDs. (→ `search-import.md`)
2. **Read before you write.** Editing an item requires its current `version`. Always `GET` it, take `.version`, then `PATCH` with that version. (→ `setup`)
3. **Discover valid values per project.** Status/type/priority IDs differ per project. Use the resource's `.../filters_data?project=<id>` or list the `*-statuses` endpoint to pick the right ID instead of guessing.
4. **Confirm before deleting.** `DELETE` is irreversible; ask the user first.

## Workflow: find a project and its building blocks

```bash
# Slug -> project id
PID=$(curl -s -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" \
  "${TAIGA_API_URL%/}/api/v1/resolver?project=apollo" | jq -r .project)
# Story statuses (id + name) for that project
curl -s -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" \
  "${TAIGA_API_URL%/}/api/v1/userstory-statuses?project=${PID}" | jq -r '.[] | "\(.id)\t\(.name)"'
```
(→ `projects.md`, `user-stories.md`)

## Workflow: create / update a work item

The shape is identical for user stories, tasks, issues, and epics — only the path and a few fields differ.

1. **Create** — `POST` the collection with `project` + `subject` (+ optional `status`, `assigned_to`, `milestone`, classifiers).
2. **Update** — `GET` the item → read `.version` → `PATCH` with the changed fields **and** `version`.
3. **Move status** — `PATCH` `{ "status": <statusId>, "version": <v> }`.
4. **Assign** — `PATCH` `{ "assigned_to": <userId>, "version": <v> }`.
5. **Tag** — `PATCH` `{ "tags": [["urgent","#ff0000"], ...], "version": <v> }`.
6. **Comment** — `PATCH` `{ "comment": "text", "version": <v> }` (comments ride on the item; → `history-webhooks.md`).
7. **Attach a file** — multipart `POST .../attachments` with `project`, `object_id`, `attached_file`.

Reference per type: stories → `user-stories.md`, tasks → `tasks.md`, issues → `issues.md`, epics → `epics.md`.

```bash
# Move story 1234 to "In progress" (status 456)
US=$(curl -s -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" "${TAIGA_API_URL%/}/api/v1/userstories/1234")
curl -s -X PATCH -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" -H "Content-Type: application/json" \
  -d "{\"status\":456,\"version\":$(echo "$US" | jq -r .version)}" \
  "${TAIGA_API_URL%/}/api/v1/userstories/1234" | jq '{id, status}'
```

## Workflow: sprint planning

1. Create the sprint: `POST /milestones` with `project`, `name`, `estimated_start`, `estimated_finish`. (→ `milestones-wiki.md`)
2. Put stories in it: on each story `PATCH { "milestone": <sprintId>, "version": <v> }`, or move many at once with `POST /userstories/bulk_update_milestone`. (→ `user-stories.md`)
3. Add tasks under stories: `POST /tasks` with `user_story` set. (→ `tasks.md`)
4. Track progress: `GET /milestones/{id}/stats` for points completed / remaining. (→ `milestones-wiki.md`)

## Workflow: bug triage

1. Discover classifier IDs: `GET /issues/filters_data?project=<id>` → status, type, priority, severity. (→ `issues.md`)
2. Create: `POST /issues` with `project`, `subject`, `type`, `priority`, `severity`.
3. Assign + comment + attach a screenshot as in "create/update a work item".
4. Resolve: `PATCH { "status": <closedStatusId>, "version": <v> }`.

## Workflow: manage project access

1. List members: `GET /memberships?project=<id>`. (→ `projects.md`)
2. Invite: `POST /memberships` with `project`, `role`, `username` (email), or many via `POST /memberships/bulk_create`.
3. Change a role: `PATCH /memberships/{id}` with `role` + `version`.
4. Manage roles/permissions: `roles` + `permissions` endpoints. (→ `projects.md`)

## Workflow: search & report

1. Find items: `GET /search?project=<id>&text=<q>`. (→ `search-import.md`)
2. Filtered lists: `GET /userstories?project=&milestone=&status=&assigned_to=` (same pattern for tasks/issues).
3. Numbers: `GET /projects/{id}/stats`, `GET /projects/{id}/issues_stats`, `GET /milestones/{id}/stats`.
4. Full export: `GET /exporter/{projectId}` → poll the dump URL. (→ `search-import.md`)

When a call fails (401, 400 version conflict, 403), switch to the `troubleshoot` skill.
