# Presentation JSON Input Example

Complete example of JSON input for `generate_pptx.js` to create a professional presentation.

## Minimal Presentation

```json
{
  "outputPath": "./presentation_overview_2026-03-18.pptx",
  "data": {
    "title": "Company Overview",
    "author": "CEO",
    "slides": [
      { "type": "title", "title": "Company Overview", "subtitle": "Q1 2026" },
      { "type": "content", "title": "Our Mission", "bullets": ["Build great products", "Serve customers", "Grow sustainably"] },
      { "type": "summary", "title": "Summary", "keyPoints": ["Revenue up 20%", "Team doubled"], "nextSteps": ["Hire 10 more", "Launch v2"] }
    ]
  }
}
```

## Full Presentation (8 slides, all types)

```json
{
  "outputPath": "./presentation_investor_pitch_2026-03-18.pptx",
  "template": {
    "styling": {
      "primaryColor": "#003366",
      "secondaryColor": "#F59E0B",
      "backgroundColor": "#FFFFFF",
      "fontFamily": "Calibri",
      "titleFontSize": 36,
      "bodyFontSize": 18
    }
  },
  "data": {
    "title": "Series A Investor Pitch",
    "subtitle": "CloudMetrics — AI-Powered Analytics",
    "author": "Alex Chen, CEO",
    "date": "March 2026",
    "slides": [
      {
        "type": "title",
        "title": "CloudMetrics",
        "subtitle": "AI-Powered Analytics for Modern Teams",
        "date": "Series A — March 2026"
      },
      {
        "type": "agenda",
        "title": "What We'll Cover",
        "items": [
          "The Problem",
          "Our Solution",
          "Traction & Metrics",
          "Business Model",
          "Go-to-Market",
          "The Ask"
        ]
      },
      {
        "type": "content",
        "title": "The Problem",
        "bullets": [
          "$200B+ spent annually on business intelligence tools",
          "Average time to create a dashboard: 3 weeks",
          "85% of data projects fail to deliver actionable insights",
          "Existing tools require SQL expertise — only 5% of employees"
        ],
        "notes": "Emphasize the massive market opportunity and the skills gap"
      },
      {
        "type": "content",
        "title": "Our Solution",
        "bullets": [
          "Natural language interface — ask questions in plain English",
          "Auto-generated dashboards in seconds, not weeks",
          "AI anomaly detection — get alerts before problems escalate",
          "One-click reports — export to PDF, DOCX, PPTX",
          "5-minute setup — connect your data, start asking questions"
        ]
      },
      {
        "type": "two-column",
        "title": "Traction & Metrics",
        "left": [
          "Revenue:",
          "ARR: $11.3M",
          "MRR: $943K",
          "Growth: 15% QoQ",
          "Net Revenue Retention: 135%"
        ],
        "right": [
          "Customers:",
          "450+ paying customers",
          "18,400 daily active users",
          "NPS: 72",
          "Logo churn: 2.1%/mo"
        ]
      },
      {
        "type": "chart",
        "title": "Revenue Growth",
        "chartType": "bar",
        "chartData": [
          {
            "name": "MRR ($K)",
            "labels": ["Q2'25", "Q3'25", "Q4'25", "Q1'26"],
            "values": [580, 690, 820, 943]
          }
        ],
        "notes": "Highlight the acceleration in Q1"
      },
      {
        "type": "summary",
        "title": "The Ask",
        "keyPoints": [
          "Raising $15M Series A",
          "Use of funds: 60% R&D, 25% Sales, 15% G&A",
          "Target: 1,000 customers by EOY 2026",
          "Path to $30M ARR in 18 months"
        ],
        "nextSteps": [
          "Follow-up meeting with CTO for tech deep-dive",
          "Customer reference calls available",
          "Data room access upon request"
        ]
      },
      {
        "type": "contact",
        "name": "Alex Chen, CEO",
        "email": "alex@cloudmetrics.io",
        "phone": "+1 (415) 555-0192",
        "website": "cloudmetrics.io"
      }
    ]
  }
}
```
