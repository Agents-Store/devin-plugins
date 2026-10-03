# NextAuth v4 and Auth.js v5 for Existing Projects

For codebases that already run NextAuth, and for a credentials login against an existing token API. New projects should start with Better Auth (see `SKILL.md`). The proxy, DAL, Server Action and Route Handler layering in `SKILL.md` is library independent: only the session helper changes.

## NextAuth v4 (`next-auth@latest`, 4.24.x)

A working path with Next.js 16, not a deprecated one: v4 is still what `npm i next-auth` installs (v5 is published only as `next-auth@beta`). The recipe below signs users in against Directus with the Credentials provider and keeps the Directus tokens in the encrypted session cookie; swap the three `fetch` calls for another token-issuing API.

**One rule shapes the recipe: only the NextAuth route may refresh the Directus tokens.** A Directus refresh token is single use, and `getServerSession()` cannot write cookies from a Server Component, Server Action or Route Handler. If server code refreshed, it would spend the refresh token and lose the new pair, and the next refresh would fail. So there are two option sets: `authOptions` (used by the `[...nextauth]` route, refreshes) and `sessionOptions` (used by `getServerSession`, never refreshes). The Directus side (payloads, `expires` in milliseconds, single-use refresh tokens) is in the `directus-dev` plugin, skill `sdk-patterns`, `references/ssr-client.md`.

```bash
npm install next-auth
```

```bash
# .env.local: generate the secret with: openssl rand -base64 32
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=<random-string>
DIRECTUS_URL=<address-of-your-directus>
```

```typescript
// lib/session-timing.ts
// Shared by the route (when to refresh) and the provider (how often to poll). Keep the order:
//   poll interval < refresh-ahead window < access token lifetime (Directus default: 15 minutes)
export const SESSION_POLL_SECONDS = 4 * 60;
// Poll interval plus a minute: whenever the tab polls, a poll lands inside the window before expiry
export const REFRESH_AHEAD_MS = (SESSION_POLL_SECONDS + 60) * 1000;
```

```typescript
// lib/auth.ts
import type { NextAuthOptions } from 'next-auth';
import type { JWT } from 'next-auth/jwt';
import CredentialsProvider from 'next-auth/providers/credentials';
import { REFRESH_AHEAD_MS } from '@/lib/session-timing';

type TokenResponse = { access_token: string; refresh_token: string; expires: number };

async function refreshTokens(token: JWT): Promise<JWT> {
  try {
    const res = await fetch(`${process.env.DIRECTUS_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: token.refreshToken, mode: 'json' }),
    });
    // Directus refused the token (spent, expired, revoked): it is dead, stop trying with it
    if (res.status === 400 || res.status === 401 || res.status === 403) {
      return { ...token, error: 'RefreshTokenError' };
    }
    // Directus down or erroring: keep the token as it is and try again on the next poll
    if (!res.ok) return token;
    const { data }: { data: TokenResponse } = await res.json();
    return {
      ...token,
      accessToken: data.access_token,
      refreshToken: data.refresh_token, // the old refresh token is now dead
      expiresAt: Date.now() + data.expires,
      error: undefined,
    };
  } catch {
    return token; // network failure: same as above
  }
}

