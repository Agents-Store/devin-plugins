---
name: repository-setup
description: This skill should be used when the user asks to "set up a restic repository on Cloudflare R2", "configure restic with S3 credentials", "create the restic encryption password", "initialize a restic repo", "fix restic AccessDenied on R2", or needs to wire up the password, R2/S3 env file, repository URL, and run restic init.
---

# restic Repository Setup (Cloudflare R2 / S3)

Create the encryption password, wire up the storage credentials, and initialize the repository. restic always encrypts client-side (AES-256) — **the password is the only key; lose it and the backup is permanently unrecoverable.** R2 server-side encryption is redundant here.

## Step 1 — Encryption password

```bash
install -d -m700 /root/.restic
openssl rand -base64 48 > /root/.restic/password   # strong random key
chmod 600 /root/.restic/password
```

> **STOP — copy this password off the server right now** (password manager / vault). Without it, none of the backups can ever be restored. This is the single most important action in the whole setup.

## Step 2 — Storage credentials env file

Write `/root/.restic/r2.env` (mode 600). For **Cloudflare R2**:

```bash
cat > /root/.restic/r2.env <<'EOF'
AWS_ACCESS_KEY_ID=<R2 access key id>
AWS_SECRET_ACCESS_KEY=<R2 secret access key>
AWS_DEFAULT_REGION=auto
RESTIC_REPOSITORY=s3:https://<account_id>.r2.cloudflarestorage.com/<bucket>
RESTIC_PASSWORD_FILE=/root/.restic/password
RESTIC_COMPRESSION=auto
EOF
chmod 600 /root/.restic/r2.env
```

- **Repository URL form:** `s3:https://<account_id>.r2.cloudflarestorage.com/<bucket>` — note the `s3:` prefix in front of the full `https://` endpoint.
- **`AWS_DEFAULT_REGION=auto` is required for R2** (or pass `-o s3.region=auto`). Standard AWS region names do not work.
- Other S3-compatible providers: same shape, e.g. Wasabi `s3:https://s3.<region>.wasabisys.com/<bucket>`, MinIO `s3:http://host:9000/<bucket>`, AWS `s3:s3.amazonaws.com/<bucket>` (+ real region).

**Sourcing for any manual restic command:**

```bash
set -a; . /root/.restic/r2.env; set +a
```

## Step 3 — Initialize and verify

```bash
set -a; . /root/.restic/r2.env; set +a

# IDEMPOTENCY: never re-init over an existing repo. Check first.
if restic cat config >/dev/null 2>&1; then
  echo "Repository already exists — do NOT re-init (would not overwrite, but never regenerate the password)."
else
  restic init           # creates the encrypted repo
fi

restic cat config       # readable config => keys + password work; expect "version":2
```

`"version":2` confirms repository format v2 — compression is active. If it shows v1 (older binary created it), upgrade in place: `restic migrate upgrade_repo_v2`.

## R2 API token requirements

The R2 API token must have:

- **Object Read & Write** permission
- a scope that **includes this bucket** (or all buckets in the account)
- the bucket must exist in the **same account** whose `account_id` is in the endpoint

## Troubleshooting `init` (AccessDenied / connection)

| Symptom | Cause | Fix |
|---------|-------|-----|
| `AccessDenied` | token lacks Object Read & Write, or scope excludes the bucket | re-issue the R2 token with Object Read & Write covering the bucket |
| `AccessDenied` but token looks right | `account_id` in the endpoint ≠ the token's account | match the endpoint's account id to the token's account (the #1 cause) |
| signature / region errors | missing region | `AWS_DEFAULT_REGION=auto` (or `-o s3.region=auto`) |
| bucket lookup / vhost failures | provider needs path-style | add `-o s3.bucket-lookup=path` |
| `NoSuchBucket` | bucket not created | create the bucket in the R2 dashboard first |
| `SignatureDoesNotMatch` | clock skew or wrong secret | sync time (`timedatectl`), re-check the secret key |

Fix R2 tokens in the Cloudflare dashboard → R2 → Manage R2 API Tokens.

## R2 cost & lifecycle

- R2 has **zero egress fees**; you pay for storage + Class A/B operations. restic's pack format keeps operation counts reasonable.
- **CRITICAL — never set a bucket lifecycle rule that deletes or expires objects.** restic owns retention via `forget --prune` (see `backup-script`); any external deletion corrupts the repository. A lifecycle rule that only **aborts incomplete multipart uploads** is safe and recommended.

## Encryption at rest

restic encrypts everything client-side before upload, so the objects in R2 are already ciphertext. Enabling R2/S3 SSE on top is harmless but redundant — it does not protect you if the restic password is lost.

## Gotchas

- **Password loss = total, unrecoverable loss.** Force an off-server copy before `init`.
- **Idempotency:** check `restic cat config` before `init`; **never regenerate the password over an existing repo** — you'd lose access to every prior snapshot.
- Both `/root/.restic/password` and `/root/.restic/r2.env` must be mode **600**, root-owned. Never commit `r2.env` to git.
- Repo format v2 / compression needs restic **≥ 0.14** (see `setup`).

## What this skill does NOT cover

- Choosing what to back up → `discover-backup-sources`
- The backup script and retention → `backup-script`
- Restoring → `disaster-recovery`
