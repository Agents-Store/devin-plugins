---
name: confluence-operations
description: This skill should be used when the user wants to do Confluence work — "create a Confluence page", "update a page", "edit a wiki page", "create a child page", "create a space", "list spaces", "comment on a page", "add a label", "attach a file in Confluence", or any everyday Confluence operation. Provides plain-language playbooks that drive the Confluence Cloud REST API v2.
---

# Confluence Common Operations

Plain-language playbooks for everyday Confluence work, each driving the REST API v2. For exact method signatures and every field, open the `api-reference` skill's matching `references/confluence/*.md` file.

## Before anything: ensure access

If `ATLASSIAN_*` aren't confirmed this session, run the `setup` skill first (one `GET /wiki/api/v2/spaces?limit=1` call). Define these once:

```bash
CONF="${ATLASSIAN_SITE_URL%/}/wiki/api/v2"
AUTH=(-u "${ATLASSIAN_EMAIL}:${ATLASSIAN_API_TOKEN}" -H "Accept: application/json")
JSON=(-H "Content-Type: application/json")
```

## The golden rules (why workflows look the way they do)

1. **`/wiki/api/v2` base** — the `/wiki` prefix is mandatory; omitting it is the usual cause of a `404`.
2. **Bodies carry a `representation`** — `{"representation":"storage","value":"<p>…</p>"}` (XHTML) or `atlas_doc_format` (ADF JSON string).
3. **Update = read-then-write.** Fetch the current `version.number`, then `PUT` with `number + 1`. A stale number returns `409`.
4. **`spaceId` is numeric**, not the space key — resolve the key first.
5. **Cursor pagination** — follow `_links.next`, don't compute offsets.
6. **Confirm destructive actions** — `DELETE /pages/{id}` (especially `?purge=true`).

## Workflow: resolve a space key → id, list its pages

```bash
SPACE_ID=$(curl -s "${AUTH[@]}" "${CONF}/spaces?keys=PROJ" | jq -r '.results[0].id')
curl -s "${AUTH[@]}" "${CONF}/pages?space-id=${SPACE_ID}&limit=25&sort=-modified-date" \
  | jq '.results[] | {id, title, status}'
```
(→ `spaces.md`, `pages-blogposts.md`)

## Workflow: create a page

```bash
curl -s "${AUTH[@]}" "${JSON[@]}" -X POST "${CONF}/pages" -d "{
  \"spaceId\": \"${SPACE_ID}\",
  \"status\": \"current\",
  \"title\": \"Onboarding Guide\",
  \"body\": {\"representation\": \"storage\", \"value\": \"<h1>Welcome</h1><p>Start here.</p>\"}
}" | jq '{id, title, _links}'
```
Add `"parentId":"<pageId>"` to nest it under another page. (→ `pages-blogposts.md`)

## Workflow: update a page safely (the #1 Confluence pitfall)

```bash
PAGE_ID=12345
# 1. Read the current version number (and title)
read VER TITLE < <(curl -s "${AUTH[@]}" "${CONF}/pages/${PAGE_ID}?body-format=storage" \
  | jq -r '"\(.version.number) \(.title)"')
# 2. Write with version.number + 1
curl -s "${AUTH[@]}" "${JSON[@]}" -X PUT "${CONF}/pages/${PAGE_ID}" -d "{
  \"id\": \"${PAGE_ID}\",
  \"status\": \"current\",
  \"title\": \"${TITLE}\",
  \"version\": {\"number\": $((VER+1)), \"message\": \"Updated via API\"},
  \"body\": {\"representation\": \"storage\", \"value\": \"<h1>Welcome</h1><p>Updated content.</p>\"}
}" | jq '{id, version: .version.number}'
```
Skipping the version bump → `409 Conflict`. (→ `pages-blogposts.md`)

## Workflow: create a space

```bash
curl -s "${AUTH[@]}" "${JSON[@]}" -X POST "${CONF}/spaces" \
  -d '{"key":"PROJ","name":"Project PROJ"}' | jq '{id, key, name}'
```
(→ `spaces.md`)

## Workflow: comment on a page

```bash
curl -s "${AUTH[@]}" "${JSON[@]}" -X POST "${CONF}/footer-comments" -d "{
  \"pageId\": \"${PAGE_ID}\",
  \"body\": {\"representation\": \"storage\", \"value\": \"<p>Looks good — shipping.</p>\"}
}" | jq '{id}'
```
Reply by adding `"parentCommentId":"<id>"`. (→ `comments-attachments.md`)

## Workflow: add a label (v1 endpoint)

Label writes aren't in v2 — use the v1 REST API:
```bash
curl -s -u "${ATLASSIAN_EMAIL}:${ATLASSIAN_API_TOKEN}" "${JSON[@]}" -X POST \
  "${ATLASSIAN_SITE_URL%/}/wiki/rest/api/content/${PAGE_ID}/label" \
  -d '[{"prefix":"global","name":"release-1-2"}]'
```
Read labels via v2: `GET ${CONF}/pages/${PAGE_ID}/labels`. (→ `labels-content-properties.md`)

## Workflow: attach a file (v1 endpoint, multipart)

```bash
curl -s -u "${ATLASSIAN_EMAIL}:${ATLASSIAN_API_TOKEN}" \
  -H "X-Atlassian-Token: nocheck" \
  -F "file=@./diagram.png" \
  "${ATLASSIAN_SITE_URL%/}/wiki/rest/api/content/${PAGE_ID}/child/attachment"
```
Read attachment metadata via v2: `GET ${CONF}/pages/${PAGE_ID}/attachments`. (→ `comments-attachments.md`)

## Workflow: full-text search (v1 CQL)

v2 lists filter by `space-id`/`title`/`status`. For real search use CQL on v1:
```bash
curl -s "${AUTH[@]}" \
  "${ATLASSIAN_SITE_URL%/}/wiki/rest/api/search?cql=space=PROJ%20AND%20text~%22login%20error%22"
```
(→ `pages-blogposts.md` Notes)

When a call fails (400/401/403/404/409/429), switch to the `troubleshoot` skill.
