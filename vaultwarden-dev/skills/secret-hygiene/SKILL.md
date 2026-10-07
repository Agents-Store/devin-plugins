---
name: secret-hygiene
description: This skill should be used when a Vaultwarden or bw task could print, log or store a secret — "store BW_SESSION", "show me the password from Vaultwarden", "export the vault in plain text", "put the master password in a script" — to keep secrets out of chat, logs, git and argv.
---

# Secret Hygiene for Vaultwarden Work

An AI agent session is a log: every command's output is written to the conversation transcript and may be stored, synced or reviewed later. A password printed once is a password that has to be rotated. Apply these rules to every Vaultwarden or Bitwarden CLI action, on every agent. The guard hook that ships with this plugin enforces part of them in Claude Code (and in agents that run Claude-format `PreToolUse` hooks unchanged); everywhere else these rules are the only protection.

## The five rules

1. **Capture, do not print.** Read secrets into variables or straight into the consuming command: `DB_PASSWORD="$(bw get password <item-id>)"`. Never run a bare `bw get password`, `bw get item`, `bw list items` or `bw unlock` whose output reaches the terminal.
2. **Select fields.** When listing, project away the secret fields: `bw list items --search x | jq -r '.[] | [.id, .name, .login.username] | @tsv'`. Show the user ids, names and usernames — they can open the web vault for the rest.
3. **No secret in argv.** Command lines are visible in `ps`, shell history and the transcript. Pass secrets through environment variables, stdin or files with mode 600: `bw unlock --passwordenv BW_PASSWORD --raw`, `printf '%s' "$VW_ADMIN_TOKEN" | curl --data-urlencode 'token@-' …`, `VAR="$(…)" cmd` prefixes, `jq` reading `env.VAR` instead of `--arg`. The one unavoidable exception is `bw export --password`, which has no env or stdin form. Short-lived bearer tokens in a `-H` header are acceptable; master passwords, API secrets and the admin token are not.
4. **Ask the human to type secrets.** When a master password, API secret or admin token is needed, have the user enter it with `read -r -s` in their own terminal (in Claude Code: `! read -r -s -p "master password: " BW_PASSWORD && export BW_PASSWORD`), or point at a file they created. Do not ask them to paste it into the chat.
5. **Short-lived sessions.** `bw lock` (or `POST /lock` on `bw serve`) when the task ends, `unset BW_SESSION BW_PASSWORD BW_CLIENTSECRET`, and delete admin cookie jars (`rm -f "$JAR"`).

## What counts as a secret here

| Value | Why it matters |
|---|---|
| master password | decrypts everything, forever |
| `BW_SESSION` | decrypts the local vault cache until `bw lock` |
| personal / org API `client_secret` | logs in without 2FA |
| `ADMIN_TOKEN`, `VW_ADMIN` cookie | full control of every account on the server |
| item passwords, TOTP seeds, notes, hidden custom fields, SSH private keys, attachments | the payload |
| `access_token` / `refresh_token` from `/identity/connect/token` | API access as the user |
| `config.json`, `rsa_key.pem` from the data folder | admin token, SMTP password, token signing key |

Not secret: item ids, names, usernames, URIs, folder and collection names, org member emails — still personal data, so show only what the task needs.

## Exports

- Backups: `bw export --format encrypted_json --password "$EXPORT_PASSWORD" --output <file>` — readable only with that password.
- A plain `json`/`csv` export is the entire vault in clear text. Create one only when the user explicitly asks, write it to a file with mode 600 (`umask 077` first), never print it, and delete it as soon as the import it serves is done.

## When the guard hook asks

The hook answers **ask** — it never blocks — when a Bash command would print decrypted data: `bw list items`, `bw get item|password|totp|notes`, uncaptured `bw unlock` / `bw login`, `bw export` without `encrypted_json`, `bw serve` bound beyond localhost or without origin protection, `bw serve` secret endpoints, `rbw get`, and `echo`/`printenv` of `BW_SESSION`, `BW_PASSWORD`, `BW_CLIENTSECRET` or the admin token.

When it asks, rewrite the command into a captured form if the value is only needed by a later command. Filtered pipelines (`bw list items … | jq -r '.[] | [.id, .name] | @tsv'`, `bw get item … | jq … | bw edit item …`) **still prompt**, because the hook cannot prove the filter drops the secrets — approve them after checking the `jq` projection. Approve anything else only when the user knowingly wants the value shown. Output captured in `$(...)`, `` `...` `` or `<(...)`, redirected to a file or piped to the clipboard passes without a prompt; a capture echoed straight back (`echo "$(bw get password …)"`) still asks. The hook has no network access and fails open.

## If a secret was printed anyway

1. Tell the user plainly which value appeared.
2. Rotate it at the source: change the item password in the target system and update the item; for an API key use `rotate-api-key`; for `BW_SESSION` run `bw lock` + `bw logout`; for the admin token generate a new hash and restart.
3. Deleting the message or the file does not undo the exposure — the transcript already holds it.

## Writing code and config

- Keep URLs, emails and secrets out of committed files; read them from the environment or the user's secret store at run time.
- In CI, inject `BW_CLIENTID`, `BW_CLIENTSECRET` and the master password as masked CI secrets, run `bw login --apikey` + `bw unlock --passwordenv`, and never `set -x` around those steps.
- In `docker-compose.yml`, reference `ADMIN_TOKEN` from an env file or `ADMIN_TOKEN_FILE` (Docker secret) instead of inlining the hash.
