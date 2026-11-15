---
name: ad-creatives
description: This skill should be used when the user asks to "generate ad creatives", "make ad images", "create a video for the ad", "add a voice-over", "resize for Stories", or needs media files for Google, Meta or TikTok ads. Not for ad text (ad-copy) or uploading (launch-campaign).
---

# Ad creatives

Produce the visual and audio assets of a campaign with OpenAI, Gemini and fal.ai: images in every size the placements need, short video, voice-over and music. Each file is generated from a written prompt, checked before anyone uploads it, and recorded with the model and prompt that made it.

Inputs: `ads/brief.md` (product, audience, proof), `ads/brand.json` (colours, tone, logo), `ads/plan/media-plan.md` (campaigns and placements), `ads/plan/copy/` (the angles and the approved claims). Outputs: files in `ads/creatives/`, the automatic `ads/creatives/manifest.jsonl`, and the list `ads/plan/creatives.md`.

References: sizes, safe zones and asset counts per placement in [specs.md](references/specs.md); what each provider can do, its parameters, prices and errors in [providers.md](references/providers.md).

## Step 1: Check providers and models

```bash
python3 ads/tools/ads.py doctor --live --only openai,gemini,fal
python3 ads/tools/ads.py models --pick
```

One working key is enough. Model ids change every few months and none is built into the toolkit: `models --pick` asks each provider what exists today and saves one default per kind (image, video, speech, music, analysis) in `ads/config.json`. A missing key prints where to get it; the `init-project` skill walks through it.

| Need | Provider |
|---|---|
| Images, edits from a product photo, text inside an image | Gemini or OpenAI |
| Transparent cut-out | OpenAI (`--transparent`) |
| Video with sound, 3 to 15 seconds, vertical or horizontal | Gemini |
| Square or longer video, a specific video model, avatars, background removal, upscaling | fal.ai |
| Voice-over | Gemini; OpenAI or fal.ai as alternatives |
| Music bed | Gemini or fal.ai |

## Step 2: Write the shot list

Derive the assets from the media plan instead of generating at random. For each campaign and angle, list the placements and take the sizes from the reference. The masters that cover most placements:

| Master | Ratio | Serves |
|---|---|---|
| 1080x1920 | 9:16 | Stories, Reels, TikTok, Shorts (image and video) |
| 1440x1800 (never below 1080x1350) | 4:5 | Meta feed |
| 1080x1080 for Meta, 1200x1200 for Google | 1:1 | feeds, carousels, Google square |
| 1200x628 | 1.91:1 | Google Performance Max, Demand Gen, display; Meta landscape |
| 1920x1080 | 16:9 | YouTube video |

This table is a summary; where it and the specs reference differ, the reference wins. Logos are not generated, because image models misdraw them: take the real file from `ads/brand/` and resize it.

Generation costs money, so one rule covers all of it: before any `video` call, before any `fal run` of a video or avatar model, and before an image batch estimated above about one US dollar, show the provider, the model, the count, the length and resolution, and the estimated cost, and wait for a yes to that figure. One clip counts. Ask again when the provider, the resolution or the length changes. Take the prices from the cost section of the providers reference; as orders of magnitude, an image costs cents, an eight-second clip between half a dollar and two dollars, a voice-over about a cent.

<example>
Shot list for de_meta_trial_202612 (3 angles), estimate about 1.06 USD

| Id | Angle | Type | Size | Use |
|---|---|---|---|---|
| outcome-4x5 | outcome | image | 4:5 | Meta feed |
| outcome-9x16 | outcome | image | 9:16 | Stories, Reels |
| pain-4x5 | pain | image | 4:5 | Meta feed |
| pain-9x16 | pain | image | 9:16 | Stories, Reels |
| offer-1x1 | offer | image | 1:1 | feed, carousel |
| outcome-reel | outcome | video, 8 s, 720p | 9:16 | Reels |

Images: two drafts each (10 images), then one final per id, on the default Gemini image model: about 0.50 USD. Video: 1 clip of 8 seconds at 720p on the default Gemini video model: about 0.56 USD. Proceed with both, images only, or neither?
</example>

