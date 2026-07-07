# 👤 Mynds-OSINT

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0-cyan?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/OSINT-Username-orange?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/platforms-60+-brightgreen?style=for-the-badge"/>
</p>

<p align="center">
  <b>Hunt a username across 60+ platforms at once — fast, keyless, false-positive-aware.</b>
</p>

---

## What it does

Mynds-OSINT takes a single username and checks **60+ platforms in parallel**, then
shows only the profiles that actually exist, grouped by category. Every run is
saved to a per-username report under `reports/`.

- ✅ **Social** — Instagram, Twitter/X, Facebook, LinkedIn, Pinterest, Reddit, Bluesky, Mastodon…
- ✅ **Development** — GitHub, GitLab, StackOverflow, Dev.to, HackerNews, Replit, NPM, Docker Hub…
- ✅ **Gaming** — Steam, PSN, Roblox, Chess.com, Minecraft, Speedrun…
- ✅ **Music & creators** — SoundCloud, Bandcamp, Last.fm, YouTube, Kick, Patreon, Ko-fi…
- ✅ **Cybersecurity** — HackTheBox, TryHackMe, BugCrowd, HackerOne…
- ✅ **Automatic Google Dorks** for deeper manual pivoting
- ✅ **Reliable detection** — API endpoints, positive content markers and
  redirect analysis instead of naive text matching, so far fewer false positives

**100% free · no API keys · no signup · no login**

---

## Why the detection is reliable

Naive username checkers flag a profile as "found" whenever a page returns
HTTP `200`. Modern sites serve a generic `200` JavaScript shell even for
non-existent users, which produces a flood of false positives.

Mynds-OSINT uses per-platform strategies:

| Strategy | Example platforms | How it works |
|----------|-------------------|--------------|
| **Public API** | Bluesky, GitHub, Reddit, Chess.com | Query a JSON endpoint and check a data key (`did`, `login`, …) |
| **Positive marker** | Steam, Telegram, Pinterest | Require a string that only a real profile renders (`profile_page`, `tgme_page_title`, `og:title`) |
| **Redirect analysis** | Bandcamp, Replit, Substack, Wordpress, Ko-fi | A missing profile redirects to `/signup`, `/login`, `/search` or the homepage — detected via the final URL |
| **Non-empty response** | StackOverflow | The API always returns an `items` key; only a non-empty list counts |

Platforms that serve identical bot-blocked shells for real and fake users
(no reliable signal from a simple request) are intentionally **excluded**
rather than reported as false positives.

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/joaoguiIherme/Mynds-OSINT
cd Mynds-OSINT

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python3 mynds_osint.py
```

Requires Python 3.9+. Dependencies: `requests`, `colorama`.

---

## Usage

```bash
python3 mynds_osint.py
```

```
▸ Username: johndoe

Scanning 60+ platforms in parallel...
[████████████████████░░░░░░░░░░░░░░░░░░░░] 65/63

── RESULTS — @johndoe ──

▸ Social Networks
  ✓ Instagram    https://www.instagram.com/johndoe/
  ✓ Reddit       https://www.reddit.com/user/johndoe

▸ Development / Tech
  ✓ GitHub       https://github.com/johndoe

▸ Gaming
  ✓ Steam        https://steamcommunity.com/id/johndoe
```

Type another username to keep searching, or `exit` to quit.

---

## Reports

Every search writes a plain-text report to `reports/{username}.txt`:

```
============================================================
Mynds-OSINT — Username OSINT Suite
Username: johndoe
Date:     2026-07-07 16:28:33
Platforms scanned: 63
Profiles found:    4
Elapsed:  11.7s
============================================================

[Instagram] https://www.instagram.com/johndoe/
[Reddit] https://www.reddit.com/user/johndoe
[GitHub] https://github.com/johndoe
[Steam] https://steamcommunity.com/id/johndoe
```

> Reports are ignored by git (`.gitignore`) so your searched targets never get
> committed. The `reports/` folder is kept in the repo via `.gitkeep`.

---

## Covered platforms

| Category | Platforms |
|----------|-----------|
| Social | Instagram, Twitter/X, Facebook, LinkedIn, Pinterest, Snapchat, Tumblr, Reddit, Bluesky, VK, Mastodon |
| Development | GitHub, GitLab, Bitbucket, HackerNews, StackOverflow, Dev.to, Replit, Codepen, Pastebin, NPM, Docker Hub |
| Gaming | Steam, PSN, Roblox, Chess.com, Minecraft, Speedrun, Fortnite |
| Music / Creators | SoundCloud, Bandcamp, Last.fm, Mixcloud, YouTube, Kick, Vimeo, Rumble, Patreon, Ko-fi |
| Photos / Design | Flickr, Behance, Dribbble, DeviantArt, ArtStation |
| Cybersecurity | HackTheBox, TryHackMe, BugCrowd, HackerOne |
| Crypto / Finance | Keybase, Cashapp |
| Work | ProductHunt, Fiverr |
| Communities | Quora, Medium, Substack, Wordpress, Goodreads, Letterboxd, Strava |
| Others | Telegram, Gravatar, About.me, Linktree |

> Some platforms (e.g. Instagram) enforce aggressive anti-bot protection and may
> return no result from certain networks. Mynds-OSINT favors a **miss over a
> false positive** in those cases.

---

## Adding a platform

Each platform is a dict in the `PLATFORMS` list in `mynds_osint.py`:

```python
{
    "name": "Example",
    "url": "https://example.com/{}",
    "detect": "not_contains:Page not found",   # or contains:TEXT / status_200
    "headers": HEADERS_DEFAULT,
    # optional:
    # "display_url": "https://example.com/user/{}",
    # "redirect_fail": ["/login", "/signup"],
    # "verify_username_in_final": True,
}
```

Always test a **known real** account and a **guaranteed fake** one — the fake
must return no match, otherwise the detection is a false positive.

---

## ⚠️ Legal notice

This tool is intended for **legal, ethical and educational use only**, such as
authorized OSINT investigations and security research. The authors are not
responsible for any misuse.

---

## License

Released under the [MIT License](LICENSE).
