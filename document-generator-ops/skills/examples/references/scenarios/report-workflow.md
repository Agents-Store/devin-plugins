# Scenario: Generating a Professional Report

End-to-end workflow for generating a quarterly performance report.

## User Request

> "Create a Q1 2026 performance report for our SaaS product. Key metrics: 15% MRR growth, 2.1% churn, NPS 72. Include methodology and recommendations."

## Step 1: CLASSIFY

Document type: **report**
Default format: **DOCX**

## Step 2: GATHER Data

Agent collects:

- Title: "Q1 2026 Performance Report"
- Subtitle: "SaaS Platform Quarterly Review"
- Author: "Analytics Team"
- Date: "2026-03-31"
- Sections: introduction, methodology, findings, analysis, conclusions, recommendations

## Step 3: SELECT

Format: DOCX (editable draft)
Script: `generate_docx.js`

## Step 4: BUILD JSON Input

```json
{
  "type": "report",
  "outputPath": "./report_q1_2026_performance_2026-03-31.docx",
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
    "title": "Q1 2026 Performance Report",
    "subtitle": "SaaS Platform Quarterly Review",
    "author": "Analytics Team",
    "date": "March 31, 2026",
    "companyName": "CloudMetrics Inc.",
    "footer": "CloudMetrics Inc. | Confidential",
    "headerText": "Q1 2026 Performance Report",
    "sections": [
      {
        "heading": "Introduction",
        "level": 1,
        "content": "This report presents a comprehensive analysis of CloudMetrics SaaS platform performance during Q1 2026 (January-March). The review covers revenue metrics, customer retention, product usage, and user satisfaction."
      },
      {
        "heading": "Methodology",
        "level": 1,
        "content": "Data was collected from three primary sources: Stripe billing API for revenue metrics, product analytics (Mixpanel) for usage data, and quarterly NPS survey (1,247 respondents, 34% response rate).\n\nAll growth metrics are calculated month-over-month unless otherwise stated. Churn is measured as logo churn (customer count), not revenue churn."
      },
      {
        "heading": "Key Findings",
        "level": 1,
        "content": "Q1 2026 showed strong growth across all primary metrics:",
        "bullets": [
          "MRR grew 15% QoQ from $820K to $943K",
          "Monthly churn rate averaged 2.1%, down from 2.8% in Q4 2025",
          "NPS score reached 72, up from 65 in Q4 2025",
          "Active daily users increased 22% to 18,400",
          "Feature adoption rate for new API v3: 41% within 6 weeks"
        ],
        "subsections": [
          {
            "heading": "Revenue Breakdown",
            "content": "Enterprise segment drove 62% of new MRR ($76K), while SMB contributed 38% ($47K). Average contract value increased 8% to $2,340/month."
          },
          {
            "heading": "Retention Analysis",
            "content": "Improved onboarding flow (launched Feb 1) correlated with 25% reduction in 30-day churn. Customers who completed onboarding had 3.2x higher 90-day retention."
          }
        ]
      },
      {
        "heading": "Analysis",
        "level": 1,
        "content": "The combination of reduced churn and increased expansion revenue indicates healthy unit economics. LTV/CAC ratio improved from 3.1 to 3.8, well above the 3.0 benchmark.",
        "table": [
          { "Metric": "MRR", "Q4 2025": "$820K", "Q1 2026": "$943K", "Change": "+15%" },
          { "Metric": "Churn Rate", "Q4 2025": "2.8%", "Q1 2026": "2.1%", "Change": "-25%" },
          { "Metric": "NPS", "Q4 2025": "65", "Q1 2026": "72", "Change": "+7pts" },
          { "Metric": "DAU", "Q4 2025": "15,100", "Q1 2026": "18,400", "Change": "+22%" },
          { "Metric": "LTV/CAC", "Q4 2025": "3.1", "Q1 2026": "3.8", "Change": "+23%" }
        ]
      },
      {
        "heading": "Conclusions",
        "level": 1,
        "content": "Q1 2026 was the strongest quarter in company history across revenue, retention, and satisfaction metrics. The onboarding improvements and API v3 launch were the primary growth drivers."
      },
      {
        "heading": "Recommendations",
        "level": 1,
        "content": "Based on Q1 data, we recommend the following priorities for Q2:",
        "bullets": [
          "Double down on enterprise sales — highest LTV segment with lowest churn",
          "Invest in API v3 documentation and developer community — 41% adoption signals strong demand",
          "Expand onboarding personalization — current improvements show clear ROI",
          "Target NPS 75+ by addressing top 3 detractor themes (page load speed, mobile app, bulk export)"
        ]
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
{ "success": true, "outputPath": "/Users/user/report_q1_2026_performance_2026-03-31.docx", "size": 52340 }
```

## Step 6: DELIVER

> Report generated successfully:
> - File: `report_q1_2026_performance_2026-03-31.docx`
> - Size: 51.1 KB
> - Format: DOCX (Microsoft Word)
> - Sections: 6 (Introduction, Methodology, Findings, Analysis, Conclusions, Recommendations)
>
> Want me to convert this to PDF for the final version?
