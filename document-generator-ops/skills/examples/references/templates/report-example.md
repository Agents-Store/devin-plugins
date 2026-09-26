# Report JSON Input Example

Complete example of JSON input for `generate_docx.js` to create a professional report.

## Minimal Report

```json
{
  "type": "report",
  "outputPath": "./report_quarterly_2026-03-31.docx",
  "data": {
    "title": "Quarterly Report",
    "author": "Analytics Team",
    "date": "2026-03-31",
    "sections": [
      {
        "heading": "Introduction",
        "level": 1,
        "content": "This report covers Q1 2026 performance."
      },
      {
        "heading": "Key Findings",
        "level": 1,
        "content": "Revenue grew 15% quarter-over-quarter.",
        "bullets": [
          "MRR reached $943K",
          "Churn decreased to 2.1%",
          "NPS improved to 72"
        ]
      },
      {
        "heading": "Conclusions",
        "level": 1,
        "content": "Q1 was the strongest quarter on record."
      }
    ]
  }
}
```

## Full Report (with all sections, tables, and branding)

```json
{
  "type": "report",
  "outputPath": "./report_security_audit_2026-03-31.docx",
  "template": {
    "styling": {
      "primaryColor": "#1F2937",
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
    "title": "Security Audit Report",
    "subtitle": "Web Application Penetration Test Results",
    "author": "Security Team",
    "date": "March 31, 2026",
    "companyName": "CyberShield Consulting",
    "footer": "CyberShield Consulting | Confidential",
    "headerText": "Security Audit Report",
    "sections": [
      {
        "heading": "Introduction",
        "level": 1,
        "content": "This report presents the findings of a comprehensive security audit conducted on the client's web application platform during March 2026."
      },
      {
        "heading": "Methodology",
        "level": 1,
        "content": "Testing followed the OWASP Testing Guide v4.2 methodology. Both automated scanning (Burp Suite, OWASP ZAP) and manual testing were performed.",
        "subsections": [
          {
            "heading": "Scope",
            "content": "All public-facing APIs, web application frontend, authentication system, and data storage layer."
          },
          {
            "heading": "Tools Used",
            "content": "Burp Suite Professional, OWASP ZAP, Nmap, SQLMap, custom scripts."
          }
        ]
      },
      {
        "heading": "Findings",
        "level": 1,
        "content": "A total of 12 vulnerabilities were identified:",
        "table": [
          { "Severity": "Critical", "Count": "1", "Description": "SQL injection in search endpoint" },
          { "Severity": "High", "Count": "3", "Description": "XSS, IDOR, broken auth" },
          { "Severity": "Medium", "Count": "4", "Description": "CSRF, info disclosure, weak crypto, session mgmt" },
          { "Severity": "Low", "Count": "4", "Description": "Missing headers, verbose errors, outdated deps" }
        ]
      },
      {
        "heading": "Recommendations",
        "level": 1,
        "bullets": [
          "Immediate: Patch critical SQL injection vulnerability",
          "Week 1: Address all High severity findings",
          "Month 1: Remediate Medium severity issues",
          "Ongoing: Implement automated security scanning in CI/CD pipeline"
        ]
      },
      {
        "heading": "Appendices",
        "level": 1,
        "content": "Detailed vulnerability descriptions, proof-of-concept payloads, and remediation guidance are provided in the attached technical appendix."
      }
    ]
  }
}
```
