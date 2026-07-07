#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════════
#   MYNDS-OSINT v1.0 — Username OSINT Suite
#   Search a username across 60+ platforms simultaneously
#   For legal, ethical and educational use only
# ═══════════════════════════════════════════════════════════════════════════════

import sys
import time
import os
import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    os.system("pip install requests colorama --break-system-packages -q")
    import requests
    from colorama import init, Fore, Style
    init(autoreset=True)

# ── Colors ──────────────────────────────────────────────────────────────────────
C  = Fore.CYAN
Y  = Fore.YELLOW
G  = Fore.GREEN
R  = Fore.RED
W  = Fore.WHITE
D  = Fore.WHITE + Style.DIM
M  = Fore.MAGENTA
B  = Style.BRIGHT
RS = Style.RESET_ALL

HEADERS_DEFAULT = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

HEADERS_API = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                  "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "X-Requested-With": "XMLHttpRequest",
}

# ══════════════════════════════════════════════════════════════════════════════
# PLATFORM DATABASE — 60+ sites with advanced detection
# detect modes:
#   status_200         — only checks for HTTP 200
#   not_contains:TEXT  — 200 and does NOT contain that text (profile exists)
#   contains:TEXT      — 200 and DOES contain that text (profile exists)
#
# optional keys:
#   display_url                — pretty URL shown to the user (when the probe
#                                URL is an API endpoint)
#   redirect_fail: [substr]    — if the final URL contains any of these, the
#                                profile does NOT exist (site redirected to
#                                signup/login/search/etc.)
#   verify_username_in_final   — the username must remain in the final URL path,
#                                otherwise the site redirected to its homepage
# ══════════════════════════════════════════════════════════════════════════════
PLATFORMS = [
    # ── Social Networks ───────────────────────────────────────────────────────
    {
        # Strict JSON API: only counts as found when the JSON carries the
        # "username" field. IG's HTML shell returned a generic 200 and produced
        # false positives, which is why the fallback was removed.
        "name": "Instagram",
        "url": "https://i.instagram.com/api/v1/users/web_profile_info/?username={}",
        "detect": "contains:\"username\"",
        "headers": {**HEADERS_API, "X-IG-App-ID": "936619743392459"},
        "display_url": "https://www.instagram.com/{}/",
    },
    {
        "name": "Twitter/X",
        "url": "https://x.com/{}",
        "detect": "not_contains:This account doesn't exist",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "YouTube",
        "url": "https://www.youtube.com/@{}",
        "detect": "not_contains:channel/about",
        "headers": HEADERS_DEFAULT,
        "alt_detect": "contains:channelId",
    },
    {
        "name": "Facebook",
        "url": "https://www.facebook.com/{}",
        "detect": "not_contains:Page Not Found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "LinkedIn",
        "url": "https://www.linkedin.com/in/{}",
        "detect": "not_contains:Page not found",
        "headers": HEADERS_DEFAULT,
    },
    {
        # The real profile carries an og:title meta tag; the "not found" page
        # does not.
        "name": "Pinterest",
        "url": "https://www.pinterest.com/{}/",
        "detect": "contains:og:title",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Snapchat",
        "url": "https://www.snapchat.com/add/{}",
        "detect": "not_contains:Sorry, we couldn't find",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Tumblr",
        "url": "https://{}.tumblr.com",
        "detect": "not_contains:There's nothing here",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Reddit",
        "url": "https://www.reddit.com/user/{}/about.json",
        "detect": "contains:\"name\"",
        "headers": {**HEADERS_DEFAULT, "Accept": "application/json"},
    },
    {
        "name": "VK",
        "url": "https://vk.com/{}",
        "detect": "not_contains:This page does not exist",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Mastodon",
        "url": "https://mastodon.social/@{}",
        "detect": "not_contains:The page you are looking for",
        "headers": HEADERS_DEFAULT,
    },
    {
        # Public API: 200 with "did" if the account exists, 400 otherwise.
        "name": "Bluesky",
        "url": "https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile?actor={}",
        "detect": "contains:\"did\"",
        "headers": {**HEADERS_DEFAULT, "Accept": "application/json"},
        "display_url": "https://bsky.app/profile/{}",
    },

    # ── Development / Tech ─────────────────────────────────────────────────────
    {
        "name": "GitHub",
        "url": "https://api.github.com/users/{}",
        "detect": "contains:\"login\"",
        "headers": {**HEADERS_DEFAULT, "Accept": "application/vnd.github.v3+json"},
        "display_url": "https://github.com/{}",
    },
    {
        "name": "GitLab",
        "url": "https://gitlab.com/{}",
        "detect": "not_contains:404",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Bitbucket",
        "url": "https://bitbucket.org/{}",
        "detect": "not_contains:Page not found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "HackerNews",
        "url": "https://hacker-news.firebaseio.com/v0/user/{}.json",
        "detect": "contains:\"id\"",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Dev.to",
        "url": "https://dev.to/api/users/by_username?url={}",
        "detect": "contains:\"username\"",
        "headers": {**HEADERS_DEFAULT, "Accept": "application/json"},
        "display_url": "https://dev.to/{}",
    },
    {
        # A non-existent profile redirects to /login.
        "name": "Replit",
        "url": "https://replit.com/@{}",
        "detect": "not_contains:page doesn't exist",
        "headers": HEADERS_DEFAULT,
        "redirect_fail": ["/login", "/signup"],
    },
    {
        "name": "Codepen",
        "url": "https://codepen.io/{}",
        "detect": "not_contains:404",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Pastebin",
        "url": "https://pastebin.com/u/{}",
        "detect": "not_contains:Not Found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "NPM",
        "url": "https://registry.npmjs.org/~{}",
        "detect": "status_200",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Dockerhub",
        "url": "https://hub.docker.com/v2/users/{}",
        "detect": "contains:\"username\"",
        "headers": {**HEADERS_DEFAULT, "Accept": "application/json"},
    },
    {
        # The API always returns the "items" key; only counts if it is NOT empty.
        "name": "StackOverflow",
        "url": "https://api.stackexchange.com/2.3/users?inname={}&site=stackoverflow",
        "detect": "not_contains:\"items\":[]",
        "headers": HEADERS_DEFAULT,
        "display_url": "https://stackoverflow.com/users?tab=Reputation&filter=all&search={}",
    },

    # ── Gaming ────────────────────────────────────────────────────────────────
    {
        # The real profile contains the "profile_page" container; the error page
        # carries "error_ctn". We use the positive marker.
        "name": "Steam",
        "url": "https://steamcommunity.com/id/{}",
        "detect": "contains:profile_page",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "PSN",
        "url": "https://psnprofiles.com/{}",
        "detect": "not_contains:User Not Found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Roblox",
        "url": "https://api.roblox.com/users/get-by-username?username={}",
        "detect": "contains:\"Id\"",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Chess.com",
        "url": "https://api.chess.com/pub/player/{}",
        "detect": "contains:\"username\"",
        "headers": HEADERS_DEFAULT,
        "display_url": "https://www.chess.com/member/{}",
    },
    {
        "name": "Minecraft",
        "url": "https://api.mojang.com/users/profiles/minecraft/{}",
        "detect": "contains:\"name\"",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Speedrun",
        "url": "https://www.speedrun.com/api/v1/users/{}",
        "detect": "contains:\"data\"",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Fortnite",
        "url": "https://fortnitetracker.com/profile/all/{}",
        "detect": "not_contains:We could not find",
        "headers": HEADERS_DEFAULT,
    },

    # ── Music / Creators ──────────────────────────────────────────────────────
    {
        "name": "SoundCloud",
        "url": "https://soundcloud.com/{}",
        "detect": "not_contains:We can't find that user",
        "headers": HEADERS_DEFAULT,
    },
    {
        # A non-existent subdomain redirects to bandcamp.com/signup.
        "name": "Bandcamp",
        "url": "https://{}.bandcamp.com",
        "detect": "status_200",
        "headers": HEADERS_DEFAULT,
        "redirect_fail": ["/signup", "bandcamp.com/?"],
    },
    {
        "name": "Last.fm",
        "url": "https://www.last.fm/user/{}",
        "detect": "not_contains:User not found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Mixcloud",
        "url": "https://api.mixcloud.com/{}/",
        "detect": "contains:\"username\"",
        "headers": HEADERS_DEFAULT,
    },

    # ── Photos / Design ───────────────────────────────────────────────────────
    {
        "name": "Flickr",
        "url": "https://www.flickr.com/people/{}",
        "detect": "not_contains:Page Not Found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Behance",
        "url": "https://www.behance.net/{}",
        "detect": "not_contains:page not found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Dribbble",
        "url": "https://dribbble.com/{}",
        "detect": "not_contains:Whoops",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "DeviantArt",
        "url": "https://www.deviantart.com/{}",
        "detect": "not_contains:page not found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "ArtStation",
        "url": "https://www.artstation.com/{}",
        "detect": "not_contains:Page not found",
        "headers": HEADERS_DEFAULT,
    },

    # ── Forums / Communities ──────────────────────────────────────────────────
    {
        "name": "Quora",
        "url": "https://www.quora.com/profile/{}",
        "detect": "not_contains:Page Not Found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Medium",
        "url": "https://medium.com/@{}",
        "detect": "not_contains:Page not found",
        "headers": HEADERS_DEFAULT,
    },
    {
        # A non-existent handle redirects to /search.
        "name": "Substack",
        "url": "https://substack.com/@{}",
        "detect": "status_200",
        "headers": HEADERS_DEFAULT,
        "redirect_fail": ["/search"],
        "verify_username_in_final": True,
    },
    {
        # A non-existent subdomain redirects to wordpress.com/typo.
        "name": "Wordpress",
        "url": "https://{}.wordpress.com",
        "detect": "status_200",
        "headers": HEADERS_DEFAULT,
        "redirect_fail": ["/typo", "wordpress.com/?"],
    },
    {
        "name": "Goodreads",
        "url": "https://www.goodreads.com/{}",
        "detect": "not_contains:Page not found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Letterboxd",
        "url": "https://letterboxd.com/{}",
        "detect": "not_contains:Sorry, we can't find",
        "headers": HEADERS_DEFAULT,
    },

    # ── Cybersecurity ─────────────────────────────────────────────────────────
    {
        "name": "HackTheBox",
        "url": "https://www.hackthebox.com/api/v4/user/profile/basic/{}",
        "detect": "contains:\"profile\"",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "TryHackMe",
        "url": "https://tryhackme.com/api/user/exist/{}",
        "detect": "contains:true",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "BugCrowd",
        "url": "https://bugcrowd.com/{}",
        "detect": "not_contains:The page you were looking for",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "HackerOne",
        "url": "https://hackerone.com/{}",
        "detect": "not_contains:Page not found",
        "headers": HEADERS_DEFAULT,
    },

    # ── Crypto / Finance ──────────────────────────────────────────────────────
    {
        "name": "Keybase",
        "url": "https://keybase.io/_/api/1.0/user/lookup.json?username={}",
        "detect": "contains:\"them\"",
        "headers": HEADERS_DEFAULT,
        "display_url": "https://keybase.io/{}",
    },

    # ── Work / Professional ───────────────────────────────────────────────────
    {
        "name": "ProductHunt",
        "url": "https://www.producthunt.com/@{}",
        "detect": "not_contains:Page not found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Fiverr",
        "url": "https://www.fiverr.com/{}",
        "detect": "not_contains:Page Not Found",
        "headers": HEADERS_DEFAULT,
    },

    # ── Streaming / Video ─────────────────────────────────────────────────────
    {
        "name": "Vimeo",
        "url": "https://vimeo.com/{}",
        "detect": "not_contains:Sorry, we couldn't find",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Rumble",
        "url": "https://rumble.com/user/{}",
        "detect": "not_contains:Page Not Found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Kick",
        "url": "https://kick.com/{}",
        "detect": "not_contains:404",
        "headers": HEADERS_DEFAULT,
    },

    # ── Others ────────────────────────────────────────────────────────────────
    {
        # A real profile/channel carries "tgme_page_title"; the empty page does not.
        "name": "Telegram",
        "url": "https://t.me/{}",
        "detect": "contains:tgme_page_title",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Gravatar",
        "url": "https://en.gravatar.com/{}",
        "detect": "not_contains:404",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "About.me",
        "url": "https://about.me/{}",
        "detect": "not_contains:page doesn't exist",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Linktree",
        "url": "https://linktr.ee/{}",
        "detect": "not_contains:Sorry",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Patreon",
        "url": "https://www.patreon.com/{}",
        "detect": "not_contains:page you're looking for",
        "headers": HEADERS_DEFAULT,
    },
    {
        # A non-existent user redirects to the homepage (username drops from the path).
        "name": "Ko-fi",
        "url": "https://ko-fi.com/{}",
        "detect": "status_200",
        "headers": HEADERS_DEFAULT,
        "verify_username_in_final": True,
    },
    {
        "name": "Strava",
        "url": "https://www.strava.com/athletes/{}",
        "detect": "not_contains:Page Not Found",
        "headers": HEADERS_DEFAULT,
    },
    {
        "name": "Cashapp",
        "url": "https://cash.app/${}",
        "detect": "not_contains:Page Not Found",
        "headers": HEADERS_DEFAULT,
    },
]

