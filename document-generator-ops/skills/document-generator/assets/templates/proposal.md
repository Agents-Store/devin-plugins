# Proposal Template (DOCX / PDF)

Commercial proposal / business proposal template. Title page, executive summary, service sections, pricing, and closing.

## Required fields

```
title: "Commercial Proposal"
subtitle: "Web Development Services"   # optional
author: "Your Name or Company"
date: "2026-03-19"
recipient: "Client Name"               # optional — shown in subtitle area

sections:
  - level: 1
    heading: "Executive Summary"
    content: "Brief overview of the proposal..."
  - level: 1
    heading: "Proposed Services"
    bullets:
      - "Service item 1"
      - "Service item 2"
  - level: 1
    heading: "Investment"
    content: "Total project investment: $15,000..."
```

## Optional fields

```
company: "Your Company"
logoBase64: "<base64>"   # company logo
```

## JSON input structure (DOCX)

```json
{
  "type": "proposal",
  "engine": "docx",
  "outputPath": "./proposal_acme_2026-03-19.docx",
  "template": {
    "styling": {
      "primaryColor": "#1E3A5F",
      "accentColor": "#2563EB",
      "fontHeading": "Georgia",
      "fontFamily": "Arial"
    }
  },
  "data": {
    "title": "Web Development Proposal",
    "subtitle": "Custom E-Commerce Platform",
    "author": "Acme Digital Agency",
    "date": "March 19, 2026",
    "recipient": "Global Client Corp.",
    "sections": [
      {
        "level": 1,
        "heading": "Executive Summary",
        "content": "We are pleased to present this proposal for a custom e-commerce platform that will help you reach new markets and streamline your online sales process."
      },
      {
        "level": 1,
        "heading": "Our Approach",
        "bullets": [
          "Discovery & Requirements (1 week)",
          "UI/UX Design (2 weeks)",
          "Development (6 weeks)",
          "Testing & QA (1 week)",
          "Deployment & Launch (1 week)"
        ]
      },
      {
        "level": 1,
        "heading": "Investment",
        "content": "Total project investment: $25,000 USD. Payment schedule: 50% upfront, 50% on delivery."
      },
      {
        "level": 1,
        "heading": "Why Choose Us",
        "bullets": [
          "5+ years of e-commerce experience",
          "50+ successful projects delivered",
          "Dedicated project manager",
          "12-month post-launch support"
        ]
      }
    ]
  }
}
```

## JSON input structure (PDF)

Same as above but:
- `"engine": "playwright"` (or omit engine, defaults to playwright for PDF)
- `"outputPath": "./proposal_acme_2026-03-19.pdf"`

## Notes

- For Ukrainian proposals: translate headings and use `₴` currency
- For formal proposals: add sections for Terms & Conditions, Validity period, Contact details
- Proposal PDF uses the generic builder with full-width navy cover header
