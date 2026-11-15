# Creative providers: OpenAI, Gemini, fal.ai

Choose the provider and model for one creative task (image, edit, video, voice-over, music, analysis), then run it through the toolkit. Facts verified 2026-11-14. Model ids and prices rot: ids appear only in the dated blocks; everywhere else use the model chosen by `models --pick`.

## Contents

1. Capability matrix
2. Choosing a provider per task
3. Parameters per provider (`image`, `video`, `speech`, `analyze`)
4. fal.ai: discover, read the schema, run
5. Known models and prices (as of 2026-11-14)
6. Cost, billing, retention
7. Errors and fixes
8. Disclosure and licensing

Official docs, one per provider: OpenAI https://developers.openai.com/api/docs, Gemini https://ai.google.dev/gemini-api/docs, fal.ai https://fal.ai/docs.

Ground rules:
- Every operation is `python3 ads/tools/ads.py <command>` from the project root (command reference: `init-project/references/toolkit.md`).
- Run `models --pick` once before the first call; it saves one default per kind across the providers whose keys are set. `--provider P --kind K` narrows it. `--model` overrides one call only.
- After each call read the size and model recorded in `ads/creatives/manifest.jsonl`; do not assume `--aspect` produced the exact pixels.
- Exit 3 = key missing: run `doctor`. Exit 2 = wrong usage, or the toolkit refused the call (an option the provider does not have, such as `--transparent` on Gemini). Exit 1 = service error: see section 7.

## 1. Capability matrix

| Task | OpenAI | Gemini | fal.ai |
|---|---|---|---|
| Text to image | yes; 1-10 per call, any size that is a multiple of 16 | yes; 1 per call (no count parameter), fixed ratio list, 1K/2K/4K | yes; dozens of models, 1-4 per call typical |
| Edit with reference images | yes; 1-16 images, optional mask | yes; up to 14 refs (fewer on the cheapest and oldest models) | yes; up to 14 on the Nano Banana edit models, mask on the GPT Image edit models |
| Transparent background | yes; png or webp | no (not documented) | yes; models with a `background` field, plus background-removal models |
| Text inside the image | partial; exact placement is a documented weakness, always verify | yes; strongest on the Pro image tier | yes; typography models (Ideogram, GPT Image) |
| Video from text | no; no video API since 2026-09-24, no replacement | yes; Omni family only, 3-15 s, 16:9 or 9:16 | yes; many models, 1-30 s depending on model |
| Video from a first frame | no | yes; one image in; first plus last frame limits the clip to 3-10 s | yes; image field name differs per model |
| Voice-over | yes, but voice models shut down 2027-01-06; successor is not served by the speech endpoint | yes; 30 prebuilt voices, 130+ languages, max 2 speakers | yes; several voice models, priced per 1000 characters |
| Music | no | yes (Lyria), paid tier only: `music --provider gemini` | yes: `music --provider fal`, or any music model through `fal run` |
| Describe an image or video | images only; for video use Gemini | images and video (public YouTube URL or uploaded file) | yes, through `fal run` with a vision or video-understanding model; `analyze` does not accept fal |

Toolkit coverage: `models --kind` knows image, video, speech, music and analysis, and each has its own command. Talking avatars, background removal, upscaling and every other special model run through `fal schema` plus `fal run`.

## 2. Choosing a provider per task

