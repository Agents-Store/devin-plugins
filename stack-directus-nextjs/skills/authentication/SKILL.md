---
name: authentication
description: This skill should be used when the user wants to "add authentication to Directus + Next.js", "implement Directus login in Next.js", "use NextAuth with Directus", "use Better Auth with Directus", "protect Next.js pages with Directus auth", "choose an auth approach for Directus and Next.js", "decide who owns the session", or needs to decide who owns the end-user session and the tokens across Directus and Next.js.
---

# Authentication: Who Owns the Session and the Tokens

Two systems can both know a user. Decide once which one owns the identity and which one owns the browser session, then wire exactly that. The code lives in the technology plugins: `nextjs-dev` → `auth-patterns` and `directus-dev` → `sdk-patterns` (`references/ssr-client.md`, the login and refresh contract).

## Two Kinds of Token

- **Service token** (`DIRECTUS_ADMIN_TOKEN`): a static token of a dedicated Directus user, in the server environment. It reads the public content of every visitor. It never leaves the server.
- **User token**: the access and refresh token Directus issues when a person signs in. It exists only if Directus is the identity provider.

## Three Paths

| Path | Who owns the user | Who owns the browser session | Which token reads the user's data | Status |
|------|-------------------|------------------------------|-----------------------------------|--------|
| **NextAuth v4**, Credentials provider against Directus | Directus (users, policies) | NextAuth: encrypted httpOnly cookie that holds the Directus tokens | The user's own access token, so Directus applies that user's policies | Working path for existing projects |
| **Better Auth** | The Next.js app's own database | Better Auth cookie | The service token. Directus does not know the end user; the app enforces who sees what | Recommended for new projects |
| **Directus session cookie** (`authentication('session')` in the browser) | Directus | A cookie set by Directus itself | Browser talks to Directus directly | Needs the app and Directus on one site (or careful CORS and cookie settings) |

How to choose:

- **Directus policies must decide what each end user sees** (a customer portal on top of Directus data): NextAuth v4 with the Credentials provider, or the Directus session cookie.
- **A content site with a few app-level accounts** (comments, favourites kept in the app's own tables): Better Auth, with Directus behind the service token.
- **Existing project already on NextAuth v4**: keep it. It works with Next.js 16. See its limits (refresh needs a browser tab polling the NextAuth route, two tabs can race on the single-use refresh token, the access token is readable in the browser) in `nextjs-dev` → `auth-patterns` → `references/nextauth-and-authjs.md`. NextAuth v5 stays beta and is in maintenance mode.
- **SSO providers at Directus** (Google, Okta through Directus) need a licensed Directus 12 tier. Signing in with Google inside Next.js (NextAuth or Better Auth) does not.

## Rules That Hold on Every Path

1. **Authenticate and authorize before writing.** A Server Action or Route Handler is a public endpoint that takes any id. "Signed in" is not permission: with the service token, every signed-in user could edit any item. On the NextAuth path write with the user's own token (`withToken(session.accessToken, ...)`, below) so Directus applies that user's policies. On the Better Auth path there is no user token: check role or ownership in code before the write. Start each action with `requireUser()`: the NextAuth recipe in `nextjs-dev` → `auth-patterns` defines it in `lib/session.ts`; on Better Auth write the same in `lib/session.ts` on top of `getSession()` (the DAL's `requireAuth()` in `auth-patterns` is that helper under another name). The templates of this stack import it from `@/lib/session`.
2. **Tokens stay on the server.** The refresh token never reaches browser JavaScript. On the NextAuth path the access token does reach the browser through `useSession()` by default (it is short-lived and the user's own); decide on purpose whether that is acceptable.
3. **Never cache a user-scoped read** (`'use cache'`, tagged `fetch`). See "Cache" in `directus-to-nextjs`.
4. **`proxy.ts` only redirects.** It checks that a session cookie exists, nothing more. The page, the Server Action and the Route Handler check again. (In Next.js 16 `proxy.ts` replaces the old middleware file.)
5. **CORS is for browser to Directus only.** A Next.js server calling Directus ignores it. Set `CORS_ORIGIN` on Directus only when browser code, WebSockets or a session cookie talk to Directus directly.

## Reading Data as the Signed-In User (NextAuth path)

```typescript
// lib/user-directus.ts
import 'server-only';
import { readItems, withToken } from '@directus/sdk';
import directus from '@/lib/directus';
import { requireUser } from '@/lib/session';

/** The posts the signed-in user may see: Directus applies that user's own policies. */
export async function getMyPosts() {
  const session = await requireUser();
  return directus.request(
    withToken(session.accessToken, readItems('posts', { fields: ['id', 'title', 'status'] })),
  );
}
```

On the Better Auth path there is no user token: call the service-token client from `lib/content.ts` and decide in code which rows the user may see.

## Environment

| Path | Variables |
|------|-----------|
| NextAuth v4 | `NEXTAUTH_URL`, `NEXTAUTH_SECRET`, and `DIRECTUS_URL` (the NextAuth recipe reads it) |
| Better Auth | `BETTER_AUTH_URL`, `BETTER_AUTH_SECRET`, `DATABASE_URL` |
| Directus session cookie | `CORS_ORIGIN` and the `SESSION_COOKIE_*` settings on the Directus side |

The recipes in `nextjs-dev` and `directus-dev` read `DIRECTUS_URL`, `DIRECTUS_TOKEN` and `NEXT_PUBLIC_CMS_URL`; this stack names the same values `NEXT_PUBLIC_DIRECTUS_URL` and `DIRECTUS_ADMIN_TOKEN`:

| Recipe variable | This stack | How |
|-----------------|------------|-----|
| `DIRECTUS_URL` | `NEXT_PUBLIC_DIRECTUS_URL` | `DIRECTUS_URL=${NEXT_PUBLIC_DIRECTUS_URL}` in `.env.local` (Next.js expands `${VAR}` in `.env` files; `templates/.env.example` has the line) |
| `DIRECTUS_TOKEN` | `DIRECTUS_ADMIN_TOKEN` | `DIRECTUS_TOKEN=${DIRECTUS_ADMIN_TOKEN}` |
| `NEXT_PUBLIC_CMS_URL` (images block of `next.config.ts`, `nextjs-dev`) | `NEXT_PUBLIC_DIRECTUS_URL` | `NEXT_PUBLIC_CMS_URL=${NEXT_PUBLIC_DIRECTUS_URL}` |

Without these lines the NextAuth login calls `undefined/auth/login` and fails with no useful message. Set all three in the hosting environment too, where `.env.local` does not exist (a platform may not expand `${...}` the way `.env.local` does: give each name its value).
