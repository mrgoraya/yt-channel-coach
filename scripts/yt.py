#!/usr/bin/env python3
"""yt-channel-coach data helper. Standard library only, prints JSON.

Works without a key (latest 15 videos from the public RSS feed, autocomplete).
A free YouTube Data API v3 key unlocks full stats, comments and competitor search.

  yt.py key-status
  yt.py save-key                      (reads the key from stdin)
  yt.py channel <@handle|url|UC id> [--max 50]
  yt.py comments <@handle|url|UC id> [--videos 10] [--per-video 100]
  yt.py search "<query>" [--days 30] [--lang hi] [--region IN] [--max 25]
  yt.py suggest "<seed>" [--hl en] [--gl US]
  yt.py compare <you> <competitor> [<competitor> ...]
  yt.py unanswered <@handle> [--videos 10] [--max 60]
  yt.py thumbs [<@handle>] [--search "<query>"] [--max 8] [--out DIR]
  yt.py snapshot <@handle>
  yt.py scorecard <@handle>          (fixed 100-point score and A-F grade)
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

KEY_FILE = Path.home() / ".config" / "yt-channel-coach" / "api_key"
API = "https://www.googleapis.com/youtube/v3/"
UA = {"User-Agent": "Mozilla/5.0 (yt-channel-coach plugin)", "Accept-Language": "en"}


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def out(data):
    print(json.dumps(data, ensure_ascii=False, indent=1))


def fail(msg, **extra):
    out({"error": msg, **extra})
    sys.exit(1)


def get_key():
    key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    if not key and KEY_FILE.exists():
        key = KEY_FILE.read_text().strip()
    return key or None


def http(url, headers=None):
    req = urllib.request.Request(url, headers=headers or UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")


class ApiError(Exception):
    pass


def api(endpoint, **params):
    key = get_key()
    if not key:
        fail("No API key. Run the setup skill first (/yt-channel-coach:setup).", needs_key=True)
    params["key"] = key
    try:
        return json.loads(http(API + endpoint + "?" + urllib.parse.urlencode(params)))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        reason = re.findall(r'"reason":\s*"([^"]+)"', body)
        raise ApiError(f"YouTube API error {e.code}: {reason[0] if reason else 'unknown'}")


def resolve_channel(ref):
    """@handle, channel URL or UC id -> UC id."""
    ref = ref.strip()
    m = re.search(r"(UC[\w-]{22})", ref)
    if m:
        return m.group(1)
    handle = re.search(r"@([\w.\-]+)", ref)
    handle = "@" + handle.group(1) if handle else "@" + ref.lstrip("@")
    if get_key():
        items = api("channels", part="id", forHandle=handle).get("items", [])
        if items:
            return items[0]["id"]
    html = http("https://www.youtube.com/" + urllib.parse.quote(handle))
    m = re.search(r'"externalId":"(UC[\w-]{22})"', html) or re.search(
        r'itemprop="identifier" content="(UC[\w-]{22})"', html)
    if not m:
        fail(f"Could not find the channel {handle}. Check the handle or paste the channel URL.")
    return m.group(1)


def days_since(iso):
    t = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return max((datetime.now(timezone.utc) - t).total_seconds() / 86400, 0.01)


def iso_minutes(d):
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d or "")
    if not m:
        return None
    dd, h, mi, s = (int(x or 0) for x in m.groups())
    return round(dd * 1440 + h * 60 + mi + s / 60, 2)


def is_short_url(vid):
    """youtube.com/shorts/ID stays on /shorts/ for a Short and redirects for a normal video."""
    try:
        req = urllib.request.Request(f"https://www.youtube.com/shorts/{vid}", headers=UA, method="HEAD")
        with urllib.request.urlopen(req, timeout=15) as r:
            return "/shorts/" in r.geturl()
    except Exception:
        return None


def rss_videos(cid):
    ns = {"a": "http://www.w3.org/2005/Atom", "m": "http://search.yahoo.com/mrss/",
          "yt": "http://www.youtube.com/xml/schemas/2015"}
    root = ET.fromstring(http(f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"))
    vids = []
    for e in root.findall("a:entry", ns):
        stats = e.find("m:group/m:community/m:statistics", ns)
        stars = e.find("m:group/m:community/m:starRating", ns)
        pub = e.find("a:published", ns).text
        vids.append({
            "id": e.find("yt:videoId", ns).text,
            "title": e.find("a:title", ns).text,
            "published": pub[:10],
            "days_live": round(days_since(pub), 1),
            "views": int(stats.get("views")) if stats is not None else None,
            "likes": int(stars.get("count")) if stars is not None else None,
            "is_short": is_short_url(e.find("yt:videoId", ns).text),
        })
    return {"channel_title": root.findtext("a:title", None, ns), "videos": vids}


def fetch_channel(ref, max_videos=50):
    cid = resolve_channel(ref)
    if not get_key():
        return {"mode": "no-key (RSS: latest 15 uploads, no subscriber count, no comments)",
                "channel_id": cid, **rss_videos(cid)}
    ch = api("channels", part="snippet,statistics,contentDetails", id=cid)["items"][0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, tok = [], None
    while len(ids) < max_videos:
        p = dict(part="contentDetails", playlistId=uploads, maxResults=50)
        if tok:
            p["pageToken"] = tok
        r = api("playlistItems", **p)
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]
        tok = r.get("nextPageToken")
        if not tok:
            break
    vids = []
    for k in range(0, len(ids[:max_videos]), 50):
        for v in api("videos", part="snippet,statistics,contentDetails",
                     id=",".join(ids[k:k + 50]))["items"]:
            s = v["statistics"]
            views = int(s.get("viewCount", 0))
            mins = iso_minutes(v["contentDetails"]["duration"])
            vids.append({
                "id": v["id"], "title": v["snippet"]["title"],
                "published": v["snippet"]["publishedAt"][:10],
                "days_live": round(days_since(v["snippet"]["publishedAt"]), 1),
                "minutes": mins, "is_short": mins is not None and mins <= 3,
                "views": views, "likes": int(s.get("likeCount", 0)),
                "comments": int(s.get("commentCount", 0)),
                "views_per_day": round(views / days_since(v["snippet"]["publishedAt"]), 1),
                "tags": v["snippet"].get("tags", [])[:15],
            })
    st = ch["statistics"]
    return {"mode": "api", "channel_id": cid, "channel_title": ch["snippet"]["title"],
            "handle": ch["snippet"].get("customUrl", ""),
            "description": ch["snippet"].get("description", "")[:500],
            "subscribers": int(st.get("subscriberCount", 0)), "total_views": int(st.get("viewCount", 0)),
            "video_count": int(st.get("videoCount", 0)), "videos": vids}


def cmd_channel(a):
    out(fetch_channel(a.ref, a.max))


def median(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else 0


def cmd_compare(a):
    """Side-by-side summary of your channel and competitors (needs a key)."""
    if not get_key():
        fail("Compare needs a free API key. Run /yt-channel-coach:setup.", needs_key=True)
    rows = []
    for ref in a.refs:
        d = fetch_channel(ref, 30)
        longs = [v for v in d["videos"] if not v["is_short"]]
        shorts = [v for v in d["videos"] if v["is_short"]]
        recent = sorted(longs, key=lambda v: v["days_live"])[:10]
        med = median([v["views"] for v in recent])
        span = max((recent[-1]["days_live"] if recent else 0), 1)
        top = sorted([v for v in longs if v["days_live"] <= 90], key=lambda v: -v["views"])[:3]
        rows.append({
            "channel": d["channel_title"], "handle": d.get("handle"), "subscribers": d["subscribers"],
            "median_views_last10_long": med,
            "median_views_per_sub": round(med / max(d["subscribers"], 1), 3),
            "long_uploads_per_week": round(len(recent) / span * 7, 2),
            "shorts_share": round(len(shorts) / max(len(d["videos"]), 1), 2),
            "avg_long_minutes": round(sum(v["minutes"] or 0 for v in longs) / max(len(longs), 1), 1),
            "top_last_90_days": [{"title": v["title"], "views": v["views"],
                                  "x_median": round(v["views"] / max(med, 1), 1)} for v in top],
        })
    out({"channels": rows})


def cmd_unanswered(a):
    """Recent viewer comments the channel owner hasn't replied to yet (needs a key)."""
    cid = resolve_channel(a.ref)
    ch = api("channels", part="snippet,contentDetails", id=cid)["items"][0]
    owner_name = ch["snippet"].get("customUrl", "").lower()
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    items = api("playlistItems", part="snippet", playlistId=uploads, maxResults=min(a.videos, 50))["items"]
    ask = re.compile(r"\?|\b(how|kaise|kese|kaisy|kya|kia|kyun|why|please|plz|pls|bana|batao|bataye|"
                     r"help|error|not working|nahi|nhi|video on|next)\b", re.I)
    rows = []
    for it in items:
        vid, title = it["snippet"]["resourceId"]["videoId"], it["snippet"]["title"]
        tok = None
        while True:
            p = dict(part="snippet,replies", videoId=vid, maxResults=100, order="time")
            if tok:
                p["pageToken"] = tok
            try:
                r = api("commentThreads", **p)
            except ApiError:
                break
            for t in r.get("items", []):
                sn = t["snippet"]["topLevelComment"]["snippet"]
                if sn.get("authorChannelId", {}).get("value") == cid or sn["authorDisplayName"].lower() == owner_name:
                    continue
                replies = t.get("replies", {}).get("comments", [])
                if any(rp["snippet"].get("authorChannelId", {}).get("value") == cid for rp in replies):
                    continue
                if t["snippet"]["totalReplyCount"] > len(replies):
                    continue  # can't see every reply; skip rather than guess
                rows.append({"video": title[:70], "video_id": vid, "comment_id": t["id"],
                             "posted": sn["publishedAt"][:10], "likes": sn["likeCount"],
                             "asks_or_complains": bool(ask.search(sn["textOriginal"])),
                             "text": sn["textOriginal"][:500],
                             "link": f"https://www.youtube.com/watch?v={vid}&lc={t['id']}"})
            tok = r.get("nextPageToken")
            if not tok:
                break
    rows.sort(key=lambda r: (not r["asks_or_complains"], -r["likes"], r["posted"]), reverse=False)
    out({"channel_title": ch["snippet"]["title"], "unanswered": len(rows),
         "questions": sum(r["asks_or_complains"] for r in rows), "comments": rows[:a.max]})


