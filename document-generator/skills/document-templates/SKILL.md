---
name: document-templates
description: Document template structures and data collection checklists for each document type (proposal, invoice, estimate, report, presentation, contract, NDA, certificate of completion). This skill should be used when determining what data to collect from the user, what fields are required or optional, or how to structure a specific document type.
---

# Document Templates

Reference for document structures, required fields, and content guidelines for each document type.

## Proposal

**Structure:** Cover -> Executive Summary -> Problem -> Solution -> Scope -> Timeline -> Pricing -> Terms -> About Us -> Contact

### Required Fields

| Field | Description | Example |
|-------|------------|---------|
| title | Proposal title | "Cloud Migration Proposal" |
| recipient | Client name/company | "Acme Corporation" |
| author | Your name/company | "TechCo Solutions" |
| date | Proposal date | "2026-03-17" |
| sections.executive_summary | Brief overview | 2-3 paragraphs |
| sections.problem_statement | Client's challenge | What problem are we solving? |
| sections.proposed_solution | Your solution | How do we solve it? |
| sections.timeline | Milestones with dates | Phase 1: Week 1-2, Phase 2: Week 3-4 |
| sections.pricing | Cost breakdown | Table with items and costs |

### Optional Fields

| Field | Description |
|-------|------------|
| subtitle | Secondary title |
| companyName | For footer branding |
| branding.primaryColor | Hex color |
| branding.logoPath | Path to logo file |
| sections.approach | Methodology description |
| sections.terms | Terms and conditions |
| sections.about_us | Company background |

---

## Invoice

**Structure:** Header (logo, company) -> Client Info -> Line Items Table -> Subtotal/Tax/Total -> Payment Details -> Notes

### Required Fields

| Field | Description | Example |
|-------|------------|---------|
| invoiceNumber | Unique identifier | "INV-2026-001" |
| date | Invoice date | "2026-03-17" |
| dueDate | Payment due date | "2026-04-17" |
| companyInfo.name | Your company name | "TechCo Solutions" |
| companyInfo.address | Your address | "123 Main St, City" |
| recipient.name | Client name | "Acme Corporation" |
| items[] | Line items array | See below |
| items[].description | Item description | "Web Development" |
| items[].quantity | Quantity | 10 |
| items[].unitPrice | Price per unit | 150 |

### Optional Fields

| Field | Description |
|-------|------------|
| companyInfo.email | Company email |
| companyInfo.phone | Company phone |
| companyInfo.logo | Logo URL or path |
| recipient.address | Client address |
| recipient.email | Client email |
| tax | Tax amount |
| discount | Discount amount |
| paymentDetails.bank | Bank name |
| paymentDetails.iban | IBAN number |
| paymentDetails.swift | SWIFT code |
| notes | Additional notes |
| currencySymbol | Currency symbol (default: $) |

### Line Item Calculation

```
item.total = item.quantity * item.unitPrice
subtotal = sum of all item.total
total = subtotal + tax - discount
```

---

## Report

**Structure:** Cover -> TOC -> Introduction -> Background -> Methodology -> Findings -> Analysis -> Conclusions -> Recommendations -> Appendices -> References

### Required Fields

| Field | Description | Example |
|-------|------------|---------|
| title | Report title | "Q1 2026 Performance Analysis" |
| author | Author name | "Data Analytics Team" |
| date | Report date | "2026-03-17" |
| sections.introduction | Context and purpose | Why was this report created? |
| sections.findings | Key findings | Data and observations |
| sections.conclusions | Summary conclusions | What does the data tell us? |

### Optional Fields

| Field | Description |
|-------|------------|
| subtitle | Secondary title |
| sections.background | Background context |
| sections.methodology | How data was collected |
| sections.analysis | Detailed analysis |
| sections.recommendations | Action items |
| sections.appendices | Supporting materials |
| sections.references | Sources cited |
| headerText | Custom header text |

---

## Presentation

**Structure:** Title Slide -> Agenda -> Content Slides -> Summary -> Contact

### Required Fields

| Field | Description | Example |
|-------|------------|---------|
| title | Presentation title | "Product Launch Strategy" |
| slides[] | Array of slide objects | See slide types below |

### Slide Types

**Title slide:**
```json
{ "type": "title", "title": "Main Title", "subtitle": "Subtitle", "date": "2026-03-17" }
```

**Agenda slide:**
```json
{ "type": "agenda", "title": "Agenda", "items": ["Topic 1", "Topic 2", "Topic 3"] }
```

**Content slide:**
```json
{ "type": "content", "title": "Slide Title", "bullets": ["Point 1", "Point 2"], "image": "path/to/img.png" }
```

