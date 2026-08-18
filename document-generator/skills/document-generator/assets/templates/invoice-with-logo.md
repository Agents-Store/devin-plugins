# Invoice Template — With Logo (PDF)

Invoice variant that includes a company logo in the header. Uses the same corporate layout as the standard invoice, but with the logo displayed above the company name.

## Logo support

Two ways to provide a logo:

**Option 1 — Base64 encoded (recommended, works offline):**
```json
"companyInfo": {
  "name": "Acme Ltd.",
  "logoBase64": "iVBORw0KGgoAAAANSUhEUg..."
}
```

**Option 2 — URL (requires internet during PDF generation):**
```json
"companyInfo": {
  "name": "Acme Ltd.",
  "logoUrl": "https://yoursite.com/logo.png"
}
```

To convert a logo file to base64 (run in terminal):
```bash
base64 -i logo.png | tr -d '\n'
```

## Required fields

Same as `invoice-standard.md`, plus one of:
- `companyInfo.logoBase64` — base64 encoded PNG/JPEG image
- `companyInfo.logoUrl` — URL to logo image

## JSON input structure

```json
{
  "type": "invoice",
  "engine": "playwright",
  "outputPath": "./invoice_inv-001_2026-03-19.pdf",
  "template": {
    "currencySymbol": "₴",
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
      "phone": "+380 67 000 0000",
      "email": "info@acme.com",
      "logoBase64": "<base64 string here>"
    },
    "recipientInfo": {
      "name": "Global Client Corp.",
      "address": "456 Client Ave, London, UK",
      "email": "accounts@globalclient.com"
    },
    "items": [
      {
        "description": "Website development",
        "quantity": 1,
        "unitPrice": 5000,
        "total": 5000
      }
    ],
    "currencySymbol": "$",
    "paymentDetails": {
      "bank": "First National Bank",
      "accountName": "Acme Services Ltd.",
      "iban": "UA21 3006 5000 0000 0026 2001 0000 1"
    },
    "notes": "Payment due within 5 business days."
  }
}
```

## Logo size

The logo is automatically constrained to `max-height: 56px, max-width: 160px`. Use a PNG with transparent background for best results.
