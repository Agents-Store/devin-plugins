---
name: files-audio
description: >
  This skill should be used when the user asks to "upload a file to Dify", "call
  /files/upload", "send an image to a Dify app", "transcribe audio with Dify",
  "/audio-to-text", "Dify text to speech", or "/text-to-audio". Covers file upload for
  multimodal input and the speech endpoints.
---

# Dify — Files & Audio

Uploading files for multimodal messages, and the speech-to-text / text-to-speech
endpoints. For auth/base URL/`user` see the `setup` skill.

## POST /files/upload — upload a file

Upload once, then reference the returned `id` as `upload_file_id` in a `files` array on
`/chat-messages`, `/completion-messages`, or `/workflows/run` (with
`transfer_method: "local_file"`). Multipart form; the file is scoped to `user`.

```bash
curl -X POST 'https://api.dify.ai/v1/files/upload' \
  --header 'Authorization: Bearer app-XXXX' \
  --form 'file=@/path/to/image.png' \
  --form 'user=user-123'
```

```json
{
  "id": "...",
  "name": "image.png",
  "size": 204800,
  "extension": "png",
  "mime_type": "image/png",
  "created_by": "...",
  "created_at": 1700000000
}
```

Then use it:

```bash
curl -X POST 'https://api.dify.ai/v1/chat-messages' \
  --header 'Authorization: Bearer app-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{
    "query": "Describe this image",
    "inputs": {},
    "response_mode": "blocking",
    "user": "user-123",
    "files": [
      { "type": "image", "transfer_method": "local_file", "upload_file_id": "<id-from-upload>" }
    ]
  }'
```

Allowed extensions/sizes depend on the app's `file_upload` config — check `GET /parameters`
(see `setup` skill). `type` is `image` / `document` / `audio` / `video`.

## GET /files/{file_id}/preview — preview / download an uploaded file

```bash
curl 'https://api.dify.ai/v1/files/{file_id}/preview' \
  --header 'Authorization: Bearer app-XXXX' \
  --output downloaded-file
```

Returns the binary content. Availability depends on Dify version/storage configuration.

## POST /audio-to-text — speech to text

Transcribe an audio file. Multipart form.

```bash
curl -X POST 'https://api.dify.ai/v1/audio-to-text' \
  --header 'Authorization: Bearer app-XXXX' \
  --form 'file=@/path/to/audio.mp3' \
  --form 'user=user-123'
```

```json
{ "text": "transcribed speech here" }
```

Supported formats: `mp3`, `mp4`, `mpeg`, `mpga`, `m4a`, `wav`, `webm` (≤ ~25 MB). Requires
a speech-to-text model configured on the app.

## POST /text-to-audio — text to speech

Generate audio from text (or from an existing `message_id`).

```bash
curl -X POST 'https://api.dify.ai/v1/text-to-audio' \
  --header 'Authorization: Bearer app-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{ "text": "Hello from Dify", "user": "user-123" }' \
  --output speech.mp3
```

You may pass `message_id` instead of `text` to synthesize an existing answer. Requires a
text-to-speech model configured on the app. Returns binary audio (`audio/wav` or
`audio/mp3`).

## Endpoint summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/files/upload` | POST | Upload a file for multimodal input |
| `/files/{file_id}/preview` | GET | Preview / download an uploaded file |
| `/audio-to-text` | POST | Transcribe audio → text |
| `/text-to-audio` | POST | Synthesize text → audio |

## Tips

- Upload is the prerequisite for `transfer_method: "local_file"`. For files already on the
  web, skip upload and use `transfer_method: "remote_url"` with a `url`.
- Audio endpoints need the corresponding STT/TTS model enabled in the app's settings;
  otherwise you'll get a model/config error (see `troubleshoot`).
