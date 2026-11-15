# Ad copy limits and editorial rules

Every text limit and rejection rule for Google Ads, Meta and TikTok ad copy, checked 2026-11-14. Count characters before handing copy to the launcher; a limit that is exceeded makes the API call fail or the text get cut.

## Contents

- Counting rules
- Google Ads: Search (RSA), Performance Max, Demand Gen, Display, video
- Google Ads: Search-side assets
- Google Ads: editorial rules
- Meta: text fields by placement
- Meta: editorial rules
- TikTok: text fields, call-to-action lists, rules
- Copy pack per platform

## Counting rules

| Rule | Value |
|---|---|
| Google, Korean / Japanese / Chinese | every character counts as 2 against the limit (sitelink and callout: 12 characters instead of 25) |
| TikTok, full-width CJK and emoji | each counts as 2 |
| TikTok, display name for CN / JP / KR | 10 instead of 20 |
| Meta | no double-width rule found in the notes; count characters |
| Safe default | write every text asset to the strictest limit of its field, then reuse it across formats |

## Google Ads: Search (RSA), Performance Max, Demand Gen, Display, video

Official: https://support.google.com/google-ads/answer/17092074 (Search), https://support.google.com/google-ads/answer/17091269 (Performance Max).

| Format | Field | Count (min - max) | Max length |
|---|---|---|---|
| RSA | Headline | 3 - 15 | 30 |
| RSA | Description | 2 - 4 | 90 |
| RSA | Display path 1 and 2 | 0 - 2 | 15 each |
| RSA | Final URL | 1 | 2,048 |
| Performance Max | Headline (at least one of 15 characters or less) | 3 - 15 (11+ recommended) | 30 |
| Performance Max | Long headline | 1 - 5 (2+ recommended) | 90 |
| Performance Max | Description | 2 - 5 (4+ recommended) | 90 |
| Performance Max | Business name | 1 | 25 |
| Performance Max | Display URL path | 0 - 2 | 15 each |
| Performance Max | Call to action | 1, automated by default or picked from a list | list not in notes |
| Demand Gen | Headline (one of them at most 30 to avoid "Incomplete" Ad Strength and to serve on Display) | 1 - 5 (5 recommended) | 40 |
| Demand Gen | Description | 1 - 5 (3 recommended) | 90 |
| Demand Gen | Business name | 1 | 25 |
| Demand Gen | Carousel card headline, ad-level headline, ad-level description | per card or ad | 40 each |
| Responsive display ad | Headline | 1 - 5 | 30 |
| Responsive display ad | Long headline | 1 | 90 |
| Responsive display ad | Description | 1 - 5 | 90 |
| Responsive display ad | Business name | 1 | 25 |
| Video, in-feed | Headline | 2 lines | 40 per line |
| Video, in-feed | Description | 2 lines | 35 per line |
| Video, in-feed | Call to action | 1 | 15 |
| Video, Efficient Reach composition | Headline / long headline / description / call to action | 1 each | 30 / 90 / 90 / 10 |

RSA pinning rules:

| Rule | Value |
|---|---|
| Pin positions | Headline 1, 2, 3; Description 1, 2 |
| Always shown | pinned H1, H2, D1; H3 and D2 are not guaranteed |
| Text that must appear in every ad (legal disclaimer) | pin it to H1, H2 or D1 |
| Pin 2 - 3 variants per position | yes; pinning every asset blocks unpinned assets from serving |
| Cost of pinning | lowers Ad Strength |
| Under AI Max (text customization, Final URL expansion) | pins are ignored when a more relevant URL is chosen; both are on by default; turning text customization off also turns Final URL expansion off |
| Layout | headline text can appear at the start of the description; unused headlines can serve as sitelink-like assets |
| Keyword | at least one headline should contain a keyword; up to 3 headlines and 2 descriptions show |

Business name (25 characters) must match the domain name or the verified legal name of the advertiser, with no extra symbols or promo text. Google AI-generated assets (text customization) may serve if predicted to beat yours; the advertiser stays responsible for them.

## Google Ads: Search-side assets

