"""Which keys the plugin uses, where each one comes from, and whether they work."""
from __future__ import annotations

from .core import AdsError

GUIDES = "ads/tools/guides"

SERVICES = [
    {"name": "firecrawl", "title": "Firecrawl", "group": "research",
     "use": "reads your site and competitor pages, extracts the brand kit",
     "keys": ["FIRECRAWL_API_KEY"], "optional": [], "guide": "keys-research.md",
     "where": "https://www.firecrawl.dev/app/api-keys", "how": "sign in, create a key (it starts with fc-); the free plan needs no card"},
    {"name": "apify", "title": "Apify", "group": "research",
     "use": "public ad libraries, social content, reviews",
     "keys": ["APIFY_TOKEN"], "optional": [], "guide": "keys-research.md",
     "where": "https://console.apify.com/settings/integrations",
     "how": "Settings > API & Integrations > Personal API tokens > Create a new token"},
    {"name": "dataforseo", "title": "DataForSEO", "group": "research",
     "use": "keyword volumes, CPC, competitors' paid keywords",
     "keys": ["DATAFORSEO_USERNAME", "DATAFORSEO_PASSWORD"], "optional": [], "guide": "keys-research.md",
     "where": "app.dataforseo.com/api-access (the dashboard, API Access tab)",
     "how": "API Access tab: the API login and the API password (not the account password)"},
    {"name": "openai", "title": "OpenAI", "group": "creative",
     "use": "images, voice-over, analysis of creatives",
     "keys": ["OPENAI_API_KEY"], "optional": [], "guide": "keys-creative.md",
     "where": "https://platform.openai.com/api-keys", "how": "create a project key; add prepaid credit before the first image"},
    {"name": "gemini", "title": "Gemini", "group": "creative",
     "use": "images, video, voice-over, music, analysis of images and video",
     "keys": ["GEMINI_API_KEY"], "optional": [], "guide": "keys-creative.md",
     "where": "https://aistudio.google.com/api-keys",
     "how": "Create API key; image, video and music need the paid tier (link billing, prepay)"},
    {"name": "fal", "title": "fal.ai", "group": "creative",
     "use": "catalogue of image, video, avatar and audio models",
     "keys": ["FAL_KEY"], "optional": [], "guide": "keys-creative.md",
     "where": "https://fal.ai/dashboard/keys", "how": "Create Key with the API preset; buy credits first"},
    {"name": "google", "title": "Google Ads", "group": "google",
     "use": "keyword planner, campaigns, reports",
     "keys": ["GOOGLE_ADS_CLIENT_ID", "GOOGLE_ADS_CLIENT_SECRET", "GOOGLE_ADS_REFRESH_TOKEN", "GOOGLE_ADS_CUSTOMER_ID"],
     "optional": ["GOOGLE_ADS_LOGIN_CUSTOMER_ID", "GOOGLE_CLOUD_PROJECT", "GOOGLE_APPLICATION_CREDENTIALS"],
     "guide": "keys-google.md", "where": "https://console.cloud.google.com/google/ads-apis/overview",
     "how": "enable the Google Ads API in a Cloud project, apply for Explorer access, create a Desktop OAuth client, "
            "then run: python3 ads/tools/ads.py google login"},
    {"name": "gsc", "title": "Search Console", "group": "google",
     "use": "organic queries and landing pages that seed paid search",
     "keys": ["GOOGLE_ADS_CLIENT_ID", "GOOGLE_ADS_CLIENT_SECRET", "GOOGLE_ADS_REFRESH_TOKEN", "GSC_SITE_URL"],
     "optional": [], "guide": "keys-google.md", "where": "https://search.google.com/search-console",
     "how": "enable the Search Console API in the same Cloud project, log in with the gsc scope, set the property"},
    {"name": "meta", "title": "Meta", "group": "meta",
     "use": "Facebook and Instagram campaigns, targeting search, Ad Library, insights",
     "keys": ["META_ACCESS_TOKEN", "META_AD_ACCOUNT_ID", "META_PAGE_ID"],
     "optional": ["META_APP_ID", "META_APP_SECRET", "META_PIXEL_ID", "META_INSTAGRAM_USER_ID"],
     "guide": "keys-meta.md", "where": "https://business.facebook.com/settings/system-users",
     "how": "create an app with the Marketing API, a system user with the Employee role, assign the ad account and the "
            "Page, generate a token with ads_management"},
    {"name": "tiktok", "title": "TikTok", "group": "tiktok",
     "use": "TikTok campaigns and reports through direct API calls",
     "keys": ["TIKTOK_ACCESS_TOKEN", "TIKTOK_ADVERTISER_ID"],
     "optional": ["TIKTOK_APP_ID", "TIKTOK_APP_SECRET", "TIKTOK_PIXEL_ID"],
     "guide": "keys-tiktok.md", "where": "https://business-api.tiktok.com/portal/apps",
     "how": "the TikTok MCP server needs no key (OAuth in the client); for direct calls register a developer app, "
            "authorize it, then run: python3 ads/tools/ads.py tiktok oauth-exchange --auth-code CODE --write"},
]
BY_NAME = {s["name"]: s for s in SERVICES}


