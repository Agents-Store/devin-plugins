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
- A machine-identity login creates no login profile; the token is all there is. For EU Cloud, a dedicated or a self-hosted instance, set `INFISICAL_DOMAIN` (or pass `--domain` on `login`) so the token is requested from the right instance.
- To scope the session to a sub-organization the identity can reach, add `--organization-slug=<slug>`; without it the session uses the organization the identity was created in.
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

# OIDC (GitHub Actions, GitLab CI, etc.)
infisical login --method=oidc-auth --machine-identity-id="$MI_ID" --jwt="$ID_TOKEN" --silent --plain

# Generic JWT auth (a JWT your own issuer signs)
infisical login --method=jwt-auth --machine-identity-id="$MI_ID" --jwt="$JWT" --silent --plain
```

`--jwt` replaces the deprecated `--oidc-jwt`. `--method` covers `universal-auth`, `kubernetes`, `azure`, `gcp-id-token`, `gcp-iam`, `aws-iam`, `oidc-auth` and `jwt-auth` (plus `user` for people). The official Infisical skills list 13 machine-identity auth methods (Universal, Token, Kubernetes, GCP, AliCloud, AWS, Azure, TLS Certificate, OCI, OIDC, JWT, LDAP, SPIFFE); for the ones `login --method` does not cover, authenticate through an SDK or the Infisical Agent.

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
# INFISICAL_DOMAIN (set on the container for EU / self-hosted) is read by both commands
exec infisical run --projectId "$PROJECT_ID" --env "$APP_ENV" -- node server.js
```

In Docker Compose, set `env_file` or `environment: [INFISICAL_TOKEN]` on the service and use the same `CMD`.

## GitHub Actions sketch

```yaml
- name: Build with secrets
  env:
    INFISICAL_CLIENT_ID:     ${{ secrets.INFISICAL_CLIENT_ID }}
    INFISICAL_CLIENT_SECRET: ${{ secrets.INFISICAL_CLIENT_SECRET }}
    PROJECT_ID:              ${{ vars.INFISICAL_PROJECT_ID }}
    INFISICAL_DOMAIN:        ${{ vars.INFISICAL_DOMAIN }}   # only for EU Cloud / dedicated / self-hosted
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
  --domain="$INFISICAL_DOMAIN" \
  --email="$ADMIN_EMAIL" \
  --password="$ADMIN_PASSWORD" \
  --organization="$ORG_NAME" \
  --ignore-if-bootstrapped
```

The command prints JSON that includes the instance-admin machine identity's token (`.identity.credentials.token`) — treat it like root credentials. For Kubernetes, add `--output=k8-secret` with `--k8-secret-name` / `--k8-secret-namespace` to write the result to a Kubernetes Secret instead (it must run inside a pod whose service account can get/create/update Secrets in that namespace).

## Infisical Agent (secrets as files, no `run`)

When an application should read secrets from files that stay fresh — or cannot be wrapped by `infisical run` — run the Infisical Agent next to it: `infisical agent --config agent-config.yaml`. It authenticates as a machine identity and renders secrets through Go templates into files (the config can also be passed as base64 in `INFISICAL_AGENT_CONFIG_BASE64`). The agent takes its instance from `infisical.address` in the config, not from `--domain`. For certificates there is `infisical cert-manager agent --config certificate-agent-config.yaml`. Flag details are in the `cli-reference` skill.

## Self-hosted note

Set `INFISICAL_DOMAIN` once (or pass `--domain`, a global flag that `login` honors, or set `domain` in `.infisical.json`). `infisical token renew` does not use a login profile, so for any instance other than US Cloud pass `--domain` or set `INFISICAL_DOMAIN` there too. A `--domain` / `INFISICAL_DOMAIN` that names a different instance than the profile you are logged in to makes the command fail (see the `troubleshoot` skill).
