---
name: ci-cd-auth
description: This skill should be used when the user asks to "use Infisical in CI/CD", "Infisical machine identity", "infisical login universal-auth", "authenticate Infisical without a browser", "Infisical in Docker", "inject secrets in a pipeline", "Infisical Kubernetes/AWS/GCP/Azure auth", or "bootstrap a self-hosted Infisical" — non-interactive Infisical CLI authentication and secret injection for automation.
---

# Infisical CLI — CI/CD & Machine-Identity Auth

For pipelines, containers, and servers, authenticate with a **machine identity** instead of `infisical login` (browser). The pattern is always: log in to get a short-lived access token, export it as `INFISICAL_TOKEN`, then run normal commands. Prefer machine identities over the deprecated service tokens.

## Universal Auth (most common)

Create a machine identity with Universal Auth in the Infisical UI, then in the pipeline:

```bash
export INFISICAL_TOKEN=$(infisical login \
  --method=universal-auth \
  --client-id="$INFISICAL_CLIENT_ID" \
  --client-secret="$INFISICAL_CLIENT_SECRET" \
  --silent --plain)

infisical run --projectId="$PROJECT_ID" --env=prod -- npm run build
```

- `--plain` prints only the JWT; `--silent` suppresses update notices — together they make the output safe to capture.
- Credentials can also come from `INFISICAL_UNIVERSAL_AUTH_CLIENT_ID` / `INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET`.
- Once `INFISICAL_TOKEN` is set, every subsequent command auto-detects it.
- With machine-identity auth there is no `.infisical.json`, so pass `--projectId` explicitly.
- In production, also set `export INFISICAL_DISABLE_UPDATE_CHECK=true`.

## Native cloud / platform auth (no stored secret)

Each method exchanges a platform-issued identity for an Infisical token — no client secret to manage:

```bash
# Kubernetes (uses the pod's service-account token)
infisical login --method=kubernetes --machine-identity-id="$MI_ID" \
  --service-account-token-path=/var/run/secrets/kubernetes.io/serviceaccount/token --silent --plain

# AWS IAM
infisical login --method=aws-iam --machine-identity-id="$MI_ID" --silent --plain

# GCP (ID token on GCE/Cloud Run, or IAM service-account key)
infisical login --method=gcp-id-token --machine-identity-id="$MI_ID" --silent --plain
infisical login --method=gcp-iam --machine-identity-id="$MI_ID" \
  --service-account-key-file-path=/path/key.json --silent --plain

# Azure
infisical login --method=azure --machine-identity-id="$MI_ID" --silent --plain

# OIDC / generic JWT (GitHub Actions, GitLab CI, etc.)
infisical login --method=oidc-auth --machine-identity-id="$MI_ID" --jwt="$ID_TOKEN" --silent --plain
```

## Renew an access token

```bash
infisical token renew "$INFISICAL_TOKEN"
```

## Docker

Install the CLI in the image (see the `setup` skill), then make `infisical run` the entrypoint so the container fetches secrets at startup:

```dockerfile
# Recommended: machine identity at runtime
CMD ["infisical", "run", "--projectId", "your-project-id", "--", "npm", "run", "start"]
```

Pass the token in at `docker run` time:

```bash
export INFISICAL_TOKEN=$(infisical login --method=universal-auth \
  --client-id="$ID" --client-secret="$SECRET" --plain --silent)
docker run --env INFISICAL_TOKEN=$INFISICAL_TOKEN your-image
```

Entrypoint script that logs in inside the container, then execs the app:

```sh
#!/bin/sh
export INFISICAL_TOKEN=$(infisical login --method=universal-auth \
  --client-id="$INFISICAL_CLIENT_ID" \
  --client-secret="$INFISICAL_CLIENT_SECRET" --plain --silent)
exec infisical run --projectId "$PROJECT_ID" --env "$APP_ENV" \
  --domain "$INFISICAL_API_URL" -- node server.js
```

In Docker Compose, set `env_file` or `environment: [INFISICAL_TOKEN]` on the service and use the same `CMD`.

## GitHub Actions sketch

```yaml
- name: Build with secrets
  env:
    INFISICAL_CLIENT_ID:     ${{ secrets.INFISICAL_CLIENT_ID }}
    INFISICAL_CLIENT_SECRET: ${{ secrets.INFISICAL_CLIENT_SECRET }}
    PROJECT_ID:              ${{ vars.INFISICAL_PROJECT_ID }}
    INFISICAL_DISABLE_UPDATE_CHECK: "true"
  run: |
    export INFISICAL_TOKEN=$(infisical login --method=universal-auth \
      --client-id="$INFISICAL_CLIENT_ID" --client-secret="$INFISICAL_CLIENT_SECRET" --silent --plain)
    infisical run --projectId="$PROJECT_ID" --env=prod -- npm run build
```

## Bootstrap a fresh self-hosted instance

Headless first-run setup that creates the admin user, organization, and an instance-admin machine identity:

```bash
infisical bootstrap \
  --domain="$INFISICAL_API_URL" \
  --email="$ADMIN_EMAIL" \
  --password="$ADMIN_PASSWORD" \
  --organization="$ORG_NAME" \
  --ignore-if-bootstrapped
```

The JSON output includes the instance-admin token — treat it like root credentials. For Kubernetes, add `--output=k8-secret` with `--k8-secret-name` / `--k8-secret-namespace` to emit a Secret manifest.

## Self-hosted note

Set `INFISICAL_API_URL` (preferred) or pass `--domain` on **every** command including `login` — historically `login` did not always honor `--domain` for self-hosted flows, so the env var is the reliable choice.
