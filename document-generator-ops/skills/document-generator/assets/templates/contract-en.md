# Contract Template — English (PDF)

Corporate English-language service contract. Used when generating contracts for English-speaking parties or international agreements.

## Required fields

```
title: "Service Agreement" | "Non-Disclosure Agreement" | etc.
number: "CONTRACT-001"
date: "2026-03-19"
city: "San Francisco"
governingLaw: "United States"

companyInfo:
  name: "Your Company Name"
  address: "100 Main Street, City, Country"
  reg: "Company Registration No"
  email: "contact@company.com"
  # Optional: logoBase64 (PNG base64 string) or logoUrl

party1:
  name: "Contractor Ltd."
  address: "Full legal address"
  reg: "Registration number"
  representative: "John Doe"
  title: "Director"

party2:
  name: "Customer Corp."
  address: "Full legal address"
  reg: "Registration number"
  representative: "Jane Smith"
  title: "CEO"

clauses:
  - number: "1"
    title: "Subject of Agreement"
    paragraphs:
      - "The Contractor agrees to provide the following services: ..."
      - "The Customer agrees to accept and pay for the services as described herein."
  - number: "2"
    title: "Payment Terms"
    paragraphs:
      - "The total fee for services is USD 5,000 (five thousand US dollars)."
      - "Payment shall be made within 5 business days of invoice receipt."
  - number: "3"
    title: "Duration"
    paragraphs:
      - "This Agreement is effective from the date of signing and remains in effect for 12 months."
  - number: "4"
    title: "Confidentiality"
    paragraphs:
      - "Both parties agree to keep all information exchanged under this Agreement strictly confidential."
  - number: "5"
    title: "Governing Law"
    paragraphs:
      - "This Agreement shall be governed by the laws of United States."
```

## JSON input structure

```json
{
  "type": "contract",
  "engine": "playwright",
  "outputPath": "./contract_service_agreement_2026-03-19.pdf",
  "template": {
    "styling": {
      "primaryColor": "#1E293B",
      "accentColor": "#1E3A5F"
    }
  },
  "data": {
    "title": "Service Agreement",
    "number": "CONTRACT-001",
    "date": "March 19, 2026",
    "city": "San Francisco",
    "governingLaw": "United States",
    "companyInfo": {
      "name": "Your Company Name",
      "address": "100 Main Street, San Francisco, CA 94105",
      "reg": "UA12345678",
      "email": "contact@yourcompany.com"
    },
    "party1": {
      "name": "Contractor Ltd.",
      "address": "200 Market Street, San Francisco, CA 94105",
      "reg": "UA87654321",
      "representative": "John Doe",
      "title": "Director"
    },
    "party2": {
      "name": "Customer Corp.",
      "address": "789 Customer Blvd, London, UK",
      "reg": "UK12345",
      "representative": "Jane Smith",
      "title": "CEO"
    },
    "clauses": [
      {
        "number": "1",
        "title": "Subject of Agreement",
        "paragraphs": ["The Contractor agrees to provide software development services as detailed in Annex A."]
      }
    ]
  }
}
```

## Notes

- Logo: add `"logoBase64": "<base64 string>"` inside `companyInfo` to display logo in header
- For NDA: use clauses covering Confidential Information definition, Obligations, Exclusions, Term, Remedies
- For Employment: use clauses for Position, Compensation, Working Hours, Benefits, Termination
