# Execution contract

One door: `${CLAUDE_PLUGIN_ROOT}/scripts/ocexec.py`. Every OpenClaw CLI call in this plugin goes
through it, including the ones that look harmless. That is not ceremony — it is the only way the bans,
the risk classification and the output redaction can be enforced in one place instead of being
re-remembered at every call site.

```
ocexec.py <instance> [--mode auto|hot|cold] [--json] [--yes] [--timeout N]
          [--plan-id ID] [--plan FILE] [--lock-token T]
          [--service S] [--user U] [--image REF] [--no-infisical]
          [--config P] [--prefix P] [--dry-run] -- <openclaw args...>
```

`--dry-run` prints the exact command line it would run, after redaction — argv included, on both the
text and the JSON path. Use it whenever you are about to show a human what will happen.

## Why direct compose exec and not the site wrapper

1. **Wrappers drift.** On a fleet cloned from one template, a verb added later exists on some
   instances and not others. Code that depends on a wrapper verb works on five instances and fails on
   two, with a different error each time.
2. **The pass-through arm is the same call.** A wrapper's "run any CLI command" verb expands to the
   same `compose exec`. Going through it adds a failure mode and buys nothing.
3. **`-T` is not optional.** Without it the exec allocates a TTY, and a TTY corrupts `--json` output
   with control characters and wrapping. `ocexec.py` always passes `-T`.

The wrapper still owns the verbs that encode *site* knowledge — pushing and pulling env, staging
tools, rewriting config env references. Call those through the wrapper; never reimplement them.
A missing verb is a finding (`fleet.wrapper.drift`), not an invitation to write the logic here.

## Modes

| Mode | Command shape | When | Notes |
|---|---|---|---|
| `hot` | `docker compose -p <project> exec -T <service> <secret-wrapper> openclaw <argv>` | the instance is running | the default. Secrets are injected inside the container and never cross the boundary. If the image has no wrapper, the same call runs without it (`--no-infisical` forces that) |
| `cold` | `docker run --rm -v <state-dir>:/home/node/.openclaw <image> openclaw <argv>` | the instance is **down** | a cold container is not a gateway: no ports, no schedules, no channels. Only for the safe-on-broken subcommands |
| site verb | `<bin-dir>/openclaw-<instance> <verb>` | site-specific operations only | outside `ocexec.py` by design; see above |

`--mode auto` (the default) picks `hot` when the instance is running and `cold` when it is down;
an explicit mode that contradicts the state is refused rather than silently downgraded.

## Safe on a broken instance

Only `setup`, `qa`, `database` (`ocexec.SAFE_BROKEN`). They are the subcommands that do not assume a
live gateway, a resolved model chain or reachable channels. Anything else against a down instance is
refused with the reason, because the failure it produces is about the missing gateway, not about the
problem you are chasing — which is how a diagnosis session turns into an hour of chasing a red herring.

## Standing bans

| Banned | Why |
|---|---|
| `--accept-capabilities` in any argv | Upstream deliberately made `--yes` and the repair flag unable to approve capabilities. Automating consent removes the mechanism. `ocexec.py` refuses; the plugin **prints** the consent line for a human to run |
| `models status --probe` while the gateway runs | The probe needs the gateway stopped. Running it live is a lie dressed as a status read. Monitoring uses the check form, whose exit code carries the verdict |
| a cold container over the state dir of a **running** instance | Gateway startup enforces unique state-directory ownership. Two owners on one state dir is corruption, not contention |
| copying auth profiles between instances | OAuth credentials are not portable. API-key and static-token entries are; an OAuth entry copied elsewhere produces failures that look like expiry |
| a chat/completion request as a health check | Every such request creates a full agent session — it costs money, writes history, and can itself be what is broken. Use the health endpoint family |
| an auth mutation without the fleet front lock | The runtime's own serialisation lock is a file lock **inside one state dir** and serialises nothing across instances. `ocexec.py` takes the `fleet-auth` lock itself for any `models auth …` call (`gate.fleet_lock`); a multi-step procedure takes it around the whole sequence with `gate.py lock take fleet-auth` and passes the printed token as `--lock-token`, then `gate.py lock release fleet-auth --token …`. Busy prints the holder, the operation and the seconds left; `gate.py lock status fleet-auth` asks the same question |
| any call against an `alien` instance, or one with `manage:false` | The layout fingerprint failed, or the operator excluded it. Nothing here knows what that object is, so it stays an inventory row: reads of the host side are fine, its CLI is not run |
| anything but `setup`, `qa`, `database` in cold mode | A cold container is not a gateway; see "Safe on a broken instance" above |
| above R0 without `--yes` **in a later turn** | Reads are free, effects are not, and `--yes` is never added in the turn the command was first proposed |
| hand-written `docker exec` / `docker compose exec` | Bypasses redaction, risk classification and every ban above |

