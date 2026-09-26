# Proposal JSON Input Example

Complete example of JSON input for `generate_docx.js` to create a business proposal.

## Minimal Proposal

```json
{
  "type": "proposal",
  "outputPath": "./proposal_consulting_2026-03-17.docx",
  "data": {
    "title": "Consulting Services Proposal",
    "author": "Your Company",
    "recipient": "Client Company",
    "date": "2026-03-17",
    "sections": [
      {
        "heading": "Executive Summary",
        "level": 1,
        "content": "Brief overview of the proposed services."
      },
      {
        "heading": "Proposed Solution",
        "level": 1,
        "content": "Description of how we will address your needs."
      },
      {
        "heading": "Pricing",
        "level": 1,
        "content": "Total investment: $25,000",
        "table": [
          { "Service": "Consulting", "Hours": "50", "Rate": "$250/hr", "Total": "$12,500" },
          { "Service": "Implementation", "Hours": "50", "Rate": "$250/hr", "Total": "$12,500" }
        ]
      }
    ]
  }
}
```

## Full Proposal (with branding and all sections)

```json
{
  "type": "proposal",
  "outputPath": "./proposal_full_example_2026-03-17.docx",
  "template": {
    "styling": {
      "primaryColor": "#1E40AF",
      "fontHeading": "Calibri",
      "fontBody": "Calibri",
      "fontSizeTitle": 28,
      "fontSizeH1": 18,
      "fontSizeBody": 11,
      "lineSpacing": 1.15,
      "margins": { "top": 1440, "bottom": 1440, "left": 1080, "right": 1080 }
    }
  },
  "data": {
    "title": "Digital Transformation Strategy",
    "subtitle": "A Comprehensive Modernization Plan",
    "author": "DigitalFirst Consulting",
    "recipient": "GlobalRetail Inc.",
    "date": "March 17, 2026",
    "companyName": "DigitalFirst Consulting",
    "footer": "DigitalFirst Consulting | Confidential",
    "headerText": "Digital Transformation Proposal",
    "tableOfContents": true,
    "sections": [
      {
        "heading": "Executive Summary",
        "level": 1,
        "content": "This proposal presents a 12-week digital transformation strategy..."
      },
      {
        "heading": "Current State Assessment",
        "level": 1,
        "content": "Based on our discovery sessions, we identified key areas...",
        "bullets": [
          "Legacy POS systems limiting omnichannel capabilities",
          "Manual inventory processes causing 15% stock discrepancies",
          "Customer data siloed across 5 different platforms"
        ]
      },
      {
        "heading": "Proposed Solution",
        "level": 1,
        "content": "Our three-phase approach addresses each challenge systematically.",
        "subsections": [
          {
            "heading": "Phase 1: Foundation",
            "content": "Unified data platform and API layer."
          },
          {
            "heading": "Phase 2: Integration",
            "content": "Connect all touchpoints through the new platform."
          },
          {
            "heading": "Phase 3: Optimization",
            "content": "AI-driven insights and automation."
          }
        ]
      },
      {
        "heading": "Timeline",
        "level": 1,
        "table": [
          { "Phase": "Foundation", "Weeks": "1-4", "Key Milestone": "Data platform live" },
          { "Phase": "Integration", "Weeks": "5-8", "Key Milestone": "All channels connected" },
          { "Phase": "Optimization", "Weeks": "9-12", "Key Milestone": "AI dashboards deployed" }
        ]
      },
      {
        "heading": "Investment",
        "level": 1,
        "content": "Total project investment: $150,000",
        "table": [
          { "Component": "Phase 1", "Cost": "$50,000" },
          { "Component": "Phase 2", "Cost": "$60,000" },
          { "Component": "Phase 3", "Cost": "$40,000" }
        ]
      },
      {
        "heading": "About DigitalFirst Consulting",
        "level": 1,
        "content": "15 years of retail digital transformation experience. 200+ successful projects. Certified partners with Salesforce, AWS, and Shopify."
      }
    ]
  }
}
```
