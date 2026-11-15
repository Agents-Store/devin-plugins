"""Creative generation through OpenAI, Gemini and fal.ai: images, video, voice, music, analysis.

No model id is built in. Providers retire models every few months, so a model
comes from --model, from ads/config.json, or from asking the provider what it
offers today (list_models / pick).
"""
from __future__ import annotations

import base64
import json
import re
import shutil
import subprocess
import time
import urllib.parse
from pathlib import Path

from .core import (AdsError, HttpError, Refused, append_jsonl, b64_file, download, guess_type, join_url, multipart, now,
                   read_file, request, save_config, slug)

OPENAI_ROOT = "https://api.openai.com/v1"
GEMINI_ROOT = "https://generativelanguage.googleapis.com/v1beta"
FAL_QUEUE = "https://queue.fal.run"
FAL_API = "https://api.fal.ai/v1"
FAL_STORAGE = "https://rest.fal.ai/storage/upload/initiate"
FAL_SCHEMA = "https://fal.ai/api/openapi/queue/openapi.json"

PROVIDERS = ("gemini", "openai", "fal")
PROVIDER_KEYS = {"openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY", "fal": "FAL_KEY"}
KINDS = ("image", "video", "speech", "music", "analysis")
SUPPORT = {"image": ("gemini", "openai", "fal"), "video": ("gemini", "fal"), "speech": ("gemini", "openai", "fal"),
           "music": ("gemini", "fal"), "analysis": ("gemini", "openai")}
FAL_CATEGORY = {"image": "text-to-image", "video": "text-to-video", "speech": "text-to-speech", "music": "text-to-audio"}
# Pixel sizes for OpenAI: both edges are multiples of 16.
OPENAI_SIZE = {"1:1": "1024x1024", "4:5": "1088x1360", "9:16": "1152x2048", "16:9": "2048x1152", "1.91:1": "1216x640"}
GEMINI_ASPECTS = ("1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9")
FAL_IMAGE_SIZE = {"1:1": "square_hd", "4:5": "portrait_4_3", "9:16": "portrait_16_9", "16:9": "landscape_16_9",
                  "1.91:1": "landscape_16_9"}
EXTENSIONS = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp", "image/gif": ".gif",
              "video/mp4": ".mp4", "video/quicktime": ".mov", "video/webm": ".webm",
              "audio/wav": ".wav", "audio/x-wav": ".wav", "audio/mpeg": ".mp3", "audio/mp3": ".mp3", "audio/ogg": ".ogg"}
RE_DATED = re.compile(r"\d{4}-\d{2}-\d{2}|-\d{4}$")
RE_VERSION = re.compile(r"(\d+(?:\.\d+)?)")


# ── shared helpers ───────────────────────────────────────────────────────

def ratio_of(aspect):
    left, right = aspect.split(":")
    return float(left) / float(right)


def nearest_aspect(aspect, allowed):
    if aspect in allowed:
        return aspect
    return min(allowed, key=lambda a: abs(ratio_of(a) - ratio_of(aspect)))


def aspect_from_size(size):
    width, height = (int(x) for x in size.lower().split("x"))
    return min(OPENAI_SIZE, key=lambda a: abs(ratio_of(a) - width / height)), width, height


def out_dir(ctx, out):
    target = Path(out) if out else ctx.ws / "creatives"
    target.mkdir(parents=True, exist_ok=True)
    return target


def target_path(folder, stem, suffix, named=False):
    """Where a generated file goes: NAME.ext for a name the user gave, else a name with a timestamp.

    An existing file is never overwritten; the next free NAME-2.ext, NAME-3.ext is used.
    """
    base = stem if named else "%s-%s" % (stem, time.strftime("%Y%m%d-%H%M%S"))
    number = 1
    while True:
        path = folder / ("%s%s%s" % (base, "" if number == 1 else "-%d" % number, suffix))
        if not path.exists():
            return path
        number += 1


def record(ctx, path, kind, provider, model, prompt, **extra):
    entry = {"ts": now(), "file": str(path), "kind": kind, "provider": provider, "model": model, "prompt": prompt}
    entry.update({k: v for k, v in extra.items() if v not in (None, "", [])})
    append_jsonl(ctx.ws / "creatives" / "manifest.jsonl", entry)
    return entry


