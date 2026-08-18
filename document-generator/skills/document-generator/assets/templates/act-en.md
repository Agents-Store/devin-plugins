# Certificate of Completion Template (PDF)

A formal certificate of completion (also known as "Act of Completed Works" in some jurisdictions). Includes a services table, totals, confirmation of no claims, and signature blocks for both parties. International business standard format.

## Required Fields

```
actNumber: "COC-001"
date: "April 7, 2026"
city: "San Francisco"

contractor:               # Service provider
  name: "TechCo Solutions LLC"
  representative: "Alex Morgan"
  title: "Managing Director"
  reg: "EIN: 12-3456789"
  address: "100 Main Street, Suite 200, San Francisco, CA 94105"

customer:                 # Client
  name: "Acme Corporation"
  representative: "Sarah Chen"
  title: "Chief Technology Officer"
  reg: "EIN: 98-7654321"
  address: "500 Enterprise Avenue, New York, NY 10001"

services:
  - description: "Service or work description"
    unit: "hrs"           # hrs / pcs / service / month
    quantity: 40
    unitPrice: 175
    total: 7000
```

## Optional Fields

```
contractRef: "Master Service Agreement MSA-2026-001 dated January 1, 2026"
vatRate: 0                                            # VAT rate in %
currencySymbol: "$"                                   # currency symbol
totalAmount: 7000                                     # auto-calculated if omitted
notes: "Additional notes or conditions."
```

## JSON Input Structure

```json
{
  "type": "act",
  "engine": "playwright",
  "outputPath": "./certificate_coc-001_2026-04-07.pdf",
  "template": {
    "currencySymbol": "$",
    "styling": {
      "primaryColor": "#0F172A",
      "accentColor": "#6366F1"
    }
  },
  "data": {
    "language": "en",
    "actNumber": "COC-2026-001",
    "date": "April 7, 2026",
    "city": "San Francisco",
    "contractRef": "Master Service Agreement MSA-2026-001 dated March 1, 2026",
    "currencySymbol": "$",
    "vatRate": 0,
    "contractor": {
      "name": "TechCo Solutions LLC",
      "representative": "Alex Morgan",
      "title": "Managing Director",
      "reg": "EIN: 12-3456789",
      "address": "100 Main Street, Suite 200, San Francisco, CA 94105"
    },
    "customer": {
      "name": "Acme Corporation",
      "representative": "Sarah Chen",
      "title": "Chief Technology Officer",
      "reg": "EIN: 98-7654321",
      "address": "500 Enterprise Avenue, New York, NY 10001"
    },
    "services": [
      {
        "description": "Frontend web application development",
        "unit": "hrs",
        "quantity": 40,
        "unitPrice": 175,
        "total": 7000
      },
      {
        "description": "Technical support and testing",
        "unit": "hrs",
        "quantity": 10,
        "unitPrice": 120,
        "total": 1200
      }
    ],
    "totalAmount": 8200,
    "notes": "All work completed in full and within the agreed timeline."
  }
}
```

## Common Units of Measure

| Abbreviation | Meaning |
|-------------|---------|
| hrs | Hours |
| pcs | Pieces / Units |
| service | Service (one-time) |
| month | Month |
| project | Project (lump sum) |

## VAT Notes

- No VAT (small business / not VAT registered): `"vatRate": 0`
- VAT registered: `"vatRate": 20` — VAT amount will be calculated and shown as a separate line

## Multi-Language Support

For non-English versions, set the `language` field. Available codes: `en`, `ua`, `de`, `fr`, `es`. The labels (title, table headers, signature blocks, confirmation text) will auto-translate. Content (service descriptions, names, addresses) should be provided in the target language.