| Task | Pick | Why / fallback |
|---|---|---|
| Draft volume (10+ variants to compare) | fal.ai fast draft model, or the Gemini fast image model | cheapest per image; keep 1K. Re-render winners on a stronger model |
| Text-heavy brand visual (headline in image) | Gemini Pro image tier, or OpenAI Sunburst-class model at high quality | then run `analyze` on the output and compare the text; retry on a typo. fal.ai typography models as alternate |
| Product shot from a customer photo | Gemini edit with `--ref`, or OpenAI edit | OpenAI when a mask is needed; fal.ai product-shot models for a fixed studio background |
| Transparent cut-out or sticker | OpenAI with `--transparent` | fal.ai: model with a `background` field or a background-removal model. Not Gemini |
| Vertical video 9:16, 3-15 s, with sound | Gemini Omni (`video --provider gemini`) | fal.ai when you need 1:1, over 15 s, a specific look, or a cheaper bulk model. Never OpenAI |
| Talking avatar from a still plus script | fal.ai only: voice step, then avatar model | see section 4 example 3 |
| Voice-over, many languages | Gemini speech | fal.ai for expressive or branded voices. OpenAI only if already integrated, ends 2027-01-06 |
| Background music | `music` on Gemini (Lyria) | `music --provider fal` for a longer bed or a specific style. Write "instrumental, no vocals" in the prompt when the track sits under a voice-over |
| Competitor ad breakdown | Gemini `analyze` (video and image) | OpenAI `analyze` for still images only |
| Exact deliverable pixels (1080x1920, 1200x628) | generate the nearest ratio and add `--fit 1200x628`: the toolkit saves a second copy, scaled and centre-cropped (needs ffmpeg) | no provider guarantees these sizes natively; keep the subject away from the edges that get cropped |

## 3. Parameters per provider

### 3.1 `image`

| Item | OpenAI | Gemini | fal.ai |
|---|---|---|---|
| Sizes | `auto`, 1024x1024, 1536x1024, 1024x1536, or any WxH: multiples of 16, ratio 1:3 to 3:1, longest edge 3840, 655,360 to 8,294,400 pixels (above 2560x1440 experimental) | tiers 1K (default), 2K, 4K; one model also has 512. Uppercase K only | per model: `image_size` preset or `{width,height}`, or `aspect_ratio` plus `resolution` |
| Ratios | any in range | 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9; the newest two models add 1:4, 1:8, 4:1, 8:1 | per model; read `fal schema` |
| `--aspect` to size (what the toolkit sends) | 1:1 = 1024x1024, 4:5 = 1088x1360, 9:16 = 1152x2048, 16:9 = 2048x1152, 1.91:1 = 1216x640; `--size WxH` is rounded to multiples of 16 | the nearest supported ratio: 1.91:1 becomes 16:9, so add `--fit 1200x628`. 1K pixels: 1:1 1024x1024, 16:9 1376x768, 9:16 768x1376, 4:5 928x1152 | read from the model's fields: `aspect_ratio` gets the nearest allowed value; otherwise `image_size` gets a preset (square_hd 1024x1024, portrait_4_3 768x1024, portrait_16_9 576x1024, landscape_16_9 1024x576) or, with `--size`, the exact width and height |
| Max per call (`--n`) | 10 | no count parameter: the toolkit makes one call per image, so `--n 4` is four billed calls | `num_images` when the model has it: 1-4 typical; 6 or 8 or 10 on some models |
| References (`--ref`) | 1-16; the first is the one edited, the rest are references; mask needs an alpha channel and the first image's size | up to 14 (fast tier: 10 objects + 4 characters; Pro: 6 objects + 5 characters + 3 style refs); cheapest tier weak at multi-ref; oldest tier best at 3 or fewer | `image_urls` (up to 14 on the Nano Banana edit models) or one `image_url`. `--ref` files are uploaded to fal storage for you; a model with neither field is refused: pick an edit model |
| Quality (`--quality`) | the toolkit passes low, medium or high; the API also knows auto, and xhigh and max on the 2.5 and 2.6 families, reachable only through a direct call; high costs far more than low | none; quality is the model tier plus the size tier. The toolkit maps `--quality high` to the 2K tier and low or medium to 1K; with `--size` the longest edge decides (up to 1400 px 1K, up to 2800 px 2K, above that 4K) | per model (`quality` on GPT Image and Ideogram models; steps on FLUX). `--quality` is not passed on: set the model's own field through `fal run` |
| Transparency (`--transparent`) | `background` transparent, output png | not documented; the toolkit refuses the flag | the toolkit refuses the flag: run a model with a `background` field (GPT Image, Seedream) or a background-removal model through `fal run` |
| Extras | `complexity` low/medium/high on 2.6 (high helps dense text); GIF and SVG output are preview, access-gated; edits take `markup` overlay; omit `input_fidelity` | thinking is always on; web and image search grounding on newer models; multi-turn edit possible | `seed`, `safety_tolerance`, `num_images`, `sync_mode`; model specific |
| Limits | prompt 32,000 characters; one call can take about 2 minutes; response is base64 | request with inline images under 20 MB total; all images carry SynthID | request body 64 MiB; use URLs for files |
| Text-in-image tip | state the exact text in quotes; verify by `analyze` | generate the copy first, then ask for the image with it; best prompt languages EN, DE, ES, FR, IT, PT, RU, JA, KO, ZH, HI, AR, ID, VI | typography models first |

