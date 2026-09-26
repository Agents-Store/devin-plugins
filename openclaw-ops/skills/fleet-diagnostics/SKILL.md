---
name: fleet-diagnostics
description: Use when an OpenClaw instance is misbehaving or suspected of it — health green but nothing is happening, a container restarting or unhealthy, an empty or ignored config, models returning unauthorized or reporting logged out, tokens that are present but empty, schedules failing or firing twice or stalling, memory search dead or paused or a state database growing without limit, keys missing inside the container, shared skills that look installed and do nothing, a version that does not match its siblings, or a port published where it should not be. Also use when a report, audit or repair needs a stable finding id.
---

# Fleet diagnostics

Symptom in, finding id out. This skill does not fix anything: it turns "something is wrong" into an id
from `references/findings-catalog.md`, which is what `/openclaw-ops:repair` accepts. A symptom without
an id is not repairable yet — add it to the catalog first, with a citation.

## Order of work

1. **State before symptom.** `${CLAUDE_PLUGIN_ROOT}/scripts/fleet.py discover --table`. A `down` instance explains most symptoms by
   itself, and half the checks below cannot run against it. An `alien` or unmanaged instance stops
   here: report it, do not investigate it as if it were yours.
2. **Split health from liveness** (the table below). Almost every silent failure in this deployment
   class lives in the gap between the two.
3. **Run the check named in the symptom table.** Every check here is R0. If a check needs `--yes`,
   it is not a check.
4. **Emit findings, not prose.** `{id, severity, instance, evidence}` — then the ready-to-run
   `/openclaw-ops:repair <instance> --issue <id>` line under each. `id` is a catalog id spelled
   exactly as the catalog spells it (or an upstream `checkId` carried verbatim); `severity` is one
   of `critical` `high` `warn` `info`, and nothing else.

## Rules while diagnosing

- **Never restart to diagnose.** A restart during a crash loop destroys the log lines holding the
  cause and buys a longer backoff. Read the log first — always.
- **Zero retries on anything auth-shaped.** A repeated login or refresh burns a single-use token and
  logs out another consumer. Diagnose by reading expiry and fingerprints from the profile.
- **Never look at a secret value.** Presence, fingerprint, size bucket, expiry and key name answer
  every question a value could. If the answer seems to need the value, the question is wrong.
- **The runtime is the authority on its own flags.** Subcommand spellings drift between versions;
  confirm against this instance's `--help` before quoting one. Anything about the *current* upstream
  version, flags or model names comes from the `docs-research` skill, never from memory.
- **Divergence between what the runtime documents and what upstream documents is a finding**, not an
  obstacle — an old instance ships old docs.

## Health is not liveness

Two verdicts from disjoint evidence, and the disagreement is the result. **HEALTH** is what the instance
says about itself — container state, `/healthz` `/startupz` `/readyz`, delivery queues, credential status,
the memory subsystem — and is blind to a process that answers every probe and does no work. **LIVENESS**
is what an outside observer sees it do — log age, last timer fire, last index write — and is blind to why
it stopped.

| Signal | Answers | Does not answer |
|---|---|---|
| container `running` / `healthy` | the process is up and its healthcheck passes | whether it does any work |
| `/healthz` | the HTTP server is alive | anything else |
| `/startupz` | startup finished | whether channels are healthy |
| `/readyz` | startup finished **and** channels passed a deep check | detail requires the bearer — without it you get a bare negative with no reason list |
| `health --json` `ok:true` | top-level rollup | that delivery queues are clear; check them explicitly |
| log movement, schedule fire times, session count | that work is happening | why it stopped |

The zombie is exactly this gap: green everywhere, silent for days. `policy.stale_log_hours` sets the
threshold; the check is log age plus schedule drift, never an HTTP probe.

## Symptom tables

Checks are shown as CLI intent, run through `${CLAUDE_PLUGIN_ROOT}/scripts/ocexec.py <instance> --json -- <args>`.

### Instance level

| Symptom | Likely cause | Check | Finding |
|---|---|---|---|
| green and healthy, nothing happens for days | zombie: secret delivery short, empty config, or work silently stopped | log age vs `policy.stale_log_hours`; `config get`; delivered key names | `fleet.liveness.zombie` |
| container restarting in a loop | startup repairs cannot complete safely — often the aftermath of an update | compose logs of the **first** failed start, not the latest | `fleet.upgrade.gateway-stopped` |
| container permanently unhealthy while the endpoint answers | healthcheck definition, not the app | `docker inspect` health log vs a direct `/healthz` | `fleet.liveness.health-vs-ready` |
| requests accepted, nothing delivered | delivery queues backed up behind a green rollup | `health --json`, queues explicitly | `fleet.liveness.queue-backlog` |
| config edits have no effect | the process reads a different state dir than the one you edited | mount table vs the running process's state dir | `fleet.inventory.state-dir-fallback` |
| config missing or nearly empty on a running instance | wiped or never written | `signals.config_present`, `config_bytes` | `fleet.config.empty` |

### Provider auth and the model chain

