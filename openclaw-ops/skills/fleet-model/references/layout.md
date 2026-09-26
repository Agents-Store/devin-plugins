# Deployment layout

Everything below is the *shape* of the deployment class. Every host path is a placeholder:
`<compose-root>`, `<data-root>`, `<bin-dir>`, `<identity-dir>`, `<instance>`. Read the real ones from
the mount table (`fleet.py discover --json` → `paths`), never from this page and never from memory.
Container-side destinations are the exception: upstream fixes them, so they are safe to know.

## Two trees, one instance

| Tree | What it is | Placeholder | Recreated by |
|---|---|---|---|
| Source | compose project directory: the compose file, the deployment layer, whatever the image is built or pulled from | `<compose-root>/<project>/` | `git pull` + `compose up`, image swap |
| State | everything the gateway has learned: config, memory database, sessions, schedules, state-side extensions | `<data-root>/<instance>/…` | never — it survives every container recreation |

The split is the reason "recreate the container" is a cheap operation and "edit inside the container"
is a red line (`in-container-write-outside-mount`): a write that lands outside a mount lives only
until the next `up`.

## Mount table

`discovery.MOUNT_ROLES` maps container-side destinations to roles. The host side is read from
`docker inspect`; the role names below are the keys of `paths` in an instance record.

| Container destination | Role | Holds | Sharing |
|---|---|---|---|
| `/home/node/.openclaw` | `state_dir` | `openclaw.json`, memory DB, sessions, schedules, state-side skills and plugins | **never shared** — startup enforces unique state-directory ownership |
| `/home/node/.config/openclaw` | `auth_secrets` | the key that encrypts stored auth profiles | per instance |
| `/home/node/.claude` | `claude_dir` | native credentials and settings of the Claude CLI backend | shareable, and sharing is the fix for the token-sink failure |
| `/home/node/.claude.json` | `claude_json` | project state, MCP registrations, onboarding flags | **keep per instance** — sharing leaks project state between instances |
| `/home/node/.codex` | `codex_home` | native credentials of the Codex CLI backend | shareable on the same terms as `claude_dir` |
| `/home/node/.local/share/claude` | `claude_share` | CLI data directory | follows `claude_dir` |
| `/home/node/.local/bin` | `claude_local_bin` | CLI-managed binaries | follows `claude_dir` |
| destination ending `shared-skills` | `shared_skills` | fleet-wide skills, mounted read-only | shared, one canonical copy |
| destination ending `shared-plugins` | `shared_plugins` | fleet-wide plugins, mounted read-only | shared, one canonical copy |
| anything else | `paths.extra[]` | unclassified mount: source, destination, type, mode | explain it or flag it; an unexplained mount is a finding, not noise |

`paths.config_file` is derived, not mounted: it is `state_dir` plus the config file name.

### Credential directories: mount the directory, not the file

A CLI backend rewrites its credential file atomically — write a temp file, rename over the target.
That replaces the inode. A single-file bind mount is bound to the *old* inode and freezes at the
moment of the first rotation, silently. Mount the containing directory.

## Compose service anatomy

One gateway service per instance. What each part contributes, in placeholders:

```yaml
services:
  gateway:                                     # service name; discovery matches by name hint + compose label
    image: <registry>/<image>:<version-or-digest>   # pin a plain version or a digest; moving tags are rebuilt
    command: ["<secret-injection-wrapper>", "node", "<entrypoint>", "gateway", "--port", "18789"]
    ports: ["127.0.0.1:<host-port>:18789"]     # publish on loopback; images publish outward by default
    environment:                               # names and secret references only, never literal values
      OPENCLAW_CONFIG_PATH: /home/node/.openclaw/<config-file>
      OPENCLAW_STATE_DIR:  /home/node/.openclaw
    healthcheck: {test: ["CMD", "<probe>", "http://127.0.0.1:18789/healthz"]}
    cap_drop: [ALL]
    volumes: [ …the mount table above… ]
```

- **18789 is the container-side gateway port** and is the same everywhere; the *host* port differs
  per instance and is discovered, never assumed.
- The command is wrapped by the secret-injection helper, so secrets exist only in the process. That is
  why `ocexec.py` runs `hot` through the same wrapper: an exec without it sees no secrets and produces
  a misleading "key missing" verdict.
- Four values must be unique per instance or isolation is broken: config path, state dir, agent
  workspace, gateway port. Credential directories are deliberately absent from that list.
- The healthcheck answers "is the HTTP server up". It does not answer "is this instance working" —
  see `fleet-diagnostics` for the liveness split.

## What persists and what does not

| Survives container recreation | Dies with the container |
|---|---|
| everything under `state_dir` (config, memory, sessions, schedules) | packages installed at runtime inside the container |
| auth-secret key material under `auth_secrets` | edits to files that are part of the image |
| credential directories, shared skill and plugin trees | anything written to a path that is not in the mount table |
| host-side wrappers, identity files, compose files | in-memory secrets from the injection wrapper |

Practical consequence: a repair is durable only if it lands in a mounted path or in the compose file.
"It worked when I ran it inside the container" is the classic non-fix.

## Host-side objects that are not mounts

| Object | Placeholder | Why it matters |
|---|---|---|
| per-instance wrapper script | `<bin-dir>/openclaw-<instance>` | encodes site knowledge (env push/pull, tool staging, config env-refs). Wrappers drift between instances — a missing verb is finding `fleet.wrapper.drift`, never a licence to reimplement the verb |
| secret-store machine identity | `<identity-dir>/<project>.env`, mode 0600 | one identity file per instance; a wrong project id or a broken identity shows up as short secret delivery |
| shared tool tree | `<data-root>/shared/…` mounted read-only | shared CLIs; being read-only inside the container is intentional |
| plugin snapshots | `policy.snapshot_dir` | this plugin's own pre-mutation copies, kept outside the CLI's own `.bak` ring |

## Template versus legacy

`discovery.layout_profile()` decides from four markers: `state_mount`, `auth_secrets_mount`,
`compose_file`, `gateway_container`. The project prefix proves nothing — it matches a legacy instance
too.

| | template | legacy | alien |
|---|---|---|---|
| all four markers | yes | no — some are missing | irrelevant |
| looks like OpenClaw at all | yes | yes | no |
| config location | mounted state dir | often a home directory outside any mount | unknown |
| secrets | injected by the wrapper, referenced by name | frequently plaintext on disk | unknown |
| healthcheck, `cap_drop` | present | often absent | unknown |
| services per project | one gateway | may be several | unknown |
| this plugin | full maintenance | inventory and reads; every mutation refused | inventory row only |

A legacy instance is a migration project, not a maintenance target — red line
`legacy-instance-mutation`. Say that out loud rather than "fixing" it in place.

## Two traps in this layout

- **Silent legacy state-dir fallback.** When the configured state directory is absent, the resolver
  falls back to a legacy directory instead of failing. An instance can therefore be running happily on
  a directory nobody intended, and the config you edit is not the config it reads. Confirm the state
  dir from the mount table and from the running process, not from the compose file alone.
- **Ownership on bind mounts.** A shared tree whose owner does not match what the runtime expects is
  refused as a suspicious plugin candidate — the mount is there, the content is there, and the feature
  is silently off. Align ownership on the host side; do not chase it inside the container.