def fit(path, size):
    """Scale and centre-crop an image to an exact pixel size. Needs ffmpeg; returns None without it."""
    if not shutil.which("ffmpeg"):
        return None
    width, height = (int(x) for x in size.lower().split("x"))
    target = path.with_name("%s-%dx%d%s" % (path.stem, width, height, path.suffix))
    chain = "scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d" % (width, height, width, height)
    done = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(path), "-vf", chain, str(target)],
                          capture_output=True, text=True)
    if done.returncode != 0:
        raise AdsError("ffmpeg could not resize %s: %s" % (path.name, done.stderr.strip()[:200]))
    return target


def default_provider(ctx, kind, wanted=None):
    if wanted:
        if wanted not in SUPPORT[kind]:
            raise Refused("%s cannot make %s; use one of: %s" % (wanted, kind, ", ".join(SUPPORT[kind])))
        return wanted
    saved = ctx.config.get("models", {}).get(kind, {})
    if saved.get("provider") in SUPPORT[kind] and ctx.key(PROVIDER_KEYS[saved["provider"]], required=False):
        return saved["provider"]
    for name in SUPPORT[kind]:
        if ctx.key(PROVIDER_KEYS[name], required=False):
            return name
    ctx.key(PROVIDER_KEYS[SUPPORT[kind][0]])  # raises MissingKey with the hint


def resolve_model(ctx, kind, provider, wanted=None):
    """--model, then the default saved by models --pick, then a remembered pick for this provider."""
    if wanted:
        return wanted
    saved = ctx.config.get("models", {}).get(kind, {})
    if saved.get("provider") == provider and saved.get("model"):
        return saved["model"]
    cache = ctx.config.setdefault("model_cache", {}).setdefault(provider, {})
    if not cache.get(kind):
        cache[kind] = pick(ctx, provider, kind)
        if (ctx.ws / "config.json").is_file():
            save_config(ctx.ws, ctx.config)
    return cache[kind]


# ── model discovery ──────────────────────────────────────────────────────

def version_of(model_id):
    found = RE_VERSION.findall(model_id)
    return float(found[0]) if found else 0.0


def _classify_openai(model_id):
    if RE_DATED.search(model_id):
        return None
    if model_id.startswith("gpt-image") or "image" in model_id:
        return "image"
    if "tts" in model_id:
        return "speech"
    if any(x in model_id for x in ("audio", "realtime", "transcribe", "whisper", "search", "codex", "embedding", "moderation")):
        return None
    return "analysis" if model_id.startswith("gpt-") else None


def _classify_gemini(model_id):
    if any(x in model_id for x in ("preview", "exp", "live", "embedding", "transcribe", "native-audio")):
        return None
    if model_id.endswith("-tts"):
        return "speech"
    if model_id.startswith("lyria"):
        return "music"
    if "omni" in model_id or model_id.startswith("veo"):
        return "video"
    if "image" in model_id or "banana" in model_id:
        return "image"
    return "analysis" if model_id.startswith("gemini") else None


