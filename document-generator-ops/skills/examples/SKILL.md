---
name: examples
description: End-to-end document generation examples, workflow walkthroughs, and complete JSON input samples for all document types (proposal, invoice, estimate, report, presentation, contract, NDA, certificate of completion). This skill should be used when the user asks for a worked example, wants to see a sample document, needs a template pattern to follow, or asks how to create a specific document step by step.
---

# Examples & Reference Index

Links to detailed workflow scenarios and JSON input examples. For script details, see the **document-generator** skill. For field requirements, see the **document-templates** skill.

## Reference Files

### Workflow Scenarios (step-by-step)

| File | Document Type |
|------|--------------|
| [Proposal Workflow](references/scenarios/proposal-workflow.md) | Business proposal (DOCX) |
| [Invoice Workflow](references/scenarios/invoice-workflow.md) | Invoice (PDF) |
| [Report Workflow](references/scenarios/report-workflow.md) | Quarterly report (DOCX) |
| [Presentation Workflow](references/scenarios/presentation-workflow.md) | Product launch presentation (PPTX) |
| [Contract Workflow](references/scenarios/contract-workflow.md) | Service agreement (DOCX) |
| [Act Workflow](references/scenarios/act-workflow.md) | Act of completed works (PDF) |

### JSON Input Examples (minimal + full)

| File | Document Type |
|------|--------------|
| [Proposal Example](references/templates/proposal-example.md) | Proposal JSON (minimal + full with branding) |
| [Invoice Example](references/templates/invoice-example.md) | Invoice JSON (minimal + full + pdfkit variant) |
| [Report Example](references/templates/report-example.md) | Report JSON (minimal + full security audit) |
| [Presentation Example](references/templates/presentation-example.md) | Presentation JSON (minimal + full investor pitch) |
| [Contract Example](references/templates/contract-example.md) | Contract JSON (NDA + service agreement + employment) |
| [Act Example](references/templates/act-example.md) | Act JSON (minimal + full with VAT) |

## Quick Command Reference

| Command | Purpose | Default Format |
|---------|---------|----------------|
| `/document-generator-ops:generate-proposal` | Business proposals | DOCX |
| `/document-generator-ops:generate-invoice` | Invoices and bills | PDF |
| `/document-generator-ops:generate-estimate` | Cost estimates and quotations | PDF |
| `/document-generator-ops:generate-report` | Reports and analysis | DOCX |
| `/document-generator-ops:generate-presentation` | Slide presentations | PPTX |
| `/document-generator-ops:generate-contract` | Contracts and agreements | DOCX |
| `/document-generator-ops:generate-nda` | Non-disclosure agreements | PDF |
| `/document-generator-ops:generate-act` | Acts of completed works | PDF |
| `/document-generator-ops:convert-document` | Format conversion | varies |
| `/document-generator-ops:setup` | Style, company profile and logo preferences | — |

These commands are defined in the `commands/` directory and are invocable as slash commands by the user.

## Plugin root in the reference files

The scenario and template files below are read as plain files, so Claude Code does not substitute path variables in them. Wherever they write `<plugin_dir>`, use the plugin root: `${CLAUDE_PLUGIN_ROOT}`. Call scripts as `node "${CLAUDE_PLUGIN_ROOT}/scripts/<script>.js" /absolute/path/input.json`, without `cd` into the plugin.
