---
name: spy
description: Compare a YouTube channel side by side with 1–4 competitors. Covers median views, views per subscriber, upload rhythm, video length and Shorts mix, plus each competitor's recent outlier videos and the gaps you can take. Use when the user says "compare me with", "competitor analysis", "spy on this channel", or "what is [channel] doing right".
---

# Competitor spy

Script: `<skill-dir>/../../scripts/yt.py`, where `<skill-dir>` is this SKILL.md's folder. Use its absolute path. Run it with `python3`; on Windows, if `python3` isn't found, use `python` or `py`. Needs the free key (`/yt-channel-coach:setup`).

1. Get the user's handle and 1–4 competitor handles. If they don't know any competitors, find similar channels with `python3 <yt.py> search "<their main topic>" --days 60 --max 15` (add `--lang hi --region IN` for Hindi/Urdu). Pick channels close to their size, not giants.
2. Run `python3 <yt.py> compare "<you>" "<comp1>" "<comp2>" …`.
3. Report:
   - A **side-by-side table**: subscribers · median views (last 10 long) · views per sub · long uploads/week · Shorts share · average length.
   - **What they do that you don't**, with numbers. For example: "uploads 2×/week vs your 1", or "videos 17 min vs your 12".
   - **Their outliers** (`x_median` ≥ 3): list the topic and title pattern. Topics that beat their own median are proven demand.
   - **Gaps you can take**: topics that work for them and that you haven't covered, or have covered weakly. Give 3, each with a fresh title. Never copy their title.
   - **Where you beat them** (views per sub, for example). Be encouraging when the data supports it.

Public data only: no one's CTR or retention is visible. Don't guess them.