def list_models(ctx, provider, kind=None, query=None):
    rows = []
    if provider == "openai":
        data = _openai(ctx, "GET", "models")
        for item in data.get("data", []):
            found = _classify_openai(item["id"])
            if found:
                rows.append({"provider": provider, "id": item["id"], "kind": found})
    elif provider == "gemini":
        data = request("GET", join_url(GEMINI_ROOT, "models"), headers=_gemini_headers(ctx), params={"pageSize": 1000}).json()
        for item in data.get("models", []):
            model_id = item.get("name", "").split("/", 1)[-1]
            found = _classify_gemini(model_id)
            if found:
                rows.append({"provider": provider, "id": model_id, "kind": found, "name": item.get("displayName")})
    elif provider == "fal":
        searches = [{"q": query}] if query else [{"category": FAL_CATEGORY[k]} for k in ([kind] if kind else KINDS)
                                                  if k in FAL_CATEGORY]
        for extra in searches:
            params = {"status": "active", "limit": 15}
            params.update(extra)
            data = request("GET", join_url(FAL_API, "models"), headers=_fal_headers(ctx), params=params).json()
            for item in data.get("models", []):
                meta = item.get("metadata", {})
                category = meta.get("category") or ""
                text = (meta.get("display_name", "") + " " + item.get("endpoint_id", "")).lower()
                if category.endswith("-to-image"):
                    found = "image"
                elif category.endswith("-to-video"):
                    found = "video"
                elif category == "text-to-speech" or (category == "text-to-audio" and "music" not in text):
                    found = "speech"
                elif category == "text-to-audio":
                    found = "music"
                else:
                    found = category or "other"
                rows.append({"provider": provider, "id": item.get("endpoint_id"), "kind": found,
                             "name": meta.get("display_name"), "category": category,
                             "license": meta.get("license_type"), "retires_at": item.get("retires_at")})
    else:
        raise Refused("unknown provider %s" % provider)
    if kind:
        rows = [r for r in rows if r["kind"] == kind]
    if query and provider != "fal":
        rows = [r for r in rows if query.lower() in r["id"].lower()]
    return rows


def pick(ctx, provider, kind, save=False):
    """Choose a sensible default among what the provider offers now."""
    if provider not in SUPPORT[kind]:
        raise Refused("%s cannot make %s" % (provider, kind))
    rows = list_models(ctx, provider, kind)
    if not rows:
        raise AdsError("%s lists no %s model for this key" % (provider, kind),
                       "check billing and tier of the account, or pass --model")
    if provider == "fal":
        chosen = rows[0]["id"]
    elif provider == "openai" and kind == "analysis":
        raise Refused("pick an OpenAI text model yourself: prices differ a lot",
                      "run models --provider openai --kind analysis, then pass --model")
    else:
        def rank(row):
            model_id = row["id"]
            score = version_of(model_id)
            if kind == "image":
                score += 100 if ("banana" in model_id or model_id.startswith("gpt-image")) else 0
                score -= 0.05 if any(x in model_id for x in ("pro", "sunburst", "mini", "lite", "latest")) else 0
            if kind in ("speech", "analysis"):
                score -= 0.05 if any(x in model_id for x in ("lite", "pro", "hd", "nano")) else 0
            if kind == "analysis":
                score += 100 if model_id.endswith("-flash") else 0
            return score
        chosen = max(rows, key=rank)["id"]
    if save:
        ctx.config.setdefault("models", {})[kind] = {"provider": provider, "model": chosen}
        if (ctx.ws / "config.json").is_file():
            save_config(ctx.ws, ctx.config)
    return chosen


# ── OpenAI ───────────────────────────────────────────────────────────────

def _openai(ctx, method, path, body=None, data=None, headers=None, timeout=300, raw=False):
    sent = {"Authorization": "Bearer " + ctx.key("OPENAI_API_KEY")}
    sent.update(headers or {})
    try:
        resp = request(method, join_url(OPENAI_ROOT, path), headers=sent, json_body=body, data=data, timeout=timeout)
    except HttpError as exc:
        error = (exc.json() or {}).get("error", {})
        code = error.get("code") or error.get("type") or exc.status
        hint = ""
        if code == "moderation_blocked":
            hint = "the prompt or a reference image was blocked: rewrite it, do not resend it unchanged"
        elif code == "insufficient_quota":
            hint = "the account has no credit: add prepaid credit on the billing page"
        elif exc.status == 403:
            hint = "the organization may need verification for this model: see the organization settings page"
        elif exc.status == 404:
            hint = "the model was retired or is not available to this key: run models --provider openai --pick"
        raise AdsError("OpenAI error %s: %s" % (code, error.get("message", exc.body[:300])), hint)
    return resp.raw if raw else resp.json()


