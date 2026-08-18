---
name: mcp-plugin
description: Use this skill when the user is integrating the Model Context Protocol with a Microsoft Teams app — exposing the Teams bot's tools as an MCP server with `McpPlugin`, consuming a remote MCP server from inside the bot, configuring `@microsoft/teams.mcp`, or wiring an A2A flow. Triggers on "Teams MCP", "MCP plugin Teams", "expose tools as MCP", "McpPlugin", "A2AClientPlugin".
---

# MCP and A2A in Teams (`@microsoft/teams.mcp`)

`@microsoft/teams.mcp` ships two plugins:
- `McpPlugin` — turn your Teams bot into an MCP server that any LLM host can call.
- `A2AClientPlugin` — let your bot's `ChatPrompt` delegate to remote A2A-compatible agents.

Both plug into `new App({ plugins: [...] })`.

## 1. Expose tools as an MCP server

```ts
import { App } from '@microsoft/teams.apps';
import { McpPlugin } from '@microsoft/teams.mcp';

const mcp = new McpPlugin({ port: 4000 });

mcp.tool({
  name: 'list_open_tickets',
  description: 'List support tickets currently in open status',
  inputSchema: {
    type: 'object',
    properties: { ownerEmail: { type: 'string' } },
    required: [],
  },
  handler: async (args) => {
    const tickets = await ticketStore.list({ ownerEmail: args.ownerEmail, status: 'open' });
    return { content: [{ type: 'text', text: JSON.stringify(tickets) }] };
  },
});

mcp.resource({
  uri: 'tickets://open',
  name: 'Open tickets',
  description: 'Live list of open tickets',
  read: async () => ({ contents: [{ uri: 'tickets://open', mimeType: 'application/json', text: JSON.stringify(await ticketStore.list({ status: 'open' })) }] }),
});

const app = new App({ plugins: [mcp] });
await app.start();
```

The plugin serves the MCP protocol at `http://<host>:<port>/mcp`. Inspect it with the DevTools plugin's MCP tab.

## 2. Why expose Teams tools as MCP

- Reuse the same business logic in chat-driven LLM hosts (Claude Desktop, Cursor, Copilot).
- Let one team consume another team's bot as a tool, without sharing internal APIs.
- Drive the same tool surface from both Teams users (chat handlers) and outside callers (MCP).

## 3. Consume a remote MCP server inside the bot

```ts
import { A2AClientPlugin } from '@microsoft/teams.mcp';

const app = new App({
  plugins: [
    new A2AClientPlugin({
      agents: [
        { name: 'docs', url: 'https://docs.example.com/a2a' },
      ],
    }),
  ],
});
```

When the local `ChatPrompt` calls a tool whose name matches a remote agent, `A2AClientPlugin` routes the JSON-RPC payload to the remote URL and returns the response as a tool message. Function-call routing happens transparently.

## 4. Authentication

MCP traffic is usually trusted internal-network traffic. If the server is exposed externally, gate it with a bearer token:

```ts
new McpPlugin({
  port: 4000,
  authenticate: async (req) => req.headers.authorization === `Bearer ${process.env.MCP_TOKEN}`,
});
```

The `authenticate` callback is invoked per request before any tool runs. Reject by returning `false`.

## 5. Sharing types between server and bot

Define the tool schema once and re-use it on both sides. With Zod:

```ts
import { z } from 'zod';
import { zodToJsonSchema } from 'zod-to-json-schema';

const ListTicketsArgs = z.object({ ownerEmail: z.string().email().optional() });

mcp.tool({
  name: 'list_open_tickets',
  inputSchema: zodToJsonSchema(ListTicketsArgs),
  handler: async (args) => {
    const parsed = ListTicketsArgs.parse(args);
    return { content: [{ type: 'text', text: JSON.stringify(await ticketStore.list({ ...parsed, status: 'open' })) }] };
  },
});
```

## 6. Inspecting MCP locally

Run with `DevtoolsPlugin`:

```ts
new App({ plugins: [new DevtoolsPlugin(), mcp] });
```

Open `http://localhost:3979/devtools` → MCP tab. The inspector lists registered tools/resources and the latest request/response payloads — invaluable for debugging tool schemas.

## Common pitfalls

- **Tool fires twice in `ChatPrompt`** — both `prompt.function(...)` and `mcp.tool(...)` registered the same name; pick one host per tool.
- **MCP requests time out** — handler throws synchronously; wrap in `try/catch` and return an error content block (`{ content: [{ type: 'text', text: 'error: ...' }], isError: true }`).
- **A2A agent never selected** — the local prompt has no description telling the model when to use that agent; add a tool stub locally that explicitly delegates ("Use 'docs' for documentation lookups").
- **MCP port in use** — pick a port that isn't already taken by another service in `.env`.
