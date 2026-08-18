# Users

User lifecycle, lookup, roles, status, preferences. Base `${MATTERMOST_API_URL%/}/api/v4`. A user `id` is a 26-char string; many endpoints accept `me` for the current user.

## CRUD & lookup

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/users` | Create a user. Body `{"email","username","password"?,"first_name"?,"last_name"?,"nickname"?}`. Admin creates without password verification. |
| GET | `/users` | List users. Query `page`, `per_page`, `in_team`, `in_channel`, `not_in_channel`, `active`, `inactive`, `role`, `sort`. |
| GET | `/users/{user_id}` | Get one user. |
| PUT | `/users/{user_id}` | Full update (send the whole user object). |
| PUT | `/users/{user_id}/patch` | Partial update — send only changed fields (preferred). |
| DELETE | `/users/{user_id}` | Deactivate (soft). Add `?permanent=true` for permanent delete if `EnableAPIUserDeletion` is on. |
| GET | `/users/username/{username}` | Look up by username. |
| GET | `/users/email/{email}` | Look up by email. |
| POST | `/users/ids` | Bulk get by IDs. Body `["id1","id2"]`. |
| POST | `/users/usernames` | Bulk get by usernames. Body `["alice","bob"]`. |
| GET | `/users/me` | The authenticated user. |

## Search & autocomplete

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/users/search` | Search users. Body `{"term","team_id"?,"in_channel_id"?,"not_in_channel_id"?,"allow_inactive"?,"limit"?}`. |
| GET | `/users/autocomplete` | Autocomplete. Query `name`, `in_team`, `in_channel`, `limit`. |
| GET | `/users/stats` | Total user count. |
| GET | `/users/stats/filtered` | Counts matching filters (`in_team`, `in_channel`, `include_deleted`, `roles`). |

## Roles & activation

| Method | Path | Purpose |
|--------|------|---------|
| PUT | `/users/{user_id}/roles` | Set system roles. Body `{"roles":"system_user system_admin"}` (space-separated). |
| PUT | `/users/{user_id}/active` | Activate/deactivate. Body `{"active":false}`. |
| POST | `/users/{user_id}/promote` / `/demote` | Promote guest→user / demote user→guest (guest accounts feature). |
| POST | `/users/{user_id}/convert_to_bot` | Convert a user into a bot account. |

## Password, email, audits

| Method | Path | Purpose |
|--------|------|---------|
| PUT | `/users/{user_id}/password` | Change password. Body `{"current_password","new_password"}` (admin may omit current). |
| POST | `/users/password/reset/send` | Send a reset email. Body `{"email"}`. |
| POST | `/users/email/verify` / `/users/email/verify/send` | Verify / resend verification. |
| GET | `/users/{user_id}/audits` | A user's audit log. |

## Status

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/users/{user_id}/status` | Get presence (`online`/`away`/`offline`/`dnd`). |
| PUT | `/users/{user_id}/status` | Set presence. Body `{"user_id","status":"online"}`. |
| POST | `/users/status/ids` | Bulk get statuses. Body `["id1","id2"]`. |
| PUT | `/users/{user_id}/status/custom` | Set custom status. Body `{"emoji","text","duration"?,"expires_at"?}`. |
| DELETE | `/users/{user_id}/status/custom` | Clear custom status. |

## Preferences

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/users/{user_id}/preferences` | All preferences. |
| PUT | `/users/{user_id}/preferences` | Upsert. Body = array of `{"user_id","category","name","value"}`. |
| POST | `/users/{user_id}/preferences/delete` | Delete listed preferences. |
| GET | `/users/{user_id}/preferences/{category}` | By category. |
| GET | `/users/{user_id}/preferences/{category}/name/{name}` | One preference. |

## Profile image

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/users/{user_id}/image` | Get profile image (binary). |
| POST | `/users/{user_id}/image` | Set image — multipart `-F "image=@avatar.png"`. |
| DELETE | `/users/{user_id}/image` | Reset to the generated default. |

## Custom profile attributes (CPA)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/custom_profile_attributes/fields` | List CPA field definitions. |
| POST | `/custom_profile_attributes/fields` | Create a CPA field (admin). |
| PATCH/DELETE | `/custom_profile_attributes/fields/{field_id}` | Update / delete a field. |
| PATCH | `/users/{user_id}/custom_profile_attributes` | Set a user's CPA values. |
