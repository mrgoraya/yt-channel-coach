---
name: audit
description: Audit a YouTube channel from its real public data. Finds which videos and topics win, what flops, title patterns, upload rhythm, Shorts vs long, and gives a grade plus 5 concrete fixes. Use when the user says "audit my channel", "why is my channel not growing", "channel review", or gives a YouTube handle or URL.
---

# Channel audit

Script: `<skill-dir>/../../scripts/yt.py`, where `<skill-dir>` is this SKILL.md's folder. Use its absolute path. Run it with `python3`; on Windows, if `python3` isn't found, use `python` or `py`. Reply in the user's language. If they write Roman Urdu or Hindi, answer in Roman Urdu or Hindi and keep YouTube terms in English.

## 1. Get the data
- Ask for the channel handle or URL if it wasn't given.
- `python3 <yt.py> channel "<handle>" --max 50`
- If `mode` is no-key, continue with what you have and mention once that `/yt-channel-coach:setup` (free key) adds subscribers and comments.
- If an API key exists, also run `python3 <yt.py> comments "<handle>" --videos 10 --per-video 60` for viewer signals.

## 2. Analyse (only from the data; never invent numbers)
- Split long videos from Shorts (`is_short`).
- **Winners and losers:** rank long videos by `views_per_day` and by total views. Name the top 3 and bottom 3 and find what separates them: topic, title words, length, promise.
- **Channel baseline:** median views of the last 10 long videos. A video above 3× the median is an outlier, and its topic is the channel's best lead.
- **Titles:** length, whether they promise a result or name a feature, numbers, brackets, curiosity.
- **Rhythm:** gaps between uploads. Is there a long gap before a drop?
- **Engagement:** likes per 100 views, and comments per 1,000 views, per video.
- **Comments (if fetched):** what viewers ask for, complain about, or praise. Quote 3–5 short real comments.

## 3. Report
Keep it short and visual:

1. **Grade (A–F)** with one line on why.
2. **Your best video and why it won** (numbers).
3. **What's not working** (2–3 points, with numbers).
4. **Viewers are asking for…** (from comments, if any).
5. **5 fixes for the next 30 days**, ordered by impact. Each fix must be concrete, like "Next title: put the result first, like your 55k video did", not "improve SEO".
6. **Next video idea:** one, based on the outlier topic plus comment requests. Offer `/yt-channel-coach:ideas` for more.

Save the report as `youtube-audit-<channel>-<YYYY-MM-DD>.md` in the current folder and tell the user where it is.

## Honesty rules
- Public data has no CTR, retention or impressions. Say so, and tell them where to find those in YouTube Studio → Analytics → Reach / Engagement.
- Don't promise views or virality. Use "likely" or "worth testing".
