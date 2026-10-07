# Vaultwarden Identity — Login, Tokens, Master Password Hash

Source: `src/api/identity.rs`, `src/api/core/accounts.rs`, `src/auth.rs` (Vaultwarden 1.37.4). All requests here are unauthenticated and `application/x-www-form-urlencoded` unless stated.

## Prelogin — KDF parameters

```bash
curl -fsS "$VW_URL/identity/accounts/prelogin" -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com"}' | jq '{kdf, kdfIterations, kdfMemory, kdfParallelism}'
```

`kdf`: `0` = PBKDF2-SHA256, `1` = Argon2id. Defaults for new accounts: PBKDF2 with 600000 iterations. `POST /identity/accounts/prelogin/password` is an alias. The old `/api/accounts/prelogin` route is gone since 1.37.4.

Unknown emails get a **deterministic fake** KDF from a fixed list (anti-enumeration), so a prelogin answer does not prove the account exists.

## `POST /identity/connect/token`

| `grant_type` | Required fields | Use |
|---|---|---|
| `client_credentials` (user) | `client_id=user.<user-uuid>`, `client_secret`, `scope=api`, `device_identifier`, `device_name`, `device_type` | scripts; **skips 2FA** |
| `client_credentials` (org) | `client_id=organization.<org-uuid>`, `client_secret`, `scope=api.organization` | only for `/api/public/organization/import` |
| `password` | `client_id` (`cli`, `web`, `desktop`…), `username`, `password` = master-password **hash**, `scope=api offline_access`, `device_identifier`, `device_name`, `device_type` | interactive-style login; triggers 2FA |
| `refresh_token` | `refresh_token` | renew without credentials |

2FA on the password grant: the first call returns 400 with `TwoFactorProviders2`; repeat with `two_factor_provider` (`0` authenticator, `1` email, …), `two_factor_token`, and optionally `two_factor_remember=1`.

`device_type` is a number; unknown values fall back to `14` (SDK/unknown). Keep `device_identifier` stable per script — a new identifier is a new device, and with SMTP on it triggers a "new device" email; if that mail fails and `REQUIRE_DEVICE_EMAIL=true`, the login fails.

```bash
# User API key → access token (store the device id once, reuse it)
VW_DEVICE_ID="${VW_DEVICE_ID:-$(uuidgen | tr 'A-Z' 'a-z')}"
printf '%s' "$BW_CLIENTSECRET" | curl -fsS "$VW_URL/identity/connect/token" \
  --data-urlencode grant_type=client_credentials \
  --data-urlencode scope=api \
  --data-urlencode "client_id=$BW_CLIENTID" \
  --data-urlencode 'client_secret@-' \
  --data-urlencode device_type=14 \
  --data-urlencode "device_identifier=$VW_DEVICE_ID" \
  --data-urlencode device_name=vw-script \
  | jq '{token_type, expires_in, scope}'
```

Successful response fields: `access_token`, `token_type: "Bearer"`, `expires_in`, `refresh_token` (password grant), `scope`, `Key` (user key, encrypted), `PrivateKey` (encrypted), `Kdf*`, `UserDecryptionOptions`. Never print the whole body — it carries the tokens. The secret is read from stdin (`@-`) so it stays out of the process list.

Lifetimes: access token 2 hours; refresh token 30 days (90 days for mobile clients).

## Where API keys come from

| Key | How to get it |
|---|---|
| Personal (`user.<uuid>`) | Web vault → Account settings → Security → Keys → View API key; or `POST /api/accounts/api-key {masterPasswordHash}` |
| Organization (`organization.<uuid>`) | Admin Console → Settings → Organization info → API key (Owner); or `POST /api/organizations/<org-uuid>/api-key {masterPasswordHash}` |

Rotate with the matching `rotate-api-key` route; the old secret stops working at once.

## Master password hash (password grant only)

The server never receives the master password. Bitwarden clients send:

1. `master_key` = PBKDF2-SHA256(password, salt = email trimmed and lowercased, iterations from prelogin, 32 bytes) — or Argon2id(password, salt = SHA-256(email), memory/iterations/parallelism from prelogin).
2. `password` field = base64( PBKDF2-SHA256(master_key, salt = password, 1 iteration, 32 bytes) ).

PBKDF2 case in Python (standard library only):

```python
import base64, hashlib

def master_password_hash(email: str, password: str, iterations: int) -> str:
    master_key = hashlib.pbkdf2_hmac("sha256", password.encode(), email.strip().lower().encode(), iterations, 32)
    return base64.b64encode(hashlib.pbkdf2_hmac("sha256", master_key, password.encode(), 1, 32)).decode()
```

A hash computed with the wrong KDF settings fails exactly like a wrong password ("Username or password is incorrect"). Prefer the API-key grant for scripts — it needs none of this and is not blocked by 2FA.

## Errors

| Status / body | Meaning |
|---|---|
| 400 `Username or password is incorrect. Try again` | wrong email, wrong hash, wrong KDF, or a client too new for the server |
| 400 `TwoFactorProviders2` in body | 2FA required on the password grant |
| 400 `Scope not supported` | scope must be `api offline_access` / `api` / `api.organization` |
| 400 `Invalid client_id`, `Malformed client_id`, `Incorrect client_secret` | API-key problem; check the `user.` / `organization.` prefix |
| 400 `{"error":"invalid_grant"}` | refresh token expired or revoked (password change, deauth) |
| 400 `This user has been disabled` | an admin disabled the account |
| 400 `Please verify your email before trying again.` | `SIGNUPS_VERIFY=true` and email not verified |
| 400 `SSO sign-in is required` | `SSO_ONLY=true` blocks the password grant |
| 429 `Too many login requests` | `LOGIN_RATELIMIT_SECONDS` / `LOGIN_RATELIMIT_MAX_BURST` (default 60 s / 10) per IP |
