#!/data/data/com.termux/files/usr/bin/bash

clear
echo ""
echo "╭───〔 𝗫𝗴𝘂𝗻𝗔𝘁𝘁𝗮𝗰𝗸 〕───"
echo "│  XgunAttack v2.1 INSTALLER"
echo "│  by XioXploit"
echo "│  Dark Media Edition"
echo "╰──────────────────────────────"
echo ""

echo "[*] Update package list..."
pkg update -y && pkg upgrade -y

echo "[*] Install python, git, curl..."
pkg install python git curl -y

echo "[*] Install pip dependencies..."
pip install --upgrade pip
pip install requests aiohttp fake-useragent colorama

echo ""
echo "╭─[ ✓ INSTALL DONE ]─"
echo "│  Jalanin : python xgun.py"
echo "│  Author  : XioXploit"
echo "╰──────────────────────────────"
echo "BY: © XioNiV"
echo ""