| Asset | Limit / rule | Source |
|---|---|---|
| Sitelink text | 25 (12 CJK); at least 2 needed to show; shows up to 6 on desktop, 8 on mobile; two optional description lines of 35 each | https://support.google.com/google-ads/answer/2375416 |
| Callout | 25 (12 CJK); up to 10 can show | https://support.google.com/google-ads/answer/6079510 |
| Structured snippet | header from the fixed list: Amenities, Brands, Courses, Degree programs, Destinations, Featured hotels, Insurance coverage, Models, Neighborhoods, Service catalog, Shows, Styles, Types; aim for 4+ values; header-values mismatch is the likeliest disapproval; value length (unverified) | https://support.google.com/google-ads/answer/6280012 |
| Price asset | at least 3 items (5+ recommended); header 25, description 25 | https://support.google.com/google-ads/answer/7065415 |
| Promotion asset | item name, final URL, promotion type (monetary or percent), optional code and dates; auto-paused when unmodified for 6 months; text limits (unverified) | https://support.google.com/google-ads/answer/7367521 |
| Call asset | E.164 number visible on the site or domain verified; no vanity, premium or fax numbers | https://support.google.com/google-ads/answer/2453991 |
| Lead form | privacy-policy link mandatory; headline 30; other limits (unverified) | https://support.google.com/google-ads/answer/9423234 |

## Google Ads: editorial rules

Official: https://support.google.com/adspolicy/answer/6021546

| Rule | Detail |
|---|---|
| Repeated punctuation | none ("flowers!!") |
| Character substitution | none ("f1owers"), no dotted-out words |
| Symbols | no decorative bullets or asterisks, no emoji; "5* hotel" and legal asterisks are allowed |
| Exclamation marks | only consecutive repeats are barred on the current page; keep them out of headlines (safe value, older rule unverified) |
| Capitalisation | no excessive or gimmicky caps; abbreviations, coupon codes and brand names may be fine |
| Repetition and spacing | do not repeat the advertiser or product name or the ad text; no missing, extra or gimmicky spaces |
| Phone numbers | not in ad text; use a call asset |
| Misrepresentation | no false affiliation, undeliverable offers, impersonation, wrong business name, dishonest pricing, unreliable claims, clickbait |
| Trademarks | allowed as keywords; restricted in a competitor's ad or when confusing; resellers state their role |
| AI-generated people | AI impersonation of a public figure is banned even if labelled (posted 2026-11-11) |

## Meta: text fields by placement

Official: https://www.facebook.com/business/ads-guide. Values are recommendations (text beyond them is cut in the feed with "See more" or dropped); hard maxima are published only for Threads.

| Placement | Primary text | Headline | Description |
|---|---|---|---|
| Facebook Feed (image, video) | 50 - 150 | 27 | - |
| Instagram Feed | 125 (max 30 hashtags) | 40 | - |
| Facebook and Instagram Stories | 125 | 40 | - |
| Facebook in-stream video | 125 | 40 | - |
| Instagram Reels | 44 | - | - |
| Facebook Reels | 40 | 55 | - |
| Carousel (Facebook Feed) | 80 | 20 | 18 |
| Marketplace | 125 | 40 | 30 |
| Lead ads with instant form | 125 | 40 | 30 |
| Facebook right column | 50 - 150 | 27 | - |
| Threads | 80 - 160 recommended, 2,200 hard (longer is not delivered); no URLs in primary text; max 30 hashtags | 40 | - |

Put the hook in the first 40 characters; write primary text at 125 or less so every placement keeps the message. Facebook Feed and Reels cut text earlier than Instagram Feed.

Advantage+ creative enhancements can rewrite copy: Text generation adds up to 5 variations of primary text and headline, plus text improvements, translations and "Enhance media text" (rewrites overlay text on single images). Some are on by default; turn them off per ad when the copy is legally constrained, and review compliance as if variations will run. Meta call-to-action list: not in the notes; pick from the list the Ads Manager offers for the objective.

## Meta: editorial rules

Official: https://transparency.meta.com/policies/ad-standards/

