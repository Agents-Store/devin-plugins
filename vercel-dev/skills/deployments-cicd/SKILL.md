---
name: deployments-cicd
description: Vercel deployment and CI/CD expert guidance. Use when deploying, promoting, rolling back, inspecting deployments, building with --prebuilt, or configuring CI workflow files for Vercel.
metadata:
  priority: 6
  docs:
    - "https://vercel.com/docs/deployments/overview"
    - "https://vercel.com/docs/git"
  sitemap: "https://vercel.com/sitemap/docs.xml"
  pathPatterns:
    - '.github/workflows/*.yml'
    - '.github/workflows/*.yaml'
    - '.gitlab-ci.yml'
    - 'bitbucket-pipelines.yml'
    - 'vercel.json'
    - 'apps/*/vercel.json'
  bashPatterns:
    - '\bvercel\s+deploy\b'
    - '\bvercel\s+--prod\b'
    - '\bvercel\s+promote\b'
    - '\bvercel\s+rollback\b'
    - '\bvercel\s+inspect\b'
    - '\bvercel\s+build\b'
    - '\bvercel\s+deploy\s+--prebuilt\b'
validate:
  -
    pattern: 'cron:\s*[''"]|from\s+[''"](node-cron)[''"]|cron\.schedule\('
    message: 'Manual cron scheduling detected. Use Vercel Cron Jobs (vercel.json crons) for platform-native scheduled tasks.'
    severity: recommended
    skipIfFileContains: 'vercel\.json.*crons|@vercel/cron'
retrieval:
  aliases:
    - deploy
    - ci cd
    - continuous deployment
    - release pipeline
  intents:
    - deploy to vercel
    - set up ci cd
    - promote deployment
    - rollback deploy
  entities:
    - vercel deploy
    - preview
    - production
    - rollback
    - promote
    - CI workflow
---

# Vercel Deployments & CI/CD

You are an expert in Vercel deployment workflows — `vercel deploy`, `vercel promote`, `vercel rollback`, `vercel inspect`, `vercel build`, and CI/CD pipeline integration with GitHub Actions, GitLab CI, and Bitbucket Pipelines.

## Deployment Commands

### Preview Deployment

```bash
# Deploy from project root (creates preview URL)
vercel

# Equivalent explicit form
vercel deploy
```

Preview deployments are created automatically for every push to a non-production branch when using Git integration. They provide a unique URL for testing.

### Production Deployment

```bash
# Deploy directly to production
vercel --prod
vercel deploy --prod

# Force a new deployment (skip cache)
vercel --prod --force
```

### Build Locally, Deploy Build Output

```bash
# Build locally (uses development env vars by default)
vercel build

# Build with production env vars
vercel build --prod

# Deploy only the build output (no remote build)
vercel deploy --prebuilt
vercel deploy --prebuilt --prod
```

**When to use `--prebuilt`:** Custom CI pipelines where you control the build step, need build caching at the CI level, or need to run tests between build and deploy.

### Promote & Rollback

```bash
# Promote a preview deployment to production
vercel promote <deployment-url-or-id>

# Rollback to the previous production deployment
vercel rollback

# Rollback to a specific deployment
vercel rollback <deployment-url-or-id>
```

**Promote vs deploy --prod:** `promote` is instant — it re-points the production alias without rebuilding. Use it when a preview deployment has been validated and is ready for production.

### Inspect Deployments

```bash
# View deployment details (build info, functions, metadata)
vercel inspect <deployment-url>

# List recent deployments
vercel ls

# View logs for a deployment
vercel logs <deployment-url>
vercel logs <deployment-url> --follow
```

## CI/CD Integration

### Required Environment Variables

Every CI pipeline needs these three variables:

```bash
VERCEL_TOKEN=<your-token>        # Personal or team token
VERCEL_ORG_ID=<org-id>           # From .vercel/project.json
VERCEL_PROJECT_ID=<project-id>   # From .vercel/project.json
```

Set these as secrets in your CI provider. Never commit them to source control.

### GitHub Actions

```yaml
name: Deploy to Vercel
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Vercel CLI
        run: npm install -g vercel

      - name: Pull Vercel Environment
        run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}

      - name: Build
        run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}

      - name: Deploy
        run: vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
```

