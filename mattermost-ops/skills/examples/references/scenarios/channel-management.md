# Scenario: Channel management

Edit a channel's metadata, change its privacy, move a member, and archive/restore it. Assumes `setup` has run.

```bash
BASE="${MATTERMOST_API_URL%/}/api/v4"
AUTH=(-H "Authorization: Bearer ${MATTERMOST_TOKEN}" -H "Content-Type: application/json")
TEAM_ID=$(curl -s "${AUTH[@]}" "${BASE}/teams/name/engineering" | jq -r .id)
CH_ID=$(curl -s "${AUTH[@]}" "${BASE}/teams/${TEAM_ID}/channels/name/general" | jq -r .id)
```

## 1. Set the header and purpose

```bash
curl -s -X PUT "${AUTH[@]}" -d '{
  "header": "On-call: @alice | Runbook: https://wiki/oncall",
  "purpose": "Team-wide engineering discussion"
}' "${BASE}/channels/${CH_ID}/patch" | jq '{display_name, header, purpose}'
```

## 2. Convert a public channel to private (or back)

```bash
curl -s -X PUT "${AUTH[@]}" -d '{"privacy":"P"}' \
  "${BASE}/channels/${CH_ID}/privacy" | jq '{name, type}'   # P = private, O = public
```
> Confirm with the user first — converting privacy changes who can discover and join the channel.

## 3. Inspect and adjust membership

```bash
# Who's in the channel?
curl -s "${AUTH[@]}" "${BASE}/channels/${CH_ID}/members?per_page=200" \
  | jq -r '.[] | .user_id'

# Remove someone
UID=$(curl -s "${AUTH[@]}" "${BASE}/users/username/bob" | jq -r .id)
curl -s -X DELETE "${AUTH[@]}" "${BASE}/channels/${CH_ID}/members/${UID}" | jq .
```

## 4. Move the channel to another team

```bash
DEST=$(curl -s "${AUTH[@]}" "${BASE}/teams/name/platform" | jq -r .id)
curl -s -X POST "${AUTH[@]}" -d "{\"team_id\":\"${DEST}\",\"force\":true}" \
  "${BASE}/channels/${CH_ID}/move" | jq '{name, team_id}'
```

## 5. Archive, then restore

```bash
# Archive (soft delete) — reversible
curl -s -X DELETE "${AUTH[@]}" "${BASE}/channels/${CH_ID}" | jq .

# Restore it
curl -s -X POST "${AUTH[@]}" "${BASE}/channels/${CH_ID}/restore" | jq '{name, delete_at}'
```
> Only add `?permanent=true` to the DELETE when the user explicitly wants an irreversible hard delete and the server allows it.

## 6. Pin an important post

```bash
POST_ID="<a post id in this channel>"
curl -s -X POST "${AUTH[@]}" "${BASE}/posts/${POST_ID}/pin" | jq .
curl -s "${AUTH[@]}" "${BASE}/channels/${CH_ID}/pinned" | jq -r '.order[]'
```
