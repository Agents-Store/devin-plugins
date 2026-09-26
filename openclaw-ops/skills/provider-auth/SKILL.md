---
name: provider-auth
description: Use when model-provider credentials are in question — unauthorized responses, an instance reporting itself logged out, tokens present but empty, an expiry approaching or passed, several instances losing the same account at once, a login that has to be performed, a choice between an API key, provider OAuth and a local CLI backend, billing that moved to metered tokens without a config change, a provider CLI reporting not-logged-in inside its container, or credential directories being shared, split or copied between instances. Embedding and vector-search failures are memory-ops, not this skill.
---

# Provider auth

The most expensive failure class in this deployment shape: invisible until every schedule on the fleet
fails at once. Per-provider detail: `references/provider-matrix.md`.

## Four layers, never conflated

| Layer | Question | Where it lives |
|---|---|---|
| provider | who authenticates, with what kind of credential | auth profiles + native credential directories |
| model | what is being asked for | the model ref in the chain |
| agent runtime | which local process makes the call — embedded HTTP, or a provider CLI | `agentRuntime.id` on the model entry |
| channel | where the conversation arrived from | `channels.*` |

Most "auth" incidents are a layer error: the credential is fine and a second profile is winning, or the
model is fine and the runtime binary is missing. Name the layer before touching anything.

## Canonical form — provider ref plus runtime override

The chain names `<provider>/<model-id>` refs, and the entry for each ref names the runtime that serves
it (`agentRuntime.id`); the exact shape is in the reference. The legacy form fusing runtime and model
into one ref still resolves, so it is drift, not an outage (`fleet.config.legacy-model-ref`) — but new
config is written the canonical way, because the migration that rewrites the old form drops the runtime
override and produces a session error days later (`fleet.model.primary-overwritten`). Every
`<model-id>` is an echo from this instance's catalogue.

## One owner per refresh chain

Refresh tokens are **single-use**: each refresh mints a new one and invalidates its predecessor, and
presenting the old one reads as theft rather than as a retry. The runtime serialises refreshes with a
**file lock inside one state directory**, which serialises nothing across two state directories. So N
copies of one account are N racers — the last to refresh stays logged in, the rest get logged out in
waves, whenever they happen to refresh.

**Each refresh chain gets exactly one owner; everyone else re-reads.** For a CLI backend the owner is
documented to be the CLI itself: the gateway never reads, stores, refreshes or forwards native login
tokens — it shells out, and the CLI refreshes its own login. The fix is a **mount**, not a copy.

## Profile states

| State | Looks like | Means | Finding |
|---|---|---|---|
| healthy | check exits 0, expiry well ahead | nothing to do | — |
| expiring | check exits 2, or expiry inside the window | one touch refresh, from the owner directory, under a fleet-level front lock | `fleet.auth.expiring` |
| expired | check exits 1 | a human logs in; demote the dead entry meanwhile | `fleet.auth.expired` |
| **emptied** | block present, token strings empty, expiry zero | the sink already fired here | `fleet.auth.emptied` |
| absent | no profile for a provider the chain names | never set up, or removed | `fleet.auth.expired` family |
| **orphan-runtime** | config names a CLI backend whose binary is unresolvable in the container | requests fail instantly; the gateway must resolve it on PATH | `fleet.auth.orphan-runtime` |
| **shadowed** | a static-token profile exists for a provider whose chain intends the CLI | that profile has no refresh, so it never expires and quietly outlives the login it shadows: the embedded path wins, billing moves to metered tokens, config unchanged | `fleet.auth.shadowed` |

## Diagnose without the probe

The probe form requires the gateway **stopped**, so on a live instance it is refused. Four signals,
none of which triggers a refresh:

1. The credential **check** — exit 1 expired, 2 expiring. Cheapest, run it first.
2. A **structure-only** read of the stored credential — presence, fingerprints, expiry.
   `redact.structure_only()` returns the same shape with values replaced; never read it raw.