### OIDC Federation (Secure Backend Access)

Vercel OIDC federation is for **secure backend access** — letting your deployed Vercel functions authenticate with third-party services (AWS, GCP, HashiCorp Vault) without storing long-lived secrets. It does **not** replace `VERCEL_TOKEN` for CLI deployments.

**What OIDC does:** Your Vercel function requests a short-lived OIDC token from Vercel at runtime, then exchanges it with an external provider's STS/token endpoint for scoped credentials.

**What OIDC does not do:** Authenticate the Vercel CLI in CI pipelines. All `vercel pull`, `vercel build`, and `vercel deploy` commands still require `--token=${{ secrets.VERCEL_TOKEN }}`.

**When to use OIDC:**
- Serverless functions that need to call AWS APIs (S3, DynamoDB, SQS)
- Functions authenticating to GCP services via Workload Identity Federation
- Any runtime service-to-service auth where you want to avoid storing static secrets in Vercel env vars

### GitLab CI

```yaml
deploy:
  image: node:20
  stage: deploy
  script:
    - npm install -g vercel
    - vercel pull --yes --environment=production --token=$VERCEL_TOKEN
    - vercel build --prod --token=$VERCEL_TOKEN
    - vercel deploy --prebuilt --prod --token=$VERCEL_TOKEN
  only:
    - main
```

### Bitbucket Pipelines

```yaml
pipelines:
  branches:
    main:
      - step:
          name: Deploy to Vercel
          image: node:20
          script:
            - npm install -g vercel
            - vercel pull --yes --environment=production --token=$VERCEL_TOKEN
            - vercel build --prod --token=$VERCEL_TOKEN
            - vercel deploy --prebuilt --prod --token=$VERCEL_TOKEN
```

## Common CI Patterns

### Preview Deployments on PRs

```yaml
# GitHub Actions
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install -g vercel
      - run: vercel pull --yes --environment=preview --token=${{ secrets.VERCEL_TOKEN }}
      - run: vercel build --token=${{ secrets.VERCEL_TOKEN }}
      - id: deploy
        run: echo "url=$(vercel deploy --prebuilt --token=${{ secrets.VERCEL_TOKEN }})" >> $GITHUB_OUTPUT
      - name: Comment PR
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `Preview: ${{ steps.deploy.outputs.url }}`
            })
```

### Promote After Tests Pass

```yaml
jobs:
  deploy-preview:
    # ... deploy preview ...
    outputs:
      url: ${{ steps.deploy.outputs.url }}

  e2e-tests:
    needs: deploy-preview
    runs-on: ubuntu-latest
    steps:
      - run: npx playwright test --base-url=${{ needs.deploy-preview.outputs.url }}

  promote:
    needs: [deploy-preview, e2e-tests]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - run: npm install -g vercel
      - run: vercel promote ${{ needs.deploy-preview.outputs.url }} --token=${{ secrets.VERCEL_TOKEN }}
```

## Global CLI Flags for CI

| Flag | Purpose |
|------|---------|
| `--token <token>` | Authenticate (required in CI) |
| `--yes` / `-y` | Skip confirmation prompts |
| `--scope <team>` | Execute as a specific team |
| `--cwd <dir>` | Set working directory |

## Best Practices

1. **Always use `--prebuilt` in CI** — separates build from deploy, enables build caching and test gates
2. **Use `vercel pull` before build** — ensures correct env vars and project settings
3. **Prefer `promote` over re-deploy** — instant, no rebuild, same artifact
4. **Use OIDC federation for runtime backend access** — lets Vercel functions auth to AWS/GCP without static secrets (does not replace `VERCEL_TOKEN` for CLI)
5. **Pin the Vercel CLI version in CI** — `npm install -g vercel@latest` can break unexpectedly
6. **Add `--yes` flag in CI** — prevents interactive prompts from hanging pipelines

## Deployment Strategy Matrix

