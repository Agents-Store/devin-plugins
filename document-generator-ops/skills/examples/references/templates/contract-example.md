# Contract JSON Input Example

Complete example of JSON input for `generate_docx.js` to create a professional contract.

## Minimal Contract

```json
{
  "type": "contract",
  "outputPath": "./contract_nda_2026-03-18.docx",
  "data": {
    "title": "NON-DISCLOSURE AGREEMENT",
    "date": "2026-03-18",
    "parties": {
      "party1": { "label": "Disclosing Party", "name": "Acme Corp" },
      "party2": { "label": "Receiving Party", "name": "Contractor Name" }
    },
    "clauses": [
      {
        "id": "confidentiality",
        "title": "Confidentiality Obligations",
        "content": "The Receiving Party agrees not to disclose any Confidential Information to third parties.\n\nThis obligation survives for 3 years after termination."
      },
      {
        "id": "governing_law",
        "title": "Governing Law",
        "content": "This Agreement is governed by the laws of the State of Delaware, USA."
      }
    ]
  }
}
```

## Full Service Agreement (with all clauses and signature blocks)

```json
{
  "type": "contract",
  "outputPath": "./contract_service_agreement_2026-03-18.docx",
  "template": {
    "styling": {
      "primaryColor": "#1E293B",
      "accentColor": "#1E3A5F",
      "fontBody": "Georgia",
      "fontSizeTitle": 16,
      "fontSizeClauseTitle": 12,
      "fontSizeBody": 11,
      "lineSpacing": 1.5,
      "margins": { "top": 1440, "bottom": 1440, "left": 1440, "right": 1440 }
    }
  },
  "data": {
    "title": "SERVICE AGREEMENT",
    "contractNumber": "SA-2026-015",
    "date": "March 18, 2026",
    "party1": {
      "role": "Service Provider",
      "name": "TechFlow Solutions LLC",
      "address": "12 Innovation Street, Kyiv, Ukraine, 01001",
      "reg": "UA-44521890"
    },
    "party2": {
      "role": "Client",
      "name": "DataVault Corp",
      "address": "500 Enterprise Blvd, Suite 300, Kyiv, Ukraine, 02002",
      "reg": "UA-33198450"
    },
    "clauses": [
      {
        "id": "definitions",
        "title": "Definitions",
        "content": "\"Services\" means the software development, consulting, and support services described herein.\n\n\"Deliverables\" means all work products, code, documentation, and materials produced under this Agreement.\n\n\"Confidential Information\" means any non-public information disclosed by either party."
      },
      {
        "id": "scope",
        "title": "Scope of Services",
        "content": "The Service Provider shall:\n\na) Design and develop a data analytics platform\nb) Integrate with Client's existing infrastructure\nc) Conduct user acceptance testing\nd) Provide technical documentation\ne) Deliver post-launch support for 30 days"
      },
      {
        "id": "payment",
        "title": "Payment Terms",
        "content": "Total compensation: $120,000 USD.\n\nPayment in 6 monthly installments of $20,000 each, due on the 1st business day of each month.\n\nLate payments accrue interest at 1.5% per month."
      },
      {
        "id": "duration",
        "title": "Duration and Termination",
        "content": "Effective: April 1, 2026. Duration: 6 months (through September 30, 2026).\n\nEither party may terminate with 30 days written notice. Client pays for all Services rendered through termination date.\n\nImmediate termination if Client fails to pay within 15 days of due date."
      },
      {
        "id": "confidentiality",
        "title": "Confidentiality",
        "content": "Each party shall maintain strict confidentiality of all information received from the other party.\n\nNo disclosure to third parties without prior written consent.\n\nSurvives termination for 2 years."
      },
      {
        "id": "ip",
        "title": "Intellectual Property",
        "content": "Deliverables become Client's property upon full payment.\n\nService Provider retains ownership of pre-existing IP. Client receives perpetual, non-exclusive license for pre-existing IP incorporated in Deliverables."
      },
      {
        "id": "liability",
        "title": "Limitation of Liability",
        "content": "Neither party's total liability shall exceed the total fees paid under this Agreement.\n\nNeither party is liable for indirect, incidental, or consequential damages."
      },
      {
        "id": "governing_law",
        "title": "Governing Law",
        "content": "Governed by the laws of Ukraine.\n\nDisputes resolved through negotiation first, then submitted to competent courts of Kyiv, Ukraine."
      }
    ],
    "signatureBlock": {
      "party1": {
        "label": "TechFlow Solutions LLC"
      },
      "party2": {
        "label": "DataVault Corp"
      }
    }
  }
}
```

## Employment Contract

```json
{
  "type": "contract",
  "outputPath": "./contract_employment_2026-03-18.docx",
  "data": {
    "title": "EMPLOYMENT CONTRACT",
    "contractNumber": "EMP-2026-042",
    "date": "2026-03-18",
    "parties": {
      "employer": { "label": "Employer", "name": "CloudMetrics Inc.", "address": "100 Tech Park, Kyiv" },
      "employee": { "label": "Employee", "name": "Maria Kovalenko", "address": "25 Shevchenko Blvd, Kyiv" }
    },
    "clauses": [
      {
        "id": "scope",
        "title": "Position and Duties",
        "content": "The Employee is hired as Senior Software Engineer.\n\nDuties include: software development, code review, mentoring junior developers, and participation in architectural decisions."
      },
      {
        "id": "payment",
        "title": "Compensation",
        "content": "Base salary: $96,000 per year ($8,000 per month), paid on the last business day of each month.\n\nAnnual performance bonus: up to 15% of base salary, at employer's discretion.\n\n20 paid vacation days per year."
      },
      {
        "id": "duration",
        "title": "Duration",
        "content": "This is an indefinite employment contract, effective April 1, 2026.\n\nProbation period: 3 months. Either party may terminate during probation with 2 weeks notice."
      },
      {
        "id": "confidentiality",
        "title": "Confidentiality and Non-Compete",
        "content": "Employee shall not disclose any proprietary information during or after employment.\n\nNon-compete: 12 months post-employment within the same market segment."
      },
      {
        "id": "governing_law",
        "title": "Governing Law",
        "content": "Governed by the Labor Code of Ukraine."
      }
    ]
  }
}
```
