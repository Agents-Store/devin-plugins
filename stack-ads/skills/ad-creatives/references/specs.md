# Creative specifications: images, video, logos

Pixel sizes, aspect ratios, safe zones, file limits and asset counts for Google Ads, Meta and TikTok, checked 2026-11-14. Use it to choose what to generate, to size it, and to verify files before upload.

## Contents

- Master sizes and toolkit values
- Google Ads
- Meta
- TikTok
- Video length bands
- Pre-upload checklist

## Master sizes and toolkit values

The toolkit `image` command takes `--aspect 1:1|4:5|9:16|16:9|1.91:1` or `--size WxH`; `video` takes `--aspect 9:16|16:9|1:1`, `--seconds N` and `--resolution 720p|1080p`. Video has no 4:5 option: for a 4:5 slot use the 9:16 or 1:1 video.

| # | File (pixels) | Ratio | Type | Serves | Toolkit values |
|---|---|---|---|---|---|
| 1 | 1080x1920 (Meta export 1440x2560) | 9:16 | video, image | Meta Stories, Reels, Instagram Feed video, Threads, WhatsApp Status (720x1280 recommended), Audience Network; Google YouTube Shorts, vertical video in Performance Max and Demand Gen; TikTok In-Feed, Spark, TopView | image `--aspect 9:16 --size 1080x1920`; video `--aspect 9:16 --resolution 1080p` |
| 2 | 1440x1800 (floor 1080x1350) | 4:5 | image | Meta Facebook Feed, Instagram Feed, right column (mobile), Threads; Google 4:5 image in Performance Max and Demand Gen (960x1200 recommended) | image `--aspect 4:5 --size 1440x1800` |
| 3 | 1080x1080 (1440x1440 for Threads, right column) | 1:1 | image, video | Meta Marketplace, carousel, Reels overlay, in-stream, Threads; Google square in Performance Max, Demand Gen, display, Search; TikTok In-Feed square | image `--aspect 1:1 --size 1080x1080`; video `--aspect 1:1 --resolution 1080p` |
| 4 | 1200x628 | 1.91:1 | image | Google Performance Max, Demand Gen, display, Search image asset; Meta landscape feed (Instagram Feed accepts up to 1.91:1) | image `--aspect 1.91:1 --size 1200x628` |
| 5 | 1920x1080 | 16:9 | video | Google YouTube in-stream, in-feed, display video; Meta Facebook in-stream (16:9 or 1:1); TikTok horizontal In-Feed | video `--aspect 16:9 --resolution 1080p` |
| 6 | 1200x1200 | 1:1 | logo | Google business logo (Performance Max, Demand Gen, display, Search) | image `--size 1200x1200` (take the logo from the vector source, do not generate it) |
| 7 | 1200x300 | 4:1 | logo | Google horizontal logo (Performance Max, display) | image `--size 1200x300` |
| 8 | 98x98, key art inside centre 66x66 | 1:1 | profile image | TikTok display profile | resize the logo; not a toolkit generation |

Meta Page and Instagram profile pictures are set on the Page or profile, not as ad assets. Meta recommends 1440-wide files; 1080-wide is the stated floor on several placements.

## Google Ads

Official: https://support.google.com/google-ads/answer/17091269

### Performance Max asset group

| Asset | Recommended | Minimum | Count | Required |
|---|---|---|---|---|
| Image 1.91:1 | 1200x628 | 600x314 | 4+ recommended, up to 20 | yes |
| Image 1:1 | 1200x1200 | 300x300 | 4+ recommended, up to 20 | yes |
| Image 4:5 | 960x1200 | 480x600 | 2+ recommended, up to 20 | no |
| Logo 1:1 | 1200x1200 | 128x128 | 1 (up to 5) | yes |
| Logo 4:1 | 1200x300 | 512x128 | 1 (up to 5) | no |
| Video 16:9, 1:1, 9:16 | HD | 10 s or more, no maximum stated | up to 15 videos; one per orientation recommended | no |