# ══════════════════════════════════════════════════════════════════════════════
# BANNER
# ══════════════════════════════════════════════════════════════════════════════
def banner():
    os.system("cls" if os.name == "nt" else "clear")

    CYAN = '\033[96m'
    ORAN = '\033[38;5;208m'
    DIM  = '\033[2m\033[37m'
    BOLD = '\033[1m'
    YEL  = '\033[33m'
    RST  = '\033[0m'

    logo = [
        "              ...::::...               ",
        "              ..:::+: ....             ",
        "        .:...:::::::.  ..:....... ..   ",
        "       :+  .:::::::    ::::::::::.     ",
        "      .+. .::::::::    +::::::::++::   ",
        "    . ::.:+:.          :::       ::+:  ",
        "   .: :::+.            +:+       .+++  ",
        "   .+ .+::             +:+.    .:+++.  ",
        "    +: :+.             ++++++++++++:   ",
        "     +:.:+             +++:......:+++: ",
        "   :. :++++.           +++         ++%:",
        "    ::  .::+++:::::    +++        .++%:",
        "     .:::....::++++   .+++:.....::+++: ",
        "   ... ..:+::+::+++:. ::++++++++++:.   ",
        "     :+:. :+.:+:.:++::......  ...      ",
        "       :+: :+..++...::::.......         ",
        "         .. :+:..:+:.........           ",
    ]

    print()
    for line in logo:
        mid = len(line) // 2
        print(f"       {CYAN}{BOLD}{line[:mid]}{ORAN}{line[mid:]}{RST}")

    print()
    print(f"  {CYAN}{BOLD}Mynds{ORAN}-OSINT{RST} {CYAN}Suite{RST}  {DIM}───────────────────────────{RST}")
    print(f"  {BOLD}╔══════════════════════════════════════════╗{RST}")
    print(f"  {BOLD}║  👤  MYNDS-OSINT  v1.0                   ║{RST}")
    print(f"  {BOLD}║  Username OSINT — 60+ platforms          ║{RST}")
    print(f"  {BOLD}╚══════════════════════════════════════════╝{RST}")
    print(f"  {DIM}[ github.com/joaoguiIherme/Mynds-OSINT ]{RST}")
    print(f"  {YEL}⚠  For legal, ethical and educational use only  ⚠{RST}")
    print()

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def separator(title=""):
    if title:
        pad = (58 - len(title)) // 2
        print(f"\n{C}{'─' * pad} {B}{title}{RS}{C} {'─' * pad}{RS}")
    else:
        print(f"{D}{'─' * 60}{RS}")

REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")

def save_report(username, found, elapsed):
    """Save the found accounts to reports/{username}.txt"""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    path = os.path.join(REPORTS_DIR, f"{username}.txt")

    lines = [
        "=" * 60,
        "Mynds-OSINT — Username OSINT Suite",
        f"Username: {username}",
        f"Date:     {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Platforms scanned: {len(PLATFORMS)}",
        f"Profiles found:    {len(found)}",
        f"Elapsed:  {elapsed:.1f}s",
        "=" * 60,
        "",
    ]

    if found:
        for f in found:
            lines.append(f"[{f['name']}] {f['url']}")
    else:
        lines.append("Username not found on any platform.")

    lines.append("")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    return path

def ok(msg):   print(f"  {G}{B}[✓]{RS} {W}{msg}{RS}")
def warn(msg): print(f"  {Y}[!]{RS} {Y}{msg}{RS}")
def fail(msg): print(f"  {R}[✗]{RS} {D}{msg}{RS}")
def info(msg): print(f"  {C}[i]{RS} {W}{msg}{RS}")

# ══════════════════════════════════════════════════════════════════════════════
# CHECKER — verifies a single platform with advanced detection
# ══════════════════════════════════════════════════════════════════════════════
def check_platform(platform, username):
    url     = platform["url"].format(username)
    detect  = platform.get("detect", "status_200")
    headers = platform.get("headers", HEADERS_DEFAULT)

    try:
        r = requests.get(url, headers=headers, timeout=10,
                         allow_redirects=True)

        # Redirect-based detection: many sites redirect to signup/login/search/
        # typo/homepage when the profile does NOT exist. If the final URL
        # contains any of those markers, the profile does not exist.
        final_url = (r.url or "").lower()
        for sub in platform.get("redirect_fail", []):
            if sub in final_url:
                return None

        # Some sites redirect to the homepage (dropping the username from the
        # path) when the profile does not exist. Require the username in the
        # final path.
        if platform.get("verify_username_in_final"):
            path = urllib.parse.urlparse(r.url).path.lower()
            if username.lower() not in path:
                return None

        body = r.text.lower() if r.text else ""

        # status_200 — simple
        if detect == "status_200":
            if r.status_code == 200:
                return {"name": platform["name"], "url": platform.get("display_url", url).format(username), "status": r.status_code}
            return None

        # contains:TEXT — the profile exists if the text is present
        if detect.startswith("contains:"):
            needle = detect.split("contains:")[1].lower()
            if r.status_code == 200 and needle in body:
                return {"name": platform["name"], "url": platform.get("display_url", url).format(username), "status": r.status_code}
            return None

        # not_contains:TEXT — the profile exists if the text is NOT present
        if detect.startswith("not_contains:"):
            needle = detect.split("not_contains:")[1].lower()
            if r.status_code == 200 and needle not in body:
                # Make sure it is not a generic empty page
                if len(r.text) > 200:
                    return {"name": platform["name"], "url": platform.get("display_url", url).format(username), "status": r.status_code}
            # Try the fallback if one exists
            if "fallback_url" in platform:
                fb_url    = platform["fallback_url"].format(username)
                fb_detect = platform.get("fallback_detect", "status_200")
                try:
                    r2   = requests.get(fb_url, headers=HEADERS_DEFAULT, timeout=8, allow_redirects=True)
                    body2 = r2.text.lower()
                    if fb_detect.startswith("not_contains:"):
                        needle2 = fb_detect.split("not_contains:")[1].lower()
                        if r2.status_code == 200 and needle2 not in body2 and len(r2.text) > 200:
                            return {"name": platform["name"], "url": fb_url, "status": r2.status_code}
                except Exception:
                    pass
            return None

        return None

    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None

