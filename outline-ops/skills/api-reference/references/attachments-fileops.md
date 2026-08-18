# Attachments & File Operations

Files uploaded into Outline, and the background jobs that import/export content. Every endpoint is `POST ${OUTLINE_API_URL%/}/<method>` with a JSON body and the Bearer header (the actual binary upload is a separate request to cloud storage — see below).

## Attachments

An attachment is a file in cloud storage. Creating one returns the inputs needed to upload the file from the client.

| Method | Purpose & key fields |
|--------|----------------------|
| `attachments.create` | Create the DB record and get a signed upload target. `{"name","contentType","size"(bytes, required)}` + `{"documentId"?}`. Returns `{maxUploadSize, uploadUrl, form, attachment}`. |
| `attachments.redirect` | Resolve an attachment to its stored file. `{"id"}`. Responds **`302`** redirecting to the file URL (a signed URL is generated on demand for private files) — use `curl -sL` to follow or `curl -sI` to read the `Location`. |
| `attachments.delete` | Permanently delete an attachment. `{"id"}`. Does not remove links/references to it inside documents. |

**Two-step upload:** call `attachments.create`, then POST the file to the returned `uploadUrl` as `multipart/form-data` using the returned `form` fields (this request goes to storage, not the Outline API, and does not use the Bearer header). The returned `attachment.url` can then be embedded in a document.

## File operations

A `FileOperation` is a long-running import or export job. `type` is `import` or `export`; `state` moves `creating → uploading → complete` (or `error`/`expired`). Exports from `collections.export` / `collections.export_all` / `documents.export` produce these.

| Method | Purpose & key fields |
|--------|----------------------|
| `fileOperations.info` | Status + details of one operation. `{"id"}` → a `FileOperation` (check `.data.state`). |
| `fileOperations.list` | List operations of a kind. `{"type":"export"|"import"(required)}` + pagination + sorting. |
| `fileOperations.redirect` | Download the resulting file. `{"id"}`. Returns the binary (a signed URL is generated on demand) — use `curl -sL … -o out.zip`. |
| `fileOperations.delete` | Delete a file operation and its files (cleanup). `{"id"}`. |

## Notes

- Poll `fileOperations.info` until `state == "complete"`, then fetch with `fileOperations.redirect`. Don't download before completion.
- Both `attachments.redirect` and `fileOperations.redirect` return signed URLs / redirects — handle the `302`/binary rather than expecting the JSON envelope.
- For exact schemas, search `operationId: attachments…` / `fileOperations…` in `outline-openapi.yml`.