def _openai_image(ctx, model, prompt, aspect, size, n, quality, refs, transparent):
    pixel = size or OPENAI_SIZE[aspect]
    width, height = (max(16, int(round(int(x) / 16.0)) * 16) for x in pixel.lower().split("x"))
    fields = {"model": model, "prompt": prompt, "size": "%dx%d" % (width, height), "n": int(n)}
    if quality:
        fields["quality"] = quality
    if transparent:
        fields["background"] = "transparent"
        fields["output_format"] = "png"
    if refs:
        files = [("image[]", Path(r).name, read_file(r), guess_type(r)) for r in refs]
        ctype, body = multipart({k: str(v) for k, v in fields.items()}, files)
        data = _openai(ctx, "POST", "images/edits", data=body, headers={"Content-Type": ctype}, timeout=600)
    else:
        data = _openai(ctx, "POST", "images/generations", body=fields, timeout=600)
    fmt = data.get("output_format", "png")
    return [(base64.b64decode(item["b64_json"]), ".jpg" if fmt == "jpeg" else "." + fmt) for item in data.get("data", [])]


def _openai_speech(ctx, model, text, voice):
    return _openai(ctx, "POST", "audio/speech", raw=True,
                   body={"model": model, "input": text, "voice": voice or "alloy", "response_format": "mp3"}), ".mp3"


def _openai_analyze(ctx, model, prompt, file, link):
    content = [{"type": "input_text", "text": prompt}]
    if file:
        if not guess_type(file).startswith("image/"):
            raise Refused("OpenAI analysis takes images only; use --provider gemini for video")
        content.append({"type": "input_image", "image_url": "data:%s;base64,%s" % (guess_type(file), b64_file(file))})
    elif link:
        content.append({"type": "input_image", "image_url": link})
    data = _openai(ctx, "POST", "responses", body={"model": model, "input": [{"role": "user", "content": content}]})
    texts = []
    for item in data.get("output", []):
        for part in item.get("content", []) or []:
            if part.get("type") == "output_text":
                texts.append(part.get("text", ""))
    return "\n".join(texts).strip()


# ── Gemini ───────────────────────────────────────────────────────────────

def _gemini_headers(ctx):
    return {"x-goog-api-key": ctx.key("GEMINI_API_KEY"), "Api-Revision": ctx.api("gemini_revision")}


def _gemini(ctx, body, timeout=900):
    try:
        return request("POST", join_url(GEMINI_ROOT, "interactions"), headers=_gemini_headers(ctx), json_body=body,
                       timeout=timeout).json()
    except HttpError as exc:
        error = (exc.json() or {}).get("error", {})
        code = error.get("code") or exc.status
        hint = ""
        if exc.status == 402:
            hint = "the prepaid balance is empty: top up the billing account linked to the key"
        elif exc.status == 429:
            hint = "rate or daily limit of the tier reached: wait, or lower the volume"
        elif exc.status == 404:
            hint = "the model was retired or is not available to this key: run models --provider gemini --pick"
        elif "safety" in str(code) or "prohibited" in str(code):
            hint = "blocked by the safety filter: rewrite the prompt, do not resend it unchanged"
        elif exc.status == 403:
            hint = "the key may be restricted or image, video and music may need the paid tier"
        raise AdsError("Gemini error %s: %s" % (code, error.get("message", exc.body[:300])), hint)


def _gemini_parts(data, kind):
    parts = []
    for step in data.get("steps", []):
        if step.get("type") != "model_output":
            continue
        parts.extend(p for p in step.get("content", []) or [] if p.get("type") == kind)
    return parts


def _gemini_media(ctx, data, kind, fallback):
    """Decode inline media, or fetch a file the API handed back by URI."""
    found = []
    for part in _gemini_parts(data, kind):
        suffix = EXTENSIONS.get(part.get("mime_type", ""), fallback)
        if part.get("data"):
            found.append((base64.b64decode(part["data"]), suffix))
        elif part.get("uri"):
            found.append((_gemini_file(ctx, part["uri"]), suffix))
    if not found:
        status = data.get("status")
        raise AdsError("Gemini returned no %s (status %s)" % (kind, status),
                       "the request may have been filtered: adjust the prompt")
    return found


def _gemini_file(ctx, uri):
    file_id = uri.split(":download")[0].rstrip("/").split("/")[-1]
    info_url = join_url(GEMINI_ROOT, "files", file_id)
    for _ in range(120):
        state = request("GET", info_url, headers=_gemini_headers(ctx)).json().get("state")
        if state == "ACTIVE":
            break
        if state == "FAILED":
            raise AdsError("Gemini failed to prepare the generated file")
        time.sleep(5)
    return request("GET", info_url + ":download", headers=_gemini_headers(ctx), params={"alt": "media"}, timeout=600).raw


