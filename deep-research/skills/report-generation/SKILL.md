---
name: report-generation
description: Report templates and generation guidelines — Executive Summary, Deep Research Report, and Comparison Table formats with methodology and citation rules. Use when formatting research results into structured reports.
---

# Report Generation

3 report templates with citation rules and mandatory Methodology section.

## Template Selection

| Research Type | Primary Template | Alternative |
|--------------|-----------------|-------------|
| Competitive Analysis | Comparison Table | Deep Research Report |
| Market Research | Deep Research Report | Executive Summary |
| Technical Audit | Deep Research Report | — |
| Person/Company Lookup | Executive Summary | — |
| Topic Deep Dive | Deep Research Report | — |
| News & Trends | Executive Summary | Deep Research Report |

## Template 1: Executive Summary

Short format for quick research and factual queries.

```markdown
# {Topic} — Executive Summary

**Date:** {YYYY-MM-DD}
**Research Depth:** {quick | standard | deep}

## Key Findings

- Finding 1 [Source](url)
- Finding 2 [Source](url)
- Finding 3 [Source](url)

## Overview

{2-3 paragraphs with main conclusions}

## Key Data Points

| Metric | Value | Source |
|--------|-------|--------|
| {metric} | {value} | [Source](url) |

## Recommendations

1. {Recommendation 1}
2. {Recommendation 2}

## Sources

1. [{Title}]({url}) — accessed {YYYY-MM-DD}
2. [{Title}]({url}) — accessed {YYYY-MM-DD}

## Methodology

- **Research type:** {type}
- **Tools used:** {list of providers}
- **Queries executed:** {count}
- **Pages analyzed:** {count}
- **Date range:** {if applicable}
```

## Template 2: Deep Research Report

Full format for in-depth research.

```markdown
# {Topic} — Deep Research Report

**Date:** {YYYY-MM-DD}
**Research Depth:** {quick | standard | deep}

## Executive Summary

{3-5 sentences with key conclusions}

## Background

{Context: why this matters, current situation}

## Findings

### {Section 1: Aspect/Angle}

{Detailed findings with inline citations [Source](url)}

### {Section 2: Aspect/Angle}

{Detailed findings}

### {Section 3: Aspect/Angle}

{Detailed findings}

## Analysis

{Cross-source analysis: patterns, trends, contradictions}

## Data & Metrics

| Metric | Value | Source | Confidence |
|--------|-------|--------|------------|
| {metric} | {value} | [Source](url) | High/Medium/Low |

## Key Quotes

> "{Quote}" — {Author/Source}, [{Link}]({url})

## Gaps & Limitations

- {What was not found}
- {Contradictory data}
- {Research limitations}

## Recommendations

1. {Recommendation 1} — rationale
2. {Recommendation 2} — rationale

## Sources

1. [{Title}]({url}) — accessed {YYYY-MM-DD}
2. [{Title}]({url}) — accessed {YYYY-MM-DD}

## Methodology

- **Research type:** {type}
- **Tools used:** {list with providers}
- **Search queries:**
  1. "{query 1}"
  2. "{query 2}"
  3. "{query 3}"
- **Pages analyzed:** {count}
- **Date of research:** {YYYY-MM-DD}
- **Limitations:** {any access issues, paywalls, blocked content}
```

## Template 3: Comparison Table

Format for competitive analysis.

```markdown
# {Item A} vs {Item B} vs {Item C} — Comparative Analysis

**Date:** {YYYY-MM-DD}

## Summary

{Brief comparison overview, 2-3 sentences}

## Feature Comparison

| Feature | {Item A} | {Item B} | {Item C} |
|---------|----------|----------|----------|
| **Price** | {value} | {value} | {value} |
| **{Feature 1}** | {value} | {value} | {value} |
| **{Feature 2}** | {value} | {value} | {value} |
| **{Feature 3}** | {value} | {value} | {value} |

## Detailed Analysis

### {Item A}

**Strengths:**
- {strength 1} [Source](url)
- {strength 2}

**Weaknesses:**
- {weakness 1}

**Best for:** {use case}

### {Item B}

**Strengths:**
- {strength 1} [Source](url)

**Weaknesses:**
- {weakness 1}

**Best for:** {use case}

### {Item C}

**Strengths / Weaknesses / Best for...**

## Verdict

Recommendation by use case:
- **For {use case 1}:** choose {Item}
- **For {use case 2}:** choose {Item}

## Sources

1. [{Title}]({url}) — accessed {YYYY-MM-DD}

## Methodology

- **Research type:** Competitive Analysis
- **Tools used:** {list}
- **Items compared:** {count}
- **Criteria evaluated:** {count}
- **Pages analyzed:** {count}
```

## Methodology Section — Required Fields

Every report MUST contain a Methodology section with:

1. **Research type** — one of 6 types
2. **Tools used** — which providers were used
3. **Search queries** — list of queries executed
4. **Pages analyzed** — number of pages read
5. **Date of research** — when research was conducted
6. **Limitations** — paywalls, blocked content, missing data

## Citation Format

### Inline citations
```
The AI code assistant market is worth $5.2B [Gartner](https://gartner.com/report)
```

### Source list
```
1. [Gartner: AI Code Assistant Market Report](https://gartner.com/report) — accessed 2026-03-16
2. [TechCrunch: The Rise of AI Coding Tools](https://techcrunch.com/article) — accessed 2026-03-16
```

### Confidence Levels
| Level | Criteria | Usage |
|-------|---------|-------|
| **High** | 3+ independent sources confirm | For facts and figures |
| **Medium** | 2 sources confirm | For estimates and forecasts |
| **Low** | 1 source or contradictory data | Must flag in text |

## Best Practices

1. **Every fact with a URL** — no exceptions
2. **Cross-check numbers** — single-source data marked as Low confidence
3. **Gaps are mandatory** — honestly state what was not found
4. **Date in every report** — research gets stale
5. **Methodology is transparent** — reader must understand how research was conducted
6. **Tables for data** — numerical comparisons always in tables
7. **Quotes for support** — direct quotes increase credibility
