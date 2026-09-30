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
