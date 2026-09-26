# Invoice JSON Input Example

Complete example of JSON input for `generate_pdf.js` to create a professional invoice.

## Minimal Invoice

```json
{
  "type": "invoice",
  "outputPath": "./invoice_001_2026-03-17.pdf",
  "data": {
    "invoiceNumber": "INV-001",
    "date": "2026-03-17",
    "dueDate": "2026-04-17",
    "companyInfo": {
      "name": "Your Company"
    },
    "recipient": {
      "name": "Client Company"
    },
    "items": [
      { "description": "Consulting Services", "quantity": 10, "unitPrice": 200, "total": 2000 }
    ],
    "subtotal": 2000,
    "total": 2000
  }
}
```

## Full Invoice (with all details)

```json
{
  "type": "invoice",
  "engine": "playwright",
  "outputPath": "./invoice_2026-042_2026-03-17.pdf",
  "template": {
    "styling": {
      "primaryColor": "#1E3A5F",
      "accentColor": "#2563EB",
      "textColor": "#1E293B",
      "mutedColor": "#64748B",
      "borderColor": "#E2E8F0",
      "backgroundColor": "#F8FAFC"
    },
    "currencySymbol": "$"
  },
  "data": {
    "invoiceNumber": "INV-2026-042",
    "date": "March 17, 2026",
    "dueDate": "April 17, 2026",
    "companyInfo": {
      "name": "Apex Development Studio",
      "address": "100 Innovation Drive, Austin, TX 78701",
      "phone": "+1 (512) 555-0190",
      "email": "billing@apexdev.io"
    },
    "recipient": {
      "name": "NovaTech Industries",
      "address": "500 Corporate Park, Chicago, IL 60601",
      "email": "accounts@novatech.com"
    },
    "items": [
      {
        "description": "Frontend Development (React)",
        "quantity": 80,
        "unitPrice": 175,
        "total": 14000
      },
      {
        "description": "Backend API Development (Node.js)",
        "quantity": 60,
        "unitPrice": 175,
        "total": 10500
      },
      {
        "description": "Database Design & Migration",
        "quantity": 20,
        "unitPrice": 200,
        "total": 4000
      },
      {
        "description": "QA Testing & Bug Fixes",
        "quantity": 30,
        "unitPrice": 150,
        "total": 4500
      },
      {
        "description": "Project Management",
        "quantity": 15,
        "unitPrice": 200,
        "total": 3000
      }
    ],
    "subtotal": 36000,
    "tax": 7200,
    "discount": 1800,
    "total": 41400,
    "paymentDetails": {
      "bank": "Silicon Valley Bank",
      "iban": "US64 1234 5678 9012 3456 78",
      "swift": "SVBKUS6S",
      "accountName": "Apex Development Studio LLC"
    },
    "notes": "Payment terms: Net 30. Early payment discount: 5% if paid within 10 days. Late payments subject to 1.5% monthly interest. Please reference invoice number in payment."
  }
}
```

## Simple Invoice with PDFKit Engine

**Important**: The pdfkit engine uses a generic document structure (`title`, `author`, `sections`) instead of the structured invoice fields (`invoiceNumber`, `companyInfo`, `items`). Use pdfkit only for simple, text-based invoices when Chromium/Playwright is not available. For professional invoices with formatted tables and branding, use the default playwright engine.

```json
{
  "type": "invoice",
  "engine": "pdfkit",
  "outputPath": "./invoice_simple_2026-03-17.pdf",
  "data": {
    "title": "Invoice #INV-003",
    "date": "2026-03-17",
    "author": "Your Company",
    "sections": [
      {
        "heading": "Bill To: Client Name",
        "content": "Service rendered: 20 hours of consulting at $100/hr.\n\nTotal: $2,000.00\n\nDue: 2026-04-17"
      }
    ]
  }
}
```
