# Scenario: Secrets from Vaultwarden in CI and Scripts

Goal: a pipeline reads the database password and an API token from Vaultwarden at run time; nothing secret is stored in the repository or printed in the job log.

## Design

- Create a dedicated Vaultwarden account for the pipeline (e.g. `ci-deploy@example.com`), add it to the org as **User** with read-only access to one collection ("CI").
- Store one item per secret, or one secure note with custom fields named like the variables.
- CI secret store holds three values only: `BW_CLIENTID`, `BW_CLIENTSECRET` (the account's personal API key) and `BW_PASSWORD` (its master password). `VW_URL` and `VW_DEVICE_ID` can be plain variables.
- Pin the `bw` version to the one the [version matrix](../../../troubleshoot/references/version-matrix.md) gives for your server, and change it together with the server version.

## Job step (bash)

```bash
set -euo pipefail                                   # never `set -x` in this step
npm install -g @bitwarden/cli@<bw-version>         # from the version matrix
export BITWARDENCLI_APPDATA_DIR="$(mktemp -d)"     # isolated CLI state per job
bw config server "$VW_URL" >/dev/null
bw login --apikey >/dev/null                        # reads BW_CLIENTID / BW_CLIENTSECRET
export BW_SESSION="$(bw unlock --passwordenv BW_PASSWORD --raw)"
unset BW_PASSWORD

export DB_PASSWORD="$(bw get password <db-item-id>)"
export API_TOKEN="$(bw get item <ci-note-id> | jq -r '.fields[] | select(.name == "API_TOKEN") | .value')"

./deploy.sh                                         # consumes DB_PASSWORD / API_TOKEN from env

bw lock >/dev/null; bw logout >/dev/null
rm -rf "$BITWARDENCLI_APPDATA_DIR"
```

GitHub Actions: put the three secrets in repository/environment secrets and map them with `env:`; Actions masks them in logs, but values derived later (like `DB_PASSWORD`) are **not** masked automatically — add `echo "::add-mask::$DB_PASSWORD"` right after capturing if a tool might echo it.

## Faster for many reads: `bw serve`

A job that fetches dozens of values can start `bw serve --hostname localhost` once and read through `curl` (see [bw-serve](../../../cli-recipes/references/bw-serve.md)), avoiding one Node start-up per value.

## Cron on a server

Same steps, with `BW_CLIENTID`, `BW_CLIENTSECRET`, `BW_PASSWORD` in a root-only env file (`chmod 600`, loaded by the systemd unit's `EnvironmentFile=`), and a stable `VW_DEVICE_ID` so the account does not collect a new device per run.

## Why not raw HTTP

`/api/ciphers` returns encrypted fields; turning them into plaintext means re-implementing Bitwarden's key derivation and AES/HMAC envelope. `bw` does that correctly and keeps pace with format changes.
