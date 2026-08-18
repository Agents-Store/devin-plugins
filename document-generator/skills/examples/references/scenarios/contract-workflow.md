# Scenario: Generating a Service Contract

End-to-end workflow for generating a service agreement contract.

## User Request

> "Create a service agreement contract between our company TechFlow Solutions and client DataVault Corp. 6-month engagement, $120,000 total, monthly payments. Ukrainian law."

## Step 1: CLASSIFY

Document type: **contract**
Default format: **DOCX** (always — needs edits and signatures)

## Step 2: GATHER Data

Agent collects:

- Title: "Service Agreement"
- Contract number: SA-2026-015
- Date: 2026-03-18
- Party 1: TechFlow Solutions LLC (service provider)
- Party 2: DataVault Corp (client)
- Key terms: 6 months, $120K, monthly payments of $20K
- Governing law: Ukraine

## Step 3: SELECT

Format: DOCX
Script: `generate_docx.js`

## Step 4: BUILD JSON Input

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
        "content": "\"Services\" means the software development, consulting, and support services described in this Agreement.\n\n\"Deliverables\" means the work products, code, documentation, and other materials produced by the Service Provider under this Agreement.\n\n\"Confidential Information\" means any non-public information disclosed by either party, including but not limited to business plans, source code, customer data, and financial information."
      },
      {
        "id": "scope",
        "title": "Scope of Services",
        "content": "The Service Provider shall provide the following services to the Client:\n\na) Design and development of a data analytics platform\nb) Integration with Client's existing data infrastructure\nc) User acceptance testing and quality assurance\nd) Technical documentation and knowledge transfer\ne) Post-launch support for 30 days after go-live"
      },
      {
        "id": "payment",
        "title": "Payment Terms",
        "content": "The total compensation for Services under this Agreement is $120,000 (one hundred twenty thousand US dollars).\n\nPayment shall be made in six (6) equal monthly installments of $20,000, due on the first business day of each month.\n\nPayment shall be made via bank wire transfer to the account specified by the Service Provider. Late payments shall accrue interest at a rate of 1.5% per month."
      },
      {
        "id": "duration",
        "title": "Duration and Termination",
        "content": "This Agreement shall commence on April 1, 2026 and shall continue for a period of six (6) months, ending on September 30, 2026.\n\nEither party may terminate this Agreement with 30 days written notice. In the event of termination, the Client shall pay for all Services rendered through the effective date of termination.\n\nThe Service Provider may terminate immediately if the Client fails to make payment within 15 days of the due date."
      },
      {
        "id": "confidentiality",
        "title": "Confidentiality",
        "content": "Each party agrees to maintain the confidentiality of all Confidential Information received from the other party.\n\nConfidential Information shall not be disclosed to any third party without the prior written consent of the disclosing party.\n\nThis obligation of confidentiality shall survive termination of this Agreement for a period of two (2) years."
      },
      {
        "id": "ip",
        "title": "Intellectual Property",
        "content": "All Deliverables created under this Agreement shall become the property of the Client upon full payment.\n\nThe Service Provider retains ownership of pre-existing tools, frameworks, and methodologies used in the performance of Services. The Client is granted a perpetual, non-exclusive license to use such pre-existing IP as incorporated in the Deliverables."
      },
      {
        "id": "governing_law",
        "title": "Governing Law",
        "content": "This Agreement shall be governed by and construed in accordance with the laws of Ukraine.\n\nAny disputes arising under this Agreement shall be resolved through negotiation. If negotiation fails, disputes shall be submitted to the competent courts of Kyiv, Ukraine."
      }
    ],
    "signatureBlock": {
      "party1": {
        "label": "TechFlow Solutions LLC",
        "name": true,
        "title": true,
        "date": true
      },
      "party2": {
        "label": "DataVault Corp",
        "name": true,
        "title": true,
        "date": true
      }
    }
  }
}
```

## Step 5: GENERATE

```bash
cd <plugin_dir> && node scripts/generate_docx.js /path/to/.doc_input.json
```

Output:
```json
{ "success": true, "outputPath": "/Users/user/contract_service_agreement_2026-03-18.docx", "size": 38920 }
```

## Step 6: DELIVER

> Contract generated successfully:
> - File: `contract_service_agreement_2026-03-18.docx`
> - Size: 38.0 KB
> - Format: DOCX (Microsoft Word)
> - Clauses: 7 (Definitions, Scope, Payment, Duration, Confidentiality, IP, Governing Law)
> - Signature blocks: 2 parties
>
> **Important**: This is a template. Please have it reviewed by a legal professional before signing.
