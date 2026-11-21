---
name: progress
description: Track a YouTube channel's progress over time. Saves a snapshot of today's numbers and shows what changed since the last run, so you can see which videos are still growing and which stalled. Use when the user says "weekly report", "how did my channel do this week", "progress", or "what changed since last time".
---

# Progress report

Script: `<skill-dir>/../../scripts/yt.py`, where `<skill-dir>` is this SKILL.md's folder. Use its absolute path. Run it with `python3`; on Windows, if `python3` isn't found, use `python` or `py`. Works without a key, but subscriber numbers need the free key.

1. Run `python3 <yt.py> snapshot "<handle>"`. Snapshots are saved on this computer in `~/.config/yt-channel-coach/history/`.
2. If it says `first_snapshot`, explain that today's numbers are saved and they should run the same command in about a week to see the change. Suggest a fixed day, like every Monday.
3. Otherwise, report for the period (`since`, `days`):
   - **Subscribers gained** and **views gained**.
   - **Still growing:** the videos with the most `views_gained`. An old video that keeps gaining is getting search or suggested traffic, so it's worth a sequel or an update to its title.
   - **New uploads** (`new_video`) and how they started.
   - **Stalled:** recent videos gaining almost nothing.
   - **One action for this week**, based on the above.
4. Keep it short: a table plus 3–5 lines. Don't invent causes. Say "likely" when you're guessing why something grew.
