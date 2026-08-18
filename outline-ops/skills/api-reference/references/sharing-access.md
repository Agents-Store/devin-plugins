# Sharing & Access

Public share links, access requests, and auth introspection. Every endpoint is `POST ${OUTLINE_API_URL%/}/<method>` with a JSON body and the Bearer header.

## Shares

A share authorizes viewing a document (or collection) without being a workspace member. Each user that shares gets their own share object; requesting a share for the same resource with the same key returns the existing one. Shares start **unpublished** — publish to make them accessible without login.

| Method | Purpose & key fields |
|--------|----------------------|
| `shares.info` | Retrieve a share. One of `{"id"}` or `{"documentId"}`. |
| `shares.list` | List all shares in the workspace. Pagination + sorting + `{"query"?}`. |
| `shares.create` | Create a share. Exactly one of `{"documentId"}` or `{"collectionId"}`. Returns a `Share` (unpublished by default). |
| `shares.update` | Change publish state / branding. `{"id","published"(required)}` + optional `{"title","iconUrl"}` to override the public page. Publishing removes authentication — anyone with the link can view. |
| `shares.revoke` | Deactivate the link so it can no longer be used. `{"id"}`. **Confirm first.** |

## Access requests

An access request is a user's request to view a document they can't currently see. A user with share permission approves (granting a membership) or dismisses it.

| Method | Purpose & key fields |
|--------|----------------------|
| `accessRequests.create` | Request access to a document. `{"documentId"}`. |
| `accessRequests.info` | Look up a request. At least one of `{"id"}` or `{"documentId"}` (the current user's pending request for that doc). |
| `accessRequests.approve` | Approve a pending request, granting a document membership. `{"id","permission":"read"|"read_write"|"admin"}` (default `read`). |
| `accessRequests.dismiss` | Dismiss a pending request without granting access. `{"id"}`. |

## Auth

| Method | Purpose & key fields |
|--------|----------------------|
| `auth.info` | Authentication details for the current key. No body → `{user, team}`. Use this as the connection/verification check. |
| `auth.config` | Workspace auth options (name, hostname, available SSO services). **Unauthenticated** — no Bearer header needed. |

## Notes

- `accessRequests.approve` is the one place a third permission value, `admin`, appears (alongside `read`/`read_write`).
- `auth.config` is the only endpoint that allows an unauthenticated request here — everything else needs the Bearer key.
- For exact schemas, search `operationId: shares…` / `accessRequests…` / `auth…` in `outline-openapi.yml`.
