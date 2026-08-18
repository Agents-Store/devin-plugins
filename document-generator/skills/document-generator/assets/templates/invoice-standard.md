# Invoice Template — Standard (PDF)

Standard invoice without logo. Clean corporate layout with items table, totals box, payment details card.

## Required fields

```
invoiceNumber: "INV-001"
date: "2026-03-19"
dueDate: "2026-04-02"

companyInfo:
  name: "Your Company Name"
  address: "123 Business St, City, Country"
  phone: "+1 (555) 000-0000"
  email: "billing@company.com"

recipientInfo:
  name: "Client Name or Company"
  address: "456 Client Ave, City, Country"
  email: "accounts@client.com"   # optional

items:
  - description: "Service or product name"
    quantity: 10
    unitPrice: 150.00
    total: 1500.00
```

## Optional fields

```
subtotal: 1500.00         # auto-calculated if omitted
tax: 0                    # tax amount in currency
discount: 0               # discount amount in currency
total: 1500.00            # auto-calculated if omitted
currencySymbol: "$"       # default $

paymentDetails:
  bank: "Bank Name"
  accountName: "Company Name"
  iban: "UA21 3006 5000 0000 0026 2001 0000 1"
  swift: "UKRSUAUX"

notes: "Thank you for your business."
```

## JSON input structure

```json
{
  "type": "invoice",
  "engine": "playwright",
  "outputPath": "./invoice_inv-001_2026-03-19.pdf",
  "template": {
    "currencySymbol": "$",
    "styling": {
      "primaryColor": "#1E3A5F",
      "accentColor": "#2563EB"
    }
  },
  "data": {
    "invoiceNumber": "INV-001",
    "date": "March 19, 2026",
    "dueDate": "April 2, 2026",
    "companyInfo": {
      "name": "Acme Services Ltd.",
      "address": "123 Business St, Kyiv, Ukraine",
      "phone": "+380 44 000 0000",
      "email": "billing@acme.ua"
    },
    "recipientInfo": {
      "name": "Global Client Corp.",
      "address": "456 Client Ave, London, UK",
      "email": "accounts@globalclient.com"
    },
    "items": [
      {
        "description": "Web Development Services",
        "quantity": 40,
        "unitPrice": 75.00,
        "total": 3000.00
      },
      {
        "description": "Project Management",
        "quantity": 8,
        "unitPrice": 50.00,
        "total": 400.00
      }
    ],
    "tax": 0,
    "paymentDetails": {
      "bank": "PrivatBank",
      "accountName": "Acme Services Ltd.",
      "iban": "UA21 3006 5000 0000 0026 2001 0000 1",
      "swift": "PBANUA2X"
    },
    "notes": "Payment due within 14 days. Thank you for your business."
  }
}
```