Override one call (as of 2026-11-14; ids rot, prefer `--pick`):

<!-- example-only -->
```bash
python3 ads/tools/ads.py image --provider openai --model gpt-image-2.6-flare --prompt "Square ad, headline FRESH ROAST centered" --size 1024x1024 --quality medium --out ads/creatives --name roast-1x1
python3 ads/tools/ads.py image --provider gemini --model gemini-nano-banana-2.1 --prompt "Product on concrete plinth, space left for headline" --aspect 4:5 --ref ads/brand/product.png --out ads/creatives --name bottle-4x5
python3 ads/tools/ads.py image --provider openai --model gpt-image-2.6-sunburst --prompt "Red running shoe cut-out, studio light" --transparent --out ads/creatives --name shoe
```
<!-- /example-only -->

### 3.2 `video`

| Item | OpenAI | Gemini | fal.ai |
|---|---|---|---|
| Availability | none (no video API since 2026-09-24); the only motion output is a short animated GIF from the 2.6 image models, preview and access-gated | Omni family only; paid tier only; synchronous call | per model, many families |
| Duration (`--seconds`, toolkit default 8) | - | whole seconds 3-15 (API default 10); first plus last frame 3-10 s; extend a clip to 30 s total | per model: Veo-class 4/6/8, Kling-class 3-30, MiniMax-class 0.92-15, Seedance-class 4-30; value type differs (string "8s", string "8", integer 8) |
| Aspect (`--aspect`, toolkit default 9:16) | - | 16:9 or 9:16 only, anything else is refused; for 1:1 crop a 16:9 clip or use fal.ai | per model: 16:9, 9:16 common; 1:1 on Kling-class and MiniMax-class |
| Resolution (`--resolution`) | - | 360p, 720p (default), 1080p and 4k (both upscaled); 24 fps | per model; MiniMax-class values are uppercase (480P, 768P, 1080P) |
| First frame (`--image`) | - | one image plus prompt (the toolkit passes one; the API also takes first and last frame and up to 6 reference images) | pick an image-to-video model; the file is uploaded to fal storage and sent as `image_url`, `first_frame_url` or `start_image_url`, whichever the model has |
| Sound | - | native audio by default (dialogue, effects, music); steer by prompt ("no dialogue"); no on/off flag | per model `generate_audio`, often default true and billed higher |
| Prompt tips | - | write "single continuous shot" or it cuts; no negative-prompt field (write "do not ..."); dictate on-screen text verbatim; English is fully supported, other languages may work | model specific |
| Rate limit | - | tier 1: 8 per minute, 40 per day | account concurrency, new accounts 2 in progress |

### 3.3 `speech`

| Item | OpenAI | Gemini | fal.ai |
|---|---|---|---|
| Voices (`--voice`) | 13 on the newer voice model: alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer, verse, marin, cedar; the older two models take 9 of them (no ballad, verse, marin, cedar) | 30 prebuilt: Zephyr, Puck, Charon, Kore, Fenrir, Leda, Orus, Aoede, Callirrhoe, Autonoe, Enceladus, Iapetus, Umbriel, Algieba, Despina, Erinome, Algenib, Rasalgethi, Laomedeia, Achernar, Alnilam, Schedar, Gacrux, Pulcherrima, Achird, Zubenelgenubi, Vindemiatrix, Sadachbia, Sadaltager, Sulafat | per model (default voice name on ElevenLabs-class: Rachel); `voice` or `voice_setting` |
| Languages | not documented (unverified): test the target language | 130+ on the standard model, 101 on the lite model; language auto-detected | per model; `language_code` or `language_boost` |
| Style control | `instructions` for tone and pace, newer voice model only | style text per input; inline tags such as short pause, laugh | `style_instructions`, `stability`, `similarity_boost` |
| Limits | max input length unverified | input 8,192 tokens; 2 speakers max, prebuilt voices only | per model |
| Output | mp3, opus, aac, flac, wav, pcm | WAV, 24 kHz mono | mp3 or pcm variants; URL returned |
| Text field name | `input` | `text` | `text` or `prompt`, per model: check `fal schema` |

