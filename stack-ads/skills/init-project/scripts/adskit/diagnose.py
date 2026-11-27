"""launch diagnose: a read-only audit of what a launched plan does in the ad platform.

It walks the objects the ledger holds for a plan, reads their state back (Meta GET, Google googleAds:search,
TikTok GET) and says what is wrong and what to do next. It never writes. The alarm it exists for: everything
approved, switched on, schedule open, and still no impressions hours after the last activation.
"""
from __future__ import annotations

import datetime
import json

from . import google, launch, meta, tiktok
from .core import AdsError, Refused

UTC = datetime.timezone.utc
TOO_EARLY_HOURS = 6
SELF = launch.SELF
FIELDS = ("level", "object", "check", "state", "detail", "next")
RANK = {"fail": 0, "warn": 1, "ok": 2}


def utcnow():
    return datetime.datetime.now(UTC)


def parse_time(text):
    """A platform timestamp such as 2026-11-26T10:00:00+0200 or 2026-11-26T10:00:00Z, or None."""
    if not text:
        return None
    text = str(text)
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S"):
        try:
            value = datetime.datetime.strptime(text, fmt)
        except ValueError:
            continue
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    try:
        value = datetime.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def whole(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def clip(text, limit=300):
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[:limit - 3] + "..."


def label(kind, ident, name=None):
    return "%s %s%s" % (kind, ident, " (%s)" % name if name else "")


# ── the ledger side ──────────────────────────────────────────────────────

def activation(ctx, name):
    """When the plan was last switched on, and until when, from the ledger.

    Returns {"on", "ever", "ts", "paused_at", "start", "end", "hours", "since", "until"}. "on" is true while no pause
    follows the last activation. start and end are the stretch the plan was switched on (end is now while it is on),
    hours its length, since and until their UTC dates. All of them are None for a plan that was never activated.
    """
    ts = paused = None
    for entry in launch._events(ctx, name):
        if entry.get("event") == "activate":
            ts, paused = entry.get("ts"), None
        elif entry.get("event") == "pause":
            paused = entry.get("ts")
    start, stopped = parse_time(ts), parse_time(paused)
    on = bool(start) and not stopped
    end = (utcnow() if on else stopped or start) if start else None
    return {"on": on, "ever": bool(start), "ts": ts, "paused_at": paused, "start": start, "end": end,
            "hours": max((end - start).total_seconds() / 3600, 0.0) if start else None,
            "since": start.strftime("%Y-%m-%d") if start else None, "until": end.strftime("%Y-%m-%d") if end else None}


class Audit:
    """The findings of one run, and the part of them that decides whether delivery should have started."""

    def __init__(self, ctx, info):
        self.ctx, self.info, self.rows, self.gate, self.windows = ctx, info, [], [], []

    @property
    def expected_off(self):
        """True when the ledger says the plan is not switched on, so a paused object is what it should be."""
        return not self.info["on"]

    def off_reason(self):
        if self.info["paused_at"]:
            return "paused by launch rollback at %s, as the ledger says" % self.info["paused_at"]
        return "paused, as the ledger says: the plan was never activated"

    def schedule(self, level, obj, start, end, start_text, end_text):
        """The schedule window of an object. A live plan fails on a window that is shut; the window is kept for the alarm."""
        if not (start or end):
            return
        self.windows.append((start, end))
        now = utcnow()
        if not self.info["on"]:
            self.add(level, obj, "schedule", "ok", "window from %s to %s" % (start_text or "now", end_text or "no end"))
        elif start and start > now:
            self.add(level, obj, "schedule", "fail", "not started: starts %s, in %.0f hours"
                     % (start_text, (start - now).total_seconds() / 3600),
                     "nothing delivers before the start time: move the start time to now, or wait")
        elif end and end < now:
            self.add(level, obj, "schedule", "fail", "ended at %s" % end_text, "set a later end for it, or create a new one")
        else:
            self.add(level, obj, "schedule", "ok", "window open: from %s to %s" % (start_text or "now", end_text or "no end"))

    def inside_hours(self):
        """Hours the plan was switched on and inside the schedule window of its objects (the best of them)."""
        info = self.info
        if not info["ever"]:
            return None
        if not self.windows:
            return info["hours"]
        best = 0.0
        for start, end in self.windows:
            low, high = max(info["start"], start) if start else info["start"], min(info["end"], end) if end else info["end"]
            best = max(best, (high - low).total_seconds() / 3600)
        return best

    def add(self, level, obj, check, state, detail, next_="", gate=None):
        row = {"level": level, "object": obj, "check": check, "state": state, "detail": detail, "next": next_}
        self.rows.append(row)
        if state != "ok" and gate is not False:
            self.gate.append(row)
        return row

    def read(self, level, obj, check, call, *args, **kwargs):
        """One read. A read that fails is a warning with the error text, never a crash."""
        try:
            return call(*args, **kwargs)
        except AdsError as exc:
            reason = exc.message
        except Exception as exc:                        # an answer the toolkit did not expect is still not a crash
            reason = "%s: %s" % (type(exc).__name__, exc)
        self.add(level, obj, check, "warn", "could not read it: %s" % clip(reason, 400),
                 "run launch diagnose again; if it keeps failing, look at this object in the ad platform", gate=False)
        return None

    def activation(self):
        info = self.info
        if info["on"]:
            self.add("plan", "plan", "activation", "ok", "switched on %.1f hours ago (%s)" % (info["hours"], info["ts"]))
        elif info["paused_at"]:
            self.add("plan", "plan", "activation", "ok",
                     "switched on at %s, paused with launch rollback at %s (on for %.1f hours)"
                     % (info["ts"], info["paused_at"], info["hours"]))
        else:
            self.add("plan", "plan", "activation", "warn",
                     "the ledger holds no activation of this plan, so nothing should deliver yet",
                     "show the plan to the user, then run: %s launch activate --file PLAN" % SELF, gate=False)

    def delivery(self, impressions, summary, suspects, steps):
        """The verdict on delivery: impressions over the stretch the plan was on, against what the checks above found.

        A paused plan is judged on the hours it was on inside its schedule, so an ad that never delivered is not forgotten
        once somebody pauses it.
        """
        info = self.info
        if impressions is None or not info["ever"]:
            return
        self.add("plan", "plan", "impressions", "ok", summary)
        if impressions > 0:
            self.add("plan", "plan", "delivery", "ok", "delivering: %d impressions" % impressions)
            return
        live, hours, inside = info["on"], info["hours"], self.inside_hours()
        early = hours < TOO_EARLY_HOURS
        when = "%.1f hours after activation" % hours if live else "in the %.1f hours it was on before the pause" % hours
        fails = [r for r in self.gate if r["state"] == "fail"]
        warns = [r for r in self.gate if r["state"] == "warn"]
        if fails:
            names = ", ".join(sorted({"%s %s" % (r["level"], r["check"]) for r in fails}))
            self.add("plan", "plan", "delivery", "warn" if early else "fail",
                     "no impressions %s%s; blocked by: %s"
                     % (when, " (too early to call it stuck, but it is already blocked)" if early and live else "", names),
                     "fix the failed checks above first, then run launch diagnose again", gate=False)
        elif warns:
            self.add("plan", "plan", "delivery", "warn",
                     "no impressions %s; still waiting on: %s"
                     % (when, ", ".join(sorted({"%s %s" % (r["level"], r["check"]) for r in warns}))),
                     "wait for the review or learning phase to finish, then run launch diagnose again", gate=False)
        elif inside < TOO_EARLY_HOURS:
            if live:
                self.add("plan", "plan", "delivery", "warn",
                         "too early: %.1f hours inside the schedule since activation and no impressions yet. Everything reads "
                         "back as approved, on and inside its schedule; delivery can take several hours to start" % inside,
                         "run launch diagnose again once %d hours have passed since activation" % TOO_EARLY_HOURS, gate=False)
            else:
                self.add("plan", "plan", "delivery", "warn",
                         "was on %.1f h inside its schedule, 0 impressions: too short to judge (switched on %s, paused %s)"
                         % (inside, info["ts"], info["paused_at"]),
                         "a longer run is needed before it can be called stuck", gate=False)
        else:
            what = ("approved, switched on, schedule open and still 0 impressions %.1f hours after activation" % inside
                    if live else "was on %.1f h inside its schedule, 0 impressions (switched on %s, paused %s)"
                    % (inside, info["ts"], info["paused_at"]))
            self.add("plan", "plan", "delivery", "fail", "%s. Suspects: %s" % (what, "; ".join(suspects)),
                     " ".join("%d) %s." % (i, step) for i, step in enumerate(steps, 1)), gate=False)


def since_until(info):
    """The dates to read metrics over: from the last activation to its pause, or to today while it is on."""
    return info["since"], info["until"]


# ── Meta ─────────────────────────────────────────────────────────────────

META_STATUS = {
    "ACTIVE": ("ok", "", ""),
    "PAUSED": ("fail", "switched off", "switch it on: %s launch activate --file PLAN --yes, after the user agreed to spend"),
    "CAMPAIGN_PAUSED": ("fail", "paused because its campaign is paused", "the campaign is off: see the campaign line"),
    "ADSET_PAUSED": ("fail", "paused because its ad set is paused", "the ad set is off: see the ad set line"),
    "DISAPPROVED": ("fail", "disapproved in review", "read the review line, fix what it names, then edit or recreate the ad"),
    "WITH_ISSUES": ("warn", "delivers with issues", "read the issues line"),
    "PENDING_REVIEW": ("warn", "still in review", "wait for the review; it normally takes up to 24 hours"),
    "IN_PROCESS": ("warn", "being processed by Meta", "wait a few minutes and run launch diagnose again"),
    "PREAPPROVED": ("warn", "approved, waiting for its start time", "check the schedule line"),
    "PENDING_BILLING_INFO": ("fail", "waiting for billing information", "add a payment method in Ads Manager, Billing"),
    "ARCHIVED": ("fail", "archived", "an archived object never delivers: recreate it"),
    "DELETED": ("fail", "deleted", "a deleted object never delivers: recreate it"),
}
META_PAUSED = ("PAUSED", "CAMPAIGN_PAUSED", "ADSET_PAUSED")
META_ACCOUNT = {1: "active", 2: "disabled", 3: "unsettled (an unpaid balance)", 7: "pending risk review",
                8: "pending settlement", 9: "in grace period", 100: "pending closure", 101: "closed",
                201: "any active", 202: "any closed"}
META_FIELDS = {
    "campaign": "name,status,effective_status,issues_info,recommendations,daily_budget,budget_remaining",
    "adset": "name,status,effective_status,start_time,end_time,daily_budget,lifetime_budget,budget_remaining,"
             "optimization_goal,issues_info,recommendations,learning_stage_info",
    "ad": "name,status,effective_status,issues_info,recommendations,ad_review_feedback,failed_delivery_checks",
}
META_SUSPECTS = [
    "Meta can keep a new ad in its own \"preparing\" state for a day or two while every status already reads ACTIVE",
    "the Instagram identity of the ad: a profile that is only backed by the Facebook Page instead of a real linked "
    "Instagram account",
    "a new ad account, Page or Instagram account with no delivery history",
]
META_STEPS = [
    "open Ads Manager and read the Delivery column of the ad set and the ad: it names what Meta is waiting for",
    "if there are still 0 impressions 48 hours after activation, recreate the ad set and the ad instead of editing them",
    "to isolate the cause, run one test: an image ad, Facebook feed only, with a real Instagram account instead of the "
    "Page's, on a small budget (about 5 USD), then run launch diagnose on it",
]


def flatten(value):
    """Every string inside a value, keys first: ad_review_feedback nests reasons as {placement: {reason: code}}."""
    if isinstance(value, dict):
        out = []
        for key, item in value.items():
            out.append(str(key))
            out.extend(flatten(item))
        return out
    if isinstance(value, list):
        return [text for item in value for text in flatten(item)]
    return [str(value)] if value not in (None, "") else []


def meta_account(audit, ctx):
    obj = "account"
    info = audit.read("account", obj, "status", meta.get, ctx, "{account}", {
        "fields": "name,account_status,disable_reason,amount_spent,spend_cap,funding_source_details,currency"})
    if info is None:
        return
    obj = label("account", meta.account(ctx), info.get("name"))
    status = info.get("account_status")
    reason = info.get("disable_reason")
    if status == 1:
        audit.add("account", obj, "status", "ok", "account status 1 (active)")
    else:
        audit.add("account", obj, "status", "fail",
                  "account status %s (%s)%s" % (status, META_ACCOUNT.get(status, "unknown"),
                                                ", disable_reason %s" % reason if reason else ""),
                  "open Account Quality in Meta Business Support Home and clear what it lists; nothing delivers until then")
    funding = info.get("funding_source_details")
    if funding:
        audit.add("account", obj, "funding", "ok", "payment method on file%s" % (
            ": %s" % funding["display_string"] if isinstance(funding, dict) and funding.get("display_string") else ""))
    else:
        audit.add("account", obj, "funding", "fail", "the account has no payment method (funding source)",
                  "add a payment method in Ads Manager, Billing")
    cap, spent = whole(info.get("spend_cap")), whole(info.get("amount_spent"))
    if cap <= 0:
        audit.add("account", obj, "spend cap", "ok", "no account spend cap (amount spent so far: %d)" % spent)
    elif spent >= cap:
        audit.add("account", obj, "spend cap", "fail", "account spend cap reached: spent %d of %d (account currency, minor units)"
                  % (spent, cap), "raise or remove the account spend cap in Ads Manager, Billing settings")
    elif spent >= cap * 0.9:
        audit.add("account", obj, "spend cap", "warn", "account spend cap nearly reached: spent %d of %d" % (spent, cap),
                  "raise the account spend cap before delivery stops")
    else:
        audit.add("account", obj, "spend cap", "ok", "spent %d of the %d account spend cap" % (spent, cap))


def meta_schedule(audit, level, obj, info):
    audit.schedule(level, obj, parse_time(info.get("start_time")), parse_time(info.get("end_time")),
                   info.get("start_time"), info.get("end_time"))


def meta_object(audit, ctx, level, item):
    ident = item["id"]
    info = audit.read(level, label(level, ident), "status", meta.get, ctx, ident, {"fields": META_FIELDS[level]})
    if info is None:
        return None
    obj = label(level, ident, info.get("name"))
    effective = info.get("effective_status") or info.get("status")
    state, word, advice = META_STATUS.get(effective, ("warn", "state not known to this audit", "read it in Ads Manager"))
    detail = "status %s, effective_status %s: %s" % (info.get("status"), effective, word) if word else \
        "status %s, effective_status %s" % (info.get("status"), effective)
    advice = advice.replace("%s", SELF)
    if state == "fail" and effective in META_PAUSED and audit.expected_off:
        state, detail, advice = "ok", "status %s, effective_status %s: %s" % (info.get("status"), effective, audit.off_reason()), ""
    audit.add(level, obj, "status", state, detail, advice)
    if level == "ad":
        reasons = flatten(info.get("ad_review_feedback"))
        if effective == "DISAPPROVED":
            audit.add(level, obj, "review", "fail", "disapproved: %s" % (clip("; ".join(reasons)) or "Meta gave no reason"),
                      "fix what the reason names, then edit the ad (it is reviewed again) or create a new one")
        elif reasons:
            audit.add(level, obj, "review", "warn", "review feedback: %s" % clip("; ".join(reasons)),
                      "read it in Ads Manager and fix it before it turns into a disapproval")
        elif effective in ("PENDING_REVIEW", "IN_PROCESS"):
            audit.add(level, obj, "review", "warn", "waiting for review", "wait; run launch diagnose again later")
        else:
            audit.add(level, obj, "review", "ok", "no review feedback")
    issues = info.get("issues_info") or []
    if issues:
        text = "; ".join("%s: %s" % (i.get("error_summary") or i.get("error_code"), i.get("error_message") or "")
                         for i in issues if isinstance(i, dict))
        audit.add(level, obj, "issues", "warn", clip(text), "fix what issues_info names; Meta shows the same list in Ads Manager")
    checks = info.get("failed_delivery_checks") or []
    if checks:
        text = "; ".join("%s: %s" % (c.get("summary") or c.get("check_name"), c.get("description") or "")
                         for c in checks if isinstance(c, dict))
        audit.add(level, obj, "delivery checks", "fail", clip(text), "fix what the failed delivery check names")
    tips = info.get("recommendations") or []
    if tips:
        audit.add(level, obj, "recommendations", "warn",
                  clip("; ".join(t.get("title") or t.get("message") or "" for t in tips if isinstance(t, dict))),
                  "advice from Meta, not a fault: apply it if the user agrees", gate=False)
    if info.get("daily_budget"):
        left, daily = whole(info.get("budget_remaining")), whole(info.get("daily_budget"))
        if "budget_remaining" in info and left <= 0:
            audit.add(level, obj, "budget", "warn", "today's budget of %d (minor units) is used up" % daily,
                      "delivery resumes tomorrow; raise the budget only after the user agreed", gate=False)
        else:
            audit.add(level, obj, "budget", "ok", "daily budget %d, remaining %s (minor units)"
                      % (daily, info.get("budget_remaining", "unknown")))
    if level == "adset":
        meta_schedule(audit, level, obj, info)
        learning = (info.get("learning_stage_info") or {}).get("status")
        if learning:
            audit.add(level, obj, "learning", "warn" if learning == "FAIL" else "ok", "learning stage %s" % learning,
                      "the ad set cannot exit learning on this budget or audience: widen the audience or raise the budget"
                      if learning == "FAIL" else "")
        params = {"optimization_goal": info["optimization_goal"]} if info.get("optimization_goal") else None
        data = audit.read(level, obj, "audience", meta.get, ctx, "%s/delivery_estimate" % ident, params)
        if data is not None:
            row = (data.get("data") or [{}])[0]
            low, high = row.get("estimate_mau_lower_bound"), row.get("estimate_mau_upper_bound")
            if row.get("estimate_ready") is False:
                audit.add(level, obj, "audience", "warn", "Meta has not finished the audience estimate", "run it again later")
            elif not low and not high:
                audit.add(level, obj, "audience", "fail", "the estimated audience is 0: the targeting reaches nobody",
                          "widen the locations, ages or interests of the ad set")
            else:
                audit.add(level, obj, "audience", "ok", "estimated audience %s to %s people"
                          % ("{:,}".format(whole(low)), "{:,}".format(whole(high))))
    return info


def meta_creative(audit, ctx, item):
    ident = item["id"]
    info = audit.read("creative", label("creative", ident), "status", meta.get, ctx, ident, {"fields": "id,name,status"})
    if info is None:
        return
    obj = label("creative", ident, info.get("name"))
    status = info.get("status")
    if status in (None, "ACTIVE"):
        audit.add("creative", obj, "status", "ok", "status %s" % (status or "not reported"))
    elif status == "IN_PROCESS":
        audit.add("creative", obj, "status", "warn", "status IN_PROCESS: Meta is still processing it", "wait and run again")
    else:
        audit.add("creative", obj, "status", "fail", "status %s" % status, "an ad cannot use this creative: create a new one")


def meta_delivery(audit, ctx, campaigns):
    since, until = since_until(audit.info)
    total, spend, platforms, failed = 0, 0.0, {}, False
    for item in campaigns:
        rows = audit.read("campaign", label("campaign", item["id"]), "insights", meta.insights, ctx, item["id"], "campaign",
                          since=since, until=until, fields="impressions,spend")
        if rows is None:
            failed = True
            continue
        total += sum(whole(r.get("impressions")) for r in rows)
        spend += sum(float(r.get("spend") or 0) for r in rows)
        if sum(whole(r.get("impressions")) for r in rows):
            split = audit.read("campaign", label("campaign", item["id"]), "insights by platform", meta.insights, ctx,
                               item["id"], "campaign", since=since, until=until, fields="impressions",
                               breakdowns="publisher_platform")
            for row in split or []:
                name = row.get("publisher_platform") or "unknown"
                platforms[name] = platforms.get(name, 0) + whole(row.get("impressions"))
    if failed:
        return
    where = ", ".join("%s %d" % kv for kv in sorted(platforms.items(), key=lambda kv: -kv[1]))
    audit.delivery(total, "%d impressions and %.2f spend from %s to %s%s" % (total, spend, since, until, "; " + where if where else ""),
                   META_SUSPECTS, META_STEPS)


def meta_audit(audit, ctx, found):
    meta_account(audit, ctx)
    kinds = {k: [i for i in found if i["type"] == k] for k in ("campaign", "adset", "ad", "creative")}
    active = []
    for level in ("campaign", "adset", "ad"):
        for item in kinds[level]:
            info = meta_object(audit, ctx, level, item)
            if level == "ad" and info and info.get("status") == "ACTIVE":
                active.append(label("ad", item["id"], info.get("name")))
    for item in kinds["creative"]:
        meta_creative(audit, ctx, item)
    volume = audit.read("account", "account", "ads running", meta.get, ctx, "{account}/ads_volume")
    if volume is not None:
        count = whole((volume.get("data") or [{}])[0].get("ads_running_or_in_review_count"))
        if count == 0 and active:
            audit.add("account", "account", "ads running", "warn",
                      "Meta counts 0 ads running or in review although %s is ACTIVE" % active[0],
                      "Meta may still be preparing the ad: read the Delivery column in Ads Manager; if it stays at 0, "
                      "recreate the ad after 48 hours", gate=False)
        else:
            audit.add("account", "account", "ads running", "ok", "%d ad(s) running or in review" % count)
    if audit.info["ever"] and kinds["campaign"]:
        meta_delivery(audit, ctx, kinds["campaign"])


# ── Google ───────────────────────────────────────────────────────────────

GOOGLE_REASONS = {
    "BIDDING_STRATEGY_LEARNING": ("the bidding strategy is still learning", "leave bids and budget alone for about two weeks"),
    "BIDDING_STRATEGY_LIMITED": ("the bidding strategy is limited by its settings", "loosen the target or the bid limits"),
    "BIDDING_STRATEGY_MISCONFIGURED": ("the bidding strategy is set up wrongly", "fix the bidding strategy in the campaign"),
    "BUDGET_CONSTRAINED": ("the daily budget limits how often the ads can show", "raise the budget if the user agrees"),
    "BUDGET_MISCONFIGURED": ("the campaign budget is set up wrongly", "fix the budget of the campaign"),
    "MOST_ADS_UNDER_REVIEW": ("most ads are still under review", "wait for the review: it normally takes one business day"),
    "HAS_ADS_DISAPPROVED": ("some ads are disapproved", "read the ad lines below and fix the policy topic they name"),
    "HAS_ADS_LIMITED_BY_POLICY": ("some ads are limited by policy", "read the ad lines below and fix the policy topic"),
    "ALL_ADS_DISAPPROVED": ("every ad is disapproved", "fix the policy topic named on the ad lines, then resubmit"),
    "CAMPAIGN_PAUSED": ("the campaign is paused", "switch it on with launch activate --yes after the user agreed"),
    "CAMPAIGN_PENDING": ("the campaign has not reached its start date", "check the start date"),
    "CAMPAIGN_ENDED": ("the campaign passed its end date", "set a later end date"),
    "CAMPAIGN_REMOVED": ("the campaign is removed", "create it again: a removed campaign never delivers"),
    "CAMPAIGN_DRAFT": ("the campaign is still a draft", "publish the draft"),
    "SEARCH_VOLUME_LIMITED": ("the keywords have low search volume", "add broader keywords"),
    "NO_AD_GROUPS": ("the campaign has no ad groups", "add an ad group"),
    "AD_GROUPS_PAUSED": ("every ad group is paused", "enable an ad group"),
    "NO_AD_GROUP_ADS": ("no ad group has an ad", "add an ad"),
    "AD_GROUP_ADS_PAUSED": ("every ad is paused", "enable an ad"),
    "NO_KEYWORDS": ("no ad group has keywords", "add keywords"),
    "KEYWORDS_PAUSED": ("every keyword is paused", "enable a keyword"),
    "MISSING_LEAD_FORM_EXTENSION": ("the campaign needs a lead form asset", "add the lead form asset"),
}
GOOGLE_PRIMARY = {"ELIGIBLE": "ok", "LEARNING": "warn", "LIMITED": "warn", "PENDING": "warn", "PAUSED": "fail",
                  "REMOVED": "fail", "ENDED": "fail", "NOT_ELIGIBLE": "fail", "MISCONFIGURED": "fail"}
GOOGLE_APPROVAL = {"APPROVED": "ok", "APPROVED_LIMITED": "warn", "UNDER_REVIEW": "warn", "AREA_OF_INTEREST_ONLY": "warn",
                   "DISAPPROVED": "fail"}
GOOGLE_SUSPECTS = [
    "ads still in review or learning in a way the status fields do not show",
    "bids or budget too low to win auctions, or keywords with low search volume",
    "targeting too narrow: audience, location or language",
]
GOOGLE_STEPS = [
    "open the campaign in Google Ads and read its Status column and the hover text",
    "read the impression share and the search terms report once the first impressions come in",
    "a Demand Gen or Performance Max campaign can need one to two days after it is enabled; widen targeting if it stays at 0",
]


def explain_reasons(reasons):
    """(text, next steps) for Google's status reasons: a sentence for the known ones, the raw name for the rest."""
    text, steps = [], []
    for reason in reasons:
        known = GOOGLE_REASONS.get(reason)
        text.append("%s (%s)" % (reason, known[0]) if known else reason)
        if known and known[1] not in steps:
            steps.append(known[1])
    return "; ".join(text), "; ".join(steps)


def google_account(audit, ctx):
    rows = audit.read("account", "account", "status", google.search, ctx, "SELECT customer.status, customer.currency_code FROM customer")
    if rows is not None:
        info = (rows[0] if rows else {}).get("customer", {})
        if info.get("status") in (None, "ENABLED"):
            audit.add("account", "account", "status", "ok", "account %s, currency %s" % (info.get("status", "ENABLED"),
                                                                                    info.get("currencyCode", "?")))
        else:
            audit.add("account", "account", "status", "fail", "account status %s" % info["status"],
                      "open the account in Google Ads and clear what blocks it")
    rows = audit.read("account", "account", "billing", google.search, ctx, "SELECT billing_setup.status FROM billing_setup")
    if rows is not None:
        found = [r.get("billingSetup", {}).get("status") for r in rows]
        if "APPROVED" in found:
            audit.add("account", "account", "billing", "ok", "billing setup APPROVED")
        elif found:
            audit.add("account", "account", "billing", "fail", "billing setup status %s, not APPROVED" % ", ".join(map(str, found)),
                      "finish or fix the billing setup in Google Ads, Billing")
        else:
            audit.add("account", "account", "billing", "fail", "the account has no billing setup",
                      "add a payment profile in Google Ads, Billing")
    rows = audit.read("account", "account", "account budget", google.search, ctx, "SELECT account_budget.status FROM account_budget")
    if rows is not None:
        found = [r.get("accountBudget", {}).get("status") for r in rows]
        if not found:
            audit.add("account", "account", "account budget", "ok", "no account budget (normal for automatic payments)")
        elif "APPROVED" in found:
            audit.add("account", "account", "account budget", "ok", "account budget APPROVED")
        else:
            audit.add("account", "account", "account budget", "warn", "account budget status %s, not APPROVED" % ", ".join(map(str, found)),
                      "an ended or cancelled account budget stops delivery on invoiced accounts: renew it in Billing")


GOOGLE_PAUSED_REASONS = {"CAMPAIGN_PAUSED", "AD_GROUPS_PAUSED", "AD_GROUP_ADS_PAUSED", "AD_GROUP_PAUSED", "AD_PAUSED"}


def google_primary(audit, level, obj, primary, reasons):
    text, steps = explain_reasons(reasons)
    state = GOOGLE_PRIMARY.get(primary, "warn")
    detail = "primary status %s%s" % (primary, ": %s" % text if text else "")
    if state == "fail" and audit.expected_off and (primary == "PAUSED" or (reasons and set(reasons) <= GOOGLE_PAUSED_REASONS)):
        state, detail, steps = "ok", "%s; %s" % (detail, audit.off_reason()), ""
    audit.add(level, obj, "primary status", state, detail, steps)


def google_campaign(audit, ctx, name):
    query = ("SELECT campaign.name, campaign.status, campaign.primary_status, campaign.primary_status_reasons, "
             "campaign.serving_status, campaign.start_date_time, campaign.end_date_time, campaign_budget.amount_micros "
             "FROM campaign WHERE campaign.resource_name = '%s'" % name)
    rows = audit.read("campaign", label("campaign", name), "status", google.search, ctx, query)
    if not rows:
        if rows is not None:
            audit.add("campaign", label("campaign", name), "status", "fail", "Google does not return this campaign",
                      "it was removed outside the toolkit: create it again")
        return
    campaign, budget = rows[0].get("campaign", {}), rows[0].get("campaignBudget", {})
    obj = label("campaign", name.rsplit("/", 1)[-1], campaign.get("name"))
    status = campaign.get("status")
    if status != "ENABLED" and audit.expected_off:
        audit.add("campaign", obj, "status", "ok", "campaign.status %s: %s" % (status, audit.off_reason()))
    else:
        audit.add("campaign", obj, "status", "ok" if status == "ENABLED" else "fail", "campaign.status %s" % status,
                  "" if status == "ENABLED" else "switch it on with launch activate --yes after the user agreed to spend")
    primary, reasons = campaign.get("primaryStatus"), campaign.get("primaryStatusReasons") or []
    google_primary(audit, "campaign", obj, primary, reasons)
    serving = campaign.get("servingStatus")
    if serving:
        audit.add("campaign", obj, "serving", "ok" if serving == "SERVING" else "warn", "serving status %s" % serving,
                  "" if serving == "SERVING" else "see the primary status line and the schedule")
    start, end = campaign.get("startDateTime"), campaign.get("endDateTime")
    if end and end.startswith("2037"):
        end = None                                      # Google's "no end date"
    audit.schedule("campaign", obj, parse_time(start), parse_time(end), start, end)
    if budget.get("amountMicros"):
        audit.add("campaign", obj, "budget", "ok", "daily budget %.2f (account currency)" % (whole(budget["amountMicros"]) / 1e6))
    return obj


def google_ads(audit, ctx, name):
    query = ("SELECT ad_group_ad.ad.id, ad_group_ad.ad.name, ad_group_ad.status, ad_group_ad.policy_summary.approval_status, "
             "ad_group_ad.policy_summary.review_status, ad_group_ad.policy_summary.policy_topic_entries, "
             "ad_group_ad.primary_status, ad_group_ad.primary_status_reasons, ad_group.name FROM ad_group_ad "
             "WHERE campaign.resource_name = '%s' AND ad_group_ad.status != 'REMOVED'" % name)
    rows = audit.read("ad", label("campaign", name.rsplit("/", 1)[-1]), "review", google.search, ctx, query)
    for row in rows or []:        # every ad counts, also one that Google made itself
        ad = row.get("adGroupAd", {})
        obj = label("ad", ad.get("ad", {}).get("id"), ad.get("ad", {}).get("name"))
        if ad.get("status") != "ENABLED" and audit.expected_off:
            audit.add("ad", obj, "status", "ok", "ad_group_ad.status %s: %s" % (ad.get("status"), audit.off_reason()))
        else:
            audit.add("ad", obj, "status", "ok" if ad.get("status") == "ENABLED" else "fail",
                      "ad_group_ad.status %s" % ad.get("status"),
                      "" if ad.get("status") == "ENABLED" else "enable the ad after the user agreed")
        policy = ad.get("policySummary", {})
        approval = policy.get("approvalStatus")
        topics = ", ".join("%s (%s)" % (t.get("topic"), t.get("type")) for t in policy.get("policyTopicEntries") or [])
        audit.add("ad", obj, "review", GOOGLE_APPROVAL.get(approval, "warn"),
                  "approval %s, review %s%s" % (approval, policy.get("reviewStatus"), "; policy topics: %s" % topics if topics else ""),
                  {"ok": "", "warn": "wait for the review, or read the policy topic and fix it"}.get(
                      GOOGLE_APPROVAL.get(approval, "warn"), "fix the policy topic named here, then edit the ad to send it to review again"))
        primary = ad.get("primaryStatus")
        if primary:
            google_primary(audit, "ad", obj, primary, ad.get("primaryStatusReasons") or [])


def google_audit(audit, ctx, found):
    google_account(audit, ctx)
    campaigns = [i["id"] for i in found if i["type"] == "campaigns"]
    for name in campaigns:
        google_campaign(audit, ctx, name)
        google_ads(audit, ctx, name)
    if not (audit.info["ever"] and campaigns):
        return
    since, until = since_until(audit.info)
    impressions, clicks, cost, failed = 0, 0, 0, False
    for name in campaigns:
        rows = audit.read("campaign", label("campaign", name.rsplit("/", 1)[-1]), "metrics", google.search, ctx,
                          "SELECT campaign.resource_name, metrics.impressions, metrics.clicks, metrics.cost_micros FROM campaign "
                          "WHERE campaign.resource_name = '%s' AND segments.date BETWEEN '%s' AND '%s'" % (name, since, until))
        if rows is None:
            failed = True
            continue
        impressions += sum(whole(r.get("metrics", {}).get("impressions")) for r in rows)
        clicks += sum(whole(r.get("metrics", {}).get("clicks")) for r in rows)
        cost += sum(whole(r.get("metrics", {}).get("costMicros")) for r in rows)
    if not failed:
        audit.delivery(impressions, "%d impressions, %d clicks, cost %.2f from %s to %s" % (impressions, clicks, cost / 1e6, since, until),
                       GOOGLE_SUSPECTS, GOOGLE_STEPS)


# ── TikTok ───────────────────────────────────────────────────────────────

TIKTOK_SUSPECTS = [
    "an audience too narrow or a bid too low for the optimization goal",
    "the ad group is in its learning phase",
    "a creative that passed review but cannot be delivered to the chosen placements",
]
TIKTOK_STEPS = [
    "open TikTok Ads Manager and read the status column of the ad group and the ad",
    "run the Diagnosis tool of the ad group in Ads Manager",
    "widen the audience or raise the bid with the user's agreement",
]
TIKTOK_GET = {"campaign": ("campaign/get", "campaign_ids", "campaign_name"), "adgroup": ("adgroup/get", "adgroup_ids", "adgroup_name"),
              "ad": ("ad/get", "ad_ids", "ad_name")}


def tiktok_state(operation, secondary):
    """(state, plain words, next step) for the status pair of a TikTok object."""
    word = str(secondary or "")
    if operation == "DISABLE" or word.endswith("_DISABLE"):
        return "fail", "switched off", "switch it on with launch activate --yes after the user agreed; if the parent is off, start there"
    if "DELIVERY_OK" in word or word.endswith("_ENABLE"):
        return "ok", "delivering", ""
    for needle, state, words, advice in (
            ("DENY", "fail", "review denied", "read the review line, fix the creative, then submit it again"),
            ("FAIL", "fail", "processing failed", "upload the file again"),
            ("AUDIT", "warn", "in review", "wait for the review; it normally takes up to 24 hours"),
            ("NOT_START", "fail", "the schedule has not started", "move the start time to now, or wait"),
            ("TIME_DONE", "fail", "the schedule has ended", "set a later end time"),
            ("EXCEED", "fail", "budget or balance used up", "raise the budget or top up the balance, with the user's agreement"),
            ("DELETE", "fail", "deleted", "a deleted object never delivers: recreate it")):
        if needle in word:
            return state, words, advice
    return "warn", "state not known to this audit", "read it in TikTok Ads Manager"


def texts(value, wanted=("reason", "reject", "denied", "message", "suggest"), keyed=False):
    """Strings under keys that name a reason, at any depth."""
    if isinstance(value, dict):
        return [t for k, v in value.items() for t in texts(v, wanted, any(w in str(k).lower() for w in wanted))]
    if isinstance(value, list):
        return [t for v in value for t in texts(v, wanted, keyed)]
    return [str(value)] if keyed and value not in (None, "") else []


def tiktok_object(audit, ctx, level, item):
    smart = bool(item.get("smart_plus"))
    route, field, name_key = TIKTOK_GET[level]
    if smart:
        route, field = "smart_plus/" + route, "smart_plus_ad_ids" if level == "ad" else field
    ident = item["id"]
    data = audit.read(level, label(level, ident), "status", tiktok.get, ctx, route, {"filtering": {field: [ident]}})
    if data is None:
        return
    row = (data.get("list") or [{}])[0]
    obj = label(level, ident, row.get(name_key))
    operation, secondary = row.get("operation_status"), row.get("secondary_status")
    state, words, advice = tiktok_state(operation, secondary)
    if state == "fail" and words == "switched off" and audit.expected_off:
        state, words, advice = "ok", audit.off_reason(), ""
    audit.add(level, obj, "status", state, "operation_status %s, secondary_status %s: %s" % (operation, secondary, words), advice)
    if level == "adgroup":
        start, end = row.get("schedule_start_time"), row.get("schedule_end_time")
        audit.schedule(level, obj, parse_time(start), parse_time(end), start, end)
    if level == "ad" and "DENY" in str(secondary):
        review = audit.read(level, obj, "review", tiktok.get, ctx, "ad/review_info", {"ad_ids": [ident]})
        if review is not None:
            mine = [r for r in review.get("list") or [] if str(r.get("ad_id", ident)) == str(ident)] or review.get("list") or []
            reasons = [t for r in mine for t in texts(r)] or ([clip(json.dumps(mine, ensure_ascii=False))] if mine else [])
            audit.add(level, obj, "review", "fail", "denied: %s" % (clip("; ".join(reasons)) or "TikTok gave no reason"),
                      "fix what the reason names in the creative, then submit the ad for review again")


def tiktok_audit(audit, ctx, found):
    data = audit.read("account", "account", "status", tiktok.get, ctx, "advertiser/info", {
        "advertiser_ids": [tiktok.advertiser(ctx)], "fields": ["name", "status", "balance", "currency"]})
    if data is not None:
        row = (data.get("list") or [{}])[0]
        obj = label("advertiser", tiktok.advertiser(ctx), row.get("name"))
        if row.get("status") == "STATUS_ENABLE":
            audit.add("account", obj, "status", "ok", "advertiser status STATUS_ENABLE")
        else:
            audit.add("account", obj, "status", "fail", "advertiser status %s" % row.get("status"),
                      "open TikTok Ads Manager, Account Center, and clear what blocks the account")
        if row.get("balance") is not None:
            if float(row["balance"]) <= 0:
                audit.add("account", obj, "balance", "fail", "balance is %s %s" % (row["balance"], row.get("currency", "")),
                          "top up the balance in TikTok Ads Manager, Billing (ignore this on an invoiced account)")
            else:
                audit.add("account", obj, "balance", "ok", "balance %s %s" % (row["balance"], row.get("currency", "")))
    for level in ("campaign", "adgroup", "ad"):
        for item in found:
            if item["type"] == level:
                tiktok_object(audit, ctx, level, item)
    campaigns = [i["id"] for i in found if i["type"] == "campaign"]
    if not (audit.info["ever"] and campaigns):
        return
    since, until = since_until(audit.info)
    rows = audit.read("campaign", "campaigns of the plan", "report", tiktok.report, ctx, "AUCTION_CAMPAIGN", since, until,
                      "impressions,spend", "campaign_id")
    if rows is None:
        return
    mine = [r for r in rows if str(r.get("campaign_id")) in campaigns]
    impressions = sum(whole(r.get("impressions")) for r in mine)
    spend = sum(float(r.get("spend") or 0) for r in mine)
    audit.delivery(impressions, "%d impressions and %.2f spend from %s to %s" % (impressions, spend, since, until), TIKTOK_SUSPECTS, TIKTOK_STEPS)


# ── entry points ─────────────────────────────────────────────────────────

def diagnose(ctx, path):
    """The findings for the plan in PATH. Reads only; a read that fails becomes a warning."""
    doc = launch.load_plan(path)
    if not launch.applied_state(ctx, doc["name"]):
        raise Refused("the ledger holds nothing applied for plan %s" % doc["name"],
                      "there is nothing to audit before launch apply has run")
    found = launch.entities(ctx, doc["name"])
    audit = Audit(ctx, activation(ctx, doc["name"]))
    audit.activation()
    {"meta": meta_audit, "google": google_audit, "tiktok": tiktok_audit}[doc["platform"]](audit, ctx, found)
    return audit.rows


def verdict(findings):
    count = {state: sum(1 for f in findings if f["state"] == state) for state in RANK}
    tally = "%d fail, %d warn, %d ok" % (count["fail"], count["warn"], count["ok"])
    worst = next((f for state in ("fail", "warn") for f in findings if f["state"] == state), None)
    if not worst:
        return "verdict: OK - %s: nothing to fix" % tally
    return "verdict: %s - %s. First: %s %s: %s" % (
        "FAIL" if count["fail"] else "WARN", tally, worst["object"], worst["check"], clip(worst["detail"], 90))


def table(findings):
    lines = ["%-5s %-9s %-34s %-16s %s" % ("STATE", "LEVEL", "OBJECT", "CHECK", "DETAIL")]
    for f in findings:
        lines.append("%-5s %-9s %-34s %-16s %s" % (f["state"].upper(), f["level"], clip(f["object"], 34), f["check"], f["detail"]))
        if f["next"] and f["state"] != "ok":
            lines.append("%-5s %s -> %s" % ("", " " * 9, f["next"]))
    lines.append("")
    lines.append(verdict(findings))
    return "\n".join(lines) + "\n"
