---
name: cli-reference
description: This skill should be used when the user asks for the "restic command reference", "all restic commands", "restic flags", "restic environment variables", "restic exit codes", or needs the full command/flag/env-var reference for restic.
disable-model-invocation: true
---

# restic CLI Reference

Complete command, flag, and environment-variable reference. For task-oriented usage see `setup`, `repository-setup`, `backup-script`, `verify-backup`, `disaster-recovery`, and `troubleshoot`. Full docs: https://restic.readthedocs.io/

## Global form

```
restic [global flags] <command> [command flags] [args]
```

Global flags: `-r/--repo`, `--repository-file`, `--password-file`, `--password-command`, `--insecure-no-password` (empty password — insecure, must be passed to every command), `--cache-dir`, `--no-cache`, `--json`, `--quiet`, `--verbose`, `--retry-lock <dur>` (wait for a held lock instead of failing with exit 11, e.g. `--retry-lock 5m`), `--compression auto|off|fastest|better|max` (repo v2), `--limit-upload <KiB/s>` / `--limit-download <KiB/s>`, `--no-extra-verify` (skip the extra pre-upload verification), `-o <key=value>` (backend options, e.g. `-o s3.region=auto`).

## Command index

| Command | Purpose |
|---------|---------|
| `restic init` | Create a new (encrypted) repository |
| `restic backup` | Create a snapshot of files/dirs |
| `restic snapshots` | List snapshots |
| `restic ls` | List files within a snapshot |
| `restic find` | Search for files across snapshots |
| `restic restore` | Restore files from a snapshot |
| `restic dump` | Stream a file/dir from a snapshot to stdout |
| `restic forget` | Remove snapshots per a retention policy |
| `restic prune` | Repack and reclaim unreferenced data |
| `restic check` | Verify repository integrity |
| `restic stats` | Repository / snapshot statistics |
| `restic cat` | Output internal objects (e.g. `cat config`) |
| `restic unlock` | Remove stale locks |
| `restic mount` | Mount the repository as a FUSE filesystem (browse snapshots; read-only) |
| `restic cache` | List / clean local cache directories (`restic cache --cleanup`) |
| `restic recover` | Build a new snapshot from directories found in the repository that no snapshot references (e.g. after an accidental `forget`) |
| `restic list` | List object IDs (locks, snapshots, packs, ...) |
| `restic copy` | Copy snapshots between repositories |
| `restic migrate` | Apply repo migrations (e.g. `upgrade_repo_v2`) |
| `restic diff` | Diff two snapshots |
| `restic tag` | Add/remove/replace snapshot tags |
| `restic rewrite` | Rewrite snapshots (e.g. drop paths) |
| `restic repair` | Repair `index` / `snapshots` / `packs` |
| `restic self-update` | Update the restic binary |
| `restic key` | Manage repository passwords/keys |
| `restic features` | List feature flags and their defaults |
| `restic options` | List extended `-o` options per backend |

## init

```
restic init [--repository-version <N|latest|stable>]
            [--from-repo <repo> --from-password-file <f> --copy-chunker-params]
```

- `--repository-version` takes a format number, `latest` or `stable` (default `stable`; repo format v2 on 0.19.x).
- `--from-repo` names a **source** repository and `--copy-chunker-params` copies its **chunker parameters** (not its keys), so a later `restic copy` from that source deduplicates against the new repo. The source password comes from `--from-password-file` / `--from-password-command` (or `$RESTIC_FROM_PASSWORD_FILE`). `--from-repository` is not a flag — restic answers `unknown flag` (the file variant is `--from-repository-file`).

## backup

```
restic backup [flags] [PATH...]
```