`speech --provider fal` fills `text` (or `prompt`) and, when the model has it, `voice`. For every other voice option use `fal run`, which works for any fal model.

### 3.4 `analyze`

| Input | OpenAI (`--provider openai`) | Gemini (`--provider gemini`) |
|---|---|---|
| Image | `--file` or `--url`; png, jpeg, webp, non-animated gif; up to 1,500 images and 512 MB per request | `--file` or `--url`; inline requests under 20 MB total, larger goes through the Files API |
| Video | not documented: extract frames, or use Gemini | public YouTube URL, or an uploaded file up to 2 GB; sampled at 1 frame per second |
| Meta or TikTok ad-library video | download first, then `--file` | download first, then `--file` (no first-party fetch of non-YouTube URLs) |
| Audio track | transcription is a separate OpenAI endpoint the toolkit does not expose; limit 25 MB | audio inside video is analysed |
| Uploaded file lifetime | - | 48 hours, then deleted |

Cheap bulk tagging: choose the fast text-and-vision model; for strategy-grade breakdowns choose a stronger one. Both come from `models --pick`.

## 4. fal.ai: discover, read the schema, run

fal.ai is the catch-all: one key, hundreds of models, every field differs per model. Never guess a field.

1. Discover: `models --provider fal --kind image|video|speech|music`, or `models --provider fal --query TEXT`, which searches the whole catalogue (for example "avatar", "background removal", "upscale", "image-to-video").
2. Read the fields: `fal schema MODEL_ID`. Note required fields (marked with an asterisk in model docs), enums, defaults, units and the output field.
3. Write the input as a JSON file. Where a field wants a file URL, write `{"@upload": "ads/creatives/frame.png"}`: the toolkit uploads that local file to fal storage and puts its URL in place. A public URL works as well.
4. Run: `fal run MODEL_ID --input @FILE --out ads/creatives --name STEM`. It uses the queue, polls, and downloads the outputs.

Rules: a `COMPLETED` queue state can still hold an error, so read the exit code and message. A deprecated or retired model fails to resolve: pick a replacement from `models`. Value formats vary: duration may be `"8s"`, `"8"` or `8`; MiniMax-class resolution is uppercase.

Examples as of 2026-11-14 (endpoint ids and fields change; run `fal schema` first):

<!-- example-only -->
1. Text to image (4:5 social visual):
```bash
python3 ads/tools/ads.py fal run google/nano-banana-2.1 --input @ads/creatives/inputs/hero.json --out ads/creatives --name hero
```
```json
{"prompt": "Studio photo of a matte black water bottle on a concrete plinth, soft key light, empty space on the left for a headline", "num_images": 2, "aspect_ratio": "4:5", "resolution": "2K", "output_format": "png"}
```
2. Image to video from a first frame (8 s, 1080p):
```bash
python3 ads/tools/ads.py fal run kling/v4/image-to-video --input @ads/creatives/inputs/clip.json --out ads/creatives --name clip-8s
```
```json
{"prompt": "Slow push-in on the bottle, condensation drips, soft morning light, single continuous shot", "start_image_url": {"@upload": "ads/creatives/frame.png"}, "duration": 8, "resolution": "1080p"}
```
3. Talking avatar: voice first, then a still plus the audio. The voice step saves the audio file under `--out`; hand it to the avatar model with `@upload`:
```bash
python3 ads/tools/ads.py fal run elevenlabs/tts/eleven-v4 --input @ads/creatives/inputs/voice.json --out ads/creatives --name vo
python3 ads/tools/ads.py fal run bytedance/omnihuman/v2 --input @ads/creatives/inputs/avatar.json --out ads/creatives --name avatar
```
```json
{"text": "Meet the bottle that keeps coffee hot for twelve hours.", "voice": "Rachel", "language_code": "en", "output_format": "mp3_44100_128"}
```
```json
{"image_url": {"@upload": "ads/creatives/presenter.png"}, "audio_url": {"@upload": "ads/creatives/vo.mp3"}, "prompt": "Friendly presenter speaking to camera, natural gestures"}
```
Avatar limits: image max 30 MB, 300-6000 px, ratio 0.4-2.5; audio wav or mp3, max 15 MB, 4-300 s.
<!-- /example-only -->

