#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════════
#   CB-USERHUNTER v1.0 — Ciberbrigada OSINT Suite
#   Búsqueda de usernames en 80+ plataformas simultáneamente
#   Uso exclusivo para fines legales y educativos
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

# ── Colores ───────────────────────────────────────────────────────────────────
C  = Fore.CYAN
Y  = Fore.YELLOW
G  = Fore.GREEN
R  = Fore.RED
W  = Fore.WHITE
D  = Fore.WHITE + Style.DIM
M  = Fore.MAGENTA
B  = Style.BRIGHT
RS = Style.RESET_ALL

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
}

# ══════════════════════════════════════════════════════════════════════════════
# BASE DE PLATAFORMAS — 80+ sitios
# Formato: nombre, url_check, método de detección
# ══════════════════════════════════════════════════════════════════════════════
PLATFORMS = [
    # ── Redes Sociales ────────────────────────────────────────────────────────
    {"name": "Instagram",       "url": "https://www.instagram.com/{}/",           "detect": "status_200"},
    {"name": "Twitter/X",       "url": "https://x.com/{}",                        "detect": "status_200"},
    {"name": "TikTok",          "url": "https://www.tiktok.com/@{}",              "detect": "status_200"},
    {"name": "Facebook",        "url": "https://www.facebook.com/{}",             "detect": "status_200"},
    {"name": "LinkedIn",        "url": "https://www.linkedin.com/in/{}",          "detect": "status_200"},
    {"name": "Pinterest",       "url": "https://www.pinterest.com/{}/",           "detect": "status_200"},
    {"name": "Snapchat",        "url": "https://www.snapchat.com/add/{}",         "detect": "status_200"},
    {"name": "Tumblr",          "url": "https://{}.tumblr.com",                   "detect": "status_200"},
    {"name": "Reddit",          "url": "https://www.reddit.com/user/{}",          "detect": "status_200"},
    {"name": "Twitch",          "url": "https://www.twitch.tv/{}",                "detect": "status_200"},
    {"name": "YouTube",         "url": "https://www.youtube.com/@{}",             "detect": "status_200"},
    {"name": "VK",              "url": "https://vk.com/{}",                       "detect": "status_200"},
    {"name": "Mastodon",        "url": "https://mastodon.social/@{}",             "detect": "status_200"},
    {"name": "Threads",         "url": "https://www.threads.net/@{}",             "detect": "status_200"},
    {"name": "Bluesky",         "url": "https://bsky.app/profile/{}",             "detect": "status_200"},

    # ── Desarrollo / Tech ─────────────────────────────────────────────────────
    {"name": "GitHub",          "url": "https://github.com/{}",                   "detect": "status_200"},
    {"name": "GitLab",          "url": "https://gitlab.com/{}",                   "detect": "status_200"},
    {"name": "Bitbucket",       "url": "https://bitbucket.org/{}",                "detect": "status_200"},
    {"name": "HackerNews",      "url": "https://news.ycombinator.com/user?id={}", "detect": "status_200"},
    {"name": "StackOverflow",   "url": "https://stackoverflow.com/users/{}",      "detect": "status_200"},
    {"name": "Dev.to",          "url": "https://dev.to/{}",                       "detect": "status_200"},
    {"name": "Replit",          "url": "https://replit.com/@{}",                  "detect": "status_200"},
    {"name": "Kaggle",          "url": "https://www.kaggle.com/{}",               "detect": "status_200"},
    {"name": "Codepen",         "url": "https://codepen.io/{}",                   "detect": "status_200"},
    {"name": "Pastebin",        "url": "https://pastebin.com/u/{}",               "detect": "status_200"},
    {"name": "NPM",             "url": "https://www.npmjs.com/~{}",               "detect": "status_200"},
    {"name": "PyPI",            "url": "https://pypi.org/user/{}/",               "detect": "status_200"},
    {"name": "Dockerhub",       "url": "https://hub.docker.com/u/{}",             "detect": "status_200"},

    # ── Gaming ────────────────────────────────────────────────────────────────
    {"name": "Steam",           "url": "https://steamcommunity.com/id/{}",        "detect": "status_200"},
    {"name": "Xbox",            "url": "https://xboxgamertag.com/search/{}",      "detect": "status_200"},
    {"name": "PSN",             "url": "https://psnprofiles.com/{}",              "detect": "status_200"},
    {"name": "Roblox",          "url": "https://www.roblox.com/user.aspx?username={}", "detect": "status_200"},
    {"name": "Chess.com",       "url": "https://www.chess.com/member/{}",         "detect": "status_200"},
    {"name": "Minecraft",       "url": "https://namemc.com/profile/{}",           "detect": "status_200"},
    {"name": "Fortnite",        "url": "https://fortnitetracker.com/profile/all/{}", "detect": "status_200"},
    {"name": "Speedrun",        "url": "https://www.speedrun.com/user/{}",        "detect": "status_200"},

    # ── Música / Creadores ────────────────────────────────────────────────────
    {"name": "Spotify",         "url": "https://open.spotify.com/user/{}",        "detect": "status_200"},
    {"name": "SoundCloud",      "url": "https://soundcloud.com/{}",               "detect": "status_200"},
    {"name": "Bandcamp",        "url": "https://{}.bandcamp.com",                 "detect": "status_200"},
    {"name": "Last.fm",         "url": "https://www.last.fm/user/{}",             "detect": "status_200"},
    {"name": "Mixcloud",        "url": "https://www.mixcloud.com/{}/",            "detect": "status_200"},

    # ── Fotos / Diseño ────────────────────────────────────────────────────────
    {"name": "Flickr",          "url": "https://www.flickr.com/people/{}",        "detect": "status_200"},
    {"name": "500px",           "url": "https://500px.com/p/{}",                  "detect": "status_200"},
    {"name": "Behance",         "url": "https://www.behance.net/{}",              "detect": "status_200"},
    {"name": "Dribbble",        "url": "https://dribbble.com/{}",                 "detect": "status_200"},
    {"name": "DeviantArt",      "url": "https://www.deviantart.com/{}",           "detect": "status_200"},
    {"name": "ArtStation",      "url": "https://www.artstation.com/{}",           "detect": "status_200"},

    # ── Foros / Comunidades ───────────────────────────────────────────────────
    {"name": "Quora",           "url": "https://www.quora.com/profile/{}",        "detect": "status_200"},
    {"name": "Medium",          "url": "https://medium.com/@{}",                  "detect": "status_200"},
    {"name": "Substack",        "url": "https://substack.com/@{}",                "detect": "status_200"},
    {"name": "Wordpress",       "url": "https://{}.wordpress.com",                "detect": "status_200"},
    {"name": "Blogspot",        "url": "https://{}.blogspot.com",                 "detect": "status_200"},
    {"name": "WikiPedia",       "url": "https://en.wikipedia.org/wiki/User:{}",   "detect": "status_200"},

    # ── Crypto / Finanzas ─────────────────────────────────────────────────────
    {"name": "Keybase",         "url": "https://keybase.io/{}",                   "detect": "status_200"},
    {"name": "Etherscan",       "url": "https://etherscan.io/enslookup-search?search={}", "detect": "status_200"},
    {"name": "CoinMarketCap",   "url": "https://coinmarketcap.com/community/profile/{}/", "detect": "status_200"},
    {"name": "BitcoinTalk",     "url": "https://bitcointalk.org/index.php?action=profile;username={}", "detect": "status_200"},

    # ── Trabajo / Profesional ─────────────────────────────────────────────────
    {"name": "AngelList",       "url": "https://angel.co/u/{}",                   "detect": "status_200"},
    {"name": "ProductHunt",     "url": "https://www.producthunt.com/@{}",         "detect": "status_200"},
    {"name": "Fiverr",          "url": "https://www.fiverr.com/{}",               "detect": "status_200"},
    {"name": "Upwork",          "url": "https://www.upwork.com/freelancers/~{}",  "detect": "status_200"},

    # ── Streaming / Video ─────────────────────────────────────────────────────
    {"name": "Vimeo",           "url": "https://vimeo.com/{}",                    "detect": "status_200"},
    {"name": "Dailymotion",     "url": "https://www.dailymotion.com/{}",          "detect": "status_200"},
    {"name": "Rumble",          "url": "https://rumble.com/user/{}",              "detect": "status_200"},
    {"name": "Kick",            "url": "https://kick.com/{}",                     "detect": "status_200"},

    # ── Ciberseguridad / OSINT ────────────────────────────────────────────────
    {"name": "HackTheBox",      "url": "https://app.hackthebox.com/users/{}",     "detect": "status_200"},
    {"name": "TryHackMe",       "url": "https://tryhackme.com/p/{}",              "detect": "status_200"},
    {"name": "BugCrowd",        "url": "https://bugcrowd.com/{}",                 "detect": "status_200"},
    {"name": "HackerOne",       "url": "https://hackerone.com/{}",                "detect": "status_200"},
    {"name": "Shodan",          "url": "https://www.shodan.io/member/{}",         "detect": "status_200"},

    # ── Otros ─────────────────────────────────────────────────────────────────
    {"name": "Telegram",        "url": "https://t.me/{}",                         "detect": "status_200"},
    {"name": "Signal",          "url": "https://signal.me/#p/{}",                 "detect": "status_200"},
    {"name": "Gravatar",        "url": "https://en.gravatar.com/{}",              "detect": "status_200"},
    {"name": "About.me",        "url": "https://about.me/{}",                     "detect": "status_200"},
    {"name": "Linktree",        "url": "https://linktr.ee/{}",                    "detect": "status_200"},
    {"name": "Carrd",           "url": "https://{}.carrd.co",                     "detect": "status_200"},
    {"name": "Cashapp",         "url": "https://cash.app/${}",                    "detect": "status_200"},
    {"name": "Patreon",         "url": "https://www.patreon.com/{}",              "detect": "status_200"},
    {"name": "Ko-fi",           "url": "https://ko-fi.com/{}",                    "detect": "status_200"},
    {"name": "OnlyFans",        "url": "https://onlyfans.com/{}",                 "detect": "status_200"},
    {"name": "Clubhouse",       "url": "https://www.clubhouse.com/@{}",           "detect": "status_200"},
    {"name": "Goodreads",       "url": "https://www.goodreads.com/{}",            "detect": "status_200"},
    {"name": "Letterboxd",      "url": "https://letterboxd.com/{}",               "detect": "status_200"},
    {"name": "Strava",          "url": "https://www.strava.com/athletes/{}",      "detect": "status_200"},
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

    print(f"                          {DIM}by: Fgunther{RST}")
    print()
    print(f"  {CYAN}{BOLD}Ciber{ORAN}brigada{RST} {CYAN}OSINT Suite{RST}  {DIM}─────────────────────{RST}")
    print(f"  {BOLD}╔══════════════════════════════════════════╗{RST}")
    print(f"  {BOLD}║  👤  CB-USERHUNTER  v1.0                ║{RST}")
    print(f"  {BOLD}║  Username OSINT — 80+ plataformas       ║{RST}")
    print(f"  {BOLD}╚══════════════════════════════════════════╝{RST}")
    print(f"  {DIM}[ ciberbrigada.com ]  [ OSINT Suite ]{RST}")
    print(f"  {YEL}⚠  Solo para uso legal, ético y educativo  ⚠{RST}")
    print()

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def separador(titulo=""):
    if titulo:
        pad = (58 - len(titulo)) // 2
        print(f"\n{C}{'─' * pad} {B}{titulo}{RS}{C} {'─' * pad}{RS}")
    else:
        print(f"{D}{'─' * 60}{RS}")

def ok(msg):   print(f"  {G}{B}[✓]{RS} {W}{msg}{RS}")
def warn(msg): print(f"  {Y}[!]{RS} {Y}{msg}{RS}")
def fail(msg): print(f"  {R}[✗]{RS} {D}{msg}{RS}")
def info(msg): print(f"  {C}[i]{RS} {W}{msg}{RS}")

# ══════════════════════════════════════════════════════════════════════════════
# CHECKER — verifica una plataforma
# ══════════════════════════════════════════════════════════════════════════════
def check_platform(platform, username):
    url = platform["url"].format(username)
    try:
        r = requests.get(
            url,
            headers=HEADERS,
            timeout=8,
            allow_redirects=True,
        )
        # Detección por status 200
        if r.status_code == 200:
            # Filtros anti-falso positivo
            body = r.text.lower()
            false_positives = [
                "page not found", "user not found", "doesn't exist",
                "no existe", "404", "this account doesn't exist",
                "sorry, this page isn't available",
                "the link you followed may be broken",
                "cuenta no encontrada", "perfil no encontrado",
                "this page could not be found",
                "usuario no encontrado",
            ]
            for fp in false_positives:
                if fp in body:
                    return None

            return {"name": platform["name"], "url": url, "status": r.status_code}

        return None

    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None

# ══════════════════════════════════════════════════════════════════════════════
# BÚSQUEDA PRINCIPAL — multihilo
# ══════════════════════════════════════════════════════════════════════════════
def search_username(username):
    separador(f"BUSCANDO: {username}")
    print(f"\n  {C}Analizando {len(PLATFORMS)} plataformas en paralelo...{RS}")
    print(f"  {D}Esto puede tardar 15-30 segundos{RS}\n")

    found     = []
    total     = len(PLATFORMS)
    completed = 0

    # Barra de progreso simple
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
# MOSTRAR RESULTADOS
# ══════════════════════════════════════════════════════════════════════════════
def show_results(username, found):
    separador(f"RESULTADOS — @{username}")

    if not found:
        warn(f"Username '{username}' no encontrado en ninguna plataforma")
        return

    ok(f"Encontrado en {G}{B}{len(found)}{RS} {W}plataformas:")
    print()

    # Agrupar por categoría
    categorias = {
        "Redes Sociales":    ["Instagram","Twitter/X","TikTok","Facebook","LinkedIn","Pinterest","Snapchat","Tumblr","Reddit","Threads","Bluesky","VK","Mastodon","Clubhouse"],
        "Desarrollo / Tech": ["GitHub","GitLab","Bitbucket","HackerNews","StackOverflow","Dev.to","Replit","Kaggle","Codepen","Pastebin","NPM","PyPI","Dockerhub"],
        "Gaming":            ["Steam","Xbox","PSN","Roblox","Chess.com","Minecraft","Fortnite","Speedrun"],
        "Música / Creadores":["Spotify","SoundCloud","Bandcamp","Last.fm","Mixcloud","YouTube","Twitch","Kick","Vimeo","Dailymotion","Rumble","Patreon","Ko-fi"],
        "Fotos / Diseño":    ["Flickr","500px","Behance","Dribbble","DeviantArt","ArtStation"],
        "Ciberseguridad":    ["HackTheBox","TryHackMe","BugCrowd","HackerOne","Shodan"],
        "Crypto / Finanzas": ["Keybase","Etherscan","CoinMarketCap","BitcoinTalk","Cashapp"],
        "Trabajo":           ["AngelList","ProductHunt","Fiverr","Upwork"],
        "Comunidades":       ["Quora","Medium","Substack","Wordpress","Blogspot","WikiPedia","Goodreads","Letterboxd","Strava"],
        "Otros":             ["Telegram","Signal","Gravatar","About.me","Linktree","Carrd","OnlyFans"],
    }

    found_names = {f["name"]: f for f in found}
    printed = set()

    for cat, plats in categorias.items():
        cat_found = [found_names[p] for p in plats if p in found_names]
        if cat_found:
            print(f"  {C}{B}▸ {cat}{RS}")
            for f in cat_found:
                print(f"    {G}[✓]{RS} {W}{B}{f['name']:<18}{RS} {D}{f['url']}{RS}")
                printed.add(f["name"])
            print()

    # Cualquier resultado que no cayó en categoría
    extras = [f for f in found if f["name"] not in printed]
    if extras:
        print(f"  {C}{B}▸ Otros{RS}")
        for f in extras:
            print(f"    {G}[✓]{RS} {W}{B}{f['name']:<18}{RS} {D}{f['url']}{RS}")
        print()

# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE DORKS
# ══════════════════════════════════════════════════════════════════════════════
def google_dorks(username):
    separador("GOOGLE DORKS")
    dorks = [
        (f'"{username}"',                              "Username exacto"),
        (f'"@{username}"',                             "Mención con @"),
        (f'"{username}" site:linkedin.com',            "LinkedIn"),
        (f'"{username}" site:github.com',              "GitHub"),
        (f'"{username}" filetype:pdf',                 "En PDFs"),
        (f'"{username}" email OR mail OR correo',      "Email asociado"),
        (f'"{username}" password OR contraseña OR leak',"En leaks"),
        (f'intext:"{username}" site:pastebin.com',     "Pastebin"),
        (f'"{username}" CV OR curriculum OR resume',   "Curriculums"),
        (f'"{username}" phone OR celular OR teléfono', "Teléfono asociado"),
    ]
    for dork, desc in dorks:
        encoded = urllib.parse.quote(dork)
        url = f"https://www.google.com/search?q={encoded}"
        print(f"  {C}▸ {W}{desc:<30}{RS} {D}{url[:70]}{RS}")

# ══════════════════════════════════════════════════════════════════════════════
# RESUMEN FINAL
# ══════════════════════════════════════════════════════════════════════════════
def resumen_final(username, found, elapsed):
    separador("RESUMEN")
    print(f"\n  {C}{B}Target:{RS}      {W}{B}@{username}{RS}")
    print(f"  {C}{B}Plataformas:{RS} {W}{len(PLATFORMS)} analizadas{RS}")
    print(f"  {C}{B}Encontrado:{RS}  {G}{B}{len(found)}{RS} {W}perfiles{RS}")
    print(f"  {C}{B}Tiempo:{RS}      {W}{elapsed:.1f}s{RS}")
    print()
    if found:
        print(f"  {D}Perfiles encontrados:{RS}")
        for f in found:
            print(f"  {G}  ✓{RS} {W}{f['name']}{RS}")
    print(f"\n  {D}Análisis completado — Ciberbrigada OSINT Suite v1.0{RS}\n")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    banner()

    print(f"  {W}Ingresá el username a buscar (sin @) o 'salir' para terminar:{RS}\n")

    while True:
        try:
            username = input(f"  {C}▸ Username:{RS} ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n  {Y}Saliendo... Hasta pronto.{RS}\n")
            sys.exit(0)

        if username.lower() in ("salir", "exit", "quit", "q"):
            print(f"\n  {Y}Saliendo... Hasta pronto.{RS}\n")
            sys.exit(0)

        # Limpiar @ si lo puso
        username = username.lstrip("@").strip()

        if not username or len(username) < 2:
            warn("Ingresá un username válido (mínimo 2 caracteres)")
            continue

        if not re.match(r'^[a-zA-Z0-9._\-]+$', username):
            warn("El username solo puede contener letras, números, puntos, guiones y guiones bajos")
            continue

        start   = time.time()
        found   = search_username(username)
        elapsed = time.time() - start

        show_results(username, found)
        google_dorks(username)
        resumen_final(username, found, elapsed)

        separador()
        print(f"\n  {D}¿Buscar otro username? (Enter para continuar / 'salir' para terminar){RS}")
        try:
            again = input(f"  {C}▸{RS} ").strip().lower()
            if again in ("salir", "exit", "quit", "q"):
                print(f"\n  {Y}Saliendo... Hasta pronto.{RS}\n")
                sys.exit(0)
        except (KeyboardInterrupt, EOFError):
            print(f"\n  {Y}Saliendo...{RS}\n")
            sys.exit(0)

        banner()

if __name__ == "__main__":
    main()
