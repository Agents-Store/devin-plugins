---
name: plugin-development
description: Plugin scaffolding and development — lifecycle, server-side, client-side, migrations, testing. This skill should be used when the user asks to develop custom plugins, extend platform functionality, or scaffold plugin structure.
---

# Plugin Development

Expert guidance on developing NocoBase plugins — lifecycle, server-side APIs, client-side components, migrations, and best practices.

## Plugin Structure

```
packages/plugins/@my-project/plugin-name/
├── package.json
├── src/
│   ├── index.ts              # Re-exports
│   ├── server/
│   │   ├── index.ts          # Server entry point
│   │   ├── plugin.ts         # Server plugin class
│   │   ├── collections/      # Collection definitions
│   │   │   └── my_table.ts
│   │   ├── actions/          # Custom API actions
│   │   │   └── myAction.ts
│   │   ├── resources/        # REST resources
│   │   ├── migrations/       # Database migrations
│   │   │   └── 20240101-init.ts
│   │   └── middleware/       # Custom middleware
│   └── client/
│       ├── index.ts          # Client entry point
│       ├── plugin.ts         # Client plugin class
│       ├── components/       # React components
│       ├── initializers/     # Schema initializers
│       └── settings/         # Schema settings
└── README.md
```

## Plugin Lifecycle

```
load → install → enable → (running) → disable → remove

load:    Register collections, actions, middleware
install: Run migrations, seed data
enable:  Activate the plugin
disable: Deactivate (data preserved)
remove:  Uninstall (optional: clean data)
```

## Server Plugin Class

```typescript
import { Plugin } from '@nocobase/server';

export class MyPlugin extends Plugin {
  async afterAdd() {
    // Called after plugin is added to app
  }

  async beforeLoad() {
    // Called before load — register event listeners
  }

  async load() {
    // Main initialization
    // Register collections, actions, middleware, resources

    // Register collection
    this.db.collection({
      name: 'my_records',
      fields: [
        { type: 'string', name: 'title' },
        { type: 'text', name: 'content' },
        { type: 'boolean', name: 'published', defaultValue: false },
      ],
    });

    // Register action
    this.app.resource({
      name: 'my_records',
      actions: {
        async publish(ctx, next) {
          const { filterByTk } = ctx.action.params;
          await ctx.db.getRepository('my_records').update({
            filterByTk,
            values: { published: true, publishedAt: new Date() },
          });
          ctx.body = { success: true };
          await next();
        },
      },
    });

    // Register middleware
    this.app.acl.allow('my_records', 'list', 'loggedIn');
    this.app.acl.allow('my_records', 'publish', 'admin');
  }

  async install() {
    // Run on first install — seed data, initial config
  }

  async afterEnable() {
    // Plugin is now active
  }

  async afterDisable() {
    // Plugin is now inactive
  }

  async remove() {
    // Cleanup on uninstall
  }
}
```

## Client Plugin Class

```typescript
import { Plugin } from '@nocobase/client';
import { MyComponent } from './components/MyComponent';

export class MyPlugin extends Plugin {
  async load() {
    // Register components
    this.app.addComponents({
      MyComponent,
    });

    // Add menu item
    this.app.pluginSettingsManager.add('my-plugin', {
      title: 'My Plugin Settings',
      icon: 'SettingOutlined',
      Component: MyPluginSettings,
    });

    // Register schema initializer
    this.app.schemaInitializerManager.addItem(
      'BlockInitializers',
      'otherBlocks.myBlock',
      {
        title: 'My Custom Block',
        Component: MyBlockInitializer,
      }
    );
  }
}
```

## Collections Definition

```typescript
// src/server/collections/tasks.ts
import { CollectionOptions } from '@nocobase/database';

export default {
  name: 'tasks',
  title: 'Tasks',
  fields: [
    {
      type: 'string',
      name: 'title',
      required: true,
    },
    {
      type: 'text',
      name: 'description',
    },
    {
      type: 'string',
      name: 'status',
      interface: 'select',
      uiSchema: {
        enum: [
          { value: 'todo', label: 'To Do' },
          { value: 'in_progress', label: 'In Progress' },
          { value: 'done', label: 'Done' },
        ],
      },
      defaultValue: 'todo',
    },
    {
      type: 'date',
      name: 'dueDate',
    },
    {
      type: 'belongsTo',
      name: 'assignee',
      target: 'users',
    },
  ],
} as CollectionOptions;
```

## Migrations

```typescript
// src/server/migrations/20240101-add-priority-field.ts
import { Migration } from '@nocobase/server';

export default class AddPriorityField extends Migration {
  async up() {
    const collection = this.db.getCollection('tasks');
    if (!collection.hasField('priority')) {
      collection.addField('priority', {
        type: 'string',
        interface: 'select',
        uiSchema: {
          enum: [
            { value: 'low', label: 'Low' },
            { value: 'medium', label: 'Medium' },
            { value: 'high', label: 'High' },
          ],
        },
        defaultValue: 'medium',
      });
      await this.db.sync();
    }
  }

  async down() {
    const collection = this.db.getCollection('tasks');
    collection.removeField('priority');
    await this.db.sync();
  }
}
```

## Custom Actions

```typescript
// src/server/actions/batchAssign.ts
export async function batchAssign(ctx, next) {
  const { filter, values } = ctx.action.params;
  const { assigneeId } = values;

  const repo = ctx.db.getRepository('tasks');
  const updated = await repo.update({
    filter,
    values: { assigneeId },
  });

  ctx.body = {
    updated: updated.length,
    message: `${updated.length} tasks assigned`,
  };

  await next();
}
```

## package.json Template

```json
{
  "name": "@my-project/plugin-name",
  "version": "0.1.0",
  "main": "dist/server/index.js",
  "client": "dist/client/index.js",
  "devDependencies": {
    "@nocobase/server": "workspace:*",
    "@nocobase/client": "workspace:*",
    "@nocobase/database": "workspace:*",
    "@nocobase/test": "workspace:*"
  }
}
```

## Best Practices

1. **One responsibility per plugin** — keep plugins focused and composable
2. **Use migrations** — never modify schema directly, always use migrations
3. **Follow naming conventions** — snake_case for collections, camelCase for fields
4. **Set ACL permissions** — always configure access control for new resources
5. **Handle errors** — add try/catch in custom actions
6. **Test with @nocobase/test** — use the built-in testing utilities
7. **Document your plugin** — README with setup instructions and configuration
8. **Use existing APIs** — leverage NocoBase's Repository and Collection APIs
9. **Support disable/remove** — clean up properly when plugin is deactivated
10. **Version your migrations** — use date-based naming for migration order
