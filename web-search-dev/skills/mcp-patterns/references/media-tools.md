# Media Search — Pexels and Unsplash REST

Neither Pexels nor Unsplash publishes an official MCP server, and community servers name their tools differently from each other. This plugin therefore documents the **public REST APIs**, called with `curl` (or any HTTP client). No MCP configuration is needed — only API keys in the environment:

| Variable | Service | Get a key |
|----------|---------|-----------|
| `PEXELS_API_KEY` | Pexels | https://www.pexels.com/api/ (instant, free) |
| `UNSPLASH_ACCESS_KEY` | Unsplash | https://unsplash.com/developers (create an app; keep the Secret Key private) |

Both keys are optional — the plugin works without them (use Jina `search_images` with `"return_url": true` for web images).

| | Pexels | Unsplash |
|--|--------|----------|
| Content | Photos **and videos** | Photos only |
| Base URL | `https://api.pexels.com` | `https://api.unsplash.com` |
| Auth header | `Authorization: ${PEXELS_API_KEY}` | `Authorization: Client-ID ${UNSPLASH_ACCESS_KEY}` |
| Rate limit | 200 req/hour and 20 000 req/month (higher limits on request through Pexels API support) | demo 50 req/hour; production 1 000 req/hour (after approval) |
| Per page | default 15, max 80 | default 10, max 30 |
| Orientation values | `landscape`, `portrait`, `square` | `landscape`, `portrait`, `squarish` |
| Re-hosting images | Allowed by the Pexels license | **Not allowed** — hotlink `photo.urls.*` |

Both APIs return rate-limit headers on success (`X-Ratelimit-Limit`, `X-Ratelimit-Remaining`; Pexels also `X-Ratelimit-Reset`). On `429`, back off and cache results.

## Pexels

All endpoints take the key in the `Authorization` header without a `Bearer` prefix. **Video endpoints live under `/v1/videos/`** — the old `/videos/` prefix is being retired.

| Endpoint | Purpose |
|----------|---------|
| `GET /v1/search` | Search photos |
| `GET /v1/curated` | Editorially curated photos |
| `GET /v1/photos/:id` | One photo |
| `GET /v1/videos/search` | Search videos |
| `GET /v1/videos/popular` | Popular videos |
| `GET /v1/videos/videos/:id` | One video |
| `GET /v1/collections/featured` | Featured collections |
| `GET /v1/collections` | The key owner's collections |
| `GET /v1/collections/:id` | Media in a collection (`type` = `photos` or `videos`, `sort` = `asc` or `desc`) |

### Search photos — `GET /v1/search`

| Parameter | Description |
|-----------|-------------|
| `query` | Search terms (required) |
| `orientation` | `landscape`, `portrait`, `square` |
| `size` | Minimum size: `large` (24 MP), `medium` (12 MP), `small` (4 MP) |
| `color` | `red`, `orange`, `yellow`, `green`, `turquoise`, `blue`, `violet`, `pink`, `brown`, `black`, `gray`, `white`, or a hex code such as `#ffffff` |
| `locale` | Language of the query: `en-US`, `pt-BR`, `es-ES`, `ca-ES`, `de-DE`, `it-IT`, `fr-FR`, `sv-SE`, `id-ID`, `pl-PL`, `ja-JP`, `zh-TW`, `zh-CN`, `ko-KR`, `th-TH`, `nl-NL`, `hu-HU`, `vi-VN`, `cs-CZ`, `da-DK`, `fi-FI`, `uk-UA`, `el-GR`, `ro-RO`, `nb-NO`, `sk-SK`, `tr-TR`, `ru-RU` |
| `page`, `per_page` | Pagination (default 1 / 15, max 80) |

```bash
curl -s -H "Authorization: ${PEXELS_API_KEY}" \
  "https://api.pexels.com/v1/search?query=office&per_page=5&orientation=landscape&locale=en-US"
```

Use `locale` for non-English queries (for example `locale=ru-RU` with a Russian `query`) instead of translating them first.

Response: `{ page, per_page, total_results, photos: [...] }`. Each photo has `id`, `width`, `height`, `url` (Pexels page), `photographer`, `photographer_url`, `avg_color`, `alt`, and `src` with `original`, `large2x`, `large`, `medium`, `small`, `portrait`, `landscape`, `tiny`.

### Search videos — `GET /v1/videos/search`

Parameters: `query` (required), `orientation`, `size` (`large` = 4K, `medium` = Full HD, `small` = HD), `locale`, `page`, `per_page`.

```bash
curl -s -H "Authorization: ${PEXELS_API_KEY}" \
  "https://api.pexels.com/v1/videos/search?query=ocean&per_page=3&orientation=landscape&size=medium"
```

Response: `videos[]` with `id`, `width`, `height`, `duration`, `url`, `user`, `video_files[]` (`id`, `quality`, `file_type`, `width`, `height`, `link`) and `video_pictures[]`.

### Popular videos — `GET /v1/videos/popular`

