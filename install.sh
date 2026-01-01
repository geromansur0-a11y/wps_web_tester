#!/bin/bash
# Auto Install WPS Web Tester
G='\033[0;32m'
Y='\033[1;33m'
NC='\033[0m'

echo -e "${Y}[*] Memulai Instalasi...${NC}"

if [ -d "/data/data/com.termux/files/usr/bin" ]; then
    pkg update && pkg upgrade -y
    pkg install root-repo -y
    pkg install python tsu aircrack-ng reaver pixiewps sqlite pciutils psmisc iw -y
    pip install flask flask-socketio eventlet
else
    sudo apt update
    sudo apt install -y python3 python3-pip aircrack-ng reaver pixiewps sqlite3 pciutils psmisc iw
    pip3 install flask flask-socketio eventlet
fi

chmod +x app.py
echo -e "${G}[V] Instalasi Selesai. Jalankan dengan: sudo python app.py${NC}"
