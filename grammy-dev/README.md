# grammy-dev (Devin plugin)

grammY (Telegram bot framework) dev plugin for Agents Store. Covers bot core, filter queries, middleware, commands, keyboards, sessions, conversations, files, payments, deployment, scaling, and the full @grammyjs/* plugin catalog for Node.js/Deno/TypeScript bot developers.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (16)

- `api-reference` — This skill should be used when the user asks for "grammY API reference", "Bot API method", "ctx.api signature", "sendMessage parameters", "answerCallbackQuery", "editMessageText", "getChat", "specific Telegram Bot API endpoint", or needs precise method signatures and parameter details for the grammY Bot API client.
- `commands-and-keyboards` — This skill should be used when the user asks about "slash commands in grammY", "bot.command", "setMyCommands", "inline keyboard", "reply keyboard", "callback query", "buttons in Telegram bot", or needs to add interactive commands and keyboards to a grammY bot.
- `conversations` — This skill should be used when the user asks about "grammY conversations plugin", "@grammyjs/conversations", "multi-step wizard", "ask user for input", "conversation.wait", "conversation.form", "checkpoint and rewind", "conversation menu", "wait timeout", "persist conversations", or needs to model multi-message dialog flows in a grammY bot.
- `deployment-hosting` — This skill should be used when the user asks about "deploy grammY bot", "webhookCallback", "long polling vs webhooks", "deploy to Cloudflare Workers", "deploy to Vercel", "deploy to Deno Deploy", "Fly.io grammY", "Heroku Telegram bot", "Supabase Edge Functions", "VPS bot deployment", "Firebase functions Telegram", "Zeabur", or needs to put a grammY bot into production.
- `error-handling` — This skill should be used when the user asks about "grammY error handling", "bot.catch", "GrammyError", "HttpError", "BotError", "errorBoundary", "bot crashed", "unhandled promise rejection in bot", or needs to understand the three error types grammY throws and how to catch them.
- `examples` — This skill should be used when the user asks "show me a complete grammY example", "give me a full grammY bot file", "example of a Telegram bot with menu", "complete echo bot in grammY", "example session counter", "example webhook bot Cloudflare Workers", "example conversation form bot", or wants end-to-end scenario walkthroughs rather than isolated snippets.
- `files-and-media` — This skill should be used when the user asks about "send photo in grammY", "send file", "send document", "send video", "InputFile", "send media group", "download user file", "getFile", "voice message", or needs to handle media uploads or downloads in a Telegram bot.
- `filter-queries` — This skill should be used when the user asks about "grammY filter query", "bot.on syntax", "listen for specific update types", "message:text", "filter photos", "filter URLs", or needs to understand grammY's filter-query DSL — the framework's signature feature for routing updates with type narrowing.
- `middleware` — This skill should be used when the user asks about "grammY middleware", "bot.use", "Composer", "middleware ordering", "skip handler", "compose plugins", "custom middleware", or needs to understand how grammY chains and routes update handlers.
- `payments-business-games` — This skill should be used when the user asks about "Telegram Stars in grammY", "sendInvoice", "pre_checkout_query", "successful_payment", "XTR currency", "Telegram payments", "Business connection", "business_message", "Telegram games", "createInvoiceLink", or needs to integrate Telegram payments, Business mode, or games into a grammY bot.
- `plugins-catalog` — This skill should be used when the user asks about "grammY plugins", "what plugins are available for grammY", "@grammyjs", "hydrate plugin", "parse-mode plugin", "i18n", "ratelimiter", "router", "emoji", "chat-members", "stateless-question", "fluent", "commands plugin", "stream plugin", "files plugin", or needs an overview of the official grammY plugin ecosystem.
- `scaling-runner` — This skill should be used when the user asks about "grammY runner", "@grammyjs/runner", "concurrent updates in grammY", "rate limit grammY", "transformer-throttler", "auto-retry", "sequentialize", "high-throughput Telegram bot", or needs to scale a grammY bot beyond default sequential polling.
- `sdk-patterns` — This skill should be used when the user asks about "grammY Bot class", "grammY Context object", "ctx.reply", "ctx.api", "send a message in grammY", "use grammY in code", or needs idiomatic grammY code patterns for everyday bot operations.
- `sessions` — This skill should be used when the user asks about "grammY session", "store user state", "ctx.session", "session storage", "Redis session", "MongoDB session", "PostgreSQL session", "free session storage", "lazy session", "multi session", or needs to persist per-chat data across messages.
- `setup` — This skill should be used when the user asks to "install grammY", "create a Telegram bot", "set up my first bot", "verify grammY installation", "get a bot token", "BotFather", or needs to bootstrap a brand-new grammY project from zero to a running echo bot.
- `troubleshoot` — This skill should be used when the user reports that "grammY bot is broken", "401 Unauthorized", "409 Conflict", "bot not responding", "double replies", "TypeScript error in grammY", "ctx.session is undefined", "conversations not working", "bot only responds once then stops", or any other grammY runtime / type / deployment failure.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/grammy-dev
