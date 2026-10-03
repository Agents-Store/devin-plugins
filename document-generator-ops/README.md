# document-generator-ops (Devin plugin)

Professional document generator. Creates proposals, invoices, estimates/quotations, reports, presentations, contracts, NDAs, and certificates of completion in PDF, DOCX, and PPTX formats. Supports multi-language documents with embedded fonts (Cyrillic, Latin). First-use onboarding for style preferences, company profiles, and logo management. Converts between MD, DOCX, PDF, HTML, and PPTX.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (7)

- `design-best-practices` — Comprehensive library of professional document design best practices sourced from top consulting firms (McKinsey, Deloitte, BCG), tech leaders (Stripe, Apple, Google), and typography/layout research. Use this skill when making design decisions, choosing fonts, colors, layouts, or when the user asks for a "professional" or "corporate" look.
- `document-generator` — Document generation process -- format selection, data collection, script invocation, and delivery. This skill should be used when generating any document (proposal, invoice, estimate, report, presentation, contract, NDA, certificate of completion), deciding which format or engine to use, or running generation scripts.
- `document-rules` — Mandatory rules for generating any business document (proposal, invoice, estimate, report, presentation, contract, NDA, certificate of completion). This skill should be used at the start of every document generation request, before gathering data or running a script, to apply the first-use onboarding check, the dependency check, the data collection protocol, the output location policy, and the format defaults, and to reply in the user's language.
- `document-templates` — Document template structures and data collection checklists for each document type (proposal, invoice, estimate, report, presentation, contract, NDA, certificate of completion). This skill should be used when determining what data to collect from the user, what fields are required or optional, or how to structure a specific document type.
- `examples` — End-to-end document generation examples, workflow walkthroughs, and complete JSON input samples for all document types (proposal, invoice, estimate, report, presentation, contract, NDA, certificate of completion). This skill should be used when the user asks for a worked example, wants to see a sample document, needs a template pattern to follow, or asks how to create a specific document step by step.
- `formatting-standards` — Typography, font, margin, color, and layout standards for professional business documents. Use this skill when making any formatting decisions — choosing fonts, colors, margins, spacing, or layout patterns for any document type.
- `user-preferences` — First-use onboarding, user style preferences, company profiles, and logo management for document generation. This skill should be used on the first document generation request to collect user preferences, when the user wants to change their style, or when managing company logos and branding profiles.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents
- 10 command(s) — Devin plugins do not support commands

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/document-generator-ops
