---
name: config-surgery
description: Use when an OpenClaw instance config is about to be read, changed, restored, split or explained — a model chain, channel, tool, plugin, skill, session or memory setting, a secret reference, an include, a gateway that refuses to start after an edit, a config the process appears to ignore, a change that looks applied and has no effect, an edit that removes lines, a stray backup or rejected sidecar file next to the config, or the question of what needs a restart.
---

# Config surgery

How an instance config is changed without taking the gateway down. Field map:
`references/config-reference.md`. The runtime's own schema is the authority; this page is the
procedure around it.

## What the file is

- One config per instance at `paths.config_file` — the state directory plus the config file name,
  read from the mount table, never from memory. Confirm the running process reads that same directory
  before editing: the resolver falls back to a legacy directory when the configured one is absent
  (`fleet.inventory.state-dir-fallback`), and then the file you edit is not the file it reads.
- **JSON5.** Comments and trailing commas are legal and carry operator intent. A parse-and-rewrite
  through an ordinary JSON writer deletes every comment in the file and reports it as formatting.
- **Strict schema.** An unknown key does not warn — the gateway refuses to start. `$schema` is the
  only non-schema root key. A mistyped key name is an outage that arrives at the next restart, far
  from the edit that caused it.
- **Not a symlink.** The loader refuses a symlinked config path. Configs are never shared by linking;
  composition is what includes are for.
- **Secret references by name only.** A literal value is `fleet.config.literal-secret` and stays
  critical after removal — it has been on disk, so it is rotated, not just deleted.
- `${UPPERCASE}` substitution applies to string values and to uppercase names only. A lowercase name
  is not an error: it stays literal, and the feature silently runs on nonsense.

## The sequence — every edit, no exceptions

1. **Read through the runtime**, not off the filesystem. You need the composed view with includes
   resolved, and the base hash of what you are about to change.
2. **Diff, and count deletions.** A non-zero deletion count in a config diff is a finding of its own
   (`fleet.config.deletions`) and belongs in the plan's CHANGE block, not in a footnote.
3. **Snapshot outside the ring** — `gate.snapshot()` into `policy.snapshot_dir`, fingerprint recorded,
   then name the ring slot this edit will evict (`gate.bak_ring_warning()`).
4. **Apply as a patch carrying the base hash** of the version you read — the runtime's own
   config write path, never a read-modify-write of the file, and never in the same turn the
   plan was first shown. Confirm the verb from `--help` on this instance; what makes it the
   right mechanism is that the write is refused when the file moved underneath you.
5. **Validate twice:** it parses, then `doctor --lint --json` shows no *new* findings. Comparing
   against a baseline matters — on a fleet with standing findings, an absolute gate blocks every edit
   forever and gets switched off.
6. **Reload or restart** per the table below. Guessing here is how a change is "applied" for a week
   without ever taking effect.
7. **Verify from the runtime:** `config get <path>` returns what the process holds. A changed file
   proves the write landed and nothing more.

A config edit is R2; one that removes a section or rewrites the model chain is planned as R3.

## Never delete a section

Additive edits only. Under a strict schema an unrecognised block is far more likely to be load-bearing
for a feature you have not met than to be leftovers, and removal fails at the next restart rather than
at the edit. Removing a key is a separate operation carrying its own justification in the plan — never
a side effect of tidying up while you were in there.

## The backup ring belongs to the human

The CLI keeps its own shallow numbered ring beside the config. It is a person's undo: the copy they
took before the change they were nervous about. A few automated edits in a row evict it silently.
Hence the plugin's own snapshot outside the ring, before the first edit of a session, and the line in
the plan naming the slot about to fall off the end (`fleet.config.bak-ring-pressure`).

## Concurrent writers: base hash and the sidecars

The gateway writes this file too — migration, self-repair, the reload machinery. Read-modify-write
against a live process is a race, and the loser loses silently.

- A patch carrying the **base hash** of the version you read is refused when the file moved underneath
  you instead of overwriting the other writer. The refusal is the feature.
- A `.rejected` or `.clobbered` sidecar next to the config means a write already lost that race. Read
  it: it holds what was refused or what was overwritten. **Do not delete it and do not re-run the
  write to clear the warning** — re-read the current config and rebuild the patch on top.
- Everything with a `.bak`, `.rejected` or `.clobbered` suffix is evidence. Move it aside, never `rm`.

## Includes and write-through

Includes compose at **read** time: the loader merges the tree into one view, to a bounded depth, and a
broken include fails the load rather than being skipped. Writes do not travel back along that path — a
programmatic write lands in the **root** file.

So patching a key that came from an include produces a root-level copy that shadows it. The include
still exists, still says the old thing, and the next reader believes the wrong file. Rule: **edit the
file that defines the key.** When the writer cannot target that file, edit the include by hand under
the same sequence — snapshot, validate, verify from the runtime.

## What hot-applies and what needs a restart

| Change | What happens |
|---|---|
| most agent, channel, tool, session and skill fields | hot-applies |
| anything under `gateway.*` — bind, port, auth, the reload mode itself | restart |
| plugin load paths | restart: the loader walks those paths at startup only |
| a secret whose **value** changed in the store | restart the process — injected env is read once, at start |
| embedding provider, model or chunking | applies, then pauses vector search with an index-identity warning until an explicit reindex |
| anything while search is stuck on a fallback model | full restart, not a reload — a reload does not clear it |

The reload mode is itself configurable (hot, restart, hybrid, off), so what a given instance does on
change is one `config get` away. Never assume a default.

## Common mistakes

| Mistake | What it costs |
|---|---|
| a plain file write while the gateway is running | loses comments, loses the race, and edits the composed view instead of the defining file |
| copying a config from a sibling instance | carries port, workspace and state paths that must be unique — isolation breaks at the next start |
| reaching for the repair flag to clean it up | R4 and a red line; it rewrites what it does not understand |
| removing a key nobody recognises | the gateway refuses to start, at the next restart, detached from the edit |
| a model id typed from memory | `fleet.config.model-id-unverified` — every id entering a diff is an echo from this instance's catalogue |
| editing inside the container outside a mount | reverted by the next `up`: the classic non-fix |
| calling it done because the file changed | the process may hold something else entirely — `config get` decides |
