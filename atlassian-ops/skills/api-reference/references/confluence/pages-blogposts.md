# Confluence Pages & Blog Posts

The core content of Confluence v2. Base `${ATLASSIAN_SITE_URL%/}/wiki/api/v2` (paths below are relative to it). **Creating content needs a `body` with a `representation`; updating needs the next `version.number` — fetch the current version first (optimistic locking).**

## Body formats

A `body` is `{"representation":"storage"|"atlas_doc_format"|"wiki","value":"<…>"}`:
- `storage` — Confluence XHTML storage format, e.g. `<p>Hello <strong>world</strong></p>`.
- `atlas_doc_format` — ADF as a JSON **string** in `value`.
On reads, request what you want back with `?body-format=storage` (or `atlas_doc_format`, `view`).

## Pages

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /pages` | List pages (`getPages`). `?space-id=&status=current&title=&body-format=&sort=-modified-date&limit=25&cursor=`. Cursor pagination. |
| `GET /spaces/{id}/pages` | Pages in a space (`getPagesInSpace`). |
| `POST /pages` | Create a page (`createPage`). Body `{"spaceId":"<numeric>","status":"current","title":"…","parentId":"<id>"?,"body":{"representation":"storage","value":"<p>…</p>"}}`. `?embedded=&private=`. |
| `GET /pages/{id}` | Get a page (`getPageById`). `?body-format=storage&get-draft=false&version=`. Read `version.number` here before updating. |
| `PUT /pages/{id}` | Update a page (`updatePage`). Body `{"id":"<id>","status":"current","title":"…","version":{"number":<current+1>,"message":"…"?},"body":{"representation":"storage","value":"<p>…</p>"}}`. |
| `PUT /pages/{id}/title` | Rename only (`updatePageTitle`) — still requires the next `version.number`. |
| `DELETE /pages/{id}` | Delete a page (`deletePage`). `?purge=true` (admin, permanent) / `?draft=true`. **Confirm first.** |

## Page hierarchy

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /pages/{id}/children` | Child pages (`getChildPages`). |
| `GET /pages/{id}/ancestors` | Ancestor chain to the root (`getPageAncestors`). |
| `GET /pages/{id}/descendants` | All descendants (`getPageDescendants`). |
| `GET /pages/{id}/direct-children` | Direct children of any type (`getPageDirectChildren`). |

## Blog posts

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /blogposts` · `GET /spaces/{id}/blogposts` | List blog posts (all / in a space). |
| `POST /blogposts` | Create (`createBlogPost`). Body like a page but no `parentId`. |
| `GET /blogposts/{id}` · `PUT /blogposts/{id}` · `DELETE /blogposts/{id}` | Get / update (version bump) / delete. |

## Other content types (create / get / delete)

| Type | Endpoints |
|------|-----------|
| Custom content | `GET/POST /custom-content`, `GET/PUT/DELETE /custom-content/{id}` (`type`, `spaceId`, `pageId`/`blogPostId`, `body`). |
| Whiteboards | `POST /whiteboards`, `GET/DELETE /whiteboards/{id}`. |
| Databases | `POST /databases`, `GET/DELETE /databases/{id}`. |
| Folders | `POST /folders`, `GET/DELETE /folders/{id}`. |
| Smart Links (embeds) | `POST /embeds`, `GET/DELETE /embeds/{id}`. |

## Notes
- **Update flow is always read-then-write**: `GET /pages/{id}` → take `version.number` → `PUT` with `version.number + 1`. A stale number returns `409`.
- **`spaceId` is the numeric id**, not the space key. Resolve it via `GET /spaces?keys=PROJ` (see `spaces.md`).
- **Cursor pagination** — follow `_links.next` (or the `Link` header); don't compute `startAt`.
- v2 lists filter by `space-id`/`title`/`status`; **full-text/CQL search is the v1 endpoint** `${ATLASSIAN_SITE_URL%/}/wiki/rest/api/search?cql=…` (not in v2).
- For exact schemas: `grep -n '"operationId": "createPage"' ../confluence-openapi-v2.json`.
