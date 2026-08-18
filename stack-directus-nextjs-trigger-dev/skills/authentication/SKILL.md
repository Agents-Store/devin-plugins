---
name: authentication
description: This skill should be used when the user wants to "add authentication to Directus + Next.js", "implement Directus login in Next.js", "use NextAuth with Directus", "protect Next.js pages with Directus auth", "set up cookie-based auth for Directus SSR", or needs patterns for authenticating users across Directus and Next.js.
---

# Authentication: Directus + NextAuth

Patterns for user authentication combining Directus as the identity provider with NextAuth.js for session management in Next.js.

## Two Authentication Modes

**1. Admin token (server-only)** — For backend operations, content fetching, and management tasks. Uses `staticToken()` on the Directus client. Already configured in `lib/directus.ts`.

**2. User authentication (cookie-based)** — For end-user login/registration. Uses NextAuth.js with a Directus CredentialsProvider. Described below.

## Install NextAuth

```bash
npm install next-auth
```

## NextAuth Configuration

Create `lib/auth.ts`:

```typescript
import type { NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'Directus',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) return null;

        const res = await fetch(`${process.env.NEXT_PUBLIC_DIRECTUS_URL}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: credentials.email,
            password: credentials.password,
          }),
        });

        if (!res.ok) return null;

        const { data } = await res.json();
        // data contains: access_token, refresh_token, expires

        // Fetch user profile with the access token
        const userRes = await fetch(`${process.env.NEXT_PUBLIC_DIRECTUS_URL}/users/me`, {
          headers: { Authorization: `Bearer ${data.access_token}` },
        });
        const { data: user } = await userRes.json();

        return {
          id: user.id,
          email: user.email,
          name: `${user.first_name ?? ''} ${user.last_name ?? ''}`.trim(),
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
          expiresAt: Date.now() + data.expires,
        };
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      // Initial sign-in: persist Directus tokens
      if (user) {
        token.accessToken = user.accessToken;
        token.refreshToken = user.refreshToken;
        token.expiresAt = user.expiresAt;
      }

      // Refresh token if expired
      if (Date.now() > (token.expiresAt as number)) {
        const res = await fetch(`${process.env.NEXT_PUBLIC_DIRECTUS_URL}/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: token.refreshToken }),
        });
        if (res.ok) {
          const { data } = await res.json();
          token.accessToken = data.access_token;
          token.refreshToken = data.refresh_token;
          token.expiresAt = Date.now() + data.expires;
        }
      }

      return token;
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken as string;
      return session;
    },
  },
  pages: {
    signIn: '/login',
  },
  secret: process.env.NEXTAUTH_SECRET,
};
```

## API Route Handler

Create `app/api/auth/[...nextauth]/route.ts`:

```typescript
import NextAuth from 'next-auth';
import { authOptions } from '@/lib/auth';

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
```

## Session Provider

Create `app/providers.tsx` (Client Component):

```typescript
'use client';
import { SessionProvider } from 'next-auth/react';

export default function Providers({ children }: { children: React.ReactNode }) {
  return <SessionProvider>{children}</SessionProvider>;
}
```

Wrap in `app/layout.tsx`:

```tsx
import Providers from './providers';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

## Middleware Protection

Create `middleware.ts` in the project root:

```typescript
import { getToken } from 'next-auth/jwt';
import { NextRequest, NextResponse } from 'next/server';

export async function middleware(request: NextRequest) {
  const token = await getToken({ req: request });

  if (!token) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('callbackUrl', request.url);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/admin/:path*'],
};
```

## Per-User Directus Client

Create a request-scoped Directus client using the authenticated user's token:

```typescript
import { createDirectus, rest, staticToken } from '@directus/sdk';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import type { Schema } from '@/types/directus';

export async function getUserDirectus() {
  const session = await getServerSession(authOptions);
  if (!session?.accessToken) throw new Error('Not authenticated');

  return createDirectus<Schema>(process.env.NEXT_PUBLIC_DIRECTUS_URL!)
    .with(staticToken(session.accessToken))
    .with(rest({ cache: 'no-store' }));
}
```

Use in Server Components for user-scoped data:

```typescript
const directus = await getUserDirectus();
const myPosts = await directus.request(readItems('posts'));
// Returns only posts the user has permission to see
```

## Login Page

Create `app/login/page.tsx`:

```typescript
'use client';
import { signIn } from 'next-auth/react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useState } from 'react';

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState('');

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);

    const result = await signIn('credentials', {
      email: formData.get('email'),
      password: formData.get('password'),
      redirect: false,
    });

    if (result?.error) {
      setError('Invalid email or password');
    } else {
      router.push(searchParams.get('callbackUrl') || '/dashboard');
    }
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

## TypeScript Augmentation

Extend NextAuth types to include Directus tokens. Create `types/next-auth.d.ts`:

```typescript
import 'next-auth';

declare module 'next-auth' {
  interface User {
    accessToken: string;
    refreshToken: string;
    expiresAt: number;
  }
  interface Session {
    accessToken: string;
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    accessToken: string;
    refreshToken: string;
    expiresAt: number;
  }
}
```

## CORS Configuration

Directus must allow requests from the Next.js domain. Set in Directus environment:

```
CORS_ENABLED=true
CORS_ORIGIN=http://localhost:3000,https://your-production-domain.com
```

For Docker local dev, this is already configured in `docker-compose.yml`.

## Authenticated tasks

When a Trigger.dev task needs to act **as a specific user** (instead of with the global admin token), pass the user's Directus access token into the task payload and rebuild the SDK client inside the task with `staticToken(payload.accessToken)`. Do NOT log the token. Prefer passing the user ID and re-issuing a short-lived token from a service role if the task runs long enough that the user's session may expire. See `directus-to-trigger` for the full pattern.
