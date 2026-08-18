# Scenario: Generating an Invoice

End-to-end workflow for generating a professional PDF invoice.

## User Request

> "Generate invoice INV-2026-042 for Acme Corp. Web development services: 40 hours at $150/hr. 20% VAT. Payment to our IBAN."

## Step 1: CLASSIFY

Document type: **invoice**
Format: **PDF** (always)

## Step 2: GATHER Data

Agent confirms and collects:

- Invoice number: INV-2026-042
- Company info: user's company details
- Client: Acme Corporation
- Line items: 1 item -- Web Development, 40 hrs, $150/hr
- Tax: 20% VAT = $1,200
- Payment details: IBAN provided

## Step 3: SELECT

Format: PDF
Engine: playwright (HTML template for branded look)
Script: `generate_pdf.js`

## Step 4: BUILD JSON Input

```json
{
  "type": "invoice",
  "engine": "playwright",
  "outputPath": "./invoice_inv-2026-042_2026-03-17.pdf",
  "template": {
    "styling": {
      "primaryColor": "#2563EB",
      "accentColor": "#F59E0B",
      "fontFamily": "Helvetica, Arial, sans-serif",
      "pageSize": "A4",
      "margins": { "top": "20mm", "bottom": "20mm", "left": "15mm", "right": "15mm" }
    },
    "currencySymbol": "$"
  },
  "data": {
    "invoiceNumber": "INV-2026-042",
    "date": "2026-03-17",
    "dueDate": "2026-04-17",
    "companyInfo": {
      "name": "TechCo Solutions LLC",
      "address": "456 Tech Avenue, Suite 200, San Francisco, CA 94102",
      "phone": "+1 (555) 123-4567",
      "email": "billing@techco.com"
    },
    "recipientInfo": {
      "name": "Acme Corporation",
      "address": "789 Enterprise Blvd, New York, NY 10001",
      "email": "ap@acme.com"
    },
    "items": [
      {
        "description": "Web Development Services",
        "quantity": 40,
        "unitPrice": 150,
        "total": 6000
      }
    ],
    "subtotal": 6000,
    "tax": 1200,
    "total": 7200,
    "paymentDetails": {
      "bank": "First National Bank",
      "iban": "US12 3456 7890 1234 5678 90",
      "swift": "FNBKUS33",
      "accountName": "TechCo Solutions LLC"
    },
    "notes": "Payment due within 30 days. Late payments subject to 1.5% monthly interest."
  }
}
```

## Step 5: GENERATE

```bash
cd <plugin_dir> && node scripts/generate_pdf.js /path/to/.doc_input.json
```

Output:
```json
{ "success": true, "outputPath": "/Users/user/invoice_inv-2026-042_2026-03-17.pdf", "size": 28934 }
```

## Step 6: DELIVER

> Invoice generated successfully:
> - File: `invoice_inv-2026-042_2026-03-17.pdf`
> - Size: 28.3 KB
> - Format: PDF
>
> Summary:
> | Item | Amount |
> |------|--------|
> | Web Development (40 hrs x $150) | $6,000.00 |
> | VAT (20%) | $1,200.00 |
> | **Total** | **$7,200.00** |
