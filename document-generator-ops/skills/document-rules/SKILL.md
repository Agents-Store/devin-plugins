---
name: document-rules
description: Mandatory rules for generating any business document (proposal, invoice, estimate, report, presentation, contract, NDA, certificate of completion). This skill should be used at the start of every document generation request, before gathering data or running a script, to apply the first-use onboarding check, the dependency check, the data collection protocol, the output location policy, and the format defaults, and to reply in the user's language.
---

# Document Rules

These rules apply to every document you generate with this plugin's Node.js scripts.

## Communication Language

**Always respond to the user in the same language they use to address you.** If the user writes in Ukrainian — respond in Ukrainian. If in English — respond in English. If they switch languages mid-conversation, switch with them.

This is completely independent from the document language. The document language (for generated content, labels, headers) is a separate setting stored in preferences or specified per document. Never assume that the conversation language equals the document language — always ask which language the document should be in.

---

## MANDATORY: First-Use Onboarding

**You MUST run this check before EVERY document generation request. This is a hard requirement — the generation scripts will reject requests if preferences are missing.**

```bash
cat ~/.document-generator/preferences.json 2>/dev/null
```

**If the file is missing or invalid:**
1. **STOP immediately.** Do NOT gather data or attempt generation.
2. Run the onboarding interview (see **user-preferences** skill):
   - Ask about preferred document style (Corporate Classic, Modern Minimal, Bold & Vibrant, Consulting Professional, Legal Formal)
   - Ask about default language and currency
   - Ask if they want to add company profile and logo
3. Save preferences to `~/.document-generator/preferences.json`
4. Only then continue with the user's original request.

**If the file exists and contains valid JSON:** load it silently and use stored values as defaults. Do NOT re-run onboarding.

**Why this matters:** All generation scripts auto-load preferences and merge them into the document styling. If preferences are missing, the scripts will still generate the document using built-in defaults, but the JSON output will contain a `warning` field with `ONBOARDING_NOT_DONE`. When you see this warning, offer to run onboarding after delivering the document.

---

## MANDATORY: Dependency Check

Before the first generation in a session, run the dependency checker:
```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/check_deps.js"
```

This outputs JSON with `ready`, `missing`, and `installCommands` fields.

**If not ready:**
1. Show the user what's missing
2. Ask permission to run the `installCommands` it lists (`npm ci` for node modules, `npx playwright install chromium` for the browser, platform-specific commands for system tools)
3. Install if approved
4. Verify by re-running the check

A marketplace install already ships the npm modules (Claude Code installs them from `package-lock.json`); they are missing only when the plugin is loaded in place (`--plugin-dir`). The Playwright browser is the usual one-time step.

**Key rule:** Never re-ask about dependencies that are already installed. Check once per session, silently proceed if everything is in place.

---

## User Preferences — Loading & Merging

When generating any document:
1. Read `~/.document-generator/preferences.json`
2. Apply style preset (colors, fonts) as template defaults
3. Pre-fill company info from stored profile if relevant
4. Apply date format and currency from preferences

**Merge priority** (lowest to highest):
1. Template defaults (from `templates/*.json`)
2. User preferences (from `preferences.json`)
3. Explicit user input for this document (always wins)

## Company Logo

If a company profile has a `logoFile` set:
1. Read base64: `cat ~/.document-generator/logos/<company_key>-logo.b64`
2. Inject as `data.companyInfo.logoBase64` in the input JSON
3. The logo appears in: PDF (all types), DOCX (cover page), PPTX (title slide)

To collect a new logo:
1. Ask the user for the file path
2. Validate it's an image: `file <path>`
3. Copy to `~/.document-generator/logos/` and generate base64
4. Update `preferences.json` with the `logoFile` reference

## Multi-Language Support

Documents support any language through the `language` field:
- `en` (default), `ua`, `de`, `fr`, `es`
- For act documents: controls all localized labels (title, table headers, confirmation, signatures)
- For other documents: the user provides content in their desired language
- Default language comes from user preferences

## Script Execution

