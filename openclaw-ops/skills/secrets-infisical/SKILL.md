---
name: secrets-infisical
description: Use when secrets reach an OpenClaw instance through an injection wrapper and something about that is in question — a feature silently off while the config looks right, an instance receiving far fewer keys than its siblings, a plaintext env file inside the state tree, a token or client id sitting in a backup or identity copy, a key that has to be added, rotated, or proven delivered, a machine identity or its project binding, a secret reference in the config, or a restart whose safety depends on every referenced key still resolving.
---

# Secret injection and the store

Secrets are not in the config. The config holds **references**; the wrapper resolves them at start.
Everything here follows from that, including the failure that looks like a broken feature and is
really a missing key name.

## Mechanics

The gateway command is wrapped: the wrapper mints a **short-lived machine-identity token**, exchanges
it for the project's secret set, and execs the real process with those values **in its environment
only**. Nothing lands on disk, so:

- Reading the config tells you what is *required*. Only running the wrapper tells you what is
  *delivered*.
- An `exec` bypassing the wrapper sees no secrets and returns a false "key missing" verdict — which
  is why `ocexec.py` `hot` mode goes through the wrapper by default.
- The identity is per instance, one file, mode 0600, owned by root
  (`fleet.secrets.identity-file-mode`). A wrong project or environment binding shows up as short
  delivery, never as an error.
- Store values are **not encrypted at rest** — a recorded decision
  (`fleet.secrets.shared-store-plaintext`), not something to fix here.

## Never a value

Presence, fingerprint (`fp:0000aaaa` — an obviously synthetic stub; a real one is eight hex digits of a
digest), size bucket, key class, expiry date and full key name answer every operational question. The
value answers none of them.

- `redact.read_env_file` / `env_names` return names and fingerprints, never values.
- `redact.structure_only` renders a credential document by shape — safe fields verbatim, identifying
  fields as fingerprints. That is also the token-sink detector: one account fingerprint across
  several credential directories.
- Files that are **never read whole**: any env file, the auth-secret tree, auth profiles, credential
  directories, identity files, logs. Use a filter that structurally cannot return a value.
- When a provider answers unauthorized the value is useless as evidence; presence, fingerprint parity
  with what is injected, and expiry are the whole answer.

## The delivery audit

Two sets, compared **by name**:

- **required** — every secret reference in the effective config, plus the names the compose file
  passes through.
- **delivered** — the key names the wrapper actually produces inside the container. Names only; count
  the characters of a value if you need "non-empty", never print it.

`required − delivered` non-empty is **critical**: the feature reading that key is dead and nothing
logs an error (`fleet.secrets.delivery-short`). A count far below the siblings' is a wrong project or
environment binding (`fleet.secrets.wrong-project`); a set of almost nothing is a broken identity
(`fleet.secrets.identity-broken`). Compare against `secrets.expected_key_count` and against the other
instances — a fleet of clones makes the outlier obvious.

## Restart precondition

`compose restart` is R2, but on this deployment it carries an R3 precondition: **a running instance
holds its secrets in memory; a restart re-resolves them.** Restarting while a reference no longer
resolves converts a working instance into a dead one, and the cause is invisible afterwards.

Run the delivery audit *before* any restart, show the resolved-name list in PRECHECK, and refuse
while `required − delivered` is non-empty.

## Writing a secret

Three leak paths, all closed at once, plus the one this plugin refuses outright.

| Path | Why it leaks | Rule |
|---|---|---|
| command output | the write command prints the full `KEY=VALUE` table even in quiet mode | always discard stdout and stderr of the write |
| process table | a value in argv is visible to every user on the box | pass by stdin or environment, never as an argument |
| history and transcript | anything printed is on disk and in the model's context, permanently | **the plugin does not accept a key in chat** |

The plugin prints the operator a line that reads the value with echo disabled, pipes it to the write,
and then verifies by fingerprint alone. Overwriting a key whose fingerprint differs is red line
`secret-overwrite-different-fingerprint` — a rotation, not an edit. Writes get zero retries
(`gate.RETRY_RULES["secret-write"]`): a repeat risks a partial write and one more appearance in a
process table.

## Identity login: capture stdout only

The store CLI writes an update-check banner to **stderr**. A login that merges the streams glues that
banner onto the token, every later call fails, and the error blames the credentials. Capture stdout
alone — a token that "works by hand and fails in the script" is almost always this.

## Plaintext env files: parity decides, not existence

A plaintext env file inside the state tree is either **redundant** (every key matches the store by
fingerprint) or **load-bearing** (a key the store does not deliver). They look identical.

**Deleting a load-bearing file takes the instance down at the next restart, silently.** Classify by
fingerprint parity first, close the gap for load-bearing keys, then neutralise the file by **moving
it to a quarantine path outside every container volume** — never `rm`. Red line
`delete-plaintext-env`, finding `fleet.secrets.plaintext-env`; six-step procedure with its stop
points and canary restart in `references/playbook.md`.

## A leaked value is not fixed by deleting the file

If a token, client id or key ever sat in a file that left the box — a backup, a copy, a paste — the
value is compromised, and removing the file removes the evidence rather than the exposure
(`fleet.secrets.leaked-in-backup`, critical, R4). **Rotation is mandatory, not advisable.** Do not let
the easy action stand in for the undone hard one: "removed the file" while the old value still
authenticates closes the ticket without closing the exposure.

## Common mistakes

- Reading the config and calling it delivery.
- Running `exec` without the wrapper and concluding the key is missing.
- Restarting before the delivery precheck.
- Printing a value "just once" to compare it — compare fingerprints.
- Deleting a plaintext env file because the store also has those keys, without checking every key.
- Merging stderr into the login capture.
- Treating a leak as filed once the file is gone.

Procedures: `references/playbook.md`. Symptom to cause to check: `references/troubleshooting.md`.
Repairs go through `/openclaw-ops:repair <selector> --issue <finding-id>`.
