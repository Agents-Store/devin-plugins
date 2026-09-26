---
name: formatting-standards
description: Typography, font, margin, color, and layout standards for professional business documents. Use this skill when making any formatting decisions — choosing fonts, colors, margins, spacing, or layout patterns for any document type.
---

# Formatting Standards

Professional document design based on **corporate best practices** (McKinsey, Deloitte, PwC style).
Core principles: **clear typographic hierarchy**, **generous whitespace**, **restrained color use**, **information architecture over decoration**.

## Design Philosophy

Good business documents communicate structure through typography and space — not through colored boxes and decorative fills.

- **White space is not empty space** — generous margins and section gaps signal professionalism
- **Color has a job** — navy anchors headers and structure; accent blue highlights key values; everything else is black/gray/white
- **Hierarchy through scale and weight** — font size + weight differences should be obvious at a glance
- **Line-based separators over box-based containers** — a 1px rule is more elegant than a colored card with borders
- **Tables anchor numbers** — dark header rows with white text; light zebra striping only, no colored fills in data cells

## Font System

### Font Pairing

Fonts differ by output format — DOCX/PPTX use system fonts; PDF uses embedded Inter + Source Serif 4 (Cyrillic+Latin, offline).

#### DOCX / PPTX — System Fonts

| Context | Headings | Body Text |
|---------|----------|-----------|
| Proposals, Reports | **Georgia** (serif) | Arial (sans-serif) |
| Presentations | **Georgia** (serif) | Arial (sans-serif) |
| Contracts, Legal | **Georgia** (serif) | Georgia (serif) |

Georgia and Arial are pre-installed on macOS and Windows — no embedding needed.

#### PDF — Embedded Fonts (Inter + Source Serif 4)

Loaded from `scripts/fonts.js`. Works fully offline. Supports Ukrainian and English.

| Context | Headings | Body Text |
|---------|----------|-----------|
| Invoices | **Source Serif 4** | Inter |
| Contracts (PDF) | **Source Serif 4** | Source Serif 4 |
| Acts of completed works | **Source Serif 4** | Source Serif 4 + Inter (meta labels) |
| Reports, Proposals (PDF) | **Source Serif 4** | Inter |

Source Serif 4 was designed for Cyrillic+Latin — ideal for Ukrainian documents.

### Font Size Hierarchy