def all_keys():
    names = []
    for service in SERVICES:
        for key in service["keys"] + service["optional"]:
            if key not in names:
                names.append(key)
    return names


def hint_for(key):
    for service in SERVICES:
        if key in service["keys"] or key in service["optional"]:
            return "%s: %s (%s). Put it in ads/.env. Guide: %s/%s" % (
                service["title"], service["how"], service["where"], GUIDES, service["guide"])
    return "put it in ads/.env"


def table(ctx):
    rows = []
    for service in SERVICES:
        for key in service["keys"] + service["optional"]:
            rows.append({"service": service["name"], "variable": key, "needed": key in service["keys"],
                         "set": bool(ctx.env.get(key)), "use": service["use"]})
    return rows


def _live(ctx, name):
    from . import creative, google, meta, recon, tiktok  # late: these modules import core
    checks = {
        "firecrawl": lambda: recon.check_firecrawl(ctx), "apify": lambda: recon.check_apify(ctx),
        "dataforseo": lambda: recon.check_dataforseo(ctx), "openai": lambda: creative.check(ctx, "openai"),
        "gemini": lambda: creative.check(ctx, "gemini"), "fal": lambda: creative.check(ctx, "fal"),
        "google": lambda: google.check(ctx), "gsc": lambda: google.check_gsc(ctx),
        "meta": lambda: meta.check(ctx), "tiktok": lambda: tiktok.check(ctx),
    }
    return checks[name]()


def doctor(ctx, live=False, only=None):
    """One row per service: configured or not, and with live a real read-only call."""
    wanted = [n.strip() for n in only.split(",") if n.strip()] if only else [s["name"] for s in SERVICES]
    unknown = [n for n in wanted if n not in BY_NAME]
    if unknown:
        from .core import Refused
        raise Refused("unknown service %s; use: %s" % (", ".join(unknown), ", ".join(BY_NAME)))
    rows = []
    for name in wanted:
        service = BY_NAME[name]
        missing = [k for k in service["keys"] if not ctx.env.get(k)]
        row = {"service": name, "title": service["title"], "use": service["use"], "missing": missing}
        if missing:
            row["state"] = "not configured" if len(missing) == len(service["keys"]) else "incomplete"
            row["next"] = "%s. %s" % (service["how"], service["where"])
            row["guide"] = "%s/%s" % (GUIDES, service["guide"])
        elif not live:
            row["state"] = "configured"
        else:
            try:
                row["detail"] = _live(ctx, name)
                row["state"] = "working"
            except AdsError as exc:
                row["state"] = "rejected"
                row["detail"] = exc.message
                row["next"] = exc.hint or "%s. %s" % (service["how"], service["where"])
                row["guide"] = "%s/%s" % (GUIDES, service["guide"])
        rows.append(row)
    return rows


def render(rows):
    lines = []
    for row in rows:
        lines.append("%-14s %-15s %s" % (row["title"], row["state"], row.get("detail", "")))
        if row["missing"]:
            lines.append("    missing: %s" % ", ".join(row["missing"]))
        if row.get("next"):
            lines.append("    next: %s" % row["next"])
        if row.get("guide"):
            lines.append("    guide: %s" % row["guide"])
    working = sum(r["state"] in ("working", "configured") for r in rows)
    lines.append("")
    lines.append("%d of %d services ready. Each one is optional: configure what the campaign needs." % (working, len(rows)))
    return "\n".join(lines) + "\n"