def _gemini_inputs(prompt, files):
    parts = [{"type": "text", "text": prompt}]
    for item in files or []:
        mime = guess_type(item)
        parts.append({"type": "video" if mime.startswith("video/") else "image", "mime_type": mime, "data": b64_file(item)})
    return parts


def _gemini_image(ctx, model, prompt, aspect, size, n, quality, refs):
    tier = {"low": "1K", "medium": "1K", "high": "2K"}.get(quality or "medium", "1K")
    if size:
        aspect, width, height = aspect_from_size(size)
        tier = "1K" if max(width, height) <= 1400 else ("2K" if max(width, height) <= 2800 else "4K")
    body = {"model": model, "input": _gemini_inputs(prompt, refs),
            "response_format": {"type": "image", "aspect_ratio": nearest_aspect(aspect, GEMINI_ASPECTS), "image_size": tier}}
    results = []
    for _ in range(int(n)):  # the API has no count parameter: one call per image
        results.extend(_gemini_media(ctx, _gemini(ctx, body), "image", ".png")[:1])
    return results


def _gemini_video(ctx, model, prompt, aspect, seconds, resolution, image):
    if aspect not in ("9:16", "16:9"):
        raise Refused("Gemini video comes in 9:16 or 16:9 only", "use --provider fal for another ratio, or crop afterwards")
    fmt = {"type": "video", "aspect_ratio": aspect, "resolution": resolution, "duration": "%ds" % int(seconds)}
    if resolution not in ("360p", "720p"):
        fmt["delivery"] = "uri"
    body = {"model": model, "response_format": fmt}
    body["input"] = _gemini_inputs(prompt, [image]) if image else prompt
    return _gemini_media(ctx, _gemini(ctx, body, timeout=1200), "video", ".mp4")[-1:]


def _gemini_audio(ctx, model, text, voice=None, speech=True):
    body = {"model": model, "response_format": {"type": "audio"}}
    if speech:
        body["input"] = [{"type": "user_input", "content": [{"type": "text", "text": text}]}]
        body["generation_config"] = {"speech_config": [{"voice": voice or "Kore"}]}
    else:
        body["input"] = text
    return _gemini_media(ctx, _gemini(ctx, body, timeout=900), "audio", ".wav" if speech else ".mp3")[-1]


def _gemini_analyze(ctx, model, prompt, file, link):
    if file:
        parts = _gemini_inputs(prompt, [file])
    elif link and re.search(r"youtube\.com|youtu\.be", link):
        parts = [{"type": "text", "text": prompt}, {"type": "video", "uri": link}]
    elif link:
        fetched = request("GET", link, timeout=120)
        mime = fetched.headers.get("Content-Type", "image/jpeg").split(";")[0]
        parts = [{"type": "text", "text": prompt},
                 {"type": "video" if mime.startswith("video/") else "image", "mime_type": mime,
                  "data": base64.b64encode(fetched.raw).decode("ascii")}]
    else:
        parts = [{"type": "text", "text": prompt}]
    data = _gemini(ctx, {"model": model, "input": parts})
    return "\n".join(p.get("text", "") for p in _gemini_parts(data, "text")).strip()


# ── fal.ai ───────────────────────────────────────────────────────────────

def _fal_headers(ctx):
    return {"Authorization": "Key " + ctx.key("FAL_KEY")}


def _fal_error(exc):
    payload = exc.json() or {}
    detail = payload.get("detail")
    hint = ""
    if isinstance(detail, list) and detail:
        first = detail[0]
        text = "%s: %s" % (first.get("type", "error"), first.get("msg", ""))
        if first.get("loc"):
            text += " (field %s)" % ".".join(str(x) for x in first["loc"])
        if first.get("type") == "content_policy_violation":
            hint = "blocked by the content filter: change the prompt or the input image"
    else:
        text = str(detail or payload or exc.body[:300])
    if exc.status in (401, 403):
        hint = "the key is wrong, lacks the API preset, or the balance is exhausted and the account is locked"
    return AdsError("fal.ai error %s: %s" % (exc.status, text), hint)


