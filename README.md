# 👤 CB-UserHunter

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0-cyan?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/OSINT-Username-orange?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/plataformas-80+-brightgreen?style=for-the-badge"/>
</p>

<p align="center">
  <b>Búsqueda de usernames en 80+ plataformas simultáneamente</b><br/>
  Parte de la <a href="https://ciberbrigada.com">Ciberbrigada OSINT Suite</a>
</p>

---

## ¿Qué hace?

CB-UserHunter busca un username en más de 80 plataformas en paralelo y muestra solo los perfiles encontrados, organizados por categoría.

- ✅ Redes sociales (Instagram, TikTok, Twitter/X, Facebook, LinkedIn...)
- ✅ Desarrollo (GitHub, GitLab, StackOverflow, HackerNews...)
- ✅ Gaming (Steam, PSN, Xbox, Roblox, Chess.com...)
- ✅ Música y creadores (Spotify, SoundCloud, Twitch, YouTube...)
- ✅ Ciberseguridad (HackTheBox, TryHackMe, BugCrowd, HackerOne...)
- ✅ Crypto (Keybase, CoinMarketCap, BitcoinTalk...)
- ✅ Google Dorks automáticos
- ✅ Búsqueda en paralelo — resultados en 15-30 segundos

**100% gratuito · Sin API keys · Sin registro · Sin login**

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/ciberbrigada/cb-userhunter
cd cb-userhunter

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar
python3 cb_user_hunter.py
```

---

## 🔄 Mantener actualizado

```bash
cd cb-userhunter
git pull
```

---

## Uso

```bash
python3 cb_user_hunter.py
```

```
▸ Username: johndoe

Analizando 80+ plataformas en paralelo...
[████████████████████░░░░░░░░░░░░░░░░░░░░] 65/80

── RESULTADOS — @johndoe ──

▸ Redes Sociales
  ✓ Instagram    https://www.instagram.com/johndoe/
  ✓ Twitter/X    https://x.com/johndoe
  ✓ Reddit       https://www.reddit.com/user/johndoe

▸ Desarrollo / Tech
  ✓ GitHub       https://github.com/johndoe

▸ Gaming
  ✓ Steam        https://steamcommunity.com/id/johndoe
```

---

## Plataformas incluidas (80+)

| Categoría | Plataformas |
|-----------|-------------|
| Redes Sociales | Instagram, Twitter/X, TikTok, Facebook, LinkedIn, Pinterest, Snapchat, Tumblr, Reddit, Threads, Bluesky, VK, Mastodon |
| Desarrollo | GitHub, GitLab, Bitbucket, HackerNews, StackOverflow, Dev.to, Replit, Kaggle, Codepen, Pastebin, NPM, PyPI, Dockerhub |
| Gaming | Steam, Xbox, PSN, Roblox, Chess.com, Minecraft, Fortnite, Speedrun |
| Música | Spotify, SoundCloud, Bandcamp, Last.fm, Mixcloud, YouTube, Twitch, Kick |
| Fotos/Diseño | Flickr, 500px, Behance, Dribbble, DeviantArt, ArtStation |
| Ciberseguridad | HackTheBox, TryHackMe, BugCrowd, HackerOne, Shodan |
| Crypto | Keybase, Etherscan, CoinMarketCap, BitcoinTalk, Cashapp |
| Comunidades | Quora, Medium, Substack, Wordpress, Goodreads, Letterboxd |
| Otros | Telegram, Gravatar, Linktree, About.me, Patreon, Ko-fi |

---

## ⚠️ Aviso Legal

Esta herramienta es para uso **exclusivamente legal, ético y educativo**.
Ciberbrigada no se hace responsable del mal uso de esta herramienta.

---

## 🛡️ Ciberbrigada OSINT Suite

- 📧 **CB-EmailHunter** — Email OSINT → [ver repo](https://github.com/ciberbrigada/cb-emailhunter)
- 👤 **CB-UserHunter** — Username OSINT *(este repositorio)*
- 📱 **CB-PhoneHunter** — OSINT de números telefónicos *(próximamente)*
- 🌐 **CB-DomainHunter** — OSINT de dominios e IPs *(próximamente)*
- 📸 **CB-InstaHunter** — Instagram OSINT *(próximamente)*

---

<p align="center">
  <a href="https://ciberbrigada.com">ciberbrigada.com</a> ·
  <a href="https://github.com/ciberbrigada">GitHub</a> ·
  <a href="https://www.linkedin.com/company/ciberbrigada/">LinkedIn</a>
  <br/><br/>
  <sub>by: Fgunther</sub>
</p>
