# Contract Template — International (PDF)

A corporate service contract template. Used when generating contracts between business entities. Supports any language for content — the template structure is universal.

## Required Fields

```
title: "SERVICE AGREEMENT"
number: "MSA-2026-001"
date: "April 7, 2026"
city: "San Francisco, CA"
governingLaw: "the State of California"

companyInfo:
  name: "TechCo Solutions LLC"
  address: "100 Main Street, Suite 200, San Francisco, CA 94105"
  reg: "EIN: 12-3456789"
  email: "info@techco.com"
  # Optional: logoBase64 (base64 PNG) or logoUrl

party1:                                # Service Provider
  name: "TechCo Solutions LLC"
  address: "100 Main Street, Suite 200, San Francisco, CA 94105"
  reg: "EIN: 12-3456789"
  representative: "Alex Morgan"
  title: "Managing Director"

party2:                                # Client
  name: "Acme Corporation"
  address: "500 Enterprise Avenue, New York, NY 10001"
  reg: "EIN: 98-7654321"
  representative: "Sarah Chen"
  title: "Chief Technology Officer"

clauses:
  - number: "1"
    title: "Subject of Agreement"
    paragraphs:
      - "The Service Provider agrees to provide the Client with software development services in accordance with the technical specification (Annex 1 to this Agreement)."
      - "The Client agrees to accept and pay for the services rendered in the manner and within the timeframe set forth in this Agreement."
  - number: "2"
    title: "Price and Payment Terms"
    paragraphs:
      - "The total fee for services under this Agreement is $70,000 (seventy thousand US dollars), exclusive of applicable taxes."
      - "Payment shall be made within 15 (fifteen) business days of receipt of invoice."
  - number: "3"
    title: "Service Duration"
    paragraphs:
      - "Services shall be provided within 90 (ninety) calendar days from the date of signing this Agreement."
  - number: "4"
    title: "Confidentiality"
    paragraphs:
      - "Both parties agree to maintain the confidentiality of any information received in the course of performing this Agreement for a period of three (3) years from the date of disclosure."
  - number: "5"
    title: "Liability"
    paragraphs:
      - "In case of late payment, the Client shall pay interest at the rate of 1.5% per month on the outstanding amount, or the maximum rate permitted by applicable law, whichever is less."
  - number: "6"
    title: "Dispute Resolution"
    paragraphs:
      - "All disputes shall first be resolved through good-faith negotiation. If no agreement is reached within thirty (30) days, disputes shall be submitted to binding arbitration in accordance with the rules of the American Arbitration Association."
  - number: "7"
    title: "General Provisions"
    paragraphs:
      - "This Agreement becomes effective upon signing by both Parties and remains in force until all obligations are fully performed."
      - "This Agreement is executed in two counterparts of equal legal force."
```

## JSON Input Structure

```json
{
  "type": "contract",
  "engine": "playwright",
  "outputPath": "./contract_service_agreement_2026-04-07.pdf",
  "template": {
    "styling": {
      "primaryColor": "#0F172A",
      "accentColor": "#6366F1"
    }
  },
  "data": {
    "title": "SERVICE AGREEMENT",
    "number": "MSA-2026-001",
    "date": "April 7, 2026",
    "city": "San Francisco, CA",
    "governingLaw": "the State of California",
    "companyInfo": {
      "name": "TechCo Solutions LLC",
      "address": "100 Main Street, Suite 200, San Francisco, CA 94105",
      "reg": "EIN: 12-3456789",
      "email": "info@techco.com"
    },
    "party1": {
      "name": "TechCo Solutions LLC",
      "address": "100 Main Street, Suite 200, San Francisco, CA 94105",
      "reg": "EIN: 12-3456789",
      "representative": "Alex Morgan",
      "title": "Managing Director"
    },
    "party2": {
      "name": "Acme Corporation",
      "address": "500 Enterprise Avenue, New York, NY 10001",
      "reg": "EIN: 98-7654321",
      "representative": "Sarah Chen",
      "title": "Chief Technology Officer"
    },
    "clauses": []
  }
}
```

## Notes

- Logo: add `"logoBase64": "<base64 string>"` inside `companyInfo`
- For NDA: use the dedicated `nda` document type with `/generate-nda` command
- For localized content: simply write clause titles and paragraphs in the target language — the rendering engine handles any Unicode text
