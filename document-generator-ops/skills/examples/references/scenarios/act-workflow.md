# Act of Completed Works — Workflow Example

Step-by-step walkthrough: user requests an act of completed works → classify → gather data → build JSON → generate PDF → deliver.

---

## User Request

> "Generate an act of completed works for March. Contractor — FOP Ivanenko, customer — Client LLC."

---

## Step 1: CLASSIFY

Keywords: "act of completed works" → **act** type, default format **PDF**.

---

## Step 2: GATHER

Ask the user for required data:

```
Collecting data for the act:

1. Act number: ACT-003/2026
2. Date: March 31, 2026
3. City: Kyiv
4. Contract reference: Contract No. 001/2026 dated January 1, 2026

Contractor:
- Name: FOP Ivanenko Ivan Ivanovych
- Representative: Ivanenko I.I.
- Role: Individual Entrepreneur
- Tax ID: 1234567890

Customer:
- Name: Client LLC
- Representative: Petrenko P.P.
- Role: Director
- Registration No.: 98765432

Services:
1. API Development (backend), 60 hrs × $25.00 = $1,500.00
2. Technical Support, 10 hrs × $15.00 = $150.00

VAT: 0% (individual entrepreneur, simplified tax)
Currency: $
```

---

## Step 3: SELECT

| Type | Format | Engine | Script |
|------|--------|--------|--------|
| act | PDF | playwright | `generate_pdf.js` |

---

## Step 4: BUILD JSON

Read template:
```bash
cat <plugin_dir>/templates/act_template.json
```

Build `.doc_input.json`:
```json
{
  "type": "act",
  "engine": "playwright",
  "outputPath": "/Users/user/Documents/act_act-003-2026_2026-03-31.pdf",
  "template": {
    "currencySymbol": "$",
    "styling": {
      "primaryColor": "#1E293B",
      "accentColor": "#1E3A5F"
    }
  },
  "data": {
    "actNumber": "ACT-003/2026",
    "date": "March 31, 2026",
    "city": "Kyiv",
    "contractRef": "Contract No. 001/2026 dated January 1, 2026",
    "currencySymbol": "$",
    "vatRate": 0,
    "contractor": {
      "name": "FOP Ivanenko Ivan Ivanovych",
      "representative": "Ivanenko I.I.",
      "title": "Individual Entrepreneur",
      "reg": "Tax ID: 1234567890"
    },
    "customer": {
      "name": "Client LLC",
      "representative": "Petrenko P.P.",
      "title": "Director",
      "reg": "Reg. No.: 98765432"
    },
    "services": [
      {
        "description": "API Development (backend)",
        "unit": "hrs",
        "quantity": 60,
        "unitPrice": 25,
        "total": 1500
      },
      {
        "description": "Technical Support",
        "unit": "hrs",
        "quantity": 10,
        "unitPrice": 15,
        "total": 150
      }
    ],
    "totalAmount": 1650
  }
}
```

---

## Step 5: GENERATE

```bash
cd <plugin_dir> && node scripts/generate_pdf.js /Users/user/Documents/.doc_input.json
```

Output:
```json
{ "success": true, "outputPath": "/Users/user/Documents/act_act-003-2026_2026-03-31.pdf", "size": 124580 }
```

---

## Step 6: DELIVER

> Act of completed works generated:
> - File: `/Users/user/Documents/act_act-003-2026_2026-03-31.pdf` (121 KB)
>
> The act must be printed and signed by both parties. Want me to convert it to DOCX or make changes?
