# Act of Completed Works — JSON Examples

## Minimal Example (3 service rows, no VAT)

```json
{
  "type": "act",
  "engine": "playwright",
  "outputPath": "./act_act-001_2026-03-19.pdf",
  "template": { "currencySymbol": "$" },
  "data": {
    "actNumber": "ACT-001",
    "date": "March 19, 2026",
    "city": "New York",
    "contractor": {
      "name": "Acme Consulting LLC",
      "representative": "John Smith",
      "title": "Managing Director"
    },
    "customer": {
      "name": "Global Corp Inc.",
      "representative": "Jane Doe",
      "title": "Director"
    },
    "services": [
      { "description": "Website development", "unit": "service", "quantity": 1, "unitPrice": 5000, "total": 5000 },
      { "description": "SEO optimization", "unit": "hrs", "quantity": 10, "unitPrice": 80, "total": 800 },
      { "description": "Technical support", "unit": "hrs", "quantity": 5, "unitPrice": 60, "total": 300 }
    ],
    "totalAmount": 6100,
    "vatRate": 0
  }
}
```

---

## Full Example (5 rows, VAT 20%, contract reference)

```json
{
  "type": "act",
  "engine": "playwright",
  "outputPath": "./act_act-002-2026_2026-03-31.pdf",
  "template": {
    "currencySymbol": "$",
    "styling": {
      "primaryColor": "#1E293B",
      "accentColor": "#1E3A5F",
      "textColor": "#1E293B",
      "mutedColor": "#64748B",
      "borderColor": "#E2E8F0",
      "backgroundColor": "#F8FAFC"
    }
  },
  "data": {
    "actNumber": "ACT-002/2026",
    "date": "March 31, 2026",
    "city": "London",
    "contractRef": "Contract No. 002/2026 dated February 1, 2026",
    "currencySymbol": "$",
    "vatRate": 20,
    "contractor": {
      "name": "DevStudio Ltd.",
      "representative": "Alex Johnson",
      "title": "Director",
      "reg": "Company No.: 12345678",
      "address": "10 Innovation Street, London, EC2A 4BX"
    },
    "customer": {
      "name": "Enterprise Solutions Corp.",
      "representative": "Michael Brown",
      "title": "CEO",
      "reg": "Company No.: 87654321",
      "address": "500 Business Park, London, SW1A 1AA"
    },
    "services": [
      { "description": "Requirements analysis and technical specification", "unit": "hrs", "quantity": 20, "unitPrice": 120, "total": 2400 },
      { "description": "Backend development (Node.js, PostgreSQL)", "unit": "hrs", "quantity": 80, "unitPrice": 150, "total": 12000 },
      { "description": "Frontend development (React)", "unit": "hrs", "quantity": 60, "unitPrice": 140, "total": 8400 },
      { "description": "QA testing", "unit": "hrs", "quantity": 20, "unitPrice": 100, "total": 2000 },
      { "description": "Deployment and documentation", "unit": "hrs", "quantity": 10, "unitPrice": 120, "total": 1200 }
    ],
    "totalAmount": 26000,
    "notes": "All work completed in accordance with the technical specification. No claims from the customer."
  }
}
```

**Calculated totals for full example:**
- Subtotal: $26,000
- VAT (20%): $5,200
- Grand total: $31,200
