# Bitwarden Client ↔ Vaultwarden Version Matrix

Single source for version advice in this plugin. Sources: Vaultwarden release notes 1.37.0–1.37.4 (https://github.com/dani-garcia/vaultwarden/releases) and issues #7750, #7820, #7829. Last checked 2026-10-07 (Vaultwarden 1.37.4, `bw` 2026.9.1).

## Minimum server per client

| Client (`bw`, web vault, desktop, mobile) | Minimum Vaultwarden | Failure below the minimum |
|---|---|---|
| 2026.9.x | 1.37.4 | `bw login` exits with 404 on `POST /api/accounts/key-management/user-key-id` (`KeyIdBackfillError`) |
| 2026.8.x | 1.37.2 | login/sync errors such as "No refresh token or API key found" |
| 2026.7.x | 1.37.0 | client features misbehave; upstream asks to update before reporting |

## Maximum age of the client per server

| Vaultwarden | Client constraint | Failure |
|---|---|---|
| ≥ 1.37.4 | an outdated `bw` that still calls `/api/accounts/prelogin` cannot log in (exact last affected version not published; 2026.8.0+ is known to work) | "Username or password is incorrect" with the right password |
| ≥ 1.37.4 | `bw` ≤ 2026.4.2 | `bw send receive` fails (creating Sends still works) |

## What to pin

| Server | Pin `bw` to |
|---|---|
| ≥ 1.37.4 | current release (2026.9.x) |
| 1.37.2 – 1.37.3 | 2026.8.x (`npm install -g @bitwarden/cli@2026.8.0`) |
| 1.37.0 – 1.37.1 | 2026.7.x |
| < 1.37.0 | upgrade the server; older client pairings are untested here |

Order of upgrades: server first, then clients. In CI, pin the exact `bw` version and change it together with the server version.

When this table is out of date, check the newest Vaultwarden release notes for lines like "required for support with clients with version …" and record the change in this file.
