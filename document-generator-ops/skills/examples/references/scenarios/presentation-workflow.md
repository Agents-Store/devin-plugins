# Scenario: Creating a Presentation

End-to-end workflow for generating a product launch presentation.

## User Request

> "Make a 8-slide presentation about our new AI analytics feature launch. Include agenda, key benefits, competitive comparison, and next steps."

## Step 1: CLASSIFY

Document type: **presentation**
Default format: **PPTX**

## Step 2: GATHER Data

Agent collects:

- Title: "AI Analytics Feature Launch"
- Subtitle: "Transforming Data Into Decisions"
- Author: "Product Team"
- Date: "2026-03-18"
- Key topics: feature overview, benefits, competitive advantage, demo highlights, roadmap

## Step 3: SELECT

Format: PPTX
Script: `generate_pptx.js`

## Step 4: BUILD JSON Input

```json
{
  "outputPath": "./presentation_ai_analytics_launch_2026-03-18.pptx",
  "template": {
    "styling": {
      "primaryColor": "#003366",
      "secondaryColor": "#F59E0B",
      "fontFamily": "Calibri",
      "titleFontSize": 36,
      "bodyFontSize": 18
    }
  },
  "data": {
    "title": "AI Analytics Feature Launch",
    "subtitle": "Transforming Data Into Decisions",
    "author": "Product Team — CloudMetrics",
    "date": "March 2026",
    "slides": [
      {
        "type": "title",
        "title": "AI Analytics Feature Launch",
        "subtitle": "Transforming Data Into Decisions",
        "date": "March 2026"
      },
      {
        "type": "agenda",
        "title": "Agenda",
        "items": [
          "Why AI Analytics?",
          "Feature Overview",
          "Key Benefits",
          "Competitive Landscape",
          "Demo Highlights",
          "Roadmap & Next Steps"
        ]
      },
      {
        "type": "content",
        "title": "Why AI Analytics?",
        "bullets": [
          "78% of enterprises say data analysis is their #1 bottleneck",
          "Average analyst spends 60% of time on data prep, not insights",
          "AI can reduce time-to-insight from days to minutes",
          "Our customers asked for it — #1 feature request in 2025"
        ],
        "notes": "Cite Gartner 2025 report for the 78% stat"
      },
      {
        "type": "content",
        "title": "Feature Overview",
        "bullets": [
          "Natural language queries — ask questions in plain English",
          "Auto-generated dashboards from raw data",
          "Anomaly detection with real-time alerts",
          "Predictive forecasting (revenue, churn, usage)",
          "One-click report generation (PDF/DOCX)"
        ]
      },
      {
        "type": "two-column",
        "title": "Key Benefits",
        "left": [
          "For Analysts:",
          "10x faster ad-hoc queries",
          "No SQL required",
          "Auto-suggested visualizations",
          "Export to any format"
        ],
        "right": [
          "For Executives:",
          "Real-time KPI dashboards",
          "Natural language questions",
          "Scheduled insight emails",
          "Mobile-ready reports"
        ]
      },
      {
        "type": "content",
        "title": "Competitive Landscape",
        "bullets": [
          "Looker/Tableau: powerful but complex, requires training",
          "Mode Analytics: good for SQL users, limited AI",
          "ThoughtSpot: strong AI search, expensive ($$$)",
          "Our advantage: integrated into existing workflow, 5-min setup, 1/3 the price"
        ]
      },
      {
        "type": "summary",
        "title": "Summary & Next Steps",
        "keyPoints": [
          "AI Analytics launches April 1, 2026",
          "Available on Pro and Enterprise plans",
          "Beta users report 65% reduction in reporting time",
          "NPS among beta users: 82"
        ],
        "nextSteps": [
          "Internal training: March 25-28",
          "Beta → GA migration: April 1",
          "Customer webinar: April 3",
          "Sales enablement kit: April 7"
        ]
      },
      {
        "type": "contact",
        "name": "Product Team — CloudMetrics",
        "email": "product@cloudmetrics.io",
        "website": "cloudmetrics.io/ai-analytics"
      }
    ]
  }
}
```

## Step 5: GENERATE

```bash
cd <plugin_dir> && node scripts/generate_pptx.js /path/to/.doc_input.json
```

Output:
```json
{ "success": true, "outputPath": "/Users/user/presentation_ai_analytics_launch_2026-03-18.pptx", "size": 67230, "slides": 8 }
```

## Step 6: DELIVER

> Presentation generated successfully:
> - File: `presentation_ai_analytics_launch_2026-03-18.pptx`
> - Size: 65.7 KB
> - Format: PPTX (PowerPoint)
> - Slides: 8 (title, agenda, 4 content, summary, contact)
