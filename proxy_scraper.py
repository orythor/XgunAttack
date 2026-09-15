import requests
import re
import time
from concurrent.futures import ThreadPoolExecutor

SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/http/data.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
    "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Https.txt",
    "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt",
    "https://raw.githubusercontent.com/oxylabs/free-proxy-list/main/http.txt",
    "https://raw.githubusercontent.com/zloi-user/hideip.me/main/http.txt",
    "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt",
    "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt",
    "https://raw.githubusercontent.com/yemixzy/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
    "https://raw.githubusercontent.com/Anonym0usWork/proxyscrapers/main/http.txt",
    "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt",
]


def fetch(url):
    try:
        r = requests.get(url, timeout=15)
        pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}"
        return re.findall(pattern, r.text)
    except Exception as e:
        print(f"[!] Gagal: {url[:50]} → {e}")
        return []


def main():
    print("╭───〔 𝗫𝗴𝘂𝗻𝗔𝘁𝘁𝗮𝗰𝗸 𝗣𝗿𝗼𝘅𝘆 𝗦𝗰𝗿𝗮𝗽𝗲𝗿 〕───")
    print("│  by XioXploit")
    print("╰──────────────────────────────\n")

    all_proxies = set()
    with ThreadPoolExecutor(max_workers=10) as ex:
        for r in ex.map(fetch, SOURCES):
            all_proxies.update(r)

    with open("proxies.txt", "w") as f:
        for p in sorted(all_proxies):
            f.write(p + "\n")

    print(f"\n[✓] {len(all_proxies)} proxy saved ke proxies.txt")


if __name__ == "__main__":
    main()
