# Scenario: Multi-Service Content Pipeline

You're building a content aggregation system that collects articles from multiple sources, extracts key information, and imports into your CMS.

## Step 1: Discover Sources

Find relevant content sites using Exa:

```
Tool: web_search_exa
Input: {
  "query": "category:news best tech blogs and news sites about web development",
  "numResults": 20
}
```

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

Read article content from discovered URLs:

```
Tool: parallel_read_url
Input: { "urls": [
  "https://techblog.example.com/article-1",
  "https://techblog.example.com/article-2",
  "https://techblog.example.com/article-3",
  "https://techblog.example.com/article-4",
  "https://techblog.example.com/article-5"
]}
```

## Step 4: Extract Structured Data

Turn articles into structured data for your CMS:

```
Tool: firecrawl_extract
Input: {
  "urls": ["<article_urls>"],
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
```

## Step 5: Classify and Categorize

Use Jina to classify articles into your app's categories:

```
Tool: classify_text
Input: {
  "texts": ["<article_titles_or_summaries>"],
  "labels": ["frontend", "backend", "devops", "ai-ml", "mobile", "security"]
}
```

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

For articles missing images, find stock photos:

```
Tool: searchPhotos
Input: {
  "query": "<article_topic>",
  "orientation": "landscape",
  "per_page": 3
}
```

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
    → Batch read content (Jina parallel)
      → Extract structured data (Firecrawl)
        → Classify (Jina)
          → Deduplicate (Jina)
            → Rerank (Jina)
              → Find missing images (Pexels)
                → Import to CMS
```

## Tips

- Run the pipeline in batches to manage rate limits
- Cache intermediate results — don't re-scrape on retry
- Log which articles were imported and their source URLs
- Schedule the pipeline to run periodically for fresh content
- Add a review step before publishing if content quality varies
