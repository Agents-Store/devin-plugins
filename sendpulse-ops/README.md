# sendpulse-ops (Devin plugin)

Sendpulse multi-channel marketing plugin. Manage chatbots (Telegram, WhatsApp, Instagram, Messenger, Viber, TikTok), CRM (contacts, deals, pipelines, boards, tasks), Courses (LMS) academies, courses and students, email campaigns, templates, addressbooks, and SMTP transactional email via 147 MCP tools.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (12)

- `chatbot-contacts-messaging` — Chatbot contact management, direct messaging across channels, contact variables, tags, and notes. Use when sending messages to contacts, managing contact data, or looking up subscribers.
- `chatbot-management` — Chatbot bots, statistics, tags, campaigns, flows, and dialogs. Use when managing bots, sending chatbot campaigns, running automation flows, or viewing bot statistics.
- `courses-management` — SendPulse Courses (LMS) - academies, courses, pricing plans, student groups, tags, and students. Use when listing academies or courses, enrolling or removing students, marking students as paying, deleting a student, or checking student progress.
- `crm-boards-tasks` — CRM Kanban boards and task management — create boards, manage columns, create and track tasks. Use when organizing work, managing projects, or tracking task completion.
- `crm-contacts` — CRM contact management — create, update, search, list deals for contacts, and add comments. Use when working with CRM contacts, customer records, or contact-deal relationships.
- `crm-deals-pipelines` — CRM deals and sales pipelines — create and manage deals, configure pipeline stages, move deals between pipelines. Use when working with sales processes, deal tracking, or pipeline configuration.
- `crm-products` — CRM product catalog and deal-product associations. Use when managing product listings, adding products to deals, or viewing product-deal relationships.
- `email-addressbooks` — Email addressbook and subscriber management — create addressbooks, add/remove subscribers, manage variables, check sending costs. Use when managing mailing lists, subscriber data, or email list segmentation.
- `email-campaigns-templates` — Email campaign creation, management, statistics, and template management. Use when creating email campaigns, designing templates, or analyzing campaign performance.
- `email-senders-config` — Email sender management, email tags, blacklist management, and account balance. Use when configuring senders, managing email tags, handling blacklisted addresses, or checking account balance.
- `examples` — MCP tool call patterns, multi-channel marketing workflow examples, and scenario references. Use when you need reference implementations for Sendpulse operations.
- `smtp-transactional` — SMTP transactional email sending, bounce management, unsubscribe handling, IP and sender domain management. Use when sending transactional emails, managing bounces, or configuring SMTP infrastructure.

## Not carried over

- 2 agent(s) — Devin plugins do not support agents
- 15 command(s) — Devin plugins do not support commands
- MCP servers — Devin plugins do not support MCP server declarations

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/sendpulse-ops
