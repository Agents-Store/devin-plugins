# Scenario: Multi-Service Content Pipeline

You're building a content aggregation system that collects articles from multiple sources, extracts key information, and imports into your CMS.

## Step 1: Discover Sources

Find relevant content sites using Exa:

```
Tool: web_search_exa
Input: {
  "query": "news sites and blogs covering web development, frameworks and tooling",
  "numResults": 20
}
```

(Inline `category:` filters on `web_search_exa` only support `company` and `people`; use the opt-in `web_search_advanced_exa` with `category: "news"` when you need a category filter.)

## Step 2: Map Each Source Site

For each relevant site, discover all article URLs:

```
Tool: firecrawl_map
Input: {
  "url": "https://techblog.example.com",
  "limit": 100,
  "search": "article"
}
```

## Step 3: Batch Read Articles

Read article content from discovered URLs (up to 5 per call; they are read concurrently):

```
Tool: read_url
Input: { "url": [
  "https://techblog.example.com/article-1",
  "https://techblog.example.com/article-2",
  "https://techblog.example.com/article-3",
  "https://techblog.example.com/article-4",
  "https://techblog.example.com/article-5"
]}
```

## Step 4: Extract Structured Data

Turn each article into structured data for your CMS (one scrape per URL):

```
Tool: firecrawl_scrape
Input: {
  "url": "<article_url>",
  "formats": ["json"],
  "jsonOptions": {
    "prompt": "Extract article title, author, publication date, main content, tags/categories, and featured image URL",
    "schema": {
      "type": "object",
      "properties": {
        "title": { "type": "string" },
        "author": { "type": "string" },
        "date": { "type": "string" },
        "content": { "type": "string" },
        "tags": { "type": "array", "items": { "type": "string" } },
        "image": { "type": "string" }
      }
    }
  }
}
```

## Step 5: Classify and Categorize

Jina's MCP server has no classification tool. Let the model assign each article one of your app's categories (`frontend`, `backend`, `devops`, `ai-ml`, `mobile`, `security`) while it processes the extracted JSON — or add a `category` enum to the extraction schema in Step 4. For high-volume pipelines outside Claude, call Jina's REST classifier (see `api-reference`).

## Step 6: Deduplicate

Remove duplicate articles (from overlapping sources):

```
Tool: deduplicate_strings
Input: {
  "strings": ["<article_titles>"]
}
```

## Step 7: Rerank by Relevance

Prioritize the most relevant articles for your audience:

```
Tool: sort_by_relevance
Input: {
  "query": "practical web development tutorials and guides",
  "documents": ["<article_summaries>"]
}
```

## Step 8: Find Featured Images

For articles missing images, find stock photos with the Pexels REST API (see `media-search`):

```bash
curl -s -H "Authorization: ${PEXELS_API_KEY}" \
  "https://api.pexels.com/v1/search?query=<article_topic>&orientation=landscape&per_page=3"
```

Keep `photographer` and `url` with the article record — the Pexels link and photographer credit are required on display.

## Step 9: Import to CMS

```typescript
// Transform and upload to your CMS
for (const article of processedArticles) {
  await cms.createItem('articles', {
    title: article.title,
    content: article.content,
    category: article.classification,
    featured_image: article.image || stockImage,
    published_at: article.date,
    tags: article.tags,
    source_url: article.url,
  });
}
```

## Pipeline Summary

```
Discover sources (Exa)
  → Map site URLs (Firecrawl)
    → Batch read content (Jina read_url, 5 URLs per call)
      → Extract structured data (Firecrawl scrape, json format)
        → Classify (model / schema enum)
          → Deduplicate (Jina)
            → Rerank (Jina)
              → Find missing images (Pexels REST)
                → Import to CMS
```

## Tips

- Run the pipeline in batches to manage rate limits
- Cache intermediate results — don't re-scrape on retry
- Log which articles were imported and their source URLs
- Schedule the pipeline to run periodically for fresh content
- Add a review step before publishing if content quality varies