## 5. Known models and prices (as of 2026-11-14)

<!-- example-only -->
Images (USD):

| Provider | Model id | Use | Price |
|---|---|---|---|
| OpenAI | gpt-image-2.6-flare, gpt-image-2.5-flare | fast everyday | tokens: $8 in, $30 out per 1M image tokens; Batch half. Per-image table for 2.5 and 2.6 unverified; the older gpt-image-2 at 1024x1024: low $0.006, medium $0.053, high $0.211 |
| OpenAI | gpt-image-2.6-sunburst, gpt-image-2.5-sunburst | editing precision, dense text | same token rates |
| Gemini | gemini-nano-banana-2.1 | default volume | $0.0336 (1K), $0.0504 (2K), $0.113 (4K); Batch half |
| Gemini | gemini-3-pro-image | text-heavy, brand-critical | $0.134 (1K-2K), $0.24 (4K) |
| Gemini | gemini-3.1-flash-lite-image | cheapest, 1K only, weak multi-ref | $0.0336 |
| fal.ai | google/nano-banana-2.1 (+ /edit) | fal default | about $0.040 (1K), $0.059 (2K), $0.134 (4K) |
| fal.ai | fal-ai/nano-banana-pro | brand work | $0.15 |
| fal.ai | openai/gpt-image-2 | exact typography, transparency | tokens as OpenAI |
| fal.ai | ideogram/v4.5 | typography | $0.03 low, $0.06 medium, $0.22 high |
| fal.ai | fal-ai/flux/schnell | fastest drafts | $0.003 per MP |

Video and avatar (USD per second of output unless stated):

| Provider | Model id | Notes | Price |
|---|---|---|---|
| Gemini | gemini-omni-1.2-flash | 3-15 s, native audio | 360p $0.023, 720p $0.07, 1080p $0.104, 4k $0.209 |
| fal.ai | fal-ai/veo3.1/fast (+ /image-to-video) | 4/6/8 s, audio | $0.10 no audio, $0.15 audio; Veo 3.1: $0.20 / $0.40 |
| fal.ai | kling/v4/image-to-video, kling/v4/text-to-video | 3-30 s | $0.157 (720p), $0.235 (1080p); flash variant $0.094 (720p) |
| fal.ai | fal-ai/kling-video/v3/pro/image-to-video | 3-15 s | $0.112 no audio, $0.168 audio |
| fal.ai | minimax/h3-max/text-to-video (+ image-to-video) | fal's default text to video | from 2026-11-16: $0.05 (480P), $0.08 (768P), $0.16 (1080P); promo -30% ends 2026-11-15 |
| fal.ai | bytedance/seedance-2.5/text-to-video | up to 30 s | about $0.22 (480p), $0.47 (720p), $1.16 (1080p) |
| fal.ai | bytedance/omnihuman/v2 | avatar from still + audio | $0.105 |
| fal.ai | fal-ai/flashtalk | talking head, fal default | $0.02 |

Voice, music, effects (USD):

| Provider | Model id | Notes | Price |
|---|---|---|---|
| OpenAI | gpt-4o-mini-tts (also tts-1, tts-1-hd) | shuts down 2027-01-06 | price unverified |
| Gemini | gemini-3.8-flash-tts | standard | $0.00225 per 10 s through 2026-12-31, double after |
| Gemini | gemini-3.8-flash-lite-tts | cheaper, 101 languages | $0.0015 per 10 s through 2026-12-31, double after |
| Gemini | lyria-3.5 (song), lyria-3-clip-preview (30 s) | `music --provider gemini` | $0.08 per song, $0.04 per clip |
| fal.ai | elevenlabs/tts/eleven-v4, eleven-v4-turbo | expressive voice | $0.08, $0.04 per 1000 characters |
| fal.ai | elevenlabs/music/v2.5, minimax/music-3 | music bed | $0.60 per minute; $0.002 per second |

