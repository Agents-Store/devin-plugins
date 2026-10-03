---
name: memory-ops
description: Use when OpenClaw memory or its embeddings are involved — embedding calls failing authorization or reporting an invalid token, vector search paused or returning nothing useful, an index-identity warning, a last-index timestamp far in the past, search still poor after the provider was fixed, choosing or changing an embedding provider, model or key, a reindex, or a state database that keeps growing and needs retention or compaction. This skill owns the subscription-session-versus-embedding-key distinction; chat-side credential and OAuth problems are provider-auth.
---

# Memory operations

## How memory is put together

- Three retrieval paths over one store: **full text**, **vectors**, and a hybrid that merges both.
  Full text needs no provider; vectors need an embedding provider and are the part that breaks.
- The index lives in the **per-agent database** (`agents/<id>/agent/openclaw-agent.sqlite` under the
  state directory), beside that agent's sessions and transcripts — not in the shared state database.
  It is per agent and per instance, it is not shareable, and it is included in a state-directory
  archive — which is also why that archive grows with it. Because the database also holds canonical
  history, it is never deleted, nor are its `-wal` / `-shm` sidecars, to "reset" memory.
- **Memory commands are per agent.** `memory status`, `index` and `reset` without `--agent` run for
  every configured agent; `search` and `forget` default to the default agent only. Say which agent you
  mean: `--agent <id>` on every call.
- Text is **chunked** before embedding, and the chunking parameters are part of the index's identity
  (below), not a tuning knob you can change quietly.
- Reads may be accelerated by a separate read-only process against the same store; it is a reader,
  so it cannot repair anything, and it does not clear a stuck state.
- Current metrics — provider, model, last index time, database size — come from
  `${CLAUDE_PLUGIN_ROOT}/scripts/healthcheck.py <selector> --json`, never from memory.

## The one diagnostic idea worth carrying

**An "invalid token" error on an embedding call is not an expired key. It is a session credential
presented where an API key was required.** Subscription sign-in through a coding-CLI provider covers
chat completions and **does not satisfy embedding requests** — this is documented behaviour, not a
defect. The usual mechanism is that the embedding client inherits the OAuth profile configured for
chat instead of a key of its own.

Consequence for triage: an authorization failure on embeddings is almost never fixed by logging in
again. Do not re-run a login to test it — a repeated OAuth refresh burns a single-use token and logs
out another consumer. Read the embedding provider's configuration and ask a different question:
*which credential is this call actually presenting, and is it a key at all?*
(`fleet.memory.embeddings-unauthorized`; provider-by-provider in `references/embedding-providers.md`.)

## Index identity

The index carries an identity derived from **provider + model + chunking + the key in use**. Change
any one of them and the identity no longer matches what is stored:

- vector search **pauses** with an identity warning; it does not silently return wrong hits;
- reindexing is **explicit only** — nothing re-embeds by itself, no matter how long it waits;
- because the key is part of the identity, **rotating an embedding key forces a reindex everywhere
  it changed**, including instances where the key was "just replaced" with an equivalent one.

Plan a key change as a reindex programme, not as a config edit (`fleet.memory.index-identity-changed`).
Read the warning with `memory status --agent <id> --deep`, rebuild with
`memory index --force --agent <id>` (`memory status --index --agent <id>` rebuilds an incompatible
index too, and implies the deep probe — it is not a plain read). A full rebuild is built in a
temporary database and published atomically, and a failed rebuild leaves the published index intact —
so a reindex is an R3 for its **provider cost and load**, not for a risk of corrupting the index.

## Fail-closed is a feature

When a non-local embedding provider is configured explicitly, failures **fail closed**: no quiet
downgrade to full-text. That is the property that makes the whole subsystem observable — if
embeddings were failing and search silently degraded, nothing would ever tell you. So absence of
errors is real evidence that the vector path works (`fleet.memory.fail-closed-silent`).

The corollary: never "fix" a broken provider by removing it from the config. That converts a loud
failure into a silent one, and search quality drops with nobody watching.

## Stuck on the fallback

