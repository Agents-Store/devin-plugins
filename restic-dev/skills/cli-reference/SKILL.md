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

Global flags: `-r/--repo`, `--repository-file`, `--password-file`, `--password-command`, `--cache-dir`, `--no-cache`, `--json`, `--quiet`, `--verbose`, `-o <key=value>` (backend options, e.g. `-o s3.region=auto`).

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
| `restic list` | List object IDs (locks, snapshots, packs, ...) |
| `restic copy` | Copy snapshots between repositories |
| `restic migrate` | Apply repo migrations (e.g. `upgrade_repo_v2`) |
| `restic diff` | Diff two snapshots |
| `restic tag` | Add/remove/replace snapshot tags |
| `restic rewrite` | Rewrite snapshots (e.g. drop paths) |
| `restic repair` | Repair `index` / `snapshots` / `packs` |
| `restic self-update` | Update the restic binary |
| `restic key` | Manage repository passwords/keys |

## init

```
restic init [--repository-version <2>] [--from-repository ... (copy keys)]
```

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
| `--host <h>` | Override hostname recorded in the snapshot |

## snapshots / ls / find / diff / stats

```
restic snapshots [--latest <n>] [--host <h>] [--path <p>] [--tag <t>] [--group-by host,path,tags] [--json]
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
restic restore <snapshotID>:<subpath> --target <dir>     # restore a subtree
restic dump <snapshotID|latest> <path>                   # to stdout
```

## forget / prune

```
restic forget [selection] [policy] [--prune] [--dry-run] [--group-by host,path,tags]
```

Retention policy flags: `--keep-last <n>`, `--keep-hourly`, `--keep-daily`, `--keep-weekly`, `--keep-monthly`, `--keep-yearly`, `--keep-within <dur>`, `--keep-within-daily/-weekly/-monthly <dur>`, `--keep-tag <t>`. Selection: `--tag`, `--host`, `--path`.

```
restic prune [--max-unused <limit|unlimited>] [--max-repack-size <size>] [--dry-run]
```

## check

```
restic check [--read-data] [--read-data-subset <n%|nM|k/N>] [--with-cache]
```

## unlock / list / cat / migrate / repair

```
restic unlock [--remove-all]
restic list <locks|snapshots|index|packs|keys>
restic cat <config|masterkey|snapshot <id>|...>
restic migrate [upgrade_repo_v2]
restic repair <index|snapshots|packs>
restic rebuild-index                 # older alias of `repair index`
```

## key / copy / self-update

```
restic key list|add|remove|passwd
restic copy --from-repo <repo> --from-password-file <f> [snapshotID...]
restic self-update [--output <path>]
```

## Environment variables

| Variable | Purpose |
|----------|---------|
| `RESTIC_REPOSITORY` | Repository location (e.g. `s3:https://<acc>.r2.cloudflarestorage.com/<bucket>`) |
| `RESTIC_REPOSITORY_FILE` | File containing the repo location |
| `RESTIC_PASSWORD` | Repository password (avoid in scripts/history) |
| `RESTIC_PASSWORD_FILE` | File containing the password (mode 600) |
| `RESTIC_PASSWORD_COMMAND` | Command that prints the password |
| `RESTIC_COMPRESSION` | `off` / `auto` (default) / `max` (repo v2) |
| `RESTIC_CACHE_DIR` | Local cache directory |
| `RESTIC_PACK_SIZE` | Target pack size (MiB) |
| `RESTIC_PROGRESS_FPS` | Progress refresh rate |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | S3/R2 credentials |
| `AWS_DEFAULT_REGION` | S3 region — **`auto` for R2** |
| `AWS_SESSION_TOKEN` | Temporary STS token |

Backend options (`-o`): `s3.region`, `s3.bucket-lookup=path|dns`, `s3.connections=<n>`, `s3.storage-class`, `s3.list-objects-v1=true`.

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | success |
| 1 | fatal error (backup: no snapshot created) |
| 3 | partial — some files unreadable, snapshot created |
| 10 | repository does not exist (≥0.17) |
| 11 | repository locked |
| 12 | wrong password (≥0.17.1) |
| 130 | cancelled (SIGINT/SIGTERM) |

## Version notes

- Compression + repository format **v2** require restic **≥ 0.14**.
- Exit codes 10 / 11 / 12 were added in 0.17.x; older binaries return 1.
- `restic repair index` replaced `restic rebuild-index` (the old name still works).