#### DOCX Documents (sizes in pt)

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| Document title | 32 | Bold | Primary (#1E3A5F) |
| Heading 1 | 18 | Bold | Primary (#1E3A5F) |
| Heading 2 | 14 | Bold | Primary (#1E3A5F) |
| Heading 3 | 12 | Bold | Text (#1E293B) |
| Body text | 11 | Regular | Text (#1E293B) |
| Meta/footer | 8–9 | Regular/Italic | Muted (#64748B) |
| Table header | 11 | Bold | White on Primary |
| Table body | 11 | Regular | Text (#1E293B) |

#### PDF Documents (sizes in px — CSS via Playwright)

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| INVOICE title | 26px | 700 | Primary |
| Company name | 20px | 700 | Primary |
| Bill-to name / grand total | 14–16px | 700 | Text / Primary |
| Section label (uppercase caps) | 9–10px | 700, uppercase, tracked | Muted |
| Body / table text | 12–13px | 400 | Text |
| Table header text | 10.5px | 600, uppercase | White |
| Notes / captions | 11px | 400 | Muted |

#### Presentations (sizes in pt)

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| Title slide heading | 40 | Bold | White |
| Slide header bar | 16 | Bold | White on Primary |
| Subtitle | 20–22 | Regular | Muted (#94A3B8) |
| Body/bullets | 16–18 | Regular | Text (#1E293B) |
| Agenda numbers | 24 | Bold | Accent (#2563EB) |
| Meta/author | 13 | Regular | Muted |

## Color System

### Primary Palette — Professional Corporate

| Role | Hex | Usage |
|------|-----|-------|
| **Primary** — Deep Navy | `#1E3A5F` | Table headers, document title, top/bottom bars, key amounts |
| **Accent** — Corporate Blue | `#2563EB` | H1 underlines, bullet markers, left-border accents in DOCX |
| **Text** — Dark Slate | `#1E293B` | Body text, names, amounts |
| **Muted** — Slate Gray | `#64748B` | Labels, captions, secondary info, footer |
| **Border** — Light | `#E2E8F0` | Table row borders, section dividers, separator lines |
| **Background** — Off-white | `#F8FAFC` | Alternating table rows only; keep page background pure white |

**Do not use** `#EFF6FF` (light blue) or other fill colors as section backgrounds in PDFs — they look like web UI widgets, not business documents. Use white + separator lines instead.

### Palette by Document Type

| Document Type | Primary | Accent | Notes |
|--------------|---------|--------|-------|
| Proposal, Report, Invoice, Presentation | `#1E3A5F` | `#2563EB` | Corporate Blue |
| Contract, Act | `#1E293B` | `#1E3A5F` | Dark Slate (more formal) |

### Color Application (60-30-10 Rule)

- **60%** White — page background, section backgrounds
- **30%** Navy — table headers, document top bar, headings, bold key values
- **10%** Blue accent — underlines, bullet colors, key amounts highlighted

## Layout & Spacing

### Spacing Grid (8px base)

Use multiples of 8px for all spacing: 8, 16, 24, 32, 48, 64px.

| Context (DOCX twips) | Before | After |
|----------------------|--------|-------|
| H1 heading | 480 twips | 60 twips + accent line |
| H2 heading | 320 twips | 120 twips |
| Body paragraph | — | 160 twips |
| Bullet item | — | 80 twips |
| Cover page title spacer | 3000 twips | — |

### Margins

| Type | Top | Bottom | Left | Right |
|------|-----|--------|------|-------|
| Proposals, Reports (DOCX) | 1" (1440) | 1" | 0.75" (1080) | 0.75" |
| Contracts (DOCX) | 1" | 1" | 1" | 1" |
| All PDFs | 28mm | 22mm | 18mm | 18mm |

PDF top/bottom are larger to accommodate Playwright's page header and footer (`displayHeaderFooter: true`).

### PDF Header/Footer (all PDFs)

| Zone | Content |
|------|---------|
| Header left | Company name (`data.companyInfo.name` → `data.company` → `data.contractor.name`) |
| Footer right | "Page N of M" |

Style: Inter 8px, muted (#64748B), 1px border line separator.

### Line Spacing

| Context | Value |
|---------|-------|
| Business docs (proposals, reports) | 1.3 |
| Legal docs (contracts, acts) | 1.5–1.7 |
| Presentations | 1.0 |

## Layout Patterns by Document Type

### Invoice Layout (PDF) — Professional Corporate

The goal is a clean financial document, not a web dashboard.

1. **5px primary top bar** — subtle anchor, not a heavy band
2. **Header row**: company name + details left; "INVOICE" (26px, Source Serif 4) + invoice number + issued/due dates right. Separated from content by a 1px border line.
3. **Bill To section**: plain text — field label (9px uppercase muted) above client name (14px bold) and address/email (12px muted). No colored background cards, no left-border accents.
4. **Amount Due** shown right-aligned in the same Bill To row (18px bold primary color).
5. **Items table**: navy header row (#1E3A5F) with white uppercase labels (10.5px). Alternating rows white / #F8FAFC. No inner vertical borders on rows.
6. **Totals section** — right-aligned, line-based:
   - Subtotal / Tax / Discount lines at 12.5px muted label + text value
   - `1.5px solid border-top` (full navy) divider line
   - "Total Due" at 13px bold + amount at 15px bold primary color
   - **No navy fill box**
7. **Payment Details**: plain section with `border-top: 1px solid #E2E8F0` separator. 2-column grid of label+value pairs. No colored background.
8. **4px primary bottom bar**

### Act Layout (PDF) — Ukrainian Legal Format

1. **Center header**: "ACT OF COMPLETED WORKS" (19px bold Source Serif 4, uppercase, 2px letter-spacing), act number below, date/city in muted Inter. The title is localized based on `data.language` (e.g., Ukrainian, German, etc.)
2. **2px solid bottom border** under header block
3. **Intro paragraph** (12px, line-height 1.8): party names bolded inline
4. **Services table**: primary header (#1E293B), numeric columns (Unit, Qty, Price, Total) with fixed widths for clean alignment, alternating rows. Column headers are localized.
5. **Totals** — right-aligned, line-based:
   - Subtotal / VAT rows at 12px muted (only shown when `vatRate > 0`)
   - `1.5px solid border-top` divider
   - "Total Due" + amount bold, primary color
6. **Confirmation box**: left border 3px accent + light gray background — acceptable here as a distinct callout block in a legal document
7. **Signature section**: uppercase section label (9px, tracked) with bottom border. Two-column CONTRACTOR / CUSTOMER blocks: party name bold + representative + reg. number. 36px margin before signature line, dashed seal line. Labels are localized based on `data.language`.

### Contract Layout (PDF) — Legal Document

1. **Centered title block**: document title in Source Serif 4 Bold (19px, uppercase, 0.08em tracking), contract number + date in muted Inter below; separated by `2.5px solid primary`
2. **Recital paragraph**: auto-generated from party names and roles, Source Serif 4 12.5px, justified
3. **Article bars**: full-width primary background with white uppercase Inter text (9.5px, 0.12em tracking) — professional dividers between clauses
4. **Party info**: two-column, clean text hierarchy — role label (8.5px uppercase muted) → company name (13px bold) → address/reg/representative (10px muted Inter)
5. **Clause paragraphs**: Source Serif 4 13px, line-height 1.45, justified with hyphenation; numbered sub-clauses use hanging indent (`padding-left: 2.2em; text-indent: -2.2em`)
6. **"IN WITNESS WHEREOF"** preamble (italic) before signatures
7. **Two-column signature block**: party label (8.5px uppercase) → party name (bold) → By / Name / Title / Date lines with 0.75px border

### Cover Pages (PDF — Full Page)

1. Full-page cover with `page-break-after: always` (content starts on page 2)
2. Top bar (5px primary color)
3. Company logo (if available, max 160x56px)
4. Type label (uppercase, accent color, 9px)
5. Title: Source Serif 4 32px Bold, primary color
6. Subtitle: Inter 16px, muted color
7. Meta block: "Prepared by", "Prepared for", date in small muted text
8. Bottom bar (3px primary color)

### Cover Pages (DOCX)

1. Company logo (if `companyInfo.logoBase64` is available, rendered as ImageRun 160x56px)
2. Large spacer (3000 twips if no logo, 600 twips if logo present — pushes title to visual center-upper area)
3. Accent line (6px blue) above title
4. Title in Georgia Bold, left-aligned, primary color
5. Subtitle in body font, muted color
6. Meta block: "Prepared by", "Prepared for", date in small muted text
7. Page break

### Presentation Slides

1. Master: navy header bar (0.75") + accent line (0.04")
2. Title slide: full navy background, accent stripe, left-aligned
3. Agenda: numbered items with accent numbers + dividers
4. Content: accent-colored bullets
5. Summary: two card boxes with top accent stripe

## Branding Customization

When the user provides branding:
1. **primaryColor** → replaces #1E3A5F in bars, headers, table headers, key amounts
2. **accentColor** → replaces #2563EB in underlines, bullets, left borders
3. **logo** → placed top-left in header section
4. **company name** → header and footer of every PDF page
5. **font override** → use in `fontHeading` / `fontBody` template fields

Default when no branding: Corporate Blue palette with Georgia (headings) + Arial (body) for DOCX; Source Serif 4 + Inter for PDF.

## Unified Design System (HTML-First)

Both PDF and DOCX outputs share the same design templates via `scripts/html_templates.js`. This module is the single source of truth for all document layouts:

- **PDF**: HTML rendered directly by Playwright
- **DOCX (pandoc engine)**: Same HTML converted to DOCX via pandoc with a reference template
- **DOCX (docx-js engine)**: Independent implementation matching the same design language (Georgia/Arial instead of Source Serif 4/Inter)

**Font mapping between formats:**

| PDF (embedded) | DOCX (system) | Purpose |
|---|---|---|
| Source Serif 4 | Georgia | Headings, legal body text |
| Inter | Arial | Body text, labels, UI elements |

This ensures documents look consistent regardless of output format.

## Anti-Patterns

These are the most common mistakes that make documents look unprofessional:

| Anti-pattern | Better approach |
|---|---|
| Colored fill boxes for info sections (blue/gray cards) | Plain text with a thin separator line |
| Navy fill on "Total Due" row | Bold text + 1.5px border-top rule |
| `border-left: 4px solid accent` on text cards | Reserve left-border accents for callout boxes only (confirmation text, warnings) |
| More than 3 colors in one document | Stick to primary + muted + accent — that's enough |
| Centered body text | Left-aligned always (except document title and act header) |
| Dense text with no paragraph breaks | Minimum 1.6 line-height; clear paragraph spacing |
| Mismatched font pairing (e.g., Arial headings + Arial body) | Always pair a serif heading with sans-serif body, or full serif for legal |
| Missing visual anchor (no top bar, no table headers, no section labels) | At minimum: top bar + dark table header + uppercase section labels |