| Flag | Notes |
|------|-------|
| `--tag <t>` | Tag the snapshot (repeatable) |
| `--files-from <f>` | Read include paths from a file (one per line) |
| `--files-from-verbatim <f>` | Like above, no shell interpretation |
| `--files-from-raw <f>` | NUL-separated list (safest for scripts) |
| `--exclude <pat>` / `--iexclude` | Exclude pattern (case-insensitive variant) |
| `--exclude-file <f>` | Exclude patterns from a file |
| `--exclude-caches` | Skip dirs containing `CACHEDIR.TAG` |
| `--exclude-larger-than <size>` | Skip files bigger than e.g. `1G` |
| `--one-file-system` | Don't cross mount points (off by default) |
| `--stdin-from-command -- <cmd>` | Back up a command's stdout |
| `--stdin-filename <name>` | Name for the stdin stream |
| `--dry-run` / `-n` | Show what would happen |
| `--host <h>` | Override hostname recorded in the snapshot (also overrides `$RESTIC_HOST`) |
| `--skip-if-unchanged` | Don't create a snapshot identical to its parent (0.19+) — keeps a daily job from piling up empty snapshots |
| `--read-concurrency <n>` | Read n files concurrently (default `$RESTIC_READ_CONCURRENCY` or 2) |

Notes for 0.19+:

