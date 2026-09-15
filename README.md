# XgunAttack v4.0

Termux L7 Flooder — Dark Media Edition
**by XioXploit**

## Fitur
- L7 HTTP/HTTPS flood multi-thread (async aiohttp)
- Auto-rotate IP tiap 30 detik
- User-Agent randomizer
- Custom port support (bebas)
- Proxy scraper & tester
- Target checker (deteksi Cloudflare/WAF)

## Install

```bash
pkg install git python -y
pkg install python git curl -y
git clone https://github.com/orythor/XgunAttack.git
cd XgunAttack
bash install.sh
```

## Usage

```bash
python xgun.py
```

## Menu
| No | Fitur |
|----|-------|
| 1  | Attack |
| 2  | Chek Target |
| 3  | Tes Proxy |
| 4  | Scrape Proxy |
| 5  | Lihat Proxy |
| 0  | Exit |

## Attack Prompt
```
#> [0] Threads : (1-500 recommen) >
#> [0] Port    :
#> [0] Target  :
#> [88] Attack : on(jalan) >
```

## Disclaimer
Tool ini dibuat untuk **educational purpose** & penetration testing di lingkungan yang Lo punya izin. Penyalahgunaan adalah tanggung jawab user.

**by XioXploit**
