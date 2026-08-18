# Scenario: Person/Company Lookup

**Query:** "Кто такой Anthropic — история, продукты, команда"
**Type:** Person/Company Lookup
**Depth:** standard
**Template:** Executive Summary

## Step-by-Step Execution

### Step 1: CLASSIFY
```
Signals: "кто такой", company name → Person/Company Lookup
Depth: standard
```

### Step 2: PLAN — Exhaustive Discovery Protocol FIRST
```
DISCOVERY — probe direct URLs in parallel:
- ~~scrape("https://anthropic.com")
- ~~scrape("https://anthropic.ai")
- ~~scrape("https://anthropic.dev")
- ~~scrape("https://anthropic.io")
- ~~scrape("https://github.com/anthropics")
- ~~scrape("https://github.com/anthropics/anthropic-sdk-python")
- ~~scrape("https://docs.anthropic.com")

→ Found: anthropic.com (main site), docs.anthropic.com, github.com/anthropics

Then generate search queries:
1. "Anthropic company overview history"
2. "Anthropic founders team leadership"
3. "Anthropic products Claude AI models"
4. "Anthropic funding valuation investors"
5. "Anthropic AI safety research mission"
```

### Step 3: SEARCH
```
~~search("Anthropic company overview products team")
→ Exa with company category filter

~~search("Anthropic company history funding products team 2026")
→ Perplexity AI answer with key facts

~~search("Anthropic AI safety research Claude models")
```

### Step 4: READ
```
~~batch_scrape([
  "https://anthropic.com/company",       ← from discovery
  "https://anthropic.com/research",       ← from discovery
  "https://docs.anthropic.com",           ← from discovery
  top_crunchbase_url,
  top_news_article_url
])
```

### Step 5: EXTRACT
```
Key data points:
- Founded: date, location
- Founders: names, backgrounds
- Mission: AI safety focus
- Products: Claude models, API
- Funding: rounds, amounts, investors
- Team size
- Key milestones
```

### Step 6: SYNTHESIZE
```
Cross-check funding data across Crunchbase and news
Verify team info across multiple sources
Timeline of key events
```

### Step 7: REPORT
Output: Executive Summary with:
- Key Findings (5 bullet points)
- Overview (founding, mission, growth)
- Key Data Points table (funding, team, products)
- Timeline of milestones
- Sources (5+ URLs)
- Methodology

### Expected Capabilities Used
`~~scrape` (discovery), `~~search`, `~~batch_scrape`