Dates in the next six months:
- 2026-11-15 and 2026-11-22: fal.ai promo prices end for MiniMax H3 Max (regular from 11-16) and FLUX 3 Max video (regular $0.17 per s at 720p, $0.29 at 1080p from 11-23).
- 2026-12-01: gpt-image-1.5, gpt-image-1-mini, chatgpt-image-latest shut down. Gemini 4 Carbon and Argon text prices double; gemini-2.5-flash and gemini-2.5-pro start routing to newer models.
- 2026-12-03: gemini-omni-1.1-flash routes to gemini-omni-1.2-flash.
- 2026-12-10: fal-ai/glm-image retires; replacement is minimax/h3-image.
- 2026-12-18: gemini-3.1-flash-tts-preview and both gemini-2.5 preview TTS models shut down.
- 2027-01-04: fal.ai Wan 2.2 family retires; replacements minimax/h3-max or wan v2.7.
- 2027-01-06: OpenAI tts-1, tts-1-hd, gpt-4o-mini-tts shut down.
- 2027-02-01: fal-ai/elevenlabs/sound-effects/v2 retires; replacement elevenlabs/sound-effects/v3.
- 2027-02-10: gpt-image-2 shuts down. 2027-02-26: whisper-1 and the 4o transcribe models shut down.
- 2027-03-15: gemini-2.5-flash-image shuts down. 2027-05-07: gemini-3.1-flash-lite shuts down.
- Already gone: OpenAI Sora and the Videos API (2026-09-24), gpt-image-1 (2026-10-23), DALL-E; Gemini Imagen 4 and Veo on the Gemini API; fal.ai Veo 2/3, Sora 2 and Imagen endpoints are deprecated.
<!-- /example-only -->

## 6. Cost, billing, retention

| | OpenAI | Gemini | fal.ai |
|---|---|---|---|
| Billing | prepaid credits, minimum $5 (moves the org to the Build tier); credits expire after 1 year; optional hard monthly spend limit per project | free tier covers text only; image, video and music need the paid tier: linked billing account and prepay of at least $5 | prepaid credits; below the lock threshold the account is locked and calls are refused; credits expire after 365 days |
| Unit | image and text tokens | image tokens by size tier, video per second, speech per audio token, music per song | per output: image, megapixel, second, 1000 characters, or request |
| Discounts | Batch 50% (image generations and edits, 24 h window) | Batch 50% for images (not for Omni, unverified) | none documented |
| Failed calls | blocked calls are not retried; billing detail unverified | blocked generation: no output | 5xx and queue time are free; a 422 can be charged if a runner already spent GPU time |
| Concurrency | per-tier requests and images per minute (numbers unverified for image models) | Omni tier 1: 8 per minute, 40 per day | new account 2 in progress, rises to 40 with spend; use the queue (the toolkit does) |

Typical cost by the notes' numbers:

| Item | OpenAI | Gemini | fal.ai |
|---|---|---|---|
| One ad image | about $0.025 (an illustrative figure, settings not stated); verify with `usage` | $0.034 (1K) to $0.05 (2K) fast tier; $0.134 Pro | $0.003 (draft) to $0.04 (default) to $0.15 (brand model) |
| 8-second clip | not available | $0.56 (720p), $0.83 (1080p) | $0.64 (768p, MiniMax-class, after 2026-11-16) to $1.20 (Veo fast with audio) to $1.88 (Kling-class 1080p) |
| 30-second voice-over | price unverified | about $0.007 (double after 2026-12-31) | about $0.04 on the expressive voice model (assuming 450 characters) |