| Scenario | Strategy | Commands |
|----------|----------|----------|
| Standard team workflow | Git-push deploy | Push to main/feature branches |
| Custom CI/CD (Actions, CircleCI) | Prebuilt deploy | `vercel build && vercel deploy --prebuilt` |
| Monorepo with Turborepo | Affected + remote cache | `turbo run build --affected --remote-cache` |
| Preview for every PR | Default behavior | Auto-creates preview URL per branch |
| Promote preview to production | CLI promotion | `vercel promote <url>` |
| Atomic deploys with DB migrations | Two-phase | Run migration → verify → `vercel promote` |
| Edge-first architecture | Edge Functions | Set `runtime: 'edge'` in route config |

## Common Build Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ERR_PNPM_OUTDATED_LOCKFILE` | Lockfile doesn't match package.json | Run `pnpm install`, commit lockfile |
| `NEXT_NOT_FOUND` | Root directory misconfigured | Set `rootDirectory` in Project Settings |
| `Invalid next.config.js` | Config syntax error | Validate config locally with `next build` |
| `functions/api/*.js` mismatch | Wrong file structure | Move to `app/api/` directory (App Router) |
| `Error: EPERM` | File permission issue in build | Don't `chmod` in build scripts; use postinstall |

## Deploy Summary Format

Present a structured deploy result block:

```
## Deploy Result
- **URL**: <deployment-url>
- **Target**: production | preview
- **Status**: READY | ERROR | BUILDING | QUEUED
- **Commit**: <short-sha>
- **Framework**: <detected-framework>
- **Build Duration**: <duration>
```

If the deployment failed, append:

```
- **Error**: <summary of failure from logs>
```

For production deploys, also include:

```
### Post-Deploy Observability
- **Error scan**: <N errors found / clean> (scanned via vercel logs --level error --since 1h)
- **Drains**: <N configured / none>
- **Monitoring**: <active / gaps identified>
```

## Deploy Next Steps

Based on the deployment outcome:

- **Success (preview)** → "Visit the preview URL to verify. When ready, run `/deploy prod` to promote to production."
- **Success (production)** → "Your production site is live. Run `/status` to see the full project overview."
- **Build error** → "Check the build logs above. Common fixes: verify `build` script in package.json, check for missing env vars with `/env list`, ensure dependencies are installed."
- **Missing env vars** → "Run `/env pull` to sync environment variables locally, or `/env list` to review what's configured on Vercel."
- **Monorepo issues** → "Ensure the correct project root is configured in Vercel project settings. Check `vercel.json` for `rootDirectory`."
- **Post-deploy errors detected** → "Review errors above. Check `vercel logs <url> --level error` for details. If drains are configured, correlate with external monitoring."
- **No monitoring configured** → "Set up drains or install an error tracking integration before the next production deploy. Run `/status` for a full observability diagnostic."

## CLI Deploy Troubleshooting (No Git Integration)

When deploying via `vercel deploy` from CLI without a connected Git repository, several issues can occur that don't apply to Git-integrated projects:

### Build succeeds but all routes return 404

**Root cause:** Vercel uses a generic builder instead of the Next.js builder. The build runs `next build` successfully, but the output routing configuration is not generated correctly.

**Fix:** Create `vercel.json` with explicit framework:
```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "framework": "nextjs"
}
```

**Diagnosis:** Run `vercel inspect <url>` — if `Builds` shows `[0ms]` for a deployment that took 30+ seconds to build, the framework was not detected.

### `VERCEL_TOKEN` env var conflicts with CLI login

**Symptom:** `vercel whoami` returns "token is not valid" even after `vercel login`.

**Root cause:** A `VERCEL_TOKEN` from `.env.local`, Infisical, or CI setup overrides the interactive CLI session.

**Fix:** `unset VERCEL_TOKEN` before running `vercel` commands, or prefix: `unset VERCEL_TOKEN && vercel deploy`.

### Git author email doesn't match Vercel team (Hobby plan)

**Symptom:** "Git author X must have access to the team Y. Hobby teams do not support collaboration."

**Root cause:** Vercel Hobby plan only allows the team owner to deploy. The git author email on the latest commit must match the team owner's email.

**Fix:**
```bash
git config user.email "team-owner@example.com"
git commit --allow-empty -m "chore: update deploy author"
```