def fal_schema(ctx, model):
    try:
        spec = request("GET", FAL_SCHEMA, params={"endpoint_id": model}).json()
    except HttpError as exc:
        raise AdsError("fal.ai has no schema for %s (HTTP %s)" % (model, exc.status),
                       "check the id with models --provider fal --query")
    schemas = spec.get("components", {}).get("schemas", {})
    name = next((n for n in schemas if n.endswith("Input")), None)
    if not name:
        return {"model": model, "fields": []}
    required = schemas[name].get("required", [])
    fields = []
    for prop, info in schemas[name].get("properties", {}).items():
        options = info.get("enum")
        kind = info.get("type")
        for alt in info.get("anyOf", []) or []:
            options = options or alt.get("enum")
            kind = kind or alt.get("type") or ("object" if "$ref" in alt else None)
        fields.append({"name": prop, "type": kind, "required": prop in required, "default": info.get("default"),
                       "options": options, "description": (info.get("description") or "")[:140]})
    return {"model": model, "fields": fields}


def fal_upload(ctx, path):
    path = Path(path)
    content = read_file(path)
    try:
        ticket = request("POST", FAL_STORAGE, headers=_fal_headers(ctx), params={"storage_type": "fal-cdn-v3"},
                         json_body={"content_type": guess_type(path), "file_name": path.name}).json()
        request("PUT", ticket["upload_url"], headers={"Content-Type": guess_type(path)}, data=content, timeout=900)
    except HttpError as exc:
        raise _fal_error(exc)
    return ticket["file_url"]


def _fal_expand(ctx, value):
    """{"@upload": "file"} becomes the URL of that file on fal storage."""
    if isinstance(value, dict):
        if set(value) == {"@upload"}:
            return fal_upload(ctx, value["@upload"])
        return {k: _fal_expand(ctx, v) for k, v in value.items()}
    if isinstance(value, list):
        return [_fal_expand(ctx, v) for v in value]
    return value


def _urls(value, found):
    if isinstance(value, dict):
        if isinstance(value.get("url"), str) and value["url"].startswith("http"):
            found.append((value["url"], value.get("content_type") or ""))
        for item in value.values():
            _urls(item, found)
    elif isinstance(value, list):
        for item in value:
            _urls(item, found)
    return found


def fal_run(ctx, model, payload, out=None, name=None, kind="fal", prompt=None, wait=1800, named=None):
    """Submit to the queue, wait, fetch the result and download every file it points to."""
    named = bool(name) if named is None else named
    payload = _fal_expand(ctx, payload)
    try:
        ticket = request("POST", join_url(FAL_QUEUE, model), headers=_fal_headers(ctx), json_body=payload, timeout=120).json()
        deadline = time.time() + wait
        while True:
            status = request("GET", ticket["status_url"], headers=_fal_headers(ctx), timeout=60).json()
            if status.get("status") == "COMPLETED":
                break
            if time.time() > deadline:
                raise AdsError("fal.ai request %s is still running after %d s" % (ticket.get("request_id"), wait),
                               "fetch it later: fal.ai keeps results for a limited time")
            time.sleep(3)
        result = request("GET", ticket["response_url"], headers=_fal_headers(ctx), timeout=120).json()
    except HttpError as exc:
        raise _fal_error(exc)
    folder = out_dir(ctx, out)
    stem = slug(name or prompt or model.split("/")[-1])
    files = []
    for link, ctype in _urls(result, []):
        suffix = EXTENSIONS.get(ctype) or Path(urllib.parse.urlsplit(link).path).suffix or ".bin"
        path = download(link, target_path(folder, stem, suffix, named=named))
        record(ctx, path, kind, "fal", model, prompt or payload.get("prompt"), source_url=link)
        files.append(str(path))
    return {"model": model, "files": files, "result": result}


def _fal_fields(ctx, model):
    return {f["name"]: f for f in fal_schema(ctx, model)["fields"]}


