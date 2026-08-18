# Scenario: Hero Images for Website

Find high-quality hero/banner images for a website using both Pexels and Unsplash.

## Goal

Find a landscape hero image for a SaaS product landing page with a "modern technology" theme.

## Step 1: Search Pexels

```
Tool: searchPhotos
Input: {
  "query": "modern technology workspace",
  "orientation": "landscape",
  "size": "large",
  "per_page": 10
}
```

Review the results. Each photo includes `src.large` (940px wide) — good for previewing — and `src.original` for production.

## Step 2: Search Unsplash

```
Tool: get_search_photos
Input: {
  "query": "modern technology workspace",
  "orientation": "landscape",
  "per_page": 10
}
```

Unsplash often returns more editorial, artistic photos. Compare with Pexels results.

## Step 3: Refine the Search

If results are too generic, add specificity:

```
Tool: searchPhotos
Input: {
  "query": "laptop desk minimal clean",
  "orientation": "landscape",
  "size": "large",
  "color": "blue",
  "per_page": 15
}
```

The `color` filter narrows results to match your brand palette.

## Step 4: Select and Use

Pick the best photo from either service. Use the appropriate size for responsive design:

```html
<picture>
  <!-- Pexels example -->
  <source media="(min-width: 1200px)" srcset="<src.large2x URL>">
  <source media="(min-width: 768px)" srcset="<src.large URL>">
  <img src="<src.medium URL>" alt="Modern workspace">
</picture>
```

```html
<picture>
  <!-- Unsplash example -->
  <source media="(min-width: 1200px)" srcset="<urls.full>">
  <source media="(min-width: 768px)" srcset="<urls.regular>">
  <img src="<urls.small>" alt="Modern workspace">
</picture>
```

## Step 5: Track Download (Unsplash Only)

If you selected an Unsplash photo, track the download:

```
Tool: get_photos_download
Input: { "id": "<selected_photo_id>" }
```

This is required by Unsplash API guidelines. Skip this step for Pexels photos.

## Tips

- Search both services for the widest selection
- Use `orientation: "landscape"` for hero images — always
- Pexels `size: "large"` pre-filters to 24MP+ photos, ensuring high resolution
- Try different search terms: "workspace", "technology", "office", "digital" yield different aesthetics
- Consider `getCuratedPhotos` or `get_photos_random` for editorial-quality alternatives