3. The CLI's own status **inside** the container, with its credential directory passed explicitly:
   that variable is not inherited by the subprocess, so good mounted credentials read as logged out.
4. One single-token request — an explicit priced step, never a routine check.

**Zero retries across all of it** (`gate.RETRY_RULES`): a repeated login or refresh burns the
single-use token and logs out whoever was working.

**The front lock is a lock, not an intention.** Every credential mutation runs under
`gate.fleet_lock` (`fleet-auth`): `ocexec.py` takes it for any `models auth …` call, and a multi-step
procedure takes it around the whole sequence with
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lib/gate.py" lock take fleet-auth`, passes the printed token
to each call as `--lock-token`, and releases it with `lock release fleet-auth --token …`. It exists
because the runtime's own lock is a file lock inside one state directory: it cannot see the second
instance refreshing the same rotating token. Held locks expire on their own, so a crashed procedure
does not wedge the fleet; busy prints who holds it and for how long.

## Root-cause detector

Compare the **account identifier fingerprint** across every credential directory on the host. One
fingerprint in several directories → token sink: architectural, not expiry, and a fresh login holds
only until the next rotation (`fleet.auth.token-sink`). Different fingerprints where one account was
intended → somebody logged in with another (`fleet.auth.account-drift`). Identical OAuth material on
two instances → a copied profile; key and token entries are portable, OAuth is not (`fleet.auth.oauth-copied`).

## The shared credential directory

One host directory per chain, mounted into every container at the destination the CLI reads. Mount
table, per role: `references/provider-matrix.md`.

- **Mount the directory, not the file** — the CLI rewrites credentials atomically, replacing the inode,
  and a single-file mount freezes on the old one. Persist every path the CLI owns, not just this one.
- **Per instance regardless:** project state, registrations, onboarding flags, and the key that
  encrypts stored profiles — sharing those leaks state, copying them clones OAuth material.
- **Isolation is not violated:** uniqueness is required on config path, state directory, workspace and
  gateway port; credential directories are deliberately not on that list.
- **The cost, said out loud:** one blast radius, one rate limit. Revoking that session logs out the
  whole fleet, and splitting back re-creates a racer per split.

## Dead profiles are not free

Rotation walks **every profile of a provider before moving to the next model in the chain**, so a dead
profile costs a retry plus a cooldown on every request, permanently, and reads as "slow but working"
rather than as an error (`fleet.auth.dead-profile`). Delete them; demote a dead primary meanwhile.

## Logins are printed, never run

The plugin prints the exact command for a human and does not execute it: consent is interactive by
design, and the OAuth callback is served **by the login process itself** on a loopback port that
nothing inside a container can reach. Five parts, printed in this order:

1. the host-side login pointed at the **owner** credential directory;
2. the loopback forwarding line, for a login driven from a workstation rather than a shell on the host —
   the callback port only exists on the machine running the login, so it has to be tunnelled there;
3. the ownership alignment on the mounted directory, run on the host side;
4. the per-instance registration that points the model at the CLI backend, on **each** instance;
5. the headless fallback — paste the full redirect URL back into the prompt.
Capability consent lines are printed for the same reason — bulk-approval flags cannot grant them.

One provider's consumer CLI OAuth route was withdrawn by its vendor and the runtime no longer offers
that login; profiles of that shape are legacy. That is a statement about the past — what replaces it
today comes from `docs-research` against current documentation, not from this page.

## Common mistakes

| Mistake | What happens |
|---|---|
| logging in again to fix a fleet-wide logout | holds until the next rotation, then the same wave. Fix ownership instead |
| copying a working profile onto the other instances | OAuth material is not portable; failures arrive later and look like expiry |
| retrying a failed refresh | burns the single-use token and logs out another consumer |
| reading a token value to check it | answers nothing that fingerprint, presence and expiry do not |
| pointing embeddings at a subscription session | wrong credential class — the mechanism and the triage are `memory-ops` |