| Symptom | Likely cause | Check | Finding |
|---|---|---|---|
| "logged out" across several instances at once | token sink: separate credential copies of one account, each rotating a single-use refresh token | compare the account identifier **fingerprint** across credential directories | `fleet.auth.token-sink` |
| credentials present, tokens are empty strings, expiry zero | the same sink, after it fired | structure-only read of the credential file | `fleet.auth.emptied` |
| credential check exits non-zero | expired, expiring or missing | `models status --check` (1 expired, 2 expiring) | `fleet.auth.expired`, `fleet.auth.expiring` |
| billing moved to metered tokens with no config change | a static-token profile shadows the CLI backend for the same provider | `models auth list`, look for a token-mode profile | `fleet.auth.shadowed` |
| config names a CLI backend, requests fail immediately | the binary is not on PATH inside the container | `command -v` for the backend binary inside the container | `fleet.auth.orphan-runtime` |
| every request is slow before it succeeds | dead profiles still in rotation, each costing a retry and a cooldown | profile list vs which ones can still authenticate | `fleet.auth.dead-profile` |
| unauthorized right after an upgrade | migration rewrote the primary and dropped the runtime override | current config vs pre-upgrade snapshot | `fleet.model.primary-overwritten` |
| one agent ignores the fleet chain | a per-agent primary is strict when the agent has no fallbacks of its own | enumerate all three levels: default, per agent, per schedule | `fleet.model.agent-override-strict` |
| a schedule fails while everything else works | pinned to a model that no longer exists | schedule payload model vs `models list` | `fleet.model.cron-pinned-dead` |
| everything "works" but the bill and latency changed | the fleet lives on its fallback | count fallback and cooldown events over 24h | `fleet.model.fallback-burn` |
| a provider goes quiet for a long stretch | long backoff after billing failures | look for a disabled-until marker | `fleet.model.disabled-until` |

### Memory and embeddings

| Symptom | Likely cause | Check | Finding |
|---|---|---|---|
| every embedding call unauthorized | a session credential presented where an API key is required — subscription OAuth covers chat, not embeddings | embedding provider config plus the delivered key name | `fleet.memory.embeddings-unauthorized` |
| vector search paused, index-identity warning | provider, model or chunking changed, so the index identity no longer matches | `memory status` | `fleet.memory.index-identity-changed` |
| search returns nothing useful, last index long ago | indexing stopped when the provider broke | last index time vs activity | `fleet.memory.stale-index` |
| search still degraded after the provider was fixed | stuck on the fallback model; only a full restart clears it | compare behaviour before and after a full restart, not a reload | `fleet.memory.search-stuck-fallback` |
| state database growing without bound | no retention or LRU on chunk and embedding-cache tables | database size and per-table row counts | `fleet.memory.db-growth` |

### Schedules

| Symptom | Likely cause | Check | Finding |
|---|---|---|---|
| a job fires two or three times per tick | an upgrade duplicated the entries; copies stay enabled and lose their agent binding | group entries by name and schedule; look for empty agent bindings | `fleet.cron.duplicates-after-upgrade` |
| timers stall for hours nightly, then catch up | known upstream stall; the process stays active and green throughout | history of expected versus actual fire times — only an outside observer sees it | `fleet.cron.night-stall` |
| one timer stopped firing for good | a series of timeouts killed it | last fire time versus schedule | `fleet.cron.timer-dead-after-timeouts` |
| every job on an instance fails | not a scheduling problem — the model chain is dead | credential check first, schedules second | `fleet.cron.all-failing` |
| jobs exist in the file but the runtime has none | the migration into the store never ran | file entries versus `cron list` | `fleet.cron.migration-not-applied` |

### Secrets, shared assets, versions, security

| Symptom | Likely cause | Check | Finding |
|---|---|---|---|
| a feature is silently off, config looks right | a referenced key is not delivered | required reference names minus delivered names — names only | `fleet.secrets.delivery-short` |
| one instance gets far fewer keys than its siblings | wrong project id or a broken machine identity | delivered key count versus `secrets.expected_key_count` | `fleet.secrets.wrong-project` |
| plaintext keys in a file inside the state tree | leftover from before secret injection | fingerprint parity against the store decides redundant versus load-bearing | `fleet.secrets.plaintext-env` |
| a token or client id sits in a backup or identity copy | it has already leaked; hiding it is not a fix | scan for token-shaped values by class, never print them | `fleet.secrets.leaked-in-backup` |
| shared skill and plugin directories mounted, nothing loads | the shared trees are empty, or ownership on the bind mount is refused | list the shared trees from inside the container | `fleet.shared.empty-mount`, `fleet.shared.ownership-blocked` |
| shared copy edited, behaviour unchanged | extra directories are the **lowest** load priority; a local copy shadows the shared one | which path a loaded skill actually came from | `fleet.shared.local-shadow` |
| an installed skill is invisible | installed by copying without registering | registered list versus files on disk | `fleet.shared.install-global-invisible` |
| a plugin change did not take effect | plugin load paths require a restart | config change time versus process start time | `fleet.shared.plugins-load-no-restart` |
| instances on different versions | drift; nobody upgrades the whole fleet at once | `--version` per instance | `fleet.version.drift` |
| what is running is not what was reviewed | pinned to a moving tag, rebuilt on its own schedule | image reference versus its digest | `fleet.version.moving-tag-pin` |
| gateway port reachable from outside the host | images publish outward by default; published ports bypass the ordinary firewall chain | `port.loopback`, then the container-aware chain | `fleet.security.port-non-loopback`, `fleet.security.docker-user-chain` |
| one operator token works on several instances | the trust boundary is per gateway, and access is all-or-nothing | fingerprint the token per instance, compare | `fleet.security.token-reuse` |

## When to escalate

- More than one instance, or more than one axis → `/openclaw-ops:audit` (the auditor agent walks every
  axis and returns one prioritised report).
- One instance, deep and unclear → the incident-responder agent.
- Neither agent mutates anything. If a walkthrough proposes a change, it comes back as a finding id and
  a `/openclaw-ops:repair` line for a human to approve.

`references/findings-catalog.md` — every id with severity, detection, fix, verification and mutation
class. It is one id space with the battery, not a parallel one, and that is checked rather than
trusted: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/catalog-check.py"` fails if `healthcheck.py` can
emit an id the catalog does not declare, or a severity its row disagrees with. `references/upstream-issues.md` — known upstream behaviour: what the symptom looks like, what
causes it, and what it means for operating the fleet.
