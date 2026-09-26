# Provider matrix

Backends by **shape** rather than by brand: what each authenticates with, who owns its refresh, what
the container has to persist for it, how it is diagnosed without spending a token, and what repairs
it. `SKILL.md` carries the rules; this page carries the per-backend detail.

## Resolve the identifiers on the box, every time

Provider ids, runtime ids and model refs are **read from the instance, never remembered**. They are
the exact strings that end up in a config, and a stale one is either a silent no-op or — under the
strict schema — a gateway that refuses to start. Four reads, all R0, none of which touches a token:

| Question | Read |
|---|---|
| which providers have profiles here, in what mode, with what expiry | the auth-profile listing, `--json` |
| which refs does this runtime actually serve | the model catalogue, `--json` |
| which runtime ids exist for a CLI backend | the runtime's own `--help` and its documentation page |
| what does this instance hold right now | `config get agents.defaults.model`, then the models map |

All four go through `${CLAUDE_PLUGIN_ROOT}/scripts/ocexec.py <instance> --json -- <args>`. Subcommand
spellings drift between versions — confirm one with `--help` before quoting it, and treat any ref you
did not just read as unverified (`fleet.config.model-id-unverified`).

## The canonical shape in config

<!-- example-only -->
```json5
{ model:  { primary: "<provider>/<model-id>", fallbacks: ["<provider>/<model-id>"] },
  models: { "<provider>/<model-id>": { agentRuntime: { id: "<runtime-id>" } } } }
```

Under the agent defaults. The chain names provider refs; the entry for each ref names the runtime that
serves it. The placeholders stay placeholders: every ref written into a config is read back from the
catalogue first, and the legacy form fusing runtime and model into one ref is migration input, never a
template (`fleet.config.legacy-model-ref`). A per-agent override with its own primary and no fallbacks
of its own is **strict** — it cancels the fleet chain for that agent (`fleet.model.agent-override-strict`),
and a schedule pinning a model the catalogue no longer lists fails on a timer nobody watches
(`fleet.model.cron-pinned-dead`). Inventory all three levels, not just the default.

## The four credential shapes

| Shape | Refresh | Portable between instances | Expires | Refresh owner | Failure signature |
|---|---|---|---|---|---|
| **API key** | none | yes | only on revocation | the secret store | unauthorized immediately and permanently, identically everywhere the key is delivered |
| **Provider OAuth held by the runtime** | single-use, rotating | **no** | yes | whichever runtime process refreshed last | unauthorized in *waves*, on instances that were working, with no config change |
| **Static token profile** | none | yes | usually never | whoever pasted it | none — which is the problem: it outlives and shadows the login you meant to use |
| **External CLI native login** | performed by the CLI itself | **no** | yes | the CLI process reading that credential directory | the CLI reports itself not logged in; the gateway reports the backend unusable |

The rule falls straight out of the table: **the only shape that survives being shared across
containers is the one where a single external process owns the refresh and everyone else re-reads.**
Copies of the OAuth shapes across separate state directories are racers, and the race is decided by
whoever refreshes last (`fleet.auth.token-sink`).

## Backend matrix

Rows are identified by the mount destination the backend reads, because that is unambiguous and
version-stable, unlike an id spelling.

| Backend | Accepts | Refresh owner | Must be mounted | Diagnosed with | Repaired by |
|---|---|---|---|---|---|
| CLI backend at `/home/node/.claude` (chain primary in this shape) | its own native login | the CLI | credential dir, data dir, binary dir; per-instance project state | credential check, structure-only read of the stored credential, CLI status inside the container with its config-dir variable set explicitly | one owner directory mounted everywhere; login printed for a human |
| CLI backend at `/home/node/.codex` (chain fallback) | native login, or an API key in embedded mode | the CLI when in CLI mode, nobody when in key mode | credential dir; the binary or its shim resolvable on `PATH` | same ladder | same; plus deleting the legacy combined-id profile if one is still present |
| A consumer CLI whose OAuth route the vendor withdrew | nothing new — the runtime no longer offers that login | — | — | the profile still lists, and every request fails or the ref never resolves | remove the profiles and the chain entries together (`fleet.auth.dead-profile`); the replacement route comes from `docs-research`, not from here |
| Embedded HTTP with an API key | key by **reference**, delivered by the injection wrapper | no refresh exists | nothing | delivery by name and fingerprint, never by value | fix delivery (`fleet.secrets.delivery-short`), or rotate the key at the vendor |
| Embedded HTTP with provider OAuth stored by the runtime | interactive login, stored encrypted under the auth-secrets key | the runtime, under a lock **local to one state directory** | the auth-secrets directory, per instance | credential check plus expiry from the profile store | login on that instance; never copy the profile to a sibling (`fleet.auth.oauth-copied`) |
| Local or self-hosted endpoint | usually nothing | — | nothing, unless the model files are mounted | connection and model presence, not authentication | it is a capacity problem, not a credential one |
| The embedding lane | its **own** key, per instance | no refresh | nothing | delivery by name; index identity | out of scope here — owned by `memory-ops` |

Notes the table cannot hold:

- **The CLI backends are the reason this deployment shape exists.** The gateway never reads, stores,
  refreshes or forwards their native tokens — it shells out, and the CLI refreshes its own login.
  That is what makes one shared owner directory correct rather than a hack.
- **A legacy combined profile id** (runtime and provider fused into one) is documented as *migration
  input only*: it still resolves, and new profiles are never created in that form.
- **Embedded and CLI paths for the same provider compete.** A static-token profile for a provider
  whose chain intends the CLI wins silently, moves billing to metered tokens, and changes no config
  (`fleet.auth.shadowed`).

## What the container has to persist

Roles as the mount table reports them. Host paths are per deployment; the destinations are fixed.

| Role | Destination | Shared across the fleet? | What breaks when it is missing |
|---|---|---|---|
| `state_dir` | `/home/node/.openclaw` | **never** — unique ownership is enforced at startup | everything; a resolver that finds no state directory falls back to a legacy one silently |
| `auth_secrets` | `/home/node/.config/openclaw` | **never** | the key that encrypts stored profiles. Sharing it makes profiles cross-readable; copying it is how OAuth material gets cloned by accident |
| `claude_dir` | `/home/node/.claude` | **yes** — this is the owner directory | the login does not stick, or every instance keeps its own racing copy |
| `claude_share` | `/home/node/.local/share/claude` | yes, with the credential directory | login appears to succeed and is gone after a restart |
| `claude_local_bin` | `/home/node/.local/bin` | yes, with the credential directory | the CLI cannot install or update itself; later, a version mismatch nobody expects |
| `claude_json` | `/home/node/.claude.json` | **no** — per instance | project state, registrations and onboarding flags leak between instances when shared |
| `codex_home` | `/home/node/.codex` | yes, same reasoning as the credential directory | second link of the chain unusable |

Two mount rules that are not obvious:

- **Mount the directory, not the credential file.** The CLI rewrites credentials atomically — write a
  temp file, rename over the target — which replaces the inode. A single-file bind mount stays
  attached to the old inode and freezes at the first rotation, silently, while the host file moves on.
- **A single-file mount that must exist anyway** (per-instance project state is the usual one) carries
  that same risk by construction. Verify it from **inside** the container rather than from the host:
  what the CLI reads is the only thing that counts.

Isolation is not weakened by any of this. Uniqueness is required on the config path, the state
directory, the workspace and the gateway port — credential directories are deliberately not on that
list. The price is stated in `SKILL.md`: one blast radius, one rate limit.

## Diagnosing a state without spending a token

| State | The read that proves it | The wrong move it invites |
|---|---|---|
| healthy | credential check exits 0, expiry well ahead | none |
| expiring | check exits 2, or expiry inside the window | refreshing from several places at once — one touch, from the owner directory, under a fleet-level front lock |
| expired | check exits 1 | logging in again per instance: it holds until the next rotation, then the same wave |
| emptied | structure-only read: block present, token strings empty, expiry zero | reading the file raw "to see what is in there" — the shape already answered |
| absent | no profile for a provider the chain names | adding a key to make the error stop, when the chain wanted the CLI |
| orphan-runtime | the binary is not resolvable inside the container | blaming the credential; the gateway must resolve the runtime on `PATH` |
| shadowed | a static-token profile exists for a provider whose chain intends the CLI | investigating the bill instead of the profile list |

The probe form of the status command requires the gateway **stopped** and is therefore banned on a
live instance; `ocexec.py` refuses it. And the CLI's own not-logged-in message inside a container is,
far more often than not, about its config-directory variable not being inherited by the subprocess —
not about the credential.

**Zero retries anywhere in this family** (`gate.RETRY_RULES`). A repeated login or refresh burns a
single-use token and logs out whoever was working.

## What is printed for a human, never executed

The login is interactive by design and its callback is served by the login process itself on a
loopback port, which nothing inside a container can reach. So the plugin prints, in this order:

1. the host-side login command, with the credential directory pointed at the **owner** directory;
2. the loopback callback forwarding line, for a login driven from a workstation;
3. the ownership alignment for the mounted directory, so the container-side user can read it —
   the mirror image of the ownership refusal that blocks assets on bind mounts;
4. the registration command, run once **per instance**, that points the model at the CLI backend;
5. the headless fallback: paste the full redirect URL back into the prompt.

Capability consent lines are printed for the same reason — bulk-approval flags deliberately cannot
grant them, and automating that away destroys the mechanism.

## Standing rules

- Never copy an OAuth profile between instances; key and static-token entries are portable, OAuth
  entries are not, and a copy authenticates for a while before failing as something else.
- Never share `auth_secrets` or `state_dir`. Share the CLI's own directories, nothing else.
- Never read a credential value. Presence, fingerprint, expiry and key name answer every question a
  value could, and the fingerprint is the only one of them that detects a shared account.
- Never leave a dead profile in the rotation: profiles rotate **before** the chain moves to the next
  model, so each dead one costs a retry plus a cooldown on every request.
- Never point the embedding lane at a subscription session — why, and how it presents, is `memory-ops`.