Without videos Google may auto-generate them from the asset group; upload all three orientations to prevent that and to reach "Excellent" Ad Strength. A vertical video of 10 - 60 s is needed for Shorts. A retail asset group with a Merchant Center feed attached does not need these minimum assets. Images .jpg or .png, 5,120 KB maximum; a transparent logo may render on white.

### Demand Gen

| Asset | Recommended | Minimum | Count | Required |
|---|---|---|---|---|
| Image 1.91:1 | 1200x628 | 600x314 | 1 - 20 (3 recommended) | yes |
| Image 1:1 | 1200x1200 | 300x300 | 1 - 20 (3 recommended) | yes |
| Image 4:5 | 960x1200 | 480x600 | 1 - 20 (3 recommended) | no |
| Logo 1:1 | 1200x1200 | 144x144 | 1 - 5 (1 recommended) | yes |
| Video 16:9, 9:16 or 4:5, 1:1 | 1920x1080, 1080x1920, 1080x1080 | 5 s (under 10 s is ineligible for in-stream) | up to 3 per orientation; 10 - 60 s recommended | no |
| Carousel | one image per card, same ratio on all cards | - | 2 - 10 cards | no |

A Demand Gen carousel is unavailable with a Merchant Center product feed. The logo shows cropped about 21.46 percent when displayed as a circle in Gmail: keep the mark centred.

### Search, display and other image assets

| Asset | Value |
|---|---|
| Search image, square | 1:1, 1200x1200 recommended, min 300x300, 1 - 20 |
| Search image, horizontal | 1.91:1, 1200x628 recommended, min 600x314, 1 - 20 |
| Business logo (Search) | 1:1, 1200x1200 recommended, min 128x128, 1 required; PNG or JPG, 5,120 KB maximum; must work on light and dark backgrounds |
| Safe area for Search images and logos | keep key content in the central 80 percent |
| Responsive display ad images | 1.91:1 1200x628 (min 600x314), 1 - 15, 5 recommended; 1:1 600x600 recommended (min 300x300), 1 - 15; logos 1:1 1200x1200 (min 128x128) and 4:1 1200x300 (min 512x128), 1 - 5 |
| Responsive display ad video | 16:9, 1:1 or 2:3, any length, 30 s preferred, 1 - 5 |
| Uploaded display images | GIF, JPG, PNG, 150 KB maximum; GIF animation up to 30 s and under 5 fps; sizes include 300x250, 336x280, 728x90, 970x90, 970x250, 160x600, 300x600, 320x50, 320x100 |
| HTML5 display | ZIP, 600 KB maximum, 40 files maximum, file name 50 characters or less |

### YouTube video

| Item | Value |
|---|---|
| Resolutions | recommended 1920x1080, 1080x1920, 1080x1080; accepted minimums 1280x720, 720x1280, 480x480; 4:3, 2:3 and 4:5 also accepted |
| File | MPG recommended; MP4, MOV, WMV, AVI, FLV, WebM, HEVC and others accepted; under 256 GB; audio-only not accepted |
| Skippable in-stream | any length; skip after 5 s; counts as a view above 10 s |
| Non-skippable in-stream | 7 - 15 s (16 - 30 s on connected TV); 6 s or less runs as a bumper (sources disagree on the exact range) |
| Bumper | up to 6 s |
| In-feed | 15 s recommended |
| Shorts | 9:16, under 60 s recommended (6 - 60 s) |
| Thumbnail | 1280x720 (min 1280x640), JPG, GIF or PNG, under 2 MB |
| Companion banner | 300x60, under 150 KB |
| Shorts safe-zone pixel margins | unverified: keep captions and logos away from every edge |

## Meta

Official: https://www.facebook.com/business/ads-guide

Image files are JPG or PNG up to 30 MB; video files are MP4, MOV or GIF up to 4 GB.