- Scripts are located at: `${CLAUDE_PLUGIN_ROOT}/scripts/` (Claude Code substitutes the installed plugin path; do not search for it)
- Always use absolute paths when calling scripts, and do not `cd` into the plugin directory: a relative `outputPath` resolves against the working directory
- Pass input as a JSON file path argument (not stdin) to avoid shell escaping issues
- Check script exit code; if non-zero, read stderr for error details
- Scripts output JSON to stdout: `{ "success": true, "outputPath": "..." }` or `{ "success": false, "error": "..." }`
- If output has `warning: "ONBOARDING_NOT_DONE"`, offer to run `/document-generator-ops:setup` after delivering the document

## Engine Selection (DOCX)

Two engines available for DOCX generation:
- `docx-js` (default) — always works, no extra dependencies
- `pandoc` — converts the same HTML templates to DOCX. Pandoc ignores CSS, so only the structure (headings, lists, tables) matches the PDF; the look (fonts, colours, spacing) comes from `assets/reference.docx`. Requires pandoc.

Check pandoc availability with `which pandoc`. Do not promise that a pandoc DOCX looks like the PDF; for a DOCX in the plugin's own styling use `docx-js`.

## Output Location

- **Always ask the user where to save the document** before generating
- If the user specifies a folder that doesn't exist, ask if you should create it, then create it
- If the user says "here" or "current folder", use the current working directory
- Never overwrite existing files without confirmation
- Naming pattern: `{type}_{sanitized_title}_{YYYY-MM-DD}.{ext}`
- After generation, confirm the output file path and its size

## MANDATORY: Data Collection Protocol

**You MUST collect all required data BEFORE generating any document. NEVER generate a document with missing required fields or placeholder content.**

### Step-by-step process:

1. **Identify document type** from user request
2. **Load required fields** checklist from the **document-templates** skill for that type
3. **Pre-fill** from stored preferences and company profiles (companyInfo, currency, language)
4. **Check what's missing** — compare required fields against what the user provided and what was pre-filled
5. **Ask the user for ALL missing required fields** in a single, organized message:
   - Group by section (e.g., "Company Info", "Client Info", "Line Items")
   - Mark which fields are required vs optional
   - Show what was pre-filled from preferences so the user can confirm or override
6. **Wait for the user's response** — do NOT proceed until you have all required data
7. **If the user's response is still incomplete**, ask again for the specific missing fields
8. **Show a summary** of all collected data before generating — let the user confirm or correct
9. **Only then** build the JSON input and run the generation script

### What counts as "required" per document type:

**Invoice:** invoiceNumber, date, dueDate, companyInfo.name, recipient.name, at least 1 line item (description + quantity + unitPrice)

**Estimate:** estimateNumber, date, companyInfo.name, recipient.name, executiveSummary, scope (description + inclusions + exclusions), team (at least 1 member), phases (at least 1 phase with tasks), timeline

**Contract:** title, date, both parties (name + role), at least 3 clauses (scope, payment, governing law)

**NDA:** date, both parties (name + representative), jurisdiction

**Proposal:** title, author, recipient, date, at least 2 sections (executive_summary + proposed_solution)

**Report:** title, author, date, at least 2 sections (introduction + findings)

**Certificate of Completion (Act):** contractor (name + representative), customer (name + representative), date, at least 1 service item

**Presentation:** title, at least 2 slides

### Key rules:
- Pre-fill company info from preferences — don't re-ask if already stored
- NEVER invent or guess content — all text must come from the user
- NEVER use generic placeholders like "Lorem ipsum" or "Your company name here"
- For optional fields, offer sensible defaults but let the user decide
- If the user says "skip" or "default" for optional fields, use reasonable defaults
- If the user provides partial data (e.g., just a topic), ask for the rest before generating

## Format Defaults

- Proposal: DOCX (editable) or PDF (final)
- Invoice: PDF always
- Estimate: PDF always
- Report: DOCX (draft) or PDF (final)
- Presentation: PPTX always
- Contract: DOCX (default, editable/signable) or PDF (final/distribution)
- NDA: PDF always
- Certificate of Completion (Act): PDF always