After a provider outage, search can stay on the fallback model **even once the provider is healthy
again**. A reload does not clear it; **only a full restart of the gateway does**. Any instance that
sat in a provider failure for a long stretch should be assumed stuck until a restart proves
otherwise — the "fix worked but search is still bad" report is this, nearly every time
(`fleet.memory.search-stuck-fallback`).

## Giving an instance its own embedding key

1. Snapshot the state directory first — this path ends in a reindex, which is R3.
2. Put a **per-instance** key in the secret store. A key shared across instances makes one revocation
   a fleet-wide outage and makes per-instance spend unattributable.
3. **Verify delivery by name, never by value.** Ask the container whether the environment name is
   populated and how long the value is; the value itself is never printed, logged, or read into
   context. A name that is referenced but not delivered is `fleet.secrets.delivery-short` — the
   feature is silently dead while the config looks correct.
4. Reference the secret **by name** in the config. A literal key in config is a leak the moment the
   config is backed up, diffed, or pasted.
5. **Full restart**, not a reload — see above.
6. **Reindex explicitly** (`memory index --force --agent <id>`, once per agent), one instance at a
   time, outside peak hours. Reindexing is the expensive part: it re-embeds the corpus, so it costs
   provider spend and competes with live traffic.

## Retention and size: use the supported tools

The embedding cache is **bounded** — the oldest entries are pruned in batches against an existing cap,
and a full rebuild trims it before publishing — but the database as a whole still grows with sessions,
transcripts and the index, and nothing in memory retention removes canonical history
(`fleet.memory.db-growth`). Start from `memory status --agent <id> --json`: database and WAL sizes,
reusable (free) bytes, retained cache payload and per-source chunk payloads. These figures overlap —
do not add them up, and a large file alone does not say which table is responsible.

The supported tools, each an **R3** (a verified backup shown in the plan first, the gateway stopped
where it says so):

| Need | Command | What it does and does not do |
|---|---|---|
| remove memory derived from chosen sessions, participants or sources | `memory forget --agent <id> …` — **`--dry-run` first** | deletes **immediately** with no prompt; transcripts are retained; this, not reset, is the privacy tool |
| discard the derived index and cache, then rebuild | `memory reset --agent <id> --yes`, then `memory index --agent <id>` | drops and recreates only memory-owned tables; sessions, transcripts and memory files are untouched; **does not shrink the file** |
| give the space back | `doctor --session-sqlite compact --session-sqlite-agent <id>` for an agent database, `doctor --state-sqlite compact` for the shared one | checkpoints, compacts and verifies integrity; needs **temporary disk space** and the gateway and other writers stopped, and they stay stopped through reset and compaction so indexing cannot refill the cache |

Order when both apply: verified backup → stop the gateway through its deployment owner → reset →
compact → start → reindex → a smoke query that must return vector hits (not a health endpoint, which is
green either way). If only free pages need reclaiming, skip the reset and keep the index.

**Hand-editing the tables is no longer a path.** Deleting cache rows with a SQL client was the
operator-owned procedure when nothing supported it; the commands above replace it, and a manual
`DELETE` is now outside upstream's support and an R4. Never delete the database file or its sidecars.

Before planning any of it, check that these verbs exist on this build (`--help`); if the gateway is
down, the database verbs run in a one-off container over the stopped state directory (cold mode —
`database` and `doctor` are the admitted verbs).

## Common mistakes

- Reading a key value to diagnose an authorization failure. Presence, fingerprint, size and expiry
  answer every question the value could, and the value cannot be un-printed.
- Re-running a login against an embeddings error — wrong credential class, and it burns a token.
- Changing provider, model or chunking and expecting search to recover on its own.
- Reloading instead of restarting after a provider is fixed.
- Deleting rows, or the database file, by hand when `memory reset`, `memory forget` and the compaction
  verbs exist — the file also holds the agent's canonical history.
- Running `memory forget` without `--dry-run` first: it deletes at once, with no prompt.
- Compacting a running instance, or skipping the compaction and reporting freed space.
- Calling a reindex "cheap" — it is provider spend plus load, one instance at a time.
