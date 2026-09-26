# Scenario: Creating a Business Proposal

End-to-end workflow for generating a consulting services proposal.

## User Request

> "Create a business proposal for cloud migration consulting services for Acme Corporation. Budget is $75,000, timeline is 8 weeks."

## Step 1: CLASSIFY

Document type: **proposal**
Default format: **DOCX**

## Step 2: GATHER Data

Agent asks the user for required fields:

- Title: "Cloud Migration Strategy & Implementation Proposal"
- Recipient: "Acme Corporation"
- Author: "CloudTech Solutions"
- Company: "CloudTech Solutions"
- Date: "2026-03-17"

Then collects section content through Q&A:

**Executive Summary**: Brief overview of the migration approach
**Problem Statement**: Current on-premise infrastructure challenges
**Proposed Solution**: Phased cloud migration to AWS
**Timeline**: 8-week plan with milestones
**Pricing**: $75,000 broken into phases

## Step 3: SELECT

Format: DOCX (editable, for client review)
Script: `generate_docx.js`

## Step 4: BUILD JSON Input

```json
{
  "type": "proposal",
  "outputPath": "./proposal_cloud_migration_2026-03-17.docx",
  "template": {
    "styling": {
      "primaryColor": "#1E3A5F",
      "accentColor": "#2563EB",
      "fontHeading": "Georgia",
      "fontBody": "Arial",
      "fontSizeBody": 11,
      "lineSpacing": 1.3,
      "margins": { "top": 1440, "bottom": 1440, "left": 1080, "right": 1080 }
    }
  },
  "data": {
    "title": "Cloud Migration Strategy & Implementation Proposal",
    "subtitle": "Prepared for Acme Corporation",
    "author": "CloudTech Solutions",
    "recipient": "Acme Corporation",
    "date": "March 17, 2026",
    "companyName": "CloudTech Solutions",
    "footer": "CloudTech Solutions | Confidential",
    "headerText": "Cloud Migration Proposal",
    "sections": [
      {
        "heading": "Executive Summary",
        "level": 1,
        "content": "This proposal outlines a comprehensive cloud migration strategy for Acme Corporation's on-premise infrastructure. Our phased approach ensures minimal disruption while maximizing cost savings and scalability.\n\nThe project spans 8 weeks with a total investment of $75,000, delivering a fully migrated cloud environment on AWS."
      },
      {
        "heading": "Problem Statement",
        "level": 1,
        "content": "Acme Corporation currently relies on aging on-premise servers that present several challenges:\n\nHigh maintenance costs exceeding $50,000 annually for hardware and licensing. Limited scalability during peak demand periods. Single point of failure with no geographic redundancy. Growing security compliance requirements that are difficult to meet with current infrastructure."
      },
      {
        "heading": "Proposed Solution",
        "level": 1,
        "content": "We propose a phased migration to Amazon Web Services (AWS) that will address all identified challenges while providing a foundation for future growth.",
        "subsections": [
          { "heading": "Phase 1: Assessment & Planning", "content": "Comprehensive audit of existing infrastructure, application dependencies, and data flows. Deliverable: Migration plan with risk assessment." },
          { "heading": "Phase 2: Migration Execution", "content": "Systematic migration of workloads using AWS Migration Hub. Includes database migration, application containerization, and network configuration." },
          { "heading": "Phase 3: Testing & Optimization", "content": "Performance testing, security hardening, and cost optimization. Ensure all SLAs are met before cutover." }
        ]
      },
      {
        "heading": "Timeline & Milestones",
        "level": 1,
        "content": "The project follows an 8-week timeline:",
        "table": [
          { "Phase": "Assessment", "Duration": "Weeks 1-2", "Deliverable": "Migration plan" },
          { "Phase": "Migration", "Duration": "Weeks 3-6", "Deliverable": "Migrated workloads" },
          { "Phase": "Testing", "Duration": "Weeks 7-8", "Deliverable": "Go-live approval" }
        ]
      },
      {
        "heading": "Pricing",
        "level": 1,
        "content": "Total project investment: $75,000",
        "table": [
          { "Item": "Assessment & Planning", "Hours": "80", "Rate": "$200/hr", "Total": "$16,000" },
          { "Item": "Migration Execution", "Hours": "200", "Rate": "$200/hr", "Total": "$40,000" },
          { "Item": "Testing & Optimization", "Hours": "80", "Rate": "$200/hr", "Total": "$16,000" },
          { "Item": "Project Management", "Hours": "15", "Rate": "$200/hr", "Total": "$3,000" }
        ]
      },
      {
        "heading": "About Us",
        "level": 1,
        "content": "CloudTech Solutions is a certified AWS Advanced Consulting Partner with 10+ years of cloud migration experience. We have successfully migrated over 200 enterprises to the cloud."
      }
    ]
  }
}
```

## Step 5: GENERATE

```bash
cd <plugin_dir> && node scripts/generate_docx.js /path/to/.doc_input.json
```

Output:
```json
{ "success": true, "outputPath": "/Users/user/proposal_cloud_migration_2026-03-17.docx", "size": 45672 }
```

## Step 6: DELIVER

> Document generated successfully:
> - File: `proposal_cloud_migration_2026-03-17.docx`
> - Size: 44.6 KB
> - Format: DOCX (Microsoft Word)
>
> Want me to convert this to PDF for the final version?
