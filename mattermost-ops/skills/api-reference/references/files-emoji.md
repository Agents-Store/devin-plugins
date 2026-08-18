# Files & Emoji

Attachments and custom emoji. Base `${MATTERMOST_API_URL%/}/api/v4`.

## Files

Upload returns `file_infos[].id`; attach those ids to a post via `file_ids` (see `posts.md`).

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/files` | Upload a file. Multipart: `-F "channel_id=<id>" -F "files=@report.pdf"`. Returns `{file_infos:[{id,...}]}`. |
| GET | `/files/{file_id}` | Download the file (binary). |
| GET | `/files/{file_id}/thumbnail` | Image thumbnail. |
| GET | `/files/{file_id}/preview` | Image preview. |
| GET | `/files/{file_id}/info` | File metadata (name, size, mime, extension). |
| GET | `/files/{file_id}/link` | Get a public link (requires `EnablePublicLink`). |
| POST | `/teams/{team_id}/files/search` | Search files in a team. Body `{"terms","is_or_search"?}`. |

```bash
# Upload then post with the attachment
FID=$(curl -s -H "Authorization: Bearer ${MATTERMOST_TOKEN}" \
  -F "channel_id=${CHANNEL_ID}" -F "files=@/path/report.pdf" \
  "${MATTERMOST_API_URL%/}/api/v4/files" | jq -r '.file_infos[0].id')
curl -s -X POST -H "Authorization: Bearer ${MATTERMOST_TOKEN}" -H "Content-Type: application/json" \
  -d "{\"channel_id\":\"${CHANNEL_ID}\",\"message\":\"Monthly report\",\"file_ids\":[\"${FID}\"]}" \
  "${MATTERMOST_API_URL%/}/api/v4/posts" | jq '{id, message}'
```

## Upload sessions (large/resumable uploads)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/uploads` | Create an upload session. Body `{"channel_id","filename","file_size"}`. |
| GET | `/uploads/{upload_id}` | Get session state. |
| POST | `/uploads/{upload_id}` | Upload binary data chunk(s). |

## Custom emoji

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/emoji` | Create. Multipart: `-F "image=@smile.png" -F 'emoji={"creator_id":"<id>","name":"smile"}'`. |
| GET | `/emoji` | List custom emoji. Query `page`, `per_page`, `sort`. |
| GET | `/emoji/{emoji_id}` | Get one. |
| DELETE | `/emoji/{emoji_id}` | Delete. |
| GET | `/emoji/name/{emoji_name}` | Look up by name. |
| GET | `/emoji/{emoji_id}/image` | Get the image (binary). |
| GET | `/emoji/autocomplete` | Autocomplete. Query `name`. |
| POST | `/emoji/names` | Bulk get by names. |
| POST | `/emoji/search` | Search. Body `{"term"}`. |

## Brand image (system-wide)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/brand/image` | Get the custom brand image. |
| POST | `/brand/image` | (Admin) Upload — multipart `-F "image=@brand.png"`. |
| DELETE | `/brand/image` | (Admin) Remove. |
