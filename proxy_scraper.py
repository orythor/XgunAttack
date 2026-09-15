#!/usr/bin/env python3
import requests
import re
from concurrent.futures import ThreadPoolExecutor

SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
]


def fetch(url):
    try:
        r = requests.get(url, timeout=10)
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