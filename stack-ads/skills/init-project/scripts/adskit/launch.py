"""Launch plans: one reviewed JSON file per campaign, dry run first, everything paused, a ledger for rollback.

A plan step is {"id": ..., "do": ..., "with": {...}}. Later steps refer to the
result of earlier ones as {{step.field}}. The ledger (ads/launch/ledger.jsonl)
remembers what each applied step created, so an interrupted apply resumes where
it stopped and a rollback knows what to undo.

What the ledger also holds, so that the plan file and the ad account cannot
drift apart unnoticed: a fingerprint of every dry run, a hash of every applied
step, a mark before every send, and every object a rollback removed.
"""
from __future__ import annotations

import hashlib
import http.client
import json
import re
import socket
import ssl
import time
import urllib.error
from datetime import datetime
from pathlib import Path

from . import google, guards, meta, tiktok
from .core import AdsError, HttpError, Refused, append_jsonl, b64_file, now, read_jsonl

STEP_KINDS = ("google.mutate", "meta.post", "meta.upload_image", "meta.upload_video",
              "tiktok.post", "tiktok.upload_video", "tiktok.upload_image")
RE_REF = re.compile(r"\{\{\s*([A-Za-z0-9_-]+)\.([A-Za-z0-9_.-]+)\s*\}\}")
RE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}")
META_TYPES = {"campaigns": "campaign", "adsets": "adset", "ads": "ad", "adcreatives": "creative"}
SELF = "python3 ads/tools/ads.py"
# The ids a plan is aimed at: a dry run holds only for the account it looked at.
ACCOUNT_KEYS = {"google": ("GOOGLE_ADS_CUSTOMER_ID", "GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
                "meta": ("META_AD_ACCOUNT_ID", "META_PAGE_ID", "META_PIXEL_ID", "META_INSTAGRAM_USER_ID"),
                "tiktok": ("TIKTOK_ADVERTISER_ID", "TIKTOK_PIXEL_ID")}
# What activate, pause and remove act on, parents first.
SWITCHED = {"google": ("campaigns", "adGroups", "assetGroups", "adGroupAds"),
            "meta": ("campaign", "adset", "ad"),
            "tiktok": ("campaign", "adgroup", "ad")}


class Unresolved(Exception):
    pass


# ── plan file ────────────────────────────────────────────────────────────

def load_plan(path):
    path = Path(path)
    if not path.is_file():
        raise Refused("plan file not found: %s" % path)
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise Refused("%s is not valid JSON: %s" % (path, exc))
    if not isinstance(plan, dict):
        raise Refused("%s must hold one JSON object" % path)
    for field in ("name", "platform", "steps"):
        if not plan.get(field):
            raise Refused("the plan needs \"%s\"" % field)
    if not RE_NAME.fullmatch(str(plan["name"])):
        # The name becomes a file name and the key of the plan in the ledger.
        raise Refused("the plan name %r must be a plain name: letters, digits, _ and -, at most 80 characters" % plan["name"])
    if plan["platform"] not in ("google", "meta", "tiktok"):
        raise Refused("platform must be google, meta or tiktok")
    if not isinstance(plan["steps"], list):
        raise Refused("\"steps\" must be a list")
    seen = set()
    for index, step in enumerate(plan["steps"]):
        if not isinstance(step, dict) or not step.get("id") or step.get("do") not in STEP_KINDS:
            raise Refused("step %d needs an id and a do among: %s" % (index, ", ".join(STEP_KINDS)))
        if not RE_NAME.fullmatch(str(step["id"])):
            raise Refused("step id %r must be a plain name: letters, digits, _ and -" % step["id"])
        if not step["do"].startswith(plan["platform"] + "."):
            raise Refused("step %s uses %s in a %s plan" % (step["id"], step["do"], plan["platform"]))
        if step["id"] in seen:
            raise Refused("step id %s is used twice" % step["id"])
        seen.add(step["id"])
        step.setdefault("with", {})
        if not isinstance(step["with"], dict):
            raise Refused("step %s: \"with\" must be an object" % step["id"])
        if step["do"] == "google.mutate":
            # campaign_operation and campaignOperation are the same to Google: keep one spelling from here on.
            step["with"] = guards.google_canonical(step["with"])
        if step["do"] == "google.mutate" and step["with"].get("partialFailure"):
            raise Refused("step %s asks for partialFailure" % step["id"],
                          "a plan step is applied whole or not at all, so the ledger knows what exists: remove the field")
    return plan


def lookup(result, dotted):
    value = result
    for part in dotted.split("."):
        if isinstance(value, list) and part.isdigit() and int(part) < len(value):
            value = value[int(part)]
        elif isinstance(value, dict) and part in value:
            value = value[part]
        else:
            raise KeyError(dotted)
    return value


def resolve(value, results):
    """Replace {{step.field}} with values of earlier steps and {"@base64": file} with file content."""
    if isinstance(value, dict):
        if set(value) == {"@base64"}:
            return b64_file(value["@base64"])
        return {k: resolve(v, results) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve(v, results) for v in value]
    if not isinstance(value, str):
        return value

    def swap(match):
        step, field = match.group(1), match.group(2)
        if step not in results:
            raise Unresolved(match.group(0))
        try:
            return str(lookup(results[step], field))
        except KeyError:
            raise Refused("%s: step %s returned no field %s" % (match.group(0), step, field))

    whole = RE_REF.fullmatch(value.strip())
    if whole and whole.group(1) in results:
        try:
            return lookup(results[whole.group(1)], whole.group(2))
        except KeyError:
            raise Refused("%s: step %s returned no field %s" % (value, whole.group(1), whole.group(2)))
    return RE_REF.sub(swap, value)


def google_body(ctx, body):
    return json.loads(json.dumps(body).replace("{customer}", google.customer_id(ctx)))


# ── identity of a plan and of its steps ──────────────────────────────────

def _currency(ctx, platform=None):
    """The currency budgets are read in: the platform's own when ads/config.json names one."""
    config = guards.for_platform(ctx.config, platform) if platform else ctx.config
    return str(config.get("project", {}).get("currency", "USD")).upper()


def _where(ctx, platform):
    """Where that currency is set, for the messages."""
    named = (ctx.config.get("project", {}).get("currencies") or {})
    return ("project.currencies.%s" % platform) if isinstance(named, dict) and named.get(platform) else "project.currency"


def _digest(path):
    target = Path(str(path))
    if not target.is_file():
        return "missing"
    digest = hashlib.sha256()
    with target.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def step_files(step):
    """Digests of the local files a step sends: its upload, and every {"@base64": path} inside it."""
    found = {}

    def walk(value):
        if isinstance(value, dict):
            if set(value) == {"@base64"}:
                found[str(value["@base64"])] = _digest(value["@base64"])
            else:
                for item in value.values():
                    walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(step["with"])
    if "upload" in step["do"] and step["with"].get("file"):
        found[str(step["with"]["file"])] = _digest(step["with"]["file"])
    return found


def step_hash(step):
    """Identity of one step, files included. Once a step is applied, this may not change."""
    return _sha({"do": step["do"], "with": step["with"], "files": step_files(step)})


def fingerprint(ctx, doc):
    """Identity of what a dry run looked at.

    The plan, the files it sends, the account it is aimed at and the currency its
    budgets are read in: if any of them changes, the dry run no longer describes
    what apply would do. Only the digest is stored, so no account id reaches the ledger.
    """
    return _sha({"plan": doc,
                 "files": {step["id"]: step_files(step) for step in doc["steps"]},
                 "account": {name: ctx.key(name, required=False) for name in ACCOUNT_KEYS[doc["platform"]]},
                 "currency": _currency(ctx, doc["platform"])})


# ── budgets of the whole plan ────────────────────────────────────────────

def _ref(value):
    """The step a whole-value reference such as {{campaign.id}} points at."""
    match = RE_REF.fullmatch(value.strip()) if isinstance(value, str) else None
    return match.group(1) if match else None


def plan_budgets(ctx, doc):
    """What the steps really carry: (daily, lifetime) in whole currency units.

    Every campaign counts. A budget on a campaign caps the ad sets or ad groups the
    plan puts under that campaign, so theirs are not added to it. Under a campaign
    with no budget of its own, or under one this plan does not create, they add up.
    """
    minor = 1 if _currency(ctx, doc["platform"]) in guards.ZERO_DECIMAL else 100
    tops, below, loose = {}, [], [0.0, 0.0]
    for step in doc["steps"]:
        args, where = step["with"], "step %s" % step["id"]
        if step["do"] == "google.mutate":
            for operation in args.get("mutateOperations") or []:
                payload = operation.get("campaignBudgetOperation") if isinstance(operation, dict) else None
                budget = (payload or {}).get("create") or (payload or {}).get("update") or {}
                if budget.get("amountMicros") is not None:
                    loose[0] += guards.amount(budget["amountMicros"], where) / 1_000_000
                if budget.get("totalAmountMicros") is not None:
                    loose[1] += guards.amount(budget["totalAmountMicros"], where) / 1_000_000
        elif step["do"] == "meta.post":
            params = args.get("params") or {}
            pair = [guards.amount(params[key], where) / minor if params.get(key) not in (None, "") else 0.0
                    for key in ("daily_budget", "lifetime_budget")]
            if str(args.get("path", "")).strip("/").split("/")[-1] == "campaigns":
                tops[step["id"]] = pair
            elif any(pair):
                below.append((_ref(params.get("campaign_id")), pair))
        elif step["do"] == "tiktok.post":
            body = args.get("body") or {}
            parts = str(args.get("path", "")).strip("/").split("/")
            budget = body.get("budget")
            if isinstance(budget, list):
                loose[0] += sum(guards.amount(item.get("budget") if isinstance(item, dict) else item, where)
                                for item in budget)
                continue
            if parts[-1] not in ("create", "update") or budget in (None, ""):
                continue
            mode, value = body.get("budget_mode", guards.TIKTOK_DAILY_MODES[0]), guards.amount(budget, where)
            pair = [value if mode in guards.TIKTOK_DAILY_MODES else 0.0, value if mode == "BUDGET_MODE_TOTAL" else 0.0]
            if "adgroup" in parts:
                below.append((_ref(body.get("campaign_id")), pair))
            elif parts[-1] == "create":
                tops[step["id"]] = pair
            else:
                loose[0], loose[1] = loose[0] + pair[0], loose[1] + pair[1]
    sums = []
    for index in (0, 1):
        value = loose[index] + sum(pair[index] for pair in tops.values())
        value += sum(pair[index] for parent, pair in below if not (parent in tops and tops[parent][index] > 0))
        sums.append(value)
    return sums[0], sums[1]


def uncapped(doc):
    """Campaigns this plan creates that no budget in the plan limits.

    Such a campaign would spend whatever the platform lets it, or draw on a budget
    whose size the plan does not show, so the declared and checked amount would not
    be what activation starts.
    """
    found = []
    campaigns, children, groups, ads = {}, [], set(), []

    def limited(value, where):
        return value not in (None, "") and guards.amount(value, where) > 0      # "0.0" and " 0 " are no budget either

    for step in doc["steps"]:
        args, where = step["with"], "step %s" % step["id"]
        if step["do"] == "google.mutate":
            operations = [op for op in args.get("mutateOperations") or [] if isinstance(op, dict)]
            budgets = {((op.get("campaignBudgetOperation") or {}).get("create") or {}).get("resourceName") for op in operations}
            for operation in operations:
                created = (operation.get("campaignOperation") or {}).get("create")
                if not isinstance(created, dict):
                    continue
                budget = created.get("campaignBudget")
                if not budget or not (budget in budgets or "{{" in str(budget)):
                    found.append("step %s creates a campaign on a budget this plan does not create (%s), so its amount "
                                 "is not checked: create the budget in the same step" % (step["id"], budget or "none"))
        elif step["do"] == "meta.post":
            params, edge = args.get("params") or {}, str(args.get("path", "")).strip("/").split("/")[-1]
            capped = any(limited(params.get(key), where) for key in ("daily_budget", "lifetime_budget"))
            if edge == "campaigns":
                campaigns[step["id"]] = capped
            elif edge == "adsets":
                groups.add(step["id"])
                children.append((step["id"], _ref(params.get("campaign_id")), capped, "ad set"))
            elif edge == "ads":
                ads.append((step["id"], _ref(params.get("adset_id")), "an ad set"))
        elif step["do"] == "tiktok.post":
            body, parts = args.get("body") or {}, str(args.get("path", "")).strip("/").split("/")
            if parts[-1] != "create":
                continue
            mode = body.get("budget_mode", guards.TIKTOK_DAILY_MODES[0])
            capped = limited(body.get("budget"), where) and mode in guards.TIKTOK_DAILY_MODES + ("BUDGET_MODE_TOTAL",)
            if "adgroup" in parts:
                groups.add(step["id"])
                children.append((step["id"], _ref(body.get("campaign_id")), capped, "ad group"))
            elif "campaign" in parts:
                campaigns[step["id"]] = capped
            elif "ad" in parts:
                ads.append((step["id"], _ref(body.get("adgroup_id")), "an ad group"))
    elsewhere = ("what it may spend would come from a budget the plan neither sets nor checks. "
                 "Add it with single commands, each shown to the user first")
    for step, parent, capped, word in children:
        if parent not in campaigns:
            found.append("%s %s joins a campaign this plan does not create: %s" % (word, step, elsewhere))
        elif not capped and not campaigns[parent]:
            found.append("%s %s has no budget and neither has its campaign %s: it would spend without a limit"
                         % (word, step, parent))
    for step, parent, word in ads:
        if parent not in groups:
            found.append("ad %s joins %s this plan does not create: %s" % (step, word, elsewhere))
    return found


def budget_check(ctx, doc):
    """Compare what the steps carry with what the plan declares and with the ceilings.

    The per-request guard rails see one object at a time; ten ad sets of 20 each
    pass a ceiling of 50 there. This check sees the plan.
    Returns (report lines, problems, daily, lifetime).
    """
    daily, total = plan_budgets(ctx, doc)
    declared = doc.get("budget") or {}
    currency = _currency(ctx, doc["platform"])
    config = guards.for_platform(ctx.config, doc["platform"])
    money = str(declared.get("currency") or currency).upper()
    lines, problems = [], []

    def bad(text):
        problems.append(text)
        lines.append("  FAIL %s" % text)

    try:
        ceiling = guards.daily_ceiling(config)
    except Refused as exc:
        ceiling = 0.0
        bad(exc.message)
    try:
        total_ceiling = max(float(config.get("guardrails", {}).get("max_total_budget") or 0), 0.0)
    except (TypeError, ValueError):
        total_ceiling = 0.0
    for text in uncapped(doc):
        bad(text)
    if money != currency:
        bad("the plan names %s but %s in ads/config.json is %s: budgets and ceilings would be read "
            "in the wrong currency" % (money, _where(ctx, doc["platform"]), currency))
    stated = {key: guards.amount(declared[key], "budget.%s" % key) for key in ("daily", "total") if declared.get(key) is not None}
    if daily:
        if ceiling and daily > ceiling:
            bad("the daily budgets in the steps add up to %g %s, above the ceiling of %g" % (daily, money, ceiling))
        if "daily" not in stated:
            bad("the steps carry %g a day but the plan declares no daily budget: add \"budget\": {\"daily\": %g, "
                "\"currency\": \"%s\"}" % (daily, daily, currency))
        elif abs(stated["daily"] - daily) > 0.005:
            bad("the plan declares %g %s a day but its steps add up to %g" % (stated["daily"], money, daily))
        elif not (ceiling and daily > ceiling):
            lines.append("  ok   daily budget %g %s, as the steps carry it (ceiling %g)" % (daily, money, ceiling))
    elif "daily" in stated:
        lines.append("  note no step sets a daily budget: the declared %g %s is not sent to the platform by this plan"
                     % (stated["daily"], money))
    if total:
        if not total_ceiling:
            bad("the steps carry a lifetime budget of %g %s and lifetime budgets are switched off: use a daily budget, "
                "or set guardrails.max_total_budget when the user asks for a lifetime budget" % (total, money))
        elif total > total_ceiling:
            bad("the lifetime budgets in the steps add up to %g %s, above the ceiling of %g" % (total, money, total_ceiling))
        if "total" not in stated:
            bad("the steps carry a lifetime budget of %g but the plan declares no \"total\" in its budget" % total)
        elif abs(stated["total"] - total) > 0.005:
            bad("the plan declares %g %s in total but its steps add up to %g" % (stated["total"], money, total))
        elif total_ceiling and total <= total_ceiling:
            lines.append("  ok   lifetime budget %g %s, as the steps carry it (ceiling %g)" % (total, money, total_ceiling))
    if not daily and not total and not stated:
        lines.append("  note this plan sets no budget")
    return lines, problems, daily, total


def _ambiguous(exc):
    """True when a write may have reached the platform although no clear answer came back."""
    if getattr(exc, "before_send", False):
        return False
    seen, limit = exc, 0
    while seen is not None and limit < 8:
        if getattr(seen, "uncertain", False):
            return True
        if isinstance(seen, HttpError) and seen.status >= 500:
            return True
        if isinstance(seen, (socket.timeout, TimeoutError, ConnectionError, http.client.HTTPException, ssl.SSLError)):
            return True
        if isinstance(seen, urllib.error.URLError) and isinstance(
                getattr(seen, "reason", None), (socket.timeout, TimeoutError, ConnectionResetError)):
            return True
        seen, limit = seen.__cause__ or seen.__context__, limit + 1
    return False


# ── ledger ───────────────────────────────────────────────────────────────

def ledger_file(ctx):
    return ctx.ws / "launch" / "ledger.jsonl"


def _events(ctx, name):
    """Ledger entries of one plan since what it created was last removed."""
    rows = []
    for entry in read_jsonl(ledger_file(ctx)):
        if entry.get("plan") != name:
            continue
        rows = [] if entry.get("event") == "rollback" else rows + [entry]
    return rows


def applied_state(ctx, name):
    """Results of the steps already applied for this plan, in order; a rollback clears them."""
    return {entry["step"]: entry for entry in _events(ctx, name) if entry.get("event") == "step" and entry.get("ok")}


def removed_ids(ctx, name):
    return {entry.get("id") for entry in _events(ctx, name) if entry.get("event") == "removed"}


def entities(ctx, name):
    """What the plan created and a rollback has not removed."""
    gone = removed_ids(ctx, name)
    found = []
    for entry in applied_state(ctx, name).values():
        found.extend(item for item in entry.get("entities", []) if item.get("id") not in gone)
    return found


def uncertain_steps(ctx, name):
    """Steps whose last send ended without a clear answer: the object may exist in the ad account.

    A send is marked in the ledger before it leaves, so an interrupted run counts as well.
    """
    last = {}
    for entry in read_jsonl(ledger_file(ctx)):      # the whole history: removing what the ledger knows does not find an orphan
        if entry.get("plan") == name and entry.get("event") in ("sending", "step", "resend") and entry.get("step"):
            last[entry["step"]] = entry
    return {step: entry for step, entry in last.items()
            if entry["event"] == "sending" or (entry["event"] == "step" and not entry.get("ok") and entry.get("uncertain"))}


def edited_steps(doc, done):
    """Applied steps whose content is no longer what was sent: the plan would describe something the account does not hold."""
    return [step["id"] for step in doc["steps"]
            if step["id"] in done and done[step["id"]].get("sha256") != step_hash(step)]


def stray_steps(doc, done):
    """Applied steps the plan no longer lists: renamed or deleted, they would be created a second time."""
    listed = {step["id"] for step in doc["steps"]}
    return [name for name in done if name not in listed]


def own_names(results):
    """Google resource names the earlier steps of a plan created."""
    names = set()
    for result in results.values():
        if isinstance(result, dict) and isinstance(result.get("results"), list):
            names.update(name for name in result["results"] if isinstance(name, str))
    return names


def require_dry_run(ctx, doc, path):
    """launch apply runs only on what a clean dry run has seen: a changed plan is a new plan."""
    last = next((entry for entry in reversed(_events(ctx, doc["name"])) if entry.get("event") == "dry-run"), None)
    hint = "run: %s launch plan --file %s, show its output to the user, then apply" % (SELF, path)
    if last is None:
        raise Refused("plan %s has no dry run on record since it was written or last removed" % doc["name"], hint)
    if last.get("sha256") != fingerprint(ctx, doc):
        raise Refused("plan %s, a file it sends, the account ids in ads/.env or the currency changed after its last dry run"
                      % doc["name"], hint)
    if not last.get("ok"):
        raise Refused("the last dry run of plan %s reported problems" % doc["name"],
                      "fix them, then " + hint)


# ── one step ─────────────────────────────────────────────────────────────

def run_step(ctx, step, args, yes, own=()):
    """Run or validate one step. Returns (result for references, entities created, note).

    own: Google resource names earlier steps of the plan created. A step may build on them,
    and on nothing else that already exists.
    """
    do = step["do"]
    if do == "google.mutate":
        body = google_body(ctx, args)
        out = google.mutate(ctx, body, yes=yes, plan=set(own))
        names, made = out["results"], []
        for operation, name in zip(body.get("mutateOperations") or [], names):
            if not name or name.count("/") < 3:
                continue
            item = {"platform": "google", "type": name.split("/")[2], "id": name}
            created = (next(iter(operation.values())) or {}).get("create") if isinstance(operation, dict) and operation else None
            # What is born paused under a campaign that already runs is switched on and off with the plan.
            if isinstance(created, dict) and created.get("status") == "PAUSED" and item["type"] != "campaigns":
                item["born"] = "PAUSED"
            made.append(item)
        note = "validated by Google Ads" if not yes else "%d operations applied" % len([n for n in names if n])
        return {"results": names}, made, note
    if do == "meta.post":
        out = meta.post(ctx, args.get("path", ""), args.get("params"), yes=yes, plan=True)
        edge = args.get("path", "").strip("/").split("/")[-1]
        if not yes:
            return {}, [], "validated by Meta" if out.get("validated_only") else "checked by the toolkit only"
        response = out["response"]
        made = [{"platform": "meta", "type": META_TYPES[edge], "id": response["id"]}] if edge in META_TYPES and response.get("id") else []
        return response, made, "created %s" % response.get("id", "")
    if do == "meta.upload_image":
        started = time.time()
        out = meta.upload_image(ctx, args["file"], yes=yes)
        if not yes:
            return {}, [], "file found, %d bytes" % out["bytes"]
        existed = _image_existed(ctx, out.get("hash"), started)
        made = [{"platform": "meta", "type": "image", "id": out["hash"], "existed": existed}] if out.get("hash") else []
        return out, made, "uploaded" + (": the library held it already, so a removal keeps it" if existed else "")
    if do == "meta.upload_video":
        out = meta.upload_video(ctx, args["file"], args.get("name"), yes=yes)
        return ({}, [], "file found, %d bytes" % out["bytes"]) if not yes else (out, [], "uploaded")
    if do == "tiktok.post":
        route = args.get("path", "").strip("/")
        out = tiktok.post(ctx, route, args.get("body"), yes=yes, plan=True)
        if not yes:
            return {}, [], "checked by the toolkit only (TikTok has no validate mode)"
        data = out["data"]
        parts = route.split("/")
        level = next((p for p in reversed(parts[:-1]) if p in ("campaign", "adgroup", "ad")), None)
        made = []
        if parts[-1] == "create" and level:
            ids = data.get("%s_ids" % level) or ([data["%s_id" % level]] if data.get("%s_id" % level) else [])
            ids = ids or ([data["smart_plus_ad_id"]] if data.get("smart_plus_ad_id") else [])
            made = [{"platform": "tiktok", "type": level, "id": str(i), "smart_plus": parts[0] == "smart_plus"} for i in ids]
        return data, made, "created %s" % ", ".join(e["id"] for e in made)
    if do == "tiktok.upload_video":
        out = tiktok.upload_video(ctx, file=args.get("file"), video_url=args.get("url"), name=args.get("name"), yes=yes)
        return ({}, [], "ready to upload") if not yes else (out, [], "uploaded %s" % out.get("video_id"))
    if do == "tiktok.upload_image":
        out = tiktok.upload_image(ctx, args["file"], yes=yes)
        return ({}, [], "file found, %d bytes" % out["bytes"]) if not yes else (out, [], "uploaded %s" % out.get("image_id"))
    raise Refused("unknown step kind %s" % do)


def _image_existed(ctx, image_hash, started):
    """True unless the image is shown to have entered the library with this upload.

    Meta keeps one image per hash: uploading a file the library already holds returns that image,
    which other ads may use. A removal deletes only an image this upload created; when its age
    cannot be read, the image is kept.
    """
    created = meta.image_created(ctx, image_hash) if image_hash else None
    try:
        stamp = datetime.strptime(str(created), "%Y-%m-%dT%H:%M:%S%z").timestamp()
    except ValueError:
        return True
    return stamp < started - 300


def describe(step):
    do, args = step["do"], step["with"]
    if do == "google.mutate":
        kinds = [next(iter(op)) for op in args.get("mutateOperations", []) if isinstance(op, dict) and op]
        return "%d operations: %s" % (len(kinds), ", ".join(sorted(set(k.replace("Operation", "") for k in kinds))))
    if do in ("meta.post", "tiktok.post"):
        body = args.get("params") or args.get("body") or {}
        label = body.get("name") or body.get("campaign_name") or body.get("adgroup_name") or ""
        return "POST %s %s" % (args.get("path", ""), ("(%s)" % label) if label else "")
    return "upload %s" % (args.get("file") or args.get("url"))


# ── commands ─────────────────────────────────────────────────────────────

def account_line(ctx, platform):
    if platform == "google":
        return "Google Ads account %s" % google.customer_id(ctx)
    if platform == "meta":
        return "Meta ad account %s, Page %s" % (meta.account(ctx), ctx.key("META_PAGE_ID", required=False) or "not set")
    return "TikTok advertiser %s" % tiktok.advertiser(ctx)


def plan(ctx, path):
    """Dry run: check every step, ask the platform to validate what it can, print the eight blocks."""
    doc = load_plan(path)
    platform = doc["platform"]
    budget = doc.get("budget") or {}
    lines, problems, results = [], [], {}
    done = applied_state(ctx, doc["name"])

    def fail(text):
        problems.append(text)
        lines.append("  FAIL %s" % text)

    lines.append("TARGET")
    lines.append("  %s" % account_line(ctx, platform))
    lines.append("  plan %s: %s" % (doc["name"], doc.get("objective", "no objective given")))
    if doc.get("landing_url"):
        lines.append("  landing page %s" % doc["landing_url"])

    lines.append("PRECHECK")
    try:
        info = {"google": google.account_info, "meta": meta.account_info, "tiktok": tiktok.account_info}[platform](ctx)
        lines.append("  ok   account reachable: %s" % info["note"])
        if info.get("currency") and str(info["currency"]).upper() != _currency(ctx, platform):
            fail("the ad account is in %s but %s in ads/config.json is %s: budgets and ceilings would be read in the "
                 "wrong currency. When the accounts of the platforms bill in different currencies, name one per platform "
                 "under project.currencies" % (str(info["currency"]).upper(), _where(ctx, platform), _currency(ctx, platform)))
    except AdsError as exc:
        fail("account check: %s" % exc.message)
    try:
        budget_lines, budget_problems, daily, total = budget_check(ctx, doc)
    except AdsError as exc:
        budget_lines, budget_problems, daily, total = ["  FAIL %s" % exc.message], [exc.message], 0.0, 0.0
    lines.extend(budget_lines)
    problems.extend(budget_problems)
    if done:
        lines.append("  note %d step(s) of this plan are already applied and will be skipped: %s" % (len(done), ", ".join(done)))
    for name in stray_steps(doc, done):
        fail("step %s was applied but is no longer in the plan: a renamed or deleted step would be created a second time. "
             "Put it back under its id, or remove what the plan created (launch rollback --remove) and start again" % name)
    for name in edited_steps(doc, done):
        fail("step %s was changed after it was applied, so the plan no longer describes what the account holds: put the "
             "step back as it was, or remove what the plan created (launch rollback --remove) and start again" % name)
    if removed_ids(ctx, doc["name"]):
        fail("part of what this plan created was removed: finish with launch rollback --remove before applying again")
    for name, entry in uncertain_steps(ctx, doc["name"]).items():
        lines.append("  note step %s ended without a clear answer on %s: look for it in the ad account before applying "
                     "again (launch apply --resend %s)" % (name, entry.get("ts"), name))

    change, validate = [], []
    for step in doc["steps"]:
        change.append("  %-14s %-20s %s" % (step["id"], step["do"], describe(step)))
        if step["id"] in done:
            results[step["id"]] = done[step["id"]].get("result", {})
            validate.append("  skip %s: already applied" % step["id"])
            continue
        try:
            args = resolve(step["with"], results)
        except Unresolved as ref:
            try:
                _local_guard(ctx, step)
                validate.append("  wait %s: needs %s, so the platform checks it during apply; toolkit rules pass" % (step["id"], ref))
            except AdsError as exc:
                problems.append("%s: %s" % (step["id"], exc.message))
                validate.append("  FAIL %s: %s" % (step["id"], exc.message))
            continue
        except AdsError as exc:
            problems.append("%s: %s" % (step["id"], exc.message))
            validate.append("  FAIL %s: %s" % (step["id"], exc.message))
            continue
        try:
            _, _, note = run_step(ctx, step, args, yes=False, own=own_names(results))
            validate.append("  ok   %s: %s" % (step["id"], note))
        except AdsError as exc:
            problems.append("%s: %s" % (step["id"], exc.message))
            validate.append("  FAIL %s: %s" % (step["id"], exc.message.replace("\n", "\n       ")))

    lines.append("CHANGE")
    lines.extend(change)
    lines.append("BACKUP")
    lines.append("  nothing existing is modified: the plan only creates new objects")
    lines.append("  every created id is written to ads/launch/ledger.jsonl")
    lines.append("IMPACT")
    lines.append("  everything that can deliver is created paused: no spend until launch activate")
    money = str(budget.get("currency") or _currency(ctx, platform)).upper()
    if daily:
        lines.append("  after activation: up to %g %s per day, about %.0f per month" % (daily, money, daily * 30.4))
    if total:
        lines.append("  after activation: up to %g %s in total over the schedule" % (total, money))
    if not daily and not total:
        lines.append("  this plan sets no budget: it creates nothing that can spend on its own")
    lines.append("VALIDATE")
    lines.extend(validate)
    lines.append("ROLLBACK")
    lines.append("  %s launch rollback --file %s --yes" % (SELF, path))
    lines.append("APPLY")
    if problems:
        lines.append("  blocked: fix the %d problem(s) above, then run launch plan again" % len(problems))
    else:
        lines.append("  %s launch apply --file %s --yes" % (SELF, path))
    text = "\n".join(lines) + "\n"
    report = ctx.path("launch", "%s.dry-run.txt" % doc["name"])
    report.write_text(text, encoding="utf-8")
    append_jsonl(ledger_file(ctx), {"ts": now(), "event": "dry-run", "plan": doc["name"], "platform": platform,
                                    "sha256": fingerprint(ctx, doc), "ok": not problems, "problems": len(problems)})
    return text, problems


def _local_guard(ctx, step):
    """Toolkit rules for a step whose references cannot be resolved before apply."""
    args = step["with"]
    if step["do"] == "google.mutate":
        guards.google_mutate(args, guards.for_platform(ctx.config, "google"), plan=set())
    elif step["do"] == "meta.post":
        guards.meta_request("POST", args.get("path", ""), args.get("params") or {}, guards.for_platform(ctx.config, "meta"),
                            plan=True)
        meta.own_account(ctx, args.get("path", ""))
    elif step["do"] == "tiktok.post":
        guards.tiktok_request(args.get("path", ""), args.get("body") or {}, guards.for_platform(ctx.config, "tiktok"),
                              plan=True)
    elif args.get("file") and not Path(args["file"]).is_file():
        raise Refused("file not found: %s" % args["file"])


def apply(ctx, path, yes=False, resend=()):
    doc = load_plan(path)
    name = doc["name"]
    if not yes:
        raise Refused("launch apply changes the ad account", "run launch plan first, then add --yes")
    require_dry_run(ctx, doc, path)
    budget_problems = budget_check(ctx, doc)[1]
    if budget_problems:
        raise Refused("the budget of plan %s does not pass: %s" % (name, "; ".join(budget_problems)),
                      "fix the plan and run launch plan again")
    if removed_ids(ctx, name):
        raise Refused("part of what plan %s created was removed" % name,
                      "finish with: %s launch rollback --file %s --remove --yes, then run launch plan and apply again"
                      % (SELF, path))
    done = applied_state(ctx, name)
    stray = stray_steps(doc, done)
    if stray:
        raise Refused("step %s was applied but is no longer in the plan" % ", ".join(stray),
                      "a renamed or deleted step would be created a second time: put it back under its id, or remove what "
                      "the plan created with: %s launch rollback --file %s --remove --yes, and start again" % (SELF, path))
    changed = edited_steps(doc, done)
    if changed:
        raise Refused("step %s was changed after it was applied, so the plan no longer describes what the account holds"
                      % ", ".join(changed),
                      "put the step back as it was, or remove what the plan created with: %s launch rollback --file %s "
                      "--remove --yes, and start again" % (SELF, path))
    unsure, resend = uncertain_steps(ctx, name), list(resend or ())
    stray = [step for step in resend if step not in unsure]
    if stray:
        raise Refused("--resend names %s, which did not end without an answer" % ", ".join(stray),
                      "--resend is only for a step that launch apply reported as unclear")
    blocked = [step for step in unsure if step not in resend]
    if blocked:
        raise Refused(
            "step %s of plan %s ended without a clear answer, so its object may exist in the ad account"
            % (", ".join(blocked), name),
            "look for it there by its name; if it is there, remove it there (it is paused). Then run: "
            "%s launch apply --file %s --yes %s" % (SELF, path, " ".join("--resend %s" % step for step in blocked)))
    for step in resend:
        append_jsonl(ledger_file(ctx), {"ts": now(), "event": "resend", "plan": name, "platform": doc["platform"], "step": step})
    results = {step: entry.get("result", {}) for step, entry in done.items()}
    log = []
    for index, step in enumerate(doc["steps"]):
        if step["id"] in done:
            log.append("skip  %s (already applied)" % step["id"])
            continue
        entry = {"ts": now(), "event": "step", "plan": name, "platform": doc["platform"], "step": step["id"],
                 "do": step["do"], "sha256": step_hash(step)}
        remaining = len(doc["steps"]) - index
        undo = "undo what was created with: %s launch rollback --file %s --yes" % (SELF, path)
        sent, failure = False, None
        try:
            args = resolve(step["with"], results)
            # Marked before it leaves: if this process dies now, the next run knows the outcome is unknown.
            append_jsonl(ledger_file(ctx), {"ts": entry["ts"], "event": "sending", "plan": name,
                                            "platform": doc["platform"], "step": step["id"]})
            sent = True
            result, made, note = run_step(ctx, step, args, yes=True, own=own_names(results))
        except Unresolved as ref:
            raise Refused("step %s refers to %s, which no earlier step produced" % (step["id"], ref))
        except AdsError as exc:
            failure = (exc.message, sent and _ambiguous(exc))
        except Exception as exc:        # anything the toolkit does not know: the write may have landed
            failure = ("%s: %s" % (type(exc).__name__, exc), sent)
        if failure:
            message, unsure_now = failure
            entry.update({"ok": False, "error": message, "uncertain": unsure_now})
            append_jsonl(ledger_file(ctx), entry)
            if unsure_now:
                hint = ("No clear answer came back, so the platform may have created this object although the ledger does "
                        "not hold it. Look for it in the ad account by its name; if it is there, remove it there (it is "
                        "paused and launch activate will not touch it). Then run: %s launch apply --file %s --yes "
                        "--resend %s. %d step(s) not applied. Or %s" % (SELF, path, step["id"], remaining, undo))
            else:
                hint = ("%d step(s) not applied. Fix the step, run launch plan again and show it, then launch apply: "
                        "applied steps are skipped. Or %s" % (remaining, undo))
            raise AdsError("step %s failed: %s" % (step["id"], message), hint)
        entry.update({"ok": True, "result": result, "entities": made})
        append_jsonl(ledger_file(ctx), entry)
        results[step["id"]] = result
        log.append("done  %s: %s" % (step["id"], note))
    log.append("all steps applied, everything is paused. Review it in the ad platform, then show the user: "
               "%s launch activate --file %s" % (SELF, path))
    return "\n".join(log) + "\n"


def status(ctx, path):
    doc = load_plan(path)
    rows = []
    for item in entities(ctx, doc["name"]):
        row = dict(item)
        try:
            if item["platform"] == "meta" and item["type"] in SWITCHED["meta"]:
                info = meta.get(ctx, item["id"], {"fields": "name,status,effective_status"})
                row.update({"name": info.get("name"), "status": info.get("status"), "effective_status": info.get("effective_status")})
            elif item["platform"] == "google" and item["type"] == "campaigns":
                found = google.search(ctx, "SELECT campaign.name, campaign.status, campaign.primary_status FROM campaign "
                                           "WHERE campaign.resource_name = '%s'" % item["id"])
                info = found[0].get("campaign", {}) if found else {}
                row.update({"name": info.get("name"), "status": info.get("status"), "primary_status": info.get("primaryStatus")})
            elif item["platform"] == "tiktok" and item["type"] == "campaign" and not item.get("smart_plus"):
                data = tiktok.get(ctx, "campaign/get", {"filtering": {"campaign_ids": [item["id"]]}})
                info = (data.get("list") or [{}])[0]
                row.update({"name": info.get("campaign_name"), "status": info.get("operation_status"),
                            "secondary_status": info.get("secondary_status")})
        except AdsError as exc:
            row["error"] = exc.message
        rows.append(row)
    return rows


# ── switching on, pausing, removing ──────────────────────────────────────

def _switchable(platform, items):
    """What the switch acts on, parents first."""
    if platform == "google":
        # Children born enabled under a campaign of this plan follow that campaign; those born paused are switched themselves.
        keep = [i for i in items if i["type"] == "campaigns" or (i["type"] in SWITCHED[platform] and i.get("born") == "PAUSED")]
    else:
        keep = [i for i in items if i["type"] in SWITCHED[platform]]
    return sorted(keep, key=lambda item: SWITCHED[platform].index(item["type"]))


def _units(ctx, platform, items, turn_on, remove, yes):
    """Yield (objects, word for the log, call) in the order to run: parents first to enable, children first otherwise."""
    ordered = items if turn_on else list(reversed(items))
    if platform == "google":
        target = "ENABLED" if turn_on else ("REMOVED" if remove else "PAUSED")
        # Enabling is one request, all or nothing. Pausing and removing go object by object, so one failure stops nothing else.
        for group in ([ordered] if turn_on else [[item] for item in ordered]):
            if group:
                yield group, target, (lambda g=group: google.set_status(ctx, [i["id"] for i in g], target, yes=yes))
    elif platform == "meta":
        for item in ordered:
            if remove and not turn_on:
                yield [item], "deleted", (lambda i=item: meta.delete(ctx, i["id"], yes=yes))
            else:
                target = "ACTIVE" if turn_on else "PAUSED"
                yield [item], target, (lambda i=item, t=target: meta.set_status(ctx, i["id"], t, yes=yes))
    else:
        target = "ENABLE" if turn_on else ("DELETE" if remove else "DISABLE")
        for kind in (SWITCHED[platform] if turn_on else reversed(SWITCHED[platform])):
            for smart in (False, True):
                group = [i for i in items if i["type"] == kind and bool(i.get("smart_plus")) == smart]
                if group:
                    yield group, target, (lambda g=group, k=kind, s=smart: tiktok.set_status(
                        ctx, k, [i["id"] for i in g], target, yes=yes, smart_plus=s))


def _leftovers(ctx, platform, items, yes):
    """What only a removal deletes, once the objects that use it are gone: creatives, then images the plan uploaded.

    Returns (units like _units yields, images that stay in the library).
    """
    if platform != "meta":
        return [], []
    units = [([item], "deleted", (lambda i=item: meta.delete(ctx, i["id"], yes=yes))) for item in items
             if item["type"] == "creative"]
    kept = []
    for item in items:
        if item["type"] != "image":
            continue
        if item.get("existed", True):
            kept.append(item)
        else:
            units.append(([item], "deleted", (lambda i=item: meta.delete_image(ctx, i["id"], yes=yes))))
    return units, kept


def _gone(exc):
    """True when the platform says the object does not exist any more."""
    if getattr(exc, "platform_code", None) == 100 and getattr(exc, "platform_subcode", None) == 33:
        return True                                                    # Meta
    return any(word in exc.message for word in ("OPERATION_NOT_PERMITTED_FOR_REMOVED_RESOURCE", "RESOURCE_NOT_FOUND"))


def _switch(ctx, doc, path, turn_on, remove, yes):
    """Enable, pause or remove what the plan created. Returns (log lines, failures).

    Enabling stops at the first failure: nothing below a parent that stayed off is
    switched on. Pausing and removing go on past a failure, because every object
    that can be stopped should be, and report what is left at the end.
    """
    name, platform = doc["name"], doc["platform"]
    if not applied_state(ctx, name):
        raise Refused("the ledger holds nothing applied for plan %s" % name)
    log, failed = [], []
    found = entities(ctx, name)
    units, kept = list(_units(ctx, platform, _switchable(platform, found), turn_on, remove, yes)), []
    extra = []
    if remove and not turn_on:
        extra, kept = _leftovers(ctx, platform, found, yes)
    for unit in units + [None] + extra:
        if unit is None:
            if failed and extra:
                # an ad that is still there may use the creative: it goes when the objects above are gone
                log.append("left for the next run: %s" % ", ".join("%s %s" % (g[0]["type"], g[0]["id"]) for g, _, _ in extra))
                break
            continue
        group, word, call = unit
        label = ", ".join("%s %s" % (item["type"], item["id"]) for item in group)
        finished = list(group)
        try:
            call()
        except AdsError as exc:
            if turn_on:
                raise AdsError("could not enable %s: %s" % (label, exc.message),
                               "nothing below it was enabled. Fix the cause and run launch activate again, or pause what "
                               "is on with: %s launch rollback --file %s --yes" % (SELF, path))
            if _gone(exc):
                log.append("skip %s: the platform reports that it no longer exists" % label)
            else:
                refused = set(getattr(exc, "failed_ids", None) or [item["id"] for item in group])
                finished = [item for item in group if item["id"] not in refused]
                failed.append("%s: %s" % (", ".join("%s %s" % (i["type"], i["id"]) for i in group if i["id"] in refused),
                                          exc.message))
        else:
            verb = {"deleted": "would delete" if not yes else "deleted"}.get(word, "would set" if not yes else "set")
            log.append("%s %s%s" % (verb, label, "" if word == "deleted" else ": %s" % word))
        if yes and remove and not turn_on:
            for item in finished:
                append_jsonl(ledger_file(ctx), {"ts": now(), "event": "removed", "plan": name, "platform": platform,
                                                "type": item["type"], "id": item["id"]})
    for item in kept:
        log.append("kept image %s in the library: it was there before this plan, or its age could not be read. If no "
                   "other ad uses it: %s meta delete {account}/adimages -p hash=%s --yes" % (item["id"], SELF, item["id"]))
    return log, failed


def _report(log, failed, what, hint):
    if failed:
        done = ("\nDone before and after that:\n  " + "\n  ".join(log)) if log else ""
        raise AdsError("%d object(s) could not be %s:\n  %s%s" % (len(failed), what, "\n  ".join(failed), done), hint)
    return "\n".join(log) + "\n"


def activate(ctx, path, yes=False):
    doc = load_plan(path)
    done = applied_state(ctx, doc["name"])
    if not done:
        raise Refused("the ledger holds nothing applied for plan %s" % doc["name"])
    stray = stray_steps(doc, done)
    if stray:
        raise Refused("step %s was applied but is no longer in the plan, so the plan does not describe everything that "
                      "would be switched on" % ", ".join(stray), "put the step back under its id before activating")
    missing = [step["id"] for step in doc["steps"] if step["id"] not in done]
    if missing:
        raise Refused("plan %s is not fully applied: %s missing" % (doc["name"], ", ".join(missing)),
                      "finish launch apply first; a campaign that is only half there should not start to spend")
    changed = edited_steps(doc, done)
    if changed:
        raise Refused("step %s was changed after it was applied, so the plan no longer describes what would be switched on"
                      % ", ".join(changed), "put the step back as it was before activating")
    _, problems, daily, total = budget_check(ctx, doc)
    if problems:
        raise Refused("the budget of plan %s does not pass now: %s" % (doc["name"], "; ".join(problems)),
                      "the ceiling, the currency or the plan changed since it was applied: settle that with the user first")
    log, _ = _switch(ctx, doc, path, turn_on=True, remove=False, yes=yes)
    money = str((doc.get("budget") or {}).get("currency") or _currency(ctx, doc["platform"])).upper()
    if daily:
        log.append("budget of this plan: up to %g %s per day, about %.0f per month" % (daily, money, daily * 30.4))
    if total:
        log.append("budget of this plan: up to %g %s in total over the schedule" % (total, money))
    if yes:
        append_jsonl(ledger_file(ctx), {"ts": now(), "event": "activate", "plan": doc["name"], "platform": doc["platform"]})
        log.append("spend can start now. Check delivery tomorrow with the performance-report skill.")
    else:
        log.append("nothing changed: this is what launch activate --yes would switch on, and spend starts then")
    return "\n".join(log) + "\n"


def rollback(ctx, path, remove=False, yes=False):
    doc = load_plan(path)
    log, failed = _switch(ctx, doc, path, turn_on=False, remove=remove, yes=yes)
    again = "%s launch rollback --file %s %s--yes" % (SELF, path, "--remove " if remove else "")
    for name in uncertain_steps(ctx, doc["name"]):
        log.append("step %s ended without a clear answer earlier: its object, if it exists, is not in the ledger and was "
                   "not touched. Look for it in the ad account by its name" % name)
    if not yes:
        log.append("nothing changed: add --yes to do it")
    elif failed:
        pass
    elif remove:
        append_jsonl(ledger_file(ctx), {"ts": now(), "event": "rollback", "plan": doc["name"], "platform": doc["platform"]})
        log.append("removed and cleared from the ledger: a new launch starts with launch plan")
    else:
        append_jsonl(ledger_file(ctx), {"ts": now(), "event": "pause", "plan": doc["name"], "platform": doc["platform"]})
        log.append("everything this plan created is paused; add --remove to delete it as well")
    return _report(log, failed, "removed" if remove else "paused",
                   "run it again: %s. What is listed above may still be live: check it in the ad platform now" % again)


def ledger(ctx, name=None):
    rows = read_jsonl(ledger_file(ctx))
    if name:
        rows = [r for r in rows if r.get("plan") == name]
    return [{k: v for k, v in r.items() if k != "result"} for r in rows]
