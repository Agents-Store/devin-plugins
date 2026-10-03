# Access Control (Policies) with the SDK

Moved out of `SKILL.md` to keep it short. Uses the `client` from the Client Setup section. The REST view of the same model is in the `api-reference` skill (`references/endpoints-system.md`).

Permissions belong to policies, which are attached to roles or users. Create the policy, then its permissions, then the role, then the attachment:

```typescript
import { createPolicy, createPermission, createRole, customEndpoint, readUserPermissions } from '@directus/sdk';

const policy = await client.request(
  createPolicy({ name: 'Blog Editor', icon: 'edit', app_access: true, admin_access: false }),
);

await client.request(
  createPermission({
    policy: policy.id,
    collection: 'posts',
    action: 'read',
    fields: ['*'],
    permissions: {},
    validation: {},
  }),
);

const role = await client.request(createRole({ name: 'Blog Editors', icon: 'edit' }));

// Attach the policy to the role: a row in directus_access (REST /access)
await client.request(
  customEndpoint({
    path: '/access',
    method: 'POST',
    body: JSON.stringify({ role: role.id, policy: policy.id }),
  }),
);

// What can the current token do? One entry per collection with none | partial | full per action
const mine = await client.request(readUserPermissions());
```

A role no longer holds `admin_access`, `app_access`, `enforce_tfa` or `ip_access`; those are policy fields.
