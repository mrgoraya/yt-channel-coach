---
name: setup
description: Set up yt-channel-coach. Check for a YouTube Data API key and walk a non-technical creator through getting a free one (about 3 minutes). Use when the user says "setup yt-channel-coach", "add my YouTube API key", or another yt-channel-coach skill reports needs_key.
---

# yt-channel-coach setup

The helper script is `<skill-dir>/../../scripts/yt.py`, where `<skill-dir>` is this SKILL.md's folder. Use its absolute path. Run it with `python3`; on Windows, if `python3` isn't found, use `python` or `py`. It needs only Python 3, which macOS already has.

1. Run `python3 <yt.py> key-status`.
   - If `has_key` is true, say it is ready and suggest `/yt-channel-coach:audit`.
   - If not, say plainly: the audit already works **without** a key (latest 15 videos and their views). A **free** key adds subscribers, comments and competitor research. Then ask whether they want to set one up now.

2. Guide them one step at a time, in the user's language (Urdu/Hindi/English), and wait after each step:
   1. Open https://console.cloud.google.com and sign in with any Google account.
   2. Top bar → project picker → **New project** → any name → **Create**.
   3. Search bar → **YouTube Data API v3** → **Enable**.
   4. **Credentials** → **Create credentials** → **API key** → copy it.
   5. Recommended: **Edit API key** → **API restrictions** → **Restrict key** → tick only *YouTube Data API v3* → **Save**.
   It is free: Google gives 10,000 units a day, and one audit uses well under 1,000. No card is needed.

3. When they paste the key, save it by piping it on stdin. Never put the key in a command argument, and never repeat it back:
   ```sh
   printf '%s' "<key>" | python3 <yt.py> save-key
   ```
   It is stored in `~/.config/yt-channel-coach/api_key`, readable only by them. Report `works`. If it says `accessNotConfigured`, step 3 was missed. If it says `keyInvalid`, the copy was incomplete.

4. Tell them: "Ready. Type `/yt-channel-coach:audit` and your channel handle."
