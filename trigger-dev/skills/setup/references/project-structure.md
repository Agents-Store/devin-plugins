# Project Structure

Standard Trigger.dev project layout.

```
your-project/
├── trigger.config.ts       # Required — project configuration
├── src/trigger/             # Required — task files (configurable via dirs)
│   ├── my-task.ts
│   ├── another-task.ts
│   └── streams.ts           # Optional — realtime stream definitions
├── package.json
├── .env                     # TRIGGER_SECRET_KEY, TRIGGER_API_URL
└── ...
```

## Configuration File

`trigger.config.ts` must be in the project root:

```ts
import { defineConfig } from "@trigger.dev/sdk";

export default defineConfig({
  project: "proj_xxxxx",
  dirs: ["./src/trigger"],    // Where to find task files
  runtime: "node",            // "node", "node-22", or "bun"
  logLevel: "info",
});
```

## Task File Conventions

- Tasks must be **exported** from files within the `dirs` directories
- Each file can contain one or more tasks
- Task IDs must be unique across the project
- Use descriptive kebab-case IDs: `process-order`, `send-email`, `daily-cleanup`

## Monorepo Support

For monorepos, point to the config explicitly:

```bash
npx trigger.dev@latest dev --config ./packages/jobs/trigger.config.ts
npx trigger.dev@latest deploy --config ./packages/jobs/trigger.config.ts
```

## Multiple Task Directories

```ts
export default defineConfig({
  project: "proj_xxxxx",
  dirs: ["./src/trigger", "./src/jobs", "./src/scheduled"],
});
```
