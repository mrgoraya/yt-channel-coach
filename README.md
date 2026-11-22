# yt-channel-coach: your free YouTube coach in Claude Code

A Claude Code plugin from the [Think with MR](https://www.youtube.com/@ThinkwithMRG) YouTube channel. It reads your channel's **real public data** (it doesn't guess) and tells you what's working, what isn't, and what to make next.

| Command | What it does |
|---|---|
| `/yt-channel-coach:audit` | A fixed 100-point scorecard (A–F), your best video and why it won, and 5 fixes |
| `/yt-channel-coach:ideas` | Next video ideas from your comments, competitor wins and real searches |
| `/yt-channel-coach:title` | Scores your title before you upload and suggests better ones |
| `/yt-channel-coach:thumbnail` | Tests your thumbnail at phone size and against this month's winning thumbnails |
| `/yt-channel-coach:replies` | Finds comments you haven't answered (questions first) and drafts replies in the viewer's language |
| `/yt-channel-coach:spy` | You vs your competitors, side by side, plus the topics you can take from them |
| `/yt-channel-coach:progress` | Saves your numbers and shows what grew since last time (run it weekly) |
| `/yt-channel-coach:setup` | Adds a free YouTube API key (optional, about 3 minutes) |

## What you get (real example)

From the audit of [@ThinkwithMRG](https://www.youtube.com/@ThinkwithMRG):

> **Score: 90/100 (A).** Weakest part: engagement (2.8 likes per 100 views).
> **Best video:** "Claude Opus 5.5 & Fable 5.1 with Millions of Free Tokens (No Paid Plan)" got 55,585 views, **71× your median**.
> **Why it won:** every outlier promises to *save money or skip a skill* (Free, $0, No Paid Plan, Without Code).
> **Not working:** plain explainers (173 views), and a 10-day gap right after the hit.
> + 5 fixes for the next 30 days and a next-video idea.

And from `/yt-channel-coach:replies`: *"73 comments have no reply, and 29 of them are questions or complaints"*, each with a draft reply in the viewer's own language.

## How the grade works

The audit uses a **fixed 100-point scorecard**, so the same data always gives the same grade:

| Part (20 pts each) | What it measures |
|---|---|
| Consistency | Long videos per week (last 60 days) and the longest recent gap |
| Momentum | Newer vs older videos' median views; your single biggest hit is left out |
| Hit power | Your best video divided by your median |
| Engagement | Likes per 100 views (+ comments per 1,000 views with a key) |
| Packaging | Titles of 60 characters or fewer that promise a result or curiosity |

**A** 90+ · **B** 75+ · **C** 60+ · **D** 45+ · **F** below 45. It compares your channel with itself, not with big channels.

## Requirements

- **Claude Code** (it comes with a paid Claude plan, Pro or Max, or with API access)
- **Python 3**: already on macOS. On Windows, install it from [python.org](https://www.python.org/downloads/) and tick "Add to PATH".
- Optional: a free YouTube Data API key (no card)

## Install (paste in Claude Code)

```
/plugin marketplace add mrgoraya/yt-channel-coach
/plugin install yt-channel-coach@think-with-mr
```

Then type: `/yt-channel-coach:audit @yourchannel`

**No key needed to start:** audit, ideas, title, thumbnail (phone test) and progress work right away with your latest 15 videos. A **free** YouTube Data API key (no card) adds subscribers, comment replies, competitor research and winning thumbnails. `/yt-channel-coach:setup` walks you through it, and your key stays on your computer in `~/.config/yt-channel-coach/`.

## Update or remove

```
/plugin marketplace update think-with-mr
/plugin update yt-channel-coach@think-with-mr
/plugin uninstall yt-channel-coach@think-with-mr
```

## Privacy

- Everything runs on your computer. The plugin calls only YouTube (public data, through your own key) and YouTube search suggestions.
- Your API key is saved in `~/.config/yt-channel-coach/api_key`, readable only by you. It's never printed or sent anywhere else.
- Weekly snapshots are saved in `~/.config/yt-channel-coach/history/`. Delete that folder to clear them.

## Troubleshooting

| Problem | Fix |
|---|---|
| `python3: command not found` (Windows) | Install Python from python.org with "Add to PATH" ticked. The plugin will try `python` or `py` |
| `needs_key` | That command needs the free key: run `/yt-channel-coach:setup` |
| `accessNotConfigured` | In Google Cloud, enable **YouTube Data API v3** for your project |
| `quotaExceeded` | You've used the free 10,000 daily units. It resets at midnight Pacific time |
| Channel not found | Use the exact handle (`@name`) or paste the channel URL |

## Honest limits

- Public data has no CTR, retention or impressions. Check those in YouTube Studio → Analytics.
- It never posts anything. You review and post replies yourself.
- No view guarantees, just what the data says.

## License

MIT: free to use, change and share. See [LICENSE](LICENSE).

## Author

Made by **Think with MR** ([YouTube](https://www.youtube.com/@ThinkwithMRG)): AI explained simply, in Urdu/Hindi. Found a bug or have an idea? Open an issue.