## Risk classes and what the door does with them

`ocexec.classify_argv()` labels the argv before anything runs.

| Class | Meaning | At the door |
|---|---|---|
| R0 | read with no observable effect | runs freely |
| R1 | read with an effect: costs money, holds a lock, moves state | needs `--yes` **and** the plan behind it |
| R2 | reversible change | needs `--yes` **and** the plan behind it |
| R3 | partially reversible: needs a backup that already exists | **refused** — belongs to a command that builds the eight-block plan |
| R4 | irreversible: needs a typed confirmation | **refused** — same reason |

The refusal of R3/R4 at the escape hatch is deliberate. The gate lives in the command layer; letting
the raw door perform them would put the most dangerous operations on the least supervised path.
A read subcommand carrying a write flag (`--fix`, `--force`, `--write`, `--set`, `--apply`) is
promoted to R2 regardless of its name — and so is any argv the read list does not recognise, which
is why an unknown verb cannot slip through as a read.

**"The plan behind it" is a thing, not a phrase.** Above R0 the door wants one of two proofs, because
`--yes` records that a human answered and nothing else: `--plan-id <command>/<instance>/<utc-stamp>`,
minted by a command that has already shown the eight blocks (the commands are repair, update, auth,
shared-sync, clone), or `--plan <file>`, the rendered plan as JSON, re-validated here for every block, a
BACKUP and an executable ROLLBACK (`gate.check_plan_authorises`). A `--dry-run` needs neither, and no
`--yes` either — it runs nothing, and it is how the plan's CHANGE and APPLY lines get written in the
first place. R3/R4 argv stays refused even as a dry run: that call belongs to a command that can collect
a backup and a typed confirmation.

### The plan id is a record, not a shape

A well-formed string is not an authorisation. Minting **writes a record** — command, instance, risk
class, a fingerprint of the plan it stands for, and an expiry — and the door reads it back
(`gate.make_plan_id` / `gate.check_plan_id`, registry under `policy.plan_dir`, else the `plans` sibling
of `policy.snapshot_dir`, else the XDG state home; files are mode 0600). Five ways a well-shaped id
still fails: it was never issued on this host, its short TTL (`gate.PLAN_TTL_SECONDS`, 30 min — a plan
describes state read at PRECHECK time) has passed, it was minted for another instance, it was minted for
a lower risk class than the call classifies as, or **it has already been used**: the door burns the
record when it applies, so one plan authorises one mutation and cannot be carried to the next change.

From a shell procedure the registry is the `plan` subcommand of the same module that owns the lock:

```bash
gate.py plan mint <command> <instance> --risk R2 [--plan rendered.json] [--ttl 1800]
gate.py plan check <plan-id> --for <instance> [--risk R2] [--consume]
gate.py plan list
```

## Output contract

- Both stdout and stderr pass through the redactor before you ever see them; the replacement count is
  visible, so a suppressed match is never invisible.
- `--json` parses **stdout only**. Merging stderr into the document is how a CLI update banner ends up
  inside a JSON value and every later parse fails with a misleading error.
- Exit codes carry meaning for a known set of commands (lint, post-upgrade, credential check, security
  audit): 0 clean, 1 error, 2 warn — and for the credential check, 1 expired, 2 expiring. For anything
  else, assume only the ordinary "0 is success" and read the payload.
- `ocexec.py` returns the child's exit code unchanged, plus its own: 64 refused by policy, 65 unknown
  or unusable instance, 66 docker unavailable.

## Repeat is worse than failure

For a set of operations the retry budget is **zero** (`gate.RETRY_RULES`): OAuth login and refresh,
version update, skill and plugin install, restart during a crash loop, secret write. One failure means
stop and inspect. A retry burns a single-use token, half-migrates a state directory, or overwrites the
log line that held the cause. When one of these fails, report the failure — do not run it again "to
see if it was transient".
