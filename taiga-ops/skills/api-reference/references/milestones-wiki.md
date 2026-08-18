# Milestones (Sprints) & Wiki — API Reference

All paths under `${TAIGA_API_URL%/}/api/v1`, header `Authorization: Bearer ${TAIGA_AUTH_TOKEN}`. Edits require the object's current `version` (GET first).

## Milestones (sprints)

In Taiga, a "milestone" is a sprint. User stories and tasks reference it via their `milestone` field.

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/milestones?project=<id>` | List (filter `?closed=true|false`) | — |
| POST | `/milestones` | Create a sprint | `project`, `name`, `estimated_start` (YYYY-MM-DD), `estimated_finish` (YYYY-MM-DD), `slug?` |
| GET | `/milestones/{id}` | Get a sprint | — |
| PATCH | `/milestones/{id}` | Edit (partial) | `version` + e.g. `name`, `estimated_start`, `estimated_finish`, `closed` |
| PUT | `/milestones/{id}` | Replace | full object + `version` |
| DELETE | `/milestones/{id}` | Delete | — |
| GET | `/milestones/{id}/stats` | Sprint stats (points, completed, days) | — |
| POST | `/milestones/{id}/watch` / `/unwatch` | Watch / unwatch | — |
| GET | `/milestones/{id}/watchers` | List watchers | — |

```bash
# Create a two-week sprint
curl -s -X POST -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" -H "Content-Type: application/json" \
  -d '{"project":7,"name":"Sprint 4","estimated_start":"2026-06-01","estimated_finish":"2026-06-14"}' \
  "${TAIGA_API_URL%/}/api/v1/milestones" | jq '{id, slug, name}'

# Burndown-style numbers for a sprint
curl -s -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" \
  "${TAIGA_API_URL%/}/api/v1/milestones/12/stats" | jq .
```

## Wiki pages

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/wiki?project=<id>` | List wiki pages | — |
| POST | `/wiki` | Create a page | `project`, `slug`, `content` |
| GET | `/wiki/{id}` | Get a page | — |
| GET | `/wiki/by_slug?slug=<slug>&project=<id>` | Get a page by slug | — |
| PATCH | `/wiki/{id}` | Edit (partial) | `version`, `content` |
| PUT | `/wiki/{id}` | Replace | full object + `version` |
| DELETE | `/wiki/{id}` | Delete | — |
| POST | `/wiki/{id}/watch` / `/unwatch` | Watch / unwatch | — |
| GET | `/wiki/{id}/watchers` | List watchers | — |

### Wiki attachments

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/wiki/attachments?project=<id>&object_id=<wikiId>` | List | — |
| POST | `/wiki/attachments` | Upload (multipart) | `project`, `object_id` (wiki page id), `attached_file` |
| GET | `/wiki/attachments/{id}` | Get | — |
| PATCH | `/wiki/attachments/{id}` | Edit metadata | `version`, `description?` |
| DELETE | `/wiki/attachments/{id}` | Delete | — |

## Wiki links (sidebar navigation)

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/wiki-links?project=<id>` | List links | — |
| POST | `/wiki-links` | Create a link | `project`, `title`, `href` (page slug), `order?` |
| GET | `/wiki-links/{id}` | Get a link | — |
| PATCH | `/wiki-links/{id}` | Edit | `title?`, `href?`, `order?` |
| DELETE | `/wiki-links/{id}` | Delete | — |