### `output: 'standalone'` causes 404 on Vercel

**Symptom:** Build succeeds, `vercel inspect` shows READY, but all pages return 404.

**Root cause:** `output: 'standalone'` in `next.config.ts` is designed for Docker/Node.js self-hosting. It changes the build output format in a way Vercel's routing doesn't expect.

**Fix:** Conditionally disable for Vercel:
```typescript
const nextConfig: NextConfig = {
  ...(process.env.VERCEL ? {} : { output: 'standalone' as const }),
  // ...
}
```

### Preview env vars missing (no Git integration)

**Symptom:** Build fails with `TypeError: Invalid URL` or similar — env vars like `NEXT_PUBLIC_*` are `undefined` during build.

**Root cause:** `vercel env add <name> preview` requires a Git branch when the project has no Git integration, and fails.

**Fix:** Pass env vars directly during deploy:
```bash
source .env.local && vercel deploy \
  -b NEXT_PUBLIC_DIRECTUS_URL="$NEXT_PUBLIC_DIRECTUS_URL" \
  -b DIRECTUS_ADMIN_TOKEN="$DIRECTUS_ADMIN_TOKEN" \
  -e NEXT_PUBLIC_DIRECTUS_URL="$NEXT_PUBLIC_DIRECTUS_URL" \
  -e DIRECTUS_ADMIN_TOKEN="$DIRECTUS_ADMIN_TOKEN"
```

Use `-b` for build-time vars and `-e` for runtime vars. `NEXT_PUBLIC_*` vars need both.

## Deploy Hooks (CMS / External Trigger Rebuilds)

Deploy Hooks let external services trigger a full production rebuild via a POST request — useful for headless CMS content changes (Directus, Sanity, Contentful, Strapi, etc.).

### Create a Deploy Hook

1. Vercel dashboard → project Settings → Git → **Deploy Hooks**
2. Name: e.g. "CMS Content Update"
3. Branch: `main` (or your production branch)
4. Copy the generated URL (format: `https://api.vercel.com/v1/integrations/deploy/prj_xxx/xxx`)

### Wire to a Headless CMS

Point your CMS webhook at the deploy hook URL. Examples:

**Directus (via Automate Flows):**
1. Settings → Flows → Create Flow
2. Trigger: Event Hook → `items.create`, `items.update` on content collections
3. Condition (optional): `{{ $trigger.payload.status }} == "published"`
4. Operation: Webhook → POST to the deploy hook URL (no body needed)

**Sanity:** Settings → API → Webhooks → add the hook URL, filter by document type.

**Contentful:** Settings → Webhooks → add URL, trigger on Entry publish.

### Deploy Hooks vs ISR Revalidation

| Approach | When to use |
|----------|-------------|
| **Deploy Hook** (full rebuild) | Static sites, infrequent content updates, need guaranteed fresh build |
| **ISR on-demand revalidation** (`revalidateTag`/`revalidatePath`) | Dynamic sites, frequent updates, instant refresh without full rebuild |

For most Next.js App Router projects, **ISR revalidation is preferred** — it's faster (seconds vs minutes) and doesn't burn a build. Deploy hooks are simpler but trigger a full redeploy. You can use both: ISR for instant cache invalidation + deploy hook as a safety net for daily full rebuilds.

### Programmatic Trigger

```bash
# Trigger a deploy hook from CLI or CI
curl -X POST "https://api.vercel.com/v1/integrations/deploy/prj_xxx/xxx"
```

No authentication needed — the URL itself is the secret. Keep it private.

## Official Documentation

- [Deployments](https://vercel.com/docs/deployments)
- [Deploy Hooks](https://vercel.com/docs/deployments/deploy-hooks)
- [Vercel CLI](https://vercel.com/docs/cli)
- [GitHub Actions](https://vercel.com/docs/deployments/git/vercel-for-github)
- [GitLab CI](https://vercel.com/docs/deployments/git/vercel-for-gitlab)
- [Bitbucket Pipelines](https://vercel.com/docs/deployments/git/vercel-for-bitbucket)
- [OIDC Federation](https://vercel.com/docs/oidc)
