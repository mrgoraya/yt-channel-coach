---
name: thumbnail
description: Check a YouTube thumbnail before upload. Compares it with the thumbnails that are winning for the same topic right now, and tests whether it still reads at phone size. Use when the user says "check my thumbnail", "is this thumbnail good", or shares a thumbnail image.
---

# Thumbnail check

Script: `<skill-dir>/../../scripts/yt.py`, where `<skill-dir>` is this SKILL.md's folder. Use its absolute path. Run it with `python3`; on Windows, if `python3` isn't found, use `python` or `py`.

1. Get the path to the thumbnail image, the video topic (2–4 words) and the planned title.
2. Look at the user's thumbnail with the Read tool.
3. **Phone-size test.** Make a small copy about 360 px wide, which is how it looks in the mobile feed, and look at it again. On macOS: `sips -Z 360 "<file>" --out /tmp/yt-thumb-small.jpg`. Elsewhere, judge from the full image. Can you still read every word and see the face and the main object?
4. **The competition** (needs the free key): `python3 <yt.py> thumbs --search "<topic>" --days 30 --max 6 --out ./yt-thumbnails`. Read each downloaded file. These are the most-viewed recent videos on the topic.
5. Compare and score out of 10, one line each:
   - **Readable on a phone**: 3–4 big words at most
   - **One clear focus**: a face with emotion, or one object, not clutter
   - **Contrast**: does it stand out from the competitor thumbnails, or blend in? Same colours as everyone else = invisible
   - **Curiosity**: does it raise a question the title answers?
   - **Title fit**: it adds to the title instead of repeating the same words
   - **Honest**: no promise the video doesn't keep
6. Give the 3 most important fixes, concrete ones like "make 'NO LIMITS' 30% bigger and drop the second line". If the user has two versions, say which one wins and why.

Keep the downloaded competitor thumbnails for reference only. They belong to their creators, so never copy one.
