# CLI Deploys Without Git, and CMS Deploy Hooks

AGENTS.STORE additions to the upstream `deployments-cicd` skill.

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

### `output: 'standalone'` as a possible cause of a 404 on Vercel

**Symptom:** Build succeeds, `vercel inspect` shows READY, but all pages return 404.

**Check first:** Vercel routes from metadata generated at build time, so a READY build with a 404 usually means a wrong Framework Preset ("Other") or Output Directory. Set `"framework": "nextjs"` as in the first section, or fix Project Settings → Build and Deployment. See [Why is my deployed project giving a 404?](https://vercel.com/kb/guide/why-is-my-deployed-project-giving-404).

**Possible cause (not reproduced):** `output: 'standalone'` in `next.config.ts` is designed for Docker/Node.js self-hosting and changes the build output format. No primary source confirms it breaks Vercel routing, so treat it as a suspect only after the preset and output directory are ruled out.

**Test:** Conditionally disable it for Vercel and redeploy:
```typescript
const nextConfig: NextConfig = {
  ...(process.env.VERCEL ? {} : { output: 'standalone' as const }),
  // ...
}
```

### Preview env vars missing (no Git integration)

**Symptom:** Build fails with `TypeError: Invalid URL` or similar — env vars like `NEXT_PUBLIC_*` are `undefined` during build.

**Root cause:** The Preview environment has no value for them. Vercel CLI 62.2.0 takes `vercel env add name [environment] [--git-branch <NAME>] [--value <VALUE>] [--yes]`, so a Git branch is not required (read from `vercel env add --help`, not re-run on a project without Git integration). If `vercel env add ... preview` still fails on your CLI, use the `-b`/`-e` fallback below.

**Fix:** Add the variables to Preview non-interactively:
```bash
vercel env add NEXT_PUBLIC_DIRECTUS_URL preview --value "$NEXT_PUBLIC_DIRECTUS_URL" --yes
```
`--value` is visible in the process list and shell history; for secrets pipe the value on stdin instead of passing `--value`.

**Fallback (nothing stored):** Pass env vars directly during deploy:
```bash
source .env.local && vercel deploy \
  -b NEXT_PUBLIC_DIRECTUS_URL="$NEXT_PUBLIC_DIRECTUS_URL" \
  -b DIRECTUS_ADMIN_TOKEN="$DIRECTUS_ADMIN_TOKEN" \
  -e NEXT_PUBLIC_DIRECTUS_URL="$NEXT_PUBLIC_DIRECTUS_URL" \
  -e DIRECTUS_ADMIN_TOKEN="$DIRECTUS_ADMIN_TOKEN"
```

Use `-b` for build-time vars and `-e` for runtime vars. `NEXT_PUBLIC_*` vars need both.

## Deploy Hooks (CMS / External Trigger Rebuilds)

Deploy Hooks let external services trigger a full rebuild of one Git branch via a GET or POST request — useful for headless CMS content changes (Directus, Sanity, Contentful, Strapi, etc.).

### Create a Deploy Hook

Deploy Hooks exist only for a project **connected to a Git repository**. A project that is deployed from the CLI alone cannot have one, so connect a repository first (or use ISR revalidation below).

1. Vercel dashboard → project Settings → Git → **Deploy Hooks** (or `vercel deploy-hooks create [name]`)
2. Name: e.g. "CMS Content Update" — one hook per branch unless you have several data sources
3. Branch: `main` (or your production branch)
4. Copy the generated URL (format: `https://api.vercel.com/v1/integrations/deploy/prj_xxx/xxx`)

### Limits and Options

- **Count:** 5 deploy hooks per project on Hobby and Pro, 10 on Enterprise.
- **Rate:** up to 60 triggers per hour per project, summed over all of its hooks. A CMS that fires a webhook on every save can hit this; trigger on publish only.
- **Build cache:** a hook reuses the build cache by default. Append `?buildCache=false` to the URL to skip it. Hooks created before 2021-05-11 default to no cache; append `?buildCache=true` or recreate the hook.
- **Duplicates:** repeated requests for the same version cancel the earlier deployments of that hook.
- **Off switch:** hooks do nothing when `vercel.json` contains `"github": { "enabled": false }`.

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
| **Deploy Hook** (full rebuild; 60 triggers per hour per project) | Static sites, infrequent content updates, need guaranteed fresh build |
| **ISR on-demand revalidation** (`revalidateTag`/`revalidatePath`) | Dynamic sites, frequent updates, instant refresh without full rebuild |

For most Next.js App Router projects, **ISR revalidation is preferred** — it's faster (seconds vs minutes) and doesn't burn a build. Deploy hooks are simpler but trigger a full redeploy. You can use both: ISR for instant cache invalidation + deploy hook as a safety net for daily full rebuilds.

### Programmatic Trigger

```bash
# Trigger a deploy hook from CLI or CI
curl -X POST "https://api.vercel.com/v1/integrations/deploy/prj_xxx/xxx"

# Same, without the build cache
curl -X POST "https://api.vercel.com/v1/integrations/deploy/prj_xxx/xxx?buildCache=false"
```

No authentication needed — the URL itself is the secret. Keep it private (a CI secret, never the repository) and revoke it in Settings → Git if it leaks. Source: https://vercel.com/docs/deploy-hooks.
