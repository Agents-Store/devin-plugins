---
name: memory-ops
description: Use when OpenClaw memory or its embeddings are involved — embedding calls failing authorization or reporting an invalid token, vector search paused or returning nothing useful, an index-identity warning, a last-index timestamp far in the past, search still poor after the provider was fixed, choosing or changing an embedding provider, model or key, a reindex, or a state database that keeps growing and needs retention or compaction. This skill owns the subscription-session-versus-embedding-key distinction; chat-side credential and OAuth problems are provider-auth.
---

# Memory operations

## How memory is put together

- Three retrieval paths over one store: **full text**, **vectors**, and a hybrid that merges both.
  Full text needs no provider; vectors need an embedding provider and are the part that breaks.
- The index lives **inside the instance's state directory**, in the same database as the rest of the
  state. It is per instance, it is not shareable, and it is included in a state-directory archive —
  which is also why that archive grows with it.
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
6. **Reindex explicitly**, one instance at a time, outside peak hours. Reindexing is the expensive
   part: it re-embeds the corpus, so it costs provider spend and competes with live traffic.

## Retention: an operator procedure with no upstream support

Say this out loud whenever it is proposed. The memory tables have **neither retention nor eviction**,
embeddings are stored as text, and the database grows without bound (`fleet.memory.db-growth`). There
is no supported command for this, so the procedure below is operator-owned and its risk is yours:

1. Back up the state directory (verified), and record what "search works" means before you start.
2. **Stop the gateway.** Editing a live store is how you get a corrupted one.
3. Delete old rows from the **embedding cache** only. The cache is regenerable by definition — that
   is the entire reason this is survivable. **Never touch the index or the chunk tables**; those are
   not regenerable without a full reindex.
4. Compact the database, or the space is not returned.
5. Start the gateway.
6. **Smoke test**: a query that must return vector hits. Not a health endpoint — those answer a
   different question and will be green either way.

Before planning it, check whether the database tooling exists in this image at all; if not, the work
runs in a one-off container over the stopped state directory (cold mode, `database` verb).

## Common mistakes

- Reading a key value to diagnose an authorization failure. Presence, fingerprint, size and expiry
  answer every question the value could, and the value cannot be un-printed.
- Re-running a login against an embeddings error — wrong credential class, and it burns a token.
- Changing provider, model or chunking and expecting search to recover on its own.
- Reloading instead of restarting after a provider is fixed.
- Deleting index or chunk rows during cleanup because they are the biggest ones.
- Compacting a running instance, or skipping the compaction and reporting freed space.
- Calling a reindex "cheap" — it is provider spend plus load, one instance at a time.