Parameters: `min_width`, `min_height`, `min_duration`, `max_duration` (seconds), `page`, `per_page`. Only this endpoint filters by resolution and duration (the search endpoint does not).

```bash
curl -s -H "Authorization: ${PEXELS_API_KEY}" \
  "https://api.pexels.com/v1/videos/popular?min_width=1920&max_duration=20&per_page=10"
```

### Curated photos, single items, collections

```bash
curl -s -H "Authorization: ${PEXELS_API_KEY}" "https://api.pexels.com/v1/curated?per_page=20"
curl -s -H "Authorization: ${PEXELS_API_KEY}" "https://api.pexels.com/v1/photos/2014422"
curl -s -H "Authorization: ${PEXELS_API_KEY}" "https://api.pexels.com/v1/videos/videos/<video_id>"
curl -s -H "Authorization: ${PEXELS_API_KEY}" "https://api.pexels.com/v1/collections/featured?per_page=10"
curl -s -H "Authorization: ${PEXELS_API_KEY}" "https://api.pexels.com/v1/collections/<collection_id>?type=photos&sort=desc&per_page=20"
```

### Pexels guidelines

- Show a **prominent link to Pexels** wherever API content appears ("Photos provided by Pexels").
- Credit photographers when possible: "Photo by <photographer> on Pexels", linking to `photo.url` / `photographer_url`.
- Do not copy or replicate core Pexels functionality (for example a wallpaper app), and do not work around the rate limit.

## Unsplash

All requests send `Authorization: Client-ID ${UNSPLASH_ACCESS_KEY}`. Add `Accept-Version: v1` to pin the API version.

| Endpoint | Purpose |
|----------|---------|
| `GET /search/photos` | Search photos |
| `GET /photos/random` | Random photos (`query`, `orientation`, `count` up to 30) |
| `GET /photos/:id` | One photo |
| `GET /photos/:id/download` | Download tracking event (normally call `photo.links.download_location` instead) |

### Search photos — `GET /search/photos`

| Parameter | Description |
|-----------|-------------|
| `query` | Search terms (required) |
| `page`, `per_page` | Pagination (default 1 / 10, max 30) |
| `order_by` | `relevant` (default) or `latest` |
| `orientation` | `landscape`, `portrait`, `squarish` |
| `color` | `black_and_white`, `black`, `white`, `yellow`, `orange`, `red`, `purple`, `magenta`, `green`, `teal`, `blue` |
| `content_filter` | `low` (default) or `high` |
| `collections` | Comma-separated collection ids |

```bash
curl -s -H "Authorization: Client-ID ${UNSPLASH_ACCESS_KEY}" \
  "https://api.unsplash.com/search/photos?query=office&per_page=5&orientation=landscape"
```

Response: `{ total, total_pages, results: [...] }`. Each photo has `id`, `width`, `height`, `alt_description`, `urls` (`raw`, `full`, `regular`, `small`, `thumb`, plus `urls.custom` when you request a custom width), `user` (`name`, `username`, `links.html`) and `links` (`html`, `download`, `download_location`).

### Track the download

When the user chooses a photo for use (inserting it in a post, setting it as a header, ...), send a request to the photo's own `download_location` URL. Keep every query parameter in it (such as `ixid`) and authorize the call, otherwise it returns `401`:

```bash
curl -s -H "Authorization: Client-ID ${UNSPLASH_ACCESS_KEY}" "<photo.links.download_location>"
```

Fire it asynchronously so it never slows the user down. It is an event endpoint only — never embed the photo from it; use `photo.urls.*` for display.

### Unsplash API checklist (all API uses)

1. **Hotlink** the images from `photo.urls.*` for every display — search results and final use alike. **Never download and re-upload Unsplash photos to your own storage or CDN** (the "download to MinIO / S3" workflow is for Pexels only). Resize with the documented URL parameters (`w`, `h`, `fit`, `q`), not by copying.
2. **Trigger the download** by calling `photo.links.download_location` whenever the photo is actually used.
3. **Attribute** Unsplash and the photographer, each linked, with UTM parameters:
   `Photo by <a href="https://unsplash.com/@<username>?utm_source=<app_name>&utm_medium=referral"><name></a> on <a href="https://unsplash.com/?utm_source=<app_name>&utm_medium=referral">Unsplash</a>`
4. **Keep the Access Key and Secret Key confidential** — proxy requests through your backend instead of calling the API from the browser.
5. Do not use the Unsplash name or logo as your app name or icon, do not sell unaltered photos, and do not replicate the Unsplash experience (wallpaper apps, unofficial clients).
6. Do not abuse the API; Unsplash expects non-automated, authentic use. Apply for production access (Developer dashboard → Your Apps) before launch — demo apps are limited to 50 req/hour.

Licence note: the Unsplash License itself does not require attribution, but API use does (item 3 above).

## Web images (any site)

For design inspiration or images that stock sites do not have, use Jina `search_images` with `"return_url": true` (see `jina-tools.md`). Licences vary by source — check each one before using an image commercially.