export const authOptions: NextAuthOptions = {
  // Keep the session no longer than the refresh token lives (Directus default: 7 days)
  session: { strategy: 'jwt', maxAge: 7 * 24 * 60 * 60 },
  providers: [
    CredentialsProvider({
      name: 'Directus',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials.password) return null;

        const login = await fetch(`${process.env.DIRECTUS_URL}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: credentials.email, password: credentials.password, mode: 'json' }),
        });
        if (!login.ok) return null;
        const { data }: { data: TokenResponse } = await login.json();

        const meRes = await fetch(`${process.env.DIRECTUS_URL}/users/me?fields=id,email,first_name,last_name`, {
          headers: { Authorization: `Bearer ${data.access_token}` },
        });
        if (!meRes.ok) return null;
        const { data: me } = await meRes.json();

        return {
          id: me.id,
          email: me.email,
          name: `${me.first_name ?? ''} ${me.last_name ?? ''}`.trim(),
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
          expiresAt: Date.now() + data.expires,
        };
      },
    }),
  ],
  callbacks: {
    // Runs in the [...nextauth] route only (see sessionOptions below for everything else)
    async jwt({ token, user }) {
      // First call after sign-in: `user` is what authorize() returned
      if (user) {
        return { ...token, accessToken: user.accessToken, refreshToken: user.refreshToken, expiresAt: user.expiresAt };
      }
      if (token.error) return token; // a dead refresh token is never retried
      // Refresh ahead of expiry: the next poll is at most SESSION_POLL_SECONDS away, so waiting
      // for the real expiry would leave the cookie expired between two polls
      if (Date.now() < token.expiresAt - REFRESH_AHEAD_MS) return token;
      return refreshTokens(token);
    },
    async session({ session, token }) {
      session.user.id = token.sub ?? '';
      session.accessToken = token.accessToken; // visible to browser code through useSession(): see below
      // 'AccessTokenExpired' means a real expiry: no poll reached the route for the whole token lifetime
      session.error = token.error ?? (Date.now() >= token.expiresAt ? 'AccessTokenExpired' : undefined);
      return session;
    },
  },
  pages: { signIn: '/login' },
};

/**
 * For getServerSession(): the same options, but the jwt callback never refreshes.
 * Server code cannot save a refreshed cookie, and refreshing would spend the single-use
 * refresh token. An expired access token shows up as session.error = 'AccessTokenExpired'.
 */
export const sessionOptions: NextAuthOptions = {
  ...authOptions,
  callbacks: {
    ...authOptions.callbacks,
    async jwt({ token }) {
      return token;
    },
  },
};
```

```typescript
// types/next-auth.d.ts
import type { DefaultSession } from 'next-auth';

declare module 'next-auth' {
  interface User {
    accessToken: string;
    refreshToken: string;
    expiresAt: number;
  }
  interface Session {
    user: { id: string } & DefaultSession['user'];
    accessToken: string;
    error?: 'RefreshTokenError' | 'AccessTokenExpired';
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    accessToken: string;
    refreshToken: string;
    expiresAt: number;
    error?: 'RefreshTokenError';
  }
}
```

```typescript
// app/api/auth/[...nextauth]/route.ts
import NextAuth from 'next-auth';
import { authOptions } from '@/lib/auth';

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
```

```tsx
// app/providers.tsx
'use client';
import { SessionProvider } from 'next-auth/react';
import { SESSION_POLL_SECONDS } from '@/lib/session-timing';

export default function Providers({ children }: { children: React.ReactNode }) {
  // Every poll is a call to /api/auth/session: the only place the Directus tokens are refreshed
  return (
    <SessionProvider refetchInterval={SESSION_POLL_SECONDS} refetchOnWindowFocus>
      {children}
    </SessionProvider>
  );
}
```

Wrap `children` in `app/layout.tsx` with `<Providers>`. The session helpers used by the rest of the app:

```typescript
// lib/session.ts
import 'server-only';
import { getServerSession } from 'next-auth';
import { headers } from 'next/headers';
import { redirect } from 'next/navigation';
import { sessionOptions } from '@/lib/auth';

/** The signed-in session, or a redirect to /login. Call it first in every Server Action and Route Handler. */
export async function requireUser() {
  const session = await getServerSession(sessionOptions);
  if (!session?.user || session.error) {
    const path = (await headers()).get('x-pathname'); // set by proxy.ts on the protected routes
    // The login page treats callbackUrl as untrusted and checks it (safeCallbackUrl)
    redirect(path ? `/login?callbackUrl=${encodeURIComponent(path)}` : '/login');
  }
  return session;
}
```

Use `sessionOptions` for every `getServerSession()` call, and `authOptions` only in the route handler.

### Proxy guard (Next.js 16)

`middleware.ts` is deprecated in Next.js 16; the file is `proxy.ts` and the function is `proxy`. `getToken` decodes the session cookie without a database or network call, so it is safe to use there:

```typescript
// proxy.ts
import { getToken } from 'next-auth/jwt';
import { NextResponse, type NextRequest } from 'next/server';

export async function proxy(request: NextRequest) {
  const token = await getToken({ req: request });
  if (!token || token.error) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('callbackUrl', request.nextUrl.pathname + request.nextUrl.search);
    return NextResponse.redirect(loginUrl);
  }
  // Hand the path to server code, so requireUser() can send the user back here after signing in
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set('x-pathname', request.nextUrl.pathname + request.nextUrl.search);
  return NextResponse.next({ request: { headers: requestHeaders } });
}

export const config = { matcher: ['/dashboard/:path*', '/admin/:path*'] };
```

This is an optimistic check, as everywhere in this skill: pages, Server Actions and Route Handlers still call `requireUser()`.

### Login page

`callbackUrl` comes from the address bar, so treat it as hostile. Checking the first characters is not enough: the URL parser used by browsers silently drops TAB, LF and CR, so `/%09/evil.example` (a slash, a tab, a slash) is a link to another site once parsed. Parse the value with the `URL` class and compare the origin:

```typescript
// lib/safe-callback-url.ts
/**
 * A same-site destination from a ?callbackUrl= value, or the fallback. Browser code only.
 * Parse first, then compare the origin: the URL parser removes TAB, LF and CR, so
 * "/<TAB>/evil.example" becomes "//evil.example".
 */
export function safeCallbackUrl(value: string | null, fallback = '/dashboard'): string {
  if (!value || /[\u0000-\u001f\u007f\\]/.test(value)) return fallback; // control characters and backslashes
  try {
    const url = new URL(value, window.location.origin);
    if (url.origin !== window.location.origin) return fallback; // other host, other scheme (javascript:)
    const path = url.pathname + url.search + url.hash;
    // Only a rooted path may leave here. "/..//evil.example" normalizes to "//evil.example", and a same-origin
    // "blob:<origin>/<id>" keeps the origin but has a pathname that is a whole absolute URL.
    return path.startsWith('/') && !path.startsWith('//') ? path : fallback;
  } catch {
    return fallback;
  }
}
```

```tsx
// app/login/page.tsx
'use client';
import { getSession, signIn } from 'next-auth/react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { safeCallbackUrl } from '@/lib/safe-callback-url';

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState('');

  // requireUser() may have sent the user here only because the cookie's access token expired.
  // getSession() is a fresh call to /api/auth/session, which is where the refresh happens and the
  // cookie is saved. If it comes back without an error, the user is signed in and goes on.
  useEffect(() => {
    let cancelled = false;
    getSession().then((fresh) => {
      if (!cancelled && fresh && !fresh.error) router.replace(safeCallbackUrl(searchParams.get('callbackUrl')));
    });
    return () => {
      cancelled = true;
    };
  }, [router, searchParams]);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const result = await signIn('credentials', {
      email: formData.get('email'),
      password: formData.get('password'),
      redirect: false,
    });
    if (result?.error) setError('Invalid email or password');
    else router.push(safeCallbackUrl(searchParams.get('callbackUrl')));
  }

  return (
    <form onSubmit={handleSubmit}>
      <input name="email" type="email" required />
      <input name="password" type="password" required />
      {error && <p>{error}</p>}
      <button type="submit">Sign In</button>
    </form>
  );
}
```

`useSearchParams()` in a statically rendered page needs a `<Suspense>` boundary around the component that calls it.

### Limits to know before choosing v4

- **Refresh depends on a browser polling.** Only `/api/auth/session` (called by `SessionProvider` on mount, on focus and every `SESSION_POLL_SECONDS`) refreshes and saves the tokens. The route's `jwt` callback refreshes once less than `REFRESH_AHEAD_MS` of the access token is left (5 minutes with a 4-minute poll), so one poll always falls inside that window and the cookie is renewed before it expires, for as long as the tab polls. A sleeping laptop, or a background tab that the browser throttles for more than about a minute, can still miss the window. With no poll for the whole access token lifetime, server code sees `AccessTokenExpired` and `requireUser()` redirects to `/login?callbackUrl=<path>`; the login page's `getSession()` call refreshes from the still-unspent refresh token and returns the user to the path (anything typed into a form before the redirect is lost). Keep the order poll interval < refresh-ahead window < access token lifetime in `lib/session-timing.ts`; if you lengthen the poll, lengthen the window, and if the token lives shorter than the poll the cookie will expire between polls. If Directus refuses the refresh token (spent, expired after 7 days, revoked), `RefreshTokenError` is stored and never retried: the user signs in again.
- **Two tabs can race.** Two requests to `/api/auth/session` that are in flight at the same moment both carry the old refresh token. The second one is refused and stores `RefreshTokenError` over the first one's good cookie. The window is narrow (browsers share the cookie jar, so a later request sends the new token), but it exists, and Directus offers no way around single-use refresh tokens. If this matters for your users, choose Better Auth.
- **The access token is readable in the browser.** `session.accessToken` is returned by `/api/auth/session` and `useSession()`. It is short-lived and belongs to the signed-in user, and the refresh token stays inside the encrypted cookie, but any script running in the page can read it. If that is not acceptable, do not copy it into `session`; call the API only from server code with a server credential.
- **No rate limit.** NextAuth does not throttle credential sign-ins. Put a limit in front of `/api/auth/callback/credentials`.

## Auth.js v5 (`next-auth@beta`)

> Auth.js v5 is still published as `next-auth@beta` and the project is in maintenance mode under Better Auth. Prefer Better Auth for new work; use this section when maintaining an Auth.js codebase.

```bash
npm install next-auth@beta
```

```typescript
// auth.ts
import NextAuth from 'next-auth'
import GitHub from 'next-auth/providers/github'

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [GitHub],
})
```

```typescript
// app/api/auth/[...nextauth]/route.ts
import { handlers } from '@/auth'
export const { GET, POST } = handlers
```

```tsx
// Usage in Server Components
import { auth } from '@/auth'

export default async function Page() {
  const session = await auth()
  if (!session?.user) return <p>Not signed in</p>
  return <p>Welcome, {session.user.name}</p>
}
```

v5 uses the `AUTH_` prefix for its settings (`AUTH_SECRET`, `AUTH_URL`); the examples above for v4 use `NEXTAUTH_SECRET` and `NEXTAUTH_URL`.