## Step 3: Write the prompts

A prompt that works names six things: the subject, the setting, the composition (where the empty space is), the light and style, the brand colours as hex values from `ads/brand.json`, and what must stay out.

- **Leave room.** Platforms place interface elements over vertical creatives. Meta publishes the zones for 9:16: keep the top 14 percent, the bottom 35 percent (40 for a Reels ad with a disclaimer) and 6 percent of each side free of anything important. TikTok and YouTube Shorts publish no figures: use Meta's as a cautious default there. Say so in the prompt ("subject in the middle third, empty background above and below").
- **Keep text out of the image when possible.** The headline and primary text are shown by the platform from the copy pack. When text inside the image is needed, give the exact words in quotes, keep it under five words, and verify the result in step 5: image models still misspell.
- **Show the real product.** Pass a product photo or a screenshot with `--ref` so the model edits reality instead of inventing a product that does not exist.
- **Do not ask a model to draw the logo.** Composite the real file afterwards (step 4).
- **No real people, no celebrities, no competitor products or trademarks**, and for health or weight topics no before-and-after scenes: platforms reject these and some are unlawful.
- **Fit the market.** Faces, interiors, plugs, street scenes and written language must look like the target country.

Write one prompt per angle and reuse it across sizes, changing only the composition sentence.

## Step 4: Generate

Draft cheaply, choose, then render the winners at delivery size.

```bash
python3 ads/tools/ads.py image --prompt "Freelance designer at a tidy desk smiling at a laptop, soft daylight, subject in the middle third, plain light wall above and below, palette #1F4FD8 and #FFB020, no text, no logos" --aspect 9:16 --n 2 --name outcome-9x16
python3 ads/tools/ads.py image --prompt "Same scene, wide composition, subject on the right, empty space on the left" --aspect 1.91:1 --fit 1200x628 --name outcome-landscape
python3 ads/tools/ads.py image --prompt "Place this app screenshot on a laptop on a wooden desk, natural light, no other text" --ref ads/brand/screenshot.png --size 1440x1800 --fit 1440x1800 --name product-4x5
```

Files land in `ads/creatives/` as `NAME.png`, `NAME-2.png` and so on, with the extension of the format the provider returned (Gemini often returns `.jpg`); an existing file is never overwritten. The command prints the paths it wrote: use those paths in later commands and in plan files. `--fit WxH` saves a second file, `NAME-WxH`, scaled and centre-cropped to the exact pixels a placement wants (it needs `ffmpeg`). `--provider` and `--model` override the saved default for one call.

Video, voice and music:

```bash
python3 ads/tools/ads.py video --prompt "Single continuous shot: a hand closes a laptop, a phone on the desk lights up with a payment notification, warm morning light, no on-screen text" --aspect 9:16 --seconds 8 --name outcome-reel
python3 ads/tools/ads.py video --prompt "Slow push-in, steam rises from the coffee cup, nothing else moves" --image ads/creatives/outcome-9x16.png --aspect 9:16 --seconds 6 --name outcome-from-still
python3 ads/tools/ads.py speech --text "Rechnung raus, Geld da. Neun Tage schneller bezahlt." --voice Kore --out ads/creatives/vo-outcome-de.wav
python3 ads/tools/ads.py music --prompt "Light upbeat acoustic bed, instrumental, no vocals, 20 seconds" --out ads/creatives/bed-upbeat.mp3
```

Each of these calls falls under the cost rule of step 2. Gemini video comes in 9:16 or 16:9, 3 to 15 seconds, with generated sound; for 1:1, longer clips or a named model use fal.ai, and for a cut above 15 seconds join clips with `ffmpeg`. Starting a clip from an approved still (`--image`) keeps the product and the look consistent.

Anything else runs through fal.ai's catalogue. Find a model, read its input fields, then run it; `{"@upload": "FILE"}` in the input uploads a local file:

```bash
python3 ads/tools/ads.py models --provider fal --query "background removal"
python3 ads/tools/ads.py fal schema MODEL_ID
python3 ads/tools/ads.py fal run MODEL_ID --input @ads/creatives/inputs/cutout.json --name product-cutout
```

