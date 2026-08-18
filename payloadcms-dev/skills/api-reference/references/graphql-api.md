# GraphQL API — Reference

Endpoint: `POST /api/graphql`. Auto-generated from collections, globals, and locales — no separate schema file to maintain. Playground at `/api/graphql-playground` in dev.

## Schema Generation Rules

For collection `posts`, Payload generates:
- Type `Post` (singular, PascalCase from slug).
- Type `Posts` (paginated result wrapper).
- Query `Post(id: ID!, draft: Boolean, locale: LocaleInputType, fallbackLocale: FallbackLocaleInputType): Post`.
- Query `Posts(where, sort, limit, page, draft, locale): Posts`.
- Query `countPosts(where, locale): count_Posts!`.
- Mutation `createPost(data: mutationPostInput!): Post`.
- Mutation `updatePost(id: ID!, data: mutationPostUpdateInput!): Post`.
- Mutation `deletePost(id: ID!): Post`.

For auth-enabled `users`, also:
- Mutation `loginUser(email: String!, password: String!): usersLoginResult`.
- Mutation `logoutUser: String`.
- Mutation `forgotPasswordUser(email: String!): Boolean`.
- Mutation `resetPasswordUser(token: String!, password: String!): usersResetPassword`.
- Query `meUser: usersMe`.

For each `relationship` field with `relationTo: 'posts'`, the related type populates inline up to `depth`.

## Query Example

```graphql
query Posts($status: Post_status_Operator) {
  Posts(
    where: { status: { equals: $status } }
    sort: "-publishedAt"
    limit: 20
    depth: 2
  ) {
    docs {
      id
      title
      slug
      publishedAt
      author { id name email }
      tags { id label }
    }
    totalDocs
    totalPages
    page
    hasNextPage
    nextPage
  }
}
```

Variables:
```json
{ "status": { "equals": "published" } }
```

## Mutation Example

```graphql
mutation CreatePost($data: mutationPostInput!) {
  createPost(data: $data) {
    id
    slug
  }
}
```

Variables:
```json
{
  "data": {
    "title": "Hello",
    "slug": "hello",
    "status": "draft",
    "content": [/* Lexical JSON */]
  }
}
```

## Auth Headers

Same as REST:
```
Authorization: JWT <token>
```

Or rely on the `payload-token` cookie.

## Globals

Each global gets `Query <Slug>` and `Mutation update<Slug>`:

```graphql
query {
  SiteSettings {
    siteName
    logo { url }
  }
}

mutation {
  updateSiteSettings(data: { siteName: "New Name" }) {
    siteName
  }
}
```

## Versions

Per-collection version queries are generated when versions are enabled:

```graphql
query {
  versionsPost(id: "...") {
    id
    parent
    version { title slug }
    createdAt
  }
}

query {
  versionsPosts(limit: 10) {
    docs {
      id
      version { title }
    }
  }
}
```

## Field-Level Operator Types

Where clauses become typed inputs. For a text field `title`, GraphQL emits:
```graphql
input Post_title_Operator {
  equals: String
  not_equals: String
  like: String
  contains: String
  in: [String]
  not_in: [String]
  all: [String]
  exists: Boolean
}
```

This means you get **type-safe filtering** in your IDE — no JSON-stringified `where` clauses.

## Localization

```graphql
query {
  Post(id: "...", locale: es, fallbackLocale: en) {
    title
    content
  }
}
```

`locale` is an enum generated from `localization.locales`.

## Drafts

```graphql
query {
  Posts(where: { _status: { equals: draft } }, draft: true) {
    docs { id title _status }
  }
}
```

## Custom GraphQL

Extend the schema with custom queries / mutations:

```ts
// payload.config.ts
import type { Config } from 'payload'

export default buildConfig({
  // …
  graphQL: {
    queries: (GraphQL, payload) => ({
      MyCustom: {
        type: new GraphQL.GraphQLObjectType({
          name: 'MyCustom',
          fields: { result: { type: GraphQL.GraphQLString } },
        }),
        args: {
          input: { type: GraphQL.GraphQLString },
        },
        resolve: async (_root, args, context) => {
          return { result: `echo: ${args.input}` }
        },
      },
    }),
    mutations: (GraphQL, payload) => ({
      // …
    }),
    schemaOutputFile: path.resolve(dirname, 'schema.graphql'),
  },
})
```

Write to disk with the `payload-graphql` bin (ships with `@payloadcms/graphql` — the `payload` bin has no GraphQL schema command):
```bash
pnpm payload-graphql generate:schema
```

## Code Generation

Use `@graphql-codegen/cli` against the introspection URL:

```yaml
# codegen.yml
schema: http://localhost:3000/api/graphql
documents: 'src/**/*.graphql'
generates:
  src/gql/types.ts:
    plugins:
      - typescript
      - typescript-operations
      - typed-document-node
```

Run during dev:
```bash
pnpm graphql-codegen
```

You now get fully typed queries against the Payload schema — type-safe variables and return values in a frontend client (urql, Apollo, fetch).

## Disabling GraphQL

If you don't need it (typed Local API is usually enough):
```ts
graphQL: { disable: true }
```

Removes the route and reduces bundle size.

## Caveats

- Mutations don't accept `req` (the HTTP request gives you that). Use Local API or REST for fine-grained transaction control across multiple ops.
- Nested mutations are not federated — for multi-step writes call them sequentially from the client OR write a custom mutation in `graphQL.mutations`.
- Custom field components, custom views, and admin-only behavior aren't exposed over GraphQL — schema reflects the data layer only.
