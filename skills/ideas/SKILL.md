---
name: ideas
description: Find the next YouTube video to make from real demand. Uses the channel's own winners, what viewers ask for in comments, competitor videos that beat their channel size, and YouTube search autocomplete. Use when the user says "what should I make next", "video ideas", "next video topic", or "research this topic".
---

# Video ideas from real demand

Script: `<skill-dir>/../../scripts/yt.py`, where `<skill-dir>` is this SKILL.md's folder. Use its absolute path. Run it with `python3`; on Windows, if `python3` isn't found, use `python` or `py`. Reply in the user's language.

## Steps
1. **Know the channel.** Ask for the handle if needed. Run `python3 <yt.py> channel "<handle>" --max 30`, then note the niche, the median views and the outlier topics.
2. **Viewer requests** (needs the key): run `python3 <yt.py> comments "<handle>" --videos 15 --per-video 80`. Keep only comments that ask for something ("please make", "how to", "kaise", "video on", questions). Group them and count them.
3. **Candidate topics:** list 5–8 from steps 1–2 plus the user's own idea, if they gave one.
4. **Search demand**, for each topic:
   - `python3 <yt.py> suggest "<topic>"`. Also run `--hl hi --gl IN` for Hindi/Urdu audiences. Autocomplete phrases are real searches; use them in titles.
   - With a key: `python3 <yt.py> search "<topic>" --days 30` (add `--lang hi --region IN` for Hindi/Urdu). Look for videos with **high `views_per_sub` from small channels** (under 50k subs). That proves the topic, not the channel, pulled the views. Note the median views.
   - Each search costs 100 of the 10,000 free daily units, so keep it to 8 or fewer per run.

## Output
A table: **Topic · Viewers asked (count) · Best small-channel proof (views / subs) · Median views · Verdict (Now / Later / Skip) · Why**.

Then pick one winner with:
- 3 title options, each with a search phrase from autocomplete, a result-first framing, and 60 characters or fewer
- a thumbnail idea in one line
- a 30-second hook

Avoid topics where only million-subscriber channels win. Say when a topic is crowded or risky, for example "free" claims that may not stay free.
