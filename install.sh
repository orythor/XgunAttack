clear
echo ""
echo "╭───〔 𝗫𝗴𝘂𝗻𝗔𝘁𝘁𝗮𝗰𝗸 〕───"
echo "│  XgunAttack v4.0 INSTALLER"
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
pip install requests aiohttp fake-useragent colorama aiohttp-socks

echo ""
echo "╭─[ ✓ INSTALL DONE ]─"
echo "│  Jalanin : python xgun.py"
echo "│  Author  : XioXploit"
echo "╰──────────────────────────────"
echo "By: © XioNiV"
echo ""
