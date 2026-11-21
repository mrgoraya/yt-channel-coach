---
name: replies
description: Find viewer comments the creator hasn't replied to yet (questions and complaints first) and draft a short reply for each in the viewer's own language. Use when the user says "reply to my comments", "unanswered comments", "comment replies", or "who should I reply to".
---

# Comment replies

Script: `<skill-dir>/../../scripts/yt.py`, where `<skill-dir>` is this SKILL.md's folder. Use its absolute path. Run it with `python3`; on Windows, if `python3` isn't found, use `python` or `py`. Needs the free key; if `needs_key` comes back, offer `/yt-channel-coach:setup`.

1. Run `python3 <yt.py> unanswered "<handle>" --videos 10 --max 40`.
2. Tell the user how many comments are unanswered, and how many ask something or complain (`asks_or_complains`). Replies in the first days help a video, and a public reply also answers every silent viewer with the same question.
3. Group repeated questions ("same error from 6 people") and give one reply that fits all of them. Suggest making it the **pinned comment** when the same question comes up 3 or more times.
4. Draft replies:
   - Use the viewer's language and script: Roman Urdu stays Roman Urdu, Hindi stays Hindi, English stays English.
   - Keep each reply to 1–2 lines: warm, specific, and an actual answer. Don't write "thanks for watching!" filler.
   - For a hostile comment ("fake", "scam"), stay calm, give a fact and a fix, and never argue. If it's only abuse, recommend **Hide user from channel** instead of replying.
   - Never invent facts about the video. If you're not sure what the video showed, write `[check: …]` in the reply.
5. Output a table: **Video · Comment (short) · Draft reply · Link** (use the `link` field, which opens the comment). Put the highest-priority comments first.

The user posts the replies themselves. This plugin never posts anything.