| Placement | Format | Ratio | Recommended | Minimum, tolerance | Duration |
|---|---|---|---|---|---|
| Facebook Feed | image | 4:5 | 1440x1800 | width 600, height 750; tolerance 3% | - |
| Facebook Feed | video | 4:5 or 1:1 | - | 120x120 | 1 s - 241 min |
| Facebook Feed carousel | 2 - 10 cards | 1:1 | 1080x1080 or larger | tolerance 3% | video 1 s - 240 min |
| Instagram Feed | image | 4:5 (accepts 1.91:1 to 4:5) | 1440x1800 | width 500; tolerance 1% | - |
| Instagram Feed | video | 9:16 (accepts 1.91:1 to 9:16) | 1080x1920 | width 250 | 1 s - 60 min |
| Instagram Stories | image, video | 9:16 | 1080x1920 | width 500 (image), 250 (video) | video: cap at 60 s (page says 1 s - 60 min) |
| Facebook Stories | video | 9:16 | 1440x2560 | width 250 | 1 s - 3 min |
| Instagram Reels | video MP4, MOV | 9:16 | 1440x2560 | width 250 (under 30 s), 500 (30 s or more) | 0 s - 15 min |
| Facebook Reels | video | 9:16 | 1440x2560 | - | no maximum |
| Facebook Reels overlay | image | 1:1 | 1080x1080 or larger | 300x300; tolerance 0% | - |
| Facebook in-stream | video | 16:9 or 1:1 | 1080x1080 or larger | - | desktop 5 - 15 s; mobile 5 s - 10 min |
| Marketplace | image | 1:1 | 1080x1080 or larger | - | - |
| Facebook right column | image, video | 1:1 (desktop and mobile), 4:5 (mobile) | 1440x1440, 1440x1800 | 120x120 | image specs unverified |
| Lead ads with instant form | image | 1:1 or 4:5 | 1080x1080, 1080x1350 | - | - |
| Threads | image, video, carousel 2 - 10 | 1.91:1 to 9:16 (taller than 4:5 is cropped to 4:5) | 1440x1440 image, 1440x1800 video | width 500 or not delivered | video max 500 s; no captions |
| WhatsApp Status | image, video | any ratio below 1.91:1 (9:16 is the Status format) | 720x1280 | image 500x320, video 120x120 | not published |

Reels encoding: H.264, square pixels, fixed frame rate, progressive scan, AAC stereo at 128 kbps or more.

Carousel: keep one ratio across cards, 1:1 or 4:5 for images; 4:5 only for Advantage+ catalog carousels.

Safe zones (9:16 Stories, Reels, in-stream): keep text, logos and key elements out of the top 14 percent, the bottom 35 percent and 6 percent on each side. Reels ads with a disclaimer: keep the bottom 40 percent free. For 1:1 and 4:5 Instagram Feed: keep bottom and side edges free of key elements (no percentage published).

Reels exclusions: licensed music, reels published before 2021-10-15, face or camera effects, GIFs, product tags, files with edit lists. Meta may auto-apply templates to non-9:16 media in Reels; upload 9:16 or pick "No template" to avoid it. Advantage+ creative enhancements (video touch-ups, visual touch-ups, overlays, music) can change the delivered media; disable them per ad when the image must stay as designed.

## TikTok

Official: https://ads.tiktok.com/resources/help/article/tiktok-auction-in-feed-ads

| Buying type | Ratio, minimum resolution | Duration | File | Formats |
|---|---|---|---|---|
| In-Feed auction (non-Spark) | 9:16 540x960 or larger (recommended); 16:9 960x540; 1:1 640x640 | up to 10 min | 500 MB maximum, bitrate 516 kbps or more | MP4, MOV, MPEG, 3GP, AVI |
| Spark Ads (from an organic post) | no ratio, resolution or size restriction | 10 min maximum | - | MP4, MOV |
| TopView | 9:16 only, 540x960 or larger | 5 - 60 s, 9 - 15 s recommended | 500 MB maximum, 2,500 kbps or more | MP4, MOV, MPEG, 3GP |
| Reservation in-feed, Reach and Frequency, Pulse | 9:16, 16:9 or 1:1 as above | 5 - 60 s, 9 - 15 s recommended | 500 MB maximum, 2,500 kbps or more | MP4, MOV, MPEG, 3GP |

