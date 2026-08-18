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
| `/generate-proposal` | Business proposals | DOCX |
| `/generate-invoice` | Invoices and bills | PDF |
| `/generate-report` | Reports and analysis | DOCX |
| `/generate-presentation` | Slide presentations | PPTX |
| `/generate-contract` | Contracts and agreements | DOCX |
| `/generate-act` | Acts of completed works | PDF |
| `/convert-document` | Format conversion | varies |

These commands are defined in the `commands/` directory and are invocable as slash commands by the user.