# ══════════════════════════════════════════════════════════════════════════════
# MAIN SEARCH — multi-threaded
# ══════════════════════════════════════════════════════════════════════════════
def search_username(username):
    separator(f"SEARCHING: {username}")
    print(f"\n  {C}Scanning {len(PLATFORMS)} platforms in parallel...{RS}")
    print(f"  {D}This may take 15-30 seconds{RS}\n")

    found     = []
    total     = len(PLATFORMS)
    completed = 0

    # Simple progress bar
    def progress(n, total):
        pct  = int(n / total * 40)
        bar  = "█" * pct + "░" * (40 - pct)
        print(f"\r  {C}[{bar}]{RS} {W}{n}/{total}{RS}", end="", flush=True)

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_platform, p, username): p for p in PLATFORMS}
        for future in as_completed(futures):
            completed += 1
            progress(completed, total)
            result = future.result()
            if result:
                found.append(result)

    print(f"\n")
    return found

# ══════════════════════════════════════════════════════════════════════════════
# SHOW RESULTS
# ══════════════════════════════════════════════════════════════════════════════
def show_results(username, found):
    separator(f"RESULTS — @{username}")

    if not found:
        warn(f"Username '{username}' not found on any platform")
        return

    ok(f"Found on {G}{B}{len(found)}{RS} {W}platforms:")
    print()

    # Group by category
    categories = {
        "Social Networks":     ["Instagram","Twitter/X","Facebook","LinkedIn","Pinterest","Snapchat","Tumblr","Reddit","Bluesky","VK","Mastodon"],
        "Development / Tech":   ["GitHub","GitLab","Bitbucket","HackerNews","StackOverflow","Dev.to","Replit","Codepen","Pastebin","NPM","Dockerhub"],
        "Gaming":              ["Steam","PSN","Roblox","Chess.com","Minecraft","Fortnite","Speedrun"],
        "Music / Creators":    ["SoundCloud","Bandcamp","Last.fm","Mixcloud","YouTube","Kick","Vimeo","Rumble","Patreon","Ko-fi"],
        "Photos / Design":     ["Flickr","Behance","Dribbble","DeviantArt","ArtStation"],
        "Cybersecurity":       ["HackTheBox","TryHackMe","BugCrowd","HackerOne"],
        "Crypto / Finance":    ["Keybase","Cashapp"],
        "Work":                ["ProductHunt","Fiverr"],
        "Communities":         ["Quora","Medium","Substack","Wordpress","Goodreads","Letterboxd","Strava"],
        "Others":              ["Telegram","Gravatar","About.me","Linktree"],
    }

    found_names = {f["name"]: f for f in found}
    printed = set()

    for cat, plats in categories.items():
        cat_found = [found_names[p] for p in plats if p in found_names]
        if cat_found:
            print(f"  {C}{B}▸ {cat}{RS}")
            for f in cat_found:
                print(f"    {G}[✓]{RS} {W}{B}{f['name']:<18}{RS} {D}{f['url']}{RS}")
                printed.add(f["name"])
            print()

    # Any result that did not fall into a category
    extras = [f for f in found if f["name"] not in printed]
    if extras:
        print(f"  {C}{B}▸ Others{RS}")
        for f in extras:
            print(f"    {G}[✓]{RS} {W}{B}{f['name']:<18}{RS} {D}{f['url']}{RS}")
        print()

# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE DORKS
# ══════════════════════════════════════════════════════════════════════════════
def google_dorks(username):
    separator("GOOGLE DORKS")
    dorks = [
        (f'"{username}"',                              "Exact username"),
        (f'"@{username}"',                             "Mention with @"),
        (f'"{username}" site:linkedin.com',            "LinkedIn"),
        (f'"{username}" site:github.com',              "GitHub"),
        (f'"{username}" filetype:pdf',                 "In PDFs"),
        (f'"{username}" email OR mail',                "Associated email"),
        (f'"{username}" password OR leak',             "In leaks"),
        (f'intext:"{username}" site:pastebin.com',     "Pastebin"),
        (f'"{username}" CV OR curriculum OR resume',   "Resumes"),
        (f'"{username}" phone OR mobile',              "Associated phone"),
    ]
    for dork, desc in dorks:
        encoded = urllib.parse.quote(dork)
        url = f"https://www.google.com/search?q={encoded}"
        print(f"  {C}▸ {W}{desc:<30}{RS} {D}{url[:70]}{RS}")

# ══════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
def final_summary(username, found, elapsed):
    separator("SUMMARY")
    print(f"\n  {C}{B}Target:{RS}     {W}{B}@{username}{RS}")
    print(f"  {C}{B}Platforms:{RS} {W}{len(PLATFORMS)} scanned{RS}")
    print(f"  {C}{B}Found:{RS}     {G}{B}{len(found)}{RS} {W}profiles{RS}")
    print(f"  {C}{B}Elapsed:{RS}   {W}{elapsed:.1f}s{RS}")
    print()
    if found:
        print(f"  {D}Profiles found:{RS}")
        for f in found:
            print(f"  {G}  ✓{RS} {W}{f['name']}{RS}")
    print(f"\n  {D}Analysis complete — Mynds-OSINT Suite v1.0{RS}\n")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    banner()

    print(f"  {W}Enter the username to search (without @) or 'exit' to quit:{RS}\n")

    while True:
        try:
            username = input(f"  {C}▸ Username:{RS} ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n  {Y}Exiting... See you soon.{RS}\n")
            sys.exit(0)

        if username.lower() in ("exit", "quit", "q"):
            print(f"\n  {Y}Exiting... See you soon.{RS}\n")
            sys.exit(0)

        # Strip @ if the user typed it
        username = username.lstrip("@").strip()

        if not username or len(username) < 2:
            warn("Enter a valid username (minimum 2 characters)")
            continue

        if not re.match(r'^[a-zA-Z0-9._\-]+$', username):
            warn("The username may only contain letters, numbers, dots, hyphens and underscores")
            continue

        start   = time.time()
        found   = search_username(username)
        elapsed = time.time() - start

        show_results(username, found)
        google_dorks(username)
        final_summary(username, found, elapsed)

        report_path = save_report(username, found, elapsed)
        info(f"Report saved to: {report_path}")

        separator()
        print(f"\n  {D}Search another username? (Enter to continue / 'exit' to quit){RS}")
        try:
            again = input(f"  {C}▸{RS} ").strip().lower()
            if again in ("exit", "quit", "q"):
                print(f"\n  {Y}Exiting... See you soon.{RS}\n")
                sys.exit(0)
        except (KeyboardInterrupt, EOFError):
            print(f"\n  {Y}Exiting...{RS}\n")
            sys.exit(0)

        banner()

if __name__ == "__main__":
    main()