Safe default: encode every TikTok video as 1080x1920, 5 - 60 s, 2,500 kbps or more, 500 MB or less, MP4 (an older preview tool quotes 350 kbps; sources disagree, so use the higher figure). Codec, frame-rate and safe-zone pixel margins are unverified; the safe zone shrinks with caption length and interactive add-ons, and TopView has a 3-second open-screen stage, so keep key content in the centre.

| Item | Value |
|---|---|
| Image carousel | 2 - 35 images; JPG, JPEG, PNG; about 100 KB suggested; horizontal 1200x628, square 640x640, vertical 720x1280; one caption, call to action and URL for all cards |
| Carousel music | required (loops, 2 s or more; Commercial Music Library or an MP3 up to 10 MB); not supported with Spark Ads |
| Image ads, preview-tool limit | JPG, JPEG, PNG, up to 100 MB |
| Profile image | 98x98 px, 1:1, JPG, JPEG or PNG, under 50 KB, key element in the centre 66x66; Spark Ads use the account's own profile photo |
| TopView rules | not silent, no plain white or harsh noise in the first 3 s, no QR codes, contact numbers or addresses, stills cannot carry the main narrative |

## Video length bands

| Band | Use |
|---|---|
| 5 - 6 s | Google bumper (6 s); Meta in-stream desktop minimum 5 s; TikTok minimum for TopView and reservation (5 s) |
| 9 - 15 s | TikTok recommended; Google skippable in-stream and in-feed 15 s |
| 10 - 60 s | Google Performance Max (10 s minimum) and Demand Gen (10 - 60 s); Shorts 6 - 60 s; TikTok reservation maximum 60 s |
| 30 - 60 s | extended cut for YouTube and Meta Feed |
| Upper limits | Facebook Stories 3 min; TikTok In-Feed 10 min; Instagram Reels 15 min; Instagram Feed and Stories 60 min |
| File size caps | Meta 4 GB; TikTok 500 MB; Google 256 GB; keep video at 500 MB or less to satisfy all three |

Plan one master video cut at 15 s, a 6 s bumper cut and a 30 - 60 s extended cut. One generation call gives at most 15 s on Gemini; a longer cut is several clips joined with `ffmpeg`, or a fal.ai model that offers the length, and every clip falls under the cost rule of the skill.

## Pre-upload checklist

1. Each file matches a row in the master table: pixel size, ratio and format; images are JPG or PNG, video is MP4.
2. Images are 5 MB or less (Google limit); video is 500 MB or less; TikTok video bitrate is 2,500 kbps or more.
3. Logos: 1200x1200 and 1200x300 for Google, 98x98 for TikTok; the mark stays inside the central 80 percent.
4. Text and logos sit inside the safe zones. Meta publishes them for 9:16: 14 percent top, 35 percent bottom, 6 percent sides, and the bottom 40 percent free for Reels with a disclaimer. TikTok and Shorts publish no figures: apply Meta's as a cautious default.
5. Performance Max has 4 images at 1.91:1, 4 at 1:1, 1 logo, and videos in 3 orientations; Demand Gen has 1 image per required ratio and a 144x144 logo or larger.
6. Video lengths fit the placement: 10 s or more for Performance Max, 5 - 60 s for TikTok TopView, 6 s or less for a bumper.
7. Meta Reels files contain original sound only (generated or owned outright, no licensed commercial track), no GIF, no product tag; TikTok videos use sound the advertiser holds the rights to or a track from the Commercial Music Library.
8. AI-generated media carries the disclosure the platform requires (TikTok toggle; Google and Meta labels where they apply).
9. No placeholder text, watermark or competitor mark remains; the file names are unique.
