---
name: title
description: Check a YouTube title (and optional thumbnail text) before uploading. Scores it against search autocomplete, competitor titles and the channel's own winners, then suggests better versions. Use when the user says "check my title", "is this title good", "title ideas", or pastes a draft title.
---

# Title check

Script: `<skill-dir>/../../scripts/yt.py`, where `<skill-dir>` is this SKILL.md's folder. Use its absolute path. Run it with `python3`; on Windows, if `python3` isn't found, use `python` or `py`. Reply in the user's language.

1. Get the draft title, the topic in one line, and (optionally) the channel handle and the thumbnail text.
2. Pull the main keyword's autocomplete: `python3 <yt.py> suggest "<keyword>"`, plus `--hl hi --gl IN` for Hindi/Urdu audiences.
3. With a key: `python3 <yt.py> search "<keyword>" --days 30 --max 15` to see winning titles in the niche right now.
4. With a handle: `python3 <yt.py> channel "<handle>" --max 20` to compare with the channel's own best titles.

## Score (out of 10), with one line each
- **Search phrase**: does it contain a real autocomplete phrase?
- **Result or curiosity**: does it promise an outcome, or open a loop, instead of naming a feature?
- **Length**: 60 characters or fewer, so it isn't cut off on phones. Count it.
- **Honest**: does the video deliver exactly this? Flag "free", "unlimited" or "never" if they're not fully true.
- **Different**: not a copy of the top competitor's title.
- **Thumbnail match**: the thumbnail text adds to the title, it doesn't repeat it.

Then give **3 better titles** with their character counts, and say which one you'd pick and why.