**Two-column slide:**
```json
{ "type": "two-column", "title": "Comparison", "leftColumn": ["Left 1", "Left 2"], "rightColumn": ["Right 1", "Right 2"] }
```

**Chart slide:**
```json
{ "type": "chart", "title": "Revenue", "chartType": "bar", "chartData": [{"name": "Q1", "labels": ["Jan","Feb","Mar"], "values": [100,200,300]}] }
```

**Summary slide:**
```json
{ "type": "summary", "title": "Summary", "keyPoints": ["Point 1"], "nextSteps": ["Step 1"] }
```

**Contact slide:**
```json
{ "type": "contact", "name": "John Doe", "email": "john@example.com", "phone": "+1-555-0123" }
```

### Optional Fields

| Field | Description |
|-------|------------|
| author | Presenter name |
| subtitle | Presentation subtitle |
| branding.primaryColor | Theme color |
| branding.secondaryColor | Accent color |
| branding.fontFamily | Font family |

---

## Contract

**Structure:** Header -> Parties -> Clauses (numbered) -> Signature Blocks

### Required Fields

| Field | Description | Example |
|-------|------------|---------|
| title | Contract title | "Service Agreement" |
| date | Agreement date | "2026-03-17" |
| parties.party1.name | First party name | "TechCo Solutions LLC" |
| parties.party2.name | Second party name | "Acme Corporation" |
| clauses[] | Array of clauses | See below |

### Standard Clauses

| ID | Title | Required |
|----|-------|----------|
| definitions | Definitions | Yes |
| scope | Scope of Services | Yes |
| deliverables | Deliverables | No |
| payment | Payment Terms | Yes |
| duration | Duration and Termination | Yes |
| confidentiality | Confidentiality | Yes |
| ip | Intellectual Property | No |
| liability | Limitation of Liability | No |
| force_majeure | Force Majeure | No |
| governing_law | Governing Law | Yes |
| dispute_resolution | Dispute Resolution | No |
| general | General Provisions | No |

### Clause Format
```json
{
  "id": "scope",
  "title": "Scope of Services",
  "content": "Paragraph 1 describing the scope.\n\nParagraph 2 with additional details."
}
```

Each paragraph within `content` (separated by `\n\n`) gets auto-numbered as sub-clauses (e.g., 2.1, 2.2).

### Optional Fields

| Field | Description |
|-------|------------|
| contractNumber | Reference number |
| parties.*.address | Party address |
| parties.*.registrationNumber | Registration/tax ID |
| parties.*.label | Custom party label |

---

## Certificate of Completion (Act)

**Structure:** Header (title, number, date, city) → Intro paragraph → Services table → Totals → Confirmation → Signature blocks

**Format:** PDF (default). Supports any language for all data values (company names, service descriptions, labels).

### Required Fields

| Field | Description | Example |
|-------|------------|---------|
| contractor.name | Contractor (service provider) | "Acme Consulting LLC" |
| contractor.representative | Signatory name | "John Smith" |
| customer.name | Customer (client) | "Global Corp Inc." |
| customer.representative | Signatory name | "Jane Doe" |
| services[] | Array of service rows | See below |
| services[].description | Service or work description | "Web development" |
| services[].quantity | Quantity | 40 |
| services[].unitPrice | Price per unit | 1500 |
| date | Document date | "March 19, 2026" |

### Optional Fields

| Field | Description |
|-------|------------|
| actNumber | Act reference number (e.g., "ACT-001") |
| city | City name (e.g., "Kyiv") |
| contractRef | Reference to contract (e.g., "Contract No. 001 dated 01.01.2026") |
| services[].unit | Unit of measure (hrs/pcs/service) |
| services[].total | Row total (auto-calculated if omitted: qty × unitPrice) |
| vatRate | VAT rate in percent (0 if not VAT payer) |
| totalAmount | Document total (auto-calculated if omitted) |
| currencySymbol | Currency symbol (default: $) |
| contractor.title | Legal role (e.g., "Director", "CEO") |
| contractor.reg | Registration number (company ID / tax ID) |
| customer.title | Legal role (e.g., "Director", "CEO") |
| customer.reg | Registration number (company ID / tax ID) |
| notes | Additional notes |

### Calculation

```
services[].total = services[].quantity × services[].unitPrice
totalAmount = sum of all services[].total
vatAmount = totalAmount × (vatRate / 100)
grandTotal = totalAmount + vatAmount
```

---

---

## NDA (Non-Disclosure Agreement)