def _fal_choice(field, wanted):
    options = field.get("options")
    if not options or wanted in options:
        return wanted
    numeric = [o for o in options if re.fullmatch(r"\d+(\.\d+)?", str(o))]
    if numeric and re.fullmatch(r"\d+(\.\d+)?", str(wanted)):
        return min(numeric, key=lambda o: abs(float(o) - float(wanted)))
    if all(re.fullmatch(r"\d+:\d+", str(o)) for o in options if o not in ("auto", None)) and ":" in str(wanted):
        return nearest_aspect(wanted, [o for o in options if o not in ("auto", None)])
    return options[0]


def _fal_image_payload(ctx, model, prompt, aspect, size, n, refs):
    fields = _fal_fields(ctx, model)
    payload = {"prompt": prompt}
    if size:
        aspect, width, height = aspect_from_size(size)
    if "aspect_ratio" in fields:
        payload["aspect_ratio"] = _fal_choice(fields["aspect_ratio"], aspect)
    elif "image_size" in fields:
        payload["image_size"] = {"width": width, "height": height} if size else FAL_IMAGE_SIZE[aspect]
    if "num_images" in fields:
        payload["num_images"] = int(n)
    if refs:
        if "image_urls" in fields:
            payload["image_urls"] = [{"@upload": r} for r in refs]
        elif "image_url" in fields:
            payload["image_url"] = {"@upload": refs[0]}
        else:
            raise Refused("%s takes no reference image" % model, "pick an image-to-image model: models --provider fal --query edit")
    return payload


def _fal_video_payload(ctx, model, prompt, aspect, seconds, resolution, image):
    fields = _fal_fields(ctx, model)
    payload = {"prompt": prompt}
    if "aspect_ratio" in fields:
        payload["aspect_ratio"] = _fal_choice(fields["aspect_ratio"], aspect)
    if "duration" in fields:
        choice = _fal_choice(fields["duration"], str(int(seconds)))
        payload["duration"] = choice if fields["duration"].get("type") == "string" or fields["duration"].get("options") else int(seconds)
    if "resolution" in fields:
        payload["resolution"] = _fal_choice(fields["resolution"], resolution)
    if image:
        key = next((k for k in ("image_url", "first_frame_url", "start_image_url") if k in fields), None)
        if not key:
            raise Refused("%s takes no first frame" % model, "pick an image-to-video model: models --provider fal --query image-to-video")
        payload[key] = {"@upload": image}
    return payload


# ── commands ─────────────────────────────────────────────────────────────

def image(ctx, prompt, provider=None, model=None, aspect=None, size=None, n=1, quality=None, refs=None,
          transparent=False, out=None, name=None, fit_size=None):
    if aspect and aspect not in OPENAI_SIZE:
        raise Refused("unknown aspect %s; use one of %s or --size WxH" % (aspect, ", ".join(OPENAI_SIZE)))
    aspect = aspect or ("1:1" if not size else aspect_from_size(size)[0])
    provider = default_provider(ctx, "image", provider)
    model = resolve_model(ctx, "image", provider, model)
    stem = slug(name or prompt)
    folder = out_dir(ctx, out)
    saved = []
    if provider == "fal":
        if transparent:
            raise Refused("--transparent works with OpenAI; on fal.ai run a background-removal model with fal run")
        result = fal_run(ctx, model, _fal_image_payload(ctx, model, prompt, aspect, size, n, refs), out=out, name=stem,
                         kind="image", prompt=prompt, named=bool(name))
        saved = [Path(p) for p in result["files"]]
    else:
        if provider == "gemini" and transparent:
            raise Refused("--transparent works with OpenAI only")
        if provider == "openai":
            blobs = _openai_image(ctx, model, prompt, aspect, size, n, quality, refs, transparent)
        else:
            blobs = _gemini_image(ctx, model, prompt, aspect, size, n, quality, refs)
        for blob, suffix in blobs:
            path = target_path(folder, stem, suffix, named=bool(name))
            path.write_bytes(blob)
            record(ctx, path, "image", provider, model, prompt, aspect=aspect, size=size, refs=refs)
            saved.append(path)
    out_rows = []
    for path in saved:
        row = {"file": str(path)}
        if fit_size:
            fitted = fit(path, fit_size)
            row["fitted"] = str(fitted) if fitted else "ffmpeg not found: resize by hand to %s" % fit_size
            if fitted:
                record(ctx, fitted, "image", provider, model, prompt, derived_from=str(path), size=fit_size)
        out_rows.append(row)
    return {"provider": provider, "model": model, "aspect": aspect, "files": out_rows}


