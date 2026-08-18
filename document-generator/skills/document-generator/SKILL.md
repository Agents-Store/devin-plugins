---
name: document-generator
description: Document generation process -- format selection, data collection, script invocation, and delivery. This skill should be used when generating any document (proposal, invoice, estimate, report, presentation, contract, NDA, certificate of completion), deciding which format or engine to use, or running generation scripts.
---

# Document Generator Process

Core process skill for generating professional business documents. Defines the end-to-end workflow from user request to delivered file.

## Generation Workflow

### Step 1: CLASSIFY

Determine the document type from the user's request:

| Keywords | Document Type | Default Format |
|----------|--------------|----------------|
| proposal, bid, offer, pitch | **proposal** | DOCX |
| invoice, bill, receipt | **invoice** | PDF |
| estimate, quotation, quote, pricing | **estimate** | PDF |
| report, analysis, findings, research | **report** | DOCX |
| presentation, slides, deck, pitch deck | **presentation** | PPTX |
| contract, agreement, MSA, terms | **contract** | DOCX |
| NDA, non-disclosure, confidentiality | **nda** | PDF |
| act, certificate of completion | **act** | PDF |
| convert, transform, export | **conversion** | varies |

### Step 1.5: CHECK USER PREFERENCES (MANDATORY)

**You MUST check preferences before any generation. Scripts will reject requests if preferences are missing.**

```bash
cat ~/.document-generator/preferences.json 2>/dev/null
```

- **File missing** → **STOP. Run the onboarding interview** (see **user-preferences** skill) before proceeding.
- **File exists** → load style preset, default company, language, and currency to pre-fill fields

### Step 2: GATHER

Collect required data from the user. Each document type has specific required and optional fields.

Refer to the **document-templates** skill for complete field checklists per document type. It defines exactly which fields are required, which are optional, and the expected format for each.

If user preferences are loaded, pre-fill company info, currency, and language from the stored profile. Only ask for fields that aren't already known.

### Step 3: SELECT FORMAT & ENGINE

| Type | Format | Engine | Script | Notes |
|------|--------|--------|--------|-------|
| Proposal | DOCX | docx-js | `generate_docx.js` | Default. Add `"engine": "pandoc"` for PDF-matching style |
| Proposal | DOCX | pandoc | `generate_docx.js` (engine: "pandoc") | Same HTML templates as PDF. Requires pandoc |
| Proposal (final) | PDF | playwright | `generate_pdf.js` | Full-page cover, TOC, sections |
| Invoice | PDF | playwright | `generate_pdf.js` | Always PDF |
| Report | DOCX | docx-js | `generate_docx.js` | Default. Add `"engine": "pandoc"` for PDF-matching style |
| Report (final) | PDF | playwright | `generate_pdf.js` | Full-page cover, TOC, sections |
| Presentation | PPTX | pptxgenjs | `generate_pptx.js` | Always PPTX |
| Contract | DOCX | docx-js | `generate_docx.js` | Default for editable contracts |
| Contract (final) | PDF | playwright | `generate_pdf.js` | Legal-grade formatting |
| Estimate | PDF | playwright | `generate_pdf.js` | Phase-based pricing, timeline |
| NDA | PDF | playwright | `generate_pdf.js` | Mutual or unilateral |
| Act / Certificate | PDF | playwright | `generate_pdf.js` | Multi-language support |

**Engine selection for DOCX:**
- `docx-js` (default): Always works, full feature support (images, complex tables, headers/footers)
- `pandoc`: Produces DOCX that visually matches PDF output (uses same HTML templates). Set `"engine": "pandoc"` in input JSON. Requires pandoc installed (`which pandoc`).

### Step 4: BUILD JSON Input

1. Read the template file from `<plugin_dir>/templates/{type}_template.json`
2. Merge user data into the template structure
3. Set `outputPath` to: `{cwd}/{type}_{sanitized_title}_{YYYY-MM-DD}.{ext}`
4. Write the complete JSON input to a temp file: `{cwd}/.doc_input.json`

**Input JSON structure:**
```json
{
  "type": "proposal|invoice|estimate|report|contract|nda|act",
  "engine": "playwright|pdfkit",
  "outputPath": "./proposal_acme_2026-03-17.docx",
  "template": { "...from template file..." },
  "data": { "...user provided data..." }
}
```

### Step 5: GENERATE

Run the appropriate script via Bash:
```bash
cd <plugin_dir> && node scripts/generate_docx.js /absolute/path/to/.doc_input.json
```

**Check dependencies first (use the centralized checker):**
```bash
cd <plugin_dir> && node scripts/check_deps.js
```
If `ready: false`, show what's missing and ask user permission to install.

**Script output** (JSON to stdout):
- Success: `{ "success": true, "outputPath": "/abs/path/to/file.docx", "size": 12345 }`
- Failure: `{ "success": false, "error": "description" }`

### Step 6: DELIVER

1. Parse the script's JSON output
2. Confirm the file exists and report its path and size
3. Offer follow-up actions: "Want me to convert this to PDF?" or "Want to make changes?"

## Format Conversion

For converting between formats, use the pandoc wrapper:
```bash
<plugin_dir>/scripts/convert.sh input.md output.pdf
```

Supported conversions: MD->PDF, MD->DOCX, MD->HTML, DOCX->PDF, DOCX->MD, HTML->PDF, HTML->DOCX, MD->PPTX

## Error Handling

| Error | Resolution |
|-------|-----------|
| `warning: ONBOARDING_NOT_DONE` | Document generated with defaults. Offer to run `/setup` for custom styling |
| Module not found (docx, playwright, etc.) | Run `cd <plugin_dir> && npm install` |
| pandoc not installed | `brew install pandoc` (macOS) or `apt install pandoc` (Linux) |
| No PDF engine for pandoc | `pip3 install weasyprint` (recommended) or `brew install wkhtmltopdf` |
| Playwright browser launch failed | Add `--no-sandbox` flag (already in script) |
| Output file not created | Check script stderr, verify output directory exists |
| Margin format mismatch | Scripts auto-normalize (twips ↔ CSS units) via `utils.js` |

## File Naming Convention

Pattern: `{type}_{title}_{date}.{ext}`

Sanitize title: lowercase, replace spaces with underscores, remove special characters, max 50 chars.

Examples:
- `proposal_acme_consulting_2026-03-17.docx`
- `invoice_inv-001_2026-03-17.pdf`
- `report_q1_analysis_2026-03-17.docx`
- `presentation_product_launch_2026-03-17.pptx`
- `contract_service_agreement_2026-03-17.docx`
- `act_akt-001_2026-03-17.pdf`