- Exit **3** is returned when some source data could not be read **or when a source path given on the command line does not exist** (a snapshot of the rest is still created). If *every* source is missing, `backup` exits **1** with no snapshot.
- Entries in a `--files-from` list are patterns: one that matches nothing is skipped with a warning (`does not match any files, skipping`) and does not by itself change the exit code.
- `--exclude*`, `--exclude-if-present`, `--exclude-caches`, `--one-file-system` and `--exclude-larger-than` are **not applied to paths named explicitly on the command line** (0.19.0, #5767) — they still filter everything *inside* a backed-up directory. Do not rely on an exclude to drop a root path.

## snapshots / ls / find / diff / stats

```
restic snapshots [--latest <n>] [--host <h>] [--path <p>] [--tag <t>] [--group-by host,path,tags] [--json]
```

`--latest <n>` keeps the last *n* snapshots **per group** (default group: host + paths), so with several path sets `--json --latest 1` returns more than one snapshot — take the maximum `time` when you want "the newest backup" (0.19.0 briefly dropped the default grouping; 0.19.1 restored it).

```
restic ls <snapshotID|latest> [path]
restic find <pattern> [--snapshot <id>]
restic diff <snap1> <snap2>
restic stats [snapshotID|latest] [--mode restore-size|files-by-contents|raw-data|blobs-per-file]
```

## restore / dump

```
restic restore <snapshotID|latest> --target <dir> [--include <p>] [--exclude <p>]
               [--iinclude/--iexclude] [--include-file <f>] [--overwrite always|if-changed|if-newer|never]
               [--delete] [--sparse] [--dry-run -vv] [--host <h>] [--path <p>]
               [--ownership-by-name] [--verify]
restic restore <snapshotID>:<subpath> --target <dir>     # restore a subtree
restic dump <snapshotID|latest> <path>                   # to stdout
```

- `--ownership-by-name` (0.19+) restores owner/group by **name** instead of numeric UID/GID — use it when rebuilding on a server whose IDs differ (POSIX ACLs are still restored numerically).
- `--verify` re-reads the restored files and checks their content against the snapshot.

## forget / prune

```
restic forget [selection] [policy] [--prune] [--dry-run] [--group-by host,path,tags]
```

Retention policy flags: `--keep-last <n>`, `--keep-hourly`, `--keep-daily`, `--keep-weekly`, `--keep-monthly`, `--keep-yearly`, `--keep-within <dur>`, `--keep-within-daily/-weekly/-monthly <dur>`, `--keep-tag <t>`. Selection: `--tag`, `--host`, `--path`.

- `--keep-tag` is protected by the `safe-forget-keep-tags` feature flag (stable, on by default): if the tag does not exist, `forget` refuses to delete all snapshots. Deleting every snapshot of a group takes an explicit `--unsafe-allow-remove-all`.
- **Exit 3** (0.19+) means one or more snapshots could not be removed; before 0.19.0 `forget` returned 0 in that case. Treat it as a failure.

```
restic prune [--max-unused <limit|unlimited>] [--max-repack-size <size>] [--dry-run]
```

`prune` repacks small pack files more aggressively since 0.19.0; `--repack-small` is deprecated and no longer needed (`--repack-smaller-than <size>` still tunes it).

## check

```
restic check [--read-data] [--read-data-subset <n%|nM|k/N>] [--with-cache]
             [--tag <t>] [--host <h>] [--path <p>] [<snapshotID>...]
```

Since 0.19.0 the snapshot filters (`--tag`, `--host`, `--path`, or explicit snapshot IDs) restrict pack verification to the selected snapshots — a cheap spot-check of just the newest backup.

## unlock / list / cat / migrate / repair

```
restic unlock [--remove-all]
restic list <locks|snapshots|index|packs|keys>
restic cat <config|masterkey|snapshot <id>|...>
restic migrate [upgrade_repo_v2]
restic repair <index|snapshots|packs>
```

`restic rebuild-index` is **deprecated** (`Command "rebuild-index" is deprecated, Use "repair index" instead`) — use `restic repair index`.

## key / copy / self-update

```
restic key list|add|remove|passwd
restic copy --from-repo <repo> --from-password-file <f> [snapshotID...]
restic self-update [--output <path>]
```

`self-update` calls the GitHub API unauthenticated; on a shared IP that can end in `403 Forbidden` (rate limit). Export `GITHUB_ACCESS_TOKEN=<personal access token>` (0.19+) for that one command, and keep the token out of the repository env file.

## Environment variables

| Variable | Purpose |
|----------|---------|
| `RESTIC_REPOSITORY` | Repository location (e.g. `s3:https://<acc>.r2.cloudflarestorage.com/<bucket>`) |
| `RESTIC_REPOSITORY_FILE` | File containing the repo location |
| `RESTIC_PASSWORD` | Repository password (avoid in scripts/history) |
| `RESTIC_PASSWORD_FILE` | File containing the password (mode 600) |
| `RESTIC_PASSWORD_COMMAND` | Command that prints the password |
| `RESTIC_COMPRESSION` | `off` / `auto` (default) / `fastest` / `better` / `max` (repo v2; `fastest` and `better` need 0.19+) |
| `RESTIC_CACHE_DIR` | Local cache directory |
| `RESTIC_PACK_SIZE` | Target pack size (MiB) |
| `RESTIC_READ_CONCURRENCY` | Files read concurrently by `backup` |
| `RESTIC_PROGRESS_FPS` | Progress refresh rate |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | S3/R2 credentials |
| `AWS_DEFAULT_REGION` | S3 region — **`auto` for R2** |
| `AWS_SESSION_TOKEN` | Temporary STS token |
| `GITHUB_ACCESS_TOKEN` | Optional GitHub token for `restic self-update` (0.19+; avoids API rate-limit 403) |

Since 0.19.0 an **invalid** `RESTIC_COMPRESSION`, `RESTIC_PACK_SIZE` or `RESTIC_READ_CONCURRENCY` is a fatal error (`invalid value for RESTIC_COMPRESSION "…"`, exit 1) — earlier versions silently ignored it. A typo in the env file now stops every command until fixed or overridden on the command line.

Backend options (`-o`): `s3.region`, `s3.bucket-lookup=auto|dns|path`, `s3.connections=<n>`, `s3.storage-class`, `s3.list-objects-v1=true`, `s3.retries=<n>` (`s3.layout` is deprecated). `restic options` lists every backend option; `restic features` lists the feature flags.

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | success |
| 1 | fatal error (backup: no snapshot created — includes "every source path is missing") |
| 3 | `backup`: partial — some source data unreadable **or a source path missing**, snapshot still created (missing path ⇒ 3 since 0.19.0; it used to be 0). `forget`: one or more snapshots could **not be removed** (≥0.19.0) — a real failure |
| 10 | repository does not exist (≥0.17) |
| 11 | repository locked |
| 12 | wrong password (≥0.17.1) |
| 130 | cancelled by SIGINT/SIGTERM (≥0.19.0; SIGINT returned 1 before) |

## Version notes

- Compression + repository format **v2** require restic **≥ 0.14** (the floor); target **≥ 0.19.1**. 0.19.0 changed exit codes (3 for a missing `backup` path and for a failed `forget`, 130 when cancelled) and made invalid `RESTIC_*` env values fatal; 0.19.1 restored the `snapshots --latest <n>` grouping, skips inaccessible `backup` paths and refuses a `mount` over the repository directory.
- Exit codes 10 / 11 / 12 were added in 0.17.x; older binaries return 1.
- Use `restic repair index`; the former index-rebuild command is deprecated (see *repair* above).