Retention: download everything at once; the toolkit does it and lists each file in `ads/creatives/manifest.jsonl`.
- OpenAI returns image bytes inline; nothing is kept for you.
- Gemini returns bytes inline; uploaded files are deleted after 48 hours; stored interactions last 55 days (paid) or 1 day (free). Large video can be delivered as a hosted file: fetch it straight away.
- fal.ai keeps a queue result 1 hour (6 minutes if the result is 10 KB or larger). Output files sit at public URLs; the stated retention conflicts (at least 7 days versus unlimited). Treat every file as public and temporary; never put embargoed or confidential assets in a fal input.

## 7. Errors and fixes

| Signal | Provider | Meaning | Action |
|---|---|---|---|
| 400 moderation_blocked | OpenAI | prompt or output filtered | rewrite prompt or inputs; never retry unchanged; log the request id |
| 400 safety, image_safety, prohibited_content, image_recitation, no_image | Gemini | blocked or no image produced | rephrase; drop people, brand and artist names; retry once |
| 422 content_policy_violation | fal.ai | blocked by the model | change prompt or input image; do not retry; do not lower safety settings unless policy allows |
| 429 credit_balance_exhausted | OpenAI | prepaid balance empty | stop; ask the user to add credits; do not retry |
| 402 payment_required | Gemini | prepay balance is $0 | stop; ask the user to top up or enable auto-reload; do not retry |
| 403 locked account or spending limit; 401 on a locked account | fal.ai | balance below lock threshold | stop; ask the user to add credits in the fal.ai dashboard |
| 429 spend or usage limit exceeded | OpenAI | project or org limit | ask the user to raise the limit; do not retry |
| 429 rate limit, slow_down; 503 overloaded | OpenAI | transient | back off (1, 2, 4, 8 s with jitter), honour Retry-After, max 5 tries |
| 429 rate_limit_exceeded; quota_exceeded | Gemini | per-minute or daily quota (Omni tier 1: 8/min, 40/day) | back off for per-minute; for daily wait for the reset or raise the tier |
| 429 concurrent_requests_limit | fal.ai | too many parallel runs | run sequentially; the queue absorbs bursts |
| 403 organization verification | OpenAI | image models may require API Organization Verification (business or ID); exact error text unverified | send the user to the General settings page of the OpenAI developer console to verify; then retry |
| 403 permission_denied, FREE_TIER_VERIFICATION_REQUIRED | Gemini | verification, billing past due, or blocked key | user fixes verification or billing, or creates a new key |
| 401 invalid key | all | wrong, expired or restricted key | `doctor --live`; Gemini rejects unrestricted standard keys: create a new key in AI Studio; fal.ai: key with the API preset |
| 404 model not found | all | retired model id | run `models --pick` again; check the dates in section 5 |
| 422 field errors | fal.ai | wrong input field or value | re-read `fal schema`; fix the named field |
| 5xx, 504, runner errors | all | provider side | retry with backoff; raise the client timeout for video |
| Result missing (404) after completion | fal.ai | result expired (1 hour) | rerun; download at once next time |

## 8. Disclosure and licensing

| Provider | Invisible mark or credential | Notes |
|---|---|---|
| Gemini | all generated images and videos carry SynthID; the lite image tier adds C2PA content credentials; Lyria audio carries SynthID | speech output: not documented (unverified); do not strip or claim removal |
| OpenAI | none verified for images or speech | do not state that OpenAI output is unmarked; apply the ad platform's AI-label rules anyway |
| fal.ai | none added by fal.ai itself; the underlying model may mark its output | some models expose a `watermark` or a disclosure field (Seedream `watermark` defaults to false; one avatar model has `manifest_disclosure`, meaning unverified): check `fal schema` |

Commercial-use flag on fal.ai: model metadata `license_type` is commercial, research or private; the model page shows a Commercial use or Research only badge. All endpoints named in section 5 were commercial on 2026-11-14. Rules:
- Use only `commercial` models for ads; skip research, private, or empty-license models (a few older community models have none).
- "Partner API" models are hosted by partners; standard discounts do not apply.
- If `models` output does not show the license, read the model page before the first paid run.
- Logos, trademarks, public figures and real people: OpenAI image policy text unverified; Gemini and fal.ai block some real-person prompts. Keep a human brand-safety review and never promise logo reproduction.
