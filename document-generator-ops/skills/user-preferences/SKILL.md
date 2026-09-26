---
name: user-preferences
description: First-use onboarding, user style preferences, company profiles, and logo management for document generation. This skill should be used on the first document generation request to collect user preferences, when the user wants to change their style, or when managing company logos and branding profiles.
---

# User Preferences & Onboarding

Manages persistent user preferences for document generation — style, branding, company profiles, and logos. Ensures consistent, personalized output across all sessions.

## First-Use Onboarding

### When to Trigger

Before generating the **first document ever**, check if a preferences file exists:

```bash
cat ~/.document-generator/preferences.json 2>/dev/null
```

- **File exists and is valid JSON** → skip onboarding, use stored preferences
- **File missing or invalid** → run onboarding interview below

### Onboarding Interview

Ask the user these questions conversationally (not as a rigid form). Adapt based on their answers — skip irrelevant questions.

**1. Document Style**

> "Before we generate your first document, I'd like to learn your preferences so all future documents match your style. What kind of look do you prefer?"
>
> Options to suggest:
> - **Corporate Classic** — navy/blue palette, serif headings (Georgia), clean and traditional
> - **Modern Minimal** — dark slate, generous whitespace, sans-serif throughout (Inter/Arial)
> - **Bold & Vibrant** — custom accent colors, strong visual hierarchy, modern feel
> - **Custom** — user provides their own colors and fonts

**2. Default Language**

> "What language should documents default to? (You can always override per document.)"
>
> Common: English, Ukrainian, German, French, Spanish, etc.

**3. Company Information (optional)**

> "Would you like to set up a default company profile? This saves time on invoices, contracts, and proposals."
>
> If yes, collect:
> - Company name
> - Address
> - Phone, email, website
> - Registration/tax ID
> - Logo (see Logo Management below)

**4. Formatting Preferences (optional)**

> "Any specific formatting preferences?"
>
> - Paper size: A4 (default) or Letter
> - Currency symbol: $, EUR, GBP, EUR, etc.
> - Date format: "March 19, 2026" / "19.03.2026" / "2026-03-19"

### Save Preferences

After collecting answers, create the preferences directory and file:

```bash
mkdir -p ~/.document-generator/logos
```

Write `~/.document-generator/preferences.json`:

```json
{
  "version": 1,
  "createdAt": "2026-03-19T10:30:00Z",
  "updatedAt": "2026-03-19T10:30:00Z",
  "style": {
    "preset": "corporate-classic",
    "primaryColor": "#1E3A5F",
    "accentColor": "#2563EB",
    "textColor": "#1E293B",
    "mutedColor": "#64748B",
    "borderColor": "#E2E8F0",
    "backgroundColor": "#F8FAFC",
    "fontHeading": "Georgia",
    "fontBody": "Arial",
    "lineSpacing": 1.3
  },
  "defaults": {
    "language": "en",
    "paperSize": "A4",
    "currencySymbol": "$",
    "dateFormat": "long"
  },
  "companies": {
    "default": {
      "name": "Acme Corp",
      "address": "123 Main St, City, Country",
      "phone": "+1 555-0100",
      "email": "billing@acme.com",
      "website": "acme.com",
      "reg": "12345678",
      "logoFile": "acme-logo.png"
    }
  }
}
```

## Style Presets

### Corporate Classic (default)
```json
{
  "preset": "corporate-classic",
  "primaryColor": "#1E3A5F",
  "accentColor": "#2563EB",
  "textColor": "#1E293B",
  "mutedColor": "#64748B",
  "borderColor": "#E2E8F0",
  "backgroundColor": "#F8FAFC",
  "fontHeading": "Georgia",
  "fontBody": "Arial",
  "lineSpacing": 1.3
}
```

### Modern Minimal
```json
{
  "preset": "modern-minimal",
  "primaryColor": "#111827",
  "accentColor": "#6366F1",
  "textColor": "#1F2937",
  "mutedColor": "#9CA3AF",
  "borderColor": "#E5E7EB",
  "backgroundColor": "#F9FAFB",
  "fontHeading": "Inter",
  "fontBody": "Inter",
  "lineSpacing": 1.4
}
```

### Bold & Vibrant
```json
{
  "preset": "bold-vibrant",
  "primaryColor": "#0F172A",
  "accentColor": "#F59E0B",
  "textColor": "#1E293B",
  "mutedColor": "#64748B",
  "borderColor": "#E2E8F0",
  "backgroundColor": "#FFFBEB",
  "fontHeading": "Georgia",
  "fontBody": "Arial",
  "lineSpacing": 1.3
}
```

### Consulting Professional (McKinsey/Deloitte inspired)
```json
{
  "preset": "consulting-professional",
  "primaryColor": "#051C2C",
  "accentColor": "#2251FF",
  "textColor": "#1A202C",
  "mutedColor": "#718096",
  "borderColor": "#E2E8F0",
  "backgroundColor": "#F7FAFC",
  "fontHeading": "Georgia",
  "fontBody": "Arial",
  "lineSpacing": 1.35
}
```