def video(ctx, prompt, provider=None, model=None, aspect="9:16", seconds=8, resolution="720p", image_file=None,
          out=None, name=None):
    provider = default_provider(ctx, "video", provider)
    model = resolve_model(ctx, "video", provider, model)
    stem = slug(name or prompt)
    if provider == "fal":
        result = fal_run(ctx, model, _fal_video_payload(ctx, model, prompt, aspect, seconds, resolution, image_file),
                         out=out, name=stem, kind="video", prompt=prompt, named=bool(name))
        files = result["files"]
    else:
        if not 3 <= int(seconds) <= 15:
            raise Refused("Gemini video lasts 3 to 15 seconds")
        files = []
        for blob, suffix in _gemini_video(ctx, model, prompt, aspect, seconds, resolution, image_file):
            path = target_path(out_dir(ctx, out), stem, suffix, named=bool(name))
            path.write_bytes(blob)
            record(ctx, path, "video", provider, model, prompt, aspect=aspect, seconds=seconds, resolution=resolution)
            files.append(str(path))
    return {"provider": provider, "model": model, "aspect": aspect, "seconds": seconds, "files": files}


def _audio(ctx, kind, text, provider, model, voice, out):
    provider = default_provider(ctx, kind, provider)
    model = resolve_model(ctx, kind, provider, model)
    if provider == "fal":
        fields = _fal_fields(ctx, model)
        payload = {("text" if "text" in fields else "prompt"): text}
        if voice and "voice" in fields:
            payload["voice"] = voice
        result = fal_run(ctx, model, payload, out=str(Path(out).parent) if out else None, name=Path(out).stem if out else None,
                         kind=kind, prompt=text)
        return {"provider": provider, "model": model, "files": result["files"]}
    if provider == "openai":
        blob, suffix = _openai_speech(ctx, model, text, voice)
    else:
        blob, suffix = _gemini_audio(ctx, model, text, voice, speech=kind == "speech")
    path = Path(out) if out else target_path(out_dir(ctx, None), slug(text, 32), suffix)
    if path.suffix != suffix:
        path = path.with_suffix(suffix)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    record(ctx, path, kind, provider, model, text, voice=voice)
    return {"provider": provider, "model": model, "files": [str(path)]}


def speech(ctx, text, provider=None, model=None, voice=None, out=None):
    return _audio(ctx, "speech", text, provider, model, voice, out)


def music(ctx, prompt, provider=None, model=None, out=None):
    return _audio(ctx, "music", prompt, provider, model, None, out)


def analyze(ctx, prompt, file=None, link=None, provider=None, model=None):
    if not file and not link:
        raise Refused("give --file or --url")
    provider = default_provider(ctx, "analysis", provider)
    model = resolve_model(ctx, "analysis", provider, model)
    if provider == "openai":
        return _openai_analyze(ctx, model, prompt, file, link)
    return _gemini_analyze(ctx, model, prompt, file, link)


def check(ctx, provider):
    if provider == "openai":
        rows = list_models(ctx, "openai")
        return "%d image and %d speech models available" % (sum(r["kind"] == "image" for r in rows),
                                                             sum(r["kind"] == "speech" for r in rows))
    if provider == "gemini":
        rows = list_models(ctx, "gemini")
        kinds = sorted({r["kind"] for r in rows})
        return "%d generation models listed (%s)" % (len(rows), ", ".join(kinds))
    first = request("GET", join_url(FAL_API, "models"), headers=_fal_headers(ctx), params={"limit": 1, "status": "active"}).json()
    endpoint = (first.get("models") or [{}])[0].get("endpoint_id", "")
    try:
        request("GET", join_url(FAL_API, "models", "pricing"), headers=_fal_headers(ctx), params={"endpoint_id": endpoint}).json()
    except HttpError as exc:
        raise _fal_error(exc)
    return "key accepted"


def dump(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False)
