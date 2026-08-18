---
name: google-workspace-setup
description: "Use when installing or troubleshooting the gws (Google Workspace CLI) that powers every google-workspace-dev skill. Triggers on \"install gws\", \"gws auth setup\", \"gws auth login\", \"set up Google Workspace CLI\", \"connect Gmail/Drive/Calendar\", or errors like \"command not found: gws\", \"Access blocked\", \"403 accessNotConfigured\", \"redirect_uri_mismatch\", or \"too many scopes\"."
---

# Google Workspace CLI (gws) — Setup & Auth

Every skill in this plugin (`gws-*`, `persona-*`, `recipe-*`) drives the **`gws` CLI**. Nothing works until `gws` is installed and authenticated. Run this checklist first whenever a command fails with a missing-binary or auth error.

## Step 1 — Confirm the binary is on PATH

```bash
gws --version
```

If this prints a version, skip to Step 2. If it errors with `command not found`, install it. Install only one way — prefer the pre-built binary or `npm`, since they pin a tested release.

| Method | Command | Notes |
|--------|---------|-------|
| npm (recommended) | `npm install -g @googleworkspace/cli` | Needs Node.js 18+. Downloads the right binary from GitHub Releases. |
| Pre-built binary | Download from [GitHub Releases](https://github.com/googleworkspace/cli/releases), extract, put `gws` on `$PATH` | No Node required. |
| Homebrew (macOS/Linux) | `brew install googleworkspace-cli` | |
| Cargo (from source) | `cargo install --git https://github.com/googleworkspace/cli --locked` | Slow; needs Rust. |
| Nix | `nix run github:googleworkspace/cli` | |

Re-run `gws --version` to confirm before continuing — an unauthenticated install still cannot call any API.

## Step 2 — Choose an auth path

`gws` needs OAuth credentials tied to a **Google Cloud project**. Pick the row that matches the environment, because each path fixes a different missing piece:

| Situation | Use |
|-----------|-----|
| Local desktop, `gcloud` installed & logged in | `gws auth setup` (fastest — automates project + API enablement) |
| Local desktop, no `gcloud` | Manual OAuth (Step 2b) |
| Already have an OAuth access token | `export GOOGLE_WORKSPACE_CLI_TOKEN=...` |
| Server / CI with a credentials file | `export GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE=/path/to/creds.json` |

### Step 2a — Interactive setup (has gcloud)

```bash
gws auth setup     # one-time: creates the Cloud project, enables APIs, logs in
gws auth login     # subsequent logins / scope changes
```

### Step 2b — Manual OAuth (no gcloud)

Do this when `gws auth setup` cannot run. The most common login failure is forgetting the **test user** step, so do not skip it.

1. Open the [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent) for your project. App type: **External** (testing mode is fine).
2. Under **Test users → Add users**, add your own Google account email. Without this, login fails with a generic "Access blocked".
3. Create an OAuth client of type **Desktop app** under [Credentials](https://console.cloud.google.com/apis/credentials).
4. Download the client JSON and save it to `~/.config/gws/client_secret.json`.
5. Run `gws auth login`.

## Step 3 — Log in with the right scopes

Request **only the scopes you need**, not the full preset. Unverified (testing-mode) apps are capped at ~25 OAuth scopes, and the `recommended` preset has 85+ — it **will fail**, especially for `@gmail.com` accounts.

```bash
# Good: scope the login to the services you will actually use
gws auth login -s drive,gmail,calendar,sheets

# Then verify end-to-end with a read-only call
gws drive files list --params '{"pageSize": 5}'
```

If the browser shows **"Google hasn't verified this app"**, that is expected in testing mode — click **Advanced → Go to <app> (unsafe)** to continue.

## Step 4 — Headless / CI (no browser)

Authenticate once on a machine with a browser, export, then move the file:

```bash
# On the machine with a browser
gws auth export --unmasked > credentials.json

# On the headless box
export GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE=/path/to/credentials.json
gws drive files list   # just works
```

For server-to-server, point at a service-account key instead:

```bash
export GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE=/path/to/service-account.json
```

## Troubleshooting

Match the symptom — each error has one root cause:

| Symptom | Cause | Fix |
|---------|-------|-----|
| `command not found: gws` | Binary not installed / not on PATH | Step 1 |
| "Access blocked" / 403 at login | Your account isn't a **test user** | Add yourself under OAuth consent → Test users, retry `gws auth login` |
| "Google hasn't verified this app" | App in testing mode (normal) | Click **Advanced → Go to <app> (unsafe)** |
| Consent fails / "too many scopes" | Unverified app exceeds ~25 scopes | Log in with `-s drive,gmail,…` instead of the full preset |
| `redirect_uri_mismatch` | OAuth client not created as **Desktop app** | Delete the client, recreate as **Desktop app**, re-download JSON |
| 403 `accessNotConfigured` | Required Google API not enabled for the project | Open the `enable_url` from the error, click **Enable**, wait ~10s, retry |
| `gcloud` not found during `gws auth setup` | setup automates via gcloud | [Install gcloud](https://cloud.google.com/sdk/docs/install) or use manual OAuth (Step 2b) |

## Environment variables

All optional; set in the shell or a `.env` file.

| Variable | Purpose |
|----------|---------|
| `GOOGLE_WORKSPACE_CLI_TOKEN` | Pre-obtained OAuth2 access token (highest priority) |
| `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` | Path to OAuth or service-account JSON |
| `GOOGLE_WORKSPACE_CLI_CLIENT_ID` / `_CLIENT_SECRET` | OAuth client pair (alternative to `client_secret.json`) |
| `GOOGLE_WORKSPACE_CLI_CONFIG_DIR` | Override config dir (default `~/.config/gws`) |
| `GOOGLE_WORKSPACE_PROJECT_ID` | GCP project override for quota/billing |

## After setup

Once `gws drive files list` returns JSON, the rest of the plugin works. Hand off to the service skills:

- Read `gws-shared` for global flags, output formats, and security rules — every other skill assumes it.
- Then load the service skill you need (`gws-gmail`, `gws-drive`, `gws-calendar`, `gws-sheets`, …), a `persona-*` skill for a role, or a `recipe-*` skill for a ready-made workflow. See `SKILLS_INDEX.md` for the full catalog.

## Exit codes (for scripting)

`gws` returns structured exit codes so scripts can branch on failure type: `0` success · `1` API error · `2` auth error · `3` validation error · `4` discovery error · `5` internal error.