### Legal Formal
```json
{
  "preset": "legal-formal",
  "primaryColor": "#1A202C",
  "accentColor": "#2D3748",
  "textColor": "#1A202C",
  "mutedColor": "#718096",
  "borderColor": "#CBD5E0",
  "backgroundColor": "#FFFFFF",
  "fontHeading": "Georgia",
  "fontBody": "Georgia",
  "lineSpacing": 1.6
}
```

## Loading Preferences at Generation Time

When generating any document:

1. Read `~/.document-generator/preferences.json`
2. Merge stored style into template styling (preferences = defaults, template overrides, user overrides win last)
3. If a company profile exists and matches the context, pre-fill company info fields
4. Apply date format and currency from defaults

**Merge priority** (lowest to highest):
1. Template defaults (from `templates/*.json`)
2. User preferences (from `preferences.json`)
3. Explicit user input for this document (always wins)

## Logo Management

### Collecting a Logo

When a user wants to add a company logo:

1. Ask for the logo file path:
   > "Please provide the path to your company logo (PNG or JPEG with transparent background recommended)."

2. Validate the file:
   ```bash
   file <logo_path>  # Verify it's an image
   ```

3. Copy to persistent storage and convert to base64:
   ```bash
   cp <logo_path> ~/.document-generator/logos/<company_key>-logo.png
   base64 -i ~/.document-generator/logos/<company_key>-logo.png | tr -d '\n' > ~/.document-generator/logos/<company_key>-logo.b64
   ```

4. Update preferences.json — set `logoFile` in the company profile:
   ```json
   "companies": {
     "acme": {
       "name": "Acme Corp",
       "logoFile": "acme-logo.png"
     }
   }
   ```

### Using a Logo in Documents

When generating a document for a known company:

1. Check if `logoFile` exists in the company profile
2. Read the base64 file:
   ```bash
   cat ~/.document-generator/logos/<company_key>-logo.b64
   ```
3. Inject into the document JSON as `data.companyInfo.logoBase64`

### Multiple Company Profiles

Users can store multiple company profiles (e.g., different legal entities):

```json
{
  "companies": {
    "default": {
      "name": "Acme Corp",
      "logoFile": "acme-logo.png"
    },
    "acme-europe": {
      "name": "Acme Europe GmbH",
      "address": "Hauptstr. 10, 10115 Berlin, Germany",
      "reg": "HRB 123456",
      "logoFile": "acme-europe-logo.png",
      "currencySymbol": "EUR",
      "language": "de"
    },
    "acme-ua": {
      "name": "Acme Europe Ltd",
      "address": "45 Berlin Strasse, Munich, Germany",
      "reg": "EDRPOU: 12345678",
      "logoFile": "acme-ua-logo.png",
      "currencySymbol": "EUR",
      "language": "de"
    }
  }
}
```

## Company Selection Logic

### Decision Tree

```
How many companies are stored?
│
├── 0 companies (first use / no profiles) →
│   Ask: "What company should I use for this document?"
│   Collect: name, address, reg, etc.
│   After generation, offer to save for future use.
│
├── 1 company →
│   Use it automatically. Do not ask.
│
└── 2+ companies →
    Always ask which one to use. Show a numbered list:
    "You have several company profiles saved:
     1. Acme Corp
     2. Acme Europe GmbH
     3. Acme Europe Ltd
     Which one should I use for this document?"
```

### Adding a New Company

When the user provides company info that does NOT match any stored profile:

1. Use the provided data for the current document
2. After generation, offer to save:
   > "I noticed this is a new company (TechFlow LLC). Want me to save it as a company profile for future documents?"
3. If yes → generate a key from the name (e.g., "techflow-llc"), save to `companies`, optionally ask for logo
4. If no → use it for this document only, do not persist

## Updating Preferences

Users can update preferences at any time:

- **"Change my document style"** → show preset options, update `style` section
- **"Update my company info"** → re-collect company fields
- **"Add a new company profile"** → create new entry in `companies`
- **"Change my logo"** → replace logo file and base64
- **"Switch to dark/legal/minimal style"** → apply corresponding preset
- **"Reset preferences"** → delete `~/.document-generator/preferences.json`

After any update, set `updatedAt` to current timestamp.

## Date Format Options

| Format Key | Example | Usage |
|-----------|---------|-------|
| `long` | March 19, 2026 | English formal |
| `short` | Mar 19, 2026 | English compact |
| `iso` | 2026-03-19 | Universal / technical |
| `eu` | 19.03.2026 | European standard |
| `uk-ua` | 19.03.2026 | Ukrainian formal (day.month.year) |

The agent should format dates according to the stored preference, unless the user specifies otherwise.