**Structure:** Header (title, NDA number, date, city) -> Recital (WHEREAS + NOW THEREFORE) -> Clauses -> Witness clause -> Signature blocks

**Format:** PDF. Supports mutual (both parties bound) or unilateral (one-way) NDA.

### Required Fields

| Field | Description | Example |
|-------|------------|---------|
| date | Agreement date | "April 7, 2026" |
| disclosingParty.name | First party name | "TechCo Solutions LLC" |
| disclosingParty.representative | Signatory name | "Alex Morgan" |
| receivingParty.name | Second party name | "Acme Corporation" |
| receivingParty.representative | Signatory name | "Sarah Chen" |

### Optional Fields

| Field | Description | Default |
|-------|------------|---------|
| title | Document title | "Non-Disclosure Agreement" |
| number | NDA reference number | — |
| city | City of execution | — |
| ndaType | "mutual" or "unilateral" | "mutual" |
| jurisdiction | Governing law jurisdiction | "the State of Delaware" |
| termYears | NDA effective period | "two (2)" |
| survivalYears | Post-termination obligation period | "three (3)" |
| disclosingParty.address | Address | — |
| disclosingParty.title | Legal title | — |
| disclosingParty.reg | Registration number | — |
| receivingParty.address | Address | — |
| receivingParty.title | Legal title | — |
| receivingParty.reg | Registration number | — |

**Note:** All 7 standard clauses (Confidential Info Definition, Obligations, Exclusions, Term, Return of Materials, Remedies, Governing Law) have professional defaults built in. Only override if the user requests specific wording.

---

## Estimate / Quotation

**Structure:** Header -> Client block -> Summary stats -> Executive summary -> Scope (inclusions/exclusions/assumptions) -> Team -> Phase-based pricing -> Optional items -> Totals -> Timeline (Gantt) -> Payment schedule -> Validity -> Terms -> Acceptance/Signatures

**Format:** PDF. Always use detailed phase-based format.

### Required Fields

| Field | Description | Example |
|-------|------------|---------|
| estimateNumber | Reference number | "EST-2026-019" |
| date | Estimate date | "April 7, 2026" |
| companyInfo.name | Your company | "Stackmakers Studio" |
| recipient.name | Client company | "Acme Corporation" |
| executiveSummary | 2-4 sentence overview | "This estimate covers..." |
| scope.description | What the project is | "End-to-end redesign..." |
| scope.inclusions[] | What IS included | ["Frontend dev", "Testing", ...] |
| scope.exclusions[] | What is NOT included | ["Hosting", "Content", ...] |
| scope.assumptions[] | Conditions/prerequisites | ["Client provides API docs by Week 1", ...] |
| team[] | Team members | See below |
| team[].role | Role name | "Senior Developer" |
| team[].rate | Hourly rate | 175 |
| phases[] | Project phases | See below |
| phases[].name | Phase name | "Phase 1: Discovery" |
| phases[].tasks[] | Tasks in phase | See below |
| phases[].tasks[].description | Task description | "Requirements gathering" |
| phases[].tasks[].role | Who does it | "Project Manager" |
| phases[].tasks[].hours | Estimated hours | 16 |
| phases[].tasks[].rate | Hourly rate | 120 |
| timeline | Project timeline | See below |
| timeline.totalDuration | Total duration | "14 weeks" |
| timeline.phases[] | Timeline phases | Start/end weeks + milestones |

### Optional Fields

| Field | Description | Default |
|-------|------------|---------|
| validDays | Validity period | 30 |
| recipient.contactPerson | Contact person name | — |
| team[].allocation | % allocation | — |
| phases[].color | Phase accent color | Auto-assigned |
| optionalItems[] | Add-on items (separate from total) | — |
| contingency.percent | Risk buffer % | — |
| contingency.label | Buffer description | "Risk contingency" |
| paymentSchedule[] | Payment milestones with % | — |
| terms[] | Terms & conditions | — |
| acceptance.enabled | Show signature block | true |
| discount | Discount amount | 0 |
| tax | Tax amount | 0 |
| notes | Additional notes | — |

---

## Template File Locations

All templates are in `<plugin_dir>/templates/`:

| File | Document Type |
|------|--------------|
| `proposal_template.json` | Proposals |
| `invoice_template.json` | Invoices |
| `estimate_template.json` | Estimates / Quotations |
| `report_template.json` | Reports |
| `presentation_template.json` | Presentations |
| `contract_template.json` | Contracts |
| `nda_template.json` | Non-Disclosure Agreements |
| `act_template.json` | Certificates of Completion (Acts) |

Read the template file to get default structure and styling, then merge with user-provided data.
