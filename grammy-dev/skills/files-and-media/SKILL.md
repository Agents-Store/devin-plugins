---
name: files-and-media
description: This skill should be used when the user asks about "send photo in grammY", "send file", "send document", "send video", "InputFile", "send media group", "download user file", "getFile", "voice message", or needs to handle media uploads or downloads in a Telegram bot.
---

# grammY — Files & Media

Telegram lets bots send photos, documents, videos, audio, voice notes, video notes, stickers, and animations. grammY exposes a uniform `InputFile` helper for uploads and a `getFile` helper for downloads.

## The three ways to specify a file

When sending, the `photo` / `document` / `video` / etc. parameter accepts one of three forms:

| Form | When |
|---|---|
| `string` (`file_id`) | Reuse a file already on Telegram's servers — cheapest, no upload |
| `string` (URL) | Tell Telegram to fetch the URL itself — no proxy through your server |
| `InputFile` | Upload from a local file, Buffer, Blob, or stream |

```typescript
import { InputFile } from "grammy";

// 1. file_id from a previous message
await ctx.replyWithPhoto(existingFileId);

// 2. URL
await ctx.replyWithPhoto("https://grammy.dev/images/grammY.png");

// 3. Local file
await ctx.replyWithPhoto(new InputFile("./assets/welcome.jpg"));

// 4. Buffer
await ctx.replyWithDocument(
  new InputFile(Buffer.from("hello", "utf8"), "hello.txt"),
);

// 5. Stream
await ctx.replyWithVideo(new InputFile(fs.createReadStream("./demo.mp4"), "demo.mp4"));
```

`file_id` strings are stable for the same file — cache them.

## Send methods reference

Aliases on `ctx` (each has a `ctx.api.send*(chatId, …)` twin for cross-chat sends):

```typescript
await ctx.replyWithPhoto(photo, { caption: "alt text", parse_mode: "Markdown" });
await ctx.replyWithDocument(file);
await ctx.replyWithVideo(video);
await ctx.replyWithAudio(audio);
await ctx.replyWithVoice(voice);
await ctx.replyWithVideoNote(round);
await ctx.replyWithSticker(sticker);
await ctx.replyWithAnimation(gif);
await ctx.replyWithLocation(latitude, longitude);
await ctx.replyWithVenue(latitude, longitude, title, address);
await ctx.replyWithContact(phone, firstName);
await ctx.replyWithDice("🎲");          // 🎲 🎯 🏀 ⚽ 🎳 🎰
await ctx.replyWithPoll(question, options);
```

## Media groups (albums)

A media group sends 2–10 photos/videos/audios/documents as a single album:

```typescript
import { InputMediaBuilder } from "grammy";

await ctx.replyWithMediaGroup([
  InputMediaBuilder.photo(new InputFile("./a.jpg"), { caption: "first" }),
  InputMediaBuilder.photo("https://example.com/b.jpg"),
  InputMediaBuilder.video(new InputFile("./c.mp4")),
]);
```

`InputMediaBuilder` covers `photo`, `video`, `animation`, `audio`, `document`. Albums are core grammY — no plugin is involved (and no official plugin waits for a whole incoming album; each photo arrives as its own update sharing a `media_group_id`).

## Receiving files

Use filter queries to target the media type, then `ctx.getFile()` to retrieve the underlying file:

```typescript
bot.on(":photo", async (ctx) => {
  // Largest photo size
  const photo = ctx.msg.photo!.at(-1)!;
  const file = await ctx.getFile();          // → File obj with file_path
  console.log("file_path:", file.file_path); // e.g. photos/file_42.jpg
});

bot.on(":document", async (ctx) => {
  const file = await ctx.getFile();
  console.log("MIME:", ctx.msg.document!.mime_type);
});

bot.on(":voice", async (ctx) => {
  const file = await ctx.getFile();
  // file.file_path → voice/file_5.oga
});
```

The filter `:file` matches *any* file attachment (photo, live_photo, video, animation, document, audio, voice, video_note, sticker) so you can handle them uniformly; `:media` narrows that to photo, live_photo and video.

## Download a received file

`ctx.getFile()` only gives you metadata (`file_id`, `file_size`, `file_path`). The core `File` type has no `getUrl()` or `download()` — those appear only after you install `@grammyjs/files`. With the core package alone, build the URL by hand:

```typescript
bot.on(":file", async (ctx) => {
  const file = await ctx.getFile();
  // file.file_path → "photos/file_42.jpg"
  const url = `https://api.telegram.org/file/bot${bot.token}/${file.file_path}`;
  const res = await fetch(url);
  const buf = Buffer.from(await res.arrayBuffer());
  await fs.promises.writeFile("./incoming.jpg", buf);
});
```

With the `@grammyjs/files` plugin (`npm i @grammyjs/files`) the same thing is one call:

```typescript
import { Bot, Context } from "grammy";
import { type FileFlavor, hydrateFiles } from "@grammyjs/files";

type MyContext = FileFlavor<Context>;
const bot = new Bot<MyContext>(process.env.BOT_TOKEN!);
bot.api.config.use(hydrateFiles(bot.token));

bot.on(":file", async (ctx) => {
  const file = await ctx.getFile();
  const path = await file.download();          // temp file; file.download("./incoming.bin") picks the location
  console.log("saved to", path, "from", file.getUrl());
});
```

### File size limits

| Action | Bot API limit |
|---|---|
| Send by `file_id` | none — the file already lives on Telegram |
| Send by URL | 5 MB for photos, 20 MB for everything else |
| Send by upload (`InputFile`, multipart) | 10 MB for photos, 50 MB for everything else |
| Download with `getFile` | 20 MB |
| Self-hosted Bot API server | upload up to 2000 MB, download without a limit |

For downloads over 20 MB you need a self-hosted Bot API server. For most bots, link to an external storage URL instead.

## Captions, parse mode, and formatting

```typescript
await ctx.replyWithPhoto(photo, {
  caption: "*Bold* _italic_ [link](https://grammy.dev)",
  parse_mode: "MarkdownV2",   // or "HTML"
});
```

In MarkdownV2 you must escape all `_*[]()~ ` `>#+-=|{}.!` characters that aren't part of formatting. To avoid escaping altogether, build the caption with `@grammyjs/parse-mode` (≥ 2.0) and send entities instead of a parse mode:

```typescript
import { b, fmt } from "@grammyjs/parse-mode";

const cap = fmt`${b}Welcome${b} to the group!`;
await ctx.replyWithPhoto(photo, {
  caption: cap.caption,
  caption_entities: cap.caption_entities,
});
```

## Streaming a generated file

For data you generate on the fly (CSV export, PDF, screenshot), pipe a stream into `InputFile`:

```typescript
import { Readable } from "node:stream";

const rows = ["id,name", "1,Alice", "2,Bob"].join("\n");
await ctx.replyWithDocument(
  new InputFile(Readable.from(rows), "users.csv"),
  { caption: "Latest export" },
);
```

## Common pitfalls

- **Sending a base64 string** as the photo arg — Telegram does NOT accept data URIs. Decode to a `Buffer` first.
- **Re-uploading every time** — once you've sent a photo, store its `file_id` and reuse it. The same `file_id` works across chats for the same bot.
- **HTTP timeout** for large uploads — bump `bot.api.config` `client` options, or use `InputFile` from a stream.
- **Wrong file type filter** — `message:photo` does NOT match documents that happen to be images. If you want any image, use `bot.on([":photo", ":document"])` and check `ctx.msg.document?.mime_type`.