| Rule | Detail |
|---|---|
| Personal attributes | do not assert or imply a person's attributes (race, religion, health, finances, sexual orientation and similar) or that you know personal data ("Are you struggling with debt?" is a violation pattern); write about the product benefit, not the viewer |
| Health, weight loss, diet, cosmetic procedures | target 18+; no statements of inferiority about appearance; no close-up of pinching fat; no claim that results come only from wearables; no claim to cure diabetes, herpes, thyroid conditions, psoriasis, Ebola, cancer, autism, Alzheimer's, Parkinson's, ALS or HIV; no clickbait; no timeframe promises without qualifiers |
| Before / after | side-by-side weight-change imagery unrelated to a product is prohibited; for weight-loss products the health rules above apply |
| Reels ads | no licensed music (use original or royalty-free sound), no pre-2021-10-15 reels, no face or camera effects, no GIFs, no product tags |
| Text in image | old 20 percent text rule: no 2026 statement found (unverified); keep overlay text outside the safe zones (14 percent top, 35 percent bottom, 6 percent sides for 9:16; bottom 40 percent free when a disclaimer is shown) |
| EU | the advertiser and payer fields are required, and political, electoral and social-issue ads are not delivered (compliance table of the `media-plan` skill: `../../media-plan/references/budgets-tracking-compliance.md`) |

## TikTok: text fields, call-to-action lists, rules

Official: https://ads.tiktok.com/resources/help/article/ad-set-up

| Field | Rule |
|---|---|
| Ad text | max 100, recommended 4 - 60; shows 4 lines, then "See more"; emoji and full-width CJK count as 2 in Ads Manager, and the API field `ad_text` accepts no emoji at all, so write without them; curly braces not allowed; minimum length unverified |
| Display (account) name | one line, max 20 (10 for CN / JP / KR), recommended 4 - 10; no emoji, no curly braces; must match the brand, product or company of the promoted site or app; app ads pull the store name |
| Links in text | none clickable; @ allowed but not clickable; # only for commercial, sponsored or organic challenges; age-restricted industries cannot use hashtags in video ads |
| Spark Ads | name and text come from the organic post, not editable |
| Search Ads | up to 1,000 keywords per ad group, 20+ recommended; Smart Multi Ad Text up to 5 titles (title length unverified) |

Standard call-to-action list: Download, Learn More, Visit Store, Book Now, Shop Now, Contact Us, Apply Now, Play Game, Watch Now, View Now, Get Quote, Interested, Install Now, Get Showtimes, Experience Now, Sign Up, Subscribe, Get Tickets Now, Listen Now, Read More, Pre-Order Now, Order Now.

Dynamic call-to-action list (pool of 20 - 40, about 10 - 20 preselected): Shop Now, View Now, Get it Now, Buy Today, Buy Here, Learn More, Order Here, Shop, Buy it Now, Buy Now.

| Rule | Detail |
|---|---|
| Misleading content | no promised or exaggerated results, false before/after, fake play buttons, clickbait |
| Healthcare | no "treat, cure, heal, prevent" claims; no before/after for OTC drugs, devices, supplements; no miracle claims |
| Weight loss | no exaggerated or guaranteed claims; 18+; healthy-lifestyle framing |
| Financial services | 18+; loans and cards need a licence and fee disclosure; payday loans, binary options, get-rich-quick, MLM and ICOs not allowed (per market) |
| TopView | no QR codes, contact numbers or addresses in the creative; a promotional sentence is not repeated more than twice in a row |
| AI content | undisclosed AI-generated content is rejected or restricted; set the AI-generated toggle (non-Spark ads) |
| Common rejections | language not accepted in the target location, unsupported actions such as "swipe up", creative or display name inconsistent with the landing page, unauthorised brands or hashtags |

## Copy pack per platform

Prepare these texts once per campaign, each within the limits above.

1. Google Search: 15 headlines (30), 4 descriptions (90), 2 paths (15), business name (25), at least 2 sitelinks (25), callouts (25), one structured snippet header with 4+ values, one pinned legal line if required.
2. Google Performance Max: 15 headlines (30, one at most 15), 5 long headlines (90), 5 descriptions (90), business name (25), 2 paths (15).
3. Google Demand Gen: 5 headlines (40, one at most 30), 5 descriptions (90), business name (25), carousel card headlines (40).
4. Meta: 5 primary-text variants (125 or less, hook in 40), 5 headlines (27 or less), 1 description (30), call-to-action choice, Reels primary text (44 or less).
5. TikTok: 5 ad texts (60 or less, emoji counted as 2), display name (20), call-to-action from the list.
6. Every platform: a landing-page URL, the claim-substantiation notes, and the age and country restrictions of the product category.
