# Scenario: the whole fleet is logged out

Symptom as reported: "scheduled jobs stopped working everywhere, and the model keeps falling back".
Symptom as measured: the credential check fails on five of six instances, one is still healthy, and
its remaining validity is measured in days.

This is the scenario where the instinctive next action — log in again, or refresh — is the one that
makes it permanently worse.

## Step 0 — the rule that comes before the diagnosis

**Zero retries on an OAuth refresh or login** (`gate.RETRY_RULES`). A refresh token is single-use and
rotates; a second attempt burns the one that another consumer is still holding. One failure is a
diagnosis, not an invitation to try again.

So the diagnosis is done entirely from **metadata**, and never by exercising the credential.

## Step 1 — measure, four independent signals

| Run | Reads | Why this one |
|---|---|---|
| `${CLAUDE_PLUGIN_ROOT}/scripts/ocexec.py <instance> --json -- models status --check` | exit 0 healthy, 1 expired, 2 expiring | the only exit contract with that meaning (`ocjson.EXIT_CONTRACTS`) |
| structure-only read of the native credential file | provider, mode, `expiresAt`, presence | `redact.structure_only` returns shape and fingerprints; values never enter the transcript |
| the CLI's own status inside the container, with the config-directory variable set **explicitly** | what the CLI believes | the variable is not inherited by subprocesses — a known upstream bug, and the reason "the credentials are mounted, why is it not logged in" |
| optional: one single-token request | that the chain actually completes | costs money; run last, once, never as a loop |

`models status --probe` is not on that list. It requires a **stopped** gateway; running it against a
live one is refused by `ocexec` (`provider-auth`).

Classification for each instance: `healthy` · `expiring` · `expired` · `emptied` (block present, tokens
are empty strings) · `absent` · `orphan-runtime` (config names a CLI backend, the binary is not
mounted) · `shadowed` (a static-token profile for the same provider outranks the CLI backend, and the
spend quietly moves to metered tokens).

Observed here: four `emptied`, one `expired`, one `healthy`, one `shadowed` on top of that.

## Step 2 — the root cause is architectural, and the evidence is a fingerprint

Four instances did not independently expire on the same day. Compare the **account identifier**
across every credential directory — as a fingerprint, never as a value. The values below are synthetic
stubs, not captured output; a real fingerprint is eight hex digits of a digest:

```
alpha  fp:0000aaaa
beta   fp:0000aaaa
gamma  fp:0000aaaa
delta  fp:0000aaaa
```

One account, four separate credential directories, four independent refresh chains. The provider
issues a new refresh token on every refresh and invalidates the previous one; the serialisation lock
is a **file lock local to each state directory**, so it cannot serialise anything across directories.
Whichever instance refreshed last is the one that still works, and it logged out the other three.

Finding: `fleet.auth.token-sink`, verdict "architectural, not expiry". A re-login fixes one instance
for a few hours and starts the same race again.

This is not provider-specific: any OAuth implementation with refresh-token rotation and reuse
detection behaves this way when several holders share one chain.

## Step 3 — the target shape

**One owner per refresh chain.** Every other consumer re-reads, none of them refreshes.

| Change | Why exactly this |
|---|---|
| one host directory mounted into every container as the CLI's home | one chain, one writer; the runtime never reads, stores, refreshes or forwards the native tokens — the installed CLI refreshes itself |
| mount the **directory**, never the credential file | the CLI rewrites credentials atomically via rename; the inode is replaced, and a single-file bind mount freezes on the old one |
| the per-instance CLI state file stays per instance | sharing it leaks project state and onboarding between instances |
| persist **all** of the CLI's paths, not just the two that are already mounted | a missing one produces a login that looks fine and does not survive a restart |
| align ownership on the bind mount | a mismatched owner is a documented blocked-candidate error, not a permissions curiosity |

Isolation is not violated by this: the uniqueness requirements are the config path, the state
directory, the workspace and the gateway port. Credential directories are not on that list.

**The cost, stated in the report rather than discovered later**: one shared blast radius — a single
session revocation logs out the whole fleet — and shared rate limits. Undoing it is re-splitting the
mount, which is why it is written down at decision time.

## Step 4 — apply it, canary first

The compose patch is R2 with an R3 precondition: a restart on an instance whose secret delivery is
broken turns a working instance into a dead one, so the precheck resolves every secret reference **by
name** first and shows the result in the dry-run (`secrets-infisical`).

```
/openclaw-ops:repair beta --issue fleet.auth.token-sink          # dry-run, eight blocks
/openclaw-ops:repair beta --issue fleet.auth.token-sink --yes    # a later turn, never the same one
```

The canary barrier stops after `beta` and shows the result. Continuing to the rest is a separate
confirmation. Direction is good-to-changed, so the batch is **fail-fast**: a failure on the second
instance stops the run, because a half-converted fleet is described by no document and covered by no
rollback.

`legacy-one` is refused and the refusal says why. `delta` is a zombie and is triaged before it is
changed, not after.

## Step 5 — the logins are printed, not executed

The plugin prints, a human runs. Three reasons: the callback is local to the process that starts the
login, the flow is interactive, and the retry budget is zero.

The printed block covers: log in on the host as the owner of the shared directory, fix ownership on
the mount afterwards, then register the backend on **each** instance so the runtime routes through the
local CLI rather than an embedded key.

Then remove the shadows, or the chain will not take effect: the static-token profile that outranks the
CLI backend (`fleet.auth.shadowed`), and every dead profile (`fleet.auth.dead-profile`) — profile
rotation inside a provider happens **before** the move to the next model, so each dead profile buys a
retry-and-cooldown cycle on every request.

## Step 6 — verify across a rotation, not across a minute

| Check | Passing looks like |
|---|---|
| credential check on every instance | exit 0 |
| the same check an hour later, after at least one refresh | still 0 **everywhere** — this is the whole point |
| fallback and cooldown events over a full day | near zero (`fleet.model.fallback-burn`) |
| scheduled jobs | the group that was failing completes |
| account fingerprint | one value, and it is the expected one — a change means someone logged in with a different account (`fleet.auth.account-drift`) |

A green check immediately after a login proves the login worked. Only the check that survives a
rotation proves the **sink** is gone. A fleet that formally has a chain and actually lives on its
reserve looks identical to a healthy one until the invoice arrives.

## Common mistakes in this scenario

- Re-running the login when the first attempt failed. One failure, then stop.
- Copying a credential directory to the instances that lost it — that is the defect, reproduced by
  hand (`fleet.auth.oauth-copied`). A static key or token is portable; an OAuth profile is not.
- Fixing the chain while the dead primary is still first. Demote it, or every request pays the cooldown
  ladder and the scheduled jobs keep failing while the credentials are perfect.
- Declaring victory on the credential check alone, without ever looking at the fallback counters.