A `fal run` of a video or avatar model falls under the cost rule as well: read the price on the model's page first. Files sent to fal.ai and its outputs sit at public addresses: do not send confidential or embargoed material there.

Finishing with `ffmpeg`, when it is installed:

```bash
ffmpeg -i ads/creatives/outcome-4x5.png -i ads/brand/logo.png -filter_complex "[1:v]scale=220:-1[logo];[0:v][logo]overlay=W-w-48:48" ads/creatives/outcome-4x5-logo.png
ffmpeg -i ads/creatives/outcome-reel.mp4 -i ads/creatives/vo-outcome-de.wav -map 0:v -map 1:a -c:v copy -shortest ads/creatives/outcome-reel-vo.mp4
```

## Step 5: Check every file before it is used

A generated file is a draft until it passes these checks.

1. **Look at it.** Open the image with the file reader, or ask a model to describe it:

```bash
python3 ads/tools/ads.py analyze --prompt "List every word visible in this image exactly as written. Then describe the subject, the colours, and any distorted hands, faces, objects or interface elements." --file ads/creatives/outcome-9x16.png
```

2. **Technical fit.** Pixel size, ratio, duration, file size and format against the placement's row in the specs reference: `file ads/creatives/NAME.png` prints image dimensions, and `ffprobe -v error -show_entries stream=codec_name,width,height,duration -of csv=p=0 FILE` prints video facts.
3. **Safe zones.** Nothing important under the interface areas of vertical placements.
4. **Truth.** The creative shows the product as it is and makes no claim the copy pack did not approve. No invented interface, no fake buttons or notifications that imitate the operating system.
5. **Brand.** Colours and tone match `ads/brand.json`; the logo is the real file, unstretched.
6. **Rights and people.** No recognisable real person, no third-party brand. Music: a Reels ad takes original sound only, such as a generated track or one the advertiser owns outright, and no licensed commercial track. A TikTok ad takes sound the advertiser holds the rights to, or a track from TikTok's Commercial Music Library; anything else is rejected for missing music authorisation.
7. **Disclosure.** Mark the file as AI-generated in the list. TikTok requires the AI-generated toggle for realistic synthetic media; Meta and Google add their own labels in some cases.

Reject and regenerate with one changed instruction at a time. Regenerating with the same prompt and hoping wastes money.

## Step 6: Record and show

`ads/creatives/manifest.jsonl` already holds, for every file, the provider, model, prompt and size. Add the human-readable list `ads/plan/creatives.md`; `launch-campaign` uses only files whose status reads `approved`, and that word is written after the user's sign-off, not before.

<example>
| Id | File | Size | Campaign | Angle | Checks | AI-generated | Status |
|---|---|---|---|---|---|---|---|
| outcome-4x5 | ads/creatives/outcome-4x5-1440x1800.jpg | 1440x1800 | de_meta_trial_202612 | outcome | size, safe zone, text, brand: ok | yes | approved |
| pain-4x5 | ads/creatives/pain-4x5-2.jpg | 1440x1800 | de_meta_trial_202612 | pain | hand distorted | yes | rejected |
</example>

Show the user the files as paths and the total spent on generation, and ask for sign-off. Then offer `launch-campaign` as the next step.

## Rules

- This skill makes media only. Ad texts belong to `ad-copy`; uploading to an ad account and creating ads belong to `launch-campaign`.
- Keep to the cost rule of step 2, and report the actual count and spend after each batch.
- A provider refusal for safety or policy is not an obstacle to work around: change the concept, do not rephrase to slip past the filter. Evading a filter breaks the provider's terms and usually produces an ad the platforms reject anyway.
- Do not remove or hide provenance marks (SynthID, C2PA) and do not claim a generated image is a photograph of a real event or customer: the platforms' disclosure rules depend on those marks, and a false claim of authenticity is deceptive advertising.
- A competitor creative studied in research is reference material. Do not recreate it: it is their copyright.