def cmd_thumbs(a):
    """Download thumbnails (your latest videos, or the top results for a search) to compare."""
    outdir = Path(a.out).expanduser()
    outdir.mkdir(parents=True, exist_ok=True)
    if a.search:
        ids = [(i["id"]["videoId"], i["snippet"]["title"]) for i in api(
            "search", part="snippet", q=a.search, type="video", maxResults=min(a.max, 25),
            order="viewCount",
            publishedAfter=(datetime.now(timezone.utc) - timedelta(days=a.days)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"))["items"]]
    else:
        d = fetch_channel(a.ref, a.max)
        ids = [(v["id"], v["title"]) for v in d["videos"] if not v.get("is_short")][:a.max]
    saved = []
    for i, (vid, title) in enumerate(ids, 1):
        for size in ("maxresdefault", "hqdefault"):
            try:
                data = urllib.request.urlopen(urllib.request.Request(
                    f"https://i.ytimg.com/vi/{vid}/{size}.jpg", headers=UA), timeout=20).read()
            except urllib.error.HTTPError:
                continue
            p = outdir / f"{i:02d}_{vid}.jpg"
            p.write_bytes(data)
            saved.append({"file": str(p), "video_id": vid, "title": title})
            break
    out({"folder": str(outdir), "thumbnails": saved})


HISTORY = Path.home() / ".config" / "yt-channel-coach" / "history"


def cmd_snapshot(a):
    """Save today's numbers and compare with the last saved run (progress over time)."""
    d = fetch_channel(a.ref, 50)
    folder = HISTORY / d["channel_id"]
    folder.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    previous = sorted(p for p in folder.glob("*.json") if p.stem != today)
    snap = {"date": today, "subscribers": d.get("subscribers"), "total_views": d.get("total_views"),
            "videos": {v["id"]: {"title": v["title"], "views": v["views"], "likes": v.get("likes")}
                       for v in d["videos"]}}
    (folder / f"{today}.json").write_text(json.dumps(snap, ensure_ascii=False))
    if not previous:
        out({"first_snapshot": True, "saved": today, "channel_title": d["channel_title"],
             "note": "Run again in a few days to see what changed."})
        return
    old = json.loads(previous[-1].read_text())
    days = max((datetime.fromisoformat(today) - datetime.fromisoformat(old["date"])).days, 1)
    changes = []
    for vid, v in snap["videos"].items():
        before = old["videos"].get(vid)
        gained = v["views"] - (before["views"] if before else 0)
        changes.append({"title": v["title"], "new_video": before is None,
                        "views_now": v["views"], "views_gained": gained,
                        "per_day": round(gained / days, 1)})
    changes.sort(key=lambda c: -c["views_gained"])

    def diff(k):
        return None if snap.get(k) is None or old.get(k) is None else snap[k] - old[k]
    out({"channel_title": d["channel_title"], "since": old["date"], "days": days,
         "subscribers_gained": diff("subscribers"), "total_views_gained": diff("total_views"),
         "videos": changes})


# A "hook" is a promised result, a number that means something, or open curiosity.
# Version numbers ("5.5") and feature words ("Tutorial", "Explained") don't count.
HOOK_WORDS = re.compile(
    r"\?|!|\$\s?\d|\b\d+\s?x\b|\b\d+\s(ways|tips|tools|steps|mistakes|minutes|mins|days|hours|seconds)\b|"
    r"\b(free|no|without|never|stop|vs|secret|mistake|truth|fake|broke|hurt|nobody|everyone|"
    r"i (built|tested|let|made|tried|gave|turned|replaced)|kaise|kyun)\b", re.I)
EXPLAINER = re.compile(r"\b(what is|explained|tutorial|introduction|intro to|basics|overview)\b", re.I)


def tier(value, steps):
    """steps: [(threshold, points), ...] high to low; the first threshold the value meets wins."""
    for threshold, points in steps:
        if value >= threshold:
            return points
    return 0


def cmd_scorecard(a):
    """Fixed 100-point channel score: same data in, same grade out."""
    d = fetch_channel(a.ref, 50)
    has_key = d["mode"] == "api"
    longs = sorted([v for v in d["videos"] if v.get("is_short") is False],
                   key=lambda v: v["days_live"])
    if len(longs) < 3:
        fail("Need at least 3 long videos to score a channel.", long_videos=len(longs))
    last10 = longs[:10]
    med = median([v["views"] for v in last10]) or 1
    parts = []

    # 1. Consistency: long uploads per week over 60 days, and the longest recent gap
    recent = [v for v in longs if v["days_live"] <= 60]
    per_week = round(len(recent) / (60 / 7), 2)
    ages = [0] + [v["days_live"] for v in longs[:6]]
    gap = round(max(b - a for a, b in zip(ages, ages[1:])), 1)
    pts = round(min(per_week, 1) * 14) + tier(-gap, [(-10, 6), (-21, 3)])
    parts.append({"criterion": "Consistency", "points": pts, "max": 20,
                  "measured": f"{per_week} long videos/week (last 60 days); longest gap {gap} days",
                  "rule": "1+ per week = 14 pts (scaled); longest gap <=10 days = 6, <=21 days = 3"})

    # 2. Momentum: newer vs older long videos (only ones at least 14 days old, so both had time).
    # The single biggest hit is left out so one outlier can't fake a trend.
    best = max(longs, key=lambda v: v["views"])
    aged = [v for v in longs if v["days_live"] >= 14 and v is not best]
    if len(aged) >= 6:
        k = min(4, len(aged) // 2)
        new_med = median([v["views"] for v in aged[:k]])
        old_med = median([v["views"] for v in aged[k:2 * k]])
        ratio = round(new_med / max(old_med, 1), 2)
        pts = tier(ratio, [(1.2, 20), (1.0, 15), (0.8, 10), (0.5, 5)])
        measured = (f"median of newest {k} = {new_med:,} vs previous {k} = {old_med:,} ({ratio}x), "
                    "biggest hit left out")
    else:
        pts, measured = 10, "not enough videos older than 14 days; neutral 10/20"
    parts.append({"criterion": "Momentum", "points": pts, "max": 20, "measured": measured,
                  "rule": "newer/older median: 1.2x+ = 20, 1.0x = 15, 0.8x = 10, 0.5x = 5"})

    # 3. Hit power: best long video vs the channel's median
    x = round(best["views"] / med, 1)
    parts.append({"criterion": "Hit power", "points": tier(x, [(10, 20), (5, 16), (3, 12), (2, 8), (0, 4)]),
                  "max": 20,
                  "measured": f"best \"{best['title'][:60]}\" = {best['views']:,} views = {x}x median ({med:,})",
                  "rule": "best/median: 10x+ = 20, 5x = 16, 3x = 12, 2x = 8, else 4"})

    # 4. Engagement: likes per 100 views (+ comments per 1,000 views with a key)
    lp = median([100 * (v.get("likes") or 0) / max(v["views"], 1) for v in last10])
    like_pts = tier(lp, [(5, 12), (3.5, 9), (2, 6), (1, 3)])
    if has_key:
        cp = median([1000 * v.get("comments", 0) / max(v["views"], 1) for v in last10])
        pts = like_pts + tier(cp, [(5, 8), (2, 6), (1, 4), (0.5, 2)])
        measured = f"{lp:.1f} likes per 100 views; {cp:.1f} comments per 1,000 views (median, last 10 long)"
        rule = "likes/100: 5+ = 12, 3.5 = 9, 2 = 6, 1 = 3; comments/1000: 5+ = 8, 2 = 6, 1 = 4, 0.5 = 2"
    else:
        pts = round(like_pts * 20 / 12)
        measured = f"{lp:.1f} likes per 100 views (median, last 10 long; comments need a key)"
        rule = "likes/100: 5+ = 20, 3.5 = 15, 2 = 10, 1 = 5 (no-key mode)"
    parts.append({"criterion": "Engagement", "points": pts, "max": 20, "measured": measured, "rule": rule})

    # 5. Packaging: title length and a result / number / curiosity signal
    titles = [v["title"] for v in last10]
    short_share = sum(len(t) <= 60 for t in titles) / len(titles)
    hook_share = sum(bool(HOOK_WORDS.search(t)) and not EXPLAINER.search(t) for t in titles) / len(titles)
    pts = round(short_share * 8 + hook_share * 12)
    parts.append({"criterion": "Packaging", "points": pts, "max": 20,
                  "measured": f"{round(short_share * 100)}% of titles <= 60 chars; {round(hook_share * 100)}% "
                              "promise a result or curiosity (free, no/without, vs, $, 'I tested/built…', a question…); "
                              "explainer titles ('What is', 'Tutorial', 'Explained') don't count",
                  "rule": "8 x share of short titles + 12 x share of hook titles (last 10 long)"})

    total = sum(p["points"] for p in parts)
    grade = "A" if total >= 90 else "B" if total >= 75 else "C" if total >= 60 else "D" if total >= 45 else "F"
    out({"channel_title": d["channel_title"], "mode": d["mode"], "score": total, "grade": grade,
         "grade_scale": "A 90+ · B 75+ · C 60+ · D 45+ · F below 45",
         "long_videos_scored": len(longs), "parts": parts,
         "weakest": min(parts, key=lambda p: p["points"] / p["max"])["criterion"]})


def cmd_comments(a):
    cid = resolve_channel(a.ref)
    ch = api("channels", part="snippet,contentDetails", id=cid)["items"][0]
    owner = ch["snippet"].get("customUrl", "").lower()
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    items = api("playlistItems", part="snippet", playlistId=uploads, maxResults=min(a.videos, 50))["items"]
    rows = []
    for it in items:
        vid, title = it["snippet"]["resourceId"]["videoId"], it["snippet"]["title"]
        tok, n = None, 0
        while n < a.per_video:
            p = dict(part="snippet", videoId=vid, maxResults=100, order="relevance")
            if tok:
                p["pageToken"] = tok
            try:
                r = api("commentThreads", **p)
            except ApiError:
                break  # comments turned off on this video
            for t in r.get("items", []):
                sn = t["snippet"]["topLevelComment"]["snippet"]
                if sn["authorDisplayName"].lower() == owner:
                    continue
                rows.append({"video": title[:70], "likes": sn["likeCount"],
                             "replies": t["snippet"]["totalReplyCount"],
                             "text": sn["textOriginal"][:400]})
                n += 1
            tok = r.get("nextPageToken")
            if not tok:
                break
    out({"channel_title": ch["snippet"]["title"], "comment_count": len(rows), "comments": rows})


def cmd_search(a):
    after = (datetime.now(timezone.utc) - timedelta(days=a.days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    p = dict(part="snippet", q=a.query, type="video", maxResults=min(a.max, 50),
             publishedAfter=after, order="relevance")
    if a.lang:
        p["relevanceLanguage"] = a.lang
    if a.region:
        p["regionCode"] = a.region
    ids = [i["id"]["videoId"] for i in api("search", **p)["items"]]
    if not ids:
        out({"query": a.query, "videos": []})
        return
    vs = api("videos", part="snippet,statistics,contentDetails", id=",".join(ids))["items"]
    chs = {c["id"]: int(c["statistics"].get("subscriberCount", 0)) for c in api(
        "channels", part="statistics", id=",".join({v["snippet"]["channelId"] for v in vs}))["items"]}
    rows = []
    for v in vs:
        views, subs = int(v["statistics"].get("viewCount", 0)), chs.get(v["snippet"]["channelId"], 0)
        rows.append({"id": v["id"], "title": v["snippet"]["title"], "channel": v["snippet"]["channelTitle"],
                     "subscribers": subs, "views": views,
                     "views_per_sub": round(views / max(subs, 1), 2),
                     "days_live": round(days_since(v["snippet"]["publishedAt"]), 1),
                     "minutes": iso_minutes(v["contentDetails"]["duration"])})
    rows.sort(key=lambda r: -r["views"])
    med = sorted(r["views"] for r in rows)[len(rows) // 2]
    out({"query": a.query, "days": a.days, "median_views": med, "videos": rows})


def cmd_suggest(a):
    u = ("https://suggestqueries.google.com/complete/search?client=firefox&ds=yt"
         f"&hl={a.hl}&gl={a.gl}&q=" + urllib.parse.quote(a.seed))
    out({"seed": a.seed, "suggestions": json.loads(http(u))[1][:10]})


def cmd_key_status(_):
    key = get_key()
    out({"has_key": bool(key), "source": "env" if os.environ.get("YOUTUBE_API_KEY") else
         (str(KEY_FILE) if key else None)})


def cmd_save_key(_):
    key = sys.stdin.read().strip()
    if not re.fullmatch(r"AIza[\w-]{30,}", key):
        fail("That doesn't look like a YouTube API key (it should start with AIza).")
    KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    KEY_FILE.write_text(key)
    KEY_FILE.chmod(0o600)
    try:
        works = bool(api("channels", part="id", forHandle="@YouTube").get("items"))
    except ApiError as e:
        works = str(e)
    out({"saved": str(KEY_FILE), "works": works})


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("key-status").set_defaults(f=cmd_key_status)
    sub.add_parser("save-key").set_defaults(f=cmd_save_key)
    p = sub.add_parser("channel"); p.add_argument("ref"); p.add_argument("--max", type=int, default=50)
    p.set_defaults(f=cmd_channel)
    p = sub.add_parser("comments"); p.add_argument("ref")
    p.add_argument("--videos", type=int, default=10); p.add_argument("--per-video", type=int, default=100)
    p.set_defaults(f=cmd_comments)
    p = sub.add_parser("search"); p.add_argument("query"); p.add_argument("--days", type=int, default=30)
    p.add_argument("--lang"); p.add_argument("--region"); p.add_argument("--max", type=int, default=25)
    p.set_defaults(f=cmd_search)
    p = sub.add_parser("compare"); p.add_argument("refs", nargs="+"); p.set_defaults(f=cmd_compare)
    p = sub.add_parser("unanswered"); p.add_argument("ref")
    p.add_argument("--videos", type=int, default=10); p.add_argument("--max", type=int, default=60)
    p.set_defaults(f=cmd_unanswered)
    p = sub.add_parser("thumbs"); p.add_argument("ref", nargs="?"); p.add_argument("--search")
    p.add_argument("--days", type=int, default=30); p.add_argument("--max", type=int, default=8)
    p.add_argument("--out", default="./yt-thumbnails"); p.set_defaults(f=cmd_thumbs)
    p = sub.add_parser("snapshot"); p.add_argument("ref"); p.set_defaults(f=cmd_snapshot)
    p = sub.add_parser("scorecard"); p.add_argument("ref"); p.set_defaults(f=cmd_scorecard)
    p = sub.add_parser("suggest"); p.add_argument("seed"); p.add_argument("--hl", default="en")
    p.add_argument("--gl", default="US"); p.set_defaults(f=cmd_suggest)
    a = ap.parse_args()
    try:
        a.f(a)
    except ApiError as e:
        fail(str(e))
    except urllib.error.URLError as e:
        fail(f"Network error: {e.reason}")


if __name__ == "__main__":
    main()
